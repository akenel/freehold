#!/usr/bin/env python3
"""Freehold — encrypted, restore-verified backup of DOCKER VOLUMES.

`ops/backup.py` covers the two Postgres databases. It does not cover data that
lives in a volume rather than a table — most importantly **openwebui_data**, which
holds every conversation anyone has had with ai.wolfhold.app. That is the most
sensitive data on the box and until 2026-08-10 it had no backup at all.

Same discipline as backup.py: tar -> encrypt -> PROVE it unpacks -> ship off-box.
Exit code is 0 only if every part of every volume passes every step.

COLD / HOT SPLIT — why this is not one archive
------------------------------------------------------------------------------
The first full run of openwebui_data produced **1.02 GB**, and open-webui was
PAUSED for the 2.4 minutes it took to tar. Nightly, that is 2.4 minutes of frozen
AI chat to back up an embedding-model cache that is not user data — webui.db, the
actual conversations, is a few MB of that gigabyte.

You cannot simply drop the cache: `OFFLINE_MODE=true` (docker-compose.openwebui.yml)
stops Open WebUI re-downloading models, so a restore without it comes back broken.

So each volume splits into:
  * COLD — big, effectively static (the model cache). Archived ONCE as a baseline
           and kept. Re-archived only with --cold.
  * HOT  — webui.db, uploads, vector_db: the data that actually changes. Small,
           so the nightly pause is seconds instead of minutes.

Restore = unpack the cold baseline, then the newest hot archive over it.
A volume with no cold paths is archived whole, as one `full` part.

COLD DOES NOT GO OFF-BOX by default. It is ~1 GB of PUBLIC model weights that
HuggingFace will hand back to anyone; the only reason we can't refetch them after a
restore is OFFLINE_MODE=true, a flag we control. Shipping it nightly exhausted a
10 GB Backblaze free tier on 2026-08-10 (403 storage_cap_exceeded) while the data
that is actually yours — the conversations — is ~5 MB. Off-box footprint with cold
excluded is ~170 MB for 30 days of everything, DBs included. Use --ship-cold if you
really want it up there.

Usage:
    python3 ops/backup-volumes.py                 # hot; cold too if no baseline yet
    python3 ops/backup-volumes.py --cold          # force a fresh cold baseline
    python3 ops/backup-volumes.py --ship-cold     # also send cold off-box (~1 GB)
    python3 ops/backup-volumes.py --inspect       # show what's big, change nothing
    python3 ops/backup-volumes.py miniodata       # a specific volume
    python3 ops/backup-volumes.py --no-pause ...  # don't pause the container first

Timer (the whole point of the split — this is now cheap enough to run nightly):
    # /etc/cron.d/freehold-volumes
    20 3 * * * root cd /root/freehold && /usr/bin/python3 ops/backup-volumes.py >> /var/log/freehold-volumes.log 2>&1
"""
import argparse
import hashlib
import os
import shutil
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

# short name -> (service to pause, file that MUST be in the hot archive, cold paths)
# `cold` names TOP-LEVEL entries inside the volume that are big and static.
VOLUMES = {
    #                 service        key_file      cold
    "openwebui_data": ("open-webui", "webui.db",   ["cache"]),
    "miniodata":      ("minio",      None,         []),
    "pgdata":         ("postgres",   None,         []),   # prefer ops/backup.py
}
DEFAULT = ["openwebui_data"]

# Only catches a truncated or empty openssl write. Do NOT raise this to something
# that "feels like a real backup" — gzip is very good at repetitive data, and a
# valid archive can be a few KB. Whether a backup is real is decided by the restore
# drill looking INSIDE it, not by the size of the ciphertext.
MIN_BYTES = 512


def sh(*args, **kw):
    return subprocess.run(args, **kw)


def volume_exists(vol: str) -> bool:
    return sh("docker", "volume", "inspect", vol, capture_output=True).returncode == 0


def list_entries(vol: str) -> list[str]:
    """Top-level entries inside the volume."""
    out = sh("docker", "run", "--rm", "-v", f"{vol}:/data:ro", "alpine",
             "sh", "-c", "ls -A /data", capture_output=True, text=True)
    return [e for e in out.stdout.split("\n") if e.strip()]


def inspect(vol: str) -> None:
    """Show what's actually in there and how big. Changes nothing."""
    sh("docker", "run", "--rm", "-v", f"{vol}:/data:ro", "alpine",
       "sh", "-c", "du -sh /data/* /data/.[!.]* 2>/dev/null | sort -rh")


