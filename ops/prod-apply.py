#!/usr/bin/env python3
"""Freehold — apply .env identity config onto the RUNNING Keycloak (idempotent).

The realm JSONs are clean templates; the deployment-specific identity bits live in
.env and are applied here, live, so a box is rebuildable in one command:

    restore .env  ->  docker compose ... up -d  ->  python3 ops/prod-apply.py

It reconciles the realm named by KC_REALM to match .env:
  * freehold-web client secret  == KC_CLIENT_SECRET
  * SMTP (host/port/user/from + vaulted password) — only if SMTP_PASSWORD is set
  * social IdPs (google/github/facebook) — enabled + clientId + vaulted secret, for
    each whose *_CLIENT_ID/*_CLIENT_SECRET is set (others left disabled)
  * first-broker-login: link an existing-email account by PASSWORD re-auth, not email
    (so social login needs no SMTP)

Reads only .env; writes secrets to the file vault (never printed). Safe to re-run.
Talks to Keycloak on the box-local admin port (127.0.0.1:8081).
"""
import json
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

REPO = pathlib.Path(__file__).resolve().parent.parent
BASE = "http://127.0.0.1:8081"
PROVIDERS = {  # alias: (id env, secret env, vault key, extra config)
    "google":   ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "googlesecret"),
    "github":   ("GITHUB_CLIENT_ID", "GITHUB_CLIENT_SECRET", "githubsecret"),
    "facebook": ("FACEBOOK_CLIENT_ID", "FACEBOOK_CLIENT_SECRET", "facebooksecret"),
}


def load_env():
    e = {}
    for line in (REPO / ".env").read_text().splitlines():
        s = line.strip()
        if s and not s.startswith("#") and "=" in s:
            k, v = s.split("=", 1)
            e[k.strip()] = v.strip()
    return e


def real(v):
    return bool(v) and not v.startswith("change_me")


def api(method, path, data=None, tok=None, form=False):
    h = {}
    if tok:
        h["Authorization"] = "Bearer " + tok
    body = None
    if data is not None:
        if form:
            body = urllib.parse.urlencode(data).encode(); h["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            body = json.dumps(data).encode(); h["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.getcode(), r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def main():
    env = load_env()
    realm = env.get("KC_REALM", "kc-prd")
    print(f"reconciling realm '{realm}' to .env ...")
    tok = json.loads(api("POST", "/realms/master/protocol/openid-connect/token", {
        "client_id": "admin-cli", "grant_type": "password",
        "username": env["KC_BOOTSTRAP_ADMIN_USERNAME"], "password": env["KC_BOOTSTRAP_ADMIN_PASSWORD"],
    }, form=True)[1])["access_token"]

    # 1) client secret
    clients = json.loads(api("GET", f"/admin/realms/{realm}/clients?clientId=freehold-web", tok=tok)[1])
    if clients and real(env.get("KC_CLIENT_SECRET", "")):
        cid = clients[0]["id"]; c = clients[0]; c["secret"] = env["KC_CLIENT_SECRET"]
        api("PUT", f"/admin/realms/{realm}/clients/{cid}", c, tok=tok)
        print("  ✓ freehold-web client secret aligned to KC_CLIENT_SECRET")

    # 2) SMTP (optional)
    vault = REPO / "keycloak" / "vault"; vault.mkdir(exist_ok=True)
    if real(env.get("SMTP_PASSWORD", "")):
        (vault / f"{realm}_smtppass").write_text(env["SMTP_PASSWORD"])
        r = json.loads(api("GET", f"/admin/realms/{realm}", tok=tok)[1])
        r["smtpServer"] = {"host": env.get("SMTP_HOST", "mail.smtp2go.com"), "port": env.get("SMTP_PORT", "587"),
                           "ssl": env.get("SMTP_SSL", "false"), "starttls": env.get("SMTP_STARTTLS", "true"),
                           "auth": "true", "user": env.get("SMTP_USER", ""), "password": "${vault.smtppass}",
                           "from": env.get("SMTP_FROM", ""), "fromDisplayName": env.get("SMTP_FROM_NAME", "Wolfhold")}
        api("PUT", f"/admin/realms/{realm}", r, tok=tok)
        print(f"  ✓ SMTP set ({env.get('SMTP_HOST')})")
    else:
        print("  · SMTP: SMTP_PASSWORD not set — skipped (forgot-password stays off)")

    # 3) social IdPs
    on = []
    for alias, (ide, se, vk) in PROVIDERS.items():
        cid, sec = env.get(ide, ""), env.get(se, "")
        if not (real(cid) and real(sec)):
            continue
        (vault / f"{realm}_{vk}").write_text(sec)
        idp = json.loads(api("GET", f"/admin/realms/{realm}/identity-provider/instances/{alias}", tok=tok)[1])
        idp["enabled"] = True
        idp.setdefault("config", {})["clientId"] = cid
        idp["config"]["clientSecret"] = "${vault." + vk + "}"
        api("PUT", f"/admin/realms/{realm}/identity-provider/instances/{alias}", idp, tok=tok)
        on.append(alias)
    print(f"  ✓ social logins enabled: {on or '(none configured)'}")

    # 4) first-broker-login: link by password, not email (no SMTP needed)
    flow = urllib.parse.quote("first broker login")
    execs = json.loads(api("GET", f"/admin/realms/{realm}/authentication/flows/{flow}/executions", tok=tok)[1])
    ev = [e for e in execs if e.get("providerId") == "idp-email-verification"]
    if ev and ev[0].get("requirement") != "DISABLED":
        api("PUT", f"/admin/realms/{realm}/authentication/flows/{flow}/executions",
            {"id": ev[0]["id"], "requirement": "DISABLED"}, tok=tok)
    print("  ✓ account-linking verifies by password re-auth (email step disabled)")

    print(f"\n✅ realm '{realm}' reconciled to .env. Rebuildable: restore .env, `up`, run this.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
