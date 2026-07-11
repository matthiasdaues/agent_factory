# 0014. Call-to-action prompts via InvocationContext

**Status**: Accepted

> **Superseded for the orchestrator, 2026-07-12 (PhaseRunner collapse):** `PromptComposer` and the call-to-action templates moved to `factory/`; the orchestrator no longer composes prompts. See the repo-root `docs/spec/prd.md` and `docs/adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md`.

The composed prompt (agent definition + context + findings) contains everything the agent needs to know but no imperative signal to act. Without a closing directive, CLI agents remain inert — they have a role description but no "go". The prompt composer gains an `InvocationContext(phase, role, iteration)` parameter and appends a role-specific call-to-action as the final `# Call to Action` section.

Five templates cover every invocation path: author-first, author-loopback (re-addressing findings), reviewer-first, reviewer-loopback (re-reviewing after remediation), and standalone (`run-step`, no phase context). Templates are hardcoded f-strings in the composer — no external config, no user-facing knobs.

## Considered Options

- **A**: No call-to-action — rely on the agent definition's role description. Failed in practice: agents acknowledged context but didn't begin work.
- **B**: Generic "begin working" suffix. Too vague for reviewers vs authors; loses iteration context.
- **C**: Role-aware templates keyed on `InvocationContext`. Precise, testable, covers all state-machine paths.

Option C chosen. The `InvocationContext` is a frozen dataclass, required on `PromptComposer.compose()` — a breaking protocol change, but all callers (`PhaseRunner`, `run-step` handler) have the needed context already.
