"""The zip-bomb brake.

An .xlsx is a zip, and the upload cap bounds the file on disk while saying
nothing about what it becomes in RAM. One uvicorn worker serves the whole app,
so an OOM here is the site, not a request. These build real bombs — no mocks —
and assert we refuse them without inflating.
"""
import io
import zipfile

import pytest

import inbound

SHEET = (b'<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/'
         b'spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="inlineStr">'
         b'<is><t>name</t></is></c></row></sheetData></worksheet>')
WB = (b'<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/'
      b'spreadsheetml/2006/main"><sheets><sheet name="Bomb" sheetId="1"/></sheets></workbook>')


def _zip(members: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in members.items():
            z.writestr(name, data)
    return buf.getvalue()


def test_a_shared_strings_bomb_is_refused_not_inflated():
    # ~200 MB of nulls compresses to a couple of hundred KB. Before the cap this
    # was a straight `z.read()` into RAM.
    bomb = _zip({"xl/workbook.xml": WB,
                 "xl/worksheets/sheet1.xml": SHEET,
                 "xl/sharedStrings.xml": b"\0" * (200 * 1024 * 1024)})
    assert len(bomb) < 1024 * 1024, "the bomb itself must be small — that's the point"
    with pytest.raises(inbound.TooBig):
        inbound.read_xlsx(bomb)


def test_a_worksheet_bomb_is_refused_too():
    bomb = _zip({"xl/workbook.xml": WB,
                 "xl/worksheets/sheet1.xml": b"\0" * (200 * 1024 * 1024)})
    with pytest.raises(inbound.TooBig):
        inbound.read_xlsx(bomb)


def test_an_archive_with_absurdly_many_members_is_refused():
    many = {f"xl/junk{i}.xml": b"x" for i in range(inbound.MAX_MEMBERS + 5)}
    many["xl/workbook.xml"] = WB
    many["xl/worksheets/sheet1.xml"] = SHEET
    with pytest.raises(inbound.TooBig):
        inbound.read_xlsx(_zip(many))


def test_sheet_names_is_bounded_as_well():
    # The tab picker reads workbook.xml before anything else touches the file.
    bomb = _zip({"xl/workbook.xml": b"\0" * (200 * 1024 * 1024),
                 "xl/worksheets/sheet1.xml": SHEET})
    with pytest.raises(inbound.TooBig):
        inbound.sheet_names(bomb)


def test_an_ordinary_workbook_still_reads():
    """The brake must not be a wall. A normal file goes through untouched."""
    rows = "".join(
        f'<row r="{r}">'
        f'<c r="A{r}" t="inlineStr"><is><t>Agency {r}</t></is></c>'
        f'<c r="B{r}" t="inlineStr"><is><t>+41 44 668 18 0{r % 10}</t></is></c>'
        "</row>"
        for r in range(2, 202))
    sheet = ('<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/'
             'spreadsheetml/2006/main"><sheetData>'
             '<row r="1"><c r="A1" t="inlineStr"><is><t>Agency</t></is></c>'
             '<c r="B1" t="inlineStr"><is><t>Phone</t></is></c></row>'
             f"{rows}</sheetData></worksheet>").encode()
    ok = _zip({"xl/workbook.xml": WB, "xl/worksheets/sheet1.xml": sheet})
    fields, records = inbound.read_xlsx(ok)
    assert fields == ["agency", "phone"]
    assert len(records) == 200
    assert records[0]["agency"] == "Agency 2"
    assert inbound.sheet_names(ok) == ["Bomb"]
