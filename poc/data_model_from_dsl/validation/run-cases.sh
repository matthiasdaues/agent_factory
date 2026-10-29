#!/usr/bin/env bash
# Spike code for the data-model DSL PoC: runs every validation-depth case.
#
# For each case in cases.tsv it records the exit code and the first error line
# of: dbml2sql (DBML's CLI), dbml-validate.sh (DBML's parser @dbml/core plus the
# domain rule), linkml-lint --ignore-warnings, and linkml-validate.sh (lint
# plus the domain rule). Writes results.tsv and one log per run under runs/.
# Usage: ./run-cases.sh   (run from poc/data_model_from_dsl/validation)
set -uo pipefail

here=$(cd "$(dirname "$0")" && pwd)
cd "$here"
mkdir -p runs
dbml_validate=$(realpath ../dbml/dbml-validate.sh)
linkml_validate=$(realpath ../linkml/linkml-validate.sh)

first_error() { grep -m1 -i -E "error|expect|not defined|duplicate|does not exist|unknown|invalid" "$1" | sed -E 's/^[[:space:]]+//' | cut -c1-140; }

echo -e "case\tdbml2sql\tdbml_core\tdbml_message\tlinkml_lint\tlinkml_wrapper\tlinkml_message" > results.tsv
tail -n +2 cases.tsv | while IFS=$'\t' read -r cid desc dfile lfile; do
  docker run --rm -v dsl-poc-dbml-node:/opt/dbml -v "$here/cases":/w:ro -v "$here/runs":/out -w /w \
    node:20-bookworm /opt/dbml/node_modules/.bin/dbml2sql --postgres "$dfile" -o "/out/$cid.sql" \
    > "runs/$cid-dbml2sql.out" 2>&1
  d_cli=$?
  "$dbml_validate" "cases/$dfile" < /dev/null > "runs/$cid-dbml-core.out" 2>&1
  d_core=$?
  d_msg=$(first_error "runs/$cid-dbml-core.out")
  if [ "$lfile" = "n/a" ]; then
    l_lint="n/a"; l_wrap="n/a"; l_msg="not applicable"
  else
    docker run --rm -v dsl-poc-linkml-venv:/venv -v "$here/cases":/w:ro -w /w \
      ghcr.io/astral-sh/uv:python3.12-bookworm /venv/bin/linkml-lint --ignore-warnings "$lfile" \
      > "runs/$cid-linkml-lint.out" 2>&1
    l_lint=$?
    "$linkml_validate" "cases/$lfile" < /dev/null > "runs/$cid-linkml-wrapper.out" 2>&1
    l_wrap=$?
    l_msg=$(grep -m1 -E "^\s+error|^Error|Traceback|Exception|ValueError" "runs/$cid-linkml-lint.out" "runs/$cid-linkml-wrapper.out" | sed -E 's/^[^:]+:[[:space:]]*//' | cut -c1-140)
  fi
  echo -e "$cid\t$d_cli\t$d_core\t${d_msg:-}\t$l_lint\t$l_wrap\t${l_msg:-}" | tee -a results.tsv
done
