"""A hand-built .xlsx writer, for tests only.

Not a test module (no test_ prefix) — it's the fixture factory. We build the zip
by hand rather than adding openpyxl to the image for the sake of the test suite:
inbound.py reads .xlsx with the standard library, so the tests should be able to
*write* one the same way. Inline strings only, so there is no sharedStrings table
to keep in sync.
"""
import zipfile
from io import BytesIO
from xml.sax.saxutils import escape

_CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
{sheets}
</Types>"""

_RELS = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""

_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def _col(i: int) -> str:
    """0 -> A, 25 -> Z, 26 -> AA."""
    out = ""
    i += 1
    while i:
        i, rem = divmod(i - 1, 26)
        out = chr(65 + rem) + out
    return out


def _cell(ref: str, value) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, bool):
        value = int(value)
    if isinstance(value, (int, float)):
        return f'<c r="{ref}"><v>{value}</v></c>'
    return f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'


def _sheet(grid: list[list]) -> str:
    rows = []
    for r, row in enumerate(grid, start=1):
        cells = "".join(_cell(f"{_col(c)}{r}", v) for c, v in enumerate(row))
        rows.append(f'<row r="{r}">{cells}</row>')
    return (f'<?xml version="1.0" encoding="UTF-8"?>'
            f'<worksheet xmlns="{_NS}"><sheetData>{"".join(rows)}</sheetData></worksheet>')


def make_xlsx(rows, sheet_names=("Sheet1",)) -> bytes:
    """Grid (or list of grids, one per tab) -> .xlsx bytes.

    Row 1 is the header row, exactly as a real spreadsheet has it. Empty cells
    are *omitted* rather than written blank, because that is what Excel does and
    it is precisely the case that breaks a naive reader's column alignment."""
    grids = rows if (rows and rows[0] and isinstance(rows[0][0], list)) else [rows]
    while len(grids) < len(sheet_names):
        grids.append([["col"], ["value"]])

    overrides = "\n".join(
        f'<Override PartName="/xl/worksheets/sheet{i + 1}.xml" '
        f'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for i in range(len(sheet_names)))
    sheets_xml = "".join(
        f'<sheet name="{escape(n)}" sheetId="{i + 1}" r:id="rId{i + 1}"/>'
        for i, n in enumerate(sheet_names))

    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", _CONTENT_TYPES.format(sheets=overrides))
        z.writestr("_rels/.rels", _RELS)
        z.writestr("xl/workbook.xml",
                   f'<?xml version="1.0" encoding="UTF-8"?>'
                   f'<workbook xmlns="{_NS}" '
                   f'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                   f'<sheets>{sheets_xml}</sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels",
                   '<?xml version="1.0" encoding="UTF-8"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   + "".join(
                       f'<Relationship Id="rId{i + 1}" Type="http://schemas.openxmlformats.org/'
                       f'officeDocument/2006/relationships/worksheet" '
                       f'Target="worksheets/sheet{i + 1}.xml"/>'
                       for i in range(len(sheet_names)))
                   + "</Relationships>")
        for i, grid in enumerate(grids[:len(sheet_names)]):
            z.writestr(f"xl/worksheets/sheet{i + 1}.xml", _sheet(grid))
    return buf.getvalue()
