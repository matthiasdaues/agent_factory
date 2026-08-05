---
id: FAGAN-0015
source: fagan-review
severity: minor
category: suggestion
artifact: factory/scripts/update-factory:53
status: open
traces: [ADR-0010]
---

# Corrupt manifest reported as "no manifest found"

**What is wrong:** `load_manifest` swallows `json.JSONDecodeError` and `OSError`
and returns `None`, so `main` cannot distinguish a missing manifest from one
that exists but is unreadable. When the file is corrupt, update-factory prints
"{target} is not an init-factory'd project — no {MANIFEST_PATH} found", which is
misleading: the manifest is present but malformed. `remove-factory` already
distinguishes the two cases (exit 1 only if the manifest "exists but can't be
read"), so this is also an inconsistency with the companion script.

**Fix:** Have `load_manifest` raise or return a distinct sentinel on a read
error, and have `main` emit a separate message — "manifest exists but is not
valid JSON" — and exit 1, matching remove-factory's distinction between absent
and corrupt.
