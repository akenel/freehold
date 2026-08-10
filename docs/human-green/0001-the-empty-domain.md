# 0001 — The empty domain

- **Date:** 2026-07-06 (referred to in a later commit as the 07-09 incident)
- **Where:** `Caddyfile`, `docker-compose.yml`
- **Commit:** `62f40d2`
- **Cost:** prod down during the Open WebUI rollout

## What the machine reported

Nothing wrong. The Caddyfile had defaults written into it — `{$APEX_DOMAIN:...}`
— which is exactly the mechanism you use so an unset variable stays harmless.
Compose was configured. The rollout proceeded.

Then Caddy crash-looped on `server block without any key must be first`, and
because everything sits behind Caddy, everything went dark at once.

## What was actually true

Compose was passing the variables through as `${VAR:-}` — that is, *set, to the
empty string*. A Caddyfile default only fires when a variable is **unset**. Set-
but-empty sailed straight past it and became an empty server-block key, which is
a parse error, which is a config that will not load at all.

Two layers each doing something reasonable. Compose said "if unset, empty."
Caddy said "if unset, use my default." Between them, unset became empty and the
default never ran.

## How the gap surfaced

Production stopped. There was no earlier signal, because there was nothing for a
test to be red about — the config was syntactically fine in every state except
the one that actually occurred.

## The shape

**Unset and empty are not the same value, and a default that only covers one of
them covers neither in practice.** Anywhere a value crosses a boundary — compose
to container, env to config, form to API — ask which of the two you are actually
producing on the far side.

## What changed

The domains are defaulted to the same inert loopback addresses *in compose*, so
unset resolves to inert rather than empty. Both layers now agree on what absence
means.

No detector was added. Five weeks later the same shape — base compose, no prod
overlay — took prod down again. See [0002](0002-the-front-door.md).
