"""Freehold — the X-ray: what is actually in this list, counted not guessed.

Every list a small company owns is a table that never got a schema. Twenty years
of rows, a header row somebody typed once, and nobody left who remembers what
column G means. This module reads such a list and produces the *profile*: how
full each column is, how many distinct values it holds, what shape those values
are, which two columns claim the same fact, and which rows are the same thing
twice.

The one rule here, and it is the reason the whole feature is credible:

    **no model may touch this file.**

Every number that ends up on the draft screen comes from counting cells. A model
is allowed to *name* things later — "this column is a company name" — but it is
never allowed to say how many, how often, or from when. A model that invents
"480 Swiss agencies collected since 2019" out of a filename is the single most
expensive failure mode in this product; the defence is not a better prompt, it is
that the number never came from the model in the first place.

It also emits `eligible`: the licence list. An action is offered only because a
deterministic trigger fired on the cells. analyze.validate() then refuses any
action the model proposes that is not on this list — so the brain can rank,
justify and drop suggestions, but it can never conjure one.

Pure: no I/O, no DB, no network, no clock. Same bytes in, same dict out — which
is what makes `sha` meaningful and what lets "same mapping, different brain" be
an honest comparison.
"""
import hashlib
import json
import re
from collections import Counter
from datetime import date, timedelta

import enrich

# --- the action ids, mirrored ---------------------------------------------
# actions.ACTIONS is the authority for the catalogue; these strings are the
# triggers' half of the contract. actions.eligible() filters anything we emit
# that isn't in the catalogue, so the two files can never silently disagree.
NORMALIZE_PHONE = "normalize_phone"
RECONCILE_PHONES = "reconcile_phones"
SCORE_QUALITY = "score_quality"
CLASSIFY = "classify"
CANONICALIZE_VALUES = "canonicalize_values"
PARSE_DATES = "parse_dates"
SPLIT_MULTIVALUE = "split_multivalue"
VALIDATE_EMAIL = "validate_email"
DEDUPE = "dedupe"
BUILD_SCHEMA = "build_schema"

PHONE_VOTE_FLOOR = 0.20      # a column only has to be *partly* phone-shaped
MULTIVALUE_MEAN = 1.2        # below this, a stray slash isn't a list
MULTIVALUE_SHARE = 0.30      # ...and it has to be common, not one weird row
MULTIVALUE_PART = 24         # ...and the pieces have to be VALUES, not sentences
SEPARATORS = ("/", ";", ",", "|", " · ")
CASE_VARIANT_CEILING = 40    # clustering 30k free-text values proves nothing
# A URL is full of slashes and an address is full of commas. Splitting either one
# produces confident nonsense — https://havas.ch/about is not four markets.
NOT_MULTIVALUE = ("url", "email", "phone")
# What may be offered as a duplicate key. A category column repeats by design:
# "10 rows repeat a market" is not a finding, it is what a market column IS.
# An email or a website that repeats is the same customer entered twice.
DUPE_UNIQUENESS = 0.90       # near-unique columns are identifiers whatever they hold
DUPE_TYPES = ("email", "phone", "url")

# --- value shape voters ----------------------------------------------------
_RE_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
_RE_URL = re.compile(r"^(https?://)?[\w.-]+\.[A-Za-z]{2,}(/\S*)?$")
_RE_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})")
_RE_DMY = re.compile(r"^(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})$")
_RE_MONEY = re.compile(r"^[€$£CHF ]*-?[\d'’., ]+$")
_RE_2DP = re.compile(r"[.,]\d{2}$")
_RE_POSTCODE = re.compile(r"^\d{4,5}$")
# 0/1 are booleans only if the WHOLE column is 0/1. Per cell they are numbers —
# otherwise a priority column of 1,2,3 votes 64% boolean and gets typed BOOLEAN,
# which is how a schema ends up lying about a customer's data.
_WORD_BOOLEANS = {"true", "false", "yes", "no", "ja", "nein", "y", "n", "x"}
_BOOLEANS = _WORD_BOOLEANS | {"0", "1", ""}
_CURRENCY = ("€", "$", "£", "CHF", "chf")

