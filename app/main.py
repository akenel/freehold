"""Freehold — Phase 2: the door.

Real OIDC login against Keycloak, a signed session cookie, a dashboard behind
auth, and role-based access (RBAC). Tokens live on the server; the browser only
carries an opaque signed cookie. Every protected route is explicit — no magic.
"""
import asyncio
import json
import os

import asyncpg
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from markdown_it import MarkdownIt

import auth
import build_info
import diagnostics
import i18n
import media
import money
import profiles
import robot
import tickets

APP_ENV = os.getenv("APP_ENV", "sandbox")
KC_REALM = os.getenv("KC_REALM", f"freehold-{APP_ENV}")
KC_PUBLIC_URL = os.getenv("KC_PUBLIC_URL", "http://localhost:8080")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8080").rstrip("/")
DATABASE_URL = os.getenv("DATABASE_URL", "")
SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-insecure-change-me")
# Mark the session cookie Secure whenever we're served over HTTPS (the default,
# even in dev via Caddy's internal CA). Override with SESSION_COOKIE_SECURE if needed.
SESSION_HTTPS_ONLY = os.getenv(
    "SESSION_COOKIE_SECURE", str(APP_BASE_URL.startswith("https"))
).strip().lower() in ("1", "true", "yes")

app = FastAPI(title="Freehold", version="0.2.0-phase2")
# Signed, http-only session cookie. same_site=lax lets the OIDC redirect back in.
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, same_site="lax", https_only=SESSION_HTTPS_ONLY)
app.mount("/static", StaticFiles(directory="static"), name="static")


def _inject_i18n(request: Request) -> dict:
    """Runs for every template render — makes i18n, build info, env, and the logged-in
    user available everywhere (so the shared nav/status bar works on any page)."""
    lang = i18n.resolve_lang(request)
    return {
        "t": i18n.translator(lang), "lang": lang, "langs": i18n.LANGS,
        "env": APP_ENV,
        "build": {"version": build_info.version(), "sha": build_info.sha(), "date": build_info.date()},
        "nav_user": request.session.get("user"),
    }


templates = Jinja2Templates(directory="templates", context_processors=[_inject_i18n])

# Markdown for bios — raw HTML is escaped (html=False), so it's safe to render
# with |safe: the renderer only emits a known, safe set of tags. Use [text](url)
# for links. typographer gives nice curly quotes/dashes.
_md = MarkdownIt("commonmark", {"html": False, "typographer": True})
templates.env.filters["markdown"] = lambda text: _md.render(text or "")


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


@app.get("/sw.js")
async def service_worker():
    """Served from root so the service worker's scope is the whole app (PWA)."""
    return FileResponse("static/sw.js", media_type="application/javascript")


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


