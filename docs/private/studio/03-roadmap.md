# 03 · Roadmap (30 / 90 / 180 days)

*From "sourced strategy" to "paying customers" without betting the team on the claims
that failed fact-checking. Phase 0 exists because the boss should never see build
budget spent before the commercial unknowns from [01](01-pain-landscape.md) Part D are
de-risked.*

**Shape:** land at **home in Switzerland** (small, dated, low-risk beachhead), then
carry the same crew-simple workflow into **Germany** ahead of the 2028 deadline.

---

## Phase 0 — Validate before you build (Week 1–2) · **do this first**

**Goal:** turn five unknowns into answers. No product code.

> 🧰 Runnable pack: [phase-0/](phase-0/README.md) — interview guide, competitor teardown,
> and the decision scorecard. Built for a junior pair to run Monday.

| Task | Unknown it kills | Owner | Done when |
|---|---|---|---|
| Interview **10 Swiss trades firms** (home, warm intros) on invoicing + QR-bill pain + spend | WTP + pain reality | Lead | 10 scored interviews |
| Interview / survey **5 German Handwerk firms** on the 2028 e-invoicing switch | DE demand + DATEV lock-in | Lead | 5 logged |
| **Teardown** plancraft, ToolTime, TAIFUN — is the *workflow* for a 2-person crew actually bad? | The workflow gap (our whole thesis) | Junior pair | Gap memo + verified pricing |
| Ask 5 firms: who chose your software — you or your **Steuerberater**? | DATEV/accountant lock-in | Junior | Clear answer |
| Confirm: do these firms want **hosted or on-prem/Swiss-data**? | Stack fit | Junior | Preference noted |

**Gate — two tests, both must pass:**
> 1. **Pain + spend:** ≥ **6 of 10** Swiss firms show real invoicing/compliance pain
>    **and** already spend money on it (software, bookkeeper, or their own hours).
> 2. **The gap is real:** the teardown finds a *genuine workflow gap* for tiny crews —
>    i.e. we can point to something plancraft/ToolTime make painful that we'd make simple.
>
> **If test 2 fails** (incumbents already nail crew-simplicity), **stop** — the format
> is commoditized and there's no wedge. Better to learn that now, free, than post-launch.

---

## Phase 1 — Beachhead ship (Day 15–45): the QR-bill fixer, at home

**Goal:** one narrow, dated, real product live in Switzerland — earn trust + first revenue.

Scope (deliberately tiny, tied to the **30 Sept 2026** bank cutoff):
- Import/enter customer + invoice data → validate & fix to **structured QR-bill addresses**.
- Generate compliant QR-bills; flag non-conformant records before the bank rejects them.
- Clean, mobile-friendly, German-first (FR/IT ready — see [04](04-team-and-freehold.md)).

**Freehold does the heavy lifting** (auth, DB, HTTPS, backups). Team writes domain CRUD
+ validation + PDF/QR generation. A junior-shaped build with a real deadline behind it.

---

## Phase 2 — The bet, validated (Day 45–90): Handwerk life raft MVP

Only if Phase 0 test 2 passed.
- Build the **mobile job → capture → structured e-invoice → GoBD archive** flow for
  1–10-person crews. Win on *simplicity*, not format.
- Onboard **3–5 design-partner firms** (start Swiss, add 1–2 German trades).
- Add **#5 site report / Rapport** as the daily-use hook so it's a habit, not a chore.
- **Stand up multi-tenancy** on Freehold (the one real infra gap — [04](04-team-and-freehold.md)).
  Per-customer deploys are an acceptable stopgap for the first few partners.

**Gate:** ≥3 firms using it weekly and ≥1 paying list price → scale into Germany.

---

## Phase 3 — Scale on the 2028 deadline (Day 90–180)

- Turn on **self-serve signup + billing**; publish *validated* pricing (not guessed).
- Push into the **German Handwerk** market — the 1M-firm pool — with the 2028 e-invoicing
  deadline as the marketing engine. Address **DATEV/Steuerberater** as a channel, not a wall
  (integrate/export to their world rather than fight it).
- Scope the **next compliance module** (the ratchet: whatever mandate lands next becomes
  expansion revenue on the same customer).

---

## What ships when (one glance)

| Horizon | Deliverable | Proof it worked |
|---|---|---|
| **Week 2** | Validation memo + go/no-go (both gate tests) | 10 CH + 5 DE interviews; workflow-gap confirmed |
| **Day 45** | QR-bill fixer live in Switzerland | Paying Swiss users before 30 Sept 2026 |
| **Day 90** | Handwerk life-raft MVP, 3–5 design partners, multi-tenant | Weekly active use |
| **Day 180** | Paid self-serve, German go-to-market on 2028 | First German list-price revenue |

---

## Risks & how the plan absorbs them

| Risk | Mitigation baked in |
|---|---|
| Format is commoditized, no wedge | Phase 0 **test 2** stops us before we build if the gap isn't real |
| Nobody will pay | Phase 0 **test 1** — validate spend before building |
| DATEV/Steuerberater lock-in | Tested in Phase 0; treated as a channel in Phase 3, not fought |
| Germany is far / not our network | We **land in Switzerland first** — revenue + proof before the big market |
| Junior team over-reaches | Phase 1 is tiny CRUD on finished infra; the bet waits for validation |
| Swiss deadline is "soft" (QR-bill) | It's the *beachhead*, not the foundation; the hard deadline (DE 2028) is the scale engine |

---
*Next: [04-team-and-freehold.md](04-team-and-freehold.md) — junior execution + the Freehold gaps (multi-tenancy, i18n).*
