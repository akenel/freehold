"""List Intake — the nine /lists routes.

House pattern throughout: GET renders, POST acts then redirects 303 so a refresh
never re-runs a job. Login required on every route (`deps.current_user(request)`
as a module attribute, never a direct import — tests monkeypatch the attribute).

No CSRF token, matching the rest of the app: there is none anywhere in this
codebase, and the session cookie is `same_site="lax"`, which is what blocks
cross-site form posts today. Adding a token to this one form would be a lie about
coverage; it belongs in an app-wide ticket, not here.
"""
import re

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse, StreamingResponse
from starlette.datastructures import UploadFile as FormFile

import actions
import audit
import business_hub
import deps
import enrich
import lists
import recipes
import vault
from deps import templates

router = APIRouter()

BAD_FILE = ("That isn't a readable .xlsx — 'Save as .xlsx' from Excel or "
            "LibreOffice, not .xls and not .csv.")
TOO_BIG = "That file is over 10 MB. Trim it, or split the tabs into two uploads."
# Above this many rows, a ticked `classify` means minutes of sequential model
# calls on a single worker. We say so rather than pretending it's instant.
SLOW_ROWS = 1000


def _owned(draft, user) -> bool:
    """One place, so every draft route agrees. A missing draft counts as owned —
    the caller then renders its own "that draft is gone", which leaks nothing.

    This exists because four routes touch drafts and only two checked. The two
    that didn't let any logged-in user re-analyse a stranger's draft (which also
    rewrote the owner, handing over the download link to their workbook) or
    delete it outright."""
    if not draft:
        return True
    owner = draft.get("owner")
    return not owner or owner == user.get("username")


def _index_context(request: Request, user, error: str = ""):
    return {
        "request": request, "user": user, "error": error,
        "models": enrich.MODELS, "default_model": enrich.DEFAULT_MODEL,
        # open_drafts() takes an owner and filters on it — calling it bare listed
        # EVERY user's drafts, and the row template renders the token as a link,
        # so the page handed out other people's draft tokens to anyone logged in.
        "recipes": recipes.index(),
        "drafts": lists.open_drafts(user.get("username", "")),
        "runs": [], "row_limit": recipes.ROW_LIMIT,
        "max_mb": lists.MAX_UPLOAD // (1024 * 1024),
    }


@router.get("/lists")
async def index(request: Request):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    ctx = _index_context(request, user)
    ctx["runs"] = [r for r in await business_hub.recent_runs(limit=40) if " → " in (r.source or "")]
    return templates.TemplateResponse("lists.html", ctx)


async def _picked_file(request: Request) -> tuple[bytes, str, dict]:
    """Read the upload straight off the form, tolerating "nothing chosen".

    Declaring `file: UploadFile = File(None)` looks right and fails in the one
    case that matters most: a browser submitting the form with no file selected
    still sends the part, as `filename=""`, and RFC 7578 says a part with an
    empty filename is a plain field — so it arrives as a str and FastAPI answers
    with a raw 422 JSON blob before our own "Pick a file first." ever runs.
    Widening the annotation to a union is worse: FastAPI then stops treating the
    field as a file at all and every real upload arrives as a string too.
    So we parse the form ourselves and decide by type. Returns (blob, filename,
    other-form-fields)."""
    form = await request.form()
    picked = form.get("file")
    blob, filename = b"", ""
    if isinstance(picked, FormFile) and picked.filename:
        # Read at most one byte past the cap, never the whole part. `await
        # picked.read()` materialises whatever was sent before anyone checks its
        # size — the limit was applied sixteen lines later, which on a single
        # worker is a limit that runs after the damage. The caller sees an
        # over-cap blob and refuses it; we just never hold more than the cap+1.
        blob = await picked.read(lists.MAX_UPLOAD + 1)
        filename = picked.filename
    rest = {k: v for k, v in form.items() if k != "file"}
    return blob, filename, rest


@router.post("/lists/upload")
async def upload(request: Request):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")

    blob, filename, form = await _picked_file(request)
    model = str(form.get("model") or enrich.DEFAULT_MODEL)
    if not blob:
        return templates.TemplateResponse(
            "lists.html", _index_context(request, user, "Pick a file first."))
    if len(blob) > lists.MAX_UPLOAD:
        return templates.TemplateResponse(
            "lists.html", _index_context(request, user, TOO_BIG))
    if not lists.is_xlsx(filename, blob):
        return templates.TemplateResponse(
            "lists.html", _index_context(request, user, BAD_FILE))

    try:
        draft = await lists.upload(blob, filename, user.get("username", "anonymous"),
                                   model=model)
    except Exception:  # noqa: BLE001 — a workbook we can't read is a message, not a 500
        return templates.TemplateResponse(
            "lists.html", _index_context(request, user, BAD_FILE))
    return RedirectResponse(f"/lists/draft/{draft['token']}", status_code=303)


