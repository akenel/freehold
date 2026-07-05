# 03 · Roadmap (30 / 90 / 180 days)

*The phased plan to get from "good idea on paper" to "paying customers" without
betting the team on an unvalidated guess. Phase 0 exists precisely because a hard-ass
boss should never see us spend build budget before we've de-risked the unknowns from
[01](01-pain-landscape.md) §5.*

---

## Phase 0 — Validate before you build (Week 1–2) · **do this first**

**Goal:** convert the four unknowns into answers. No product code yet.

| Task | Answers which unknown | Owner | Done when |
|---|---|---|---|
| Interview **10 small construction firms** on CIS pain + what they'd pay | WTP + real pain | Lead | 10 conversations logged |
| Hands-on trial of **Tradify, Commusoft, Xero** — where does CIS actually break? | Competitor gap | Junior pair | Gap memo written |
| Pin down **HMRC recognition + Peppol Access Point** process, cost, lead time | Certification barrier | Lead | 1-page cost/time answer |
| Confirm **reported pricing** (£15–50/user/mo) against live vendor pages | Price anchor | Junior | Verified pricing table |

**Gate:** if ≥6 of 10 contractors say the CIS burden is real *and* would pay for a
tool that keeps them audit-ready → proceed. If not → revisit the portfolio, don't
throw good money after a hunch. **This gate is the thing that covers you.**

---

## Phase 1 — First slice (Day 15–45): `CIS Companion` MVP on Freehold

**Goal:** one narrow, real, demoable feature the boss can click — built on the
Freehold starter so infra is free.

Scope (deliberately tiny):
- **Subcontractor register** — add a sub, store UTR/verification reference, status.
- **Verification & monitoring log** — record each verification + ongoing checks, timestamped → the *evidence trail* the 2026 rules demand.
- **Monthly return prep view** — labour/materials split per sub, flags the three common error modes *before* they file.
- **Audit-ready export** — clean PDF/CSV a contractor (or HMRC) can inspect.

Explicitly **out of scope for v1:** filing to HMRC (certification gate), payments,
full accounting. Integrate/export, don't rebuild.

**Freehold does the heavy lifting:** auth + roles (Keycloak), data + backups
(Postgres + backup-gated deploy), HTTPS (Caddy). Team writes domain CRUD + exports.

---

## Phase 2 — First paying customers (Day 45–90)

- Onboard **3–5 of the Phase 0 contractors** as design partners (free/discounted).
- Add the **Reverse-Charge VAT helper** and a minimal **Job Hub** (jobs the subs
  attach to) so it's daily-useful, not just monthly.
- **Stand up multi-tenancy** on Freehold (the one real infra gap — see
  [04](04-team-and-freehold.md)). Until then, one isolated deploy per design partner
  is an acceptable stopgap.
- Instrument: are they *using* the monitoring log weekly? That's the retention signal.

**Gate:** ≥3 firms using it in anger and ≥1 willing to pay list price → scale.

---

## Phase 3 — Scale the wedge + open the second act (Day 90–180)

- Turn on **self-serve signup + billing**; publish real pricing (validated, not guessed).
- Pursue **HMRC recognition** so `CIS Companion` can file directly — the upsell.
- Scope the **Peppol/ViDA e-invoicing connector** (portfolio #5): the durable,
  EU-wide, 2029–2030 play with a certification moat that protects us once we're through it.
- Decide on the second vertical only *after* construction is repeatable.

---

## What ships when (one-glance)

| Horizon | Deliverable | Proof it worked |
|---|---|---|
| **Week 2** | Validation memo + go/no-go | 10 interviews, certification cost known |
| **Day 45** | `CIS Companion` MVP on Freehold | Boss clicks a real audit-ready export |
| **Day 90** | 3–5 design partners live, multi-tenant | Weekly active use |
| **Day 180** | Paid self-serve + HMRC-recognition in progress | First list-price revenue |

---

## Risks & how the plan absorbs them

| Risk | Mitigation baked into the plan |
|---|---|
| Nobody will pay | Phase 0 gate — validate WTP before building |
| Certification blocks us | v1 is workflow/evidence, no filing licence needed |
| Peppol timeline shifts (Nov 2026 Budget) | It's the *second act*, not the first bet — we're not exposed to its date |
| Junior team over-reaches | Scope is CRUD + exports on finished infra; no exotic tech |
| Incumbent adds CIS depth | We're faster and domain-native; and we own the customer relationship early |

---
*Next: [04-team-and-freehold.md](04-team-and-freehold.md) — how the juniors execute, and the one thing Freehold must grow.*
