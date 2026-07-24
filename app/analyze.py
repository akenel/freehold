"""Freehold — the design-time model call: the brain names things, and only things.

xray.py already counted everything. What is still missing is the part a machine
genuinely cannot do from arithmetic: *what is this list about*, and *what does
column `ansprech` mean*. That is naming, and naming is what a language model is
actually good at.

So the division of labour is absolute, and it is the whole safety story:

    the code writes every number · the model writes every noun

The model never sees the sheet — it sees a PROFILE of the sheet: column names,
fill rates, distinct counts, at most five sample values per column and three
sample rows. And whatever comes back goes through seven brakes in validate()
before a single character of it reaches a screen. Anything that fails is
DROPPED, counted, and the count is printed on the page. Dropping loudly is a
feature: it is the only visible proof that the gate is real.

The one that matters most is brake 5, the grounding check. A model handed
"Agenturen 2024.xlsx" will cheerfully summarise it as "480 Swiss media agencies
collected since 2019" — a sentence that is fluent, plausible, useful-sounding,
and entirely invented. Nothing in the profile said Swiss, and nothing said 2019.
Brake 5 deletes it. You cannot prompt your way out of that failure mode; you can
only refuse to print anything the model was not shown.

If there is no brain — no key, "none" picked, network down — this module returns
a complete, usable analysis built from the X-ray alone, every field labelled
source="rule" at 0.60 confidence so the gate marks it "review" rather than
"auto". The draft screen works fully with no AI at all. That is the demo you give
when the wifi dies, and it is why every test in this feature is network-free.
"""
import json
import os
import re

import httpx

import actions
import enrich
import xray

PROMPT_VERSION = "list-analyze-v1"

# Rules-only confidence. Deliberately in the "review" band: a rule_type guess is
# a decent hint, not a decision, and it should never arrive pre-ticked.
RULE_CONFIDENCE = 0.60

# --- the closed vocabularies ----------------------------------------------
# Anything outside these becomes "other"/"unknown" at zero confidence. A model
# that invents a category is not adding information, it is adding a word nobody
# downstream can switch on.
LIST_KINDS = ["contacts", "call_list", "customers", "suppliers", "products",
              "inventory", "price_list", "transactions", "assets", "events", "other"]
SEMANTIC = ["person_name", "company_name", "email", "phone", "url", "street", "city",
            "postcode", "country", "region", "date", "datetime", "amount_money",
            "quantity", "percentage", "identifier", "code", "category", "status",
            "boolean", "free_text", "note", "tag_list", "unknown"]
ACTION_IDS = list(actions.ACTIONS)

CAPS = {"title": 80, "summary": 240, "role": 60, "why": 120}
MAX_TAXONOMY, MAX_TAXONOMY_LEN = 40, 24
SAMPLES_PER_COLUMN, SAMPLE_ROWS, MAX_PROFILED_COLUMNS = 5, 3, 40


# --- transport -------------------------------------------------------------
# NOTE: this is a deliberate ~25-line duplicate of enrich._ask_model. That
# function is welded to Profile/_task/_SCHEMA, has no other callers and no test
# coverage; refactoring shipped, untested, load-bearing code to save 25 lines is
# a bad trade. When a third caller appears, extract a brain.py — and change both.
# The other copy lives in enrich.py.
def _base() -> str:
    return os.getenv("OLLAMA_BASE_URL", "https://ollama.com").rstrip("/")


def _key() -> str:
    return os.getenv("OLLAMA_API_KEY", "")


# Read at CALL time, not import time — unlike enrich._BASE/_KEY, which freeze at
# import and therefore ignore a key set after boot. The inconsistency is on
# purpose: this is the better behaviour, and enrich.py is not ours to edit today.

_SYSTEM = """You are a data librarian. You are shown a PROFILE of a spreadsheet — column
names, fill rates, distinct counts, a few sample values — and your job is to
say what the list IS, name what each column MEANS, and rank the actions the
system has already determined it is able to perform.

HARD RULES. Output that breaks any of these is discarded by the system and
reported to the user as a dropped claim.
1. Never state a quantity, count, percentage, total, sum, date range or
   "how many". Every number shown to the user is computed from the cells by
   code. Numbers you write are deleted unread.
2. Use ONLY the allowed values for list_kind and semantic. Anything else
   becomes "other" / "unknown".
3. Use ONLY column names that appear in the profile, spelled exactly.
4. Choose actions ONLY from eligible_actions, copying the id and the columns
   array exactly as given. You may reorder them, justify them, and leave some
   out. You may NOT invent an action, and you may NOT change its columns.
5. Every proper noun and every digit you write in title, summary, role or why
   must already appear in the profile you were shown. Do not add country
   names, industries, years, or company facts you were not given.
6. title <= 80 chars. summary <= 240. role <= 60. why <= 120.
7. confidence is your own honesty, 0.0 to 1.0. Low is a fine answer. A high
   confidence on a guess is the one thing we cannot forgive.

Return only the JSON object."""

