#!/usr/bin/env python3
"""Freehold — wire the Resend SMTP key into Keycloak's file vault.

Keycloak sends the "forgot password" (and verify-email) mails via Resend. The
realm JSONs reference the key as ${vault.resendkey} — the actual value NEVER
lives in git. This script reads RESEND_API_KEY from .env and writes it into the
gitignored vault files Keycloak reads at runtime, one per realm:

    keycloak/vault/<realm>_resendkey     (kc-sbx / kc-stg / kc-prd)

Run it once on each box before `up` (or after rotating the key), then restart
Keycloak so it re-reads the vault:

    python3 ops/set-smtp.py
"""
import sys

from _common import REPO, load_env

REALMS = ("kc-sbx", "kc-stg", "kc-prd")
VAULT_KEY = "resendkey"   # matches ${vault.resendkey} in the realm JSONs


def main() -> int:
    env = load_env()
    key = env.get("RESEND_API_KEY", "").strip()
    if not key or key.startswith("change_me"):
        print("ERROR: RESEND_API_KEY is not set (or still a placeholder) in .env")
        print("       Get it from https://resend.com — the same key you use for helixnet.")
        return 1

    vault = REPO / "keycloak" / "vault"
    vault.mkdir(exist_ok=True)
    for realm in REALMS:
        # files-plaintext vault naming: <realm>_<key> (no trailing newline —
        # Keycloak reads the file's bytes verbatim as the secret).
        path = vault / f"{realm}_{VAULT_KEY}"
        path.write_text(key)
        print(f"  wrote {path.relative_to(REPO)}  (Resend key for {realm})")

    print("\n✅ Resend key written to the vault for all realms.")
    print("   Restart Keycloak to pick it up:  docker compose up -d keycloak")
    print("   (fresh box: just `up` — the vault is read on boot.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
