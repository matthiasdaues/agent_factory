---
type: reconcile-spec
title: Reconciliation of the counter-ids specification and architecture
date: 2026-11-06
status: pass
reviewer: reconciliation-agent
findings_filed: 0
story: counter-ids
scope: feature/counter-ids at d0a78a5c40327c1f7e4c9a204ab5e766a7e0c44b against dev at 9b60fd702d36cb288bc4d5a51281132b103b4e60 — next-id, the init-factory counter check, and the producer and rule texts, against counter-ids.feature, the counter-ids sections of the spec, the scope map, the QA strategy, the ID Allocation architecture, ADR-0031, and ADR-0032
---

# Reconciliation of the counter-ids specification and architecture

## Result

The code matches the specification in every behaviour that a Scenario or a
rule checks. No finding blocks the merge into `dev`. The run recorded six
`minor` findings as register lines: five in the document class and one in the
code class. The largest one is BUG-0117: the counter port in `next-id` has the
operations `read` and `push`, while DEC-11 and the architecture name `claim`
and `seed`. The other drift is stale text: two gaps that the code has answered,
a wrong worst-case bound in BR-076, a heading, the prefix examples, and the
test statuses of the QA strategy. Next, the human reads the tables below and
decides for each row whether the owner fixes the text or the code changes.
Then the backfeed step of `documentation-update` runs on the open rows.

## Scope

The run compared the code of `git diff dev...feature/counter-ids` at
`d0a78a5c`:

- `packages/factory/scripts/next-id`
- `check_counter` and its call in `packages/factory/scripts/init-factory`
- the producer and rule texts: `create-backlog/SKILL.md`, `finding-format.md`,
  `bug-fix.md`, `todo-format.md`, `write-adr/SKILL.md`, `rules.md`,
  `branching-policy.md`, and `planning-agent.md`
- the tests in `tests/factory/` for `next-id`, the race, `init-factory`, the
  texts, and the guardrail hook

It compared them against these documents on the same commit:

- `docs/spec/features/counter-ids.feature` and `docs/spec/scope-map.md`
- the Counter IDs sections of `entity-model.md`, `interface-contracts.md`,
  `validation-rules.md` (BR-068 to BR-076), `state-machines.md`, and
  `glossary.md`
- `docs/spec/work/counter-ids-gaps.md` and
  `docs/spec/work/counter-ids-qa-strategy.md`
- the ID Allocation elements of `docs/spec/architecture.dsl`, arc42 5.11,
  6.15, 8.18, QS-18 to QS-21, ADR-0031, and ADR-0032
- `backlog/ST-0368.md` to `ST-0375.md` and `backlog/epics-counter-ids.md`
- `docs/agent-context.md`

The classification follows the accepted proposal `finding-classification.md`,
as the brief requires. No artifact of the run is in use, because nothing
outside `feature/counter-ids` encodes the counter-ids text or runs `next-id`.
So no finding is `critical`. The run did not run the test suite.

## Earlier rows

No earlier reconciliation report covers counter-ids. The run checked the three
drifts that the brief names as handled, and all three hold:

- BR-076 now states that a claim keeps the user's ssh command and adds
  ` -o BatchMode=yes`. `ssh_command_with_batch_mode` in `next-id` does exactly
  that (row of ST-0370, `71abb4ac`).
- The QA strategy names the checked setup for ten stale leases (CID-QG01), and
  its row CID-03-IT-02 names the QS-19 test
  `test_st_0369_eight_claims_at_once_all_get_their_own_id` (row of ST-0369,
  `189205df`).
- `ARCH` and `QA` are in `PREFIXES` of `next-id`, in BR-068, the entity model,
  arc42 5.11, the Feature description, and the producer table of the feature
  file (DEC-25, `585dda18`). Two places still list ten prefixes: RECON-0025
  and a note below.

## Discrepancy table

Each finding ID names a register line in `docs/findings/register/`.

