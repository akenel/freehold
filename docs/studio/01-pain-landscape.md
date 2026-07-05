# 01 · The Pain Landscape (sourced)

*What actually drives a small German-speaking firm to buy software in 2026 — split
cleanly into what we can **prove** and what is still a **hypothesis**. That line is
the whole point of this document, and it matters more here than in the UK draft,
because the *commercially* critical claims are exactly the ones that failed checking.*

> **Confidence tags.** ✅ Verified (primary source — GOV/association/tax-authority —
> and survived 3-reviewer adversarial fact-checking). 🟡 Medium (one dissent / narrower
> than it looks). ⚠️ Unverified / hypothesis (plausible, widely repeated, but did **not**
> survive checking — do **not** state as fact to the boss; these are leads to validate).

---

## The core thesis

**The easiest software to sell is software a firm is legally compelled to own.** In
DACH, that compulsion is strongest and clearest in **Germany's B2B e-invoicing
mandate**. Switzerland — our home beachhead — has no equivalent hard deadline; its
demand comes from a *cluster* of softer, narrower forcing functions. So the shape is:
**land in Switzerland, scale on Germany's deadline.**

---

## PART A — Germany: the forcing function (the scale market)

### ✅ The e-invoicing deadline is real, dated, and unavoidable
- **Receive:** since **1 Jan 2025**, *every* domestic B2B firm — including one-person
  Handwerker and Kleinunternehmer — must be able to receive structured EN 16931
  e-invoices. *(But an email inbox suffices — receiving alone does not force a purchase.)*
- **Issue (the real buy trigger):** firms with turnover **> €800k from 1 Jan 2027**;
  **all** domestic B2B firms **from 1 Jan 2028**. For the micro/small trades we target,
  the binding date is effectively **1 Jan 2028**.
- **Format:** must be structured — **XRechnung** (XML) or **ZUGFeRD 2.x** (hybrid).
  A plain **PDF no longer counts** as an e-invoice.
- *Sources: IHK Frankfurt, DATEV, BMF FAQ, EU Commission, rickert.law, sevDesk.* [1–4]
- ⚠️ *Precision note: the €800k is total turnover (§19/§27 UStG), not B2B-only;
  Kleinunternehmer are exempt from issuing; B2C, cross-border and sub-€250 invoices are out of scope.*

### ✅ The addressable market is huge and micro-skewed
- German **Handwerk: ~1,038,254 firms (2024)**, ~6.3M employment relationships,
  **averaging ~6 employees** — squarely below DATEV-grade ERP complexity. This is the core segment.
- The official Destatis *construction* table (~20,857 establishments) only counts firms
  with **20+ employees** — so most small builders are invisible there and sit **inside
  the ~1M Handwerk count**. The winnable niche is the sub-20-employee crew.
- *Sources: ZDH (peak trades association, official URS data); Destatis.* [5][6]

### ⚠️ …but the format layer is already SERVED — this is the pivotal risk
- Incumbents across the whole price range — ERP-grade **TAIFUN** down to cheap
  mobile-first SaaS (**plancraft, HERO, ToolTime, mfr, Das Programm**) — already output
  XRechnung/ZUGFeRD and are GoBD-compliant, **with solo tiers on the market.**
- So the mandate is a **migration/adoption** opportunity, **not an empty-format gap.**
  *Raw XRechnung generation is commoditized.* [7]
- 🟡 This "broadly served" finding was **2-1**, and two supporting commercial claims were
  **refuted** (see below) — so the *size of the still-unconverted micro-firm segment is
  genuinely unknown.* The opening, if it exists, is **workflow + last-mile adoption for
  tiny mobile crews**, not the format. **This is the single thing Phase 0 must prove.**

---

## PART B — Switzerland: the beachhead (home advantage, softer pull)

### ✅ Switzerland has NO hard e-invoicing mandate
- B2B/B2C e-invoicing is **entirely voluntary**; **PDF invoices are legally valid**;
  the Federal Council has announced no timeline. The only mandate is **B2G** (federal
  suppliers, invoices **≥ CHF 5,000**, since 2016 — deliberately set to exempt small SMEs).
- Germany's mandate does **not** bind Swiss exporters (it obligates German-established
  firms only). So for a Swiss firm it's *market pull*, not a legal gun.
- *Sources: ESTV, primetax, ecosio, Sovos, BDO.* [8]

