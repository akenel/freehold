"""Business Hub — the systems-integration pack, served as a Freehold page.

Login required (any user who came through the door). The page shows what the
integration does + the log of past runs; the button fires one sync. Mirrors the
profile.py pattern: GET renders, POST acts then redirects back (303) so a refresh
never re-runs the job.
"""
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

import business_hub
import deps
from deps import templates

router = APIRouter()


@router.get("/business-hub")
async def hub(request: Request):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    runs = await business_hub.recent_runs()
    return templates.TemplateResponse("business_hub.html", {
        "request": request, "user": user, "runs": runs,
        "source": business_hub.SOURCE_NAME,
        "report_url": business_hub.report_url,
    })


@router.post("/business-hub/sync")
async def sync(request: Request):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    await business_hub.run_sync(run_by=user.get("username", "anonymous"))
    return RedirectResponse("/business-hub", status_code=303)
