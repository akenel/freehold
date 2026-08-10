# 0005 — The backup that never saw it

- **Date:** 2026-08-10
- **Where:** `ops/backup.py` → new `ops/backup-volumes.py`
- **Commit:** `4eb4f36`
- **Cost:** near-miss. Weeks of live AI conversations with zero copies anywhere.

## What the machine reported

`ops/backup.py`: green. Running nightly, dumping both Postgres databases,
restore-verified, shipping off-box. Every run succeeded. Nothing was ever red.

## What was actually true

`backup.py` backs up **databases**. `openwebui_data` is a Docker **volume**, so
`pg_dump` never saw it and never could. That volume holds every conversation
anyone has had with ai.wolfhold.app, plus per-user settings and uploads.

On a box whose entire pitch is data sovereignty, the most personal data on it was
the one thing with no backup at all. The backup system was working perfectly
within a scope that simply did not include it.

## How the gap surfaced

Fell out of [0004](0004-a-stack-we-do-not-run.md) — checking the AI residency
claims meant reading the compose file, which meant seeing the volume, which
raised the question nobody had asked: *is that in the backups?* It was not.

Found sideways, while looking at something else. There was no process that would
have found it.

## The shape

**A backup's name is not its scope.** "Backups are green" answers a question
about the job, not about the data — and the gap between them is invisible from
the job's side, because a backup that has never heard of your data cannot report
it missing. The only reliable question is the inverse one: *name every store on
this box, and for each, point at the artifact that would bring it back.*

## What changed

`ops/backup-volumes.py`: tar → encrypt → **open the archive and check the thing
you actually need is inside** → ship to `b2:<bucket>/<env>/volumes`.

Design decisions worth keeping:

- **Streamed** (`tar | openssl | file`), never buffered. The box has 4 GB and
  these archives run to hundreds of MB; nothing plaintext touches disk.
- **Pauses the container while reading** (`docker pause` = SIGSTOP; connections
  survive, resumes in ms). Without it you can tar a half-written SQLite page and
  get an archive that unpacks perfectly around a corrupt database.
- **Not part of the deploy gate**, deliberately — tarring hundreds of MB on every
  promote would make deploys slow and B2 expensive. Cron instead.
- **The drill checks content, not size.** An early version rejected a valid
  archive because gzip had squeezed it under a byte threshold. *The size of
  ciphertext says nothing about whether a backup is real* — that is this file's
  thesis in one line, and it had to be learned inside the fix for it.

Verified, not assumed: 200 conversations seeded, backed up, volume emptied to
zero entries, restored with the documented command, all 200 rows back with
correct content. Each guard tested individually — a 61 KB archive that looked
entirely healthy but carried a corrupt `webui.db` was refused, as was one missing
`webui.db`, as was a volume that does not exist on the host.
