# QA Strategy — Mechanized Dispatch and Step Isolation

Derived from [mechanized-dispatch.md](mechanized-dispatch.md) (behavioral specification) and the [Contract-Owned Testing Strategy](../../../factory/rulebooks/conventions/testing-strategy.md). This document assigns each observable contract to its owning test layer, identifies equivalence classes, and defines the integration and end-to-end fixtures needed.

## Principles Applied

1. **One contract, one owner.** Every Gherkin scenario maps to exactly one test layer. Higher layers may traverse the same path but do not duplicate lower-layer assertions.
2. **Cases by behavior, not by count.** Equivalence classes, boundaries, and distinct failure modes — never a coverage percentage target.
3. **Linters before tests.** Anything a deterministic linter can own (YAML schema, enum membership, frontmatter structure) stays out of pytest.
4. **Security boundaries stay separate.** The write-guard deny-list for script-owned state files (ledger, manifest) is a security contract even though it shares code with the general output-glob check.

## Test Layers and Contract Ownership

### Layer 1 — Deterministic Linter

Contracts that are declarative structure checks. These belong in `backlog-lint`, `spec-lint`, or a new `dispatch-lint` script — not in pytest.

| Contract                                     | Owning linter             | Spec scenarios                                         |
| -------------------------------------------- | ------------------------- | ------------------------------------------------------ |
| `risk_domains` values are from closed enum   | `backlog-lint`            | backlog-lint rejects unknown risk_domains values       |
| `strategy` values are from closed enum       | `backlog-lint`            | backlog-lint rejects unknown strategy values           |
| `seam_outputs` ∩ `impl_outputs` = ∅          | `backlog-lint`            | backlog-lint rejects overlapping seam and impl outputs |
| `seam_outputs` ∪ `impl_outputs` = `outputs`  | `backlog-lint`            | backlog-lint validates union matches outputs           |
| Failure class is from seven-value vocabulary | `dispatch` (argparse)     | Unknown failure class is rejected                      |
| Evidence path is a tracked artifact          | `dispatch` (git ls-files) | Untracked evidence path is rejected                    |
| Ledger SHAs are 40 hex characters            | `dispatch-lint` (new)     | Commit SHAs in the ledger are full 40-character hashes |
| Step manifest schema validity                | `dispatch-lint` (new)     | Manifest is written with story declarations            |

### Layer 2 — Contract Test (pytest, no git repos)

Pure behavioral logic testable with in-memory data structures and fixtures. No subprocess calls, no real git repositories, no filesystem side effects beyond tmp directories.

#### 2a. Dispatch Planning (pure computation)

| Contract                           | Equivalence classes                                                                        | Boundaries                                                                                       |
| ---------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| Dependency graph → wave assignment | No deps (wave 1), linear chain (sequential), diamond (fan-in), independent parallel        | Empty story set, single story, circular dependency (error)                                       |
| File-overlap detection             | Disjoint globs, overlapping globs, nested globs (`src/**` vs `src/foo/*`), identical globs | Zero-file glob (prefix fallback), single-file exact match                                        |
| Serial chain vs parallel set       | All parallel, all serial, mixed within one wave                                            | Two stories same glob, three-way overlap                                                         |
| Tier rubric (first-match-wins)     | security → strong, multi-dir → standard, single-dir+tests → economy, default → standard    | Multiple conditions true (first wins), no conditions true (default), safety_critical_paths empty |

Owner: `tests/test_dispatch_planning.py`

#### 2b. Story Lifecycle State Machine

| Contract                                   | Equivalence classes                                                                                                                                                                                                                                                    | Boundaries                                      |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| Valid transitions                          | PENDING→PREPARED, PREPARED→DISPATCHING, DISPATCHING→DISPATCHED, DISPATCHING→FAILED, DISPATCHED→DONE/BLOCKED/FAILED, FAILED→PREPARED (re-dispatch), BLOCKED→PREPARED (re-dispatch)                                                                                      | Each terminal→re-dispatch, DONE has no outbound |
| Invalid transitions                        | PENDING→DISPATCHED (skip), PREPARED→DISPATCHED (skip DISPATCHING), DISPATCHING→DONE (skip DISPATCHED), DONE→anything, DISPATCHED→PREPARED (reverse)                                                                                                                    | Every invalid pair                              |
| Re-dispatch preconditions by failure class | context_missing (same tier), contract_violation 1st (same tier), contract_violation 2nd (terminal), environment (same tier), spend_death (same tier), seam_defect (seam session), acceptance_unmet (requires escalation), contradictory_evidence (requires escalation) | contract_violation at exactly 2 attempts        |

