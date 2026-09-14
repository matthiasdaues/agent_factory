# Interface Contracts — Factory Flow Control

Command-line contract for every script this specification covers: inputs, flags, outputs, and exit codes. All scripts are stdlib-only Python 3.8+; none requires a virtualenv.

## `factory/scripts/transition-lint`

|               |                                                                                                                                    |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Usage         | `transition-lint [--repo-root DIR] [--marker PATH] [--playbooks-dir DIR] [--format text\|json] [--report-only]`                    |
| Reads         | `.current-work/playbook-state.yml` (or `--marker`); `git diff --cached --name-only`; the marker's playbook `.fsm.yml`              |
| Writes        | Nothing — read-only                                                                                                                |
| Exit code     | Count of error-severity findings (`0` = clean), unless `--report-only` (always `0`)                                                |
| Finding codes | `TL-NOMARKER` (info), `TL-MARKER` (error — missing `playbook`/`state`), `TL-NOFSM` (error), `TL-STATE` (error), `TL-ORDER` (error) |

See [UC-02](../../~archive/spec/use_cases/UC-02-block-an-out-of-phase-commit.md).

## `factory/scripts/phase advance`

|               |                                                                                                        |
| ------------- | ------------------------------------------------------------------------------------------------------ |
| Usage         | `phase advance [--by NAME] [--repo-root DIR] [--marker PATH] [--playbooks-dir DIR] [--playbook NAME]`  |
| Reads         | The marker (if present); the target `.fsm.yml`; `docs/findings/**` (for `no_open_findings` conditions) |
| Writes        | The marker, only on success                                                                            |
| Exit code     | `0` on success; `1` on refusal (unmet conditions, terminal state, missing FSM)                         |
| stdout/stderr | Success message to stdout; refusal message (with every unmet condition) to stderr                      |

See [UC-01](../../~archive/spec/use_cases/UC-01-advance-a-playbook-phase.md).

## `factory/scripts/phase retry`

|               |                                                                                                    |
| ------------- | -------------------------------------------------------------------------------------------------- |
| Usage         | `phase retry [--repo-root DIR] [--marker PATH] [--playbooks-dir DIR] [--default-max-iterations N]` |
| Reads         | The marker (required — errors if absent); the target `.fsm.yml`'s `halt_conditions`                |
| Writes        | The marker, only when the retry is allowed                                                         |
| Exit code     | `0` allowed; `1` no marker; `2` cap exceeded                                                       |
| stdout/stderr | Success message to stdout; refusal (with cap and any declared `message`) to stderr                 |

See [UC-03](../../~archive/spec/use_cases/UC-03-retry-a-phase-within-the-iteration-cap.md).

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

See [UC-04](../../~archive/spec/use_cases/UC-04-dispatch-an-agent-via-trigger.md).

## `factory/scripts/dispatch`

|               |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage         | `dispatch init --base <branch> --stories <ids> [--feature-branch <name>] [--baseline-commit --yes]`<br>`dispatch plan --backlog-dir backlog [--stories <ids>]`<br>`dispatch prepare-wave <wave>`<br>`dispatch prepare-story <story-id>`<br>`dispatch mark-dispatching <story-id>`<br>`dispatch mark-dispatched <story-id>`<br>`dispatch verify-story <story-id> --sha <sha>`<br>`dispatch escalate <story-id>`<br>`dispatch merge-story <story-id> [--dry-run]`<br>`dispatch mark-blocked <story-id> --reason <text>`<br>`dispatch mark-failed <story-id> [--class CLASS] [--evidence PATH]`<br>`dispatch re-dispatch <story-id>`<br>`dispatch close-wave <wave>`<br>`dispatch suggest-merge-args` |
| Reads         | Backlog stories, `config/project.json`, `config/model.conf`, git state, and the active dispatch ledger (`.current-work/<feature-branch>/dispatch-ledger.yaml` after `init`; `--ledger` may override)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Writes        | `init` creates the feature branch/worktree namespace and ledger under `.current-work/<feature-branch>/dispatch-ledger.yaml`; `prepare-wave` / `prepare-story` prepare story worktrees, run pre-spawn `verify-base`, and update ledger state to `prepared`; `mark-*`, `verify-story`, `merge-story`, and `close-wave` advance the same ledger and append wave closeout data                                                                                                                                                                                                                                                                                                                         |
| Exit code     | `0` on success or idempotent no-op; non-zero on missing ledger, malformed ledger, missing story, invalid transition, failed verification, blocked merge, or failed initialization/planning precondition                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| stdout/stderr | Human-readable planning output or errors; no structured output contract beyond subcommand success/failure                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |

