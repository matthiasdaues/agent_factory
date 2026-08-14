---
id: RECON-0007
source: reconcile-spec
severity: major
category: defect
artifact: factory/scripts/init-factory
status: resolved
traces: [ST-0043]
---

# Codex usage hooks are inactive until trusted, but installation does not say so

**What is wrong:** `init-factory` merge-installs Codex `Stop` and
`SubagentStop` hooks, but Codex skips project-local command hooks until the user
explicitly trusts their current definitions. Installation emits no activation
instruction, and the factory guide previously presented installation as
operational capture. Synthetic tests invoke the adapter directly and therefore
do not prove that a real Codex session executes the installed hooks.

**Fix:** Make `init-factory` report the Codex `/hooks` trust step after wiring
the entries, retain that requirement in user documentation, and record a
trusted live Codex smoke test as acceptance evidence.

## Analysis

The deterministic part of the fix reports that Codex usage capture is installed
but inactive until the user opens `/hooks`, reviews the project hooks, and
trusts their current definitions. The instruction is emitted on fresh installs
and idempotent re-runs because Codex records trust against the current hook
definition and requires renewed review after a change.

Automated tests observe the public `init-factory` stdout boundary. Existing
installation and end-to-end tests remain the evidence that the hook entries are
merge-installed and that direct invocation of each installed command produces
canonical artifacts. Those synthetic tests cannot prove that Codex admitted
the hook through its trust gate.

## Resolution

`init-factory` now distinguishes installation from activation and reports the
required `/hooks` review-and-trust step on fresh installs and re-runs. Automated
tests cover both public installer paths.

On 2026-07-22, a user completed the interactive trust flow without bypassing
hook trust. A real Codex turn then produced exactly one canonical usage record
and an existing transcript-copy artifact. The metadata-only acceptance record
is [Codex usage-capture trusted smoke test](../reviews/codex-usage-capture-smoke-2026-07-22.md).
