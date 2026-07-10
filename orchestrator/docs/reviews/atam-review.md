# ATAM Review — Agent Session Orchestrator

**Date**: 2026-07-06\
**Reviewer**: Architecture Review Agent (automated)\
**Architecture version**: Commit 436437f (post ADR-0010 spec alignment)\
**Scope**: Full ATAM review — all 17 quality scenarios

## 1. Reviewed Architecture

Reviewed chapters 01–11, `architecture.dsl`, ADRs 0001–0010, and the supplementary interface/state-machine specs. For ADR-0010 impact, the current implementation was spot-checked in `src/orchestrator/cli.py` and related adapters.

`arch-lint` summary: **0 errors, 0 warnings, 0 info** — exit code 0.

## 2. Quality Scenarios Evaluated

| ID    | Quality      | Verdict  |
| ----- | ------------ | -------- |
| QS-01 | Determinism  | Risk     |
| QS-02 | Determinism  | Non-risk |
| QS-03 | Determinism  | Non-risk |
| QS-04 | Isolation    | Non-risk |
| QS-05 | Safety       | Non-risk |
| QS-06 | Safety       | Non-risk |
| QS-07 | Safety       | Non-risk |
| QS-08 | Safety       | Non-risk |
| QS-09 | Safety       | Non-risk |
| QS-10 | Safety       | Non-risk |
| QS-11 | Operability  | Risk     |
| QS-12 | Operability  | Non-risk |
| QS-13 | Operability  | Non-risk |
| QS-14 | Portability  | Non-risk |
| QS-15 | Portability  | Non-risk |
| QS-16 | Bounded cost | Non-risk |
| QS-17 | Minimal deps | Non-risk |

## 3. Findings

### QS-01 — Repeatable gate outcome

- **Architectural approach**: `PreCommitGateRunner`, pinned hook configuration, structured `GateResult`, and package-relative lint scripts behind the tooling-assets boundary.
- **Sensitivity points**: the version and location of `scripts/` after ADR-0010; a tooling update outside the target repo can change gate behavior without any project artifact change.
- **Tradeoff points**: ADR-0010 improves context hygiene and reuse, but moves part of the deterministic gate input outside the project tree.
- **Verdict**: **Risk**
- **Notes**: The gate is no longer purely a function of committed project artifacts; it also depends on mutable external tooling. Same repo commit can yield a different gate result after a global tooling update.

### QS-02 — Error-only blocking

- **Architectural approach**: ADR-0003 plus the `GateResult` contract define non-zero blocking only for error-severity findings; warning/info remain non-blocking.
- **Sensitivity points**: hook discipline; each phase hook must keep honoring the error-only exit contract.
- **Tradeoff points**: extensibility via hooks versus the need to keep hook semantics uniform.
- **Verdict**: **Non-risk**
- **Notes**: The contract is explicit and centralized enough to support later hooks safely.

### QS-03 — Structured control-flow decisions

- **Architectural approach**: `InvocationResult`, `GateResult`, the findings schema, and the state machine keep decisions on structured signals rather than prose.
- **Sensitivity points**: any attempt to infer pass/fail from free text in adapters or logs would weaken the seam.
- **Tradeoff points**: richer diagnostics are available in logs, but control flow intentionally ignores them.
- **Verdict**: **Non-risk**
- **Notes**: The architecture now closes the earlier failure-classification gap with explicit `auth_error`, `config_error`, `errored`, and `timed_out` signals.

### QS-04 — Fresh reviewer session

- **Architectural approach**: ADR-0002 enforces a fresh subprocess per invocation behind `CLIAdapter`; reviewer and author share no in-process state.
- **Sensitivity points**: adapters must continue forcing a clean session and never silently resume prior CLI conversations.
- **Tradeoff points**: strong isolation versus process-start overhead and repeated prompt composition.
- **Verdict**: **Non-risk**
- **Notes**: Isolation is structural, not prompt-based, which is the right architectural choice for this quality goal.

### QS-05 — Bounded review loop

- **Architectural approach**: `PhaseRunner` routes recoverable failures to `LoopPolicy`, which caps retries at one decision point.
- **Sensitivity points**: misclassifying fatal failures as recoverable would waste iterations; the explicit failure flags are the key seam.
- **Tradeoff points**: autonomy inside a phase versus early halt on non-author-fixable faults.
- **Verdict**: **Non-risk**
- **Notes**: The documented `config_error` and gate-error paths remove the earlier cap-burning ambiguity.

### QS-06 — Gate crash halts cleanly

