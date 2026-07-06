# Nextcloud on Freehold — what we could do

*Handoff note (written 2026-07-06 from the helixnet session). Not started. Read this first when you pick it up in the freehold repo.*

## The idea

Add **Nextcloud** (self-hosted Drive/Office/Calendar/Talk) to the Freehold box as a
companion service, **single-sign-on'd to the Keycloak we already run**. One login →
your Freehold app AND your own cloud office. That IS the manifesto — "own your stack,
owe no one" — made touchable. It's the reference example that shows a Freeholder they
can dump Google Drive / Microsoft 365 without owing a monthly ransom.

Target URL: **`cloud.wolfhold.app`** (own subdomain, behind the existing Caddy).

## Why it fits Freehold (not a detour)

- Same thesis: EU-hosted, no per-seat SaaS, data on your box, GDPR-friendly by default.
- Reuses what's already up: **Postgres** (own DB), **Caddy** (reverse proxy + Let's Encrypt), **Keycloak** (OIDC login).
- Teachable: "here's how you SSO a real 3rd-party app to your own identity server" is a
  great lesson — it proves Keycloak is doing real work, not just gating our own app.

## Two things the official Hub page confirms (2026-07-06)

- **SSO is a headline, first-class feature** ("LDAP/AD, built-in account management, 2FA and
  SSO"). So Phase 3 (Keycloak OIDC) is a supported path, not a hack — **de-risks the payoff step.**
- **Nextcloud Assistant = a *local* AI built in** ("runs with any model and data location you
  need"). That's the **BYO-brain thesis** in someone else's product — point it at your Ollama
  Turbo / local model and it's on-Freehold-message out of the box. Nice bonus, not core.
- **Nextcloud Flow** (Windmill-based automation) + **Tables** (no-code data) exist too —
  parking-lot ideas, not for the first pass.

## Reality check FIRST (the seal-inspection view)

**The box is the constraint.** wolfhold = Hetzner **CX22 (2 vCPU / 4 GB RAM / ~40 GB disk)**,
already running Postgres + Keycloak + FastAPI + Caddy. Nextcloud is **heavy** (PHP-FPM +
its own DB + Redis; Collabora/OnlyOffice office-editing is a whole extra JVM/container).

Honest options, pick one before building:
1. **Lean Nextcloud** — Files + Calendar + Contacts only, **skip Collabora office** (the RAM hog). Probably fits a CX22 *snugly*; watch swap.
2. **Resize the box** — bump to **CX32 (4 vCPU / 8 GB)** or **CX42 (8 vCPU / 16 GB)** if you want Office + Talk. ~1-click Hetzner resize, few min downtime.
3. **Dedicated Nextcloud box** — cleanest separation (Nextcloud's update cadence won't touch Freehold), but it's a 3rd server + cost. Given you said "2 servers now," probably NOT this yet.

**Recommendation:** start with **Option 1 (lean, no office)** on the current box to prove
the SSO + reverse-proxy wiring cheaply; add Collabora + a resize later only if it earns it.

Also honest: Nextcloud is **not fire-and-forget** — updates, app-compat, occasional
"upgrade broke sync" days. It adds a maintenance surface. Worth it for the demo value,
but know it going in.

## First-session plan (phased, cheap-first)

**Phase 0 — decide (5 min):** pick the resource option above. Confirm DNS for
`cloud.wolfhold.app` → box IP (A record at Porkbun, like wolfhold.app).

**Phase 1 — stand it up (compose):**
- Add a `nextcloud` service (official `nextcloud:apache` or `nextcloud:fpm` image) + a
  `redis` service to `docker-compose.prod.yml`.
- Create a **`nextcloud` database + user** in the existing Postgres (don't reuse app DB).
- Point Nextcloud at Postgres + Redis via env (`POSTGRES_HOST`, `REDIS_HOST`).
- Persist `/var/www/html` (Nextcloud data + config) to a named volume — **this is what the
  backup cron must include** (see Phase 4).

**Phase 2 — Caddy reverse proxy:**
- Add a `cloud.wolfhold.app` site block → `reverse_proxy nextcloud`.
- Nextcloud needs the **`.well-known/carddav|caldav` redirects** and
  `X-Forwarded-*` / `trusted_proxies` set (Caddy handles headers; set Nextcloud
  `trusted_proxies` to the Caddy container IP + `overwriteprotocol=https`).
- Let's Encrypt cert issues automatically like the main site.

**Phase 3 — Keycloak SSO (the payoff):**
- In Keycloak: create a **`nextcloud` OIDC client** (confidential, redirect
  `https://cloud.wolfhold.app/apps/user_oidc/*`). Decide which realm (likely the same
  one Freehold users live in so it's one identity).
- In Nextcloud: install the **`user_oidc`** app, add the provider (discovery URL =
  `https://wolfhold.app/realms/<realm>/.well-known/openid-configuration`).
- Test: log into Nextcloud with a Freehold Keycloak user. Keep admin/local-login as a
  break-glass fallback.

**Phase 4 — make it durable (Freehold rails):**
- Extend the **nightly encrypted restore-verified backup** to include the Nextcloud
  Postgres DB **and** the data volume (config + files). Same discipline as the app backup.
- Add a health check / pulse entry so a broken Nextcloud shows up.

**Phase 5 (optional, later):** Collabora/OnlyOffice for in-browser Office; Nextcloud Talk
(needs a TURN server — coturn — for calls to work through NAT). Only if there's demand.

## Decisions to make before we build
1. Resource option (1/2/3 above) — I recommend **1 (lean)**.
2. Which Keycloak realm owns cloud identities (reuse Freehold's, or a dedicated one).
3. Scope: Files+Calendar only, or go for Office too (drives the resource decision).
4. Is this a **personal** cloud for you, a **showcase** in the Freehold teaching site, or a
   **template** Freeholders deploy? (Changes how much we document + parameterize it.)

## Open questions / risks
- CX22 RAM headroom with Nextcloud PHP-FPM + Redis alongside Keycloak (JVM) — measure early; be ready to resize.
- Nextcloud upgrades vs the app's deploy cadence — separate compose profile so one doesn't force the other.
- Backup size grows with real files — watch disk + the offsite copy budget.

## To resume
Open a fresh session in this repo and say: *"read docs/private/NEXTCLOUD-ON-FREEHOLD.md,
we're doing Phase 0-1."* Everything Freehold-side (Caddy, Keycloak, backup cron, deploy
key `~/.ssh/wolfhold_ed25519`, box `/root/freehold`) already exists to build on.
