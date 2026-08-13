[back to index](../README.md)

# 5. Building Block View

## 5.1 Level 1: Container View

Factory Flow Control consists of three primary containers:

| Container         | Responsibility                                                                                   | Technology                |
| ----------------- | ------------------------------------------------------------------------------------------------ | ------------------------- |
| **State Manager** | Reads/writes playbook state marker, resolves FSM transitions, drives phases                      | Bash, Python              |
| **Validator**     | Enforces gates, permissions, and mechanically triggered test execution                           | Bash, Python              |
| **Dispatcher**    | Resolves agents/models from catalog, spawns CLI sessions with scoped permits                     | Bash, Python              |
| **Usage Capture** | Normalizes CLI transcripts and appends canonical runtime usage records                           | Python, shell, TypeScript |
| State Files       | Local git-ignored marker (`.agent-factory/playbook-state.yml`) and FSM defs                      | YAML (storage)            |
| Catalog           | Generated `factory/INDEX.yaml` from agent/skill/playbook/rulebook frontmatter, with token counts | YAML (storage)            |

![Containers](../assets/images/Containers.png)

## 5.2 Level 2: Component View — Validator

The **Validator** container enforces deterministic gates. Three are hook-triggered — they fire mechanically on a git or CLI event, so an agent cannot skip them:

| Component               | Trigger Point                  | What it validates                                   | Exit codes                           |
| ----------------------- | ------------------------------ | --------------------------------------------------- | ------------------------------------ |
| **transition-lint**     | Pre-commit hook (git commit)   | Staged files match current phase's `outputs:` globs | 0 (pass), 1 (findings)               |
| **block-dangerous-git** | Native hook or Pi extension    | Shell command not in deny list                      | 0 (allow), 2 (deny)                  |
| **run-tests**           | Pre-commit, pre-push, FSM gate | Project tests pass via auto-detected framework      | 0 (pass), 1 (fail), 2 (no framework) |

Two more — `schema-validate` and `policy-validate` — are on-demand validators invoked by the research skills and agents (and from the CLI) rather than by a hook. They are described in §5.2.2.

### 5.2.1 run-tests — Test Execution Component

**Purpose**: Framework-agnostic test runner invoked by mechanical gates. Agents use the Factory runner rather than bare test commands.

**Interfaces**:

- **IN (CLI)**: `--changed-only` (pre-commit fast subset), `--full` (pre-push, phase advance), `--staged` (agent iteration on staged files)
- **OUT (stdout)**: JSON summary `{"passed": N, "failed": M, "skipped": K, "duration_ms": T}`
- **OUT (stderr)**: Framework-native test output (failures, errors, progress)
- **OUT (exit code)**: 0 (pass), 1 (test failures), 2 (framework detection/config error)

**Behavior**:

1. **Framework Detection** (BR-023): Scans project structure for all framework markers:
   - `pyproject.toml` + pytest → `uv run pytest`
   - `package.json` + jest/npm test → `npm test`
   - `go.mod` → `go test ./...`
   - `Cargo.toml` → `cargo test`
   - Multiple frameworks detected → exit 2 with error listing all found markers (monorepo multi-framework not yet supported)
   - None found → exit 2 with error listing checked markers
2. **Mode Selection**:
   - `--changed-only`: Fast subset (pytest `--lf`, jest `--onlyChanged`, go/cargo per-package filter)
   - `--full`: Complete suite, no filtering
   - `--staged`: Tests on staged files only (agent iteration mode, no commit required)
3. **Invocation**: Runs detected command, streams stderr for real-time progress
4. **Result**: Emits JSON summary on stdout, exits with framework's exit code

**Integration Points**:

- **Pre-commit hook**: Fires on `git commit`, runs `--changed-only` mode. Fast feedback. Bypassable via `--no-verify` (discouraged).
- **Pre-push hook**: Fires on `git push`, runs `--full` mode. "Ready to share" gate. No bypass.
- **Phase advance FSM gate**: Evaluated as `script_exit_zero: factory/scripts/run-tests --full` entry condition. Phase refuses to advance if tests fail.
- **Agent iteration**: `factory/scripts/run-tests --staged` runs tests on staged files without committing. Agents can stage test files and verify before commit. Included in agent allowlist (BR-024).
- **Agent prohibition**: Bare test commands (`pytest`, `npm test`, etc.) are denied by `block-dangerous-git.sh` at PreToolUse. Agents see exit 2 with message directing them to `run-tests --staged` or hook output.

