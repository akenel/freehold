"""Recipe tests — the spec hash, the two enrich.py guards, and a rules-only run.

No vault, no MinIO, no Postgres: recipes imports vault lazily inside save/load
precisely so the parts that decide what happens to a customer's data can be
tested on a laptop.
"""
import asyncio
import copy

import actions
import enrich
import recipes
import xray

FIELDS = ["agentur", "telefon", "telefon_2", "status", "erfasst", "markt", "email"]
ROWS = [
    {"agentur": "Havas Media", "telefon": "+41 44 668 18 00", "telefon_2": "+41 44 668 18 00",
     "status": "Active", "erfasst": "2024-01-05", "markt": "CH / DE", "email": "info@havas.ch"},
    {"agentur": "havas media", "telefon": "+41 44 668 18 00", "telefon_2": "+41 79 111 22 33",
     "status": "active", "erfasst": "2024-02-06", "markt": "FR", "email": "info@havas.ch"},
    {"agentur": "Dentsu CH", "telefon": "+41 43 210 10 10", "telefon_2": "",
     "status": "ACTIVE", "erfasst": "2023-11-07", "markt": "CH", "email": "a@dentsu.ch"},
]
XR = xray.xray(FIELDS, ROWS, "Agenturen.xlsx", "Kontakte")


def _spec(action_list):
    spec = {
        "spec_version": 1, "key": "agenturen-2024", "label": "Media agency call list",
        "version": 3, "summary": "s", "list_kind": "call_list",
        "inbound": {"kind": "xlsx", "sheet": 0, "limit": 5000},
        "label_fields": ["agentur"],
        "semantics": {f: {"semantic": "free_text", "source": "rule",
                          "confidence": 0.6, "role": ""} for f in FIELDS},
        "actions": action_list,
        "derived_from": {"model": "gpt-oss:120b", "prompt_version": "list-analyze-v1",
                         "at": "2026-07-24T09:12:00+00:00", "src_key": "src/ab12",
                         "xray_sha": XR["sha"]},
    }
    return spec


def test_the_spec_hash_identifies_the_mapping_not_the_version():
    a = _spec([{"id": "dedupe", "columns": ["email"], "params": {}}])
    b = copy.deepcopy(a)
    b["version"] = 9
    b["derived_from"] = {"model": "deepseek-v3.1:671b", "at": "later"}
    assert recipes.spec_sha(a) == recipes.spec_sha(b)     # same mapping, different brain


def test_the_spec_hash_moves_when_the_mapping_moves():
    a = _spec([{"id": "dedupe", "columns": ["email"], "params": {}}])
    for change in (
        lambda s: s["actions"].append({"id": "build_schema", "columns": [], "params": {}}),
        lambda s: s["actions"][0].__setitem__("columns", ["agentur"]),
        lambda s: s["semantics"]["email"].__setitem__("semantic", "email"),
        lambda s: s.__setitem__("label_fields", ["email"]),
    ):
        b = copy.deepcopy(a)
        change(b)
        assert recipes.spec_sha(a) != recipes.spec_sha(b)


def test_validate_drops_what_cannot_run_and_says_so():
    spec = _spec([
        {"id": "geocode", "columns": ["markt"], "params": {}},
        {"id": "dedupe", "columns": ["nope"], "params": {}},
        {"id": "classify", "columns": ["agentur"], "params": {"taxonomy": ["CH"], "to": "m"}},
        {"id": "reconcile_phones", "columns": ["telefon"], "params": {}},
    ])
    got, warnings = recipes.validate(spec, FIELDS)
    assert [a["id"] for a in got["actions"]] == []
    assert len(warnings) == 5      # unknown id, bad column, dropped dedupe, thin taxonomy, lone pair


def test_validate_slugifies_and_caps_the_key():
    spec = _spec([])
    spec["key"] = "Agenturen 2024!! " + "x" * 60
    got, _ = recipes.validate(spec, FIELDS)
    assert got["key"].startswith("agenturen-2024-")
    assert len(got["key"]) <= 40