Owner: `tests/test_dispatch_lifecycle.py`

#### 2c. Escalation Predicate (six conditions)

| Contract                            | Equivalence classes                                                                                           | Boundaries                                             |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| All six conditions met → grant      | Happy path with acceptance_unmet, happy path with contradictory_evidence                                      | Exactly one prior attempt (boundary of "at least one") |
| Each condition independently blocks | No prior attempt, non-qualifying class, already strong, wave slot taken, second escalation, verify-base fails | Each condition as sole blocker while others pass       |
| Wave escalation exhausted           | Second qualifying failure after slot taken → blocked                                                          | Exactly two qualifying failures in one wave            |
| Tier arithmetic                     | economy→standard, standard→strong, strong→saturated                                                           | Floor at economy (seams-first impl), ceiling at strong |

Owner: `tests/test_dispatch_escalation.py`

#### 2d. Glob Matching (shared implementation)

| Contract                            | Equivalence classes                                         | Boundaries                                                        |
| ----------------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------- |
| `*` matches within segment          | `UC-*.md` matches `UC-01.md`, does not match `sub/UC-01.md` | Empty segment, segment with only `*`                              |
| `**` matches across segments        | `src/**/*.py` matches `src/a/b/c.py`                        | Zero intermediate segments, deeply nested                         |
| `?` matches one character           | `file?.py` matches `file1.py`, not `file12.py`              | At path boundary (should not match `/`)                           |
| Literal matching                    | Exact path, case sensitivity                                | Paths with special characters                                     |
| step-guard and premerge-check agree | Same glob, same path → same result                          | Globs that prefix-matching would accept but glob-matching rejects |

Owner: `tests/test_glob_matching.py`

#### 2e. Handoff Contract Generation

| Contract                         | Equivalence classes                                              | Boundaries                                   |
| -------------------------------- | ---------------------------------------------------------------- | -------------------------------------------- |
| Seven parts present              | Direct strategy, seams-first strategy                            | Minimal story (fewest fields), maximal story |
| Legacy clauses absent            | verify-base preamble, sub-agent addressing, workflow restatement | —                                            |
| Budget gate                      | Under 800 tokens, exactly 800 tokens, over 800 tokens            | Boundary at 3200 bytes                       |
| Acceptance criteria by reference | Path present, text not inlined                                   | —                                            |

Owner: `tests/test_handoff_contract.py`

#### 2f. Context Guard (token estimation)

| Contract              | Equivalence classes      | Boundaries                        |
| --------------------- | ------------------------ | --------------------------------- |
| Within budget → allow | Total < max_input_tokens | Exactly at budget (boundary)      |
| Over budget → deny    | Total > max_input_tokens | One byte over boundary            |
| Estimation formula    | bytes ÷ 4                | Zero-byte file, empty inputs list |

Owner: `tests/test_context_guard.py`

### Layer 3 — Integration Test (pytest, real git repos in tmp)

Contracts that cross process or filesystem boundaries. Each test creates a temporary git repository, runs dispatch subcommands as subprocesses, and asserts on filesystem and git state.

#### 3a. Dispatch Init

| Contract                    | Test fixture                                       | Assertions                                                                            |
| --------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Atomic creation             | Clean tmp repo + config/project.json + story files | Invocation branch exists, worktree exists, ledger exists, stories recorded as pending |
| Untracked directories block | Tmp repo with untracked files in output dirs       | Non-zero exit, no branch created                                                      |
| Baseline commit             | Tmp repo with untracked files, --baseline-commit   | Baseline commit on base branch, invocation branch cut from it                         |
| Missing test_command        | config/project.json without test_command           | Non-zero exit                                                                         |
| Tier mismatch blocking      | Story with security risk_domain, tier: economy     | Non-zero exit                                                                         |

