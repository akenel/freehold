# Freehold — the whole kit, in a few words.
.PHONY: up down logs ps restart nuke backup deploy parity help

help:    ; @echo "up | down | logs | ps | restart | nuke | backup | deploy [ENV=sandbox] | parity"
up:      ; @[ -f .env ] || cp .env.example .env ; docker compose up -d --build
down:    ; docker compose down
logs:    ; docker compose logs -f
ps:      ; docker compose ps
restart: ; docker compose restart
nuke:    ; docker compose down -v   # also wipes the database volumes

# --- the rails ---
backup:  ; python3 ops/backup.py
deploy:  ; python3 ops/deploy.py $${ENV:-sandbox}
parity:  ; python3 ops/env-parity.py
