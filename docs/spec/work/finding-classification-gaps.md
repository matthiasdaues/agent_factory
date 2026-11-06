# Gaps Report: finding-classification

Generated: 2026-11-06
Source: [finding-classification.md](../../proposals/finding-classification.md)

The requirements agent ran this pass as a child agent, without the stakeholder. Each point where it would have asked the stakeholder is a question in [Questions for the Stakeholder](#questions-for-the-stakeholder) or a choice in [Choices made without the stakeholder](#choices-made-without-the-stakeholder).

## Actor-Goal Matrix

Six actors see an outcome of this feature. The reviewer agent is any agent or skill that files findings, such as `fagan-review` or `security-review`. The proposal-review agent gets its own Rule, because its rows follow a two-question rule and stay in the proposal. The orchestrator is the agent that starts each step of a playbook run. `finding-lint` is the gate that checks the recorded values. The agent under the hook `guard-human-fields` is any agent whose tool call the hook answers. The stakeholder is the human who owns the project, as the [glossary](../glossary.md) defines.

| ID    | Actor                 | Goal                                                        | Rule                                                                                         | Status    |
| ----- | --------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------- | --------- |
| FC-01 | Reviewer agent        | Find the classification rules in one rulebook               | Rule: Reviewer agent finds the classification rules in one rulebook                          | specified |
| FC-02 | Reviewer agent        | Classify a finding by the class of its material             | Rule: Reviewer agent classifies a finding by the class of its material                       | specified |
| FC-03 | Reviewer agent        | Get a document, code, or runtime severity                   | Rule: Reviewer agent gets a document, code, or runtime severity from the consequence tree    | specified |
| FC-04 | Reviewer agent        | Get a security severity                                     | Rule: Reviewer agent gets the severity of a security finding from the bug bar                | specified |
| FC-05 | Reviewer agent        | Get an architecture severity                                | Rule: Reviewer agent gets the severity of an architecture risk from the matrix               | specified |
| FC-06 | Reviewer agent        | File a blocking finding                                     | Rule: Reviewer agent files a blocking finding as a finding file                              | specified |
| FC-07 | Reviewer agent        | Record a minor finding                                      | Rule: Reviewer agent records a minor finding as one register line                            | specified |
| FC-08 | Proposal-review agent | Rate each Appendix row                                      | Rule: Proposal-review agent rates each Appendix row with two questions                       | specified |
| FC-09 | Reviewer agent        | Report counts on the shared scale                           | Rule: Reviewer agent reports its counts on the shared scale                                  | specified |
| FC-10 | `finding-lint`        | Reject recorded values that break the rules                 | Rule: finding-lint rejects a finding whose recorded values break the classification rules    | specified |
| FC-11 | `finding-lint`        | Check `in_use` against git                                  | Rule: finding-lint checks in_use against git for code, runtime, and security findings        | specified |
| FC-12 | User                  | Run `finding-lint` through `validate` and pre-commit        | Rule: User runs finding-lint through validate and the pre-commit hook                        | specified |
| FC-13 | Orchestrator          | Loop a major finding back until no blocking finding is open | Rule: Orchestrator loops a major finding back to its owner until no blocking finding is open | specified |
| FC-14 | Orchestrator          | Stop the run on an open, unconfirmed critical finding       | Rule: Orchestrator stops the run on an open, unconfirmed critical finding                    | specified |
| FC-15 | Orchestrator          | Show each new minor finding with its `fails_purpose` reason | Rule: Orchestrator shows each new minor finding with its fails_purpose sentence              | specified |
| FC-16 | Stakeholder           | Confirm the stop of a critical finding                      | Rule: Stakeholder confirms the stop of a critical finding after the damage checks            | specified |
| FC-17 | Stakeholder           | Waive a blocking finding                                    | Rule: Stakeholder waives a blocking finding with a reason                                    | specified |
| FC-18 | Agent                 | Learn that only the human writes the human fields           | Rule: Agent is refused when it sets a field that only the human writes                       | specified |
| FC-19 | Test-strategy agent   | State the consequence in the QA triage table                | Rule: Test-strategy agent states the consequence in the QA triage table                      | specified |
| FC-20 | Stakeholder           | Get the open findings migrated                              | Rule: Stakeholder gets the open findings migrated under the new rules                        | specified |
| FC-21 | Stakeholder           | Measure how often two runs agree on the severity            | Rule: Stakeholder measures how often two runs agree on the severity                          | specified |

## Completion Criteria Trace

Each completion criterion of the proposal traces to a Rule or to a gap below.

| Completion criterion (short form)                                                                       | Rule or gap   |
| ------------------------------------------------------------------------------------------------------- | ------------- |
| `finding-classification.md` defines the values, the scale, the tree, and five classes with examples     | FC-01         |
| No other rulebook, skill, or agent in the boundaries defines a severity level                           | FC-01         |
| Each review skill and agent names its review class and links its class section                          | FC-01         |
| `finding-lint` exits `1` on a severity mismatch, with a test per review class                           | FC-10         |
| `finding-lint` exits `1` on `in_use: false` for lines unchanged on `dev`, with six named tests          | FC-11, FC-G07 |
| `finding-lint` checks `in_use` only on a finding new or changed against `HEAD`, with two tests          | FC-11         |
| `finding-lint` exits `1` on a waived finding without companions, and the loop grep skips it             | FC-10, FC-13  |
| `finding-lint` exits `1` on a critical finding without `## Possible damage`, and on a lone confirmer    | FC-10         |
| A `minor` finding adds one register line, and `schema-validate` and `finding-lint` check it             | FC-07, FC-10  |
| `dispatch` and `premerge-check` exit `1` with the stop notice, and run again once confirmed             | FC-14, FC-G05 |
| `guard-human-fields` refuses the two named calls and passes the five named calls                        | FC-18         |
| The pause point shows every new `minor` finding with its `fails_purpose` sentence                       | FC-15, FC-G02 |
| The final summary of a headless run lists each new register line with that sentence                     | FC-15         |
| The QA triage table has a `Consequence` column and no severity column                                   | FC-19         |
| Every adversarial proposal-review row ends with a `Severity:` sentence, and the template lists `waived` | FC-08, FC-17  |
| A child-result envelope carries the four keys                                                           | FC-09         |
| `finding-lint` exits `0` after the migration, and every open finding carries `review_class`             | FC-20, FC-G01 |
| No migrated finding is `open` and `minor`, and each migrated `minor` finding is a register line         | FC-20         |
| No open `critical` finding lacks `stop_confirmed_by` after the migration, and the report counts them    | FC-20         |
| The agreement check reaches 16 of 20 and beats the old rules, recorded in `docs/reviews/`               | FC-21         |

## Missing Rules

None. Every actor-goal pair has a Rule.

## Rules Without Scenarios

None. Every Rule has at least one Scenario.

## Questions for the Stakeholder

The stakeholder answered all eight questions on 2026-11-06. Each question ends with its answer and the Scenarios that carry it.

### FC-G01: Does the migration cover the findings opened after the proposal was accepted?

The proposal migrates 39 open findings. Today 47 findings are open. The eight new ones are SPEC-0055 to SPEC-0058, filed on 2026-11-05, and ATAM-0010 to ATAM-0013, filed on 2026-11-06. None of them carries `review_class`.

- **Migrate every open finding without `review_class` at the time of the migration.** All 47 or more findings pass the pause point. The criterion "every open finding carries `review_class`" holds, and no `minor` finding among the eight keeps blocking.
- **Migrate only the 39 named findings.** The eight stay open without `review_class`. `finding-lint` skips them, so the criterion "every open finding carries `review_class`" fails, and a `minor` one among them keeps the loop running.

Recommendation: migrate every open finding without `review_class`, because only that keeps the criterion and DEC-12 true. The answer settles Rule FC-20 and the size of the migration story.

**Answered:** yes. The migration covers every open finding without `review_class`, 47 today, not only the 39. FC-20 carries the answer in the new Scenario "The migration covers every open finding without review_class" and in the changed Scenario "The stakeholder reviews every result before any file changes".

### FC-G02: Does a `minor` security or architecture finding carry a `fails_purpose` sentence?

A security finding of level Low is `minor`. Its basis holds the effect, the four preconditions, the confidence, and `in_use`, but no `fails_purpose`. The proposal still requires a "no" sentence for `fails_purpose` on every `minor` finding (DEC-27), and the pause point shows that sentence (DEC-22).

- **The sentence applies only to the document, code, and runtime classes.** A Low security finding shows its precondition sentences at the pause point instead. A `minor` architecture risk shows its exposure sentence. `finding-lint` checks the `fails_purpose` sentence only where the basis asks the question.
- **The sentence applies to every class.** The security reviewer writes one more sentence about a question its bug bar never asks. The lint checks it on every `minor` line.

Recommendation: the first option, because the user raises a wrong downgrade by changing an answer that the rule actually uses. The answer settles one lint rule in FC-10 and the pause point in FC-15. The feature file tests the sentence only with a document finding, so it fits both answers.

**Answered:** only the document, code, and runtime classes need the `fails_purpose` sentence on a `minor` finding. FC-10 carries the answer in the two Scenario Outlines "A minor line of the consequence tree classes needs its fails_purpose sentence" and "A minor security or architecture line needs no fails_purpose sentence". FC-15 carries it in "A minor security finding shows its Why this severity line" (FC-C14).

### FC-G03: How does a register line leave the register once its finding is fixed?

Commit `ca3b3ae5` removed RECON-0025 and RECON-0026 from `docs/findings/register/document.jsonl`. The proposal gives a register line no status and no rule for its end.

- **The fix removes the line, and git history keeps it.** The register holds only unfixed findings, as § Register of minor findings says ("every recorded, unfixed finding"). The schema needs no status field, and parallel reviews keep adding lines at the end.
- **The line gets a status field that the fix sets to `resolved`.** The register keeps every line forever. A fix rewrites a line in the middle of the file, so two parallel fixes can collide.

Recommendation: the first option, because it matches the practice of `ca3b3ae5` and keeps the merge property of DEC-33. The answer settles the register schema, which the domain-modeling agent writes, and one more Scenario in FC-07.

**Answered:** the register line is deleted once its finding is fixed, and git keeps the history. FC-07 carries the answer in the new Scenario "The fix of a minor finding deletes its register line" (FC-C13). The register schema needs no status field.

### FC-G04: Can the human raise a `minor` finding after its line is in the register?

The proposal lets the user raise a wrong downgrade at the pause point (DEC-22). A headless run writes the register line first and shows it only in its final summary. Take a headless ATAM review that records the ADR-0026 gap as `minor`. The user reads the summary the next morning and disagrees.

- **The human changes the basis, removes the line, and files a finding file under the same ID.** The finding then blocks the next run like any `major` finding. `guard-human-fields` does not guard the basis, so an agent can do the edit for the human.
- **No path exists after the line is written.** The user opens a new finding by hand, under a new ID, and the old line stays.

Recommendation: the first option, because it keeps one ID per problem. The answer adds one Scenario to FC-15 and one rule to `finding-format.md`.

**Answered:** yes. The human may raise a registered `minor` finding to blocking. It becomes a finding file under the same ID, and its register line is removed. FC-15 carries the answer in the new Scenario "The human raises a registered minor finding to blocking", and FC-17 in the changed Scenario "No override raises a minor finding".

### FC-G05: Which `dispatch` subcommands refuse to run during a stop?

The proposal says that `dispatch` refuses to run while an open, unconfirmed `critical` finding exists. Take BUG-0037 stopping a run in wave 2. The orchestrator wants `dispatch status` to show the ledger, and `dispatch mark-failed ST-0351` to record the failed story.

- **Every subcommand refuses.** The human cannot read the ledger through `dispatch` while the stop holds, and the failed story stays `dispatched` in the ledger.
- **Only the subcommands that start, dispatch, or merge work refuse.** `init`, `prepare-wave`, `prepare-story`, `mark-dispatching`, `mark-dispatched`, `re-dispatch`, `escalate`, `refresh-story`, and `merge-story` refuse. `refresh-story` refuses because it merges into a story branch. `status`, `plan`, `suggest-merge-args`, `verify-story`, `mark-done`, `mark-blocked`, `mark-failed`, `clear-manifest`, and `close-wave` still run, because they read or record state.

Recommendation: the second option, because the stop exists so that the run "must dispatch and merge nothing more". Reading and recording a failure do neither. The answer settles the `dispatch` contract in `docs/spec/interface-contracts.md` and the Scenario "dispatch refuses to run" in FC-14.

**Answered:** only the `dispatch` subcommands that start or merge work refuse during a stop. Reads and status queries stay allowed. FC-14 replaces "dispatch refuses to run" with two Scenario Outlines: "dispatch refuses every subcommand that starts or merges work" and "dispatch still answers reads and status queries during a stop". The split of the subcommands is FC-C12.

### FC-G06: Which `docs/findings/` do `dispatch` and `premerge-check` read?

A story worktree, the feature worktree, and the main checkout each hold their own `docs/findings/`. Take a code review in the feature worktree of `feature/core-artifact-ownership` that files BUG-0037 as `critical` and has not committed it yet. The orchestrator then runs `dispatch prepare-wave 3` from the same worktree.

- **The scripts read `docs/findings/` of the working tree they run in.** The stop holds in that worktree. A `premerge-check` run from the main checkout does not see the uncommitted finding.
- **The scripts read the working tree and every branch of the run.** The stop holds everywhere, but each script must list and read files across branches.

Recommendation: the first option, with the filing rule that a reviewer files its findings in the working tree where the orchestrator runs `dispatch`. That is the practice of today's playbooks. The answer settles the Reads row of both script contracts.

**Answered:** the scripts read `docs/findings/` in the working tree where they run. FC-14 carries the answer in the new Scenario "The scripts read the findings of the working tree they run in". The answer names no filing rule for reviewers, so the specification states none.

### FC-G07: Which git tags count as release tags for the `in_use` check?

The repository holds the tags `v1.0.0`, `v1.1.0-rc`, `1.1.0`, and `orchestrator-v0.1.0`, among others. The proposal names "each release tag" without a pattern.

- **Every tag counts.** Lines at `orchestrator-v0.1.0` and `v1.1.0-rc` make `in_use` true. The check finds more `critical` findings and never misses a released line.
- **Only tags of the form `v<major>.<minor>.<patch>` count.** `1.1.0`, `v1.1.0-rc`, and `orchestrator-v0.1.0` do not count. A line released only under one of those tags passes as not in use.

Recommendation: every tag counts, because the git check is a lower bound and a missed stop does the most harm (DEC-31). The answer settles step 2 of § Line identity in the `finding-lint` contract.

**Answered:** each project defines which git tags count as releases, and the Factory sets no default. When the setting is missing, `finding-lint` fails closed: it exits `1` and names the missing setting. The setting is the key `release_tag_patterns` in the tracked file `docs/factory-settings.yaml`, which the stakeholder chose (FC-C11). FC-11 carries the answer in the changed Scenario "A consumer project skips the installed copy step" and in four new Scenarios: "Only the tags that release_tag_patterns names count as releases", "A missing release setting fails closed", "An empty release setting counts no tag", "A missing release setting does not matter when no git check is due", and "init-factory leaves the release setting to the project". The feature description names the setting.

### FC-G08: Does any subsystem need an area spec?

Step 1d asks the stakeholder which subsystems need more depth than the feature file gives. No stakeholder was present. The one candidate is the `in_use` git check with its line identities, because the proposal explains it at a depth that a Scenario does not hold.

- **No area spec.** The proposal § Line identity and the FC-11 Scenarios are the reference.
- **An area spec `docs/spec/areas/finding-lint.md`.** It holds the comparison steps, the places it checks, and the HEAD rule in prose.

Recommendation: no area spec, because the proposal holds that depth and the domain-modeling agent writes the `finding-lint` contract. The answer settles whether the requirements agent runs again for step 1d.

**Answered:** no area spec is needed.

## Ambiguous Wording

| Location                                             | Step Text                                                   | Issue                                                                                                                         | Suggested Fix                                                                                                     |
| ---------------------------------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Proposal § The consequence tree, `raises_cost`       | "makes later reading, change, or testing measurably harder" | "Measurably" names no measure. The class tables give examples, but no bound.                                                  | "names one concrete later cost, such as a second reading or a function above the CRAP threshold"                  |
| Proposal § Class: architecture                       | "Only architecture review uses this category" (`risk`)      | The lint list does not name the rule. The vocabulary rule covers it only if category vocabularies are per class.              | State that the category vocabulary is per class, and that `risk` belongs only to the architecture class (FC-C08). |
| Proposal § Register of minor findings                | "the story"                                                 | A finding from spec review before the backlog exists has no story. The proposal does not say whether the field may be `null`. | Allow `null` for `story` in each register schema.                                                                 |
| Rule FC-08, Scenario "A major row blocks acceptance" | "Then the major row blocks the transition"                  | The proposal does not name who refuses the transition: the proposal-review agent's disposition or a check.                    | Name the proposal-review agent's disposition `findings` as the block, as today.                                   |

## Choices made without the stakeholder

| ID     | Choice                                                                                                                                                                                                                                                                                                                                                                                             | Reason                                                                                                                                                                                                                                                                                                                         |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| FC-C01 | Step 1d wrote no area spec.                                                                                                                                                                                                                                                                                                                                                                        | No stakeholder was present to name a subsystem. The stakeholder later confirmed that none is needed (FC-G08).                                                                                                                                                                                                                  |
| FC-C02 | The scope map was not rebuilt with `reverse-map`.                                                                                                                                                                                                                                                                                                                                                  | `docs/spec/scope-map.md` exists, and the requirements agent leaves an existing map as it is.                                                                                                                                                                                                                                   |
| FC-C03 | The 21 new scope-map rows link the feature file in the Sources column and leave Feature Link empty.                                                                                                                                                                                                                                                                                                | The existing `specified` rows, such as those of counter-ids, follow this form. The reconciliation agent fills Feature Link after implementation.                                                                                                                                                                               |
| FC-C04 | The feature file names the register fields in words and leaves their JSON keys to the domain-modeling agent.                                                                                                                                                                                                                                                                                       | The lines in `docs/findings/register/` already use the keys `finding`, `story`, `why_this_severity`, and `commit`. The schema is a structure file, which the domain-modeling agent owns.                                                                                                                                       |
| FC-C05 | The Rule of the guard hook names "Agent" as its actor.                                                                                                                                                                                                                                                                                                                                             | The brief names the guard hook as seen by an agent. Any agent can meet the refusal, so the Rule names no single agent.                                                                                                                                                                                                         |
| FC-C06 | The migration Scenarios say "every open finding", not "the 39 open findings".                                                                                                                                                                                                                                                                                                                      | The count changed to 47, and the stakeholder chose to migrate all of them (FC-G01).                                                                                                                                                                                                                                            |
| FC-C07 | No Scenario covers the fallback "the reviewer takes the next plausible number" for finding IDs.                                                                                                                                                                                                                                                                                                    | `next-id` exists in `packages/factory/scripts/` on `dev`, so the fallback has no case left (DEC-32).                                                                                                                                                                                                                           |
| FC-C08 | `finding-lint` rejects the category `risk` outside the architecture class.                                                                                                                                                                                                                                                                                                                         | The proposal states that only architecture review uses `risk`, and the lint checks the category against "the vocabulary of their class".                                                                                                                                                                                       |
| FC-C09 | DEC-40 and DEC-41 enter the feature file as stated rules.                                                                                                                                                                                                                                                                                                                                          | The stakeholder accepted both assumptions with the proposal, as the brief states.                                                                                                                                                                                                                                              |
| FC-C10 | The QA strategy Rule names the test-strategy agent as its actor.                                                                                                                                                                                                                                                                                                                                   | The test-strategy agent writes `docs/spec/work/<feature-name>-qa-strategy.md` from the template, as feature-addition Step 1.1 states.                                                                                                                                                                                          |
| FC-C11 | Decided by the stakeholder. The release setting is the key `release_tag_patterns` in the new tracked file `docs/factory-settings.yaml`. It holds a list of glob patterns, such as `["v[0-9]*"]`. An empty list `[]` is a valid setting and counts no tag. `init-factory` does not write the file. When the file or the key is missing, `finding-lint` exits `1` and names the file and the key.    | `/.agent-factory/` is git-ignored, so a setting there would differ from clone to clone, the same fault as counter-ids PROP-04. A tracked file gives every clone the same setting.                                                                                                                                              |
| FC-C12 | During a stop, `dispatch` refuses `init`, `prepare-wave`, `prepare-story`, `mark-dispatching`, `mark-dispatched`, `re-dispatch`, `escalate`, `refresh-story`, `merge-story`, and `close-wave`. It still runs `status`, `plan`, `suggest-merge-args`, `verify-story`, `mark-done`, `mark-blocked`, `mark-failed`, and `clear-manifest`. The stakeholder moved `close-wave` into the refusing group. | The first group starts work or merges it. `refresh-story` merges into a story branch, and `escalate` grants a new dispatch tier. `close-wave` refuses, because closing a wave lets the next wave start. The second group reads state or records an outcome, which the stakeholder's answer allows as reads and status queries. |
| FC-C13 | The commit that fixes a `minor` finding deletes its register line.                                                                                                                                                                                                                                                                                                                                 | The answer says the line goes once the finding is fixed. No repeat pass reads register lines, so only the fixing commit knows the moment.                                                                                                                                                                                      |
| FC-C14 | The pause point shows a `minor` security or architecture finding with its `**Why this severity:**` line instead of a `fails_purpose` sentence.                                                                                                                                                                                                                                                     | DEC-22 lets the user catch a wrong downgrade. For these classes, the answers that set the severity are the preconditions or the exposure, and the Why line names them.                                                                                                                                                         |
| FC-C15 | `finding-lint` checks the release setting only when a git check is due.                                                                                                                                                                                                                                                                                                                            | A document finding or an unchanged finding needs no tag list, so the lint has nothing to guess there. A commit that touches no code, runtime, or security finding passes in a project without the file or the key.                                                                                                             |

## Other Gaps

These gaps belong to the agents that run after this step. They need no stakeholder answer.

- **Interface contracts (domain-modeling agent).** The proposal sets `external_contract_change: true`. `docs/spec/interface-contracts.md` § Child-result envelope says "counts keyed by severity" and needs the four keys `critical`, `major`, `minor`, and `note`. The file has no entry yet for the finding file, the five register schemas, `finding-lint`, `guard-human-fields`, or the stop notice. The `dispatch` and `premerge-check` entries need the stop and its exit code `1`. The proposal does not say whether the stop notice goes to stdout or stderr. A headless run must carry it into its final summary, so the contract must name the stream. The `dispatch` entry needs the split of FC-C12, and both script entries need the Reads row of FC-G06. The `finding-lint` entry needs the file `docs/factory-settings.yaml`, its key `release_tag_patterns`, and the exit `1` when the file or the key is missing (FC-C11). The new file needs its own contract entry.
- **Envelope example (implementation).** The example in [report-format.md § Child-result envelope](../../../packages/factory/rulebooks/conventions/report-format.md#child-result-envelope) shows three keys. The story that changes `report-format.md` adds `note`.
- **Glossary terms (domain-modeling agent).** The feature file uses these project terms: review class, basis, in use, consequence tree, bug bar, register, stop notice, possible damage, blocking finding, and orchestrator. This pass did not write `docs/spec/work/term-candidates.md`, because the brief limits it to three files.
- **Architecture (architecture agent).** The proposal sets `architecture_change: true`. `docs/spec/architecture.dsl` needs the gate `finding-lint`, the hook `guard-human-fields`, and the dependency of `dispatch` and `premerge-check` on `docs/findings/`.
- **Release setting at install (implementation).** `init-factory` and `update-factory` do not write `docs/factory-settings.yaml`, because the Factory sets no default. The message of `finding-lint` must name the file and the key to add, so a project can recover without reading the specification.
- **Linked headings.** [review-loop-cap.md](../../proposals/review-loop-cap.md) links the proposal headings "Shared severity scale and blocking rule" and "Human override". This specification renames neither heading.

## Deferred Scope

The proposal defers these items, and this specification defines no Rule for them: protection against an agent that hides a human field from `guard-human-fields` (DEC-42), a review class for claim review (DEC-36), the migration of the files that are not `open` (DEC-24), a script for the agreement check, environment data and numeric scoring in the security rating (DEC-05, DEC-20), severity levels for the lint scripts, and a utility tree in arc42 chapter 10 (DEC-19). Rule FC-09 covers only the envelope counts of claim review.
