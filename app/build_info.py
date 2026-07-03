"""Freehold — what build is actually running?

Reads build-sha.txt (stamped by ops/deploy.py at deploy time):
  line 1: short git SHA
  line 2: build date (human)
  line 3: commit count  -> version "bNNN"
If the file is absent (never deployed), everything reads "dev" — honestly.
"""
from pathlib import Path

_FILE = Path(__file__).parent / "build-sha.txt"


def _lines() -> list[str]:
    if _FILE.exists():
        parts = _FILE.read_text().strip().splitlines()
        return parts + [""] * (3 - len(parts))
    return ["", "", ""]


def sha() -> str:
    return _lines()[0] or "dev"


def date() -> str:
    return _lines()[1]


def version() -> str:
    count = _lines()[2]
    return f"b{count}" if count else "dev"
