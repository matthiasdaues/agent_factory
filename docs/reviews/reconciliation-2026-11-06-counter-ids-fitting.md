---
type: reconcile-spec
title: Reconciliation of the counter-ids-fitting specification and architecture
date: 2026-11-06
status: pass
reviewer: reconciliation-agent
findings_filed: 1
story: counter-ids-fitting
scope: feature/counter-ids-fitting at 4988f93cdba9c87bae4a3585a46dd1592685f533 against dev at 13c55ff47eae0e82de8f7a8398b6e8c5e07805e1 — next-id (--plan-seed, the local counter, --move-to-origin), init-factory (counter_seeded and the hints), housekeeping-about, and the agent texts, against counter-ids-fitting.feature, the changed Scenarios of counter-ids.feature, the counter-ids-fitting sections of the spec, the scope map, the QA strategy, the ID Allocation architecture, and ADR-0033
---

# Reconciliation of the counter-ids-fitting specification and architecture

## Result

One finding blocks the merge into `dev`. RECON-0030 is `major`: Rule CIF-11
of `counter-ids-fitting.feature` still expects a refused move to put the claim
commit C back on the local counter. DEC-16 forbids that, and the code, BR-102,
ADR-0033, and the architecture follow DEC-16. The fix is a text change in the
feature file. The run recorded three `minor` findings as register lines in
`docs/findings/register/document.jsonl`, and it found no code defect. Next,
the human reads the tables below and decides each row. Then the requirements
agent fixes RECON-0030, and a short recheck of that one finding clears the
merge.

## Scope

The run compared the code of `git diff dev...feature/counter-ids-fitting` at
`4988f93c`:

- `packages/factory/scripts/next-id`: `--plan-seed`, the local counter, and
  `--move-to-origin`
- `check_counter` and `record_counter_seeded` in
  `packages/factory/scripts/init-factory`, and
  `packages/factory/scripts/housekeeping-about`
- the agent texts: `virgil.md` § Fitting, the four `AGENTS.*.md` files,
  `session-menu.md` § Counter check, `id-prefixes.md`, and the ID producer
  files
- the tests in `tests/factory/` for these files

It compared them against these documents on the same commit:

- `docs/spec/features/counter-ids-fitting.feature`, the changed Scenarios of
  `counter-ids.feature`, and `docs/spec/scope-map.md`
- the counter-ids-fitting sections of `entity-model.md`,
  `interface-contracts.md`, `validation-rules.md` (BR-096 to BR-108),
  `state-machines.md` (Claim and Move Lifecycle), and `glossary.md`
- `docs/spec/work/counter-ids-fitting-gaps.md` and
  `docs/spec/work/counter-ids-fitting-qa-strategy.md`
- the ID Allocation elements of `docs/spec/architecture.dsl`, arc42 5.11,
  6.16, 6.16.1, 8.18, QS-22, QS-23, and ADR-0033
- `backlog/ST-0376.md` to `ST-0385.md` and
  `backlog/epics-counter-ids-fitting.md`
- `docs/agent-context.md`

The classification follows the accepted proposal `finding-classification.md`,
as the brief requires. No artifact of the run is in use, because nothing on
`dev` runs the new code or encodes the new text. So no finding is `critical`.
The run did not run the test suite.

## Earlier rows

The brief names decisions and drift rows that the build settled. The run
checked each one, and each holds:

- **DEC-15.** `RECON` is in `PREFIXES` of `next-id`, in `id-prefixes.md`, and
  in the tag table of `finding-format.md`. `reconcile-spec` and the
  reconciliation agent name `next-id RECON` for a drift finding.
- **DEC-16.** `_after_refusal` and the time-limit branch of `move_to_origin`
  keep the marker and the setting (`next-id:844`, `:897`). BR-102, the
  `next-id --move-to-origin` contract, the Move Lifecycle, ADR-0033, arc42
  6.16 and 8.18, QS-23, and the DSL say the same. The feature file and the QA
  strategy do not: RECON-0030 and RECON-0031.
- **ST-0376.** BR-099 counts the working tree, BR-101 fixes the order of
  `PREFIXES`, and the `--plan-seed` contract names both, the run outside a
  clone, and the in-use line. The entity model lags: RECON-0033.
- **ST-0377 and BUG-0118.** `housekeeping-about` lists `counter_seeded` and
  counts against the length of its list.
- **ST-0378.** The counter check table names fitting step 4 in its hints, as
  `check_counter` prints them.
- **ST-0380.** The contract defines the success line
  `moved refs/ids/counters from <local> to <remote>`. The seven named QA rows
  say `implemented`.