`dispatch` is the script-owned implementation dispatch state machine. `prepare-wave` / `prepare-story` establish the `prepared` state by creating the story branch/worktree, recording the declared base, writing the step manifest, and running `verify-base` before any developer-agent spawns. `escalate` performs a read-only check of the ledger, branch verification, and scope boundaries before granting a one-tier promotion or blocking the story when the wave slot is exhausted. `merge-story` runs `premerge-check --scope`/`--scope-glob` with `--max-files` scaled from the story's declared `outputs` count (`max(20, len(outputs) * 2)`, so the pre-existing default of 20 holds for small stories), performs the merge, updates the story file status in the merge commit, runs post-merge tests, and records the terminal outcome in the ledger. `close-wave` succeeds only when every story in the requested wave is terminal, and it records a wave closeout entry with completed, blocked, failed, next_ready, and branch_head fields. `suggest-merge-args` reads the ledger and sums each story's declared `outputs` count to print a recommended `--max-files` value (floored at 20) for the final feature-branch-to-dev merge, which routinely exceeds any single story's per-story threshold.

## `factory/scripts/step-guard`

|             |                                                                                                                                                                                                                                                                              |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage       | `step-guard --guard-type read\|write\|bash\|context`                                                                                                                                                                                                                         |
| Reads       | One JSON tool event on stdin; `.current-work/current-step.yml` when present; declared inputs/outputs and `max_input_tokens` from the event or manifest                                                                                                                       |
| Writes      | Nothing — read-only; deny reasons to stderr on refusal                                                                                                                                                                                                                       |
| Exit code   | `0` on allow; `1` on scope/budget denial; `2` on malformed JSON or malformed event/manifest                                                                                                                                                                                  |
| Guard types | `read` checks one path against declared inputs and always-allowed prefixes; `write` checks one path against declared outputs plus the security deny-list; `bash` extracts obvious read/write paths from common shell commands; `context` compares estimated tokens to budget |

`step-guard` is intentionally best-effort for Bash path extraction. It allows commands with no extractable path, and it treats declared input size as file bytes divided by 4 when estimating context usage.

See [UC-12](../../~archive/spec/use_cases/UC-12-audit-dispatch-safeguards.md).

## `factory/scripts/index-lint`

|           |                                                                                                                                        |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Usage     | `index-lint [--agents-dir DIR] [--skills-dir DIR] [--playbooks-dir DIR] [--rulebooks-dir DIR] [--out PATH] [--check]`                  |
| Reads     | `factory/agents/*.md`, `factory/skills/*/SKILL.md`, `factory/playbooks/*.md`, `factory/rulebooks/**/*.md` (excluding templates)        |
| Writes    | `factory/INDEX.yaml` (or `--out`), unless `--check` or content is unchanged                                                            |
| Exit code | `0` if up to date (now or already); `1` in `--check` mode if it was stale                                                              |
| stderr    | One `[WARNING]` per: agent missing `phase-name`, skill missing `category`, agent `total_tokens` exceeding 20 000, tiktoken unavailable |

See [UC-06](../../~archive/spec/use_cases/UC-06-regenerate-the-catalog.md).

## `factory/config/hooks/block-dangerous-git.sh`

|            |                                                                                                                                                                                           |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Invocation | Native `PreToolUse` hook for Claude Code, GitHub Copilot CLI, and Codex; command JSON on stdin                                                                                            |
| Reads      | `.tool_input.command`, `.toolArgs.command`, or `.tool_input.cmd`, according to the calling runtime; `docs/testing.yaml` (charter-declared test commands for the agent allowlist — BR-024) |
| Writes     | Deny reason to stderr; `{"permissionDecision":"deny","permissionDecisionReason":"..."}` to stdout on deny                                                                                 |
| Exit code  | `0` allow; `2` deny (shared by the three native-hook CLIs)                                                                                                                                |

See [UC-07](../../~archive/spec/use_cases/UC-07-block-a-dangerous-git-command.md).

## `factory/config/extensions/run-agent.ts` — the `run_agent` tool

|            |                                                                                                                                                                                                                                                                                                             |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Invocation | Pi model-callable tool `run_agent(agent: string, task: string, model?: string)`, registered by the project-local extension when Pi trusts the project                                                                                                                                                       |
| Reads      | `factory/agents/<agent>.md` (persona and `tier` frontmatter); `config/model.conf` `pi.<tier>` (via the shared tier resolver); the `PI_RUN_AGENT_DEPTH` env var                                                                                                                                              |
| Spawns     | `pi --no-session -a --mode json --model <m> --append-system-prompt <agent.md> -p <task>` in the project directory, with `PI_RUN_AGENT_DEPTH` incremented                                                                                                                                                    |
| Streaming  | Asynchronously spools complete stdout to protected capture staging, incrementally parses arbitrarily chunked JSONL with bounded non-result state, and emits bounded progress updates                                                                                                                        |
| Returns    | A BR-040 bounded result envelope plus `{ usage, exitCode }` parsed from the child's final assistant `message_end`; an error result on unknown agent, unresolved model, exceeded depth, spawn failure, non-zero/no-result exit, or cancellation                                                              |
| Capture    | Hands the complete raw staging file to detached best-effort usage capture; capture failure leaves the agent result unchanged, and cancellation terminates the process group through bounded `SIGTERM` → `SIGKILL` escalation, bounds pipe drain, cleans staging, and returns a distinct no-retry diagnostic |
| Guardrail  | The child loads `.pi/extensions/`, so the git-safety guardrail binds it too; the charter-declared test commands from `docs/testing.yaml` are allowlisted with exact matching                                                                                                                                |

