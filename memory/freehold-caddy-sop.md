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

**Deploy is `make deploy ENV=production`** (`ops/deploy.py` — stamps build, backup-gate, rebuild,
health-check). Its 60s health wait can time out while DB migrations run on boot — that "error" is
often not fatal; verify the served build after. `_common.compose()` runs bare `docker compose`, so
the prod file set must come from the environment/`.env` (COMPOSE_FILE), not `-f` flags.

**Tempest lives as a ROUTE, not a subdomain.** `/tempest` = `freehold/app/static/tempest.html` +
`freehold/app/routers/tempest.py` + a nav link in `_topbar.html`/`_footer.html`. No separate app,
container, or DNS. Prefer this pattern for adding features. See [[deploy-ritual]].

**Diagnosis lessons:** connection-refused from outside ≠ IP ban — check if the service is even
listening first (`docker ps`, `ss -tlnp | grep :443`). Reproduce config errors LOCALLY (same
`caddy:2-alpine` image) before touching prod — that's how the root cause was proven, not guessed.
There is NO fail2ban on the box.
