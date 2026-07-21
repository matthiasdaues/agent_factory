[back to index](README.md)

# 8. Cross-cutting Concepts

## 8.1 Agentic Creation, Deterministic Validation

**Principle**: Creation is agentic; validation is deterministic. Where a check must be *unavoidable* — tests, phase-order gates, dangerous commands — it is triggered mechanically through hooks an agent cannot skip. Other deterministic validators run *on demand*, invoked by a playbook, agent, or operator; they trade unavoidability for reproducibility, and are trustworthy because their result is a mechanical exit code, not an agent's word.

Derived from [`factory/rulebooks/conventions/foundational-principles.md`](../factory/rulebooks/conventions/foundational-principles.md).

### What It Means

| Concern                      | Who/What Owns It                                                               | Enforced How                                                                                                   |
| ---------------------------- | ------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| **Creation**                 | Agents and humans write specs, code, tests, docs, ADRs                         | Agentic — LLM-driven or human-authored, inherently non-deterministic                                           |
| **Validation**               | Scripts check artifacts against predefined, state-dependent rules              | Deterministic — hooks, exit codes, no judgment calls                                                           |
| Tests run                    | Hooks (pre-commit, pre-push, FSM gate) invoke `run-tests`                      | `script_exit_zero` gate condition, exit 0/1/2                                                                  |
| Commits gated                | Pre-commit hook runs `transition-lint`                                         | Blocks staged files outside current phase's `outputs:` globs                                                   |
| Git safety                   | PreToolUse hook runs `block-dangerous-git.sh`                                  | Denies commands before execution, exit 2                                                                       |
| Phase gates                  | `phase advance` evaluates FSM `entry_conditions`                               | Refuses (exit 1) if any condition unmet, lists all failures                                                    |
| Research artifacts validated | `schema-validate` (stage 1) and `policy-validate` (stage 2), invoked on demand | Deterministic — exit codes, no judgment; invoked by the research playbook/agents, not hook-enforced (see §8.6) |

### Why It Matters

**Trust boundary**: Agents are noisy channels. You cannot trust an agent to validate its own work correctly, report test failures honestly, or obey soft guidelines ("please don't push"). Validation must be external, unavoidable, and mechanical.

**Separation of concerns**: Agents are excellent at generation (specs, code, tests). They are poor at discipline (running the right tests, not bypassing gates). Hooks enforce discipline; agents create value. This separation makes AI-assisted output shippable.

**No self-validation**: An agent reporting "tests passed" is unverified hearsay. `run-tests` exiting 0 from a pre-commit hook is a fact. The architecture treats agent output as untrusted until a deterministic gate validates it.

### Concrete Manifestation: Test Execution

Test execution exemplifies this principle end-to-end:

1. **Agent writes test** — agentic creation. The agent authors a test file (e.g., `test_user_auth.py`).
2. **Agent commits** — `git commit` fires pre-commit hook.
3. **Hook runs tests** — `run-tests --changed-only` executes (deterministic validation). Agent does not run tests; hook does.
4. **Pass/fail mechanical** — exit 0 or 1 determines commit success. No agent judgment involved.
5. **Agent blocked from running tests directly** — `block-dangerous-git.sh` denies `pytest`, `npm test`, etc. at PreToolUse. Agent cannot bypass or "double-check" — only the hook's result is trustworthy.

**Result**: Tests always run. Test results are always trustworthy. Agents cannot skip them, misinterpret them, or fake them.

## 8.2 Hook-Triggered Validation Pattern

Factory Flow Control uses **unavoidable hooks** as the enforcement layer. Three hook types:

| Hook Type             | Fires When                 | Runs What                      | Cannot Be Bypassed By           | Exit Codes           |
| --------------------- | -------------------------- | ------------------------------ | ------------------------------- | -------------------- |
| **Pre-commit**        | `git commit`               | `transition-lint`, `run-tests` | Agent (human can `--no-verify`) | 0 (allow), 1 (block) |
| **Pre-push**          | `git push`                 | `run-tests --full`             | Anyone (no `--no-verify`)       | 0 (allow), 1 (block) |
| **PreToolUse**        | Before every shell command | `block-dangerous-git.sh`       | Agent or human (CLI enforces)   | 0 (allow), 2 (deny)  |
| **FSM gate** (pseudo) | `phase advance` invocation | `script_exit_zero` condition   | Manual invocation required      | 0 (met), 1 (unmet)   |

### Zero-Trust Command Execution

Agents do not have unrestricted shell access. Every command passes through a PreToolUse hook (`block-dangerous-git.sh`) before execution. The hook:

1. Receives the command as JSON on stdin (both CLIs use the same schema).
2. Matches it against a deny list (destructive git commands, test commands).
3. Exits 0 (allow) or 2 (deny). Exit 2 surfaces as a denial message to the agent; the command never executes.

This is **preventive validation**, not reactive. The agent never sees test output from a run it initiated, because it cannot initiate one.

## 8.3 Framework Detection and Zero-Install Principle

`run-tests` auto-detects the project's test framework from structure markers (BR-023):

