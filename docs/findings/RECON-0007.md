---
id: RECON-0007
source: reconcile-spec
severity: major
category: defect
artifact: factory/scripts/init-factory
status: open
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
