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


@router.get("/status")
async def health_status():
    """JSON health report for all services."""
    postgres_ok, postgres_detail = await check_postgres()
    keycloak_ok, keycloak_detail = await check_keycloak()
    minio_ok, minio_detail = await check_minio()
    app_ok, app_detail = await check_app()
    
    # Record results
    await asyncio.gather(
        record_check("postgres", postgres_ok, postgres_detail),
        record_check("keycloak", keycloak_ok, keycloak_detail),
        record_check("minio", minio_ok, minio_detail),
        record_check("app", app_ok, app_detail),
    )
    
    overall = all([postgres_ok, keycloak_ok, minio_ok, app_ok])
    
    return JSONResponse({
        "status": "ok" if overall else "degraded",
        "services": {
            "postgres": {"status": "ok" if postgres_ok else "down", "detail": postgres_detail},
            "keycloak": {"status": "ok" if keycloak_ok else "down", "detail": keycloak_detail},
            "minio": {"status": "ok" if minio_ok else "down", "detail": minio_detail},
            "app": {"status": "ok" if app_ok else "down", "detail": app_detail},
        },
        "build": {"version": build_info.version(), "sha": build_info.sha(), "date": build_info.date()},
    })


@router.get("/status/page")
async def health_page(request: Request):
    """HTML health dashboard with green/red indicators."""
    user = deps.current_user(request)
    
    postgres_ok, postgres_detail = await check_postgres()
    keycloak_ok, keycloak_detail = await check_keycloak()
    minio_ok, minio_detail = await check_minio()
    app_ok, app_detail = await check_app()
    
    # Record results
    await asyncio.gather(
        record_check("postgres", postgres_ok, postgres_detail),
        record_check("keycloak", keycloak_ok, keycloak_detail),
        record_check("minio", minio_ok, minio_detail),
        record_check("app", app_ok, app_detail),
    )
    
    overall = all([postgres_ok, keycloak_ok, minio_ok, app_ok])
    
    services = [
        {"name": "PostgreSQL", "ok": postgres_ok, "detail": postgres_detail},
        {"name": "Keycloak", "ok": keycloak_ok, "detail": keycloak_detail},
        {"name": "MinIO", "ok": minio_ok, "detail": minio_detail},
        {"name": "App", "ok": app_ok, "detail": app_detail},
    ]
    
    return deps.templates.TemplateResponse("status.html", {
        "request": request,
        "user": user,
        "overall_ok": overall,
        "services": services,
        "build": {"version": build_info.version(), "sha": build_info.sha(), "date": build_info.date()},
    })
