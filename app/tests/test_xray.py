"""X-ray unit tests — the numbers, and the promise that a model never wrote one.

Pure and offline by construction: xray imports nothing but stdlib and enrich, so
these run on a laptop with no database, no MinIO and no API key. That is the
point — the deterministic half of the feature must be provable without the half
that can be unavailable.
"""
import re

import inbound
import xray
from tests._xlsx import make_xlsx


def _xr(fields, records, **kw):
    return xray.xray(fields, records, kw.get("filename", "t.xlsx"), kw.get("sheet", "Sheet1"))


def _rows(field, values):
    return [field], [{field: v} for v in values]


def test_the_xlsx_helper_round_trips_through_inbound():
    # If the fixture factory and the reader disagree, every other test lies.
    blob = make_xlsx([["Agentur", "Telefon"], ["Havas", "+41 44 668 18 00"]],
                     sheet_names=("Kontakte", "Notizen"))
    assert inbound.sheet_names(blob) == ["Kontakte", "Notizen"]
    fields, records = inbound.read_xlsx(blob)
    assert fields == ["agentur", "telefon"]
    assert records == [{"agentur": "Havas", "telefon": "+41 44 668 18 00"}]


def test_an_empty_sheet_does_not_crash():
    xr = _xr([], [])
    assert xr["row_count"] == 0 and xr["col_count"] == 0
    assert xr["findings"] == []
    assert xr["sha"]


def test_fill_counts_are_arithmetic():
    fields, records = _rows("a", ["x", "", "y", "", ""])
    c = _xr(fields, records)["columns"]["a"]
    assert (c["filled"], c["empty"], c["fill"]) == (2, 3, 0.4)


def test_a_unique_column_is_the_primary_key():
    fields, records = _rows("kundennr", ["K1", "K2", "K3", "K4"])
    c = _xr(fields, records)["columns"]["kundennr"]
    assert c["distinct"] == 4 and c["uniqueness"] == 1.0 and c["is_key"] is True


def test_constant_and_empty_columns_are_named_as_such():
    fields = ["region", "notiz"]
    records = [{"region": "Zürich", "notiz": ""} for _ in range(4)]
    cols = _xr(fields, records)["columns"]
    assert cols["region"]["is_constant"] is True and cols["region"]["is_key"] is False
    assert cols["notiz"]["is_empty"] is True and cols["notiz"]["filled"] == 0


def test_phone_column_is_recognised_from_messy_real_strings():
    fields, records = _rows("telefon", [
        "+41 44 668 18 00", "0041 44 668 18 01", "+31 (0) 20 890 8064",
        "1-770-736-8031 x56442", "(254)954-1289", "+44 207 549 4040",
        "+49 30 1234567", "+1 202 555 0148",
    ])
    c = _xr(fields, records)["columns"]["telefon"]
    assert c["rule_type"] == "phone"
    assert c["type_votes"]["phone"] == 1.0


def test_the_other_shape_voters():
    for values, expect in (
        (["a@b.ch", "c@d.com", "e@f.org"], "email"),
        (["www.havas.ch", "https://dentsu.com/ch", "serviceplan.de"], "url"),
        ([45231, 45232, 45233], "excel_serial"),
        (["8001", "3011", "1201"], "postcode"),
        (["2024-11-08", "2011-03-14", "2019-01-02"], "date"),
        (["CHF 1'240.00", "CHF 90.50", "CHF 12.00"], "money"),
        (["ja", "nein", "ja"], "boolean"),
        (["ask Marc", "do not call", "left a message"], "free_text"),
    ):
        fields, records = _rows("c", [str(v) for v in values])
        assert _xr(fields, records)["columns"]["c"]["rule_type"] == expect, values


def test_phone_multi_counts_only_the_ambiguous_cells():
    messy = "+31 20 -NL Tel: +31 (0)207 975 000 or +44 207 549 4040)"
    fields, records = _rows("telefon", ["+41 44 668 18 00", messy, messy, ""])
    c = _xr(fields, records)["columns"]["telefon"]
    assert c["phone_multi"] == 2
    assert len(xray.enrich.candidates(messy)) == 2      # the rule, not our arithmetic


def test_multivalue_picks_the_dominant_separator_and_declines_otherwise():
    fields, records = _rows("markt", ["CH / DE", "CH / DE / AT", "FR / IT", "CH / DE"])
    mv = _xr(fields, records)["columns"]["markt"]["multivalue"]
    assert mv["sep"] == "/" and mv["cells"] == 4 and mv["mean_per_cell"] > 1.2

    fields, records = _rows("markt", ["CH", "DE", "AT / FR", "IT"])
    assert _xr(fields, records)["columns"]["markt"]["multivalue"] is None


def test_case_variants_cluster_the_same_word_and_nothing_else():
    fields, records = _rows("status", ["Active", "active", "ACTIVE", "N/A", "n/a", "Closed"])
    cv = _xr(fields, records)["columns"]["status"]["case_variants"]
    assert sorted(sorted(g) for g in cv) == [["ACTIVE", "Active", "active"], ["N/A", "n/a"]]


def test_invisible_whitespace_is_counted():
    fields = ["agentur"]
    # a non-breaking space is invisible in Excel and matches nothing in a lookup
    records = [{"agentur": " Havas "}, {"agentur": "Dentsu\u00a0CH"}, {"agentur": "Ok"}]
    c = _xr(fields, records)["columns"]["agentur"]
    assert c["whitespace_dirty"] == 1 and c["nbsp"] == 1


