#!/usr/bin/env python3
"""Freehold — encrypted, restore-verified backup of DOCKER VOLUMES.

`ops/backup.py` covers the two Postgres databases. It does not cover data that
lives in a volume rather than a table — most importantly **openwebui_data**, which
holds every conversation anyone has had with ai.wolfhold.app. That is the most
sensitive data on the box and until now it had no backup at all.

Same discipline as backup.py: tar -> encrypt -> PROVE it restores -> ship off-box.
Exit code is 0 only if every volume passes every step.

Deliberately NOT part of the deploy gate. A volume archive can be hundreds of MB;
tarring it on every promote would make deploys slow and B2 expensive. Run it on a
timer instead:

    # /etc/cron.d/freehold-volumes  — nightly at 03:20
    20 3 * * * root cd /root/freehold && /usr/bin/python3 ops/backup-volumes.py >> /var/log/freehold-volumes.log 2>&1

Usage:
    python3 ops/backup-volumes.py                 # the default set (openwebui_data)
    python3 ops/backup-volumes.py miniodata       # a specific volume, short name
    python3 ops/backup-volumes.py --no-pause ...  # don't pause the container first
"""
import argparse
import hashlib
import os
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from _common import REPO, load_env

# Compose project name (docker-compose.yml `name: freehold`) — volumes are created
# as <project>_<volume>, containers as <project>-<service>-1.
PROJECT = "freehold"

# short name -> (container to pause while we read it, a file that MUST be in the
# archive for it to count as a real backup)
VOLUMES = {
    "openwebui_data": ("open-webui", "webui.db"),
    "miniodata":      ("minio",      None),
    "pgdata":         ("postgres",   None),   # prefer ops/backup.py; this is the raw cluster
}
DEFAULT = ["openwebui_data"]

# Only catches a truncated or empty openssl write. Do NOT raise this to something
# that "feels like a real backup" — gzip is very good at repetitive data, and a
# perfectly valid archive can be a few KB. Whether the backup is real is decided by
# the restore drill looking INSIDE it, not by the size of the ciphertext.
MIN_BYTES = 512


def sh(*args, **kw):
    return subprocess.run(args, **kw)


def volume_exists(vol: str) -> bool:
    return sh("docker", "volume", "inspect", vol, capture_output=True).returncode == 0


