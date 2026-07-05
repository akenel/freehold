# 🐺 Freehold

### Own your stack. Owe no one.

A **production-grade app foundation** you clone, run in five minutes locally, and
deploy to your **own** server with real HTTPS, real login, and real social sign-in —
no platform landlord, no lock-in, no per-user rent. The real tools the top builders
use, wired up right, with the **why** in plain Lego language.

> A **freehold** is land you own free and clear — no lease, no ground rent, nobody
> can raise it or evict you. This repo is that, for your software: **your code, your
> data, your infrastructure — yours, portable, free.**

---

## What you get, out of the box

- 🔐 **Real login + roles + social sign-in** — Keycloak (OIDC) with RBAC. Username/
  password **plus Google & GitHub** login, across **three environments** (sandbox ·
  staging · production) served by **one shared Keycloak** (`kc-sbx`/`kc-stg`/`kc-prd`).
- 🗄️ **Postgres** — your data, on the DB that runs Fortune 500s.
- ⚡ **FastAPI (async Python)** + a **PWA front-end** — installs like an app, offline-ready, one codebase, any device.
- 🔒 **HTTPS everywhere** — Caddy's internal CA in dev (no mkcert), **free auto-renewing Let's Encrypt** in prod.
- 📧 **Email that's provider-agnostic** — forgot-password / verify-email over any SMTP (SMTP2GO free tier by default; Gmail, Resend, SES, Brevo — a 4-line swap).
- 🔑 **Secrets done right** — SOPS + `age`: encrypted **in git**, one key you hold (no Vault container, no unseal ceremony).
- 🚀 **A deploy pipeline that won't break prod** — stamp the build → **encrypted, restore-verified backup that gates production** → restart → prove the running SHA.
- 🎫 **Feedback + QA loop** · 🌗 **light/dark** · 🌍 **i18n (EN + हिन्दी)** · ℹ️ **an honest build/SHA status bar**.
- 🤖 **Optional pack:** a Raspberry-Pi robot control panel (sim-first) — a bolt-on demo, not core; delete `app/robot.py` + `app/routers/robot_panel.py` + `robot-sim/` to drop it.

Full requirements are in [`docs/FREEHOLD-SPEC.md`](docs/FREEHOLD-SPEC.md).

---

## ⚠️ First, the honest truth: you need a VPS for the real thing

Locally, Freehold runs on `https://localhost:8443` and everything works — *except*
the things the outside world has to reach:

