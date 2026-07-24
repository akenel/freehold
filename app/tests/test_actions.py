"""Catalogue tests — the ten, their guards, and the two enrich.py landmines.

Pure and offline. Notably test_validate_email_makes_no_network_calls actively
breaks the network before running, because "no MX lookup" is a promise printed
on the customer's screen and a promise on a screen deserves a test.
"""
import socket

import actions
import enrich
import xray


def _recs(rows):
    """Rows in the shape enrich.enrich() hands to the post-pass."""
    return [{**r, "_enriched": {}, "_gate": enrich.AUTO, "_label": "—"} for r in rows]


def _bare(env):
    """An envelope minus its timestamp — for comparing two runs of the same rule."""
    return {k: v for k, v in env.items() if k != "at"}


def test_the_catalogue_is_closed_at_ten():
    assert len(actions.ACTIONS) == 10
    assert set(actions.ACTIONS) == {
        "normalize_phone", "reconcile_phones", "score_quality", "classify",
        "canonicalize_values", "parse_dates", "split_multivalue", "validate_email",
        "dedupe", "build_schema"}
    # Exactly one action calls a brain at run time. That sentence is on the screen.
    assert [a for a, m in actions.ACTIONS.items() if m["needs_model"]] == ["classify"]


def test_eligible_never_licences_an_action_we_cannot_execute():
    xr = {"eligible": [{"id": "dedupe", "columns": ["email"], "reason": "", "strength": 1.0},
                       {"id": "geocode", "columns": ["stadt"], "reason": "", "strength": 1.0}]}
    assert [e["id"] for e in actions.eligible(xr)] == ["dedupe"]


def test_profile_from_never_hands_enrich_an_empty_quality_list():
    # enrich.quality() divides by len(fields): empty means ZeroDivisionError on row 1.
    spec = {"key": "k", "version": 1, "label": "L", "semantics": {"agentur": {}, "telefon": {}},
            "label_fields": ["agentur"], "actions": []}
    p, _ = actions.profile_from(spec)
    assert p.quality_fields
    assert enrich.quality({"agentur": "Havas"}, p.quality_fields)["value"]["score"] == 1.0


def test_profile_from_forces_rules_only_when_nobody_ticked_classify():
    # enrich.enrich() writes _enriched[p.target] unconditionally; target="" plus a
    # live brain produces an envelope keyed "". Forcing "none" sidesteps it.
    spec = {"key": "k", "version": 1, "label": "L", "semantics": {"a": {}},
            "label_fields": ["a"], "actions": [{"id": "dedupe", "columns": ["a"], "params": {}}]}
    p, override = actions.profile_from(spec)
    assert p.target == "" and override == "none"


def test_profile_from_carries_a_classify_into_the_profile():
    spec = {"key": "k", "version": 2, "label": "L",
            "semantics": {"agentur": {}, "markt": {}}, "label_fields": ["agentur"],
            "actions": [{"id": "classify", "columns": ["agentur", "markt"],
                         "params": {"to": "markets", "multi": True,
                                    "taxonomy": ["CH", "DE"], "instruction": "Normalize."}}]}
    p, override = actions.profile_from(spec)
    assert override is None
    assert (p.target, p.multi, p.taxonomy, p.feed) == ("markets", True, ("CH", "DE"),
                                                       ("agentur", "markt"))
    assert p.key == "_recipe:k:2"          # namespaced: a recipe can never shadow "contacts"


def test_profile_from_makes_the_reconcile_pair_work_without_dropping_it():
    # enrich.Profile compares phone_field against reconcile_with, so one side of
    # the pair has to BE phone_field. Ticking "show me where these disagree"
    # without also ticking "normalise" is a reasonable thing to want.
    spec = {"key": "k", "version": 1, "label": "L", "semantics": {"tel": {}, "tel_2": {}},
            "label_fields": ["tel"],
            "actions": [{"id": "reconcile_phones", "columns": ["tel", "tel_2"], "params": {}}]}
    p, _ = actions.profile_from(spec)
    assert p.phone_field == "tel" and p.reconcile_with == "tel_2"


