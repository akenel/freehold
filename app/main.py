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
templates = Jinja2Templates(directory="templates")


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


@app.get("/")
async def index(request: Request):
    ok, message = await db_check()
    return templates.TemplateResponse("index.html", {
        "request": request, "env": APP_ENV, "realm": KC_REALM, "kc_url": KC_PUBLIC_URL,
        "db_ok": ok, "db_msg": message, "user": current_user(request),
    })


# ---------------------------------------------------------------- the door
@app.get("/login")
async def login(request: Request):
    state, nonce = auth.new_secret(), auth.new_secret()
    verifier, challenge = auth.make_pkce()
    request.session["oauth"] = {"state": state, "nonce": nonce, "cv": verifier}
    redirect_uri = f"{APP_BASE_URL}/auth/callback"
    return RedirectResponse(auth.build_auth_redirect(redirect_uri, state, nonce, challenge))


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