_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "list_kind": {"type": "string", "enum": LIST_KINDS},
        "suggested_key": {"type": "string"},
        "confidence": {"type": "number"},
        "label_fields": {"type": "array", "items": {"type": "string"}},
        "columns": {"type": "array", "items": {"type": "object", "properties": {
            "name": {"type": "string"},
            "semantic": {"type": "string", "enum": SEMANTIC},
            "role": {"type": "string"},
            "confidence": {"type": "number"}},
            "required": ["name", "semantic", "confidence"]}},
        "actions": {"type": "array", "items": {"type": "object", "properties": {
            "id": {"type": "string", "enum": ACTION_IDS},
            "columns": {"type": "array", "items": {"type": "string"}},
            "why": {"type": "string"},
            "confidence": {"type": "number"}},
            "required": ["id", "columns", "confidence"]}},
        "taxonomy_proposal": {"type": "array", "items": {"type": "string"}},
        "classify_target": {"type": "string"},
        "classify_multi": {"type": "boolean"},
        "classify_instruction": {"type": "string"},
    },
    "required": ["title", "summary", "list_kind", "confidence", "columns", "actions"],
}


def profile_payload(xr: dict, records: list[dict] | None = None) -> dict:
    """What actually leaves the box. Everything else stays on the customer's server.

    Column names, counts, and a handful of sample values — because a column called
    `markt` full of "Benelux" means nothing without seeing one. Five values per
    column and three whole rows is enough for naming and small enough to say out
    loud on the screen, which we do. The findings text is deliberately NOT sent:
    it is full of numbers, and a model that has read our numbers will happily
    repeat them back as its own, which defeats brake 5."""
    cols = xr.get("columns", {})
    names = list(cols)
    out_cols = []
    for name in names[:MAX_PROFILED_COLUMNS]:
        c = cols[name]
        out_cols.append({
            "name": name,
            "header": c.get("header", name),
            "fill": c.get("fill", 0),
            "distinct": c.get("distinct", 0),
            "unique": bool(c.get("is_key")),
            "rule_type": c.get("rule_type", ""),
            "samples": [str(v)[:60] for v, _n in c.get("top", [])[:SAMPLES_PER_COLUMN]],
        })
    out_cols += [{"name": n} for n in names[MAX_PROFILED_COLUMNS:]]

    sample_rows = []
    for rec in (records or [])[:SAMPLE_ROWS]:
        sample_rows.append({k: str(v)[:60] for k, v in rec.items()
                            if not k.startswith("_") and str(v).strip()})
    return {
        "filename": xr.get("filename", ""),
        "sheet": xr.get("sheet_name", ""),
        "row_count": xr.get("row_count", 0),
        "columns": out_cols,
        "sample_rows": sample_rows,
        "eligible_actions": [{"id": e["id"], "columns": e["columns"]}
                             for e in actions.eligible(xr)],
    }


def _task(payload: dict) -> str:
    return (
        f"Allowed list_kind: [{', '.join(LIST_KINDS)}].\n"
        f"Allowed semantic: [{', '.join(SEMANTIC)}].\n"
        f"Allowed action ids: [{', '.join(ACTION_IDS)}] — but only the "
        f"(id, columns) pairs listed in eligible_actions may be used.\n"
        f"Name every column in the profile. suggested_key is a short lowercase "
        f"slug for this list.\n\nProfile:\n"
        + json.dumps(payload, ensure_ascii=False)
    )


async def _ask(model: str, payload: dict) -> tuple[dict, int, str]:
    """One call to the brain. Returns (raw_object, tokens, error). Never raises."""
    if model == "none":
        return {}, 0, ""
    if not _key():
        return {}, 0, "no OLLAMA_API_KEY set — ran on rules alone"
    body = {
        "model": model,
        "stream": False,
        "format": _SCHEMA,
        "options": {"temperature": 0},
        "messages": [{"role": "system", "content": _SYSTEM},
                     {"role": "user", "content": _task(payload)}],
    }
    try:
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(f"{_base()}/api/chat",
                             headers={"Authorization": f"Bearer {_key()}"}, json=body)
            r.raise_for_status()
            data = r.json()
        tokens = int(data.get("prompt_eval_count", 0)) + int(data.get("eval_count", 0))
        return _parse(data["message"]["content"]), tokens, ""
    except Exception as exc:  # noqa: BLE001 — a busy brain must never break the page
        return {}, 0, f"{type(exc).__name__}: {exc}"[:200]


