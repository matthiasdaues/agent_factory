---
id: FAGAN-0014
source: fagan-review
severity: minor
category: suggestion
artifact: factory/scripts/update-factory:140
status: resolved
traces: [ADR-0010]
---

# Failure path leaves the project without a factory/ and no recovery note

**What is wrong:** update-factory `shutil.rmtree(target_factory)` unconditionally
before delegating to the sourced init-factory. If init returns non-zero — a
`Collision` is the only such case, since `provision_usage_runtime` and
`pre_commit_install` fail gracefully — update-factory returns that code but
`target/factory/` is already gone, leaving dangling symlinks in `.claude/`,
`.github/`, `.pi/` and a stale removal manifest until the user resolves the
collision and re-runs. The script docstring and ADR-0010 note that init "stops
on a collision" but do not state this intermediate broken state or how to
recover. The byte-exact-mirror guarantee is only reached on success; on
failure the project is worse off than before the update.

**Fix:** Either rename `target/factory/` to a side backup and restore it when
init returns non-zero (copy-then-swap rather than remove-then-reinstall), or
add an explicit recovery note to the docstring and the factory-guide
"Updating it again" section: resolve the reported collision and re-run
`update-factory` to finish the refresh.

## Resolution

Verified on `798d95b`. update-factory now `os.rename`s `target/factory/` to
`.agent-factory/factory-backup-<uuid>` (no `rmtree`) before the reinstall, and
on a non-zero `_run_init` return restores it in place (guarded by
`backup.is_dir() and not target_factory.exists()`), so the project is never
left without a `factory/`. On success the backup is `rmtree`'d. The rollback
is documented in the script docstring, ADR-0010 (new "refresh is
rollback-safe" consequence), and the factory-guide "Updating it again"
section. `test_failed_reinstall_restores_previous_factory` asserts the prior
`factory/` (with a custom marker) reappears after a failed reinstall and that
no `factory-backup-*` dir lingers.
