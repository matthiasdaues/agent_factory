#!/usr/bin/env bash
# Spike code for the data-model DSL PoC (DEC-07 wrapper). Not shipped tooling.
#
# Compares a LinkML schema with Gigacron's live schema. LinkML has no
# comparison tool, so the wrapper:
#   1. generates SQLAlchemy code with gen-sqla,
#   2. renames each table from its class name to the class's `sql_table`
#      annotation and puts it in the PostgreSQL schema `application`,
#   3. runs alembic.autogenerate.compare_metadata against the live database.
# Usage:
#
#   linkml-compare.sh <schema.yaml> <table> [<table> ...]
#
# Only the named tables are compared. Needs the Docker volume
# dsl-poc-linkml-venv (linkml, alembic, psycopg2) and container dsl-poc-pg.
set -euo pipefail

dir=$(cd "$(dirname "$1")" && pwd)
file=$(basename "$1")
shift
tables="$*"

docker run --rm -i --network dsl-poc -v dsl-poc-linkml-venv:/venv -v "$dir":/w -w /w \
  -e TABLES="$tables" ghcr.io/astral-sh/uv:python3.12-bookworm bash -c "
    /venv/bin/gen-sqla '$file' > /tmp/model.py
    /venv/bin/python - '$file'
  " <<'PY'
import os, re, sys
from linkml_runtime import SchemaView
from sqlalchemy import MetaData, create_engine
from alembic.migration import MigrationContext
from alembic.autogenerate import compare_metadata

view = SchemaView(sys.argv[1])
names = {}
for cname, cls in view.all_classes().items():
    ann = cls.annotations.get("sql_table")
    if ann is not None:
        names[cname] = str(ann.value)

src = open("/tmp/model.py").read()
src = src.replace("Base = declarative_base()",
                  "from sqlalchemy import MetaData as _M\nBase = declarative_base(metadata=_M(schema='application'))")
for cname, table in names.items():
    src = src.replace(f"__tablename__ = '{cname}'", f"__tablename__ = '{table}'")
    src = re.sub(rf"ForeignKey\('{cname}\.", f"ForeignKey('application.{table}.", src)
ns = {}
exec(compile(src, "model.py", "exec"), ns)
metadata = ns["metadata"]

wanted = set(os.environ["TABLES"].split())
def include_name(name, type_, parent_names):
    if type_ == "table":
        return name in wanted
    return True
def include_object(obj, name, type_, reflected, compare_to):
    if type_ == "table":
        return obj.name in wanted
    return True

engine = create_engine("postgresql+psycopg2://postgres:poc@dsl-poc-pg:5432/gigacron")
with engine.connect() as conn:
    ctx = MigrationContext.configure(conn, opts={
        "include_schemas": True,
        "include_name": include_name,
        "include_object": include_object,
        "compare_type": True,
        "compare_server_default": False,
    })
    diffs = compare_metadata(ctx, metadata)
for d in diffs:
    print(d)
print(f"{len(diffs)} difference(s)")
PY