def _parse(content) -> dict:
    """Get the answer object out of whatever the model actually returned.

    A sibling of enrich._coerce rather than a change to it: _coerce hunts for a
    list of ROWS (and its `"i" in data` step is enrichment-specific), we want one
    object. `format` is a hint the server does not enforce, so both exist."""
    try:
        data = json.loads(content) if isinstance(content, (str, bytes)) else content
    except Exception:  # noqa: BLE001 — non-JSON is just an empty answer
        return {}
    if isinstance(data, list):
        return data[0] if data and isinstance(data[0], dict) else {}
    if not isinstance(data, dict):
        return {}
    if "title" in data or "columns" in data:
        return data
    for v in data.values():                    # {"result": {...}} and friends
        if isinstance(v, dict) and ("title" in v or "columns" in v):
            return v
    return {}


# --- the seven brakes ------------------------------------------------------
_WORD = re.compile(r"[A-Za-zÀ-ÿ][\wÀ-ÿ'’-]*")
_DIGITS = re.compile(r"\d{3,}")
_SENTENCE_START = re.compile(r"(?:^|[.!?…]\s+|\n\s*)$")


def _grounded(text: str, blob: str) -> bool:
    """Brake 5. Every proper noun and every long number must already be in the
    profile we sent.

    Sentence-initial capitals are exempt — "Agencies with a named contact" starts
    with a capital because it is a sentence, not because it is a proper noun.
    Mid-sentence capitalised words of four letters or more are, overwhelmingly,
    exactly the thing we are trying to catch: a country, a brand, an industry the
    model decided the customer belongs to.
    """
    hay = blob.casefold()
    for m in _DIGITS.finditer(text or ""):
        if m.group() not in hay:
            return False
    for m in _WORD.finditer(text or ""):
        word = m.group()
        if len(word) < 4 or not word[0].isupper():
            continue
        if _SENTENCE_START.search(text[:m.start()]):
            continue
        if word.casefold() not in hay:
            return False
    return True


def _conf(value) -> float:
    """Brake 7. Anything unnumberable is zero; the range is clamped, not trusted."""
    try:
        c = float(value)
    except (TypeError, ValueError):
        return 0.0
    if c != c:                                  # NaN compares unequal to itself
        return 0.0
    return max(0.0, min(1.0, c))


def _capped(text, kind: str) -> str:
    """Brake 6. Over-length is a DROP, not an ellipsis — a truncated sentence
    reads as a real one and hides that the model ignored the instruction."""
    s = str(text or "").strip()
    return s if 0 < len(s) <= CAPS[kind] else ""


def slug(text: str, cap: int = 40) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(text or "").casefold()).strip("-")[:cap]


def _target_name(text: str, fields) -> str:
    name = re.sub(r"[^a-z0-9_]+", "_", str(text or "").casefold()).strip("_")[:40]
    if not name:
        return ""
    # A model-written field must never quietly shadow a source column: the
    # original is not allowed to disappear, and _enriched[col] beside col is
    # exactly how you lose track of which one a human typed.
    return f"{name}_ai" if name in fields else name


def _default_taxonomy(xr: dict, col: str) -> list[str]:
    """The rules-only proposal: the values already in the column, capped.

    Not as good as a model's list, and true — which is the trade this whole pack
    is built on. The human edits it anyway; that edit is the product."""
    top = xr.get("columns", {}).get(col, {}).get("top", [])
    vals = [str(v).strip() for v, _n in top if str(v).strip()
            and len(str(v).strip()) <= MAX_TAXONOMY_LEN]
    return list(dict.fromkeys(vals))[:MAX_TAXONOMY - 1] + ["Other"]


def _params_for(aid: str, cols: list[str], xr: dict, key: str) -> dict:
    """The pre-filled knobs for one action, computed from the cells."""
    col = cols[0] if cols else ""
    meta = xr.get("columns", {}).get(col, {})
    if aid == "canonicalize_values":
        return {"map": actions.value_map(xr, col)}
    if aid == "parse_dates":
        return {"from": "excel_serial" if meta.get("rule_type") == "excel_serial" else "auto"}
    if aid == "split_multivalue":
        return {"sep": (meta.get("multivalue") or {}).get("sep", "/")}
    if aid == "build_schema":
        return {"table": actions.ident(key.replace("-", "_"), "list_table")}
    return {}