- **Architectural approach**: `GateResult.errored` and `timed_out` distinguish infrastructure/tooling failure from author-fixable findings.
- **Sensitivity points**: machine-readable hook output must stay parseable so findings and crashes remain distinguishable.
- **Tradeoff points**: reusing `pre-commit` keeps the core simple, but requires disciplined hook contracts.
- **Verdict**: **Non-risk**
- **Notes**: The halt path is now explicit in both ADR-0003 and the state machine.

### QS-07 — Adapter auth/availability halt

- **Architectural approach**: `CLIAdapter` exposes `auth_error`; the state machine halts before consuming an iteration.
- **Sensitivity points**: adapter-specific auth detection remains sensitive to CLI behavior changes.
- **Tradeoff points**: portability through a common port versus some CLI-specific classification logic inside adapters.
- **Verdict**: **Non-risk**
- **Notes**: This is an adapter-test obligation more than an architectural gap.

### QS-08 — Single active run

- **Architectural approach**: `RunLock`, `run.json` mode checks, and stale-lock reclamation rules in ADR-0005.
- **Sensitivity points**: lock acquisition/reclaim policy and PID liveness checks.
- **Tradeoff points**: safety over convenience; the design prefers refusing work to concurrent mutation.
- **Verdict**: **Non-risk**
- **Notes**: The combination of live-PID detection and explicit run mode is adequate.

### QS-09 — Atomic state writes

- **Architectural approach**: write-then-rename for `run.json` and finding files; ID allocation derives from existing findings.
- **Sensitivity points**: all persistence adapters must preserve the atomic-write discipline.
- **Tradeoff points**: many small files and extra fsyncs versus crash safety and inspectability.
- **Verdict**: **Non-risk**
- **Notes**: The design addresses both half-written records and ID reuse.

### QS-10 — Safe commit isolation

- **Architectural approach**: dedicated run branch, clean-tree precondition, no force-push, and stage-only declared outputs.
- **Sensitivity points**: startup enforcement of clean-tree and branch selection rules.
- **Tradeoff points**: operator safety versus the convenience of starting from a dirty tree.
- **Verdict**: **Non-risk**
- **Notes**: The architecture is conservative in the right place.

### QS-11 — Resume from checkpoint

- **Architectural approach**: `run.json` + findings store + run-branch HEAD define the checkpoint; resume is specified as idempotent within an iteration.
- **Sensitivity points**: after ADR-0010, the effective execution context also includes the tooling version/path, but that is not recorded in `run.json`.
- **Tradeoff points**: simple checkpoints versus full replayability across tool upgrades.
- **Verdict**: **Risk**
- **Notes**: A paused or halted run resumed after `git pull` + `uv tool install` may continue with different agent definitions, prompts, or lint scripts than the checkpoint was created with.

### QS-12 — Read-only status

- **Architectural approach**: `StatusService` projects persisted run state plus open-finding counts; `last_gate` is stored explicitly.
- **Sensitivity points**: the persisted schema must retain enough data for status without re-running anything.
- **Tradeoff points**: minimal state shape versus richer operator visibility.
- **Verdict**: **Non-risk**
- **Notes**: The current contracts now contain the previously missing gate data.

### QS-13 — Invocation logging

- **Architectural approach**: `Logger` port with default `.orchestrator/log.jsonl` sink and a dedicated `AGENT_INVOCATION` shape.
- **Sensitivity points**: every subprocess path must log consistently; gaps would reduce diagnostic value.
- **Tradeoff points**: observability versus extra I/O and another persistence artifact.
- **Verdict**: **Non-risk**
- **Notes**: Logging is now architecturally owned rather than implied.

### QS-14 — Add CLI by adapter

- **Architectural approach**: ADR-0001/0002 keep CLI specifics in `CLIAdapter`; the core depends only on ports.
- **Sensitivity points**: the shared `InvocationResult` contract must remain sufficient for all adapters.
- **Tradeoff points**: small common contract versus adapter-specific richness.
- **Verdict**: **Non-risk**
- **Notes**: The core-extension mechanism is sound. ADR-0010 introduces operational alignment concerns, but not a core portability break.

### QS-15 — Add deterministic check by hook

- **Architectural approach**: `pre-commit` is the gate bus; later checks are hook/config changes, not orchestrator changes.
- **Sensitivity points**: hooks must emit parseable machine results and obey timeout/exit conventions.
- **Tradeoff points**: configurability versus disciplined hook authoring.
- **Verdict**: **Non-risk**
- **Notes**: The architecture correctly localizes new checks to hook configuration.

### QS-16 — Timeout-bounded invocations