See [UC-10](../../~archive/spec/use_cases/UC-10-invoke-a-factory-agent-under-pi.md).

## `factory/scripts/usage-capture`

|                   |                                                                                                                                                      |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Invocation        | `usage-capture --cli <claude-code\|copilot\|codex\|pi> --transcript PATH --session ID [--model MODEL] [...]`                                         |
| Reads             | One CLI-native transcript, explicit invocation context, and `config/project.json`                                                                    |
| Writes            | One normalized JSONL usage record with non-null `project_id` and `project_name`, configured evidence, and session-end derived signals when available |
| Model attribution | Explicit `--model` first; otherwise the latest non-empty native transcript model; otherwise null                                                     |
| Required coverage | A model-bearing contract fixture for every CLI registered in `SUPPORTED_CLIS`                                                                        |

Derived session-end fields are `cache_miss_turns`, `cache_miss_input_tokens`, `late_early_input_ratio`, `cli`, `provider`, and `usage_capability`. `usage_capability` is `full-cache`, `input-only`, or `unavailable`. Exact eligible-turn, predicate, partition, formula, zero, and null rules are canonical in BR-042. The fields are retrospective evidence only.

See [system-use-cases.md § Usage capture attribution](../../~archive/spec/use_cases/system-use-cases.md#usage-capture-attribution).

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

See [UC-11](../../~archive/spec/use_cases/UC-11-cross-a-phase-boundary.md).

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

See [UC-08](../../~archive/spec/use_cases/UC-08-initialize-agent-factory-into-a-project.md).

## `factory/scripts/backlog-lint`

|               |                                                                                                                                                                                    |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage         | `backlog-lint [--backlog-dir DIR] [--format text\|json] [--report-only]`                                                                                                           |
| Reads         | Story files in `backlog/ST-*.md`                                                                                                                                                   |
| Writes        | Nothing; validation is read-only                                                                                                                                                   |
| Exit code     | Count of error-severity findings (`0` = clean), unless `--report-only` (always `0`)                                                                                                |
| Finding codes | `BL-ID`, `BL-MISSING`, `BL-EXTRA`, `BL-ENUM`, `BL-TYPE`, `BL-DEP`, `BL-FILE`, `BL-EMPTY`, `BL-NAME`, `BL-PARSE`, `BL-DUP-ID`, `BL-CYCLE`, `BL-DUP`, `BL-NOTES`, `VR-027`, `VR-028` |

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

| Field           | Type             | Notes                                                                                                                         |
| --------------- | ---------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `deps`          | array of strings | Story IDs that must complete first; must match pattern `ST-\d{4,}`                                                            |
| `traces`        | array of strings | Use Case / ADR / component IDs this story implements                                                                          |
| `tests`         | array of strings | Pre-existing test file paths covering acceptance criteria; missing files generate warnings only                               |
| `risk_domains`  | array of strings | Closed enum: `security`, `privacy`, `data_integrity`, `compatibility`, `reliability`, `operations`                            |
| `strategy`      | string           | Closed enum: `direct`, `seams-first`, `deletion`; defaults to `direct` when absent                                            |
| `seam_outputs`  | array of strings | Optional seams-first test outputs; validated only when present                                                                |
| `impl_outputs`  | array of strings | Optional seams-first implementation outputs; validated only when present                                                      |
| `concerns`      | mapping          | `{domain: [string], technical: [string]}`; both keys optional. Names must match `###` headings in `docs/agent-context.md`     |
| `quality-gates` | array of strings | Closed enum: `crap-score`, `mutation-analysis`, `dependency-check`; omitting a default gate requires justification in `notes` |
| `notes`         | string           | Free-text; required justification when `quality-gates` omits a default gate                                                   |

### Validation rules

- `backlog-lint` reports one `Finding` per detected error or anomaly
- Errors block (exit code > 0); warnings and info do not
- Filename must match pattern `ST-NNNN.md` and its stem must match frontmatter `id`
- `outputs` globs are matched relative to the project root; when status is `done`, at least one glob must match an existing file (inverted for `strategy: deletion`: none of the globs must match an existing file)
- `deps` referential integrity: listed story IDs must exist (warning if missing); no circular dependencies allowed (error)
- `tests` files are checked for existence; missing files produce `BL-FILE` warnings (not errors — tests may be written after planning)
- `risk_domains` and `strategy` are closed enums; unknown values produce `BL-ENUM` errors
- `seam_outputs` and `impl_outputs` are optional arrays of strings; when both are present, they must not share any path
- `strategy: seams-first` requires `seam_outputs ∪ impl_outputs == outputs`
- Machine field names (`tier`, `deps`, `traces`, `outputs`) must not appear as prose headings or bold terms in the story body
- `concerns` must be a mapping with only `domain` and `technical` keys (both optional); each value must be a list of strings
- `quality-gates` is a closed enum (`crap-score`, `mutation-analysis`, `dependency-check`); omitting a factory-default gate requires justification in `notes`

## `factory/scripts/module-graph-check`

|           |                                                                                                                                                                                     |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage     | `module-graph-check [--dsl-path PATH] [--interface-contracts PATH] [--entity-model PATH] [--proposal PATH] [--story-id ID] [--report-dir DIR]`                                      |
| Reads     | `docs/arc42/architecture.dsl`; `docs/spec/supplementary_specs/interface-contracts.md`; `docs/spec/supplementary_specs/entity-model.md`; the proposal file (when `--proposal` given) |
| Writes    | `.current-work/module-graph-check/<story-id>.json`; updates `impact.architecture_change` in proposal frontmatter (when `--proposal` given and override semantics apply)             |
| Exit code | `0` on success (regardless of architecture_change result); `2` on missing input file                                                                                                |
| stdout    | `architecture_change=true\|false`; optional `new_modules=`, `new_dependency=`, `inverted_dependency=` lines                                                                         |

The script derives the module map from `architecture.dsl` (containers, components, relationships), compares it against Phase 1 outputs, and checks three conditions: (a) new module not in DSL, (b) changed public interface, (c) new or inverted dependency direction. Override semantics: `false`→`true` machine wins (annotated `# mechanical detection`); `true`→`false` prior human declaration respected conservatively. A new entity in an existing module does not trigger `architecture_change=true`.

## `factory/scripts/test-design-verify`

|               |                                                                                                                                                                                                                                                      |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage         | `test-design-verify --story <path> [--story-id ID] [--scope-map PATH] [--spec-dir PATH] [--repo-root PATH] [--report-dir DIR]`                                                                                                                       |
| Reads         | The story file's `traces:` frontmatter; `docs/spec/scope-map.md`; `.feature` files referenced by the scope map; the story's `#### Test Design` and `#### Prior Tests` sections                                                                       |
| Writes        | `.current-work/test-design-verify/<story-id>.json` — the resolved traces, findings, and pass/fail verdict; the gate is otherwise read-only against the story and spec files                                                                          |
| Exit code     | `0` when every reachable scenario has a corresponding test assertion or valid waiver; `1` when any owned contract lacks an assertion or a waiver is invalid; `2` on configuration error (unresolvable trace ID, missing scope map, missing .feature) |
| stdout/stderr | One line per validation result; unresolvable trace IDs and invalid waivers reported to stderr                                                                                                                                                        |

### Resolution chain

1. Read the story's `traces:` frontmatter (e.g., `[DOM-01, OBS-04]`, or the `<feature>.feature/Rule-<NN>` shorthand this backlog's own stories use, e.g. `test-design.feature/Rule-14`).
2. For each trace ID, look up the corresponding entry in `docs/spec/scope-map.md` to find the `.feature` file and rule:
   - **`<feature>.feature/Rule-<NN>` shorthand:** the trace ID names the feature file and the rule's 1-indexed position directly; the scope map is still consulted to confirm at least `NN` rows reference that feature file, so a rule the scope map hasn't caught up with is a configuration error rather than a silent pass.
   - **Generic token (e.g. `DOM-01`, `UC-09`):** the trace ID is searched for in the scope map's Sources column; the matching row's Rule-column text is then located verbatim as a `Rule:` line inside the `.feature` file the row names.
