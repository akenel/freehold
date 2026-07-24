"""Freehold — inbound channels (the left-hand side of the service interface).

An integration has three parts: an **inbound channel**, a **mapping**, and an
**outbound schema**. business_hub.py wires the API channel. This module adds the
one that actually walks in the door of a twelve-person company: a spreadsheet.

The channel is deliberately dumb — read the rows, name the columns, hand them on.
All the judgement lives downstream in enrich.py, which is what makes the two
channels interchangeable: an API pull and an .xlsx upload produce the same list
of dicts, so they get the same enrichment, the same provenance and the same gate.

Parsed with the standard library (an .xlsx is a zip of XML) rather than pulling
in openpyxl — one less dependency in the image for a job this small.
"""
import re
import zipfile
from io import BytesIO
from xml.etree import ElementTree as ET

_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
_T = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"

# --- decompression limits (the zip-bomb brake) -----------------------------
# An .xlsx is a zip, and `ZipFile.read()` will happily inflate a few kilobytes
# of deflated nulls into gigabytes. The upload cap bounds the file ON DISK and
# says nothing about what it becomes in RAM, so the cap has to be applied again
# on the way out of the decompressor. One worker serves the whole app; an OOM
# here is the whole site, not one request.
#
# Sized against reality, not hope: a 5,000-row sheet with 40 text columns is a
# few MB of XML. 48 MiB for one member is roughly ten times the worst legitimate
# case we accept, and a file that genuinely needs more is one we cannot read
# anyway — read_xlsx stops at `limit` rows.
MAX_MEMBER = 48 * 1024 * 1024
MAX_TOTAL = 96 * 1024 * 1024
MAX_MEMBERS = 512          # a real workbook has tens of parts, not thousands


class TooBig(Exception):
    """Refuse to inflate. Caught by the callers and shown as "unreadable file"."""


def _read_capped(z: zipfile.ZipFile, name: str, cap: int = MAX_MEMBER) -> bytes:
    """Inflate one member, stopping the moment it exceeds `cap`.

    Reads in chunks rather than trusting the declared `file_size` in the zip
    header — that number is written by whoever made the file, so a bomb simply
    lies about it. We stop at the byte count we actually produced."""
    out = bytearray()
    with z.open(name) as fh:
        while True:
            chunk = fh.read(262144)
            if not chunk:
                break
            out.extend(chunk)
            if len(out) > cap:
                raise TooBig(f"{name} inflates past {cap} bytes")
    return bytes(out)


def _open(blob: bytes) -> zipfile.ZipFile:
    """Open the archive with the cheap structural checks done first."""
    z = zipfile.ZipFile(BytesIO(blob))
    infos = z.infolist()
    if len(infos) > MAX_MEMBERS:
        raise TooBig(f"{len(infos)} members")
    # The declared total is not trustworthy on its own, but a bomb that is honest
    # about its size can be refused before we decompress a single byte.
    if sum(i.file_size for i in infos) > MAX_TOTAL:
        raise TooBig("declared contents exceed the total cap")
    return z


def _col(ref: str) -> int:
    """'A' -> 0, 'Z' -> 25, 'AA' -> 26. Spreadsheets skip empty cells entirely,
    so we index by column letter or the rows come out misaligned."""
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group():
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _key(header: str, taken: set[str]) -> str:
    """Human header -> snake_case field name, de-duplicated.

    Real spreadsheets have two columns called 'PHONE' and 'phone'. We keep both
    (as phone and phone_2) rather than silently dropping one — two columns that
    claim the same fact is a *finding*, not a nuisance. See enrich.reconcile()."""
    base = re.sub(r"[^a-z0-9]+", "_", (header or "").strip().lower()).strip("_") or "col"
    name, i = base, 2
    while name in taken:
        name, i = f"{base}_{i}", i + 1
    taken.add(name)
    return name


def sheet_names(blob: bytes) -> list[str]:
    """The tabs, in workbook order — so a human can pick which one to import."""
    with _open(blob) as z:
        wb = ET.fromstring(_read_capped(z, "xl/workbook.xml", 4 * 1024 * 1024))
        return [s.get("name") for s in wb.iter(f"{{{_NS['m']}}}sheet")]


def read_xlsx(blob: bytes, sheet: int = 0, limit: int = 5000) -> tuple[list[str], list[dict]]:
    """Read one sheet into (field_names, records). Row 1 is the header row.

    Returns plain dicts of strings — no type guessing. Guessing types at the door
    is how a postcode becomes a float and a phone number loses its leading zero;
    if a value needs to become a number, that's the mapping's decision, not the
    reader's."""
    with _open(blob) as z:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(_read_capped(z, "xl/sharedStrings.xml"))
            shared = ["".join(t.text or "" for t in si.iter(_T))
                      for si in root.findall("m:si", _NS)]

        names = [n for n in z.namelist()
                 if re.match(r"xl/worksheets/sheet\d+\.xml$", n)]
        names.sort(key=lambda n: int(re.search(r"\d+", n.rsplit("/", 1)[1]).group()))
        root = ET.fromstring(_read_capped(z, names[sheet]))

        grid: list[list[str]] = []
        for row in root.iter(f"{{{_NS['m']}}}row"):
            cells: list[str] = []
            for c in row.findall("m:c", _NS):
                i = _col(c.get("r", "A1"))
                while len(cells) <= i:
                    cells.append("")
                t, v, inline = c.get("t"), c.find("m:v", _NS), c.find("m:is", _NS)
                if t == "s" and v is not None and v.text is not None:
                    cells[i] = shared[int(v.text)]
                elif inline is not None:
                    cells[i] = "".join(x.text or "" for x in inline.iter(_T))
                elif v is not None:
                    cells[i] = v.text or ""
            grid.append(cells)

    if not grid:
        return [], []

    taken: set[str] = set()
    fields = [_key(h, taken) for h in grid[0]]
    records = []
    for cells in grid[1:limit + 1]:
        rec = {f: (cells[i].strip() if i < len(cells) and cells[i] else "")
               for i, f in enumerate(fields)}
        if any(rec.values()):          # skip the blank rows every spreadsheet has
            records.append(rec)
    return fields, records
