#!/usr/bin/env python3
"""Freehold — deploy the ladder.

  stamp the build  ->  (backup GATES production)  ->  rebuild  ->  wait for health
  ->  PROVE what's actually running (re-probe after restart; the healthcheck greens
      a beat before the first request serves, so never trust the 'before' snapshot).

Usage:
  python3 ops/deploy.py sandbox
  python3 ops/deploy.py production [git-ref]
"""
import argparse
import json
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone

from _common import REPO, compose, load_env

ENVS = ("sandbox", "staging", "production")


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout.strip()


def http_json(url: str, timeout: int = 5) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read())


def main() -> int:
    ap = argparse.ArgumentParser(description="Deploy Freehold to an environment.")
    ap.add_argument("env", choices=ENVS)
    ap.add_argument("ref", nargs="?", help="git ref to deploy (default: current checkout)")
    args = ap.parse_args()

    env = load_env()
    base = env.get("APP_BASE_URL", "http://localhost:8080").rstrip("/")

    if args.ref:
        print(f"→ checkout {args.ref}")
        if subprocess.run(["git", "checkout", args.ref], cwd=REPO).returncode != 0:
            return 1

    # 1) stamp the build (this is what the app will serve at /version) -------
    sha = git("rev-parse", "--short", "HEAD") or "nogit"
    count = git("rev-list", "--count", "HEAD") or "0"
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    (REPO / "app" / "build-sha.txt").write_text(f"{sha}\n{date}\n{count}\n")
    print(f"→ stamped build: b{count} · {sha} · {date}")

    # 2) backup GATES production -------------------------------------------
    if args.env == "production":
        print("→ production: running the backup gate (must pass to proceed) ...")
        if subprocess.run([sys.executable, str(REPO / "ops" / "backup.py")]).returncode != 0:
            print("✋ ABORT: backup gate failed — refusing to deploy production.")
            return 1

    # 3) rebuild + restart --------------------------------------------------
    print("→ rebuild + restart ...")
    if compose("up", "-d", "--build").returncode != 0:
        print("ERROR: compose up failed"); return 1

    # 4) wait for health ----------------------------------------------------
    print("→ waiting for health ...")
    healthy = False
    for _ in range(30):
        try:
            if http_json(f"{base}/healthz").get("status") == "ok":
                healthy = True; break
        except Exception:
            pass
        time.sleep(2)
    if not healthy:
        print("ERROR: app did not become healthy in time"); return 1

    # 5) PROVE — re-probe; confirm the SHA we stamped is the SHA now serving -
    ver = http_json(f"{base}/version")
    served = ver.get("sha")
    verdict = "✅" if served == sha else "⚠️  MISMATCH — the running build is not what you stamped"
    print(f"\n✅ DEPLOYED · {args.env}")
    print(f"   stamped sha : {sha}")
    print(f"   served  sha : {served}   {verdict}")
    print(f"   version     : {ver.get('version')}    env: {ver.get('env')}")
    return 0 if served == sha else 1


if __name__ == "__main__":
    sys.exit(main())