3. Read the `.feature` file and collect the individual Scenarios under that rule.
4. For owning stories: verify each reachable Scenario has a corresponding entry in the story's `#### Test Design` section — matched by the Scenario's title text appearing in the section, or by a valid waiver for its trace ID.
5. For non-owning stories: verify the story has a `#### Prior Tests` entry pointing to the owner's test module and function — matched by trace ID or by the Scenario's title text.

### Waiver format

A blockquote line within the `#### Test Design` section:

```markdown
> Waiver: DOM-01 — owned by tests/test_domain.py::test_entity_uniqueness
```

The gate parses these lines and verifies the named test module exists. A waiver without a resolvable owner path fails validation (exit 1).

### Conditional activation

The gate is skipped when the story has no `#### Test Design` section and no `#### Prior Tests` section — it exits 0 and produces no findings. This preserves backward compatibility with stories that predate the test-design skill.

## `docs/testing.yaml` — `gates` section schema

The `gates` section centralizes gate configuration that the dispatcher reads at runtime. It does not define gate execution ordering; [ADR-0012](../../adr/0012-dispatcher-owned-semantic-gate-loop.md) owns the dispatcher's gate sequence.

```yaml
gates:
  crap_score:
    enabled: true
    threshold: 8
  mutation_testing:
    enabled: false
  test_design_verify:
    # Implicitly enabled when test-design output exists in the story.
    # Skipped when no test-design sections are present.
```