def test_validate_guarantees_the_two_things_enrich_cannot_survive_without():
    spec = _spec([{"id": "score_quality", "columns": [], "params": {}}])
    spec["label_fields"] = ["not_a_column"]
    got, _ = recipes.validate(spec, FIELDS)
    # score_quality with no columns would be a ZeroDivisionError in enrich.quality
    quality = next(a for a in got["actions"] if a["id"] == "score_quality")
    assert quality["columns"] == ["agentur"]
    assert got["label_fields"] == ["agentur"]


def test_a_rules_only_run_produces_the_exact_enrich_stats_shape():
    spec = _spec([{"id": "score_quality", "columns": ["agentur", "email"], "params": {}},
                  {"id": "normalize_phone", "columns": ["telefon"], "params": {}}])
    out, stats, extra = asyncio.run(recipes.run(spec, ROWS, model="none", xr=XR))
    assert set(stats) == {"profile", "model", "prompt_version", "enriched_count",
                          "tokens", "review_count", "note"}
    for rec in out:
        assert rec["_label"] and rec["_gate"] == enrich.AUTO and rec["_enriched"]
    assert out[0]["_enriched"]["phone_e164"]["value"] == "+41446681800"
    assert extra["recipe"]["spec_sha"] == recipes.spec_sha(spec)


def test_nothing_runs_that_you_did_not_tick():
    # enrich.enrich writes `quality` unconditionally in its seed pass.
    spec = _spec([{"id": "normalize_phone", "columns": ["telefon"], "params": {}}])
    out, _stats, _extra = asyncio.run(recipes.run(spec, ROWS, model="none", xr=XR))
    assert all("quality" not in r["_enriched"] for r in out)


def test_without_a_classify_the_brain_is_never_called_and_writes_no_empty_key():
    spec = _spec([{"id": "score_quality", "columns": ["agentur"], "params": {}}])
    out, stats, _ = asyncio.run(recipes.run(spec, ROWS, model="gpt-oss:120b", xr=XR))
    assert stats["model"] == "none"          # forced: there is nothing to classify
    assert all("" not in r["_enriched"] for r in out)
    assert "_recipe:agenturen-2024:3" not in enrich.PROFILES    # deregistered again


def test_canonicalize_runs_before_dedupe_so_merged_spellings_collapse():
    # "Havas Media" and "havas media" are the same agency. The order of the
    # post-pass is what makes the second one a duplicate rather than a new row.
    spec = _spec([
        {"id": "canonicalize_values", "columns": ["agentur"],
         "params": {"map": {"havas media": "Havas Media"}}},
        {"id": "dedupe", "columns": ["agentur"], "params": {}},
    ])
    out, _stats, extra = asyncio.run(recipes.run(spec, ROWS, model="none", xr=XR))
    assert out[1]["_enriched"]["agentur_canon"]["value"] == "Havas Media"
    assert out[1]["_enriched"]["dupe_of"]["value"]["first_row"] == 1
    assert extra["action_stats"]["dedupe"] == {"groups": 1, "rows": 1}
    assert extra["action_stats"]["canonicalize_values"]["merged"] == 1


def test_a_run_never_touches_the_records_it_was_given():
    before = copy.deepcopy(ROWS)
    spec = _spec([{"id": "validate_email", "columns": ["email"], "params": {}},
                  {"id": "dedupe", "columns": ["email"], "params": {}}])
    asyncio.run(recipes.run(spec, ROWS, model="none", xr=XR))
    assert ROWS == before


def test_every_post_pass_envelope_wears_the_same_seven_key_paper_trail():
    spec = _spec([
        {"id": "canonicalize_values", "columns": ["status"], "params": {"map": {"active": "Active"}}},
        {"id": "parse_dates", "columns": ["erfasst"], "params": {"from": "auto"}},
        {"id": "split_multivalue", "columns": ["markt"], "params": {"sep": "/"}},
        {"id": "validate_email", "columns": ["email"], "params": {}},
        {"id": "dedupe", "columns": ["email"], "params": {}},
    ])
    out, _stats, extra = asyncio.run(recipes.run(spec, ROWS, model="none", xr=XR))
    for rec in out:
        for name, env in rec["_enriched"].items():
            assert set(env) == {"value", "original", "replaces", "source", "model",
                                "prompt_version", "confidence", "at"}
            assert env["source"] == "rule", name
    assert extra["action_stats"]["parse_dates"]["parsed"] == 3
    assert extra["action_stats"]["split_multivalue"] == {"cells": 3, "values": 4}
    assert extra["action_stats"]["validate_email"]["checked"] == 3


