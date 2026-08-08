"""Tests for the health check endpoint and status page."""
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


@pytest.mark.parametrize("endpoint", ["/status", "/status/page"])
def test_health_endpoints_respond(endpoint):
    """Both health endpoints should respond without errors."""
    resp = client.get(endpoint)
    assert resp.status_code in (200, 307)  # 307 if redirect to login for page
