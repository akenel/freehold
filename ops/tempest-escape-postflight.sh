#!/usr/bin/env bash
# PART 2 — POST-FLIGHT. Run ON THE BOX, in ~/freehold, immediately AFTER
#   make deploy ENV=production
# Proves the escape hatch is really serving and that nothing else went dark.
# Nothing is "done" until this prints ✅ 100%.
set -uo pipefail
cd "$(dirname "$0")/.."
sec(){ printf '\n\033[1;36m===== %s =====\033[0m\n' "$*"; }
OK=1
SITE=$(grep -E '^SITE_DOMAIN=' .env 2>/dev/null | cut -d= -f2-); SITE=${SITE:-www.wolfhold.app}
AUTH=$(grep -E '^AUTH_DOMAIN=' .env 2>/dev/null | cut -d= -f2-); AUTH=${AUTH:-auth.wolfhold.app}
HEAD_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "?")

sec "0. Am I actually on the wolfhold box?"
# Same guard as the pre-flight: off-box, HEAD here is not the HEAD that was
# deployed, so the SHA comparison below would compare two unrelated things.
BOX_IP=167.233.125.248
myip=$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7; exit}')
myip=${myip:-$(hostname -I 2>/dev/null | awk '{print $1}')}
if [ "$myip" = "$BOX_IP" ]; then
  echo "  ✅ on the box — $(hostname) · $myip"
elif [ "${FORCE_OFFBOX:-0}" = "1" ]; then
  echo "  ⚠️  NOT the box ($(hostname) · ${myip:-unknown}) — FORCE_OFFBOX=1 set; the SHA check in §1 is meaningless from here"
else
  echo "  ❌ STOP — this is not the wolfhold box."
  echo "     here:     $(hostname) · ${myip:-unknown}"
  echo "     expected: $BOX_IP"
  echo "     Run:  ssh wolfhold   then  cd ~/freehold && bash ops/tempest-escape-postflight.sh"
  echo "     (deliberate override: FORCE_OFFBOX=1 bash $0)"
  exit 2
fi

sec "1. Is the NEW build actually serving? (not a cached 'before' in disguise)"
VER=$(curl -sS --max-time 15 "https://$SITE/version" 2>/dev/null || echo "")
echo "  /version -> ${VER:-(nothing)}"
echo "  local HEAD -> $HEAD_SHA"
if [ -n "$VER" ] && echo "$VER" | grep -q "$HEAD_SHA"; then
  echo "  ✅ served SHA matches local HEAD ($HEAD_SHA)"
else
  echo "  ❌ served SHA does NOT match HEAD — the deploy did not take (old container still up?)"
  OK=0
fi

sec "2. THE ACTUAL FEATURE — is the escape hatch in the page the world receives?"
PAGE=$(curl -sS --max-time 15 "https://$SITE/tempest" 2>/dev/null || echo "")
check(){ # needle, label
  if printf '%s' "$PAGE" | grep -q "$1"; then echo "  ✅ $2"; else echo "  ❌ $2 — MISSING"; OK=0; fi
}
if [ -z "$PAGE" ]; then
  echo "  ❌ /tempest returned nothing"; OK=0
else
  check 'id="back"'        'corner link  ← FREEHOLD  is in the served HTML'
  check 'ESC — EXIT'       'hint line advertises ESC — EXIT'
  check 'function leaveGame' 'Esc handler leaveGame() shipped'
  check 'function backHref'  'adaptive target backHref() shipped'
fi

sec "3. Where does the hatch send people? (both cases must be sane)"
# Anonymous player -> "/" (NOT /dashboard: that bounces to /login, a worse dead-end).
for path in / /tempest; do
  code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 12 "https://$SITE$path" 2>/dev/null || echo "ERR")
  if [ "$code" = "200" ]; then echo "  ✅ https://$SITE$path -> $code"; else echo "  ❌ https://$SITE$path -> $code"; OK=0; fi
done
# Signed-in player -> /dashboard. Anonymous hitting it should still redirect to /login.
dcode=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 12 "https://$SITE/dashboard" 2>/dev/null || echo "ERR")
case "$dcode" in
  30*|200) echo "  ✅ /dashboard -> $dcode (redirects anonymous to /login, as designed)" ;;
  *)       echo "  ❌ /dashboard -> $dcode — unexpected"; OK=0 ;;
esac

sec "4. Regression sweep — did anything else go dark?"
for u in "https://$SITE/" "https://$AUTH/" "https://$SITE/leaderboard"; do
  code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 12 "$u" 2>/dev/null || echo "ERR")
  case "$code" in
    2*|30*|40*) echo "  ✅ $u -> $code" ;;
    *)          echo "  ❌ $u -> $code"; OK=0 ;;
  esac
done
echo "  containers:"
docker compose ps --format '  {{.Name}}  |  {{.Status}}' 2>/dev/null || docker ps --format '  {{.Names}}  |  {{.Status}}'

sec "VERDICT"
if [ "$OK" = 1 ]; then
  echo "  ✅ 100% — machine-green. The escape hatch is serving and nothing regressed."
  echo
  echo "  NOW THE HUMAN-GREEN (this is the part that counts):"
  echo "    1. open  https://$SITE/tempest"
  echo "    2. bottom-left should read  ← FREEHOLD  (dim slate; goes amber on hover)"
  echo "    3. play a few seconds — it must NOT block the ship or eat your shots"
  echo "    4. click it -> you land on Freehold. Come back, press Esc -> same thing."
  echo "    NOTE: the signed-in path (-> /dashboard) CANNOT fire yet — freehold has no"
  echo "    /me endpoint, so the page can never learn who you are and always sends you"
  echo "    to /. The adaptive branch is correct but dormant until /me exists."
  echo "  Screenshot that and send it to Tig. Not done until you say it's right."
else
  echo "  ❌ NOT GREEN — something above is ❌. Do not walk away."
  echo "     Fastest rollback:  git log --oneline -3   then"
  echo "       git revert --no-edit <the escape-hatch commit> && make deploy ENV=production"
  echo "     Re-run this script after any fix."
fi
sec "DONE — screenshot & send to Tig."