- **ST-0381.** The contract and BR-102 describe the restart and the resume.
  The case table has the row for ten stale leases. arc42 6.16.1 asks `origin`
  with `git ls-remote` before the push.
- **IMPL-0008.** The Move Lifecycle has the state `RECHECKING`. BR-102 and
  the contract state the second `git ls-remote` and the push from a throwaway
  repository.

The report `reconciliation-2026-11-06-counter-ids.md` holds rows on the same
script. RECON-0025 and RECON-0026 are fixed. RECON-0027, RECON-0028,
RECON-0029, BUG-0117, and its notes are still open, so this run repeats none
of them. BUG-0117 now covers more: arc42 5.11 gives the counter port the
operations `inspect` and `move` too, and `plan_seed` and `move_to_origin`
reach git without the port. The open register lines SPEC-0061 to SPEC-0070,
IMPL-0011 to IMPL-0013, and ATAM-0015 to ATAM-0017 still describe the code as
built, so the run repeats none of them either.

## Discrepancy table

Each finding ID names a finding file in `docs/findings/` or a register line in
`docs/findings/register/document.jsonl`.

| Artifact                                            | Drift                                                                                                                                                                                                                                                                                                                                                                 | Evidence                                                                                                                                                                              | Owner                   | Status |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- | ------ |
| `docs/spec/features/counter-ids-fitting.feature`    | RECON-0030 (major, spec-stale, file). Rule CIF-11 and its two Scenarios expect the local counter to hold C after a refused move. DEC-16 and the code keep the marker. Rename the Rule and both Scenarios, and expect the marker with parent C.                                                                                                                        | `counter-ids-fitting.feature:323` to `:342`; `next-id:897` (`_after_refusal`); `test_next_id_move.py:194` and `:212` assert the marker                                                | `requirements-agent`    | open   |
| `docs/spec/work/counter-ids-fitting-qa-strategy.md` | RECON-0031 (minor, spec-stale). The rows CIF-11-IT-01 and CIF-11-IT-02 still describe the restore, and CIF-11-IT-02 names the test `test_st_0380_a_refused_push_puts_c_back`, which no longer exists. State the marker and name the DEC-16 test.                                                                                                                      | QA strategy lines 98 and 99; `test_next_id_move.py:212` (`test_dec_16_a_refused_push_keeps_the_marker_and_a_second_move_resumes`)                                                     | `test-strategy-agent`   | open   |
| `docs/spec/work/counter-ids-fitting-qa-strategy.md` | RECON-0032 (minor, spec-stale). 33 rows still say `planned`, although all ten stories are done. 28 of them have a test with their marker. CIF-08-IT-03 and the four CIF-13 rows name only a file, and their tests carry no marker. The note at line 120 calls CIF-09-LN-01 `blocked`. Set the rows to `implemented`, name the five test functions, and drop the note. | QA strategy lines 71 to 118 and 120; `test_init_factory_counter.py:123`, `:200`, `:213`, `:231`; `test_next_id.py` (`test_st_0370_clone_without_origin_names_origin_remote_and_seed`) | `test-strategy-agent`   | open   |
| `docs/spec/entity-model.md`                         | RECON-0033 (minor, spec-stale). ID_IN_USE counts only a local or remote-tracking branch. BR-099 and `--plan-seed` also count the working tree of the current worktree. Add it.                                                                                                                                                                                        | `entity-model.md:943` to `:948`; `next-id:633` (`_working_tree`); BR-099                                                                                                              | `domain-modeling-agent` | open   |

## Notes

These rows need a decision but change no behaviour. They stay in this report
and get no register line.

