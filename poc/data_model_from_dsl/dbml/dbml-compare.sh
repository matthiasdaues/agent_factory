#!/usr/bin/env bash
# Spike code for the data-model DSL PoC (DEC-07 wrapper). Not shipped tooling.
#
# Compares a DBML model with Gigacron's live schema. DBML has no comparison
# tool, so the wrapper:
#   1. generates PostgreSQL DDL with dbml2sql,
#   2. loads it into a fresh scratch database, schema `application`,
#   3. reflects the named tables from the scratch database and runs
#      alembic.autogenerate.compare_metadata against the live database.
# Usage:
#
#   dbml-compare.sh <model.dbml> <table> [<table> ...]
#
# Needs the Docker volumes dsl-poc-dbml-node (@dbml/cli) and
# dsl-poc-linkml-venv (sqlalchemy, alembic, psycopg2), and container dsl-poc-pg.
set -euo pipefail

dir=$(cd "$(dirname "$1")" && pwd)
file=$(basename "$1")
shift
tables="$*"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

docker run --rm -v dsl-poc-dbml-node:/opt/dbml -v "$dir":/w:ro -v "$tmp":/out -w /w \
  node:20-bookworm /opt/dbml/node_modules/.bin/dbml2sql --postgres "$file" -o /out/model.sql >/dev/null 2>&1

docker exec dsl-poc-pg psql -q -U postgres -c "DROP DATABASE IF EXISTS dbml_scratch" >/dev/null
docker exec dsl-poc-pg psql -q -U postgres -c "CREATE DATABASE dbml_scratch" >/dev/null
docker exec dsl-poc-pg psql -q -U postgres -d dbml_scratch -c "CREATE SCHEMA application" >/dev/null
{ echo "SET search_path TO application;"; cat "$tmp/model.sql"; } \
  | docker exec -i dsl-poc-pg psql -q -v ON_ERROR_STOP=1 -U postgres -d dbml_scratch >/dev/null

docker run --rm -i --network dsl-poc -v dsl-poc-linkml-venv:/venv -e TABLES="$tables" \
  ghcr.io/astral-sh/uv:python3.12-bookworm /venv/bin/python - <<'PY'
import os
from sqlalchemy import MetaData, create_engine
from alembic.migration import MigrationContext
from alembic.autogenerate import compare_metadata

wanted = os.environ["TABLES"].split()
scratch = create_engine("postgresql+psycopg2://postgres:poc@dsl-poc-pg:5432/dbml_scratch")
metadata = MetaData(schema="application")
metadata.reflect(bind=scratch, only=wanted)

def include_object(obj, name, type_, reflected, compare_to):
    if type_ == "table":
        return obj.name in wanted
    return True

live = create_engine("postgresql+psycopg2://postgres:poc@dsl-poc-pg:5432/gigacron")
with live.connect() as conn:
    ctx = MigrationContext.configure(conn, opts={
        "include_schemas": True,
        "include_name": lambda name, type_, parents: type_ != "table" or name in wanted,
        "include_object": include_object,
        "compare_type": True,
        "compare_server_default": False,
    })
    diffs = compare_metadata(ctx, metadata)
for d in diffs:
    print(d)
print(f"{len(diffs)} difference(s)")
PY
