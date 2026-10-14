#!/usr/bin/env bash
# Apply a Caddyfile.prod change on wolfhold the only way that works: recreate Caddy.
#
#   bash ops/caddy-recreate.sh preflight    # read-only. GO / NO-GO, then stops.
#   bash ops/caddy-recreate.sh deploy       # git pull --ff-only, recreate caddy only
#   bash ops/caddy-recreate.sh postflight   # live file == repo file, every site as before
#   bash ops/caddy-recreate.sh rollback     # previous Caddyfile.prod back, recreate again
#
# Why not `caddy reload`: Caddyfile.prod is a single-FILE bind mount, pinned by inode.
# `git pull` writes a new inode, so reload re-reads the old file and reports success
# (memory/freehold-caddy-sop.md). Recreate costs every site on the box a few seconds.
#
# First used 2026-10-14 to retire ai.wolfhold.app (route -> 302 to www).
# EXPECT is the set of status codes the change should produce; edit it per change.
set -uo pipefail
cd /root/freehold 2>/dev/null || { echo "❌ /root/freehold missing"; exit 2; }

C=freehold-caddy-1
STATE=/root/.caddy-recreate-prev   # sha of Caddyfile.prod before deploy, for rollback
COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.prod.yml)
SITES=(https://www.wolfhold.app https://auth.wolfhold.app/realms/kc-prd
       https://staging.wolfhold.app https://sandbox.wolfhold.app
       https://wk.wolfhold.app https://iw.wolfhold.app https://docudiff.wolfhold.app
       https://www.wolfhold.app/tempest https://plants.wolfhold.app https://ai.wolfhold.app)
declare -A EXPECT=([https://plants.wolfhold.app]=302 [https://ai.wolfhold.app]=302)

FAIL=0
ok()   { echo "  ✅ $*"; }
bad()  { echo "  ❌ $*"; FAIL=1; }
info() { echo "  ·  $*"; }

on_box() {
  local ip; ip=$(ip route get 1.1.1.1 | awk '{print $7}')
  [ "$ip" = "167.233.125.248" ] || { echo "❌ not on wolfhold (ip $ip) — exit"; exit 2; }
}
code() { curl -s -o /dev/null -m 15 -w '%{http_code}' "$1"; }
live_sha() { docker exec "$C" sha256sum /etc/caddy/Caddyfile | cut -c1-16; }
file_sha() { sha256sum Caddyfile.prod | cut -c1-16; }

sites() {   # $1 = "now" (report only) or "expect" (judge against EXPECT, default 200)
  echo "── sites ──"
  for u in "${SITES[@]}"; do
    c=$(code "$u"); want=${EXPECT[$u]:-200}
    if [ "$1" = now ]; then info "$c  $u"
    elif [ "$c" = "$want" ]; then ok "$c  $u"
    else bad "$c  $u  (want $want)"; fi
  done
}

case "${1:-}" in
preflight)
  on_box
  echo "═══ PRE-FLIGHT · Caddy recreate · $(date -u +%FT%TZ) ═══"
  git fetch -q origin
  [ -z "$(git status --porcelain --untracked-files=no)" ] && ok "worktree clean (tracked files)" || bad "tracked files modified: $(git status --porcelain --untracked-files=no | tr '\n' ' ')"
  read -r ahead behind < <(git rev-list --left-right --count HEAD...origin/main)
  [ "$ahead" = 0 ] && ok "box has no local commits" || bad "box is $ahead commit(s) ahead of origin/main"
  info "box is $behind commit(s) behind origin/main — deploy pulls them (tracked files only)"
  git diff --stat HEAD origin/main | sed 's/^/     /'
  git show origin/main:Caddyfile.prod > /tmp/cand.caddy
  docker cp /tmp/cand.caddy "$C":/tmp/cand >/dev/null
  docker exec "$C" caddy validate --config /tmp/cand --adapter caddyfile >/dev/null 2>&1 \
    && ok "origin/main Caddyfile.prod validates in the running caddy" || bad "origin/main Caddyfile.prod does NOT validate"
  echo "── parsed config: live vs origin/main ──"
  docker exec "$C" caddy adapt --config /etc/caddy/Caddyfile --adapter caddyfile 2>/dev/null | python3 -m json.tool > /tmp/a.json
  docker exec "$C" caddy adapt --config /tmp/cand            --adapter caddyfile 2>/dev/null | python3 -m json.tool > /tmp/b.json
  diff /tmp/a.json /tmp/b.json | grep -v -E '/etc/caddy/Caddyfile|/tmp/cand|^---$|^[0-9,]+c[0-9,]+$' | sed 's/^/     /'
  docker exec "$C" rm -f /tmp/cand; rm -f /tmp/cand.caddy /tmp/a.json /tmp/b.json
  info "live caddy sha $(live_sha) · repo file sha $(file_sha)"
  "${COMPOSE[@]}" config -q 2>/dev/null && ok "compose file set parses" || bad "compose config fails"
  sites now
  echo
  [ $FAIL = 0 ] && echo "🟢 GO — say 'deploy'. Every site blips for a few seconds." || echo "🔴 NO-GO — fix the ❌ above first."
  ;;
deploy)
  on_box
  echo "═══ DEPLOY · pull + recreate caddy ═══"
  git rev-parse HEAD > "$STATE"
  git pull -q --ff-only origin main && ok "pulled → $(git log -1 --format='%h %s')" || { bad "pull failed — nothing recreated"; exit 1; }
  "${COMPOSE[@]}" up -d --no-deps --no-build --force-recreate caddy && ok "caddy recreated" || bad "recreate failed — run rollback"
  for i in $(seq 1 30); do [ "$(code https://www.wolfhold.app)" = 200 ] && break; sleep 2; done
  info "www answered after ~$((i*2))s"
  ;;
postflight)
  on_box
  echo "═══ POST-FLIGHT · Caddy recreate · $(date -u +%FT%TZ) ═══"
  st=$(docker inspect -f '{{.State.Status}} restarts={{.RestartCount}}' "$C")
  [[ $st == running* ]] && ok "caddy $st" || bad "caddy $st"
  [ "$(live_sha)" = "$(file_sha)" ] && ok "live config == repo file ($(live_sha)) — no stale inode" || bad "live $(live_sha) != file $(file_sha)"
  loc=$(curl -s -o /dev/null -m 15 -w '%{redirect_url}' https://ai.wolfhold.app)
  [ "$loc" = "https://www.wolfhold.app" ] && ok "ai.wolfhold.app → $loc" || bad "ai.wolfhold.app → '$loc'"
  sites expect
  errs=$(docker logs --since 5m "$C" 2>&1 | grep -c '"level":"error"')
  [ "$errs" = 0 ] && ok "no caddy errors in the last 5 min" || info "$errs caddy error lines in 5 min — read: docker logs --since 5m $C"
  echo
  [ $FAIL = 0 ] && echo "✅ 100%" || echo "❌ see above — rollback: bash $0 rollback"
  ;;
rollback)
  on_box
  [ -s "$STATE" ] || { echo "❌ no saved previous sha in $STATE"; exit 1; }
  prev=$(cat "$STATE")
  git checkout "$prev" -- Caddyfile.prod && echo "  restored Caddyfile.prod from $prev (worktree now differs from main)"
  "${COMPOSE[@]}" up -d --no-deps --no-build --force-recreate caddy && echo "  ✅ caddy recreated on the previous config"
  ;;
*) sed -n '2,9p' "$0"; exit 1 ;;
esac
exit $FAIL
