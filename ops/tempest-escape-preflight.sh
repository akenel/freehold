#!/usr/bin/env bash
# PART 1 — PRE-FLIGHT (look-only). Run ON THE BOX, in ~/freehold, before deploying
# the Tempest "escape hatch" (corner ← FREEHOLD link + Esc key on /tempest).
#
# The change is one static file — app/static/tempest.html — so the blast radius is
# small. What this checks is the stuff that has actually bitten us before:
#   2026-07-09  Caddy started from base compose (no prod overlay) -> whole front door dark
#   2026-08-09  stock caddy:2-alpine + Caddyfile.prod -> acme_dns porkbun unparseable, crash
# This script CHANGES NOTHING. It verifies and prints GO / NO-GO.
set -uo pipefail
cd "$(dirname "$0")/.."
sec(){ printf '\n\033[1;36m===== %s =====\033[0m\n' "$*"; }
GO=1
SITE=$(grep -E '^SITE_DOMAIN=' .env 2>/dev/null | cut -d= -f2-); SITE=${SITE:-www.wolfhold.app}

sec "1. Is the escape-hatch change actually here? (did the git pull land?)"
# The decisive tell — deploying without pulling is how you 'deploy' nothing and
# then wonder why the page looks identical.
if grep -q 'id="back"' app/static/tempest.html 2>/dev/null; then
  echo "  ✅ app/static/tempest.html contains the corner link (id=\"back\")"
  grep -q 'ESC — EXIT' app/static/tempest.html \
    && echo "  ✅ the hint line advertises ESC — EXIT" \
    || { echo "  ❌ hint line not updated — partial/stale file"; GO=0; }
  grep -q 'function leaveGame' app/static/tempest.html \
    && echo "  ✅ leaveGame() present (Esc handler)" \
    || { echo "  ❌ leaveGame() missing — partial/stale file"; GO=0; }
else
  echo "  ❌ tempest.html has NO escape hatch — you're on an old commit. Run: git pull"
  GO=0
fi
echo "  local HEAD: $(git rev-parse --short HEAD 2>/dev/null || echo '?')  ($(git log -1 --format=%s 2>/dev/null | cut -c1-60))"

sec "2. Does the page still parse as HTML/JS? (no half-finished edit)"
# Cheap structural sanity: tag balance + both <script> blocks intact.
opens=$(grep -c '<script>' app/static/tempest.html || true)
closes=$(grep -c '</script>' app/static/tempest.html || true)
if [ "$opens" = "$closes" ] && [ "$opens" -ge 2 ]; then
  echo "  ✅ $opens <script> blocks, $closes closers — balanced"
else
  echo "  ❌ script tags unbalanced ($opens open / $closes close)"; GO=0
fi

sec "3. Caddy: right image, up, holding public 80/443?"
running_image=$(docker inspect freehold-caddy-1 --format '{{.Config.Image}}' 2>/dev/null || echo "")
case "$running_image" in
  "")                  echo "  ❌ no freehold-caddy-1 container — front door is DOWN"; GO=0 ;;
  "freehold-caddy:prd") echo "  ✅ running image: $running_image" ;;
  *)                   echo "  ❌ running image: $running_image — WRONG (needs freehold-caddy:prd)"
                       echo "     That's the base-compose image: the prod overlay was not applied."; GO=0 ;;
esac
docker ps --format '{{.Names}}  |  {{.Status}}  |  {{.Ports}}' | grep -i caddy || echo "  (caddy not in docker ps)"

sec "4. What is live RIGHT NOW (the 'before' snapshot — screenshot this)"
for path in / /tempest /dashboard; do
  code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 12 "https://$SITE$path" 2>/dev/null || echo "ERR")
  echo "  https://$SITE$path  ->  HTTP $code"
done
echo "  currently-served build:"
curl -sS --max-time 12 "https://$SITE/version" 2>/dev/null | head -c 300 || echo "  (no /version)"
echo
echo -n "  escape hatch live already? "
if curl -sS --max-time 12 "https://$SITE/tempest" 2>/dev/null | grep -q 'id="back"'; then
  echo "YES — already deployed, this would be a no-op"
else
  echo "no (expected — that's what we're shipping)"
fi

sec "5. Neighbours that must NOT break (same Caddy, same box)"
for host in "$SITE" "$(grep -E '^AUTH_DOMAIN=' .env 2>/dev/null | cut -d= -f2- || echo auth.wolfhold.app)"; do
  [ -n "$host" ] || continue
  code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 12 "https://$host/" 2>/dev/null || echo "ERR")
  echo "  https://$host/  ->  HTTP $code"
done

sec "VERDICT"
if [ "$GO" = 1 ]; then
  echo "  ✅ GO — one static file changes. Deploy with:"
  echo "         make deploy ENV=production"
  echo "     (stamps a new build, backup-gate runs first. Its 60s health wait can time"
  echo "      out while migrations run — that is often NOT fatal; the post-flight is"
  echo "      what decides.)"
  echo "     Then run:  bash ops/tempest-escape-postflight.sh"
else
  echo "  ⚠️  NO-GO — fix every ❌ above first, then re-run this. Do not deploy."
fi
echo "  (nothing was changed — this was look-only)"
sec "DONE — screenshot & send to Tig. Say 'deploy' and he takes it from here."
