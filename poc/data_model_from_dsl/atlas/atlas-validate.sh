#!/usr/bin/env bash
# Spike code for the data-model DSL PoC (DEC-07 wrapper). Not shipped tooling.
#
# Validates an Atlas HCL model and asserts the domain_id convention, which
# needs `atlas schema lint` (Atlas Pro) otherwise. A table whose comment is
# "domain-owned" must carry a column domain_id. Usage:
#
#   atlas-validate.sh <model.pg.hcl>
#
# Needs the dev database atlas_dev in container dsl-poc-pg, with the
# extension btree_gist installed, because Atlas declares extensions only for
# logged-in users.
set -euo pipefail

dir=$(cd "$(dirname "$1")" && pwd)
file=$(basename "$1")
dev="postgres://postgres:poc@dsl-poc-pg:5432/atlas_dev?sslmode=disable&search_path=public"

json=$(docker run --rm --network dsl-poc -v "$dir":/w -w /w arigaio/atlas:latest \
  schema inspect --url "file://$file" --dev-url "$dev" --format '{{ json . }}')

printf '%s' "$json" | docker run --rm -i ghcr.io/astral-sh/uv:python3.12-bookworm python3 -c '
import json, sys
realm = json.load(sys.stdin)
errors = [
    "table " + t["name"] + " is domain-owned but has no column domain_id"
    for s in realm["schemas"] for t in s.get("tables", [])
    if t.get("comment") == "domain-owned"
    and "domain_id" not in {c["name"] for c in t["columns"]}
]
for e in errors:
    print(f"Error: {e}", file=sys.stderr)
sys.exit(1 if errors else 0)
'
