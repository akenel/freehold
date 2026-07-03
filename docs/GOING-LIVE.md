# Going live — free real HTTPS on your own domain

Dev runs on `https://localhost:8443` with Caddy's **internal CA** (self-signed —
trust it once with `make trust`). Production is the *same stack* on a real
domain, with a **real, free, auto-renewing HTTPS certificate**. No cert to buy,
no landlord. One overlay flips dev → prod.

## The free stack
| Piece | Who | Cost |
|-------|-----|------|
| Domain | **DuckDNS** — a free subdomain like `freeholder.duckdns.org` | $0 |
| Server | any small VPS (Hetzner, a Pi, an old laptop) | ~$0–5/mo |
| HTTPS | **Caddy** fetches a Let's Encrypt cert automatically | $0 |
| The app | Freehold | $0 (MIT) |

## Steps (turnkey)
On your **production server** (a clone of this repo):

1. **Free subdomain.** At <https://www.duckdns.org>, create `freeholder.duckdns.org`
   and point it at the server's public IP. Open ports **80** and **443**.
2. **Teach Keycloak your domain** (adds it to the realms; keeps localhost too):
   ```
   python3 ops/set-domain.py freeholder.duckdns.org
   ```
3. **Launch with the prod overlay:**
   ```
   SITE_DOMAIN=freeholder.duckdns.org CADDYFILE=./Caddyfile.prod \
     docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```
   Caddy fetches the Let's Encrypt cert on first request. Green padlock,
   everywhere, for everyone. Done.

## What the overlay changes (and nothing else)
`docker-compose.prod.yml` + `Caddyfile.prod` only touch the **front door**:
- the site is your domain (not `localhost`), and `tls internal` is gone → real
  Let's Encrypt HTTPS;
- Caddy binds **80 + 443**;
- `KC_HOSTNAME`, `APP_BASE_URL`, `KC_PUBLIC_URL` become `https://<domain>`.

Same Postgres, Keycloak, MinIO, app. **One stack, dev to prod.**

## Staging + production
Give each its own free subdomain (e.g. `freeholder-staging.duckdns.org` and
`freeholder.duckdns.org`), each `set-domain.py`'d and launched with its own
`SITE_DOMAIN`. Ship through the ladder with `ops/deploy.py staging` then
`ops/deploy.py production` (production runs the backup gate first).

> Own the domain, own the cert, own the box. Owe no one — not even a certificate
> authority.
