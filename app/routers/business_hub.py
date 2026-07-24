"""Business Hub — the systems-integration pack, served as a Freehold page.

Login required (any user who came through the door). The page shows what the
integration does, the model picker (bring your own brain), a before/after pane
for the most recent run, and the log of past runs; the button fires one sync.
Mirrors the profile.py pattern: GET renders, POST acts then redirects back (303)
so a refresh never re-runs the job.
"""
import re

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, StreamingResponse

import business_hub
import deps
import enrich
from deps import templates

router = APIRouter()

# The only key shape we mint. An allowlist, not a "../" hunt — a report holds
# every enriched record in a run, which is to say the customer's contact list.
_REPORT_KEY = re.compile(r"^[0-9a-f]{32}\.json$")


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
async def report(request: Request, key: str):
    """The full run report, behind the login. Replaces the old public /media link.

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
