# Freehold — the spec

*The requirements, drawn once so we build the right thing. Harvested from the battle-tested `helixnet` / Banco platform — best-of-the-best, stripped of app logic.*

## The one target that matters
> **Clone → `docker compose up -d` → logged in and looking at a dashboard, in 5 minutes.**

If a stranger can't get there in five minutes on a fresh machine, we've failed. Everything below serves that.

---

## 🟢 CORE — the kit itself (without these, it's not Freehold)
- **FastAPI** async skeleton — the app spine
- **Postgres** — the data
- **Keycloak (OIDC) + RBAC** — login, roles, and **3 realms = sandbox / staging / production** baked in from day one
- **One reverse proxy** — Caddy *or* Traefik (pick one; make the swap a one-liner)
- **Docker + Compose** — the whole thing runs with one command
- **The base screens** — login · logout · dashboard · account/settings · terms + privacy · a real 404 · the **status bar** (live build + SHA)
- **The deploy pipeline as scripts** — checkout → stamp SHA → restart → health-check · **encrypted + restore-verified backup that gates prod** · env-parity check. *Prove, don't assume — welded in.*
- **Feedback + QA loop built in** — feedback button → ticket → backlog → QA dashboard. Tickets are the knowledge base (capture the *why* on every close).
- **The docs** — a `CLAUDE.md`-style context file + a README that teaches the *why*, not just the *what*

## 🟡 OPTIONAL — bolt on when the app needs it (kit shows you how)
- **MinIO** object storage (wired to Postgres)
- **A queue (RabbitMQ)** — throttle AI / heavy calls so you never melt the box
- **BYO-brain LLM layer** — model-as-data, hosted default (Turbo) else local; the AI plug
- **i18n** — multi-language
- **The backup-brain chapter** — run your own model, Ollama Turbo, Aider; never single-point-of-failure

## 🔴 OVERKILL — teach them to *say no* until they truly need it
- **Kafka** (a queue is plenty) · **Kong / heavy gateway** (Caddy/Traefik covers it) · **Kubernetes** (Compose until you're huge — and you still build *this* first) · **full microservices** (modular monolith first; split when it hurts)

## ⚪ LATER — the grows-with-you stuff (rough in the seam now)
- **Multi-tenant** — ship the `tenant_id` seam now, build the full thing when tenant #2 is real
- **Telemetry / observability** — start with the status bar + logs; add real monitoring when there are users to monitor

---

## Build phases (start small, prove, expand)
1. **Skeleton up** — Compose + Postgres + Keycloak (3 realms) + FastAPI hello + Caddy. `up -d` → it runs.
2. **The door** — login/logout/RBAC working end-to-end; dashboard behind auth; the status bar.
3. **The rails** — the deploy scripts + the backup gate + env-parity, ported and proven.
4. **The loop** — feedback → backlog → QA dashboard.
5. **The base pages** — account, T&C, privacy, 404.
6. **The book** — the READMEs and the *why*, Lego-clear. This is what makes it a gift, not just a repo.
7. *(Then optional packs on demand.)*

Each phase: build it, verify it with your own eyes, commit. Same ritual as always.

---
*🐺 own your stack · owe no one*