Owner: `tests/test_dispatch_init_integration.py`

#### 3b. Wave and Story Preparation

| Contract                               | Test fixture                          | Assertions                                                                       |
| -------------------------------------- | ------------------------------------- | -------------------------------------------------------------------------------- |
| Wave gate (prior wave non-terminal)    | Ledger with wave 1 partially terminal | Non-zero exit from prepare-wave 2                                                |
| Branch + worktree creation             | Ledger with wave 1 terminal           | Feature branches exist, worktrees exist, `git worktree list --porcelain` matches |
| Manifest written                       | Prepared story                        | `current-step.yml` exists in worktree with correct content                       |
| Serial chain links stay pending        | Chain of two stories                  | Head prepared, link pending                                                      |
| Chain link cuts from predecessor merge | Predecessor merged                    | Link branch parent is predecessor's merge commit                                 |
| Verify-base runs pre-spawn             | —                                     | verify-base-ok marker present after prepare                                      |

Owner: `tests/test_dispatch_prepare_integration.py`

#### 3c. Story Merge

| Contract                         | Test fixture                                                      | Assertions                                                                |
| -------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Clean merge + green suite        | Feature branch with non-conflicting changes, passing test_command | Story status = done in merge commit, worktree removed, branch removed     |
| Merge conflict → abort + blocked | Feature branch with conflicting changes                           | `git merge --abort` called, story blocked, invocation branch unchanged    |
| Red suite → revert + blocked     | Feature branch with breaking changes                              | Merge commit reverted, invocation branch at pre-merge HEAD, story blocked |
| premerge-check --scope-glob      | Feature branch with out-of-scope changes                          | Non-zero exit before merge                                                |

Owner: `tests/test_dispatch_merge_integration.py`

#### 3d. Step Guard Enforcement

| Contract                             | Test fixture                                             | Assertions                     |
| ------------------------------------ | -------------------------------------------------------- | ------------------------------ |
| Read guard allows declared input     | Manifest with inputs, simulated Read event JSON          | Exit 0                         |
| Read guard allows Factory prefixes   | Manifest with inputs, Read event for factory/ path       | Exit 0                         |
| Read guard denies out-of-scope       | Manifest with inputs, Read event for unlisted path       | Non-zero exit                  |
| Write guard allows declared output   | Manifest with outputs, simulated Write event JSON        | Exit 0                         |
| Write guard denies ledger            | Any manifest, Write event targeting dispatch-ledger.yaml | Non-zero exit                  |
| Write guard denies manifest          | Any manifest, Write event targeting current-step.yml     | Non-zero exit                  |
| Write guard allows findings          | Any manifest, Write event for docs/findings/             | Exit 0                         |
| Write guard allows gate markers      | Any manifest, Write event for verify-base-ok             | Exit 0                         |
| Bash guard extracts and checks paths | Manifest, Bash event with `cat <path>`                   | Allowed/denied per input scope |
| Bash guard passes opaque commands    | Manifest, Bash event with `git status`                   | Exit 0                         |
| No manifest → unrestricted           | No manifest file, any event                              | Exit 0                         |

Owner: `tests/test_step_guard_integration.py`

#### 3e. Manifest Lifecycle

| Contract                 | Test fixture                                | Assertions                                        |
| ------------------------ | ------------------------------------------- | ------------------------------------------------- |
| No-supersede             | Existing manifest, attempt to write new one | Non-zero exit, original manifest unchanged        |
| Independent per worktree | Two worktrees with manifests                | Removing one leaves the other                     |
| clear-manifest --force   | Stale manifest in worktree                  | Manifest removed, warning printed, ledger updated |

Owner: `tests/test_manifest_lifecycle_integration.py`

#### 3f. Idempotency

| Contract                             | Test fixture                                   | Assertions                                                 |
| ------------------------------------ | ---------------------------------------------- | ---------------------------------------------------------- |
| Re-run after success is no-op        | Fully prepared wave                            | No duplicate branches, no duplicate ledger entries, exit 0 |
| Re-run after partial failure resumes | Wave preparation interrupted after first story | First story recognized, second story prepared              |

