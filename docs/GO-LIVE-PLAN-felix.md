# THE GO-LIVE PLAN — Freehold / BANCO for Felix (Customer Zero)

*Lead synthesis. Grounded in the four system audits, the real 500-row sample, the packet spec, and the brutal critique — with the critique's fixes folded in, not footnoted. Solo-dev-survivable or it doesn't ship.*

---

## 0. GATE ZERO — answer this before anything else (blocks the entire plan's shape)

**Is Felix already trading on BANCO in production, yes or no?** The sample is a named live shop (`La Piazza, LP-WB-20260725`). Nothing upstream resolves this, and the whole plan inverts on the answer:

- **IF YES** — then "Phase 0: prove the box before go-live" is retrospective theatre and the **untested restore is a live emergency, not a checkbox.** A live shop is running with no proven recovery and a backup that silently omits logins and images (see §4). Jump straight to the DR emergency in §8, item 1.
- **IF NO** — then there is a **data-migration milestone** (existing stock / till state → BANCO) that appears in *none* of the source plans. That is Phase 0, task zero, and it must be scoped before any go-live date is spoken.

Do not proceed past this line without the answer written down. Everything below assumes you've stated it.

---

## 1. Verdict

**The software is ~90% there; the shop is not.** The online sell flow (scan→ring→pay→receipt, server-side 18+ age gate, Swiss per-line VAT split, cash-drawer shifts with variance, manager refunds, RBAC, on-the-fly create, EAN-13 labels) is genuinely production-grade and battle-scarred — this is not a build project, it's a **proof-and-discipline** project. The gap to Felix trading is **three things, none of them features**: (a) **data quality** — 97.8% of stock carries synthetic `2000000…` in-store EANs, so "scan → right product" is a *label-printing discipline* problem, not an AI or catalogue problem; (b) **offline resilience** — the till *cannot complete a sale* if its own box/LAN blips (no outbox), and the one restore that proves ownership has never been drilled and omits Keycloak logins + MinIO photos; (c) **ops discipline** — bus factor of one at the counter, a card path that's a mock seam, a cost-privacy leak in the recommended cleaning loop, and hardware (printer/scanner/UPS/LAN) treated as given rather than assembled. Felix can trade within **~2 weeks of proofs** on a single box with an operational offline stance — *provided* the restore is drilled and the cost leak is closed first. The moat (clean 4-language catalogue) is months of Felix-shelf-time behind that and blocks zero revenue.

---

## 2. Locked decisions (settled — do not relitigate)

