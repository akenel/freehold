# Restore — bringing the data back

`ops/backup.py` produces two encrypted, restore-verified dumps per run and ships
them off-box. This is the other half: **how you actually get them back in.**

A backup you have never restored is a rumor. A restore procedure nobody has ever
run is the same rumor wearing a hat. Every command below was executed end to end
against a clean-room stack on 2026-08-10 — a throwaway Postgres, both dumps
restored into it, Keycloak 26.0 booted on the result, and a restored credential
used to obtain a real access token. What's written here is what ran.

---

## What a backup run gives you

Each `python3 ops/backup.py` writes two files to `backups/` and copies both to B2:

| File | Contains | Losing it means |
|---|---|---|
| `<POSTGRES_APP_DB>-<stamp>.sql.enc` | tickets, profiles, business-hub runs, audit events, health checks | app data gone |
| `<POSTGRES_KC_DB>-<stamp>.sql.enc` | **every user, credential, role grant, social-login link, realm and client** | everyone re-registers and re-links their Google account |

Both are `openssl enc -aes-256-cbc -pbkdf2`, keyed on `BACKUP_PASSPHRASE` from
`.env`. **The passphrase is not in the backup.** If you lose it, the dumps are
noise — keep it in your password manager, not only on the box.

> The Keycloak dump is ~30× the size of the app dump (483 KB vs 15 KB on prod as
> of 2026-08-10). That ratio is the point: most of what you'd lose is identity.

---

## Getting the files back

**Still on the box?** They're in `backups/`.

**Box is gone?** Pull from B2. `rclone` reads the remote straight from env — no
config file, no creds on disk:

```bash
export RCLONE_CONFIG_B2_TYPE=b2
export RCLONE_CONFIG_B2_ACCOUNT=<B2_KEY_ID>
export RCLONE_CONFIG_B2_KEY=<B2_APP_KEY>

rclone ls   b2:<B2_BUCKET>/production                    # newest stamp wins
rclone copy b2:<B2_BUCKET>/production ./backups --include "*-20260810T083327Z.sql.enc"
```

Note the box's upload key is **write-only by design** (`ops/backup.py` uses
`--no-check-dest` so a key with no list/read rights still works). If `rclone ls`
is denied, that's the hardening working — use a key with read rights from your
laptop, not the box key.

---

## Restore into a live box

**Restore the DB the service is using while that service is running and you will
corrupt it.** Stop the consumers first; leave Postgres up.

The dumps are taken with `--clean --if-exists`, so they drop and recreate their
own objects — you do not need to drop the databases, and you must not drop them
while anything holds a connection.

```bash
cd ~/freehold
FILES="-f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.multienv.yml -f docker-compose.openwebui.yml"

# 1. take a backup of what's there NOW, even if it's broken.
#    You are about to overwrite it, and "the state before the restore" is
#    sometimes the thing you actually wanted.
python3 ops/backup.py

# 2. stop everything that holds a DB connection. Postgres stays up.
CADDYFILE=./Caddyfile.prod docker compose $FILES stop app app-sandbox app-staging keycloak open-webui

# 3. restore. Decrypt straight into psql — no plaintext dump on disk.
#    ON_ERROR_STOP=1 so a partial restore fails loudly instead of half-landing.
openssl enc -d -aes-256-cbc -pbkdf2 -pass env:BACKUP_PASSPHRASE \
  -in backups/keycloak-<stamp>.sql.enc \
  | docker compose $FILES exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_KC_DB" -v ON_ERROR_STOP=1

openssl enc -d -aes-256-cbc -pbkdf2 -pass env:BACKUP_PASSPHRASE \
  -in backups/freehold-<stamp>.sql.enc \
  | docker compose $FILES exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_APP_DB" -v ON_ERROR_STOP=1

# 4. bring it back
CADDYFILE=./Caddyfile.prod docker compose $FILES start keycloak app app-sandbox app-staging open-webui

# 5. schema may be older than the code that's deployed — catch it up
CADDYFILE=./Caddyfile.prod docker compose $FILES exec app alembic upgrade head

# 6. reconcile Keycloak config to .env (client secret, IdPs, link flow)
python3 ops/prod-apply.py
```

`BACKUP_PASSPHRASE` must be exported for step 3 (`set -a; . ./.env; set +a`, or
paste it into the shell). `-pass env:` keeps it out of the process list, which
`-pass pass:` does not.

Step 6 matters after a restore: the dump carries the client secret that was live
when it was taken. If `.env` has since rotated, `prod-apply.py` realigns them.
It's idempotent — running it when nothing changed does nothing.

---

## Rebuild a dead box, with the data

The procedure in `GOING-LIVE.md` gets a box *running*. This gets your users back.

1. New box, DNS pointed at it, ports 80/443 open.
2. `git clone` the repo.
3. Restore `.env` from your password manager. It carries every secret — DB,
   Keycloak, session, social client id + secret, **and `BACKUP_PASSPHRASE`**.
