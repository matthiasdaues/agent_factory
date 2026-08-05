---
id: FAGAN-0014
source: fagan-review
severity: minor
category: suggestion
artifact: factory/scripts/update-factory:140
status: open
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
