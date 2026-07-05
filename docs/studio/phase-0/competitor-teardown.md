# Phase 0 · Workstream 3 — Competitor teardown

*The make-or-break workstream. Our entire wedge rests on one hypothesis: that the
invoice/job **workflow for a tiny 1–10-person crew** is genuinely bad in the
incumbents — because the **format (XRechnung/ZUGFeRD/QR-bill) is already commoditized.**
If the incumbents already nail crew-simplicity, there is no business. Prove it or kill it.*

> ⚠️ **This is Gate Test 2.** In [01](../01-pain-landscape.md) Part A the "incumbents
> broadly serve the mandate" finding survived (2-1) and the commercial-gap claims were
> **refuted**. So the format gap is closed; the *workflow* gap is our unproven thesis.
> This teardown is where it lives or dies.

---

## Who to tear down (free trials, a few hours each)

| Tool | Why it's on the list | Market |
|---|---|---|
| **plancraft** | Popular mobile-first Handwerk SaaS, cheap solo tier | 🇩🇪 |
| **ToolTime** | Mobile-first trades app, small crews | 🇩🇪 |
| **TAIFUN Handwerk** | ERP-grade, 1-person to KMU, ZUGFeRD + auto-accounting | 🇩🇪 |
| **HERO / mfr / Das Programm** | Round out the mobile-SaaS field if time allows | 🇩🇪 |
| **Bexio** | The Swiss SME accounting/invoicing default (QR-bill) | 🇨🇭 |
| *Optional:* Abacus/AbaBau, SORBA | The Swiss construction-ERP heavyweights (the "too complex" end) | 🇨🇭 |

Split across the junior pair. **~3 hours per tool.** You're not learning the whole
product — you're pressure-testing whether a *non-technical two-person crew* could
actually live in it.

---

## The five questions (score 0 = painless → 3 = genuinely bad-for-tiny-crews)

**High scores here = our opportunity.** We're hunting for pain, specifically for the smallest firms.

1. **On-site → invoice flow** — can a worker capture hours/materials/photos **on a phone
   on site**, and does that flow *straight* into an invoice, or is there re-typing at a desk?
2. **Time-to-first-invoice** — how long from signup to sending one real compliant
   invoice? Could a non-technical Meister do it alone without a setup call/onboarding fee?
3. **Simplicity vs bloat** — how much of the UI is stuff a 2-person crew will *never*
   use? Is it a job app or a shrunk-down ERP?
4. **Structured e-invoice / QR-bill output** — does it actually produce XRechnung/ZUGFeRD
   (DE) or structured QR-bill (CH) cleanly? *(Expect yes — this is the commoditized part.)*
5. **Price + model for a micro firm** — real solo/small-tier price (VERIFY live), per-user
   scaling, hidden setup/onboarding fees.

---

## Teardown record (one per tool)

```
Tool:                    Country: CH/DE    Trial type:        Reviewer:      Date:
Priced at (VERIFY live): ____ /mo   Model: flat / per-user / +setup fee

Q1 On-site→invoice flow    (0–3): __   Notes (where's the re-typing?):
Q2 Time-to-first-invoice   (0–3): __   Notes:
Q3 Simplicity vs bloat     (0–3): __   Notes:
Q4 Structured output       (0–3): __   Notes (confirm format works):
Q5 Micro-firm price/model  (0–3): __   Notes:

The ONE thing this tool makes clearly painful for a 2-person crew:
The ONE thing it does better than we'd expect:
```

---

## Also: kill the refuted pricing claim while you're in there

Our research **refuted** the €15–120/user/mo price ladder — so we have **no** trusted
price anchor. For each tool, record the **live, current** solo/small-tier price straight
from the vendor page. Replace guesses with facts in
[decision-scorecard.md](decision-scorecard.md).

---

## The verdict this workstream must deliver

A one-paragraph **gap memo**:

> *"Across N tools, on-site→invoice flow scored an average of __/3 of pain and
> time-to-first-invoice __/3. The clearest thing incumbents make painful for a tiny
> crew is ________. Verified solo-tier prices are €/CHF __–__. This [does / does not]
> support a workflow-first wedge for micro trades firms."*

- **If the gap is real** (incumbents force desk re-typing, heavy setup, ERP bloat) →
  Gate Test 2 passes, proceed to build.
- **If incumbents already nail crew-simplicity** → **stop.** The format is commoditized
  and there's no room. Learn it from a free trial, not a failed launch.

---
*Next: [format-and-channel-brief.md](format-and-channel-brief.md).*
