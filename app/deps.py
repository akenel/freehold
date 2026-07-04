"""Freehold — shared app dependencies.

Config, the template engine, the current-user lookup, and the RBAC guards — in one
place so the route modules under routers/ never import each other or main.py.
"""
import os

import asyncpg
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from markdown_it import MarkdownIt

import build_info
import i18n

APP_ENV = os.getenv("APP_ENV", "sandbox")
# One shared Keycloak holds all three realms; each environment uses its own.
_REALM_BY_ENV = {"sandbox": "kc-sbx", "staging": "kc-stg", "production": "kc-prd"}
KC_REALM = os.getenv("KC_REALM") or _REALM_BY_ENV.get(APP_ENV, f"kc-{APP_ENV}")
KC_PUBLIC_URL = os.getenv("KC_PUBLIC_URL", "http://localhost:8080")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8080").rstrip("/")
DATABASE_URL = os.getenv("DATABASE_URL", "")
SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-insecure-change-me")
# Mark the session cookie Secure whenever we're served over HTTPS (the default,
# even in dev via Caddy's internal CA). Override with SESSION_COOKIE_SECURE if needed.
SESSION_HTTPS_ONLY = os.getenv(
    "SESSION_COOKIE_SECURE", str(APP_BASE_URL.startswith("https"))
).strip().lower() in ("1", "true", "yes")


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
# with |safe: the renderer only emits a known, safe set of tags.
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


def require_admin(request: Request):
    """Returns the user if admin, else None (caller redirects/403s)."""
    user = current_user(request)
    if user and "admin" in user.get("roles", []):
        return user
    return None


def admin_or_deny(request: Request):
    """Guard for admin-only PAGES. Returns (user, None) for admins; otherwise
    (user_or_None, response) — a redirect to /login when logged out, or a clean 403
    forbidden page when logged in without the role. Caller: `if denied: return denied`."""
    user = current_user(request)
    if not user:
        return None, RedirectResponse("/login")
    if "admin" not in user.get("roles", []):
        return user, templates.TemplateResponse(
            "forbidden.html", {"request": request, "user": user}, status_code=403,
        )
    return user, None
