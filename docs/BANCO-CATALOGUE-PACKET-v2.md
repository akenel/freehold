# BANCO Catalogue Packet — v2 spec

*The work packet BANCO exports, the Business Hub cleans, and BANCO re-imports.
This is the contract between the two. v1 was one Worklist tab; v2 adds the
reference tabs that give the AI ground truth to reason from, and separates what
is **universal** (the shared catalogue) from what is **shop-private** (cost).*

---

## 0. The one idea that makes the rest make sense: two layers

A head-shop catalogue is really **two databases wearing one coat**, and mixing
them is what makes the cost question feel confusing.

**Layer 1 — the universal catalogue (public product truth).**
What a product *is*: EAN, names in four languages, brand, category, description,
images, dimensions, which suppliers carry it and at what *advertised* price. This
is the same for every head shop in Switzerland. **Angel owns and maintains this.**
It is the moat: the software is free, the hardware they buy, but nobody else has a
clean, four-language, credited head-shop catalogue. This layer has **no cost in
it, ever** — there is nothing shop-specific to hide, which is exactly why it can
be shared across every shop.

**Layer 2 — the shop overlay (private economics).**
What a product costs *this shop*, what *this shop* sells it for, how many are on
the shelf. Cost is a secret the shop negotiated with a wholesaler; it lives in
that shop's own BANCO instance and **never leaves it**. The catalogue tells the
shop *what the thing is*; the shop adds *what it costs them and what they charge*.

So the answer to "how do we work the cost?": **you don't.** The cleaner fills the
universal layer and never touches cost. Each shop fills cost once, itself, in its
own system. Retail price is the shop's call too — but the catalogue can *suggest*
a range from the suppliers' public prices, which is where "find the best deal"
comes from.

> Rule of thumb for every column below: **if it would be true in any head shop in
> Switzerland, it belongs in the universal catalogue. If it's this shop's secret,
> it stays in the shop.** Cost is always the second kind.

---

## 1. The spine: EAN

Everything joins on the **EAN barcode**. 90% of head-shop stock carries a number
somewhere — on the product, the box, the delivery slip, the invoice. EAN is how
the cleaner matches a row to a supplier's product page, to another supplier
selling the same thing, and to the same product in another shop. Match on EAN
first; fall back to name only when there's no number.

`sku` is the shop's *internal* id and is sacred on re-import — the cleaner never
touches it — but it is not the cross-shop key. EAN is.

---

## 2. The packet — tabs

| Tab | Role | Who writes it |
|---|---|---|
| **START HERE** | Human instructions (unchanged from v1) | BANCO |
| **Worklist** | The items to clean — the data | BANCO out, cleaner back |
| **Suppliers** | name → website, URL pattern, what they carry | **Angel (build first)** |
| **Taxonomy** | the 52 categories, each with a one-line meaning | BANCO (from Lists) |
| **Glossary** | domain terms: `NS = Normschliff → bong joint` | **Angel (build first)** |
| **Brands** | brand → typical category — *derived, optional* | cleaner (auto) |
| **Languages** | the 4 targets + a term glossary for consistent translation | Angel |
| **Examples** | ~20 gold `ean → category` rows, for few-shot | Angel |
| **Summary** | live readiness dashboard (unchanged) | cleaner recomputes |

The two tabs marked **build first** are the whole point of v2: the `Suppliers`
tab is what enables sourcing + (eventually) scraping, and the `Glossary` tab is
what fixes the confident category misses (the `NS 19/19 → Vape Accessories`
mistake dies the moment the AI can read that `NS` is a bong joint).

---

## 3. Worklist columns

`layer`: **U** = universal catalogue · **S** = shop-private · **K** = key.
`fill`: who is expected to provide it.

| Column | layer | fill | Meaning |
|---|---|---|---|
| `ean` | K | till/BANCO | the barcode. The spine. Never invented. |
| `sku` | K/S | BANCO | shop's internal id. Sacred on re-import — cleaner never edits. |
| `name_de` / `name_fr` / `name_it` / `name_en` | U | cleaner | the product name in each Swiss language. |
| `name_source_lang` | U | cleaner | which language the till operator typed, detected. |
| `brand` | U | cleaner | brand, from the name or the Brands tab. |
| `category` | U | cleaner | one of the 52. `Unsorted` if the AI isn't sure. |
| `description_de/fr/it/en` | U | cleaner | truthful description — only what's derivable or sourced. |
| `image_1`…`image_n` | U | cleaner | image URL(s). Multiple allowed. Each carries its credit (below). |
| `size_variant`, `unit` | U | cleaner/till | 180mm, 5-pack, etc. |
| `suppliers` | U | cleaner | list of `{supplier, url, public_price_chf, scanned_at}` — who sells it and for how much *advertised*. |
| `retail_price_chf` | S | shop | what THIS shop charges. Catalogue may suggest a range; shop decides. |
| `cost_chf` | **S** | **shop only** | **secret. Blank in the universal catalogue. Cleaner never fills it.** |
| `status` / `action` | — | cleaner | workflow: `ENRICH` still needs work, `DONE` ready, `SKIP`, `DELETE`. Cleaner sets these to drive the Summary. |
| `notes` | — | either | free text. |

