---
id: FAGAN-0005
source: fagan-review
severity: major
category: defect
artifact: factory/config/hooks/capture-usage.sh:68
status: resolved
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

**Resolution:** All four adapters now share one capture-specific lifecycle
implemented through the provisioned, hash-verified Python runtime. Claude,
Codex, and Copilot hooks synchronously validate the installation, register a
generation-fenced pending token, copy the provider transcript into private
scratch storage, and spawn the detached supervisor before returning. Pi keeps
its native stream registration but transfers ownership to the same supervisor.
Normalization and persistence remain detached. The supervisor retains sole
ownership of completion status, bounded diagnostics, and guarded cleanup.

Default removal drains every registered adapter; explicit cancel discards only
pending captures, while committing captures still drain. Installed races cover
both dispositions for Claude, Codex, and Copilot, including deletion of the
provider source after hook return, missing source/runtime/handoff cleanup,
Codex with a poisoned `node`, and absence of post-removal resurrection. A
durable transcript snapshot necessarily performs O(transcript-size) local I/O
inside the hook; no normalization, tokenization, or canonical persistence runs
there. The lifecycle is purpose-built for usage capture and is not a generic
queue or process framework.
