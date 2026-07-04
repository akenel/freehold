"""The feedback → backlog → QA loop. Tickets are the knowledge base; closing one
requires the WHY."""
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

import deps
import tickets
from deps import admin_or_deny, require_admin, templates

router = APIRouter()


@router.get("/feedback")
async def feedback_form(request: Request):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("feedback.html", {"request": request, "user": user})


@router.post("/feedback")
async def feedback_submit(request: Request):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    form = await request.form()
    title = (form.get("title") or "").strip()
    if not title:
        return templates.TemplateResponse(
            "feedback.html",
            {"request": request, "user": user, "error": "A short title is required."},
            status_code=400,
        )
    await tickets.create_ticket(
        kind=form.get("kind", "feedback"),
        title=title,
        body=(form.get("body") or "").strip(),
        created_by=user["username"],
    )
    return RedirectResponse("/backlog", status_code=303)


@router.get("/backlog")
async def backlog(request: Request):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse(
        "backlog.html",
        {"request": request, "user": user, "tickets": await tickets.list_tickets()},
    )


@router.get("/qa")
async def qa(request: Request):
    user, denied = admin_or_deny(request)
    if denied:
        return denied
    return templates.TemplateResponse("qa.html", {
        "request": request, "user": user,
        "tickets": await tickets.list_tickets(), "counts": await tickets.counts(),
    })


@router.post("/qa/{ticket_id}/status")
async def qa_set_status(request: Request, ticket_id: int):
    if not require_admin(request):
        return RedirectResponse("/login")
    form = await request.form()
    await tickets.set_status(ticket_id, form.get("status", "open"))
    return RedirectResponse("/qa", status_code=303)


@router.post("/qa/{ticket_id}/close")
async def qa_close(request: Request, ticket_id: int):
    user = require_admin(request)
    if not user:
        return RedirectResponse("/login")
    form = await request.form()
    resolution = (form.get("resolution") or "").strip()
    if not resolution:
        # Enforce the discipline: no close without the WHY.
        return templates.TemplateResponse("qa.html", {
            "request": request, "user": user,
            "tickets": await tickets.list_tickets(), "counts": await tickets.counts(),
            "error": f"Ticket #{ticket_id}: a resolution note is required to close (capture the why).",
        }, status_code=400)
    await tickets.close_ticket(ticket_id, resolution, user["username"])
    return RedirectResponse("/qa", status_code=303)
