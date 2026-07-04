"""Optional-taste routes: the multi-currency demo and the admin system pulse."""
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

import deps
import diagnostics
import money
from deps import admin_or_deny, templates

router = APIRouter()


@router.get("/money")
async def money_demo(request: Request):
    """Enterprise taste: one base amount, formatted the way each market writes it."""
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    base_amount = 123456.78
    rows = [{
        "code": code,
        "label": cfg["label"],
        "formatted": money.format_money(base_amount, code),
        "grouping": money.GROUP_LABEL[cfg["group"]],
    } for code, cfg in money.CURRENCIES.items()]
    return templates.TemplateResponse("money.html", {
        "request": request, "user": user, "base": base_amount, "rows": rows,
    })


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
