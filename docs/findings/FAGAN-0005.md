---
id: FAGAN-0005
source: fagan-review
severity: major
category: defect
artifact: factory/config/hooks/capture-usage.sh:68
status: open
traces: [ST-0042, ST-0043, ADR-0007, RECON-0012]
---

# Native hook captures can race Factory removal

**What is wrong:** the Claude, Codex, and Copilot lifecycle hooks launch
`usage-capture-runtime` in the background and immediately exit. Unlike Pi,
these detached captures do not register with the generation-fenced pending
registry, and `remove-factory` therefore cannot see or drain them. An uninstall
started immediately after a native hook can delete the runtime or persistence
paths before capture completes, losing token usage. If Python has already read
its inputs, it can instead finish after removal and recreate
`.agent-factory/usage` after the remover reported success. This violates both
the no-accounting-loss requirement and traceless removal. Existing uninstall
race tests exercise Pi only.

**Fix:** Reuse the existing generation-fenced, supervised durable handoff for
Claude, Codex, and Copilot native hooks. Each hook must durably register before
returning, while normalization and persistence remain detached and
best-effort. `remove-factory` must drain or explicitly cancel these
registrations through the same bounded lifecycle protocol. Add one installed
drain/cancel uninstall-race regression per adapter, proving the selected
disposition, no lost accepted capture, and no post-removal path recreation.
Keep the change narrow: do not introduce a general job queue, process manager,
or reusable background-work framework.
