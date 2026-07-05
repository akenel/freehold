# 00 · The Brief

*The situation, the mission, and the honest risk — so nobody can say we walked in blind.*

## The situation

- New lead, new company. Boss wants **business-grade software that just works** and
  a team of juniors pointed in a valuable direction.
- We have a real asset already: **Freehold**, a production-ready starter kit
  (FastAPI + Postgres + Keycloak auth + Caddy HTTPS + encrypted secrets + a
  backup-gated deploy pipeline). The plumbing that usually eats a small team's first
  three months is done.
- The company's home turf is **construction / small-team project management**. That
  is not a limitation — it's our unfair advantage. We know the customer.

## The mission

Build **SaaS products we sell to other small businesses in the UK and Europe**,
starting in the domain we understand best (construction, trades, field service) and
using Freehold so we ship on a solid footing instead of reinventing infrastructure.

## Constraints (the real ones)

| Constraint | Implication |
|---|---|
| Team is **junior** | Scope must be small, well-specified, and boring to operate. No exotic tech. |
| New lead, **hard-ass boss** | Direction must be **defensible with sources**, not opinion. Hence this folder. |
| **Build to sell** (not internal) | We carry market risk: strangers must choose to pay. We de-risk that on purpose (below). |
| **UK / Europe** market | Compliance and VAT/e-invoicing rules differ from the US — and that's an *opportunity*, not just friction. |
| Freehold is **single-tenant today** | Selling to many customers needs multi-tenancy. That's a known, scoped gap — see [04](04-team-and-freehold.md). |

## The honest risk of the path we chose — and how we kill it

"Build to sell" is the higher-risk fork. A new lead betting the team on a product
strangers might not buy is exposed. We de-risk it three deliberate ways:

1. **Sell into the domain we already know.** Construction/trades, not a random
   vertical. We can talk to real users on day one because the company lives there.
2. **Anchor on compliance-driven "forced buy" demand.** The easiest software to
   sell is software a business is *legally required* to have. UK/EU are rolling out
   mandates (Making Tax Digital, CIS, Building Safety Act, EU e-invoicing/ViDA) that
   create must-buy demand from exactly our target customer. See [01](01-pain-landscape.md).
3. **Start narrow, prove willingness to pay early.** One sharp tool that a small
   crew will pay £X/month for beats a broad "platform" nobody adopts. The
   portfolio in [02](02-app-portfolio.md) is scored to find that first wedge.

## What "done" looks like for Monday

Not a demo. A **decision the boss can sign off on**: *this segment, this first
product, this reason it wins, this 90-day plan.* Backed by sourced pain-point
research so it reads as judgement, not a hunch.

## What we are explicitly NOT doing yet

- Not writing product code (the boss asked for the plan first — correct call).
- Not building a broad "platform." One wedge product first.
- Not competing head-on with US giants (Procore, Buildertrend) on their turf. We go
  where they're too expensive, too complex, or not localised for the UK/EU small crew.

---
*Next: [01-pain-landscape.md](01-pain-landscape.md) — the sourced evidence.*