| Marker                    | Framework Detected | Command Invoked                  |
| ------------------------- | ------------------ | -------------------------------- |
| `pyproject.toml` + pytest | pytest             | `uv run pytest ...`              |
| `package.json` + jest     | jest / npm test    | `npm test`                       |
| `go.mod`                  | go test            | `go test ./...`                  |
| `Cargo.toml`              | cargo test         | `cargo test`                     |
| None                      | (error)            | Exit 2, report missing framework |

**Zero-install**: Factory Flow Control does not install test frameworks. It uses what the project already has (`uv run`, `npm`, `go`, `cargo`). If the project has no test framework, `run-tests` exits 2 and reports the gap — the operator/agent must add one before test gates can pass.

**Mode-specific flags**:

- `--changed-only`: Fast subset (pytest `--lf`, jest `--onlyChanged`, go/cargo per-package filter)
- `--full`: Complete suite, no caching, no filters

Exact framework-specific filters are implementation-defined (BR-025); the intent is sub-second feedback for small changes in `--changed-only` mode, exhaustive coverage in `--full`.

## 8.4 JSON Output Convention

Machine-readable output from validation scripts goes to **stdout**, human-readable progress/errors to **stderr**. This separation allows:

- Hooks to parse structured results (exit code + JSON) without fragile string parsing.
- Humans/agents to see real-time progress on stderr while the command runs.
- Logs to capture both streams independently.

Example (`run-tests`):

```bash
$ factory/scripts/run-tests --full
# stderr: test framework detection, progress, failures
Running pytest tests (full)...
test_user_auth.py::test_login_success PASSED
test_user_auth.py::test_login_invalid FAILED
...

# stdout: JSON summary, one line, parseable
{"passed": 247, "failed": 1, "skipped": 3, "duration_ms": 1234}

# exit code: 0 (pass), 1 (fail), 2 (no framework)
$ echo $?
1
```

Hooks that need to act on results (e.g., `phase advance` evaluating `script_exit_zero`) read the exit code only. The JSON summary is for human/log consumption, not for gate decisions.

## 8.5 Single Source of Truth: Marker and FSM

The playbook state marker (`.agent-factory/playbook-state.yml`) and the FSM (e.g., `greenfield-development.fsm.yml`) are the **only** sources of truth for "what phase are we in" and "what's next."

- **Observable-state resume** (ADR-0002): Every mechanism (`phase advance`, `run-step`, `transition-lint`) derives its answer from these files on disk, not from a separately persisted execution status. If the marker says `state: PHASE_2`, then the run is in PHASE_2 — regardless of what any orchestrator process last remembered.
- **No process-local state**: `orchestrator/` has its own `RUN`/`RUN_LOCK` bookkeeping (a distinct concern), but it does not hold a competing notion of "current phase." It reads the marker like everyone else.

This makes resumption trivial: start a new agent session, read the marker, derive "what's next." No recovery logic, no stale state reconciliation.

## 8.6 Staged Validation: Research Artifacts

The falsification-driven research feature validates its JSON artifacts through a fixed three-stage order, layered by *whether a machine can decide the check* rather than bundled into one pass:

| Stage        | Owner                               | Decides                                                                                         |
| ------------ | ----------------------------------- | ----------------------------------------------------------------------------------------------- |
| 1 — schema   | `factory/scripts/schema-validate`   | Structure — required fields, types, enums, identifier patterns, timestamps, array minimums      |
| 2 — policy   | `factory/scripts/policy-validate`   | Enforceable cross-artifact policy — role separation, references, quorum, current claim versions |
| 3 — semantic | a qualified human or agent reviewer | Meaning — evidence support, source independence in substance, test severity, claim atomicity    |

The order is fixed: an artifact must pass stage 1, then stage 2, then stage 3 before the next playbook step begins, and progression blocks on the first failing stage (`policy-validate --pipeline` chains stages 1 and 2 and stops at the first failure). This is the same "Agentic Creation, Deterministic Validation" principle applied to a new domain: mechanise every check that can be mechanised (stages 1–2, stdlib-only exit-code validators, exactly like `spec-lint` and `arch-lint`), and name honestly the residue that a script cannot settle (stage 3).

Two distinctions from §8.2 matter. First, these validators are **on demand, not hook-enforced**: the research playbook and agents invoke them, so they are deterministic and reproducible but not *unavoidable* the way a pre-commit gate is. Second, the schemas they check against are **data, not prose** — JSON-Schema files under `factory/rulebooks/schemas/`, a rulebook category deliberately outside `INDEX.yaml`. See [ADR-0006](09_architecture_decisions.md) and [`research-topic.md` § The Validation Gate](../factory/playbooks/research-topic.md).

## Referenced from

- [foundational-principles.md](../factory/rulebooks/conventions/foundational-principles.md)
- [05_building_block_view.md § 5.2.1](05_building_block_view.md#521-run-tests--test-execution-component)
- [06_runtime_view.md § 6.2](06_runtime_view.md#62-test-execution-flow)
- [09_architecture_decisions.md](09_architecture_decisions.md)