def validate(raw, xr: dict, model: str = "none", payload: dict | None = None):
    """The gate between a model's answer and a human's screen.

    Returns (analysis, dropped, note). Never raises — a model that returns a list,
    a string, None or a megabyte of nested junk must produce a usable page, not a
    500. Everything that survives is wrapped in enrich.field() so the screen can
    show, per statement, whether a rule or a brain wrote it.
    """
    payload = payload if payload is not None else profile_payload(xr)
    blob = json.dumps(payload, ensure_ascii=False)
    cols_meta = xr.get("columns", {})
    fields = list(cols_meta)
    raw = raw if isinstance(raw, dict) else {}
    dropped = 0

    def model_field(value, confidence, original=""):
        return enrich.field(value, original=original, source="model", model=model,
                            confidence=confidence, prompt_version=PROMPT_VERSION)

    def rule_field(value, original=""):
        return enrich.field(value, original=original, source="rule",
                            confidence=RULE_CONFIDENCE, prompt_version="")

    overall = _conf(raw.get("confidence"))

    # --- brakes 1, 5, 6 on the free text ---
    fallback_title = (xr.get("filename", "") or "This list").rsplit(".", 1)[0].strip() or "This list"
    title, summary = _capped(raw.get("title"), "title"), _capped(raw.get("summary"), "summary")
    if title and not _grounded(title, blob):
        title, dropped = "", dropped + 1
    elif not title and raw.get("title"):
        dropped += 1
    if summary and not _grounded(summary, blob):
        summary, dropped = "", dropped + 1
    elif not summary and raw.get("summary"):
        dropped += 1

    out = {
        "title": model_field(title, overall) if title else rule_field(fallback_title),
        "summary": (model_field(summary, overall) if summary
                    else rule_field(xray.one_liner(xr))),
        "confidence": overall,
        "model": model,
        "prompt_version": PROMPT_VERSION if (title or summary) else "",
    }

    # --- brake 2 on list_kind ---
    kind = str(raw.get("list_kind", "") or "")
    if kind in LIST_KINDS and kind != "other":
        out["list_kind"] = model_field(kind, overall)
    else:
        if kind and kind not in LIST_KINDS:
            dropped += 1
        out["list_kind"] = model_field("other", 0.0) if raw else rule_field("other")

    out["suggested_key"] = (slug(raw.get("suggested_key")) or slug(fallback_title)
                            or "list")

    # --- brakes 2 and 3 on the columns ---
    named: dict[str, dict] = {}
    for item in (raw.get("columns") or []):
        if not isinstance(item, dict):
            dropped += 1
            continue
        name = str(item.get("name", "") or "")
        if name not in fields or name in named:      # unknown column, or a repeat
            dropped += 1
            continue
        sem = str(item.get("semantic", "") or "")
        conf = _conf(item.get("confidence"))
        if sem not in SEMANTIC:
            dropped += 1
            sem, conf = "unknown", 0.0
        role = _capped(item.get("role"), "role")
        if role and not _grounded(role, blob):
            role, dropped = "", dropped + 1
        named[name] = {
            "semantic": model_field(sem, conf, original=name),
            "role": model_field(role, conf, original=name) if role else rule_field("", name),
            "rule_type": cols_meta.get(name, {}).get("rule_type", ""),
        }

    # Columns the model skipped are not left blank — the rules already have an
    # opinion, honestly labelled and honestly unconfident.
    for name in fields:
        if name in named:
            continue
        rt = cols_meta.get(name, {}).get("rule_type", "")
        named[name] = {
            "semantic": rule_field(rt if rt in SEMANTIC else "unknown", name),
            "role": rule_field("", name),
            "rule_type": rt,
        }
    out["columns"] = {f: named[f] for f in fields}       # source column order, always

    # --- brake 4: actions are licensed by the rule engine, not by the model ---
    licensed = {(e["id"], tuple(e["columns"])): e for e in actions.eligible(xr)}
    chosen: list[dict] = []
    seen: set[tuple] = set()
    for item in (raw.get("actions") or []):
        if not isinstance(item, dict):
            dropped += 1
            continue
        aid = str(item.get("id", "") or "")
        cols = [str(c) for c in (item.get("columns") or []) if isinstance(c, (str, int))]
        pair = (aid, tuple(cols))
        if aid not in actions.ACTIONS or pair not in licensed or pair in seen:
            dropped += 1
            continue
        why = _capped(item.get("why"), "why")
        if why and not _grounded(why, blob):
            why, dropped = "", dropped + 1
        # The rule's own strength is a FLOOR, not a starting suggestion. A model
        # that omits `confidence` — which gpt-oss does, because Ollama's `format`
        # is a hint and not a constraint — used to score 0.0 here and drop a
        # rule-licensed action into "rejected". That silently inverted the stated
        # contract two comments below: the model may rank the menu, it may not
        # remove items from it. Deterministic evidence ("89% of these cells parse
        # as a phone number") does not stop being true because a model went quiet.
        model_conf = _conf(item.get("confidence"))
        floor = _conf(licensed[pair].get("strength"))
        conf = max(model_conf, floor)
        src = "model" if model_conf > floor else "rule"
        seen.add(pair)
        chosen.append({
            "id": aid, "columns": cols, "source": src, "confidence": conf,
            "gate": enrich.gate(conf), "reason": licensed[pair]["reason"],
            "why": model_field(why, conf) if why else rule_field(licensed[pair]["reason"]),
            "params": _params_for(aid, cols, xr, out["suggested_key"]),
            "label": actions.ACTIONS[aid]["label"], "blurb": actions.ACTIONS[aid]["blurb"],
        })
    # Everything the rules licensed and the model didn't mention is still offered,
    # tagged as a rule at its own computed strength. The model may rank the menu;
    # it may not remove items from it.
    for pair, e in licensed.items():
        if pair in seen:
            continue
        chosen.append({
            "id": e["id"], "columns": list(e["columns"]), "source": "rule",
            "confidence": e["strength"], "gate": enrich.gate(e["strength"]),
            "reason": e["reason"], "why": rule_field(e["reason"]),
            "params": _params_for(e["id"], list(e["columns"]), xr, out["suggested_key"]),
            "label": actions.ACTIONS[e["id"]]["label"],
            "blurb": actions.ACTIONS[e["id"]]["blurb"],
        })
    order = {a: i for i, a in enumerate(ACTION_IDS)}
    chosen.sort(key=lambda a: (order.get(a["id"], 99), a["columns"]))
    out["actions"] = chosen

    # --- the classify proposal: the one thing a human MUST edit ---
    taxonomy = []
    for v in (raw.get("taxonomy_proposal") or []):
        s = str(v).strip()
        if s and len(s) <= MAX_TAXONOMY_LEN and s not in taxonomy:
            taxonomy.append(s)
        elif s:
            dropped += 1
    taxonomy = taxonomy[:MAX_TAXONOMY]
    cls = next((a for a in chosen if a["id"] == "classify"), None)
    out["classify"] = {}
    if cls:
        tax_source = "model"
        if len(taxonomy) < 2:                    # too thin to be a closed list
            taxonomy = _default_taxonomy(xr, cls["columns"][0])
            tax_source = "rule"
        if len(taxonomy) < 2:
            # One allowed value is not a classification, it is a constant. Rather
            # than offer a box a human has to fill from nothing, take the action
            # off the menu — the rules could not licence it after all.
            chosen.remove(cls)
        else:
            target = _target_name(raw.get("classify_target"), fields) or _target_name(
                f"{cls['columns'][0]}_class", fields)
            instruction = _capped(raw.get("classify_instruction"), "summary") or (
                "Pick the single best value from the allowed list for each row.")
            cls["params"] = {"to": target, "multi": bool(raw.get("classify_multi")),
                             "taxonomy": taxonomy, "instruction": instruction,
                             "taxonomy_source": tax_source}
            out["classify"] = cls["params"]

    labels = [f for f in (raw.get("label_fields") or []) if f in fields]
    out["label_fields"] = labels or fields[:1]
    out["dropped"] = dropped
    return out, dropped, (
        f"{dropped} model claim(s) dropped as ungrounded or out-of-vocabulary"
        if dropped else "")


async def analyze(xr: dict, model: str = enrich.DEFAULT_MODEL,
                  records: list[dict] | None = None) -> tuple[dict, dict]:
    """Name this list. Returns (analysis, stats). Never raises, never blocks on a brain.

    With model="none", no API key, or any transport failure, the analysis is built
    from the X-ray alone and every field says so. The page is fully functional
    either way — that is principle 6 expressed in control flow rather than in a
    paragraph of marketing."""
    model = model if model in enrich.MODELS else enrich.DEFAULT_MODEL
    payload = profile_payload(xr, records)
    raw, tokens, err = await _ask(model, payload)
    used = model if raw else "none"
    analysis, dropped, note = validate(raw, xr, used, payload)
    analysis["note"] = " · ".join(n for n in (err, note) if n)
    stats = {
        "model": used,
        "prompt_version": PROMPT_VERSION if raw else "",
        "tokens": tokens,
        "dropped": dropped,
        "note": analysis["note"],
    }
    return analysis, stats