| Artifact                                     | Drift                                                                                                                                                                                                                                                                                                                                                                       | Evidence                                                                                                                    | Owner                   | Status |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ----------------------- | ------ |
| `docs/spec/work/counter-ids-fitting-gaps.md` | Seven gaps stand open, although the build answers them. CIF-G01: the hints name step 4. CIF-G02: BR-074 and BR-075 name the local counter. CIF-G04: `session-menu.md` § Counter check holds the check. CIF-G06: the setting stays on a decline. CIF-G07: `record_counter_seeded` writes the greenfield key. CIF-G09 and CIF-G10: CIFP-C06 and CIFP-C05. Mark them answered. | `counter-ids-fitting-gaps.md:67` to `:81`; `virgil.md:308`; `session-menu.md:5`; `init-factory:3157`                        | `requirements-agent`    | open   |
| `docs/spec/validation-rules.md`              | BR-106 says that gap CIF-G04 asks which file holds the session-start check. `session-menu.md` § Counter check holds it. Name the file, and keep the reference to CIF-G03.                                                                                                                                                                                                   | `validation-rules.md:583`; `session-menu.md:5`                                                                              | `domain-modeling-agent` | open   |
| `docs/spec/entity-model.md`                  | The note on COUNTER_REMOTE_SETTING says that gap CIF-G06 asks whether the setting stays on a decline. `virgil.md` answers that it stays.                                                                                                                                                                                                                                    | `entity-model.md:973`; `virgil.md:308`                                                                                      | `domain-modeling-agent` | open   |
| `docs/spec/state-machines.md`                | `RESUMING` has no event for an `origin` that does not answer. The move then ends with "cannot read refs/ids/counters on <remote>" and "the move changed nothing". The case table of the move contract has no row for it either. Add the event, with REFUSED as its target.                                                                                                  | `next-id:812` (`_origin_counter`), called from `move_to_origin` at `:844`                                                   | `domain-modeling-agent` | open   |
| `docs/spec/glossary.md`                      | Marker Commit says the move leaves it "after the move". The move sets it before the push, and it stays after a refused push (DEC-16). Say that the move sets it before the push.                                                                                                                                                                                            | `glossary.md:128`; BR-102                                                                                                   | `domain-modeling-agent` | open   |
| `docs/arc42/06_runtime_view.md`              | In 6.16 and 6.16.1, step 4 says that the adapter fetches `refs/ids/counters` from the Local Counter. `next-id` reads it in place with `git -C <local> rev-parse` and `git show`. 6.16 also leaves out the second `git ls-remote` after a refused push.                                                                                                                      | `06_runtime_view.md`, step 4 of both diagrams and the third key point of 6.16; `next-id:706` (`read_local_counter`), `:897` | `architecture-agent`    | open   |
| `docs/arc42/05_building_block_view.md`       | The last paragraph of 5.11 lists the Move Lifecycle states that the adapter performs and leaves out `RECHECKING`.                                                                                                                                                                                                                                                           | `05_building_block_view.md`, § 5.11, last paragraph; `state-machines.md`, Move Lifecycle                                    | `architecture-agent`    | open   |
| `backlog/ST-0380.md`                         | Two acceptance criteria still expect both refs unchanged and C back on the local counter. The story is `done`, and the tests check DEC-16.                                                                                                                                                                                                                                  | `ST-0380.md:90`, `:91`                                                                                                      | `planning-agent`        | open   |
| `backlog/ST-0376.md` to `ST-0385.md`         | No story has a `tests:` field. Each story names its test files in `touches:` and its contracts in its Quality Gates. Nothing breaks without the field, so the run recommends no change.                                                                                                                                                                                     | `grep -l '^tests:' backlog/ST-03[78]*.md` finds no file                                                                     | `planning-agent`        | open   |

## Scope map and `@`-references

The scope map holds the 17 counter-ids-fitting Rules, and the feature file
holds the same 17. So the run found no new Rule and no dropped Rule. All ten
stories are `done`. Each row below asks the requirements agent to move a Rule
from `specified` to `implemented`, to fill its Feature Link, and to add the
proposed `@`-references to the feature file. Seven Rules carry a Rule-level
reference, and one Scenario carries its own.

