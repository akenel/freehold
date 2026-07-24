"""Freehold — the recipe: what a human approved, frozen as config.

This is the module that makes the whole feature honest rather than clever.

A model proposed a mapping. A human looked at it, edited the taxonomy, unticked
two things and ticked a box. From that moment on the prompt is irrelevant: what
is saved is a **spec** — a list of named actions with frozen parameters — and
every future run of that spec does exactly the same arithmetic, in the same
order, whether or not any model is reachable. That is "AI at design time,
deterministic at run time", written down as a file format instead of a slogan.

Two consequences worth stating out loud:

  * `spec_sha` deliberately excludes `version` and `derived_from`. Two versions
    with identical mappings hash identically — so the recipe screen can say
    "same mapping, different brain" and mean it. That comparison is exactly what
    the user asked for, and it is only trustworthy because the X-ray is
    deterministic and the spec is a hash.
  * The version chain is append-only, like AuditEvent. A recipe is never
    deleted and a version is never rewritten; `archived` is the only mutation
    besides appending. If the mapping that ran last March was wrong, you need to
    be able to read it, not to discover it has been tidied away.

There is no table for any of this. A recipe is one JSON object in the private
vault, which is why this feature ships with alembic head still at 0005.

Import note: `vault` is imported lazily inside the persistence functions on
purpose. Everything above them is pure, so the tests that matter run on a laptop
with no MinIO, no Postgres and no API key.
"""
import copy
import hashlib
import json
import re
from datetime import datetime, timezone

import actions
import analyze
import enrich
import xray

SPEC_VERSION = 1
ROW_LIMIT = 5000            # what inbound.read_xlsx will read, stated in the spec

# Actions that can only appear once in a recipe, and why:
#   normalize_phone / reconcile_phones — enrich.Profile has ONE phone_field
#   score_quality / classify           — one quality score, one target field
#   dedupe                             — one `dupe_of` envelope per record, and
#                                        "which row survives" is ambiguous with two keys
#   build_schema                       — one table definition
# The rest (canonicalize, parse_dates, split, validate_email) write per-column
# envelopes and may appear as often as there are columns.
SINGLETON = ("normalize_phone", "reconcile_phones", "score_quality", "classify",
             "dedupe", "build_schema")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def slug(text: str, cap: int = 40) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(text or "").casefold()).strip("-")[:cap].strip("-")


def spec_sha(spec: dict) -> str:
    """The identity of a MAPPING, not of a version.

    `version` and `derived_from` are excluded so that re-approving the same
    mapping after a run with a different brain produces the same hash. If two
    versions hash the same, the only thing that changed is who proposed it."""
    body = {k: v for k, v in spec.items() if k not in ("version", "derived_from")}
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


