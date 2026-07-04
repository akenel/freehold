"""Route-level tests via FastAPI's TestClient — no live Postgres/Keycloak needed.

Covers: public pages serve, auth guards redirect, RBAC-gated pages redirect,
the branded 404, and i18n switching. (Full OIDC login is exercised separately
against the live stack.)
"""
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_public_pages_serve():
    for path in ("/", "/terms", "/privacy", "/manifesto", "/healthz", "/version"):
        assert client.get(path).status_code == 200, path


def test_protected_pages_redirect_to_login_when_anonymous():
    for path in ("/dashboard", "/qa", "/console", "/account", "/feedback", "/backlog", "/money"):
        r = client.get(path, follow_redirects=False)
        assert r.status_code == 307, path
        assert r.headers["location"] == "/login", path


def test_unknown_path_renders_branded_404():
    r = client.get("/definitely-not-a-real-page", follow_redirects=False)
    assert r.status_code == 404
    assert "this ground isn't claimed" in r.text


def test_language_switch_via_query_renders_hindi():
    r = client.get("/?lang=hi")
    assert r.status_code == 200
    assert "फ्रीहोल्ड खड़ा है।" in r.text


def test_lang_route_sets_cookie_and_redirects():
    r = client.get("/lang/hi", follow_redirects=False)
    assert r.status_code == 303
    assert "lang=hi" in r.headers.get("set-cookie", "")


def test_healthz_reports_shape():
    body = client.get("/healthz").json()
    assert body["status"] == "ok"
    assert body["realm"] == "kc-sbx"   # sandbox env -> shared Keycloak's kc-sbx realm
