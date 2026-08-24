# Interface Contracts — Factory Flow Control

Command-line contract for every script this specification covers: inputs, flags, outputs, and exit codes. All scripts are stdlib-only Python 3.8+; none requires a virtualenv.

## `factory/scripts/transition-lint`

|               |                                                                                                                                    |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Usage         | `transition-lint [--repo-root DIR] [--marker PATH] [--playbooks-dir DIR] [--format text\|json] [--report-only]`                    |
| Reads         | `.agent-factory/playbook-state.yml` (or `--marker`); `git diff --cached --name-only`; the marker's playbook `.fsm.yml`             |
| Writes        | Nothing — read-only                                                                                                                |
| Exit code     | Count of error-severity findings (`0` = clean), unless `--report-only` (always `0`)                                                |
| Finding codes | `TL-NOMARKER` (info), `TL-MARKER` (error — missing `playbook`/`state`), `TL-NOFSM` (error), `TL-STATE` (error), `TL-ORDER` (error) |

See [UC-02](../use_cases/UC-02-block-an-out-of-phase-commit.md).

## `factory/scripts/phase advance`

|               |                                                                                                        |
| ------------- | ------------------------------------------------------------------------------------------------------ |
| Usage         | `phase advance [--by NAME] [--repo-root DIR] [--marker PATH] [--playbooks-dir DIR] [--playbook NAME]`  |
| Reads         | The marker (if present); the target `.fsm.yml`; `docs/findings/**` (for `no_open_findings` conditions) |
| Writes        | The marker, only on success                                                                            |
| Exit code     | `0` on success; `1` on refusal (unmet conditions, terminal state, missing FSM)                         |
| stdout/stderr | Success message to stdout; refusal message (with every unmet condition) to stderr                      |

See [UC-01](../use_cases/UC-01-advance-a-playbook-phase.md).

## `factory/scripts/phase retry`

|               |                                                                                                    |
| ------------- | -------------------------------------------------------------------------------------------------- |
| Usage         | `phase retry [--repo-root DIR] [--marker PATH] [--playbooks-dir DIR] [--default-max-iterations N]` |
| Reads         | The marker (required — errors if absent); the target `.fsm.yml`'s `halt_conditions`                |
| Writes        | The marker, only when the retry is allowed                                                         |
| Exit code     | `0` allowed; `1` no marker; `2` cap exceeded                                                       |
| stdout/stderr | Success message to stdout; refusal (with cap and any declared `message`) to stderr                 |

See [UC-03](../use_cases/UC-03-retry-a-phase-within-the-iteration-cap.md).

## `factory/scripts/trigger`