# --- building the spec from a screen full of ticks -------------------------
def build(xr: dict, analysis: dict, form: dict) -> dict:
    """Turn (what the cells say, what the model proposed, what the human ticked)
    into one immutable mapping. The human's ticks win every disagreement."""
    fields = list(xr.get("columns", {}))
    proposed = {(a["id"], tuple(a["columns"])): a for a in analysis.get("actions", [])}

    acts: list[dict] = []
    seen: set[tuple] = set()
    for token in form.get("actions", []):
        aid, _, colstr = str(token).partition(":")
        cols = [c for c in colstr.split("|") if c]
        if aid not in actions.ACTIONS or (aid, tuple(cols)) in seen:
            continue
        seen.add((aid, tuple(cols)))
        params = dict((proposed.get((aid, tuple(cols))) or {}).get("params", {}))

        if aid == "score_quality":
            cols = list(form.get("quality_cols") or cols)
        elif aid == "parse_dates" and form.get("parse_from") in (
                "auto", "excel_serial", "iso", "dmy", "mdy"):
            params = {"from": form["parse_from"]}
        elif aid == "classify":
            cols = list(form.get("classify_feed") or cols)
            taxonomy = [t.strip() for t in form.get("classify_taxonomy", []) if t.strip()]
            params = {
                "to": analyze._target_name(form.get("classify_to", ""), fields)
                      or params.get("to", "category"),
                "multi": bool(form.get("classify_multi")),
                "taxonomy": list(dict.fromkeys(taxonomy))[:analyze.MAX_TAXONOMY]
                            or list(params.get("taxonomy", ())),
                "instruction": (form.get("classify_instruction") or "").strip()
                               or params.get("instruction", ""),
            }
        elif aid == "build_schema":
            cols = []
            params = {"table": actions.ident(form.get("schema_table")
                                             or slug(form.get("key", "")).replace("-", "_"),
                                             "list_table")}
        acts.append({"id": aid, "columns": cols, "params": params})

    semantics = {}
    for col in fields:
        meta = analysis.get("columns", {}).get(col, {})
        sem = meta.get("semantic") or {}
        role = meta.get("role") or {}
        semantics[col] = {
            "semantic": sem.get("value", "unknown"),
            "source": sem.get("source", "rule"),
            "confidence": sem.get("confidence", 0.0),
            "role": role.get("value", ""),
        }

    spec = {
        "spec_version": SPEC_VERSION,
        "key": slug(form.get("key") or analysis.get("suggested_key") or "list"),
        "label": (form.get("label") or analysis.get("title", {}).get("value")
                  or "Untitled list")[:120],
        "version": 0,                       # save() mints the real one
        "summary": analysis.get("summary", {}).get("value", "")[:240],
        "list_kind": analysis.get("list_kind", {}).get("value", "other"),
        "inbound": {"kind": "xlsx", "sheet": int(form.get("sheet", 0) or 0),
                    "limit": ROW_LIMIT},
        "label_fields": list(form.get("label_fields") or analysis.get("label_fields") or []),
        "semantics": semantics,
        "actions": acts,
        "derived_from": {
            "model": analysis.get("model", "none"),
            "prompt_version": analysis.get("prompt_version", ""),
            "at": _now(),
            "src_key": form.get("src_key", ""),
            "xray_sha": xr.get("sha", ""),
        },
    }
    return spec


def validate(spec: dict, fields: list[str] | None = None) -> tuple[dict, list[str]]:
    """Last check before a mapping becomes permanent. Returns (spec, warnings).

    Warnings are shown, not swallowed: a recipe that quietly dropped the action a
    human ticked is worse than one that says it did."""
    warnings: list[str] = []
    spec = copy.deepcopy(spec)
    fields = list(fields if fields is not None else spec.get("semantics", {}))

    spec["key"] = slug(spec.get("key")) or "list"
    spec["label"] = (str(spec.get("label") or "").strip() or spec["key"])[:120]

    kept: list[dict] = []
    for a in spec.get("actions", []):
        aid = a.get("id")
        if aid not in actions.ACTIONS:
            warnings.append(f"dropped unknown action '{aid}'")
            continue
        cols = [c for c in a.get("columns", []) if c in fields]
        if len(cols) != len(a.get("columns", [])):
            warnings.append(f"'{aid}' referenced a column that isn't in this sheet")
        if aid == "build_schema":
            cols = []
        elif aid == "score_quality" and not cols:
            # Never dropped and never empty: enrich.quality() divides by len(fields).
            cols = fields[:1]
            warnings.append("'score_quality' had no columns — scoring the first one")
        elif not cols:
            warnings.append(f"dropped '{aid}' — it had no usable column")
            continue
        if aid == "reconcile_phones" and len(cols) < 2:
            warnings.append("dropped 'reconcile_phones' — it needs two columns")
            continue
        if aid == "classify":
            tax = [t for t in a.get("params", {}).get("taxonomy", []) if str(t).strip()]
            if len(tax) < 2:
                warnings.append("dropped 'classify' — a closed list needs at least "
                                "two allowed values")
                continue
            a["params"]["taxonomy"] = tax
            a["params"]["to"] = analyze._target_name(a["params"].get("to", ""), fields) \
                or "category"
        a["columns"] = cols
        a.setdefault("params", {})
        kept.append(a)

    # Collapse the ones that can only run once. Loudly: a recipe that quietly
    # ignored the second phone column a human ticked is worse than one that says
    # "I kept 'telefon' and dropped 'telefon_2', here's why."
    once: set[str] = set()
    kept2: list[dict] = []
    for a in kept:
        if a["id"] in SINGLETON and a["id"] in once:
            warnings.append(f"'{a['id']}' can only run once per recipe — kept the first, "
                            f"dropped the one on {', '.join(a['columns']) or 'this list'}")
            continue
        once.add(a["id"])
        kept2.append(a)

    order = {aid: i for i, aid in enumerate(actions.ACTION_IDS)}
    spec["actions"] = sorted(kept2, key=lambda a: (order[a["id"]], a["columns"]))

    # The two guards enrich.py cannot make for itself. See actions.profile_from.
    quality = next((a for a in spec["actions"] if a["id"] == "score_quality"), None)
    if quality and not quality["columns"]:
        quality["columns"] = fields[:1]
    spec["label_fields"] = [f for f in spec.get("label_fields", []) if f in fields] \
        or fields[:1]
    return spec, warnings


