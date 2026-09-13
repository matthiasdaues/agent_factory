# Validation Rules — Factory Flow Control

Field- and behavior-level rules each mechanism enforces, grouped by the entity or mechanism they govern. Business rule IDs (BR-###) are defined here or in the use case that introduces them; this file is the canonical index.

## Marker schema (`PLAYBOOK_STATE_MARKER`)

- `playbook` and `state` are required. `phase advance` and `phase retry` both refuse (non-zero exit) if either is missing from an existing marker file.
- `state` must name a state defined in the resolved FSM. `transition-lint` reports `TL-STATE` (error) if it does not; `phase advance` and `phase retry` fail resolving the current state's transitions in the same case.
- `recorded_at` is written in UTC, `%Y-%m-%dT%H:%M:%SZ` format, always from the writing script's own `datetime.now(timezone.utc)` call — never accepted as an input field.
- `iteration` is an integer, defaulting to `1` when absent or unparseable. `phase advance` always resets it to `1` on a successful advance; `phase retry` is the only mechanism that increments it.
- The marker is rendered as flat `key: value` lines in a fixed field order (`playbook`, `state`, `gate`, `result`, `open_findings`, `next`, `iteration`, `recorded_by`, `recorded_at`); a value of `None` renders as the literal `null`.
- The marker file lives at `.current-work/playbook-state.yml` and is git-ignored — local, single-machine state, never committed, never a distributed lock (see [PRD § Constraints](../prd.md#5-constraints)).

## Entry conditions (`GATE_CONDITION`)

- `file_exists`: satisfied if `repo_root.glob(path)` yields at least one match.
- `files_exist`: satisfied if every path in `paths` yields at least one glob match; the unmet reason lists every missing path by name.
- `no_open_findings`: satisfied if zero matching finding files (by `pattern` or `patterns`, globbed under `docs/findings/`) have frontmatter `status: open`. A file whose frontmatter cannot be parsed (no leading `---` block) is not counted as open.
- `script_exit_zero`: executes the named script and checks for exit code 0. When the `script` field uses the `charter:<field>` notation (e.g. `charter:test_command`), the evaluator reads the `charter_file` path from the condition, parses the YAML, and resolves the named field to the actual command before execution. Blocks with a clear message when the charter file is absent or the field is missing. See [UC-09](../../~archive/spec/use_cases/UC-09-run-tests-via-hook.md) and [ADR-0003](../../adr/0003-test-execution-via-hooks.md).
- An `entry_conditions` name with no matching entry in `gate_conditions` is treated as unmet, with the reason `"<name> (not defined in gate_conditions)"`.
- Unmet conditions are collected exhaustively, not short-circuited — a refusal always lists every unmet condition, not just the first.

## Glob matching (`outputs:` ownership)

- `*` matches within one path segment; `**` matches across segments (`**/` also consumes a trailing `/`); `?` matches exactly one non-separator character. Every other character is matched literally.
- A staged (or on-disk) path can match more than one state's globs; `transition-lint` reports the sorted list of matches and treats the first as the file's owner for messaging purposes.
- A path matching no state's `outputs:` glob is ungoverned: `transition-lint` never reports a finding for it, and `run-step` never treats it as evidence a state's outputs exist.

## Iteration cap resolution (BR-008, BR-009, BR-010)

1. Resolve the loop-back target: the current state's `else` transition target, if the FSM declares one; otherwise the current state itself.
2. Look up a `halt_conditions` entry of `type: max_iterations` naming that target state. If found, its `limit` (falling back to the default if unparseable) and `message` apply.
3. If no such entry exists, `--default-max-iterations` (default `5`) applies, with no escalation message.
4. Increment the marker's `iteration`. If the result exceeds the resolved limit, refuse (exit `2`) and leave the marker unwritten. Otherwise write the marker with the new `iteration` and a fresh `recorded_at`.

This resolution order is why `halt_conditions` must name the **author** state being retried (e.g. `PHASE_1_REQUIREMENTS`), not its gate (`PHASE_1_GATE`) — `greenfield-development.fsm.yml` declares all three review-loop caps this way.

## Permission scoping (`trigger`, BR-011, BR-012, BR-013)

- **Never** a blanket bypass: `--dangerously-skip-permissions` (Claude Code) and `--allow-all-tools` (Copilot CLI) are excluded from the background-mode command construction entirely — there is no flag path that reaches them from `trigger agent ... --background`.
- **Never** a bare interpreter wildcard: an allowlist entry that only scopes the outer command while leaving `python3 *`, `uv *`, `uvx *`, or `npm *` unscoped is treated as equivalent to no scoping, and is excluded on that basis.
- Every allowlist entry is derived from a command literally observed in this repo's own playbooks, skills, agents, and config files — grep-verified, not guessed ahead of a real need, per [YAGNI](../../../factory/rulebooks/conventions/foundational-principles.md#yagni). Adding a new entry requires the same evidence standard.
- Claude Code's allow/deny lists use its own `Bash(<cmd> *)` glob syntax; Copilot CLI's use its colon-wildcard `shell(<cmd>:*)` syntax. The two-word-prefix form (`shell(git commit:*)`) is confirmed against GitHub's own documentation; the three-word forms (`shell(uv run pytest:*)`) follow the same pattern but are unconfirmed — see [T-05](../todos.md#t-05-copilot-clis-three-word-shell-wildcard-syntax-unconfirmed).
- The deny list mirrors [`block-dangerous-git.sh`](../../../factory/config/hooks/block-dangerous-git.sh)'s own pattern list exactly — a second, independent layer, not a substitute for it.
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
- `config/model.conf` is copied only if absent; its presence is checked once, and its content is never diffed or refreshed afterward (BR-022) — the same non-diffing treatment `factory/` itself receives once already present.

## Project-owned test gates (`testing.yaml`, BR-023, BR-024, BR-025, BR-026, BR-027, BR-028, BR-029)

- **BR-023**: Factory does not detect or construct test commands. The project declares its test commands in `docs/testing.yaml`. Factory reads that declaration; it does not guess, detect, or override. The `detect-test-regime` skill scans for existing test entrypoints during onboarding and populates the charter; it is not a runtime detection mechanism.
- **BR-024**: Bare test commands (`pytest`, `npm test`, `go test`, `cargo test`, and common variants) are blocked for agent execution via `block-dangerous-git.sh` deny patterns. The agent allowlist is populated from `docs/testing.yaml`: all declared command fields (`test_command`, `test_staged_command`, `test_changed_command`) are allowlisted with exact-string matching. No prefix matching. A command that differs from the declared string by even one character is denied.
- **BR-025**: The `test_changed_command` field in `docs/testing.yaml` is optional. When present, it is the command the project uses for fast feedback on changed files. Factory does not engineer mode flags or substitute its own mode logic; the project owns its mode story.
- **BR-026**: The `test_command` field in `docs/testing.yaml` is required. It is the full test suite command used by FSM `script_exit_zero` gate conditions. Factory calls it as-is from the repository root and reads only its exit code.
- **BR-027**: Factory does not parse structured test output. The gate contract is exit-code-only: zero means pass, nonzero means fail. Structured test counts, JSON summaries, and reporting are the project's concern.
- **BR-028**: The `test_staged_command` field in `docs/testing.yaml` is optional. When present, it is the command agents may use for TDD iteration on staged files. It is allowlisted in `block-dangerous-git.sh` with exact matching.
- **BR-029**: Factory does not inject test hooks into `.pre-commit-config.yaml`. Test hooks are project-owned infrastructure. The project decides when and how tests trigger on commit, push, or other events. The `agent_factory_hook-run-tests-full` entry that previously existed in Factory's pre-commit config is removed.

The `script_exit_zero` condition evaluator resolves `test_command` from `docs/testing.yaml` via the `charter:test_command` notation and reads its exit code; the pass/fail decision is exit-code-only (BR-027).

## Anchor-file prerequisite (feature-addition)

The `feature-addition` playbook checks for the existence of three anchor files before proceeding. This replaces the former prerequisite "existing project with spec and architecture."

- The three anchor files are: `docs/arc42/architecture.dsl`, `docs/spec/scope-map.md`, and `docs/CONTEXT.md`.
- The check is file-existence only — no content validation, no gate marker, no structural inspection.
- If all three exist, the prerequisite passes and the playbook proceeds normally.
- If any file is missing, the playbook reports which files are absent and suggests running `brownfield-onboarding` to establish the baseline.
- Full specification artifacts (`docs/spec/prd.md`, `docs/spec/*.feature`, `docs/spec/scope-map.md`, `docs/spec/supplementary_specs/*.md`) are optional inputs that deepen the process when present, not prerequisites.
- The anchor-file check does not distinguish between a brownfield-lite baseline (Stage 1 only) and a fully reverse-engineered project (Stage 2 complete). The depth is a continuum; the prerequisite only establishes the minimum.

See [newcomer-onboarding.feature](../newcomer-onboarding.feature) and [entity-model.md § ANCHOR_FILE_SET](entity-model.md).

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

See [newcomer-onboarding.feature](../newcomer-onboarding.feature).

## Referenced from

- [entity-model.md](entity-model.md)
- [UC-01](../../~archive/spec/use_cases/UC-01-advance-a-playbook-phase.md)
- [UC-03](../../~archive/spec/use_cases/UC-03-retry-a-phase-within-the-iteration-cap.md)
- [UC-04](../../~archive/spec/use_cases/UC-04-dispatch-an-agent-via-trigger.md)
- [UC-06](../../~archive/spec/use_cases/UC-06-regenerate-the-catalog.md)
- [UC-08](../../~archive/spec/use_cases/UC-08-initialize-agent-factory-into-a-project.md)
- [UC-09](../../~archive/spec/use_cases/UC-09-run-tests-via-hook.md)
- [UC-11](../../~archive/spec/use_cases/UC-11-cross-a-phase-boundary.md)

## Test-design validation (BR-051, BR-052, BR-053, BR-054, BR-055)

- **BR-051**: The test-design skill requires `detect-test-regime` as a prerequisite. If `docs/testing.yaml` lacks a `testing_strategy:` link or a `suites:` section, the skill fails with a diagnostic message and produces no output. This is a hard prerequisite, not a fallback path.
- **BR-052**: Test ownership is resolved in a single backlog-wide pass through `backlog/epics.md`. Each contract has exactly one owning story determined by dependency order: the story that introduces the contract's infrastructure or first exercises it (earliest in dependency-sorted order among stories that trace the contract). No contract is tested twice at the same layer.
- **BR-053**: Risk-class classification follows a three-level precedence chain: `testing.yaml` `risk_classes:` overrides > project-linked strategy document > Factory convention defaults. The Factory convention defines three risk classes: `critical` (format: `forbidden`, budget: `unbounded`), `standard` (format: `scenario`, budget: `equivalence`), `structural` (format: `linter`). Projects may add custom risk classes; custom classes must define at least `format` and `budget`.
- **BR-054**: The `test-design-verify` gate validates the trace-to-scenario resolution chain. Exit codes follow the gate convention: `0` = pass, `1` = validation failure, `2` = configuration error. The gate is conditionally active — it runs when the story has `#### Test Design` or `#### Prior Tests` sections and exits `0` with no findings when neither exists.
- **BR-055**: The `gates` section in `docs/testing.yaml` configures individual gates (enabled/disabled, thresholds). It does not define execution ordering; [ADR-0012](../../adr/0012-dispatcher-owned-semantic-gate-loop.md) owns the dispatcher's gate sequence. The CRAP-score script reads `gates.crap_score.threshold` from `testing.yaml`, replacing the dead-code `read_threshold_from_house_rules()` function. When the `gates` section is absent, the script falls back to its hardcoded default of 30.

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
- `update-context` is retired and performs no write. The team maintains `docs/agent-context.md` directly.
- `detect-test-regime` and test gates own the schema and values in `docs/testing.yaml`; concern validation does not parse test configuration.

See [agent-context.feature](../agent-context.feature) and [interface-contracts.md § concern-lint](interface-contracts.md#factoryscriptsconcern-lint).

## Dispatch ledger (`dispatch`)

- `mark-dispatching`, `mark-dispatched`, `mark-blocked`, `mark-failed`, `re-dispatch`, and `escalate` are idempotent no-ops when the story is already in the target state or tier outcome.
- `mark-failed` records an attempt entry with `session`, `tier`, `failure_class`, `evidence`, `commit_sha`, and `normalized_total`; a legacy ledger without `attempts` still loads as zero attempts.
- `escalate` requires exactly one prior impl attempt with `acceptance_unmet` or `contradictory_evidence`, a passing `verify-base`, no scope violation, a non-strong current tier, and no earlier escalation in the same wave.
- `close-wave <N>` refuses if any story in wave N is non-terminal.
- `close-wave <N>` appends at most one closeout record for the wave. Re-running a successful close-wave is a no-op and does not duplicate the record.

## Local usage processing and analysis

These rules support the [local usage feature](../local-usage-processing-and-analysis.feature).

### Input and contract validation

- Snapshot a sorted list of top-level `*.jsonl` files at query start. Do not recurse or admit lifecycle diagnostic files.
- Validate every selected line. A valid line and a preflight failure are mutually exclusive and collectively exhaustive.
- Report each failure with source file, one-based line number, field when applicable, and a stable failure code.
- Validate usage objects against the installed JSON Schema Draft 2020-12 contract and the manifest's accepted version range.
- Enforce identifiers, timestamps, declared nullability, non-negative counters, nested `transcript_ref` shape, and `normalized_total = normalized_input + normalized_output` outside schema where required.
- Reject an unknown CLI. The supported CLI set and accounting registry keys must be exactly `claude-code`, `pi`, `codex`, and `copilot`.
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
- Codex total: latest inclusive root snapshot; descendants provide attribution only.
- GitHub Copilot CLI total: latest inclusive root snapshot; descendants provide attribution only.
- Canonical session dimensions and timestamp come from the selected root snapshot. Additive descendant measures do not replace those dimensions.
- Cache aggregation uses the same contributing logical-run set as the CLI's conservation rule.
- Dimensional measures are additive over canonical session rows. Accept an ordered, duplicate-free subset of project, CLI, provider, model, agent, branch, and exit status plus time granularity `none`, `hour`, `day`, `week`, or `month`.
- Default to no dimensions and time granularity `none`, producing one all-input total. Reject duplicate or unknown dimensions. Use UTC calendar truncation and ISO Monday week starts.
- Preserve cache availability and input-only states. Do not replace unavailable values with zero.

### Query and export validation

- Publish exactly six stable views: `raw_usage_snapshots`, `latest_run_snapshots`, `canonical_session_usage`, `usage_by_dimension`, `cache_efficiency`, and `capture_health`.
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