| Artifact                                    | Drift                                                                                                                                                                                                                                                                                                                                                                                                           | Evidence                                                                                                                                                                                                 | Owner                   | Status |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- | ------ |
| `docs/spec/features/counter-ids.feature`    | RECON-0025 (minor, spec-stale). The Examples of the Scenario Outline "Every ID prefix of the list can be claimed" list ten prefixes. `ARCH` and `QA` are missing. Add both rows.                                                                                                                                                                                                                                | `counter-ids.feature:121`; `PREFIXES` at `packages/factory/scripts/next-id:52`; the parametrized test at `tests/factory/test_next_id.py:491` claims all twelve                                           | `requirements-agent`    | open   |
| `docs/spec/validation-rules.md`             | RECON-0026 (minor, inconsistent). The heading reads "Counter IDs (`next-id`, BR-068…BR-075)", but the section holds BR-076. Rename it to BR-068…BR-076 and update the four links to its anchor.                                                                                                                                                                                                                 | `validation-rules.md:475`; the anchor `#counter-ids-next-id-br-068br-075` in `interface-contracts.md:1066`, `06_runtime_view.md:875`, `08_crosscutting_concepts.md:490`, `counter-ids-qa-strategy.md:10` | `domain-modeling-agent` | open   |
| `docs/spec/validation-rules.md`             | RECON-0027 (minor, incorrect). BR-076 says that ten stale leases end a claim "after at most twenty git calls of 30 seconds each and nine waits". `next-id` puts the limit on every git call of a claim: one `git init`, then six calls per try (fetch, rev-parse, show, mktree, commit-tree, push). So the worst case is 61 calls. Count all 61, or state the bound for the twenty calls that reach the remote. | `next-id:238` (`throwaway`), `next-id:301` and `:334` (`RemoteCounter.read` and `.push`), `next-id:356` to `:359`; QS-20 takes its response measure from this bound                                      | `domain-modeling-agent` | open   |
| `docs/spec/interface-contracts.md`          | RECON-0028 (minor, spec-stale). The rows Writes and Seed output still call CID-G06 and CID-G03 open. The code answers both: a seed runs in a throwaway repository, and its output holds the `start` and pair lines without the token line. State both answers, or ask the stakeholder first.                                                                                                                    | `next-id:390` (`with throwaway() as repo`), `next-id:402` (`number_lines`, no token); `interface-contracts.md`, rows Writes and Seed output of § `packages/factory/scripts/next-id`                      | `domain-modeling-agent` | open   |
| `docs/spec/work/counter-ids-qa-strategy.md` | RECON-0029 (minor, spec-stale). 37 of the 39 test rows still say `planned`, although the named tests exist. The CID-10 rows name a file whose tests carry no CID marker, and a note says "for all ten prefixes". Set each built test to `implemented`, name the three `init-factory` tests, and say twelve prefixes. CID-11-AC-01 stays `planned`.                                                              | QA strategy lines 63 to 100 and 122; `tests/factory/test_init_factory_counter.py:59`, `:70`, `:78`; every other CID test ID appears in `tests/factory/`                                                  | `test-strategy-agent`   | open   |

## Notes

These rows need a decision but change no behaviour. They stay in this report
and get no register line.

