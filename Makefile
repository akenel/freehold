# Freehold — the whole kit, in a few words.
.PHONY: up down logs ps restart nuke backup deploy parity smtp idp help

help:    ; @echo "up | down | logs | ps | restart | nuke | trust | test | backup | deploy [ENV=sandbox] | parity | smtp | idp"

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
deploy:  ; python3 ops/deploy.py $${ENV:-sandbox}
parity:  ; python3 ops/env-parity.py

# Load the SMTP password from .env into Keycloak's vault + stamp the sender (all realms).
smtp:    ; python3 ops/set-smtp.py

# Turn on social logins (Google/GitHub/Facebook) from .env — see docs/SOCIAL-LOGIN.md
idp:     ; python3 ops/set-idp.py

# Reconcile a RUNNING Keycloak to .env (client secret, SMTP, social IdPs, link flow).
# The one-command "make prod match .env" — run after `up` on a deployed box.
apply:   ; python3 ops/prod-apply.py

# Promote a git ref's code to ONE env (per-env images). ENV=sandbox|staging|production REF=<sha>
# e.g. `make promote ENV=sandbox` then `make promote ENV=staging REF=<sha>` up the ladder.
promote: ; python3 ops/promote.py $${ENV:-sandbox} $${REF:-HEAD}

# --- secrets (SOPS + age) — see docs/SECRETS.md ---
# Decrypt this env's secrets to .env AND load them into Keycloak (vault + IdPs).
secrets:      ; python3 ops/secrets.py apply $${ENV:-sandbox}
# Edit an env's encrypted secrets in $EDITOR (re-encrypts on save).
secrets-edit: ; sops secrets/$${ENV:-sandbox}.enc.yaml
# Re-encrypt to the current recipients in .sops.yaml (after adding a box/teammate).
secrets-rekey: ; @for f in secrets/*.enc.yaml; do sops updatekeys -y $$f && echo "rekeyed $$f"; done
