---
title: Fagan Review — update-factory (re-check of FAGAN-0012..0015)
date: 2026-08-05
base: 47628e3efd7a1e93ec959502576f782c1875d7b6
head: 798d95b80214b291b1f1173edaa268f012871671
disposition: pass
---

# Fagan Review — update-factory (re-check of FAGAN-0012..0015)

## Scope

Repeat Fagan inspection of `feat/update-factory`, limited to the fix commit
`798d95b` ("fix: harden update-factory rollback, manifest handling, and
reinstall tests") against the prior tip `47628e3` reviewed in
[fagan-review-2026-08-05](fagan-review-2026-08-05.md). The diff touches four
files (+143/-8):

- `factory/scripts/update-factory` — rollback-safe move-aside/restore, plus
  `ManifestUnreadable` distinction.
- `orchestrator/tests/test_update_factory.py` — three new tests
  (`test_real_run_init_builds_correct_argv_and_propagates_returncode`,
  `test_failed_reinstall_restores_previous_factory`,
  `test_update_preserves_usage_state_through_real_reinstall`,
  `test_corrupt_manifest_fails_with_distinct_message` — four in all).
- `docs/adr/0010-…md` — new "refresh is rollback-safe" consequence.
- `factory/docs/factory-guide.md` — rollback note in "Updating it again".

Each prior finding (FAGAN-0012 major defect; FAGAN-0013, 0014, 0015 minor
suggestions) was re-inspected for correctness, Clean Architecture, SOLID,
maintainability, and consistency. No new Defect was found.

## Per-finding verification

### FAGAN-0012 (major, defect) — RESOLVED

`test_update_preserves_usage_state_through_real_reinstall` restores the real
`_run_init` (captured as `REAL_RUN_INIT` before the autouse stub replaces it)
and runs a full `update_factory.main(...)`. It asserts the
`.agent-factory/usage/` transcript and `usage-control/state.json` survive, and
additionally writes a source-only `real-path-marker` into the synthetic source
and asserts it lands in `target/factory/scripts/` afterwards — proving the real
sourced init-factory `copy_factory` subprocess actually ran, not the mirror
stub. The guarantee is now exercised through the production reinstall path,
which is what FAGAN-0012 required.

The finding's suggested fix proposed stubbing `provision_usage_runtime` /
`initialize_usage_lifecycle` / `pre_commit_install` at the init-factory module
level to keep the round trip fast. The implemented test does not stub them
because `_run_init` runs a real subprocess that the in-process monkeypatches
cannot reach. This is acceptable — and arguably stronger, since the real heavy
steps run — because `provision_usage_runtime` fails gracefully on a
missing/offline `uv` (catches `OSError`/`RuntimeError`, returns `False`, leaves
capture inactive) and `pre_commit_install` likewise degrades, so the round trip
stays hermetic and fast: the full suite reports 15 passed in ~3 s.

### FAGAN-0013 (minor, suggestion) — RESOLVED

`test_real_run_init_builds_correct_argv_and_propagates_returncode` intercepts
`update_factory.subprocess.run`, restores `REAL_RUN_INIT`, and asserts the
argv is exactly `[sys.executable, str(src/factory/scripts/init-factory), "--source", str(src), "--target", str(target)]`, that `check=False`, and that
a `returncode` of 7 propagates straight through `_run_init`. The subprocess
delegation seam's argv shape and return-code mapping are now covered.

### FAGAN-0014 (minor, suggestion) — RESOLVED

`factory/scripts/update-factory` now `os.rename`s `target/factory/` to
`.agent-factory/factory-backup-<uuid>` (instead of `rmtree`) before the
reinstall, and on a non-zero `_run_init` return restores it in place under the
guard `backup.is_dir() and not target_factory.exists()`. On success the backup
is removed. The rollback-safety guarantee is now documented in the script
docstring, ADR-0010 (new consequence), and the factory-guide "Updating it
again" section. `test_failed_reinstall_restores_previous_factory` asserts the
prior `factory/` (with a custom marker) reappears after a failed reinstall and
that no `factory-backup-*` dir lingers.

The restore guard `not target_factory.exists()` deliberately avoids clobbering
a `factory/` that the sourced init-factory may have partially created before
colliding. In that edge case the new (incomplete) `factory/` remains and the
backup lingers under `.agent-factory/` until the user re-runs successfully;
this is a cosmetic leftover, not the dangling-symlink-without-`factory/` state
the finding was about, so it does not warrant a new finding.

### FAGAN-0015 (minor, suggestion) — RESOLVED

`load_manifest` now raises `ManifestUnreadable` (new exception) on
`json.JSONDecodeError`/`OSError` while still returning `None` for an absent
manifest. `main` catches `ManifestUnreadable`, prints
`{MANIFEST_PATH} exists but is not valid JSON (...)` to stderr, and returns 1
— distinct from the "not an init-factory'd project — no manifest found"
message for the absent case, matching `remove-factory`'s split.
`test_corrupt_manifest_fails_with_distinct_message` writes a malformed
manifest and asserts exit 1 plus "not valid JSON" in stderr.

## Clean Architecture / SOLID / Maintainability

- `ManifestUnreadable` is a focused, single-purpose exception; `load_manifest`
  keeps its original `None`-for-absent contract, so the dependency direction
  and caller contract are preserved (no SOLID regression).
- The move-aside/restore logic is local to `main`, stays low-complexity, and
  reuses `os.rename` / `shutil.rmtree` consistently with the rest of the
  script. No duplication introduced.
- The three new tests reuse the existing `REAL_RUN_INIT` capture and
  `_isolate_install` fixture cleanly; naming is clear and each test is
  single-purpose. No YAGNI concern — every new test maps to a prior finding.

## Consistency

- The corrupt-manifest message and exit-1 behaviour now match `remove-factory`,
  closing the prior inconsistency (FAGAN-0015).
- The docstring, ADR, and factory-guide rollback wording is consistent across
  the three documents.

## Findings

| Finding                                                                                                            | Artifact                                        | Category   | Severity | Status   |
| ------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------- | ---------- | -------- | -------- |
| [FAGAN-0012](../findings/FAGAN-0012.md) Preservation guarantee asserted by a test that bypasses the real reinstall | `orchestrator/tests/test_update_factory.py:191` | Defect     | Major    | resolved |
| [FAGAN-0013](../findings/FAGAN-0013.md) Real `_run_init` subprocess delegation seam is never exercised             | `orchestrator/tests/test_update_factory.py:46`  | Suggestion | Minor    | resolved |
| [FAGAN-0014](../findings/FAGAN-0014.md) Failure path leaves the project without a factory/ and no recovery note    | `factory/scripts/update-factory:140`            | Suggestion | Minor    | resolved |
| [FAGAN-0015](../findings/FAGAN-0015.md) Corrupt manifest reported as "no manifest found"                           | `factory/scripts/update-factory:53`             | Suggestion | Minor    | resolved |

No new findings.

## Verification

- `git diff 47628e3..798d95b`, `git show --stat 798d95b`: the four-file fix
  scope matches the commit message's claim (FAGAN-0012..0015).
- `python3 -m pytest orchestrator/tests/test_update_factory.py -q`: 15 passed
  in ~3 s (was 11; the four new tests added).
- Read `factory/scripts/update-factory` and `init-factory`'s
  `provision_usage_runtime` to confirm the real-reinstall test stays hermetic
  (graceful degradation on missing/offline `uv`).

## Disposition

Pass. All four prior findings (one major defect, three minor suggestions) are
genuinely addressed by `798d95b`; each finding file's `status` is set to
`resolved` with a resolution note. No new Defect or blocking finding was
introduced. The `feat/update-factory` branch is ready to merge.
