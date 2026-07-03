"""Freehold — Phase 2: the door.

Real OIDC login against Keycloak, a signed session cookie, a dashboard behind
auth, and role-based access (RBAC). Tokens live on the server; the browser only
carries an opaque signed cookie. Every protected route is explicit — no magic.
"""
import os

import asyncpg
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

import auth
import build_info
import diagnostics
import i18n
import money
import tickets

APP_ENV = os.getenv("APP_ENV", "sandbox")
KC_REALM = os.getenv("KC_REALM", f"freehold-{APP_ENV}")
KC_PUBLIC_URL = os.getenv("KC_PUBLIC_URL", "http://localhost:8080")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8080").rstrip("/")
DATABASE_URL = os.getenv("DATABASE_URL", "")
SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-insecure-change-me")

app = FastAPI(title="Freehold", version="0.2.0-phase2")
# Signed, http-only session cookie. same_site=lax lets the OIDC redirect back in.
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, same_site="lax", https_only=False)
app.mount("/static", StaticFiles(directory="static"), name="static")


def _inject_i18n(request: Request) -> dict:
    """Runs for every template render — makes t()/lang/langs available everywhere."""
    lang = i18n.resolve_lang(request)
    return {"t": i18n.translator(lang), "lang": lang, "langs": i18n.LANGS}


templates = Jinja2Templates(directory="templates", context_processors=[_inject_i18n])


def current_user(request: Request):
    return request.session.get("user")


async def db_check() -> tuple[bool, str]:
    if not DATABASE_URL:
        return False, "DATABASE_URL is not set"
    try:
        conn = await asyncpg.connect(dsn=DATABASE_URL, timeout=5)
        try:
            version = await conn.fetchval("SELECT version()")
        finally:
            await conn.close()
        return True, version.split(" on ")[0]
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


# ---------------------------------------------------------------- public
@app.get("/healthz")
async def healthz():
    ok, _ = await db_check()
    return JSONResponse({"status": "ok", "env": APP_ENV, "realm": KC_REALM, "db": ok})


@app.get("/version")
async def version():
    """The truthful build bar — what deploy.py stamps, this serves, parity checks."""
    return JSONResponse({
        "version": build_info.version(), "sha": build_info.sha(),
        "date": build_info.date(), "env": APP_ENV,
    })


@app.get("/")
async def index(request: Request):
    ok, message = await db_check()
    return templates.TemplateResponse("index.html", {
        "request": request, "env": APP_ENV, "realm": KC_REALM, "kc_url": KC_PUBLIC_URL,
        "db_ok": ok, "db_msg": message, "user": current_user(request),
        "build": {"version": build_info.version(), "sha": build_info.sha(), "date": build_info.date()},
    })


# ---------------------------------------------------------------- the door
@app.get("/login")
async def login(request: Request):
    state, nonce = auth.new_secret(), auth.new_secret()
    verifier, challenge = auth.make_pkce()
    request.session["oauth"] = {"state": state, "nonce": nonce, "cv": verifier}
    redirect_uri = f"{APP_BASE_URL}/auth/callback"
    lang = i18n.resolve_lang(request)  # carry the app language into the login page
    return RedirectResponse(
        auth.build_auth_redirect(redirect_uri, state, nonce, challenge, ui_locales=lang)
    )


@app.get("/auth/callback")
async def auth_callback(request: Request):
    saved = request.session.get("oauth") or {}
    code = request.query_params.get("code")
    if not code or request.query_params.get("state") != saved.get("state"):
        return HTMLResponse("Login failed: bad or missing state.", status_code=400)
    redirect_uri = f"{APP_BASE_URL}/auth/callback"
    try:
        tokens = await auth.exchange_code(code, redirect_uri, saved["cv"])
        claims = auth.verify_id_token(tokens["id_token"], saved.get("nonce"))
        roles = auth.roles_from_access(tokens["access_token"])
    except Exception as exc:  # noqa: BLE001
        return HTMLResponse(f"Login failed: {exc}", status_code=400)

    request.session.pop("oauth", None)
    request.session["user"] = {
        "username": claims.get("preferred_username"),
        "name": claims.get("name") or claims.get("preferred_username"),
        "email": claims.get("email"),
        "roles": roles,
    }
    request.session["id_token"] = tokens["id_token"]
    return RedirectResponse("/dashboard", status_code=303)


