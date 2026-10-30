#!/usr/bin/env bash
# Spike code for the data-model DSL PoC (DEC-07 wrapper). Not shipped tooling.
#
# Runs linkml-lint, then asserts the domain_id convention: a class annotated
# `domain_owned: true` must have a slot domain_id. LinkML's linter has no
# custom rules for this. Usage:
#
#   linkml-validate.sh <schema.yaml>
#
# Needs the Docker volume dsl-poc-linkml-venv with linkml installed.
set -euo pipefail

dir=$(cd "$(dirname "$1")" && pwd)
file=$(basename "$1")
run() {
  docker run --rm -i -v dsl-poc-linkml-venv:/venv -v "$dir":/w -w /w \
    ghcr.io/astral-sh/uv:python3.12-bookworm "$@"
}

run /venv/bin/linkml-lint --ignore-warnings "$file" >/dev/null
run /venv/bin/python - "$file" <<'PY'
import sys
from linkml_runtime import SchemaView

view = SchemaView(sys.argv[1])
errors = []
for name, cls in view.all_classes().items():
    owned = cls.annotations.get("domain_owned")
    if owned is not None and str(owned.value).lower() == "true":
        if "domain_id" not in view.class_slots(name):
            errors.append(f"class {name} is domain-owned but has no slot domain_id")
for e in errors:
    print(f"Error: {e}", file=sys.stderr)
sys.exit(1 if errors else 0)
PY
