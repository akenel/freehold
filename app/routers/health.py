"""Service Health Dashboard — a status page that checks Postgres, Keycloak, MinIO, and app build.

The /status endpoint returns a JSON health report; /status/page renders an HTML dashboard
with green/red indicators. Each check is recorded in the health_checks table for history.
"""
import asyncio
import os

import asyncpg
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

import build_info
import deps
from db import async_session
from models import HealthCheck
from sqlalchemy import select

router = APIRouter()

# --- External service checks ---

async def check_postgres() -> tuple[bool, str]:
    """Check Postgres connectivity and version."""
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        return False, "DATABASE_URL is not set"
    try:
        conn = await asyncpg.connect(dsn=database_url, timeout=5)
        try:
            version = await conn.fetchval("SELECT version()")
        finally:
            await conn.close()
        return True, version.split(" on ")[0]
    except Exception as exc:
        return False, str(exc)


async def check_keycloak() -> tuple[bool, str]:
    """Check Keycloak availability via its health endpoint or base URL."""
    kc_url = os.getenv("KC_PUBLIC_URL", "http://localhost:8080").rstrip("/")
    try:
        async with asyncio.timeout(5):
            async with httpx.AsyncClient(timeout=5) as client:
                # Try the standard Keycloak health endpoint first
                resp = await client.get(f"{kc_url}/health/ready")
                if resp.status_code == 200:
                    return True, "Keycloak ready"
                # Fallback: just check if the base URL responds
                resp = await client.get(kc_url)
                if resp.status_code < 500:
                    return True, f"Keycloak responding ({resp.status_code})"
                return False, f"Keycloak returned {resp.status_code}"
    except Exception as exc:
        return False, str(exc)


async def check_minio() -> tuple[bool, str]:
    """Check MinIO availability via its health endpoint."""
    minio_url = os.getenv("MINIO_URL", "http://localhost:9000").rstrip("/")
    minio_health = f"{minio_url}/minio/health/live"
    try:
        async with asyncio.timeout(5):
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(minio_health)
                if resp.status_code == 200:
                    return True, "MinIO healthy"
                return False, f"MinIO returned {resp.status_code}"
    except Exception as exc:
        return False, str(exc)


async def check_app() -> tuple[bool, str]:
    """Check the app itself — build info proves we're running."""
    sha = build_info.sha()
    version = build_info.version()
    if sha == "dev":
        return True, f"Running {version} (dev mode)"
    return True, f"Running {version} ({sha})"


# The Ground Control Bridge is an OPTIONAL peer on a private network, not part of
# the Freehold stack. Two rules follow, both learned the hard way:
#   - OFF unless BRIDGE_URL is set. It used to default to a hard-coded Tailscale
#     address, so a prod box that cannot route there paid two 5s timeouts per page
#     load to discover that.
#   - ADVISORY. Reported, never folded into `overall`. An optional peer being
#     unreachable is not a Freehold outage, and a status page that cries degraded
#     over it is a red light that lies — same sin as a green one.
BRIDGE_URL = os.getenv("BRIDGE_URL", "").rstrip("/")


async def check_bridge() -> tuple[bool, str]:
    """Check Ground Control Bridge reachability. Only called when BRIDGE_URL is set."""
    try:
        async with asyncio.timeout(5):
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(BRIDGE_URL)
                # Report what we actually observed. A 200 proves it answered — it
                # does NOT prove the version or that auth is on, so don't claim it.
                if resp.status_code == 200:
                    return True, f"Reachable at {BRIDGE_URL} (HTTP 200)"
                return False, f"Bridge returned {resp.status_code}"
    except Exception as exc:
        return False, str(exc)


async def record_check(service: str, ok: bool, detail: str) -> None:
    """Record a health check result in the database."""
    try:
        async with async_session() as session:
            stmt = select(HealthCheck).where(HealthCheck.service == service)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                existing.status = "ok" if ok else "down"
                existing.detail = detail
            else:
                session.add(HealthCheck(
                    service=service,
                    status="ok" if ok else "down",
                    detail=detail,
                ))
            await session.commit()
    except Exception:
        # Don't let health recording break the health check itself
        pass


async def gather_checks() -> tuple[bool, list[dict]]:
    """Probe every service once, record the results, return (overall_ok, rows).

    Both /status and /status/page go through here so the JSON and the HTML can
    never disagree about what's up. `overall` counts only the services Freehold
    actually owns — advisory rows are shown but never flip the light.
    """
    postgres_ok, postgres_detail = await check_postgres()
    keycloak_ok, keycloak_detail = await check_keycloak()
    minio_ok, minio_detail = await check_minio()
    app_ok, app_detail = await check_app()

    rows = [
        {"key": "postgres", "name": "PostgreSQL", "ok": postgres_ok, "detail": postgres_detail, "advisory": False},
        {"key": "keycloak", "name": "Keycloak", "ok": keycloak_ok, "detail": keycloak_detail, "advisory": False},
        {"key": "minio", "name": "MinIO", "ok": minio_ok, "detail": minio_detail, "advisory": False},
        {"key": "app", "name": "App", "ok": app_ok, "detail": app_detail, "advisory": False},
    ]
    if BRIDGE_URL:
        bridge_ok, bridge_detail = await check_bridge()
        rows.append({"key": "bridge", "name": "Ground Control Bridge",
                     "ok": bridge_ok, "detail": bridge_detail, "advisory": True})

    await asyncio.gather(*(record_check(r["key"], r["ok"], r["detail"]) for r in rows))
    return all(r["ok"] for r in rows if not r["advisory"]), rows


@router.get("/status")
async def health_status():
    """JSON health report for all services."""
    overall, rows = await gather_checks()
    return JSONResponse({
        "status": "ok" if overall else "degraded",
        "services": {
            r["key"]: {"status": "ok" if r["ok"] else "down",
                       "detail": r["detail"], "advisory": r["advisory"]}
            for r in rows
        },
        "build": {"version": build_info.version(), "sha": build_info.sha(), "date": build_info.date()},
    })


@router.get("/status/page")
async def health_page(request: Request):
    """HTML health dashboard with green/red indicators."""
    user = deps.current_user(request)
    overall, services = await gather_checks()

    return deps.templates.TemplateResponse("status.html", {
        "request": request,
        "user": user,
        "overall_ok": overall,
        "services": services,
        "build": {"version": build_info.version(), "sha": build_info.sha(), "date": build_info.date()},
    })
