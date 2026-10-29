#!/usr/bin/env bash
# Spike code for the data-model DSL PoC (DEC-07 wrapper). Not shipped tooling.
#
# Mermaid has no model checker and no comparison tool. This wrapper parses
# the erDiagram with regular expressions. Usage:
#
#   mermaid-check.sh validate <model.mmd>
#   mermaid-check.sh compare  <model.mmd> <table> [<table> ...]
#
# validate: runs mmdc for syntax, then fails when a relationship names an
#   undeclared entity, or when an entity listed on the `%% domain-owned:`
#   line has no attribute domain_id.
# compare: compares attribute names per entity with the columns of the live
#   database, schema `application`. Mermaid states no nullability and no
#   constraints beyond PK/FK/UK markers, so only column names are compared.
set -euo pipefail

mode=$1
dir=$(cd "$(dirname "$2")" && pwd)
file=$(basename "$2")
shift 2
tables="$*"

if [ "$mode" = validate ]; then
  docker run --rm -u "$(id -u):$(id -g)" -v "$dir":/data minlag/mermaid-cli:latest \
    -i "$file" -o /tmp/check.svg >/dev/null
fi

docker run --rm -i --network dsl-poc -v dsl-poc-linkml-venv:/venv -v "$dir":/w:ro -w /w \
  -e MODE="$mode" -e TABLES="$tables" ghcr.io/astral-sh/uv:python3.12-bookworm \
  /venv/bin/python - "$file" <<'PY'
import os, re, sys

text = open(sys.argv[1]).read()
entities = {}
for m in re.finditer(r"^\s*([A-Z_]+) \{\n(.*?)^\s*\}", text, re.S | re.M):
    entities[m.group(1)] = [line.split()[1] for line in m.group(2).strip().splitlines()]
rels = re.findall(r"^\s*([A-Z_]+) \S+ ([A-Z_]+) :", text, re.M)

if os.environ["MODE"] == "validate":
    errors = []
    for a, b in rels:
        for e in (a, b):
            if e not in entities:
                errors.append(f"relationship names undeclared entity {e}")
    owned = re.search(r"^%% domain-owned: (.*)$", text, re.M)
    for e in (owned.group(1).split() if owned else []):
        if "domain_id" not in entities.get(e, []):
            errors.append(f"entity {e} is domain-owned but has no attribute domain_id")
    for e in errors:
        print(f"Error: {e}", file=sys.stderr)
    sys.exit(1 if errors else 0)

import psycopg2
conn = psycopg2.connect("host=dsl-poc-pg dbname=gigacron user=postgres password=poc")
cur = conn.cursor()
count = 0
for table in os.environ["TABLES"].split():
    cur.execute("select column_name from information_schema.columns "
                "where table_schema = 'application' and table_name = %s", (table,))
    live = {r[0] for r in cur.fetchall()}
    model = set(entities.get(table.upper(), []))
    if not live:
        print(f"table {table}: not in the live schema")
        count += 1
        continue
    for c in sorted(model - live):
        print(f"table {table}: column {c} in the model, not in the live schema")
        count += 1
    for c in sorted(live - model):
        print(f"table {table}: column {c} in the live schema, not in the model")
        count += 1
print(f"{count} difference(s)")
PY
