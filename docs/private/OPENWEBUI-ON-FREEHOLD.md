# Open WebUI on Freehold — "bring your own brain"

*The AI showcase. One Freehold login → your own ChatGPT at `ai.wolfhold.app`,
with the **brain hosted off-box** on **Ollama Turbo**. The box stays light — it
only relays API calls; no GPU, no local model. This is the manifesto made
touchable: own your stack + your login, rent only the brain, swap it anytime,
no OpenAI lock-in.*

Everything here is **opt-in** via `docker-compose.openwebui.yml` — it never
forces onto boxes that don't want it.

---

## Why this shape (the honest reasoning)

The wolfhold box is a Hetzner **CX22 (2 vCPU / 4 GB / no swap)** already running
Keycloak (JVM, ~650 MB) + Postgres + MinIO + three app envs. We measured ~1.9 GB
available. So we **do not run a model on the box** — Ollama Turbo runs it on
Ollama's GPUs and we call `https://ollama.com` over the API. Open WebUI itself,
with a remote brain, idles ~300–500 MB. A `mem_limit: 1536m` guard keeps it from
ever OOM-killing Keycloak, and we add **2 GB swap** as insurance.

## What you must do by hand (2 things)

1. **DNS:** add an `A` record `ai.wolfhold.app` → box IP (Porkbun, same as
   `wolfhold.app`). Caddy auto-issues the Let's Encrypt cert once it resolves.
2. **Ollama Turbo key:** create one at <https://ollama.com/settings/keys> and put
   it in the secret store (below). Turbo is a paid Ollama subscription; the key
   is a Bearer token. Cloud models incl. `gpt-oss:120b-cloud`, deepseek, qwen,
   glm, gemma — pick in the Open WebUI model dropdown after login.

## Secrets (SOPS → .env → Keycloak)

Add four keys to the encrypted prod secrets, with real values:

```bash
make secrets-edit ENV=production        # opens decrypted; re-encrypts on save
```

```
OPENWEBUI_DOMAIN=ai.wolfhold.app
OPENWEBUI_CLIENT_SECRET=<openssl rand -hex 32>   # OIDC client secret
OPENWEBUI_SECRET_KEY=<openssl rand -hex 32>      # Open WebUI session signing
OLLAMA_API_KEY=<from ollama.com/settings/keys>
```

`OPENWEBUI_CLIENT_SECRET` is stamped into the running Keycloak `open-webui`
client by `ops/prod-apply.py` (same path as `freehold-web`). The realm template
`keycloak/realms/kc-prd-realm.json` already carries the `open-webui` client with
a placeholder secret + redirect `https://ai.wolfhold.app/oauth/oidc/callback`.

## Deploy (on the box)

```bash
# 0) one-time: 2 GB swap (insurance on a no-swap 4 GB box)
fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab        # survive reboot

# 1) pull config + secrets
git pull
make secrets ENV=production                             # decrypt -> .env

# 2) bring up the stack WITH the Open WebUI overlay
CADDYFILE=./Caddyfile.prod \
  docker compose -f docker-compose.yml \
                 -f docker-compose.prod.yml \
                 -f docker-compose.openwebui.yml up -d

# 3) reconcile Keycloak (aligns the open-webui client secret to .env)
make apply
```

> If the box also runs the multi-env pack, add its `-f docker-compose.multienv.yml`
> to the same command — overlays compose in order.

## First login (who becomes admin)

Open WebUI makes the **first account** the admin. So **you log in first** at
`https://ai.wolfhold.app` → "Continue with Freehold" → you're the admin. After
that, other Freehold users self-provision on first login (`ENABLE_OAUTH_SIGNUP`)
and land as normal users; promote/limit them in the Open WebUI admin panel. The
local login form stays available as a break-glass fallback.

## Verify it works

- `https://ai.wolfhold.app` shows the login with a **"Continue with Freehold"** button.
- Logging in with a Keycloak user drops you straight into chat (no second signup).
- The model dropdown lists Ollama **cloud** models → send a message → you get a reply.
- `docker logs freehold-open-webui-1` shows no OIDC/`OLLAMA_API_CONFIGS` warnings.
- `free -m` on the box still shows healthy headroom (swap barely touched).

## Config we set & why (from the Open WebUI source)

| Env | Value | Why |
|---|---|---|
| `OLLAMA_BASE_URL` | `https://ollama.com` | Turbo/cloud host; native `/api/*` |
| `OLLAMA_API_CONFIGS` | `{"0":{"enable":true,"key":"…"}}` | index-keyed Bearer key for backend #0 |
| `ENABLE_OPENAI_API` | `false` | Ollama-only; no stray OpenAI calls |
| `OPENID_PROVIDER_URL` | `…/realms/kc-prd/.well-known/openid-configuration` | discovery, kc-prd realm |
| `OPENID_REDIRECT_URI` | `https://ai.wolfhold.app/oauth/oidc/callback` | must match the KC client exactly |
| `OAUTH_MERGE_ACCOUNTS_BY_EMAIL` | `true` | a Freehold user is the same person |
| `ENABLE_PERSISTENT_CONFIG` | `false` | env is authoritative every boot (no DB drift) |
| `mem_limit` | `1536m` | can't OOM-kill Keycloak |

## Gotchas / notes

- **Pin the image** for prod: set `OPENWEBUI_IMAGE` in `.env` to a dated release
  once you've confirmed the tag exists (default is `:main`).
- **RAG/doc upload** lazily pulls a small local embedding model the first time
  it's used (~a few hundred MB). Fine with swap; know it before demoing uploads.
- **Turbo cost:** every chat is a metered call to Ollama's cloud. It's a demo —
  watch the usage if you hand out lots of accounts.
- **Backups:** the `openwebui_data` volume holds users/chats/settings. If this
  becomes more than a throwaway demo, add it to the nightly backup set.

## To resume / redo cheaply

The whole thing is rebuildable: restore `.env`, run the `up` command with the
overlay, `make apply`. `ENABLE_PERSISTENT_CONFIG=false` means no hidden state —
the env is the config.
