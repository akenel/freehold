#!/usr/bin/env bash
# Turn Open WebUI (ai.wolfhold.app) OFF to give the 4 GB box its memory back.
#
#   bash openwebui-off.sh preflight    # read-only. GO / NO-GO, then stops.
#   bash openwebui-off.sh deploy       # docker stop — container kept, volume kept
#   bash openwebui-off.sh postflight   # memory after, every other site still 200
#   bash openwebui-off.sh rollback     # docker start — back as it was
#
# Why (measured 2026-10-14): open-webui held 549M RAM + 1443M swap = ~2 GB of a
# 3.7 GB box with 2 GB swap; nobody needs it. `docker stop` on an
# `unless-stopped` container stays stopped across reboots. Data volume
# freehold_openwebui_data is NOT touched. ai.wolfhold.app will answer 502.
set -uo pipefail

C=freehold-open-webui-1
VOL=freehold_openwebui_data
FAIL=0
ok()   { echo "  ✅ $*"; }
bad()  { echo "  ❌ $*"; FAIL=1; }
info() { echo "  ·  $*"; }

on_box() {
  local ip; ip=$(ip route get 1.1.1.1 | awk '{print $7}')
  [ "$ip" = "167.233.125.248" ] || { echo "❌ not on wolfhold (ip $ip) — exit"; exit 2; }
}

memory() {
  echo "── memory ──"
  free -m | sed 's/^/  /'
  echo "  pressure: $(head -1 /proc/pressure/memory)"
  echo "── per container (RAM + swap) ──"
  for id in $(docker ps -q); do
    n=$(docker inspect -f '{{.Name}}' "$id" | tr -d /)
    cg=/sys/fs/cgroup/system.slice/docker-$(docker inspect -f '{{.Id}}' "$id").scope
    m=$(cat "$cg/memory.current" 2>/dev/null || echo 0)
    s=$(cat "$cg/memory.swap.current" 2>/dev/null || echo 0)
    printf "  %-24s ram=%5dM swap=%5dM total=%5dM\n" "$n" $((m/1048576)) $((s/1048576)) $(((m+s)/1048576))
  done | sort -t= -k4 -n -r
}

code() { curl -s -o /dev/null -m 15 -w '%{http_code}' "$1"; }

sites() {
  echo "── sites ──"
  for u in https://www.wolfhold.app https://auth.wolfhold.app/realms/kc-prd \
           https://staging.wolfhold.app https://sandbox.wolfhold.app \
           https://wk.wolfhold.app https://iw.wolfhold.app; do
    c=$(code "$u")
    case $c in 2??|3??) ok "$c  $u" ;; *) bad "$c  $u" ;; esac
  done
}

case "${1:-}" in
preflight)
  on_box
  echo "═══ PRE-FLIGHT · Open WebUI off · $(date -u +%FT%TZ) ═══"
  st=$(docker inspect -f '{{.State.Status}}' "$C" 2>/dev/null || echo missing)
  [ "$st" = running ] && ok "$C is running (will stop it)" || bad "$C is '$st' — nothing to stop"
  docker volume inspect "$VOL" >/dev/null 2>&1 && ok "volume $VOL exists (will be kept)" || bad "volume $VOL missing"
  deps=$(docker ps -q | xargs docker inspect -f '{{.Name}} {{index .Config.Labels "com.docker.compose.depends_on"}}' | grep -i 'open-webui' | grep -v "^/$C " || true)
  [ -z "$deps" ] && ok "no container depends on open-webui" || bad "dependents: $deps"
  docker inspect -f '{{.State.Status}}' freehold-caddy-1 | grep -q running && ok "caddy running" || bad "caddy not running"
  info "ai.wolfhold.app now: $(code https://ai.wolfhold.app) (expect 502 after)"
  sites
  memory
  echo
  [ $FAIL = 0 ] && echo "🟢 GO — say 'deploy'." || echo "🔴 NO-GO — fix the ❌ above first."
  ;;
deploy)
  on_box
  echo "═══ DEPLOY · stopping $C ═══"
  docker stop "$C" && ok "stopped" || bad "docker stop failed"
  ;;
postflight)
  on_box
  echo "═══ POST-FLIGHT · Open WebUI off · $(date -u +%FT%TZ) ═══"
  st=$(docker inspect -f '{{.State.Status}} restarts={{.RestartCount}}' "$C" 2>/dev/null)
  [[ $st == exited* ]] && ok "$C $st" || bad "$C is '$st' — expected exited"
  docker volume inspect "$VOL" >/dev/null 2>&1 && ok "volume $VOL kept" || bad "volume $VOL GONE"
  c=$(code https://ai.wolfhold.app); [ "$c" = 502 ] && ok "ai.wolfhold.app → 502 (expected)" || info "ai.wolfhold.app → $c"
  docker inspect -f '{{.State.Status}}' freehold-caddy-1 | grep -q running && ok "caddy still running" || bad "caddy down"
  sites
  memory
  echo
  [ $FAIL = 0 ] && echo "✅ 100%" || echo "❌ see above — rollback: bash $0 rollback"
  ;;
rollback)
  on_box
  docker start "$C" && echo "✅ $C started — give it ~60s, then check https://ai.wolfhold.app"
  ;;
*) sed -n '2,8p' "$0"; exit 1 ;;
esac
exit $FAIL
