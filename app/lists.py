"""Freehold — List Intake: upload → X-ray → name it → approve → run it forever.

The spine, and the order matters:

    upload  → the original goes into the PRIVATE vault, under an unguessable key
            → inbound.read_xlsx → xray()        (pure, deterministic, no model)
            → analyze()                         (the model names things, never counts)
            → a throwaway draft in the vault
            → A HUMAN edits, ticks and approves ← the gate
            → RecipeVersion N, immutable, spec_sha'd
            → recipes.run() → enrich.enrich() + the deterministic post-pass
            → a report in MinIO + a BusinessHubRun row + an audit row

Between the upload and the approval, **nothing durable is written except the
original blob and a deletable draft**. There is no database row for a mapping
nobody approved. That is principle 4 — the human gate — expressed in the schema
rather than in the UI, which is the only place it can't be quietly bypassed.

The run deliberately produces the *identical* artefacts the Business Hub already
produces: the same report shape, the same BusinessHubRun columns, the same audit
detail keys. So a list run appears in the existing run log and the existing
before→after pane with no new code and no second result screen — and there is no
second screen to drift out of sync with the first one.
"""
import io
import json
import re
import secrets
from datetime import datetime, timezone

import actions
import analyze
import audit
import business_hub
import inbound
import recipes
import vault
import xray
from db import async_session
from models import BusinessHubRun

MAX_UPLOAD = 10 * 1024 * 1024      # 10 MiB, enforced after the read (see routers/lists.py)
MAX_TABS = 12                      # how many tabs we preview headers for
XLSX_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def is_xlsx(filename: str, blob: bytes) -> bool:
    """Suffix + magic number, deliberately NOT content-type.

    Browsers hand us application/octet-stream for .xlsx often enough that a
    content-type allowlist rejects real files from real customers. The zip magic
    is the honest check; anything that gets past it fails in read_xlsx, which we
    catch."""
    return bool(filename) and filename.lower().endswith(".xlsx") \
        and blob[:4] == b"PK\x03\x04"


# --- drafts ----------------------------------------------------------------
def draft_key(token: str) -> str:
    return f"{vault.DRAFTS}{token}.json"


def draft_load(token: str) -> dict | None:
    if not re.fullmatch(r"[0-9a-f]{32}", token or ""):
        return None
    return vault.get_json(draft_key(token))


def draft_save(draft: dict) -> str:
    vault.put_json(draft, draft_key(draft["token"]))
    return draft["token"]


def draft_discard(token: str) -> None:
    """Bins the mapping. Leaves the original alone — it is the customer's file,
    and "I discarded a draft" is not "I want my upload destroyed"."""
    if re.fullmatch(r"[0-9a-f]{32}", token or ""):
        vault.delete(draft_key(token))


def open_drafts(owner: str = "") -> list[dict]:
    out = []
    for name in vault.list_prefix(vault.DRAFTS):
        d = vault.get_json(name) or {}
        if not d.get("token") or (owner and d.get("owner") != owner):
            continue
        out.append({"token": d["token"], "filename": d.get("filename", ""),
                    "at": d.get("at", ""), "rows": d.get("xray", {}).get("row_count", 0),
                    "model": d.get("stats", {}).get("model", "none"),
                    "owner": d.get("owner", "")})
    return sorted(out, key=lambda d: d["at"], reverse=True)


def _tab_headers(blob: bytes, names: list[str]) -> list[dict]:
    """The header row we ACTUALLY read for each tab.

    This exists because of a latent mismatch in inbound.py: sheet_names() returns
    workbook order, while read_xlsx(sheet=N) indexes worksheet files sorted by
    filename. They usually coincide and are not guaranteed to. Showing the header
    row beside the tab name makes a mismatch visible to the one person who can
    recognise it — instead of silently importing the wrong tab."""
    out = []
    for i, name in enumerate(names[:MAX_TABS]):
        try:
            fields, _rows = inbound.read_xlsx(blob, sheet=i, limit=1)
        except Exception:  # noqa: BLE001 — a tab we can't read is still a tab
            fields = []
        out.append({"index": i, "name": name, "headers": fields[:8]})
    return out


