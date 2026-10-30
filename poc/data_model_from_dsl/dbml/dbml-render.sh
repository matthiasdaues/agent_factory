#!/usr/bin/env bash
# Spike code for the data-model DSL PoC (DEC-07 wrapper). Not shipped tooling.
#
# dbml-renderer 1.0.31 has its own parser, which rejects the `checks` block
# of current DBML. This wrapper removes every `checks` block from a copy of
# the model and renders the copy to SVG. Usage:
#
#   dbml-render.sh <model.dbml> <out.svg>
#
# Needs the Docker volume dsl-poc-dbml-node with @softwaretechnik/dbml-renderer.
set -euo pipefail

model=$(realpath "$1")
out=$(realpath "$2")
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

python3 - "$model" "$tmp/render.dbml" <<'PY'
import re, sys
text = open(sys.argv[1]).read()
text = re.sub(r"\n  checks \{\n.*?\n  \}\n", "\n", text, flags=re.S)
open(sys.argv[2], "w").write(text)
PY

docker run --rm -u "$(id -u):$(id -g)" -v dsl-poc-dbml-node:/opt/dbml -v "$tmp":/w -w /w \
  node:20-bookworm /opt/dbml/node_modules/.bin/dbml-renderer -i render.dbml -o render.svg
cp "$tmp/render.svg" "$out"
