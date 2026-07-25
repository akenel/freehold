# Data Migration — scoped (Felix, customer zero)

*Gate Zero answered: Felix is NOT trading yet. Today's box is pre-prod / "fake
production." So this is a **clean stand-up**, not a rescue of a live shop. That's
the good kind: no live data to save, no shop running blind, no this-hour restore
emergency. The restore drill still matters (before real go-live) but it's not on
fire.*

---

## 0. The reframe that matters most — name the chicken-and-egg

Angel wants "a preloaded clean catalogue to test with, so scanning just works."
**That catalogue does not exist yet, and the only way to make it is the exact
in-shop week Angel is about to do.** You cannot pre-load a clean catalogue of
Felix's stock *before* capturing Felix's stock — and capture *is* the shop week.

So the week in Felix's shop is not "testing a finished catalogue." It is
**building the catalogue by scanning what actually sells.** Day one is rough
(lots of create-on-the-fly). By day ten-to-fifteen the moving assortment is
captured and it starts to feel like "scan → it works." That progression *is* the
migration. There is no shortcut where a clean catalogue appears first.

---

## 1. There are THREE migrations. Only one is hard.

### Migration A — CAPTURE: Felix's reality → the catalogue  *(the hard one)*

Turn the physical shelf (the assortment that actually sells) into clean
catalogue rows. **Two ways to do it — use both:**

- **Live at the till** (the shop days): scan each item as Felix sells it. Best for
  learning his real flow and catching the true impulse-buy assortment.
- **From the daily sales list** (the smarter preload): Felix hands over his daily
  sales — today's, or a whole month of them, day by day. Angel walks the store,
  finds each sold product, and makes sure it's in the system, scanning correctly,
  priced right. This is **batch capture from the sales log**, and it's better for
  preloading because it works *retrospectively* — a month of "what actually sold"
  is exactly the moving assortment, no guessing, no waiting at the counter.

Perpetual inventory is zero, so the sales log *is* the definition of "what to
capture." Don't try to catalogue 5,000 SKUs — catalogue what the sales list says
moves.

Either way, every item resolves to one of three outcomes:

| Scan result | What it means | The one action |
|---|---|---|
| **Found** (real EAN already in system) | Working as intended | Confirm price → done. This is the "it just works" case. |
| **Real EAN, not found** | Product may exist, barcode isn't bound yet | **Bind the barcode** to the product (alias). Now it scans forever. |
| **No real EAN / unknown** | Generic glass, on-the-fly item | **Create** (name + price), **print a shelf label**, stick it on the bin. Now it scans. |

Then Angel types the **cost** for that item — by hand, shop-private, stays on
the local box, never in the shared catalogue.

- **Volume:** Felix sells ~30–50 items/day. After **~10–15 shop-days** the moving
  assortment is captured. That is the honest timeline — it is bounded by *shelf
  hours*, not by code. This is the "give me one hour and bang" wish, told the
  truth: it's ~2–3 weeks of shop time, not an hour.
- **Not a code task.** It's a disciplined data-capture process. The tooling to do
  it (scan, bind-alias, create-on-the-fly, print label) already exists in BANCO.

### Migration B — LOAD/SYNC: the catalogue → Felix's BANCO  *(the "download" model)*

This is the part Angel said he's unsure about. In lego, below (§2). Mechanically:
the owned catalogue is exported as the **packet** and imported into the shop's
local BANCO, matched on **SKU**, **cost and retail price left untouched**. Same
contract we designed, running *downhill* (Angel → Felix) instead of *uphill*
(worklist → cleaner).

**For customer zero this is nearly trivial**, because Angel is *also* the one
capturing Felix's assortment — so "the master catalogue" and "Felix's local data"
are the same thing right now. The download/sync model only starts to matter when
there is a **second shop** pulling from Angel's master. Build it then, not now.

### Migration C — DEPLOY: pre-prod → real production  *(a clean stand-up, not a copy)*

Real production = a separate server + a separate domain (e.g. `luzern.app`),
**same code**. The mistake to avoid: do **not** copy the messy pre-prod database
into prod. Today's box is "pre-prod" — the real working system, but with junk and
experiments in it. It's where Angel *builds* the catalogue over the three weeks.
That catalogue becomes the **source of truth**. The junk does not travel.