Every **U** field the cleaner writes carries provenance (next section). Every
**S** field the cleaner leaves exactly as it found it.

---

## 4. Provenance & credit — on every enriched field

This is what makes taking a supplier's image or description *safe*: it's not
copied, it's **cited**. Each universal field the cleaner writes gets:

```
{ value, source, source_url, scanned_at, confidence, gate }
```

- `source`: `till` | `rule` | `model` | `supplier`
- `source_url`: e.g. `https://tam-shop.ch/product/25644` — shown on the product
  page as "info from … , fetched 2026-07-25".
- `scanned_at`: when it was pulled, so a stale price is visible as stale.
- `gate`: `auto` (clear) / `review` (a human confirms) / `rejected`.

**Scraped values are always `review`, never `auto`.** A wrong price pulled from
the web is worse than a blank one, so a human always confirms a sourced value
before it becomes catalogue truth.

---

## 5. Suppliers tab — the priority build

Columns:

| Column | Meaning |
|---|---|
| `supplier` | name (4:20, Tamer/TAM, NearDark, …) |
| `website` | their site |
| `product_url_pattern` | how to build a product page from an EAN or SKU, e.g. `https://tam-shop.ch/?ean={ean}` — blank if unknown (then search by name) |
| `carries` | domain hint: "bong glassware, shisha", used as a category prior |
| `notes` | tier pricing quirks, languages, etc. |

Start with the four you have (4:20, TAM/Tamer, NearDark, +one). Fill website +
what they carry. That alone raises category accuracy (supplier → category prior)
*before any scraping*. Scraping is a later tier that reads `product_url_pattern`.

---

## 6. Glossary tab — the accuracy fix

Two columns: `term`, `means`. Seed it with the abbreviations that tripped the AI:

```
NS            Normschliff — ground-glass joint; a bong/pipe part
Steckkopf     bong bowl / slide
DripTip       vape mouthpiece part
Wickeldraht   coil wire (vape)
Schleuder…    spinning ashtray
Kokoskohle    coconut charcoal (shisha coal)
```

The AI reads this before classifying, so `Adapter NS 19/19` stops becoming a Vape
Accessory. This tab is small, it's pure head-shop domain knowledge, and it *is*
the moat — a generic tool will never have it.

---

## 7. What the cleaner does — and refuses

**Does (universal layer only):**
- sort `Unsorted` → category from the 52, using name + brand + Suppliers +
  Glossary; low confidence → stays `Unsorted`, gated.
- normalize + translate the name into all four Swiss languages.
- draft a **truthful** description from name/brand/category (or a sourced one from
  a supplier page), gated to review, marked AI-drafted.
- record which suppliers carry the EAN and their **public** prices (comparison).
- pull images with credit (later tier).
- flag every missing field; set `action` = `DONE` / `ENRICH`; recompute Summary.

**Refuses, always:**
- inventing a `cost` — it's shop-private and secret; the cleaner never writes it.
- inventing a spec, a price, or a fact not derivable or sourced.
- touching `sku` or any **S** field.
- auto-applying anything scraped — sourced values are `review`.

---

## 8. Re-import

The file goes back as the **same tabs**. The Worklist comes back with the
universal fields filled and provenance recorded, `sku` untouched, `cost` exactly
as it left (blank/unchanged), `action`/`status`/Summary updated. BANCO matches on
`sku` and imports. A separate "provenance" export (source_url + scanned_at per
field) can ride along for the product-page credits without cluttering the import.

---

## 9. Build order

1. **Suppliers tab** (4 you have) + **Glossary tab** (seed above). Hand-authored,
   small, highest leverage. No code.
2. Re-run the sample worklist with those two tabs as context → measure the
   category-accuracy jump.
3. **Languages / translation** enrichment (the four-language sanitising).
4. **Tier-1 scrape** of one supplier by EAN → sourced image/description/price,
   gated. Prove it before building per-supplier adapters.
5. Everything else (kiosk, multi-image product page, alternative-supplier
   comparison) reads from this same clean catalogue.
