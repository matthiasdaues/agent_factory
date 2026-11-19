# Validation Rules — Factory Flow Control

Field- and behavior-level rules each mechanism enforces, grouped by the entity or mechanism they govern. Business rule IDs (BR-###) are defined here or in the use case that introduces them; this file is the canonical index.

## Precondition types (`eligibility.py`)

- `file_exists`: satisfied if `repo_root.glob(path)` yields at least one match.
- `files_exist`: satisfied if every path in `paths` yields at least one glob match; the unmet reason lists every missing path by name.
- `no_open_findings`: satisfied if zero matching finding files (by `pattern` or `patterns`, globbed under `docs/findings/`) have frontmatter `status: open`. A file whose frontmatter cannot be parsed (no leading `---` block) is not counted as open.
- `script_exit_zero`: executes the named script and checks for exit code 0. When the `script` field uses the `charter:<field>` notation (e.g. `charter:test_command`), the evaluator reads the `charter_file` path from the condition, parses the YAML, and resolves the named field to the actual command before execution. Blocks with a clear message when the charter file is absent or the field is missing. See `UC-09` and [ADR-0003](../adr/0003-test-execution-via-hooks.md).
- A precondition name with no matching evaluator is treated as unmet, with the reason `"<name> (not defined)"`.
- Unmet preconditions are collected exhaustively, not short-circuited — a refusal always lists every unmet precondition, not just the first.

## Glob matching (`outputs:` ownership)

- `*` matches within one path segment; `**` matches across segments (`**/` also consumes a trailing `/`); `?` matches exactly one non-separator character. Every other character is matched literally.
- A path can match more than one agent's output declarations. The fence runner validates all matching declarations.
- A path matching no agent's `outputs:` declarations is ungoverned: `run-step` never treats it as evidence an agent's outputs exist.

## Permission scoping (`trigger`, BR-011, BR-012, BR-013)

- **Never** a blanket bypass: `--dangerously-skip-permissions` (Claude Code) and `--allow-all-tools` (Copilot CLI) are excluded from the background-mode command construction entirely — there is no flag path that reaches them from `trigger agent ... --background`.
- **Never** a bare interpreter wildcard: an allowlist entry that only scopes the outer command while leaving `python3 *`, `uv *`, `uvx *`, or `npm *` unscoped is treated as equivalent to no scoping, and is excluded on that basis.
- Every allowlist entry is derived from a command literally observed in this repo's own playbooks, skills, agents, and config files — grep-verified, not guessed ahead of a real need, per [YAGNI](../../.agent-factory/factory/rulebooks/conventions/foundational-principles.md#yagni). Adding a new entry requires the same evidence standard.
- Claude Code's allow/deny lists use its own `Bash(<cmd> *)` glob syntax; Copilot CLI's use its colon-wildcard `shell(<cmd>:*)` syntax. The two-word-prefix form (`shell(git commit:*)`) is confirmed against GitHub's own documentation; the three-word forms (`shell(uv run pytest:*)`) follow the same pattern but are unconfirmed — see [T-05](work/todos.md#t-05-copilot-clis-three-word-shell-wildcard-syntax-unconfirmed).
- The deny list mirrors [`block-dangerous-git.sh`](../../.agent-factory/factory/config/hooks/block-dangerous-git.sh)'s own pattern list exactly — a second, independent layer, not a substitute for it.
- `--interactive` mode constructs no allow/deny list at all; it launches a live session the actor controls directly, after printing the composed prompt (BR-013).

## Phase handoff and result envelope (BR-037…BR-042)

- **BR-037**: compression removes wording only. A valid handoff explicitly retains decisions, open items (including an explicit none), artifact paths, exact 40-character HEAD and other machine-consumed SHAs, branch/upstream state, gate results, verification evidence, and one next action.

- **BR-038**: `handoff-lint` validates all mechanically observable requirements and reports all detectable failures in one run. Every declared referenced repository path must exist; every declared machine-consumed SHA must match `[0-9a-f]{40}`; required sections and declared branch/upstream, verification, open-decision, and next-action fields must be present and non-placeholder. Passing lint makes no claim about facts the author never declared.

- **BR-049**: after structural lint passes, a designated Handoff Semantic Reviewer compares the handoff with the outgoing phase's artifacts, decisions, open items, and evidence. The reviewer alone confirms the losslessness invariant; an omission or distortion blocks closure until correction, repeated lint, and repeated semantic review pass.

- **BR-039**: a phase transition is complete only after a valid handoff is written and the outgoing session stops. Starting the next phase within that session violates the workflow contract. A continuation within the same phase does not require a handoff.

- **BR-040**: before child return, every complete report and finding is written to canonical tracked artifacts. The parent-facing envelope contains exactly the disposition, severity counts, complete artifact-path list, and a one-to-three-sentence next action; it does not contain verbatim finding detail or full reasoning.

- **BR-041**: a potentially large artifact is initially read through a bounded offset/limit chunk. Further chunks are requested only when needed. No prose-only cache-restabilisation turn is required or recommended.

- **BR-042**: derived usage metrics follow this deterministic contract:

  1. The aggregation unit is one chronological, top-level assistant model-response turn in the captured session. Tool/progress events, child-session turns, and synthetic session aggregates are excluded. `N` is the number of these eligible turns.
  2. `input_i` and `cache_read_i` are the native provider-reported per-turn values normalized without reinterpretation; the stored CLI and provider qualify their semantics.
  3. Cache capability is `full-cache` only when every eligible turn has both values. For that class, turn `i` is a cache miss exactly when `input_i > 0` and `cache_read_i = 0`; `cache_miss_turns` is the count, and `cache_miss_input_tokens` is `sum(input_i)` over miss turns. A complete session with no misses stores numeric `0` for both.
  4. Input capability is `input-only` when every eligible turn has `input_i` but at least one lacks `cache_read_i`. Both cache metrics are then `null`; no partial subset is aggregated.
  5. Capability is `unavailable` when `N = 0` or any eligible turn lacks `input_i`. All three metrics are then `null`.
  6. With complete input and `N >= 2`, let `k = max(1, floor(N / 3))`. Early is the first `k` eligible turns and late is the last `k`; the sets are disjoint. `late_early_input_ratio = mean(late input) / mean(early input)`. If `N < 2` or the early mean is zero, the ratio is `null`; no infinity or guessed substitute is stored.
  7. The metrics are computed once at session end, stored with CLI, provider, and capability class, and consumed only retrospectively. They never control a live session.

## Dispatch safeguard assurance (BR-043…BR-048)

- **BR-043**: the audit matrix has one row per accepted mechanism and names its contract, runtime implementation point, automated evidence, and disposition (`complete` or `verified gap`).
- **BR-044**: declared base SHAs and every SHA used in machine-consumed dispatch, gate, marker, or handoff state are lowercase 40-character hexadecimal object names; abbreviations are display-only.
- **BR-045**: base-preflight evidence proves a child halts before source reads, writes, or commits when either the target is not an ancestor or the declared base is wrong.
- **BR-046**: pre-merge evidence proves stale, out-of-scope, file-count-blowout, and target-reverting diffs block integration pending explicit investigation.
- **BR-047**: nested-agent evidence requires a resolvable parent instance ID and forbids indefinite waiting on an unreachable child; unattended-launch evidence asserts actual argv and deny-list construction, excluding blanket bypass and bare-interpreter wildcards.
- **BR-048**: scope-cap/checkpoint behavior is covered where mechanically enforceable; otherwise the audit records the contract evidence. A `complete` row creates no reimplementation story, while a `verified gap` may create only the smallest remediation needed to complete that row.

## Catalog generation (`index-lint`, BR-015, BR-016)

- Frontmatter parsing extracts scalar/folded-block-scalar keys (`name`, `title`, `phase`, `phase-name`, `category`, `description`, `tier`) and list-valued keys (`skills`, `inputs`) from `- item` lines. Other list-valued keys (`outputs`, `triggers`, `handoff-to`) are silently skipped. The `skills` and `inputs` lists are used to resolve agent dependencies for `total_tokens` computation.
- An agent with no `name` frontmatter field is excluded from the catalog entirely — not an error, just absent.
- A playbook's agent sequence is extracted from every `**Agent**: `x\`\` occurrence in file order, duplicates kept — a playbook that invokes the same agent twice (e.g. `implementation-agent` appearing once for the main chain) lists it once per occurrence.
- `--check` mode performs the identical generation and diffs the result against disk; it is a plain text-content comparison, not a structural/semantic diff.

## Origin/HEAD repair (`init-factory`, BR-050)

- **BR-050**: Right after ensuring the target is a git repo, `init-factory` best-effort-repairs a dangling `origin/HEAD` symref — one pointing at a ref that no longer exists locally, most often left over from a remote's default branch moving from `master` to `main`. It tries `git remote set-head origin --auto` first (requires a reachable remote), then falls back to scanning locally-known `refs/remotes/origin/*` for `main` or `master` (preferring `main`) if the remote is unreachable. Unlike a `Collision` (BR-021), a repair failure is logged and swallowed — it never stops the run.

## Installation collisions (`init-factory`, BR-021, BR-022)

- A destination path is safe to proceed past only if it is missing, or already a symlink resolving to the exact expected target. Any other existing state (a real file, a real directory, or a symlink to something else) raises a `Collision`.
- A `Collision` stops the entire run immediately — steps already completed earlier in the run stay applied; no step later than the collision point runs at all (BR-021).
- `config/model.conf` is copied only if absent; its presence is checked once, and its content is never diffed or refreshed afterward (BR-022) — the same non-diffing treatment `.agent-factory/factory/` itself receives once already present.

## Project-owned test gates (`testing.yaml`, BR-023, BR-024, BR-025, BR-026, BR-027, BR-028, BR-029)

- **BR-023**: Factory does not detect or construct test commands. The project declares its test commands in `docs/testing.yaml`. Factory reads that declaration; it does not guess, detect, or override. The `detect-test-regime` skill scans for existing test entrypoints during onboarding and populates the charter; it is not a runtime detection mechanism.
- **BR-024**: Bare test commands (`pytest`, `npm test`, `go test`, `cargo test`, and common variants) are blocked for agent execution via `block-dangerous-git.sh` deny patterns. The agent allowlist is populated from `docs/testing.yaml`: all declared command fields (`test_command`, `test_staged_command`, `test_changed_command`) are allowlisted with exact-string matching. No prefix matching. A command that differs from the declared string by even one character is denied.
- **BR-025**: The `test_changed_command` field in `docs/testing.yaml` is optional. When present, it is the command the project uses for fast feedback on changed files. Factory does not engineer mode flags or substitute its own mode logic; the project owns its mode story.
- **BR-026**: The `test_command` field in `docs/testing.yaml` is required. It is the full test suite command used by the `script_exit_zero` precondition evaluator. Factory calls it as-is from the repository root and reads only its exit code.
- **BR-027**: Factory does not parse structured test output. The gate contract is exit-code-only: zero means pass, nonzero means fail. Structured test counts, JSON summaries, and reporting are the project's concern.
- **BR-028**: The `test_staged_command` field in `docs/testing.yaml` is optional. When present, it is the command agents may use for TDD iteration on staged files. It is allowlisted in `block-dangerous-git.sh` with exact matching.
- **BR-029**: Factory does not inject test hooks into `.pre-commit-config.yaml`. Test hooks are project-owned infrastructure. The project decides when and how tests trigger on commit, push, or other events. The `agent_factory_hook-run-tests-full` entry that previously existed in Factory's pre-commit config is removed.

The `script_exit_zero` precondition evaluator resolves `test_command` from `docs/testing.yaml` via the `charter:test_command` notation and reads its exit code; the pass/fail decision is exit-code-only (BR-027).

## Anchor-file prerequisite (feature-addition)

The `feature-addition` playbook checks that four anchor files exist before it proceeds. The brownfield Stage 1 exit (Step 2.6 of `brownfield-onboarding`) checks the same four files.

- The four anchor files are `docs/spec/architecture.dsl`, `docs/spec/scope-map.md`, the vocabulary file, and `docs/agent-context.md`.
- The vocabulary anchor passes when `docs/spec/glossary.md` or `docs/spec/work/term-candidates.md` exists. Both playbooks apply this one rule. `reverse-map` writes term candidates, not glossary rows, so a fresh Stage 1 baseline may hold the work file alone (stakeholder, 2026-11-05).
- `docs/CONTEXT.md` is not an anchor file. The terms live in `docs/spec/glossary.md` or, before confirmation, in `docs/spec/work/term-candidates.md`. The routing lives in `docs/agent-context.md` (DEC-07, DEC-12). No project has a `docs/CONTEXT.md` after the fold (gap CAL-G01 in [core-artifact-layout-gaps.md](work/core-artifact-layout-gaps.md)).
- The check is file-existence only — no content validation, no gate marker, no structural inspection.
- If all four exist, the prerequisite passes and the playbook proceeds normally.
- If any file is missing, the playbook names each missing file and suggests running `brownfield-onboarding` to establish the baseline.
- Full specification artifacts (`docs/spec/work/prd.md`, `docs/spec/features/*.feature`, and the other single-file core artifacts in `docs/spec/`) are optional inputs that deepen the process when present, not prerequisites.
- The anchor-file check does not distinguish between a brownfield-lite baseline (Stage 1 only) and a fully reverse-engineered project (Stage 2 complete). The depth is a continuum; the prerequisite only establishes the minimum.

See [core-artifact-layout.feature](features/core-artifact-layout.feature) and [entity-model.md § ANCHOR_FILE_SET](entity-model.md#notes). `newcomer-onboarding.feature` names the same four anchor files in its three anchor-file Rules (gap CAL-G15 in [core-artifact-layout-gaps.md](work/core-artifact-layout-gaps.md)).

## Reverse-map confidence hierarchy

The `reverse-map` skill assigns a confidence level to each scope-map row based on the source type. The hierarchy, from highest to lowest confidence:

| Source type                      | Confidence  | Rationale                                  |
| -------------------------------- | ----------- | ------------------------------------------ |
| Passing test                     | verified    | Mechanically proven behavioral claim       |
| Failing/skipped test             | flagged     | Documents intent, known broken or deferred |
| Code entry point                 | high        | Exists and executes, but not test-verified |
| Test fixture/factory             | medium-high | Reveals entity model and relationships     |
| API spec (OpenAPI, Postman)      | medium      | Declared contract, may not match code      |
| Repo docs (README, comments)     | medium-low  | Close to code, but often stale             |
| External docs (Confluence, wiki) | low         | Furthest from code, most likely to drift   |
| Stakeholder verbal claim         | lowest      | Tribal knowledge, unfindable elsewhere     |
| Document-only (no code match)    | claimed     | Asserted by docs but unverifiable in code  |

- A row's confidence is determined by its strongest supporting source.
- The Sources column lists all contributing sources, not just the strongest.
- Confidence levels are informational, not gatekeeping — no confidence level blocks feature work.

See [newcomer-onboarding.feature](features/newcomer-onboarding.feature).

## Referenced from

- [entity-model.md](entity-model.md)
- `UC-04`
- `UC-06`
- `UC-08`
- `UC-09`
- `UC-11`

## Test-design validation (BR-051, BR-052, BR-053, BR-054, BR-055)

- **BR-051**: The test-design skill requires `detect-test-regime` as a prerequisite. If `docs/testing.yaml` lacks a `testing_strategy:` link or a `suites:` section, the skill fails with a diagnostic message and produces no output. This is a hard prerequisite, not a fallback path.
- **BR-052**: Test ownership is resolved in a single backlog-wide pass through `backlog/epics.md`. Each contract has exactly one owning story determined by dependency order: the story that introduces the contract's infrastructure or first exercises it (earliest in dependency-sorted order among stories that trace the contract). No contract is tested twice at the same layer.
- **BR-053**: Risk-class classification follows a three-level precedence chain: `testing.yaml` `risk_classes:` overrides > project-linked strategy document > Factory convention defaults. The Factory convention defines three risk classes: `critical` (format: `forbidden`, budget: `unbounded`), `standard` (format: `scenario`, budget: `equivalence`), `structural` (format: `linter`). Projects may add custom risk classes; custom classes must define at least `format` and `budget`.
- **BR-054**: The `test-design-verify` gate validates the trace-to-scenario resolution chain. Exit codes follow the gate convention: `0` = pass, `1` = validation failure, `2` = configuration error. The gate is conditionally active — it runs when the story has `#### Test Design` or `#### Prior Tests` sections and exits `0` with no findings when neither exists.
- **BR-055**: The `gates` section in `docs/testing.yaml` configures individual gates (enabled/disabled, thresholds). It does not define execution ordering; [ADR-0012](../adr/0012-dispatcher-owned-semantic-gate-loop.md) owns the dispatcher's gate sequence. The CRAP-score script reads `gates.crap-score.threshold` from `testing.yaml`, replacing the dead-code `read_threshold_from_house_rules()` function. When the `gates` section is absent, the script falls back to its hardcoded default of 30. `premerge-check`, `crap-score`, and `mutation-testing` also read the old keys with underscores: `crap_score`, `mutation_testing`, and `test_design_verify`. `premerge-check` writes no `docs/testing.yaml`, and the test-strategy agent writes only the keys with hyphens (OI-02). When a gate has an entry under both forms, such as `crap_score` and `crap-score`, the key with hyphens wins and the gate runs once. Each of the three scripts then prints a warning that names the old key, so the User can delete it.

## Concern registry validation (`concern-lint`, CTX-\* codes)

`concern-lint` validates the single concern-oriented routing format. All findings are errors and make the command exit non-zero.

| Code           | Condition                                                                                                                                                  |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CTX-SECTIONS` | A required category is absent, or a concern lacks a description or `Read:` path                                                                            |
| `CTX-PATHS`    | A repository-relative path or glob on a `Read:` or `Boundary:` line has no match                                                                           |
| `CTX-REFS`     | A technical or domain name in story `concerns:` has no matching heading in `docs/agent-context.md`                                                         |
| `CTX-LEGACY`   | `docs/agent-context.md` exists beside legacy YAML agent-context files or `docs/charter/`; `docs/testing.yaml` is the only accepted test-configuration path |

- Category headings are exactly `## Always (cross-cutting)`, `## Technical concerns`, and `## Domain concerns`.
- Cross-cutting concerns are always active and never repeated in story frontmatter.
- Technical and domain concern names form a controlled vocabulary. The planning maintainer proposes and obtains confirmation for a new entry before a story uses it.
- `capture-context --fold-context-map` writes one domain concern per context of a context map or a routing-only `CONTEXT.md`, and marks it as folded. A folded concern has a `Read:` path that passes `CTX-PATHS`. `capture-context --update --scan` keeps every folded concern, also when it is not a scope-map area. See [core-artifact-layout.feature](features/core-artifact-layout.feature).
- `update-context` is retired and performs no write. The team maintains `docs/agent-context.md` directly.
- `detect-test-regime` and test gates own the schema and values in `docs/testing.yaml`; concern validation does not parse test configuration.

See [agent-context.feature](features/agent-context.feature) and [interface-contracts.md § concern-lint](interface-contracts.md#agent-factoryfactoryscriptsconcern-lint).

## Dispatch ledger (`dispatch`)

These rules hold the ledger of a run in [run-lifecycle.feature](features/run-lifecycle.feature). [state-machines.md § Ledger Entry Lifecycle](state-machines.md#ledger-entry-lifecycle) holds the states of a unit of work. [interface-contracts.md § dispatch](interface-contracts.md#agent-factoryfactoryscriptsdispatch) holds the subcommands, and [interface-contracts.md § premerge-check](interface-contracts.md#agent-factoryfactoryscriptspremerge-check) holds the checks at the merges. The items RL-G01 to RL-G23 are in [run-lifecycle-gaps.md § Settled Items](work/run-lifecycle-gaps.md#settled-items). The items OI-01 to OI-16 are in [run-lifecycle-qa-strategy.md § Settled Items](work/run-lifecycle-qa-strategy.md#settled-items).

- `mark-dispatching`, `mark-dispatched`, `mark-blocked`, `mark-failed`, `re-dispatch`, and `escalate` are idempotent no-ops when the story is already in the target state or tier outcome.
- `mark-failed` records an attempt entry with `session`, `tier`, `failure_class`, `evidence`, `commit_sha`, and `normalized_total`; a legacy ledger without `attempts` still loads as zero attempts.
- `close-wave <N>` refuses while a unit of work in wave N can still go on, and names it. A unit of work lets its wave close in five states: `done`; `blocked`; `failed` when the predicate HasStopped of [state-machines.md § Ledger Entry Lifecycle](state-machines.md#ledger-entry-lifecycle) holds; `pending` after a return, with `returned: true`; and `pending` while it depends on a returned story, directly or through another story. Such a dependent story can never start in this run, because BR-113 holds it back and `dispatch add` refuses a story ID (BR-117). Every other state keeps the wave open: `prepared`, `dispatching`, `dispatched`, `failed` with a retry left, and `pending` with no returned dependency. For example, ST-0350 is returned in wave 1, and ST-0351 depends on it. Both stay `pending`, and once the drift rows of wave 1 are handled, `close-wave 1` passes.
- `close-wave <N>` appends at most one closeout record for the wave. Re-running a successful close-wave is a no-op and does not duplicate the record.
- **BR-111**: The ledger's `mode` is `orchestrated` or `by-hand`. `dispatch init` without `--mode` writes `orchestrated` (RL-G02). The ledger names the branch of its run in `feature_branch`. It has no `closed` field, because a ledger exists only while its run is active. No entry has `gate_results`, because `premerge-check` runs the gates again at the merge. `dispatch` reads `invocation_branch` as the old name of `feature_branch` and `mode: automated` as the old name of `mode: orchestrated`. It writes only `feature_branch` and the values `orchestrated` and `by-hand` (OI-09). So `dispatch close` ends an old ledger whose branch still exists.
- **BR-112**: One ledger exists per feature branch, and several runs may be active at once. `dispatch init` on a feature branch whose ledger lists the same stories is a no-op that exits `0`, so an interrupted start can resume. With other stories, `init` refuses (RL-G04). An orchestrated run starts beside any other run. A run by hand is refused while another run by hand is active, because both need the primary checkout, and the message names the active run. `init` refuses a story whose dependency outside the run is not done in the backlog, and names that dependency. `branch_root` is the 40-character SHA of the tip of the feature branch at `init`. `init` reads the test command from `docs/testing.yaml`, and without one it refuses and names that file.
- **BR-113**: `dispatch prepare-wave` and `dispatch prepare-story` read only the ledger to check dependencies. A unit of work starts only when every story it depends on inside the run is `done`, and both commands check every such dependency. So a returned story holds back every story that depends on it, directly or through another story, and stories outside that chain start. Both commands refuse until the previous wave has a wave record. Both also refuse an entry with `returned: true`, because a returned unit of work waits for the end of the run. Only `dispatch add` takes a returned finding back and sets `returned` to `false` (BR-117). For example, ST-0351 was returned in the closed wave 1, and `prepare-story ST-0351` refuses and names the return. By hand, each story is a wave of its own, and `prepare-story` writes the next free wave number into an entry without a wave (RL-G08). It keeps the wave that `dispatch add` wrote into the entry of a finding (BR-117). By hand, `prepare-story` also refuses while the primary checkout holds an uncommitted change to a tracked file, as `git status --porcelain --untracked-files=no` lists it. It exits `1`, names each file, cuts no branch, and changes nothing. Untracked files do not count. A failing `git status` also refuses, because `prepare-story` cannot tell whether the checkout is clean. For example, the primary checkout holds an uncommitted change to `src/login.py`, and `prepare-story ST-0350` names `src/login.py` and creates no branch `story/ST-0350`.
- **BR-114**: A counted attempt is an attempt with the failure class `acceptance_unmet` or `contradictory_evidence`. A failing gate records `acceptance_unmet` (RL-G01). A unit of work gets `gates.attempts` counted attempts on its tier, the first attempt included, and then `gates.attempts_escalated` counted attempts on the next tier. Both values default to `3`, and `gates.attempts_escalated: 0` turns escalation off. `dispatch` enforces both limits on both ways, not only the implementation agent (OI-03). `re-dispatch` after a counted attempt keeps the tier while the counted attempts on that tier are fewer than the tier's limit. Once they reach the limit, `re-dispatch` refuses while `dispatch escalate` can still promote the unit of work (BR-116). An attempt of any other class does not count and keeps its re-dispatch rule: a unit of work with two `contract_violation` attempts is terminal (RL-G16). For example, ST-0350 fails a gate, then dies on the spend limit with `spend_death`, then fails the gate again. That is two counted attempts, so with `gates.attempts: 3` ST-0350 gets a third counted attempt on its tier before it escalates. The tier of a unit of work is the tier it runs on now: `active_tier` of its entry, else the tier of the story. `mark-failed` records each attempt on that tier, and `dispatch` counts it there. A seams-first implementation session runs one tier below the story's tier, so its attempts count on that lower tier, and it escalates from there. So a seams-first story declared `standard` starts its implementation session on `economy`, and its one escalation takes it to `standard`.
- **BR-115**: `dispatch escalate` grants a promotion to the next tier only when all of these hold: the counted attempts on the current tier reach `gates.attempts`; `gates.attempts_escalated` is above `0` (OI-03); the tier is not `strong`; the unit of work has not escalated before; `verify-base` passes; and the diff stays inside the scope. Otherwise it refuses, exits non-zero, and leaves the tier unchanged. A refusal for `verify-base` or for the scope is a check of the branch, so `escalate` records it in the field `reason` of the entry, as `escalate refused: verify-base` or `escalate refused: scope`. The record holds until the next `escalate`, which clears it on a grant or rewrites it on a refusal, or until `re-dispatch` sets the entry `prepared`. The other refusals write nothing, because the ledger already shows their cause. `escalate` and `re-dispatch` also refuse an entry without `branch` or without `base_sha` when they need the checks of the branch, because the checks cannot run. They exit non-zero and write no record then. An escalation of another story in the same wave does not count, so every story that uses up its attempts escalates. A unit of work that `escalate` refuses for any of these reasons other than the attempt count becomes `failed` once its attempts are used up (RL-G01): its tier is `strong`, it has escalated, escalation is off, `verify-base` fails, or the diff leaves the scope. Only `re-dispatch` gives such a unit of work new counted attempts (BR-116). Every other unit of work escalates first.
- **BR-116**: A failing gate or a failed spawn sets a unit of work to `failed`. A `failed` unit of work has stopped only when the predicate HasStopped of [state-machines.md § Ledger Entry Lifecycle](state-machines.md#ledger-entry-lifecycle) holds: two of its attempts have the failure class `contract_violation`, or its counted attempts on its tier reached the limit and it cannot escalate any more. A unit of work cannot escalate any more when `dispatch escalate` refuses it for any reason of BR-115: its tier is `strong`, it has escalated, `gates.attempts_escalated` is `0`, `verify-base` fails, or its diff leaves the scope. HasStopped reads the last two from the field `reason`, where `escalate` records them (BR-115), so `close-wave` reads only the ledger. Every other `failed` unit of work still has a retry, and the implementation agent starts the retry without the User. A unit of work stops as `blocked` on a red test suite after its merge. In an orchestrated run it also stops as `blocked` on a refresh conflict, or when git refuses its merge and `merge-story` records the reason `merge conflict`. The refresh merges the feature branch into the story branch first, so a content conflict shows up as a refresh conflict. git refuses the merge itself for another cause, for example an untracked file in the worktree of the feature branch that the merge would overwrite. By hand, a refused merge keeps the unit of work `dispatched` (BR-124). On a red test suite, `dispatch merge-story` moves the feature branch back to the commit before the merge and sets `blocked`; it makes no revert commit. `dispatch re-dispatch` keeps the branch `story/<id>` and its worktree. It refuses a `failed` unit of work whose counted attempts on its tier reached the limit while `dispatch escalate` can still promote it, and names `dispatch escalate` (OI-03). When no promotion is left, because the unit of work cannot escalate any more, the User fixes the cause and tells the implementation agent to continue. `re-dispatch` then grants `gates.attempts` new counted attempts on the current tier. It records the grant as one item in the list `attempt_grants` of the entry (OI-13). The item holds `tier`, the tier of the grant, and `attempt_count`, the number of items in `attempts` at the grant. Only the counted attempts after the last grant count toward the limit (RL-G19). For example, ST-0350 failed three counted attempts on `standard` and three on `strong`, because a shared test fixture was broken. The User fixes the fixture, and `re-dispatch` gives ST-0350 three new counted attempts on `strong`. In a second example, ST-0350 failed three counted attempts on `standard`, and its diff changes a file outside its declared outputs. `escalate` refuses and records `escalate refused: scope` in `reason`, so ST-0350 has stopped, `close-wave 1` passes, and the User decides. Once the User moves the diff back inside the scope, `re-dispatch` refuses again and names `dispatch escalate`. `re-dispatch` takes no flag for the grant, and `dispatch` cannot check that the User fixed the cause. That is an accepted limit: on the last tier an agent can start a retry that the User did not ask for. The User watches the run, and the guardrail blocks only the two commands that destroy work, `dispatch return-story` and `dispatch close --drop`. `dispatch return-story` sets a `failed` or `blocked` unit of work to `pending` and sets the field `returned` of its entry to `true`. For a story it also sets `pending` in `backlog/<id>.md`. For a finding it changes only the ledger entry: the finding file keeps `status: open` and its `run`, so it still blocks the feature merge, and `dispatch` reads no `backlog/<id>.md`.
- **BR-117**: `dispatch add` accepts only an open blocking finding (BR-085). It refuses a story ID, a finding that is not open, and a finding that does not block, and names the reason (RL-G07). A new ID gets a new ledger entry in a new wave, the next free number, on the default tier and without dependencies. The finding's `artifact` serves the overlap planning in place of a story's file list. An ID that the ledger holds as `pending` reuses its entry: the entry goes into a new wave, its attempts restart at the first attempt on the default tier, its field `returned` goes back to `false`, and the branch `story/<id>` stays. `add` refuses an ID that the ledger holds in any other state, and names that state.
- **BR-118**: Only `dispatch merge-story` sets a unit of work to `done`. It sets `status: done` in `backlog/<id>.md` for a story, or `status: resolved` in `docs/findings/<id>.md` for a finding, in the merge commit. When a hook refuses the amend that writes this status into the merge commit, `merge-story` exits `1`, names the installed commit hooks, and leaves the entry `dispatched`. A rerun reads the status from the merge commit and amends again. `dispatch` has no `mark-done` subcommand, and the developer agent's commits never set either status. After the merge, the entry's `commit_sha` holds the merge commit, and `prepare-story` reads it as the base of the next story in a serial chain.
- **BR-119**: `dispatch close` and `dispatch close --drop` refuse while a unit of work of the run is `failed` or `blocked`, whether HasStopped holds for it or not, and name it. They accept a run whose units of work are `done` or `pending`. `dispatch close` also refuses while the feature branch is not merged into `dev`, and names `dispatch close --drop` (RL-G05). Before a close removes a worktree, it puts the untracked files and the uncommitted changes of tracked files of that worktree into one stash, named such as `run feature/login ST-0350 2026-11-24`, and does not apply it (RL-G15). The close lists each stash it made and each branch of the run that is not merged.
- **BR-120**: `dispatch close --orphans` lists the worktrees and branches that belong to no ledger. It removes each such worktree whose branch is merged into `dev`, and lists every other one (RL-G10). It finds each ledger whose feature branch is gone, also a ledger nested inside a worktree. It removes such a ledger when every story in it is `done`, and lists every other one.
- **BR-121**: A finding file names the review that filed it in two fields. A finding of a story's review has `story` set to the story ID and an empty `run`. A finding of the feature checks has an empty `story` and `run` set to the feature branch, such as `run: feature/login`. A finding of a review outside any run leaves both fields empty. `finding-lint` refuses a finding file that sets both `story` and `run`, and names the finding ID and both fields (OI-05). This check covers every finding file in `docs/findings/*.md`, also a file without `review_class` (OI-14). A register file keeps its required `story` field. `traces` lists related spec items and stories, but only `story` and `run` count at the merges.
- **BR-122**: The code-review report of a story is `docs/reviews/code-review-<story-id>-YYYY-MM-DD.md`. A second review of the same story on the same day adds `-2` to the name, and a third adds `-3`. Its frontmatter sets `story` to the story ID and `branch_head` to the head of the story branch it reviewed. The developer agent commits the report on the story branch, also when the review filed no finding. A report of the feature checks sets `run` to the feature branch and `branch_head` to the head of the feature branch it reviewed (RL-G06). These reports are the code review of the whole feature, `docs/reviews/code-review-<feature-branch>-YYYY-MM-DD.md` with the slash of the branch name replaced by a hyphen, and the Fagan, security, and bug-hunt reports of the QA agent. A report of the feature checks leaves `story` empty. A doc-scoped review, such as a spec review or a reconciliation, sets `story` to the ID of the artifact it reviewed. The numbers `-2` and `-3` apply only to the review of a story. A second code review of the whole feature on the same day writes the same name, so it replaces the first report.
- **BR-123**: Each merge check of `premerge-check` adds a temporary worktree and removes it afterwards. A story or finding check adds it at `.current-work/<feature-branch>/premerge/<id>`. The feature merge `premerge-check dev <feature-branch>` adds it at `.current-work/<feature-branch>/premerge/feature`, such as `.current-work/feature/login/premerge/feature`. A crashed earlier run can leave a worktree at that path. So before `premerge-check` adds the worktree, it runs `git worktree remove --force` on the path and then `git worktree prune` (ATAM-0023). A leftover worktree thus never blocks the next check of the same unit of work. For example, a crash left `.current-work/feature/login/premerge/ST-0350`, and the next `premerge-check` on `story/ST-0350` removes it, adds its own worktree there, and passes.
- **BR-124**: `dispatch merge-story` merges nothing when `premerge-check` refuses, when the worktree of the feature branch in an orchestrated run holds an uncommitted change, or when git refuses the checkout or the merge. In each case it exits `1`, the entry stays `dispatched`, the story branch stays checked out, and the feature branch does not move (ATAM-0021). By hand, the checkout or the merge refuses, for example, when the primary checkout holds an uncommitted change to a tracked file. The message then names the files and the checkout they sit in. The User commits or reverts the change and runs `merge-story` again, which reruns `premerge-check`. In an orchestrated run, `merge-story` runs in the worktree of the feature branch and checks nothing out. It runs `premerge-check` first and checks that worktree only after `premerge-check` exits `0`. It then refuses when the worktree holds an uncommitted change to a tracked file, also to a file the story did not touch. A failing gate thus never hides behind a message about an uncommitted file. Its message names the files and the worktree. The implementation agent reports the message to the User unchanged and does not repair the worktree. The key `dispatch.refuse_dirty_feature_worktree` in `docs/testing.yaml` turns this refusal off with `false`, and a missing key means `true`. The key affects only orchestrated runs, so by hand git's own refusal of the checkout or the merge stays. For example, by hand `premerge-check` passes `story/ST-0350`. The primary checkout holds an uncommitted change to `packages/factory/scripts/dispatch`, which ST-0350 also changed, so git refuses the checkout of `feature/login`. `merge-story` names `packages/factory/scripts/dispatch` and the primary checkout, exits `1`, and ST-0350 stays `dispatched`.

## Local usage processing and analysis

These rules support the [local usage feature](features/local-usage-processing-and-analysis.feature).

### Input and contract validation

- Snapshot a sorted list of top-level `*.jsonl` files at query start. Do not recurse or admit lifecycle diagnostic files.
- Validate every selected line. A valid line and a preflight failure are mutually exclusive and collectively exhaustive.
- Report each failure with source file, one-based line number, field when applicable, and a stable failure code.
- Validate usage objects against the installed JSON Schema Draft 2020-12 contract and the manifest's accepted version range.
- Enforce identifiers, timestamps, declared nullability, non-negative counters, nested `transcript_ref` shape, and `normalized_total = normalized_input + normalized_output` outside schema where required.
- Reject an unknown CLI. The supported CLI set and accounting registry keys must be exactly `claude-code`, `pi`, `codex`, `copilot`, and `opencode`.
- Before selecting a latest snapshot, group evidence by `(cli, session_id, run_id)` and require one distinct `parent_run_id`, treating null as a value. If evidence disagrees, classify every snapshot for that key as `USAGE_ANCESTRY_PARENT_CONFLICT`; do not select one snapshot to establish or override the parent.
- Partition logical runs by `(cli, session_id)` and require exactly one null-parent root, same-partition parent resolution for every non-root, no self-links, no cycles, and reachability of every run from the root.
- Report malformed ancestry with `USAGE_ANCESTRY_ROOT_COUNT`, `USAGE_ANCESTRY_PARENT_MISSING`, `USAGE_ANCESTRY_PARENT_BOUNDARY`, `USAGE_ANCESTRY_SELF_PARENT`, or `USAGE_ANCESTRY_CYCLE`. Any ancestry failure blocks canonical accounting.

### Snapshot and accounting validation

- Normalize source paths relative to the selected usage directory: valid UTF-8, Unicode NFC per segment, `/` separators, no `.` segments, and rejection of absolute paths or `..` traversal.
- Preserve `(normalized_source_path, source_line)` as evidence identity until canonical-run reduction; line numbers are positive and one-based.
- For each supported CLI, define logical-run identity as `(cli, session_id, run_id)`. The invariant `parent_run_id` defines the validated rooted-tree ancestry but does not enter identity. Direct children name the unique root's run ID; descendants are the transitive closure of valid parent links. Evidence source, capture sequence, and record content are excluded from logical-run identity.
- Select the latest cumulative snapshot by maximum `(capture_sequence, normalized_source_path, source_line)`. Compare capture sequence and line numerically and normalized paths by unsigned UTF-8 byte lexicographic order.
- Claude Code total: latest root snapshot plus each distinct child run once.
- Pi total: root record plus each distinct descendant run once.
- OpenCode total: latest root snapshot plus each distinct child run once (matches Claude Code model).
- Codex total: latest inclusive root snapshot; descendants provide attribution only.
- GitHub Copilot CLI total: latest inclusive root snapshot; descendants provide attribution only.
- Canonical session dimensions and timestamp come from the selected root snapshot. Additive descendant measures do not replace those dimensions.
- Cache aggregation uses the same contributing logical-run set as the CLI's conservation rule.
- Dimensional measures are additive over canonical session rows. Accept an ordered, duplicate-free subset of project, CLI, provider, model, agent, branch, and exit status plus time granularity `none`, `hour`, `day`, `week`, or `month`.
- Default to no dimensions and time granularity `none`, producing one all-input total. Reject duplicate or unknown dimensions. Use UTC calendar truncation and ISO Monday week starts.
- Preserve cache availability and input-only states. Do not replace unavailable values with zero.

### Query and export validation

- Publish exactly six stable views: `raw_usage_snapshots`, `latest_run_snapshots`, `session_usage`, `usage_by_dimension`, `cache_efficiency`, and `capture_health`.
- Enforce the complete `query-model-v1` schema, key, nullability, and stable result ordering declared in [interface-contracts.md § Query-model-v1 schema contract](interface-contracts.md#query-model-v1-schema-contract) for non-empty and empty results.
- Allow `capture_health` for any preflight outcome. Refuse every other stable view and all stable exports when any preflight failure exists.
- Treat an empty input directory as valid and return each view's typed empty schema.
- Ensure table, JSON, DuckDB relation, and PyArrow table outputs preserve view schema, logical rows, and null states.
- Reject Pandas and Polars conversions in release 1.
- Write Parquet to a temporary sibling, verify rows and schema, attach query-model and input-set provenance, then atomically replace the destination. Failure leaves an existing destination unchanged.
- Never schedule or automatically refresh Parquet.

### Privacy, dependency, and lifecycle validation

- Read selected usage records only. Do not follow `transcript_ref`, recurse into transcript storage, or use a remote reader.
- Keep analytical dependencies isolated from Factory capture. Capture succeeds when analysis is absent or corrupt.
- Declare DuckDB and PyArrow as direct usage-analysis dependencies, pin a compatible pair and their transitive closure in the shipped lockfile, and reject an unlocked or incompatible dependency set.
- Prove offline installation and query execution from a complete locked-artifact cache with network access disabled. Do not add DuckDB or PyArrow to Factory's dependency graph.
- Verify the documented DuckDB UI launch command and query-model bootstrap without starting the UI or fetching assets; the bootstrap registers exactly the six published views.
- Install analysis only on `--with-usage` or `--add usage`; record it under `installed_components`.
- Update only the named component after compatibility succeeds. Remove only analysis on `--remove usage`. Both preserve `.agent-factory/usage/`.
- Keep `update-factory` scoped to Factory core. Preserve installed components.
- Keep `remove-factory` as a complete uninstall, including `.agent-factory/usage/`.
- Repeating a successful component operation against its resulting state is a clean no-op.

### Explicit deferrals

Release 1 excludes persistent analytical databases, automatic Parquet materialization, notebooks, dashboard products, the community `dash` extension, services, containers, remote resources, centralized collection, access control, price catalogs, transcript-content indexing, automatic evidence retention or deletion, Pandas, and Polars.

## Activity-Graph Orchestration Validation Rules

Proposal trace: [activity-graph-orchestration.md](../proposals/activity-graph-orchestration.md).
Feature trace: [activity-graph-orchestration.feature](features/activity-graph-orchestration.feature).

### Workstream state validation

Rules for `.agent-factory/workstreams/<workstream-id>.yaml`:

1. `schema_version` must be `2`.
2. `workstream_id` must be a non-empty string matching the filesystem-safe slug pattern `[a-z0-9][a-z0-9_-]*`.
3. `topic` must be a non-empty string.
4. `origin_ref` must be null or a valid repository-relative file path.
5. No other fields may exist. The presence of `cycle`, `attempt`, `revision`, `delegation`, or `work` makes the file invalid.
6. The file is immutable after creation. Any attempt to modify an existing state file must fail without changing it.

### Session binding validation

Rules for `.agent-factory/workstreams/sessions/<session-id>.yaml`:

1. `session_id` must be a non-empty string.
2. `workstream_id` must be present as a key. A known workstream identifier means the session is bound. Explicit `null` means Open Stage. A missing key fails validation.
3. When `workstream_id` is not null, it must reference an existing workstream state file under `.agent-factory/workstreams/`.
4. `bound_at` must be a valid UTC timestamp in ISO 8601 format.
5. Selecting a different workstream updates `workstream_id` and `bound_at`. No workstream state file is modified.

### Agent definition structural validation

Rules for agent definition files under `packages/factory/agents/` (tracked source):

1. `inputs` must contain `required` and `context` subkeys. Both may be empty lists.
2. Each `inputs.required` entry must have `artifact` (string) and `path_pattern` (string). `conditions` is optional.
3. Each condition must contain exactly one of: `field`+`value`, `field`+`one_of`, or `check`.
4. `check` must reference a trusted validator by name — resolved to a bash script under `.agent-factory/factory/scripts/` or a Python validator under `.agent-factory/factory/engine/validators/`. Shell commands are rejected.
5. `inputs.context` entries are plain path strings (no conditions, no artifact type).
6. `outputs` must contain `minimum_changed` (non-negative integer) and `declarations` (list).
7. Each output declaration must contain `path_pattern` (string), `validator` (string), and `required` (boolean). Missing fields make the agent definition invalid.
8. `minimum_changed: 0` is valid and permits a legitimate no-output activity.

### Skill definition structural validation

Rules for skill definition files:

1. Skills may have `inputs.context` (plain paths). They must not have `inputs.required`.
2. Skills do not appear in the precondition graph.
3. Skills do not declare `outputs` with validators or `minimum_changed`.

### Scope declaration validation

Rules for governed artifacts in the closed first-release set: proposals, epics, stories, Gherkin feature files, `architecture.dsl`, `scope-map.md`, and `entity-model.yaml`.

1. Every governed artifact must carry a `scope` declaration.
2. The value must be either `global` or a known workstream identifier (one that has a state file under `.agent-factory/workstreams/`).
3. Proposals carry `scope` in YAML frontmatter in place of `title`. The display name is in the document heading.
4. Epics, stories, and `scope-map.md` carry `scope` in YAML frontmatter alongside other fields.
5. `entity-model.yaml` carries `scope` as a top-level YAML field.
6. Gherkin feature files carry `scope` as a first-line comment: `# scope: <value>`.
7. Structurizr DSL (`architecture.dsl`) carries `scope` as a first-line comment in the same form as feature files: `# scope: global`. The older `// scope: global` form still passes.
8. A governed artifact missing the declaration or carrying an unknown value is rejected at artifact creation time.
9. Non-governed artifacts (ADRs, reviews, findings, research records, etc.) need no scope declaration.

### Fence validation rules

01. The fence runner snapshots the agent's declared output patterns before invocation.
02. After the activity, each output declaration is checked against files created or modified.
03. A required output with no created or modified match fails the fence.
04. An optional output with no match is skipped. If it changed, its validator runs.
05. The fence fails when fewer than `minimum_changed` declarations have a created or modified match.
06. When one declaration matches several changed files, its validator receives the resolved file list in one invocation.
07. When several declarations match, all applicable validators run.
08. The aggregate fence passes only when every required output changed, the minimum was met, and every invoked validator passed.
09. Per-output and aggregate evidence is stored at `.agent-factory/checks/fences/<session-id>/<invocation-id>.yaml`.
10. Fence failure does not block human action. Fence results are informational in human sessions.

### Artifact precondition validation

For each artifact type, the following mechanical validation checks apply. Semantic assessment (`intent assess`) is a separate, human-triggered layer.

**Proposal.** File exists at the declared path. YAML frontmatter contains `scope` (workstream identifier, replacing `title`), `status`, and `owner`. Required sections exist. The `status` field satisfies the declared condition.

**Scope map.** File exists at `docs/spec/scope-map.md`. Passes scope-map validation (`spec-lint`). Behavior identifiers are unique. Source references resolve to existing artifacts. Feature link references resolve to existing code.

**Entity model.** File exists at `docs/spec/entity-model.yaml`. Passes LinkML metamodel validation. `linkml-lint` reports no errors. Every referenced class and slot resolves.

**Architecture.** File exists at `docs/spec/architecture.dsl`. Passes Structurizr validation. Passes architecture lint (`arch-lint`). Referenced views resolve.

**Feature specifications.** Every `.feature` file referenced by the scope map exists. Each file parses as valid Gherkin. First-line scope comment is present and valid.

**Gaps report.** Required sections (actor-goal matrix, missing rules, ambiguous wording) exist. Every recorded gap has an identifier and a disposition.

**Research brief.** Passes brief schema validation (`research-brief.schema.json`). `decision_needed` is the only delivery-link field. No `origin_cycle` or `return_cycle` fields exist.

**Research report.** Passes route-specific validation (survey or falsification). References the originating brief. Records evidence disposition for each claim or source.

## OpenCode CLI Integration Validation Rules

Proposal trace: [opencode-cli-integration.md](../proposals/opencode-cli-integration.md).
Feature trace: [opencode-cli-integration.feature](features/opencode-cli-integration.feature).

### Installation validation

1. Detection markers for OpenCode are `.opencode/`, `opencode.json`, and `opencode.jsonc`. The presence of any one marker selects OpenCode as an active CLI target.
2. Explicit `--cli opencode` selection produces the same installation as auto-detection.
3. The installer checks `opencode --version` before creating any OpenCode path. A version older than `1.18.31` stops installation and prints an upgrade instruction naming the minimum version.
4. The installer creates `.opencode/INDEX.yaml`, `.opencode/agents/`, and links the plugin into `.opencode/plugins/`. Skills are placed at `.agents/skills/`.
5. Every created OpenCode path is recorded in `.agent-factory/install.json` under the `opencode` CLI key.
6. Repeated installation against the same project state produces no additional changes (idempotent).
7. User-owned files under `.opencode/` are not overwritten, modified, or removed during installation or update.

### Removal validation

1. `remove-factory` removes every path listed in `.agent-factory/install.json` for the `opencode` CLI key.
2. `remove-factory` does not remove user-owned OpenCode configuration (files not recorded in `.agent-factory/install.json`).

### Coexistence validation

1. A project with Pi, Codex, and OpenCode installed has exactly one root `AGENTS.md`.
2. Adding OpenCode to an existing multi-CLI project does not modify the other CLIs' files.

### Plugin permission validation

1. The plugin evaluates allow rules first, ask rules second, and deny rules last.
2. An explicit configured deny is final. The plugin's permission hook does not change a `deny` effect to `allow` or `ask`.
3. A pre-tool hook reads the active step manifest and denies reads outside its declared inputs.
4. A pre-tool hook reads the active step manifest and denies writes outside its declared outputs.
5. The plugin passes the command of each `shell` call and the JavaScript of each `execute` call to `block-dangerous-git.sh` as command text. It denies the call before execution when the script denies it (ATAM-0022).
6. Review agents whose definitions declare no write outputs receive read-only tool sets (write tools removed).
7. Tool removal restricts the active agent to its declared tool set.
8. Child sessions inherit session-scoped restrictions from the root session and apply their own generated agent permissions.

### Plugin fail-closed validation

1. The plugin fails closed when initialization fails. The Factory entry flow stops and the error names the failed control and the recovery action.
2. The plugin fails closed when the step manifest cannot be read or parsed. Tool invocations are denied.
3. The plugin fails closed when the permission evaluation hook encounters an error. Tool invocations are denied.
4. The plugin fails closed when worktree creation fails. The dispatch is denied and the error names the recovery action.
5. Usage capture failure does not trigger fail-closed behavior. Usage capture is best-effort.

### Usage capture validation

1. Completed root sessions produce one usage record following the existing usage contract with `cli: opencode`.
2. Completed child sessions produce one usage record following the existing usage contract with `cli: opencode`.
3. The root session's usage record does not include the child session's usage.
4. Session completion does not reactivate the agent. No OpenCode-specific completion gate is introduced.
5. Usage capture failure is reported but does not block the session.

### Worktree isolation validation

1. The plugin registers a worktree strategy through `ctx.worktree.transform()` with strategy ID `agent-factory`.
2. Branch and worktree creation is delegated to Factory scripts. The Factory's naming, base, path, and verification rules remain authoritative.
3. Each dispatched child receives its own branch and worktree under `.current-work/<feature-branch>/`.
4. Each dispatched child verifies its declared base commit before reading or changing files.
5. The primary checkout receives a session-scoped write denial while any child session is active in an isolated worktree.

### Model configuration validation

1. `model.conf` supports `opencode.economy`, `opencode.standard`, and `opencode.strong` entries.
2. Model identifiers follow the `provider/model` format.
3. A missing required tier halts dispatch with the existing `on_missing = halt` policy.
4. Each generated OpenCode agent definition carries an explicit `model` field derived from its tier mapping in `model.conf`. This is the workaround for the model inheritance bug (OpenCode issue #49765).

## Value-First Onboarding Validation Rules

Proposal trace: [value-first-onboarding-journey.md](../proposals/value-first-onboarding-journey.md).
Feature trace: [value-first-onboarding-journey.feature](features/value-first-onboarding-journey.feature).

### Release and source validation

- **VFO-001:** A release build emits exactly one bootstrap, Factory archive, and checksum manifest for the requested version.
- **VFO-002:** Repeated builds from the same source tree and version produce the same archive SHA-256 digest.
- **VFO-003:** Installation accepts exactly one source selector. `--version` is valid only for a remote source.
- **VFO-004:** A remote archive is not extracted until its SHA-256 digest matches `SHA256SUMS` from the selected release base.
- **VFO-005:** An update never changes the recorded source kind or remote URL without an explicit selector and separate confirmation.

### Target and preflight validation

- **VFO-006:** First installation requires `--target`. The target must resolve to an existing Git repository or empty directory.
- **VFO-007:** The filesystem root, user home, unresolved paths, and unsupported target content are rejected without changes.
- **VFO-008:** Supported hosts are native macOS and Linux on `x86_64` and `arm64`, plus the Linux path under Windows Subsystem for Linux.
- **VFO-009:** Preflight produces exactly one readiness value: `Ready`, `Ready with limitations`, or `Blocked`.
- **VFO-010:** Preflight does not install software or edit host or project files.
- **VFO-011:** Every offered prerequisite fix identifies its purpose, command, scope, reversal, and verification command.
- **VFO-012:** A fix runs only after affirmative consent. Blank input, cancellation, and refusal stop the fix sequence.
- **VFO-013:** The related check must pass after a fix. Failure stops the sequence and produces recovery guidance.

### Installation and instruction-file validation

- **VFO-014:** Installation starts only after approval of a preview that names the source, version, target, interfaces, affected paths, instruction files, and uninstall command.
- **VFO-015:** Blank interface selection chooses one interface only when one detected active interface is unambiguous. It never means all interfaces.
- **VFO-016:** The receipt lists only paths changed by the completed installation and gives one exact next command.
- **VFO-017:** Instruction discovery visits existing regular `AGENTS.md` and `copilot-instructions.md` files outside the documented exclusions.
- **VFO-018:** Instruction discovery does not follow external symlinks or create missing nested instruction files.
- **VFO-019:** Each discovered instruction file contains at most one marker-delimited Factory header.
- **VFO-020:** The manifest records enough original state to update or remove only the Factory header and restore the prior newline state.

### Update validation

- **VFO-021:** `update-factory --check` performs no writes.
- **VFO-022:** A remote update verifies and stages all replacement content before applying any change.
- **VFO-023:** An application failure restores the previous Factory tree and instruction headers.
- **VFO-024:** Modified Factory-owned files stop update unless the user explicitly selects the preservation flow.
- **VFO-025:** A successful update records the resolved version or local revision, source, remote digest when applicable, and changed paths.

### First-session and configuration validation

- **VFO-026:** The initial project scan distinguishes observations, unknowns, and recommendations and performs no writes.
- **VFO-027:** Context capture starts only after onboarding explains its scan, decisions, single output, validation, and consumers.
- **VFO-028:** Onboarding defines `concern` as a routing topic before using the term without a paraphrase.
- **VFO-029:** Deferring or cancelling context capture before scanning produces no scan and no output file.
- **VFO-030:** The gate demonstration runs on a Factory-owned disposable fixture, removes the fixture, and leaves the target project unchanged.
- **VFO-031:** Consumer hook configuration omits `index-lint` and any trigger that can match only ignored Factory runtime paths.
- **VFO-032:** `matrix-lint` runs after model configuration and before dispatch.

### First-task validation

- **VFO-033:** First-task approval is affirmative and follows a preview of the goal, duration, artifacts, decisions, and cleanup.
- **VFO-034:** A repository with `HEAD` uses a detached worktree from that commit. A repository without `HEAD` uses a plain sandbox.
- **VFO-035:** The sandbox path is `.current-work/onboarding-spike/<session-id>/`. The first task creates no branch or commit.
- **VFO-036:** Retention copies only separately confirmed artifacts to a named path under `poc/spikes/`.
- **VFO-037:** Discard verifies sandbox removal. Production handoff requires separate approval and never promotes the sandbox.

## Ownership and spec-feedback reports (core artifact ownership, BR-056…BR-066)

These rules hold the producer and review contract of
[core-artifact-ownership.feature](features/core-artifact-ownership.feature).
The contract test and `index-lint` check BR-056 to BR-060. `dispatch close-wave`
checks BR-062 to BR-064. The agents and skills follow BR-061, BR-065, and BR-066. The `documentation-update` playbook follows BR-067.

- **BR-056**: Each entry of `packages/factory/rulebooks/core-artifacts.yaml` has exactly one producer. A producer is an output declaration without `edits: wording` whose path pattern matches the entry's sample path. No match fails the contract test, and more than one match fails it too, also when one match is a wide pattern such as `docs/spec/**/*.md`. Working output in `docs/spec/work/`, the reports in `docs/reviews/`, and the findings in `docs/findings/` are not entries, so several agents may declare them (DEC-34).
- **BR-057**: A sample path matches a path pattern by the rules of [Glob matching](#glob-matching-outputs-ownership). A placeholder such as `{name}` matches like `*`, inside one path segment. Gap CAO-G14 in [core-artifact-ownership-gaps.md](work/core-artifact-ownership-gaps.md) decides this.
- **BR-058**: The producer's declaration of a core or seam artifact carries `reviewed_by:` with a list of at least one entry. Each entry is an agent name or `stakeholder` (DEC-20, DEC-22). A missing field or an empty list fails the contract test.
- **BR-059**: `index-lint` fails when an entry of `reviewed_by:` is neither `stakeholder` nor the name of an existing agent. It also fails when the named agent declares the artifact neither as a required nor as a context input. The check matches the producer's output and the reviewer's input through the sample path, as BR-057 defines. An agent that only reads an artifact is never its review.
- **BR-060**: A declaration with `edits: wording` changes wording and never meaning. The contract test does not count it as a producer (DEC-32). `index-lint` carries `reviewed_by:` and `edits:` into `INDEX.yaml` unchanged.
- **BR-061**: A row of a spec-feedback report or a reconciliation report carries one of four statuses. The writer of the report sets `open`. The row's owner sets `fixed` after it changed the artifact. The owner's reviewer sets `confirmed` or `rejected`. When the reviewer is the stakeholder, the agent that ran the session with the stakeholder sets the status (DEC-28, DEC-34).
- **BR-062**: `dispatch close-wave <N>` reads the spec-feedback report of every story in wave N. It fails while a row has the status `open`, or the status `fixed` on an artifact that matches an entry of the core list. A `fixed` row on any other artifact, such as a QA strategy or an ADR, passes, because only core and seam artifacts have a declared review (DEC-35). A `rejected` row passes, because a `BUG` finding against the code takes its place.
- **BR-063**: A story without a spec-feedback report counts as a story without rows (CAO-G13).
- **BR-064**: By hand, each story is a wave of its own (BR-113). So `dispatch close-wave` runs after each story, and the story's spec-feedback report passes the check of BR-062 before the next story starts.
- **BR-065**: `docs/spec/glossary.md` holds only confirmed terms (DEC-15). Only the domain-modeling agent writes it. Any other agent that meets a term writes a row of `docs/spec/work/term-candidates.md` with the status `candidate`, or `confirmed` when the stakeholder settled the term in that session. The domain-modeling agent moves each `confirmed` row into the glossary and removes the row. A `rejected` row keeps the stakeholder's note. The domain-modeling agent may write a new definition from the note. The row then returns to `proposed` and keeps the note, and the stakeholder sees it at the next pause point (CAO-G09). Terms that `migrate-spec-layout` moved into the glossary count as confirmed (DEC-33). The `domain-modeling` and `grilling` skills write the glossary only when called with `--write-glossary`, and only the domain-modeling agent passes it; without it they write a `term-candidates.md` row (stakeholder, 2026-11-04).
- **BR-066**: The gates of a unit of work are `dependency-check` when `docs/spec/dependency-rules.dsl` exists, `test-design-verify` when the story has a Test Design or a Prior Tests section (BR-054), and each entry under `gates` in `docs/testing.yaml` with `enabled: true` and a command. `premerge-check` builds the calls of `crap-score` and `mutation-testing` itself, so their entries need no `command`. Every other gate needs a `command` in its entry (RL-G17). An entry under an old key with underscores, such as `crap_score`, counts as the entry of its gate (BR-055). The implementation agent runs them in the gate-check step, and `premerge-check` runs them again at the merge. Without `docs/spec/dependency-rules.dsl`, the gate-check step and `premerge-check` skip `dependency-check`, print that they skipped it because the file does not exist, and still run the other gates. A story's `quality-gates` field can only add gates: each gate it names runs as well, also when its entry has `enabled: false`. So a story with `quality-gates: [mutation-testing]` still runs an enabled `crap-score`. When the field names a gate that has no entry or no command in `docs/testing.yaml`, `premerge-check` refuses and names the gate (RL-G09). The field names `crap-score` and `mutation-testing` without an entry, because `premerge-check` builds their calls. `dependency-check` and `test-design-verify` keep their own conditions, so naming them in the field adds nothing. An entry with `enabled: true` and no `command`, for a gate other than `crap-score` and `mutation-testing`, gets the same refusal, also when no story's `quality-gates` names the gate (OI-15). When the story has no such field and `testing.yaml` has no `gates` section, the fail-closed default runs `crap-score`. The default never runs `mutation-testing`, because the mutation command lives only in the `gates` section (CAO-G25). An enabled mutation gate without `gates.mutation-testing.command` fails and names the test-strategy agent. The gate script stops the mutation command after `gates.mutation-testing.timeout_minutes`, 30 by default, and writes a failing result file; the merge reads that result (CAO-G27). A surviving mutant does not block the merge once the gate-check step has resolved it by one of the three actions of the `mutation-testing` skill: `remove-dead-code`, `add-missing-test`, or `file-qa-finding`. The gate-check step writes the list `mutants` into the result file, one entry per mutant in the report format of the skill, with `operator`, `location`, `status`, and `resolution_action`. An entry with `file-qa-finding` also names its finding in `finding`. The gate-check step commits each such `QA` finding on the story branch, so the merge brings it into the feature branch. `premerge-check` passes the mutation gate when the command exited `0`, or when all of these hold: the command ran within the time limit, the result file holds a list `mutants`, at least one entry of the list has `status: survived`, no entry has `resolution_action: unresolved`, and the `finding` of every `file-qa-finding` entry names a file `docs/findings/<ID>.md` at the head of the story branch. A non-zero exit fails without a list `mutants`, for example when the gate-check step never wrote the list. It fails the same way with an empty list or a list without a survivor, for example when the mutation command stopped on a broken configuration before it mutated a line. A result after a time-out, or of a command that did not run, fails whatever `mutants` holds. A `QA` finding of a survivor does not block the story merge. It carries `run: <feature-branch>`, so it blocks the merge of the feature branch into `dev` until it is resolved (BR-121). For example, ST-0350 leaves one survivor in `src/login.py:42`, and the gate-check step commits QA-0012 for it on `story/ST-0350`. ST-0350 merges, and QA-0012 runs in a later wave of the run. The `gates` section replaces `default_quality_gates` in `docs/charter/house-rules.md`. When `premerge-check` still finds `default_quality_gates`, it warns and names the file (CAO-G28). A failing gate blocks the merge. The pre-commit hook `agent_factory_hook-dependency-check` runs `dependency-check` on the whole repository when a commit stages a `.py` file anywhere in the repository. Its source root is the repository root, the default `.` of `dependency-check`; `premerge-check` passes the root of its temporary worktree the same way. Without `docs/spec/dependency-rules.dsl`, the hook prints `dependency-check: no docs/spec/dependency-rules.dsl, skipped` and passes, while the script called directly still exits `2`. pre-commit shows the output of a passing hook only under `pre-commit run --verbose`, so a plain commit shows the hook as `Passed` without the notice.
- **BR-067**: The orchestrator of the `documentation-update` playbook, the session that runs the playbook, carries each row of a reconciliation report back into its artifact. After a reconciliation run, the backfeed step reads every reconciliation report, not only the new one. It dispatches the owner of each `open` row and the reviewer of each `fixed` row on an artifact of the core list, one session at a time. So the step picks up where a stopped session left off. The owner fixes the artifact with the skill or workflow step its own agent definition names for that artifact, such as `model-structurizr-slice` for `docs/spec/architecture.dsl`. The owner sets the row to `fixed` in the same commit as the change. The reviewer is the one the owner's declaration names in `reviewed_by:`, and the reviewer sets `confirmed` or `rejected` (BR-061). When the reviewer is `stakeholder`, the orchestrator presents the fix to the stakeholder in its session and sets `confirmed` or `rejected` itself. When `reviewed_by:` names an agent and `stakeholder`, the agent reviews first, and the stakeholder sees the fix only after the agent confirmed it. A `rejected` row becomes a `BUG` finding with `owner: developer-agent`. The orchestrator reads `rulebooks/core-artifacts.yaml` under the Factory root to tell a row on an artifact of the core list from the others, as `dispatch close-wave` does. A `fixed` row on an artifact outside the core list closes at `fixed`, because the artifact has no declared review (DEC-35). The owner and the reviewer commit on the branch that holds the reconciliation report, normally the feature branch before its merge into `dev` (stakeholder, 2026-11-05). A row stays in the report that first wrote it for its whole life, and only that row changes status. A later run checks the row against the code but does not repeat it in its own report. It writes a new row only when the drift of a closed row appears again: a `confirmed` row, or a `fixed` row on an artifact outside the core list. For a row that is still `open`, or `fixed` on an artifact of the core list, it records nothing, because the backfeed step still waits on that row (stakeholder, 2026-11-05). The playbook is done only when no row of any reconciliation report is `open`, or `fixed` on an artifact of the core list. No script reads the reconciliation reports, so an unhandled row blocks no merge and no reconciliation run (CAO-G32).

## Counter IDs (`next-id`, BR-068…BR-078)

These rules hold the claim and the seed of
[counter-ids.feature](features/counter-ids.feature). `next-id` checks BR-068
and BR-069 before it contacts the remote. BR-076 bounds every git call of a claim. BR-077 and BR-078 keep a token out of every message. The remote enforces the leases of
BR-072 and BR-073. A case the proposal leaves open carries the identifier of
its gap in [counter-ids-gaps.md](work/counter-ids-gaps.md).

- **BR-068**: The prefix list in `next-id` holds exactly `ST`, `BUG`, `SPEC`, `FAGAN`, `SEC`, `RECON`, `ATAM`, `IMPL`, `T`, `ADR`, `ARCH`, and `QA`. A claim for any other prefix, such as `XX`, `PROP`, or `RETRO`, fails and names the prefix and the list (DEC-09, DEC-25).
- **BR-069**: `next-id --seed` takes one `<number>` and any number of `<PREFIX>=<n>` pairs. `<number>` and every `<n>` are whole numbers from 0 to 9998, so the first claim of every prefix stays at or below `9999`. Every `<PREFIX>` is in the list of BR-068, and each prefix has at most one pair. A wrong argument fails before the remote is contacted and creates no ref. The message names the argument, such as `10000`, `abc`, or `ST=x`. For a prefix outside the list, it names the prefix and the list. For a second pair of one prefix, such as `ST=5 ST=7`, it names the prefix.
- **BR-070**: Every ID has the form `<PREFIX>-<NNNN>`, with the number padded to four digits, so `backlog-lint` and the other ID parsers accept it. `seed` writes every number in the claim commit as four digits, so `ADR=6` becomes `ADR=0006`. A claim on a line that holds `9999` has no defined result (CID-G04). BR-069 keeps a seed from writing `9999`, so only claims can reach it.
- **BR-071**: A claim raises the line of its prefix by one. A prefix without a line gets `start` plus one (DEC-17). The claim keeps every other line and writes a new token. A claim commit without a `start` line, or with a line that is not a number, has no defined result (CID-G05).
- **BR-072**: A claim pushes with the lease `--force-with-lease=refs/ids/counters:<old sha>`. Only a stale lease leads to a retry, after a random wait of 0.1 to 1 second. After ten stale leases in a row, the claim fails and names the prefix and the last number it tried (DEC-15). Any other refusal fails after one push, with git's message (DEC-23). `next-id` runs git with `LC_ALL=C`, so the stale-lease check reads git's English messages.
- **BR-073**: A seed pushes with the create-only lease `--force-with-lease=refs/ids/counters:`. When the ref exists, the seed fails without a retry and leaves the ref unchanged. So two seeds at once leave exactly one claim commit (DEC-17).
- **BR-074**: `next-id` claims on the URL of `--remote <url>`, or else on the URL that `git remote get-url origin` prints, so the clone's URL rewrites apply. Without either, it fails and names `origin` and `--remote`. BR-096 puts the git setting `agent-factory.counterRemote` between `--remote` and `origin`, so a project without `origin` claims from a local counter.
- **BR-075**: A claim runs in a throwaway bare repository, made with `git init --bare --template=` in a new temporary directory and deleted at exit. The clone gains no ref and no object (DEC-19). When the clone's own repository holds the local counter of BR-096, the push of the claim commit is the one write to it. Every claim commit carries the author and committer `next-id <next-id@agent-factory.invalid>`, so a clone without `user.name` can claim (DEC-23).
- **BR-076**: A claim runs every git call without a prompt: with `GIT_TERMINAL_PROMPT=0`, so git asks no user name or password on the terminal, and with `GIT_SSH_COMMAND` set to the ssh command git would run (`GIT_SSH_COMMAND`, else `core.sshCommand`, else `ssh`) followed by ` -o BatchMode=yes`, so ssh asks no passphrase. The claim keeps the user's own ssh command and adds only the option (DEC-23). Missing credentials then make git fail with its own message. `next-id` stops any git call of a claim that runs longer than 30 seconds. The claim fails, prints no ID, and names the remote and the time limit. So ten stale leases in a row end a claim after at most twenty git calls of 30 seconds each and nine waits. `next-id --seed` keeps git's prompts and has no time limit, because a person runs it and can answer a prompt (ATAM-0012).
- **BR-077**: `next-id` and `init-factory` send every line on standard output and standard error through one redaction. The redaction replaces the user info of a URL with a scheme, such as `user:token@` in `https://user:token@host/r.git`, with `***`, so the URL shows as `https://***@host/r.git`. The match runs to the last `@` before the path, so a password with an `@` goes too. An scp-style URL, such as `git@host:group/project.git`, has no scheme and stays as it is. The redaction runs in the script, so an AI process never sees a token in the clear. The git calls get the URL unchanged (SEC-0007).
- **BR-078**: When the URL of `origin` carries user info, `init-factory` warns that the URL carries a user name or token and shows only the redacted URL. The warning advises a git credential helper in place of the credential in the URL. The counter check then goes on, and `init-factory` finishes the install (SEC-0007).

## Finding classification (BR-079…BR-095)

These rules hold the classification, the stop, and the guard of
[finding-classification.feature](features/finding-classification.feature).
`finding-lint` checks BR-079 to BR-090, BR-109, and BR-110. `dispatch` and `premerge-check` check
BR-091, and the hook `guard-human-fields` checks BR-092. The review agents and
the orchestrator follow BR-093 to BR-095. The rulebook
`packages/factory/rulebooks/conventions/finding-classification.md` explains
each rule with examples. A decision of the proposal carries its identifier, and
a decision of the stakeholder on a gap carries the identifier in
[finding-classification-gaps.md](work/finding-classification-gaps.md).

### Values of a finding

- **BR-079**: `review_class` is `document`, `code`, `security`, `architecture`, or `runtime`. The reviewed material decides the class, for a review and for any other source, such as a diagnosis (DEC-17, DEC-37). Text that agents execute is code: playbooks, skills, agent definitions, rulebooks, and hook configuration. `category` is `defect`, `risk`, or `suggestion`, and `risk` belongs to the architecture class only (FC-C08). `type` comes from the vocabulary of the class:

  | Class        | Types                                                                                                                                                                                   |
  | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | document     | `incorrect`, `ambiguous`, `incomplete`, `inconsistent`, `unverifiable`, `infeasible`, `untraced`, `unnecessary`, `compound`, `code-defect`, `spec-stale`, `undocumented`, `speculative` |
  | code         | `function`, `interface`, `checking`, `assignment`, `timing`, `algorithm`, `build`, `documentation`, `structure`, `test`                                                                 |
  | security     | an OWASP Top 10 category from `A01` to `A10`, such as `A06`                                                                                                                             |
  | architecture | `risk`, `non-risk`, `sensitivity-point`, `tradeoff-point`                                                                                                                               |
  | runtime      | `crash`, `hang`, `wrong-result`, `data-loss`, `security`, `performance`, `usability`, `cosmetic`                                                                                        |

  In the document and code classes, the type names the change that the `**Fix:**` line demands, not a guess about the cause (DEC-09). A CWE identifier of a security finding goes into its `**What is wrong:**` line, because the proposal names no field for it.

- **BR-080**: `basis` has the shape of its class, as [schemas/finding-basis.json](schemas/finding-basis.json) defines. The document, code, and runtime classes record `in_use`, `harms_downstream`, `fails_purpose`, and `raises_cost`. The security class records `effect`, `second_breach`, `trusted_access`, `non_default`, `user_action`, `confidence`, and `in_use`. The architecture class records `importance`, `exposure`, and `in_use`. The reviewer agent records every field, also after the first "yes".

### Severity rules

- **BR-081**: The consequence tree computes the severity of a document, code, or runtime finding. `harms_downstream` true gives `critical`. Otherwise `fails_purpose` true gives `major`. Otherwise `raises_cost` true gives `minor`. Three false answers give `note`. `harms_downstream` is true only when `in_use` is true.
- **BR-082**: The bug bar computes the severity of a security finding. The effect class sets the starting level: `execution` and `secrets` start at Critical; `gate-bypass`, `tampering`, and `disclosure` at High; `limited` at Medium; and `leak` at Low. Each of the four preconditions answered true lowers the level one step, and the level never falls below Low. Critical becomes `critical` only when `in_use` is true and `confidence` is `proven`; otherwise Critical becomes `major`. High and Medium become `major`, and Low becomes `minor`. `rating` holds the level as `Critical`, `High`, `Medium`, or `Low`. The effect `hardening` has no level: the finding is a `suggestion` of severity `note`, and `rating` is null. An attack that needs the capability it gains is no finding (DEC-20).
- **BR-083**: The matrix computes the severity of an architecture `risk`. Importance `high` gives `major` for both exposures. Importance `medium` gives `major` for `fails` and `minor` for `uncertain`. Importance `low` gives `minor` for `fails` and `note` for `uncertain`. `in_use` true raises `major` to `critical` and changes no other level (DEC-18). Priority 1 in arc42 § 10.2 is `high`, and priority 2 is `medium` (DEC-19). A finding of type `non-risk`, `sensitivity-point`, or `tradeoff-point` is a `note`, and a non-risk names its assumptions.
- **BR-084**: A `suggestion` describes material that works. So a suggestion of the document, code, or runtime class answers false to `harms_downstream` and `fails_purpose`, and `finding-lint` rejects a suggestion of these classes with either answer true. Its severity is then `minor` or `note`, and a `minor` suggestion gives its "no" to `fails_purpose` as BR-087 requires. A suggestion of the security or architecture class is at most `minor`: when the rule of its class gives `critical` or `major`, the severity is `minor`. A Conventional Comments label `nitpick` gives `note`. The label is not recorded, so `finding-lint` does not check it.
- **BR-085**: A finding is blocking when its category is `defect` or `risk` and its severity is `critical` or `major` (DEC-03). A `critical` or `major` finding becomes a finding file `docs/findings/<ID>.md`. A `minor` finding becomes one register file in the register of its class and never a finding file. A `note` stays in the review report. A `question` becomes an entry in `docs/spec/work/todo.md` only, so no finding file and no register file carries the category `question` (DEC-41). An observation that names no artifact is no finding. It becomes an action item of its retrospective or a `todo.md` entry (DEC-37). Every finding takes its ID from `next-id`, as a finding file and as a register file (DEC-32).

### Finding file and register file

- **BR-086**: A finding file holds the line `**Why this severity:**` in its body. It holds `## Possible damage` exactly when its severity is `critical`, with at least one item and a check for each item. A set `stop_confirmed_by` comes with a non-empty `stop_confirmed_reason`, and only on a `critical` finding. A finding file with `status: waived` has a non-empty `override_by` and `override_reason`, and its severity is `critical` or `major`. A waived `minor` finding is a register file (BR-110). A waived `critical` finding also has a non-empty `stop_confirmed_by` and `stop_confirmed_reason` (DEC-47). `artifact` has the form `path:line`, `path:start-end`, or `path#anchor`. An agent sets `status` to `open` or `resolved`. Only the stakeholder sets `waived` (BR-092), also to set a blocking finding aside. Only the migration sets `deferred`, on a file without `review_class` (BR-095). So `finding-lint` rejects `deferred` on a file that carries `review_class` (DEC-55). Any other status value fails. A finding file with `status: open` has the severity `critical` or `major`, because a `minor` finding is a register file and a `note` stays in the review report, except the `note` results of the migration (BR-095, DEC-53). A `critical` finding gets `status: resolved` only when `stop_confirmed_by` and `stop_confirmed_reason` both hold text, so the damage checks run before the stop ends (DEC-52). A finding file that carries `review_class` and whose frontmatter `finding-lint` cannot read fails with the rule name `frontmatter`, and the lint runs no other check on that file. An unreadable frontmatter is an unclosed `---` block, a line that is no key and value, an unclosed quote or flow list, or a value type outside the supported subset.
- **BR-087**: A `minor` finding of the document, code, or runtime class gives the reason for its "no" to `fails_purpose` in its `**Why this severity:**` sentence (DEC-27). The sentence marks that reason with the text `no to fails_purpose`, as in "a reader can still act (no to fails_purpose)". The marker makes the check mechanical (DEC-53). A `minor` security or architecture finding needs no such sentence. Its sentence names the preconditions, or the importance and the exposure (FC-G02).
- **BR-088**: `finding-lint` checks `in_use` against git for a finding of the code, runtime, or security class (DEC-21, DEC-31). It checks only a finding file or a register file that does not exist at `HEAD`, or whose `basis` or `artifact` differs from its `HEAD` version (DEC-60). A register file that the migration writes from a line of an old `.jsonl` register counts as unchanged when the `HEAD` version of that register holds a line with the same `id`, `basis`, and `artifact` (FC-C25). With `--staged`, as in the pre-commit hook, it reads the staged version; without it, as in `validate`, the working tree (DEC-43, DEC-46). When every line of the `artifact` range exists unchanged in one place, `in_use` must be true. The places are the branches `dev` and `main`, the remote-tracking branches `origin/dev` and `origin/main`, each release tag (BR-089), and the installed copy (DEC-50). A branch that the clone does not have is skipped, and the output names it. A line has its line identity: the commit that introduced it, its line number in that commit, and its file name in that commit, as `git blame -M -C --porcelain` reports them. Two lines are the same line when all three values match, so two lines of different files never match. On each place, the lint blames the `artifact` path, and also each rename or copy source that `git diff -M -C <place> <reviewed branch>` names for that path. It does not blame the file name of the porcelain output, because that names the path at the line's first commit, which may no longer exist (DEC-49). The installed copy is `.agent-factory/factory/`, checked against `packages/factory/` with `git blame --contents`. In a linked worktree, the lint finds it in the primary checkout through `packages/factory/scripts/_main_checkout.py`, because git ignores `.agent-factory/` and only the primary checkout holds it (DEC-49). A line of the installed copy that no commit introduced does not count as unchanged. An artifact whose range cannot be read passes the check, because no lines exist to compare. This covers a file that is missing or untracked at `HEAD`, a file with fewer lines than the range needs, and a `path#anchor` whose heading is not in the file. BR-086 checks only the form of the `artifact`, so the reviewer's answer stands in these cases. A project without `packages/factory/` skips the installed copy. The range of a `path#anchor` artifact is the heading line and every line below it down to the next heading of the same or a higher level. The git check sets a lower bound only: `in_use` true always passes it. Document and architecture findings skip the git check, and their `**Why this severity:**` line names the story or code that encodes the statement or the decision.
- **BR-089**: A git tag counts as a release tag when `git tag --list '<pattern>'` lists it for one pattern of `release_tag_patterns` in `docs/factory-settings.yaml` (DEC-48, FC-C11). An empty list `[]` counts no tag. When a git check is due and the file or the key is missing, `finding-lint` exits `1` and names the file and the key. It does not guess. When no git check is due, the lint does not read the file (FC-C15). The lint reads the working-tree version of the file, with `--staged` as well. The file configures the check and is not part of the finding under check, so `--staged` does not extend its promise of the commit's content (BR-088, DEC-46) to it. The tags it selects come from `git tag --list`, which no commit's content decides. The Factory sets no default, and neither `init-factory` nor `update-factory` writes the file.
- **BR-090**: The register of a class is the folder `docs/findings/register/<class>/`. Each `minor` finding is one register file `docs/findings/register/<class>/<ID>.json` that holds one JSON object with the severity `minor` (DEC-60). The folder name equals the `review_class` of the object, and the file name equals its `id` with the extension `.json`. `finding-lint` checks each register file against that schema with the validator of `schema-validate`, which it loads from the same folder and runs in its own process, and it computes the severity again. The schema is `rulebooks/schemas/finding-register-<class>.schema.json` under the Factory root that `finding-lint` runs from: `packages/factory/` in this repository and `.agent-factory/factory/` in an installed project. Two reviews on two branches add two different files, so git merges them without a conflict and without a merge driver. An ID names either a finding file `docs/findings/<ID>.md` or a register file, never both, and at most one register file. `finding-lint` fails on an ID that breaks this (DEC-53). It counts a finding file only when the file carries `review_class`, because it skips every other finding file (BR-095 classifies those at the migration). A register file that is not valid JSON fails with the rule name `BR-090 register file`, and the lint checks that file no further. The pause point shows each new register file with its `**Why this severity:**` sentence before any file is written. The final summary of a headless run lists each new register file in the same way (DEC-22).
- **BR-110**: The `status` of a register file is `open`, `resolved`, or `waived`, and any other value fails (DEC-60, DEC-63). The reviewer agent writes `open` when it records the finding, and so do the migration (BR-095) and the stakeholder who lowers a filed finding (BR-109). The commit that fixes the finding sets `resolved`, and the file may stay as the record. Only the stakeholder sets `waived` (BR-092), when nobody will fix the `minor` finding and it is accepted as is. A waived register file holds text in `override_by` and `override_reason`, as a waived finding file does (DEC-44). A register file is never `deferred`, because only the migration sets `deferred`, on a finding file without `review_class` (DEC-55). An `open` register file that `HEAD` holds is removed only when a finding file with the same ID replaces it (DEC-65). A register file whose `HEAD` status is `resolved` or `waived` may be removed, and the lint passes that. To raise a registered finding, an agent or the stakeholder changes an answer of its basis, removes the register file, and files a finding file under the same ID (FC-G04, DEC-56). `finding-lint` compares the working tree, or the staged version with `--staged`, with `HEAD`, as BR-088 does. The replacing finding file carries `review_class`, because a finding file without it is skipped and replaces nothing. An `open` register file does not move to the folder of another class: the lint sees the old path as removed, and no finding file replaces it. To change the class of a registered finding, follow the raise above. `finding-lint` rejects a removed `open` register file without such a finding file of the same ID and names the ID and the rule.
- **BR-109**: Only the stakeholder lowers a filed finding (DEC-56). `finding-lint` compares each finding file whose `HEAD` version carries `review_class` with that version. It reads the staged version with `--staged` and the working tree without it, as BR-088 does. A version of such a file keeps the `review_class` of its `HEAD` version: the lint rejects a working-tree or staged version that lacks the field or holds another value. So BR-086 checks every file that `HEAD` holds with `review_class`, and an agent cannot end a stop (BR-091) or set `deferred` by deleting the field. A finding is lowered when its severity falls below its `HEAD` severity, or when its file is removed and a register file with the same ID appears (DEC-60). A lowered finding file holds a non-empty `override_by` and `override_reason`. A register file that replaces a finding file holds the keys `override_by` and `override_reason`, both non-empty, and the status `open`. An `open` finding file is removed only by that lowering: the lint rejects its removal unless a register file with the same ID and both override keys replaces it (DEC-65). A finding file whose `HEAD` version has status `resolved` or `waived` may be removed, and the lint passes that. So a filed finding has no path down to a `note`, and the stakeholder sets it aside with `waived` instead (BR-086). A finding whose `HEAD` version has severity `critical` is lowered only when that `HEAD` version holds text in `stop_confirmed_by` and `stop_confirmed_reason`. So the stakeholder confirms the stop in one commit and lowers the finding in a later one, and a lowering never ends a stop (BR-091). A file lowered from `critical` to `major` drops the two confirmation fields, because BR-086 allows them only on a `critical` finding. When a rule of this paragraph fails, the lint exits `1` and names the ID and the rule. A raise needs neither override field, so an agent may raise a finding for the stakeholder (FC-G04). A file whose `HEAD` version carries no `review_class` is not compared, so the migration moves a `minor` result into a register file after the stakeholder's pause point without these fields (BR-095).

### Stop and guard

- **BR-091**: A stop holds while a finding in `docs/findings/*.md` is critical and unconfirmed (DEC-28, DEC-52, FC-G06). `dispatch` and `premerge-check` read each finding file in the working tree and its `HEAD` version. A finding is critical when its working-tree version or its `HEAD` version has `severity: critical` together with `status: open` or a `review_class` field. A finding is confirmed when its working-tree version or its `HEAD` version holds text in both `stop_confirmed_by` and `stop_confirmed_reason`. Only the stakeholder writes these two fields (BR-092), so only the stakeholder's confirmation ends a stop. A status change, a lower severity, or a removed file in the working tree does not end it, and `finding-lint` rejects a status change, a lower severity, or the removal of an `open` file with `review_class` at the commit (BR-086, BR-109). A `resolved` or `waived` `critical` file already holds both confirmation fields (BR-086), so removing it ends no stop. A `critical` file without `review_class` that is not `open`, such as the resolved BUG-0037, stops no run. During a stop, `dispatch` refuses `init`, `prepare-wave`, `prepare-story`, `add`, `mark-dispatching`, `mark-dispatched`, `re-dispatch`, `escalate`, `refresh-story`, `merge-story`, and `close-wave`. It still runs `status`, `plan`, `suggest-merge-args`, `verify-story`, `mark-blocked`, `mark-failed`, and `clear-manifest` (FC-C12). It also runs `return-story`, `close`, `close --drop`, and `close --orphans`, because they start and merge no work. `add` starts new work in a new wave, so the stop refuses it (RL-G18). `premerge-check` refuses every run, runs no other check, and writes no `premerge-check-ok` marker, so `block-dangerous-git` denies the merge. `block-dangerous-git` also checks the stop itself, so a marker from before the stop lets no merge through. A refusing script changes no file, prints the stop notice, and exits `1`. Once every stopping finding is confirmed, both scripts run again. A confirmed finding keeps severity `critical` and loops like a `major` one. In an interactive session, the orchestrator explains each stopping finding with `explain-review-finding`. A headless run ends without waiting, and its final summary carries the stop notice.
- **BR-092**: Only the stakeholder writes a human field: a non-null `override_by`, `override_reason`, `stop_confirmed_by`, or `stop_confirmed_reason`, the status `waived` in a finding file or a register file, or `waived` in the Status cell of a proposal review row (DEC-42, DEC-45). The hook `guard-human-fields` runs in every supported CLI: Claude Code, Codex, Copilot CLI, Pi, and OpenCode (DEC-51). Each CLI registers it on its own hook events for edit, write, and shell calls, as the [guard contract](interface-contracts.md#packagesfactoryconfighooksguard-human-fields) lists (DEC-61). It refuses an agent's edit, write, or shell call that sets such a value in `docs/findings/*.md`, in a register file `docs/findings/register/**/*.json` (BR-109), or in the Appendix tables of `docs/proposals/*.md`. "Sets" means that the value appears and was not there before. For an edit, the hook compares the old text with the new text, such as `old_string` with `new_string` of a Claude Code `Edit`, or the removed with the added lines of a patch call: `apply_patch` in Codex, Copilot CLI, and Pi, and `patch` in OpenCode. In every CLI, the hook refuses a patch call that it cannot parse when the raw patch text names a guarded path (DEC-61). For a write, it compares the new content with the current file. For a shell call, it checks only a command that writes into a guarded path, such as a redirect, `sed -i`, or `tee`, and refuses it when the command text assigns such a value. A command text does not show which cell of a proposal it writes. So for a shell call that writes into `docs/proposals/*.md`, the hook refuses every command whose text holds the word `waived`, and the agent makes such a change with an edit or a write instead. It checks the JavaScript of an OpenCode `execute` call in the same way as the text of a shell call. In Pi and OpenCode, the extension or the plugin blocks the call when the guard script is missing (DEC-61). The stakeholder writes the fields in an editor or with a `!` command, which runs outside the tool hooks. An agent that hides the field name gets past the hook. That case is deferred to [gate-evidence.md](../proposals/gate-evidence.md) (DEC-42).

### Counts, proposal rows, and migration

- **BR-093**: `finding_counts` of every [child-result envelope](interface-contracts.md#child-result-envelope) carries the four keys `critical`, `major`, `minor`, and `note`, each a whole number of zero or more. A key with zero findings stays in the envelope. `adversarial-review` counts a BLOCKER under `major`, and MAJOR, MINOR, and NOTE under their namesakes. It counts nothing under `critical` (DEC-36).
- **BR-094**: The proposal-review agent rates each Appendix row with two questions. `fails_purpose` is true when a planner would have to ask the author or would cut a wrong story, and it gives `major`. Otherwise `raises_cost` is true when the planner can act but a reader pays later, and it gives `minor`. Two false answers give `note`. A row is never `critical`. The Finding cell ends with one sentence that starts with `Severity:` and names the deciding answer. An open `major` row blocks the transition to `accepted`: the proposal-review agent returns the disposition `findings`. `minor` and `note` rows stay in the table and enter no register. Only the stakeholder sets a `major` row to `waived`, with the reason in its Resolution cell. The consultative pass writes only `note` rows. `finding-lint` does not read proposals (DEC-38).
- **BR-095**: The one-time migration covers every open finding file without `review_class` when it runs, not only the 39 the proposal counted (FC-G01). The migration agent classifies each one, rewrites `artifact` to the range or heading where its fix goes, and fills `## Possible damage` for each `critical` result (DEC-40, DEC-35). The stakeholder reviews every result at one pause point before any file changes, and confirms the stop of each `critical` result there. After the pause point, a `minor` result becomes a register file with `status: open` under its old ID, and its finding file is removed (DEC-60). The old file carries no `review_class` at `HEAD`, so BR-109 does not compare it, and the register file needs no override keys. The migration also moves each line of the old registers `docs/findings/register/architecture.jsonl`, `code.jsonl`, and `document.jsonl` into one register file under the line's ID, adds `status: open`, and removes the three files (DEC-60). A result without an artifact becomes a `todo.md` entry, and its file gets `status: deferred` with the todo ID in its body. No other step sets `deferred` (DEC-55). That file carries no `review_class`, so `finding-lint` skips it. A finding that is not `open` stays unchanged (DEC-24). Two exceptions hold. A `note` result of the migration stays a finding file with `status: resolved` and its classification, as a one-time exception to the rule of BR-086 that a `note` stays in the review report. A finding that already carries `review_class` and fails `finding-lint` is corrected at the pause point, by the stakeholder's decision, and its status stays. The stakeholder raised the resolved BUG-0116 to `critical` this way, because BR-081 computes `critical` from its basis.

## Counter IDs fitting (BR-096…BR-108)

These rules hold the seed step, the local counter, and the ID producers of
[counter-ids-fitting.feature](features/counter-ids-fitting.feature). They
continue the rules of [§ Counter IDs](#counter-ids-next-id-br-068br-078).
`next-id` checks BR-096 to BR-103. VIRGIL follows BR-104 and BR-106, and
`init-factory` follows BR-105. The text test for ID producers checks BR-107
and BR-108. A decision of the proposal
[counter-ids-fitting.md](../proposals/counter-ids-fitting.md) carries its
identifier. A case the proposal leaves open carries the identifier of its gap
in [counter-ids-fitting-gaps.md](work/counter-ids-fitting-gaps.md).

### Remote and local counter

- **BR-096**: `next-id` resolves its remote in this order: the `--remote` URL, then the git setting `agent-factory.counterRemote`, then the URL that `git remote get-url origin` prints (DEC-08). The order holds for an ID claim, a seed, and `--plan-seed`. Without all three, `next-id` fails and names `origin` and `--remote`. The setting holds the absolute path of the project's main repository: the parent of the directory that `git rev-parse --git-common-dir` prints. So a local counter is `refs/ids/counters` in that repository's `.git`, and every worktree and local clone of the project claims from it (DEC-05).
- **BR-097**: A marker commit is a commit at `refs/ids/counters` whose message is the one line `moved=<remote>`, with the remote redacted by BR-077. An ID claim or a `--plan-seed` that reads a marker commit fails, prints nothing on standard output, and names the remote of the marker as the remote that holds the counter. The message never mentions `--seed`, so no clone starts a second counter.

### `next-id --plan-seed`

- **BR-098**: `next-id --plan-seed` changes no ref and no file in the clone or on the remote (DEC-07). It checks the remote as an ID claim does before it counts. When the remote holds a claim commit at `refs/ids/counters`, it prints that the counter is in use on that remote, prints no seed command, and exits `0`. A missing or unreachable remote fails with the messages of an ID claim, and a marker commit fails by BR-097.
- **BR-099**: `--plan-seed` counts an ID as in use only from four sources, on every local branch and every remote-tracking branch: a file name `backlog/ST-NNNN.md`, `docs/findings/<PREFIX>-NNNN.md`, or `docs/adr/NNNN-*.md` for `ADR`; the file name of a register file `docs/findings/register/<class>/<PREFIX>-NNNN.json`, in any subfolder of the register folder; the `id` field of each line in `docs/findings/register/*.jsonl`; and a heading `## T-NNNN` in `docs/spec/work/todo.md`. It never reads body text, also not the body of a register file, because body text holds examples such as `ST-9999`. The working tree of the current worktree counts too, so a file that no commit holds yet raises the seed (CIFP-C05 in [epics-counter-ids-fitting.md](../../backlog/epics-counter-ids-fitting.md)).
- **BR-100**: A file name counts when it starts with a prefix of BR-068, a hyphen, and digits, and its number is those digits. So `ST-0380A.md` counts as 380, and `SPEC-011-title.md` counts as 11. A name without digits after the hyphen, such as `BUG-HUNT.md`, does not count. For each counted name that breaks both `<PREFIX>-NNNN.md` and `<PREFIX>-NNNN<letter>.md`, `--plan-seed` prints a warning that names the path, and it goes on. An old name therefore never blocks the seed and never lowers it unnoticed (DEC-12).
- **BR-101**: `--plan-seed` prints one command, `next-id --seed 0 <PREFIX>=<highest> …`, with one pair for each prefix that has an ID in use. `<highest>` is the highest number in use, not the count, so a gap in a sequence does not lower the pair. A prefix without an ID in use gets no pair and starts at `0001` after the seed. A project without an indexed artifact gets `next-id --seed 0` (DEC-04). The pairs follow the order of the prefix list in `next-id` (CIFP-C06).

### `next-id --move-to-origin`

- **BR-102**: `next-id --move-to-origin` moves the local counter that `agent-factory.counterRemote` names to `origin` in four steps (DEC-09). It reads the claim commit C of the local counter. It replaces the local `refs/ids/counters` with a marker commit, with a lease on C. A stale lease starts the move again at the read, after a random wait of 0.1 to 1 second. After ten stale leases in a row, the move fails, sets no marker, keeps the setting, and names the ten stale leases. It pushes C to `refs/ids/counters` on `origin` with the create-only lease `--force-with-lease=refs/ids/counters:`. When the push succeeds, it removes `agent-factory.counterRemote`. The push runs from a throwaway repository that fetches the local counter, so no hook of the project runs (BR-075). When the push is refused, the move asks `origin` again with `git ls-remote`. When `origin` then holds C, the move removes the setting and succeeds. Otherwise the local counter keeps the marker, the setting stays, and the move exits non-zero. The message names both counters when `origin` holds another counter (DEC-05), and holds git's message otherwise. The move never puts C back, on a first move as on a resume, so a counter seeded on `origin` meanwhile never repeats a number of the local counter (DEC-16). The marker commit has C as its parent, so C stays reachable (DEC-14). A move that was cut off after the marker leaves the marker in place and the setting set, and every ID claim fails by BR-097. A second `next-id --move-to-origin` that reads a marker commit at the local counter takes C from the marker's parent, and asks `origin` with `git ls-remote` for `refs/ids/counters`. When `origin` holds no counter, it goes on at the push. When `origin` already holds C, the push was done, and the move only removes the setting. When `origin` holds a claim commit other than C, the move cannot tell whether that counter grew from C, because a claim commit has no parent. It treats the case as a collision: it names both counters, changes nothing, and exits non-zero. The local counter keeps the marker, and the setting stays. So an interrupted move loses no claimed number and needs no seed. Gap CIF-G08 asks for the exit codes.
- **BR-103**: No ID goes out twice while ID claims run during the move. A claim that lands on the local counter before the marker makes the lease on C stale, so the move reads the counter again and carries the new number to `origin`. A claim that reads the counter after the marker fails by BR-097 and claims nothing.

### Fitting step and fitting key

- **BR-104**: The fitting in `packages/factory/agents/virgil.md` holds step 4, "Seed the ID counter", directly after step 3, "Decide on hooks", because a seed is a push (DEC-01). Without `origin`, VIRGIL first sets `agent-factory.counterRemote` by BR-096. VIRGIL then runs `next-id --plan-seed`, shows the seed command, and says that it creates `refs/ids/counters` on the counter's remote once and that every later ID continues from it. VIRGIL runs the command only after the User confirms it, and then sets `fitting.counter_seeded` to `true` (DEC-03). When the User declines or the remote is unreachable, VIRGIL runs no seed, names the reason, and leaves the key `false`. When the counter is in use, VIRGIL runs no seed and sets the key `true`. A greenfield project walks step 0 and this step (DEC-06). `fitting.status` becomes `fitted` only when all six fitting keys are `true`.
- **BR-105**: `init-factory` derives `fitting.counter_seeded` on every run from the remote that `next-id` would use without `--remote`: `agent-factory.counterRemote`, then `origin`. The key is `true` when that remote holds `refs/ids/counters`, checked with `git ls-remote`, and `false` when it does not or when neither remote exists. An unreachable remote leaves the key as it is. `init-factory` changes no ref. A greenfield project follows the same rule (gap CIF-G07).
- **BR-106**: At the session start, VIRGIL offers the move when `agent-factory.counterRemote` is set and `origin` exists. VIRGIL runs `next-id --move-to-origin` only after the User confirms. On a counter on `origin`, VIRGIL reports that two counters exist and names both. Gap CIF-G04 asks which file holds the check, and gap CIF-G03 asks how a human resolves the collision.

### ID producers and the prefix table

- **BR-107**: An ID producer names the literal call `next-id <PREFIX>` at each step that creates an indexed artifact, with the prefix of that artifact's kind (DEC-02, DEC-10). A file that creates two kinds names one prefix at each of the two steps. No ID producer holds the text `next-id <TAG>`. A file that points to `todo-format.md` at a step that adds an entry to `docs/spec/work/todo.md` is an ID producer of `T` and names `next-id T` at that step. A file that only links to `todo.md` is no ID producer.
- **BR-108**: `packages/factory/rulebooks/conventions/id-prefixes.md` holds one table row for each prefix of BR-068, with the kind of artifact and the ID producer files of the prefix (DEC-11). `rules.md`, `branching-policy.md`, and `finding-format.md` point to it. `finding-format.md` keeps one row per finding tag with the review that files it, and holds a row for `RECON`. The text test for ID producers fails and names the file and the prefix when an ID producer drops its prefix. It fails and names the file when a `T` producer does not name `next-id T`. It fails and names the prefix when the table and the list in `next-id` differ.
