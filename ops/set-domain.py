#!/usr/bin/env python3
"""Freehold — add your production domain to the Keycloak realms.

Keycloak only accepts logins that redirect to a URL it knows. This adds
https://<domain>/* to every realm's redirect / web-origin / post-logout lists
(keeping localhost so dev still works). Run it on your production server BEFORE
the first `up` — realms import once (if they already imported, `down -v` first).

    python3 ops/set-domain.py freeholder.duckdns.org
"""
import json
import sys

from _common import REPO


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: set-domain.py <domain>   e.g. freeholder.duckdns.org")
        return 1
    domain = sys.argv[1].strip().rstrip("/")
    base = f"https://{domain}"

    for path in sorted((REPO / "keycloak" / "realms").glob("*.json")):
        realm = json.loads(path.read_text())
        for client in realm.get("clients", []):
            redirects = client.setdefault("redirectUris", [])
            if f"{base}/*" not in redirects:
                redirects.append(f"{base}/*")
            origins = client.setdefault("webOrigins", [])
            if base not in origins:
                origins.append(base)
            attrs = client.setdefault("attributes", {})
            existing = [p for p in attrs.get("post.logout.redirect.uris", "").split("##") if p]
            if f"{base}/*" not in existing:
                existing.append(f"{base}/*")
                attrs["post.logout.redirect.uris"] = "##".join(existing)
        path.write_text(json.dumps(realm, indent=2, ensure_ascii=False) + "\n")
        print(f"  {path.name}: + {base}")

    print(f"\nNow deploy on this server:")
    print(f"  SITE_DOMAIN={domain} CADDYFILE=./Caddyfile.prod \\")
    print(f"    docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d")
    print("(if the realms were already imported once, run `docker compose down -v` first)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
