"""Freehold — the ten things we can do to a list. There is no eleventh.

A closed catalogue is a strange thing to be proud of, so here is why it is the
feature and not a limitation.

An open-ended "what would you like done?" box means the model gets to propose
work that no code can perform. It then either fails at run time or — far worse —
somebody writes a generic "just do what it said" executor, and now a language
model is editing a customer's master data with no reviewable definition of what
it did. Ten named actions, each with a pure Python executor and a test, means the
model's job shrinks to *ranking a menu somebody else wrote*. It can reorder,
justify, and leave things out. It cannot invent.

Six of the ten never call anything new — they are enrich.py's existing rules,
reached through a Profile. **Nine of the ten never call a model at run time.**
Only `classify` does, and only against a taxonomy a human froze at approval time.

Explicitly rejected, and named here so the list visibly stays closed: geocoding,
web company lookup, email MX/deliverability probing, currency conversion,
translation, joining against another list, and "guess the missing values". Every
one of them needs an outside call, which means writing into a customer's data a
fact that was not in the customer's file. That is not enrichment, that is
invention with a receipt. Adding an eleventh action costs a catalogue entry, an
executor and a test — that friction is deliberate.
"""
import re

import enrich
import xray

# --- the catalogue ---------------------------------------------------------
# `scope`      what the action operates on, for the screen's grouping
# `needs_model` whether the RUN calls a brain (exactly one does)
# `params`     the knobs a human may turn before approving
ACTIONS: dict[str, dict] = {
    "normalize_phone": {
        "label": "Turn phone numbers into one dialable format (+41 44 …)",
        "blurb": "Ambiguous cells are handed to a human, never guessed.",
        "scope": "column", "needs_model": False, "params": (),
    },
    "reconcile_phones": {
        "label": "Two phone columns — show me where they disagree",
        "blurb": "agree · overlap · conflict · only-one-side. No value is overwritten.",
        "scope": "pair", "needs_model": False, "params": (),
    },
    "score_quality": {
        "label": "Score how complete each row is, and say what's missing",
        "blurb": "The number that sells the whole thing: 'you are missing 340 emails'.",
        "scope": "row", "needs_model": False, "params": (),
    },
    "classify": {
        "label": "Sort every row into a category — you approve the categories first",
        "blurb": "The only action that calls a brain at run time, against a frozen list.",
        "scope": "row", "needs_model": True,
        "params": ("to", "multi", "taxonomy", "instruction"),
    },
    "canonicalize_values": {
        "label": "Merge the spellings of the same value into one",
        "blurb": "Active / active / ACTIVE are one value. The map is frozen into the recipe.",
        "scope": "column", "needs_model": False, "params": ("map",),
    },
    "parse_dates": {
        "label": "Read the dates properly and add year + quarter",
        "blurb": "Declines on genuine DD/MM vs MM/DD ambiguity instead of guessing.",
        "scope": "column", "needs_model": False, "params": ("from",),
    },
    "split_multivalue": {
        "label": "This cell holds a list — give it its own table",
        "blurb": "A many-to-many hiding inside a cell, pulled out into values.",
        "scope": "column", "needs_model": False, "params": ("sep",),
    },
    "validate_email": {
        "label": "Check the email addresses look real (no network)",
        "blurb": "Syntax, role accounts, free providers. No MX lookup, no probe, ever.",
        "scope": "column", "needs_model": False, "params": (),
    },
    "dedupe": {
        "label": "Find rows that are the same thing twice",
        "blurb": "Flags the copies. Deletes nothing — that's your call, not ours.",
        "scope": "row", "needs_model": False, "params": (),
    },
    "build_schema": {
        "label": "Turn this list into a real table — give me the schema",
        "blurb": "Emits CREATE TABLE as text. It does not run it.",
        "scope": "table", "needs_model": False, "params": ("table",),
    },
}

ACTION_IDS = list(ACTIONS)

# The post-pass runs in this order regardless of what order the spec lists, and
# the order is load-bearing: canonicalising spellings BEFORE deduping is what
# makes "Havas Media" and "havas media" collapse into one duplicate group.
POST_ORDER = ("canonicalize_values", "parse_dates", "split_multivalue",
              "validate_email", "dedupe", "build_schema")

