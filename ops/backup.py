#!/usr/bin/env python3
"""Freehold — encrypted, restore-verified database backup.

A backup you have never restored is a rumor. This script:
  1. dumps Postgres,
  2. encrypts it (openssl AES-256),
  3. PROVES it restores into a throwaway database before declaring success.

Exit code is 0 only if BOTH the dump and the restore drill pass — so a deploy
can gate production on it (see ops/deploy.py).
"""
import hashlib
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
    print(f"[1/3] dumping database '{db}' ...")
    dump = compose("exec", "-T", "postgres", "pg_dump", "-U", user, "-d", db,
                   "--clean", "--if-exists", capture_output=True)
    if dump.returncode != 0:
        print("ERROR: pg_dump failed\n" + dump.stderr.decode(errors="replace")); return 1
    sql_bytes = dump.stdout
    print(f"      dump size: {len(sql_bytes):,} bytes")

    # 2) encrypt ------------------------------------------------------------
    print("[2/3] encrypting (openssl AES-256, pbkdf2) ...")
    enc = subprocess.run(
        ["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-salt", "-pass", f"pass:{passphrase}"],
        input=sql_bytes, capture_output=True)
    if enc.returncode != 0:
        print("ERROR: encryption failed\n" + enc.stderr.decode(errors="replace")); return 1
    enc_file.write_bytes(enc.stdout)
    sha = hashlib.sha256(enc.stdout).hexdigest()
    print(f"      wrote {enc_file.name}  ({len(enc.stdout):,} bytes)  sha256 {sha[:16]}…")

    # 3) restore drill ------------------------------------------------------
    print("[3/3] restore drill — proving it actually restores ...")
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
    print("   The backup is real, not a rumor.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