|                 |                                                                                                                                                         |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage           | `trigger agent <name> [--background\|--interactive] [--cli claude\|copilot] [--cwd DIR]`                                                                |
|                 | `trigger playbook <name> --step <agent-name-or-index> [--background\|--interactive] [...]`                                                              |
|                 | `trigger list`                                                                                                                                          |
| Reads           | `factory/INDEX.yaml`'s source data (via `index-lint`'s loaders); `config/model.conf` (via `matrix-lint`'s parser); the resolved agent's definition file |
| Writes          | Nothing of its own — the dispatched CLI subprocess writes whatever its own session produces                                                             |
| Exit code       | The invoked CLI's own exit code (`--background`); `0` after printing launch instructions (`--interactive`); `2` on a resolution error                   |
| Default `--cli` | `claude`                                                                                                                                                |

See [UC-04](../use_cases/UC-04-dispatch-an-agent-via-trigger.md).

## `factory/scripts/index-lint`

|           |                                                                                                                                        |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Usage     | `index-lint [--agents-dir DIR] [--skills-dir DIR] [--playbooks-dir DIR] [--rulebooks-dir DIR] [--out PATH] [--check]`                  |
| Reads     | `factory/agents/*.md`, `factory/skills/*/SKILL.md`, `factory/playbooks/*.md`, `factory/rulebooks/**/*.md` (excluding templates)        |
| Writes    | `factory/INDEX.yaml` (or `--out`), unless `--check` or content is unchanged                                                            |
| Exit code | `0` if up to date (now or already); `1` in `--check` mode if it was stale                                                              |
| stderr    | One `[WARNING]` per: agent missing `phase-name`, skill missing `category`, agent `total_tokens` exceeding 20 000, tiktoken unavailable |

See [UC-06](../use_cases/UC-06-regenerate-the-catalog.md).

## `factory/config/hooks/block-dangerous-git.sh`

|            |                                                                                                           |
| ---------- | --------------------------------------------------------------------------------------------------------- |
| Invocation | Native `PreToolUse` hook for Claude Code, GitHub Copilot CLI, and Codex; command JSON on stdin            |
| Reads      | `.tool_input.command`, `.toolArgs.command`, or `.tool_input.cmd`, according to the calling runtime        |
| Writes     | Deny reason to stderr; `{"permissionDecision":"deny","permissionDecisionReason":"..."}` to stdout on deny |
| Exit code  | `0` allow; `2` deny (shared by the three native-hook CLIs)                                                |

See [UC-07](../use_cases/UC-07-block-a-dangerous-git-command.md).

## `factory/config/extensions/run-agent.ts` — the `run_agent` tool

|            |                                                                                                                                                                                                                                                                                                             |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Invocation | Pi model-callable tool `run_agent(agent: string, task: string, model?: string)`, registered by the project-local extension when Pi trusts the project                                                                                                                                                       |
| Reads      | `factory/agents/<agent>.md` (persona and `tier` frontmatter); `config/model.conf` `pi.<tier>` (via the shared tier resolver); the `PI_RUN_AGENT_DEPTH` env var                                                                                                                                              |
| Spawns     | `pi --no-session -a --mode json --model <m> --append-system-prompt <agent.md> -p <task>` in the project directory, with `PI_RUN_AGENT_DEPTH` incremented                                                                                                                                                    |
| Streaming  | Asynchronously spools complete stdout to protected capture staging, incrementally parses arbitrarily chunked JSONL with bounded non-result state, and emits bounded progress updates                                                                                                                        |
| Returns    | A BR-040 bounded result envelope plus `{ usage, exitCode }` parsed from the child's final assistant `message_end`; an error result on unknown agent, unresolved model, exceeded depth, spawn failure, non-zero/no-result exit, or cancellation                                                              |
| Capture    | Hands the complete raw staging file to detached best-effort usage capture; capture failure leaves the agent result unchanged, and cancellation terminates the process group through bounded `SIGTERM` → `SIGKILL` escalation, bounds pipe drain, cleans staging, and returns a distinct no-retry diagnostic |
| Guardrail  | The child loads `.pi/extensions/`, so the git-safety guardrail binds it too; the one sanctioned `factory/scripts/run-tests --staged` remains permitted                                                                                                                                                      |

See [UC-10](../use_cases/UC-10-invoke-a-factory-agent-under-pi.md).

## `factory/scripts/usage-capture`

|                   |                                                                                                                                                      |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Invocation        | `usage-capture --cli <claude-code\|copilot\|codex\|pi> --transcript PATH --session ID [--model MODEL] [...]`                                         |
| Reads             | One CLI-native transcript, explicit invocation context, and `config/project.json`                                                                    |
| Writes            | One normalized JSONL usage record with non-null `project_id` and `project_name`, configured evidence, and session-end derived signals when available |
| Model attribution | Explicit `--model` first; otherwise the latest non-empty native transcript model; otherwise null                                                     |
| Required coverage | A model-bearing contract fixture for every CLI registered in `SUPPORTED_CLIS`                                                                        |

Derived session-end fields are `cache_miss_turns`, `cache_miss_input_tokens`, `late_early_input_ratio`, `cli`, `provider`, and `usage_capability`. `usage_capability` is `full-cache`, `input-only`, or `unavailable`. Exact eligible-turn, predicate, partition, formula, zero, and null rules are canonical in BR-042. The fields are retrospective evidence only.

See [system-use-cases.md § Usage capture attribution](../use_cases/system-use-cases.md#usage-capture-attribution).

## Business Rules

- **BR-036**: usage capture applies model attribution in this order: explicit invocation context, latest non-empty CLI-native transcript model, then null; registry-complete contract coverage is mandatory.

## `factory/scripts/handoff-lint`

|           |                                                                                                                                                                         |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage     | `handoff-lint <handoff-path> [--repo-root DIR]`                                                                                                                         |
| Reads     | The handoff document, referenced artifact paths, and repository branch, upstream, and HEAD state                                                                        |
| Writes    | Nothing; validation is read-only                                                                                                                                        |
| Exit code | `0` when every structural and referential rule passes; non-zero when any required content is absent or malformed                                                        |
| Reports   | Every mechanically detectable missing section/declared field/path, malformed exact SHA, malformed declared repository state/evidence, or missing next action in one run |

`handoff-lint` does not infer undeclared decisions, open items, evidence, or artifact references. A designated semantic review against outgoing phase evidence is a separate phase-closure obligation (BR-049).

See [UC-11](../use_cases/UC-11-cross-a-phase-boundary.md).

## Child-result envelope

| Field            | Contract                                                                                                       |
| ---------------- | -------------------------------------------------------------------------------------------------------------- |
| `disposition`    | Required pass/fail/block outcome                                                                               |
| `finding_counts` | Required counts keyed by severity; zero counts remain explicit                                                 |
| `artifact_paths` | Required complete list of canonical tracked report and finding paths                                           |
| `next_action`    | Required one-to-three-sentence downstream action                                                               |
| Full detail      | Forbidden in the envelope; it is persisted before return and read deliberately from `artifact_paths` if needed |

The envelope applies to native subagents, `run_agent`, and `dispatch_wave`; runtime-specific transport may differ but content does not (BR-040).

## `factory/scripts/init-factory`

|               |                                                                                                                                                                                                           |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage         | `init-factory [--source DIR] [--target DIR]`                                                                                                                                                              |
| Reads         | The source checkout's `factory/`; the target's existing `.gitignore`, runtime hook/settings files, `.pre-commit-config.yaml`, and `config/model.conf`, if present                                         |
| Writes        | `factory/` (copy, once), `.gitignore` (merge), `.claude/`, `.github/`, `.codex/`, `.agents/`, and `.pi/` runtime surfaces, `config/model.conf` (copy, once), `.pre-commit-config.yaml` (symlink or merge) |
| Exit code     | `0` on success, including a clean no-op re-run; `1` on any collision or unsupported existing state                                                                                                        |
| stdout/stderr | One `init-factory: <line>` report line per step; `init-factory: STOPPED — <reason>` on collision                                                                                                          |

See [UC-08](../use_cases/UC-08-initialize-agent-factory-into-a-project.md).

## `factory/scripts/backlog-lint`

|               |                                                                                                                                                                        |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage         | `backlog-lint [--backlog-dir DIR] [--format text\|json] [--report-only]`                                                                                               |
| Reads         | Story files in `backlog/ST-*.md`                                                                                                                                       |
| Writes        | Nothing; validation is read-only                                                                                                                                       |
| Exit code     | Count of error-severity findings (`0` = clean), unless `--report-only` (always `0`)                                                                                    |
| Finding codes | `BL-ID`, `BL-MISSING`, `BL-EXTRA`, `BL-ENUM`, `BL-TYPE`, `BL-DEP`, `BL-FILE`, `BL-EMPTY`, `BL-NAME`, `BL-PARSE`, `BL-DUP-ID`, `BL-CYCLE`, `BL-DUP`, `VR-027`, `VR-028` |

### StoryFrontmatter schema

All stories must have YAML frontmatter with the following fields:

#### Required fields

| Field     | Type             | Valid values                                          | Notes                                       |
| --------- | ---------------- | ----------------------------------------------------- | ------------------------------------------- |
| `id`      | string           | `ST-\d{4,}` (pattern)                                 | Zero-padded, must match filename stem       |
| `epic`    | string           | Any non-empty string                                  | Grouping label, not a separate artifact     |
| `title`   | string           | Any non-empty string                                  | One-line story title                        |
| `tier`    | string           | `economy`, `standard`, `strong`                       | Model tier for implementation workload      |
| `status`  | string           | `pending`, `in-progress`, `review`, `blocked`, `done` | Current status                              |
| `outputs` | array of strings | File paths or glob patterns                           | Files the story produces; must be non-empty |

#### Optional fields

| Field    | Type             | Notes                                                                                           |
| -------- | ---------------- | ----------------------------------------------------------------------------------------------- |
| `deps`   | array of strings | Story IDs that must complete first; must match pattern `ST-\d{4,}`                              |
| `traces` | array of strings | Use Case / ADR / component IDs this story implements                                            |
| `tests`  | array of strings | Pre-existing test file paths covering acceptance criteria; missing files generate warnings only |

### Validation rules

- `backlog-lint` reports one `Finding` per detected error or anomaly
- Errors block (exit code > 0); warnings and info do not
- Filename must match pattern `ST-NNNN.md` and its stem must match frontmatter `id`
- `outputs` globs are matched relative to the project root; when status is `done`, at least one glob must match an existing file
- `deps` referential integrity: listed story IDs must exist (warning if missing); no circular dependencies allowed (error)
- `tests` files are checked for existence; missing files produce `BL-FILE` warnings (not errors — tests may be written after planning)
- Machine field names (`tier`, `deps`, `traces`, `outputs`) must not appear as prose headings or bold terms in the story body

## `factory/scripts/charter-lint`

|               |                                                                                                                                       |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Usage         | `charter-lint [--charter-dir DIR] [--template-dir DIR] [--planning-gate] [--format text\|json] [--report-only]`                       |
| Reads         | Charter files in `docs/charter/{tech-stack,development,house-rules}.md`; template files in `factory/rulebooks/templates/charter-*.md` |
| Writes        | Nothing; validation is read-only                                                                                                      |
| Exit code     | Count of error-severity findings (`0` = clean), unless `--report-only` (always `0`)                                                   |
| Finding codes | `CH-DIR`, `CH-FILE`, `CH-FM`, `CH-SECT`, `CH-EMPTY`, `CH-TBD`                                                                         |

### Charter validation modes

**Default mode:** Validates structural integrity and template compliance:

- All three charter files exist under `docs/charter/`
- Required sections present per template (derived from `## headings` in template files)
- No section is empty (content beyond HTML comment prompt required)
- YAML frontmatter parses cleanly

**Planning gate mode** (`--planning-gate`): Stricter pre-planning validation:

- All default checks pass
- `tech-stack.md` contains no "To be decided" entries
- `development.md` contains no "To be decided" entries
- `house-rules.md` may contain "To be decided" entries (not validated)

### Validation rules

- `charter-lint` reports one `Finding` per detected error or anomaly
- Errors block (exit code > 0); warnings and info do not
- Templates are read to discover required sections dynamically (no hardcoded section names)
- Section content is extracted between `## Section` markers; empty or comment-only sections fail validation
- "To be decided" entries are detected case-insensitively and block planning gate unless in house-rules.md

## Referenced from

- [entity-model.md](entity-model.md)
- [validation-rules.md](validation-rules.md)
- [use_cases/system-use-cases.md](../use_cases/system-use-cases.md)
