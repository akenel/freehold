"""Shared bits for the Freehold ops scripts. Stdlib only — runs on any host
with python3 + docker + openssl, no pip installs."""
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def load_env(path: Path | None = None) -> dict:
    """Parse a KEY=value .env file into a dict (ignores blanks + # comments)."""
    path = path or (REPO / ".env")
    env: dict[str, str] = {}
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip()
    return env


def compose(*args, **kwargs):
    """Run `docker compose ...` from the repo root."""
    return subprocess.run(["docker", "compose", *args], cwd=REPO, **kwargs)
