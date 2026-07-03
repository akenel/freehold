# ops — the rails

The part most starter kits skip. Three small Python scripts (stdlib only — they
run on any host with `python3`, `docker`, and `openssl`, no pip installs) that
turn "it runs" into "it runs safely, and I can prove what's running."

## `deploy.py` — the ladder
```
python3 ops/deploy.py sandbox            # or: make deploy ENV=sandbox
python3 ops/deploy.py production [ref]
```
1. **Stamps the build** — writes `app/build-sha.txt` (sha · date · commit count); the
   app serves it at `/version`, so the build bar can never lie.
2. **Backup gates production** — deploying `production` runs `backup.py` first and
   **aborts if it fails**. No backup, no deploy.
3. **Rebuild + restart**, then **waits for health**.
4. **Proves it** — re-probes `/version` and checks the SHA now serving equals the SHA
   it stamped. The healthcheck greens a beat before the first request serves, so a
   "before" snapshot can masquerade as "after." We check *after*. Prove, don't assume.

## `backup.py` — the safety net
```
python3 ops/backup.py                     # or: make backup
```
Dumps Postgres → encrypts (openssl AES-256) → **restores it into a throwaway database
to prove it actually restores.** Exits non-zero if the drill fails — which is what lets
`deploy.py` gate on it. *A backup you have never restored is a rumor.*

## `env-parity.py` — drift radar
```
python3 ops/env-parity.py                 # or: make parity
```
Checks `.env` has exactly the keys `.env.example` expects, reports git HEAD + clean/dirty,
and compares the build the app is **serving** against HEAD (catches a stale or dirty prod).

---
🐺 own your stack · owe no one
