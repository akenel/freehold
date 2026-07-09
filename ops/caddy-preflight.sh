#!/usr/bin/env bash
# PART 1 — PRE-FLIGHT (look-only). Confirms the Caddy fix is safe BEFORE running it.
#
# Proven root cause: Caddy was started WITHOUT SITE_DOMAIN/AUTH_DOMAIN (base compose,
# no prod overlay), so {$SITE_DOMAIN} was empty and Caddy crashed at Caddyfile.prod:16.
# Fix = start Caddy with the prod overlay so it gets those vars + binds public 80/443.
# This script CHANGES NOTHING — it just verifies and prints GO / NO-GO.
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
SITE=$(grep -E '^SITE_DOMAIN=' .env 2>/dev/null | cut -d= -f2-); SITE=${SITE:-www.wolfhold.app}
AUTH=$(grep -E '^AUTH_DOMAIN=' .env 2>/dev/null | cut -d= -f2-); AUTH=${AUTH:-auth.wolfhold.app}
docker run --rm -e SITE_DOMAIN="$SITE" -e AUTH_DOMAIN="$AUTH" \
  -v "$PWD/Caddyfile.prod:/etc/caddy/Caddyfile:ro" caddy:2-alpine \
  caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile 2>&1 | grep -iE 'error|valid config' | head -3

sec "3. Current caddy container (expect: Restarting)"
docker ps -a --format '{{.Names}}  |  {{.Status}}  |  {{.Ports}}' | grep -i caddy || echo "  (none)"

sec "4. What's on public 80 / 443 right now"
( ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null ) | grep -E ':(80|443)\b' || echo "  (nothing — expected while caddy is down)"

sec "VERDICT"
if [ "$GO" = 1 ]; then
  echo "  ✅ GO — .env already has the domains. Fix = restart Caddy WITH the prod overlay"
  echo "         (gives it SITE_DOMAIN/AUTH_DOMAIN + binds public 80/443). Nothing else changes."
else
  echo "  ⚠️  NO-GO yet — .env is missing SITE_DOMAIN/AUTH_DOMAIN. The fix will ADD them"
  echo "         (SITE_DOMAIN=www.wolfhold.app, AUTH_DOMAIN=auth.wolfhold.app) then restart."
  echo "         Confirm those two values with Tig before running the fix."
fi
echo "  (nothing was changed — this was look-only)"
sec "DONE — screenshot & send to Tig. He gives you PART 2 (the fix) once this says GO."