# Excel counts days from 1900-01-01 *and* believes 1900 was a leap year, which
# it wasn't. Anchoring at 1899-12-30 absorbs both off-by-ones at once — the
# standard fix, and the reason a naive "1900-01-01 + n" is two days wrong.
_EXCEL_EPOCH = date(1899, 12, 30)
_SERIAL_LO, _SERIAL_HI = 20000, 60000     # 1954 → 2064; outside that it's just a number


def _is_serial(v: str) -> bool:
    try:
        n = float(v)
    except (TypeError, ValueError):
        return False
    return n == int(n) and _SERIAL_LO <= n <= _SERIAL_HI


def _num(v: str) -> float | None:
    """Best-effort number out of a spreadsheet cell. Handles 1'234.50, 1 234,50,
    CHF 1,234.50 — the four ways a Swiss office writes the same amount."""
    s = str(v).strip()
    for tok in _CURRENCY:
        s = s.replace(tok, "")
    s = s.replace("'", "").replace("\u2019", "").replace("\u00a0", "").replace(" ", "")
    if s.count(",") and s.count("."):
        s = s.replace(",", "") if s.rfind(".") > s.rfind(",") else s.replace(".", "").replace(",", ".")
    elif s.count(",") == 1:
        s = s.replace(",", "") if re.search(r",\d{3}$", s) else s.replace(",", ".")
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def iso_from(raw: str, order: str = "auto") -> tuple[str, str]:
    """One cell → (iso_date, status). status is ok | ambiguous | unparsed.

    `order` is "dmy", "mdy", "excel_serial", "iso" or "auto". The interesting
    case is 03/04/2024: that is the 3rd of April in Zürich and the 4th of March
    in Denver, and *there is no way to tell from the cell*. We return
    "ambiguous" and leave the value alone. Guessing here silently shifts a third
    of a customer's dates by up to eleven months, and nobody ever notices."""
    s = str(raw or "").strip()
    if not s:
        return "", "unparsed"
    if order in ("auto", "excel_serial") and _is_serial(s):
        return (_EXCEL_EPOCH + timedelta(days=int(float(s)))).isoformat(), "ok"
    m = _RE_ISO.match(s)
    if m and order in ("auto", "iso"):
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat(), "ok"
        except ValueError:
            return "", "unparsed"
    m = _RE_DMY.match(s)
    if m:
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        y += 2000 if y < 70 else (1900 if y < 100 else 0)
        if order == "dmy" or (order == "auto" and a > 12 and b <= 12):
            d, mo = a, b
        elif order == "mdy" or (order == "auto" and b > 12 and a <= 12):
            d, mo = b, a
        elif a > 12 and b > 12:
            return "", "unparsed"
        else:
            return "", "ambiguous"
        try:
            return date(y, mo, d).isoformat(), "ok"
        except ValueError:
            return "", "unparsed"
    return "", "unparsed"


def date_order(values: list[str]) -> str:
    """Which way round a whole column writes its dates, decided by evidence.

    A single "03/04/2024" is unknowable. A *column* usually isn't: as soon as one
    row says 25/12/2023, the column is day-first and every other row in it can be
    read with confidence. That is inference from the customer's own cells, not a
    guess about their nationality — and if the column contains both 25/12 and
    12/25 we go back to declining, because then it really is a mess."""
    dmy = mdy = False
    for v in values:
        m = _RE_DMY.match(str(v or "").strip())
        if not m:
            continue
        a, b = int(m.group(1)), int(m.group(2))
        if a > 12 and b <= 12:
            dmy = True
        elif b > 12 and a <= 12:
            mdy = True
    if dmy and not mdy:
        return "dmy"
    if mdy and not dmy:
        return "mdy"
    return "auto"


