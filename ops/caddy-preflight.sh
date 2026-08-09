#!/usr/bin/env bash
# PART 1 — PRE-FLIGHT (look-only). Confirms the Caddy fix is safe BEFORE running it.
#
# Both proven root causes are the SAME mistake — Caddy started from base compose with
# no prod overlay — and both take the whole front door down (app, auth, ai at once):
#   2026-07-09  no SITE_DOMAIN/AUTH_DOMAIN -> empty {$SITE_DOMAIN}, crash at Caddyfile.prod:16
#   2026-08-09  stock caddy:2-alpine + Caddyfile.prod -> `acme_dns porkbun` unparseable, crash
# Fix both ways: start Caddy WITH the prod overlay (real domains, freehold-caddy:prd,
# public 80/443). This script CHANGES NOTHING — it just verifies and prints GO / NO-GO.
set -uo pipefail
cd "$(dirname "$0")/.."
sec(){ printf '\n\033[1;36m===== %s =====\033[0m\n' "$*"; }
GO=1

sec "1. Does .env have the two domains Caddy needs?"
for v in SITE_DOMAIN AUTH_DOMAIN; do
  val=$(grep -E "^$v=" .env 2>/dev/null | head -1 | cut -d= -f2-)
  if [ -n "$val" ]; then echo "  ✅ $v = $val"; else echo "  ❌ $v is MISSING/empty in .env"; GO=0; fi
done

sec "2. Will Caddyfile.prod parse WITH your real domains? (local proof, throwaway caddy)"
# Validate with the PORKBUN-enabled image, never stock caddy. Caddyfile.prod:21 uses
# `acme_dns porkbun`, a module that only exists in freehold-caddy:prd (caddy/Dockerfile).
# Stock caddy:2-alpine ALWAYS fails here with "module not registered: dns.providers.
# porkbun" — a false alarm that read like the root cause during the 2026-08-09 outage.
SITE=$(grep -E '^SITE_DOMAIN=' .env 2>/dev/null | cut -d= -f2-); SITE=${SITE:-www.wolfhold.app}
AUTH=$(grep -E '^AUTH_DOMAIN=' .env 2>/dev/null | cut -d= -f2-); AUTH=${AUTH:-auth.wolfhold.app}
PRD_IMAGE=freehold-caddy:prd
if docker image inspect "$PRD_IMAGE" >/dev/null 2>&1; then
  docker run --rm -e SITE_DOMAIN="$SITE" -e AUTH_DOMAIN="$AUTH" \
    -v "$PWD/Caddyfile.prod:/etc/caddy/Caddyfile:ro" "$PRD_IMAGE" \
    caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile 2>&1 | grep -iE 'error|valid config' | head -3
else
  echo "  ❌ $PRD_IMAGE is not built — Caddyfile.prod CANNOT parse without it. Build it:"
  echo "       CADDYFILE=./Caddyfile.prod docker compose \\"
  echo "         -f docker-compose.yml -f docker-compose.prod.yml build caddy"
  GO=0
fi

sec "3. Current caddy container (want: Up, image freehold-caddy:prd, 80+443 bound)"
docker ps -a --format '{{.Names}}  |  {{.Status}}  |  {{.Ports}}' | grep -i caddy || echo "  (none)"
# The decisive tell: stock image + Caddyfile.prod = crash loop, every host behind it dark.
running_image=$(docker inspect freehold-caddy-1 --format '{{.Config.Image}}' 2>/dev/null || echo "")
case "$running_image" in
  "")             echo "  (no freehold-caddy-1 container)" ;;
  "$PRD_IMAGE")   echo "  ✅ running image: $running_image" ;;
  *)              echo "  ❌ running image: $running_image — WRONG. Needs $PRD_IMAGE for acme_dns porkbun."
                  echo "     This is the base-compose image (docker-compose.yml): the prod overlay was not applied."
                  GO=0 ;;
esac

sec "4. What's on public 80 / 443 right now"
( ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null ) | grep -E ':(80|443)\b' || echo "  (nothing — expected while caddy is down)"

sec "VERDICT"
if [ "$GO" = 1 ]; then
  echo "  ✅ GO — restart Caddy WITH the prod overlay (real domains + freehold-caddy:prd"
  echo "         + public 80/443). Only caddy is touched; no app image is rebuilt."
else
  echo "  ⚠️  NO-GO — fix whatever is marked ❌ above first (missing .env domains, or the"
  echo "         freehold-caddy:prd image unbuilt / the wrong image running). Re-run this."
fi
echo "  (nothing was changed — this was look-only)"
sec "DONE — screenshot & send to Tig. He gives you PART 2 (the fix) once this says GO."