@app.get("/logout")
async def logout(request: Request):
    id_token = request.session.get("id_token")
    request.session.clear()
    if id_token:
        return RedirectResponse(auth.logout_redirect(id_token, f"{APP_BASE_URL}/"))
    return RedirectResponse("/")


# ---------------------------------------------------------------- behind the door
@app.get("/dashboard")
async def dashboard(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "user": user, "env": APP_ENV, "realm": KC_REALM,
    })


@app.get("/console")
async def console(request: Request):
    """RBAC demo: admins only. A logged-in 'staff' user gets a clean 403."""
    user = current_user(request)
    if not user:
        return RedirectResponse("/login")
    if "admin" not in user.get("roles", []):
        return templates.TemplateResponse(
            "forbidden.html", {"request": request, "user": user}, status_code=403,
        )
    return templates.TemplateResponse("console.html", {"request": request, "user": user})


# ---------------------------------------------------------------- the loop
@app.get("/feedback")
async def feedback_form(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("feedback.html", {"request": request, "user": user})


@app.post("/feedback")
async def feedback_submit(request: Request):
    user = current_user(request)
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


@app.get("/backlog")
async def backlog(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse(
        "backlog.html",
        {"request": request, "user": user, "tickets": await tickets.list_tickets()},
    )


def _require_admin(request: Request):
    """Returns the user if admin, else None (caller redirects/403s)."""
    user = current_user(request)
    if user and "admin" in user.get("roles", []):
        return user
    return None


@app.get("/qa")
async def qa(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login")
    if "admin" not in user.get("roles", []):
        return templates.TemplateResponse(
            "forbidden.html", {"request": request, "user": user}, status_code=403,
        )
    return templates.TemplateResponse("qa.html", {
        "request": request, "user": user,
        "tickets": await tickets.list_tickets(), "counts": await tickets.counts(),
    })


@app.post("/qa/{ticket_id}/status")
async def qa_set_status(request: Request, ticket_id: int):
    if not _require_admin(request):
        return RedirectResponse("/login")
    form = await request.form()
    await tickets.set_status(ticket_id, form.get("status", "open"))
    return RedirectResponse("/qa", status_code=303)


@app.post("/qa/{ticket_id}/close")
async def qa_close(request: Request, ticket_id: int):
    user = _require_admin(request)
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


# ---------------------------------------------------------------- base pages
@app.get("/account")
async def account(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("account.html", {
        "request": request, "user": user, "env": APP_ENV, "realm": KC_REALM, "kc_url": KC_PUBLIC_URL,
    })


@app.get("/pulse")
async def pulse(request: Request):
    """System pulse — real diagnostics (DB · migrations · Keycloak · build). Admin only."""
    user = current_user(request)
    if not user:
        return RedirectResponse("/login")
    if "admin" not in user.get("roles", []):
        return templates.TemplateResponse("forbidden.html", {"request": request, "user": user}, status_code=403)
    checks = await diagnostics.pulse()
    overall = "ok" if all(c["status"] in ("ok", "info") for c in checks) else "error"
    return templates.TemplateResponse("pulse.html", {
        "request": request, "user": user, "checks": checks, "overall": overall,
    })


@app.get("/manifesto")
async def manifesto(request: Request):
    return templates.TemplateResponse("manifesto.html", {"request": request, "user": current_user(request)})


@app.get("/terms")
async def terms(request: Request):
    return templates.TemplateResponse("terms.html", {"request": request, "user": current_user(request)})


@app.get("/privacy")
async def privacy(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request, "user": current_user(request)})


@app.get("/lang/{code}")
async def set_lang(request: Request, code: str):
    """Switch language (sets a cookie), then bounce back where you came from."""
    resp = RedirectResponse(request.headers.get("referer") or "/", status_code=303)
    if code in i18n.LANGS:
        resp.set_cookie("lang", code, max_age=31536000, samesite="lax")
    return resp


@app.get("/money")
async def money_demo(request: Request):
    """Enterprise taste: one base amount, formatted the way each market writes it."""
    user = current_user(request)
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


@app.exception_handler(404)
async def not_found(request: Request, exc):
    user = request.session.get("user") if "session" in request.scope else None
    return templates.TemplateResponse("404.html", {"request": request, "user": user}, status_code=404)
