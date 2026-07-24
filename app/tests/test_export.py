"""Outbound formats — the deliverable actually opens, and says the right thing.

The xlsx is round-tripped through inbound.read_xlsx (our own paranoid reader), so
"it produced a workbook" means "a workbook that parses", not "some bytes".
"""
import csv
import io
import json

import export
import inbound

REPORT = {
    "meta": {
        "source": "SAP_Call_Campaign.xlsx", "channel": "list", "count": 3,
        "model": "gpt-oss:120b", "prompt_version": "v1", "enriched_count": 1,
        "tokens": 842, "review_count": 1,
        "columns": ["agency", "phone"],
        "findings": [{"text": "'phone' holds more than one number in 1 of 3 cells."}],
    },
    "records": [
        {"agency": "Eursap NL", "phone": "+31 20 890 8064", "_label": "Eursap NL",
         "_gate": "auto", "_enriched": {
             "phone_e164": {"value": "+31208908064", "original": "+31 20 890 8064",
                            "source": "rule", "model": "", "confidence": 1.0},
             "quality": {"value": {"score": 1.0, "missing": []}, "original": None,
                         "source": "rule", "model": "", "confidence": 1.0}}},
        {"agency": "Deckow", "phone": "call us", "_label": "Deckow",
         "_gate": "review", "_enriched": {
             "industry": {"value": "Logistics", "original": "Deckow", "source": "model",
                          "model": "gpt-oss:120b", "confidence": 0.61}}},
        {"agency": "PROGRESS", "phone": "", "_label": "—",
         "_gate": "review", "_enriched": {
             "quality": {"value": {"score": 0.12, "missing": ["phone"]}, "original": None,
                         "source": "rule", "model": "", "confidence": 1.0}}},
    ],
}


def test_default_format_echoes_the_inbound_channel():
    assert export.default_format(REPORT) == "xlsx"                       # a sheet came in
    assert export.default_format({"meta": {"channel": "spreadsheet"}}) == "xlsx"
    assert export.default_format({"meta": {}}) == "json"                 # the API demo


def test_csv_has_a_header_a_gate_column_and_every_row():
    raw = export.to_csv(REPORT).decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(raw)))
    assert len(rows) == 3
    assert "Gate" in rows[0] and rows[0]["Gate"] == "auto"
    assert rows[0]["agency"] == "Eursap NL"
    assert "+31208908064" in rows[0]["✦ phone_e164"]


def test_json_is_the_report_verbatim():
    back = json.loads(export.to_json(REPORT))
    assert back == REPORT


def test_xlsx_opens_and_carries_the_cleaned_grid_plus_the_extra_tabs():
    blob = export.to_xlsx(REPORT)
    # our own reader parses it → it is a real workbook, not just bytes
    assert inbound.sheet_names(blob) == ["Cleaned", "Needs review", "How this was made"]
    fields, records = inbound.read_xlsx(blob)          # first sheet
    assert "agency" in fields and "gate" in fields
    assert len(records) == 3
    assert records[0]["agency"] == "Eursap NL"
    assert records[0]["gate"] == "auto"
    # the enriched value made it into a cell (header carries the ✦ marker)
    assert any("phone_e164" in f for f in fields)


def test_the_review_tab_holds_only_the_rows_a_human_must_touch():
    blob = export.to_xlsx(REPORT)
    _fields, review = inbound.read_xlsx(blob, sheet=1)   # "Needs review"
    labels = {r.get("agency") for r in review}
    assert "Deckow" in labels and "PROGRESS" in labels
    assert "Eursap NL" not in labels                     # it was applied, not reviewed


def test_render_dispatch_matches_the_mime():
    for fmt, mime_needle in (("xlsx", "spreadsheetml"), ("csv", "text/csv"),
                             ("json", "application/json")):
        blob, mime = export.render(REPORT, fmt)
        assert mime_needle in mime and blob
