# WORKLIST — Freehold Health Dashboard
<!-- Ordered by priority. Top = next. Cross off when done. -->

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
