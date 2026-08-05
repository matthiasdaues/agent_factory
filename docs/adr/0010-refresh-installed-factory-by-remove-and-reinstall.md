---
id: 0010
status: accepted
evaluation: none
---

# Refresh an installed factory/ by remove-and-reinstall

## Context

`init-factory` copies the toolset's `factory/` into a target project exactly
once, on install. The install is deliberately idempotent and tracelessly
removable, but had no way to move an *existing* `factory/` forward when the
agent_factory checkout the project was installed from gets newer. The
workaround was manual: delete the project's `factory/` and re-run
`init-factory`. The install manifest recorded what init added for `remove- factory` but not *where the checkout it came from* was, so an update script
had no reliable way to know which repo to pull from.

## Decision

Introduce `factory/scripts/update-factory` as the single command for bringing
an installed project up to date with a factory checkout.

- **Remove-and-reinstall, not diff-and-merge.** `update-factory` replaces
  `target/factory/` with a byte-exact copy of the current checkout, then
  re-runs the *sourced* `init-factory` so every derived step outside `factory/`
  is brought up to date too: regenerated Codex adapters, re-verified runtime
  symlinks, re-merged guardrail/usage hook wiring, and a re-run pre-commit
  install. A recency merge (make `factory/` match the source "per element based
  on the file's timestamp") is rejected: the contract is fully determined by
  (target, source), so the merge can only add nondeterministic divergence, and
  git stamps every file with its checkout time rather than its last edit time,
  making mtime an unreliable oracle. `factory/` holds no project-owned state —
  it is git-ignored, manifest-whitelisted for removal, and meant to be an exact
  mirror of the checkout — so a wholesale replacement can never lose work.
- **Record the source at install time.** `init-factory` now writes the resolved
  checkout path to the manifest as `factory_source`. `update-factory` reads
  that as its default; `--source` overrides it for installs that predate the
  field or whose recorded path went stale.
- **`update-factory` never removes `.agent-factory/`.** Only `factory/` is
  replaced. The usage-tracking transcripts under `.agent-factory/usage/` and
  the lifecycle state under `.agent-factory/usage-control/` are preserved;
  `init-factory`'s lifecycle step only initializes-if-absent and repairs
  permissions, never deletes usage data. The manifest
  `.agent-factory/factory-install.json` is rewritten by the re-run — expected,
  it is the removal manifest — but usage data survives.

`evaluation: none` because remove-and-reinstall is the obvious path (it is the
shape the existing design already carved out for "the update script's job"),
and the only alternative considered, merge-by-recency, is a flawed idea rather
than a genuine tie.

## Consequences

**Easier**: a one-command, deterministic upgrade path that keeps an install
current and re-derives everything that depends on `factory/` content; the
recorded `factory_source` makes most updates flag-free; usage-tracking
continuity is guaranteed across updates.

**Harder**: updates delegate to the real `init-factory`, so they re-run its
idempotent wiring (including usage-runtime provisioning and `pre-commit install`) rather than a focused file swap — an acceptable cost for an explicit,
user-triggered upgrade that keeps wiring authoritative. A shipped
`factory_source` is an absolute path and can rot if the checkout is moved or
re-cloned elsewhere; `--source` is then required.
