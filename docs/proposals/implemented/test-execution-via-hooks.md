---
schema_version: 2
title: "Test Execution via Hooks"
status: implemented
owner: agent-factory
created: 2026-07-12
updated: 2026-07-29
supersedes:

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: false
  boundaries:
    - factory/scripts/run-tests
    - factory/config/pre-commit-config.yaml

governance:
  assurance: high
  risk_domains:
    - reliability
    - operations

estimate:
  as_of: 2026-07-29
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
---

# Implementation Strategy: Test Execution via Hooks

**Principle**: Creation is agentic, validation is deterministic and MUST be triggered mechanically through unavoidable hooks.

**Goal**: Make test execution part of the hook infrastructure globally, not agent-driven commands.

______________________________________________________________________

## Current State

✅ **Existing Hook Infrastructure:**

- Pre-commit hooks: mdformat, ruff, spec-lint, arch-lint, backlog-lint, transition-lint
- PreToolUse hooks: block-dangerous-git.sh (both CLIs)
- All hooks use zero-install pattern (uvx, stdlib Python)

❌ **Missing:**

- No `factory/scripts/run-tests` implementation
- No test hooks in pre-commit-config.yaml
- FSM references `script_exit_zero: factory/scripts/run-tests` but it doesn't exist
- No detection of project test framework (pytest/jest/go test/etc)

______________________________________________________________________

## Design Principles

1. **Hook-triggered, not agent-commanded** — tests run via pre-commit, pre-push, or phase advance, never via agent shell commands
2. **Framework detection** — auto-detect test runner from project structure (pytest/jest/go test/cargo test/etc)
3. **Performance-aware** — don't block fast commits; run full suite only at phase boundaries
4. **Zero additional install** — leverage what the project already has (uv run, npm, go test)
5. **Fail-fast, explicit** — test failures MUST block commits/advances with clear error messages

______________________________________________________________________

## Implementation Strategy

### Phase 1: Test Runner Script (Foundation)

**Create:** `factory/scripts/run-tests`

**Responsibilities:**

1. Auto-detect test framework from project structure
2. Run appropriate test command
3. Exit 0 on pass, non-zero on fail
4. Emit machine-readable output (JSON summary) + human-readable stderr

**Detection logic:**

```python
# Ordered by specificity
if exists("pyproject.toml") and contains("pytest"):
    return "uv run pytest"
elif exists("package.json") and contains("jest"):
    return "npm test"
elif exists("go.mod"):
    return "go test ./..."
elif exists("Cargo.toml"):
    return "cargo test"
elif exists("*.rs") and no_cargo:
    return "rustc --test && ./tests"
# ... fallback: error "no test framework detected"
```

**Exit codes:**

- `0` — all tests pass
- `1` — tests fail
- `2` — test framework not detected or not runnable

**Output:**

```json
{"passed": 247, "failed": 0, "skipped": 3, "duration_ms": 1234}
```

______________________________________________________________________

### Phase 2: Hook Integration Points

Three integration points, each serving a different validation tier:

#### 2A. Pre-Commit Hook (Fast Subset)

**When:** Every `git commit`
**Scope:** Changed files only (fast subset)
**Implementation:**

```yaml
- id: test-changed
  name: test (changed files only)
  entry: factory/scripts/run-tests --changed-only
  language: system
  pass_filenames: false
  stages: [commit]
```

**Rationale:** Fast feedback loop. Don't block every commit with full suite.
**Escape hatch:** `git commit --no-verify` for WIP commits (discouraged but available)

#### 2B. Pre-Push Hook (Full Suite)

**When:** Every `git push`
**Scope:** Full test suite
**Implementation:**

```yaml
- id: test-full
  name: test (full suite)
  entry: factory/scripts/run-tests --full
  language: system
  pass_filenames: false
  stages: [push]
```

**Rationale:** Unavoidable gate before sharing work. Full regression check.
**No escape hatch:** Push is the "ready to share" boundary.

#### 2C. Phase Advance Gate (FSM Exit Condition)

**When:** `phase advance` checks exit_conditions
**Scope:** Full test suite
**Implementation:** Already designed in bug-fix.fsm.yml

```yaml
tests_pass:
  type: script_exit_zero
  script: factory/scripts/run-tests --full
```

**Rationale:** Phase boundary = quality gate. No advancement on red tests.
**Enforcement:** `phase advance` refuses if condition unmet.

______________________________________________________________________

### Phase 3: Agent Prohibition

**Block agents from running tests directly:**

Add to `block-dangerous-git.sh` patterns:

```bash
# Test execution must go through hooks, not agent commands
"pytest"
"npm test"
"go test"
"cargo test"
"python -m pytest"
"uv run pytest"
```

**Why:** Agents can't be trusted to run tests correctly or report failures honestly. Hook-triggered execution is the only trustworthy path.

**Exception:** Agents CAN write test files. They CANNOT execute them.

______________________________________________________________________

### Phase 4: Opt-in Rollout

**Stage 1: Optional (week 1)**

- Create `factory/scripts/run-tests`
- Add `--changed-only` and `--full` modes
- Document in factory-guide.md
- No pre-commit hook yet (manual `factory/scripts/run-tests` only)

**Stage 2: Pre-commit fast subset (week 2)**

- Add `test-changed` pre-commit hook to factory/config/pre-commit-config.yaml
- Set `stages: [commit]` so it doesn't run on push
- Announce: "Tests now run on commit (changed files only)"