def test_exact_duplicate_rows_counts_the_copies_not_the_originals():
    fields = ["a", "b"]
    records = [{"a": "1", "b": "x"}] * 3 + [{"a": "2", "b": "y"}]
    assert _xr(fields, records)["exact_duplicate_rows"] == 2


def test_trailer_rows_are_a_tail_phenomenon():
    fields = ["a", "b"]
    records = ([{"a": "1", "b": "x"}, {"a": "2", "b": ""}, {"a": "3", "b": "z"}]
               + [{"a": "TOTAL", "b": ""}, {"a": "9", "b": ""}])
    xr = _xr(fields, records)
    assert xr["trailer_rows"] == [4, 5]          # the sparse row 2 is data, not a footer


def test_header_smell_reports_duplicates_and_missing_headers():
    # Two columns called Phone, and a third whose header somebody blanked out.
    blob = make_xlsx([["Phone", "phone", " "], ["a", "b", "c"]])
    fields, records = inbound.read_xlsx(blob)
    smell = " ".join(_xr(fields, records)["header_smell"])
    assert "phone_2" in smell and "no header" in smell


def test_cross_finds_phone_pairs_only_when_there_are_two():
    fields = ["telefon", "telefon_2", "agentur"]
    records = [{"telefon": "+41 44 668 18 00", "telefon_2": "+41 44 668 18 01",
                "agentur": "Havas"}]
    assert _xr(fields, records)["cross"]["phone_pairs"] == [["telefon", "telefon_2"]]

    one = _xr(["telefon"], [{"telefon": "+41 44 668 18 00"}])
    assert one["cross"]["phone_pairs"] == []


def test_cross_counts_duplicate_keys_and_their_groups():
    fields = ["email"]
    records = [{"email": e} for e in
               ["a@x.ch", "a@x.ch", "a@x.ch", "b@x.ch", "b@x.ch",
                "c@x.ch", "d@x.ch", "e@x.ch", "f@x.ch", "g@x.ch"]]
    assert _xr(fields, records)["cross"]["dupe_keys"] == [
        {"column": "email", "dupes": 3, "groups": 2}]


def test_every_number_in_every_finding_was_counted_from_the_cells():
    """The anti-drift assertion: a finding may not contain a number that isn't
    in the deterministic stats. This is the test that stops somebody 'improving'
    a finding by adding a percentage the code never computed."""
    fields = ["agentur", "telefon", "email", "status", "erfasst", "leer"]
    records = [{"agentur": f"A{i}", "telefon": "+41 44 668 18 0" + str(i % 10),
                "email": "a@x.ch" if i % 2 else f"b{i}@x.ch",
                "status": ["Active", "active", "ACTIVE"][i % 3],
                "erfasst": str(45000 + i), "leer": ""} for i in range(12)]
    xr = _xr(fields, records)
    assert xr["findings"]

    allowed_ints, allowed_strs = set(), set()

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k != "findings":
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
        elif isinstance(node, bool):
            pass
        elif isinstance(node, int):
            allowed_ints.add(node)
        elif isinstance(node, float):
            allowed_ints.add(int(node * 100))
            allowed_strs.add(str(node))
        elif isinstance(node, str):
            allowed_strs.add(node)

    walk(xr)
    for f in xr["findings"]:
        assert set(f) == {"code", "column", "text", "severity"}
        assert f["severity"] in ("info", "warn")
        for tok in re.findall(r"\d+(?:\.\d+)?", f["text"]):
            ok = (("." not in tok and int(tok) in allowed_ints)
                  or tok in allowed_strs
                  or any(tok in s for s in allowed_strs))
            assert ok, f"{tok!r} in {f['text']!r} was never counted"


def test_eligible_offers_only_what_the_cells_licence():
    fields = ["agentur", "telefon", "markt"]
    records = [{"agentur": f"A{i}", "telefon": "+41 44 668 18 0" + str(i % 10),
                "markt": "CH / DE"} for i in range(6)]
    ids = [e["id"] for e in _xr(fields, records)["eligible"]]
    assert "score_quality" in ids and "build_schema" in ids          # always
    assert "normalize_phone" in ids and "split_multivalue" in ids

    plain = _xr(["note"], [{"note": "hello"}])
    plain_ids = [e["id"] for e in plain["eligible"]]
    assert "normalize_phone" not in plain_ids
    assert "split_multivalue" not in plain_ids
    assert "score_quality" in plain_ids and "build_schema" in plain_ids
    for e in plain["eligible"]:
        assert set(e) == {"id", "columns", "reason", "strength"}
        assert 0.0 <= e["strength"] <= 1.0


def test_the_sha_is_stable_and_moves_on_a_one_cell_change():
    fields = ["a"]
    a = _xr(fields, [{"a": "1"}, {"a": "2"}])
    b = _xr(fields, [{"a": "1"}, {"a": "2"}])
    c = _xr(fields, [{"a": "1"}, {"a": "3"}])
    assert a["sha"] == b["sha"] and a["sha"] != c["sha"]


def test_the_no_brain_one_liner_is_computed():
    fields, records = _rows("email", ["a@b.ch", "c@d.ch"])
    assert xray.one_liner(_xr(fields, records)) == "2 rows, 1 columns; 1 of them look like email."
