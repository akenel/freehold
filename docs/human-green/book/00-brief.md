# The book — brief

Settled 2026-08-10. Read this before writing any chapter. If a draft argues with
this file, the draft is wrong.

## Working title

**Human-Green** — from CLAUDE.md rule 4: *tests passing ≠ done.*

## The sentence the whole book sits under

> *"I just want to scan stuff and know what I sold. Today it's paper and pen."*
>
> — Felix, the customer, asked what he wanted

No stack. No sovereignty. No cloud. He isn't asking to own anything — he wants to
point a scanner at a jar and know what left the shop.

Every chapter answers to that. If a page defends an architecture that doesn't help
a man scan a jar, cut the page. The book earns its technical material only by
showing what "just scan stuff" actually costs.

## Who it's for

**One reader: a solo developer shipping real software to a real paying customer.**

He has one box. One customer who loses money when it stops. Nobody to call at
3am. He is doing ops, support, sales and the actual code, and he is doing them
after the customer's working day ends.

Everyone else is secondary and gets no accommodations:

- **Felix and shop owners like him** are *characters in the book*, not readers.
  This matters — it means the technical chapters never get softened for a
  non-technical audience, and the customer's stakes stay real instead of
  hypothetical.
- **Buyers evaluating Helix or Freehold** may read it. Good. They should find a
  book that wasn't written for them.

Write every page as though that one developer is reading it at 23:00, tired,
because something is broken.

## What it's for

**One objective: a teaching gift.** `FREEHOLD-SPEC.md` phase 6 — *the why,
Lego-clear.* Settled 2026-08-10. Nothing else gets to win an argument with it.

What that decision costs, stated so it stays honest:

- **Nothing gets sanded smooth.** The failures stay ugly, because ugly is what
  teaches. If a chapter starts making us look competent, it has stopped working.
- **Length is whatever the lesson needs.** No word target to hit or pad.
- **No launch, no cover, no deadline.** Chapters publish as they're finished.
- **It's free.**

Three other things may happen. None of them are objectives, and none of them
change a sentence:

- **Credibility** — a side effect of doing the above honestly. Never write *for*
  it. Writing for credibility is how the failures get sanded down.
- **Money** — if it's ever worth selling, that's a packaging decision made after
  the eight chapters exist. Not before, and never a reason to finish faster.
- **Interest in Helix / Freehold** — arrives sideways, from people who like how
  you work. It does **not** arrive by pitching shop owners.

**The standing risk:** drifting toward Felix as the reader in order to sell
something. That produces a book for nobody. The tell is a chapter that starts
explaining what Postgres is. Shop-owner material is a separate short PDF, later.

## Voice — Lego-clear

The register is set by the spec's own phrase. Checkable rules, not vibes:

- **Second person.** The reader has a box and a customer. "You," never "one."
- **No abstract noun as the subject of a sentence.** Not "the substitution of a
  legible dependency for an illegible one" — "you swap a risk you can't check for
  one you can."
- **Every claim carries a number, a command, or a file path** where one exists.
  `97.8%`. `--retries 2`. `ops/backup-volumes.py`. Vague is a smell.
- **Define the term in the sentence that first uses it**, the way you'd say it
  out loud. "RTO — how fast you're trading again after the box dies."
- **Say it to a friend in a bar first.** If it would sound strange there, rewrite.
- **Short sentences.** Break anything over ~25 words unless the length is doing
  real work.
- **Banned phrases:** "It is tempting to", "It is worth noting", "Here is the
  part that", "genuinely", "precisely", "the whole point is". They are padding
  that sounds like thinking.

Plain does not mean shallow. The technical detail stays — WAL files, compose
overlays, retry multipliers. It gets explained in plain words, not removed.

## The spine

Each chapter is one thing that was **machine-green and wrong**, from
`docs/human-green/`, plus what it taught.

1. **Owe no one** — why own the box; what ownership actually costs; you own what
   you can restore
2. **The crew of two** — how a human and a machine work a codebase together
3. **The lying backup** — [0005](../0005-the-backup-that-never-saw-it.md)
4. **Thirty copies** — [0007](../0007-thirty-copies.md)
5. **The empty domain** / **the front door** — [0001](../0001-the-empty-domain.md),
   [0002](../0002-the-front-door.md); the same mistake twice, five weeks apart
6. **Secrets you can't paste** — SOPS + age; making the safe path the easy path
7. **Customer zero** — Felix, the catalogue, what a real user does to your
   assumptions
8. **Human-green** — the discipline, stated plainly, earned by chapters 3–7

Target: 25–35k words. Ships as PDF/EPUB with a real cover.

## Not decided yet

- Whether chapter 1 names the real dates (three of the seven incidents landed on
  2026-08-10, which reads as invented) or keeps the timeline vague until the
  chapters that own those incidents.
- Whether the book is published before or after Felix trades. Trading changes
  chapter 7 from a plan into a result.
