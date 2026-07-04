# Secrets — SOPS + age (own your stack, owe no one)

No HashiCorp Vault, no unseal ceremony, no cloud KMS. Secrets are **encrypted at
rest inside the repo** with [SOPS](https://github.com/getsops/sops) + a single
[age](https://github.com/FiloSottile/age) key. You commit ciphertext; only the
holder of the age key can read it.

```
KeePass (source of truth) → sops secrets/<env>.enc.yaml → make secrets ENV=<env> → Keycloak vault
```

## Install the tools (once per box, no sudo)

```bash
mkdir -p ~/.local/bin
curl -fsSL https://github.com/FiloSottile/age/releases/download/v1.2.1/age-v1.2.1-linux-amd64.tar.gz \
  | tar xz -C /tmp && install -m755 /tmp/age/age /tmp/age/age-keygen ~/.local/bin/
curl -fsSL -o ~/.local/bin/sops \
  https://github.com/getsops/sops/releases/download/v3.9.4/sops-v3.9.4.linux.amd64 && chmod +x ~/.local/bin/sops
# ensure ~/.local/bin is on PATH
```

## The one key

The age **private key** lives at `~/.config/sops/age/keys.txt` (perms `600`),
**outside the repo** — it is never committed. Back it up in **KeePass**; that
single entry is your whole recovery story. The matching **public** recipient is
in `.sops.yaml` (safe to commit).

To put the key on another box: copy your KeePass value into that box's
`~/.config/sops/age/keys.txt` and `chmod 600` it. To add a *second* key (a
teammate / a per-box key), append its public recipient in `.sops.yaml` and run
`make secrets-rekey`.

## What's encrypted

`secrets/sandbox.enc.yaml`, `secrets/staging.enc.yaml`, `secrets/production.enc.yaml`
— each is the full `.env` for that environment, values encrypted, keys readable
(so `git diff` shows *which* secret changed, never the value). These are safe to
commit.

## Everyday use

```bash
# edit a secret (opens $EDITOR decrypted; re-encrypts on save)
make secrets-edit ENV=production        # or: sops secrets/production.enc.yaml

# on a box: decrypt to .env AND load into Keycloak (vault + social logins) in one shot
make secrets ENV=production
docker compose up -d                    # fresh box; or down && up to re-import realms
```

`make secrets` runs `ops/secrets.py`: `sops -d` → writes `.env`, then
`ops/set-smtp.py` (Resend key → vault) and `ops/set-idp.py` (social-login secrets
→ vault, providers enabled). One command from encrypted-in-git to live-in-Keycloak.

## Rotating a secret

1. `make secrets-edit ENV=production`, change the value, save.
2. `git commit -am "rotate <thing>"` — the diff proves *when*, not *what*.
3. On the box: `git pull && make secrets ENV=production && docker compose up -d`.

## Where KeePass and the banco rotate script fit

KeePass stays your human source of truth and holds the age key. Your banco rotate
script becomes the courier that writes values **into** the SOPS file (via
`sops --set` or by editing `secrets/<env>.enc.yaml`) — so the flow is
KeePass → rotate → SOPS (in git) → `make secrets` → Keycloak, with no hand-copying.

## Public repo note

SOPS ciphertext is safe to commit to a public repo — that's the design. If you'd
still rather keep `secrets/` out of git entirely, add `secrets/` to `.gitignore`
and sync those files out-of-band; everything else works unchanged.
