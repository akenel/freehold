"""The hallucination suite — the most important tests in this feature.

Every one of these hands validate() the output of a model behaving badly, and
asserts that the bad part never reaches the screen. No network: validate() is a
pure function of (what the model said, what the cells say), which is exactly why
the anti-hallucination story is testable at all.
"""
import asyncio
import json
import types

import analyze
import enrich
import xray

FIELDS = ["agentur", "telefon", "markt", "erfasst"]
ROWS = [{"agentur": f"Havas {i}", "telefon": "+41 44 668 18 0" + str(i),
         "markt": "CH / DE", "erfasst": "2024-01-0" + str(i)} for i in range(1, 6)]
XR = xray.xray(FIELDS, ROWS, "Agenturen.xlsx", "Kontakte")
BLOB = json.dumps(analyze.profile_payload(XR), ensure_ascii=False)


def _v(raw, model="gpt-oss:120b"):
    return analyze.validate(raw, XR, model)


def _base(**over):
    """A well-behaved model answer, for mutating one field at a time."""
    return {"title": "Agentur list", "summary": "A list of agentur and telefon values.",
            "list_kind": "call_list", "confidence": 0.86,
            "columns": [{"name": "agentur", "semantic": "company_name",
                         "role": "", "confidence": 0.94}],
            "actions": [], **over}


def test_parse_survives_every_shape_a_model_actually_returns():
    obj = '{"title": "x", "columns": []}'
    assert analyze._parse(obj)["title"] == "x"
    assert analyze._parse('{"result": {"title": "x", "columns": []}}')["title"] == "x"
    assert analyze._parse('[{"title": "x"}]')["title"] == "x"
    assert analyze._parse('{"nope": 1}') == {}
    assert analyze._parse("not json at all") == {}
    assert analyze._parse("") == {}


def test_brake_1_a_number_the_model_wrote_never_reaches_the_screen():
    out, _dropped, _note = _v(_base(row_count=9999, distinct=4242, tokens=777))
    assert "9999" not in json.dumps(out) and "4242" not in json.dumps(out)


def test_brake_2_an_invented_list_kind_becomes_other():
    out, dropped, _ = _v(_base(list_kind="spaceships"))
    assert out["list_kind"]["value"] == "other" and out["list_kind"]["confidence"] == 0.0
    assert dropped >= 1


def test_brake_2_an_invented_semantic_becomes_unknown():
    out, dropped, _ = _v(_base(columns=[{"name": "agentur", "semantic": "vibes",
                                         "confidence": 0.9}]))
    assert out["columns"]["agentur"]["semantic"]["value"] == "unknown"
    assert out["columns"]["agentur"]["semantic"]["confidence"] == 0.0
    assert dropped >= 1


def test_brake_2_an_invented_action_is_dropped():
    out, dropped, note = _v(_base(actions=[{"id": "geocode", "columns": ["markt"],
                                            "confidence": 0.99}]))
    assert "geocode" not in json.dumps(out)
    assert dropped == 1 and "dropped" in note


def test_brake_3_a_column_that_does_not_exist_is_dropped():
    out, dropped, _ = _v(_base(columns=[{"name": "not_a_column", "semantic": "email",
                                         "confidence": 0.9}]))
    assert "not_a_column" not in out["columns"] and dropped == 1


def test_brake_3_the_first_claim_about_a_column_wins():
    out, dropped, _ = _v(_base(columns=[
        {"name": "agentur", "semantic": "company_name", "confidence": 0.9},
        {"name": "agentur", "semantic": "person_name", "confidence": 0.9}]))
    assert out["columns"]["agentur"]["semantic"]["value"] == "company_name"
    assert dropped == 1


def test_brake_3_a_column_the_model_skipped_falls_back_to_the_rules():
    out, _dropped, _ = _v(_base())
    telefon = out["columns"]["telefon"]["semantic"]
    assert telefon["source"] == "rule" and telefon["value"] == "phone"
    assert telefon["confidence"] == analyze.RULE_CONFIDENCE
    assert list(out["columns"]) == FIELDS            # source column order, always


def test_brake_4_an_eligible_action_with_the_wrong_columns_is_dropped():
    out, dropped, _ = _v(_base(actions=[
        {"id": "normalize_phone", "columns": ["agentur"], "confidence": 0.95}]))
    phone = [a for a in out["actions"] if a["id"] == "normalize_phone"]
    assert all(a["columns"] == ["telefon"] for a in phone)   # the rules' pair, not the model's
    assert all(a["source"] == "rule" for a in phone)
    assert dropped == 1


def test_brake_4_an_eligible_action_the_model_ignored_is_still_offered():
    out, _dropped, _ = _v(_base(actions=[]))
    offered = {(a["id"], tuple(a["columns"])) for a in out["actions"]}
    licensed = {(e["id"], tuple(e["columns"])) for e in XR["eligible"]}
    assert offered == licensed
    assert all(a["source"] == "rule" for a in out["actions"])


