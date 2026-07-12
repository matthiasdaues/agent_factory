---
id: ATAM-0001
title: Agent test iteration friction - no tight feedback loop without committing
status: resolved
severity: Major
category: Usability
date: 2026-07-12
found_by: architecture-review-agent
resolved_by: architecture-agent
resolved_at: 2026-07-12T11:21:00Z
resolution_summary: Added `run-tests --staged` mode for agent iteration. Agents can stage test files and verify before committing. Agent allowlist extended to include `factory/scripts/run-tests --staged` while bare test commands remain blocked. Documented in ADR-0003 Amendment, BR-024, BR-028.
tags: [ATAM, test-hooks, agent-workflow, TDD, resolved]
---

# ATAM-0001: Agent test iteration friction - no tight feedback loop without committing

## Summary

Agents are blocked from running test commands (BR-024), and tests only run via hooks on commit. This prevents agents from iterating "write test → run test → fix test → run again" within a single turn without committing. Agents writing tests in TDD style must commit after every test write to see results, creating high friction and polluting git history with micro-commits.

## Evaluated Quality Attribute

**Simplicity** - Minimal cognitive load

## Architecture Context

Per ADR-0003 and BR-024:

- `block-dangerous-git.sh` denies test commands (`pytest`, `npm test`, etc.) at PreToolUse
- Agents receive exit 2 denial with message: "Test execution blocked. Tests run via hooks only."
- Tests run automatically via pre-commit hook (`run-tests --changed-only`)
- Agents must commit to trigger hooks and see test output

## Sensitivity Point

Agent workflow depends on seeing test results to iterate on test code. The only way to trigger test execution is via git commit. This creates a forced coupling between "run tests" and "commit changes."

## Impact

**Development workflow friction**:

1. Agent writes `test_foo.py`
2. Agent must commit to see if test passes
3. If test fails, agent fixes it
4. Agent must commit again to verify fix
5. Repeat for every test iteration

**Consequences**:

- Micro-commits: Every test write/fix cycle creates a commit, cluttering git history
- No fail-fast feedback: Agent can't verify test syntax/basic logic without committing
- TDD anti-pattern: Test-Driven Development expects tight red-green-refactor loop (seconds), not commit-bounded loop (minutes)
- Agent confusion: Denied test commands may make agents think they can't verify their work at all

**ADR-0003 acknowledges this**:

> **Negative / risks**:
>
> - **Agents cannot verify their own test writes** — agent writes `test_foo.py`, commits, hook runs it. Agent sees pass/fail in hook output but cannot iterate "write test, run test, fix test, run again" within one turn without committing. Mitigated by agent seeing hook stderr (real-time test output during commit).

But "mitigated by seeing hook output" underestimates the severity. The mitigation doesn't address the commit-per-iteration problem.

## Tradeoff

**Agent prohibition (safety) vs. Agent iteration speed (usability)**:

- Blocking agents from running tests enforces single source of truth (hooks only)
- But prevents natural TDD workflow where tests are written and verified rapidly before committing

## Risk Classification

**Major** - This friction degrades agent developer experience significantly. While not a correctness risk (tests still run via hooks), it makes agent-authored test development slow and awkward.

## Proposed Mitigation

**Option 1: Pre-commit bypass for test-only changes** (minimal invasive)

Allow agents to trigger `run-tests --changed-only` without committing when only test files are modified. Requires:

1. New command: `factory/scripts/run-tests --changed-only --no-commit` (runs tests, doesn't require commit)
2. Agent allowlist includes this command (but NOT bare `pytest`)
3. Command only works when `git diff --name-only` shows only `test_*` / `*_test.*` files

**Trade-off**: Adds complexity (new mode), but preserves "tests run via factory scripts" principle.

**Option 2: Allow agent test commands in limited scope** (principle relaxation)

Permit agents to run tests with restrictions:

1. Only in interactive mode (not background)
2. Only changed-file scope (e.g., `pytest test_foo.py`, not `pytest .`)
3. Still require hook-triggered full run on commit

**Trade-off**: Weakens "single source of truth" principle - now two test paths exist (agent ad-hoc + hook authoritative).

**Option 3: Accept the friction as designed** (no change)

Document that agent test development is intentionally commit-bounded. Agents must commit frequently. Git history will have micro-commits; squash them later.

**Trade-off**: Simplest (no code change), but leaves developer experience degraded.

## Recommended Action

**Option 1** with scoping: `factory/scripts/run-tests --staged` command that runs tests on staged files only, without requiring commit completion. Agents can stage test files and run `run-tests --staged` to verify before committing.

**Implementation**:

- Add `--staged` mode to `run-tests` (reads `git diff --staged --name-only`)
- Agent allowlist includes `factory/scripts/run-tests --staged` (not bare test commands)
- Pre-commit hook still runs authoritative `--changed-only` on actual commit
- Both paths use same `run-tests` script, preserving single implementation

This preserves "tests run via factory mechanisms" while unblocking agent iteration.

## References

- docs/adr/0003-test-execution-via-hooks.md (Consequences § Negative)
- docs/spec/supplementary_specs/validation-rules.md § BR-024
- docs/spec/use_cases/UC-09-run-tests-via-hook.md

## Category Rationale

**Usability**: The architecture is technically correct (tests run deterministically) but imposes high friction on a common workflow (agent-authored TDD). Usability risk, not correctness risk.