# Role accounts and free providers, for validate_email. Deliberately short and
# deliberately offline — a longer list is a data file, not a code change.
ROLE_LOCALS = {"info", "office", "kontakt", "contact", "sales", "admin", "noreply",
               "no-reply", "mail", "hello", "support", "team", "buchhaltung"}
FREE_DOMAINS = {"gmail", "hotmail", "outlook", "yahoo", "gmx", "bluewin", "icloud",
                "live", "msn", "aol", "protonmail", "sunrise"}
_RE_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


def eligible(xr: dict) -> list[dict]:
    """The licence list, filtered against the catalogue.

    xray computes the triggers (it is the thing that can see the cells); this is
    the guard that guarantees it can never licence an action no executor exists
    for. If the two files ever drift, the entry is dropped here rather than
    exploding at run time in front of a customer."""
    return [e for e in xr.get("eligible", []) if e.get("id") in ACTIONS]


# --- the run-time profile --------------------------------------------------
def profile_from(spec: dict) -> tuple[enrich.Profile, str | None]:
    """Turn an approved recipe into an enrich.Profile. Returns (profile, model_override).

    This is the seam that lets the whole feature reuse the enrichment engine with
    ZERO edits to enrich.py. A Profile is just "what enriched means for one kind
    of record" — a recipe is exactly that, written by a human instead of a
    developer.

    Two guards here are load-bearing, and both work around live bugs in enrich.py
    that we are deliberately not fixing in this change (see the follow-ups):

      * enrich.quality() divides by len(fields). An empty quality_fields is a
        ZeroDivisionError on row one, so we always hand it at least one column.
      * enrich.enrich() writes _enriched[p.target] unconditionally. With an empty
        target and a live brain you get an envelope keyed "" — invisible garbage
        in the report. So if nobody ticked `classify`, we force the model to
        "none": there is nothing for it to do anyway.
    """
    acts = {a["id"]: a for a in spec.get("actions", [])}
    cols = list(spec.get("_all_columns") or spec.get("semantics") or ())

    quality_cols = tuple(acts["score_quality"]["columns"]) if "score_quality" in acts else ()
    if not quality_cols:
        quality_cols = tuple(cols[:1]) or ("_row",)      # never empty. See above.

    # Read from the LIST, not from `acts`: a spec may legitimately hold two
    # normalize_phone entries, and a dict keyed by id keeps only the last one.
    # That collapse is how you end up reconciling a column against itself and
    # reporting "these two agree" about one column, which is a lie that looks
    # like a feature.
    phones = [a for a in spec.get("actions", ())
              if a.get("id") == "normalize_phone" and a.get("columns")]
    pair = next((a["columns"] for a in spec.get("actions", ())
                 if a.get("id") == "reconcile_phones" and len(a.get("columns", ())) > 1), [])
    phone = phones[0]["columns"][0] if phones else ""
    recon = ""
    if pair:
        # enrich.Profile compares phone_field against reconcile_with, so one side
        # of the approved pair has to BE phone_field. If the human ticked the
        # comparison, honour it rather than silently dropping the action.
        phone, recon = (phone, pair[1] if pair[0] == phone else pair[0]) \
            if phone in pair else (pair[0], pair[1])

    cls = acts.get("classify")
    params = (cls or {}).get("params", {})
    p = enrich.Profile(
        key=f"_recipe:{spec.get('key', 'unsaved')}:{spec.get('version', 0)}",
        label=spec.get("label", "List"),
        quality_fields=quality_cols,
        phone_field=phone,
        reconcile_with=recon,
        target=(params.get("to", "") if cls else ""),
        taxonomy=tuple(params.get("taxonomy", ())) if cls else (),
        feed=tuple(cls["columns"]) if cls else (),
        instruction=(params.get("instruction", "") if cls else ""),
        multi=bool(params.get("multi")) if cls else False,
        label_fields=tuple(spec.get("label_fields") or ()) or tuple(cols[:1]) or ("_row",),
    )
    return p, (None if cls else "none")