def archive_paths(vol: str, paths: list[str], dest: Path, passphrase: str) -> bool:
    """Stream `tar czf -` of the named paths straight through openssl into dest.

    Paths are passed explicitly rather than using --exclude: busybox tar's exclude
    handling is fiddly, and an explicit include list means a NEW top-level
    directory lands in the hot set by default. Silently excluding unknown new data
    is exactly the failure this whole script exists to prevent.
    """
    tar = subprocess.Popen(
        ["docker", "run", "--rm", "-v", f"{vol}:/data:ro", "alpine",
         "tar", "czf", "-", "-C", "/data", *paths],
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

    "tar exited 0" is not proof. This opens the archive and looks for the file that
    makes the backup worth having — for Open WebUI that is webui.db, the SQLite
    database holding every account, chat and setting.
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
                # tells you nothing. Volume analogue of backup.py refusing a dump
                # that restores to zero tables.
                if not files:
                    print("   ERROR: archive contains no files at all — that is not a backup.")
                    return False
                if key_file:
                    match = next((n for n in names
                                  if n.rstrip("/").endswith("/" + key_file) or n == key_file
                                  or n == "./" + key_file), None)
                    if not match:
                        print(f"   ERROR: '{key_file}' is NOT in the archive — "
                              f"this would restore an empty volume")
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

    print(f"   ✅ VERIFIED — {enc_file.name} unpacks clean "
          f"({len(names):,} entries, {total:,} bytes uncompressed).")
    return True


def ship(files: list[Path], env: dict) -> bool:
    if not files:
        print("\n→ off-box copy: nothing to ship.")
        return True

    key_id, app_key = env.get("B2_KEY_ID", "").strip(), env.get("B2_APP_KEY", "").strip()
    bucket = env.get("B2_BUCKET", "").strip()
    if not (key_id and app_key and bucket) or app_key.startswith("change_me"):
        print("\n→ off-box copy: B2 not configured — LOCAL ONLY ⚠️")
        return True
    if shutil.which("rclone") is None:
        print("\nERROR: rclone is not installed — cannot ship off-box. "
              "A backup that never leaves the box is not disaster recovery.")
        return False

    dest = f"b2:{bucket}/{env.get('APP_ENV', 'prod')}/volumes"
    rc = {**os.environ, "RCLONE_CONFIG_B2_TYPE": "b2",
          "RCLONE_CONFIG_B2_ACCOUNT": key_id, "RCLONE_CONFIG_B2_KEY": app_key}
    print(f"\n→ shipping {len(files)} archive(s) off-box → {dest} ...")

    # Try EVERY file, then report. Aborting on the first failure once meant a 5 MB
    # hot archive — the irreplaceable one — never got attempted because a 1 GB cold
    # archive of re-downloadable model weights failed ahead of it. The small
    # important thing must never be blocked by the big disposable one.
    failed: list[Path] = []
    for f in files:
        # --multi-thread-streams 0 is REQUIRED, not tuning. rclone's multi-thread
        # path (used for large files) verifies with a read-back HEAD after upload,
        # and the box's B2 key is deliberately WRITE-ONLY — so that HEAD returns
        # 401 and the whole copy fails. Small DB dumps never hit this; the 1 GB
        # openwebui archive did, on 2026-08-10. Single-stream skips the read-back.
        if sh("rclone", "copy", str(f), dest, "--no-traverse", "--no-check-dest",
              "--multi-thread-streams", "0", env=rc).returncode != 0:
            print(f"      ❌ FAILED  — {f.name}")
            failed.append(f)
        else:
            print(f"      ✅ OFF-BOX — {f.name}")

    if failed:
        shipped = len(files) - len(failed)
        print(f"\nERROR: {len(failed)} of {len(files)} archive(s) did not ship: "
              + ", ".join(f.name for f in failed))
        # Say exactly what is and isn't off-box. "The rest shipped" when nothing
        # shipped is the kind of comfortable half-truth this repo exists to avoid.
        print(f"       {shipped} did ship and {'is' if shipped == 1 else 'are'} off-box."
              if shipped else "       NOTHING shipped — no off-box copy exists for this run.")
        print("       Local copies of every archive are in backups/ and passed their drills.")
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Back up docker volumes, encrypted and verified.")
    ap.add_argument("volumes", nargs="*", default=None,
                    help=f"short names (default: {' '.join(DEFAULT)}). Known: {', '.join(VOLUMES)}")
    ap.add_argument("--cold", action="store_true",
                    help="re-archive the cold baseline even if one already exists")
    ap.add_argument("--ship-cold", action="store_true",
                    help="also copy the cold baseline off-box (it is ~1 GB of "
                         "re-downloadable model weights; off by default)")
    ap.add_argument("--inspect", action="store_true",
                    help="show what's in each volume and how big — changes nothing")
    ap.add_argument("--no-pause", action="store_true",
                    help="don't pause the container while reading (risks a torn SQLite)")
    args = ap.parse_args()
    wanted = args.volumes or DEFAULT

    env = load_env()
    passphrase = env.get("BACKUP_PASSPHRASE", "")
    if not passphrase and not args.inspect:
        print("ERROR: BACKUP_PASSPHRASE is not set in .env"); return 1

    backups = REPO / "backups"; backups.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    made: list[tuple[str, Path]] = []

    if not args.inspect:
        print(f"→ backing up {len(wanted)} volume(s): {', '.join(wanted)}")

    for short in wanted:
        service, key_file, cold_paths = VOLUMES.get(short, (None, None, []))
        vol = f"{PROJECT}_{short}"
        container = f"{PROJECT}-{service}-1" if service else None

        if not volume_exists(vol):
            print(f"ERROR: docker volume '{vol}' does not exist on this host."); return 1

        if args.inspect:
            print(f"\n── {vol} " + "─" * max(0, 40 - len(vol)))
            inspect(vol)
            print(f"   cold (archived once): {cold_paths or '(none — whole volume is one part)'}")
            continue

        print(f"\n── VOLUME {vol} " + "─" * max(0, 40 - len(vol)))
        entries = list_entries(vol)
        if not entries:
            print(f"   ERROR: volume '{vol}' is empty — nothing to back up."); return 1

        # Partition into parts. Anything not named cold is hot — a new top-level
        # directory we've never seen goes into the nightly backup by default.
        present_cold = [e for e in entries if e in cold_paths]
        hot = [e for e in entries if e not in cold_paths]

        parts: list[tuple[str, list[str]]] = []
        if not cold_paths:
            parts.append(("full", entries))
        else:
            have_baseline = bool(list(backups.glob(f"{short}-cold-*.tar.gz.enc")))
            if present_cold and (args.cold or not have_baseline):
                why = "forced with --cold" if args.cold else "no baseline exists yet"
                print(f"   cold baseline: archiving {present_cold} ({why})")
                parts.append(("cold", present_cold))
            elif present_cold:
                print(f"   cold baseline: skipping {present_cold} — baseline already on disk "
                      f"(re-make with --cold)")
            if hot:
                parts.append(("hot", hot))

        if not parts:
            print("   ERROR: nothing selected to archive."); return 1

        # Pause the writer so we don't tar a half-written SQLite page. `pause` is a
        # SIGSTOP, not a stop: connections survive and it resumes in milliseconds.
        paused = False
        if container and not args.no_pause:
            if sh("docker", "pause", container, capture_output=True).returncode == 0:
                paused = True
                print(f"   paused {container} for a consistent read")
            else:
                print(f"   {container} not running — reading the volume as-is")

        try:
            for part, paths in parts:
                enc_file = backups / f"{short}-{part}-{stamp}.tar.gz.enc"
                print(f"   [{part}] tar + encrypt {paths} ...")
                if not archive_paths(vol, paths, enc_file, passphrase):
                    return 1
                size = enc_file.stat().st_size
                if size < MIN_BYTES:
                    print(f"   ERROR: {part} archive is only {size} bytes — "
                          f"refusing to call that a backup."); return 1
                sha = hashlib.sha256(enc_file.read_bytes()).hexdigest()
                print(f"         wrote {enc_file.name}  ({size:,} bytes)  sha256 {sha[:16]}…")
                # Only the hot/full part carries the key file; cold is the model cache.
                if not restore_drill(enc_file, passphrase,
                                     key_file if part in ("hot", "full") else None):
                    print(f"\n✋ ABORT: '{short}' {part} failed its drill — "
                          f"not shipping a backup we can't trust.")
                    return 1
                made.append((part, enc_file))
        finally:
            if paused:
                sh("docker", "unpause", container, capture_output=True)
                print(f"   unpaused {container}")

    if args.inspect:
        return 0

    # Cold is ~1 GB of PUBLIC model weights. HuggingFace will hand them back to
    # anyone; the only reason we can't re-download after a restore is
    # OFFLINE_MODE=true, a flag we control. Shipping it nightly blew a 10 GB B2
    # free tier on 2026-08-10 while the data that is actually yours — the
    # conversations — is ~5 MB. So cold stays on the box unless asked for.
    to_ship = [p for part, p in made if part != "cold" or args.ship_cold]
    kept = [p for part, p in made if part == "cold" and not args.ship_cold]
    for p in kept:
        print(f"\n   ℹ️  {p.name} stays ON THE BOX (--ship-cold to send it).")
        print("      It is the model cache, not your data. If the box is lost, restore")
        print("      hot from B2 and set OFFLINE_MODE=false for one boot to refetch it.")

    if not ship(to_ship, env):
        return 1

    print("\n   Volume backups are real, not a rumor.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
