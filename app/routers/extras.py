"""Admin system pulse — real diagnostics behind the login."""
from fastapi import APIRouter, Request

import deps
import diagnostics
from deps import admin_or_deny, templates

router = APIRouter()


@router.get("/pulse")
async def pulse(request: Request):
    """System pulse — real diagnostics (DB · migrations · Keycloak · build). Admin only."""
    user, denied = admin_or_deny(request)
    if denied:
        return denied
    checks = await diagnostics.pulse()
    overall = "ok" if all(c["status"] in ("ok", "info") for c in checks) else "error"
    return templates.TemplateResponse("pulse.html", {
        "request": request, "user": user, "checks": checks, "overall": overall,
    })
