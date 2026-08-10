#!/usr/bin/env python3
"""Freehold — encrypted, restore-verified database backup.

A backup you have never restored is a rumor. For EACH database this script:
  1. dumps it,
  2. encrypts it (openssl AES-256),
  3. PROVES it restores into a throwaway database before declaring success,
and then ships every encrypted file OFF-BOX to Backblaze B2 (if configured) — a
backup on the same box it protects is not disaster recovery.

TWO databases are covered, and both matter:
  - the APP db  (POSTGRES_APP_DB)  — tickets, profiles, runs, audit events
  - the KEYCLOAK db (POSTGRES_KC_DB) — every user, credential, role grant, and
    social-login link. `ops/prod-apply.py` can rebuild realm CONFIG from .env,
    but it cannot rebuild your USERS. Without this, "restore the box" silently
    means "everyone re-registers and re-links their Google account".

Exit code is 0 only if every dump, every restore drill, AND (when B2 is set) the
off-box copy all pass — so a deploy can gate production on it (see ops/promote.py).
"""
import hashlib
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from _common import REPO, compose, load_env

CHECK_DB = "freehold_restorecheck"
# A dump that restores to zero tables "succeeds" at every step while containing
# nothing. Refuse it — that is precisely the green light that lies.
MIN_TABLES = 1


def backup_one(db: str, label: str, user: str, passphrase: str, out_dir: Path,
               stamp: str) -> Path | None:
    """Dump -> encrypt -> restore-drill ONE database. Returns the encrypted file,
    or None if any step failed (caller aborts; the gate must not pass partially)."""
    enc_file = out_dir / f"{db}-{stamp}.sql.enc"
    print(f"\n── {label}: database '{db}' " + "─" * max(0, 40 - len(label) - len(db)))

    # 1) dump ---------------------------------------------------------------
    print("   [1/3] dumping ...")
    dump = compose("exec", "-T", "postgres", "pg_dump", "-U", user, "-d", db,
                   "--clean", "--if-exists", capture_output=True)
    if dump.returncode != 0:
        print("   ERROR: pg_dump failed\n" + dump.stderr.decode(errors="replace")); return None
    sql_bytes = dump.stdout
    print(f"         dump size: {len(sql_bytes):,} bytes")

    # 2) encrypt ------------------------------------------------------------
    print("   [2/3] encrypting (openssl AES-256, pbkdf2) ...")
    enc = subprocess.run(
        ["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-salt", "-pass", f"pass:{passphrase}"],
        input=sql_bytes, capture_output=True)
    if enc.returncode != 0:
        print("   ERROR: encryption failed\n" + enc.stderr.decode(errors="replace")); return None
    enc_file.write_bytes(enc.stdout)
    sha = hashlib.sha256(enc.stdout).hexdigest()
    print(f"         wrote {enc_file.name}  ({len(enc.stdout):,} bytes)  sha256 {sha[:16]}…")

    # 3) restore drill ------------------------------------------------------
    print("   [3/3] restore drill — proving it actually restores ...")
    # decrypt, and confirm it round-trips to the exact original bytes
    dec = subprocess.run(
        ["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-pass", f"pass:{passphrase}"],
        input=enc.stdout, capture_output=True)
    if dec.returncode != 0 or dec.stdout != sql_bytes:
        print("   ERROR: decrypt/integrity check failed"); return None

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
        print("   ERROR: restore drill FAILED\n" + restore.stderr.decode(errors="replace")); return None
    if not tables.isdigit() or int(tables) < MIN_TABLES:
        print(f"   ERROR: restored clean but found {tables or '?'} public tables "
              f"(expected >= {MIN_TABLES}) — refusing to call an empty dump a backup.")
        return None

    print(f"   ✅ RESTORE VERIFIED — {enc_file.name} restores clean ({tables} public tables).")
    return enc_file


def main() -> int:
    env = load_env()
    user = env.get("POSTGRES_USER", "freehold")
    app_db = env.get("POSTGRES_APP_DB", "freehold")
    kc_db = env.get("POSTGRES_KC_DB", "keycloak")
    passphrase = env.get("BACKUP_PASSPHRASE", "")
    if not passphrase:
        print("ERROR: BACKUP_PASSPHRASE is not set in .env"); return 1

    backups = REPO / "backups"; backups.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    targets = [(app_db, "APP"), (kc_db, "KEYCLOAK")]
    print(f"→ backing up {len(targets)} databases: " + ", ".join(d for d, _ in targets))

    enc_files: list[Path] = []
    for db, label in targets:
        result = backup_one(db, label, user, passphrase, backups, stamp)
        if result is None:
            print(f"\n✋ ABORT: the '{db}' backup failed — the gate does not pass on a partial set.")
            return 1
        enc_files.append(result)

    print()
    # off-box copy to Backblaze B2 (if configured) --------------------------
    key_id, app_key = env.get("B2_KEY_ID", "").strip(), env.get("B2_APP_KEY", "").strip()
    bucket = env.get("B2_BUCKET", "").strip()
    if key_id and app_key and bucket and not app_key.startswith("change_me"):
        keep = env.get("B2_KEEP_DAYS", "30").strip() or "30"
        dest = f"b2:{bucket}/{env.get('APP_ENV', 'prod')}"
        # rclone reads the B2 remote straight from env — no config file, no creds on disk.
        rc = {**os.environ, "RCLONE_CONFIG_B2_TYPE": "b2",
              "RCLONE_CONFIG_B2_ACCOUNT": key_id, "RCLONE_CONFIG_B2_KEY": app_key}
        print(f"→ shipping {len(enc_files)} encrypted files off-box → {dest} ...")
        # Upload only, --no-check-dest so a key with no read/list rights still works:
        # cleanup + immutability are handled B2-side (lifecycle rule + Object-Lock
        # retention, see ops/b2-immutable.py), so the box key never needs to read or
        # delete — only add. An attacker who owns the box can't wipe recovery points.
        # Shipped one at a time so a failure names the file that didn't make it.
        for enc_file in enc_files:
            # Capped retries. rclone defaults to 3 attempts x 10 low-level retries,
            # and B2 keeps a VERSION of every upload — on 2026-08-10 that turned one
            # failing 1 GB copy into 30 stored copies and 30.7 GB of billed storage.
            # These dumps are small, but the exposure is the same shape.
            if subprocess.run(["rclone", "copy", str(enc_file), dest,
                               "--no-traverse", "--no-check-dest",
                               "--retries", "2", "--low-level-retries", "2"],
                              env=rc).returncode != 0:
                print(f"ERROR: off-box copy to B2 failed for {enc_file.name}"); return 1
            print(f"      ✅ OFF-BOX — {enc_file.name} shipped to B2 (immutable; lifecycle keeps ≤ {keep}d).")
        print("      Survives box loss.")
    else:
        print("→ off-box copy: B2 not configured (set B2_KEY_ID/B2_APP_KEY/B2_BUCKET) — LOCAL ONLY ⚠️")

    print("\n   The backup is real, not a rumor — app data AND every user account.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
