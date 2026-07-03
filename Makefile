# Freehold — the whole kit, in a few words.
.PHONY: up down logs ps restart nuke help

help:    ; @echo "up | down | logs | ps | restart | nuke"
up:      ; @[ -f .env ] || cp .env.example .env ; docker compose up -d --build
down:    ; docker compose down
logs:    ; docker compose logs -f
ps:      ; docker compose ps
restart: ; docker compose restart
nuke:    ; docker compose down -v   # also wipes the database volumes
