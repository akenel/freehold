#!/usr/bin/env python3
"""Freehold — encrypted, restore-verified database backup.

A backup you have never restored is a rumor. This script:
  1. dumps Postgres,
  2. encrypts it (openssl AES-256),
  3. PROVES it restores into a throwaway database before declaring success,
  4. ships the encrypted copy OFF-BOX to Backblaze B2 (if configured) — a backup
     on the same box it protects is not disaster recovery.

Exit code is 0 only if the dump, the restore drill, AND (when B2 is set) the
off-box copy all pass — so a deploy can gate production on it (see ops/deploy.py).
"""
import hashlib
import os
import subprocess
import sys
from datetime import datetime, timezone

from _common import REPO, compose, load_env

CHECK_DB = "freehold_restorecheck"


def main() -> int:
    env = load_env()
    user = env.get("POSTGRES_USER", "freehold")
    db = env.get("POSTGRES_APP_DB", "freehold")
    passphrase = env.get("BACKUP_PASSPHRASE", "")
    if not passphrase:
        print("ERROR: BACKUP_PASSPHRASE is not set in .env"); return 1

    backups = REPO / "backups"; backups.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    enc_file = backups / f"{db}-{stamp}.sql.enc"

    # 1) dump ---------------------------------------------------------------
    print(f"[1/4] dumping database '{db}' ...")
    dump = compose("exec", "-T", "postgres", "pg_dump", "-U", user, "-d", db,
                   "--clean", "--if-exists", capture_output=True)
    if dump.returncode != 0:
        print("ERROR: pg_dump failed\n" + dump.stderr.decode(errors="replace")); return 1
    sql_bytes = dump.stdout
    print(f"      dump size: {len(sql_bytes):,} bytes")

    # 2) encrypt ------------------------------------------------------------
    print("[2/4] encrypting (openssl AES-256, pbkdf2) ...")
    enc = subprocess.run(
        ["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-salt", "-pass", f"pass:{passphrase}"],
        input=sql_bytes, capture_output=True)
    if enc.returncode != 0:
        print("ERROR: encryption failed\n" + enc.stderr.decode(errors="replace")); return 1
    enc_file.write_bytes(enc.stdout)
    sha = hashlib.sha256(enc.stdout).hexdigest()
    print(f"      wrote {enc_file.name}  ({len(enc.stdout):,} bytes)  sha256 {sha[:16]}…")

    # 3) restore drill ------------------------------------------------------
    print("[3/4] restore drill — proving it actually restores ...")
    # decrypt, and confirm it round-trips to the exact original bytes
    dec = subprocess.run(
        ["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-pass", f"pass:{passphrase}"],
        input=enc.stdout, capture_output=True)
    if dec.returncode != 0 or dec.stdout != sql_bytes:
        print("ERROR: decrypt/integrity check failed"); return 1

    # restore into a fresh throwaway database, then drop it
    compose("exec", "-T", "postgres", "psql", "-U", user, "-d", "postgres",
            "-c", f"DROP DATABASE IF EXISTS {CHECK_DB};", capture_output=True)
    compose("exec", "-T", "postgres", "psql", "-U", user, "-d", "postgres",
            "-c", f"CREATE DATABASE {CHECK_DB};", capture_output=True)
    restore = compose("exec", "-T", "postgres", "psql", "-U", user, "-d", CHECK_DB,
                      "-v", "ON_ERROR_STOP=1", input=dec.stdout, capture_output=True)
    tables = compose("exec", "-T", "postgres", "psql", "-U", user, "-d", CHECK_DB, "-tAc",
                     "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';",
                     capture_output=True, text=True).stdout.strip()
    compose("exec", "-T", "postgres", "psql", "-U", user, "-d", "postgres",
            "-c", f"DROP DATABASE IF EXISTS {CHECK_DB};", capture_output=True)

    if restore.returncode != 0:
        print("ERROR: restore drill FAILED\n" + restore.stderr.decode(errors="replace")); return 1

    print(f"\n✅ RESTORE VERIFIED — {enc_file.name} restores clean ({tables} public tables).")

    # 4) off-box copy to Backblaze B2 (if configured) -----------------------
    key_id, app_key = env.get("B2_KEY_ID", "").strip(), env.get("B2_APP_KEY", "").strip()
    bucket = env.get("B2_BUCKET", "").strip()
    if key_id and app_key and bucket and not app_key.startswith("change_me"):
        keep = env.get("B2_KEEP_DAYS", "30").strip() or "30"
        dest = f"b2:{bucket}/{env.get('APP_ENV', 'prod')}"
        # rclone reads the B2 remote straight from env — no config file, no creds on disk.
        rc = {**os.environ, "RCLONE_CONFIG_B2_TYPE": "b2",
              "RCLONE_CONFIG_B2_ACCOUNT": key_id, "RCLONE_CONFIG_B2_KEY": app_key}
        print(f"[4/4] shipping encrypted copy off-box → {dest} ...")
        # Upload only, --no-check-dest so a key with no read/list rights still works:
        # cleanup + immutability are handled B2-side (lifecycle rule + Object-Lock
        # retention, see ops/b2-immutable.py), so the box key never needs to read or
        # delete — only add. An attacker who owns the box can't wipe recovery points.
        if subprocess.run(["rclone", "copy", str(enc_file), dest,
                           "--no-traverse", "--no-check-dest"], env=rc).returncode != 0:
            print("ERROR: off-box copy to B2 failed"); return 1
        print(f"      ✅ OFF-BOX — {enc_file.name} shipped to B2 (immutable; lifecycle keeps ≤ {keep}d). Survives box loss.")
    else:
        print("[4/4] off-box copy: B2 not configured (set B2_KEY_ID/B2_APP_KEY/B2_BUCKET) — LOCAL ONLY ⚠️")

    print("   The backup is real, not a rumor.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
