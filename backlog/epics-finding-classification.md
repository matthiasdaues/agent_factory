---
scope: global
---

# EPICs — Finding Classification

Proposal trace: [finding-classification.md](../docs/proposals/finding-classification.md), accepted at `74e036f1`, with DEC-01 to DEC-64
Specification trace: [finding-classification.feature](../docs/spec/features/finding-classification.feature), [gaps report](../docs/spec/work/finding-classification-gaps.md), [validation-rules.md § Finding classification](../docs/spec/validation-rules.md#finding-classification-br-079br-095), [interface-contracts.md § Finding Classification Contracts](../docs/spec/interface-contracts.md#finding-classification-contracts), [state-machines.md § Finding Lifecycle](../docs/spec/state-machines.md#finding-lifecycle), [schemas/finding-basis.json](../docs/spec/schemas/finding-basis.json)
Architecture trace: [ADR-0034](../docs/adr/0034-one-register-file-per-minor-finding.md), [ADR-0035](../docs/adr/0035-guard-human-fields-in-every-cli.md), [ADR-0036](../docs/adr/0036-typescript-tests-run-as-a-node-test-suite.md), [arc42 § 5.12](../docs/arc42/05_building_block_view.md#512-level-2-component-view----finding-classification), [arc42 § 6.17 to § 6.21](../docs/arc42/06_runtime_view.md#617-a-critical-finding-stops-the-run), [arc42 § 8.19](../docs/arc42/08_crosscutting_concepts.md#819-finding-classification), [QS-24](../docs/arc42/10_quality_requirements.md#qs-24-a-critical-finding-stops-every-dispatch-and-merge), [QS-25](../docs/arc42/10_quality_requirements.md#qs-25-no-agent-writes-a-human-field)
QA strategy trace: [finding-classification-qa-strategy.md](../docs/spec/work/finding-classification-qa-strategy.md), 111 contract-owner rows

Dependency order: four stories start at once: the rulebook (ST-0386), the stop (ST-0397), the Claude Code guard (ST-0400), and the `--plan-seed` change (ST-0404). The lint (E2) starts once the review files and the register schemas exist (ST-0387). The migration (ST-0406) comes last, because it needs the complete lint, the hook, the release setting, and the `--plan-seed` change. The second agreement check (ST-0407) follows it, because the first check failed and the stakeholder chose on 2026-11-08 to sharpen the rulebook and measure again.

## Story waves

| Wave | Stories                                     | Merge order inside the wave                                                                                                                       |
| ---- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| W1   | ST-0386, ST-0397, ST-0400, ST-0404          | any; the four stories share no file except `pyproject.toml`, where ST-0386 adds `FC-*` to the `spec` marker first                                 |
| W2   | ST-0387, ST-0389, ST-0390, ST-0401, ST-0402 | ST-0401 before ST-0402, because both edit `init-factory` and `test_init_factory.py`; ST-0387 before ST-0389, because both regenerate `INDEX.yaml` |
| W3   | ST-0388, ST-0391, ST-0398, ST-0403          | ST-0388 before ST-0398, because both regenerate `INDEX.yaml`; ST-0391 and ST-0403 any                                                             |
| W4   | ST-0392, ST-0393, ST-0399                   | ST-0392 before ST-0393, because both edit `finding-lint`                                                                                          |
| W5   | ST-0394, ST-0395, ST-0396                   | ST-0394, then ST-0395, then ST-0396; the first two edit `finding-lint`, and ST-0394 and ST-0396 both edit `test_update_factory.py`                |
| W6   | ST-0405                                     | alone                                                                                                                                             |
| W7   | ST-0406                                     | alone                                                                                                                                             |
| W8   | ST-0407                                     | alone; it follows ST-0406 so that no later story touches the rulebook before the second measurement                                               |

Every story carries `quality-gates: []`, because `docs/testing.yaml` disables both gates.

## Terms used in every EPIC

The proposal's [§ Design](../docs/proposals/finding-classification.md#design) defines each term. A short reminder:

- **Finding file.** `docs/findings/<ID>.md`, the record of a `critical` or `major` finding.
- **Review class.** The rule that classifies a finding: `document`, `code`, `security`, `architecture`, or `runtime`. The reviewed material decides it, not the review.
- **Basis.** The yes/no answers and fixed choices that the reviewer records. The rule of the class computes the severity from them.
- **In use.** The defective artifact is on `dev` or `main`, at a release tag, or in the installed copy, or an artifact outside the run reads it. The run's feature branch does not count.
- **Register file.** `docs/findings/register/<class>/<ID>.json`, one JSON object for one `minor` finding (ADR-0034).
- **Human field.** A non-null `override_by`, `override_reason`, `stop_confirmed_by`, or `stop_confirmed_reason`, or the status `waived`. Only the stakeholder writes one.
- **Stop.** The refusal of `dispatch` and `premerge-check` to start or merge work while a `critical` finding is unconfirmed.
- **Stop notice.** The text both scripts print during a stop: the finding, its artifact, the `in_use` evidence, each item of `## Possible damage` with its check, and the confirmation step.
- **Installed copy.** `.agent-factory/factory/`, the copy of `packages/factory/` that the CLIs run.

## Rules that hold for every EPIC

- Source edits go to `packages/factory/`, never to `.agent-factory/factory/`.
- No story edits the specification, the architecture, the QA strategy, or `todo.md`. A story that finds a mismatch writes a spec-feedback row.
- Pytest tests carry `@pytest.mark.spec("FC-NN-XX-NN")` with the Test ID of their row. A `node:test` test starts its name with the Test ID.
- Every git test builds its own repository in `tmp_path`, as [§ Test setup](../docs/spec/work/finding-classification-qa-strategy.md#test-setup-on-temporary-git-repositories) defines. No test reads the branches or tags of this project, except FC-20-IT-01.
- Agents do not run `uv run pytest` by hand, because the guardrail hook blocks it. The tests run through the commit hooks.
- A story that changes an agent, skill, convention, or playbook regenerates `packages/factory/INDEX.yaml` in the same commit, and `index-lint --check` passes.
- No story plans a deferred item: protection against a hidden field name (DEC-42), a claim-review class (DEC-36), the 208 files that are not `open` (DEC-24), an agreement-check script, environment data or numeric security scores, lint severity levels, or a utility tree (DEC-19).

## Governance and risk

The proposal declares `assurance: elevated` and two risk domains:

| Risk domain   | What goes wrong                                                                                            | Stories that guard it                                                                                |
| ------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `reliability` | A stop does not fire, because the lint accepts a wrong `in_use: false`, or a stop ends before confirmation | ST-0393, ST-0394, ST-0395 (git check), ST-0397 (stop), ST-0392 and ST-0396 (no lowering at a commit) |
| `security`    | An agent writes a human field and lifts its own block or stop                                              | ST-0400, ST-0401, ST-0402, ST-0403 (the guard in each CLI)                                           |

Each of these stories has `risk_level: high`.

## Choices made without the stakeholder

No stakeholder was present. Each phase that asks for approval took the option below. The stakeholder approves the backlog at playbook step 3.4.

| ID      | Phase           | Choice                                                                                                                                                                                               | Reason                                                                                                                                                   |
| ------- | --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FCP-C01 | 1, EPIC slicing | Five EPICs: classify and file (E1), the lint (E2), the stop and the loop (E3), the guard (E4), and the migration of this repository (E5).                                                            | Each EPIC is one journey of one actor group: the reviewer agent, the user at a commit, the orchestrator, the agent under the guard, and the stakeholder. |
| FCP-C02 | 3, story slices | ST-0386 changes the old rulebooks, `rules.md`, and the envelope example of `report-format.md` together with the new rulebook, and owns FC-09-LN-01.                                                  | All four files lose their own severity definitions in the same edit. The envelope example sits in `report-format.md`.                                    |
| FCP-C03 | 3, story slices | ST-0387 changes the twelve review files, the finding template, the review-report template, and the five register schemas together.                                                                   | Each review file must both name its class and write a `minor` finding as a register file. Two stories would edit the same twelve files twice.            |
| FCP-C04 | 3, story slices | ST-0388 waits for ST-0387.                                                                                                                                                                           | Both edit `proposal-review-agent.md`.                                                                                                                    |
| FCP-C05 | 3, story slices | `finding-lint` grows in six stories: the values (ST-0391), the rules against `HEAD` (ST-0392), the git places (ST-0393), the release tags (ST-0394), the trigger (ST-0395), and the hooks (ST-0396). | Each story makes one group of Scenarios true that a user sees on its own. One story for all of it would hold 60 test rows.                               |
| FCP-C06 | 3, story slices | ST-0396 owns FC-14-IT-10 and waits for ST-0397.                                                                                                                                                      | The test commits a lowering through the pre-commit hook. The hook story is the first that makes it true.                                                 |
| FCP-C07 | 3, story slices | ST-0395 owns the moved-line rule, FC-20-CT-01 and FC-20-IT-02.                                                                                                                                       | The rule is part of the trigger of BR-088, and the migration commit needs it.                                                                            |
| FCP-C08 | 3, story slices | ST-0392 owns FC-15-IT-01, the raise of a register file to a finding file.                                                                                                                            | The test checks the removal rule of BR-110 with its replacing finding file, which ST-0392 introduces.                                                    |
| FCP-C09 | 3, story slices | The stop (ST-0397) and the Claude Code guard (ST-0400) have no dependency.                                                                                                                           | Both read frontmatter that the specification defines. Their demos use hand-written finding files.                                                        |
| FCP-C10 | 3, story slices | ST-0404 makes `--plan-seed` count the register file names and keeps counting the `id` of each `.jsonl` line.                                                                                         | A consumer project keeps its old registers until it migrates. Dropping them would seed below an ID in use.                                               |
| FCP-C11 | 3, story slices | ST-0405 commits `release_tag_patterns: ["v[0-9]*"]`. In this repository it matches 16 tags, `v1.1.0-rc` and `v1.2.0-rc` among them, and leaves out `1.1.0` and `orchestrator-v0.1.0`.                | The pattern is the one of the Scenario Outline. The stakeholder confirms the value, because only the project knows its releases.                         |
| FCP-C12 | 3, story slices | Until ST-0406, `finding-lint` may fail on this repository's own `docs/findings/`. Earlier stories report such a failure and do not edit the finding files.                                           | 19 files already carry `review_class`. The migration owns the repository state, and FC-20-IT-01 lands with it.                                           |
| FCP-C13 | 3, story slices | No story declares the `node:test` suite. `docs/testing.yaml` declares it at baseline (`a6635e62`), and ST-0402 and ST-0403 add their tests to it.                                                    | The completion criterion asks for the declaration and a passing suite. The declaration exists, and the two stories show the suite passes.                |
| FCP-C14 | 4, stories      | All 21 stories are must-have.                                                                                                                                                                        | Each story traces to a completion criterion, or, like ST-0404 and ST-0405, is a precondition of the migration (DEC-54).                                  |
| FCP-C15 | 4, stories      | ST-0404 records the change of BR-099 as a spec-feedback row and edits no specification.                                                                                                              | The brief keeps the specification out of the planner's reach, and the domain-modeling agent owns BR-099.                                                 |

## E1: Classify each finding by one rule and file it by its severity

### Why this EPIC exists

Today six severity scales exist, and their levels are adjectives. So the same review rates a borderline finding differently on two runs, and the review loop changes length by chance. This EPIC gives every reviewer one rulebook, one scale, and a rule per review class that computes the severity from recorded answers. Each review then files a blocking finding as a finding file and a `minor` finding as a register file.

### Actor Goals

- Reviewer agent finds the classification rules in one rulebook
- Reviewer agent classifies a finding by the class of its material
- Reviewer agent gets a document, code, or runtime severity from the consequence tree
- Reviewer agent gets the severity of a security finding from the bug bar
- Reviewer agent gets the severity of an architecture risk from the matrix
- Reviewer agent files a blocking finding as a finding file
- Reviewer agent records a minor finding as one register file
- Proposal-review agent rates each Appendix row with two questions
- Reviewer agent reports its counts on the shared scale
- Test-strategy agent states the consequence in the QA triage table
- Stakeholder measures how often two runs agree on the severity

### Demo

1. Open `packages/factory/rulebooks/conventions/finding-classification.md`. It holds the four values of a finding, the shared scale, the consequence tree, and five class sections with calibration examples.
2. Run `fagan-review` on a story branch whose `premerge-check` lets an empty story pass. The skill names the class `code` and links `Class: code`.
3. The review answers `fails_purpose: true` and files `docs/findings/FAGAN-NNNN.md` with `severity: major`, its `basis`, and its `**Why this severity:**` line.
4. The same review records an unclear comment as `docs/findings/register/code/FAGAN-NNNN.json` with `status: open`. Its envelope reports `{"critical": 0, "major": 1, "minor": 1, "note": 0}`.
5. Open `docs/reviews/` and read the agreement report. The two new runs agree on at least 16 of 20 findings and on more findings than the two old runs.

### Scope

**In:**

- The rulebook `finding-classification.md`: the values, the scale and the blocking rule, the consequence tree, the bug bar, the matrix, the waiver and confirmation rules, and two or three calibration examples per level and class (BR-079 to BR-085).
- `report-format.md`, `finding-format.md` § When to file, `owasp-top-10.md`, and `rules.md` link the rulebook and define no severity. The envelope example carries four keys (BR-093).
- The twelve review skills and agents name their class and link its section. They file blocking findings from the new finding template and write each `minor` finding as a register file under its class schema (BR-086, BR-090, BR-110).
- `finding-format.md` names the two removals of a finding file that leave a register file under the same ID (DEC-56, DEC-60).
- `proposal-review-agent.md` and the proposal template rate each row with two questions and list `waived` as stakeholder-only (BR-094).
- The triage table of `templates/qa-strategy.md` gets a `Consequence` column.
- The agreement check, run once by hand, with its report in `docs/reviews/` (DEC-23, DEC-39).

**Out:**

- `finding-lint`, which checks the recorded values (E2).
- The pause point that shows each new `minor` finding (E3, ST-0399).
- A script for the agreement check (deferred).

### Dependencies

None.

### Boundaries

- Rulebooks: `packages/factory/rulebooks/conventions/` (new `finding-classification.md`; `report-format.md`, `finding-format.md`), `rulebooks/principles/owasp-top-10.md`, `rulebooks/rules.md`
- Templates: `rulebooks/templates/finding.md`, `review-report.md`, `proposal.md`, `qa-strategy.md`
- Schemas: `rulebooks/schemas/` (five new `finding-register-<class>.schema.json`)
- Review files: the twelve files of the Scenario Outline in FC-01
- Contracts: [§ finding file](../docs/spec/interface-contracts.md#docsfindingsidmd--finding-file), [§ register file](../docs/spec/interface-contracts.md#docsfindingsregisterclassidjson--register-file), [§ `finding_counts`](../docs/spec/interface-contracts.md#finding_counts-of-the-child-result-envelope), [§ Proposal review row](../docs/spec/interface-contracts.md#proposal-review-row)
- Tests: `tests/factory/` (new `test_finding_classification_text.py`, `test_finding_register.py`)

### Domain Rules

- The reviewed material decides the class, for any source. Text that agents execute is code.
- The reviewer records the basis; the rule computes the severity. No reviewer picks a severity.
- A finding is blocking when its category is `defect` or `risk` and its severity is `critical` or `major`.
- A `minor` finding is a register file and never a finding file. A `note` stays in the report. A `question` becomes a todo entry.
- A `suggestion` is at most `minor`.
- A waiver keeps the computed severity.

### Size

6 stories.

### Building-Block Inventory

| Story   | Capability                                                | Tier     | Size | Goal                                                                                                                                                     | Basis                                                                                                                                        |
| ------- | --------------------------------------------------------- | -------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0386 | Classify a finding with the one rulebook                  | strong   | L    | A reviewer agent reads one rulebook that computes the severity of each class from the basis, and no other rulebook defines a severity level.             | `report-format.md` and `finding-format.md` define three levels by adjectives; `owasp-top-10.md` uses a fourth scale. Adds the rulebook.      |
| ST-0387 | File each review finding by its computed severity         | standard | L    | Each of the twelve review files names its class, files a blocking finding from the new template, and writes a `minor` finding as one register file.      | The review files define their own levels; the template lacks the new fields; no register schema exists. Adds fields, schemas, and links.     |
| ST-0388 | Rate each proposal review row with two questions          | economy  | S    | The proposal-review agent ends each adversarial row with a `Severity:` sentence from two questions, and the template lists `waived` as stakeholder-only. | `proposal-review-agent.md` rates rows major or note. Adds the two questions.                                                                 |
| ST-0389 | State the consequence in the QA triage table              | economy  | S    | The test-strategy agent fills a triage table with a `Consequence` column, and its actions follow the computed severity.                                  | The triage table in `templates/qa-strategy.md` has a severity column. Replaces it.                                                           |
| ST-0390 | Measure how often two runs agree on the severity          | standard | M    | The stakeholder reads one review report that compares two runs under the new rulebook with two runs under the old rules on 20 fixed findings.            | No measurement exists. Adds four fresh subagent runs and the report.                                                                         |
| ST-0407 | Re-measure the agreement after sharpening two class rules | standard | M    | The stakeholder reads a second agreement report, measured with a sharper document and runtime rule on 20 fresh findings.                                 | The first check failed, 18 of 20 against 20 of 20; two runs split on SPEC-0012 and BUG-0006. Sharpens the two class rules and adds a report. |

### Testability Assessment

The text goals have observable outcomes in the files: section headings, links to class sections, absent severity definitions, required keys of the schemas, and the column of the triage table. Text tests in `test_finding_classification_text.py` and schema checks in `test_finding_register.py` instrument these boundaries. Text tests show only that the instruction exists, not that a reviewer follows it (FC-QG02). The agreement check is the one measurement of the reviewer's judgement, and it is a one-time report, not a test.

### Ownership Resolution

| Contract                                                                   | .feature Rule                                                                                           | Owner   | Rationale                                    |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ------- | -------------------------------------------- |
| FC-01-LN-01: the rulebook holds the values, scale, tree, and five sections | finding-classification.feature#Reviewer agent finds the classification rules in one rulebook            | ST-0386 | introduces the rulebook                      |
| FC-01-LN-02: calibration examples per level, each ID real or invented      | finding-classification.feature#Reviewer agent finds the classification rules in one rulebook            | ST-0386 | introduces the examples                      |
| FC-02-LN-01: the class follows the material, executed text is code         | finding-classification.feature#Reviewer agent classifies a finding by the class of its material         | ST-0386 | introduces the class rule                    |
| FC-04-LN-01: an attack that needs the capability it gains is not a finding | finding-classification.feature#Reviewer agent gets the severity of a security finding from the bug bar  | ST-0386 | introduces the bug bar section               |
| FC-09-LN-01: the envelope example carries four keys                        | finding-classification.feature#Reviewer agent reports its counts on the shared scale                    | ST-0386 | first to change `report-format.md` (FCP-C02) |
| FC-17-LN-01: a waiver keeps the severity; a critical needs confirmation    | finding-classification.feature#Stakeholder waives a blocking finding with a reason                      | ST-0386 | introduces the waiver rules in the rulebook  |
| FC-01-LN-03: the twelve review files link their class section              | finding-classification.feature#Reviewer agent finds the classification rules in one rulebook            | ST-0387 | introduces the links                         |
| FC-05-LN-01: a non-risk names its assumptions                              | finding-classification.feature#Reviewer agent gets the severity of an architecture risk from the matrix | ST-0387 | first to change `atam-review`                |
| FC-06-LN-01: the finding template holds the sixteen fields                 | finding-classification.feature#Reviewer agent files a blocking finding as a finding file                | ST-0387 | introduces the template fields               |
| FC-07-LN-01: the review skills write a minor finding as a register file    | finding-classification.feature#Reviewer agent records a minor finding as one register file              | ST-0387 | introduces the instruction                   |
| FC-07-LN-02: each register schema lists the required keys                  | finding-classification.feature#Reviewer agent records a minor finding as one register file              | ST-0387 | introduces the schemas                       |
| FC-08-LN-01: two questions per row, no critical, `waived` stakeholder-only | finding-classification.feature#Proposal-review agent rates each Appendix row with two questions         | ST-0388 | introduces the row rule                      |
| FC-19-LN-01: the `Consequence` column with three values                    | finding-classification.feature#Test-strategy agent states the consequence in the QA triage table        | ST-0389 | introduces the column                        |

The agreement check (FC-21) has no row; ST-0390 shows it with its report, as [§ One-time checks](../docs/spec/work/finding-classification-qa-strategy.md#one-time-checks) defines.

## E2: Let finding-lint check the recorded values of every finding

### Why this EPIC exists

A rule that computes the severity helps only when someone checks the answers. A reviewer on a feature branch can answer `in_use: false` for lines that already sit on `dev`, and then a stop that should fire does not, as with BUG-0037. This EPIC adds the gate `finding-lint`. It recomputes each severity, checks each structural rule, refuses a lowering or a removal by an agent, and settles `in_use` from git for code, runtime, and security findings.

### Actor Goals

- finding-lint rejects a finding whose recorded values break the classification rules
- finding-lint checks in_use against git for code, runtime, and security findings
- User runs finding-lint through validate and the pre-commit hook

### Demo

1. In a temporary repository, commit `packages/factory/scripts/premerge-check` on `dev` and branch `feature/demo`.
2. Write `docs/findings/FAGAN-0042.md` with `review_class: code`, `fails_purpose: true`, and `severity: minor`. Run `finding-lint`. It exits `1` and names the file and the severity rule.
3. Fix the severity to `major` and set `in_use: false` on lines 100 to 114, which exist unchanged on `dev`. `finding-lint` exits `1` with `artifact lines exist unchanged on dev`.
4. Remove `docs/factory-settings.yaml`. `finding-lint` exits `1` and names the file and the key `release_tag_patterns`.
5. Set `in_use: true` and `harms_downstream: true`, so the severity becomes `critical`, and add `## Possible damage`. `git commit` runs the hook `agent_factory_hook-finding-lint` and succeeds.
6. Run `validate`. Its gate table lists `finding-lint`, and the run exits `0`.

### Scope

**In:**

- `finding-lint` in `packages/factory/scripts/`, Python with the standard library only: the vocabulary, the basis shape, the three severity rules, the structural rules, the status rules, and the register rules (BR-079 to BR-087, BR-090, BR-110).
- The comparison with `HEAD`: no lowering, no removal, no lost `review_class` by an agent, read from the staged version with `--staged` and from the working tree without it (BR-109, BR-110).
- The git check of `in_use` by line identity on `dev`, `main`, `origin/dev`, `origin/main`, each release tag, and the installed copy, also from a linked worktree (BR-088, DEC-30, DEC-49, DEC-50).
- The release setting `release_tag_patterns` in `docs/factory-settings.yaml`, which fails closed when a git check is due (BR-089).
- The trigger: the git check runs only for a file new against `HEAD` or with a changed `basis` or `artifact`, and the moved-line rule for the migration (BR-088, FC-C25).
- The `validate` row, the pre-commit hook, its `hook-metadata.yaml` entry, and the `update-factory` refresh (QS-24).

**Out:**

- Severity levels for the lint itself (deferred).
- The data repair of this repository's findings (ST-0406).

### Dependencies

E1: ST-0391 waits for ST-0387, because the lint validates register files against its schemas. ST-0396 waits for ST-0397 of E3, because FC-14-IT-10 commits a lowering during a stop.

### Boundaries

- Scripts: `packages/factory/scripts/` (new `finding-lint`; `_main_checkout.py`, `schema-validate`, `update-factory`, `init-factory`)
- Configuration: `packages/factory/config/pre-commit-config.yaml`, `hook-metadata.yaml`
- Skill: `packages/factory/skills/validate/SKILL.md`
- Contracts: [§ `finding-lint`](../docs/spec/interface-contracts.md#packagesfactoryscriptsfinding-lint), [§ `docs/factory-settings.yaml`](../docs/spec/interface-contracts.md#docsfactory-settingsyaml)
- Runtime: [§ 6.19](../docs/arc42/06_runtime_view.md#619-finding-lint-at-a-commit)
- Tests: `tests/factory/` (new `test_finding_lint.py`, `test_finding_lint_git.py`; `test_precommit_config_contract.py`, `test_update_factory.py`, `test_init_factory.py`, `test_block_dangerous_git.py`)

### Domain Rules

- The recorded severity equals the severity that the rule of the class computes from the basis.
- `harms_downstream` is true only with `in_use` true.
- Lines that exist unchanged where they are in use make `in_use` true; the git check sets a lower bound only.
- A line is unchanged when its introducing commit and original line number match.
- Without the release setting, a due git check fails closed.
- `in_use` records a fact at the time of the review; only a new or changed basis or artifact checks it again.
- Only the stakeholder lowers or removes a filed finding.

### Size

6 stories.

### Building-Block Inventory

| Story   | Capability                                                                 | Tier     | Size | Goal                                                                                                                                                              | Basis                                                                                                     |
| ------- | -------------------------------------------------------------------------- | -------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| ST-0391 | Reject a finding whose recorded values break the rules                     | strong   | L    | The user runs `finding-lint` and sees it exit `1`, naming file and rule, for any finding file or register file whose values break a classification rule.          | No `finding-lint` exists. `schema-validate` and `load_script` exist. Adds the script and the value rules. |
| ST-0392 | Refuse a lowering or removal of a filed finding                            | strong   | M    | The user sees `finding-lint` exit `1` when a commit lowers a filed finding, removes it, or drops a register file without a replacing finding file.                | ST-0391 reads one version. Adds the `HEAD` comparison and `--staged`.                                     |
| ST-0393 | Reject in_use: false for lines that exist unchanged where they are in use  | strong   | L    | The user sees `finding-lint` exit `1` with `artifact lines exist unchanged on <place>` when a code, runtime, or security finding answers `in_use: false` wrongly. | `_main_checkout.py` exists. Adds the porcelain parser, the places, and the line identity.                 |
| ST-0394 | Count only the project's release tags, and fail closed without the setting | standard | M    | The user sets `release_tag_patterns` and sees only matching tags count; without the setting a due git check exits `1` and names file and key.                     | ST-0393 checks branches and the installed copy. Adds the settings parser and the tag places.              |
| ST-0395 | Check in_use only when a finding is new or its basis or artifact changed   | strong   | M    | The user waives a merged `major` finding and the lint still exits `0`, while a new or changed finding gets the check, also after a register line moves.           | ST-0392 reads `HEAD`; ST-0393 runs the check on every file. Adds the trigger and the moved-line rule.     |
| ST-0396 | Run finding-lint through validate and the pre-commit hook                  | standard | M    | The user runs `validate` or `git commit` and gets the `finding-lint` result; an earlier install gets the hook from `update-factory`.                              | `validate` and the hook block list other gates. Adds the row, the hook, and its metadata.                 |

### Testability Assessment

Every goal ends in an exit code and a message of `finding-lint` that names the file and the rule. Contract tests import the script with `load_script` and call each rule on parsed values. Integration tests run it as a subprocess on temporary git repositories with local and remote-tracking branches, tags, renames, moves, linked worktrees, and an untracked installed copy. No goal has a red flag. One risk is named: the lint may fail on this repository's own findings until the migration (FCP-C12).

### Ownership Resolution

| Contract                                                                                | .feature Rule                                                                                                          | Owner   | Rationale                                  |
| --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ------- | ------------------------------------------ |
| FC-02-CT-01: a security or architecture suggestion is at most minor                     | finding-classification.feature#Reviewer agent classifies a finding by the class of its material                        | ST-0391 | introduces the suggestion rule             |
| FC-03-CT-01: the consequence tree                                                       | finding-classification.feature#Reviewer agent gets a document, code, or runtime severity from the consequence tree     | ST-0391 | introduces the computation                 |
| FC-04-CT-01, FC-04-CT-02: the bug bar and its mapping                                   | finding-classification.feature#Reviewer agent gets the severity of a security finding from the bug bar                 | ST-0391 | introduces the computation                 |
| FC-05-CT-01: the matrix                                                                 | finding-classification.feature#Reviewer agent gets the severity of an architecture risk from the matrix                | ST-0391 | introduces the computation                 |
| FC-06-CT-01, FC-06-CT-02: the basis shape and the artifact form                         | finding-classification.feature#Reviewer agent files a blocking finding as a finding file                               | ST-0391 | introduces the structural rules            |
| FC-07-IT-01: `schema-validate` on each register file                                    | finding-classification.feature#Reviewer agent records a minor finding as one register file                             | ST-0391 | first to run the schemas (FCP-C05)         |
| FC-10-CT-01 to FC-10-CT-05, FC-10-CT-08, FC-10-IT-01                                    | finding-classification.feature#finding-lint rejects a finding whose recorded values break the classification rules     | ST-0391 | introduces the value rules                 |
| FC-10-CT-06, FC-10-CT-07, FC-10-CT-09, FC-10-IT-02: lowering, removal, register removal | finding-classification.feature#finding-lint rejects a finding whose recorded values break the classification rules     | ST-0392 | introduces the `HEAD` comparison           |
| FC-15-IT-01: the raise of FAGAN-0032 passes                                             | finding-classification.feature#Orchestrator shows each new minor finding with its fails_purpose sentence               | ST-0392 | first to accept a replacing file (FCP-C08) |
| FC-11-CT-01: the porcelain parser                                                       | finding-classification.feature#finding-lint checks in_use against git for code, runtime, and security findings         | ST-0393 | introduces the line identity               |
| FC-11-IT-01 to FC-11-IT-11, FC-11-IT-19, FC-11-IT-20, FC-11-IT-22 to FC-11-IT-25        | finding-classification.feature#finding-lint checks in_use against git for code, runtime, and security findings         | ST-0393 | introduces the git check                   |
| FC-11-CT-02, FC-11-IT-12 to FC-11-IT-15, FC-11-IT-21: the release setting               | finding-classification.feature#finding-lint checks in_use against git for code, runtime, and security findings         | ST-0394 | introduces the setting                     |
| FC-11-CT-03, FC-11-IT-16 to FC-11-IT-18, FC-11-IT-26, FC-11-IT-27: the trigger          | finding-classification.feature#finding-lint checks in_use against git for code, runtime, and security findings         | ST-0395 | introduces the trigger                     |
| FC-20-CT-01, FC-20-IT-02: the moved-line rule                                           | finding-classification.feature#Stakeholder gets the open findings migrated under the new rules                         | ST-0395 | part of the trigger (FCP-C07)              |
| FC-12-LN-01, FC-12-CT-01, FC-12-IT-01, FC-12-CT-02, FC-12-IT-02, FC-12-IT-03            | finding-classification.feature#User runs finding-lint through validate and the pre-commit hook                         | ST-0396 | introduces the row and the hook            |
| FC-14-IT-10: a committed lowering is refused, and the stop holds                        | finding-classification.feature#Orchestrator stops the run on a critical finding that the stakeholder has not confirmed | ST-0396 | first with the hook (FCP-C06)              |

## E3: Stop the run on a critical finding and loop a major one back

### Why this EPIC exists

A `critical` finding means the harm may already exist outside the run, such as merges that a broken `premerge-check` reset. No author agent can undo that. So the run must dispatch and merge nothing until the stakeholder has checked the possible damage. This EPIC makes `dispatch` and `premerge-check` hold that stop, makes the orchestrator explain it, loops `major` findings back, and shows each new `minor` finding to the user before it is written.

### Actor Goals

- Orchestrator loops a major finding back to its owner until no blocking finding is open
- Orchestrator stops the run on a critical finding that the stakeholder has not confirmed
- Orchestrator shows each new minor finding with its fails_purpose sentence
- Stakeholder confirms the stop of a critical finding after the damage checks
- Stakeholder waives a blocking finding with a reason

### Demo

1. In a temporary project, write `docs/findings/BUG-0037.md` with `severity: critical`, `status: open`, and one item under `## Possible damage`.
2. Run `dispatch prepare-wave 1`. It exits `1` and prints the stop notice with the finding, its artifact, the damage item, its check, and the confirmation step. `dispatch status` still answers.
3. Run `premerge-check dev feature/demo`. It prints the same notice, exits `1`, and writes no marker, so `git merge feature/demo` is denied.
4. Write `stop_confirmed_by: human` and a reason in an editor. Both scripts run again, and the playbook loops BUG-0037 back to its owner.
5. Set `status: waived` with `override_by` and `override_reason` on a `major` finding. The loop grep of `feature-addition.md` no longer lists it.
6. Run a review that records one `minor` finding. The pause point shows it with its `no to fails_purpose` sentence before any file is written.

### Scope

**In:**

- The stop check in `dispatch` and `premerge-check`: both versions of each finding file, the two subcommand lists, the stop notice on standard output, exit `1`, and no marker (BR-091, DEC-28, DEC-52, DEC-57 to DEC-59).
- The playbooks: anchored loop greps, the explanation of each stopping finding with `explain-review-finding`, and the notice in a headless final summary (DEC-29, FC-QG17).
- `finding-format.md`: the confirmation step, the loop of a confirmed `critical` finding, and the human fields written in an editor or with a `!` command.
- The pause point and the final summary show each new `minor` finding with its sentence, and say how the stakeholder raises it (DEC-22).

**Out:**

- The guard that keeps agents from writing the confirmation (E4).
- The lint rule that refuses a committed lowering (E2, ST-0392 and ST-0396).

### Dependencies

None for ST-0397. ST-0398 waits for ST-0387 of E1, because both edit `finding-format.md`.

### Boundaries

- Scripts: `packages/factory/scripts/dispatch`, `dispatch_lib.py`, `premerge-check`
- Playbooks: `packages/factory/playbooks/` with a review loop
- Rulebook: `rulebooks/conventions/finding-format.md`
- Skills: `skills/explain-review-finding/SKILL.md`, `skills/run-step/SKILL.md`
- Contract: [§ The stop](../docs/spec/interface-contracts.md#the-stop-in-dispatch-and-premerge-check)
- Runtime: [§ 6.17](../docs/arc42/06_runtime_view.md#617-a-critical-finding-stops-the-run), [§ 6.21](../docs/arc42/06_runtime_view.md#621-what-the-review-loop-reads)
- Tests: `tests/factory/` (new `test_finding_stop.py`, `test_finding_loop_grep.py`; `test_finding_classification_text.py`)

### Domain Rules

- A stop holds while one version of a finding is critical and neither version holds text in both confirmation fields.
- A status change, a lower severity, or a removed file in the working tree never ends a stop.
- During a stop, no subcommand that starts or merges work runs, and `premerge-check` writes no marker.
- A confirmed `critical` finding loops back like a `major` one and keeps its severity.
- A waived finding drops out of the loop and keeps its severity.

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                                                           | Tier     | Size | Goal                                                                                                                                         | Basis                                                                                              |
| ------- | ------------------------------------------------------------------------------------ | -------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| ST-0397 | Stop every dispatch and merge while a critical finding is unconfirmed                | strong   | L    | The stakeholder sees `dispatch` and `premerge-check` exit `1` with the stop notice until both confirmation fields hold text.                 | `dispatch` has 18 subcommands and run blockers; `premerge-check` writes the marker. Adds the stop. |
| ST-0398 | Loop a blocking finding back and leave its confirmation or waiver to the stakeholder | standard | M    | The orchestrator explains each stop, loops `open` blocking findings back, and drops a waived one; `finding-format.md` gives the human steps. | The playbook greps match `status: open` anywhere. Adds anchored greps and the steps.               |
| ST-0399 | Show each new minor finding with its fails_purpose sentence                          | standard | S    | The user sees each new `minor` finding with its sentence at the pause point, and a headless run lists each new register file in its summary. | The pause point shows filed findings only. Adds the `minor` view and the raise step.               |

### Testability Assessment

The stop has observable outcomes at the exit code, standard output, the marker file `.current-work/premerge-check-ok`, and the decision of `block-dangerous-git.sh`. Integration tests run the scripts on temporary repositories with the ledger fixtures of `test_dispatch_run_blockers.py`. The loop grep is tested by running the greps that the playbook text names on fixture findings. The orchestrator's explanation and the pause point are agent text, so text tests show only that the instruction exists (FC-QG02).

### Ownership Resolution

| Contract                                                                         | .feature Rule                                                                                                          | Owner   | Rationale                                        |
| -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------ |
| FC-14-CT-01 to FC-14-CT-03: the stop condition, the notice, the subcommand lists | finding-classification.feature#Orchestrator stops the run on a critical finding that the stakeholder has not confirmed | ST-0397 | introduces the stop                              |
| FC-14-IT-01 to FC-14-IT-09                                                       | finding-classification.feature#Orchestrator stops the run on a critical finding that the stakeholder has not confirmed | ST-0397 | introduces the stop                              |
| FC-14-LN-01: each playbook explains the stopping finding                         | finding-classification.feature#Orchestrator stops the run on a critical finding that the stakeholder has not confirmed | ST-0398 | introduces the playbook step                     |
| FC-13-IT-01: the loop greps skip a waived finding                                | finding-classification.feature#Orchestrator loops a major finding back to its owner until no blocking finding is open  | ST-0398 | introduces the anchored greps                    |
| FC-13-LN-01: a confirmed critical finding loops like a major one                 | finding-classification.feature#Orchestrator loops a major finding back to its owner until no blocking finding is open  | ST-0398 | introduces the text                              |
| FC-16-LN-01: the confirmation step                                               | finding-classification.feature#Stakeholder confirms the stop of a critical finding after the damage checks             | ST-0398 | introduces the text                              |
| FC-18-LN-01: the human fields written outside the tool hooks                     | finding-classification.feature#Agent is refused when it sets a field that only the stakeholder writes                  | ST-0398 | first to change that part of `finding-format.md` |
| FC-15-LN-01, FC-15-LN-02: the pause point and the raise                          | finding-classification.feature#Orchestrator shows each new minor finding with its fails_purpose sentence               | ST-0399 | introduces the `minor` view                      |

FC-14-IT-10 is owned by ST-0396 in E2 (FCP-C06).

## E4: Keep agents from writing the fields that only the stakeholder writes

### Why this EPIC exists

`finding-lint` checks that a waiver or a confirmation carries its companion fields, but it cannot tell who wrote them. A headless run that a stop ends could write `stop_confirmed_by: human` and carry on. This EPIC adds the hook `guard-human-fields` and registers it in every supported CLI, so an agent's edit, write, or shell call that sets a human field is refused. It also writes the first, guard-only OpenCode plugin.

### Actor Goals

- Agent is refused when it sets a field that only the stakeholder writes

### Demo

1. Install the Factory with `init-factory --cli claude codex copilot pi opencode` into a temporary project.
2. In Claude Code, an agent tries an `Edit` that sets `stop_confirmed_by: human` in `docs/findings/BUG-0037.md`. The hook refuses it with exit `2`.
3. The same agent runs `sed -i 's/status: open/status: waived/' docs/findings/FAGAN-0042.md`. The hook refuses it. `grep "status: waived" docs/findings/*.md` passes.
4. In Codex, an `apply_patch` that the guard cannot parse and that names `docs/findings/BUG-0037.md` is refused.
5. Remove the guard script and try an edit in Pi and in OpenCode. Both CLIs block the call.
6. `.opencode/plugins/agent-factory.ts` links to the Factory plugin.

### Scope

**In:**

- The script `guard-human-fields` in `packages/factory/config/hooks/`: the guarded paths, "sets" for edits, writes, shell calls, and patches, and the refusal of an unparsable patch that names a guarded path (BR-092, DEC-42, DEC-45, DEC-56, DEC-60).
- The entries of Claude Code (`Edit`, `MultiEdit`, `Write`, `NotebookEdit`, `Bash`), Codex (`Edit`, `Write`, `apply_patch`, `Bash`), and Copilot CLI (`preToolUse` under `.github/hooks/`), written by `init-factory` beside the `step-guard` entries.
- The Pi extension that calls the guard from `tool_call` and blocks when the script is missing.
- The guard-only plugin `packages/factory/config/plugins/agent-factory.ts`, and `init-factory --cli opencode`, which links it into `.opencode/plugins/` (DEC-61).

**Out:**

- An agent that hides the field name, for example by building it in a script (DEC-42, deferred to gate-evidence).
- The full OpenCode plugin and the rest of the OpenCode integration ([opencode-cli-integration.md](../docs/proposals/opencode-cli-integration.md)).

### Dependencies

None.

### Boundaries

- Hooks: `packages/factory/config/hooks/` (new `guard-human-fields` and its registration files)
- Extensions: `packages/factory/config/extensions/` (new Pi guard extension and its test)
- Plugins: `packages/factory/config/plugins/` (new `agent-factory.ts` and its test)
- Scripts: `packages/factory/scripts/init-factory`, `update-factory`
- Contracts: [§ `guard-human-fields`](../docs/spec/interface-contracts.md#packagesfactoryconfighooksguard-human-fields), [§ `init-factory` change for OpenCode](../docs/spec/interface-contracts.md#init-factory-change-for-the-guard-in-opencode)
- Runtime: [§ 6.18](../docs/arc42/06_runtime_view.md#618-the-guard-refuses-a-human-field); ADR-0035, ADR-0036
- Tests: `tests/factory/` (new `test_guard_human_fields.py`; `test_init_factory.py`, `test_update_factory.py`), the `typescript` suite

### Domain Rules

- A call sets a human field when a value appears that was not there before. An unchanged line does not count.
- The guard checks only `docs/findings/*.md`, `docs/findings/register/**/*.json`, and the Appendix tables of `docs/proposals/*.md`.
- A read and a heredoc that writes a test fixture pass.
- A patch the guard cannot parse is refused when its raw text names a guarded path.
- Pi and OpenCode block the call when the guard script is missing.

### Size

4 stories.

### Building-Block Inventory

| Story   | Capability                                                              | Tier     | Size | Goal                                                                                                                                  | Basis                                                                                                     |
| ------- | ----------------------------------------------------------------------- | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| ST-0400 | Refuse a Claude Code agent's call that sets a human field               | strong   | L    | An agent in Claude Code is refused when an edit, write, or shell call sets a human field, and its legitimate calls pass.              | `step-guard` and `block-dangerous-git.sh` show the hook form. Adds the guard and its Claude Code entries. |
| ST-0401 | Refuse the same call in Codex and Copilot CLI, patches included         | strong   | M    | An agent in Codex or Copilot CLI is refused for the same calls, including an `apply_patch`, and for a patch the guard cannot parse.   | ST-0400 reads Claude Code payloads. Adds the patch parser and two CLI registrations.                      |
| ST-0402 | Refuse the call in Pi and block it when the guard script is missing     | standard | M    | An agent in Pi is refused through a project-local extension, and a missing guard script blocks the call.                              | `step-guard.ts` lets a call through when its script is missing. Adds the guard extension.                 |
| ST-0403 | Install the guard-only OpenCode plugin with init-factory --cli opencode | standard | M    | A user runs `init-factory --cli opencode` and an OpenCode agent is refused for the same calls, also when the guard script is missing. | No plugin exists, and `init-factory` knows four CLIs. Adds the plugin, the CLI name, and the link.        |

### Testability Assessment

Every goal ends in the exit code of the guard, `0` or `2`, for one tool call on standard input, or in the files that `init-factory` writes. Integration tests pass each call in the format of its CLI. Contract tests in the `typescript` suite load the Pi extension and the OpenCode plugin with stubbed CLI APIs. One red flag is named: the fixtures follow the contract formats and were not recorded from real CLI runs (FC-QG23), so each CLI story names a manual check.

### Ownership Resolution

| Contract                                                                        | .feature Rule                                                                                         | Owner   | Rationale                                      |
| ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------- | ---------------------------------------------- |
| FC-18-IT-01 to FC-18-IT-05, FC-18-IT-11, FC-18-IT-12, FC-18-IT-14               | finding-classification.feature#Agent is refused when it sets a field that only the stakeholder writes | ST-0400 | introduces the guard                           |
| FC-18-IT-06: the Claude Code entries                                            | finding-classification.feature#Agent is refused when it sets a field that only the stakeholder writes | ST-0400 | introduces the registration                    |
| FC-18-IT-07, FC-18-IT-08: the Codex and Copilot CLI entries                     | finding-classification.feature#Agent is refused when it sets a field that only the stakeholder writes | ST-0401 | introduces the registrations                   |
| FC-18-IT-09, FC-18-IT-10, FC-18-IT-13: patches and Copilot calls                | finding-classification.feature#Agent is refused when it sets a field that only the stakeholder writes | ST-0401 | introduces the patch parser                    |
| FC-18-IT-16, FC-18-CT-01: the Pi extension                                      | finding-classification.feature#Agent is refused when it sets a field that only the stakeholder writes | ST-0402 | introduces the extension                       |
| FC-18-IT-15, FC-18-IT-17, FC-18-CT-02: the OpenCode plugin and `--cli opencode` | finding-classification.feature#Agent is refused when it sets a field that only the stakeholder writes | ST-0403 | introduces the plugin; unblocks the three rows |

## E5: Move this repository's open findings onto the new rules

### Why this EPIC exists

The orchestrator loops on every `open` finding file. 47 open finding files carry no `review_class`, and 18 or more of them are `minor` by the old rule, so they would keep blocking although a `minor` finding never blocks. The 26 lines of the old `.jsonl` registers would also stay outside the lint. This EPIC prepares the repository and then migrates every open finding and every register line once, with one pause point for the stakeholder.

### Actor Goals

- Stakeholder gets the open findings migrated under the new rules

### Demo

1. Run `next-id --plan-seed` in a clone whose only `SEC` ID is `docs/findings/register/security/SEC-0012.json`. The seed command holds `SEC=12`.
2. Run `finding-lint` on this repository. It counts the 16 tags that match `v[0-9]*` and names no missing setting.
3. Start the migration. The agent shows each open finding with its `review_class`, `basis`, severity, and Why line at one pause point. The stakeholder confirms each `critical` finding's stop.
4. After the migration commit, `finding-lint` exits `0`, no open finding file is `minor`, and `docs/findings/register/` holds no `.jsonl` file.
5. The migration review report in `docs/reviews/` states how many migrated findings are `critical`.

### Scope

**In:**

- `next-id --plan-seed` counts each file name `docs/findings/register/**/<PREFIX>-NNNN.json` as an ID in use (cross-feature, BR-099 change, FCP-C10).
- `docs/factory-settings.yaml` with `release_tag_patterns` in this repository, before the migration commit (DEC-54, FCP-C11).
- The migration: each open finding without `review_class` gets its class, basis, Why line, and an `artifact` at the place of its fix. A `minor` result becomes a register file under its old ID; a finding without an artifact moves into `todo.md` with `status: deferred`; each `.jsonl` line becomes a register file (BR-095, DEC-35, DEC-40, DEC-54, DEC-60).

**Out:**

- The 208 files that are not `open` (DEC-24).
- The fixes of the migrated findings; the backlog takes them later.

### Dependencies

E1 (ST-0387), E2 (ST-0394, ST-0395, ST-0396). ST-0404 has no dependency.

### Boundaries

- Script: `packages/factory/scripts/next-id`
- Settings: `docs/factory-settings.yaml` (new)
- Data: `docs/findings/`, `docs/findings/register/`, `docs/spec/work/todo.md` (for findings without an artifact), `docs/reviews/`
- Runtime: [§ 6.20](../docs/arc42/06_runtime_view.md#620-migration-of-open-findings)
- Tests: `tests/factory/` (`test_next_id_plan_seed.py`; new `test_findings_repository.py`)

### Domain Rules

- The migration covers every open finding without `review_class` when it runs.
- A migrated `minor` finding keeps its ID as a register file.
- No migrated finding is `open` with severity `minor`.
- The migration commit holds no unconfirmed `critical` finding.
- The user sees every result at one pause point before any file changes.

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                                     | Tier     | Size | Goal                                                                                                                                    | Basis                                                                                        |
| ------- | -------------------------------------------------------------- | -------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| ST-0404 | Count register file names as IDs in use in next-id --plan-seed | standard | S    | A user runs `next-id --plan-seed` and its seed command covers the IDs of register files as well as the old register lines.              | `--plan-seed` counts `id` in `docs/findings/register/*.jsonl` only. Adds the file names.     |
| ST-0405 | Name this repository's release tags for finding-lint           | economy  | S    | The stakeholder sees `finding-lint` on this repository count the release tags of `release_tag_patterns` and name no missing setting.    | No `docs/factory-settings.yaml` exists. Adds the file.                                       |
| ST-0406 | Migrate the open findings and the old registers                | strong   | L    | The stakeholder confirms every result at one pause point, and after the commit `finding-lint` exits `0` and no open finding is `minor`. | 47 open findings lack `review_class`; three `.jsonl` registers hold 26 lines. Migrates them. |

### Testability Assessment

The goals end in the seed command of `next-id --plan-seed`, the output and exit code of `finding-lint` on this repository, and the file tree under `docs/findings/`. FC-20-IT-01 reads the real `docs/findings/` and stays true after the migration. The migration itself is one-time work, so it shows completion with its own evidence, not with a retained test. The `--plan-seed` change has no row in this QA strategy, so ST-0404 names its test without a Test ID.

### Ownership Resolution

| Contract                                                  | .feature Rule                                                                                  | Owner   | Rationale                       |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ------- | ------------------------------- |
| FC-20-IT-01: the lint passes and no open finding is minor | finding-classification.feature#Stakeholder gets the open findings migrated under the new rules | ST-0406 | makes the repository state true |

FC-20-CT-01 and FC-20-IT-02 are owned by ST-0395 in E2 (FCP-C07).