# --- persistence (the only part that touches the vault) --------------------
def _doc_key(key: str) -> str:
    return f"recipes/{slug(key)}.json"


def load_doc(key: str) -> dict | None:
    """The whole recipe object: metadata + every version ever approved."""
    import vault
    return vault.get_json(_doc_key(key))


def save(spec: dict, approved_by: str, note: str = "",
         warnings: list[str] | None = None) -> tuple[str, int]:
    """Append version N+1. Returns (key, version). Never rewrites a version.

    `warnings` rides along on the version so the recipe screen can show what
    validate() dropped between the ticks and the saved mapping. A silent
    difference between "what I approved" and "what runs" is the one thing a
    versioned artefact must never have."""
    import vault
    key = slug(spec.get("key")) or "list"
    doc = load_doc(key) or {
        "key": key, "label": spec.get("label", key), "created_by": approved_by,
        "created_at": _now(), "current": 0, "archived": False, "versions": [],
    }
    version = int(doc.get("current", 0)) + 1
    stored = {**copy.deepcopy(spec), "key": key, "version": version}
    doc["versions"].append({
        "version": version, "spec": stored, "spec_sha": spec_sha(stored),
        "approved_by": approved_by, "approved_at": _now(), "note": note[:200],
        "warnings": list(warnings or []),
    })
    doc["current"] = version
    doc["label"] = stored.get("label", doc["label"])
    vault.put_json(doc, _doc_key(key))
    return key, version


def load(key: str, version: int | None = None) -> dict | None:
    """One version's spec — the current one unless you name another."""
    doc = load_doc(key)
    if not doc or not doc.get("versions"):
        return None
    want = version or doc.get("current")
    for v in reversed(doc["versions"]):
        if v["version"] == want:
            return v["spec"]
    return doc["versions"][-1]["spec"]


def index() -> list[dict]:
    """Every recipe on the box, newest approval first — the cards on /lists."""
    import vault
    out = []
    for name in vault.list_prefix("recipes/"):
        doc = vault.get_json(name)
        if not doc or not doc.get("versions"):
            continue
        last = doc["versions"][-1]
        out.append({
            "key": doc["key"], "label": doc.get("label", doc["key"]),
            "current": doc.get("current", 0), "archived": bool(doc.get("archived")),
            "approved_by": last.get("approved_by", ""),
            "approved_at": last.get("approved_at", ""),
            "spec_sha": last.get("spec_sha", ""), "versions": len(doc["versions"]),
            "actions": [a["id"] for a in last["spec"].get("actions", [])],
        })
    return sorted(out, key=lambda r: r["approved_at"], reverse=True)


