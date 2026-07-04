"""Auth helper unit tests — the OIDC glue, tested as pure functions (no network)."""
import base64
import hashlib
from urllib.parse import parse_qs, urlparse

import auth


def test_make_pkce_is_valid_s256():
    verifier, challenge = auth.make_pkce()
    # challenge must be base64url(sha256(verifier)) with padding stripped (RFC 7636)
    expected = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    assert challenge == expected
    assert "=" not in challenge
    assert len(verifier) >= 43  # 32 bytes urlsafe-b64 => 43+ chars


def test_new_secret_is_unique():
    assert auth.new_secret() != auth.new_secret()


def test_build_auth_redirect_carries_pkce_and_scope():
    url = auth.build_auth_redirect("https://app/cb", "state1", "nonce1", "chal1", ui_locales="hi")
    assert url.startswith(auth.AUTH_URL + "?")
    q = parse_qs(urlparse(url).query)
    assert q["response_type"] == ["code"]
    assert q["code_challenge"] == ["chal1"]
    assert q["code_challenge_method"] == ["S256"]
    assert q["state"] == ["state1"] and q["nonce"] == ["nonce1"]
    assert q["scope"] == ["openid profile email"]
    assert q["ui_locales"] == ["hi"]
    assert q["client_id"] == [auth.CLIENT_ID]


def test_register_redirect_hits_registrations_endpoint():
    url = auth.build_register_redirect("https://app/cb", "s", "n", "c")
    assert url.startswith(auth.REGISTER_URL + "?")
    assert "registrations?" in url


def test_logout_redirect_includes_id_token_hint():
    url = auth.logout_redirect("the-id-token", "https://app/")
    q = parse_qs(urlparse(url).query)
    assert url.startswith(auth.LOGOUT_URL + "?")
    assert q["id_token_hint"] == ["the-id-token"]
    assert q["post_logout_redirect_uri"] == ["https://app/"]