@app.get("/register")
async def register(request: Request):
    """Self-serve sign-up — Keycloak's registration page. New users land back at
    /auth/callback already logged in (same code path as login)."""
    state, nonce = auth.new_secret(), auth.new_secret()
    verifier, challenge = auth.make_pkce()
    request.session["oauth"] = {"state": state, "nonce": nonce, "cv": verifier}
    redirect_uri = f"{APP_BASE_URL}/auth/callback"
    lang = i18n.resolve_lang(request)
    return RedirectResponse(
        auth.build_register_redirect(redirect_uri, state, nonce, challenge, ui_locales=lang)
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
    prof = await profiles.get(request.session["user"]["username"])
    request.session["user"]["avatar"] = media.url(prof.avatar_key) if prof else ""
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
    user, denied = _admin_or_deny(request)
    if denied:
        return denied
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


def _admin_or_deny(request: Request):
    """Guard for admin-only PAGES. Returns (user, None) for admins; otherwise
    (user_or_None, response) — a redirect to /login when logged out, or a clean
    403 forbidden page when logged in without the role. Caller: `if denied: return denied`."""
    user = current_user(request)
    if not user:
        return None, RedirectResponse("/login")
    if "admin" not in user.get("roles", []):
        return user, templates.TemplateResponse(
            "forbidden.html", {"request": request, "user": user}, status_code=403,
        )
    return user, None


@app.get("/qa")
async def qa(request: Request):
    user, denied = _admin_or_deny(request)
    if denied:
        return denied
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


# ---------------------------------------------------------------- profiles
SAMPLE_BIO = """## About me

Hey — I'm **{name}**, and this is my corner of the town square.

- 🛠️ I like to build things
- 🌍 I believe in *owning my stack*
- 🐺 Say hi anytime

> This bio is **Markdown** — headers, **bold**, lists and quotes all render.
> Hit **Edit profile** and make it your own."""


async def _seed_if_missing(user: dict):
    """Everyone starts with a filled-in profile — no blank page."""
    profile = await profiles.get(user["username"])
    if profile is None:
        name = user.get("name") or user["username"]
        profile = await profiles.upsert(
            user["username"], display_name=name, tagline="New in the piazza",
            bio=SAMPLE_BIO.format(name=name),
            links=[{"label": "YouTube", "url": "https://youtube.com"},
                   {"label": "LinkedIn", "url": "https://linkedin.com"}],
        )
    return profile


def _profile_ctx(request: Request, profile, viewer, is_owner: bool) -> dict:
    return {
        "request": request, "user": viewer, "profile": profile, "is_owner": is_owner,
        "avatar_url": media.url(profile.avatar_key), "banner_url": media.url(profile.banner_key),
    }


@app.get("/profile")
async def my_profile(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login")
    profile = await _seed_if_missing(user)
    return templates.TemplateResponse("profile.html", _profile_ctx(request, profile, user, True))


@app.get("/u/{username}")
async def public_profile(request: Request, username: str):
    profile = await profiles.get(username)
    if profile is None:
        return templates.TemplateResponse(
            "404.html", {"request": request, "user": current_user(request)}, status_code=404)
    viewer = current_user(request)
    is_owner = bool(viewer and viewer.get("username") == username)
    return templates.TemplateResponse("profile.html", _profile_ctx(request, profile, viewer, is_owner))


@app.get("/profile/edit")
async def edit_profile(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login")
    profile = await _seed_if_missing(user)
    return templates.TemplateResponse("profile_edit.html", _profile_ctx(request, profile, user, True))


@app.post("/profile/edit")
async def save_profile(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login")
    form = await request.form()
    fields = {
        "display_name": (form.get("display_name") or "").strip()[:120],
        "tagline": (form.get("tagline") or "").strip()[:160],
        "bio": (form.get("bio") or "").strip(),
    }
    # links come as parallel label[]/url[] rows; keep the ones with a URL
    pairs = zip(form.getlist("link_label"), form.getlist("link_url"))
    fields["links"] = [{"label": (l or "").strip()[:60], "url": u.strip()[:300]}
                       for l, u in pairs if u and u.strip()]
    # uploads: avatar + banner -> MinIO (only if a real image was sent)
    for field, attr in (("avatar", "avatar_key"), ("banner", "banner_key")):
        upload = form.get(field)
        if upload is not None and getattr(upload, "filename", ""):
            data = await upload.read()
            if data and media.is_image(upload.content_type) and len(data) <= 5 * 1024 * 1024:
                fields[attr] = media.save_image(data, upload.content_type)
    profile = await profiles.upsert(user["username"], **fields)
    request.session["user"]["avatar"] = media.url(profile.avatar_key)  # refresh topbar
    return RedirectResponse("/profile", status_code=303)


@app.get("/pulse")
async def pulse(request: Request):
    """System pulse — real diagnostics (DB · migrations · Keycloak · build). Admin only."""
    user, denied = _admin_or_deny(request)
    if denied:
        return denied
    checks = await diagnostics.pulse()
    overall = "ok" if all(c["status"] in ("ok", "info") for c in checks) else "error"
    return templates.TemplateResponse("pulse.html", {
        "request": request, "user": user, "checks": checks, "overall": overall,
    })


@app.get("/manifesto")
async def manifesto(request: Request):
    return templates.TemplateResponse("manifesto.html", {"request": request, "user": current_user(request)})


@app.get("/sitemap")
async def sitemap(request: Request):
    """A human site map — everything the app does, one honest page."""
    return templates.TemplateResponse("sitemap.html", {"request": request, "user": current_user(request)})


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


# ---------------------------------------------------------------- robot (Pi control pack)
def _can_drive(user) -> bool:
    return bool(user and "admin" in user.get("roles", []))


@app.get("/robot")
async def robot_panel(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("robot.html", {
        "request": request, "user": user, "can_drive": _can_drive(user),
    })


@app.get("/robot/stream")
async def robot_stream(request: Request):
    """Server-Sent Events — live telemetry streamed from the hardware bridge."""
    if not current_user(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    async def events():
        while True:
            if await request.is_disconnected():
                break
            try:
                payload = await robot.get_state()
            except Exception as exc:  # noqa: BLE001
                payload = {"error": str(exc)[:80]}
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(0.6)

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})


@app.post("/robot/drive")
async def robot_drive(request: Request):
    """Only an operator (admin role) may send drive commands — RBAC on the wire."""
    user = current_user(request)
    if not _can_drive(user):
        return JSONResponse({"error": "operator (admin) role required to drive"}, status_code=403)
    body = await request.json()
    return JSONResponse(await robot.drive(body.get("action", "stop"), body.get("speed", 0.5)))


@app.exception_handler(404)
async def not_found(request: Request, exc):
    user = request.session.get("user") if "session" in request.scope else None
    return templates.TemplateResponse("404.html", {"request": request, "user": user}, status_code=404)