# --- running it ------------------------------------------------------------
async def run(spec: dict, records: list[dict], model: str = enrich.DEFAULT_MODEL,
              xr: dict | None = None) -> tuple[list[dict], dict, dict]:
    """Execute an approved recipe. Returns (records, stats, extra).

    `stats` is the *unmodified* enrich.enrich stats dict — same seven keys the
    Business Hub template and BusinessHubRun already read, so a list run shows up
    in the existing run log and the existing before→after pane with no new code
    and no second result screen. Everything this feature invented lives in
    `extra`, deliberately kept out of the shape other modules depend on.
    """
    p, override = actions.profile_from(spec)
    ids = {a["id"] for a in spec.get("actions", [])}

    # enrich.PROFILES *is* the registry, and registering here is how we reuse the
    # engine with zero edits to enrich.py. The assert matters: enrich.enrich()
    # silently falls back to PROFILES["contacts"] on an unknown key, which would
    # enrich a customer's list against somebody else's mapping and look fine.
    enrich.PROFILES[p.key] = p
    assert p.key in enrich.PROFILES, "transient profile did not register"
    try:
        out, stats = await enrich.enrich(list(records), model=(override or model),
                                         profile=p.key)
    finally:
        enrich.PROFILES.pop(p.key, None)

    # enrich writes `quality` unconditionally in its seed pass, and writes
    # `phone_e164` for whatever phone_field the profile carries — which may be
    # set purely so reconcile_phones has a left-hand side. If nobody ticked
    # those actions, take the fields back out: "nothing runs that you didn't
    # tick" has to be literally true, not nearly true.
    for aid, key in (("score_quality", "quality"), ("normalize_phone", "phone_e164")):
        if aid not in ids:
            for rec in out:
                rec["_enriched"].pop(key, None)

    action_stats: dict[str, dict] = {}
    schema_sql = ""

    def tally(aid: str, got: dict) -> None:
        """Several instances of one action (two columns to split, say) report as
        one set of numbers — the screen asks "how many cells", not "how many ticks"."""
        have = action_stats.setdefault(aid, {})
        for k, v in got.items():
            have[k] = have.get(k, 0) + v if isinstance(v, int) else v

    for aid in actions.POST_ORDER:
        for a in spec.get("actions", []):
            if a.get("id") != aid:
                continue
            cols = a.get("columns", [])
            params = a.get("params", {})
            if aid == "canonicalize_values":
                tally(aid, actions.canonicalize(out, cols[0], params.get("map", {})))
            elif aid == "parse_dates":
                tally(aid, actions.parse_dates(out, cols[0], params.get("from", "auto")))
            elif aid == "split_multivalue":
                tally(aid, actions.split_multivalue(out, cols[0], params.get("sep", "/")))
            elif aid == "validate_email":
                tally(aid, actions.validate_email(out, cols[0]))
            elif aid == "dedupe":
                tally(aid, actions.dedupe(out, cols))
            elif aid == "build_schema":
                shot = xr if xr is not None else xray.xray(
                    list(spec.get("semantics", {})), records,
                    spec.get("label", ""), str(spec.get("inbound", {}).get("sheet", 0)))
                schema_sql = actions.build_schema(spec, shot)
                tally(aid, {"tables": schema_sql.count("CREATE TABLE"),
                            "lines": len(schema_sql.splitlines())})

    extra = {
        "actions": [a["id"] for a in spec.get("actions", [])],
        "action_stats": action_stats,
        "schema_sql": schema_sql,
        "recipe": {"key": spec.get("key", ""), "version": spec.get("version", 0),
                   "spec_sha": spec_sha(spec)},
        "xray_sha": (xr or {}).get("sha", "") or spec.get("derived_from", {}).get("xray_sha", ""),
        "src_key": spec.get("derived_from", {}).get("src_key", ""),
    }
    return out, stats, extra