4. Pull the two newest `.sql.enc` files from B2 (above).
5. Launch **with the full file set for this box** — see `GOING-LIVE.md`; a bare
   `docker compose up` drops the prod overlay and takes the front door with it.
6. Wait for Postgres healthy, then restore both dumps (steps 2–3 above; nothing
   is holding connections yet on a fresh box, so you can skip the `stop`).
7. `alembic upgrade head`, then `python3 ops/prod-apply.py`.
8. **Verify** (below). Do not skip this and assume.

You do **not** recreate your admin by re-registering. That was the old procedure,
from when there was no Keycloak backup. Your admin is in the dump.

---

## Verify — the part that makes it real

A restore that "completed without errors" is not a restore. Prove all four:

```bash
# 1. the app's tables are back
docker compose $FILES exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_APP_DB" -c '\dt'

# 2. the identity data is back — this is the bit that had no backup before 2026-08-10
docker compose $FILES exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_KC_DB" -tAc \
  "SELECT 'realms='||(SELECT count(*) FROM realm)
        ||' users='||(SELECT count(*) FROM user_entity)
        ||' creds='||(SELECT count(*) FROM credential)
        ||' social='||(SELECT count(*) FROM federated_identity)
        ||' roles='||(SELECT count(*) FROM user_role_mapping);"

# 3. Keycloak boots on the restored schema and serves OIDC
curl -sS -o /dev/null -w 'kc-prd discovery %{http_code}\n' \
  https://auth.wolfhold.app/realms/kc-prd/.well-known/openid-configuration

# 4. a restored credential still authenticates — log in at the front door
curl -sS -o /dev/null -w 'app %{http_code}\n' https://www.wolfhold.app/healthz
```

Then **log in as a real user in a browser**, including a social login if you use
one. Step 2 counting rows proves the bytes arrived; only a login proves the
credentials and IdP links survived. Human-green, not machine-green.

---

## Rehearsing without touching production

This is how the procedure above was validated, and how you should re-validate it
after any Keycloak or Postgres version bump. It touches nothing you own — a
separate network, a throwaway Postgres, and a Keycloak that never sees your box.

```bash
docker network create fh-dr
docker run -d --name fh-dr-pg --network fh-dr \
  -e POSTGRES_USER=freehold -e POSTGRES_PASSWORD=rehearsal -e POSTGRES_DB=postgres \
  postgres:16-alpine
docker exec fh-dr-pg psql -U freehold -d postgres -c 'CREATE DATABASE freehold;' -c 'CREATE DATABASE keycloak;'

# restore both dumps into it (same openssl | psql pipe as above, targeting fh-dr-pg)

docker run -d --name fh-dr-kc --network fh-dr -p 127.0.0.1:18080:8080 \
  -e KC_DB=postgres -e KC_DB_URL=jdbc:postgresql://fh-dr-pg:5432/keycloak \
  -e KC_DB_USERNAME=freehold -e KC_DB_PASSWORD=rehearsal \
  -e KC_HOSTNAME_STRICT=false -e KC_HTTP_ENABLED=true \
  quay.io/keycloak/keycloak:26.0 start-dev

# proof: a RESTORED credential gets a real token
curl -s -d client_id=admin-cli -d grant_type=password \
     -d username=<admin> -d password=<pw> \
     http://127.0.0.1:18080/realms/master/protocol/openid-connect/token

docker rm -f fh-dr-kc fh-dr-pg && docker network rm fh-dr
```

Observed on 2026-08-10: both dumps restored with `psql exit=0`; the Keycloak DB
came back with 4 realms, 5 users, 5 credentials, 6 role grants; Keycloak 26.0.8
started in 3.8s on the restored schema with **no realm import**; and `admin`
authenticated against it, returning a valid access token.

The role name inside the dump (`freehold`, from `POSTGRES_USER`) must exist on
the target Postgres or ownership statements fail — that's why the throwaway is
created with the same `POSTGRES_USER`.

---

---

## Volumes — `ops/backup-volumes.py`

Some data lives in a volume, not a table, so `pg_dump` never sees it. The big one
is **`openwebui_data`**: every conversation anyone has had with `ai.wolfhold.app`,
plus per-user settings and uploads. Arguably the most sensitive data on the box.

```bash
cd ~/freehold
python3 ops/backup-volumes.py                 # hot; cold too if no baseline yet
python3 ops/backup-volumes.py --cold          # force a fresh cold baseline
python3 ops/backup-volumes.py --inspect       # what's in there and how big; changes nothing
python3 ops/backup-volumes.py miniodata       # a specific volume
```

### Cold / hot — why this is two archives, not one

The first full run on prod produced **1.02 GB**, and `open-webui` was paused for the
2.4 minutes it took to tar. Nightly, that is 2.4 minutes of frozen AI chat spent
backing up an embedding-model cache that is not user data — `webui.db`, the actual
conversations, is a few MB of that gigabyte.