def _draft_context(request: Request, user, draft: dict, error: str = ""):
    """Everything the money screen needs, grouped by the existing gate."""
    analysis = draft.get("analysis", {})
    acts = analysis.get("actions", [])
    xr = draft.get("xray", {})
    classify = next((a for a in acts if a["id"] == "classify"), None)
    rows = xr.get("row_count", 0)
    return {
        "request": request, "user": user, "error": error, "draft": draft,
        "xr": xr, "analysis": analysis, "stats": draft.get("stats", {}),
        "auto": [a for a in acts if a["gate"] == enrich.AUTO],
        "review": [a for a in acts if a["gate"] == enrich.REVIEW],
        "rejected": [a for a in acts if a["gate"] == enrich.REJECTED],
        "classify": classify,
        "columns": xr.get("columns", {}),
        "models": enrich.MODELS, "default_model": draft.get("stats", {}).get("model")
        or enrich.DEFAULT_MODEL,
        "auto_above": enrich.AUTO_ABOVE, "review_above": enrich.REVIEW_ABOVE,
        "slow": bool(classify) and rows > SLOW_ROWS,
        "calls": (rows + 24) // 25,
    }


@router.get("/lists/draft/{token}")
async def draft(request: Request, token: str):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    d = lists.draft_load(token)
    if not d:
        return templates.TemplateResponse(
            "lists.html", _index_context(request, user, "That draft is gone."))
    if d.get("owner") and d["owner"] != user.get("username"):
        return templates.TemplateResponse(
            "forbidden.html", {"request": request, "user": user}, status_code=403)
    return templates.TemplateResponse("list_draft.html", _draft_context(request, user, d))


@router.post("/lists/draft/{token}/analyze")
async def reanalyze(request: Request, token: str, sheet: int = Form(0),
                    model: str = Form(enrich.DEFAULT_MODEL)):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    if not _owned(lists.draft_load(token), user):
        return templates.TemplateResponse(
            "forbidden.html", {"request": request, "user": user}, status_code=403)
    got = await lists.analyze_draft(token, sheet, model, user.get("username", "anonymous"))
    if not got:
        return RedirectResponse("/lists", status_code=303)
    return RedirectResponse(f"/lists/draft/{token}", status_code=303)


@router.post("/lists/draft/{token}/discard")
async def discard(request: Request, token: str):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    if not _owned(lists.draft_load(token), user):
        return templates.TemplateResponse(
            "forbidden.html", {"request": request, "user": user}, status_code=403)
    lists.draft_discard(token)
    return RedirectResponse("/lists", status_code=303)


@router.post("/lists/draft/{token}/approve")
async def approve(request: Request, token: str,
                  key: str = Form(""), label: str = Form(""), note: str = Form(""),
                  confirm: str = Form(""), action: list[str] = Form([]),
                  quality_col: list[str] = Form([]), label_fields: list[str] = Form([]),
                  classify_to: str = Form(""), classify_multi: str = Form(""),
                  classify_taxonomy: str = Form(""), classify_instruction: str = Form(""),
                  classify_feed: list[str] = Form([]), schema_table: str = Form(""),
                  parse_from: str = Form(""),
                  model: str = Form(enrich.DEFAULT_MODEL), run: str = Form("1")):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    d = lists.draft_load(token)
    if not d:
        return RedirectResponse("/lists", status_code=303)
    if d.get("owner") and d["owner"] != user.get("username"):
        return templates.TemplateResponse(
            "forbidden.html", {"request": request, "user": user}, status_code=403)
    if confirm != "on":
        return templates.TemplateResponse("list_draft.html", _draft_context(
            request, user, d, "Tick the approval box — that's the gate."))

    who = user.get("username", "anonymous")
    form = {
        "key": key, "label": label, "note": note, "actions": action,
        "quality_cols": quality_col, "label_fields": label_fields,
        "classify_to": classify_to, "classify_multi": classify_multi == "on",
        "classify_taxonomy": [t for t in classify_taxonomy.splitlines()],
        "classify_instruction": classify_instruction, "classify_feed": classify_feed,
        "schema_table": schema_table, "parse_from": parse_from,
    }
    spec, version, warnings = lists.approve(d, form, who)
    await audit.record(
        who, audit.RECIPE_APPROVE, f"{spec['key']} v{version}",
        spec_sha=recipes.spec_sha(spec)[:12],
        actions=",".join(a["id"] for a in spec["actions"]),
        proposed_by=d.get("stats", {}).get("model", "none"),
        overrides=len(warnings),
    )
    # Run FIRST, discard the draft only once it worked. The other order looks
    # tidier and is quietly destructive: any failure in the run — a model that
    # answers "confidence": "high", MinIO hiccuping, Postgres away — left the
    # user with a 500, no draft to retry from, and a saved recipe version they
    # never saw execute. The draft is cheap; losing it is not.
    if run == "1":
        try:
            blob = vault.get(d["src_key"])
            await lists.run_recipe(spec, version, blob, d["filename"], who, model)
        except Exception:  # noqa: BLE001 — keep the draft so the human can retry
            return templates.TemplateResponse("list_draft.html", _draft_context(
                request, user, d,
                f"Recipe {spec['key']} v{version} was saved, but the run failed. "
                "Your draft is still here — try again, or run it from the recipe page."))
        lists.draft_discard(token)
        return RedirectResponse("/business-hub", status_code=303)

    lists.draft_discard(token)
    return RedirectResponse(f"/lists/recipe/{spec['key']}", status_code=303)


