"""Freehold — outbound formats. The right-hand side of the service interface.

A report is stored as JSON because JSON is the honest wire format. But nobody
asked for their customer list back as JSON — they asked for it back *cleaned*, in
the shape they sent it. xlsx in, xlsx out. So this turns one stored report into
whatever a human actually wants to open:

    xlsx   a real workbook: frozen bold header, autofilter, a coloured Gate
           column, the enriched values folded in, and two extra tabs — the review
           queue on its own, and the run's provenance. This is the deliverable.
    csv    the same grid, flat, for the system on the other end that wants a feed.
    json   the raw report, untouched — for diffing and re-import.

The rule the user asked for: **default to the format they gave us.** A spreadsheet
came in, a spreadsheet goes out. The reader (inbound.py) is stdlib and paranoid
because it parses untrusted files; the writer here is openpyxl because we control
every byte it writes — there is no bomb to build out of our own records.
"""
import csv
import io
import json

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

# One value per cell for the flat exports: the enriched fields carry a whole
# provenance envelope, but a spreadsheet cell wants the answer, not the paperwork.
_GATE_FILL = {
    "auto": "C7EBD1",       # green — applied
    "review": "F6E2B8",     # amber — a human should look
    "rejected": "F5C6C6",   # red — held back
}
_HEAD_FILL = "2C3E50"
_HEAD_FONT = "FFFFFF"


def _cell_value(v):
    """Flatten one enriched value to something a cell can hold.

    quality -> its score; reconcile -> its status; everything else -> as-is. The
    detail (what was missing, which numbers disagreed) is a column of its own."""
    if isinstance(v, dict):
        if "score" in v:
            return v["score"]
        if "status" in v:
            return v["status"]
        return json.dumps(v, ensure_ascii=False)
    return v


def _detail(v):
    """The human note that goes beside a flattened value, or ""."""
    if isinstance(v, dict):
        if "missing" in v and v.get("missing"):
            return "missing: " + ", ".join(v["missing"])
        if "status" in v:
            bits = []
            for k, nums in v.items():
                if isinstance(nums, list) and nums:
                    bits.append(f"{k}: {', '.join(nums)}")
            return " | ".join(bits)
    return ""


def _grid(report: dict) -> tuple[list[str], list[dict], list[str]]:
    """(header, rows, enriched-field-names) — the shared shape all formats render.

    Source columns first, in sheet order, then one column per enriched field, then
    Gate. Every record contributes; paging is a preview concern, not an export one."""
    meta = report.get("meta", {})
    records = report.get("records", [])
    source = list(meta.get("columns") or [])
    enriched: list[str] = []
    for r in records:
        for k in r:
            if not k.startswith("_") and k not in source:
                source.append(k)
        for k in (r.get("_enriched") or {}):
            if k not in enriched:
                enriched.append(k)

    header = list(source) + [f"✦ {e}" for e in enriched] + ["Gate"]
    rows = []
    for r in records:
        row = {c: r.get(c, "") for c in source}
        for e in enriched:
            env = (r.get("_enriched") or {}).get(e)
            if env is None:
                row[f"✦ {e}"] = ""
                continue
            val = _cell_value(env.get("value"))
            note = _detail(env.get("value"))
            row[f"✦ {e}"] = f"{val}  ({note})" if note else val
        row["Gate"] = r.get("_gate", "")
        rows.append(row)
    return header, rows, enriched


# --- csv -------------------------------------------------------------------
def to_csv(report: dict) -> bytes:
    header, rows, _ = _grid(report)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, extrasaction="ignore")
    w.writeheader()
    for row in rows:
        w.writerow(row)
    return buf.getvalue().encode("utf-8-sig")   # BOM so Excel opens UTF-8 cleanly


# --- json ------------------------------------------------------------------
def to_json(report: dict) -> bytes:
    return json.dumps(report, indent=2, ensure_ascii=False).encode("utf-8")


# --- xlsx ------------------------------------------------------------------
def _write_sheet(ws, header, rows):
    head_fill = PatternFill("solid", fgColor=_HEAD_FILL)
    head_font = Font(bold=True, color=_HEAD_FONT)
    gate_fills = {g: PatternFill("solid", fgColor=c) for g, c in _GATE_FILL.items()}
    gate_col = header.index("Gate") + 1 if "Gate" in header else 0

    for j, name in enumerate(header, start=1):
        c = ws.cell(row=1, column=j, value=name)
        c.fill, c.font = head_fill, head_font
        c.alignment = Alignment(vertical="center")

    widths = [max(10, min(48, len(str(h)) + 2)) for h in header]
    for i, row in enumerate(rows, start=2):
        for j, name in enumerate(header, start=1):
            val = row.get(name, "")
            ws.cell(row=i, column=j, value=val)
            widths[j - 1] = max(widths[j - 1], min(48, len(str(val)) + 2))
        if gate_col:
            fill = gate_fills.get(row.get("Gate"))
            if fill:
                ws.cell(row=i, column=gate_col).fill = fill

    for j, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(j)].width = w

    ws.freeze_panes = "A2"                                  # header stays put
    if rows:
        ws.auto_filter.ref = f"A1:{get_column_letter(len(header))}{len(rows) + 1}"


def to_xlsx(report: dict) -> bytes:
    """The deliverable: a workbook better than the one that came in."""
    header, rows, _ = _grid(report)
    meta = report.get("meta", {})
    wb = Workbook()

    ws = wb.active
    ws.title = "Cleaned"
    _write_sheet(ws, header, rows)

    # The review queue on its own tab — the rows a human actually has to touch,
    # which is the whole point of the gate. Empty tab if the run was all-green.
    review = [r for r in rows if r.get("Gate") == "review"]
    rq = wb.create_sheet("Needs review")
    if review:
        _write_sheet(rq, header, review)
    else:
        rq["A1"] = "Nothing needed review — every row cleared the gate."

    # Provenance, so the file stands alone once it leaves the box.
    info = wb.create_sheet("How this was made")
    facts = [
        ("Source", meta.get("source", "")),
        ("Run at", meta.get("run_at", "")),
        ("Run by", meta.get("run_by", "")),
        ("Records", meta.get("count", "")),
        ("Brain", meta.get("model", "none")),
        ("Prompt version", meta.get("prompt_version", "")),
        ("AI-written rows", meta.get("enriched_count", 0)),
        ("Tokens", meta.get("tokens", 0)),
        ("Needs review", meta.get("review_count", 0)),
        ("", ""),
        ("Findings", ""),
    ]
    for f in meta.get("findings", []):
        facts.append(("", f.get("text", "")))
    info.column_dimensions["A"].width = 18
    info.column_dimensions["B"].width = 90
    for i, (k, v) in enumerate(facts, start=1):
        info.cell(row=i, column=1, value=k).font = Font(bold=True)
        info.cell(row=i, column=2, value=v).alignment = Alignment(wrap_text=True)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# --- dispatch --------------------------------------------------------------
FORMATS = {
    "xlsx": (to_xlsx, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    "csv": (to_csv, "text/csv; charset=utf-8"),
    "json": (to_json, "application/json"),
}


def default_format(report: dict) -> str:
    """Give them back what they gave us. A spreadsheet came in → a spreadsheet
    goes out. Only the API-channel demo (no uploaded file) defaults to json."""
    return "xlsx" if report.get("meta", {}).get("channel") in ("spreadsheet", "list") else "json"


def render(report: dict, fmt: str) -> tuple[bytes, str]:
    fn, mime = FORMATS[fmt]
    return fn(report), mime
