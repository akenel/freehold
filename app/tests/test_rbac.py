"""RBAC gating — the admin-only routes must redirect the logged-out, 403 the staff,
and admit the admin. Infra-free: we monkeypatch the session user."""
import pytest
from fastapi.testclient import TestClient

import deps
import main

client = TestClient(main.app, follow_redirects=False)


@pytest.fixture
def as_user(monkeypatch):
    """Pretend a given user is logged in (or None) — patched where the routes read it."""
    def _set(user):
        monkeypatch.setattr(deps, "current_user", lambda request: user)
    return _set


ADMIN = {"username": "boss", "name": "Boss", "roles": ["admin"]}
STAFF = {"username": "sam", "name": "Sam", "roles": ["staff"]}


def test_dashboard_redirects_when_logged_out(as_user):
    as_user(None)
    r = client.get("/dashboard")
    assert r.status_code in (302, 303, 307)
    assert "/login" in r.headers["location"]


def test_dashboard_ok_when_logged_in(as_user):
    as_user(STAFF)
    assert client.get("/dashboard").status_code == 200


def test_console_redirects_when_logged_out(as_user):
    as_user(None)
    r = client.get("/console")
    assert r.status_code in (302, 303, 307) and "/login" in r.headers["location"]


def test_console_forbidden_for_staff(as_user):
    as_user(STAFF)
    assert client.get("/console").status_code == 403


def test_console_ok_for_admin(as_user):
    as_user(ADMIN)
    assert client.get("/console").status_code == 200


def test_audit_forbidden_for_staff(as_user):
    # /audit is admin-only; the guard denies before any DB read (infra-free safe).
    as_user(STAFF)
    assert client.get("/audit").status_code == 403


def test_robot_drive_requires_admin(as_user):
    # POST /robot/drive is operator-only (admin role) — staff gets 403 JSON
    as_user(STAFF)
    r = client.post("/robot/drive", json={"action": "forward", "speed": 0.5})
    assert r.status_code == 403
