---
name: freehold-caddy-sop
description: Freehold prod deploy gotchas (Caddy env vars, ports, route-not-subdomain) — recall before touching the wolfhold box
type: reference
---

Operational SOP for the wolfhold box (167.233.125.248), learned the hard way 2026-07-09.

**Caddy MUST start with the prod overlay.** Run Caddy with
`COMPOSE_FILE=docker-compose.yml:docker-compose.prod.yml CADDYFILE=./Caddyfile.prod`.
The prod overlay (`docker-compose.prod.yml`) is what passes `SITE_DOMAIN` + `AUTH_DOMAIN` to
Caddy AND binds public `0.0.0.0:80/443`. **Base compose alone omits them** → `{$SITE_DOMAIN}`
is empty → Caddy reads the collapsed line as a global-options block → crashes at
`Caddyfile.prod:16` ("unrecognized global option: header"). `.env` on the box already has
`SITE_DOMAIN=www.wolfhold.app`, `AUTH_DOMAIN=auth.wolfhold.app`.

**Deploy is `python3 ops/promote.py production HEAD`** (or `make promote ENV=production`).
⚠️ **Corrected 2026-08-14 — it is NOT `make deploy ENV=production`.** `deploy.py` *refuses* on this
box and says so: the box runs the multi-env stack (`freehold-app-sandbox-1`,
`freehold-app-staging-1`), and `deploy.py` would restart it from `docker-compose.yml` alone — dev
Caddyfile, dev `KC_HOSTNAME`, every image rebuilt from the working tree. The refusal is a guard, not
a bug; do not work around it.

`promote.py` is the right tool: it builds `freehold-app:<tag>` from a **git ref** via `git archive`
(never the working tree), runs the backup gate and the full test suite *inside* the new image, then
recreates **only that env's** container and confirms the served SHA. So sandbox can run newer code
than prod, and one ref walks the ladder: `promote.py sandbox` → `staging <sha>` → `production <sha>`.
Verified 2026-08-14 shipping the Tempest escape hatch: `b120 · 0fce1f7`, 156 tests passed.

The health wait can still time out while DB migrations run on boot — that "error" is often not
fatal; verify the served build after. `_common.compose()` runs bare `docker compose`, so the prod
file set must come from the environment/`.env` (COMPOSE_FILE), not `-f` flags.

**Know which machine you are on.** The box holds a public IP on its interface; a laptop holds a
private LAN one. `ip route get 1.1.1.1 | awk '{print $7}'` → `167.233.125.248` means the box,
`192.168.…` means you are about to deploy nothing from the wrong machine. The
`ops/tempest-escape-*flight.sh` scripts guard on exactly this and exit 2 off-box.

**Tempest lives as a ROUTE, not a subdomain.** `/tempest` = `freehold/app/static/tempest.html` +
`freehold/app/routers/tempest.py` + a nav link in `_topbar.html`/`_footer.html`. No separate app,
container, or DNS. Prefer this pattern for adding features. See [[deploy-ritual]].

**Diagnosis lessons:** connection-refused from outside ≠ IP ban — check if the service is even
listening first (`docker ps`, `ss -tlnp | grep :443`). Reproduce config errors LOCALLY (same
`caddy:2-alpine` image) before touching prod — that's how the root cause was proven, not guessed.
There is NO fail2ban on the box.
