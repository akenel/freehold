"""Freehold — the enrichment step (bring your own brain).

The pack used to be pull → transform → store → record. This inserts one step:

    pull → transform → **enrich** → store → record

Enrichment is where messy master data gets cleaned, classified and completed.
It is NOT where we fetch trivia — a weather lookup is an HTTP call, not a model.
The model is here for the jobs no regex can do: "which industry is this company
in?", "are these two customers the same person?", "what category does this
article belong to?"

Four rules, and they are the entire product:

  1. **Rules first, model second.** Deterministic wins every time it can. The
     model only ever sees the rows the rules could not resolve. Cheap, fast,
     stable, and it shrinks the surface where a model can be wrong.
  2. **Provenance on every written value.** Each enriched field carries who
     wrote it (rule / model / source), which model, which prompt version, how
     confident, and when. No silent AI edits, ever.
  3. **The original is never destroyed.** We add alongside; we don't overwrite.
     A bad enrichment is always reversible because the input is still there.
  4. **A human gate.** Confidence decides: auto-apply, queue for review, or
     reject. The client sets the thresholds. Nothing sneaks into master data.

Bring-your-own-brain: the model is chosen per run from MODELS below and recorded
on the run, so six months later you know exactly which brain touched which row —
and you can replay the same payload through a better one and diff the result.
Pick "none" and the pipeline still runs on rules alone; that is the honest
baseline, and it proves the plumbing doesn't depend on the AI.
"""
import json
import os
import re
from dataclasses import dataclass, field as dc_field
from datetime import datetime, timezone

import httpx

# --- the brain shelf -------------------------------------------------------
# Hosted off-box on Ollama Turbo (same key the Open WebUI pack uses). Add or
# remove rows freely — this dict *is* the model picker in the UI. Swap the base
# URL for a local Ollama and nothing else changes; that's the BYO-brain promise.
MODELS: dict[str, str] = {
    "none": "Rules only (no AI) — the honest baseline",
    "gpt-oss:20b": "gpt-oss 20B — fast, cheap, good enough for tagging",
    "gpt-oss:120b": "gpt-oss 120B — the default workhorse",
    "deepseek-v3.1:671b": "DeepSeek V3.1 — heavyweight, slower, sharper",
    "qwen3-coder:480b": "Qwen3 Coder 480B — strong at structured output",
}
DEFAULT_MODEL = "gpt-oss:120b"

_BASE = os.getenv("OLLAMA_BASE_URL", "https://ollama.com").rstrip("/")
_KEY = os.getenv("OLLAMA_API_KEY", "")

# Bump this whenever the prompt text below changes. It rides along on every
# value the model writes, so an enrichment is always reproducible — and you can
# find every row written by the prompt you later discovered was wrong.
PROMPT_VERSION = "contact-enrich-v1"

# The human gate. Client-configurable in a real deployment; sane defaults here.
AUTO_ABOVE = 0.90      # >= this → applied automatically
REVIEW_ABOVE = 0.70    # >= this → queued for a human; below → rejected outright

AUTO, REVIEW, REJECTED = "auto", "review", "rejected"


