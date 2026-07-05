# Freehold — the whole kit, in a few words.
.PHONY: up down logs ps restart nuke backup deploy promote apply parity secrets help docs-serve docs-build

help:    ; @echo "up | down | logs | ps | restart | nuke | trust | test | backup | deploy [ENV=] | promote ENV=.. REF=.. | apply | secrets ENV=.. | parity | docs-serve | docs-build"

# Run the test suite in a throwaway app container (no infra needed).
test:    ; docker compose run --rm --no-deps app python -m pytest -q tests/
up:      ; @[ -f .env ] || cp .env.example .env ; docker compose up -d --build

# Trust Caddy's local CA so https://localhost is green (run once).
trust:   ; @docker compose cp caddy:/data/caddy/pki/authorities/local/root.crt ./freehold-local-ca.crt && echo "Saved freehold-local-ca.crt — trust it once:  Linux: sudo cp freehold-local-ca.crt /usr/local/share/ca-certificates/freehold.crt && sudo update-ca-certificates   ·   Firefox: Settings→Privacy→Certificates→Import.  Then restart the browser."
down:    ; docker compose down
logs:    ; docker compose logs -f
ps:      ; docker compose ps
restart: ; docker compose restart
nuke:    ; docker compose down -v   # also wipes the database volumes

# --- the rails ---
backup:  ; python3 ops/backup.py
parity:  ; python3 ops/env-parity.py
# One-time: make B2 backups immutable (Object-Lock retention + lifecycle cleanup).
b2-lock: ; python3 ops/b2-immutable.py

# Deploy — TWO tools, pick by topology:
#   deploy  : single-env box, rebuild the whole stack from the working tree (+ backup gate).
#   promote : multi-env ladder — build ONE env's image from a git ref (test-gated, per-env code).
deploy:  ; python3 ops/deploy.py $${ENV:-sandbox}
promote: ; python3 ops/promote.py $${ENV:-sandbox} $${REF:-HEAD}

# The ONE config path: reconcile a RUNNING Keycloak to .env — client secret, SMTP,
# social IdPs, and the no-email account-link flow. Run after `up`. Idempotent.
apply:   ; python3 ops/prod-apply.py

# Promote a git ref's code to ONE env (per-env images). ENV=sandbox|staging|production REF=<sha>
# e.g. `make promote ENV=sandbox` then `make promote ENV=staging REF=<sha>` up the ladder.
promote: ; python3 ops/promote.py $${ENV:-sandbox} $${REF:-HEAD}

# --- public docs (MkDocs Material) — see mkdocs.yml ---
# Only docs/public/ is ever published; the rest of docs/ stays internal.
# One-time: pip install -r docs/requirements.txt
docs-serve: ; mkdocs serve            # live preview at http://127.0.0.1:8000
docs-build: ; mkdocs build --strict   # -> ./site/ (Caddy serves it in prod)

# --- secrets (SOPS + age) — see docs/SECRETS.md ---
# Decrypt this env's secrets to .env (then `up` + `make apply` load them into Keycloak).
secrets:      ; python3 ops/secrets.py apply $${ENV:-sandbox}
# Edit an env's encrypted secrets in $EDITOR (re-encrypts on save).
secrets-edit: ; sops secrets/$${ENV:-sandbox}.enc.yaml
# Re-encrypt to the current recipients in .sops.yaml (after adding a box/teammate).
secrets-rekey: ; @for f in secrets/*.enc.yaml; do sops updatekeys -y $$f && echo "rekeyed $$f"; done