**Referenced Specifications**:

- [UC-09 — Run Tests via Hook](../spec/use_cases/UC-09-run-tests-via-hook.md)
- [PRD § FR-I — Test Execution](../spec/prd.md#fr-i--test-execution-run-tests)
- [validation-rules.md § Test execution (BR-023..BR-027)](../spec/supplementary_specs/validation-rules.md#test-execution-run-tests-br-023-br-024-br-025-br-026-br-027)

### 5.2.2 Research artifact validators (schema-validate, policy-validate)

The falsification-driven research feature validates its JSON artifacts through a fixed three-stage order — **schema → policy → semantic** — that splits validation by whether a machine can decide it. The first two stages are deterministic scripts in this container; the third is human or agent judgment, outside it. Unlike the hook gates above, these are invoked on demand by the research skills and agents, and from the CLI.

| Component           | Stage      | What it validates                                                                                                                        | Exit codes                                        |
| ------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| **schema-validate** | 1 — schema | One JSON artifact against one JSON Schema: required fields, types, enums, identifier patterns, timestamps, array minimums                | 0 (conforms), 1 (violations), 2 (operational)     |
| **policy-validate** | 2 — policy | The enforceable half of the four research policies across related artifacts: role separation, references, quorum, current claim versions | 0 (pass), 1 (policy/schema fail), 2 (operational) |

**Behavior**:

- Both are stdlib-only Python (3.8+), no third-party dependencies — the same zero-install pattern as `spec-lint` and `arch-lint`.
- `schema-validate <artifact-file> <schema-file>` is stage 1, the load-bearing gate every later stage assumes. It implements only the JSON-Schema keyword subset the research schemas need, not a full Draft implementation.
- `policy-validate <artifact-or-dir>...` is stage 2. Its `--pipeline` mode runs stage 1 then stage 2 in order and stops at the first failing stage.
- Semantic judgment — evidence support, source independence in substance, test severity, claim atomicity — is stage 3, deliberately left to a qualified human or agent reviewer. No script decides it.
- The schemas the validators read live in `factory/rulebooks/schemas/research-*.schema.json`, a rulebook category of JSON-Schema data contracts that is intentionally absent from `INDEX.yaml` (which catalogs Markdown only).

**Referenced Specifications**:

- [ADR-0006 — Research: flat storage and validation pipeline](../adr/0006-research-flat-storage-and-validation-pipeline.md)
- [factory/playbooks/research-topic.md § The Validation Gate](../../factory/playbooks/research-topic.md)

## 5.3 Level 2: Component View — State Manager

| Component          | What it does                                                          | Reads                        | Writes               |
| ------------------ | --------------------------------------------------------------------- | ---------------------------- | -------------------- |
| **phase advance**  | Advances marker to next state when entry conditions met               | Marker, FSM, gate results    | Marker               |
| **phase retry**    | Retries current phase's author step, capped by FSM `halt_conditions`  | Marker, FSM                  | Marker (iteration++) |
| **run-step skill** | Derives "what's next" from observable state (fresh, resume, escalate) | Marker, FSM, outputs on disk | (none — read-only)   |

All three read the same marker (`.agent-factory/playbook-state.yml`) and FSM (e.g., `greenfield-development.fsm.yml`). Single source of truth.

## 5.4 Level 2: Component View — Dispatcher

| Component               | What it does                                                                                                                      | Reads                 | Writes                |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------- | --------------------- | --------------------- |
| **trigger**             | Resolves agent/model, spawns CLI session with scoped permits                                                                      | INDEX.yaml            | (none)                |
| **index-lint**          | Generates INDEX.yaml from frontmatter with token budget counts; `--check` validates drift                                         | source .md            | INDEX.yaml            |
| **run-agent** (Pi)      | Pi model-callable tool: spawns a separate `pi` session to run one factory agent                                                   | agent .md, model.conf | (none)                |
| **dispatch-wave** (Pi)  | Pi model-callable tool: runs a parallel wave of agents, each in its own git worktree, integrating `premerge-check` before merging | agent .md, model.conf | git worktrees, merges |
| **openrouter-discover** | Operator aid: queries the OpenRouter catalog to curate/validate `pi.*` tier rows in model.conf, offline of the runtime path       | OpenRouter API        | (none)                |

## 5.5 Interfaces Summary

Every building block's entry point, invoked how, and by whom:

| Script / Component     | Invoked by                             | Entry point                                                         | Exit codes                                    |
| ---------------------- | -------------------------------------- | ------------------------------------------------------------------- | --------------------------------------------- |
| transition-lint        | Pre-commit hook                        | `factory/scripts/transition-lint`                                   | 0 (pass), 1 (findings)                        |
| run-tests              | Pre-commit, pre-push, phase advance    | `factory/scripts/run-tests [--changed-only\|--full\|--staged]`      | 0 (pass), 1 (fail), 2 (no framework)          |
| block-dangerous-git.sh | Claude, Copilot, Codex native hook     | stdin: CLI-specific command JSON, stdout: empty, exit 0 or 2        | 0 (allow), 2 (deny)                           |
| phase advance          | Human, orchestrator                    | `factory/scripts/phase advance`                                     | 0 (advanced), 1 (conditions unmet), 2 (misc)  |
| phase retry            | Human, orchestrator                    | `factory/scripts/phase retry [--default-max-iterations]`            | 0 (retried), 2 (cap exceeded)                 |
| trigger                | Human, orchestrator, run-step skill    | `factory/scripts/trigger agent <name> [--background]`               | 0 (dispatched), 1+ (error)                    |
| usage-capture          | Native CLI hooks and Pi extensions     | `factory/scripts/usage-capture --cli ... --transcript ...`          | 0 (captured or best-effort no-op)             |
| index-lint             | Pre-commit hook, CI                    | `factory/scripts/index-lint [--check]`                              | 0 (fresh), 1 (stale)                          |
| run-step skill         | Any supported CLI (LLM-executed)       | Skill markdown invoked by AI                                        | (N/A — skill is prose)                        |
| run-agent (Pi)         | Pi session (via `run_agent` tool call) | `.pi/extensions/run-agent.ts` → spawns `pi ... -p <task>`           | (tool result: text + usage, or error)         |
| dispatch-wave (Pi)     | Pi session (via `dispatch_wave` call)  | `.pi/extensions/dispatch-wave.ts` → worktree + spawn + merge/item   | (tool result: per-item status, or error)      |
| openrouter-discover    | Human operator, CI (`--check`)         | `factory/scripts/openrouter-discover [--list\|--suggest\|--check]`  | 0 (ok), 1 (drift)                             |
| schema-validate        | Research skills/agents, CLI            | `factory/scripts/schema-validate <artifact-file> <schema-file>`     | 0 (conforms), 1 (violations), 2 (operational) |
| policy-validate        | Research skills/agents, CLI            | `factory/scripts/policy-validate [--pipeline] <artifact-or-dir>...` | 0 (pass), 1 (fail), 2 (operational)           |

## 5.6 Level 2: Runtime Usage Capture

`usage-capture` is a CLI-agnostic pipeline with two adapter seams. A
CLI-specific normalizer maps Claude Code, Copilot, Codex, or Pi events into
ordered input/output text and nullable provider usage. The fixed
`cl100k_base` tokenizer produces comparable `normalized_*` counts. A JSONL
logging adapter appends the canonical record beneath `.agent-factory/usage/`
and persists the exact tokenized transcript copy referenced by the record.

Native lifecycle adapters own invocation: Claude `Stop`/`SubagentStop`,
Copilot `agentStop`/`subagentStop`, Codex `Stop`/`SubagentStop`, and Pi
`session_shutdown` plus inline child capture. The orchestrator never writes a
second record. See
[ADR-0007](../adr/0007-normalize-runtime-usage-through-cli-adapters.md).

## Referenced from

- [06_runtime_view.md § 6.2](06_runtime_view.md#62-test-execution-flow)
- [09_architecture_decisions.md](09_architecture_decisions.md)