**Stage 3: Pre-push full suite (week 3)**

- Add `test-full` pre-push hook
- Set `stages: [push]`
- Announce: "Full test suite now blocks push"

**Stage 4: FSM integration (week 4)**

- Enable `script_exit_zero` condition evaluation in `factory/scripts/phase`
- Update bug-fix.fsm.yml and greenfield-development.fsm.yml
- Announce: "Phase advance now enforces test passage"

**Stage 5: Agent prohibition (week 5)**

- Add test command patterns to block-dangerous-git.sh
- Announce: "Agents can no longer run tests directly"

______________________________________________________________________

## factory/scripts/run-tests Implementation Skeleton

```python
#!/usr/bin/env python3
"""run-tests — framework-agnostic test runner for hook integration.

Auto-detects project test framework and runs appropriate command.
Exit 0 on pass, non-zero on fail. Emits JSON summary + human stderr.

Modes:
  --changed-only    Run tests for changed files only (fast, pre-commit)
  --full            Run full test suite (slow, pre-push / phase advance)
  --detect          Print detected framework and exit (diagnostic)
"""

import json
import subprocess
import sys
from pathlib import Path


def detect_framework():
    """Return (framework_name, command_argv) or (None, None)."""
    if Path("pyproject.toml").exists():
        # Check for pytest in deps
        return ("pytest", ["uv", "run", "pytest", "--tb=short", "--quiet"])
    elif Path("package.json").exists():
        return ("npm", ["npm", "test"])
    elif Path("go.mod").exists():
        return ("go", ["go", "test", "./..."])
    elif Path("Cargo.toml").exists():
        return ("cargo", ["cargo", "test", "--quiet"])
    return (None, None)


def run_tests(mode="full"):
    framework, cmd = detect_framework()

    if not framework:
        print("ERROR: No test framework detected", file=sys.stderr)
        sys.exit(2)

    if mode == "changed-only":
        # TODO: add framework-specific changed-file filtering
        cmd.append("--lf")  # pytest: last-failed

    print(f"Running {framework} tests ({mode})...", file=sys.stderr)
    result = subprocess.run(cmd, capture_output=False)

    # TODO: parse output for JSON summary
    summary = {"passed": "?", "failed": "?" if result.returncode else 0}
    print(json.dumps(summary))

    sys.exit(result.returncode)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--changed-only", action="store_const", const="changed", dest="mode"
    )
    parser.add_argument("--full", action="store_const", const="full", dest="mode")
    parser.add_argument("--detect", action="store_true")
    parser.set_defaults(mode="full")
    args = parser.parse_args()

    if args.detect:
        fw, _ = detect_framework()
        print(fw or "none")
        sys.exit(0)

    run_tests(args.mode)
```

______________________________________________________________________

## Success Criteria

✅ **After full rollout:**

1. No agent can run test commands (blocked by PreToolUse hook)
2. Every commit runs changed-file tests automatically (pre-commit)
3. Every push runs full suite automatically (pre-push)
4. Every `phase advance` refuses if tests fail (FSM exit_condition)
5. Zero additional install burden (uses project's existing test framework)
6. Clear error messages on failure (which test failed, how to fix)

✅ **Behavioral proof:**

- Agent writes test file → commit succeeds, tests run, agent sees pass/fail in hook output
- Agent tries `pytest .` → blocked by PreToolUse hook
- Human commits with failing test → commit blocked, clear error
- Human runs `phase advance` with red tests → advancement refused

______________________________________________________________________

## Documentation Updates

**factory/docs/factory-guide.md § Linting and gating:**
Add row:

```
| factory/scripts/run-tests | pre-commit, pre-push, phase advance | Auto-detected test suite |
```

**factory/rulebooks/conventions/foundational-principles.md:**
Already updated with "Agentic Creation, Deterministic Validation" — tests are now the canonical example.

**factory/playbooks/\*.fsm.yml:**
Add `tests_pass` condition to every IMPLEMENTATION phase exit_conditions.

______________________________________________________________________

## Risk Mitigation

**Risk 1: Slow full suite blocks fast iteration**

- Mitigation: `--changed-only` mode on commit, `--full` only on push/advance
- Escape: `--no-verify` for WIP commits (document as anti-pattern)

**Risk 2: Framework detection fails**

- Mitigation: Exit 2 with clear error, point at manual `factory/scripts/run-tests --detect`
- Fallback: Document override via `.current-work/test-config.yml`

**Risk 3: Existing projects have broken tests**

- Mitigation: Rollout is opt-in per stage; announce each stage clearly
- Fallback: Projects can disable hook temporarily to fix backlog

**Risk 4: Agent finds workaround (e.g., writes script that runs tests)**

- Mitigation: Block scripts that shell out to test commands
- Long-term: This is a discipline problem, not a technical one

______________________________________________________________________

## Next Steps

1. Implement `factory/scripts/run-tests` (Phase 1)
2. Test against agent_factory (pytest), orchestrator (pytest), example JS/Go projects
3. Add pre-commit hook as opt-in (Phase 2A)
4. Gather feedback, iterate on framework detection
5. Roll out remaining phases (2B, 2C, 3, 4, 5) per timeline above

______________________________________________________________________

## Referenced from

- factory/playbooks/bug-fix.fsm.yml (tests_pass condition)
- factory/rulebooks/conventions/foundational-principles.md (validation principle)
- docs/spec/supplementary_specs/validation-rules.md (script_exit_zero)
