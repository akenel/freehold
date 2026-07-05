# Phase 0 · Workstream 2 — Competitor teardown

*Confirm or kill the one hypothesis our whole wedge rests on: that existing tools
handle **UK construction compliance (CIS + Domestic Reverse Charge VAT) badly** for
small crews. If they actually do it well, we need to know now.*

> ⚠️ **This is a hypothesis, not a finding.** In [01](../01-pain-landscape.md) §4 the
> "incumbents are weak on CIS" story did **not** survive fact-checking — it's the most
> promising lead we have, and completely unproven. This teardown proves or buries it.

---

## Who to tear down (free trials, a few hours each)

| Tool | Why it's on the list | Trial |
|---|---|---|
| **Tradify** | Popular UK trade job-management, aimed at small crews/sole traders | 14-day free trial (reported) |
| **Commusoft** | Aimed at larger trade teams (5+ engineers) — the tier above us | Demo/trial |
| **Xero** (+ a CIS add-on) | The accounting incumbent; already MTD-recognised; where CIS often actually lives | Free trial |
| *Optional:* Powered Now, Jobber, Sage | Round out the picture if time allows | Trials |

Split across the junior pair. Timebox: ~3 hours per tool. You're not learning the
whole product — you're pressure-testing **five specific questions**.

---

## The five questions to answer for each tool

Score each **0 (absent) → 3 (does it well)**. Low scores are *our opportunity*.

1. **CIS monthly return prep** — can it produce/prepare a monthly CIS return,
   including **nil returns**? How much manual work is left?
2. **Subcontractor verification & monitoring** — does it track verification status and
   keep an **ongoing-monitoring audit trail** (the *new* April 2026 duty), or nothing?
3. **Labour/materials split & error-checking** — does it help get the split right and
   catch the three classic CIS error modes *before* filing?
4. **Domestic Reverse Charge VAT** — does it produce correct DRC invoices for
   construction, or does the user hand-bodge it?
5. **Fit for a 4–15 person crew** — pricing model (per-user? scales badly past 10?),
   mobile usability on site, setup complexity for a non-technical owner.

---

## Teardown record (one per tool)

```
Tool:                     Trial type:            Reviewer:        Date:
Priced at (VERIFY live):  ____ /user/mo   Model: per-user / flat / tiered

Q1 CIS return prep         (0–3): __   Notes:
Q2 Verification+monitoring (0–3): __   Notes:
Q3 Split & error-checking  (0–3): __   Notes:
Q4 Reverse-charge VAT      (0–3): __   Notes:
Q5 Fit for small crew      (0–3): __   Notes:

Where it clearly BREAKS for a small construction firm:
The one thing it does better than we'd expect:
```

---

## Also: verify the pricing while you're in there

Kill two birds — workstream 4 (pricing) gets answered here. For each tool, record the
**live, current** price and model straight from the vendor's page. In
[01](../01-pain-landscape.md) we only have *reported, unverified* numbers (Tradify
~£34/user/mo, iTrade ~£29, Powered Now ~£19–27, "small teams £30–50"). Replace them
with confirmed figures in [decision-scorecard.md](decision-scorecard.md).

This gives us the **price anchor**: if crews already pay £30–50/user/mo for a job app
that's weak on CIS, a compliance-strong tool has a clear place to sit.

---

## The verdict this workstream must deliver

A one-paragraph **gap memo**:

> *"Across N tools, CIS monitoring/audit-trail scored an average of __/3 and reverse-
> charge __/3. The clearest unmet need for a small crew is ________. The realistic
> price anchor is £__–__/user/mo. This [does / does not] support CIS Companion as a
> distinct product."*

If the incumbents already nail CIS compliance → we pivot (maybe to a different pain in
the portfolio). Better to learn it from a free trial than from a failed launch.

---
*Next: [certification-brief.md](certification-brief.md).*
