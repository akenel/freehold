# 2026-12-19 — Freehold Health Dashboard

## What we built
A service health dashboard that checks PostgreSQL, Keycloak, MinIO, and the app itself, with both JSON API (`/status`) and HTML page (`/status/page`).

## Key decisions

### 1. HealthCheck model is NOT append-only
Unlike `AuditEvent`, the `HealthCheck` table updates existing rows per service. This is intentional — we want the *current* state of each service, not a history log. The `checked_at` timestamp with `onupdate=func.now()` proves freshness.

### 2. Direct httpx usage, not deps.http_client()
The existing `deps.py` doesn't expose an `http_client()` helper. Other modules (analyze.py, auth.py, business_hub.py) use `httpx.AsyncClient()` directly, so we followed that pattern.

### 3. TestClient import path matters
Tests in `tests/` import `from main import app` (not `from app.main import app`) because the Docker container runs with `/app` as the working directory and Python path.

### 4. Graceful degradation on external checks
- Keycloak: tries `/health/ready` first, falls back to base URL
- MinIO: checks `/minio/health/live` endpoint
- All checks have 5-second timeouts so the dashboard never hangs
- Recording failures are swallowed — health checks must never fail due to logging issues

### 5. Build info as app health proof
The app check doesn't just return "ok" — it returns the actual build SHA and version from `build_info.py`. This proves the running code matches what was deployed.

## Files created/modified
- `app/models.py` — added `HealthCheck` model
- `app/routers/health.py` — new router with check functions
- `app/templates/status.html` — visual dashboard
- `app/main.py` — registered health router
- `app/tests/test_health.py` — 6 tests

## Test results
All 154 tests passing, including the 6 new health tests.
