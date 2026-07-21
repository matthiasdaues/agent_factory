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

## Pending live acceptance

Keep this finding open until a user completes this procedure:

1. Run `init-factory` against a disposable consumer repository.
2. Start interactive Codex in that repository without
   `--dangerously-bypass-hook-trust`.
3. Open `/hooks`, review the installed project `Stop` and `SubagentStop`
   commands, and explicitly trust them.
4. Complete a minimal real Codex turn and exit normally.
5. Verify that the installed lifecycle hook appended one canonical record under
   `.agent-factory/usage/` and persisted the transcript copy referenced by the
   record.

Acceptance evidence must record the date, Codex version, disposable repository
identifier, trusted hook events, generated record path, transcript-copy path,
and schema/usage checks. It must not include prompt or transcript contents. A
synthetic adapter invocation or a run using the hook-trust bypass does not count.
