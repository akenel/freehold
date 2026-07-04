# Going live — wolfhold.app, free real HTTPS, three environments

Dev runs on `https://localhost:8443` with Caddy's **internal CA** (self-signed —
trust it once with `make trust`). Production is the *same stack* on real domains,
with **real, free, auto-renewing HTTPS**. No cert to buy, no landlord.

## The shape

Three environments, one shared login:

| Host | Role | Realm |
|------|------|-------|
| `sandbox.wolfhold.app` | sandbox — where you test first | `kc-sbx` |
| `staging.wolfhold.app` | staging — retest before prod | `kc-stg` |
| `www.wolfhold.app` (apex → www) | production | `kc-prd` |
| `auth.wolfhold.app` | **one shared Keycloak**, holds all three realms | — |

Each app env picks its realm on the shared Keycloak; the browser always logs in
at `auth.wolfhold.app`, so the token issuer is stable and deterministic.

## DNS (Porkbun / any registrar)

Point every name at your box's public IP (A records). One box today; split to
separate IPs per env later by changing one record each:

```
wolfhold.app            A   <ip>     # apex → redirect to www
www.wolfhold.app        A   <ip>     # production
sandbox.wolfhold.app    A   <ip>
staging.wolfhold.app    A   <ip>
auth.wolfhold.app       A   <ip>     # the shared Keycloak
```

Open ports **80** and **443** to the box (port-forward if it's behind a router —
Caddy's ports are configurable via `CADDY_HTTP_PORT`/`CADDY_HTTPS_PORT`).

## Launch a box

On the server (a clone of this repo):

```
cp deploy/sandbox.env.example .env     # or staging / production
# fill in every change_me secret, then:
CADDYFILE=./Caddyfile.prod \
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Caddy fetches the Let's Encrypt certs on first request — for both the app host
and `auth.wolfhold.app`. Green padlock, everywhere, for everyone. Done.

## The promotion ladder

Changes walk **local → sandbox → staging → production**, the same git ref each
step, and production won't move unless the restore-verified backup passes:

```
# local: make it, prove it, commit, push
git commit -am "..."  &&  git push

# sandbox box — deploy the ref, test at sandbox.wolfhold.app
git pull  &&  python3 ops/deploy.py sandbox

# good? staging box — same ref, retest at staging.wolfhold.app
git pull  &&  python3 ops/deploy.py staging

# good? prod box — the backup GATE runs first, then deploy + prove the SHA
git pull  &&  python3 ops/deploy.py production
```

`deploy.py` stamps the build, rebuilds, health-checks, and re-probes `/version`
to prove the SHA now serving is the one you shipped. Promotion is never a leap of
faith.

## One box now, three boxes later

Today all five names point at one IP — one box runs the shared Keycloak *and* the
app. To split an env onto its own box: give it its own IP (change its A record),
clone the repo there, and on the app boxes that no longer run Keycloak set
`KC_INTERNAL_URL=https://auth.wolfhold.app` and drop the `{$AUTH_DOMAIN}` block
from that box's Caddyfile. The shared Keycloak lives on exactly one box.

> Own the domain, own the cert, own the box. Owe no one — not even a certificate
> authority.