1. **Decoupled contract.** Catalogue service and BANCO POS are separate, joined only by a versioned file packet + a cross-system key. The till never makes a runtime call to Angel's catalogue server.
2. **Offline-first, stated honestly.** "Never depend on the *catalogue service* being online" — **met** (till runs on local Postgres). "Never stop selling on any network event" — **NOT met today** and mitigated operationally at go-live, built properly later. Say this to Felix in words; do not let "offline-first" imply resilience the code lacks.
3. **Two-layer cost.** Universal layer (public product truth, Angel owns) vs shop-private COST (secret, never leaves the shop's box). **The cleaner never writes cost — and no packet that leaves the box may contain cost.** This is currently violated in production (see §4/§7); closing it is a go-live gate, not a nicety.
4. **The spine is SKU + name, NOT the manufacturer EAN.** For 98% of Felix's stock the EAN is a shop-local synthetic placeholder — un-lookupable, colliding across shops. The real manufacturer EAN is a *bonus* on branded consumables. Re-key every cross-shop/supplier-scrape join on SKU+name or the enrichment build-order fires on empty.
5. **Scope = Felix's moving assortment, not 5,000 SKUs.** Perfect what sells (read from the sales log — perpetual inventory is deliberately zero); clean the long tail as it sells.
6. **Deferred, by prior agreement:** kiosk (built, route-off), member marketplace (not built), Europe/DACH expansion.
7. **Local Keycloak, not shared/remote.** The till authenticates against the local realm in `compose.yml`. A remote realm means one blip logs out the whole shop and the offline-read mode is dead too. This is a **Phase-0 hard gate**, not a "verify and note."

---

## 3. Phased roadmap

Effort bands are **part-time calendar** for one person also running a shop's backbone — not ideal heads-down days. The critique's fantasy estimates are corrected here.

### PHASE 0 — PROVE THE BOX + STOP THE BLEEDING · ~1.5–2 weeks · **CRITICAL PATH**
*FELIX-SPECIFIC. Proofs and two emergencies, not features. Tasks are parallelizable — do NOT serialize them behind the restore drill.*

| Task | Effort (realistic) | Gate / DoD |
|---|---|---|
| **P0.1 — Close the cost leak at BANCO's export edge.** BANCO's `worklist.xlsx` writes `cost` (`pos_router.py:5178`). The recommended loop uploads it to Angel's single-tenant remote server. **Stop.** Either strip `cost` from any packet that leaves the box, OR run the cleaner strictly on-box until stripped. No clean cycle touches the remote until this ships. | 0.5–1 day | Exported packet provably contains no `cost` column; verified by diff. |
| **P0.2 — Make the backup COMPLETE.** Current `pg_dump` captures `helix_db` only — Keycloak logins (`keycloak` DB) and product photos (`minio_data` volume) are silently omitted. Add second DB dump + MinIO mirror + push secrets (`.env`, realm, GPG passphrase, B2 key) **off-box** via existing SOPS+age. | 1–2 days | One artifact set restores product rows **+ a post-go-live staff login + a rendered product photo**. |
| **P0.3 — DRILL THE RESTORE FROM ZERO** on a clean box. Blocked only on a read-only B2 key (trivial). First run *will* detonate (volume perms, Keycloak realm import ordering, MinIO buckets) — budget for it. | **3–5 days** (not "half a day"); passes-twice bar may take a week | Clean box: zero → HTTPS-serving → real data + logins + images. Wall-clock logged. Snag list empty on second run. |
| **P0.4 — Local-Keycloak hard gate.** Confirm the till auths against the local realm, not the inherited wolfhold shared Keycloak. | 0.5 day | Pull the box's WAN link; already-logged-in cashier stays authenticated. Written down. |
| **P0.5 — Native-review the de-CH staff strings.** Header says "NATIVE REVIEW REQUIRED BEFORE PROD." Felix reads, Angel edits. FR/IT stay draft (not on a German-CH shop's daily path). Make blocker/error strings **iconographic** where a cashier may not read DE/IT/EN. | 1 session | Every string on scan→checkout→shift-close→refund path signed off by Felix; no machine-German visible. |
| **P0.6 — Assemble & prove the physical print/scan chain.** *This is the hidden go-live killer.* Decide the topology: box (headless server) + **till client device** (tablet/PC with browser) + scanner gun (USB-HID vs BT) + Brother QL-820NWB on the client's OS print path. Then print 10 labels (both sizes) → rescan each → correct single SKU, incl. 3 variant look-alikes. | 1 day *once hardware is present* | Print→scan→right-SKU proven on real hardware, on the real client device. |
| **P0.7 — Card-path decision, written + dry-run.** Standalone terminal (SumUp/Worldline/Nexi), cashier taps CARD tender in BANCO, no integration in v1. **Add:** a daily reconciliation line — terminal settlement total vs BANCO card total (the accountant's first question). | 0.5 day | One end-to-end dry run; reconciliation step written into the daily-close SOP. |
| **P0.8 — go-live hygiene guards.** Hard-fail `go-live` on unchanged default secrets; DNS preflight before cert issuance. | 0.5–1 day | `go-live` refuses to run with defaults. |
| **P0.9 — Buy the load-bearing hardware.** UPS (~CHF 150), **wired LAN** between till client and box (not WiFi — see §4), scanner gun, label roll stock. | procurement | Physically present and cabled. |

**PHASE-0 GO-LIVE GATE (all must be true, all pre-trade-provable):**
1. Restore drilled from zero, twice, wall-clock logged — **the ownership promise is proven, not assumed.**
2. Backup captures the whole shop (DB + Keycloak + MinIO + off-box secrets).
3. Cost never leaves the box in any packet.
4. Till auths local; one label prints and rescans to the right SKU on real hardware.
5. Card path + daily reconciliation documented.
6. DE staff UI reviewed; box on UPS + wired LAN.

*Explicitly NOT in Phase 0: offline outbox, PDF receipts, catalogue enrichment, structured refunds, FR/IT enrichment, the cleaner packet refactor.*

### GO-LIVE → PHASE 1 — FELIX TRADES · 2–4 weeks wall-clock, throttled by shelf time
*This IS the go-live. Dominated by manual shop work, not code.*

**Goal:** Felix sells daily on his actual moving assortment, on placeholder EANs + printed labels.

- **Label-printing SOP with hygiene rule (the real EAN spine).** Every physical item carries exactly one scannable code → one SKU. **Critical hygiene rule the source plans missed:** when a barcode changes (placeholder → real-EAN alias, or a variant re-bin), the **old physical labels must be hunted down and destroyed.** Two labels for one SKU, or a placeholder left on the wrong variant bin, *is* the "1-in-5 wrong / wrong price rung" failure. Label round-trip proof tests a clean label; hygiene-over-time is where real errors live.
- **Real-EAN backfill on fast-moving branded consumables** (papers, filters, pouches, lighters, e-liquids — the ~2% with a real pack barcode). Scan pack → bind as **alias** (placeholder demoted, old labels still scan). `product_barcodes` + `_find_product_by_any_barcode` already support this — it's data entry, not code. **Realistic: 2–3× the "1 min/SKU" estimate** — find item, pick the right barcode among several on the pack, confirm alias-not-conflict, back-stock vs shelf, interrupted by customers. Several shelf-days.
- **A <5s fast path for scanner misses during a Saturday rush.** On-the-fly create (30s + photo-AI) is not a rush answer with six people in the queue. Configure **PLU quick-keys** for top impulse items (papers/lighters/filters) so a miss doesn't stall the counter. *(Verify BANCO supports quick-keys; if not, this is a small, high-value v1 addition — the one place a feature may be justified.)*
- **Scan-time visual confirmation for variants.** The most common head-shop error is ringing the blue 18mm at the black 14mm price. Ensure the scanned line shows a **photo large enough to eyeball** "yes, that one." *(Confirm the till line renders the product image at usable size; if not, small UI fix.)*
- Everything else (categories, sizes, brands, translations) stays un-enriched behind Phase 3. Blocks no sale.

**GO-LIVE GATE (this milestone) — pre-trade, provable now:**
- Fast-moving branded pile carries its **real** manufacturer EAN as alias — target 100% of that small pile (dozens, not thousands).
- Label round-trip + hygiene SOP written and walked with Felix.
- PLU fast-path and variant photo-confirmation working.
- Offline stance stated aloud to Felix (see below).
- Cart-preservation confirmed: a failed checkout POST **keeps the cart on screen** so the cashier can copy it to paper, not re-ring from memory.

**POST-GO-LIVE ACCEPTANCE (confidence checkpoints — NOT pre-trade gates; you cannot measure a trading week before trading):**
- **Scan → correct product on first scan ≥ 98% on the fast-moving branded pile** — measured over a real trading week. **No first-scan promise on no-barcode generic glass** (it resolves only via a human-placed shelf label; 99.9% is a fantasy number). One bar, survivable, honest.
- 5 consecutive trading days: cash drawer variance in tolerance; no scan miss the cashier couldn't resolve via PLU or on-the-fly.

### PHASE 2 — OFFLINE CONTINUITY: OPERATIONAL NOW, CODE ONLY IF PROVEN NEEDED
*GENERAL-PLATFORM. The critique is right: do NOT build the outbox on faith.*

The outbox is **the single hardest thing in the stack** and where projects die. Idempotent `/sales` (`client_uuid`) solves *double-submit* only — it does **not** solve the draining queue, background-sync lifecycle, the **offline-auth hole** (Keycloak network-only in the SW — a shift-change or session-expiry mid-blip locks out all staff), cashier-visible sync state, partial-failure reconciliation, "closed the tab with 3 unsynced sales," or two devices queuing the same shift. Honest band: **4–8 weeks part-time with a bug tail in months** — not 1–2 weeks.

**So:**
1. **NOW (operational, in Phase 1):** box on UPS + **wired LAN** (not WiFi) between till client and box. This covers power loss *and* the most common connectivity blips — but be precise with Felix: UPS covers power only; wired LAN covers the switch/WiFi drop that UPS does not. A mid-sale box crash still loses the in-flight sale to paper.
2. **NOW (instrument):** log how often the box/LAN actually blips during trading. If it's twice a year, weeks of sync-engine code is the wrong place for a solo dev's scarcest hours.
3. **LATER (build only if incident data proves the pain):** the outbox on top of the idempotent keystone. Solve offline-auth first (cached short-lived till session) or the feature defeats itself.

**DoD (if built):** airplane-mode mid-sale → sale completes + prints → reconnect → server shows exactly one sale, no dupe → lands in shift close. Cashier can log in with the box offline. Test 10 queued incl. one deliberate double-flush.

### PHASE 3 — CATALOGUE / THE MOAT · months, part-time, behind a live till · blocks zero revenue
*Runs in parallel with a trading shop. Gated by Felix's shelf hours, not Angel's code.*

**The critique's sharpest cut, adopted:** for Felix's go-live, **route catalogue maintenance through BANCO's OWN in-app tools** (worklist export, AI product-suggest, snap-a-photo, catalog-health, integrity sweep, 52-cat taxonomy, one-click audit revert). Freehold is a generic cleaner with *zero* catalogue/EAN/BANCO-specific code; wiring it up (taxonomy caps, reference-tab ingestion, cost guard, pristine round-trip export) is **weeks of engineering that serves the multi-shop moat, not Felix trading.** Angel categorises inside BANCO's worklist for the first months. Freehold gets wired only when a second paying shop justifies the platform.

**3a — Cleaner code (deferred until moat-justified; do first *within* Phase 3, small pieces high-leverage):**
- Raise/remove taxonomy caps (`MAX_TAXONOMY=40`→52, `MAX_TAXONOMY_LEN=24` drops a 26-char category) + a test. ~0.5 day.
- Feed Glossary + Suppliers tabs into the `analyze` payload — the fix for confident misses (`NS = Normschliff → bong joint`). **Hidden blocker the source plan mispriced:** the cleaner reads exactly one sheet today; multi-sheet ingestion is a real code change, not part of the "1–2 day hand-authoring." Band the *code* separately: ~2–3 days.
- Hard S-column denylist (`cost_chf`, `sku`) refusing any action targeting them, + test. ~0.5 day. *(Note: this guards the cleaner input; the actual live leak is fixed at BANCO's export edge in P0.1 — both needed.)*
- Pristine round-trip export (reproduce BANCO's schema, write `action`/`status`, keep `sku`/`cost` untouched). **The larger lift: 1–2 weeks** of fiddly, test-heavy work. Until it ships, a human hand-copies categories back — acceptable for months, and a reason to keep this deferred.

**3b — Enrich Felix's moving assortment (content, the long grind):**
- **Size/variant** (100% missing) — disambiguates the look-alike families that cause wrong scans. Do before variant families are trustworthy; it's C4's dependency.
- **Brand** (85% missing, much genuinely generic) — AI-drafts from name, human-gated.
- **4-language DE→FR/IT/EN** — **CUT until a second paying shop demands it** (see §6). No FR/IT native reviewer exists in Angel's world; "weeks" is really months of review capacity he doesn't have.

**DoD (per assortment slice):** >95% category, sized, brand-filled, real EANs where they physically exist — on SKUs Felix actually sells.

### PHASE 4 — LATER (do not pull forward)
Multi-shop / per-tenant vault isolation (today any logged-in user reads any vault key — fine for one box, blocks the subscription business); supplier scraping (fires on empty for synthetic EANs); cross-shop GS1 moat; kiosk (parked); PDF receipt archiving (reprint-from-history covers CH's legal need); structured refunds/voids + reason codes.

---

## 4. DR & resilience

**RTO/RPO for a head shop (not a bank):** never fully stop taking money; never lose a committed sale (VAT, 10-yr retention, end-of-day reconciliation). The honest bounding truth the DR table must state out loud: **the real RTO is bounded by Angel's consciousness.** "≤4h restore" and "phone rings when the box dies" both assume Angel is awake, reachable, free. With bus factor 1, if Angel is asleep/sick/flying, recovery time = "whenever Angel wakes up." Fix that with a **cold spare + a runbook a non-Angel (Felix) can execute**, not more monitoring that wakes one man.

| Failure | RPO | RTO | How met |
|---|---|---|---|
| App crash, box healthy | 0 | ≤10 min | `docker compose restart` |
| Internet down, box up | 0 | 0 lookup/price; **sale blocked** | Local box; paper + card terminal fallback |
| LAN/WiFi blip | 0 | **sale blocked mid-transaction** | Wired LAN reduces frequency; paper fallback; outbox LATER |
| Angel's server down | 0 | 0 | Already met — async file packet |
| Box death/theft/fire | ≤1h target, ≤24h ceiling | ≤4h *if Angel awake* + cold spare | Hourly dumps + drilled restore |

**Backup (fix in P0.2):** current chain (`pg_dump→gzip→gpg AES256→B2`, healthchecks.io dead-man switch, careful restore) is well-built but **silently omits Keycloak logins and MinIO photos** and has never been restored from zero. Add second DB, MinIO mirror, off-box secrets.

**Monitoring (Phase 0/1, ~1 day):** external uptime check → **push/SMS to Angel's phone** on box-unreachable / postgres-down / disk>85% / backup-missed / cert-renewal-failed. Do **not** page on MinIO/Keycloak-only faults (they don't stop sales) — page fatigue kills solo-dev alerting.

**Continuity ladder:** L1 internet-down → paper + standalone terminal, key in later; **cart stays on screen** on failed checkout. L4 box-dead → trade on paper, restore B2 onto cold spare, reconcile paper sales in. **Compliance note:** a paper sale puts the **18+ age gate on the honor system** — Felix must know this is a legal exposure on exactly the busy day it's most likely, not a UX inconvenience.

---

## 5. Catalogue cutover (EAN-integrity-first, no big-bang)

**There is no cutover event.** The catalogue improves under a live, selling till. Concretely:

1. **The EAN work is two non-conflatable jobs.** (a) In-shop scan integrity = **label-printing SOP + hygiene** (destroy old labels on any change) — the catalogue cannot touch it. (b) Real-EAN backfill on branded consumables = manual shelf work, the only genuine "EAN task." The cross-shop moat join keyed on EAN is broken for 98% by construction and is a LATER/platform concern — never a Felix gate.
2. **Parallel run is the default state, not a phase.** BANCO already sells on placeholder EANs + local labels. Cleaning improves product *pages* behind a shop that never stopped trading.
3. **Batch, never big-bang.** One shelf / one supplier block per cycle (the sample is already one TAM block). Import is **dry-run by default** — see the diff before writing.
4. **Fallback is in the identity model.** Import matches on `sku`, refuses blind barcode binds; `sku` and `cost` never change; audit feed has one-click revert. Blast radius of a bad clean = a revertable category label, never a lost sale or corrupted price.
5. **The cleaning loop runs in BANCO's own worklist for now** (§3), not through Freehold — until the moat justifies wiring Freehold and P0.1 + the round-trip export make the loop safe and closed.

**Soft go-live gate for "catalogue ready":** fast pile ≥85% category accuracy, real EANs where they physically exist, variant families sized-and-labelled. SLOW tail and 4-language moat trail behind forever, on the shop's clock.

---

## 6. Cut from v1

| CUT | Why safe for Felix's go-live |
|---|---|
| **Kiosk** | Built, route-off. Zero revenue path removed. |
| **Member marketplace** | Members refuse to be in the system yet. Building it = building a refused feature. |
| **FR staff UI** | German-CH shop. Canton-triggered LATER. |
| **4-language FR/IT/EN enrichment** | The moat, not the till. Un-enriched product still scans and sells. **No native reviewer exists** — would be months of capacity Angel lacks. Kill until a second paying shop demands it. |
| **Freehold wired to Felix's daily loop** | Weeks of platform engineering. Angel categorises in BANCO's own worklist. Wire it when the moat pays. |
| **Offline outbox** | 4–8 weeks of the hardest code. Operational mitigation (UPS + wired LAN + paper + cold spare) covers day one. Build only when instrumented blip data proves the pain. |
| **Pristine round-trip export refactor** | 1–2 weeks. Human hand-copy of categories is fine for months. |
| **Worldline TIM card integration** | Standalone terminal + CARD-tender SOP is standard CH practice, works day one. |
| **PDF/archival receipt** | Browser-print + reprint-from-history covers the CH legal need (no fiscal signing required). |
| **Structured returns / reason codes / line-level / restock** | Manager refund + audit-revert is enough for one-shop day-one. Perpetual inventory is zero → restock meaningless. |
| **Server-side void** | Post-completion correction = manager refund, which exists. |
| **Multi-tenant / per-shop vault isolation** | Felix is one box. Gates the *subscription business*, not Felix trading. |

Everything cut is (a) already parked, (b) not needed to complete a sale or maintain the catalogue, or (c) wouldn't function on Felix's actual data anyway.

---

## 7. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Restore never drilled** (backup omits logins+photos) | High it fails first run | Catastrophic — no recovery, ownership promise collapses | P0.2 + P0.3. **THE lowest-effort/highest-consequence item.** If Felix is already live, this is a *this-hour* emergency. |
| **Cost leaks to Angel's remote single-tenant server** in the endorsed loop | Certain until fixed | Two-layer model violated in production | P0.1 — strip cost at BANCO's export edge; run cleaner on-box until then. No clean cycle to remote before this. |
| **LAN/WiFi blip or box crash mid-sale = money stops** | Medium (WiFi high, box low) | Sale lost / re-rung from memory | Wired LAN + cart-preservation + paper SOP now; outbox only if data proves need. Age gate on paper is a compliance exposure — tell Felix. |
| **Print/scan physical chain never assembled** (headless box, client device, driver, pairing) | High if unaddressed | Go-live physically dies | P0.6 — assemble and prove the whole chain on real hardware, not just "print 10 labels." |
| **Label hygiene rot** — old labels not destroyed on change | High over time | The "1-in-5 wrong price" the plan claims to solve | Written destroy-old-labels rule in the SOP; audit shelf periodically. |
| **On-the-fly + cash + zero inventory = sweethearting** | Medium | Shrinkage | Manager reviews the "clean later" queue; consider a daily count of on-the-fly cash lines. Name it as loss-prevention, not a feature. |
| **Card terminal vs BANCO settlement never reconciled** | Certain if unaddressed | Daily error/shrinkage vector; accountant's first question | P0.7 — daily reconciliation line in the close SOP. |
| **Bus factor 1 at the counter AND on-call** | Ongoing | Shop down when Angel/Felix unavailable | Cashier runbook a non-Felix can follow; cold spare + restore runbook a non-Angel can execute. |
| **Accountant/Treuhänder requirements unmet** | Medium | Compliance/rework | Confirm daily Z-report + VAT export meet the Treuhänder's needs *before* go-live, not after. |
| **Effort overrun** — outbox + export refactor + enrichment + 2am on-call, concurrently, solo | High | Timeline collapse | Cut per §6. No two multi-week builds run in parallel. |

**THE SINGLE TIMELINE-KILLER:** **Felix's shelf hours.** Every slow phase (1, 3b) is throttled by *his* time to scan real EANs, print labels, validate enrichment — not by Angel's code. The sample flatters every estimate (effectively one supplier; multi-supplier reality will be worse). Any timeline assuming Angel can code past this is wrong.

**THE ONE THING THAT SLIPS EVERYTHING:** Felix going live and trading daily. Until then there's no live signal, no reference shop, no reason to build multi-tenant. The cheap catastrophe under it is the untested restore — a five-minute B2-creds fix standing in front of the entire ownership promise.

---

## 8. This week (in order)

1. **Answer Gate Zero: is Felix already trading on BANCO in production?** Write it down. If YES → the restore drill is a *this-hour emergency*; do items 2–3 today. If NO → scope the data-migration milestone before anything else.
2. **Close the cost leak (P0.1).** Strip `cost` from any packet leaving the box, or run the cleaner on-box only. Do not run one more clean cycle against the remote until done.
3. **Get the read-only B2 key and drill the restore from zero (P0.2 + P0.3)** — with the Keycloak + MinIO + off-box-secrets fixes. Budget for it to detonate. This is the highest-consequence, lowest-effort item on the board.
4. **Sit with Felix: native-review the de-CH strings (P0.5)** and **make the card-path + reconciliation call (P0.7).** Parallelizable with the restore drill — do not serialize behind it.
5. **Assemble and prove the physical print/scan chain (P0.6)** the day the Brother lands — print → rescan → right SKU on the real client device; and confirm the till preserves the cart on a failed checkout.

Items 2–5 plus the Phase-0 hygiene guards (P0.4/P0.8) and hardware (P0.9) are the go-live gate. Do **not** start the outbox, the Freehold wiring, or any enrichment until Felix is trading.