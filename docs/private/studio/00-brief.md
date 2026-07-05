# 00 · The Brief

*The situation, the mission, and the honest risk — re-anchored to the founder's home
region (Switzerland → Germany), built on sourced research, so nobody can say we walked
in blind.*

## The situation

- New lead, new company, based in **Switzerland**. Boss wants **business-grade
  software that just works** and a team of juniors pointed somewhere valuable.
- We have a real asset: **Freehold**, a production-ready starter kit (FastAPI +
  Postgres + Keycloak auth + Caddy HTTPS + encrypted secrets + backup-gated deploy).
  The infra that usually eats a small team's first three months is done.
- The company's home turf is **construction / small-team project management** — our
  unfair advantage: we know the customer and speak the language.

## The mission

Build **SaaS we sell to other small businesses**, aimed at the one force that only
grows: **the rising compliance burden on small firms.** Land in **Switzerland** (home,
trust, network), scale into **Germany** (10× the market, and the only DACH country
with a hard e-invoicing deadline).

## The thesis: sell the life raft, not the vulture

Compliance is becoming a **permanent, ratcheting tax on the right to trade** — and a
*regressive* one. Digital-reporting mandates carry a roughly **fixed cost per firm**,
so they hit a 3-person crew a hundred times harder than a 300-person company. Every new
rule quietly transfers survival odds from small to large.

That's not a reason the market shrinks — it's the reason it exists. **The survivors are
whoever gets cheap, simple tooling that makes compliance disappear.** We sell that. We
are the thing that lets a small firm stay legal without hiring IT or a full-time
bookkeeper. Each new regulation is a new module on the same customer — an *expanding*
revenue surface with a demand driver that only grows.

## The forcing function we build around

**Germany's B2B e-invoicing mandate** (sourced, verified — see [01](01-pain-landscape.md)):

| Date | Who must issue structured e-invoices (XRechnung/ZUGFeRD) |
|---|---|
| 1 Jan 2025 | *Everyone* must be able to **receive** them (already live) |
| 1 Jan 2027 | Firms with turnover **> €800k** must **issue** |
| **1 Jan 2028** | **All** domestic B2B firms must issue — incl. the ~1M micro Handwerk crews |

That 2028 date is the deadline doing our marketing for us — the thing Switzerland's
softer rules don't give us.

## Constraints (the real ones)

| Constraint | Implication |
|---|---|
| Team is **junior** | Scope small, well-specified, boring to operate. No ERP-scale ambitions. |
| New lead, **hard-ass boss** | Direction defensible **with sources**, not opinion. Hence this folder. |
| **Build to sell** | Market risk is real; we de-risk it deliberately (below). |
| **CH beachhead → DE scale** | Two regimes. Switzerland's forcing functions are softer; Germany's is the hard deadline. |
| Freehold is **single-tenant, single-language today** | Selling to many firms needs multi-tenancy + DE/FR/IT i18n — known, scoped gaps ([04](04-team-and-freehold.md)). |

## The honest risk — and how we kill it

Two things make "build to sell" dangerous here. We name both up front.

1. **The format is already commoditized.** A dozen incumbents (TAIFUN → plancraft →
   ToolTime) already generate XRechnung/ZUGFeRD, some with cheap solo tiers. **We
   cannot win by "making e-invoices."** Our wedge is the *whole workflow for the
   smallest crews* — job → mobile capture → e-invoice → archived — simple enough that
   a non-technical 2–6 person firm actually switches. If we can't out-simplify the
   incumbents on workflow, there is no business. **Phase 0 must confirm this gap is real.**
2. **The commercial numbers are unproven.** Pricing, the size of the still-on-paper
   segment, and whether tiny firms pick us over their *Steuerberater's* DATEV setup —
   all failed fact-checking. **We validate with real firms before we build.** See
   [03-roadmap.md](03-roadmap.md) Phase 0.

We de-risk on top of that by **landing in our home market** (Switzerland — we can talk
to ten real firms this week) and by **anchoring on a legally-compelled deadline**
(Germany 2028) rather than a discretionary "nice to have."

## What "done" looks like for Monday

Not a demo. A **decision the boss can sign**: *this segment (micro German-speaking
trades), this forcing function (2028 e-invoicing), this wedge (the workflow, not the
format), this beachhead (Switzerland), this 90-day validation plan.* Backed by sources.

## What we are explicitly NOT doing

- Not writing product code yet (plan first — correct call).
- Not building another XRechnung generator (commoditized).
- Not chasing manufacturing (macro pain in CH, ERP-scale in DE — both wrong for us).
- Not leading in Austria (no B2B mandate — a later follow-on).
- Not competing with DATEV/ERPs on their turf. We go *underneath* them, to the firms
  they're too complex and too expensive to serve.

---
*Next: [01-pain-landscape.md](01-pain-landscape.md) — the sourced evidence, Switzerland + Germany.*
