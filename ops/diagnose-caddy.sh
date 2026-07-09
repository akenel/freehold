#!/usr/bin/env bash
# PRE-FLIGHT (look-only) — why is Caddy rejecting Caddyfile.prod at line 16?
# Changes NOTHING. Just shows the exact file, any local edits, the full parse
# error, and the Caddy version. Run on the box:  bash ops/diagnose-caddy.sh
set -uo pipefail
cd "$(dirname "$0")/.."                       # -> freehold repo root
sec(){ printf '\n\033[1;36m===== %s =====\033[0m\n' "$*"; }

sec "A. Caddyfile.prod — lines 1-30 WITH line numbers (what's really at line 16?)"
cat -n Caddyfile.prod | head -30

sec "B. Was Caddyfile.prod changed vs the committed (last-working) version?"
git status --short Caddyfile.prod || true
echo "--- diff vs committed (blank = identical to git) ---"
git --no-pager diff -- Caddyfile.prod | head -60 || true

sec "C. Full Caddy parse error, run against THIS exact file (throwaway container)"
docker run --rm -v "$PWD/Caddyfile.prod:/etc/caddy/Caddyfile:ro" caddy:2-alpine \
  caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile 2>&1 | head -25

sec "D. Caddy image + version (a version bump can change parsing)"
docker inspect freehold-caddy-1 --format 'running image: {{.Config.Image}}' 2>/dev/null || true
docker run --rm caddy:2-alpine caddy version 2>&1 | head -1

sec "DONE — screenshot everything above and send it to Tig. (Nothing was changed.)"