def archive_volume(vol: str, dest: Path, passphrase: str) -> bool:
    """Stream `tar czf -` from the volume straight through openssl into dest.

    Streamed, never buffered: the box has 4 GB of RAM and these archives can be
    hundreds of MB. Nothing plaintext ever touches the disk.
    """
    tar = subprocess.Popen(
        ["docker", "run", "--rm", "-v", f"{vol}:/data:ro", "alpine",
         "tar", "czf", "-", "-C", "/data", "."],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    with open(dest, "wb") as out:
        enc = subprocess.Popen(
            ["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-salt",
             "-pass", f"pass:{passphrase}"],
            stdin=tar.stdout, stdout=out, stderr=subprocess.PIPE)
        tar.stdout.close()          # let tar see EPIPE if openssl dies
        _, enc_err = enc.communicate()
    tar_err = tar.stderr.read()
    tar.wait()

    if tar.returncode != 0:
        print(f"   ERROR: tar failed\n{tar_err.decode(errors='replace')[:500]}"); return False
    if enc.returncode != 0:
        print(f"   ERROR: encryption failed\n{enc_err.decode(errors='replace')[:500]}"); return False
    return True


def restore_drill(enc_file: Path, passphrase: str, key_file: str | None) -> bool:
    """Decrypt, unpack, and confirm the thing you actually need is inside.

    "The tar command exited 0" is not proof. This opens the archive and looks for
    the file that makes the backup worth having — for Open WebUI that is webui.db,
    the SQLite database holding every account, chat and setting.
    """
    with tempfile.TemporaryDirectory() as tmp:
        plain = Path(tmp) / "vol.tar.gz"
        dec = sh("openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2",
                 "-pass", f"pass:{passphrase}", "-in", str(enc_file), "-out", str(plain),
                 capture_output=True)
        if dec.returncode != 0:
            print("   ERROR: decrypt failed — the archive or the passphrase is wrong"); return False

        try:
            with tarfile.open(plain, "r:gz") as tf:
                names = tf.getnames()
                files = [m for m in tf.getmembers() if m.isfile()]
                total = sum(m.size for m in files)
                # The real emptiness check — an archive of nothing unpacks fine and
                # tells you nothing. This is the volume analogue of backup.py
                # refusing a dump that restores to zero tables.
                if not files:
                    print("   ERROR: archive contains no files at all — that is not a backup.")
                    return False
                if key_file:
                    match = next((n for n in names if n.rstrip("/").endswith("/" + key_file)
                                  or n == "./" + key_file), None)
                    if not match:
                        print(f"   ERROR: '{key_file}' is NOT in the archive — "
                              f"this would restore an empty {enc_file.stem}")
                        return False
                    member = tf.extractfile(match)
                    head = member.read(16) if member else b""
                    if key_file.endswith(".db") and not head.startswith(b"SQLite format 3"):
                        print(f"   ERROR: '{key_file}' is not a valid SQLite file "
                              f"(header was {head[:16]!r}) — torn or corrupt")
                        return False
                    print(f"   ✅ '{key_file}' present and valid SQLite")
        except tarfile.TarError as exc:
            print(f"   ERROR: archive will not open: {exc}"); return False

    print(f"   ✅ RESTORE VERIFIED — {enc_file.name} unpacks clean "
          f"({len(names):,} entries, {total:,} bytes uncompressed).")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Back up docker volumes, encrypted and verified.")
    ap.add_argument("volumes", nargs="*", default=None,
                    help=f"short names (default: {' '.join(DEFAULT)}). Known: {', '.join(VOLUMES)}")
    ap.add_argument("--no-pause", action="store_true",
                    help="don't pause the container while reading (faster, risks a torn SQLite)")
    args = ap.parse_args()
    wanted = args.volumes or DEFAULT

    env = load_env()
    passphrase = env.get("BACKUP_PASSPHRASE", "")
    if not passphrase:
        print("ERROR: BACKUP_PASSPHRASE is not set in .env"); return 1

    backups = REPO / "backups"; backups.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    made: list[Path] = []

    print(f"→ backing up {len(wanted)} volume(s): {', '.join(wanted)}")

    for short in wanted:
        service, key_file = VOLUMES.get(short, (None, None))
        vol = f"{PROJECT}_{short}"
        container = f"{PROJECT}-{service}-1" if service else None
        enc_file = backups / f"{short}-{stamp}.tar.gz.enc"
        print(f"\n── VOLUME {vol} " + "─" * max(0, 40 - len(vol)))

        if not volume_exists(vol):
            print(f"   ERROR: docker volume '{vol}' does not exist on this host."); return 1

        # Pause the writer so we don't tar a half-written SQLite page. `pause` is a
        # SIGSTOP, not a stop: connections survive, it resumes in milliseconds. The
        # UI hangs for the length of the tar, which is why this is a nightly job and
        # not part of a deploy.
        paused = False
        if container and not args.no_pause:
            if sh("docker", "pause", container, capture_output=True).returncode == 0:
                paused = True
                print(f"   [1/3] paused {container} for a consistent read")
            else:
                print(f"   [1/3] {container} not running — reading the volume as-is")
        else:
            print("   [1/3] not pausing (--no-pause)" if args.no_pause else "   [1/3] no container to pause")

        try:
            print("   [2/3] tar + encrypt (streamed, nothing plaintext on disk) ...")
            ok = archive_volume(vol, enc_file, passphrase)
        finally:
            if paused:
                sh("docker", "unpause", container, capture_output=True)
                print(f"         unpaused {container}")

        if not ok:
            return 1

        size = enc_file.stat().st_size
        if size < MIN_BYTES:
            print(f"   ERROR: archive is only {size} bytes — refusing to call that a backup.")
            return 1
        sha = hashlib.sha256(enc_file.read_bytes()).hexdigest()
        print(f"         wrote {enc_file.name}  ({size:,} bytes)  sha256 {sha[:16]}…")

        print("   [3/3] restore drill — proving it actually unpacks ...")
        if not restore_drill(enc_file, passphrase, key_file):
            print(f"\n✋ ABORT: '{short}' failed its drill — not shipping a backup we can't trust.")
            return 1
        made.append(enc_file)

    # off-box copy to Backblaze B2 (if configured) --------------------------
    key_id, app_key = env.get("B2_KEY_ID", "").strip(), env.get("B2_APP_KEY", "").strip()
    bucket = env.get("B2_BUCKET", "").strip()
    if key_id and app_key and bucket and not app_key.startswith("change_me"):
        dest = f"b2:{bucket}/{env.get('APP_ENV', 'prod')}/volumes"
        rc = {**os.environ, "RCLONE_CONFIG_B2_TYPE": "b2",
              "RCLONE_CONFIG_B2_ACCOUNT": key_id, "RCLONE_CONFIG_B2_KEY": app_key}
        print(f"\n→ shipping {len(made)} archive(s) off-box → {dest} ...")
        for f in made:
            if sh("rclone", "copy", str(f), dest, "--no-traverse", "--no-check-dest",
                  env=rc).returncode != 0:
                print(f"ERROR: off-box copy failed for {f.name}"); return 1
            print(f"      ✅ OFF-BOX — {f.name}")
    else:
        print("\n→ off-box copy: B2 not configured — LOCAL ONLY ⚠️")

    print("\n   Volume backups are real, not a rumor.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
