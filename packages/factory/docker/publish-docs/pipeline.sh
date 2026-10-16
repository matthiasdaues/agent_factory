#!/bin/bash
# pipeline.sh — Stages 2 to 5 of publish-docs, run inside the render image.
#
# What: Assembles the documents, compiles them with Quarkdown, renders and
#       checks the PDF.
# When: Called by `publish-docs pdf` after the Structurizr export.
# By:   packages/factory/scripts/publish-docs, through `docker run`.
#
# Mounts: /docs (project docs, read-only), /factory (factory files,
# read-only), /build (build directory). Provenance arrives in PUBLISH_* env.
# Exit codes: 0 PDF written to /build/out.pdf, 1 a check failed, 2 a
# precondition failed.

set -uo pipefail

dirty=()
[ "${PUBLISH_DIRTY:-0}" = "1" ] && dirty=(--dirty)

python3 /factory/scripts/_docs_assemble.py \
  --docs /docs --out /build/src --views /build/model/assets/images \
  --factory-css /factory/docker/publish-docs/publish.css \
  --project "${PUBLISH_PROJECT}" --sha "${PUBLISH_SHA}" --branch "${PUBLISH_BRANCH}" \
  --built-at "${PUBLISH_BUILT_AT}" "${dirty[@]}" || exit $?

rm -rf /build/html
if ! (cd /build/src && quarkdown c main.qd -o /build/html); then
  echo "FAIL quarkdown: compile failed" >&2
  exit 1
fi
index=$(find /build/html -maxdepth 2 -name index.html | head -1)
if [ -z "${index}" ]; then
  echo "FAIL quarkdown: no index.html produced" >&2
  exit 1
fi

node /factory/docker/publish-docs/render.js "$(dirname "${index}")" /build/out.pdf /build/src/expected.json
