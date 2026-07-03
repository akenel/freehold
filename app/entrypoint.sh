#!/bin/sh
# Run database migrations, then start the app. A fresh `up -d` self-migrates.
set -e
echo "→ migrations: alembic upgrade head"
alembic upgrade head
echo "→ starting app"
exec uvicorn main:app --host 0.0.0.0 --port 8000
