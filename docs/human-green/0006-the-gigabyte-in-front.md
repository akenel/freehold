# 0006 — The gigabyte in front

- **Date:** 2026-08-10
- **Where:** `ops/backup-volumes.py`
- **Commits:** `48fe579`, `8f6e0eb`
- **Cost:** 2.4 minutes of frozen AI chat per nightly run; the entire Backblaze
  free tier; and one run where the irreplaceable archive was never attempted

## What the machine reported

The first prod run of the brand-new, carefully verified backup from
[0005](0005-the-backup-that-never-saw-it.md) did exactly what it was told. It
archived 1.02 GB, paused the container for the 2.4 minutes that took, uploaded,
and reported failure on the upload — `403 storage_cap_exceeded`, after an earlier
run had failed with `Unknown 401`.

Every one of those was the correct behaviour for the spec it had been given.

## What was actually true

Three separate things, all downstream of one wrong assumption — that the volume
is a single undifferentiated blob.

**The pause was protecting the wrong data.** Of that gigabyte, the conversations
— `webui.db`, the part that is actually yours — are a few MB. The rest is an
embedding-model cache. Nightly, that was 2.4 minutes of frozen chat spent
backing up something HuggingFace will hand back to anyone. It could not simply be
dropped either: `OFFLINE_MODE=true` stops Open WebUI re-downloading models, so a
restore without the cache comes back broken.

**The cap was spent on the replaceable half.** 1 GB of public model weights
exhausted the free tier. The data that is genuinely irreplaceable compresses to
5.1 MB.

**And the big disposable archive blocked the small irreplaceable one.** `ship()`
aborted on the first failure. In that run the 5 MB hot archive was *never even
attempted*, because the 1 GB cold one failed ahead of it in the list.

## How the gap surfaced

Running it in prod for the first time and reading what actually happened, rather
than trusting a suite that had passed on a 3 MB test volume. Scale was the
variable the tests did not have.

## The shape

**Fail-fast on a list of independent items is fail-most.** Sequential-abort is
right for dependent steps and actively harmful for independent ones — and the
ordering that decides what gets sacrificed is usually accidental.

Second shape: **cost and risk are not correlated with size, and systems default
to treating them as if they were.** The expensive thing to protect was the cheap
thing to lose.

## What changed

- Volumes split **cold** (big, static — archived once as a baseline, re-made only
  with `--cold`) and **hot** (`webui.db`, uploads, `vector_db` — every run).
  Measured on the test volume: cold 3.0 MB, hot 41 KB. The nightly archive is
  1.4% of the whole and the pause is a blink.
- **Anything not named cold is hot**, so a new top-level directory appearing
  after an Open WebUI upgrade lands in the nightly backup by default. Silently
  excluding unknown new data is precisely the failure this script exists to
  prevent — the [0005](0005-the-backup-that-never-saw-it.md) shape, designed out.
- Cold is now made, drill-verified and **kept on the box**, not shipped;
  `--ship-cold` overrides. Off-box footprint for 30 days of everything, both
  databases included, drops from ~30 GB to ~170 MB. `RESTORE.md` documents the
  one extra recovery step: restore hot, set `OFFLINE_MODE=false` for one boot to
  refetch the models, set it back.
- `ship()` now attempts **every** file and reports all failures. An earlier draft
  of the summary printed "the rest DID ship" even when nothing had — a green
  message inside the fix for a green-message bug.
- The 401: rclone's multi-thread path verifies with a read-back HEAD after
  upload, and the box's B2 key is deliberately write-only, so B2 refuses. Small
  DB dumps never reach that path, which is why `backup.py` was unaffected.
  `--multi-thread-streams 0` is now passed always — required, not tuning.
- `--inspect` added (what is in a volume, how big, changes nothing) so the cold
  set is chosen from measurement instead of assumption.

Also found by `--inspect` on prod: hot carries `webui.db-wal` (8.3 MB) and `-shm`
alongside `webui.db`. SQLite keeps recent transactions in the WAL until
checkpoint, so **backing up `webui.db` alone opens fine and silently loses the
newest conversations** — a perfect miniature of this whole directory. The
include-everything-not-cold design picks them up without being told.
