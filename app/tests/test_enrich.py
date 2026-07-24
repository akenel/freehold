"""Enrichment unit tests — the rules and the gate, as pure functions (no network).

The model half is deliberately untested here: with model="none" (or no API key)
enrich() must produce a complete, correct, fully-provenanced result on rules
alone. That's the contract that keeps a busy brain from ever breaking a sync.
"""
import asyncio

import enrich


def test_phone_rule_normalizes_nanp_and_strips_extension():
    assert enrich.phone_e164("1-770-736-8031 x56442")["value"] == "+17707368031"
    assert enrich.phone_e164("(254)954-1289")["value"] == "+12549541289"
    assert enrich.phone_e164("+41 44 668 18 00")["value"] == "+41446681800"


def test_phone_rule_keeps_the_original_beside_the_value():
    got = enrich.phone_e164("1-770-736-8031 x56442")
    assert got["original"] == "1-770-736-8031 x56442"
    assert got["source"] == "rule" and got["model"] == ""


def test_phone_rule_declines_rather_than_guesses():
    # Ambiguous input is handed to the model, not invented — a wrong phone
    # number in master data is worse than an absent one.
    assert enrich.phone_e164("") is None
    assert enrich.phone_e164("call the office") is None
    assert enrich.phone_e164("123") is None
    # A national number with no country context: 10 digits, but the leading 0
    # says it is not NANP. Real row from the SAP call list (Hays NL, "020 36 30
    # 310") — the naive rule turned it into a US number, which is worse than
    # returning nothing at all.
    assert enrich.phone_e164("020 36 30 310") is None
    assert enrich.candidates("020 36 30 310") == []


def test_phone_rule_declines_when_a_cell_holds_several_numbers():
    messy = "+31 20 -The Netherlands Tel: +31 (0)207 975 000 or +44 207 549 4040)"
    assert enrich.candidates(messy) == ["+31207975000", "+442075494040"]
    assert enrich.phone_e164(messy) is None      # ambiguous -> handed to the model


def test_candidates_strips_the_trunk_prefix():
    # "+31 (0) 20 890 8064" and "+31 20 890 8064" are the same number; if the
    # (0) survives they read as a conflict and a human gets pinged for nothing.
    assert enrich.candidates("+31 (0) 20 890 8064") == ["+31208908064"]
    assert enrich.candidates("0041 44 668 18 00") == ["+41446681800"]


def test_reconcile_spots_agreement_and_conflict():
    agree = enrich.reconcile({"a": "+31 20 890 8064", "b": "+31 (0) 20 890 8064"}, "a", "b")
    assert agree["value"]["status"] == "agree"
    assert agree["source"] == "rule"

    clash = enrich.reconcile({"a": "+31 20 890 8064", "b": "+41 44 668 18 00"}, "a", "b")
    assert clash["value"]["status"] == "conflict"

    lonely = enrich.reconcile({"a": "+31 20 890 8064", "b": "no number here"}, "a", "b")
    assert lonely["value"]["status"] == "only_a"

    assert enrich.reconcile({"a": "", "b": ""}, "a", "b") is None


def test_quality_scores_completeness_and_names_what_is_missing():
    got = enrich.quality({"name": "A", "email": "a@b.c", "company": "X"})
    assert got["value"]["score"] == 0.6                       # 3 of 5 present
    assert got["value"]["missing"] == ["phone", "city"]
    assert got["source"] == "rule"


def test_gate_thresholds():
    assert enrich.gate(0.95) == enrich.AUTO
    assert enrich.gate(0.90) == enrich.AUTO                   # boundary is inclusive
    assert enrich.gate(0.80) == enrich.REVIEW
    assert enrich.gate(0.70) == enrich.REVIEW
    assert enrich.gate(0.42) == enrich.REJECTED


def test_enrich_without_a_brain_still_produces_provenanced_output():
    records = [{"name": "Leanne", "email": "l@x.ch", "company": "Acme",
                "phone": "1-770-736-8031 x56442", "city": "Zug"}]
    out, stats = asyncio.run(enrich.enrich(records, model="none"))

    assert stats["model"] == "none"
    assert stats["enriched_count"] == 0 and stats["tokens"] == 0
    assert stats["prompt_version"] == ""                      # no model, no prompt claim

    rec = out[0]
    assert rec["name"] == "Leanne"                            # source fields untouched
    assert rec["_enriched"]["phone_e164"]["value"] == "+17707368031"
    assert rec["_enriched"]["quality"]["value"]["score"] == 1.0
    assert rec["_gate"] == enrich.AUTO                        # nothing AI-written to doubt


def test_every_enriched_value_carries_its_paper_trail():
    records = [{"name": "A", "email": "a@b.ch", "company": "X", "phone": "", "city": "Bern"}]
    out, _ = asyncio.run(enrich.enrich(records, model="none"))
    for f in out[0]["_enriched"].values():
        assert set(f) == {
            "value", "original", "source", "model",
            "prompt_version", "confidence", "at",
        }
        assert f["source"] in ("source", "rule", "model")
