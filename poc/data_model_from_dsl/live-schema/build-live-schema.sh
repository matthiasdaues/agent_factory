#!/usr/bin/env bash
# Spike code for the data-model DSL PoC. Not shipped tooling.
#
# Builds Gigacron's live schema at the pinned commit in an ephemeral
# PostgreSQL container and dumps it as DDL. Every candidate story compares
# its model with this database. Usage:
#
#   build-live-schema.sh <gigacron-export-dir> <out-dir>
#
# <gigacron-export-dir> holds `git archive 40954f18... packages uv.lock
# pyproject.toml` from the Gigacron repository. It is mounted read-only.
# The database container stays up as `dsl-poc-pg` on network `dsl-poc`, so
# the stories can connect to it; stop it with `docker rm -f dsl-poc-pg`.
set -euo pipefail

src=$(realpath "$1")
out=$(realpath "$2")
mkdir -p "$out"

docker network inspect dsl-poc >/dev/null 2>&1 || docker network create dsl-poc >/dev/null
docker rm -f dsl-poc-pg >/dev/null 2>&1 || true
docker run -d --rm --name dsl-poc-pg --network dsl-poc \
  -e POSTGRES_PASSWORD=poc -e POSTGRES_DB=gigacron postgres:16 >/dev/null

until docker exec dsl-poc-pg pg_isready -U postgres -d gigacron >/dev/null 2>&1; do sleep 1; done
sleep 2

docker run --rm --network dsl-poc -v "$src":/src:ro \
  -e UV_PROJECT_ENVIRONMENT=/tmp/venv -e UV_LINK_MODE=copy \
  -e UV_DYNAMIC_VERSIONING_BYPASS=0.0.0 \
  ghcr.io/astral-sh/uv:python3.12-bookworm bash -c '
    set -euo pipefail
    cp -r /src /work && cd /work
    uv sync --frozen --no-dev --package gigacron-server --quiet \
      --python 3.13 --python-preference only-managed
    /tmp/venv/bin/python - <<"PY"
from sqlalchemy import create_engine, text
from gigacron_server.db.base import Base
from gigacron_server.db.schemas import APPLICATION_SCHEMA, AUDIT_SCHEMA
import gigacron_server.domain_registry.models  # noqa: F401
import gigacron_server.task_registry.models  # noqa: F401

engine = create_engine("postgresql+psycopg://postgres:poc@dsl-poc-pg:5432/gigacron")
with engine.begin() as conn:
    for schema in (APPLICATION_SCHEMA, AUDIT_SCHEMA):
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
Base.metadata.create_all(engine)
print("tables:", sorted(Base.metadata.tables))
PY
  '

docker exec dsl-poc-pg pg_dump -U postgres -d gigacron --schema-only --no-owner --no-privileges \
  > "$out/live-schema.sql"
echo "wrote $out/live-schema.sql"