Instead, stand prod up **clean**:
1. Fresh box, fresh strong secrets (exactly like the wolfhold prod cutover).
2. Load the **one real thing**: the captured, clean catalogue (via the packet) —
   exported out of pre-prod, imported into the new prod box.
3. Create Felix's real staff accounts.
4. Point the real domain (`luzern.app` or similar) at it.

The catalogue is the *only* data that crosses from pre-prod to prod, and it
crosses through the same packet export/import. Everything else starts fresh. So
the three weeks of capture on pre-prod aren't throwaway — that clean catalogue is
the seed the real production system is stood up around.

---

## 2. "Download it to him and his system runs independent" — in lego

Angel: *"I don't think he connects to a catalogue anymore… his system should
work independent of the catalogue. Not really sure how that works."*

Here it is:

> **The catalogue is a master recipe book that Angel keeps.**
> **Felix's till gets a COPY downloaded into its own local kitchen.**
> Once the copy is on Felix's box, **he cooks from his own copy** — he does not
> phone Angel's kitchen for every order. That's why the till runs independent:
> it owns a full local copy of everything it needs to sell.

- **Between updates:** Felix's BANCO is 100% standalone. Server down, internet
  down, Angel on a plane — the till still sells, because the products live in its
  own local database.
- **Updates:** when Angel improves the master (new products, better categories,
  photos, real-EAN bindings), he pushes a **new copy down** — like a software
  update. Felix's system merges it in and keeps running.
- **The sacred rule at the sync line:** the download carries **public** catalogue
  data (names, categories, photos, descriptions, barcode bindings). It **never**
  carries or overwrites Felix's **private cost** or **his chosen retail price**.
  Public flows down; private stays put. That's the two-layer model, enforced
  exactly at the download boundary.

So "he doesn't connect to the catalogue anymore" is right: the catalogue is a
*source that syncs down*, not a *service the till calls*. Copy, don't phone.

---

## 3. The capture playbook (Angel's shop day)

Print this. For every item Felix sells, in order:

1. **Scan the real pack barcode.**
2. **Found?** → glance at the photo on the line ("yes, that one") → confirm price
   → sold. (Cigarettes, papers, lighters, branded consumables live here.)
3. **Not found but it has a real barcode?** → **bind** the barcode to the right
   product. If the product doesn't exist yet, create it first, then bind.
4. **No barcode / generic glass?** → **create** (name + price) → **print a shelf
   label** → stick it on the bin/shelf so it scans next time.
5. **Type the cost** (private, local).
6. **Move on** — never hold the queue. Anything unfinished goes to the tidy-later
   worklist.

**Hygiene rule (this is the real "scan works" secret):** one item → one
scannable code → one product. When a code changes (placeholder → real EAN, or a
variant re-bin), **hunt down and destroy the old label.** Two labels for one item
is exactly the "1-in-5 wrong / wrong price" failure.

---

## 4. What "it comes up with stupid stuff" actually is

When a scan "doesn't know what it is," it's almost always one of:
- the real EAN isn't **bound** yet (fix: bind it once, done forever), or
- a **no-barcode** item with no shelf label (fix: print + stick), or
- a wrong/duplicate binding from before (fix: the hygiene rule).

The **scanning itself is deterministic and reliable** once the binding exists —
it's a lookup, not a guess. The part that "guesses" is the AI *category/desc
suggestion* on an unknown item, and that's fine, because a human confirms it.
Don't confuse "the scanner is unreliable" (it isn't) with "this item was never
captured yet" (that's the work).

---

## 5. Keep it in the sandbox until the gate is green

Agreed and correct: do the whole capture week on the pre-prod / sandbox box.
Nothing needs to touch a real prod server until the catalogue of Felix's moving
assortment is captured, clean, and the Phase-0 go-live gates (drilled restore,
closed cost leak, proven print/scan chain, card reconciliation) are met. Then —
and only then — stand up the clean prod box and load the catalogue into it.

**Order:** capture (sandbox) → clean → gates green → stand up clean prod → load
catalogue → Felix trades. The kiosk, the multi-shop download model, and Freehold
wiring all come after Felix is trading.
