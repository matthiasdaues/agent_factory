#!/usr/bin/env bash
# Spike code for the data-model DSL PoC (DEC-07 wrapper). Not shipped tooling.
#
# Renders every DiagramView of a DBML model to its own SVG. @dbml/core lists
# each view's tables; the wrapper copies those Table blocks, the Enums they
# use, and the Refs between them from the source, drops `checks` blocks that
# dbml-renderer cannot read, and renders the result. Usage:
#
#   dbml-views.sh <model.dbml> <out-dir>
set -euo pipefail

dir=$(cd "$(dirname "$1")" && pwd)
file=$(basename "$1")
out=$(realpath "$2")
mkdir -p "$out"

views=$(docker run --rm -i -v dsl-poc-dbml-node:/opt/dbml -v "$dir":/w:ro -w /w \
  -e NODE_PATH=/opt/dbml/node_modules node:20-bookworm node - "$file" <<'JS'
const fs = require("fs");
const { Parser } = require("@dbml/core");
const db = new Parser().parse(fs.readFileSync(process.argv[2], "utf8"), "dbmlv2");
for (const v of db.diagramViews || []) {
  console.log(v.name + " " + v.visibleEntities.tables.map((t) => t.name).join(" "));
}
JS
)

while read -r name tables; do
  [ -n "$name" ] || continue
  python3 - "$dir/$file" "$out/$name.dbml" $tables <<'PY'
import re, sys
src, dst, keep = open(sys.argv[1]).read(), sys.argv[2], set(sys.argv[3:])
blocks = {m.group(1): m.group(0) for m in re.finditer(r"^Table (\w+) \{\n.*?^\}\n", src, re.S | re.M)}
enums = {m.group(1): m.group(0) for m in re.finditer(r"^Enum (\w+) \{\n.*?^\}\n", src, re.S | re.M)}
tables = [re.sub(r"\n  checks \{\n.*?\n  \}\n", "\n", blocks[t], flags=re.S) for t in blocks if t in keep]
used = {e for e in enums if any(re.search(rf"\s{e}\s", t) for t in tables)}
refs = [l for l in src.splitlines() if l.startswith("Ref ")
        and all(t in keep for t in re.findall(r"(\w+)\.(?:\(|\w)", l.split(":", 1)[1]))]
open(dst, "w").write("\n".join([enums[e] for e in sorted(used)] + tables + refs) + "\n")
PY
  docker run --rm -u "$(id -u):$(id -g)" -v dsl-poc-dbml-node:/opt/dbml -v "$out":/w -w /w \
    node:20-bookworm /opt/dbml/node_modules/.bin/dbml-renderer -i "$name.dbml" -o "$name.svg"
  echo "view $name: $tables -> $out/$name.svg"
done <<< "$views"
