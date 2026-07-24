"""The golden corpus, asserted.

Every expectation in samples.py was worked out by hand BEFORE running the code.
That ordering is the whole value: a fixture whose expected output was copied from
a run will agree with the code forever, including when the code is wrong.
"""
import asyncio

import enrich
import inbound
from tests import samples as S
from tests._xlsx import make_xlsx


def _read(name):
    grid, tabs = S.SAMPLES[name]
    return inbound.read_xlsx(make_xlsx(grid, tabs))


def _by_label(records, key):
    return {r[key]: r for r in records}


# --- 1. clean -------------------------------------------------------------
def test_clean_list_needs_nothing_done_to_it():
    fields, recs = _read("1-clean-contacts")
    e = S.CLEAN_EXPECT
    assert len(recs) == e["rows"] and len(fields) == e["columns"]

    qf = ("company", "contact", "email", "phone", "city")
    assert all(enrich.quality(r, qf)["value"]["score"] == 1.0 for r in recs)
    resolved = [r for r in recs if enrich.phone_e164(r["phone"])]
    assert len(resolved) == e["phone_resolved"]
    # a tool that finds work on clean data is a tool nobody trusts
    assert all(len(enrich.candidates(r["phone"])) == 1 for r in recs)


# --- 2. messy phones ------------------------------------------------------
def test_every_phone_candidate_is_exactly_what_we_worked_out_by_hand():
    _fields, recs = _read("2-messy-phones")
    got = {r["agency"]: enrich.candidates(r["phone"]) for r in recs}
    assert got == S.MESSY_EXPECT["candidates"]


def test_the_rule_resolves_only_the_unambiguous_ones():
    _fields, recs = _read("2-messy-phones")
    resolved = [r["agency"] for r in recs if enrich.phone_e164(r["phone"])]
    declined = [r["agency"] for r in recs if not enrich.phone_e164(r["phone"])]
    assert resolved == S.MESSY_EXPECT["resolved_by_rule"]
    assert declined == S.MESSY_EXPECT["declined_by_rule"]


def test_reconcile_reports_the_right_disagreement_shape():
    _fields, recs = _read("2-messy-phones")
    got = {r["agency"]: (enrich.reconcile(r, "phone", "contact_details") or {})
           .get("value", {}).get("status")
           for r in recs}
    assert got == S.MESSY_EXPECT["reconcile"]


# --- 3. notes in the data -------------------------------------------------
def test_note_rows_survive_the_reader_and_are_caught_by_the_score():
    fields, recs = _read("3-notes-in-the-data")
    e = S.NOTES_EXPECT
    assert len(recs) == e["rows"], "the blank spacer is dropped, the notes are not"

    qf = tuple(fields)
    scored = [(r["agency"], enrich.quality(r, qf)["value"]["score"]) for r in recs]
    records = [s for s in scored if s[1] == e["quality_of_records"]]
    notes = [s for s in scored if s[1] == e["quality_of_notes"]]
    assert len(records) == e["real_records"]
    assert len(notes) == e["note_rows"]
    # this is the finding that impressed on the real call list: the junk rows
    # separate themselves by completeness alone, with no AI involved at all.
    assert {n for n, _ in notes} == {"PROGRESS", "Calls made", "3 of 12 done",
                                     "BEST TIME TO CALL",
                                     "Tuesday to Thursday, 09:30-11:00"}


# --- 4. dirty headers -----------------------------------------------------
def test_duplicate_blank_and_punctuated_headers_all_survive_as_distinct_fields():
    fields, recs = _read("4-dirty-headers")
    assert fields == S.DIRTY_EXPECT["fields"]
    assert len(recs) == S.DIRTY_EXPECT["rows"]
    # keeping both PHONE columns is the point — two columns claiming one fact
    # is a finding, not a nuisance.
    assert recs[0]["phone"] == "+41445551234" and recs[0]["phone_2"] == "044 555 12 34"


# --- 5. several tabs ------------------------------------------------------
def test_the_picker_sees_every_tab_and_reads_the_one_it_is_asked_for():
    grid, tabs = S.SAMPLES["5-several-tabs"]
    blob = make_xlsx(grid, tabs)
    assert inbound.sheet_names(blob) == S.MULTI_EXPECT["sheet_names"]
    for idx, expected in S.MULTI_EXPECT["fields_by_tab"].items():
        fields, _recs = inbound.read_xlsx(blob, sheet=idx)
        assert fields == expected, f"tab {idx} read the wrong sheet"


# --- the pipeline, rules only --------------------------------------------
def test_the_whole_enrichment_runs_on_every_sample_without_a_brain():
    """No sample may crash the engine, and none may quietly invent an AI field."""
    for name in S.SAMPLES:
        _fields, recs = _read(name)
        out, stats = asyncio.run(enrich.enrich(recs, model="none", profile="call_list"))
        assert len(out) == len(recs), name
        assert stats["model"] == "none" and stats["enriched_count"] == 0, name
        for r in out:
            assert r["_gate"] in (enrich.AUTO, enrich.REVIEW), name
            for f in r["_enriched"].values():
                assert f["source"] in ("rule", "source"), name


def test_footer_rows_are_gated_for_review_not_silently_applied():
    """The bug this fixes shipped to sandbox: a page of footer junk — PROGRESS,
    'Best time to call', a person's own margin notes — all scored ~0.12 by quality
    and all gated 'auto', i.e. green/applied, review_count 0. The X-ray SAW them
    (a 'trailer' finding) but nothing acted on it. Now completeness drives the
    gate: a row too empty to be a record is handed to a human."""
    _fields, recs = _read("3-notes-in-the-data")
    out, stats = asyncio.run(enrich.enrich(recs, model="none", profile="call_list"))

    reviewed = [r["agency"] for r in out if r["_gate"] == enrich.REVIEW]
    applied = [r["agency"] for r in out if r["_gate"] == enrich.AUTO]
    # the three real agencies pass; the five note rows are held for a human
    assert set(applied) == {"Alpina AG", "Bernina GmbH", "Cervin SA"}
    assert len(reviewed) == 5
    assert stats["review_count"] == 5
