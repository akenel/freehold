# 04 · Team & Freehold — how the juniors execute

*How a junior team ships `CIS Companion` on top of Freehold, and the one real
infrastructure gap between "starter kit" and "sellable SaaS."*

---

## Why Freehold is the right launchpad (not a rebuild)

Freehold already ships the plumbing that normally eats a small team's first three
months. For a junior team this is the difference between shipping in weeks and
drowning in DevOps:

| Freehold gives us | So the juniors *don't* build | Where it lives |
|---|---|---|
| Login, roles, social sign-in | Auth, sessions, RBAC | Keycloak + `app/auth.py`, `app/deps.py` |
| Postgres + SQLAlchemy 2.0 models | DB setup, migrations plumbing | `app/models.py`, `app/db.py`, Alembic |
| HTTPS in dev *and* prod | TLS, certs, mkcert pain | Caddy (`Caddyfile`, `Caddyfile.prod`) |
| Backup-gated deploy pipeline | "how do we not nuke prod" | `ops/deploy.py`, `ops/backup.py` |
| Encrypted secrets in git | Secret management | SOPS + age (`secrets/`, `.sops.yaml`) |
| A clean router pattern | App architecture bikeshedding | `app/main.py` + `app/routers/*` |

**What the team actually writes for `CIS Companion`** is squarely junior-appropriate:
new SQLAlchemy models (subcontractor, verification, monitoring entry), a handful of
routers following the existing `app/routers/` pattern, Jinja templates matching the
existing ones, and export endpoints (PDF/CSV). That's well-scoped CRUD with real
stakes — exactly what grows juniors without exposing them to distributed-systems risk.

> The existing `Ticket` / `Profile` models in `app/models.py` are the *template* to
> copy, then delete. They show the pattern; they aren't the product.

---

## The one real gap: multi-tenancy

Freehold today is **single-tenant** — one deployment, one organisation. Selling to
many construction firms means each customer's data must be isolated. This is the only
infrastructure work that isn't already done, and it's a known, scoped piece — **not**
a reason to start from scratch.

Three options, cheapest-to-hardest:

| Approach | How | Good for | Trade-off |
|---|---|---|---|
| **One deploy per customer** | Spin a Freehold stack per firm | Phase 1–2 (a handful of design partners) | Manual, doesn't scale past ~10 — fine as a *stopgap* |
| **Shared DB, `org_id` column** | Every row carries an org; scope every query | Phase 2–3, the real answer | Requires discipline — one missed filter leaks data. Needs a review checklist. |
| **Schema/DB per tenant** | Postgres schema per org | Later, if compliance demands hard isolation | More ops weight |

**Recommendation:** stopgap with per-customer deploys for the first few design
partners (Phase 1), then implement **shared-DB `org_id` tenancy** in Phase 2 — with a
strict "every query is org-scoped" rule and a senior review gate, because that's the
one place a junior mistake becomes a data breach. Keycloak already models
organisations/groups, so tenant → realm-group mapping is a natural fit.

---

## How to run juniors on this (so it "just works" for the boss)

The boss wants *business-grade software that just works*. With a junior team that
comes from **process**, not heroics:

1. **Tiny, well-specified tickets.** Each maps to one model or one router. The
   Freehold `Ticket` model literally demands a *resolution* on close — use it as the
   team's own QA loop (dogfood the tool).
2. **The pipeline is the safety net.** Freehold's deploy **gates on a restore-verified
   backup** — a junior can't ship something that eats prod data. This is a feature,
   not overhead. Keep it.
3. **One senior review gate on two things only:** anything touching **auth** and
   anything touching **tenant isolation**. Everywhere else, let juniors move.
4. **Definition of done = tested + deployed + demoable.** Freehold's 22-test suite
   and one-command deploy make this cheap to enforce.

---

## The honest infra caveat (say it before the boss finds it)

Freehold is **single-box** — one well-run VPS, no high-availability/failover. That is
**correct and cost-efficient for Phase 0–2** (design partners, first revenue). It has
a ceiling: before we're a load-bearing SaaS for hundreds of firms, we'll re-architect
for HA and managed Postgres. **Know the ceiling; don't pretend it isn't there.** It's
a Phase 3+ problem, not a Day-1 one — but naming it now is the difference between
looking prepared and looking caught out.

---

## Bottom line

- **Reuse Freehold. Don't rebuild.** The infra that's hard and boring is done.
- **The product is CRUD + evidence + exports** in a domain we know — junior-shaped work.
- **One real gap (multi-tenancy)**, with a clear stopgap and a clear real answer.
- **One real ceiling (single-box)**, which is a Phase 3 concern, flagged honestly.

That's a solid footing to hit the ground running Monday — on paper first, code when
Phase 0 says go.

---
*Back to [README](README.md) · [00-brief](00-brief.md) · [01-pain-landscape](01-pain-landscape.md) · [02-app-portfolio](02-app-portfolio.md) · [03-roadmap](03-roadmap.md)*
