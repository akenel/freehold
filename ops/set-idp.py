#!/usr/bin/env python3
"""Freehold — turn on social logins (Google / GitHub / Facebook) as code.

Each provider is defined in every realm JSON but ships DISABLED with an empty
clientId, so a fresh clone shows no broken buttons. This script reads the client
id + secret from .env and, for each provider you've actually configured:

  * writes the secret into Keycloak's file vault (never committed), and
  * stamps the clientId in + flips the provider ENABLED in the realm JSONs.

Providers you leave unconfigured stay disabled. Run it BEFORE `up` (realms import
once); if Keycloak already imported, re-run then `docker compose down && up` (or
`up -d keycloak` on a fresh box). Idempotent.

    python3 ops/set-idp.py

Client SECRETS are secrets — keep them in .env (gitignored). Client IDs are not
secret; this writes them into the realm JSON (fine to commit in your own fork).
"""
import json
import sys

from _common import REPO, load_env

REALMS = ("kc-sbx", "kc-stg", "kc-prd")

# alias -> (env var for client id, env var for secret, vault key in ${vault.X})
PROVIDERS = {
    "google":   ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "googlesecret"),
    "github":   ("GITHUB_CLIENT_ID", "GITHUB_CLIENT_SECRET", "githubsecret"),
    "facebook": ("FACEBOOK_CLIENT_ID", "FACEBOOK_CLIENT_SECRET", "facebooksecret"),
}


def _set(value: str) -> bool:
    """A value is 'really set' if it's non-empty and not a change_me placeholder."""
    v = (value or "").strip()
    return bool(v) and not v.startswith("change_me")


def configure(realm_dir, vault_dir, env: dict) -> list[str]:
    """Enable + stamp every configured provider across all realms. Returns the
    list of aliases that were turned on. Pure enough to unit-test with temp dirs."""
    enabled = []
    for alias, (id_env, secret_env, vault_key) in PROVIDERS.items():
        client_id, secret = env.get(id_env, ""), env.get(secret_env, "")
        if not (_set(client_id) and _set(secret)):
            print(f"  {alias}: not configured (skipped) — set {id_env} + {secret_env} in .env")
            continue
        # secret -> vault file per realm (same secret across realms)
        vault_dir.mkdir(parents=True, exist_ok=True)
        for realm in REALMS:
            (vault_dir / f"{realm}_{vault_key}").write_text(secret.strip())
        # clientId + enabled -> each realm JSON
        for realm in REALMS:
            path = realm_dir / f"{realm}-realm.json"
            data = json.loads(path.read_text())
            for idp in data.get("identityProviders", []):
                if idp.get("alias") == alias:
                    idp["enabled"] = True
                    idp.setdefault("config", {})["clientId"] = client_id.strip()
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        enabled.append(alias)
        print(f"  {alias}: enabled + clientId stamped, secret vaulted for all realms")
    return enabled


def main() -> int:
    env = load_env()
    enabled = configure(REPO / "keycloak" / "realms", REPO / "keycloak" / "vault", env)
    if not enabled:
        print("\nNothing configured yet. Add a provider's *_CLIENT_ID/*_CLIENT_SECRET to")
        print(".env (see docs/SOCIAL-LOGIN.md for the OAuth-app setup), then re-run.")
        return 1
    print(f"\n✅ Social login on for: {', '.join(enabled)}")
    print("   Fresh box: just `up`. Already running: `docker compose down && up -d`")
    print("   (realms re-import), or set them in the admin console to avoid a wipe.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