# --- the provenance envelope ----------------------------------------------
def field(value, *, original=None, source="rule", model="",
          confidence=1.0, prompt_version="") -> dict:
    """Wrap one enriched value in its paper trail.

    This little dict is the whole compliance story: what we wrote, what it came
    from, who decided it, how sure they were, and when. Everything downstream —
    the diff pane, the review queue, the audit row — reads this shape.
    """
    return {
        "value": value,
        "original": original,
        "source": source,                 # "source" | "rule" | "model"
        "model": model,
        "prompt_version": prompt_version,
        "confidence": round(float(confidence), 2),
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def as_confidence(value) -> float:
    """A confidence, clamped to 0..1, from whatever the model actually sent.

    `float()` on raw model output is a live grenade: a model that answers
    `"confidence": "high"` used to raise ValueError out of enrich(), through the
    caller, and into a 500 — after the recipe was saved and the draft deleted.
    Unnumberable means zero, which the gate then sends to a human. That is the
    safe direction to fail."""
    try:
        c = float(value)
    except (TypeError, ValueError):
        return 0.0
    if c != c:                                  # NaN compares unequal to itself
        return 0.0
    return max(0.0, min(1.0, c))


def gate(confidence: float) -> str:
    """Auto-apply, hand to a human, or bin it. The decision tree, in one line."""
    if confidence >= AUTO_ABOVE:
        return AUTO
    return REVIEW if confidence >= REVIEW_ABOVE else REJECTED


# --- step 1: the rules (deterministic, free, boring, correct) --------------
_EXT = re.compile(r"\s*(x|ext\.?|extension)\s*\d+", re.I)
# A phone-ish run of characters. Deliberately greedy about separators (real
# spreadsheet cells wrap over newlines) and stopped by any letter.
_RUN = re.compile(r"\+?\d[\d\s(). \-]{5,}\d")


def candidates(raw: str) -> list[str]:
    """Every phone number we can confidently pull out of a messy cell, E.164.

    Master data does not arrive as one number per field. It arrives as
    "+31 20 -The Netherlands Tel: +31 (0)207 975 000 - Amsterdam office
    or +44 207 549 4040)". Finding *all* of them is what lets us say the cell is
    ambiguous instead of silently keeping whichever one came first."""
    if not raw:
        return []
    text = _EXT.sub("", raw).replace("(0)", "").replace("(0 )", "")
    out: list[str] = []
    for run in _RUN.findall(text):
        plus = run.strip().startswith("+")
        digits = re.sub(r"\D", "", run)
        if digits.startswith("00"):                        # 0041… international
            digits, plus = digits[2:], True
        if len(digits) < 7:
            continue
        if plus:
            num = f"+{digits}" if 8 <= len(digits) <= 15 else ""
        elif len(digits) == 10 and digits[0] in "23456789":
            # NANP without a country code. The leading-digit check matters: a
            # NANP area code never starts with 0 or 1, so "020 36 30 310" (a
            # Dutch local number) is correctly declined instead of being
            # mangled into a US number. Found this the hard way on real data.
            num = f"+1{digits}"
        elif len(digits) == 11 and digits.startswith("1"):
            num = f"+{digits}"
        else:
            num = ""                                       # no country context — decline
        if num and num not in out:
            out.append(num)
    return out


def phone_e164(raw: str) -> dict | None:
    """Normalize a phone number by rule alone. Returns None if we can't be sure —
    that 'None' is the handoff to the model, and keeping it honest is the point.

    Deliberately conservative: a wrong phone number in master data is worse than
    an absent one, so anything ambiguous (nothing found, or *several* found)
    falls through rather than guessing."""
    found = candidates(raw)
    return field(found[0], original=raw) if len(found) == 1 else None


def reconcile(rec: dict, a: str, b: str) -> dict | None:
    """Two columns claiming the same fact — do they agree? Pure rule, no model.

    Every real spreadsheet has this: a tidy PHONE column and a pasted blob that
    also contains a number. Nobody knows which is right, so nobody trusts either.
    Saying "these two agree" (or "these two disagree, here's both") is one of the
    most valuable things you can hand back, and it needs no AI whatsoever."""
    ca, cb = candidates(str(rec.get(a, ""))), candidates(str(rec.get(b, "")))
    if not ca and not cb:
        return None
    sa, sb = set(ca), set(cb)
    if sa and sb:
        status = "agree" if sa == sb else ("overlap" if sa & sb else "conflict")
    else:
        status = f"only_{a if sa else b}"
    return field(
        {"status": status, a: ca, b: cb},
        original=f"{rec.get(a, '')} | {rec.get(b, '')}"[:120], source="rule",
    )


_QUALITY_FIELDS = ("name", "email", "company", "phone", "city")


def quality(rec: dict, fields: tuple[str, ...] = _QUALITY_FIELDS) -> dict:
    """Completeness score + the list of what's missing. Pure rule, no model.

    This is the field that sells the whole pack in a demo: point it at a client's
    real spreadsheet and it instantly says 'you are missing 340 emails'."""
    missing = [f for f in fields if not str(rec.get(f, "")).strip()]
    score = round(1 - len(missing) / len(fields), 2)
    return field({"score": score, "missing": missing}, original=None, source="rule")


# --- profiles: one engine, many kinds of master data -----------------------
@dataclass(frozen=True)
class Profile:
    """What "enriched" means for one kind of record.

    The rules (phones, completeness, reconciliation) are universal. What changes
    between a CRM contact, a product catalogue and a call list is *which* columns
    hold what, and what the model is being asked to decide. Keeping that in a
    profile — rather than in the code — is what makes this an engine instead of
    a one-off script, and it's the seam where a new client's data plugs in."""
    key: str
    label: str
    quality_fields: tuple[str, ...]
    phone_field: str = ""
    reconcile_with: str = ""
    target: str = ""                      # the field the model writes
    taxonomy: tuple[str, ...] = ()        # the allowed values — a closed list, on purpose
    feed: tuple[str, ...] = ()            # which columns the model gets to see
    instruction: str = ""
    multi: bool = False                   # may the answer be several taxonomy values?
    label_fields: tuple[str, ...] = dc_field(default=("name",))  # what to call a row


PROFILES: dict[str, Profile] = {
    "contacts": Profile(
        key="contacts", label="CRM contacts",
        quality_fields=("name", "email", "company", "phone", "city"),
        phone_field="phone",
        target="industry",
        taxonomy=("Software", "Manufacturing", "Retail", "Logistics", "Healthcare",
                  "Finance", "Construction", "Hospitality", "Media", "Education",
                  "Energy", "Other"),
        feed=("company", "slogan", "keywords"),
        instruction="Pick the single best industry for this company from the taxonomy.",
        label_fields=("name",),
    ),
    "call_list": Profile(
        key="call_list", label="Agency call list",
        quality_fields=("agency", "market", "phone", "ask_for", "first_move", "website"),
        phone_field="phone", reconcile_with="phone_2",
        target="markets",
        # The first live run on the real call list rejected 21 of 45 rows: the
        # model kept honestly answering "Other, confidence 0.3" for Nordics and
        # US entries because they had no code to map to. That is the taxonomy
        # telling you it's incomplete — a config fix, not a code fix, which is
        # exactly the point of keeping it here.
        taxonomy=("NL", "DE", "CH", "AT", "BE", "FR", "UK", "IE", "LU",
                  "SE", "NO", "FI", "DK", "IT", "ES", "PL", "US", "EU", "Other"),
        feed=("agency", "market", "why_them", "website"),
        instruction=(
            "Normalize the free-text market column into ISO 3166-1 alpha-2 country "
            "codes from the taxonomy. Several codes are allowed — return them "
            "comma-separated, most important first. Use EU only when the text means "
            "the whole region rather than named countries."
        ),
        multi=True,
        label_fields=("agency",),
    ),
}


# --- step 2: the model (only for what rules couldn't resolve) --------------
_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "i": {"type": "integer"},
                    "label": {"type": "string"},
                    "confidence": {"type": "number"},
                    "phone_e164": {"type": "string"},
                    "phone_confidence": {"type": "number"},
                },
                "required": ["i", "label", "confidence"],
            },
        }
    },
    "required": ["results"],
}

