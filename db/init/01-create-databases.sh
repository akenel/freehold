#!/bin/bash
# Runs once, on a fresh Postgres volume. The app DB is created by POSTGRES_DB;
# here we add Keycloak's own database so the two never share a schema.
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE DATABASE ${POSTGRES_KC_DB};
EOSQL
echo "freehold: created database '${POSTGRES_KC_DB}' for Keycloak"