async def _make_draft(blob: bytes, src_key: str, filename: str, run_by: str,
                      model: str, sheet: int, token: str) -> dict:
    """Read one tab, X-ray it, ask the brain to name it, and stash the result."""
    try:
        names = inbound.sheet_names(blob)
    except Exception:  # noqa: BLE001
        names = []
    sheet = sheet if 0 <= sheet < max(len(names), 1) else 0
    fields, records = inbound.read_xlsx(blob, sheet=sheet, limit=recipes.ROW_LIMIT)
    sheet_name = names[sheet] if sheet < len(names) else ""

    xr = xray.xray(fields, records, filename, sheet_name)
    analysis, stats = await analyze.analyze(xr, model=model, records=records)

    draft = {
        "token": token, "src_key": src_key, "filename": filename, "owner": run_by,
        "at": _now(), "sheet": sheet, "tabs": _tab_headers(blob, names),
        "xray": xr, "analysis": analysis, "stats": stats,
    }
    draft_save(draft)
    await audit.record(
        run_by, audit.LIST_ANALYZE, filename, rows=xr["row_count"], cols=xr["col_count"],
        sheet=sheet, model=stats["model"], prompt_version=stats["prompt_version"],
        tokens=stats["tokens"], dropped=stats["dropped"], findings=len(xr["findings"]),
    )
    return draft


def owner_key(src_key: str) -> str:
    """Where we record who uploaded a source.

    A source outlives its draft — the draft is discarded at approval, but the
    .xlsx stays so a recipe can be re-run against it. So ownership cannot be read
    off the draft; it needs its own record, or /lists/source/<key> degenerates
    into "any logged-in user may download any customer's spreadsheet"."""
    return f"{src_key}.owner.json"


def source_owner(src_key: str) -> str:
    """Who uploaded this original. Empty string means unknown — treat as denied."""
    rec = vault.get_json(owner_key(src_key)) or {}
    return str(rec.get("owner") or "")


async def upload(blob: bytes, filename: str, run_by: str,
                 model: str = "", sheet: int = 0) -> dict:
    """Store the original privately, then analyse tab `sheet`. Returns the draft."""
    src_key = vault.put(blob, vault.new_key(vault.SRC, "xlsx"), XLSX_TYPE)
    vault.put_json({"owner": run_by, "filename": filename}, owner_key(src_key))
    token = secrets.token_hex(16)
    return await _make_draft(blob, src_key, filename, run_by, model, sheet, token)


async def analyze_draft(token: str, sheet: int, model: str, run_by: str) -> dict | None:
    """Re-read a different tab of the SAME stored original, and re-analyse it.

    The original is never re-uploaded, so this is also the cheapest honest way to
    compare two brains on one file: same bytes, same X-ray, different namer.

    Keeps the ORIGINAL owner. Re-analysing rebuilds the draft from scratch, and
    stamping the caller as owner let anyone who could POST here take a draft away
    from the person who uploaded it — and with it the download link to their
    workbook. The route checks ownership too; this is the second lock."""
    old = draft_load(token)
    if not old:
        return None
    blob = vault.get(old["src_key"])
    return await _make_draft(blob, old["src_key"], old["filename"],
                             old.get("owner") or run_by, model, sheet, token)


# --- running an approved recipe -------------------------------------------
def _store_report(report: dict) -> str:
    """The run report, into the Business Hub's bucket under an unguessable key.

    Same bucket as the API channel on purpose — that is what makes the existing
    run log and before→after pane work for list runs with no new code. The key is
    token_hex(16) rather than the old `{filename}-{timestamp}.json`, which was
    guessable in a day's worth of requests if you knew the filename."""
    business_hub._ensure_bucket()
    key = f"{secrets.token_hex(16)}.json"
    body = json.dumps(report, indent=2, ensure_ascii=False).encode()
    business_hub._client.put_object(business_hub._BUCKET, key, io.BytesIO(body),
                                    length=len(body), content_type="application/json")
    return key