def test_profile_from_never_reconciles_a_column_against_itself():
    # Two normalize_phone entries in one spec used to collapse through a dict
    # keyed by action id, leaving phone_field == reconcile_with — which reports
    # "these two columns agree" about a single column. A lie that looks like a feature.
    spec = {"key": "k", "version": 1, "label": "L", "semantics": {"tel": {}, "tel_2": {}},
            "label_fields": ["tel"], "actions": [
                {"id": "normalize_phone", "columns": ["tel"], "params": {}},
                {"id": "normalize_phone", "columns": ["tel_2"], "params": {}},
                {"id": "reconcile_phones", "columns": ["tel", "tel_2"], "params": {}}]}
    p, _ = actions.profile_from(spec)
    assert p.phone_field == "tel" and p.reconcile_with == "tel_2"
    assert p.phone_field != p.reconcile_with


def test_canonicalize_merges_variants_and_leaves_everything_else_alone():
    xr = xray.xray(["status"], [{"status": v} for v in
                                ["Active", "Active", "active", "ACTIVE", "Closed"]], "f", "s")
    vmap = actions.value_map(xr, "status")
    assert vmap == {"active": "Active", "ACTIVE": "Active"}

    recs = _recs([{"status": "active"}, {"status": "Closed"}])
    stats = actions.canonicalize(recs, "status", vmap)
    assert recs[0]["_enriched"]["status_canon"]["value"] == "Active"
    assert recs[0]["_enriched"]["status_canon"]["original"] == "active"
    assert recs[1]["_enriched"]["status_canon"]["value"] == "Closed"
    assert stats == {"merged": 1, "variants": 2}


def test_parse_dates_reads_excel_serials():
    recs = _recs([{"erfasst": "45231"}])
    stats = actions.parse_dates(recs, "erfasst", "excel_serial")
    got = recs[0]["_enriched"]["erfasst_iso"]["value"]
    assert got == {"iso": "2023-11-01", "year": 2023, "quarter": "Q4"}
    assert stats["parsed"] == 1


def test_parse_dates_reads_iso():
    recs = _recs([{"d": "2024-11-08"}])
    actions.parse_dates(recs, "d", "auto")
    assert recs[0]["_enriched"]["d_iso"]["value"]["iso"] == "2024-11-08"
    assert recs[0]["_enriched"]["d_iso"]["value"]["quarter"] == "Q4"


def test_parse_dates_refuses_to_guess_day_versus_month():
    recs = _recs([{"d": "03/04/2024"}])
    stats = actions.parse_dates(recs, "d", "auto")
    assert recs[0]["_enriched"]["d_iso"]["value"] == {"status": "ambiguous", "raw": "03/04/2024"}
    assert stats == {"parsed": 0, "ambiguous": 1, "unparsed": 0}


def test_parse_dates_resolves_the_order_from_the_columns_own_evidence():
    # One row saying 25/12 proves the whole column is day-first. That is inference
    # from the customer's cells, not a guess about their passport.
    recs = _recs([{"d": "25/12/2023"}, {"d": "03/04/2024"}])
    stats = actions.parse_dates(recs, "d", "auto")
    assert recs[1]["_enriched"]["d_iso"]["value"]["iso"] == "2024-04-03"
    assert stats == {"parsed": 2, "ambiguous": 0, "unparsed": 0}


def test_parse_dates_says_unparsed_rather_than_inventing():
    recs = _recs([{"d": "hello"}])
    actions.parse_dates(recs, "d", "auto")
    assert recs[0]["_enriched"]["d_iso"]["value"] == {"status": "unparsed", "raw": "hello"}


def test_split_multivalue_strips_and_drops_empties():
    recs = _recs([{"markt": "CH / DE /  AT / "}])
    stats = actions.split_multivalue(recs, "markt", "/")
    assert recs[0]["_enriched"]["markt_values"]["value"] == {
        "sep": "/", "values": ["CH", "DE", "AT"]}
    assert stats == {"cells": 1, "values": 3}


