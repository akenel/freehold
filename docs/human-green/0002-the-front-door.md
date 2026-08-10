# 0002 — The front door

- **Date:** 2026-08-09
- **Where:** `ops/deploy.py`, `ops/_common.py`, `ops/caddy-preflight.sh`
- **Commit:** `4b6b7e4`
- **Cost:** prod outage — app, auth and AI all dark behind one container; real
  minutes lost to a misleading diagnostic during recovery

## What the machine reported

`deploy.py` ran its deploy and then probed a public URL for health. The app it
was deploying was never unhealthy. Separately, `caddy-preflight.sh` validated the
Caddyfile and reported a failure whose message named the wrong cause entirely:
`module not registered: dns.providers.porkbun`.

## What was actually true

`deploy.py` shells out to a bare `docker compose up -d --build` with no `-f`
flags. On the shared multi-env box that silently drops the prod overlay, so Caddy
was recreated from the base compose file on **stock** `caddy:2-alpine` — while
still mounting `Caddyfile.prod`, which uses `acme_dns porkbun`. Stock Caddy has
no Porkbun DNS module. Crash loop. Everything behind Caddy went with it.

The preflight script was validating against stock Caddy too, not against the
built `freehold-caddy:prd` image. So it *always* emitted the missing-module
error, in health and in sickness alike. During the outage that read as the root
cause, and it cost real minutes.

The app health probe was green-adjacent for the worst possible reason: it was
asking a public URL a question that no longer had a front door to reach it.

## How the gap surfaced

Production stopped, again.

## The shape

**A check that fails identically in the healthy and unhealthy case carries no
information — and during an incident it actively misleads, because everyone
reads it as the finding.** A check must be run against the artifact that will
actually run, not a stand-in that resembles it.

Second shape: this is [0001](0001-the-empty-domain.md) wearing different clothes
— base compose, no prod overlay. The first instance was fixed and not recorded,
so nobody recognised the second one on sight.

## What changed

- `deploy.py` refuses to run at all when the multi-env containers exist, before
  the build stamp and before the backup gate, and points at `ops/promote.py`.
  Its docstring now says single-stack boxes only.
- `caddy-preflight.sh` validates against `freehold-caddy:prd`, and checks the
  **running container's image** — the decisive tell, and it had been missing.
- The script header records both incidents as one mistake. That header is the
  detector this file argues for: the next person to read it sees the pattern
  before they repeat it.
