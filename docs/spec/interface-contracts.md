# Interface Contracts — Factory Flow Control

Command-line contract for every script this specification covers: inputs, flags, outputs, and exit codes. All scripts are stdlib-only Python 3.8+; none requires a virtualenv.

## `.agent-factory/factory/scripts/trigger`

|                 |                                                                                                                                                                        |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage           | `trigger agent <name> [--background\|--interactive] [--cli claude\|copilot] [--cwd DIR]`                                                                               |
|                 | `trigger playbook <name> --step <agent-name-or-index> [--background\|--interactive] [...]`                                                                             |
|                 | `trigger list`                                                                                                                                                         |
| Reads           | `.agent-factory/factory/INDEX.yaml`'s source data (via `index-lint`'s loaders); `config/model.conf` (via `matrix-lint`'s parser); the resolved agent's definition file |
| Writes          | Nothing of its own — the dispatched CLI subprocess writes whatever its own session produces                                                                            |
| Exit code       | The invoked CLI's own exit code (`--background`); `0` after printing launch instructions (`--interactive`); `2` on a resolution error                                  |
| Default `--cli` | `claude`                                                                                                                                                               |

See `UC-04`.

## `.agent-factory/factory/scripts/dispatch`

|               |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage         | `dispatch init --base <branch> --stories <ids> [--feature-branch <name>] [--baseline-commit --yes]`<br>`dispatch plan --backlog-dir backlog [--stories <ids>]`<br>`dispatch prepare-wave <wave>`<br>`dispatch prepare-story <story-id>`<br>`dispatch mark-dispatching <story-id>`<br>`dispatch mark-dispatched <story-id>`<br>`dispatch verify-story <story-id> --sha <sha>`<br>`dispatch escalate <story-id>`<br>`dispatch merge-story <story-id> [--dry-run]`<br>`dispatch mark-blocked <story-id> --reason <text>`<br>`dispatch mark-failed <story-id> [--class CLASS] [--evidence PATH]`<br>`dispatch re-dispatch <story-id>`<br>`dispatch close-wave <wave>`<br>`dispatch suggest-merge-args` |
| Reads         | Backlog stories, `config/project.json`, `config/model.conf`, git state, and the active dispatch ledger (`.current-work/<feature-branch>/dispatch-ledger.yaml` after `init`; `--ledger` may override)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Writes        | `init` creates the feature branch/worktree namespace and ledger under `.current-work/<feature-branch>/dispatch-ledger.yaml`; `prepare-wave` / `prepare-story` prepare story worktrees, run pre-spawn `verify-base`, and update ledger state to `prepared`; `mark-*`, `verify-story`, `merge-story`, and `close-wave` advance the same ledger and append wave closeout data                                                                                                                                                                                                                                                                                                                         |
| Exit code     | `0` on success or idempotent no-op; non-zero on missing ledger, malformed ledger, missing story, invalid transition, failed verification, blocked merge, or failed initialization/planning precondition                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| stdout/stderr | Human-readable planning output or errors; no structured output contract beyond subcommand success/failure                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |

`dispatch` is the script-owned implementation dispatch state machine. `prepare-wave` / `prepare-story` establish the `prepared` state by creating the story branch/worktree, recording the declared base, writing the step manifest, and running `verify-base` before any developer-agent spawns. `escalate` performs a read-only check of the ledger, branch verification, and scope boundaries before granting a one-tier promotion or blocking the story when the wave slot is exhausted. `merge-story` runs `premerge-check` with the story's declared `outputs`, else its `touches`, as the scope: a plain entry as `--scope`, an entry with `*` or `?` as `--scope-glob`. It always adds three paths to the scope: `backlog/<story-id>.md`, whose status the merge updates; `docs/spec/work/spec-feedback-<story-id>.md`, the story's drift report (ADR-0029); and `packages/factory/INDEX.yaml`, which the `index-lint` hook rewrites during a commit. `merge-story` passes `--max-files` scaled from the story's declared `outputs` count (`max(20, len(outputs) * 2)`, so the pre-existing default of 20 holds for small stories). It then performs the merge, updates the story file status in the merge commit, runs post-merge tests, and records the terminal outcome in the ledger. `close-wave` succeeds only when every story in the requested wave is terminal, and it records a wave closeout entry with completed, blocked, failed, next_ready, and branch_head fields. `suggest-merge-args` reads the ledger and sums each story's declared `outputs` count to print a recommended `--max-files` value (floored at 20) for the final feature-branch-to-dev merge, which routinely exceeds any single story's per-story threshold.

While a `critical` finding lacks text in `stop_confirmed_by` or in `stop_confirmed_reason`, the subcommands that start or merge work exit `1` with the stop notice, as [The stop in `dispatch` and `premerge-check`](#the-stop-in-dispatch-and-premerge-check) defines.

## `.agent-factory/factory/scripts/step-guard`

|             |                                                                                                                                                                                                                                                                              |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage       | `step-guard --guard-type read\|write\|bash\|context`                                                                                                                                                                                                                         |
| Reads       | One JSON tool event on stdin; `.current-work/current-step.yml` when present; declared inputs/outputs and `max_input_tokens` from the event or manifest                                                                                                                       |
| Writes      | Nothing — read-only; deny reasons to stderr on refusal                                                                                                                                                                                                                       |
| Exit code   | `0` on allow; `1` on scope/budget denial; `2` on malformed JSON or malformed event/manifest                                                                                                                                                                                  |
| Guard types | `read` checks one path against declared inputs and always-allowed prefixes; `write` checks one path against declared outputs plus the security deny-list; `bash` extracts obvious read/write paths from common shell commands; `context` compares estimated tokens to budget |

`step-guard` is intentionally best-effort for Bash path extraction. It allows commands with no extractable path, and it treats declared input size as file bytes divided by 4 when estimating context usage.

See `UC-12`.

## `.agent-factory/factory/scripts/index-lint`

|           |                                                                                                                                                                                                                                                      |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage     | `index-lint [--agents-dir DIR] [--skills-dir DIR] [--playbooks-dir DIR] [--rulebooks-dir DIR] [--out PATH] [--check]`                                                                                                                                |
| Reads     | `.agent-factory/factory/agents/*.md`, `.agent-factory/factory/skills/*/SKILL.md`, `.agent-factory/factory/playbooks/*.md`, `.agent-factory/factory/rulebooks/**/*.md` (excluding templates)                                                          |
| Writes    | `.agent-factory/factory/INDEX.yaml` (or `--out`), unless `--check` or content is unchanged                                                                                                                                                           |
| Exit code | `0` if up to date (now or already); `1` in `--check` mode if it was stale. `1` in either mode on a reviewer finding, an agent in the rejected flat format, a duplicate name, or a malformed `any_of` input; `index-lint` then writes no `INDEX.yaml` |
| stderr    | One `[WARNING]` per: agent missing `phase-name`, skill missing `category`, agent `total_tokens` exceeding 20 000, tiktoken unavailable                                                                                                               |

See `UC-06`.

## `.agent-factory/factory/config/hooks/block-dangerous-git.sh`

|            |                                                                                                                                                                                           |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Invocation | Native `PreToolUse` hook for Claude Code, GitHub Copilot CLI, and Codex; command JSON on stdin                                                                                            |
| Reads      | `.tool_input.command`, `.toolArgs.command`, or `.tool_input.cmd`, according to the calling runtime; `docs/testing.yaml` (charter-declared test commands for the agent allowlist — BR-024) |
| Writes     | Deny reason to stderr; `{"permissionDecision":"deny","permissionDecisionReason":"..."}` to stdout on deny                                                                                 |
| Exit code  | `0` allow; `2` deny (shared by the three native-hook CLIs)                                                                                                                                |

See `UC-07`.

## `.agent-factory/factory/config/extensions/run-agent.ts` — the `run_agent` tool

|            |                                                                                                                                                                                                                                                                                                             |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Invocation | Pi model-callable tool `run_agent(agent: string, task: string, model?: string)`, registered by the project-local extension when Pi trusts the project                                                                                                                                                       |
| Reads      | `.agent-factory/factory/agents/<agent>.md` (persona and `tier` frontmatter); `config/model.conf` `pi.<tier>` (via the shared tier resolver); the `PI_RUN_AGENT_DEPTH` env var                                                                                                                               |
| Spawns     | `pi --no-session -a --mode json --model <m> --append-system-prompt <agent.md> -p <task>` in the project directory, with `PI_RUN_AGENT_DEPTH` incremented                                                                                                                                                    |
| Streaming  | Asynchronously spools complete stdout to protected capture staging, incrementally parses arbitrarily chunked JSONL with bounded non-result state, and emits bounded progress updates                                                                                                                        |
| Returns    | A BR-040 bounded result envelope plus `{ usage, exitCode }` parsed from the child's final assistant `message_end`; an error result on unknown agent, unresolved model, exceeded depth, spawn failure, non-zero/no-result exit, or cancellation                                                              |
| Capture    | Hands the complete raw staging file to detached best-effort usage capture; capture failure leaves the agent result unchanged, and cancellation terminates the process group through bounded `SIGTERM` → `SIGKILL` escalation, bounds pipe drain, cleans staging, and returns a distinct no-retry diagnostic |
| Guardrail  | The child loads `.pi/extensions/`, so the git-safety guardrail binds it too; the charter-declared test commands from `docs/testing.yaml` are allowlisted with exact matching                                                                                                                                |

See `UC-10`.

## `.agent-factory/factory/scripts/usage-capture`

|                   |                                                                                                                                                      |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Invocation        | `usage-capture --cli <claude-code\|copilot\|codex\|pi\|opencode> --transcript PATH --session ID [--model MODEL] [...]`                               |
| Reads             | One CLI-native transcript, explicit invocation context, and `config/project.json`                                                                    |
| Writes            | One normalized JSONL usage record with non-null `project_id` and `project_name`, configured evidence, and session-end derived signals when available |
| Model attribution | Explicit `--model` first; otherwise the latest non-empty native transcript model; otherwise null                                                     |
| Required coverage | A model-bearing contract fixture for every CLI registered in `SUPPORTED_CLIS`                                                                        |

Derived session-end fields are `cache_miss_turns`, `cache_miss_input_tokens`, `late_early_input_ratio`, `cli`, `provider`, and `usage_capability`. `usage_capability` is `full-cache`, `input-only`, or `unavailable`. Exact eligible-turn, predicate, partition, formula, zero, and null rules are canonical in BR-042. The fields are retrospective evidence only.

See `system-use-cases.md § Usage capture attribution`.

## Business Rules

- **BR-036**: usage capture applies model attribution in this order: explicit invocation context, latest non-empty CLI-native transcript model, then null; registry-complete contract coverage is mandatory.

## `.agent-factory/factory/scripts/handoff-lint`

|           |                                                                                                                                                                         |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage     | `handoff-lint <handoff-path> [--repo-root DIR]`                                                                                                                         |
| Reads     | The handoff document, referenced artifact paths, and repository branch, upstream, and HEAD state                                                                        |
| Writes    | Nothing; validation is read-only                                                                                                                                        |
| Exit code | `0` when every structural and referential rule passes; non-zero when any required content is absent or malformed                                                        |
| Reports   | Every mechanically detectable missing section/declared field/path, malformed exact SHA, malformed declared repository state/evidence, or missing next action in one run |

`handoff-lint` does not infer undeclared decisions, open items, evidence, or artifact references. A designated semantic review against outgoing phase evidence is a separate phase-closure obligation (BR-049).

See `UC-11`.

## Child-result envelope

| Field            | Contract                                                                                                                    |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `disposition`    | Required pass/fail/block outcome                                                                                            |
| `finding_counts` | Required counts keyed by the four severities `critical`, `major`, `minor`, and `note`; zero counts remain explicit (BR-093) |
| `artifact_paths` | Required complete list of canonical tracked report and finding paths                                                        |
| `next_action`    | Required one-to-three-sentence downstream action                                                                            |
| Full detail      | Forbidden in the envelope; it is persisted before return and read deliberately from `artifact_paths` if needed              |

The envelope applies to native subagents, `run_agent`, and `dispatch_wave`; runtime-specific transport may differ but content does not (BR-040).

## `factory/scripts/init-factory`

|                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage              | `init-factory [--source DIR] [--target DIR]`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Reads              | The source checkout's `.agent-factory/factory/`; the target's existing `.gitignore`, runtime hook/settings files, `.pre-commit-config.yaml`, and `config/model.conf`, if present; the `factory_version` of the prior `.agent-factory/install.json`, read before the new version is written                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Writes             | `.agent-factory/factory/` (copy, once), `.gitignore` (merge), `.claude/`, `.github/`, `.codex/`, `.agents/`, and `.pi/` runtime surfaces, `config/model.conf` (copy, once), `.pre-commit-config.yaml` (symlink or merge)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Layout migration   | Runs `migrate-spec-layout` as its last step only on an update. An update is a run where `install.json` exists and records a factory version older than the layout release `1.4.0`, the constant `LAYOUT_RELEASE`. `init-factory` passes its `--target` directory as the `TARGET` argument. It captures the output of `migrate-spec-layout` and prints it after the script exits, so the output passes the redaction of BR-077. Only a run without `install.json` is a first install. A first install and a later run at the same or a newer version move no project file. A first install runs `migrate-spec-layout --dry-run`, prints each line of its plan as `init-factory: old layout: <line>`, and names `.agent-factory/factory/scripts/migrate-spec-layout` as the command the developer can run. See [core-artifact-layout.feature](features/core-artifact-layout.feature) |
| Version comparison | Follows the precedence of Semantic Versioning 2.0.0. So `1.4.0` is older than `1.10.0`, and the prerelease `1.4.0-rc` is older than `1.4.0`. A missing `factory_version`, the value `unknown`, a value that does not parse as a semantic version, such as `dev`, and an `install.json` that does not parse count as older                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Version record     | On an update, writes the new `factory_version` into `install.json` only after `migrate-spec-layout` succeeds. When the migration fails, `install.json` keeps the prior `factory_version`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Failed migration   | Reports that the project is still in the old layout, names the fix: run the factory update again, and exits non-zero                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Test regime draft  | Creates `docs/testing.yaml` with `test_command` only when the file is missing and the scan finds exactly one test command; asks when it finds several; never overwrites the file. This is the one write besides the test-strategy agent; the stakeholder confirms the draft in the fitting step "Test regime" (CAO-G30)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Exit code          | `0` on success, including a clean no-op re-run; `1` on any collision or unsupported existing state, and when `migrate-spec-layout` fails                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| stdout/stderr      | One `init-factory: <line>` report line per step; `init-factory: STOPPED — <reason>` on collision. Every line passes the redaction of BR-077, so a URL shows without its user info                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |

See `UC-08`.

## `.agent-factory/factory/scripts/migrate-spec-layout`

`migrate-spec-layout` moves an installed project from the old file layout into the core artifact layout. `init-factory` runs it as its last step on an update, and a developer can run it by hand. The path table of the proposal [core-artifact-layout.md § Path table](../proposals/core-artifact-layout.md#path-table) defines every move. See [core-artifact-layout.feature](features/core-artifact-layout.feature).

|                |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage          | `migrate-spec-layout [--dry-run] [TARGET]`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Project root   | The optional positional `TARGET`, the project directory; it defaults to the current directory, as in `migrate-layout`. `init-factory` passes its `--target` value (CAL-G10)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `--dry-run`    | Prints what a real run prints and changes no file: each planned move, the `theme` line, each `remove:` and `delete by hand:` line, each glossary line, each `link:` and `hook:` rewrite, each duplicate term, the old-path listing, and the `next step:` lines. It skips the two refusals of the Preconditions row for a busy repository and an existing destination, so it also prints the plan in those states. It exits `0`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Reads          | The project's files at the old paths of the path table; `docs/arc42/12_glossary.md`; every `CONTEXT.md` with a `## Language` section, a per-context `CONTEXT.md` that a context map lists included; the factory hook template `config/pre-commit-config.yaml`; the project's `.pre-commit-config.yaml`. For old paths it scans every text file that git tracks or that is untracked and not ignored, outside `.git/` and `.agent-factory/`, except binary files and the removal set. For links it scans every `*.md` file of that set (CAL-G11)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Moves          | Each tracked file of the path table with `git mv`, so git records a rename, also when the file has uncommitted changes. Each untracked or ignored file of the path table with a plain file move, because git holds no history for it. The git state of a file never stops the migration. The Structurizr theme moves from `docs/arc42/themes/` to `docs/assets/themes/`, and the `theme` line of `docs/spec/architecture.dsl` reads `theme ../assets/themes/default/theme.json`, a path relative to the DSL file as before (DEC-14). When `docs/spec/<name>-qa-strategy.md` and `docs/spec/supplementary_specs/<name>-qa-strategy.md` share the new path `docs/spec/work/<name>-qa-strategy.md`, the second one moves to `docs/spec/work/<name>-area-qa-strategy.md`, and the script prints the pair as `same new path: <old> -> <new>, because <old> -> <new>` (IMPL-0001). A move never replaces a file, tracked or untracked                                                                                                                                                                                                                                                                                                                 |
| Removes        | `actor-goal-list.md` and every `use_cases/` folder under `docs/`, `docs/~archive/` included, with `git rm`. A file in that set that is untracked, ignored, or tracked with uncommitted changes, staged or unstaged, stays in place, and the script lists it for the developer to delete. A plain removal or `git rm -f` would lose content that git cannot restore, so the script never uses either. Every other file in `docs/~archive/` stays (DEC-10)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Rewrites       | Each local Markdown link that points at an old path, so it points at the new path. Each relative link inside a moved file, so it resolves from the new folder. Each Markdown link to a removed file, which becomes its link text in a code span. Inline links, images, and reference definitions count as links; a link in front matter, a fenced block, or a code span is an example and stays. An anchor stays with its link. External links and links to paths outside the path table stay. Each rewrite prints one line, `link: <file>: <old target> -> <new target>`, the file at its path after the run. The undo journal holds the old content of each rewritten file before the write. The `files:` value of each hook in the `agent_factory_hook-*` block takes the value of the hook template `config/pre-commit-config.yaml` of the same factory tree, without a question. The script changes only that key and keeps comments, key order, and every other hook. Each such rewrite prints one line, `hook: .pre-commit-config.yaml: <hook id>: <old value> -> <new value>`. The `theme` line of `docs/spec/architecture.dsl`, as the Moves row states, prints `docs/spec/architecture.dsl: theme themes/ -> theme ../assets/themes/` |
| Order          | The script first removes the files of the removal set. It then writes every content edit: the glossary, chapter 12, each `CONTEXT.md`, the link rewrites, the `theme` line, and the hook block. A file that moves gets its edit at its old path, and the move takes the edit along. The moves come last, so a failed move undoes every edit before it                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Glossary       | Moves each chapter 12 section that holds a two-column table into `docs/spec/glossary.md`, under its heading, and writes a new chapter 12 with one link line. A section whose table has another column count stays in chapter 12. When `docs/spec/glossary.md` exists, its sections stay and the chapter 12 sections follow them (DEC-18). Moves the terms of each `CONTEXT.md` with `## Language` into a section of their own and removes that section from the source file. A term is `**Term**:` or the bullet `- **Term**:` or `* **Term**:`; its `_Avoid_:` part fills the Avoid cell, which stays empty without one. A `###` subheading under `## Language` becomes a section of its own, named after the subheading. Text before the first term of a section becomes that section's prose, so no form of the vocabulary stops the script (IMPL-0002, DEC-18). The script stages `docs/spec/glossary.md` with `git add`, and chapter 12 when git tracks it, so `git status` shows the glossary as added. It does not stage an edited `CONTEXT.md`, and it commits nothing. The table form is defined in [entity-model.md § Glossary Entities](entity-model.md#glossary-entities)                                                           |
| Never rewrites | An old path outside a Markdown link, for example in a CI file, a script, or one of the project's own hooks. The factory hook block and the `theme` line of the DSL are the only exceptions, as the Rewrites row states. The script lists each such occurrence instead. `CONTEXT-MAP.md` and a `CONTEXT.md` without `## Language` stay in place for the fold                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Output         | Report lines go to standard output in this order: each move as `<old path> -> <new path>` and the `theme` line; the `remove: <path>` and `delete by hand: <path>` lines; the glossary lines `<source> -> docs/spec/glossary.md: <n> terms` and `keep in docs/arc42/12_glossary.md: <section> (table with <n> columns)`; the `link:` and `hook:` lines; one line `duplicate term: <term> in <section>, <section>` per term in more than one section; the old-path listing; and the `next step:` lines. The listing is the line `Old paths the script did not rewrite:`, then per occurrence `old path: <file>:<line>: <old path>`, the file at its path after the run, and no heading without an occurrence. One `next step:` line names `capture-context --fold-context-map` when a context map or a `CONTEXT.md` exists; another names the cleanup of duplicate terms when the run lists one. A refusal goes to standard error as `migrate-spec-layout: refused, <reason>; no file changed`, and a failure as `migrate-spec-layout: failed: <error>`                                                                                                                                                                                           |
| No work        | On a project without any old path that the proposal's [migration section](../proposals/core-artifact-layout.md#the-migration-script) lists, and with a factory hook block equal to the template, the script moves nothing, prints nothing, and exits `0`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Preconditions  | Before its first change, the script checks the repository. During a merge or a rebase, or while another git process holds the index lock, it changes nothing, names the state, and exits `2`. It also exits `2` without a change when the destination of a planned move already exists, the distinguishable `-area-qa-strategy.md` name included, or when two planned moves still share a destination                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Exit code      | `0` on success, also when it lists duplicate terms (DEC-18), when it has no work, and for `--dry-run`. `1` when it fails partway, after it has undone every change it made: moves, removals, link rewrites, the new or appended `docs/spec/glossary.md` and chapter 12 with their index entries, the removed `## Language` sections, the hook block, and the `theme` line. A file that moved with a plain move moves back with a plain move. `git status` then shows no change against the state before the run. `2` when it refuses before its first change: a busy repository, an existing destination of the path table, two planned moves that still share a destination, or bad arguments; a `## Language` section is never a reason to refuse; an existing `docs/spec/glossary.md` is no reason to refuse                                                                                                                                                                                                                                                                                                                                                                                                                                 |

## `capture-context --fold-context-map`

`--fold-context-map` is a mode of the `capture-context` skill. It turns the bounded contexts of a context map into domain concerns of `docs/agent-context.md`, because that file is the project's one routing file (DEC-07, DEC-13). The developer runs it after `migrate-spec-layout`. See [core-artifact-layout.feature](features/core-artifact-layout.feature).

|                 |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Invocation      | `capture-context --fold-context-map`. Like every mode of the skill, it runs in the orchestrating session with the developer present                                                                                                                                                                                                                                                                                                                                                                                                |
| Reads           | The context map `docs/arc42/CONTEXT-MAP.md`, and every `CONTEXT.md` that holds routing only, which means it has no `## Language` section                                                                                                                                                                                                                                                                                                                                                                                           |
| Precondition    | `docs/agent-context.md` exists. Without it, the mode stops, writes nothing, and names `capture-context --init` as the first step (CAL-G14)                                                                                                                                                                                                                                                                                                                                                                                         |
| Writes concerns | One domain concern in `docs/agent-context.md` per listed context, with the context's description and `Read:` paths. Every `Read:` path passes `concern-lint` `CTX-PATHS`, and none names a `CONTEXT.md` or `CONTEXT-MAP.md`. The domain concerns also route to `docs/spec/glossary.md`. Each such concern carries the fold mark, the line `Folded: yes` directly after its description line. `concern-lint` accepts the mark only in this form and only under `## Domain concerns`, and reports `CTX-SECTIONS` otherwise (CAL-G03) |
| Review          | The skill shows the proposed concerns and link rewrites. It writes them after the developer confirms, then shows the `concern-lint` result (CAL-G14)                                                                                                                                                                                                                                                                                                                                                                               |
| Rewrites links  | Every Markdown link under `docs/` that points at a `CONTEXT.md` or at `CONTEXT-MAP.md`, so that it points at `docs/agent-context.md`                                                                                                                                                                                                                                                                                                                                                                                               |
| Never deletes   | `CONTEXT-MAP.md` and the routing-only `CONTEXT.md` files. The developer deletes them after the review                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Validation      | `concern-lint` passes on the result. After the developer deletes the old files, `link-check` passes on every Markdown file under `docs/`                                                                                                                                                                                                                                                                                                                                                                                           |
| Rescan          | `capture-context --update --scan` keeps every concern marked as folded, also when it is not a scope-map area. See [entity-model.md § Agent Context Entities](entity-model.md#agent-context-entities)                                                                                                                                                                                                                                                                                                                               |

## `.agent-factory/factory/scripts/backlog-lint`

|               |                                                                                                                                                                                    |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage         | `backlog-lint [--backlog-dir DIR] [--format text\|json] [--report-only]`                                                                                                           |
| Reads         | Story files in `backlog/ST-*.md`                                                                                                                                                   |
| Writes        | Nothing; validation is read-only                                                                                                                                                   |
| Exit code     | `1` when there is at least one error-severity finding, `0` when clean or with `--report-only`, `2` on a usage error                                                                |
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

| Field           | Type             | Notes                                                                                                                                                                                                                                                                                                                                                                                                     |
| --------------- | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `deps`          | array of strings | Story IDs that must complete first; must match pattern `ST-\d{4,}`                                                                                                                                                                                                                                                                                                                                        |
| `traces`        | array of strings | Use Case / ADR / component IDs this story implements                                                                                                                                                                                                                                                                                                                                                      |
| `tests`         | array of strings | Pre-existing test file paths covering acceptance criteria; missing files generate warnings only                                                                                                                                                                                                                                                                                                           |
| `risk_domains`  | array of strings | Closed enum: `security`, `privacy`, `data_integrity`, `compatibility`, `reliability`, `operations`                                                                                                                                                                                                                                                                                                        |
| `strategy`      | string           | Closed enum: `direct`, `seams-first`, `deletion`; defaults to `direct` when absent                                                                                                                                                                                                                                                                                                                        |
| `seam_outputs`  | array of strings | Optional seams-first test outputs; validated only when present                                                                                                                                                                                                                                                                                                                                            |
| `impl_outputs`  | array of strings | Optional seams-first implementation outputs; validated only when present                                                                                                                                                                                                                                                                                                                                  |
| `concerns`      | mapping          | `{domain: [string], technical: [string]}`; both keys optional. Names must match `###` headings in `docs/agent-context.md`                                                                                                                                                                                                                                                                                 |
| `quality-gates` | array of strings | Closed enum: `crap-score`, `mutation-testing`. Picks the test guardrails before the `gates` section of `docs/testing.yaml` ([BR-066](validation-rules.md#ownership-and-drift-reports-core-artifact-ownership-br-056br-066)). `test-design-verify` and `dependency-check` are not in the enum, because they run without a pick. Omitting `crap-score`, the default gate, requires justification in `notes` |
| `notes`         | string           | Free-text; required justification when `quality-gates` omits `crap-score`                                                                                                                                                                                                                                                                                                                                 |

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
- `quality-gates` is a closed enum (`crap-score`, `mutation-testing`); omitting `crap-score` requires justification in `notes`, and omitting `dependency-check` needs no note

## `.agent-factory/factory/scripts/arch-lint`

`arch-lint` compares the Structurizr model with chapter 5 of the arc42 documentation and checks ADR frontmatter. In the core artifact layout it reads the DSL from `docs/spec/` and chapter 5 from `docs/arc42/` (CAL-G16). It never falls back to `docs/arc42/architecture.dsl` (DEC-11). See [core-artifact-layout.feature](features/core-artifact-layout.feature).

|                            |                                                                                                                                                                                                                                                                                |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Usage                      | `arch-lint [--dsl PATH] [--docs-dir DIR] [--no-validate] [--allow-missing-docs-dir]`                                                                                                                                                                                           |
| `--dsl`                    | The Structurizr workspace. Default `docs/spec/architecture.dsl`. The file must lie inside the docs folder, which is the parent of `--docs-dir`                                                                                                                                 |
| `--docs-dir`               | The arc42 folder that holds `05_building_block_view.md`. Default `docs/arc42`. Its parent is the docs folder: images are read from `assets/images/` and ADRs from `adr/` there                                                                                                 |
| `--no-validate`            | Skips `structurizr validate`                                                                                                                                                                                                                                                   |
| `--allow-missing-docs-dir` | A missing `--docs-dir` gives the warning `ARCH-NO-DIR` instead of exit `2`; the DSL and ADR checks still run                                                                                                                                                                   |
| Calls                      | `structurizr validate` and, when the workspace property `arc42.projected` is `"true"` and an image is older than the DSL, `structurizr export-all`. Both run with `STRUCTURIZR_DOCS` set to the docs folder and `STRUCTURIZR_WORKSPACE` set to the `--dsl` path relative to it |
| Writes                     | Re-exported SVGs in `docs/assets/images/` when they are stale; nothing else                                                                                                                                                                                                    |
| Exit code                  | `1` when at least one error-severity finding exists; `2` when `--docs-dir` is not a directory and `--allow-missing-docs-dir` is absent; `0` otherwise                                                                                                                          |

## `.agent-factory/factory/scripts/structurizr`

|                         |                                                                                                                                          |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Usage                   | `structurizr export-svg\|export-all\|validate\|list-views`                                                                               |
| `STRUCTURIZR_DOCS`      | The docs folder, mounted into the container at `/workspace`. Default `./docs`                                                            |
| `STRUCTURIZR_WORKSPACE` | The DSL file, relative to the docs folder. Default `spec/architecture.dsl`                                                               |
| `STRUCTURIZR_IMAGE`     | The container image. Default `structurizr/structurizr:2026.05.22-playwright`                                                             |
| Writes                  | `export-svg` and `export-all` write SVGs to `assets/images/` in the docs folder                                                          |
| Exit code               | `1` when Docker is missing, the docs folder is missing, or the workspace file is missing; otherwise the exit code of the Structurizr CLI |

## `.agent-factory/factory/scripts/publish-docs`

`publish-docs` renders the documents of `docs/publish-docs.yaml` as one PDF. In the core artifact layout it reads the DSL from `docs/spec/` and the themes from `docs/assets/themes/` (CAL-G16). It never reads `docs/arc42/architecture.dsl` (DEC-11). Wherever the manifest selects `arc42/12_glossary.md`, by name or by glob, the PDF shows `docs/spec/glossary.md` when that file exists (DEC-16).

|            |                                                                                                                                                                                     |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage      | `publish-docs pdf`, run in the project root                                                                                                                                         |
| Reads      | `docs/publish-docs.yaml`, `docs/publish-docs.css` when present, every document the manifest selects, `docs/spec/architecture.dsl`, and `docs/assets/themes/` when present           |
| Build copy | `docs/spec/` and `docs/assets/themes/` are copied to `.current-work/publish-docs/build/model/` at the same relative paths, so a `theme ../assets/themes/<file>` line resolves there |
| Calls      | `structurizr validate` and `structurizr export-svg`, with `STRUCTURIZR_DOCS` set to the build copy and the default `STRUCTURIZR_WORKSPACE`                                          |
| Chapter 12 | A manifest entry or glob match `arc42/12_glossary.md` resolves to `docs/spec/glossary.md` when it exists; the manifest never needs a change                                         |
| Writes     | `docs/dist/<project>-architecture.pdf`, and `docs/dist/` in `.gitignore` when it is missing                                                                                         |
| Exit code  | `0` PDF written; `1` a check failed; `2` a precondition failed, among them a missing `docs/spec/architecture.dsl`, which the message names                                          |

## `.agent-factory/factory/scripts/dependency-check`

|                 |                                                                                                                                                                           |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage           | `dependency-check [--dsl-path PATH] [--source-root DIR] [--story-id ID] [--report-dir DIR]`                                                                               |
| `--dsl-path`    | The dependency rules. Default `docs/spec/dependency-rules.dsl`                                                                                                            |
| `--source-root` | The folder whose Python files are scanned. Default `.`                                                                                                                    |
| Writes          | A JSON report to `<report-dir>/<story-id>.json`, by default under `.current-work/dependency-check/`                                                                       |
| Stdout          | The same rows as the report file                                                                                                                                          |
| Exit code       | `1` when a rule fails; `2` when the rules file or the source root is missing; `0` otherwise                                                                               |
| Owner           | Each failing result entry carries `owner: architecture-agent`, the agent that fixes the violation. A passing entry carries no `owner` (field name decided in gap CAO-G07) |

## `.agent-factory/factory/scripts/scope-lint`

`scope-lint` checks the scope declaration of each governed artifact. In the core artifact layout it reads feature files, the DSL, and the entity model from `docs/spec/` (CAL-G16). It never reads their paths from before the migration (DEC-11).

|              |                                                                                                                                                                                                                           |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage        | `scope-lint [--base-dir DIR] [--format text\|json]`                                                                                                                                                                       |
| `--base-dir` | The project root. Default `.`                                                                                                                                                                                             |
| Reads        | `docs/proposals/*.md`, `backlog/epics-*.md`, `backlog/ST-*.md`, `docs/spec/features/*.feature`, `docs/spec/scope-map.md`, `docs/spec/architecture.dsl`, `docs/spec/entity-model.yaml` or else `docs/spec/entity-model.md` |
| Valid scope  | `global` or the ID of a workstream in `.agent-factory/workstreams/`                                                                                                                                                       |
| Exit code    | `1` when a file has no scope declaration or an unknown value; `0` otherwise                                                                                                                                               |

## `.agent-factory/factory/scripts/module-graph-check`

|           |                                                                                                                                                                         |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage     | `module-graph-check [--dsl-path PATH] [--interface-contracts PATH] [--entity-model PATH] [--proposal PATH] [--story-id ID] [--report-dir DIR]`                          |
| Reads     | `docs/spec/architecture.dsl`; `docs/spec/interface-contracts.md`; `docs/spec/entity-model.md`; the proposal file (when `--proposal` given)                              |
| Writes    | `.current-work/module-graph-check/<story-id>.json`; updates `impact.architecture_change` in proposal frontmatter (when `--proposal` given and override semantics apply) |
| Exit code | `0` on success (regardless of architecture_change result); `2` on missing input file                                                                                    |
| stdout    | `architecture_change=true\|false`; optional `new_modules=`, `new_dependency=`, `inverted_dependency=` lines                                                             |

The three path arguments default to the core in `docs/spec/`: `--dsl-path` to `docs/spec/architecture.dsl`, `--interface-contracts` to `docs/spec/interface-contracts.md`, and `--entity-model` to `docs/spec/entity-model.md` (ST-0341). A project in the old layout passes its paths explicitly.

The script derives the module map from `architecture.dsl` (containers, components, relationships), compares it against Phase 1 outputs, and checks three conditions: (a) new module not in DSL, (b) changed public interface, (c) new or inverted dependency direction. Override semantics: `false`→`true` machine wins (annotated `# mechanical detection`); `true`→`false` prior human declaration respected conservatively. A new entity in an existing module does not trigger `architecture_change=true`.

## `.agent-factory/factory/scripts/test-design-verify`

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

The `gates` section centralizes gate configuration that the dispatcher reads at runtime. It does not define gate execution ordering; [ADR-0012](../adr/0012-dispatcher-owned-semantic-gate-loop.md) owns the dispatcher's gate sequence.

The section picks only the test guardrails. `dependency-check` has no entry here, because the implementation agent runs it after every story ([BR-066](validation-rules.md#ownership-and-drift-reports-core-artifact-ownership-br-056br-066)).

The section replaces `default_quality_gates` in `docs/charter/house-rules.md`. When `premerge-check` still finds `default_quality_gates`, it prints a warning that names the file (CAO-G28).

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

| Field                                    | Type    | Required | Notes                                                                                                                                                                                                                                     |
| ---------------------------------------- | ------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gates.crap_score.enabled`               | bool    | yes      | Whether the dispatcher runs the crap-score gate                                                                                                                                                                                           |
| `gates.crap_score.threshold`             | float   | yes      | Per-function CRAP threshold; replaces the dead-code house-rules lookup                                                                                                                                                                    |
| `gates.mutation_testing.enabled`         | bool    | yes      | Whether the dispatcher runs mutation testing; `false` until infrastructure ready                                                                                                                                                          |
| `gates.mutation_testing.command`         | string  | no       | The project's mutation command, written by the test-strategy agent. Enabled without a command, the gate fails and names the test-strategy agent (BR-066). The tool's own configuration lives in the project's files, not here (DEC-36)    |
| `gates.mutation_testing.timeout_minutes` | integer | no       | The time limit of the mutation command in minutes; default 30. The gate script `packages/factory/scripts/mutation-testing` stops the command at the limit and writes a failing result file. The merge reads that result (BR-066, CAO-G27) |
| `gates.test_design_verify`               | —       | no       | Conditional; active when test-design output exists in the story                                                                                                                                                                           |

### Gate result files

Each gate writes one result file to `.current-work/<gate>/<story-id>.json`. `premerge-check` reads it before a story merge and accepts two shapes (`read_gate_result`). A missing file fails as `result not found`. A file that is not valid JSON, or holds neither shape, fails as `invalid result`.

| Gate                 | Writer                                        | Shape                                                                                                                               | Passes when                                             |
| -------------------- | --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| `crap-score`         | `packages/factory/scripts/crap-score`         | A list of rows, one per function, each with `pass_fail`                                                                             | Every row has `pass_fail: "pass"`; an empty list passes |
| `dependency-check`   | `packages/factory/scripts/dependency-check`   | A list of rows, each with `pass_fail`: one `fail` row per violating import and per unparsable file, one `pass` row per passing rule | Every row has `pass_fail: "pass"`; an empty list passes |
| `test-design-verify` | `packages/factory/scripts/test-design-verify` | An object with `passed`                                                                                                             | `passed` is `true`                                      |
| `mutation-testing`   | `packages/factory/scripts/mutation-testing`   | An object with `passed`                                                                                                             | `passed` is `true`                                      |

The gate script `packages/factory/scripts/mutation-testing` runs as `mutation-testing --story-id ST-NNNN [--testing-yaml PATH] [--report-dir DIR]`. It runs `gates.mutation_testing.command` within the time limit and writes `<report-dir>/<story-id>.json`, by default under `.current-work/mutation-testing/`. It prints the result to stdout. It exits `0` when the command exited `0` within the limit, `1` when the gate failed or could not run, and `2` on a usage error (BR-066).

| Field             | Type            | Contract                                                                                                  |
| ----------------- | --------------- | --------------------------------------------------------------------------------------------------------- |
| `story_id`        | string          | The story from `--story-id`                                                                               |
| `passed`          | bool            | `true` only when the command exited `0` within the time limit                                             |
| `command`         | string or null  | The command from `gates.mutation_testing.command`; `null` when the gate could not run                     |
| `timeout_seconds` | integer or null | The time limit in seconds, from `timeout_minutes`; `null` when the gate could not run                     |
| `exit_code`       | integer or null | The exit code of the command; `null` after a time-out or when the command did not run                     |
| `timed_out`       | bool            | `true` when the script stopped the command at the time limit                                              |
| `message`         | string          | `passed`, or the reason for the failure. For a missing command, the message names the test-strategy agent |

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

## `.agent-factory/factory/scripts/concern-lint`

|               |                                                       |
| ------------- | ----------------------------------------------------- |
| Usage         | `concern-lint [--root DIR] [--format text\|json]`     |
| Reads         | `docs/agent-context.md`, `backlog/ST-*.md`            |
| Writes        | Nothing; validation is read-only                      |
| Exit code     | Count of error-severity findings (`0` = clean)        |
| Finding codes | `CTX-SECTIONS`, `CTX-PATHS`, `CTX-LEGACY`, `CTX-REFS` |

### Checks

- **CTX-SECTIONS** — Required category headings (`## Always (cross-cutting)`, `## Technical concerns`, `## Domain concerns`) exist; each `###` concern section has a description line and at least one `Read:` path; a fold mark is the line `Folded: yes`, directly after the description line of a concern under `## Domain concerns`.
- **CTX-PATHS** — Every path in a `Read:` or `Boundary:` line resolves to an existing file or glob match, relative to root.
- **CTX-LEGACY** — No legacy YAML agent-context files (other than `testing.yaml`) or `docs/charter/` directory exist alongside `docs/agent-context.md`.
- **CTX-REFS** — Every concern name in any story's `concerns:` frontmatter has a matching `###` heading under "Technical concerns" or "Domain concerns" in `agent-context.md`. Active only when both `docs/agent-context.md` and `backlog/ST-*.md` files exist.

## Referenced from

- [entity-model.md](entity-model.md)
- [validation-rules.md](validation-rules.md)
- [test-design.feature](features/test-design.feature)
- [agent-context.feature](features/agent-context.feature)

## Local Usage Processing and Analysis

The [feature specification](features/local-usage-processing-and-analysis.feature) adds a local analytical consumer while keeping Factory capture as the producer.

### Usage-record contract

| Property             | Contract                                                                                   |
| -------------------- | ------------------------------------------------------------------------------------------ |
| Canonical source     | `packages/factory/contracts/usage-record/contract.yaml` and `v1.schema.json`               |
| Owner                | Factory                                                                                    |
| Schema dialect       | JSON Schema Draft 2020-12                                                                  |
| Installed projection | `.agent-factory/usage-analysis/contract/`                                                  |
| Consumer rule        | Usage Analysis reads only the installed projection and declares its accepted version range |
| Known CLI values     | `claude-code`, `copilot`, `codex`, `pi`, and `opencode` (registry, not schema-enforced)    |
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

The registry keys are exactly the producer values `claude-code`, `pi`, `codex`, `copilot`, and `opencode`. Logical-run identity is `(cli, session_id, run_id)`. Claude Code, Pi, and OpenCode descendants contribute once per distinct key. Codex and Copilot descendants remain attribution-only. `parent_run_id` defines ancestry and is not an identity field. Evidence source, capture sequence, and record content are excluded after reduction.

Before latest-snapshot selection, strict preflight groups all evidence snapshots by logical-run key and requires exactly one distinct `parent_run_id`, with null treated as a value. If snapshots disagree, every evidence snapshot for that key is classified as `USAGE_ANCESTRY_PARENT_CONFLICT`; no snapshot establishes or overrides the parent. The conflict enters the query-scoped failure relation and blocks canonical accounting.

Each `(cli, session_id)` partition must form one rooted directed tree. The root is the only logical run whose `parent_run_id` is null. Every non-root `parent_run_id` must resolve to a distinct logical run in the same CLI and session partition. The graph must be acyclic, and every run must be reachable from the unique root. A direct child names the root's `run_id`; descendants are the transitive closure of valid parent links.

Strict preflight reports ancestry failures before accounting. Root count other than one is `USAGE_ANCESTRY_ROOT_COUNT`. A parent ID absent from every selected run is `USAGE_ANCESTRY_PARENT_MISSING`. A parent ID found only under another CLI or session is `USAGE_ANCESTRY_PARENT_BOUNDARY`. A self-link is `USAGE_ANCESTRY_SELF_PARENT`. A directed cycle is `USAGE_ANCESTRY_CYCLE`. All detectable failures enter the query-scoped failure relation; any such failure blocks every stable view except `capture_health`.

Canonical session dimensions and `captured_at` come from the selected root snapshot. Additive Claude, Pi, and OpenCode descendants contribute measures but do not replace root dimensions. Cache aggregation uses exactly the logical runs whose measures contribute under the selected CLI conservation rule.

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

## Eligibility and Orchestration Commands

All scripts are stdlib-only Python 3.10+.

Proposal trace: [activity-graph-orchestration.md](../proposals/activity-graph-orchestration.md)

### `.agent-factory/factory/scripts/intent select`

|           |                                                                                                                                            |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Usage     | `intent select [--workstream ID]`                                                                                                          |
| Reads     | Agent definitions under `.agent-factory/factory/agents/`, the repository filesystem, the session binding                                   |
| Writes    | Nothing — read-only                                                                                                                        |
| Exit code | `0` on success; `2` on invalid input                                                                                                       |
| stdout    | Every agent listed with its name, description, and each required input marked satisfied or unsatisfied with evidence (matched path or gap) |
| Behavior  | Calls the precondition evaluator for all agents, applies scope filtering when a workstream is bound, and formats the result for the human  |

### `.agent-factory/factory/scripts/intent assess`

|           |                                                                                                                           |
| --------- | ------------------------------------------------------------------------------------------------------------------------- |
| Usage     | `intent assess [--workstream ID] [--format text\|json]`                                                                   |
| Reads     | Agent definitions, governed artifacts, the repository filesystem                                                          |
| Writes    | Nothing — read-only                                                                                                       |
| Exit code | `0` on success; `2` on invalid input                                                                                      |
| stdout    | Per-artifact validator results in the shared format: artifact type, artifact reference, assessed commit, checks, warnings |
| Behavior  | Runs all applicable validators (mechanical and, when triggered, semantic) and reports results per the shared format       |

### Precondition evaluator (engine API)

|                 |                                                                                                                                                                       |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Module          | `packages/factory/engine/eligibility.py` (tracked source); `.agent-factory/factory/engine/eligibility.py` (installed)                                                 |
| Input           | All agent definitions with `inputs.required` declarations, the repository filesystem, the bound workstream identifier (or null for Open Stage)                        |
| Output          | Per-agent, per-requirement evidence: each required input marked satisfied or unsatisfied, with matched path, condition result, and validator output where applicable  |
| Side effects    | None — the evaluator never writes repository state                                                                                                                    |
| Path resolution | Four ordered steps: glob expansion (placeholders → `*`), scope filtering (match bound workstream or `global`; skipped in Open Stage), condition checking, cardinality |
| Cardinality     | Zero survivors = unsatisfied; one = satisfied; multiple = reported for human or orchestrator selection                                                                |

### Fence runner (engine API)

|                   |                                                                                                                                                                 |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Module            | `packages/factory/engine/fence.py` (tracked source); `.agent-factory/factory/engine/fence.py` (installed)                                                       |
| Input             | The agent's output declarations, pre-activity and post-activity filesystem state                                                                                |
| Output            | Per-output validator results and an aggregate pass/fail result                                                                                                  |
| Storage           | `.agent-factory/checks/fences/<session-id>/<invocation-id>.yaml`                                                                                                |
| Aggregate rule    | Passes when every required output changed, `declarations_changed >= minimum_changed`, and every invoked validator passed                                        |
| Required output   | Must have a created or modified match; missing match fails the fence                                                                                            |
| Optional output   | No match → skipped; changed → validator runs                                                                                                                    |
| Human sessions    | Fence result is informational — no enforcement, no warning for missing or unexpected outputs                                                                    |
| External chaining | The caller (implementation-agent dispatcher, script, or human) inspects the fence result and evaluator evidence to decide whether to dispatch the next activity |

## Usage Record v1 Schema — Deferred Additions

The following fields were planned as v1-additive additions. They are deferred to a future proposal that addresses usage record enrichment, capture-hook integration, and workstream-dimension analysis in bulk:

| Field               | Type               | Description                                    | Status   |
| ------------------- | ------------------ | ---------------------------------------------- | -------- |
| `workstream_id`     | `string` or `null` | Workstream identifier from the session binding | deferred |
| `workstream_origin` | `string` or `null` | Path to the workstream's origin artifact       | deferred |
| `skills_invoked`    | `array` or `null`  | Skill names called during the session          | deferred |

## Research Brief Schema

The precondition graph handles routing: a research agent's output is an artifact, and any agent that declares that artifact as a required input sees the requirement become satisfied when the research completes.

| Field             | Type               | Description                                              |
| ----------------- | ------------------ | -------------------------------------------------------- |
| `decision_needed` | `string` or `null` | The decision the research result must inform (unchanged) |

Standalone research omits this field. The existing survey and falsification routes remain unchanged.

## OpenCode CLI Integration Contracts

Feature trace: [opencode-cli-integration.feature](features/opencode-cli-integration.feature)

### `packages/factory/config/plugins/agent-factory.ts` — Factory plugin

|                 |                                                                                                                               |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Plugin ID       | `agent-factory`                                                                                                               |
| API             | OpenCode V2 `Plugin.define()` with `setup(ctx)` function                                                                      |
| Hooks           | `execute.before`, `execute.after`, `permission.hook("evaluate")`, `session.hook("context")`                                   |
| Reads           | `.current-work/current-step.yml` (step manifest), agent definition frontmatter (tier, permissions, outputs)                   |
| Enforces        | Ordered allow/ask/deny permission rules, step-boundary reads and writes, dangerous Git command denial, tool removal per agent |
| Fails closed on | Initialization failure, manifest loading failure, permission evaluation failure, worktree creation failure                    |
| Error contract  | Error names the failed control and the recovery action                                                                        |

### Plugin permission evaluation

|                |                                                                                                                                         |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Hook           | `permission.hook("evaluate")`                                                                                                           |
| Fires after    | Configured `allow` and `ask` rules                                                                                                      |
| Cannot broaden | A configured `deny` is final. The hook may change `effect` to `deny` but never to `allow` or `ask` when the configured effect is `deny` |
| Effect values  | `allow`, `ask`, `deny`                                                                                                                  |
| Message        | Appears as denial reason or escalated request text                                                                                      |

### Plugin tool removal

|                |                                                                                  |
| -------------- | -------------------------------------------------------------------------------- |
| Hook           | `session.hook("context")`                                                        |
| Removes        | Tools not in the active agent's declared tool set                                |
| Review agents  | Receive read-only permissions unless their procedure declares a write output     |
| Child sessions | Inherit session-scoped restrictions; apply their own generated agent permissions |

### Plugin usage capture

|                     |                                                                  |
| ------------------- | ---------------------------------------------------------------- |
| Observes            | Completed root and child sessions                                |
| Sends to            | Existing Factory usage pipeline                                  |
| Contract            | Existing usage record contract with `cli: opencode`              |
| Double-count guard  | Root session usage does not include child session usage          |
| Completion behavior | Session completion does not reactivate the agent                 |
| Failure behavior    | Usage capture failure is reported but does not block the session |

### Plugin worktree strategy

|                    |                                                                                          |
| ------------------ | ---------------------------------------------------------------------------------------- |
| API                | `ctx.worktree.transform()` with `WorktreeDefinition` interface                           |
| Strategy ID        | `agent-factory`                                                                          |
| Branch creation    | Delegated to Factory scripts (naming, base, verification rules)                          |
| Worktree creation  | Delegated to Factory scripts (path under `.current-work/<feature-branch>/`)              |
| Write denial       | Session-scoped write denial on the primary checkout while isolated work is active        |
| Child session path | OpenCode tracks the worktree location and starts each child session there                |
| Failure behavior   | Fails closed: worktree creation failure denies the dispatch with a named recovery action |

### `init-factory` OpenCode CLI additions

|                   |                                                                                                          |
| ----------------- | -------------------------------------------------------------------------------------------------------- |
| Detection markers | `.opencode/`, `opencode.json`, `opencode.jsonc`                                                          |
| CLI name          | `opencode`                                                                                               |
| Dot-dir           | `.opencode`                                                                                              |
| Version check     | `opencode --version` must report `1.18.31` or later. Failure stops installation with upgrade instruction |
| Creates           | `.opencode/INDEX.yaml`, `.opencode/agents/`, `.opencode/plugins/agent-factory.ts` (link)                 |
| Skills path       | `.agents/skills/` (native OpenCode discovery path)                                                       |
| Orientation       | Injected by the plugin via `session.hook("context")`, not via `instructions` field or root `AGENTS.md`   |
| Manifest          | Records every created OpenCode path in `.agent-factory/install.json`                                     |
| Idempotency       | Repeated installation produces no additional changes                                                     |
| User preservation | User-owned files under `.opencode/` remain unchanged                                                     |

### `model.conf` OpenCode entries

|                |                                                                                                                                              |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Key format     | `opencode.economy`, `opencode.standard`, `opencode.strong`                                                                                   |
| Value format   | `provider/model` identifier                                                                                                                  |
| Missing policy | `on_missing = halt` (existing policy)                                                                                                        |
| Workaround     | Each generated agent definition carries an explicit `model` field from its tier mapping due to model inheritance bug (OpenCode issue #49765) |

### `AGENTS.md` OpenCode additions

|                  |                                                              |
| ---------------- | ------------------------------------------------------------ |
| CLI table        | Adds OpenCode row with `.opencode/INDEX.yaml`                |
| Orientation file | `AGENTS.opencode.md` (new, under `packages/factory/config/`) |
| Root AGENTS.md   | Not replaced — OpenCode orientation is plugin-injected       |

### `AGENTS.opencode.md` — OpenCode orientation

|             |                                                                    |
| ----------- | ------------------------------------------------------------------ |
| Injected by | Factory plugin via `session.hook("context")`                       |
| Describes   | OpenCode tool names, child-session behavior, skill discovery paths |

## Value-First Onboarding Contracts

Proposal trace: [value-first-onboarding-journey.md](../proposals/value-first-onboarding-journey.md)

### `build-release`

| Property    | Contract                                                                              |
| ----------- | ------------------------------------------------------------------------------------- |
| Input       | Versioned Agent Factory source tree and release version                               |
| Output      | `install-agent-factory`, `agent-factory.tar.gz`, and `SHA256SUMS`                     |
| Determinism | Repeated builds from the same source tree and version produce the same archive digest |
| Failure     | Exits non-zero and publishes no partial release set                                   |

### `install-agent-factory`

| Property      | Contract                                                                                                                                           |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Source        | Exactly one of `--from-local <relative-path>` and `--from-remote <URL>`                                                                            |
| Version       | `--version <release>` is valid only with `--from-remote`                                                                                           |
| Target        | First installation requires `--target <path>` and rejects root, user home, unresolved paths, and unsupported content                               |
| Preflight     | Reads host, tools, Git state, network, interfaces, and target; returns `Ready`, `Ready with limitations`, or `Blocked` without changes             |
| Remote assets | Resolves an immutable version URL and verifies `agent-factory.tar.gz` against `SHA256SUMS` before extraction                                       |
| Fixes         | Shows purpose, command, scope, reversal, and verification per supported fix (uv, managed Python); runs it only after affirmative consent           |
| Approval      | Shows source, version, target, interfaces, paths, instruction files, and uninstall command before requesting consent                               |
| Receipt       | Lists changed paths, interfaces, version, resolved source, uninstall command, and one next command                                                 |
| Cancellation  | Blank input is not consent; cancellation reports completed fixes and reversals and leaves the target valid                                         |
| Delegation    | Passes `init-factory` a `--project-name` derived from the target directory, so the project-identity step never falls back to an interactive prompt |

The remote release base exposes `<base>/latest`,
`<base>/releases/<version>/install-agent-factory`,
`<base>/releases/<version>/agent-factory.tar.gz`, and
`<base>/releases/<version>/SHA256SUMS` over HTTPS.

### Instruction header management

| Property   | Contract                                                                                                             |
| ---------- | -------------------------------------------------------------------------------------------------------------------- |
| Discovery  | Finds existing regular files named `AGENTS.md` or `copilot-instructions.md` below the target                         |
| Exclusions | Skips `.git/`, `.agent-factory/`, `.current-work/`, dependency trees, virtual environments, caches, and build output |
| Symlinks   | Does not follow external symlinks and reports matching symlinks as unchanged                                         |
| Injection  | Prepends one idempotent marker-delimited Factory block with links relative to the instruction file                   |
| Manifest   | Records the path, installed block, and original newline state                                                        |
| Update     | Adds, refreshes, or removes only Factory-owned blocks                                                                |
| Removal    | Restores original content and newline state without changing user-owned content                                      |

### `update-factory`

| Property       | Contract                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Default source | Reads the source selector and resolved source from `.agent-factory/install.json`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Check mode     | `--check` reports installed and candidate versions, source, digest, local modifications, and header changes without writing                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Approval       | A normal update requires confirmation before download or mutation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Safety         | Downloads, verifies, and stages the complete replacement before application                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Rollback       | Application failure restores the previous Factory tree and instruction headers                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Layout move    | The approval of the update covers the move into the core artifact layout; the developer is not asked about the move. A failed `migrate-spec-layout` undoes its own changes and fails `init-factory`. `update-factory` then rolls the whole update back: every project file, `.pre-commit-config.yaml` included, has its old path and its old content, the factory tree is the old one, and `install.json` keeps the old factory version. `update-factory` reports the failure. The layout release supports updates only from an installed `update-factory` `v1.1.0-rc` or later, the first release with this rollback. A project on an older release updates to 1.3.x first, as the release notes say. No check enforces this |
| Hook refresh   | After the new factory tree is in place, `update-factory` brings the `agent_factory_hook-*` block of `.pre-commit-config.yaml` to the hook template of the new release. When the update ran the layout migration, that is, when the version recorded before the update is older than the `LAYOUT_RELEASE` of the new `init-factory`, it writes the block without a question and logs `applied the factory hook block of this release to .pre-commit-config.yaml` (DEC-17). Every other update shows the diff and writes only on an explicit yes. A missing file, a symlink, or a file without factory hooks stays as it is                                                                                                     |
| Local changes  | Modified Factory-owned files stop update unless the user selects the existing preservation flow                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Source change  | A different source selector or remote URL requires an explicit option and separate confirmation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Receipt        | Records selected source, immutable version or local revision, remote digest when applicable, and changed paths                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |

### First-session insight

| Property          | Contract                                                                              |
| ----------------- | ------------------------------------------------------------------------------------- |
| Reads             | Real project files needed to detect stack, test entry point, and one safety signal    |
| Writes            | None                                                                                  |
| Output            | Observed facts, explicit unknowns, and one recommended action                         |
| Configuration     | Requests model, hook, or context decisions only before an action that depends on them |
| Ready-host budget | Insight within two minutes and three decisions after installation approval            |

### Gate demonstration

| Property  | Contract                                                                           |
| --------- | ---------------------------------------------------------------------------------- |
| Input     | One Factory-owned disposable fixture and one real Factory gate                     |
| Output    | Failing input, specific failure, corrected input, and passing result               |
| Isolation | Does not change the target project and removes the fixture after the demonstration |
| Decline   | Skipping the demonstration does not change recommended hook defaults               |

### Consumer hook configuration

| Property        | Contract                                                                                                                                                                                                                                                                                                                                                                              |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Metadata source | `packages/factory/config/hook-metadata.yaml` maps each `agent_factory_hook-*` id to an `outcome`, a `trade_off` (`auto-fix`, `material-cost`, or `none`), an `availability`, and a `description`                                                                                                                                                                                      |
| Presentation    | Hooks are grouped by `outcome`; `trade_off: none` hooks are included without asking; `trade_off: auto-fix` or `material-cost` hooks require separate consent                                                                                                                                                                                                                          |
| Unavailability  | A hook whose `availability` condition is unmet by the target project shows its `description`; it is never presented as an error or a choice                                                                                                                                                                                                                                           |
| Exclusion       | `index-lint` is excluded unconditionally; any hook whose `files:` trigger is anchored under `.agent-factory/factory/` and matches nothing in `git ls-files` is excluded (BUG-0029)                                                                                                                                                                                                    |
| `matrix-lint`   | Its generated stanza drops the broken `files:` trigger on the gitignored `.agent-factory/config/model.conf` path for `always_run: true`, and is always ordered last — after model configuration, before dispatch                                                                                                                                                                      |
| Splice          | The filtered, reordered template is handed to `merge-precommit-config` as `--template`; `pre-commit-config.yaml` itself is read-only                                                                                                                                                                                                                                                  |
| Layout move     | `migrate-spec-layout` sets the `files:` value of each hook in the project's `agent_factory_hook-*` block to the value in the new template, without a question. The `arch-lint` hook then matches `docs/spec/architecture.dsl`, `docs/spec/dependency-rules.dsl`, and `docs/arc42/05_building_block_view.md`. The project's own hooks stay unchanged; the script lists their old paths |

### First-task sandbox

| Property                  | Contract                                                                                                               |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Approval                  | Shows goal, duration, artifacts, decisions, and cleanup before creating the sandbox                                    |
| Repository with `HEAD`    | Creates a detached worktree from `HEAD` at `.current-work/onboarding-spike/<session-id>/`; creates no branch or commit |
| Repository without `HEAD` | Creates a plain sandbox at the same path pattern                                                                       |
| Execution                 | Runs the `poc-spike` workflow only inside the sandbox                                                                  |
| Result                    | Shows inspectable output, check results, and removal instructions                                                      |
| Retention                 | Copies separately confirmed artifacts to a named `docs/spikes/` path                                                   |
| Production handoff        | Requires approval for a normal workstream; never promotes the sandbox                                                  |
| Ready-host budget         | Inspectable result within ten minutes and five decisions after installation approval                                   |

## Core Artifact Layout Gate Contracts

### `spec-lint`

| Property       | Contract                                                                                                                                                                           |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Glossary input | `--glossary PATH`, default `docs/spec/glossary.md`, replaces `--context` (CAL-G16). `GLOSS001` reads the Term column of every table in it and strips `**` and `_` around a term    |
| `GLOSS001`     | `info` for a term that no Markdown or feature file under `--spec-dir` uses. The glossary itself and every file under `work/` never count as a use                                  |
| `TRACE002`     | `error` for a business rule that a core file or `features/*.feature` references and no core file defines, whether or not use-case files exist. A feature file never defines a rule |
| Core paths     | Reads `entity-model.md` (required, `STRUCT005`, `TRACE004`), `state-machines.md`, and the todo lists `work/todo.md` and `work/todos.md` under `--spec-dir`; reads no old path      |
| Removed checks | The checks that read use-case files or the actor-goal list are gone (DEC-10): `STRUCT001` to `STRUCT004`, `STRUCT006`, `FMT001` to `FMT004`, `TRACE001`, and `TRACE006`            |
| Exit code      | 1 on any error finding, 0 when clean or with `--report-only`, 2 on a usage error                                                                                                   |

## Core Artifact Ownership Contracts

The contracts of [core-artifact-ownership.feature](features/core-artifact-ownership.feature).
A value that the proposal leaves open carries the identifier of the gap in
[core-artifact-ownership-gaps.md](work/core-artifact-ownership-gaps.md) that decides it.

### `packages/factory/rulebooks/core-artifacts.yaml`

| Property | Contract                                                                                                                                                   |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Readers  | The producer and review contract test, `index-lint` for its reviewer check (CAO-G06), and `dispatch close-wave` to tell core rows from other rows (BR-062) |
| Entry    | `path_pattern`, `sample_path`, `family`, and `optional` (field names decided in CAO-G05)                                                                   |
| Family   | `scope-and-behaviour`, `domain-structure`, `architecture`, or `seam`                                                                                       |
| Optional | `true` when a project may lack the artifact. Its reviewer then declares it as a context input (DEC-25)                                                     |

| Path pattern                       | Family              | Producer              | Reviewed by                    | Optional        |
| ---------------------------------- | ------------------- | --------------------- | ------------------------------ | --------------- |
| `docs/spec/scope-map.md`           | scope-and-behaviour | requirements-agent    | stakeholder                    | false           |
| `docs/spec/features/*.feature`     | scope-and-behaviour | requirements-agent    | spec-review-agent              | false           |
| `docs/spec/areas/*.md`             | scope-and-behaviour | requirements-agent    | spec-review-agent              | true            |
| `docs/spec/glossary.md`            | domain-structure    | domain-modeling-agent | spec-review-agent, stakeholder | false           |
| `docs/spec/entity-model.md`        | domain-structure    | domain-modeling-agent | spec-review-agent              | false           |
| `docs/spec/state-machines.md`      | domain-structure    | domain-modeling-agent | spec-review-agent              | true            |
| `docs/spec/validation-rules.md`    | domain-structure    | domain-modeling-agent | spec-review-agent              | true            |
| `docs/spec/interface-contracts.md` | domain-structure    | domain-modeling-agent | spec-review-agent              | true            |
| `docs/spec/schemas/*`              | domain-structure    | domain-modeling-agent | spec-review-agent              | true            |
| `docs/spec/architecture.dsl`       | architecture        | architecture-agent    | architecture-review-agent      | false (CAO-G12) |
| `docs/spec/dependency-rules.dsl`   | architecture        | architecture-agent    | architecture-review-agent      | true            |
| `docs/agent-context.md`            | seam                | virgil                | stakeholder                    | false (CAO-G12) |
| `docs/testing.yaml`                | seam                | test-strategy-agent   | stakeholder                    | true (CAO-G12)  |

### `docs/spec/schemas/<entity>-<column>.json`

| Property   | Contract                                                                                                      |
| ---------- | ------------------------------------------------------------------------------------------------------------- |
| File       | One JSON Schema per payload column with inner structure in `docs/spec/entity-model.md`, such as a JSON column |
| Name       | `docs/spec/schemas/<entity>-<column>.json`, in lowercase kebab case                                           |
| Link       | The column's row in the entity model links its schema file                                                    |
| No payload | When no column has inner structure, the folder `docs/spec/schemas/` does not exist                            |
| Writer     | The domain-modeling agent, through the schema step of the `domain-modeling` skill                             |

### Output declaration fields

| Field          | Contract                                                                                                                                           |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `reviewed_by:` | A list of agent names or `stakeholder`, on every core and seam output declaration (BR-058). Working output carries none                            |
| `edits:`       | `wording` for a declaration that changes wording and never meaning, such as the lector agent's `docs/**/*.md`. The contract test skips it (BR-060) |

### `index-lint` reviewer check

| Property  | Contract                                                                                                                                                                                                                                                      |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Writes    | `reviewed_by:` and `edits:` of every output declaration into `INDEX.yaml`, beside `path_pattern`, `validator`, and `required`                                                                                                                                 |
| Fails     | On a `reviewed_by:` entry that is neither `stakeholder` nor an existing agent, or that names an agent without the artifact as a required or context input (BR-059)                                                                                            |
| Matching  | Producer output and reviewer input match through the sample path (BR-057)                                                                                                                                                                                     |
| Exit code | `1` on a reviewer finding, with or without `--check`, so that the pre-commit hook, which runs without `--check`, stops a broken reviewer. On a reviewer finding, `index-lint` writes no `INDEX.yaml`. `1` in `--check` mode on a stale catalog; `0` otherwise |

### `dispatch close-wave`

| Property     | Contract                                                                                                                                                                                                                                                                                                                                                                                |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Reads        | `docs/spec/work/spec-feedback-<story-id>.md` of every story in the wave, as committed at the head of the invocation branch, not from a working tree. Owner and reviewer sessions commit each row status there (ADR-0029). The branch is the ledger's invocation branch, else `HEAD`. Also reads `packages/factory/rulebooks/core-artifacts.yaml` as installed beside the running script |
| Fails        | While a row is `open`, or `fixed` on an artifact of the core list (BR-062). The error names the report, the artifact, and the status of each row                                                                                                                                                                                                                                        |
| Fails closed | On a report without a table that holds the five report columns, a row with an empty Artifact cell, a row with an unknown status, a report that exists but cannot be read, and a core list that is missing, unreadable, or lists no entry with a `path_pattern` (ATAM-0008)                                                                                                              |
| Passes       | On `confirmed` and `rejected` rows, on `fixed` rows about other artifacts, and for a story without a report (BR-063)                                                                                                                                                                                                                                                                    |
| Manual mode  | `close-wave` does not run. The dispatch contract's manual-mode section states the same rule per story (BR-064)                                                                                                                                                                                                                                                                          |

### Report rows: spec-feedback and reconciliation

Both reports hold one Markdown table with the columns below. Gap CAO-G04
decides the column names.

| Column   | Contract                                                                                                                                                   |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Artifact | The path of the artifact that drifted, such as `docs/spec/validation-rules.md`                                                                             |
| Drift    | The mismatch between the artifact and the code, in one sentence                                                                                            |
| Evidence | The code path and line that show the mismatch                                                                                                              |
| Owner    | The producer of the artifact, which acts on the row first, such as `domain-modeling-agent`                                                                 |
| Status   | `open`, `fixed`, `confirmed`, or `rejected`, set as [BR-061](validation-rules.md#ownership-and-drift-reports-core-artifact-ownership-br-056br-066) defines |

| Report         | Path                                         | Writer of `open` rows                    | Dispatcher of owner and reviewer                                 | Check that waits for the rows                     |
| -------------- | -------------------------------------------- | ---------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------- |
| Spec feedback  | `docs/spec/work/spec-feedback-<story-id>.md` | developer agent, through `spec-feedback` | implementation agent, after each merge                           | `dispatch close-wave` (BR-062)                    |
| Reconciliation | `docs/reviews/reconciliation-<date>.md`      | reconciliation agent, one per run        | orchestrator of the `documentation-update` playbook, after a run | the playbook's DONE list; no script gate (BR-067) |

The first reconciliation run of a day writes `reconciliation-<date>.md`. A second run on the same day writes `reconciliation-<date>-2.md`, a third `reconciliation-<date>-3.md`, and so on. The reports sort by date first, then by suffix, and the file without a suffix is run 1 (CAO-G29).

### `docs/spec/work/term-candidates.md`

| Column              | Contract                                                                                          |
| ------------------- | ------------------------------------------------------------------------------------------------- |
| Term                | The term as the code or the session names it                                                      |
| Domain area         | The scope-map area the term belongs to; the stakeholder confirms one area at a time               |
| Source              | The code path or the session that found the term                                                  |
| Proposed definition | Written by the domain-modeling agent, or by the session that settled the term                     |
| Status              | `candidate`, `proposed`, `confirmed`, or `rejected` (BR-065)                                      |
| Note                | The stakeholder's reason for a rejection; the row keeps it when it returns to `proposed` (BR-065) |

### Finding frontmatter `owner:`

| Property | Contract                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Field    | `owner:` names the agent that acts on the finding next. By default it is the producer of the artifact the finding is about. A `BUG` finding names the developer agent, and a `QA` finding for a missing test names the planning agent (CAO-G10). A finding about a proposal under `docs/proposals/` names `virgil`, who revises the proposal with `draft-proposal`. A finding without an artifact, such as a `RETRO` finding, names `virgil`. So does a finding whose artifact spans several producers, such as `RECON-cycle-retirement`. Virgil shapes or splits such a finding into work with the stakeholder (stakeholder, 2026-11-05). An open finding without `owner:` goes to the producer of the artifact it names, read from the output declarations (CAO-G26) |
| Routing  | The orchestrator sends each open finding to the agent in `owner:`, not to the author of the reviewed phase                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Tags     | The tag table adds `ARCH` (the architecture agent's read check) and `QA` (an unresolved mutant) and drops `RECON`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |

## Counter IDs Contracts

The contracts of [counter-ids.feature](features/counter-ids.feature) and
[counter-ids-fitting.feature](features/counter-ids-fitting.feature). The
rules behind them are BR-068 to BR-078 in
[validation-rules.md](validation-rules.md#counter-ids-next-id-br-068br-078)
and BR-096 to BR-108 in
[validation-rules.md](validation-rules.md#counter-ids-fitting-br-096br-108).
A value that a proposal leaves open carries the identifier of its gap in
[counter-ids-gaps.md](work/counter-ids-gaps.md) or
[counter-ids-fitting-gaps.md](work/counter-ids-fitting-gaps.md).

### `packages/factory/scripts/next-id`

| Property     | Contract                                                                                                                                                                                                                       |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Claim usage  | `next-id <PREFIX> [--remote <url>]`                                                                                                                                                                                            |
| Seed usage   | `next-id --seed <number> [<PREFIX>=<n> …] [--remote <url>]`                                                                                                                                                                    |
| Plan usage   | `next-id --plan-seed [--remote <url>]`, as [§ `next-id --plan-seed`](#next-id---plan-seed) defines                                                                                                                             |
| Move usage   | `next-id --move-to-origin`, as [§ `next-id --move-to-origin`](#next-id---move-to-origin) defines                                                                                                                               |
| Remote       | The `--remote` URL, else the path in the git setting `agent-factory.counterRemote`, else the URL of `origin` (BR-096). Tests pass a local bare repository with `--remote`                                                      |
| Clone        | Optional. With `--remote`, `next-id` runs outside any git repository                                                                                                                                                           |
| Writes       | Only `refs/ids/counters` on the remote. A claim leaves the clone unchanged (BR-075). CID-G06 asks whether `--seed` also runs in a throwaway repository. `--move-to-origin` also removes `agent-factory.counterRemote` (BR-102) |
| Claim output | On success, the ID alone on standard output, such as `ST-1013`, and exit `0`. An agent reads the ID from the output, because a shell variable does not survive (DEC-08)                                                        |
| Seed output  | On success, the seed lines on standard output, and exit `0`. Whether the token line is one of them is open (CID-G03)                                                                                                           |
| Failure      | Exit non-zero, nothing on standard output, and the message on standard error. The proposal names no exit code other than `0`                                                                                                   |
| Credentials  | From the user's global git config, a credential helper, or an SSH key. A credential helper in the clone's own `.git/config` does not reach the claim                                                                           |
| Git calls    | A claim runs git without prompts and with a time limit per call (BR-076). A seed keeps git's prompts                                                                                                                           |
| Messages     | A message names the remote by its redacted URL (BR-077). The git calls get the URL unchanged                                                                                                                                   |

A claim fails in these cases. `next-id` checks the prefix before it looks for
the remote.

| Case                                    | Message names                              |
| --------------------------------------- | ------------------------------------------ |
| prefix not in the list                  | the prefix and the list of prefixes        |
| no `--remote`, no setting, no `origin`  | `origin`, `--remote`, and `next-id --seed` |
| a marker commit at the counter (BR-097) | the remote of the marker, never `--seed`   |
| remote unreachable                      | the remote and git's error message         |
| `refs/ids/counters` missing             | the remote and `next-id --seed`            |
| fetch refused by the remote             | the remote and git's error message         |
| ten stale leases in a row (BR-072)      | the prefix and the last number tried       |
| push refused for another reason         | the remote and git's error message         |
| a git call over the time limit (BR-076) | the remote and the time limit              |

A seed fails and changes nothing in these cases. `next-id` checks the
arguments before it looks for the remote.

| Case                                               | Message names                       |
| -------------------------------------------------- | ----------------------------------- |
| a number that is not a whole number from 0 to 9998 | the argument                        |
| two pairs for one prefix                           | the prefix                          |
| a prefix not in the list                           | the prefix and the list of prefixes |
| no `--remote`, no setting, and no `origin`         | `origin` and `--remote`             |
| remote unreachable                                 | the remote and git's error message  |
| access refused by the remote                       | the remote and git's error message  |
| `refs/ids/counters` exists                         | the remote and `refs/ids/counters`  |

git reports a stale lease as `stale info` when the client notices, and as
`cannot lock ref … is at <sha> but expected <sha>` when the remote notices.
`next-id` retries only on these two messages (DEC-23). It runs every git
command with `LC_ALL=C`, so git prints its own messages in English. A message
that the remote server writes keeps the server's language. This specification
does not check which language a hosted remote such as GitHub uses.

### Claim commit message

The claim commit at `refs/ids/counters` is a commit with no parent on the
empty tree, made with `git commit-tree`. Its message holds one `key=value`
line per entry:

```text
start=1000
ST=1012
FAGAN=1003
token=9f3a61c0d2e4b871
```

| Line              | Contract                                                                                       |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| `start=<number>`  | The seed number, four digits (BR-070). Exactly one per claim commit                            |
| `<PREFIX>=<NNNN>` | The highest number claimed so far for the prefix, four digits. At most one per prefix (BR-071) |
| `token=<value>`   | A random value that differs in every claim commit, so no two claim commits share a SHA         |

### Marker commit message

`next-id --move-to-origin` leaves a marker commit at the local
`refs/ids/counters` before it pushes the counter to `origin`. Its parent is
the claim commit C that the move carries, so C stays reachable and a second
move can take it from there (DEC-14). Its message is one line:

```text
moved=https://***@host/demo.git
```

| Line             | Contract                                                                    |
| ---------------- | --------------------------------------------------------------------------- |
| `moved=<remote>` | The URL of `origin` at the move, redacted by BR-077. The only line (BR-097) |

| Property | Contract                                                          |
| -------- | ----------------------------------------------------------------- |
| Parent   | The claim commit C of the local counter, its only parent (DEC-14) |

### `next-id --plan-seed`

`next-id --plan-seed` prints the seed command that the fitting step shows to
the User. It changes no ref and no file (BR-098).

| Property | Contract                                                                                                                                                                                              |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Remote   | The order of BR-096                                                                                                                                                                                   |
| Reads    | `refs/ids/counters` on the remote; the file names, register `id` fields, and todo headings of every local branch, every remote-tracking branch, and the working tree of the current worktree (BR-099) |
| Output   | One line `next-id --seed 0 <PREFIX>=<highest> …` on standard output, or `next-id --seed 0` alone. The pairs follow the order of the prefix list in `next-id` (BR-101)                                 |
| Warnings | One warning per counted file name that breaks the new pattern, naming its path (BR-100). The warnings do not change the exit code                                                                     |
| Messages | The remote by its redacted URL (BR-077)                                                                                                                                                               |

| Case                                                                                        | Exit     | Output                                                                                                                |
| ------------------------------------------------------------------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------- |
| the remote holds no `refs/ids/counters`                                                     | `0`      | the seed command                                                                                                      |
| the remote holds a claim commit                                                             | `0`      | the line `refs/ids/counters is in use on <remote>; the project needs no seed` on standard output, and no seed command |
| the remote holds a marker commit                                                            | non-zero | the remote of the marker, and no mention of `--seed` (BR-097)                                                         |
| no `--remote`, no setting, and no `origin`                                                  | non-zero | `origin` and `--remote`, and no seed command                                                                          |
| remote unreachable                                                                          | non-zero | the remote and git's error message, and no seed command                                                               |
| run with `--remote` outside any git repository, and the remote holds no `refs/ids/counters` | `1`      | a message that names `--plan-seed` and asks for a run inside the project's clone, and no seed command                 |

### `next-id --move-to-origin`

`next-id --move-to-origin` moves the local counter that
`agent-factory.counterRemote` names to `origin`. BR-102 defines its steps, and
the [Move Lifecycle](state-machines.md#move-lifecycle) shows them.

| Property | Contract                                                                                                                                                                                       |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Reads    | The local counter at the path of `agent-factory.counterRemote`, and `origin`                                                                                                                   |
| Writes   | The local `refs/ids/counters`, `refs/ids/counters` on `origin`, and the removal of `agent-factory.counterRemote` from `.git/config`                                                            |
| Leases   | A lease on the claim commit C for the marker, and the create-only lease for the push                                                                                                           |
| Messages | Every remote by its redacted URL (BR-077)                                                                                                                                                      |
| Output   | On success, the line `moved refs/ids/counters from <local> to <remote>` on standard output, and exit `0`. `<local>` is the path of the setting, and `<remote>` is the redacted URL of `origin` |
| Remote   | The marker names `remote.origin.url` as the clone configures it. The push goes to the URL that `git ls-remote --get-url` prints for it, so the clone's `url.<base>.insteadOf` rewrites apply   |
| Push     | From a throwaway repository, as for a claim (BR-075). It fetches the local counter, whose marker has C as its parent, and pushes C. So no hook of the project runs                             |

| Case                                                                             | Result                                                                                                                                                                                                                 |
| -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `origin` holds no `refs/ids/counters`                                            | `origin` holds C, the local counter holds the marker, the setting is gone                                                                                                                                              |
| an ID claim raised C before the marker                                           | the move reads the local counter again and carries the new claim commit to `origin` (BR-103)                                                                                                                           |
| ten stale leases in a row on C                                                   | exit non-zero, no marker, the local counter and the setting stay, and the message names the move and the ten stale leases                                                                                              |
| the push is refused, and `origin` then holds C                                   | the push of C got through after all. The move removes the setting, and the result is that of the first row                                                                                                             |
| the push is refused, and `origin` then holds another counter                     | a collision: the local counter keeps the marker, the setting stays, and the message names both counters (DEC-16)                                                                                                       |
| the push is refused, and `origin` then holds no counter or does not answer       | the local counter keeps the marker, the setting stays, and the message holds git's message (DEC-16)                                                                                                                    |
| the push runs over the time limit of BR-076                                      | the local counter keeps the marker, the setting stays, and the message names the remote and the time limit. This is the CutOff of the [Move Lifecycle](state-machines.md#move-lifecycle), and a second move resumes it |
| the local counter holds a marker, and `origin` holds no `refs/ids/counters`      | the move takes C from the marker's parent and pushes it. The result is that of the first row (BR-102)                                                                                                                  |
| the local counter holds a marker, and `origin` holds C                           | the push was done before the cut-off. The move only removes the setting, and the setting is gone                                                                                                                       |
| the local counter holds a marker, and `origin` holds a claim commit other than C | a collision: the message names both counters, the local counter keeps the marker, and the setting stays (BR-102)                                                                                                       |

The proposal names no exit code for the failure cases (CIF-G08). This
specification takes non-zero, as for every failure of `next-id`.

A stale lease on C makes the move wait 0.1 to 1 second and read the local
counter again, at most ten times in a row. A marker at the read makes the move
resume: it takes C from the marker's parent and asks `origin` with
`git ls-remote` for `refs/ids/counters` before it pushes. The three resume rows
of the case table follow from that answer.

After a refused push, the move asks `origin` again with `git ls-remote`, on a
first move as on a resume. The three rows on a refused push follow from that
answer. The move never puts C back on the local counter: from the marker on,
the local counter hands out no number, so a counter that someone else seeded on
`origin` meanwhile never repeats one (DEC-16).

### `init-factory` counter check

`init-factory` asks the resolved remote whether `refs/ids/counters` exists,
with `git ls-remote`. The remote is `agent-factory.counterRemote`, else
`origin` (BR-105). It never seeds (DEC-17) and changes no ref.

| Case                                             | Output                                                                                                                                                   |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `refs/ids/counters` missing on `origin`          | "counter: missing on origin; walk fitting step 4, or run `next-id --plan-seed` to print the seed command"                                                |
| `refs/ids/counters` missing on the local counter | The same hint, with the redacted URL of `agent-factory.counterRemote` in place of `origin`                                                               |
| no setting and no `origin`                       | "counter: no remote", then "fitting step 4 keeps the counter in this repository until `origin` exists"                                                   |
| remote unreachable                               | A warning that names the redacted remote and git's last line. `init-factory` finishes the install and exits `0` (DEC-23)                                 |
| remote URL has user info                         | A warning that names `origin` or `agent-factory.counterRemote`, shows only the redacted URL, and advises a credential helper (BR-078). The check goes on |

No hint names a number for the seed, because `next-id --plan-seed` finds the
numbers (DEC-07). The proposal names no exit code for the hints and no output
when the counter exists (CID-G02).

The check returns `true` when the remote holds the counter, `false` when it
does not or no remote exists, and no value when the remote does not answer. A
separate step, `record_counter_seeded`, writes that result into the fitting key
and skips the write when the check returned no value.

The same check derives the sixth fitting key.

| Fitting key              | Contract                                                                                                                                                                            |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `fitting.counter_seeded` | `true` when the resolved remote holds `refs/ids/counters`, `false` when it does not or no remote exists, unchanged when the remote is unreachable. Greenfield too (BR-105, CIF-G07) |
| `fitting.status`         | `fitted` only when all six keys are `true` (BR-104)                                                                                                                                 |

### Guardrail hook and `next-id`

`block-dangerous-git.sh` stays unchanged. It matches the literal text of a
push command, so the commands `next-id ST` and `next-id --move-to-origin`
pass with exit `0`. A push written
with `git -C .` before the subcommand also passes, so the hook does not force a
claim through `next-id`. The lease of BR-072 still refuses every stale claim
(DEC-22).

### `id-prefixes.md` table

`packages/factory/rulebooks/conventions/id-prefixes.md` holds one table with a
row per ID prefix of BR-068 (BR-108).

| Column      | Contract                                             |
| ----------- | ---------------------------------------------------- |
| Prefix      | One prefix of the list in `next-id`, once per table  |
| Artifact    | The kind of indexed artifact the prefix numbers      |
| ID producer | The files that name `next-id <PREFIX>` for that kind |

The text test for ID producers reads this table, the list in `next-id`, and
each ID producer file. It fails as BR-108 defines.

## Finding Classification Contracts

The contracts of
[finding-classification.feature](features/finding-classification.feature):
the finding file, the register file, the envelope counts, the gate
`finding-lint` with its settings file, the stop in `dispatch` and
`premerge-check`, the hook `guard-human-fields`, and the proposal review row.
The rules behind them are BR-079 to BR-095, BR-109, and BR-110 in
[validation-rules.md](validation-rules.md#finding-classification-br-079br-095).
A value that the stakeholder settled on a gap carries the identifier in
[finding-classification-gaps.md](work/finding-classification-gaps.md).

### `docs/findings/<ID>.md` — finding file

A reviewer agent writes a finding file for each `critical` or `major`
finding. The frontmatter holds these fields:

| Field                   | Contract                                                                                                                                                              |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                    | The ID that `next-id` printed, such as `FAGAN-0042`. The file name is `<id>.md`                                                                                       |
| `source`                | The review or session that found the finding, such as `fagan-review` or `diagnosis`                                                                                   |
| `review_class`          | `document`, `code`, `security`, `architecture`, or `runtime` (BR-079)                                                                                                 |
| `category`              | `defect`, `risk`, or `suggestion` (BR-079)                                                                                                                            |
| `type`                  | A type from the vocabulary of the class (BR-079)                                                                                                                      |
| `severity`              | `critical` or `major`, computed from `basis` (BR-081 to BR-085)                                                                                                       |
| `basis`                 | A YAML mapping with the shape of the class, as [schemas/finding-basis.json](schemas/finding-basis.json) defines (BR-080)                                              |
| `rating`                | The bug-bar level `Critical`, `High`, `Medium`, or `Low` of a security finding; `null` in every other class (BR-082)                                                  |
| `override_by`           | `null`, or the stakeholder who waived or lowered the finding. Human field (BR-092, BR-109)                                                                            |
| `override_reason`       | `null`, or why the finding stays unfixed or why it was lowered. Human field                                                                                           |
| `stop_confirmed_by`     | `null`, or the stakeholder who confirmed the stop of a `critical` finding. Human field                                                                                |
| `stop_confirmed_reason` | `null`, or what the stakeholder checked and found. Human field                                                                                                        |
| `artifact`              | `path:line`, `path:start-end`, or `path#anchor` (BR-086)                                                                                                              |
| `status`                | `open` or `resolved`, set by an agent. `waived`, set only by the stakeholder. `deferred`, set only by the migration on a file without `review_class` (BR-086, DEC-55) |
| `owner`                 | The agent that acts on the finding next, as [Finding frontmatter `owner:`](#finding-frontmatter-owner) defines                                                        |
| `traces`                | Optional list of related IDs, such as `[ST-0351]`                                                                                                                     |

A new finding written from the template carries `null` in all four human
fields. The body holds three lines in this order: `**What is wrong:**`,
`**Why this severity:**`, and `**Fix:**`. The Why line holds one sentence per
"yes" answer, per precondition, or for the effect class, and it names the
evidence for `in_use`.

A `critical` finding ends with the section `## Possible damage`, and no other
severity holds it. Each item is one list entry in this form:

```markdown
- merges on `dev` from dispatch runs since the installed copy was last updated — check: compare `git log --merges dev` with the merges the dispatch log records
```

The text before `— check:` names one thing outside the artifact that
depends on it, as a fact from git or the file tree. The text after it names
one command or step that the stakeholder runs.

A finding file whose `HEAD` version carries `review_class` is never removed,
except when a register file with the same ID and both override keys replaces
it (BR-109).

### `docs/findings/register/<class>/<ID>.json` — register file

A reviewer agent records each `minor` finding as one register file in the
register of its class, the folder `docs/findings/register/<class>/` (DEC-60).
The file holds one JSON object with these keys:

| Key                 | Contract                                                                                                                                                                                          |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                | The ID that `next-id` printed. A migrated finding keeps its old ID, such as `BUG-0067`. The file name is `<id>.json`                                                                              |
| `source`            | As in the finding file                                                                                                                                                                            |
| `review_class`      | The class of the register, such as `code` in `docs/findings/register/code/`                                                                                                                       |
| `category`          | `defect`, `risk`, or `suggestion`                                                                                                                                                                 |
| `type`              | A type from the vocabulary of the class                                                                                                                                                           |
| `severity`          | `minor`                                                                                                                                                                                           |
| `artifact`          | `path:line`, `path:start-end`, or `path#anchor`                                                                                                                                                   |
| `story`             | The story ID the review ran for, such as `ST-0370`, or `null` when no story exists yet                                                                                                            |
| `finding`           | What is wrong and the fix, as plain text                                                                                                                                                          |
| `basis`             | A JSON object with the shape of the class                                                                                                                                                         |
| `why_this_severity` | The Why this severity sentence. In the consequence tree classes it holds `no to fails_purpose` (BR-087)                                                                                           |
| `commit`            | The reviewed commit as 40 hexadecimal characters                                                                                                                                                  |
| `status`            | `open`, written by the reviewer agent, the migration, or the stakeholder who lowers a filed finding. `resolved`, set by the fixing commit. `waived`, set only by the stakeholder (BR-110, DEC-63) |
| `override_by`       | Only on a register file that replaces a finding file or that is waived: the stakeholder who lowered or waived the finding. Human field (BR-092, BR-109, BR-110)                                   |
| `override_reason`   | Only on a register file that replaces a finding file or that is waived: why the stakeholder lowered the finding, or why nobody will fix it. Human field                                           |

The commit that fixes the finding sets `status` to `resolved`, and the file
stays. When nobody will fix the finding, the stakeholder sets `status` to
`waived` and writes both override keys, and the file stays as well (BR-110,
DEC-63). A register file that `HEAD` holds is removed only when a finding file
with the same ID replaces it, which is the raise of FC-G04 (BR-110). The schema
allows both override keys on any register file. `finding-lint` requires both
with text on a waived register file, and on a register file that replaces a
finding file, because only a comparison with `HEAD` shows the replacement
(BR-109). This object, with its two texts shortened, holds RECON-0027 after the
migration:

```json
{"id": "RECON-0027", "source": "reconcile-spec", "review_class": "document", "category": "defect", "type": "incorrect", "severity": "minor", "artifact": "docs/spec/validation-rules.md:491", "story": "ST-0370", "finding": "BR-076 bounds a claim ...", "basis": {"in_use": false, "harms_downstream": false, "fails_purpose": false, "raises_cost": true}, "why_this_severity": "... (no to fails_purpose) ...", "commit": "d0a78a5c40327c1f7e4c9a204ab5e766a7e0c44b", "status": "open"}
```

When the stakeholder waives RECON-0027, the object keeps its other keys and
ends with these three:

```json
"status": "waived", "override_by": "human", "override_reason": "... accepted as is ..."
```

`finding-lint` reads each register schema under the Factory root that it runs
from: `packages/factory/` in this repository and `.agent-factory/factory/` in
an installed project (BR-090).

| Register                               | Schema under the Factory root                                 |
| -------------------------------------- | ------------------------------------------------------------- |
| `docs/findings/register/document/`     | `rulebooks/schemas/finding-register-document.schema.json`     |
| `docs/findings/register/code/`         | `rulebooks/schemas/finding-register-code.schema.json`         |
| `docs/findings/register/security/`     | `rulebooks/schemas/finding-register-security.schema.json`     |
| `docs/findings/register/architecture/` | `rulebooks/schemas/finding-register-architecture.schema.json` |
| `docs/findings/register/runtime/`      | `rulebooks/schemas/finding-register-runtime.schema.json`      |

Each register schema lists the first thirteen keys as required, allows
`override_by` and `override_reason` as optional strings, forbids other keys,
restricts `status` to `open`, `resolved`, and `waived`, and takes the basis shape of its
class from [schemas/finding-basis.json](schemas/finding-basis.json).
`finding-lint` runs `schema-validate <file> <schema>` on each register file
with the schema of its folder (FC-C27). The schemas use only the keywords that
the validator of `schema-validate` supports, so they hold no `oneOf`. So the
schema cannot tie `waived` to the override keys, and `finding-lint` checks that
rule itself (BR-110). An
implementation story writes them.

Two branches that each add a register file add two different paths, so git
merges them without a conflict and needs no merge driver. An ID is a finding
file or a register file, never both, and names at most one register file
(DEC-53, BR-090). The orchestrator loop greps `docs/findings/*.md` for
`status: open`, which matches no register file.

### `finding_counts` of the child-result envelope

[Child-result envelope](#child-result-envelope) defines the envelope. A
review that files one `major` finding and records nothing else returns:

```json
"finding_counts": {"critical": 0, "major": 1, "minor": 0, "note": 0}
```

`adversarial-review` keeps its own scale in its records and maps it only here:
BLOCKER and MAJOR count under `major`, MINOR under `minor`, and NOTE under
`note` (BR-093).

### `packages/factory/scripts/finding-lint`

| Property  | Contract                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Usage     | `finding-lint [--staged]`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Reads     | Every `docs/findings/*.md` that carries `review_class` or whose `HEAD` version carries it, every register file `docs/findings/register/**/*.json`, and the register schema of each class under the Factory root that `finding-lint` runs from (BR-090). With `--staged`, the staged version of each file; without it, the working tree. The `HEAD` version of each file, to decide whether a git check is due, whether a finding was lowered or removed, and whether a file kept its `review_class` (BR-109, BR-110). During the migration commit, the `HEAD` version of the old `.jsonl` registers (FC-C25)             |
| Reads too | Only when a git check is due: `docs/factory-settings.yaml`, the branches `dev`, `main`, `origin/dev`, and `origin/main`, the release tags, and the installed copy `.agent-factory/factory/` when `packages/factory/` exists. In a linked worktree, the installed copy is the one in the main checkout, which `packages/factory/scripts/_main_checkout.py` finds (BR-088, BR-089, DEC-49, DEC-50)                                                                                                                                                                                                                         |
| Writes    | Nothing                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Skips     | A finding file without `review_class` in both its checked version and its `HEAD` version, such as a resolved file from before the migration                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Checks    | BR-079 to BR-090, BR-109, and BR-110, including `schema-validate` on each register file with the schema of its class, an unknown status, `deferred` on a file that carries `review_class` (DEC-55), an open `minor` or `note` file, an ID that is both a finding file and a register file (DEC-53), a finding lowered or removed without the override fields (DEC-56), a register file removed without a finding file of the same ID (DEC-60), a waived register file with an empty `override_by` or `override_reason` (DEC-63), and a version that drops or changes the `review_class` of its `HEAD` version            |
| Messages  | One line per violation. It names the file and the rule, and for a removed file also the ID. One line per branch that the clone does not have, such as `skipped origin/main: no such branch`. A skipped branch is no violation                                                                                                                                                                                                                                                                                                                                                                                            |
| Exit code | `0` when every checked file passes; `1` on any violation, and on a missing release setting when a git check is due; `2` on a usage error or a git call that fails                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Run by    | The `validate` skill, without `--staged`, and the pre-commit hook, with `--staged`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Hook      | The hook id `agent_factory_hook-finding-lint` in `packages/factory/config/pre-commit-config.yaml`, with `files: ^docs/findings/` and `pass_filenames: false`. Its entry in `packages/factory/config/hook-metadata.yaml` is `trade_off: none` and `availability: requires-path:docs/findings`, because the lint changes no file and runs fast. So fitting includes it without asking                                                                                                                                                                                                                                      |
| Update    | `update-factory` re-splices the `agent_factory_hook-*` block of `.pre-commit-config.yaml` from the template of the new release with `merge-precommit-config --update`. It shows the diff and writes the block on a yes, and writes it without asking after the layout migration. So a project that finished its fitting earlier gets the hook. A project that answers no keeps its old block without the hook                                                                                                                                                                                                            |
| Bypass    | `block-dangerous-git.sh` denies an agent's commit with `--no-verify`. A user who commits with `--no-verify` skips the hook. A stop committed earlier still holds against an uncommitted change, because the stop check reads `HEAD` and the working tree. A bypass commit that lowers or removes a `critical` finding puts the changed version into `HEAD`, so the stop ends. A later `validate` run or commit rejects a severity that disagrees with its basis. It does not see a removal or a lowering with a matching basis, because `HEAD` then holds the changed version. This is an accepted residual risk (QS-24) |

On each place, the git check blames the `artifact` path, and also each rename
or copy source that `git diff -M -C <place> <reviewed branch>` names for that
path. It compares line identities: the introducing commit, the line number in
that commit, and the file name in that commit (BR-088). A failed git check
names the first place where the lines exist unchanged:

| Place found        | Message                                                |
| ------------------ | ------------------------------------------------------ |
| branch `dev`       | `artifact lines exist unchanged on dev`                |
| branch `main`      | `artifact lines exist unchanged on main`               |
| `origin/dev`       | `artifact lines exist unchanged on origin/dev`         |
| `origin/main`      | `artifact lines exist unchanged on origin/main`        |
| a release tag      | `artifact lines exist unchanged at tag <tag>`          |
| the installed copy | `artifact lines exist unchanged in the installed copy` |

A missing release setting gives a message that names the file, the key, and
the fix, so a project can recover without reading the specification:

```text
docs/factory-settings.yaml: key release_tag_patterns is missing. Add the list of git tag patterns that count as releases, such as ["v[0-9]*"], or [] for none.
```

### `docs/factory-settings.yaml`

| Property               | Contract                                                                                                                               |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Location               | The project root, tracked in git, so every clone uses the same setting (FC-C11)                                                        |
| Writer                 | The project. `init-factory` and `update-factory` never write the file                                                                  |
| `release_tag_patterns` | A YAML list of glob patterns as strings. A tag counts as a release when `git tag --list '<pattern>'` lists it for one pattern (BR-089) |
| Empty list             | `[]` is valid and counts no tag                                                                                                        |
| Missing                | A missing file, a missing key, or a value that is not a list of strings makes `finding-lint` exit `1` when a git check is due          |
| Other keys             | `finding-lint` reads only `release_tag_patterns`                                                                                       |

```yaml
release_tag_patterns:
  - "v[0-9]*"
```

With this setting, the tags `v1.0.0` and `v1.1.0-rc` count as releases, and
`1.1.0` and `orchestrator-v0.1.0` do not.

### The stop in `dispatch` and `premerge-check`

| Property         | Contract                                                                                                                                                                                                                                                                                               |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Condition        | A finding file is critical and unconfirmed. Critical: its working-tree version or its `HEAD` version has `severity: critical` together with `status: open` or a `review_class` field. Unconfirmed: neither version holds text in both `stop_confirmed_by` and `stop_confirmed_reason` (BR-091, DEC-52) |
| Reads            | `docs/findings/*.md` in the working tree where the script runs, at the top level that `git rev-parse --show-toplevel` prints, and the `HEAD` version of each finding file of that worktree. An uncommitted finding counts. Other worktrees and branches do not (FC-G06)                                |
| `dispatch` stops | `init`, `prepare-wave`, `prepare-story`, `mark-dispatching`, `mark-dispatched`, `re-dispatch`, `escalate`, `refresh-story`, `merge-story`, and `close-wave` (FC-C12)                                                                                                                                   |
| `dispatch` runs  | `status`, `plan`, `suggest-merge-args`, `verify-story`, `mark-done`, `mark-blocked`, `mark-failed`, and `clear-manifest`, as without a stop                                                                                                                                                            |
| `premerge-check` | Checks the stop before any other check. During a stop it runs no other check and writes no `.current-work/premerge-check-ok` marker                                                                                                                                                                    |
| Writes           | Nothing during a stop. The ledger stays unchanged                                                                                                                                                                                                                                                      |
| Output           | The stop notice on standard output. Standard error keeps usage and git errors                                                                                                                                                                                                                          |
| Exit code        | `1` during a stop                                                                                                                                                                                                                                                                                      |
| Lift             | Both scripts run again once every stopping finding is confirmed. A status change, a lower severity, or a removed file does not lift the stop (BR-091)                                                                                                                                                  |

Both scripts print the same stop notice. It lists each stopping finding with
these parts, in this order: the finding ID and title, the artifact, the
evidence for `in_use` from the `**Why this severity:**` line, and each item of
`## Possible damage` with its check. The notice ends with the confirmation
step. The scripts take each part from the version that makes the finding
critical: the working-tree version when both versions do, and the `HEAD`
version otherwise. So a lowered or removed file still prints its damage items
from `HEAD` (BR-091). For BUG-0037 it reads:

```text
STOP: a critical finding has no confirmed stop. No work is dispatched or merged.

BUG-0037: An empty story passes verify-story, and a red suite then resets earlier merges away
  artifact: packages/factory/scripts/dispatch:1383
  in use: the lines exist unchanged in .agent-factory/factory/scripts/dispatch, which every dispatch run executes
  possible damage:
    - merges on `dev` from dispatch runs since the installed copy was last updated
      check: compare `git log --merges dev` with the merges the dispatch log records

To confirm: run each check, then write stop_confirmed_by and stop_confirmed_reason
into docs/findings/BUG-0037.md in your editor or with a ! command.
```

### `packages/factory/config/hooks/guard-human-fields`

The implementation story picks the file extension, as for
`block-dangerous-git.sh`.

| Property   | Contract                                                                                                                                                                                                                                                                                         |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Hook       | Runs in every supported CLI, registered on the hook events of that CLI for edit, write, and shell calls, as the table below lists (DEC-51, DEC-61)                                                                                                                                               |
| Reads      | The tool call as the CLI passes it, and for a write the current content of the target file                                                                                                                                                                                                       |
| Guarded    | `docs/findings/*.md`, the register files `docs/findings/register/**/*.json` (BR-092), and the Appendix tables of `docs/proposals/*.md`. Templates, the rulebook, and test fixtures lie outside (DEC-45)                                                                                          |
| Refuses    | A call that sets a human field, as [BR-092](validation-rules.md#stop-and-guard) defines                                                                                                                                                                                                          |
| Patch      | A patch call names its paths inside the patch text: `apply_patch` in Codex, Copilot CLI, and Pi, and `patch` in OpenCode. The guard reads the paths and the removed and added lines from the patch, and refuses a patch it cannot parse when the raw text names a guarded path (BR-092)          |
| Passes     | A new finding from the template with every human field `null`, an edit that leaves a waived status line as it is, an edit of `packages/factory/rulebooks/templates/finding.md`, a read-only `grep "status: waived" docs/findings/`, and a heredoc that writes a fixture outside `docs/findings/` |
| Exit code  | A hook script exits `0` to let the call through and `2` to refuse it, as `block-dangerous-git.sh` does. The Pi extension and the OpenCode plugin block the call through the API of their CLI, and block it also when the guard script is missing (DEC-61)                                        |
| Message    | On refusal, standard error names the file, the field, and that the stakeholder writes it in an editor or with a `!` command                                                                                                                                                                      |
| Blind spot | An agent that hides the field name passes the hook, such as with a field name built from pieces in a script, a `cp` of a prepared file, or `git checkout <ref> -- <file>` (DEC-42)                                                                                                               |

Each CLI registers the guard where the hook `step-guard` already sits for
edit, write, and shell calls (DEC-61). `init-factory` writes the entries of
Claude Code, Codex, Copilot CLI, and Pi beside the `step-guard` entries.
`update-factory` runs `init-factory` of the new release after each update, so
a project installed earlier gets the missing entries. The last column names
what the guard does beyond the shared rule, which includes the patch rule.

| CLI         | Registration                                                                                  | Calls guarded                                                  | CLI-specific behavior                                                                                                                                                                                     |
| ----------- | --------------------------------------------------------------------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Claude Code | `PreToolUse` entries in `.claude/settings.json`                                               | `Edit`, `MultiEdit`, `Write`, `NotebookEdit`, `Bash`           | None                                                                                                                                                                                                      |
| Codex       | `PreToolUse` entries in `.codex/hooks.json`                                                   | `Edit`, `Write`, `apply_patch`, `Bash`                         | None                                                                                                                                                                                                      |
| Copilot CLI | `preToolUse` entries in a hook file under `.github/hooks/`, as `step-guard.json` does         | `edit`, `apply_patch`, `write_file`, `create`, `bash`          | None                                                                                                                                                                                                      |
| Pi          | The `tool_call` event of a project-local extension, as `config/extensions/step-guard.ts` does | `edit`, `write`, `write_file`, `create`, `apply_patch`, `bash` | Blocks the call when the guard script is missing. `step-guard.ts` lets a call through in that case                                                                                                        |
| OpenCode    | `execute.before` of the Factory plugin `packages/factory/config/plugins/agent-factory.ts`     | `edit`, `write`, `patch`, `shell`, `execute`                   | Blocks the call when the guard script is missing. Checks the JavaScript of an `execute` call as the text of a shell call. This feature writes the first version of the plugin, which holds only the guard |

### `init-factory` change for the guard in OpenCode

| Property | Contract                                                                                                                                                                          |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CLI name | `--cli opencode` is accepted, and `opencode` joins the list of known CLIs (DEC-61)                                                                                                |
| Creates  | `.opencode/plugins/agent-factory.ts` as a link to `.agent-factory/factory/config/plugins/agent-factory.ts`                                                                        |
| Rest     | The detection markers, the version check, and the other paths of [`init-factory` OpenCode CLI additions](#init-factory-opencode-cli-additions) belong to the OpenCode CLI feature |

### Proposal review row

The proposal-review agent writes one row per finding into the table
`## Review findings` of the proposal's Appendix (BR-094).

| Column     | Contract                                                                                                |
| ---------- | ------------------------------------------------------------------------------------------------------- |
| Severity   | `major`, `minor`, or `note`                                                                             |
| Status     | `open`, `fixed`, `resolved`, or `waived`. Only the stakeholder sets `waived`, and only on a `major` row |
| Finding    | Ends with one sentence that starts with `Severity:` and names the deciding answer                       |
| Resolution | Holds the evidence of a fix, or the stakeholder's reason for a waiver                                   |
