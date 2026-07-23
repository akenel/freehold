"""The Audit Cockpit — an admin-only, read-only view of the append-only trail.

Who did what, when: logins, Business Hub syncs, ticket moves. The page never
writes — it only reads audit.recent(). Filter by who (actor) or what (action)
via query params; the chips are just links that set them.
"""
from fastapi import APIRouter, Request

import audit
from deps import admin_or_deny, templates

router = APIRouter()


@router.get("/audit")
async def audit_cockpit(request: Request):
    user, denied = admin_or_deny(request)
    if denied:
        return denied
    action = (request.query_params.get("action") or "").strip()
    actor = (request.query_params.get("actor") or "").strip()
    events = await audit.recent(limit=200, action=action, actor=actor)
    return templates.TemplateResponse("audit.html", {
        "request": request, "user": user,
        "events": events, "facets": await audit.facets(),
        "f_action": action, "f_actor": actor,
    })
