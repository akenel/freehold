# Going live — free real HTTPS on your own domain

Dev runs on `https://localhost:8443` with Caddy's **internal CA** (self-signed —
you trust it once with `make trust`). Production is the same stack, on a real
domain, with a **real, free, auto-renewing HTTPS certificate**. No cert to buy,
no landlord.

## The free stack
| Piece | Who | Cost |
|-------|-----|------|
| Domain | **DuckDNS** — a free subdomain like `you.duckdns.org` | $0 |
| Server | any small VPS (Hetzner, a Pi, an old laptop) | ~$0–5/mo |
| HTTPS | **Caddy** fetches a Let's Encrypt cert automatically | $0 |
| The app | Freehold | $0 (MIT) |

## Steps
1. **Get a free subdomain.** Sign up at <https://www.duckdns.org>, create
   `you.duckdns.org`, and point it at your server's public IP (DuckDNS gives you
   a token + a one-line updater if your IP is dynamic).
2. **Open ports 80 + 443** on the server (Let's Encrypt validates over 80/443).
3. **Swap `localhost` for your domain** in four places:
   - `Caddyfile` — change the site line `localhost` → `you.duckdns.org`, and
     **delete `tls internal`** (Caddy then uses Let's Encrypt automatically).
   - `.env` — `APP_BASE_URL` and `KC_PUBLIC_URL` → `https://you.duckdns.org`.
   - `docker-compose.yml` — `KC_HOSTNAME` → `https://you.duckdns.org`, and map
     Caddy to the real ports (`80:80` and `443:443`).
   - `keycloak/realms/*.json` — redirect / web-origin / post-logout URIs →
     `https://you.duckdns.org/*`.
4. **`docker compose up -d`.** Caddy gets the cert on first request. Green
   padlock, everywhere, for everyone. Done.

## Staging + production
Give each its own free subdomain — e.g. `you-staging.duckdns.org` and
`you.duckdns.org` — each its own box (or the same box, different ports), each its
own realm (`freehold-staging`, `freehold-production`). Ship through the ladder
with `ops/deploy.py staging` then `ops/deploy.py production` (production runs the
backup gate first).

> Own the domain, own the cert, own the box. Owe no one — not even a certificate
> authority.
