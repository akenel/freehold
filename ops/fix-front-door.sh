#!/usr/bin/env bash
# Recover Freehold's front door after a bad Caddy port change (Tig, 2026-07-09).
#
# Background: Caddy was intentionally on 127.0.0.1:8443 (a front router forwards
# public 443 -> 8443). A mistaken `docker-compose.prod.yml` run forced Caddy onto
# 0.0.0.0:443, which collided with that router and crash-looped it. This puts
# Caddy back to 127.0.0.1:8443 + Caddyfile.prod (the original working state).
#
# Safe + idempotent. Run on the box:  bash ops/fix-front-door.sh
set -uo pipefail
cd "$(dirname "$0")/.."                       # -> freehold repo root
sec(){ printf '\n\033[1;36m===== %s =====\033[0m\n' "$*"; }

sec "1. WHY caddy is crashing — last 15 log lines"
docker logs freehold-caddy-1 --tail 15 2>&1 || echo "(no logs)"

sec "2. WHAT is listening on public 80 / 443 (the front router should be here)"
( ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null ) | grep -E ':(80|443|8443)\b' || echo "(nothing on 80/443/8443)"

sec "3. caddy container BEFORE the fix"
docker ps -a --format '{{.Names}}  |  {{.Status}}  |  {{.Ports}}' | grep -i caddy || echo "(no caddy container)"

sec "4. FIX — put Caddy back to 127.0.0.1:8443 + Caddyfile.prod (base compose, NO prod port override)"
CADDYFILE=./Caddyfile.prod docker compose up -d caddy

sec "5. wait 6s, then verify"
sleep 6
echo "--- caddy container AFTER the fix (want: Up, 127.0.0.1:8443->443) ---"
docker ps --format '{{.Names}}  |  {{.Status}}  |  {{.Ports}}' | grep -i caddy || echo "(no caddy container)"
echo "--- does Caddy serve on the box now? ---"
code=$(curl -sk -o /dev/null -w '%{http_code}' --max-time 8 https://127.0.0.1:8443/healthz -H 'Host: www.wolfhold.app' 2>/dev/null || echo 000)
if [ "$code" = "200" ] || [ "$code" = "302" ] || [ "$code" = "303" ]; then
  echo "  ✅ Caddy@8443 answered HTTP $code — front door is back up"
else
  echo "  ⚠️  Caddy@8443 answered HTTP $code — screenshot this whole run for Tig"
fi

sec "DONE — screenshot everything above and send it to Tig"
