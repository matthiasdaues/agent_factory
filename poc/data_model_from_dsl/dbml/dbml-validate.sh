#!/usr/bin/env bash
# Spike code for the data-model DSL PoC (DEC-07 wrapper). Not shipped tooling.
#
# dbml2sql prints "ERROR:" for a broken model but exits 0. This wrapper
# parses the model with DBML's own library @dbml/core, which throws on
# errors, and asserts the domain_id convention: every table in the
# TableGroup `domain_owned` must have a column domain_id. Usage:
#
#   dbml-validate.sh <model.dbml>
#
# Needs the Docker volume dsl-poc-dbml-node with @dbml/cli installed.
set -euo pipefail

dir=$(cd "$(dirname "$1")" && pwd)
file=$(basename "$1")

docker run --rm -i -v dsl-poc-dbml-node:/opt/dbml -v "$dir":/w -w /w \
  -e NODE_PATH=/opt/dbml/node_modules node:20-bookworm node - "$file" <<'JS'
const fs = require("fs");
const { Parser } = require("@dbml/core");
const file = process.argv[2];
let db;
try {
  db = new Parser().parse(fs.readFileSync(file, "utf8"), "dbmlv2");
} catch (e) {
  const diags = e.diags || [e];
  for (const d of diags) {
    const loc = d.location ? `(${d.location.start.line},${d.location.start.column})` : "";
    console.error(`Error: ${file}${loc}: ${d.message}`);
  }
  process.exit(1);
}
const errors = [];
for (const schema of db.schemas) {
  for (const group of schema.tableGroups) {
    if (group.name !== "domain_owned") continue;
    for (const table of group.tables) {
      if (!table.fields.some((f) => f.name === "domain_id")) {
        errors.push(`table ${table.name} is domain-owned but has no column domain_id`);
      }
    }
  }
}
for (const e of errors) console.error(`Error: ${e}`);
process.exit(errors.length ? 1 : 0);
JS
