#!/usr/bin/env bash
# PART 2 — THE FIX + POST-FLIGHT. Pre-flight = GO (.env has SITE_DOMAIN/AUTH_DOMAIN).
#
# Restarts Caddy WITH the prod overlay so it gets those vars + binds public 80/443
# (base compose alone omitted them -> {$SITE_DOMAIN} empty -> the line-16 crash).
# Then PROVES the site is back. Only the caddy container is touched.
set -uo pipefail
cd "$(dirname "$0")/.."
sec(){ printf '\n\033[1;36m===== %s =====\033[0m\n' "$*"; }

sec "1. THE FIX — start Caddy WITH the prod overlay (domains + public 80/443)"
COMPOSE_FILE=docker-compose.yml:docker-compose.prod.yml CADDYFILE=./Caddyfile.prod \
  docker compose up -d caddy

sec "2. wait 8s for Caddy to settle"
sleep 8

sec "POST-FLIGHT — prove it's back"
echo "--- caddy (want: Up, 0.0.0.0:443->443, NOT Restarting) ---"
docker ps --format '{{.Names}}  |  {{.Status}}  |  {{.Ports}}' | grep -i caddy || echo "  (no caddy!)"
echo
echo "--- public 80/443 listening now? ---"
( ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null ) | grep -E ':(80|443)\b' || echo "  (nothing — problem)"
echo
echo "--- site serving, checked from the box ---"
for p in /login /tempest; do
  code=$(curl -sk -o /dev/null -w '%{http_code}' --max-time 8 "https://127.0.0.1${p}" -H 'Host: www.wolfhold.app' 2>/dev/null || echo 000)
  echo "  www.wolfhold.app${p}  ->  HTTP ${code}"
done

sec "VERDICT"
echo "  ✅ GREEN if caddy is 'Up' on 0.0.0.0:443 AND /login + /tempest = 200"
echo "     -> refresh your browser (Ctrl+Shift+R), log in — Tempest is in the nav."
echo "  ❌ anything else -> screenshot this whole run for Tig."
sec "DONE — screenshot everything and send it to Tig"