async def run_recipe(spec: dict, version: int, blob: bytes, filename: str,
                     run_by: str, model: str) -> BusinessHubRun:
    """Apply an approved recipe to a spreadsheet. The whole point of the feature.

    Note what does NOT happen here: no prompt is written, no mapping is decided,
    nothing is asked of a human. The recipe already answered all of that, months
    ago if necessary. The only variable is which brain runs the one action that
    needs one."""
    sheet = int(spec.get("inbound", {}).get("sheet", 0) or 0)
    try:
        names = inbound.sheet_names(blob)
    except Exception:  # noqa: BLE001
        names = []
    if sheet >= len(names):
        sheet = 0
    fields, records = inbound.read_xlsx(blob, sheet=sheet, limit=recipes.ROW_LIMIT)
    xr = xray.xray(fields, records, filename, names[sheet] if sheet < len(names) else "")

    enriched, stats, extra = await recipes.run(spec, records, model=model, xr=xr)

    source = f"{filename} → {spec['key']} v{version}"[:120]
    report = {
        "meta": {
            "source": source, "run_by": run_by, "channel": "list",
            "run_at": _now(), "count": len(enriched), "columns": fields,
            "recipe": extra["recipe"], "actions": extra["actions"],
            "action_stats": extra["action_stats"], "schema_sql": extra["schema_sql"],
            "xray_sha": extra["xray_sha"], "src_key": extra["src_key"],
            "findings": xr["findings"], **stats,
        },
        "records": enriched,
    }
    key = _store_report(report)

    async with async_session() as s:
        run = BusinessHubRun(
            source=source, count=len(enriched), report_key=key, run_by=run_by,
            model=stats["model"], prompt_version=stats["prompt_version"],
            enriched_count=stats["enriched_count"], tokens=stats["tokens"],
            review_count=stats["review_count"],
        )
        s.add(run)
        await s.commit()
        await s.refresh(run)

    await audit.record(
        run_by, audit.LIST_RUN, f"{spec['key']} v{version} · {filename}",
        count=len(enriched), report_key=key, recipe=spec["key"], version=version,
        spec_sha=extra["recipe"]["spec_sha"][:12], model=stats["model"],
        prompt_version=stats["prompt_version"], enriched=stats["enriched_count"],
        tokens=stats["tokens"], review=stats["review_count"],
    )
    return run


async def runs_for(recipe_key: str, limit: int = 40) -> list[BusinessHubRun]:
    """This recipe's runs, read out of the one run log everybody else uses.

    A `source` LIKE is a blunt instrument and it is the right trade: a dedicated
    column would be a migration, and the whole feature is built on the promise
    that it needs no new table."""
    runs = await business_hub.recent_runs(limit=200)
    needle = f"→ {recipe_key} v"
    return [r for r in runs if needle in (r.source or "")][:limit]


def approve(draft: dict, form: dict, approved_by: str) -> tuple[dict, int, list[str]]:
    """The gate. Build the spec from the ticks, validate it, mint version N+1.

    Returns (spec, version, warnings). This is the only function in the feature
    that writes something permanent from a model's suggestion, and it takes an
    explicit human as an argument for exactly that reason."""
    spec = recipes.build(draft["xray"], draft["analysis"],
                         {**form, "src_key": draft.get("src_key", ""),
                          "sheet": draft.get("sheet", 0)})
    spec, warnings = recipes.validate(spec, list(draft["xray"].get("columns", {})))
    key, version = recipes.save(spec, approved_by, form.get("note", ""), warnings)
    spec["key"], spec["version"] = key, version
    return spec, version, warnings


def ticked_ids(form_actions: list[str]) -> list[str]:
    return [str(t).partition(":")[0] for t in form_actions
            if str(t).partition(":")[0] in actions.ACTIONS]