def test_a_silent_model_cannot_veto_a_rule_licensed_action():
    """The model may rank the menu; it may not remove items from it.

    gpt-oss returns actions with no `confidence` key at all — Ollama's `format`
    is a hint, not a constraint. Scoring that as 0.0 dropped every rule-licensed
    action into "rejected", which is a veto wearing a ranking's clothes. The
    rule's own strength is the floor: deterministic evidence doesn't stop being
    true because a model went quiet."""
    lic = XR["eligible"][0]
    raw = _base(actions=[{"id": lic["id"], "columns": list(lic["columns"])}])  # no confidence
    out, _dropped, _ = _v(raw)
    got = next(a for a in out["actions"]
               if a["id"] == lic["id"] and a["columns"] == list(lic["columns"]))
    assert got["confidence"] == lic["strength"], "rule strength must be the floor"
    assert got["gate"] == enrich.gate(lic["strength"])
    assert got["source"] == "rule", "the rule set this number, so say so"


def test_a_confident_model_may_still_raise_an_action_above_the_rule_floor():
    # Deliberately the WEAKEST licensed action — most are licensed at 1.0, where
    # a floor of 1.0 means the model can never move the number and the test would
    # prove nothing.
    lic = min(XR["eligible"], key=lambda e: e["strength"])
    assert lic["strength"] < 0.99, "pick a rule the model can actually out-rank"
    raw = _base(actions=[{"id": lic["id"], "columns": list(lic["columns"]),
                          "confidence": 0.99}])
    out, _dropped, _ = _v(raw)
    got = next(a for a in out["actions"]
               if a["id"] == lic["id"] and a["columns"] == list(lic["columns"]))
    assert got["confidence"] == 0.99
    assert got["source"] == "model"


def test_brake_5_kills_the_confident_invention():
    # Nothing in the profile said "Swiss" and nothing said "2019". This sentence
    # is fluent, plausible, useful-sounding and entirely made up.
    out, dropped, _ = _v(_base(summary="480 Swiss agencies collected since 2019."))
    assert "Swiss" not in json.dumps(out) and "2019" not in json.dumps(out)
    assert out["summary"]["source"] == "rule"        # replaced by the counted sentence
    assert out["summary"]["value"] == xray.one_liner(XR)
    assert dropped >= 1


def test_brake_5_lets_a_grounded_sentence_through_verbatim():
    good = "Agencies listed with a telefon number and the agentur that owns it."
    out, dropped, _ = _v(_base(summary=good))
    assert out["summary"]["value"] == good
    assert out["summary"]["source"] == "model"
    assert dropped == 0


def test_brake_6_over_length_is_dropped_not_truncated():
    out, dropped, _ = _v(_base(summary="a " * 200))
    assert out["summary"]["source"] == "rule"
    assert len(out["summary"]["value"]) <= 240
    assert dropped >= 1


def test_brake_7_confidence_is_clamped_and_never_trusted():
    assert _v(_base(confidence="high"))[0]["confidence"] == 0.0
    assert _v(_base(confidence=4.2))[0]["confidence"] == 1.0
    assert _v(_base(confidence=-1))[0]["confidence"] == 0.0
    assert _v(_base(confidence=None))[0]["confidence"] == 0.0


def test_the_taxonomy_is_capped_cleaned_and_replaced_when_too_thin():
    cls = [{"id": "classify", "columns": ["agentur", "markt"], "confidence": 0.8}]
    eligible_classify = [e for e in XR["eligible"] if e["id"] == "classify"]
    cls[0]["columns"] = list(eligible_classify[0]["columns"])

    big = _v(_base(actions=cls, taxonomy_proposal=[f"V{i}" for i in range(60)]))[0]
    assert len(big["classify"]["taxonomy"]) == analyze.MAX_TAXONOMY

    longs = _v(_base(actions=cls, taxonomy_proposal=["CH", "D" * 30, "DE"]))[0]
    assert longs["classify"]["taxonomy"] == ["CH", "DE"]

    thin = _v(_base(actions=cls, taxonomy_proposal=["CH"]))[0]
    assert thin["classify"]["taxonomy_source"] == "rule"
    assert len(thin["classify"]["taxonomy"]) >= 2


def test_the_classify_target_is_slugged_and_never_shadows_a_source_column():
    cls = [{"id": "classify", "columns": list(
        [e for e in XR["eligible"] if e["id"] == "classify"][0]["columns"]),
        "confidence": 0.8}]
    out = _v(_base(actions=cls, classify_target="Markets!!",
                   taxonomy_proposal=["CH", "DE"]))[0]
    assert out["classify"]["to"] == "markets"

    clash = _v(_base(actions=cls, classify_target="agentur",
                     taxonomy_proposal=["CH", "DE"]))[0]
    assert clash["classify"]["to"] == "agentur_ai"