| Field                            | Type  | Required | Notes                                                                            |
| -------------------------------- | ----- | -------- | -------------------------------------------------------------------------------- |
| `gates.crap_score.enabled`       | bool  | yes      | Whether the dispatcher runs the crap-score gate                                  |
| `gates.crap_score.threshold`     | float | yes      | Per-function CRAP threshold; replaces the dead-code house-rules lookup           |
| `gates.mutation_testing.enabled` | bool  | yes      | Whether the dispatcher runs mutation testing; `false` until infrastructure ready |
| `gates.test_design_verify`       | —     | no       | Conditional; active when test-design output exists in the story                  |

## `docs/testing.yaml` — `risk_classes` section schema

Optional per-project overrides of Factory convention risk-class defaults. Precedence: `testing.yaml` inline > project-linked strategy document > Factory convention defaults.

```yaml
risk_classes:
  critical:
    format: forbidden          # Given/When/Then/Forbidden
    budget: unbounded          # every distinct failure mode gets a scenario
  standard:
    format: scenario           # concrete input/output pairs
    budget: equivalence        # one per equivalence class + boundaries
  structural:
    format: linter             # no test-design output; linter owns it
  financial:                   # project-specific addition
    format: forbidden
    budget: unbounded
    requires:
      - double_entry_invariant
      - idempotent_retry
```

| Field per risk class | Type           | Required | Notes                                          |
| -------------------- | -------------- | -------- | ---------------------------------------------- |
| `format`             | string         | yes      | `forbidden`, `scenario`, or `linter`           |
| `budget`             | string         | yes      | `unbounded` or `equivalence`                   |
| `requires`           | list of string | no       | Named invariants the contract must demonstrate |

## `factory/scripts/concern-lint`

|               |                                                       |
| ------------- | ----------------------------------------------------- |
| Usage         | `concern-lint [--root DIR] [--format text\|json]`     |
| Reads         | `docs/agent-context.md`, `backlog/ST-*.md`            |
| Writes        | Nothing; validation is read-only                      |
| Exit code     | Count of error-severity findings (`0` = clean)        |
| Finding codes | `CTX-SECTIONS`, `CTX-PATHS`, `CTX-LEGACY`, `CTX-REFS` |

### Checks

- **CTX-SECTIONS** — Required category headings (`## Always (cross-cutting)`, `## Technical concerns`, `## Domain concerns`) exist; each `###` concern section has a description line and at least one `Read:` path.
- **CTX-PATHS** — Every path in a `Read:` or `Boundary:` line resolves to an existing file or glob match, relative to root.
- **CTX-LEGACY** — No legacy YAML agent-context files (other than `testing.yaml`) or `docs/charter/` directory exist alongside `docs/agent-context.md`.
- **CTX-REFS** — Every concern name in any story's `concerns:` frontmatter has a matching `###` heading under "Technical concerns" or "Domain concerns" in `agent-context.md`. Active only when both `docs/agent-context.md` and `backlog/ST-*.md` files exist.

## Referenced from

- [entity-model.md](entity-model.md)
- [validation-rules.md](validation-rules.md)
- [use_cases/system-use-cases.md](../../~archive/spec/use_cases/system-use-cases.md)
- [test-design.feature](../test-design.feature)
- [agent-context.feature](../agent-context.feature)

## Local Usage Processing and Analysis

The [feature specification](../local-usage-processing-and-analysis.feature) adds a local analytical consumer while keeping Factory capture as the producer.

### Usage-record contract

| Property             | Contract                                                                                   |
| -------------------- | ------------------------------------------------------------------------------------------ |
| Canonical source     | `packages/factory/contracts/usage-record/contract.yaml` and `v1.schema.json`               |
| Owner                | Factory                                                                                    |
| Schema dialect       | JSON Schema Draft 2020-12                                                                  |
| Installed projection | `.agent-factory/usage-analysis/contract/`                                                  |
| Consumer rule        | Usage Analysis reads only the installed projection and declares its accepted version range |
| Known CLI values     | `claude-code`, `copilot`, `codex`, and `pi` (registry, not schema-enforced)                |
| Gate                 | `packages/usage/scripts/usage-contract-check`                                              |

The YAML manifest declares owner, current version, compatibility policy, and accepted consumer range. The schema owns field names, types, nullability, and nested structure. The gate additionally owns cross-field invariants and producer/consumer version agreement. A failure identifies source file, line number, field, and stable failure code.

### `usage-query`

| Property                      | Contract                                                                                                                   |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Invocation                    | `uv run --project .agent-factory/usage-analysis usage-query <published-view> [options]`                                    |
| Default input                 | Top-level `*.jsonl` files beneath `.agent-factory/usage/`, sorted at query start                                           |
| Input override                | `--usage-dir <path>`                                                                                                       |
| Published views               | `raw_usage_snapshots`, `latest_run_snapshots`, `session_usage`, `usage_by_dimension`, `cache_efficiency`, `capture_health` |
| Required presentation outputs | Table and JSON                                                                                                             |
| Required programmatic outputs | DuckDB relation and PyArrow table                                                                                          |
| Parquet export                | `--format parquet --output <path>`                                                                                         |
| Dimension selection           | `--dimensions <comma-list>` and `--time-granularity none\|hour\|day\|week\|month`                                          |
| Direct runtime dependencies   | Compatible DuckDB and PyArrow versions, both declared in `pyproject.toml` and pinned by the installed `uv.lock`            |
| Reads                         | Selected top-level JSONL files, installed contract, bundled SQL and accounting registry                                    |
| Writes                        | Only the explicit output path through a temporary sibling; optional private UI state is outside stable output              |
| Network                       | None after dependencies are cached; deterministic gates never require the UI                                               |