| Artifact                                 | Drift                                                                                                                                                                                                                                                                                                                       | Evidence                                                                                                             | Owner                   | Status |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | ----------------------- | ------ |
| `docs/spec/entity-model.md`              | The note on THROWAWAY_REPOSITORY still asks whether `--seed` uses one (CID-G06). The code answers yes, as RECON-0028 describes.                                                                                                                                                                                             | `entity-model.md`, § Counter IDs Entities, Notes; `next-id:390`                                                      | `domain-modeling-agent` | open   |
| `docs/spec/work/counter-ids-gaps.md`     | CID-G03 and CID-G06 stand as open gaps. The code answers both, as RECON-0028 describes. Mark them answered once the human accepts the answers.                                                                                                                                                                              | `counter-ids-gaps.md`, Ambiguous Wording and Other Gaps; `next-id:390`, `:402`                                       | `requirements-agent`    | open   |
| `docs/spec/interface-contracts.md`       | The Failure row says the proposal names no exit code other than `0`. `next-id` exits `1` on a failed claim or seed and `2` on a usage error, as its docstring states. `next-id --seed` without a number exits `1`, although it is a usage error. Name the codes in the contract, or keep the row.                           | `next-id` docstring, "Exit code"; `next-id:121` (`--seed needs a number`, exit 1); `next-id:421` (`p.error`, exit 2) | `domain-modeling-agent` | open   |
| `docs/spec/interface-contracts.md`       | The Credentials row names only global config, a credential helper, or an SSH key. Since the IMPL-0004 fix, the clone's own `core.sshCommand` also reaches the claim, because `next-id` reads it in the current directory. The row is still true, but a user with a per-clone key cannot learn from it that the claim works. | `ssh_command_with_batch_mode` in `next-id`; code review pass 2, notes on the fix                                     | `domain-modeling-agent` | open   |
| `docs/spec/features/counter-ids.feature` | The Rule "User learns from init-factory how to seed the counter" points at `init-factory::main`. The behaviour lives in `check_counter`. Point the reference at `@packages/factory/scripts/init-factory::check_counter`.                                                                                                    | `init-factory:3046` (`check_counter`), called from `main` in section "Counter IDs"                                   | `requirements-agent`    | open   |
| `backlog/epics-counter-ids.md`           | The ownership row for CID-02-IT-01 to CID-02-IT-05 says "all ten prefixes". BR-068 holds twelve since DEC-25.                                                                                                                                                                                                               | `epics-counter-ids.md:185`                                                                                           | `planning-agent`        | open   |
| `backlog/ST-0368.md` to `ST-0375.md`     | No story has a `tests:` field. No story of the 366 in `backlog/` has one, and each counter-ids story names its test files in `touches:`. Nothing breaks without the field, so the run recommends no change.                                                                                                                 | `grep -l '^tests:' backlog/ST-*.md` finds no file                                                                    | `planning-agent`        | open   |

## Scope map and `@`-references

The scope map holds the 11 counter-ids Rules, and the feature file holds the
same 11. So the run found no new Rule and no dropped Rule. Each row below asks
the requirements agent to move a Rule from `specified` to `implemented`, to
fill its Feature Link, and to add the proposed `@`-references to the feature
file. Two Rules already carry a Rule-level reference. No Scenario carries one.

