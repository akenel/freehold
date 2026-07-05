# 04 · Team & Freehold — how the juniors execute

*How a junior team ships the beachhead product (and then the bet) on top of Freehold,
and the real gaps between "starter kit" and "sellable DACH SaaS."*

---

## Why Freehold is the right launchpad (not a rebuild)

Freehold already ships the plumbing that normally eats a small team's first three
months — the difference between shipping in weeks and drowning in DevOps:

| Freehold gives us | So the juniors *don't* build | Where it lives |
|---|---|---|
| Login, roles, social sign-in | Auth, sessions, RBAC | Keycloak + `app/auth.py`, `app/deps.py` |
| Postgres + SQLAlchemy 2.0 | DB setup, migrations plumbing | `app/models.py`, `app/db.py`, Alembic |
| HTTPS dev *and* prod | TLS, certs | Caddy (`Caddyfile`, `Caddyfile.prod`) |
| Backup-gated deploy | "how do we not nuke prod" | `ops/deploy.py`, `ops/backup.py` |
| Encrypted secrets in git | Secret management | SOPS + age (`secrets/`, `.sops.yaml`) |
| Clean router pattern | App-architecture bikeshedding | `app/main.py` + `app/routers/*` |
| **i18n scaffolding (EN + हिन्दी today)** | The multilingual *mechanism* | `app/i18n.py` + Keycloak themes |

**What the team actually writes** for the QR-bill fixer / Handwerk life raft is
junior-shaped: new SQLAlchemy models (customer, invoice, job, capture), routers
following the existing `app/routers/` pattern, mobile-friendly templates, and
generation/validation endpoints (QR-bill, XRechnung/ZUGFeRD export, PDF). Well-scoped
CRUD with real stakes — the work that grows juniors without distributed-systems risk.

> The existing `Ticket` / `Profile` models in `app/models.py` are the *template* to
> copy, then delete. They show the pattern; they aren't the product.

---

## The three gaps between Freehold and a DACH SaaS

None is a reason to start over. All are known and scoped.

### 1. Multi-tenancy (the real infra work)
Freehold is **single-tenant** today. Selling to many firms means isolating each
customer's data. Cheapest-to-hardest:

| Approach | Good for | Trade-off |
|---|---|---|
| **One deploy per customer** | Phase 1–2 (a few design partners) | Manual; fine as a stopgap to ~10 |
| **Shared DB, `org_id` column** | Phase 2–3, the real answer | One missed filter leaks data → needs a review gate |
| **Schema/DB per tenant** | Later, if hard isolation demanded | More ops weight |

Stopgap with per-customer deploys, then shared-DB `org_id` in Phase 2 with a strict
"every query is org-scoped" rule. Keycloak groups map naturally to tenants.

### 2. Multilingual (DE / FR / IT) — now a first-class requirement, not a nice-to-have
The **Swiss market is DE/FR/IT**, and it's a **moat**: foreign incumbents handle the
3-language, 26-canton fragmentation badly. Freehold already has the i18n *mechanism*
(currently EN + Hindi) — we swap the locales for **de-CH / fr-CH / it-CH** (and de-DE
for the German market). Build **German-first**, structure every string for translation
from day one so FR/IT is a content task, not a rewrite.

### 3. Data residency — a selling point, if the buyer wants it
Swiss firms *may* prefer Swiss-hosted / on-prem for data-residency. Freehold's
self-hostable stack fits that — but ⚠️ whether non-technical trades actually *choose*
on that basis is **unverified** ([01](01-pain-landscape.md) Part D). Likely a
*back-office* advantage (cheap, ownable infra we control) more than a front-of-box
selling line. Validate in Phase 0; don't over-invest in it until a customer asks.

---

## How to run juniors on this (so it "just works")

1. **Tiny, well-specified tickets** — each maps to one model or one router. Dogfood the
   `Ticket` model's forced *resolution*-on-close as the team's own QA loop.
2. **The pipeline is the safety net** — Freehold's deploy **gates on a restore-verified
   backup**, so a junior can't ship something that eats prod data. Keep it.
3. **One senior review gate on two things only:** anything touching **auth** and
   anything touching **tenant isolation** (a junior mistake there is a data breach).
   Everywhere else, let juniors move.
4. **Definition of done = tested + deployed + demoable.** The 22-test suite and
   one-command deploy make that cheap to enforce.

---

## The honest infra caveat (say it before the boss finds it)

Freehold is **single-box** — one well-run VPS, no HA/failover. Correct and cheap for
Phase 0–2. It has a ceiling: before we're load-bearing SaaS for hundreds of German
firms, we re-architect for HA and managed Postgres. **A Phase 3+ problem — flag it now,
so it reads as prepared, not caught out.**

---

## Bottom line

- **Reuse Freehold. Don't rebuild.** The hard, boring infra is done.
- **The product is CRUD + capture + generation** in a domain we know — junior-shaped.
- **Three scoped gaps:** multi-tenancy (real work), DE/FR/IT i18n (a moat), data
  residency (a maybe). None argues for starting from scratch.

That's a solid footing to hit the ground running Monday — on paper first, code when
Phase 0 says go.

---
*Back to [README](README.md) · [00-brief](00-brief.md) · [01](01-pain-landscape.md) · [02](02-app-portfolio.md) · [03](03-roadmap.md) · [phase-0/](phase-0/README.md)*