def test_build_schema_lands_in_extra_and_not_in_a_record():
    spec = _spec([{"id": "build_schema", "columns": [],
                   "params": {"table": "agenturen_2024"}}])
    out, _stats, extra = asyncio.run(recipes.run(spec, ROWS, model="none", xr=XR))
    assert "CREATE TABLE agenturen_2024" in extra["schema_sql"]
    assert all("schema" not in r["_enriched"] for r in out)
    assert extra["action_stats"]["build_schema"]["tables"] == 1


def test_profile_from_and_run_agree_on_the_namespaced_key():
    spec = _spec([])
    p, override = actions.profile_from(spec)
    assert p.key == "_recipe:agenturen-2024:3" and override == "none"
    assert p.key not in enrich.PROFILES          # only registered for the length of a run


def test_a_column_action_with_no_columns_is_dropped_not_saved_as_a_noop():
    """A recipe that claims to normalize phones and doesn't is a lie in the
    artefact. Found by driving the form with the wrong token shape: the action
    id alone (no ":col" suffix) produced an action with columns=[] that was
    saved, ran, changed nothing, and reported success."""
    spec = recipes.build(XR, {"actions": []}, {
        "key": "t", "label": "T",
        # every scope except `table`, all without the ":cols" suffix
        "actions": ["normalize_phone", "reconcile_phones", "dedupe",
                    "parse_dates", "validate_email"],
    })
    assert [a["id"] for a in spec["actions"]] == []

    # build_schema is genuinely list-scoped and keeps its empty column list.
    spec = recipes.build(XR, {"actions": []}, {
        "key": "t", "label": "T", "actions": ["build_schema"]})
    assert [a["id"] for a in spec["actions"]] == ["build_schema"]

    # ...while the shape the template actually submits still works.
    spec = recipes.build(XR, {"actions": []}, {
        "key": "t", "label": "T", "actions": ["normalize_phone:telefon"]})
    assert [(a["id"], a["columns"]) for a in spec["actions"]] == [("normalize_phone", ["telefon"])]


def test_build_schema_withholds_primary_key_when_a_footer_pollutes_uniqueness():
    """The bug shipped to sandbox: the SAP list's 'agency' column read as unique
    'in every row' only because the footer rows were unique sentences, so the
    schema declared `agency TEXT PRIMARY KEY` — a note as the table's identity.
    With a trailer detected, the key candidate is named in a comment and the
    table gets a synthetic id instead."""
    import actions
    fields = ["agency", "phone"]
    rows = [{"agency": "Alpina AG", "phone": "+41445551234"},
            {"agency": "Bernina GmbH", "phone": "+41315559876"},
            {"agency": "TOTALS", "phone": ""},          # the footer
            {"agency": "Best time to call: Tue-Thu", "phone": ""}]
    xr = xray.xray(fields, rows, "list.xlsx", "Sheet1")
    assert xr["trailer_rows"], "the fixture must actually have a detected footer"

    spec = {"key": "agencies", "label": "Agencies",
            "semantics": {"agency": {"semantic": "company_name"}, "phone": {"semantic": "phone"}},
            "actions": [{"id": "build_schema", "columns": [], "params": {"table": "agencies"}}]}
    sql = actions.build_schema(spec, xr)
    assert "id            SERIAL PRIMARY KEY" in sql     # synthetic key
    assert "agency        TEXT NOT NULL" in sql          # agency is a column, NOT the key
    assert "agency        TEXT PRIMARY KEY" not in sql   # the exact bug we shipped
    assert "-- NOTE" in sql and "footer" in sql          # and we say why, in the file