# --- the pure executors ----------------------------------------------------
def _env(value, raw, replaces=""):
    """Every post-pass value wears the same paper trail as an enrichment.

    source="rule", confidence 1.0, no prompt version: these are arithmetic, not
    opinions. Rule-written fields deliberately do not move enrich's gate — a
    parsed date is not something a human needs to second-guess. `replaces` names
    the source column this is the clean form of, so a deliverable folds it in."""
    return enrich.field(value, original=raw, source="rule", confidence=1.0,
                        prompt_version="", replaces=replaces)


def value_map(xr: dict, col: str) -> dict:
    """The canonicalisation map, computed from the cells: most frequent spelling wins.

    Frozen into the recipe at approval time, so next quarter's run merges the same
    way even if the counts have shifted. A map that recomputes itself every run is
    not a rule, it's a mood."""
    groups = xr.get("columns", {}).get(col, {}).get("case_variants", [])
    return {v: g[0] for g in groups for v in g[1:]}


def canonicalize(records: list[dict], col: str, vmap: dict) -> dict:
    """Merge spelling variants into one value. Writes <col>_canon, keeps the original."""
    merged = 0
    for rec in records:
        raw = str(rec.get(col, "") or "")
        if not raw.strip():
            continue
        value = vmap.get(raw, raw)
        merged += value != raw
        rec["_enriched"][f"{col}_canon"] = _env(value, raw, replaces=col)
    return {"merged": merged, "variants": len(vmap)}


def parse_dates(records: list[dict], col: str, from_: str = "auto") -> dict:
    """Read a date column into ISO + year + quarter, or say why it couldn't.

    `from_` is frozen in the recipe so the same file parses the same way forever.
    "auto" resolves the column's day/month order from evidence in the column
    itself; a cell that is still genuinely ambiguous is left alone and flagged,
    because silently shifting a third of a customer's dates by eleven months is
    the kind of bug that is found years later, by an accountant."""
    order = from_
    if from_ == "auto":
        order = xray.date_order([str(r.get(col, "") or "") for r in records])
    out = {"parsed": 0, "ambiguous": 0, "unparsed": 0}
    for rec in records:
        raw = str(rec.get(col, "") or "")
        if not raw.strip():
            continue
        iso, status = xray.iso_from(raw, order)
        if status == "ok":
            y, m = int(iso[:4]), int(iso[5:7])
            value = {"iso": iso, "year": y, "quarter": f"Q{(m - 1) // 3 + 1}"}
            out["parsed"] += 1
        else:
            value = {"status": status, "raw": raw}
            out[status] += 1
        rec["_enriched"][f"{col}_iso"] = _env(value, raw, replaces=col)
    return out


def split_multivalue(records: list[dict], col: str, sep: str = "/") -> dict:
    """One cell holding a list becomes a list. Writes <col>_values."""
    cells = values = 0
    for rec in records:
        raw = str(rec.get(col, "") or "")
        if not raw.strip():
            continue
        parts = [p.strip() for p in raw.split(sep) if p.strip()]
        rec["_enriched"][f"{col}_values"] = _env({"sep": sep, "values": parts}, raw)
        cells += 1
        values += len(parts)
    return {"cells": cells, "values": values}


def validate_email(records: list[dict], col: str) -> dict:
    """Syntax + role account + free provider. NO NETWORK — and the UI says so.

    An MX lookup or an SMTP probe would tell you more and would also (a) leak
    every customer address to a DNS resolver, (b) make the run fail when the box
    is offline, and (c) get the box's IP listed as a spam prober. Three honest
    booleans computed locally beat one unreliable one fetched remotely."""
    out = {"checked": 0, "bad_syntax": 0, "role": 0, "free": 0}
    for rec in records:
        raw = str(rec.get(col, "") or "").strip()
        if not raw:
            continue
        syntax = bool(_RE_EMAIL.match(raw))
        local, _, domain = raw.partition("@")
        root = domain.split(".")[0].casefold() if domain else ""
        value = {
            "syntax": syntax,
            "role_account": syntax and local.casefold() in ROLE_LOCALS,
            "free_provider": syntax and root in FREE_DOMAINS,
            "domain": domain.casefold() if syntax else "",
        }
        out["checked"] += 1
        out["bad_syntax"] += not syntax
        out["role"] += value["role_account"]
        out["free"] += value["free_provider"]
        rec["_enriched"][f"{col}_check"] = _env(value, raw)
    return out