#### Query-model-v1 schema contract

Every published result carries schema version `query-model-v1`. `NOT NULL` below is mandatory; all other columns are nullable. A key is unique within one snapshotted input set. Stable command, JSON, Arrow, and Parquet results apply the declared `ORDER BY`; callers must not rely on physical DuckDB storage order.

##### `raw_usage_snapshots`

| Column                   | DuckDB type                | Constraint                         |
| ------------------------ | -------------------------- | ---------------------------------- |
| `query_model_version`    | `VARCHAR`                  | `NOT NULL`, value `query-model-v1` |
| `normalized_source_path` | `VARCHAR`                  | `NOT NULL`, key part               |
| `source_line`            | `UBIGINT`                  | `NOT NULL`, key part, one-based    |
| `captured_at`            | `TIMESTAMP WITH TIME ZONE` | `NOT NULL`                         |
| `capture_sequence`       | `UBIGINT`                  | `NOT NULL`                         |
| `cli`                    | `VARCHAR`                  | `NOT NULL`                         |
| `session_id`             | `VARCHAR`                  | `NOT NULL`                         |
| `run_id`                 | `VARCHAR`                  | `NOT NULL`                         |
| `parent_run_id`          | `VARCHAR`                  | nullable                           |
| `project`                | `VARCHAR`                  | `NOT NULL`                         |
| `provider`               | `VARCHAR`                  | nullable                           |
| `model`                  | `VARCHAR`                  | nullable                           |
| `agent`                  | `VARCHAR`                  | nullable                           |
| `branch`                 | `VARCHAR`                  | nullable                           |
| `exit_status`            | `VARCHAR`                  | nullable                           |
| `normalized_input`       | `UBIGINT`                  | `NOT NULL`                         |
| `normalized_output`      | `UBIGINT`                  | `NOT NULL`                         |
| `normalized_total`       | `UBIGINT`                  | `NOT NULL`                         |
| `provider_input`         | `UBIGINT`                  | nullable                           |
| `provider_output`        | `UBIGINT`                  | nullable                           |
| `cache_read`             | `UBIGINT`                  | nullable                           |
| `cache_write`            | `UBIGINT`                  | nullable                           |
| `transcript_ref`         | `JSON`                     | nullable, never dereferenced       |

Key: `(normalized_source_path, source_line)`. Order: that key ascending.

##### `latest_run_snapshots`

| Column                   | DuckDB type                | Constraint                         |
| ------------------------ | -------------------------- | ---------------------------------- |
| `query_model_version`    | `VARCHAR`                  | `NOT NULL`, value `query-model-v1` |
| `cli`                    | `VARCHAR`                  | `NOT NULL`, key part               |
| `session_id`             | `VARCHAR`                  | `NOT NULL`, key part               |
| `run_id`                 | `VARCHAR`                  | `NOT NULL`, key part               |
| `parent_run_id`          | `VARCHAR`                  | nullable                           |
| `captured_at`            | `TIMESTAMP WITH TIME ZONE` | `NOT NULL`                         |
| `capture_sequence`       | `UBIGINT`                  | `NOT NULL`                         |
| `normalized_source_path` | `VARCHAR`                  | `NOT NULL`, selected evidence      |
| `source_line`            | `UBIGINT`                  | `NOT NULL`, selected evidence      |
| `project`                | `VARCHAR`                  | `NOT NULL`                         |
| `provider`               | `VARCHAR`                  | nullable                           |
| `model`                  | `VARCHAR`                  | nullable                           |
| `agent`                  | `VARCHAR`                  | nullable                           |
| `branch`                 | `VARCHAR`                  | nullable                           |
| `exit_status`            | `VARCHAR`                  | nullable                           |
| `normalized_input`       | `UBIGINT`                  | `NOT NULL`                         |
| `normalized_output`      | `UBIGINT`                  | `NOT NULL`                         |
| `normalized_total`       | `UBIGINT`                  | `NOT NULL`                         |

Key and order: `(cli, session_id, run_id)` ascending.

##### `session_usage`

