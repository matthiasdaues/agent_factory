# Validation Rules — Factory Specification

Field- and behavior-level rules each mechanism enforces, grouped by the entity or mechanism they govern. Business rule IDs (BR-###) are defined here or in the use case that introduces them; this file is the canonical index.

## Marker schema (`PLAYBOOK_STATE_MARKER`)

- `playbook` and `state` are required. `phase advance` and `phase retry` both refuse (non-zero exit) if either is missing from an existing marker file.
- `state` must name a state defined in the resolved FSM. `transition-lint` reports `TL-STATE` (error) if it does not; `phase advance` and `phase retry` fail resolving the current state's transitions in the same case.
- `recorded_at` is written in UTC, `%Y-%m-%dT%H:%M:%SZ` format, always from the writing script's own `datetime.now(timezone.utc)` call — never accepted as an input field (BR-006).
- `iteration` is an integer, defaulting to `1` when absent or unparseable. `phase advance` always resets it to `1` on a successful advance (BR-005); `phase retry` is the only mechanism that increments it.
- The marker is rendered as flat `key: value` lines in a fixed field order (`playbook`, `state`, `gate`, `result`, `open_findings`, `next`, `iteration`, `recorded_by`, `recorded_at`); a value of `None` renders as the literal `null`.
- The marker file lives at `.agent-factory/playbook-state.yml` and is git-ignored — local, single-machine state, never committed, never a distributed lock (see [PRD § Constraints](../prd.md#5-constraints)).

## Entry conditions (`GATE_CONDITION`)

- `file_exists`: satisfied if `repo_root.glob(path)` yields at least one match.
- `files_exist`: satisfied if every path in `paths` yields at least one glob match; the unmet reason lists every missing path by name.
- `no_open_findings`: satisfied if zero matching finding files (by `pattern` or `patterns`, globbed under `docs/findings/`) have frontmatter `status: open`. A file whose frontmatter cannot be parsed (no leading `---` block) is not counted as open.
- `script_exit_zero`: **always satisfied** in the current implementation — deliberately stubbed, not yet running the named script. See [T-03](../todos.md#t-03-script_exit_zero-condition-type-is-stubbed).
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
- The deny list mirrors [`block-dangerous-git.sh`](../../../factory/config/hooks/block-dangerous-git.sh)'s own pattern list exactly (BR-020) — a second, independent layer, not a substitute for it.
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

## Installation collisions (`init-factory`, BR-021, BR-022)

- A destination path is safe to proceed past only if it is missing, or already a symlink resolving to the exact expected target. Any other existing state (a real file, a real directory, or a symlink to something else) raises a `Collision`.
- A `Collision` stops the entire run immediately — steps already completed earlier in the run stay applied; no step later than the collision point runs at all (BR-021).
- `config/model.conf` is copied only if absent; its presence is checked once, and its content is never diffed or refreshed afterward (BR-022) — the same non-diffing treatment `factory/` itself receives once already present.

## Test execution (`run-tests`, BR-023, BR-024, BR-025, BR-026, BR-027, BR-028, BR-029)

- **BR-023**: Framework detection scans project structure for all framework markers: `pyproject.toml` (contains pytest → `uv run pytest`), `package.json` (→ `npm test`), `go.mod` (→ `go test ./...`), `Cargo.toml` (→ `cargo test`). Multiple frameworks detected → exit `2` with error listing all found markers (monorepo multi-framework orchestration not yet supported; see T-06). Single framework detected → execute that framework's tests. No framework detected → exit `2` with error message listing checked markers.
- **BR-024**: Bare test commands are blocked for agent execution via `block-dangerous-git.sh` deny patterns: `pytest`, `npm test`, `go test`, `cargo test`, and common variants (`python -m pytest`, `uv run pytest`, `yarn test`). Agents receive exit `2` denial at `PreToolUse` with message directing them to `factory/scripts/run-tests --staged` or hook-triggered execution instead. Agent allowlist includes `factory/scripts/run-tests --staged` for test iteration during development; bare test commands remain blocked.
- **BR-025**: `--changed-only` mode applies framework-specific fast filters: pytest uses `--lf` (last-failed) or `--testmon` if available; jest uses `--onlyChanged`; go test and cargo test filter by package/crate path derived from git diff. Exact filter per framework is implementation-defined; the intent is sub-second feedback for small changes.
- **BR-026**: `--full` mode runs the complete test suite with no file/package filtering, no cached result reuse. Used by pre-push and FSM `script_exit_zero` gates where partial coverage is insufficient.
- **BR-027**: JSON summary is emitted on stdout in the format `{"passed": int, "failed": int, "skipped": int, "duration_ms": int}` after test execution completes. All test progress, failure details, and error messages go to stderr only — stdout is reserved for the JSON line.
- **BR-028**: `--staged` mode runs tests on staged files only (reads `git diff --staged --name-only`), without requiring commit completion. Used by agents to iterate on test development before committing. Applies same framework-specific filters as `--changed-only` but scoped to staging area.
- **BR-029**: Pre-commit hook only triggers test execution when files in `src/` or `test/`/`tests/` directories are modified. Documentation, configuration, playbooks, and backlog changes do not trigger test execution. This is language-agnostic: applies to Python, JavaScript, Go, Rust, or any other language using standard directory conventions.

The `script_exit_zero` condition evaluator (currently stubbed per [T-03](../todos.md#t-03-script_exit_zero-condition-type-is-stubbed)) will invoke `run-tests` and read its exit code; the JSON summary on stdout is for human/log consumption, not for the gate's pass/fail decision.

## Architecture model invariants (BR-050, BR-051, BR-052)

- **BR-050**: The JSONC model (`docs/arc42/architecture.jsonc`) is the single source of truth for architectural structure: elements, relationships, views, and constraints. The draw.io file (`docs/arc42/architecture.drawio`) owns layout and visual arrangement. Neither file is authoritative for the other's domain.
- **BR-051**: The Factory workflow permits only label and description text to change via draw.io reverse sync. Element creation, deletion, and structural renaming are workflow-permitted only through the JSONC-first path. The `bausteinsicht sync` command itself performs a full, unrestricted reverse pass — it carries back all draw.io changes, including structural ones, into the JSONC model. Enforcement of the labels-only workflow restriction relies on `bausteinsicht validate` catching structural drift after the fact, and on the pre-commit hook (BR-056) blocking commits that contain such drift. No `--reverse-mode=labels-only` flag exists in the first release. See [T-11](../todos.md#t-11-no-restricted-reverse-mode-flag-in-first-release).
- **BR-052**: Factory agents work in the JSONC model exclusively. An agent never edits the draw.io file directly. This constraint is enforced by skill and agent instructions, not by a mechanical gate.

## Architecture Docker execution (BR-053)

- **BR-053**: All Bausteinsicht operations run inside a Docker container via the `factory/scripts/bausteinsicht` wrapper. The Factory does not install the Bausteinsicht binary directly on the host. The wrapper requires a running Docker daemon and exits non-zero if Docker is unavailable.

## Architecture pre-commit validation (BR-054, BR-055, BR-056)

- **BR-054**: Co-staging enforcement: the pre-commit hook rejects a commit when `architecture.jsonc` is staged without `architecture.drawio`, or vice versa. Both files must be staged together to pass the hook.
- **BR-055**: The pre-commit hook fires conditionally. It checks whether any files matching `*.jsonc` or `*.drawio` under `docs/arc42/` appear in the staging area (`git diff --cached --name-only`). If no such files are staged, the hook is a no-op and exits `0` immediately. Files with those extensions outside `docs/arc42/` do not trigger the hook.
- **BR-056**: `bausteinsicht validate` checks structural consistency between the JSONC model and the draw.io diagram (schema, referential integrity, element correspondence). `bausteinsicht lint` checks architectural constraints declared in the JSONC model's `constraints` array. Both must pass for the pre-commit hook to allow the commit.

## Architecture image export (BR-057)

- **BR-057**: Exported images are written to `docs/assets/images/`. Arc42 chapters embed them with relative image references to this path (e.g. `SystemContext.png` for the System Context view). The filenames are derived from view names in the JSONC model.

## Architecture migration (BR-058)

- **BR-058**: Migration via `bausteinsicht import` is a one-time operation that produces `architecture.jsonc` and an initial `architecture.drawio` from an existing Structurizr DSL file. The command refuses to run if `architecture.jsonc` already exists at the target path. After verification, the `.dsl` file is deleted manually by the actor; the import command does not delete it.

## Architecture lint delegation (BR-059)

- **BR-059**: `arch-lint` delegates model-specific checks to `bausteinsicht validate` and `bausteinsicht lint`, retaining its own Factory-specific checks (arc42 chapter coupling, ADR format, image staleness). The condition for running the delegated checks is the existence of `architecture.jsonc` (replacing the previous `architecture.dsl` condition). When `architecture.jsonc` is absent, `arch-lint` skips the delegated checks and runs only its own Factory-specific checks.

## Referenced from

- [entity-model.md](entity-model.md)
- [UC-01](../use_cases/UC-01-advance-a-playbook-phase.md)
- [UC-03](../use_cases/UC-03-retry-a-phase-within-the-iteration-cap.md)
- [UC-04](../use_cases/UC-04-dispatch-an-agent-via-trigger.md)
- [UC-06](../use_cases/UC-06-regenerate-the-catalog.md)
- [UC-08](../use_cases/UC-08-initialize-agent-factory-into-a-project.md)
- [UC-09](../use_cases/UC-09-run-tests-via-hook.md)
- [UC-11](../use_cases/UC-11-cross-a-phase-boundary.md)
- [UC-13](../use_cases/UC-13-synchronize-model-and-diagram.md)
- [UC-14](../use_cases/UC-14-validate-model-consistency.md)
- [UC-15](../use_cases/UC-15-export-architecture-views.md)
- [UC-16](../use_cases/UC-16-migrate-from-structurizr-dsl.md)
- [UC-17](../use_cases/UC-17-validate-architecture-at-commit.md)
