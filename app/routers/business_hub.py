"""Business Hub — the systems-integration pack, served as a Freehold page.

Login required (any user who came through the door). The page shows what the
integration does, the model picker (bring your own brain), a before/after pane
for the most recent run, and the log of past runs; the button fires one sync.
Mirrors the profile.py pattern: GET renders, POST acts then redirects back (303)
so a refresh never re-runs the job.
"""
import re
from collections import Counter

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, StreamingResponse

import business_hub
import deps
import enrich
import export
from deps import templates

router = APIRouter()

# The only key shape we mint. An allowlist, not a "../" hunt — a report holds
# every enriched record in a run, which is to say the customer's contact list.
_REPORT_KEY = re.compile(r"^[0-9a-f]{32}\.json$")

# Rows per page in the preview. A report can hold 5,000 records; rendering
# them all is a slow page and an unreadable one.
PAGE = 50


@router.get("/business-hub")
async def hub(request: Request):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    runs = await business_hub.recent_runs()
    # The diff pane shows the newest run's report, read back out of MinIO. If
    # it's gone or unreadable the pane simply doesn't render — see load_report.
    latest = business_hub.load_report(runs[0].report_key) if runs else {}
    return templates.TemplateResponse("business_hub.html", {
        "request": request, "user": user, "runs": runs,
        "source": business_hub.SOURCE_NAME,
        "report_url": business_hub.report_url,
        "models": enrich.MODELS,
        "default_model": enrich.DEFAULT_MODEL,
        "latest": latest,
        "auto_above": enrich.AUTO_ABOVE,
        "review_above": enrich.REVIEW_ABOVE,
    })


@router.post("/business-hub/sync")
async def sync(request: Request, model: str = Form(enrich.DEFAULT_MODEL)):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    await business_hub.run_sync(run_by=user.get("username", "anonymous"), model=model)
    return RedirectResponse("/business-hub", status_code=303)


@router.get("/business-hub/report/{key}")
async def report_view(request: Request, key: str, gate: str = "", page: int = 1):
    """The run report as a LIST, which is what it is.

    It used to hand back raw JSON. That is the correct wire format and a terrible
    answer to "what did it do to my spreadsheet?" — the one question the whole
    product exists to answer. Same bytes, rendered: source columns as they came
    in, enriched columns with the original struck through beside the new value,
    and every AI-written cell carrying its model and confidence. The JSON is
    still one click away at /raw for anyone who wants to diff or re-import it."""
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    if not _REPORT_KEY.fullmatch(key or ""):
        raise HTTPException(status_code=404)
    rep = business_hub.load_report(key)
    if not rep:
        raise HTTPException(status_code=404)

    records = rep.get("records") or []
    if gate in (enrich.AUTO, enrich.REVIEW, enrich.REJECTED):
        records = [r for r in records if r.get("_gate") == gate]

    page = max(1, page)
    start = (page - 1) * PAGE
    shown = records[start:start + PAGE]
    # Source columns are whatever the records actually carry, minus our own
    # underscore-prefixed bookkeeping. Order comes from meta.columns when the
    # spreadsheet channel recorded it, so the preview matches the sheet.
    enriched_names, source_names = [], list(rep.get("meta", {}).get("columns") or [])
    for r in records:
        for k in r:
            if not k.startswith("_") and k not in source_names:
                source_names.append(k)
        for k in (r.get("_enriched") or {}):
            if k not in enriched_names:
                enriched_names.append(k)

    counts = Counter(r.get("_gate", "") for r in (rep.get("records") or []))
    default_fmt = export.default_format(rep)
    other_fmts = [f for f in ("xlsx", "csv") if f != default_fmt]
    return templates.TemplateResponse("report.html", {
        "request": request, "user": user, "key": key,
        "meta": rep.get("meta", {}), "records": shown,
        "source_names": source_names, "enriched_names": enriched_names,
        "counts": counts, "gate": gate, "page": page, "per_page": PAGE,
        "total": len(records), "pages": max(1, (len(records) + PAGE - 1) // PAGE),
        "auto_above": enrich.AUTO_ABOVE, "review_above": enrich.REVIEW_ABOVE,
        "default_fmt": default_fmt, "other_fmts": other_fmts,
    })


@router.get("/business-hub/report/{key}/export")
async def report_export(request: Request, key: str, fmt: str = ""):
    """The cleaned list, in the format they want — default: the format they gave.

    This is the actual deliverable. /raw hands back the wire JSON; this renders
    the same report into a polished workbook (frozen header, autofilter, a
    coloured Gate column, a review-queue tab) or a flat csv. See export.py."""
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    if not _REPORT_KEY.fullmatch(key or ""):
        raise HTTPException(status_code=404)
    rep = business_hub.load_report(key)
    if not rep:
        raise HTTPException(status_code=404)

    fmt = fmt or export.default_format(rep)
    if fmt not in export.FORMATS:
        raise HTTPException(status_code=404)
    blob, mime = export.render(rep, fmt)

    stem = re.sub(r"[^A-Za-z0-9_.-]+", "-",
                  (rep.get("meta", {}).get("source") or "list").rsplit(".", 1)[0])[:60] or "list"
    name = f"{stem}-cleaned.{fmt}"
    return StreamingResponse(
        iter((blob,)), media_type=mime,
        headers={"Content-Disposition": f'attachment; filename="{name}"'})


@router.get("/business-hub/report/{key}/raw")
async def report(request: Request, key: str):
    """The full run report as JSON, behind the login. The machine-readable half.

    load_report() already read through the authenticated MinIO client, so nothing
    on the page ever needed the bucket to be world-readable — the public policy
    was only ever serving this one link. Now it doesn't have to."""
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    if not _REPORT_KEY.fullmatch(key or ""):
        raise HTTPException(status_code=404)
    try:
        resp = business_hub._client.get_object(business_hub._BUCKET, key)
    except Exception:  # noqa: BLE001 — a missing report is a 404, not a stack trace
        raise HTTPException(status_code=404)

    def body():
        try:
            yield from resp.stream(64 * 1024)
        finally:
            resp.close()
            resp.release_conn()

    return StreamingResponse(body(), media_type="application/json")
