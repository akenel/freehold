"""Freehold — the system pulse.

One honest screen that actually probes the moving parts, instead of a green light
that lies. Each check returns (status, detail): status is ok / error / info.
"""
import os

import httpx
from sqlalchemy import text

import build_info
from db import async_session

KC_INTERNAL = os.getenv("KC_INTERNAL_URL", "http://keycloak:8080").rstrip("/")
REALM = os.getenv("KC_REALM", "freehold-sandbox")
APP_ENV = os.getenv("APP_ENV", "?")


async def _database_and_migrations() -> tuple[tuple, tuple]:
    try:
        async with async_session() as s:
            version = (await s.execute(text("SELECT version()"))).scalar()
            revision = (await s.execute(text("SELECT version_num FROM alembic_version"))).scalar()
        db = ("ok", version.split(" on ")[0])
        mig = ("ok", f"at revision {revision}") if revision else ("error", "no alembic_version")
        return db, mig
    except Exception as exc:  # noqa: BLE001
        return ("error", str(exc)[:90]), ("error", "unreachable")


async def _keycloak() -> tuple:
    url = f"{KC_INTERNAL}/realms/{REALM}/.well-known/openid-configuration"
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(url)
            resp.raise_for_status()
        return ("ok", resp.json().get("issuer", ""))
    except Exception as exc:  # noqa: BLE001
        return ("error", str(exc)[:90])


async def pulse() -> list[dict]:
    (db_status, db_detail), (mig_status, mig_detail) = await _database_and_migrations()
    kc_status, kc_detail = await _keycloak()
    return [
        {"name": "Database", "status": db_status, "detail": db_detail},
        {"name": "Migrations", "status": mig_status, "detail": mig_detail},
        {"name": "Keycloak", "status": kc_status, "detail": kc_detail},
        {"name": "Build", "status": "info",
         "detail": f"{build_info.version()} · {build_info.sha()} · env {APP_ENV}"},
    ]