| Column                | DuckDB type                | Constraint                         |
| --------------------- | -------------------------- | ---------------------------------- |
| `query_model_version` | `VARCHAR`                  | `NOT NULL`, value `query-model-v1` |
| `cli`                 | `VARCHAR`                  | `NOT NULL`, key part               |
| `session_id`          | `VARCHAR`                  | `NOT NULL`, key part               |
| `captured_at`         | `TIMESTAMP WITH TIME ZONE` | `NOT NULL`                         |
| `project`             | `VARCHAR`                  | `NOT NULL`                         |
| `provider`            | `VARCHAR`                  | nullable                           |
| `model`               | `VARCHAR`                  | nullable                           |
| `agent`               | `VARCHAR`                  | nullable                           |
| `branch`              | `VARCHAR`                  | nullable                           |
| `exit_status`         | `VARCHAR`                  | nullable                           |
| `accounting_rule`     | `VARCHAR`                  | `NOT NULL`                         |
| `normalized_input`    | `UBIGINT`                  | `NOT NULL`                         |
| `normalized_output`   | `UBIGINT`                  | `NOT NULL`                         |
| `normalized_total`    | `UBIGINT`                  | `NOT NULL`                         |

Key and order: `(cli, session_id)` ascending.

##### `usage_by_dimension`

| Column                | DuckDB type                | Constraint                                     |
| --------------------- | -------------------------- | ---------------------------------------------- |
| `query_model_version` | `VARCHAR`                  | `NOT NULL`, value `query-model-v1`             |
| `time_granularity`    | `VARCHAR`                  | `NOT NULL`, `none\|hour\|day\|week\|month`     |
| `period_start`        | `TIMESTAMP WITH TIME ZONE` | nullable; null only when granularity is `none` |
| `project`             | `VARCHAR`                  | nullable; non-null only when selected          |
| `cli`                 | `VARCHAR`                  | nullable; non-null only when selected          |
| `provider`            | `VARCHAR`                  | nullable; selected null values remain null     |
| `model`               | `VARCHAR`                  | nullable; selected null values remain null     |
| `agent`               | `VARCHAR`                  | nullable; selected null values remain null     |
| `branch`              | `VARCHAR`                  | nullable; selected null values remain null     |
| `exit_status`         | `VARCHAR`                  | nullable; selected null values remain null     |
| `normalized_input`    | `HUGEINT`                  | `NOT NULL`                                     |
| `normalized_output`   | `HUGEINT`                  | `NOT NULL`                                     |
| `normalized_total`    | `HUGEINT`                  | `NOT NULL`                                     |
| `session_count`       | `UBIGINT`                  | `NOT NULL`                                     |

The key and order are `period_start` when present, followed by selected dimension columns in the caller's declared order; all are ascending with nulls last. With no selected dimensions and granularity `none`, exactly one row represents all canonical sessions when input is non-empty. Empty input returns zero rows with this declared schema.

##### `cache_efficiency`

| Column                | DuckDB type | Constraint                                                |
| --------------------- | ----------- | --------------------------------------------------------- |
| `query_model_version` | `VARCHAR`   | `NOT NULL`, value `query-model-v1`                        |
| `provider`            | `VARCHAR`   | nullable, key part                                        |
| `availability_state`  | `VARCHAR`   | `NOT NULL`, key part, `unavailable\|input_only\|measured` |
| `provider_input`      | `HUGEINT`   | nullable                                                  |
| `cache_read`          | `HUGEINT`   | nullable                                                  |
| `cache_write`         | `HUGEINT`   | nullable                                                  |
| `cache_ratio`         | `DOUBLE`    | nullable                                                  |
| `session_count`       | `UBIGINT`   | `NOT NULL`                                                |

Key and order: `(provider, availability_state)` ascending with null providers last. `cache_ratio` is null unless the state is `measured` and the denominator is non-zero.

##### `capture_health`

| Column                   | DuckDB type | Constraint                         |
| ------------------------ | ----------- | ---------------------------------- |
| `query_model_version`    | `VARCHAR`   | `NOT NULL`, value `query-model-v1` |
| `normalized_source_path` | `VARCHAR`   | `NOT NULL`, key part               |
| `failure_code`           | `VARCHAR`   | nullable, key part                 |
| `valid_count`            | `UBIGINT`   | `NOT NULL`                         |
| `failure_count`          | `UBIGINT`   | `NOT NULL`                         |

Key and order: `(normalized_source_path, failure_code)` ascending with nulls last. A null failure code is the valid-record count for that source and has `failure_count = 0`; a non-null code has `valid_count = 0`. Empty input returns zero rows with the declared schema.

#### Dimension request contract

The command accepts `--dimensions <name>[,<name>...]` and `--time-granularity none|hour|day|week|month`. The Python entry point accepts `dimensions: Sequence[str] = ()` and `time_granularity: Literal[...] = "none"`. Supported dimension names are `project`, `cli`, `provider`, `model`, `agent`, `branch`, and `exit_status`. The declared list order determines key and output ordering, but not totals. For non-empty input, omitted options mean an empty dimension list and `none`, producing one all-input total. Empty input returns zero rows with the declared schema. Duplicate or unknown names are errors. Selecting a time dimension is expressed only through a non-`none` granularity; `period_start` is UTC and uses DuckDB calendar truncation, with ISO Monday starts for weeks.

#### Logical-run and source-position contract