| Artifact                                                                                                                               | Drift                                                                                                                                                                                                                                                                             | Evidence                                                                | Owner                | Status |
| -------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | -------------------- | ------ |
| `docs/spec/scope-map.md:200`, Rule "User confirms the seed of the counter in a fitting step"                                           | Move to `implemented`. Feature Link `@packages/factory/agents/virgil.md`, the Rule's reference.                                                                                                                                                                                   | `virgil.md` § 4; tests CIF-01-LN-01, CIF-01-LN-02, CIF-01-IT-01         | `requirements-agent` | open   |
| `docs/spec/scope-map.md:201`, Rule "VIRGIL points next-id at the project's own repository when origin is missing"                      | Move to `implemented`. Feature Link `@packages/factory/agents/virgil.md`. The worktree Scenario takes `@packages/factory/scripts/next-id::resolve_remote`.                                                                                                                        | `next-id:325`; tests CIF-02-LN-01, CIF-02-IT-01                         | `requirements-agent` | open   |
| `docs/spec/scope-map.md:202`, Rule "User walks the seed step in a greenfield project"                                                  | Move to `implemented`. Feature Link `@packages/factory/agents/virgil.md`. The `ST-0001` Scenario takes `@packages/factory/scripts/next-id::plan`.                                                                                                                                 | `next-id:598`; tests CIF-03-LN-01, CIF-03-IT-01                         | `requirements-agent` | open   |
| `docs/spec/scope-map.md:203`, Rule "User sees the fitting finished only when all six fitting keys are true"                            | Move to `implemented`. Feature Link `@packages/factory/scripts/init-factory::_fitting_status`. The Outline takes one bare `@` line for each of the four `AGENTS.*.md` files.                                                                                                      | `init-factory:2647`; tests CIF-04-CT-01, CIF-04-LN-01                   | `requirements-agent` | open   |
| `docs/spec/scope-map.md:204`, Rule "next-id --plan-seed prints one seed command from the highest number of each ID prefix"             | Move to `implemented`. Feature Link `@packages/factory/scripts/next-id::plan_seed`, in place of `::PREFIXES`. The branch Scenarios take `::_branch_trees`; the body text, register, and todo Scenarios take `::ids_in_tree`; the gap, no-pair, and zero Scenarios take `::plan`.  | `next-id:579`, `:598`, `:610`, `:656`; tests CIF-05-CT-01, CIF-05-IT-01 | `requirements-agent` | open   |
| `docs/spec/scope-map.md:205`, Rule "next-id --plan-seed counts an old file name by its number and warns about it"                      | Move to `implemented`. Feature Link and Rule reference `@packages/factory/scripts/next-id::count_name`.                                                                                                                                                                           | `next-id:540`; tests CIF-06-CT-01, CIF-06-IT-01                         | `requirements-agent` | open   |
| `docs/spec/scope-map.md:206`, Rule "next-id --plan-seed checks the remote before it plans a seed"                                      | Move to `implemented`. Feature Link and Rule reference `@packages/factory/scripts/next-id::plan_seed`. The no-origin Scenario takes `::resolve_remote`; the moved-counter Scenario takes `::MovedCounter`.                                                                        | `next-id:161`, `:656`; tests CIF-07-IT-01 to CIF-07-IT-04               | `requirements-agent` | open   |
| `docs/spec/scope-map.md:207`, Rule "ID Producer claims an ID from the local counter in a project without origin"                       | Move to `implemented`. Feature Link `@packages/factory/scripts/next-id::resolve_remote`, the Rule's reference. The moved-counter Scenario takes `::MovedCounter`.                                                                                                                 | tests CIF-08-CT-01, CIF-08-IT-01 to CIF-08-IT-04                        | `requirements-agent` | open   |
| `docs/spec/scope-map.md:208`, Rule "VIRGIL offers to move a local counter to origin at the session start"                              | Move to `implemented`. Feature Link and Rule reference `@packages/factory/config/session-menu.md`. The hook Scenario keeps its reference.                                                                                                                                         | `session-menu.md:5`; tests CIF-09-LN-01, CIF-09-IT-01                   | `requirements-agent` | open   |
| `docs/spec/scope-map.md:209`, Rule "next-id --move-to-origin moves the local counter to an origin without a counter"                   | Move to `implemented`. Feature Link and Rule reference `@packages/factory/scripts/next-id::move_to_origin`.                                                                                                                                                                       | `next-id:844`; tests CIF-10-CT-01, CIF-10-IT-01                         | `requirements-agent` | open   |
| `docs/spec/scope-map.md:210`, Rule "next-id --move-to-origin leaves both counters as they are when origin holds one or the push fails" | Move to `implemented` once RECON-0030 renames the Rule, and take the new title. Feature Link and Rule reference `@packages/factory/scripts/next-id::_after_refusal`.                                                                                                              | `next-id:897`; tests CIF-11-IT-01, CIF-11-IT-02                         | `requirements-agent` | open   |
| `docs/spec/scope-map.md:211`, Rule "next-id --move-to-origin hands out no number twice while ID claims run during the move"            | Move to `implemented`. Feature Link and Rule reference `@packages/factory/scripts/next-id::mark_loop`. The after-marker Scenario takes `::MovedCounter`.                                                                                                                          | `next-id:787`; tests CIF-12-IT-01, CIF-12-IT-02                         | `requirements-agent` | open   |
| `docs/spec/scope-map.md:212`, Rule "init-factory derives counter_seeded from the remote that next-id uses"                             | Move to `implemented`. The Rule points at `::_derive_fitting_keys`, which the build did not change and which reads no counter. Point it at `@packages/factory/scripts/init-factory::check_counter`, and add `::record_counter_seeded` to the Outline and the greenfield Scenario. | `init-factory:3087`, `:3157`; four `test_st_0378` tests                 | `requirements-agent` | open   |
| `docs/spec/scope-map.md:213`, Rule "ID Producer names the literal ID prefix at each step that creates an indexed artifact"             | Move to `implemented`. Rule references: one bare `@` line for each producer file of the Outline. The two-step Scenario takes `@packages/factory/skills/reconcile-spec/SKILL.md`.                                                                                                  | tests CIF-14-LN-01, CIF-14-LN-02                                        | `requirements-agent` | open   |
| `docs/spec/scope-map.md:214`, Rule "ID Producer that adds a todo entry names next-id T"                                                | Move to `implemented`. Rule reference `@packages/factory/rulebooks/conventions/todo-format.md`. The `write-prd` Scenario takes `@tests/factory/test_counter_ids_text.py::todo_writers`.                                                                                           | `test_counter_ids_text.py:375`; tests CIF-15-LN-01, CIF-15-LN-02        | `requirements-agent` | open   |
| `docs/spec/scope-map.md:215`, Rule "User finds every ID prefix in one table in id-prefixes.md"                                         | Move to `implemented`. Rule reference `@packages/factory/rulebooks/conventions/id-prefixes.md`. The Outline takes bare `@` lines for `rules.md`, `branching-policy.md`, and `finding-format.md`; the tag Scenario takes `finding-format.md`.                                      | tests CIF-16-LN-01 to CIF-16-LN-03                                      | `requirements-agent` | open   |
| `docs/spec/scope-map.md:216`, Rule "User sees the text test fail when an ID producer or the prefix table drifts from next-id"          | Move to `implemented`. Rule reference `@tests/factory/test_counter_ids_text.py::check_id_prefix_table`. The todo-writer Scenario takes `::todo_writer_problems`.                                                                                                                  | `test_counter_ids_text.py:193`, `:387`; test CIF-17-CT-01               | `requirements-agent` | open   |