- **Real HTTPS** (Let's Encrypt) needs a **public domain + a public IP on ports 80/443**.
- **Social login callbacks** (Google/GitHub) must redirect to a **real https URL**, not localhost-for-everyone.
- **Email** goes out from a server, not your laptop.

So: **local dev = learn + build. Production = a small VPS you own.** A **~$5/month
box** (Hetzner, a cheap VPS, or even a Raspberry Pi on your home network with a
port-forward) runs the whole thing. That's the "owe no one" price — versus ~$300/mo
for the trendy managed stack at real scale. **Budget one cheap VPS and a domain
(~$10/yr) and you're golden.**

---

## 🏃 Run it locally in 5 minutes

Prereqs: **Docker + Docker Compose**, `git`, `make`.

```bash
git clone https://github.com/akenel/freehold.git
cd freehold
make up          # copies .env.example -> .env, builds, starts everything
make trust       # trust Caddy's local CA once (green padlock; PWA/camera work)
```

Open **https://localhost:8443** and log in with a seeded sandbox user:

| user | pass | role |
|------|------|------|
| `demo` | `demo` | admin |
| `sam` | `sam` | staff |

That's the whole stack — app, Postgres, Keycloak, MinIO, Caddy, robot-sim — running
on your machine. Poke around: `/dashboard`, `/qa` (admin), `/pulse`, `/robot`,
`/profile`. Run the tests any time with `make test` (22, no infra needed).

---

## 🚀 Go to production (the full runbook)

This is exactly what a real deploy looks like. Say your domain is `example.com`.

### 1. DNS — point these A records at your box's public IP
```
example.com            A   <ip>     # apex → redirects to www
www.example.com        A   <ip>     # the app
auth.example.com       A   <ip>     # the shared Keycloak
sandbox.example.com    A   <ip>     # (optional, later)
staging.example.com    A   <ip>     # (optional, later)
```
Open **ports 80 and 443** to the box (port-forward if it's behind a router).

### 2. On the box — clone, configure, launch
```bash
git clone https://github.com/akenel/freehold.git && cd freehold
cp deploy/production.env.example .env
#   edit .env: replace EVERY change_me with a strong secret (openssl rand -base64 36),
#   and set SITE_DOMAIN=www.example.com  AUTH_DOMAIN=auth.example.com  APEX_DOMAIN=example.com
#   (the kc-prd realm's client secret must match KC_CLIENT_SECRET — see the gotchas)

CADDYFILE=./Caddyfile.prod \
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
Caddy fetches Let's Encrypt certs for `www.` and `auth.` on first request. Done —
green padlock, everywhere, for free.

### 3. Deploy through the pipeline (stamps the build + proves the backup)
```bash
COMPOSE_FILE=docker-compose.yml:docker-compose.prod.yml CADDYFILE=./Caddyfile.prod \
  python3 ops/deploy.py production
```
It stamps the SHA, runs the **encrypted restore-verified backup gate** (won't deploy
if a backup can't be proven), restarts, and confirms the *served* SHA matches.

### 4. Your first admin (the realm ships with NO users)
1. Register yourself at `https://www.example.com/register`.
2. Grant your account the `admin` realm role — via the Keycloak admin console at
   `https://auth.example.com/admin` (user `admin`, password = `KC_BOOTSTRAP_ADMIN_PASSWORD`
   in your `.env`), **Users → you → Role mapping → assign `admin`**.
3. **Log out and back in** so your token carries the new role.

More detail + the shared-auth topology: [`docs/GOING-LIVE.md`](docs/GOING-LIVE.md).

---

## 🔌 Turn on the optional packs

- **Social login (Google/GitHub/Facebook)** — [`docs/SOCIAL-LOGIN.md`](docs/SOCIAL-LOGIN.md).
  Register an OAuth app, add the redirect URIs, drop the creds in `.env`, `make apply`.
- **Email (forgot-password)** — [`docs/EMAIL.md`](docs/EMAIL.md). Any SMTP; SMTP2GO
  free by default, Gmail app-password works instantly. `make apply`.
- **Secrets (SOPS + age)** — [`docs/SECRETS.md`](docs/SECRETS.md). Encrypt `.env` into
  git, hold one key in your password manager. `make secrets ENV=production`.

---

## 🪤 The gotchas (tips we learned the hard way — read these)

**Local / Keycloak**
- **`make trust` once**, or the browser warns on `https://localhost:8443`.
- **Realms import only on a *fresh* Keycloak DB.** Editing a realm JSON needs a
  re-import — locally `make nuke && make up` (⚠️ wipes data). A plain `restart` does
  **not** re-import. For a *running* box, change realms live via the admin API instead.
- The PWA **service worker** must not cache `/realms/*` (auth) pages — it's already
  set to bypass them; if you add auth-ish routes, add them to the bypass list in `app/static/sw.js`.

**Deploy**
- **`deploy.py` uses the base compose by default.** For the prod overlay you *must*
  export `COMPOSE_FILE=docker-compose.yml:docker-compose.prod.yml CADDYFILE=./Caddyfile.prod`.
- **No inline `# comments` on `.env` value lines** (e.g. `APEX_DOMAIN=example.com   # note`) —
  Compose can keep the comment as part of the value and Caddy chokes. Put notes on their own line.
- The **kc-prd client secret** (in `keycloak/realms/kc-prd-realm.json`) must equal
  `KC_CLIENT_SECRET` in `.env`, or login fails. Set both, or stamp one into the other.
- `kc-prd` ships **hardened**: no seeded users, `sslRequired: external`. Create your admin (step 4 above).

**Social login**
- Redirect URI to register at the provider:
  `https://auth.<domain>/realms/<realm>/broker/<google|github|facebook>/endpoint`.
- **GitHub allows only ONE callback per app** — set it to just the host
  `https://auth.<domain>` (GitHub matches sub-paths) so one app covers every realm.
- **Google:** publish the OAuth **consent screen** or only test users can sign in.
- **Email collision:** if a social login's email matches an existing account, Keycloak
  asks to *link* it (needs password re-auth or a verification email). **Brand-new users
  are created silently** — the prompt only hits accounts that already exist.

**Email**
- Email is **optional** — only forgot-password + email-based account-linking use it.
  Social-login users never touch it. Skip it and the app is fully usable.
- The **From address must be a domain the provider has verified**, or mail bounces.
- **SMTP2GO** signup rejects free-mail — sign up with an address on your own domain
  (a free registrar email-forward like `admin@yourdomain` works). **Gmail SMTP** needs
  2-Step-Verification on + an **App Password**, and the From must be your gmail.

**Secrets**
- **Never commit `.env`** (it's gitignored). Real secrets live in `.env` on each box,
  or encrypted via SOPS. On a fresh box, install `sops`+`age` and restore your age key
  from your password manager before `make secrets`.

---

## 🧰 Make targets

```
make up        # build + start (local)         make test    # run the test suite
make trust     # trust Caddy's local CA         make logs    # tail logs
make down      # stop            make nuke      # stop + WIPE volumes (fresh realms)
make deploy ENV=sandbox          # single-env: rebuild the whole stack (+ backup gate)
make promote ENV=.. REF=..       # multi-env ladder: build one env's image from a git ref
make apply     # reconcile running Keycloak to .env (client secret, SMTP, social logins)
make backup    # encrypted, restore-verified, off-box (B2) backup
make secrets ENV=<env>           # decrypt SOPS secrets -> .env
```

## 📚 Docs
- [`FREEHOLD-SPEC.md`](docs/FREEHOLD-SPEC.md) — what it is and what it deliberately says *no* to
- [`GOING-LIVE.md`](docs/GOING-LIVE.md) — production, shared auth, the promotion ladder
- [`SOCIAL-LOGIN.md`](docs/SOCIAL-LOGIN.md) · [`EMAIL.md`](docs/EMAIL.md) · [`SECRETS.md`](docs/SECRETS.md)

---

## The philosophy

Enterprise-grade open-source tools, **right-sized.** You'll understand every layer,
because that is the entire point. Built by someone shipping real software since
**1983** — currency systems in 64K machines, process-control plants, a whole POS
platform — distilled to the best of it and handed to you.

Clone it, read it, run it, deploy it, go build something real. The tools are all
open — the **judgment to assemble them is the gift.**

> The top few percent build this way. Here it is, free.

🐺 The Wolf built the road. 🐯 The Tiger kept it honest. Now it's yours to walk free.
