#!/usr/bin/env python3
"""Freehold — wire an SMTP provider into Keycloak: vault the password + stamp the sender.

Keycloak sends "forgot password" / verify-email over SMTP. Provider-agnostic —
the default is SMTP2GO (free tier: 1,000 mails/mo, custom sender domains), but any
SMTP works (Resend, Brevo, SES, your own postfix). Two pieces:

  1. the SMTP password -> Keycloak's file vault (gitignored), referenced as
     ${vault.smtppass} in the realm JSONs, one file per realm:
         keycloak/vault/<realm>_smtppass     (kc-sbx / kc-stg / kc-prd)
  2. host / port / ssl / starttls / user / from / fromDisplayName -> stamped into
     each realm's smtpServer from the SMTP_* vars in .env (only those that are set;
     unset ones keep the committed default). The From MUST be a sender/domain your
     provider has verified, else mail is rejected.

Run once on each box before `up` (or after rotating creds / changing sender):

    python3 ops/set-smtp.py
"""
import json
import sys

from _common import REPO, load_env

REALMS = ("kc-sbx", "kc-stg", "kc-prd")
VAULT_KEY = "smtppass"   # matches ${vault.smtppass} in the realm JSONs

# smtpServer field  ->  .env var that overrides it (when set)
FIELD_ENV = {
    "host": "SMTP_HOST",
    "port": "SMTP_PORT",
    "ssl": "SMTP_SSL",
    "starttls": "SMTP_STARTTLS",
    "user": "SMTP_USER",
    "from": "SMTP_FROM",
    "fromDisplayName": "SMTP_FROM_NAME",
}


def _real(v: str) -> bool:
    v = (v or "").strip()
    return bool(v) and not v.startswith("change_me")


def main() -> int:
    env = load_env()
    pw = env.get("SMTP_PASSWORD", "").strip()
    if not _real(pw):
        print("ERROR: SMTP_PASSWORD is not set (or still a placeholder) in .env")
        print("       Create an SMTP user at your provider (default: smtp2go.com).")
        return 1

    vault = REPO / "keycloak" / "vault"
    vault.mkdir(exist_ok=True)
    for realm in REALMS:
        # files-plaintext vault naming: <realm>_<key>, verbatim bytes (no newline).
        (vault / f"{realm}_{VAULT_KEY}").write_text(pw)

    # Stamp any SMTP_* overrides into every realm's smtpServer.
    stamped = {}
    for realm in REALMS:
        path = REPO / "keycloak" / "realms" / f"{realm}-realm.json"
        data = json.loads(path.read_text())
        smtp = data.setdefault("smtpServer", {})
        smtp["auth"] = "true"
        smtp["password"] = f"${{vault.{VAULT_KEY}}}"
        for field, var in FIELD_ENV.items():
            if _real(env.get(var, "")):
                smtp[field] = env[var].strip()
                stamped[field] = env[var].strip()
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    print(f"  vaulted SMTP password for all realms (keycloak/vault/*_{VAULT_KEY})")
    if stamped:
        print("  stamped into realms: " + ", ".join(f"{k}={v}" for k, v in stamped.items()))
    else:
        print("  no SMTP_* overrides set — keeping the committed smtpServer defaults")
    print("\n✅ SMTP wired for all realms.")
    print("   Restart Keycloak to pick it up:  docker compose up -d keycloak")
    print("   (fresh box: just `up` — the vault + realms load on boot.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
