---
id: FAGAN-0015
source: fagan-review
severity: minor
category: suggestion
artifact: factory/scripts/update-factory:53
status: resolved
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

## Resolution

Verified on `798d95b`. `load_manifest` now raises `ManifestUnreadable` (new
exception) on `json.JSONDecodeError`/`OSError` instead of returning `None`,
while still returning `None` for an absent manifest. `main` catches
`ManifestUnreadable`, prints
`{MANIFEST_PATH} exists but is not valid JSON (...)` to stderr, and returns 1
— distinct from the "not an init-factory'd project — no manifest found"
message for the absent case, matching remove-factory's split.
`test_corrupt_manifest_fails_with_distinct_message` writes a malformed
manifest and asserts exit 1 plus "not valid JSON" in stderr.
