#!/usr/bin/env python3
"""Freehold — promote a git ref's code to ONE environment (per-env images).

Each env runs its own image (freehold-app:sbx / :stg / :prd). This builds that
image from a **git ref** — without touching the working tree or the other envs —
stamps the build, recreates only that env's app container, and confirms the served
SHA. So sandbox can run newer code than staging/prod. Promotion is the same ref
walking up the ladder:

    python3 ops/promote.py sandbox            # build HEAD -> sandbox, test it
    python3 ops/promote.py staging <sha>      # same ref -> staging, retest
    python3 ops/promote.py production <sha>   # -> prod (backup gate runs first)

`ref` defaults to HEAD. On a shared multi-env box, deploy with THIS — never
`up --build`, which would rebuild every env's image from the working tree at once.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from _common import REPO, compose, load_env

# env -> (image tag, compose service, .env var holding its public domain)
ENVS = {
    "sandbox":    ("sbx", "app-sandbox", "SANDBOX_DOMAIN"),
    "staging":    ("stg", "app-staging", "STAGING_DOMAIN"),
    "production": ("prd", "app",         "SITE_DOMAIN"),
}
FILES = ["-f", "docker-compose.yml", "-f", "docker-compose.prod.yml", "-f", "docker-compose.multienv.yml"]


def git(*a):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout.strip()


def build_from_ref(ref, tag):
    """Build freehold-app:<tag> from app/ at <ref>, stamped, no working-tree checkout."""
    sha = git("rev-parse", "--short", ref) or "nogit"
    count = git("rev-list", "--count", ref) or "0"
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    arch = subprocess.run(["git", "archive", f"{ref}:app"], cwd=REPO, capture_output=True)
    if arch.returncode != 0:
        print("ERROR: git archive failed —", arch.stderr.decode()[:200]); return None
    tmp = Path(tempfile.mkdtemp())
    try:
        subprocess.run(["tar", "-x", "-C", str(tmp)], input=arch.stdout, check=True)
        (tmp / "build-sha.txt").write_text(f"{sha}\n{date}\n{count}\n")   # what /version serves
        if subprocess.run(["docker", "build", "-t", f"freehold-app:{tag}", str(tmp)]).returncode != 0:
            print("ERROR: docker build failed"); return None
        return sha, count
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description="Promote a git ref to one environment.")
    ap.add_argument("env", choices=ENVS)
    ap.add_argument("ref", nargs="?", default="HEAD")
    args = ap.parse_args()
    tag, service, domain_var = ENVS[args.env]
    env = load_env()
    os.environ.setdefault("CADDYFILE", "./Caddyfile.prod")

    if args.env == "production":
        print("→ production: backup gate (must pass) ...")
        if subprocess.run([sys.executable, str(REPO / "ops" / "backup.py")]).returncode != 0:
            print("✋ ABORT: backup gate failed — not promoting."); return 1

    print(f"→ building freehold-app:{tag} from '{args.ref}' ...")
    built = build_from_ref(args.ref, tag)
    if not built:
        return 1
    sha, count = built

    print(f"→ recreating {service} on the new image (no rebuild, no other env touched) ...")
    if compose(*FILES, "up", "-d", "--no-deps", "--no-build", "--force-recreate", service).returncode != 0:
        print("ERROR: recreate failed"); return 1

    base = f"https://{env.get(domain_var, '')}"
    print(f"→ waiting for health at {base}/healthz ...")
    healthy = False
    for _ in range(30):
        try:
            if json.loads(urllib.request.urlopen(f"{base}/healthz", timeout=5).read()).get("status") == "ok":
                healthy = True; break
        except Exception:
            pass
        time.sleep(2)
    if not healthy:
        print("ERROR: did not become healthy in time"); return 1

    served = json.loads(urllib.request.urlopen(f"{base}/version", timeout=5).read()).get("sha")
    ok = served == sha
    print(f"\n{'✅' if ok else '⚠️ '} PROMOTED {args.env} · {base}")
    print(f"   ref {args.ref} → b{count} · {sha}   served: {served}   {'✓ match' if ok else '✗ MISMATCH'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
