# Phase 0 · Workstream 4 — Format & channel brief

*Two questions that shape the product before a line is written: (1) exactly which
**open standards** must we hit to be compliant, and (2) is the **Steuerberater / DATEV
channel** a wall between us and the customer? Unlike the UK plan, there is **no
licence/certification gate** here — Swiss QR-bill and German XRechnung/ZUGFeRD are open
formats anyone can generate. The barriers are technical conformance and distribution.*

> This replaces the old "certification" workstream. Good news, confirmed by the
> research: generating a valid e-invoice needs **no HMRC/Peppol-style accreditation** —
> it's an open EN 16931 standard. The risk moved from *"are we allowed to sell it"* to
> *"can the customer's accountant block us."*

---

## A. The format targets (what "compliant" concretely means)

Confirm the exact spec each product must produce. All are published standards.

### Switzerland — QR-bill (beachhead product)
- **QR-bill Implementation Guidelines v2.3** (SIX), in force since **22 Nov 2025**.
- **Only structured (Type S) addresses** permitted; combined/Type K no longer processed.
- Banks **expected to reject non-compliant addresses from 30 Sept 2026** → our deadline.
- **To confirm:** the exact structured-address field spec, the Swico/SIX QR spec version
  to embed, and whether any Swiss "recognised software" list exists (research suggests **no**).

### Germany — XRechnung / ZUGFeRD (scale product)
- Must be a **structured format compliant with EN 16931**: **XRechnung** (pure XML) or
  **ZUGFeRD 2.x** (hybrid XML+PDF). A plain PDF does **not** count.
- **To confirm (important nuance):** not all ZUGFeRD 2.x profiles qualify — **MINIMUM and
  BASIC-WL do NOT** meet EN 16931 as full e-invoices. We must target **≥ BASIC / EN 16931
  COMFORT** profiles. Pin the exact profile before building the generator.
- Retention: output must be **GoBD-compliant** (immutable, retained, auditable). Confirm
  the concrete GoBD retention requirements our archive must satisfy.

**Deliverable:** a one-line spec per market — *"we generate `<format>` at `<profile/version>`,
archived per `<retention rule>`."* This is the acceptance criterion for the build.

---

## B. The channel question (the potentially-fatal one)

⚠️ From [01](../01-pain-landscape.md) Part D: in Germany the **Steuerberater often
chooses the software**, and DATEV dominates that ecosystem. If accountants funnel their
clients to DATEV/lexoffice, a newcomer is locked out of the micro-firm segment no matter
how good the workflow is.

Find out:
1. **Who decides?** (This is also Interview Q4.) Across the firms you talk to, how often
   does the *Treuhänder/Steuerberater* pick the tool vs the firm itself?
2. **Is DATEV a wall or a rail?** Can we **integrate/export** to DATEV (so the accountant
   keeps their world and the crew gets our app), turning the channel into a *feature*
   rather than a competitor? What does DATEV's import/export path look like?
3. **Switzerland parallel:** does the **Treuhänder** play the same gatekeeper role? (It
   may be weaker — many Swiss micro-firms self-serve on Bexio.)

**Deliverable:** a verdict — *"the accountant is a WALL (they choose, and won't touch a
newcomer) / a RAIL (we export to DATEV and everyone's happy) / NOT a factor (firms
self-serve)."* This single answer strongly shapes go-to-market.

---

## Why this is a workstream, not an afterthought

A new lead who says *"generating the format needs no licence — it's open EN 16931 — and
here's our DATEV-export path so the Steuerberater is a channel, not a blocker"* sounds
like they've done the homework. A lead who discovers the accountant lock-in *after*
launch looks reckless. That two-sentence answer is the entire deliverable.

---
*Next: [decision-scorecard.md](decision-scorecard.md) — where it all comes together.*