- **Architectural approach**: timeouts apply to agent invocations and gate execution; timeout outcomes are explicit failure classes.
- **Sensitivity points**: consistent timeout plumbing across adapters and `GateRunner`.
- **Tradeoff points**: bounded cost versus allowing long-running tools unlimited time.
- **Verdict**: **Non-risk**
- **Notes**: The architecture now covers the earlier gate-timeout hole.

### QS-17 — Stdlib-first installability

- **Architectural approach**: ADR-0006 and ADR-0007 keep runtime deps to stdlib + `jsonschema`, with `uv` handling packaging and tool distribution.
- **Sensitivity points**: future convenience libraries could erode the policy if admitted casually.
- **Tradeoff points**: minimal dependency surface versus framework convenience.
- **Verdict**: **Non-risk**
- **Notes**: The dependency policy is coherent and appropriately narrow.

## 4. Risk Summary

| ID   | Risk                                                                                                                                                                                                                                                                    | Quality | Severity | Proposed Mitigation                                                                                                                                                                                        |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R-01 | **Mutable external tooling after ADR-0010 weakens gate determinism.** `scripts/` and agent definitions can change outside the target repo, so the same project commit may gate or review differently after a global tooling update.                                     | Q1, Q4  | High     | Treat tooling as a versioned runtime input: record tooling commit/path in `run.json` and logs; optionally pin projects to a released tooling version or verify the expected tooling SHA before run/resume. |
| R-02 | **Resume checkpoints omit tooling identity.** `run.json` and findings capture phase state, but not which tooling version created it.                                                                                                                                    | Q4, Q1  | Medium   | Extend run state with tooling root + version/commit and fail fast on mismatch, or require an explicit operator override to resume with changed tooling.                                                    |
| R-03 | **Tooling-root drift between package-relative resolution, project symlinks, and current implementation can misalign behavior.** The docs describe package-relative assets plus symlinks, while the current CLI still prefers `.ai_tooling/` and old bootstrap behavior. | Q5, Q4  | Medium   | Make one asset root authoritative, validate symlink targets during `init`/startup, remove deprecated `.ai_tooling` fallback, and add an explicit compatibility check in the composition root.              |

## 5. Tradeoff Summary

| ID   | Tradeoff                                       | Qualities in tension                     | Current resolution                                                                                            |
| ---- | ---------------------------------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| T-01 | Fresh subprocess per invocation                | Isolation vs cost                        | Chosen in favor of isolation; timeouts and retry caps bound the cost.                                         |
| T-02 | `pre-commit` as shared gate bus                | Determinism vs hook-authoring discipline | Chosen in favor of determinism and reuse; hook contracts carry the discipline burden.                         |
| T-03 | Dedicated run branch + clean tree              | Safety vs operator convenience           | Chosen in favor of safety; the tool refuses unsafe starting states.                                           |
| T-04 | Package-relative tooling with project symlinks | Operability/reuse vs reproducibility     | ADR-0010 chooses reuse and cleaner project context; version capture is now needed to restore reproducibility. |
| T-05 | Stdlib-first runtime                           | Minimal deps vs framework convenience    | Chosen in favor of low runtime footprint; `jsonschema` remains the single justified exception.                |

## 6. ADR-0010 Impact Assessment

The updated **DSL, system scope, building block view, and deployment view are internally consistent**: all four describe tooling assets as package-relative resources exposed into target projects via symlinks, with the orchestrator core still depending on ports rather than concrete filesystem layout.

ADR-0010 nevertheless introduces three new architectural concerns:

1. **Determinism moved from project-local to environment-local.** Before tooling separation, agent definitions and lint scripts lived with the project checkout. After ADR-0010, they are shared mutable assets. That improves context hygiene, but it means a global tooling update can change gate and reviewer behavior for an unchanged project.
2. **Resume is no longer fully self-describing.** `run.json` plus findings are not a complete checkpoint once tooling lives outside the repo. A resumed run may execute with different prompts or hooks unless tooling identity is captured.
3. **Alignment between the documented architecture and the implementation is not yet complete.** The current `src/orchestrator/cli.py` still clones `.ai_tooling/`, writes `CONTEXT.md`, and resolves agents with `.ai_tooling` precedence. That is not a documentation inconsistency among the updated views; it is an implementation lag that can produce operational drift until the code is brought into line with ADR-0010.

**Overall judgment**: the core architecture remains sound, and the earlier ATAM failure-classification risks are materially addressed. The main remaining concerns are all ADR-0010 side effects around **tooling identity, reproducibility, and migration consistency**, not around the author/gate/reviewer control flow itself.