| Artifact                                                                                               | Drift                                                                                                                                                                                                                                                                                                                                     | Evidence                                                                                | Owner                | Status |
| ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | -------------------- | ------ |
| `docs/spec/scope-map.md:168`, Rule "User seeds the counter once for a project"                         | Move to `implemented`. Feature Link and Rule reference `@packages/factory/scripts/next-id::seed`. The Outline of wrong arguments takes `::parse_seed`; the Scenario without a remote takes `::resolve_remote`.                                                                                                                            | `next-id:386`; tests CID-01-CT-01 and CID-01-IT-01 to CID-01-IT-06 in `test_next_id.py` | `requirements-agent` | open   |
| `docs/spec/scope-map.md:169`, Rule "User gets the next ID of an ID prefix from an ID claim"            | Move to `implemented`. Feature Link and Rule reference `@packages/factory/scripts/next-id::claim`. The Scenarios on lines and on the ID form take `::raise_line`; the Scenario without a user name takes `::_commit`; the Scenario on URL rewrites takes `::resolve_remote`.                                                              | tests CID-02-CT-01 and CID-02-IT-01 to CID-02-IT-05                                     | `requirements-agent` | open   |
| `docs/spec/scope-map.md:170`, Rule "User gets different IDs from two ID claims at the same time"       | Move to `implemented`. Feature Link and Rule reference `@packages/factory/scripts/next-id::claim_loop`. The stale-lease Scenario also takes `::is_stale_lease`.                                                                                                                                                                           | `next-id:347`; tests CID-03-CT-01, CID-03-CT-02, CID-03-IT-01, CID-03-IT-02             | `requirements-agent` | open   |
| `docs/spec/scope-map.md:171`, Rule "User sees a failed ID claim stop and name its reason"              | Move to `implemented`. Feature Link and Rule reference `@packages/factory/scripts/next-id::claim_loop`. Per Scenario: ten stale leases `::claim_loop`; another refusal `::RemoteCounter.push`; missing counter and unreachable remote `::RemoteCounter.read`; no `origin` `::resolve_remote`; a prefix outside the list `::check_prefix`. | tests CID-04-CT-01 and CID-04-IT-01 to CID-04-IT-06                                     | `requirements-agent` | open   |
| `docs/spec/scope-map.md:172`, Rule "User makes an ID claim on a named remote without a clone"          | Move to `implemented`. Feature Link and Rule reference `@packages/factory/scripts/next-id::resolve_remote`.                                                                                                                                                                                                                               | tests CID-05-IT-01, CID-05-IT-02                                                        | `requirements-agent` | open   |
| `docs/spec/scope-map.md:173`, Rule "User keeps the clone unchanged by an ID claim"                     | Move to `implemented`. Feature Link and Rule reference `@packages/factory/scripts/next-id::throwaway`.                                                                                                                                                                                                                                    | `next-id:238`; tests CID-06-IT-01, CID-06-IT-02                                         | `requirements-agent` | open   |
| `docs/spec/scope-map.md:174`, Rule "User gets every new indexed artifact numbered by next-id"          | Move to `implemented`. Rule references: one bare `@` line for each of the five producer files of the Outline. The ADR Scenario takes `@packages/factory/skills/write-adr/SKILL.md`; the split-story Scenario takes `@packages/factory/skills/create-backlog-slice-story/SKILL.md`.                                                        | tests CID-07-LN-01 to CID-07-LN-03 in `test_counter_ids_text.py`                        | `requirements-agent` | open   |
| `docs/spec/scope-map.md:175`, Rule "User commits an indexed artifact on any branch"                    | Move to `implemented`. Rule references: bare `@` lines for `rules.md`, `branching-policy.md`, and `planning-agent.md`. The two-session Scenario takes `@packages/factory/scripts/next-id::claim`.                                                                                                                                         | tests CID-08-LN-01, CID-08-IT-01                                                        | `requirements-agent` | open   |
| `docs/spec/scope-map.md:176`, Rule "User lets an agent push the counter through next-id in both modes" | Move to `implemented`. The Rule keeps its reference to the hook. The Outline on `rules.md` takes `@packages/factory/rulebooks/rules.md`.                                                                                                                                                                                                  | tests CID-09-LN-01, CID-09-CT-01                                                        | `requirements-agent` | open   |
| `docs/spec/scope-map.md:177`, Rule "User learns from init-factory how to seed the counter"             | Move to `implemented`. Feature Link `@packages/factory/scripts/init-factory::check_counter`, as the note on the Rule reference proposes.                                                                                                                                                                                                  | `init-factory:3046`; three tests in `test_init_factory_counter.py`                      | `requirements-agent` | open   |
| `docs/spec/scope-map.md:178`, Rule "Stakeholder checks the ID claim against GitHub"                    | Keep `specified`. ST-0371 is still `pending`, so the stakeholder's run on GitHub has not happened. No product code implements this Rule. Its Scenario can take `@tests/factory/next_id_race.py::main`, the harness the stakeholder runs.                                                                                                  | `backlog/ST-0371.md`, `status: pending`; `next_id_race.py:197`                          | `requirements-agent` | open   |

The merge into `dev` is script-owned and has no pull request. So the list of
newly discovered Rules belongs here: the run discovered none.

## Code defects filed

No code defect blocks. One `minor` code finding is a register line in
`docs/findings/register/code.jsonl`:

- **BUG-0117: the counter port does not have the operations of DEC-11.**
  DEC-11, ADR-0031, the DSL, arc42 5.11, and 6.15 give the counter port the
  operations `claim` and `seed`, and they put the retry and the wait in the
  git-ref adapter. In `next-id`, the protocol `Counter` has `read` and `push`
  (`next-id:276`). `claim_loop` in the script core runs the retry and the wait
  (`next-id:347`), and `seed` reaches git without the port (`next-id:386`).
  Every behaviour that BR-071 to BR-073 require holds. The cost falls on a
  second backend, which ADR-0031 expects: it must bring its own seed and fit a
  lease-shaped `read` and `push`, instead of only implementing `claim` and
  `seed`. Fix: move the loop and the seed behind a port with `claim` and
  `seed`, or ask the architecture agent to describe the port as built. The
  human decides which side changes.

## Agent context and test traceability

Every `Read:` path in `docs/agent-context.md` resolves in the main checkout.
Its three sections (cross-cutting, technical, and domain concerns) match the
project. The run wrote no row for it.

Every contract in the three Ownership Resolution tables of
`backlog/epics-counter-ids.md` has a test in a file that the owning story
touches. The CID-10 tests and the QS-19 test carry no CID marker, as
RECON-0029 describes. So the run filed no `QA` finding.