_SYSTEM = (
    "You are a master-data enrichment engine. You classify and normalize business "
    "records. Answer ONLY with the requested JSON. Never invent facts you cannot "
    "derive from the input. If you are unsure, say so with a LOW confidence number "
    "rather than guessing — a low-confidence answer is queued for a human, a "
    "confident wrong answer corrupts a customer's master data."
)


def _task(p: Profile) -> str:
    """The instruction, assembled from the profile. Changing a taxonomy is a
    config edit, not a code edit — and PROMPT_VERSION below pins what was sent."""
    return (
        f"{p.instruction}\n"
        f"Allowed values for `label` ({p.target}): [{', '.join(p.taxonomy)}].\n"
        + ("`label` may contain several allowed values, comma-separated.\n"
           if p.multi else "`label` must be exactly one allowed value.\n")
        + "If a record includes `phone_raw`, also normalize it to E.164 (leading +, "
          "digits only, no extension). If the cell holds several different numbers, "
          "or you cannot tell the country, omit phone_e164 entirely.\n"
          "Confidences are 0.0-1.0 and must be honest. 'Other' takes a low confidence."
    )


def _coerce(content: str) -> list[dict]:
    """Pull the result rows out of whatever shape the model actually returned.

    We ask for {"results": [...]} and declare a JSON schema, but `format` is a
    hint that not every model honours — gpt-oss cheerfully returns a bare array
    instead. Being liberal here is the difference between 'the AI silently did
    nothing' and a working pipeline, and it costs four lines."""
    data = json.loads(content)
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)]
    if isinstance(data, dict):
        if isinstance(data.get("results"), list):
            return [r for r in data["results"] if isinstance(r, dict)]
        for v in data.values():                     # any single list of rows will do
            if isinstance(v, list) and v and isinstance(v[0], dict):
                return v
        if "i" in data:                             # a lone row, unwrapped
            return [data]
    return []