@router.get("/lists/recipe/{key}")
async def recipe(request: Request, key: str, version: int = 0):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    doc = recipes.load_doc(key)
    if not doc or not doc.get("versions"):
        raise HTTPException(status_code=404)
    spec = recipes.load(key, version or None) or {}
    chain = list(reversed(doc["versions"]))
    shown = next((v for v in chain if v["version"] == spec.get("version")), chain[0])
    return templates.TemplateResponse("list_recipe.html", {
        "request": request, "user": user, "doc": doc, "spec": spec,
        "shown": shown, "chain": chain,
        "runs": await lists.runs_for(key),
        "models": enrich.MODELS, "default_model": enrich.DEFAULT_MODEL,
        "last_src": next((v["spec"].get("derived_from", {}).get("src_key", "")
                          for v in chain if v["spec"].get("derived_from", {}).get("src_key")), ""),
        "actions_meta": actions.ACTIONS,
    })


@router.post("/lists/recipe/{key}/run")
async def rerun(request: Request, key: str):
    # Same empty-file-part story as /lists/upload — and it bites harder here,
    # because re-running a saved recipe against the STORED source is the normal
    # path, i.e. submitting with no file chosen is the common case, not the edge.
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    blob, filename, form = await _picked_file(request)
    src_key = str(form.get("src_key") or "")
    model = str(form.get("model") or enrich.DEFAULT_MODEL)
    try:
        version = int(form.get("version") or 0)
    except ValueError:
        version = 0
    spec = recipes.load(key, version or None)
    if not spec:
        raise HTTPException(status_code=404)

    if blob:
        if len(blob) > lists.MAX_UPLOAD or not lists.is_xlsx(filename, blob):
            return RedirectResponse(f"/lists/recipe/{key}", status_code=303)
    elif vault.SRC_KEY.fullmatch(src_key or ""):
        blob = vault.get(src_key)
        filename = spec.get("label", key)
    if not blob:
        return RedirectResponse(f"/lists/recipe/{key}", status_code=303)

    await lists.run_recipe(spec, spec.get("version", 0), blob, filename,
                           user.get("username", "anonymous"), model)
    return RedirectResponse("/business-hub", status_code=303)


@router.get("/lists/source/{key:path}")
async def source(request: Request, key: str):
    """Download an original. Login required, OWNER required, audited.

    The regex allowlists the exact key shape we mint rather than hunting for
    '..', but a shape check is not an access check: this streams back a
    customer's whole spreadsheet, so it has to know *whose* it is. Ownership is
    recorded beside the source at upload (lists.owner_key) because the source
    outlives the draft — the draft is discarded at approval, the .xlsx stays."""
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    if not vault.SRC_KEY.fullmatch(key or "") or not vault.exists(key):
        raise HTTPException(status_code=404)
    owner = lists.source_owner(key)
    if owner != user.get("username"):
        # 404, not 403: to anyone but the owner this key does not exist.
        raise HTTPException(status_code=404)

    await audit.record(user.get("username", "anonymous"), audit.SOURCE_DOWNLOAD,
                       f"downloaded {key}", kind="source_download")
    resp = vault.stream(key)

    def body():
        try:
            yield from resp.stream(64 * 1024)
        finally:
            resp.close()
            resp.release_conn()

    name = re.sub(r"[^A-Za-z0-9_.-]+", "-", key.rsplit("/", 1)[-1])
    return StreamingResponse(body(), media_type=lists.XLSX_TYPE, headers={
        "Content-Disposition": f'attachment; filename="{name}"'})
