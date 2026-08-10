# Human-Green

> **Tests passing ≠ done.** — CLAUDE.md, rule 4

This directory is a running record of the times something was **machine-green
and still wrong**: the tests passed, the deploy reported success, the backup ran
clean, the config validated — and the thing was broken anyway.

It exists for two reasons.

1. **It stops repeats.** Two of the incidents below are the same mistake made
   twice, five weeks apart. Writing the first one down properly would have cost
   ten minutes and saved a prod outage.
2. **It is raw material.** These notes are the spine of a book. Each one is a
   chapter in miniature. That is a byproduct, not the point — capture takes ten
   minutes, writing a book does not. Do the capture; the book can wait until
   there is a stack of these worth binding.

## The rule for what belongs here

An entry qualifies when **a machine reported success against the spec it was
given, and the spec was the bug.** Not "I wrote a bug and the tests caught it" —
that is Tuesday. This is for the gap between *green* and *correct*.

Some shapes that keep recurring:

- The check measured the wrong thing (archive size, not archive contents).
- The check ran against the wrong target (stock Caddy, not the built image).
- The scope was silently narrower than the name implied (`backup.py` backed up
  databases; the conversations were in a volume).
- The document described a system nobody runs.
- The retry loop treated a systematic failure as a transient one.

## Where entries live

**Next to the work.** An incident goes in the repo where it happened:

- Infra, ops, Freehold/Wolfhold platform → **this directory**
- Helix POS, Felix, catalogue, anything customer-zero → **`banco-starter`**,
  under the same `docs/human-green/` path

This has been the standing rule for Felix/POS artifacts and it applies here too.
Capture only survives if it sits where you already are when the thing stings. A
central book repo would mean a context switch at exactly the wrong moment, and
the note would never get written.

Assembling a manuscript is a later job for a later repo. Do not pre-build it.

## How to write one

Copy `_TEMPLATE.md` to the next number. Write it **while it still stings** —
same day, ideally same hour. Two hundred words is plenty; a thousand is a sign
you are drafting the chapter instead of capturing the incident.

Two things matter more than polish:

- **What the machine actually reported.** Quote it. The exact misleading string
  is the most valuable line in the note, and it is the first thing you forget.
- **The general shape.** One sentence, stated so it would apply to a system you
  have not built yet. This is the part that becomes a chapter.

If a commit message already did the work — several below did — the note can be a
short frame plus a pointer. Do not retype the commit.

## Index

| # | Date | Incident | The shape |
|---|------|----------|-----------|
| [0001](0001-the-empty-domain.md) | 2026-07-06 | A set-but-empty env var crash-looped Caddy and took prod down | Unset and empty are not the same value |
| [0002](0002-the-front-door.md) | 2026-08-09 | `deploy.py` recreated Caddy without the prod overlay; app, auth and AI all went dark | The health probe was checking a URL with no front door behind it |
| [0003](0003-the-runbook-that-discarded-the-backups.md) | 2026-08-10 | The disaster-recovery procedure had no restore step — it rebuilt an empty box | A procedure nobody has run is a rumor wearing a hat |
| [0004](0004-a-stack-we-do-not-run.md) | 2026-08-10 | Public claims described a self-hosted AI stack that exists nowhere in the repo | Documentation is green until someone greps it |
| [0005](0005-the-backup-that-never-saw-it.md) | 2026-08-10 | Backups ran clean for weeks; every AI conversation was outside their scope | A backup's name is not its scope |
| [0006](0006-the-gigabyte-in-front.md) | 2026-08-10 | A 1 GB replaceable archive blocked the 5 MB irreplaceable one and ate the storage cap | Fail-fast on a list of independent items is fail-most |
| [0007](0007-thirty-copies.md) | 2026-08-10 | One failing upload stored thirty copies of the same 1 GB archive | Retrying a systematic failure cannot help; it can only cost money |