async def _ask_model(model: str, profile: Profile,
                     payload: list[dict]) -> tuple[list[dict], int, str]:
    """One batched call to the brain. Returns (results, tokens_used, error).

    Any failure — no key, network, bad JSON, model down — returns empty and the
    run continues on rules alone. The AI is an *enhancement* to the pipeline,
    never a dependency of it. A sync must never fail because a model was busy.

    But it must never fail *silently* either: the reason comes back as `error`
    and rides along in the run's stats. A pipeline that quietly stops enriching
    is worse than one that breaks loudly."""
    if model == "none":
        return [], 0, ""
    if not payload:
        return [], 0, ""
    if not _KEY:
        return [], 0, "no OLLAMA_API_KEY set — ran on rules alone"
    body = {
        "model": model,
        "stream": False,
        "format": _SCHEMA,
        "options": {"temperature": 0},   # determinism as far as a model allows
        "messages": [
            {"role": "system", "content": _SYSTEM},
            {"role": "user",
             "content": f"{_task(profile)}\n\nRecords:\n{json.dumps(payload, ensure_ascii=False)}"},
        ],
    }
    try:
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(
                f"{_BASE}/api/chat",
                headers={"Authorization": f"Bearer {_KEY}"},
                json=body,
            )
            r.raise_for_status()
            data = r.json()
        tokens = int(data.get("prompt_eval_count", 0)) + int(data.get("eval_count", 0))
        return _coerce(data["message"]["content"]), tokens, ""
    except Exception as exc:  # noqa: BLE001 — a busy brain must never break the pipeline
        return [], 0, f"{type(exc).__name__}: {exc}"[:200]


# --- the step itself -------------------------------------------------------
async def enrich(records: list[dict], model: str = DEFAULT_MODEL,
                 profile: str = "contacts", batch: int = 25) -> tuple[list[dict], dict]:
    """Enrich a batch of records. Returns (enveloped_records, stats).

    Each returned record keeps its source fields untouched and gains:
      _enriched — {field: provenance envelope}
      _gate     — "auto" | "review" | "rejected", the human decision hint
      _label    — a human name for the row, for the review UI
    """
    model = model if model in MODELS else DEFAULT_MODEL
    p = PROFILES.get(profile) or PROFILES["contacts"]

    out: list[dict] = []
    for rec in records:
        out.append({
            **rec,
            "_label": " ".join(str(rec.get(f, "")) for f in p.label_fields).strip() or "—",
            "_enriched": {"quality": quality(rec, p.quality_fields)},
            "_gate": AUTO,
        })

    # Rules pass: resolve what we can for free, and note what we couldn't.
    unresolved: set[int] = set()
    for i, rec in enumerate(out):
        if p.reconcile_with:
            got = reconcile(rec, p.phone_field, p.reconcile_with)
            if got:
                rec["_enriched"]["phone_check"] = got
        if not p.phone_field:
            continue
        raw = str(rec.get(p.phone_field, ""))
        got = phone_e164(raw)
        if got:
            rec["_enriched"]["phone_e164"] = got
        elif raw.strip():
            unresolved.add(i)          # ambiguous or unknown country — ask the brain

    # Model pass, in batches: the profile's target for everyone, phones only
    # where the rules gave up. Batching keeps one bad row from costing the run.
    results: list[dict] = []
    tokens, note = 0, ""
    for start in range(0, len(out), batch):
        ask = []
        for i in range(start, min(start + batch, len(out))):
            rec = out[i]
            item = {"i": i, **{f: rec.get(f, "") for f in p.feed}}
            if i in unresolved:
                item["phone_raw"] = rec.get(p.phone_field, "")
            ask.append(item)
        got, used, err = await _ask_model(model, p, ask)
        results.extend(got)
        tokens += used
        note = note or err          # keep the first reason the brain didn't answer

    used_model = model if results else "none"
    enriched_count = 0
    for res in results:
        i = res.get("i")
        if not isinstance(i, int) or not (0 <= i < len(out)):
            continue
        rec = out[i]
        rec["_enriched"][p.target] = field(
            res.get("label", ""), original=" / ".join(
                str(rec.get(f, "")) for f in p.feed[:2] if rec.get(f)),
            source="model", model=model, confidence=as_confidence(res.get("confidence")),
            prompt_version=PROMPT_VERSION,
        )
        enriched_count += 1
        if res.get("phone_e164"):
            rec["_enriched"]["phone_e164"] = field(
                res["phone_e164"], original=rec.get(p.phone_field, ""), source="model",
                model=model, confidence=as_confidence(res.get("phone_confidence")),
                prompt_version=PROMPT_VERSION,
            )

    # The gate: a record is only as trustworthy as its least-confident AI field.
    for rec in out:
        confs = [f["confidence"] for f in rec["_enriched"].values() if f["source"] == "model"]
        rec["_gate"] = gate(min(confs)) if confs else AUTO

    stats = {
        "profile": p.key,
        "model": used_model,
        "prompt_version": PROMPT_VERSION if results else "",
        "enriched_count": enriched_count,
        "tokens": tokens,
        "review_count": sum(1 for r in out if r["_gate"] != AUTO),
        "note": note,               # why the brain didn't answer, if it didn't
    }
    return out, stats
