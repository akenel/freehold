# 02 · The App Portfolio (scored)

*From the sourced pains in [01](01-pain-landscape.md) to a ranked build list. This is
the page you put in front of the boss next to [00-brief](00-brief.md).*

## The scoring

Each concept is scored 1–5 on three axes:

- **Pull** — how *compelled* the demand is. A legal deadline = 5. "Would be nice" = 2.
- **Reach** — size of the buyer pool in our domain.
- **Ease** — how buildable by a **junior team on Freehold**, *including the regulatory
  barrier to entry* (certification lowers Ease).

**Score = Pull × Reach × Ease** (higher = better first bet). Certification barriers
are called out explicitly because they can sink a junior team's timeline.

---

## The one insight that shapes everything

> **Sell the compliance *workflow and evidence layer*, not the *filing engine* — at least for v1.**

Filing tax returns or e-invoices to government requires **HMRC recognition / Peppol
Access Point certification** (unknown cost + lead time — see [01](01-pain-landscape.md) §5).
That's a heavy, slow gate for a new junior team.

But the **new 2026 CIS burden is mostly *record-keeping and workflow*** — verifying
subcontractors, **proving ongoing monitoring**, keeping an **audit trail**, and
*preparing* the monthly return. None of that requires filing certification. A tool
that makes a contractor **audit-ready and return-ready** — sitting *alongside*
whatever they file with — is a genuine must-have that **sidesteps the certification
gate entirely**. Add direct filing later, once recognised.

This turns the scariest unknown into a phasing decision instead of a blocker.

---

## The scorecard

| # | Concept | Segment | Pull | Reach | Ease | **Score** | Verdict |
|---|---|---|:-:|:-:|:-:|:-:|---|
| 1 | **CIS Companion** — sub verification + monitoring log + audit trail + monthly-return *prep* | Construction 4–50 | 5 | 5 | 4 | **100** | 🥇 **Build first** |
| 2 | **Site Diary + Timesheets** — daily logs, labour/materials capture, feeds CIS splits | Construction 4–50 | 3 | 5 | 5 | **75** | 🥈 Bundle with #1 |
| 3 | **Small-crew Job Hub** — jobs, quotes, scheduling (the original PM idea) | Construction 3–30 | 3 | 5 | 4 | **60** | 🥉 The platform #1 & #2 live on |
| 4 | **Reverse-Charge VAT helper** — correct DRC invoices for construction | Construction 3–50 | 4 | 4 | 4 | **64** | Fold into #1/#3 |
| 5 | **Peppol / ViDA e-invoicing connector** | UK+EU SMB 16–50 | 5 | 4 | 2 | **40** | Second act (needs cert) |
| 6 | **MTD quarterly filing** | All UK sole traders | 5 | 5 | 1 | **25** | ❌ Skip — commoditised + cert-heavy |
| 7 | **Golden-thread doc vault** (Building Safety Act) | HRB owners only | 4 | 1 | 3 | **12** | ❌ Too narrow |
| 8 | **Generic GDPR record-keeping** | Any SMB | 2 | 4 | 4 | **32** | Weak pull, crowded |
| 9 | **Subcontractor onboarding/compliance packs** | Construction 10–50 | 3 | 3 | 4 | **36** | Feature of #1, not a product |
| 10 | **Payment-chasing / cashflow** for trades | Trades 1–15 | 3 | 5 | 3 | **45** | Real pain, crowded — later |

*(Scores use unverified Reach/pull estimates from [01](01-pain-landscape.md); the
CIS pull=5 and construction Reach=5 rest on **verified** findings, which is why #1 is
the confident pick.)*

---

## The recommendation

**Lead product: `CIS Companion` (#1), built on top of a minimal `Job Hub` (#3),
with `Site Diary` (#2) as the daily-use hook.**

Why this wins as a *new lead's first bet*:

- **Pull is legally compelled and dated** — April 2026 CIS reforms are live. This is
  the rare B2B product with a *deadline doing your marketing for you.*
- **It's our domain** — construction, the biggest UK SME sector. We can find ten real
  customers to talk to this week because the company already lives here.
- **It routes around the certification gate** — v1 is workflow + evidence, not filing.
- **It's junior-buildable on Freehold** — auth, DB, deploy, backups already exist. The
  team builds *forms, records, a monitoring log, exports, and a clean audit trail* —
  well-scoped CRUD with real stakes, not distributed-systems heroics.
- **It has a second act** — once trusted, add HMRC-recognised filing, then the
  durable **Peppol/ViDA e-invoicing** play (#5) for the 2029–2030 wave. A roadmap
  with a moat at the end, not a dead end.

**What we deliberately skip:** direct MTD filing (#6) — every accounting incumbent
already owns it and it's certification-gated. We *integrate with* Xero/QuickBooks
rather than fight them.

---

## The 90-second pitch (for the boss)

> "The government just made monthly compliance mandatory for the UK's biggest small-
> business sector — construction — and is spending £1.7bn with AI to enforce it,
> starting this April. We build the tool that keeps a small crew audit-ready and
> return-ready, in the trade we already know, on infrastructure we already have. It
> needs no tax-filing licence to start, a junior team can ship the first version, and
> it opens onto the EU e-invoicing wave worth a decade of runway. We validate price
> with ten real contractors before we scale a line of it."

The unknowns (price, exact competitor gap, certification cost) are named up front in
[01](01-pain-landscape.md) §5 and scheduled as **Phase 0** in
[03-roadmap.md](03-roadmap.md) — so we're validating, not guessing.

---
*Next: [03-roadmap.md](03-roadmap.md) — the 30/90/180-day plan.*