You can't simply drop the cache: `OFFLINE_MODE=true` stops Open WebUI re-downloading
models, so a restore without it comes back broken.

| Part | Contains | When |
|---|---|---|
| **cold** | `cache/` — the model cache. Big, static. | **once**, kept as a baseline; re-made only with `--cold` |
| **hot** | `webui.db`, `uploads/`, `vector_db/`, and anything new | every run |

Measured on the test volume: cold 3.0 MB, **hot 41 KB** — the nightly archive is 1.4%
of the whole, and the pause drops from minutes to a blink.

Anything **not** named as cold is hot, so a new top-level directory appearing after an
Open WebUI upgrade lands in the nightly backup by default. Silently excluding unknown
new data is the failure this script exists to prevent.

A volume with no cold paths (`miniodata`, `pgdata`) is archived whole as one `full` part.

Same discipline as the databases: tar → encrypt (`BACKUP_PASSPHRASE`) → **open the
archive and check the thing you actually need is inside** → ship to
`b2:<bucket>/<env>/volumes`. Exit 0 only if every volume passes every step.

Two details worth knowing:

- It **pauses the container** while reading (`docker pause`, a SIGSTOP — connections
  survive, it resumes in milliseconds). Without that you can tar a half-written
  SQLite page and get an archive that unpacks perfectly and contains a corrupt
  database. `--no-pause` skips it if you accept that risk.
- It is **not part of the deploy gate**, on purpose. These archives can be hundreds
  of MB; tarring one on every promote would make deploys slow and B2 expensive. Run
  it on a timer:

```
# /etc/cron.d/freehold-volumes — nightly at 03:20
20 3 * * * root cd /root/freehold && /usr/bin/python3 ops/backup-volumes.py >> /var/log/freehold-volumes.log 2>&1
```

### Restoring a volume

```bash
FILES="-f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.multienv.yml -f docker-compose.openwebui.yml"

# stop the writer first — restoring under a running container corrupts it
CADDYFILE=./Caddyfile.prod docker compose $FILES stop open-webui

# empty it, then unpack COLD FIRST, then the newest HOT over the top.
# Order matters: hot is the current state and must win.
docker run --rm -v freehold_openwebui_data:/data alpine sh -c 'rm -rf /data/* /data/.[!.]* 2>/dev/null'

for A in backups/openwebui_data-cold-<stamp>.tar.gz.enc \
         backups/openwebui_data-hot-<stamp>.tar.gz.enc; do
  openssl enc -d -aes-256-cbc -pbkdf2 -pass env:BACKUP_PASSPHRASE -in "$A" \
    | docker run --rm -i -v freehold_openwebui_data:/data alpine tar xzf - -C /data
done

CADDYFILE=./Caddyfile.prod docker compose $FILES start open-webui
```

`set -a; . ./.env; set +a` first so `BACKUP_PASSPHRASE` is exported. Note the
volume's **full docker name** (`freehold_openwebui_data`) — the compose project
prefixes it.

The cold baseline is **older than the hot archive by design** — that is not a
mistake, it just hasn't changed. If the box is gone you need **both** files from
B2, and the cold one may be weeks or months older than the hot one.

**Verified end to end on 2026-08-10:** 200 conversations plus a 3 MB model cache
seeded, backed up as cold + hot, the volume emptied to zero entries, restored with
the loop above — cache, uploads, a directory added after the baseline was taken,
and all 200 conversations back. The drill's guards were tested individually too: a
61 KB archive that looked entirely healthy but carried a corrupt `webui.db` was
**refused**, as was one missing `webui.db`, as was a volume that doesn't exist.

### The B2 write-only key needs `--multi-thread-streams 0`

The first prod run uploaded 1 GB and failed three times with
`failed to find object after copy: failed to HEAD for download: Unknown 401`.

That is the hardening working. rclone's multi-thread path — used for large files —
verifies with a **read-back HEAD** after upload, and the box's B2 key is
deliberately write-only. Small DB dumps never reach that path, which is why
`backup.py` was unaffected. `--multi-thread-streams 0` uses a single stream and
skips the read-back; it is baked into `ops/backup-volumes.py`, not optional tuning.

---

## Known gaps

Covered: the app database, the Keycloak database (`ops/backup.py`), and
`openwebui_data` (`ops/backup-volumes.py`).

**Still not covered — no backup exists today:**

- **MinIO objects** — uploaded files, volume `miniodata`. `backup-volumes.py`
  already knows this volume (`python3 ops/backup-volumes.py miniodata`); it just
  isn't in the default set or on the timer yet. Enable it once you know the size —
  MinIO can be large, and B2 charges by the GB.
- **`iw` / `wk`** — separate compose projects from their own repos; whatever they
  persist is their own problem to solve.
- **sandbox / staging databases** — deliberate. They're throwaway.

Named here so each gap is a decision rather than a surprise.