def _dupe_key(rec: dict, cols: list[str]) -> str:
    """The normalised key. Prefers the canonicalised value when there is one —
    which is why the post-pass runs canonicalize_values BEFORE dedupe. If a human
    approved a map saying "Havas Media AG" is "Havas Media", then those two rows
    are one agency, and the dedupe has to see the merged spelling to know it."""
    parts = []
    for c in cols:
        env = rec.get("_enriched", {}).get(f"{c}_canon")
        raw = env["value"] if isinstance(env, dict) else rec.get(c, "")
        parts.append(re.sub(r"[^a-z0-9]+", "", str(raw or "").casefold()))
    return "|".join(parts)


def dedupe(records: list[dict], cols: list[str]) -> dict:
    """Flag rows that are the same thing twice. Marks the copies, never the first.

    It does not delete anything, and it never will: which of two half-filled rows
    is 'the real one' is a business decision with money attached. Our job is to
    make the question visible, not to answer it at 3am with no supervision."""
    if not cols:
        return {"groups": 0, "rows": 0}
    seen: dict[str, list[int]] = {}
    for i, rec in enumerate(records):
        key = _dupe_key(rec, cols)
        if not key.strip("|"):
            continue
        seen.setdefault(key, []).append(i)

    groups = rows = 0
    for key, idx in seen.items():
        if len(idx) < 2:
            continue
        groups += 1
        for i in idx[1:]:
            rows += 1
            records[i]["_enriched"]["dupe_of"] = _env(
                {"key": key, "first_row": idx[0] + 1, "group_size": len(idx)},
                " | ".join(str(records[i].get(c, "") or "") for c in cols)[:120])
    return {"groups": groups, "rows": rows}


# --- schema: the blueprint, never the build --------------------------------
_SQL_TYPE = {
    "person_name": "TEXT", "company_name": "TEXT", "email": "TEXT", "phone": "VARCHAR(40)",
    "url": "TEXT", "street": "TEXT", "city": "TEXT", "postcode": "VARCHAR(12)",
    "country": "VARCHAR(64)", "region": "VARCHAR(64)", "date": "DATE",
    "datetime": "TIMESTAMPTZ", "amount_money": "NUMERIC(14,2)", "quantity": "INTEGER",
    "percentage": "NUMERIC(5,2)", "identifier": "VARCHAR(64)", "code": "VARCHAR(64)",
    "category": "VARCHAR(80)", "status": "VARCHAR(40)", "boolean": "BOOLEAN",
    "free_text": "TEXT", "note": "TEXT", "tag_list": "TEXT", "unknown": "TEXT",
}
_RULE_TYPE = {"email": "TEXT", "phone": "VARCHAR(40)", "url": "TEXT", "date": "DATE",
              "excel_serial": "DATE", "money": "NUMERIC(14,2)", "number": "NUMERIC",
              "postcode": "VARCHAR(12)", "boolean": "BOOLEAN", "free_text": "TEXT"}


def ident(name: str, fallback: str = "t") -> str:
    """A safe SQL identifier. Nothing derived from an uploaded file is ever
    interpolated into SQL without passing through here — and even then the SQL is
    only ever handed back as text."""
    out = re.sub(r"[^a-z0-9_]+", "_", str(name or "").casefold()).strip("_")[:60]
    return out or fallback


