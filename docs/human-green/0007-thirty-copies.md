# 0007 — Thirty copies

- **Date:** 2026-08-10
- **Where:** `ops/backup-volumes.py`, `ops/backup.py`
- **Commit:** `54eeb50`
- **Cost:** 30.7 GB into B2 from a single run; a 10 GB free tier exhausted

## What the machine reported

A backup run that failed. Correctly, and with a real error.

## What was actually true

The bucket held **thirty versions of the same
`openwebui_data-20260810T105743Z` archive**, all uploaded within six minutes.
One nightly run, one gigabyte, thirty copies, and B2 keeps a version of every
one.

Mechanism: the write-only B2 key makes rclone's post-upload read-back HEAD return
401, so rclone treats a copy that **actually succeeded** as failed, and retries.
Default is 3 attempts × 10 low-level retries = 30 full uploads. Each one worked.
Each one was recorded as a failure. Each one was retried.

The 401 itself was already fixed by then (`--multi-thread-streams 0`, see
[0006](0006-the-gigabyte-in-front.md)) and cold no longer ships — but the
underlying exposure was unbounded. Any systematic failure — a bad key, wrong
permissions, a cap — could burn storage without limit while never being able to
succeed. And the nightly run tries again tomorrow.

## How the gap surfaced

The storage cap. A bill, effectively — the crudest possible detector, and the one
that fires after the money is spent rather than before.

## The shape

**Retrying a systematic failure cannot help; it can only cost money.** A retry
loop is a bet that the failure is transient. Nothing in a default retry
configuration ever checks whether that bet is sound, so the same code that
rescues a flaky network amplifies a misconfiguration into a bill.

Sharper version: **the retry count is the multiplier on your worst case, and
almost nobody has looked at what it multiplies.** 3 × 10 reads like defensive
defaults. Against a 1 GB object and a permanent error it is a 30 GB write
amplifier.

Third: the error was *wrong about itself*. Uploads that succeeded were reported
as failures. When a system misreports success as failure, retry logic converts
the misreport into cost — the inverse of the usual machine-green problem, and it
bites harder.

## What changed

`--retries 2 --low-level-retries 2` in **both** `backup.py` and
`backup-volumes.py`. Worst case drops from 30 full uploads to 4.

The DB dumps are small and were never going to blow a cap — but the shape of the
bug was identical there and it had no cap either. Fixing only the instance that
hurt would have left the same unbounded loop sitting in the other file, waiting
for the day the dumps get big.