The registry keys are exactly the producer values `claude-code`, `pi`, `codex`, and `copilot`. Logical-run identity is `(cli, session_id, run_id)`. Claude Code and Pi descendants contribute once per distinct key. Codex and Copilot descendants remain attribution-only. `parent_run_id` defines ancestry and is not an identity field. Evidence source, capture sequence, and record content are excluded after reduction.

Before latest-snapshot selection, strict preflight groups all evidence snapshots by logical-run key and requires exactly one distinct `parent_run_id`, with null treated as a value. If snapshots disagree, every evidence snapshot for that key is classified as `USAGE_ANCESTRY_PARENT_CONFLICT`; no snapshot establishes or overrides the parent. The conflict enters the query-scoped failure relation and blocks canonical accounting.

Each `(cli, session_id)` partition must form one rooted directed tree. The root is the only logical run whose `parent_run_id` is null. Every non-root `parent_run_id` must resolve to a distinct logical run in the same CLI and session partition. The graph must be acyclic, and every run must be reachable from the unique root. A direct child names the root's `run_id`; descendants are the transitive closure of valid parent links.

Strict preflight reports ancestry failures before accounting. Root count other than one is `USAGE_ANCESTRY_ROOT_COUNT`. A parent ID absent from every selected run is `USAGE_ANCESTRY_PARENT_MISSING`. A parent ID found only under another CLI or session is `USAGE_ANCESTRY_PARENT_BOUNDARY`. A self-link is `USAGE_ANCESTRY_SELF_PARENT`. A directed cycle is `USAGE_ANCESTRY_CYCLE`. All detectable failures enter the query-scoped failure relation; any such failure blocks every stable view except `capture_health`.

Canonical session dimensions and `captured_at` come from the selected root snapshot. Additive Claude and Pi descendants contribute measures but do not replace root dimensions. Cache aggregation uses exactly the logical runs whose measures contribute under the selected CLI conservation rule.

A source path is made relative to the selected usage directory, converted to `/` separators, stripped of `.` segments, rejected if absolute or containing `..`, decoded as valid UTF-8, and normalized segment-by-segment to Unicode NFC. Source position is `(normalized_source_path, source_line)`, comparing paths lexicographically by unsigned UTF-8 bytes and lines as one-based unsigned integers. The latest snapshot is the maximum `(capture_sequence, normalized_source_path, source_line)` tuple, with numeric ordering for the first and last items.

The command registers query-scoped valid and failure relations. `capture_health` remains queryable when failures exist. Every other published view exits non-zero without a partial result until the failure relation is empty. An empty input directory succeeds with typed empty results.

Stable output reads only published views. A diagnostic mode may expose valid and invalid lines, must label the result incomplete, and cannot export a stable result. Parquet replacement occurs only after schema and logical-row round-trip verification; provenance records the query-model version and input-set digest.

### Usage-analysis component lifecycle

| Operation                     | Effect                                                                                                  | Preserved boundary                       |
| ----------------------------- | ------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| `init-factory --with-usage`   | Installs `.agent-factory/usage-analysis/` during initial setup and records `installed_components.usage` | Existing raw usage data                  |
| `init-factory --add usage`    | Adds and records the component after Factory installation                                               | Factory core, CLI wiring, raw usage data |
| `init-factory --update usage` | Replaces only a compatible installed component and refreshes its install metadata                       | Factory core, CLI wiring, raw usage data |
| `init-factory --remove usage` | Removes only the component and its manifest entry                                                       | Raw usage data and capture               |
| `update-factory`              | Updates Factory core and reports component presence                                                     | Installed components                     |
| `remove-factory`              | Performs the existing complete uninstall, including analysis and raw usage data                         | Nothing beneath `.agent-factory/`        |

All component operations are idempotent. An update whose consumer range excludes the installed contract version aborts before replacement unless explicitly forced. Component operations use a component namespace distinct from CLI names; components have no dot-directory integration, symlinks, guardrails, or capture hooks.

### Contract ownership boundaries

| Contract                                                   | Sole owner                      |
| ---------------------------------------------------------- | ------------------------------- |
| Record schema and cross-field validity                     | Usage contract gate             |
| Supported CLI registry completeness                        | Accounting registry gate        |
| Snapshot and conservation arithmetic                       | SQL accounting contract tests   |
| File-order independence                                    | Reproducibility gate            |
| All-line classification and strict refusal                 | Operational preflight           |
| Local, transcript-blind dependency boundary                | Boundary integration test       |
| Published-view table, JSON, relation, and Arrow projection | Query-command integration tests |
| Atomic attributable export                                 | Parquet round-trip test         |
| Capture independence                                       | Existing capture contract tests |
| Component installation, update, removal, and idempotency   | Distribution lifecycle tests    |
| Factory-to-Usage Analysis dependency direction             | `dependency-check`              |
| Locked DuckDB and PyArrow runtime isolation                | Distribution dependency gate    |
| DuckDB UI launch documentation and six-view bootstrap      | UI documentation smoke test     |

Non-owning layers may exercise a journey but must not duplicate the owner's assertions.