The merge into `dev` is script-owned and has no pull request. So the list of
newly discovered Rules belongs here: the run discovered none.

## Code defects filed

None. The run found no place where the code breaks a rule that the
specification states correctly. In RECON-0030, the specification is wrong and
the code is right.

## Agent context and test traceability

Every `Read:` path in `docs/agent-context.md` resolves in the main checkout.
The two glob paths, `docs/adr/*.md` and `docs/arc42/*.md`, match files. Its
three sections match the project, so the run wrote no row for it.

Every contract in the three Ownership Resolution tables of
`backlog/epics-counter-ids-fitting.md` has a row in the QA strategy and a
test in `tests/factory/`. Five of those tests carry no marker, as RECON-0032
describes. So the run filed no `QA` finding.

## Verdict on the merge into `dev`

Do not merge yet. RECON-0030 blocks, because the feature file is the
acceptance specification and it contradicts DEC-16. The code needs no change.
Once the requirements agent has renamed Rule CIF-11 and fixed its two
Scenarios, a recheck of RECON-0030 alone decides the merge. The three `minor`
findings and the notes can follow on `dev`.

## Recheck

The recheck read `feature/counter-ids-fitting` at
`4b3a875d07dcf3c655b513f01a4d9b97df6e46b8`. Both rechecked findings hold
as fixed:

- **RECON-0030 is resolved.** Rule CIF-11 now keeps the marker and the
  setting. Both Scenarios expect the marker commit with parent C, and the
  second one resumes the move once the remote accepts pushes. This matches
  DEC-16, BR-102, and the tests with the markers CIF-11-IT-01 and
  CIF-11-IT-02.
- **RECON-0031 is fixed.** The rows CIF-11-IT-01 and CIF-11-IT-02 describe
  the marker and name `test_st_0380_a_counter_on_origin_refuses_the_move` and
  `test_dec_16_a_refused_push_keeps_the_marker_and_a_second_move_resumes`.
  Both tests exist. The run removed its line from the register.
- **The scope map is reconciled.** All 17 Rules are `implemented`, and row
  210 carries the new title of Rule CIF-11.

Two notes stay open and block nothing:

- The new step "the next local ID claim fails and names the remote" has no
  assertion in CIF-11-IT-02. CIF-12-IT-02 checks a claim after the marker, so
  the behaviour is tested. Owner: `test-strategy-agent`.
- `backlog/epics-counter-ids-fitting.md:238` still lists the old Rule title.
  Owner: `planning-agent`.

No finding blocks the merge into `dev` any more. RECON-0032, RECON-0033, and
the notes above can follow on `dev`.
