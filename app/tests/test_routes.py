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
    for path in ("/dashboard", "/qa", "/console", "/account", "/feedback", "/backlog", "/audit"):
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


# --- the empty-file-input trap ---------------------------------------------
# A browser that submits an upload form with nothing chosen still sends the
# part, as `filename=""`. Per RFC 7578 a part with an empty filename is a plain
# field, so it arrives as a str — and a route typed `file: UploadFile` answers
# with a raw 422 JSON blob before any of our own "Pick a file first." runs.
# Anonymous is the right way to test it: request validation happens BEFORE the
# login check, so reaching the redirect at all proves the body parsed.

def test_upload_with_empty_file_input_does_not_422():
    r = client.post("/lists/upload", data={"model": "none"},
                    files={"file": ("", b"", "application/octet-stream")},
                    follow_redirects=False)
    assert r.status_code != 422, "empty file input must not blow up on validation"
    assert r.headers["location"] == "/login"


def test_recipe_rerun_with_no_file_chosen_does_not_422():
    # Here it matters even more: re-running a saved recipe against the STORED
    # source means submitting with no file chosen is the normal path.
    r = client.post("/lists/recipe/anything/run", data={"model": "none", "src_key": ""},
                    files={"file": ("", b"", "application/octet-stream")},
                    follow_redirects=False)
    assert r.status_code != 422
    assert r.headers["location"] == "/login"
