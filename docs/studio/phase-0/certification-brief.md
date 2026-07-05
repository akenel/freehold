# Phase 0 · Workstream 3 — The certification question

*The unglamorous workstream that can quietly kill a timeline. Before we build
anything that talks to HMRC or the Peppol network, we need to know what it **costs**
and how **long** it takes to be *allowed* to. This is the unknown that most shapes
product scope.*

> This is why [02-app-portfolio.md](../02-app-portfolio.md) recommends building the
> **compliance workflow + evidence layer first** and the **filing engine later**. If
> certification turns out to be cheap and fast, we can pull filing forward. If it's
> expensive and slow, our phasing already routes around it. Either way — **we need the
> real numbers**, not a guess.

---

## What to find out (the answers that change the plan)

### A. HMRC — for anything that *files* (CIS returns, MTD)
1. **Is our v1 in scope at all?** Confirm the [02](../02-app-portfolio.md) thesis: does
   *preparing* returns + keeping records + exporting (without submitting to HMRC)
   require **no** recognition? (Strong expectation: yes, no recognition needed — that's
   the whole point of starting there.) **Verify it.**
2. **CIS filing recognition** — what's the process to become HMRC-recognised software
   that can *submit* CIS returns? Is it self-service registration, a technical
   conformance test, or a formal accreditation? Cost? Lead time?
3. **MTD recognition** — same questions for MTD for Income Tax. (We're *skipping* MTD
   filing per the portfolio, but know the barrier so the decision is informed.)
4. **Ongoing obligations** — once recognised, what must we maintain (audits, re-tests,
   fees per year)?

**Where to look:** GOV.UK developer / "recognised software" pages, HMRC's Software
Developers Support Team (there's a mailbox — email them the specific questions), and
the CIS/MTD developer hub docs.

### B. Peppol / ViDA — for the e-invoicing second act (portfolio #5)
1. **Access Point certification** — to send/receive on the Peppol network you go
   through a **certified Access Point** (or become one). What does it cost to *use* an
   existing AP vs. *become* one? Which is right for us?
2. **Lead time & conformance** — testing/onboarding time to be live on Peppol.
3. **UK 2029 mandate scope** — the detailed roadmap is expected at the **Nov 2026
   Budget**. Note that our plan must not *depend* on a date that could move.

**Where to look:** OpenPeppol authority pages, UK Peppol authority guidance, and the
EC ViDA page already in our sources.

---

## The output: a one-page answer

```
HMRC — v1 (prepare + export, no submit):  recognition needed?  Y / N
    → (expected N; if Y, that reshapes v1)

CIS filing recognition:   process = ______   cost = £____   lead time = ____ weeks
MTD filing recognition:   process = ______   cost = £____   lead time = ____ weeks
Ongoing obligations:      ______

Peppol: use existing AP   cost = £____/mo or per-doc = ______   lead time = ____
        become an AP      cost = £____        lead time = ____
UK 2029 mandate scope:    known / awaiting Nov 2026 Budget

VERDICT: does certification block v1?   NO (build now) / YES (adjust scope)
Cheapest legal path to a sellable v1:   ______________________
```

---

## Why this is a workstream, not an afterthought

A new lead who launches a "CIS filing tool" and *then* discovers a six-month
accreditation gauntlet looks reckless. A new lead who says up front *"v1 needs no
licence because it prepares and evidences rather than files; here's the certification
cost and timeline for the filing upsell, sourced from HMRC directly"* looks like they
belong in the room. That sentence is the entire deliverable of this workstream.

---
*Next: [decision-scorecard.md](decision-scorecard.md) — where it all comes together.*