def test_validate_never_raises_whatever_the_model_returns():
    for junk in ({}, None, [], [1, 2, 3], "a string", 42,
                 {"columns": "not a list", "actions": {"nope": 1}},
                 {"columns": [None, 7, {"name": None}], "actions": [None, "x"]},
                 {"title": "🐺" * 50, "summary": "x" * 1_000_000},
                 {"nested": {"deep": {"deeper": [{"a": 1}] * 100}}}):
        out, dropped, note = analyze.validate(junk, XR, "gpt-oss:120b")
        assert out["title"]["value"] and out["columns"]
        assert isinstance(dropped, int) and isinstance(note, str)


def test_the_no_brain_path_is_a_complete_usable_analysis():
    analysis, stats = asyncio.run(analyze.analyze(XR, model="none"))
    assert stats == {"model": "none", "prompt_version": "", "tokens": 0,
                     "dropped": 0, "note": ""}
    assert analysis["title"]["source"] == "rule"
    assert analysis["summary"]["value"] == xray.one_liner(XR)
    for c in analysis["columns"].values():
        assert c["semantic"]["source"] == "rule"
        assert c["semantic"]["confidence"] == analyze.RULE_CONFIDENCE
    ids = {(a["id"], tuple(a["columns"])) for a in analysis["actions"]}
    assert ids == {(e["id"], tuple(e["columns"])) for e in XR["eligible"]}
    assert all(a["source"] == "rule" for a in analysis["actions"])


def test_only_the_profile_ever_leaves_the_box():
    """The screen promises 'never the sheet'. This is that promise, asserted."""
    payload = analyze.profile_payload(XR, ROWS)
    blob = json.dumps(payload, ensure_ascii=False)
    assert payload["row_count"] == 5
    assert len(payload["sample_rows"]) == analyze.SAMPLE_ROWS
    for col in payload["columns"]:
        assert len(col.get("samples", [])) <= analyze.SAMPLES_PER_COLUMN
    # The findings are full of numbers; sending them would let the model repeat
    # our arithmetic back as its own and quietly defeat the grounding check.
    for f in XR["findings"]:
        assert f["text"] not in blob


def test_a_busy_brain_degrades_to_rules_and_says_why(monkeypatch):
    """Principle 6, asserted: the AI is an enhancement, never a dependency."""
    class Boom:
        def __init__(self, *a, **kw): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return False
        async def post(self, *a, **kw): raise TimeoutError("the brain was busy")

    monkeypatch.setenv("OLLAMA_API_KEY", "test-key")
    monkeypatch.setattr(analyze.httpx, "AsyncClient", Boom)
    analysis, stats = asyncio.run(analyze.analyze(XR, model="gpt-oss:120b"))
    assert stats["model"] == "none" and stats["tokens"] == 0
    assert "TimeoutError" in stats["note"]              # loudly, not silently
    assert analysis["title"]["source"] == "rule"
    assert analysis["actions"] and analysis["columns"]  # the page is still complete


def test_no_api_key_is_a_stated_reason_not_a_crash(monkeypatch):
    monkeypatch.setenv("OLLAMA_API_KEY", "")
    analysis, stats = asyncio.run(analyze.analyze(XR, model="gpt-oss:120b"))
    assert stats["note"] == "no OLLAMA_API_KEY set — ran on rules alone"
    assert analysis["summary"]["value"] == xray.one_liner(XR)


def test_the_whole_transport_wires_up_against_a_stubbed_brain(monkeypatch):
    """One end-to-end pass with a model that answers well AND badly at once."""
    answer = {
        "title": "Agentur list", "summary": "A list of agentur and telefon values.",
        "list_kind": "call_list", "confidence": 0.86, "suggested_key": "Agenturen 2024",
        "columns": [{"name": "agentur", "semantic": "company_name",
                     "role": "", "confidence": 0.94},
                    {"name": "ghost", "semantic": "email", "confidence": 0.99}],
        "actions": [{"id": "dedupe", "columns": ["agentur"], "confidence": 0.4}],
        "row_count": 99999,
    }

    class Fake:
        def __init__(self, *a, **kw): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return False
        async def post(self, url, **kw):
            assert url.endswith("/api/chat")
            assert kw["headers"]["Authorization"] == "Bearer test-key"
            assert kw["json"]["options"]["temperature"] == 0
            body = json.dumps(kw["json"])
            assert "Havas" in body                    # samples go, sheets don't
            assert "eligible_actions" in body
            return types.SimpleNamespace(
                raise_for_status=lambda: None,
                json=lambda: {"message": {"content": json.dumps(answer)},
                              "prompt_eval_count": 3000, "eval_count": 140})

    monkeypatch.setenv("OLLAMA_API_KEY", "test-key")
    monkeypatch.setattr(analyze.httpx, "AsyncClient", Fake)
    analysis, stats = asyncio.run(analyze.analyze(XR, model="gpt-oss:120b", records=ROWS))

    assert stats["model"] == "gpt-oss:120b" and stats["tokens"] == 3140
    assert analysis["columns"]["agentur"]["semantic"]["source"] == "model"
    assert analysis["suggested_key"] == "agenturen-2024"
    assert "99999" not in json.dumps(analysis)          # brake 1
    assert "ghost" not in analysis["columns"]           # brake 3
    assert stats["dropped"] >= 1 and "dropped" in stats["note"]
