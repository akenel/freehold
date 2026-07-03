#!/usr/bin/env python3
"""Freehold — env parity. Catch config drift before it bites.

Three cheap checks that save expensive surprises:
  1. does .env have exactly the keys .env.example expects? (missing/extra)
  2. is the working tree clean, and what's HEAD?
  3. is the build the app is SERVING the same as HEAD? (or is prod stale/dirty?)
"""
import json
import subprocess
import sys
import urllib.request

from _common import REPO, load_env


def keys_of(name: str) -> set:
    return set(load_env(REPO / name).keys())


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout.strip()


def main() -> int:
    env = load_env()
    base = env.get("APP_BASE_URL", "http://localhost:8080").rstrip("/")
    print("=== Freehold · env parity ===\n")

    # 1) config keys --------------------------------------------------------
    example, current = keys_of(".env.example"), keys_of(".env")
    missing, extra = example - current, current - example
    print("[config keys]")
    print(f"  .env.example: {len(example)} keys   ·   .env: {len(current)} keys")
    print(f"  missing in .env : {sorted(missing) or 'none ✅'}")
    print(f"  extra   in .env : {sorted(extra) or 'none ✅'}")

    # 2) git state ----------------------------------------------------------
    head = git("rev-parse", "--short", "HEAD") or "nogit"
    dirty = bool(git("status", "--porcelain"))
    print("\n[git]")
    print(f"  HEAD: {head}   ·   working tree: {'DIRTY ⚠️' if dirty else 'clean ✅'}")

    # 3) what is actually running ------------------------------------------
    print("\n[running app]")
    try:
        ver = json.loads(urllib.request.urlopen(f"{base}/version", timeout=5).read())
        served = ver.get("sha")
        if served == head:
            state = "✅ matches HEAD"
        elif served == "dev":
            state = "dev (not deployed yet)"
        else:
            state = "⚠️  DRIFT — running build ≠ HEAD"
        print(f"  serving: {ver.get('version')} · {served} ({ver.get('env')})   {state}")
    except Exception as exc:  # noqa: BLE001
        print(f"  (app not reachable at {base}: {exc})")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