def test_validate_email_flags_role_accounts_free_providers_and_junk():
    recs = _recs([{"e": "info@havas.ch"}, {"e": "a@gmail.com"}, {"e": "nope"}])
    stats = actions.validate_email(recs, "e")
    a, b, c = (r["_enriched"]["e_check"]["value"] for r in recs)
    assert a["role_account"] is True and a["free_provider"] is False and a["domain"] == "havas.ch"
    assert b["free_provider"] is True and b["role_account"] is False
    assert c["syntax"] is False and c["domain"] == ""
    assert stats == {"checked": 3, "bad_syntax": 1, "role": 1, "free": 1}


def test_validate_email_makes_no_network_calls(monkeypatch):
    """The screen promises 'no network'. Break the network and prove it."""
    def boom(*a, **kw):
        raise AssertionError("validate_email tried to touch the network")

    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    recs = _recs([{"e": "info@havas.ch"}, {"e": "b@x.example"}])
    assert actions.validate_email(recs, "e")["checked"] == 2


def test_dedupe_marks_the_copies_and_leaves_the_first_row_untouched():
    recs = _recs([{"e": "A@x.ch"}, {"e": "a@x.ch"}, {"e": " a@x .ch "}, {"e": "b@x.ch"}])
    stats = actions.dedupe(recs, ["e"])
    assert "dupe_of" not in recs[0]["_enriched"]
    assert recs[1]["_enriched"]["dupe_of"]["value"]["first_row"] == 1
    assert recs[2]["_enriched"]["dupe_of"]["value"]["group_size"] == 3
    assert "dupe_of" not in recs[3]["_enriched"]
    assert stats == {"groups": 1, "rows": 2}


def test_build_schema_emits_ddl_and_never_anything_that_runs():
    xr = xray.xray(["kundennr", "markt", "erfasst"],
                   [{"kundennr": f"K{i}", "markt": "CH / DE", "erfasst": "2024-01-0" + str(i)}
                    for i in range(1, 5)], "Agenturen.xlsx", "Kontakte")
    spec = {
        "key": "agenturen-2024", "version": 1, "label": "L",
        "semantics": {"kundennr": {"semantic": "identifier"}, "markt": {"semantic": "tag_list"},
                      "erfasst": {"semantic": "date"}},
        "label_fields": ["kundennr"],
        "actions": [
            {"id": "split_multivalue", "columns": ["markt"], "params": {"sep": "/"}},
            {"id": "classify", "columns": ["markt"],
             "params": {"to": "markets", "multi": False, "taxonomy": ["CH", "DE", "Other"]}},
            {"id": "build_schema", "columns": [], "params": {"table": "agenturen_2024"}},
        ],
    }
    sql = actions.build_schema(spec, xr)
    assert "CREATE TABLE agenturen_2024 (" in sql
    assert "kundennr" in sql and "PRIMARY KEY" in sql
    assert "CHECK (markets IN ('CH', 'DE', 'Other'))" in sql
    assert "CREATE TABLE agenturen_2024_markt (" in sql
    for forbidden in ("DROP", "INSERT", "EXECUTE", "DELETE", "TRUNCATE"):
        assert forbidden not in sql.upper()


def test_every_executor_is_idempotent():
    rows = [{"status": "active", "d": "2024-11-08", "markt": "CH / DE", "e": "info@x.ch"},
            {"status": "Active", "d": "2024-11-09", "markt": "FR", "e": "info@x.ch"}]
    vmap = {"active": "Active"}

    def run(recs):
        actions.canonicalize(recs, "status", vmap)
        actions.parse_dates(recs, "d", "auto")
        actions.split_multivalue(recs, "markt", "/")
        actions.validate_email(recs, "e")
        actions.dedupe(recs, ["e"])
        return [{k: _bare(v) for k, v in r["_enriched"].items()} for r in recs]

    once = run(_recs(rows))
    twice_recs = _recs(rows)
    run(twice_recs)
    assert run(twice_recs) == once
