# WORKLIST — Freehold
<!-- Ordered by priority. Top = next. Cross off when done. -->

## ▶️ ON DECK — Wednesday 2026-08-12

*Set 2026-08-11, late. Work now spans three repos; this is the one list. Start at
the top and don't let items 2–4 push item 1 down the page — item 1 is the only
one with a paying customer at the end of it.*

- [ ] **1 · SEE FELIX. This week, and it's the whole week's job.**
      Gate Zero is answered — he's on paper, not on BANCO
      (`banco-starter/WORKLIST.md`). What's unanswered is whether he's serious:
      a deadline, what "acceptable to go live" means to him, and whether money
      changes hands. Take the two questions from `PARALLEL-RUN.md` with you —
      *turnover or profit?* and *is a 30% catalogue a win or a fail?* Five
      minutes, and between them they halve or double the project.
      ⚠️ Before any shadow day: prod authenticates against the **DEMO realm**,
      whose passwords are in a public repo. Close that or shadow locally.
      **"He's slow" and "I didn't ask" look identical from here.**

- [ ] **2 · Chapter 2 needs your half.** ~20 minutes in Longhand
      (<http://127.0.0.1:1984>, `docker compose up -d` in `~/repos/longhand`).
      The draft has my three failures because I have the transcript. It has
      nothing of yours: what it's like when it confidently does the wrong thing,
      whether ON DECK survives a bad week, what you stopped doing yourself and
      whether you regret it. Also: clear your note on line 156, it's answered.

- [ ] **3 · Write `longhand/docs/human-green/0001` YOURSELF.**
      Three defects on 2026-08-11, all reporting success while broken: settings
      mounted read-only so no setting could be changed; `--bind-addr` dropped so
      it listened on the container's own loopback while logging "HTTP server
      listening"; a root-owned volume that killed it on EACCES *after* a clean
      start. Template: `freehold/docs/human-green/_TEMPLATE.md`.
      **This one is the habit test.** If the notes only get written when the
      machine writes them, it's an archive, not a practice — and the book runs
      out of material at chapter 3.

- [ ] **4 · Unblock prod deploys for zero francs.** Make the off-box backup
      target pluggable — any rclone remote counts (laptop over Tailscale sftp),
      not hard-wired to B2. Currently `promote.py` gates on `backup.py` reaching
      B2, and B2 is capped until ~24 Aug, so nothing can ship to prod. Already
      scoped in the BLOCKED section below, in your own words. An afternoon.

- [ ] **5 · Decide the openwebui transcript.** It's in UNDECIDED below and has
      been for days: committed to a public repo, carries bKf's messages, two
      mentions of your wife, and pricing strategy. You already recommended
      `git rm --cached` + gitignore. Ten minutes. Undecided items about public
      exposure don't age — they just stop being visible to you.

*Longhand's own next step (after 1–3): `references.md` for chapter 2, and decide
whether the check runs on demand or continuously. On demand first — continuous
gets expensive fast.*

---

- [x] 1. Read deps.py, models.py, main.py, audit.py, build_info.py to understand Freehold's patterns
- [x] 2. Create a HealthCheck model in models.py (service, status, checked_at, detail)
- [x] 3. Create routers/health.py with a /status page that checks Postgres, Keycloak, MinIO, and app build SHA
- [x] 4. Register the health router in main.py
- [x] 5. Create a templates/status.html page showing service health with green/red indicators
- [x] 6. Write tests for the health endpoint in tests/test_health.py
- [x] 7. Run the full test suite to prove nothing broke
- [x] 8. Git commit with a meaningful message

## ON DECK — next session
- [ ] 1. `python3 ops/promote.py production` — ships migration 0006 so /status actually records (prod is on 0005)
- [ ] 2. Rehearse the restore with a REAL prod dump pulled from B2 (docs/private/RESTORE.md, "Rehearsing without touching production"). Mine used local data; this proves prod's users come back. Touches nothing live.
- [x] 3. ~~Back up openwebui_data (AI chat history)~~ — done: `ops/backup-volumes.py`, round-trip verified
- [ ] 4. Decide on MinIO: `python3 ops/backup-volumes.py miniodata` works today, but check the volume size first (B2 charges by GB) before adding it to the nightly timer
- [ ] 5. Put backup-volumes.py on a cron timer on the box (see docs/private/RESTORE.md) — cheap now: nightly hot is ~1.4% of the volume
- [ ] 6. Re-run `python3 ops/backup-volumes.py --cold` once on the box to ship the 1 GB baseline off-box (the 2026-08-10 attempt failed on the write-only-key 401, now fixed)

## BLOCKED — B2 out of space (2026-08-10)
Bucket is 30.7 GB / 10 GB free tier: 30 versions of one 1 GB cold archive, from
rclone retrying a copy that had actually succeeded (401 on the write-only key's
read-back). Object Lock 14d means they can't be deleted yet. No credit card on the
account, so the cap can't be raised.

- [ ] **~24 Aug**: delete the 30 versions in `production/volumes/`, wait <24h for
      usage to recalculate. B2 free again. Deleting never needs a card.
- [ ] Set a B2 lifecycle rule: keep current version, drop previous after 1 day
- [ ] Until then, prod deploys are BLOCKED — promote.py gates on backup.py
      reaching B2. Fix = make the off-box target pluggable (any rclone remote
      counts, e.g. the laptop over Tailscale sftp), not hard-wired to B2.
- [ ] Optional tonight, real off-box copy, run ON THE LAPTOP:
      `rsync -av root@100.122.129.118:/root/freehold/backups/ ~/freehold-offbox/`

Already fixed today: retry caps in both backup scripts, so this can't recur.

## UNDECIDED
- [ ] `docs/private/openwebui-AI-wolfhold-app.md` — I committed this previously
      untracked chat transcript to the PUBLIC repo. No secrets, but it has bKf's
      messages, two mentions of Angel's wife, and pricing strategy. Options: leave
      it / `git rm --cached` + gitignore / rewrite history. Recommend the middle
      one, keeping the accuracy note as its own doc.
