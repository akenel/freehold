# 0003 — The runbook that discarded the backups

- **Date:** 2026-08-10
- **Where:** `docs/private/GOING-LIVE.md` → `docs/private/RESTORE.md`
- **Commit:** `0d24d13`
- **Cost:** near-miss. Never invoked in anger.

## What the machine reported

Backups: green. Both Postgres databases dumped, restore-verified, shipped
off-box (`b729c11`). The disaster-recovery procedure: present, written, followed
end to end without error.

## What was actually true

The DR procedure had **no database restore step in it.** It said: restore `.env`,
launch, `make apply`, then "recreate your admin (register at `/register`)."

That was correct once — back when the Keycloak database had no backup, starting
over was genuinely the only option. Then the backups landed and the runbook was
never revisited. So the documented recovery path for a dead box was: rebuild it
empty, throw away every verified backup you were diligently shipping, and tell
the operator to start from scratch.

The backups were real. The restore was fiction. Following the procedure
correctly was the failure mode.

## How the gap surfaced

Reading the runbook against the backup system on purpose, as a task — not
because anything broke. This one was caught by looking, which is the only reason
it is a near-miss instead of an entry with a cost in it.

## The shape

**A procedure nobody has run is a rumor wearing a hat.** And: when a capability
lands, every document that predates it is now describing a system that no longer
exists. The backups did not just add a step — they invalidated the old
procedure's whole premise, silently.

## What changed

`RESTORE.md`: getting files back from B2 (including why the box key cannot list
them — write-only on purpose), restoring into a live box in the right order,
rebuilding a dead box *with* its data, a four-step verification, and a clean-room
rehearsal that can be re-run after any Postgres or Keycloak bump.

Every command in it was executed before it was written. Against a throwaway
network and Postgres: both dumps restored with `psql` exit 0; the Keycloak DB
came back with 4 realms, 5 users, 5 credentials, 6 role grants; Keycloak 26.0.8
booted on the restored schema in 3.8s with no realm import; and a **restored**
credential obtained a valid access token from the master realm.

It also names the remaining gaps rather than implying completeness — at the time
of writing, MinIO objects, the `openwebui_data` volume, and iw/wk had no backup
at all. That last admission became [0005](0005-the-backup-that-never-saw-it.md).