def build_schema(spec: dict, xr: dict) -> str:
    """Emit CREATE TABLE for this list, as TEXT. **It is never executed.**

    The vision is "build a database on the fly". The honest version of that ships
    the blueprint and lets a human run it: executing DDL derived from an uploaded
    spreadsheet needs a table-naming policy, ownership, grants, upsert semantics
    and an erasure story we have not designed. A schema you can read, diff and
    paste into psql is worth more than one that appeared in your database while
    you were at lunch — and comparing two tabs' schemas is how you find out they
    were the same table all along.
    """
    acts = {a["id"]: a for a in spec.get("actions", [])}
    table = ident(acts.get("build_schema", {}).get("params", {}).get("table")
                  or spec.get("key"), "list_table")
    sem = spec.get("semantics", {})
    cols = xr.get("columns", {})

    # A footer contaminates uniqueness: "TOTALS", "Best time to call" and your
    # own margin notes are each a distinct string, so a column reads as unique
    # "in every row" only because the junk rows are junk-unique. Declaring that a
    # PRIMARY KEY makes a sentence the identity of your table. If the sheet has a
    # detected trailer, we still name the key candidate but hold the PRIMARY KEY
    # back until those rows are gone.
    trailer = bool(xr.get("trailer_rows"))
    key_col = next((c for c in sem if cols.get(c, {}).get("is_key")), "")
    # A column the recipe parses into a real date is a DATE, whatever the
    # semantic says. Excel handed it to us as the number 45231; declaring that
    # TEXT after we went to the trouble of reading it is the wrong blueprint.
    dated = {c for a in spec.get("actions", []) if a["id"] == "parse_dates"
             for c in a.get("columns", [])}
    lines = [f"-- {table}: proposed by Freehold from {xr.get('filename') or 'an upload'}"
             f" (sheet {xr.get('sheet_name') or '1'}), {xr.get('row_count', 0)} rows.",
             "-- Reviewed by a human before it means anything. Freehold does not run this.",
             f"CREATE TABLE {table} ("]
    body: list[str] = []
    if not key_col or trailer:
        # No clean key (or a contaminated one) → give the table a synthetic key
        # and don't pretend a data column is unique.
        body.append("  id            SERIAL PRIMARY KEY")
    if key_col and trailer:
        lines.insert(2, f"-- NOTE: '{key_col}' looks unique, but this sheet has footer/"
                        f"note rows mixed in — remove those first, then '{key_col}' can be "
                        f"the PRIMARY KEY instead of the synthetic id.")

    for col, meta in sem.items():
        c = cols.get(col, {})
        semantic = meta.get("semantic", "")
        # "unknown" is the analysis saying it has no opinion — fall through to
        # what the cells look like rather than declaring everything TEXT.
        sql = ("DATE" if col in dated else
               (_SQL_TYPE.get(semantic, "") if semantic != "unknown" else "")
               or _RULE_TYPE.get(c.get("rule_type", ""), "TEXT"))
        parts = [f"  {ident(col, 'c'):<13} {sql}"]
        if col == key_col and not trailer:
            parts.append("PRIMARY KEY")
        elif c.get("fill") == 1.0 and not c.get("is_empty"):
            parts.append("NOT NULL")
        body.append(" ".join(parts))

    cls = acts.get("classify")
    if cls:
        target = ident(cls.get("params", {}).get("to"), "category")
        allowed = [v.replace("'", "''") for v in cls.get("params", {}).get("taxonomy", ())]
        line = f"  {target:<13} TEXT"
        if allowed and not cls.get("params", {}).get("multi"):
            line += "\n    CHECK (" + target + " IN (" + ", ".join(
                f"'{v}'" for v in allowed) + "))"
        body.append(line)

    lines.append(",\n".join(body))
    lines.append(");")

    for a in spec.get("actions", []):
        if a["id"] != "split_multivalue" or not a.get("columns"):
            continue
        col = a["columns"][0]
        child = ident(f"{table}_{col}", "child")
        parent = ident(key_col or "id", "id")
        lines += [
            "",
            f"-- '{col}' held {a.get('params', {}).get('sep', '/')}-separated lists;"
            f" a many-to-many belongs in its own table.",
            f"CREATE TABLE {child} (",
            f"  {parent:<13} {'VARCHAR(64)' if key_col else 'INTEGER'} "
            f"REFERENCES {table}({parent}),",
            f"  value         TEXT NOT NULL,",
            f"  PRIMARY KEY ({parent}, value)",
            ");",
        ]
    return "\n".join(lines)