### ✅ The real Swiss forcing functions — a cluster, not a cliff
| Driver | What it forces | Date | Strength |
|---|---|---|---|
| **QR-bill structured address** | Update invoicing data/software or banks reject payments | banks expected to reject from **30 Sept 2026** | Strongest dated one, but "expected bank behaviour", narrow window [9] |
| **LMV 2026–2031** (binding construction collective agreement) | Minimum-wage + **working-time recording** for ~80,000 workers | in force **1 Jan 2026**, 6-yr term | Durable, sector-specific, founder knows it [10] |
| **Cantonal e-building-permit** (e.g. Zürich eBaugesucheZH) | All permits filed electronically | mandatory **1 Apr 2027** (ZH) | Real but **fragmented across 26 cantons** [11] |
| **Posted-worker notification** (Meldeverfahren) | Construction must notify **from day one**, 8 days in advance | ongoing | Recurring cross-border admin pain [12] |
| **nFADP** data protection | Processing register etc. | in force since Sept 2023 | 🟡 SME exemption <250 staff softens it [13] |

### ✅ Switzerland pays for software, and fragmentation is our MOAT
- **624,219 Swiss SMEs** (2023), **614,428 are micro/small (1–49)** — our band. [14]
- Construction already sustains **5+ entrenched construction-ERP incumbents**
  (AbaBau/Abacus, BauBit PRO, BauPlus, SORBA, WinBau) — willingness-to-pay is proven,
  and they leave the usual small-crew gaps (too expensive/complex, German-only, poor mobile). [15]
- **DE/FR/IT multilingual + 26-canton + Swiss-data-residency** repels foreign
  incumbents — a **defensible moat for a local team**, and a fit for our self-hostable stack.

---

## PART C — What we ruled OUT (and why that's a finding)

- ✅ **Manufacturing (Swiss MEM):** top pains are **macro and un-software-able** — lack
  of orders (60%), franc/FX (41%), energy (23%); skilled-labour only 4th (22%). ~75%
  rate their situation unfavourable. Only ~10,000 firms. **Not our wedge.** [16]
- ✅ **Manufacturing (German Mittelstand/ERP):** high willingness-to-pay but **ERP-scale
  delivery** (~€5,917/user, ~50% of projects over budget) — beyond a junior team. A
  later, higher-ticket adjacency, not an entry point. [17]
- ✅ **Austria:** **no** mandatory B2B e-invoicing, no binding timeline; only B2G (2014)
  + the Registrierkassenpflicht cash-register rule. ~251,598 trades firms (¼ of
  Germany). **A format-similar follow-on, not the beachhead.** [18]

---

## PART D — What we DON'T know (put this in front of the boss yourself)

Every one of these failed or was never established in research. They are Phase 0.

1. ⚠️ **Pricing / willingness-to-pay** — the Handwerker SaaS price ladder (€15–120/user/mo)
   was **refuted (1-2)**. We have **no** verified price point. Validate.
2. ⚠️ **Size of the unconverted segment** — the "only 24% ready to send" readiness gap
   was **refuted (0-3)**. How many micro-firms are still on paper is **unknown**.
3. ⚠️ **The workflow gap** — that tiny crews are underserved *on workflow* (vs format) is
   our whole thesis and is **unverified**. If incumbents already out-simplify us, there's no wedge.
4. ⚠️ **Steuerberater / DATEV lock-in** — the German tax-advisor often *chooses the
   software*. If they funnel clients to DATEV/lexoffice, a newcomer is locked out. **Potentially fatal — test early.**
5. ⚠️ **Hosted vs on-prem, and any Swiss-team advantage** — unproven either way.

---

## Sources
Verified findings rest on primary sources — Germany [1][3][5][6] (IHK/BMF, DATEV, ZDH,
Destatis); Switzerland [8][10][11][12][14][15] (ESTV, baumeister.swiss, zh.ch,
sem.admin.ch, kmu.admin.ch); Austria [18] (WKO, usp.gv.at).

1. IHK Frankfurt — E-Rechnungspflicht · 2. rickert.law — E-Rechnung B2B 2027 ·
3. DATEV — gesetzliche Regelungen · 4. sevDesk — E-Rechnung Handwerker ·
5. ZDH — Betriebe/Beschäftigte · 6. Destatis — Baugewerbe Betriebe ·
7. TAIFUN + für-gründer Handwerker-Vergleich · 8. primetax / invoicedataextraction — Swiss e-invoicing ·
9. SIX / projektron — QR-bill v2.3 · 10. baumeister.swiss — LMV 2026–2031 ·
11. zh.ch — eBaugesucheZH · 12. sem.admin.ch — Meldeverfahren ·
13. kmu.admin.ch — nFADP · 14. kmu.admin.ch — SME figures (STATENT) ·
15. baumeister.swiss — ERP-Vergleich · 16. swissinfo/Swissmechanic — MEM climate ·
17. erp-4-business / Trovarit — ERP TCO · 18. brandauer / WKO / usp.gv.at — Austria.

*Regulatory dates are time-sensitive. Germany's issue-deadline (2027/2028) is fixed as
of mid-2026; Austria's status is the most likely to change (a BMF proposal was expected
~Q3 2026). Re-check before committing budget.*

---
*Next: [02-app-portfolio.md](02-app-portfolio.md) — the scored build list.*