def _vote(v: str) -> str:
    """One cell, one vote, most specific test first.

    Order matters more than it looks: `float()` succeeds on "8001", so if the
    generic number test ran before the postcode test, no column would ever be a
    postcode. Same for booleans written as 0/1. The specific voters go first.
    """
    if _RE_EMAIL.match(v):
        return "email"
    if enrich.candidates(v):
        return "phone"
    if _RE_URL.match(v):
        return "url"
    if _is_serial(v):
        return "excel_serial"
    if _RE_ISO.match(v) or _RE_DMY.match(v):
        return "date"
    if _RE_MONEY.match(v) and (any(t in v for t in _CURRENCY) or _RE_2DP.search(v)):
        return "money"
    if _RE_POSTCODE.match(v):
        return "postcode"
    if v.casefold() in _WORD_BOOLEANS:
        return "boolean"
    if _num(v) is not None and re.search(r"\d", v):
        return "number"
    return "free_text"


def _cluster_key(v: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", v.casefold())


def _column(field: str, index: int, values: list[str], row_count: int) -> dict:
    """Everything we can say about one column without asking anyone."""
    filled = [v for v in values if v.strip()]
    n = len(filled)
    counts = Counter(filled)
    distinct = len(counts)

    votes: Counter = Counter(_vote(v) for v in filled)
    type_votes = {k: round(c / n, 2) for k, c in votes.most_common()} if n else {}
    rule_type = ""
    if type_votes:
        best, share = votes.most_common(1)[0]
        rule_type = best if share / n >= 0.50 else ""
    # A flag column is a column where EVERY value is a flag — decided once for the
    # column, not voted on cell by cell. See the note on _WORD_BOOLEANS.
    if n and all(v.casefold() in _BOOLEANS for v in filled):
        rule_type = "boolean"

    col = {
        "header": field,          # the raw header is gone: inbound.read_xlsx snake_cases it
        "index": index,
        "filled": n,
        "empty": len(values) - n,
        "fill": round(n / row_count, 2) if row_count else 0.0,
        "distinct": distinct,
        "uniqueness": round(distinct / n, 2) if n else 0.0,
        "is_key": bool(n) and distinct == n and (n / row_count if row_count else 0) >= 0.99,
        "is_constant": distinct == 1 and n > 0,
        "is_empty": n == 0,
        "min_len": min((len(v) for v in filled), default=0),
        "max_len": max((len(v) for v in filled), default=0),
        "top": [[v, c] for v, c in counts.most_common(5)],
        "type_votes": type_votes,
        "rule_type": rule_type,
        # inbound.read_xlsx() already .strip()s every cell, so this is 0 for the
        # spreadsheet channel. It is kept because the API channel doesn't strip,
        # and a trailing space in a lookup key is invisible and fatal.
        "whitespace_dirty": sum(1 for v in values if v != v.strip()),
        "nbsp": sum(1 for v in values if "\u00a0" in v),
        "phone_multi": sum(1 for v in filled if len(enrich.candidates(v)) > 1),
        "multivalue": None,
        "case_variants": [],
        "date_range": None,
        "numeric": None,
    }

    for sep in (() if rule_type in NOT_MULTIVALUE else SEPARATORS):
        hits = [v for v in filled if sep in v]
        if not hits or len(hits) / n < MULTIVALUE_SHARE:
            continue
        parts = [p.strip() for v in filled for p in v.split(sep) if p.strip()]
        mean = round(len(parts) / n, 2)
        # The length test is what separates a list from a sentence: "CH / DE / AT"
        # splits into values, "Call Marc, he owns the budget" splits into prose.
        if mean > MULTIVALUE_MEAN and parts and \
                sum(len(p) for p in parts) / len(parts) <= MULTIVALUE_PART:
            col["multivalue"] = {"sep": sep, "mean_per_cell": mean, "cells": len(hits)}
            break

    if 0 < distinct <= CASE_VARIANT_CEILING:
        groups: dict[str, list[str]] = {}
        for v, _c in counts.most_common():
            groups.setdefault(_cluster_key(v), []).append(v)
        col["case_variants"] = [g for g in groups.values() if len(g) > 1]

    if rule_type in ("date", "excel_serial"):
        order = date_order(filled)
        isos = sorted(i for i, st in (iso_from(v, order) for v in filled) if st == "ok")
        if isos:
            col["date_range"] = [isos[0], isos[-1]]
            col["date_parsed"] = len(isos)

    if rule_type in ("number", "money"):
        nums = [x for x in (_num(v) for v in filled) if x is not None]
        if nums:
            col["numeric"] = {
                "sum": round(sum(nums), 2), "min": min(nums), "max": max(nums),
                "mean": round(sum(nums) / len(nums), 2),
            }
    return col


def _cross(fields: list[str], records: list[dict], cols: dict, row_count: int) -> dict:
    """Facts that live between columns, not inside one."""
    phones = [f for f in fields if cols[f]["type_votes"].get("phone", 0) >= PHONE_VOTE_FLOOR]
    pairs = [[phones[i], phones[j]]
             for i in range(len(phones)) for j in range(i + 1, len(phones))]

    dupe_keys = []
    for f in fields:
        c = cols[f]
        # Identifier-ish: mostly filled, and either near-unique or a kind of value
        # that identifies a thing. Without the second test, every category column
        # in every spreadsheet gets reported as "10 rows are duplicates", which is
        # both wrong and the fastest way to teach a user to ignore the findings.
        identifier = (c["uniqueness"] >= DUPE_UNIQUENESS
                      or (c["rule_type"] in DUPE_TYPES and c["uniqueness"] >= 0.60))
        if c["is_empty"] or c["filled"] < row_count * 0.5 or not identifier:
            continue
        groups = Counter(str(r.get(f, "")).strip() for r in records if str(r.get(f, "")).strip())
        repeated = {v: n for v, n in groups.items() if n > 1}
        if repeated:
            dupe_keys.append({"column": f, "dupes": sum(repeated.values()) - len(repeated),
                              "groups": len(repeated)})
    return {"phone_pairs": pairs[:6], "dupe_keys": dupe_keys}


def _findings(fields: list[str], cols: dict, cross: dict, row_count: int,
              trailer: list[int]) -> list[dict]:
    """The "how did it know that?" list. Every one of these is arithmetic.

    They are ordered by kind rather than by column, because the order is what a
    human reads as a story: what's wrong with the values, then what's wrong with
    the rows, then what's wrong with the shape."""
    out: list[dict] = []

    def add(code, column, text, severity="warn"):
        out.append({"code": code, "column": column, "text": text, "severity": severity})

    for f in fields:
        if cols[f]["phone_multi"]:
            add("phone_multi", f, f"'{f}' holds more than one number in "
                f"{cols[f]['phone_multi']} of {row_count} cells. Pick one by hand today "
                f"and you'll pick a different one next quarter.")
    for d in cross["dupe_keys"]:
        rows = "row repeats" if d["dupes"] == 1 else "rows repeat"
        things = "thing is" if d["groups"] == 1 else "things are"
        add("dupe_key", d["column"], f"{d['dupes']} {rows} a '{d['column']}' that "
            f"appeared earlier — {d['groups']} {things} in this file twice.")
    for f in fields:
        if cols[f]["date_range"]:
            lo, hi = cols[f]["date_range"]
            add("date_range", f, f"'{f}' spans {lo} → {hi}, across {cols[f]['distinct']} "
                f"distinct values.", "info")
    for f in fields:
        mv = cols[f]["multivalue"]
        if mv:
            add("multivalue", f, f"'{f}' isn't one value — it averages "
                f"{mv['mean_per_cell']} per cell, split on '{mv['sep']}'. That's a lookup "
                f"table hiding inside a cell.")
    for f in fields:
        cv = cols[f]["case_variants"]
        if cv:
            add("case_variants", f, f"'{f}' has {cols[f]['distinct']} distinct values, but "
                f"some are the same word twice: {' · '.join(cv[0][:3])}.")
    for f in fields:
        c = cols[f]
        if c["is_empty"] or (c["fill"] <= 0.05 and c["filled"]):
            said = ", ".join(f'"{v}"' for v, _n in c["top"][:2])
            tail = f" The ones that aren't say: {said}." if said else ""
            headerless = " It doesn't even have a header." if re.fullmatch(r"col(_\d+)?", f) else ""
            add("dead_column", f, f"'{f}' is empty in {c['empty']} of {row_count} rows."
                f"{headerless}{tail}")
    if trailer:
        one = len(trailer) == 1
        span = f"Row {trailer[0]}" if one else f"Rows {trailer[0]}–{trailer[-1]}"
        add("trailer", "", f"{span} of {row_count} {'has' if one else 'have'} at most one "
            f"column filled. That looks like a footer somebody typed, not data.", "info")
    for f in fields:
        c = cols[f]
        if c["whitespace_dirty"]:
            add("whitespace", f, f"{c['whitespace_dirty']} cells in '{f}' have leading or "
                f"trailing spaces — invisible in Excel, fatal in a lookup.")
        if c["nbsp"]:
            add("whitespace", f, f"{c['nbsp']} cells in '{f}' contain a non-breaking space. "
                f"It looks exactly like a space and matches nothing.")
    for f in fields:
        c = cols[f]
        if c["is_constant"]:
            add("constant", f, f"'{f}' says \"{c['top'][0][0]}\" in all {c['filled']} filled "
                f"rows. That's a constant, not a column.", "info")
    for f in fields:
        if cols[f]["is_key"]:
            add("is_key", f, f"'{f}' is unique in every one of {cols[f]['filled']} rows — "
                f"that's your primary key, whether anyone declared it or not.", "info")
    for f in fields:
        if cols[f]["rule_type"] == "excel_serial":
            add("excel_serial", f, f"'{f}' arrived as raw Excel day numbers "
                f"({cols[f]['top'][0][0]}). Nobody can read that; "
                f"'read the dates properly' fixes it.")
    return out


def _eligible(fields: list[str], cols: dict, cross: dict, dup_rows: int) -> list[dict]:
    """The licence list: what the *cells* say we are allowed to offer.

    This bounds the model. analyze.validate() drops any action the brain proposes
    whose (id, columns) pair isn't in here, so the worst a hallucinating model can
    do is re-rank a menu somebody else wrote."""
    out: list[dict] = []

    def add(aid, columns, reason, strength):
        out.append({"id": aid, "columns": list(columns), "reason": reason,
                    "strength": round(float(strength), 2)})

    for f in fields:
        share = cols[f]["type_votes"].get("phone", 0)
        if share >= PHONE_VOTE_FLOOR:
            add(NORMALIZE_PHONE, [f], f"{int(share * 100)}% of cells parse as a phone number", share)
    for a, b in cross["phone_pairs"]:
        add(RECONCILE_PHONES, [a, b], f"'{a}' and '{b}' both hold phone numbers", 1.0)

    live = [f for f in fields if not cols[f]["is_empty"] and not cols[f]["is_constant"]]
    add(SCORE_QUALITY, live[:8] or fields[:1],
        "every list can be scored on how much of it is actually filled in", 1.0)

    free = [f for f in fields
            if cols[f]["rule_type"] in ("free_text", "") and not cols[f]["is_empty"]]
    if free:
        add(CLASSIFY, free[:3],
            "free text the rules can't categorise — the only job here that needs a brain",
            0.78)

    for f in fields:
        cv = cols[f]["case_variants"]
        if cv:
            add(CANONICALIZE_VALUES, [f],
                f"{len(cv)} value(s) in '{f}' are spelled more than one way", 0.95)
    for f in fields:
        c = cols[f]
        if c["rule_type"] in ("date", "excel_serial"):
            parsed = c.get("date_parsed", 0)
            strength = round(parsed / c["filled"], 2) if c["filled"] else 0.0
            add(PARSE_DATES, [f],
                f"{parsed} of {c['filled']} cells read as a real date without guessing",
                strength)
    for f in fields:
        mv = cols[f]["multivalue"]
        if mv:
            add(SPLIT_MULTIVALUE, [f],
                f"{mv['cells']} cells contain '{mv['sep']}' — {mv['mean_per_cell']} values each",
                round(mv["cells"] / cols[f]["filled"], 2))
    for f in fields:
        share = cols[f]["type_votes"].get("email", 0)
        if cols[f]["rule_type"] == "email":
            add(VALIDATE_EMAIL, [f], f"{int(share * 100)}% of cells are email-shaped", share)

    for d in cross["dupe_keys"]:
        one = d["groups"] == 1
        add(DEDUPE, [d["column"]],
            f"{d['groups']} value{'' if one else 's'} of '{d['column']}' "
            f"appear{'s' if one else ''} more than once", 1.0)
    if not cross["dupe_keys"] and dup_rows:
        add(DEDUPE, live[:5] or fields[:1],
            f"{dup_rows} rows are byte-for-byte copies of an earlier row", 1.0)

    add(BUILD_SCHEMA, [], "any list can be handed back as a table definition", 1.0)
    return out


def xray(fields: list[str], records: list[dict], filename: str = "",
         sheet_name: str = "") -> dict:
    """Profile one sheet. Deterministic, offline, and the source of every number
    the draft screen shows. See the module docstring for why that matters."""
    row_count, col_count = len(records), len(fields)
    values = {f: [str(r.get(f, "") or "") for r in records] for f in fields}
    cols = {f: _column(f, i, values[f], row_count) for i, f in enumerate(fields)}

    seen: set[tuple] = set()
    dup_rows = 0
    for r in records:
        sig = tuple(str(r.get(f, "")).strip() for f in fields)
        if sig in seen:
            dup_rows += 1
        else:
            seen.add(sig)

    # A footer is a *tail* phenomenon. A sparse row in the middle of the sheet is
    # a lazily-filled record; the same row at the bottom is somebody's "TOTAL:"
    # line, and importing it as a customer is how a fake customer is born.
    trailer: list[int] = []
    for i in range(row_count - 1, -1, -1):
        if sum(1 for f in fields if str(records[i].get(f, "")).strip()) > 1:
            break
        trailer.append(i + 1)
    trailer.reverse()
    if len(trailer) == row_count:      # the whole sheet is one column — not a footer
        trailer = []

    smell: list[str] = []
    for i, f in enumerate(fields):
        m = re.fullmatch(r"(.+)_(\d+)", f)
        if m and m.group(1) in fields:
            smell.append(f"duplicate header '{m.group(1)}' kept as {f} — two columns "
                         f"claiming the same fact is a finding, not a nuisance")
        if re.fullmatch(r"col(_\d+)?", f):
            smell.append(f"column {i + 1} had no header")

    cross = _cross(fields, records, cols, row_count)
    out = {
        "filename": filename,
        "sheet_name": sheet_name,
        "row_count": row_count,
        "col_count": col_count,
        "exact_duplicate_rows": dup_rows,
        "trailer_rows": trailer,
        "header_smell": smell,
        "columns": cols,
        "cross": cross,
        "findings": _findings(fields, cols, cross, row_count, trailer),
        "eligible": _eligible(fields, cols, cross, dup_rows),
    }
    out["sha"] = hashlib.sha256(
        json.dumps(out, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()
    return out


def one_liner(xr: dict) -> str:
    """The summary we use when there is no brain — computed, therefore never wrong.

    This is the honest baseline for the draft screen's headline. It reads worse
    than the model's sentence and it is true, which is the trade the whole pack
    is built on."""
    kinds = Counter(c["rule_type"] for c in xr["columns"].values() if c["rule_type"])
    if not kinds:
        return f"{xr['row_count']} rows, {xr['col_count']} columns; nothing in them has an obvious shape."
    kind, n = kinds.most_common(1)[0]
    return (f"{xr['row_count']} rows, {xr['col_count']} columns; "
            f"{n} of them look like {kind.replace('_', ' ')}.")