Owner: `tests/test_dispatch_idempotency_integration.py`

#### 3g. Interruption Safety

| Contract                                    | Test fixture                                                      | Assertions                                                   |
| ------------------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------ |
| Pre-write interruption is idempotent        | Kill prepare-wave before any ledger write, re-run                 | Re-run succeeds, no duplicate entries                        |
| Post-partial-write interruption resumes     | Kill prepare-wave after preparing first story, re-run             | First story recognized, second prepared                      |
| merge-story interrupted after merge re-runs | Kill merge-story after merge commit but before test suite, re-run | Prior merge detected, test suite runs against existing merge |
| Omitted abort signal executes without error | Invoke prepare-wave without passing a signal                      | Exit 0, normal execution                                     |
| Active abort signal triggers clean shutdown | Invoke prepare-wave with signal, fire signal mid-execution        | Stops at safe point, ledger reflects only completed work     |
| Already-aborted signal prevents execution   | Invoke prepare-wave with pre-aborted signal                       | Immediate exit, ledger unchanged                             |

Owner: `tests/test_dispatch_interruption_integration.py`

#### 3h. Verification Immutability

| Contract                                   | Test fixture                                                           | Assertions                                               |
| ------------------------------------------ | ---------------------------------------------------------------------- | -------------------------------------------------------- |
| verify-story leaves index unchanged        | Tmp repo with staged and unstaged changes, run verify-story            | `git status --porcelain` identical before and after      |
| verify-story leaves working tree unchanged | Tmp repo with uncommitted modifications, run verify-story              | No file added, removed, or modified by the command       |
| premerge-check does not stage files        | Feature branch ready to merge, run merge-story (intercept after check) | Index unchanged after premerge-check returns             |
| Escalation check does not mutate state     | Story with failed attempt, run dispatch escalate                       | Working tree, index, and HEAD unchanged after evaluation |

Owner: `tests/test_dispatch_immutability_integration.py`

### Layer 4 — End-to-End Smoke Test

One representative journey through the dispatch lifecycle with the real `dispatch` script, real git operations, and the real test suite runner. Not a Gherkin scenario test — a journey that exercises the golden path and one failure/recovery path.

#### Smoke 1: Two-story, two-wave dispatch to completion

