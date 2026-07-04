#!/usr/bin/env python3
"""Freehold — decrypt this env's SOPS secrets into .env.

    python3 ops/secrets.py apply <sandbox|staging|production>

Decrypts secrets/<env>.enc.yaml (needs the age key at ~/.config/sops/age/keys.txt
— from KeePass, perms 600) and writes .env. That's the ONLY thing it does now —
loading the secrets into Keycloak is `make apply` (ops/prod-apply.py), the single
config path, run after `up`. So the deploy sequence is always:

    make secrets ENV=<env>   # SOPS -> .env
    docker compose ... up -d
    make apply               # .env -> running Keycloak (client secret, SMTP, IdPs, link flow)

Secrets never sit in plaintext in git: the encrypted secrets/<env>.enc.yaml is
committed, .env is gitignored, the vault files are gitignored. Edit secrets with:
  sops secrets/<env>.enc.yaml   (or `make secrets-edit ENV=<env>`).
"""
import subprocess
import sys
from pathlib import Path

from _common import REPO

ENVS = ("sandbox", "staging", "production")
AGE_KEY = Path.home() / ".config" / "sops" / "age" / "keys.txt"


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] != "apply" or sys.argv[2] not in ENVS:
        print("usage: secrets.py apply <sandbox|staging|production>")
        return 1
    env = sys.argv[2]
    enc = REPO / "secrets" / f"{env}.enc.yaml"
    if not enc.exists():
        print(f"ERROR: {enc.relative_to(REPO)} not found")
        return 1
    if not AGE_KEY.exists():
        print(f"ERROR: age key not found at {AGE_KEY}")
        print("       Restore it from KeePass (chmod 600), then re-run.")
        return 1

    print(f"→ decrypting {enc.relative_to(REPO)} -> .env ...")
    dec = subprocess.run(["sops", "-d", "--output-type", "dotenv", str(enc)],
                         capture_output=True, text=True)
    if dec.returncode != 0:
        print("ERROR: sops decrypt failed\n" + dec.stderr)
        return 1
    (REPO / ".env").write_text(dec.stdout)
    print(f"      wrote .env ({len(dec.stdout.splitlines())} lines)")
    print(f"\n✅ {env} secrets in .env. Next:  docker compose ... up -d   then   make apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
