# 0013. Working-tree gate — agents commit, orchestrator verifies

**Status**: Accepted — partially supersedes ADR-0003 (gating mechanism)

## Context

ADR-0003 established `pre-commit` as the deterministic gate bus. Under that model the *orchestrator* staged artifacts, committed on the run branch, and used the hook exit code to decide pass/fail. This worked for single-file phases (requirements, architecture) but breaks under parallelism: the implementation phase runs multiple stories concurrently inside one CLI-agent subprocess, and the orchestrator cannot know when or how many commits to create on behalf of the agent.

The fundamental tension: the orchestrator needs a gate, but the agent — not the orchestrator — knows when a unit of work is done and ready to commit.

### Alternatives

**A (status quo)**: Orchestrator stages + commits after agent exits. Requires the orchestrator to understand per-story outputs; blocks parallelism.

**B (agents commit)**: Agents commit their own work inside the subprocess; `pre-commit` hooks fire on each `git commit`; the orchestrator verifies a clean working tree after the agent exits. The hooks still provide deterministic gating, but the commit responsibility shifts to the agent.

**C (post-hoc linting)**: Agents write files, orchestrator runs linters directly (no `pre-commit`). Loses the commit-bound determinism that ADR-0003 established.

| Criterion                        | Weight | A: orch commits | B: agents commit | C: post-hoc lint |
| -------------------------------- | ------ | --------------- | ---------------- | ---------------- |
| Parallelism support (FR-M)       | 3      | -1              | +1               | +1               |
| Determinism bound to commit (Q1) | 3      | +1              | +1               | -1               |
| Confabulation detection          | 2      | 0               | +1               | 0                |
| Orchestrator simplicity          | 2      | 0               | +1               | 0                |
| No change to hook config         | 1      | +1              | +1               | -1               |
| **Weighted total**               |        | **+2**          | **+11**          | **-2**           |

B wins. The hooks still fire (ADR-0003's config stays valid), but the *who-commits* shifts from orchestrator to agent. The orchestrator's gate becomes a working-tree cleanliness check.

## Decision

1. **Agents commit their own work** inside the CLI subprocess. The `.pre-commit-config.yaml` hooks fire on each `git commit`, providing the same deterministic gating as before — the agent cannot land code that fails the hooks.

2. **The orchestrator's gate is `git status --porcelain`** after the agent process exits. `WorkingTreeGate.verify(cwd, exit_code) → GateResult`:

   - `exit 0 + clean tree` → **Passed**. Agent committed all work, hooks accepted it.
   - `exit 0 + dirty tree` → **Confabulation** → Halt. Agent claimed success but left uncommitted changes — a trust violation (VR-025).
   - `non-zero + dirty tree` → **Failed**. Clean tree (`git checkout .`), then RetryOrHalt.
   - `non-zero + clean tree` → **Failed** (infra/auth). RetryOrHalt or Halt per failure classification.

3. **Clean tree before retry**: after a failed iteration with a dirty tree, the orchestrator runs `git checkout . && git clean -fd` before the next author invocation, ensuring session isolation across iterations.

4. **ADR-0003 remains valid** for hook configuration — which hooks run, how they are versioned, how new phases add checks. Only the commit responsibility (who calls `git commit`) changes.

## Consequences

**Positive**

- Parallelism works: the CLI agent commits per-story internally; the orchestrator sees one atomic invocation.
- Confabulation detection: a new failure mode (exit 0 + dirty) that ADR-0003 could not express — the orchestrator can now detect when an agent lies about success.
- Simpler orchestrator: `PreCommitGateRunner` (stage, commit, parse hook output) shrinks to `WorkingTreeGate` (one `git status` call).

**Negative / risks**

- Agents must be instructed to commit. The call-to-action prompt (ADR-0014) and the agent definition files carry this instruction. An agent that ignores it triggers confabulation detection — fail-safe, not fail-silent.
- The orchestrator can no longer distinguish "hook findings" from "agent crash" via hook output parsing. This is acceptable: if hooks reject the commit, the agent process sees the failure and either retries or exits non-zero — the orchestrator only needs the final tree state.
- The once-only auto-fix re-stage (ADR-0003 ext. 5c) is now the agent's responsibility, not the orchestrator's.