01. Create a tmp repo with two stories, ST-001 (wave 1) and ST-002 (wave 2, depends on ST-001).
02. `dispatch init --base main --stories ST-001,ST-002`
03. `dispatch plan --backlog-dir backlog`
04. `dispatch prepare-wave 1`
05. `dispatch mark-dispatching ST-001`
06. Simulate subagent spawn and work: commit changes to ST-001's feature branch.
07. `dispatch mark-dispatched ST-001`
08. `dispatch verify-story ST-001 --sha <sha>`
09. `dispatch merge-story ST-001`
10. `dispatch close-wave 1`
11. `dispatch prepare-wave 2` (cuts from ST-001's merge)
12. Mark dispatching, simulate subagent work on ST-002.
13. Mark dispatched, verify, merge, close wave 2.
14. Assert: both stories done, ledger clean, no stale worktrees, no stale branches.

#### Smoke 2: Failure, escalation, and re-dispatch

1. Same setup as Smoke 1 but ST-001 fails with `acceptance_unmet`.
2. `dispatch mark-dispatching ST-001`, spawn, `dispatch mark-dispatched ST-001`
3. `dispatch mark-failed ST-001 --class acceptance_unmet --evidence <finding>`
4. `dispatch escalate ST-001`
5. `dispatch re-dispatch ST-001`
6. `dispatch mark-dispatching ST-001`, spawn at escalated tier, `dispatch mark-dispatched ST-001`
7. Merge, close.
8. Assert: two attempts in ledger, escalation recorded, story done.

Owner: `tests/test_dispatch_e2e.py`

## Contracts NOT Tested in pytest

These are owned by deterministic linters or are the responsibility of existing test suites, and must not be duplicated in the dispatch test suite.

| Contract                      | Owner                                     | Reason                         |
| ----------------------------- | ----------------------------------------- | ------------------------------ |
| Story frontmatter schema      | `backlog-lint`                            | Declarative structure          |
| Manifest YAML schema          | `dispatch-lint` (new)                     | Declarative structure          |
| Commit message format         | `commit-conventions.md` + pre-commit hook | Already enforced mechanically  |
| CLI wiring (hook config JSON) | `init-factory` tests                      | Boundary of a different script |
| Agent definition content      | `index-lint`                              | Catalog consistency            |

## Test Infrastructure Needed

| Component                  | Purpose                                                                                    | Notes                                                        |
| -------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------ |
| `tmp_git_repo` fixture     | Create an isolated git repo with branches, config, and story files                         | Shared across all integration tests. Cleanup via `tmp_path`. |
| `story_factory` fixture    | Generate story YAML with configurable fields (outputs, deps, risk_domains, strategy, tier) | Parameterized helper, not a separate file per test.          |
| `ledger_factory` fixture   | Generate ledger YAML in specific states (wave N terminal, story X in state Y)              | Avoids hand-writing ledger fixtures for every scenario.      |
| `step_guard_event` fixture | Generate simulated PreToolUse JSON events for Read/Write/Bash                              | Matches the real hook event schema from each CLI.            |
| `dispatch_run` helper      | Subprocess wrapper: runs `dispatch <subcommand>`, captures exit code, stdout, stderr       | Thin wrapper, not a framework.                               |

## Risk-Based Prioritization

Contracts are ordered by the cost of an undetected failure, not by scenario count.

| Priority | Area                                     | Risk                                                                     | Contract test count | Integration test count        |
| -------- | ---------------------------------------- | ------------------------------------------------------------------------ | ------------------- | ----------------------------- |
| 1        | Write guard deny-list (ledger, manifest) | Agent writes to script-owned state → silent corruption                   | 2                   | 3                             |
| 2        | Merge-story revert on red suite          | Invocation branch poisoned → cascade failure                             | 1                   | 2                             |
| 3        | Verification immutability                | Validator mutates state → accepts what it should reject                  | 0                   | 4                             |
| 4        | Interruption safety                      | Interrupted subcommand leaves unrecoverable ledger → manual repair       | 0                   | 6                             |
| 5        | Escalation predicate (six conditions)    | Wrong-tier dispatch → wasted spend or insufficient capability            | 8                   | 0 (covered by contract tests) |
| 6        | Story lifecycle state machine            | Invalid transition → ledger inconsistency                                | ~15                 | 0 (pure logic)                |
| 7        | Glob matching consistency                | Guard/premerge-check disagree → false blocks or false passes             | 5                   | 2                             |
| 8        | Wave gate (prior wave terminal)          | Non-terminal stories leak into next wave → contamination                 | 1                   | 1                             |
| 9        | Re-dispatch preconditions by class       | Wrong disposition → wasted or blocked re-dispatch                        | 7                   | 0 (pure logic)                |
| 10       | File-overlap computation                 | Over-serialization (inefficiency) or under-serialization (contamination) | 5                   | 0 (pure logic)                |
| 11       | Idempotency                              | Duplicate branches/entries on re-run → confusion                         | 0                   | 2                             |
| 12       | Context guard budget                     | Over-budget spawn → context blowup                                       | 3                   | 0 (pure logic)                |

## Estimated Test Counts

| Layer                      | Count   | Notes                                                 |
| -------------------------- | ------- | ----------------------------------------------------- |
| Deterministic linter rules | 8       | Owned by backlog-lint (4), dispatch-lint (4, new)     |
| Contract tests             | ~46     | Pure logic, fast, no I/O                              |
| Integration tests          | ~35     | Real git repos in tmp, subprocess calls               |
| E2E smoke tests            | 2       | Full journey, ~30s each                               |
| **Total**                  | **~91** | +10 from interruption safety (6) and immutability (4) |

These counts are estimates from equivalence-class analysis. Implementation may consolidate cases into parameterized tests or split them where distinct failure modes emerge.
