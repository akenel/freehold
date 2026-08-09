"""Tests for the health check endpoint and status page."""
import asyncio

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_status_json():
    """The /status endpoint returns a valid JSON health report."""
    resp = client.get("/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "services" in data
    assert "build" in data
    assert data["status"] in ("ok", "degraded")
    
    # Check service structure
    services = data["services"]
    assert "postgres" in services
    assert "keycloak" in services
    assert "minio" in services
    assert "app" in services
    
    for svc_name, svc_data in services.items():
        assert "status" in svc_data
        assert "detail" in svc_data
        assert svc_data["status"] in ("ok", "down")


def test_health_status_page():
    """The /status/page endpoint returns an HTML page."""
    resp = client.get("/status/page")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert b"Service Health" in resp.content
    assert b"All systems operational" in resp.content or b"Some services degraded" in resp.content


def test_health_checks_postgres():
    """Postgres check should always return something (even if down)."""
    resp = client.get("/status")
    assert resp.status_code == 200
    data = resp.json()
    postgres = data["services"]["postgres"]
    # Postgres should be ok in test environment or have a meaningful error
    assert postgres["status"] in ("ok", "down")
    assert len(postgres["detail"]) > 0


def test_health_checks_app():
    """App check should always return ok with build info."""
    resp = client.get("/status")
    assert resp.status_code == 200
    data = resp.json()
    app_check = data["services"]["app"]
    assert app_check["status"] == "ok"
    assert "Running" in app_check["detail"]
    
    # Build info should match
    assert data["build"]["version"] is not None
    assert data["build"]["sha"] is not None


def test_bridge_absent_when_unconfigured():
    """No BRIDGE_URL -> no bridge row, and no 5s timeout paid to discover that.

    The bridge is an optional peer on a private network. A prod box that can't
    route there must not probe it on every page load.
    """
    from routers import health

    assert health.BRIDGE_URL == "", "test env must not configure a bridge"
    data = client.get("/status").json()
    assert "bridge" not in data["services"]


def test_advisory_service_never_degrades_overall(monkeypatch):
    """An unreachable advisory peer is reported, but `overall` stays ok.

    Regression guard: the bridge check was once folded into
    `all([...bridge_ok])`, so a peer Freehold doesn't own could paint prod
    degraded. asyncio.run keeps this plugin-free — the suite has no async runner.
    """
    from routers import health

    async def ok(detail):
        return True, detail

    monkeypatch.setattr(health, "BRIDGE_URL", "http://127.0.0.1:1")   # nothing listens
    monkeypatch.setattr(health, "check_postgres", lambda: ok("pg"))
    monkeypatch.setattr(health, "check_keycloak", lambda: ok("kc"))
    monkeypatch.setattr(health, "check_minio", lambda: ok("minio"))
    monkeypatch.setattr(health, "check_app", lambda: ok("build"))

    overall, rows = asyncio.run(health.gather_checks())

    bridge = next(r for r in rows if r["key"] == "bridge")
    assert bridge["advisory"] is True
    assert bridge["ok"] is False, "nothing listens on port 1 — it must report down"
    assert overall is True, "an advisory peer must never flip the overall light"


@pytest.mark.parametrize("endpoint", ["/status", "/status/page"])
def test_health_endpoints_respond(endpoint):
    """Both health endpoints should respond without errors."""
    resp = client.get(endpoint)
    assert resp.status_code in (200, 307)  # 307 if redirect to login for page
