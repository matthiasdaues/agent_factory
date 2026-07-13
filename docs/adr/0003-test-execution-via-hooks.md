---
id: 0003
status: accepted
evaluation: none
---

# Test execution via unavoidable hooks only

## Context

Agent Factory's foundational principle "Agentic Creation, Deterministic Validation" (foundational-principles.md) states: agents create, hooks validate. No agent self-validation, no trust-based checking. This principle was already applied to commit gating (`transition-lint` pre-commit hook) and git safety (`block-dangerous-git.sh` PreToolUse hook). Test execution was ungoverned — neither enforced by hooks nor explicitly blocked for agents.

Without test hooks, three failure modes existed:

1. **Agent forgets to run tests** — writes code, commits, pushes without running test suite.
2. **Agent runs wrong tests** — executes partial suite, believes it's complete, reports "all tests pass."
3. **Agent misreports results** — test failures occur, agent doesn't surface them or misinterprets exit code.

All three violate the trust boundary: agents are noisy channels; their self-reported validation is unverified hearsay. Tests must run mechanically and unavoidably, like commit gates and git safety checks. This decision extends that pattern to test execution.

Three integration points emerged as natural enforcement boundaries:

- **Pre-commit** (fast feedback) — changed-file subset, sub-second, bypassable for WIP
- **Pre-push** (ready-to-share gate) — full suite, unavoidable, blocks work leaving local machine
- **Phase advance FSM gate** (phase boundary) — full suite, blocks state transition on red tests

Agent-commanded test execution (`pytest .`, `npm test`) became redundant once hooks covered all three boundaries. Leaving agents able to run tests created a second, competing validation path — which result is trustworthy, the hook's or the agent's? The SOLID Single Responsibility Principle and "single source of truth" (ADR-0002) both point to: one path, hook-triggered only.

This decision was not a choice among competing approaches; it was the only option consistent with the already-accepted validation principle. The decision being recorded is: extend "Agentic Creation, Deterministic Validation" to test execution, using the same unavoidable-hook pattern.

## Decision

Test execution happens via three unavoidable hooks only. Agents are blocked from running test commands.

**Hook integration points:**

1. **Pre-commit** — `run-tests --changed-only` fires on `git commit`. Fast subset (pytest `--lf`, jest `--onlyChanged`). Human bypass via `--no-verify` available (discouraged). Agent commits trigger same hook, no bypass.
2. **Pre-push** — `run-tests --full` fires on `git push`. Complete test suite, no filtering. No bypass for anyone. Work cannot leave local machine with failing tests.
3. **Phase advance FSM gate** — `script_exit_zero: factory/scripts/run-tests --full` evaluated as entry condition. Phase refuses to advance while tests are red.

**Agent iteration mode:**

`run-tests --staged` runs tests on staged files only, without requiring commit completion. Agents can stage test files (`git add test_foo.py`) and run `factory/scripts/run-tests --staged` to verify before committing. This mode is included in the agent allowlist (BR-024 permits `factory/scripts/run-tests --staged` while blocking bare test commands).

**Agent prohibition (BR-024):**

`block-dangerous-git.sh` deny patterns extended to include bare test commands: `pytest`, `npm test`, `go test`, `cargo test`, `python -m pytest`, `uv run pytest`, `yarn test`. Agent attempts receive exit 2 denial at PreToolUse: "Test execution blocked. Tests run via hooks only."

Agent allowlist includes `factory/scripts/run-tests --staged` for iteration during test development; bare test commands remain blocked.

**Framework detection (BR-023):**

`run-tests` auto-detects framework from project structure. Scans for all framework markers (`pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`); if multiple detected, fails loudly with error listing all found markers — monorepo multi-framework orchestration is not yet supported. Single framework detected → executes that framework's tests. No framework found → exit 2, operation blocked.

**Output:**

- JSON summary on stdout: `{"passed": N, "failed": M, "skipped": K, "duration_ms": T}`
- Test progress/failures on stderr (framework-native output)
- Exit codes: 0 (pass), 1 (test fail), 2 (framework missing/config error)

Agents can write tests (creation). Agents cannot run tests (validation). The hook's exit code is the sole trustworthy result.

## Amended

**Date**: 2026-07-12
**Reason**: ATAM review findings (ATAM-0001, ATAM-0002)

Post-review changes address two major gaps identified during architecture review:

1. **Agent test iteration friction (ATAM-0001)**: Original design blocked agents from iterating "write test → run test → fix test" without committing. Added `--staged` mode to `run-tests`, allowing agents to verify staged test files before committing. Agent allowlist extended to include `factory/scripts/run-tests --staged` while bare test commands remain blocked. Preserves "tests run via factory mechanisms" principle while unblocking TDD workflows.

2. **Monorepo multi-framework blind spot (ATAM-0002)**: Original first-match framework detection silently skipped additional frameworks in monorepos. Changed to detect ALL framework markers and fail loudly when multiple found, preventing silent partial coverage. Long-term multi-framework orchestration deferred as T-06.

Both changes strengthen the architecture without compromising the core "Agentic Creation, Deterministic Validation" principle. Single validation path (hook-triggered) remains; agent prohibition on bare test commands remains; added affordances improve usability (staged mode) and safety (fail-loud multi-framework).

## Consequences

**Positive:**

- **Tests always run** — pre-commit catches failures immediately (changed files), pre-push enforces full suite, phase gates block advancement on red tests. No agent amnesia, no partial runs mistaken for complete ones.
- **Single validation path** — hook result is the only result. No "agent says pass, hook says fail" conflict. Single source of truth.
- **Trust boundary enforced mechanically** — agents blocked at PreToolUse before command executes. No reliance on agent restraint or judgment.
- **Consistent with existing pattern** — follows same unavoidable-hook shape as `transition-lint` and `block-dangerous-git.sh`. Test execution is not special-cased.

**Negative / risks:**

- **Pre-commit can slow feedback** — even changed-file subset takes time. Mitigated by `--no-verify` escape hatch for WIP commits (discouraged but available). Pre-push has no bypass — deliberate.
- **Framework detection is heuristic** — `run-tests` scans for known markers; unrecognized frameworks report "no framework detected." Projects must use a supported framework or extend `run-tests`. Not every test setup auto-detects.
- **Monorepo multi-framework limitation** — detecting multiple frameworks fails loudly rather than running all. Multi-framework orchestration deferred as future work (T-06). Single-framework projects unaffected.
- **Phase advance becomes test-dependent** — a single failing test blocks phase transition. Deliberately strict; the alternative (advancing with red tests) violates the gate's purpose. Operator can fix tests or temporarily remove the `script_exit_zero` condition from FSM if gate is incorrect.

## Referenced from

- [UC-09 — Run Tests via Hook](../spec/use_cases/UC-09-run-tests-via-hook.md)
- [foundational-principles.md § Agentic Creation, Deterministic Validation](../../factory/rulebooks/conventions/foundational-principles.md#agentic-creation-deterministic-validation)
- [08_crosscutting_concepts.md § 8.1](../08_crosscutting_concepts.md#81-agentic-creation-deterministic-validation)
