"""Freehold — Phase 1 hello.

A deliberately tiny FastAPI app whose only job is to PROVE the skeleton is real:
it reads its environment/realm from config and it actually connects to Postgres.
The login flow (OIDC/RBAC) arrives in Phase 2 — this is the foundation, poured.
"""
import os
import asyncpg
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

APP_ENV = os.getenv("APP_ENV", "sandbox")
KC_REALM = os.getenv("KC_REALM", f"freehold-{APP_ENV}")
KC_PUBLIC_URL = os.getenv("KC_PUBLIC_URL", "http://localhost:8080")
DATABASE_URL = os.getenv("DATABASE_URL", "")

app = FastAPI(title="Freehold", version="0.1.0-phase1")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


async def db_check() -> tuple[bool, str]:
    """Return (ok, message) after a live round-trip to Postgres."""
    if not DATABASE_URL:
        return False, "DATABASE_URL is not set"
    try:
        conn = await asyncpg.connect(dsn=DATABASE_URL, timeout=5)
        try:
            version = await conn.fetchval("SELECT version()")
        finally:
            await conn.close()
        return True, version.split(" on ")[0]
    except Exception as exc:  # noqa: BLE001 — report anything, this is a health probe
        return False, str(exc)


@app.get("/healthz")
async def healthz():
    ok, _ = await db_check()
    return JSONResponse({"status": "ok", "env": APP_ENV, "realm": KC_REALM, "db": ok})


@app.get("/")
async def index(request: Request):
    ok, message = await db_check()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "env": APP_ENV,
            "realm": KC_REALM,
            "kc_url": KC_PUBLIC_URL,
            "db_ok": ok,
            "db_msg": message,
        },
    )
