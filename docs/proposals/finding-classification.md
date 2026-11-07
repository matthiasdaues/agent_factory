---
schema_version: 2
scope: global
title: Finding Classification
status: accepted
owner: agent-factory
created: 2026-11-04
updated: 2026-11-07
supersedes:

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - packages/factory/rulebooks/conventions/report-format.md
    - packages/factory/rulebooks/conventions/finding-format.md
    - packages/factory/rulebooks/templates/finding.md
    - packages/factory/rulebooks/templates/review-report.md
    - packages/factory/rulebooks/templates/qa-strategy.md
    - packages/factory/rulebooks/principles/owasp-top-10.md
    - packages/factory/rulebooks/rules.md
    - packages/factory/skills/fagan-review/SKILL.md
    - packages/factory/skills/inspect-spec/SKILL.md
    - packages/factory/skills/security-review/SKILL.md
    - packages/factory/skills/atam-review/SKILL.md
    - packages/factory/skills/bug-hunt/SKILL.md
    - packages/factory/skills/reconcile-spec/SKILL.md
    - packages/factory/skills/validate/SKILL.md
    - packages/factory/agents/code-review-agent.md
    - packages/factory/agents/proposal-review-agent.md
    - packages/factory/rulebooks/templates/proposal.md
    - packages/factory/agents/qa-agent.md
    - packages/factory/agents/spec-review-agent.md
    - packages/factory/agents/architecture-review-agent.md
    - packages/factory/agents/reconciliation-agent.md
    - packages/factory/config/pre-commit-config.yaml
    - packages/factory/config/hook-metadata.yaml
    - packages/factory/scripts
    - docs/spec/interface-contracts.md
    - packages/factory/playbooks
    - packages/factory/skills/run-step/SKILL.md
    - packages/factory/skills/explain-review-finding/SKILL.md
    - packages/factory/rulebooks/schemas
    - docs/spec/architecture.dsl
    - packages/factory/config/hooks
    - packages/factory/config/plugins/agent-factory.ts
    - packages/factory/scripts/init-factory
    - docs/testing.yaml

governance:
  assurance: elevated
  risk_domains:
    - reliability
    - security

estimate:
  as_of: 2026-11-07
  basis: decomposition
  confidence: medium
  human_review_hours:
    min: 5.5
    max: 10.0
  normalized_tokens:
    min: 90000
    max: 155000
  estimated_consumption:
    min: 1800000
    max: 3100000
    overhead_multiplier: 20
    playbook: feature-addition
---

# Feature Request: Finding Classification

## Primer

In Agent Factory, agents review the work of other agents. Each problem that a
review finds becomes a finding, a short record that says what is wrong and how
to fix it. The orchestrator, the agent that starts each step of the work,
sends serious findings back to their author and waits for the fix.

The same review, run twice on the same work, rates its findings differently.
The levels are defined by adjectives such as "significant", and the reviews use
six different scales. So a borderline finding goes back on one run and is
dropped on the next, and the fix loop changes length by chance.

The proposal puts every finding on one scale: critical, major, minor, or note.
A review class names the rule that sets the severity. The five classes are
document, code, security, architecture, and runtime. The material decides the
class, not the review that found the problem.

The reviewer records facts, and a fixed rule computes the severity. For
documents, code, and runtime behavior, the reviewer answers three yes-or-no
questions in order. Does the problem cause harm in work that is already in use?
Does the work fail its own purpose? Does it only make later work harder? The
first "yes" gives critical, major, or minor, and three "no" answers give a
note. Work is in use when something outside the current run depends on it, for
example when it is installed.

Take a defect in the script that checks a finished story. An empty story
passes, and a failing test suite then resets earlier merges. If the
defective lines exist only on the run's own branch, the finding is
major and goes back to the developer. If the same lines exist in the installed
copy, real runs may already have lost merges, so the finding is critical. A
checking script settles this from git and rejects a wrong answer.

Security review uses a lookup table, because a study found that users of
numeric scores disagree on their many fine judgments.

A critical finding stops the run, because the harm may already exist outside
the reviewed work. The reviewer lists what may be damaged, such as the lost
merges, with a check for each item. No new work is dispatched or
merged until the human runs the checks and confirms. Then the finding goes back
like a major one.

A minor finding never blocks. It becomes one small file in the register of
its class. A finding rated too low escapes later review, so the human sees each new
minor finding with the reason the work still serves its purpose.

Only the human may lift a block or confirm a stop. A guard on the agents' tool
calls refuses any agent edit that gives these fields a value. An agent that
hides the field name gets past the guard, and that case is left for later.

Every finding keeps its answers, so a later reader can check its severity. The
proposal has no open questions.

## Summary

The feature adds the rulebook `finding-classification.md`, which computes each
finding's severity from recorded answers. The gate `finding-lint` recomputes
it, so a reader can check why a finding has its severity. The first release
also adds one register per review class for `minor` findings, the `critical`
stop in `dispatch` and `premerge-check`, and the hook `guard-human-fields`. It
migrates every open finding without `review_class` and defers the other 208 files and a script for
the agreement check.

## Motivation

The same review run twice on the same input classifies its findings
differently. Three causes produce this.

The criteria are adjectives. `report-format.md` defines Major as "significant
defect that must be fixed before the review can pass". A review passes when no
Major finding is open, so the definition is circular. "Significant",
"low-impact", and "will propagate" carry no test that sorts a finding into one
level.

The scales are not one scale. Six scales exist side by side. Spec, Fagan, and
code review use Critical, Major, and Minor. Security review uses Critical,
High, Medium, and Low, and nothing defines those levels. ATAM review files at
"Medium or higher" without a scale of its own. The QA strategy uses blocking,
fix-in-same-story, and defer. Claim review uses BLOCKER, MAJOR, MINOR, and NOTE.
Proposal review uses major and note.

The finding files show the result. `docs/findings/` holds 247 files. They
carry seven different severity spellings: `major` (153), `minor` (53),
`critical` (15), `medium` (7), `Major` (3), `high` (2), and `Minor` (1).
Thirteen files carry no severity. Fifty-three files are `minor`, although
`finding-format.md` says that Minor findings stay in the report unless the
user asks to track them.

The filing threshold makes the variance expensive. A finding between Major and
Minor is filed on one run and dropped on the next. The orchestrator loops on
filed findings, so the loop length depends on the run, not on the artifact.

## Core Principles

- **Kind, size, and action are separate.** The category says what kind of
  finding it is. The severity says how bad it is. The blocking rule says what
  happens. No value stands in for another.[^odc][^ieee1044][^cc]
- **The reviewer records facts, and a rule computes the severity.** A fact is a
  yes/no answer or a choice from a fixed list. The rule is fixed per review
  class. So variance can come only from the answers, and a reader can check
  each answer.
- **One shared scale for action, a class-specific basis for judgment.** Every
  class maps onto the same four severities, so blocking and counting work the
  same everywhere. Each class keeps the questions that fit its material.
- **Agents classify, scripts verify.** `finding-lint` recomputes the severity
  from the recorded [basis](#the-values-of-a-finding). The
  [foundational principles](../../packages/factory/rulebooks/conventions/foundational-principles.md)
  require that agents create artifacts and scripts validate them.

## Design

### The values of a finding

| Value    | Question it answers           | Values                                           | Set by                                                           |
| -------- | ----------------------------- | ------------------------------------------------ | ---------------------------------------------------------------- |
| Category | What kind of finding is it?   | `defect`, `risk`, `suggestion`, `question`       | Reviewer                                                         |
| Type     | Which part of the work fails? | Class-specific vocabulary (see each class below) | Reviewer                                                         |
| Severity | How bad is it?                | `critical`, `major`, `minor`, `note`             | Computed from the basis                                          |
| Blocking | Does it stop the review?      | `true` or `false`                                | Computed from category and severity; only the human overrides it |

The basis is the set of answers that the reviewer records. The rule of the
review class computes the severity from it, so the shape of the basis depends
on the class.

The four categories mean this:

- A **defect** means the artifact is wrong as it stands.
- A **risk** means the artifact is not wrong today but may fail a stated
  requirement. Only architecture review uses this category.
- A **suggestion** means the artifact works, but a change would improve it. A
  suggestion is at most `minor`.
- A **question** means the reviewer needs the author's intent before
  classifying the finding. A question becomes an entry in
  `docs/spec/work/todo.md` only. It gets no finding file and no register file,
  and it carries no severity.

### Review classes

The review class of a finding names the rule that classifies it, not the review
that found it (DEC-17). The class follows from the reviewed material. Take
ATAM-0004: ATAM review found that ADR-0026 does not define what happens to an
untracked file in the path table. The gap is in a document, so the finding
belongs to the document class, with type `incomplete`. It carries
`source: atam-review` and `review_class: document` together.

The table maps each class to its material, the reviews that usually produce its
findings, its rule, and the fields of its basis.

| Class        | Material                                                     | Reviews that usually produce it                                                                    | Rule                                                                                                | Basis fields                                                 |
| ------------ | ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| document     | Specifications, proposals, ADRs, and arc42 chapters          | `inspect-spec`, `proposal-review-agent`, `reconcile-spec`, and the document defects of ATAM review | [Consequence tree](#the-consequence-tree); proposal rows use [two questions](#proposal-review-rows) | `in_use`, `harms_downstream`, `fails_purpose`, `raises_cost` |
| code         | Code, and the text that agents execute                       | `fagan-review` and `code-review-agent`                                                             | [Consequence tree](#the-consequence-tree)                                                           | `in_use`, `harms_downstream`, `fails_purpose`, `raises_cost` |
| security     | Code and configuration lines                                 | `security-review` and the security step of `qa-agent`                                              | [Bug bar](#class-security)                                                                          | `effect`, the four preconditions, `confidence`, `in_use`     |
| architecture | Architectural decisions, measured against a quality scenario | `atam-review`                                                                                      | [Matrix of importance and exposure](#class-architecture), raised by `in_use`                        | `importance`, `exposure`, `in_use`                           |
| runtime      | Observed behavior                                            | `bug-hunt` and the exploratory testing of `qa-agent`                                               | [Consequence tree](#the-consequence-tree)                                                           | `in_use`, `harms_downstream`, `fails_purpose`, `raises_cost` |

The rule holds for every source, not only for reviews (DEC-37). A finding from
`diagnosis`, `bug-report`, `grilling`, `onboarding`, or a dispatch run takes the
class of the material it names. Text that agents execute is code: playbooks,
skills, agent definitions, rulebooks, and hook configuration. Take a diagnosis
that finds `playbooks/feature-addition.md:37` telling the orchestrator to merge
before the premerge check. The playbook runs in every session from the
installed copy. So the finding belongs to the code class,
[the git check](#the-git-check-for-in-use) applies, and the finding is
`critical`.

A finding names an artifact. An observation without one, such as RETRO-0002, is
not a finding. It becomes an action item of its retrospective or an entry in
`docs/spec/work/todo.md`.

### Shared severity scale and blocking rule

| Severity   | Meaning in one sentence                                                                       | Filed    | Blocks        |
| ---------- | --------------------------------------------------------------------------------------------- | -------- | ------------- |
| `critical` | The defective artifact is already [in use](#in-use), so the harm may already exist elsewhere. | yes      | stops the run |
| `major`    | The reviewed artifact fails its own purpose.                                                  | yes      | yes           |
| `minor`    | The artifact works, but the finding raises the cost of later work.                            | register | no            |
| `note`     | Preference, context, or information. Nothing needs to change.                                 | no       | no            |

A finding is blocking when its category is `defect` or `risk` and its severity
is `critical` or `major`. One threshold applies to every class, so the
orchestrator and `finding-lint` need no blocking table per class (DEC-03). A
class-native rating, such as OWASP Medium, stays in the `rating` field. "Medium
or higher" in security and ATAM review becomes `major` or higher through the
mappings below.

Inspection practice knows a tier above major defects, defined by a larger cost
downstream.[^gilb] This design borrows the idea of a tier but defines it by
`in_use`, not by the size of the cost. A `critical` finding is one whose harm
may already exist outside the run.

A `minor` finding goes to the [register](#register-of-minor-findings) of its
review class and never blocks (DEC-12, DEC-60). A `note` stays in the review
report only.

### In use

Some severities depend on whether the defective artifact is already in use. An
artifact is in use when something outside the current playbook run depends on
it. That holds when the artifact is merged into `dev` or `main`, installed, or
released. It also holds when an artifact that the current run did not produce
reads it. The feature branch of the run does not count. It is the run's own
workspace, and fixing a defect there is the normal review loop (DEC-16). Every
finding records the answer in the field `in_use` (DEC-21).

A document is in use only when stories or code outside the run encode its
statement. Being merged on `dev` is not enough, because a document does harm
only through what is built from it (DEC-26). Take ATAM-0004 again: when ATAM review
filed it, ADR-0026 was accepted and on `dev`, but no migration code was built
from it yet. So the gap was not in use, and the finding was `major`.

The reviewer checks "in use" as a fact, for example in the git state, and does
not predict which later gate might catch the defect (DEC-15). Take BUG-0037: an
empty story passes `verify-story`, and a red suite then resets earlier merges
away. Suppose a story introduced the defect, and code review finds it after the
story was merged into `feature/core-artifact-ownership`. `dev` does not carry
the defect, and only this run uses that branch. So the finding is `major` and
loops back to the developer. The same defect in the installed copy in
`.agent-factory/factory/scripts/` is `critical` and stops the run, because a
real dispatch may already have reset merges.

### The consequence tree

The document, code, and runtime classes share one decision tree. The reviewer
answers three questions in order. The severity is the level of the first "yes".
Three "no" answers give `note`. Each question asks what happens if the finding
is left uncorrected, as inspection practice defines major and minor
defects.[^nasa]

1. **`harms_downstream`**: Does the finding cause a wrong result, data loss, a
   security breach, or a broken contract, and is the defective artifact already
   [in use](#in-use)? A "yes" gives `critical`. Before the artifact is in use,
   for example on the feature branch of the run, the same consequence answers
   "yes" to `fails_purpose`.
2. **`fails_purpose`**: Does the reviewed artifact fail the job it exists for?
   A "yes" gives `major`.
3. **`raises_cost`**: Does the artifact work, but the finding makes later
   reading, change, or testing measurably harder? A "yes" gives `minor`.

The tree asks for the worst consequence first. A reviewer who answers "yes" to
`harms_downstream` still records the other two answers. The lint then checks
the full set, and a reader sees the complete reasoning.

Each "yes" carries one sentence of evidence that names the concrete
consequence. A `minor` finding also carries one sentence for its "no" to
`fails_purpose`, because the pause point shows that sentence (DEC-22, DEC-27).
A "yes" without a sentence of evidence fails review, not the lint. The lint
checks structure and `in_use`, and the next review pass checks whether the
other evidence holds. Each class section below defines what the three
questions mean for its material.

### Type from the fix

In the document and code classes, the reviewer picks the type from the change
that the `**Fix:**` line demands. The reviewer does not guess where the defect
came from. ODC chooses the type from the fix that was made, because a fix is
an observable event and a guess about the cause is an opinion.[^odc] A review
has no finished fix yet, so the demanded fix takes its place (DEC-09).

### Class: document

The document class covers findings in specifications, proposals, ADRs, and
arc42 chapters: the text that people and agents read but do not execute. Its
findings come from spec review (`inspect-spec`), proposal review
(`proposal-review-agent`), spec reconciliation (`reconcile-spec`), and the
document defects of ATAM review (DEC-17).

The types are the factory's own list: `incorrect`, `ambiguous`, `incomplete`,
`inconsistent`, `unverifiable`, `infeasible`, `untraced`, `unnecessary`, and
`compound`. The list draws on the quality characteristics of requirements that
ISO/IEC/IEEE 29148 names, but it was not checked against the standard's
text.[^iso29148] A `compound` statement bundles two requirements in one, so
neither can be checked or traced alone (DEC-11). Reconciliation adds its four
existing kinds: `code-defect`, `spec-stale`, `undocumented`, and `speculative`.

| Question           | What "yes" means for a document                                                                                                                                                                                 |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `harms_downstream` | The statement contradicts an accepted ADR, an interface contract, or an accepted specification, or it states a rule that makes the implementation wrong, and stories or code outside the run already encode it. |
| `fails_purpose`    | A planner or implementer cannot act on the statement without asking the author. Two statements in the reviewed artifact contradict each other. A requirement has no check.                                      |
| `raises_cost`      | The reader can act, but only after a second reading. Examples are an unclear sentence, a missing cross-link, or two terms for one concept.                                                                      |

#### Proposal review rows

Proposal review records its findings as rows in the proposal's Appendix, and
the rows stay there (DEC-38). Their `PROP-NN` numbers count within the
proposal, as DEC-09 of the [counter-ids](counter-ids.md) proposal states. A
proposal under review has no stories built from it, so it is never in use. So
a row is `major`, `minor`, or `note`, never `critical`.

The purpose of a proposal is that a planning agent cuts stories from it without
asking back. So the reviewer asks two questions for each row, in order:

1. **`fails_purpose`**: Would a planning agent have to ask the author, or cut a
   wrong story? A "yes" gives `major`.
2. **`raises_cost`**: Can the planner act, while a reader pays later through a
   second reading, a wrong number, or a source that does not hold? A "yes"
   gives `minor`.

Two "no" answers give `note`. The Finding cell ends with one sentence that
names the deciding answer, for example "Severity: the planner can act, because
the migration counts its own files, but the wrong number misleads a reader."
The repeat pass checks that sentence as it checks the resolution. Checks 01,
02, 03, and 06 of the proposal review test whether a planner can act, so their
failures lean toward `major`. Checks 04, 05, 07, and 08 test accuracy and lean
toward `minor`. The reviewer still answers the questions for each row.

A `major` row blocks the transition to `accepted`. `minor` and `note` rows do
not block, and they stay in the table, not in a register, because the next
review pass tracks them. Only the stakeholder may set a `major` row to the
status `waived`, with the reason in its Resolution cell. `finding-lint` does
not read proposals.

The proposal review keeps its consultative pass. That pass writes only `note`
rows, because a draft is not yet expected to be complete.

### Class: code

The code class covers Fagan inspection (`fagan-review`) and implementation code
review (`code-review-agent`). Its material includes the text that agents
execute, as [Review classes](#review-classes) describes.

The types follow Orthogonal Defect Classification (ODC):[^odc] `function`,
`interface`, `checking`, `assignment`, `timing`, `algorithm`, `build`, and
`documentation`. Two types cover findings that ODC does not name. `structure`
covers a dependency rule, layering, or a SOLID violation with a concrete cost.
`test` covers a missing or weak test for an owned contract.

| Question           | What "yes" means for code                                                                                                                         |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `harms_downstream` | A reachable code path produces a wrong result, corrupts or loses data, or breaks a published contract or CLI interface, and the code is in use.   |
| `fails_purpose`    | Behavior that the story or specification requires is missing or wrong. An owned contract has no test. A rule in `dependency-rules.dsl` is broken. |
| `raises_cost`      | The code works, but a named cost follows: a duplicated rule, a function above the CRAP threshold, or a name that misleads.                        |

Review comments may carry a Conventional Comments label, such as `issue:`,
`suggestion:`, `question:`, or `nitpick:`. The label maps onto the category, and
`nitpick` always gives `note`.[^cc][^google] The label helps the author read
the review. The category and the basis decide the classification.

### Class: security

The security class covers `security-review` and the security step of the
`qa-agent`. The type is the OWASP Top 10 category, such as `A06`. A CWE
identifier can be added when one fits.

The class uses a bug bar, not a score (DEC-20). A bug bar is a lookup table:
the effect of an attack sets a starting level, and each precondition of the
attack lowers it by one step. Microsoft's SDL bug bar and Chromium's severity
guidelines work this way.[^sdl][^chromium]

Numeric scoring asks the reviewer for many fine judgments, and those judgments
disagree. In a study of 196 CVSS users, no case was scored consistently. Nine
months later, 68 % of the 59 participants who scored again changed their own
severity.[^wunder] The least agreement was on abstract metrics such as Scope
and Attack Vector. The authors recommend central guidance with examples for
hard cases. A bug bar is that guidance in the form of a table.

**Step 1: effect.** The reviewer picks the effect class that describes what the
attacker gains. The effect sets the starting level.

| Effect class  | What the attacker gains                                                                                                                                                                     | Starting level |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| `execution`   | Runs code or writes arbitrary files with the privileges of the developer or the CI job.                                                                                                     | Critical       |
| `secrets`     | Reads credentials, tokens, keys, or all project data.                                                                                                                                       | Critical       |
| `gate-bypass` | Lands a change that a factory gate should stop, such as the git guard hook, `premerge-check`, `step-guard`, or a consent gate.                                                              | High           |
| `tampering`   | Changes project artifacts persistently in the default setup, such as specifications, backlog stories, findings, or git history.                                                             | High           |
| `disclosure`  | Reads chosen data from a known location, such as personal data or a private file.                                                                                                           | High           |
| `limited`     | Reads or changes data only in a specific, non-default setup, or causes a denial of service that needs a reinstall or manual repair.                                                         | Medium         |
| `leak`        | Learns untargeted information, such as paths or versions, or causes a denial of service that a rerun fixes.                                                                                 | Low            |
| `hardening`   | Gains nothing today. The finding names a missing defense in depth. It is a `suggestion` of severity `note`, which keeps hygiene findings out of the loop, as the CVSS study warns.[^wunder] | none           |

**Step 2: preconditions.** The reviewer answers four yes/no questions. Each
"yes" lowers the level by one step. The level never falls below Low. Chromium
lowers a level for each mitigating factor in the same way.[^chromium]

| Precondition     | "Yes" when the attack needs …                                                                       |
| ---------------- | --------------------------------------------------------------------------------------------------- |
| `second_breach`  | another compromise first: a malicious upstream release, a stolen account, or a second flaw.         |
| `trusted_access` | a local shell, write access to the repository, or an account in the project.                        |
| `non_default`    | a configuration or an opt-in feature that the factory does not enable by default.                   |
| `user_action`    | the user to do something unusual, such as run a command the attacker supplied or confirm a warning. |

An attacker who already holds the gained capability through a precondition
gains nothing. That is not a finding. Microsoft's bug bar treats administrator
scenarios the same way.[^sdl]

**Step 3: confidence.** The reviewer records `proven` when the attack path is
reproduced or traced from the input to the sink in the code. Otherwise the
reviewer records `plausible`. CWSS and Semgrep keep confidence as a separate
value for the same reason: a weakness that nobody has shown to be reachable
must not count like one that someone has.[^cwss][^semgrep]

**Step 4: mapping.** The level maps onto the shared scale:

- **Critical** becomes `critical` only when the vulnerable code is
  [in use](#in-use) (DEC-16) and the confidence is `proven`. Otherwise Critical
  becomes `major`.
- **High** and **Medium** become `major`.
- **Low** becomes `minor`.

The finding keeps the level in its `rating` field, so the report still shows
High and Medium apart.

**Example.** SEC-0003: every installed lifecycle hook runs `usage-capture`,
which declares `tiktoken` with no version pin.

1. A malicious `tiktoken` release would run with the developer's privileges.
   The effect class is `execution`, and the starting level is Critical.
2. The attacker first needs that malicious release published, so
   `second_breach` is "yes". The other three preconditions are "no". The level
   becomes High.
3. The path from the unpinned declaration to execution in the hook is traced in
   the code, so the confidence is `proven`.
4. High becomes `major`, and the finding loops back to the developer.

OpenSSF Scorecard rates missing pins as Medium.[^scorecard] The bar lands one
level higher, because the hooks run the code automatically on every command.

CodeQL derives the severity from the weakness type, so every finding of one
type gets the same severity.[^codeql] The factory keeps the type in `type` and
decides the severity per finding, because one weakness type can have very
different effects in a command-line tool.

### Class: architecture

The architecture class covers what only ATAM review produces: findings measured
against a quality scenario. ATAM sorts architectural decisions by kind, and the
types are those kinds: `risk`, `non-risk`, `sensitivity-point`, and
`tradeoff-point`.[^atam] A defect that ATAM review finds in an architecture
document, such as ATAM-0004, belongs to the [document class](#class-document).
An `arch-lint` error also enters the review as a document defect, usually of
type `inconsistent`.

A `risk` gets its severity from two facts. The first fact is the importance of
the quality scenario it threatens. ATAM rates each scenario in the utility tree
on two dimensions: its importance to the success of the system, and the
perceived risk of achieving it. Both ratings are `high`, `medium`, or `low`,
because "stakeholders cannot reliably and repeatably make finer distinctions
than High, Medium, and Low".[^atam]

The factory does not keep a utility tree. Chapter 10, § 10.2 "Quality Attribute
Priority", gives each scenario a priority of 1 or 2, set by the stakeholder.
The severity maps that priority: priority 1 becomes `high`, and priority 2
becomes `medium` (DEC-10, DEC-19). The row `low` stays in the matrix for
projects that rank scenarios on three levels. If a risk against a priority-2
scenario should block, the stakeholder raises the scenario to priority 1.

The second fact is the exposure, which is the reviewer's own analysis:

- `fails` means the analysis shows the decision cannot meet the scenario's
  response measure.
- `uncertain` means no evidence exists either way, or the result depends on an
  assumption nobody has checked.

| Scenario importance \\ Exposure | `fails` | `uncertain` |
| ------------------------------- | ------- | ----------- |
| `high`                          | `major` | `major`     |
| `medium`                        | `major` | `minor`     |
| `low`                           | `minor` | `note`      |

The matrix gives at most `major`. A third fact, `in_use`, raises a `major` risk
to `critical`. It holds when something built from the decision is in use, as
[In use](#in-use) defines (DEC-18). Take a risk against QS-9, "Read-only
preflight before installation". While the design exists only in an ADR, the
risk is `major` and loops back to the architecture author. Once an installer
built from that design is released, the same risk is `critical` and stops the
run, because installed copies may already act on the flawed design.

Non-risks, sensitivity points, and tradeoff points are recorded in the report
with severity `note`. They support the analysis and do not demand a change. A
non-risk is a good decision that rests on assumptions, so each non-risk names
its assumptions. If an assumption changes, the non-risk must be judged
again.[^atam] The report groups risks into risk themes.[^bass] A theme is not a
finding of its own.

### Class: runtime

The runtime class covers `bug-hunt` and the exploratory testing of the
`qa-agent`. The types name the observed effect: `crash`, `hang`, `wrong-result`,
`data-loss`, `security`, `performance`, `usability`, and `cosmetic`.

| Question           | What "yes" means for observed behavior                                                                                                                               |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `harms_downstream` | Data is lost or corrupted, a security boundary breaks, the system crashes or hangs, or the primary actor-goal path fails with no workaround, and the code is in use. |
| `fails_purpose`    | The primary actor-goal path fails but has a workaround, or any path returns a wrong result.                                                                          |
| `raises_cost`      | A secondary path degrades and has a workaround, a message misleads, or an observability gap hides a failure from the operator.                                       |

The levels match the example severity values of IEEE 1044.[^ieee1044]
Critical becomes `critical`, Major becomes `major`, Minor becomes `minor`, and
Inconsequential becomes `note`. IEEE 1044 also names a level Blocking, which
means that testing stops until a fix or workaround exists. Blocking describes
the state of testing, not the size of the harm, so this design records it in
the blocking flag and not in the severity.

The QA strategy keeps its per-feature triage table, but the table states the
consequence, not the severity (DEC-34). Its `Severity` column becomes
`Consequence`, with the values "harm if in use", "fails purpose", and "raises
cost". The table gives the feature-specific examples for the three questions,
and the tree and `in_use` compute the severity. The action follows the
severity: `critical` stops the run, `major` loops back to the author, and
`minor` goes to the register.

Take a bug hunt that finds a new migration step deleting the story files of a
test project. The table lists data loss under "harm if in use". The code
exists only on the feature branch, so it cannot harm anything outside the run
yet. The finding is `major`, and the automated loop fixes it before the
merge. The same defect on `dev` is `critical` and stops the run. The reviewer
records severity, not priority, as [Design Details](#design-details) explains.

### Claim review stays outside

Claim review is not a review class (DEC-36). `adversarial-review` decides
whether a research claim survives, not how bad a defect in an artifact is. A
claim that fails review harms nothing, because nothing outside the research
run depends on it yet. Its refutation is a success, because the research has
eliminated a bad argument. So `adversarial-review` keeps its BLOCKER, MAJOR,
MINOR, and NOTE, its schemas, and its survival rule.

Only its envelope follows the shared scale, because every child-result
envelope carries the four keys. A BLOCKER counts under `major`, because it
blocks the claim as a `major` finding blocks a review. MAJOR, MINOR, and NOTE
count under their namesakes. No BLOCKER counts under `critical`, because no
claim review finds harm that already exists elsewhere.

### What a blocking finding does

A `critical` finding stops the playbook run, and a `major` finding loops back to
its author (DEC-14). The loop runs until no blocking finding is open. Take
BUG-0037 again. The merges are lost before the bug hunt finds the cause, and no
author agent can bring them back. So the run must dispatch and merge nothing
more.

Two scripts hold the stop (DEC-28). `dispatch` and `premerge-check` read each
finding file in the working tree and its `HEAD` version (DEC-57). They refuse
to run while a finding is critical and unconfirmed. A finding is critical when
one of its two versions has `severity: critical` together with `status: open`
or a `review_class` field. A finding is confirmed when one of its two versions
holds text in both `stop_confirmed_by` and `stop_confirmed_reason` (DEC-52).
Only the human writes these two fields, so only the human's confirmation ends a
stop. A status change, a lower severity, or a removed file in the working tree
does not end it. The human lowers a `critical` finding only once its `HEAD`
version holds the confirmation, so a lowering never ends a stop (DEC-58,
DEC-59).
`block-dangerous-git` lets `git merge` through only with the marker that
`premerge-check` writes, so no merge passes the stop either.

Both scripts print the same stop notice and exit `1`. The notice names the
finding ID and title, the artifact, the evidence for `in_use`, each item of the
finding's [possible damage](#finding-file) with its check, and the
confirmation step (DEC-29). In an interactive session, the orchestrator then
explains each stopping finding with `explain-review-finding`, which leads with
cause and effect. A headless run does not wait. It ends and carries the notice
in its final summary.

The human runs the checks and then writes `stop_confirmed_by` and
`stop_confirmed_reason` into the finding file. The reason says what the human
checked and what they found. The scripts then run again, and the finding loops
back to its author like a `major` one. It keeps its severity. Only the human
writes the two fields, as
[Fields only the human writes](#fields-only-the-human-writes) describes.

### Human override

Only the human may override the computed blocking value (DEC-13). Take a
`major` finding on wave-0 handling that the human decides not to fix. The human
sets `status: waived` in the finding file, with `override_by` and
`override_reason` (DEC-44). Every review loop greps for `status: open`, so the
waived finding drops out of the loop without a change to any playbook. The
finding keeps its computed severity, so the severity stays checkable. The
status says what happened: the finding is accepted unfixed, as a proposal row
is when the stakeholder waives it. The override only lowers a
blocking finding. A `minor` finding never blocks, and no override raises it
(DEC-25).

A `critical` finding can be waived only after the human has confirmed its
stop with `stop_confirmed_by` and `stop_confirmed_reason` (DEC-47). Waiving
lifts the stop as confirming does, so without this rule the human could skip
the damage checks. With it, the damage is checked even when the finding stays
unfixed. The same holds for `resolved` (DEC-52). A `critical` finding becomes
`resolved` only after its stop is confirmed, so whoever fixes the defect by
hand confirms the stop first. The stop holds until both confirmation fields
hold text.

### Fields only the human writes

`finding-lint` checks that an override carries both companion fields, but it
cannot check who wrote them. So a guard hook keeps agents from writing them
(DEC-42). The hook `guard-human-fields` refuses an agent's edit, write, or
shell call that sets one of these values: a non-null
`override_by`, `override_reason`, `stop_confirmed_by`, or
`stop_confirmed_reason`, or the status `waived`. The human writes them in an
editor or with a `!` command in the session, which runs outside the tool
hooks.

The guard runs in every CLI the Factory supports: Claude Code, Codex, Copilot
CLI, Pi, and OpenCode (DEC-51, DEC-61). Each CLI registers it on its own hook
events for edits, writes, and shell calls:

- Claude Code registers it as `PreToolUse` hooks for `Edit`, `MultiEdit`,
  `Write`, `NotebookEdit`, and `Bash`.
- Codex registers it as `PreToolUse` hooks for `Edit`, `Write`,
  `apply_patch`, and `Bash`.
- Copilot CLI registers it as `preToolUse` entries in a hook file under
  `.github/hooks/`, as `step-guard.json` does.
- Pi calls it from the `tool_call` event of a project-local extension.
- OpenCode calls it from `execute.before` of the Factory plugin
  `packages/factory/config/plugins/agent-factory.ts`, for the tools `edit`,
  `write`, `patch`, `shell`, and `execute`. The guard checks the JavaScript
  of an `execute` call as the text of a shell call. This feature writes the
  first version of that plugin, and it holds only the guard. `init-factory`
  accepts the CLI name `opencode` and links the plugin into
  `.opencode/plugins/`.

A patch call names its paths inside the patch text: `apply_patch` in Codex,
Copilot CLI, and Pi, and `patch` in OpenCode. So in every CLI the guard reads
the paths from the patch. When the guard cannot parse a patch whose raw text
names a guarded path, it refuses the call.

Pi and OpenCode block the call when the guard script is missing, so a broken
install refuses the edit instead of letting it through. The Pi extension
`step-guard.ts` lets a call through in that case; the guard does not.

A register file that replaces a filed finding carries `override_by` and
`override_reason`, as [Register of minor findings](#register-of-minor-findings)
describes. So the hook checks `docs/findings/*.md`, the register files
`docs/findings/register/**/*.json`, and the Appendix tables of
`docs/proposals/*.md`, and no other path (DEC-45, DEC-56, DEC-60). The rulebook, the
templates, and the test fixtures lie outside, so the stories that build this
feature can write them.
"Sets" means that a value appears that was not there before:

- For `Edit`, the hook compares `old_string` with `new_string`. A line that
  stays unchanged does not count, so an agent can fix a typo in a waived
  finding.
- For `Write`, it compares the new content with the current file. A new
  finding from the template carries only `null`, so a reviewer can file it.
- For `Bash`, it checks only a command that writes into a guarded path, such
  as a redirect, `sed -i`, or `tee` on a finding file, a register file, or a
  proposal. It refuses the command when its text assigns a non-null value to one of the
  fields, or `waived` to a `status:` line or to the Status cell of a proposal
  row. A read such as `grep "status: waived"` and a heredoc that writes a
  test fixture pass.

Take a headless run that a `critical` finding stops. The orchestrator tries to
write `stop_confirmed_by: human` into the finding file to finish the run. The
hook refuses the edit, and the run ends with the stop notice.

The hook checks the text of each call, as `block-dangerous-git.sh` does. An
agent that hides the field name, for example by building it from pieces in a
script, gets past it. No local check can tell a human from an agent with a
shell, the fault that [gate-evidence.md](gate-evidence.md) describes for gate
receipts. The design for that path is deferred.

### Register of minor findings

A `minor` finding is recorded as one register file in the register of its
review class. The register of a class is the folder
`docs/findings/register/<class>/`, and each register file in it holds one
finding as one JSON object, such as
`docs/findings/register/security/SEC-0012.json`. So a reader finds every
recorded `minor` finding in one folder. A blocking finding stays a Markdown
finding file, because its `Fix`, its possible damage, and its status changes
on each repeat pass read better as a document (DEC-60).

The object holds the ID, the `source`, the category, the type, the artifact,
the story, the finding, the `basis`, the `**Why this severity:**` sentence, the
reviewed commit, and the `status`. A register file that replaces a filed
finding also holds `override_by` and `override_reason`, because only the human
lowers a filed finding (DEC-56). The `basis` has the shape of the class, so
each register has its own JSON Schema, such as
`rulebooks/schemas/finding-register-security.schema.json` under the Factory
root. The Factory root is `packages/factory/` in this repository and
`.agent-factory/factory/` in an installed project. `finding-lint` runs
`schema-validate` on each register file with the schema of its class under
the Factory root that it runs from, and then recomputes the file's severity
(DEC-60).

The `status` of a register file is `open`, `resolved`, or `waived`. The
reviewer agent writes `open` when it records the finding. The commit that
fixes the finding sets `resolved`, and the file stays as the record. Nobody
fixes some `minor` findings, such as an unclear sentence in a document that a
later feature replaces. The human sets such a file to `waived`, with
`override_by` and `override_reason`, as on a finding file (DEC-44, DEC-63).
The finding is then accepted as is, and the file stays as well. A register
file is never `deferred` (DEC-55). A register file is removed only when the finding is raised and a
finding file with the same ID replaces it.

One file per finding keeps parallel work apart. Two reviews on two branches
add two new files, and two fixes change two different files, so git merges
both without a conflict and without a merge driver. A fix that changes a
status leaves every other finding as it is. The `basis` nests in JSON, where
CSV would flatten it into columns, and the factory already validates JSON
against schemas with the standard library only. The orchestrator loop greps
`docs/findings/*.md` for `status: open`. A register file lies in a subfolder
and holds JSON, so the grep never lists it.

A finding classified too high blocks, so someone looks at it. A finding
classified too low becomes a register file, and nothing questions its answers
again. The lint checks only that the severity matches the answers, and a
wrong "no" matches as well as a right one. The repeat pass reads only blocking
findings. So the pause point in `finding-format.md` shows each new `minor`
finding with its "no" sentence for `fails_purpose` (DEC-22). The pause point
and the orchestrator's final summary render the new register files as text
for the human. Take an ATAM review that records "an implementer can pick the obvious
behavior" for the gap in ADR-0026. The user reads the sentence and can raise
the finding to `major` by changing the answer. In a headless run, the
orchestrator's final summary lists the new register files with the same
sentence. That summary comes only after the loop ends, so a headless run can
still carry a wrong downgrade into implementation.

### Finding IDs

Every finding gets its ID from `next-id`, whether it becomes a finding file
or a register file (DEC-32). The [counter-ids](counter-ids.md) proposal defines that
script. Until it ships, the reviewer takes the next plausible number of the
tag. The reviewer looks at the finding files, the IDs in the registers, and the
branches of open runs, and checks by hand that no other finding holds that
number.

### Finding file

The finding template gains eight fields, one status, and one body line. The
new fields are `review_class`, `type`, `basis`, `rating`, `override_by`,
`override_reason`, `stop_confirmed_by`, and `stop_confirmed_reason`. The new
status is `waived`. A
`critical` finding also carries the body section `## Possible damage`:

```markdown
---
id: FAGAN-0042
source: fagan-review
review_class: code            # document | code | security | architecture | runtime
category: defect              # defect | risk | suggestion | question
type: checking                # vocabulary of the review class
severity: major               # critical | major | minor | note — computed from basis
basis:                        # shape depends on review_class
  in_use: false               # every class; git-checked for code, runtime, security
  harms_downstream: false
  fails_purpose: true
  raises_cost: true
rating: null                  # security: bug-bar level
override_by: null             # required with status: waived — set only by the human
override_reason: null         # required with status: waived
stop_confirmed_by: null       # critical only — set only by the human
stop_confirmed_reason: null   # required when stop_confirmed_by is set
artifact: packages/factory/scripts/premerge-check:120
status: open                  # open | resolved | waived (human only) | deferred (migration only)
traces: [ST-0351]
---

# <one-line finding title>

**What is wrong:** <the defect, stated concretely>

**Why this severity:** <one sentence per "yes" answer, per precondition, or for the effect class>

**Fix:** <the concrete remediation>

## Possible damage              <!-- critical only -->

- <what outside the artifact depends on it> — check: <command or step>
```

The reviewer fills `## Possible damage` when filing a `critical` finding, and
only then (DEC-29). Each item names one thing outside the reviewed artifact
that depends on it, as a fact from git or the file tree, and one check the
human can run. For BUG-0037, one item reads "merges on `dev` from dispatch runs
since the installed copy was last updated — check: compare
`git log --merges dev` with the merges the dispatch log records".

The example shows the basis of the code class. Each class records the basis
fields that [Review classes](#review-classes) lists.

The child-result envelope keys `finding_counts` by the shared scale:
`critical`, `major`, `minor`, and `note`. Every key is always present.

### `finding-lint`

`finding-lint` is a new deterministic gate in `packages/factory/scripts/`. It
reads every `docs/findings/*.md` that carries `review_class`, and every
register file. After the migration, only files that are not `open` lack the
field, as [Migration of open findings](#migration-of-open-findings) lists. The
lint skips them. The lint checks these rules:

- `review_class`, `category`, and `type` hold values from the vocabulary of
  their class.
- `basis` has the shape its class requires.
- The severity computed from `basis` equals the recorded `severity`.
- A `suggestion` is at most `minor`. No finding file and no register file has
  the category `question`.
- The body holds a `**Why this severity:**` line.
- A finding file or a register file with `status: waived` has a non-empty
  `override_by` and `override_reason` (DEC-63). A waived
  `critical` finding also has a non-empty `stop_confirmed_by` and
  `stop_confirmed_reason`, and so does a resolved one (DEC-52).
- `status` is one of `open`, `resolved`, `deferred`, and `waived`. Only the
  migration sets `deferred`, so a file that carries `review_class` is never
  `deferred` (DEC-55). An `open` finding file is not `minor` or `note`. A
  register file is `open`, `resolved`, or `waived`, and a register file that `HEAD`
  holds is removed only for a finding file with the same ID (DEC-60). No ID
  names both a finding file and a register file (DEC-53).
- A `critical` finding holds `## Possible damage` with at least one item and
  its check. No other severity holds the section.
- A set `stop_confirmed_by` comes with a non-empty `stop_confirmed_reason`,
  and only on a `critical` finding.
- `artifact` resolves to a line range (`path:line` or `path:start-end`) or to a
  Markdown heading (`path#anchor`).
- For a finding of the code, runtime, or security class, `in_use` agrees with
  git, as [The git check for in use](#the-git-check-for-in-use) defines
  (DEC-21, DEC-31).
- In the document, code, and runtime classes, `harms_downstream` is `true` only
  when `in_use` is `true`.
- A `minor` finding holds one sentence for its "no" answer to `fails_purpose`
  in its `**Why this severity:**` sentence (DEC-27). The sentence contains the
  marker `no to fails_purpose`, so the lint can check it on each register file
  (DEC-53).

The script exits `1` on any violation and names the file and the rule. The
`validate` skill and the pre-commit configuration run it.

#### The git check for in use

For code, runtime, and security findings, `in_use` is the one answer that git
settles without judgment, and it is the answer that stops the run. A security
finding points at code or configuration lines like a code finding, and a missed
security stop does the most harm. So the lint checks it (DEC-21, DEC-31).

Take BUG-0037 from [In use](#in-use), but suppose the story did not touch the
defective lines. Then `dev` carries the same lines. A Fagan review on
`feature/core-artifact-ownership` answers `in_use: false`, because the review
runs on the feature branch. The lint finds the lines unchanged on `dev` and
rejects the finding. After the correction, the finding is `critical`, and the
run stops.

The rule is this: if every line of the `artifact` range exists unchanged on
`dev`, on `main`, at a release tag, or in the installed copy, `in_use` must be
`true`. Otherwise the lint exits `1` with a message such as "artifact lines
exist unchanged on dev". [Line identity](#line-identity) defines when a line is
unchanged.

The git check sets a lower bound only. When git finds no match, the reviewer
may still answer `in_use: true`, for example when another project already
reads the artifact. The `**Why this severity:**` line then names who reads it.

The lint checks `in_use` only when a finding is new or its `basis` or
`artifact` changed (DEC-43). It compares each finding file and each register file with
its version at `HEAD` (DEC-46, DEC-60). A file that does not exist at `HEAD`, or whose `basis` or
`artifact` differs from it, gets the check. The pre-commit hook compares the
staged file, and `validate` compares the working tree, so both give the same
answer. A change to the override or confirmation fields, the status, or the
text does not trigger the check. `in_use` records a fact at the time of the review.
Otherwise a `major` finding that the human overrides after its branch merged
into `dev` would fail the lint, although its answer was correct when the
reviewer gave it.

The git check does not apply to document and architecture findings. Both are in
use only through what is built from them: a document through the stories or
code that encode it (DEC-26), and a decision through what is built from it
(DEC-18). Git cannot tell whether code encodes a statement. So the reviewer
answers `in_use` for a document and names the encoding story or code in the
`**Why this severity:**` line.

#### Line identity

The lint compares line identities from git, not text (DEC-30).
`git blame -M -C --porcelain` gives each line the commit that introduced it and
its line number in that commit.[^blame] Two lines are the same line when both
values match. `-M` and `-C` follow a line that moved within a file or between
files.

1. The lint blames the `artifact` range on the reviewed branch and collects one
   identity per line. For a `path#anchor` artifact, the range is the section
   under the heading.
2. On each place that counts, it blames the `artifact` path and every path
   that `git diff -M -C` between that place and the reviewed branch names as
   the source of a rename or a copy (DEC-49). So a range that moved to another
   file on the reviewed branch is still found in its old file. The porcelain
   file name stays part of the identity only. It names the path at the line's
   first commit, which may no longer exist.
   The places are `dev` and `main`, both as local branches and as `origin/dev`
   and `origin/main`, because a local branch can lag behind the remote
   (DEC-50). A branch that the clone does not have is skipped and named in the
   output. The places also include each release tag.
   Each project defines which tags count as release tags, as the list
   `release_tag_patterns` in the tracked file `docs/factory-settings.yaml`
   (DEC-48). Git carries the setting, so every clone uses the same one. The
   Factory sets no default, and `init-factory` does not write the file.
   Without the file or the key, `finding-lint` exits `1` and names both.
3. It blames the installed copy with `--contents`, which annotates a file
   outside git against the history of the tracked path. In this repository,
   the installed copy of `packages/factory/` is `.agent-factory/factory/`. In
   a linked worktree, the lint finds the installed copy in the main checkout
   through `_main_checkout.py` (DEC-49). A consumer project has no
   `packages/factory/` and skips this step.
4. If every identity of the range shows up in one of these places, the lines
   exist there unchanged.

Take the BUG-0037 case above with a story that inserted 20 lines above the
defect. The defective lines sit at 120–134 on the feature branch and at
100–114 on `dev`. Their identities match, so the lint finds them on `dev`. A
range that holds a single `}` has its own identity too, so it cannot match
every other brace in the file.

### Migration of open findings

Every open finding without `review_class` is migrated once (DEC-24, DEC-54).
On 2026-11-04 these were 39: 20 `major`, 1 `high`, and 18 `minor` findings, by
tag 25 BUG, 5 PROP, 4 RECON, 4 RETRO, and 1 SEC. By 2026-11-06, SPEC-0055 to
SPEC-0058 and ATAM-0010 to ATAM-0013 had raised the count to 47. The migration
counts again when it runs. The migration commit triggers the git check, so
`docs/factory-settings.yaml` lands before the migration. The orchestrator loops on every `open` file. So
without the migration, the 18 `minor` findings would keep blocking, against the
rule that a `minor` finding never blocks (DEC-12).

An agent classifies each open finding with the new rulebook. It writes
`review_class`, `basis`, and the `**Why this severity:**` line. It rewrites
`artifact` to a line range or a heading, at the place the fix goes (DEC-40).
BUG-0016 names `docs/`, BUG-0086 names a whole script, and both get the range
of their fix. For each finding that comes out `critical`, the migration agent
fills `## Possible damage`, as a reviewer does.

The user reviews all results at one pause point before any file changes. For
each `critical` finding, the human runs the checks and sets
`stop_confirmed_by` and `stop_confirmed_reason` (DEC-35). The finding then
blocks like a `major` one, and its fix goes into the backlog. So the migration
commit holds no unconfirmed `critical` finding, and no later run stops on a
finding it did not produce. The migration review report records how many open
findings the new rule makes `critical` (DEC-35).

After the pause point, the agent changes the files:

- A finding that comes out `minor` becomes a register file with
  `status: open` in the register of its class and keeps its ID, for example
  `docs/findings/register/code/BUG-0067.json`. The finding file is removed,
  and git history keeps its text. This is one of two exceptions to the rule in
  `finding-format.md` that a finding file is never deleted. The other is a
  lowering by the human (DEC-56, DEC-60).
- Any other finding stays a file and is checked by the lint from then on, for
  example BUG-0105.
- A finding that names no artifact, such as RETRO-0002, is not a finding
  (DEC-37, DEC-40). The agent moves it into `docs/spec/work/todo.md`, and the
  file gets `status: deferred` with the todo ID in its body.

The migration also moves each line of the old registers
`docs/findings/register/architecture.jsonl`, `code.jsonl`, and
`document.jsonl` into one register file under the same ID, with
`status: open`, and removes the three files (DEC-60). On 2026-11-07 they held
25 lines. For example, the line of RECON-0027 in `document.jsonl` becomes
`docs/findings/register/document/RECON-0027.json`.

The other 208 files stay as they are: 195 resolved findings, IMPL-0003 with
`status: deferred`, and 12 files without frontmatter. Three of the twelve are
not findings at all: `BUG-HUNT.md`, `qa-handoff-envelope.md`, and
`qa-review-summary.md`. None of them carries a future action, so their old
format costs nothing.

### Agreement check

The agreement check measures how often two runs give a finding the same
severity (DEC-23, DEC-39). It re-classifies a fixed set of 20 closed findings
from `docs/findings/`, none of them migrated. They are picked by the class of
their material, not by tag: 6 document, 5 code, 4 runtime, 2 architecture, and
3 security. The security picks are FAGAN-0021, SEC-0005, and SEC-0006. Each
finding keeps only the text that says what is wrong and how it was fixed. No
finding in the set is a calibration example of the rulebook or a worked
example of this proposal.

Each run of the check is a fresh subagent session. It receives only the rules
under test and the 20 texts, with no conversation and no other file. All four
runs use the model that the review agents use. Two runs classify the set with
the new rulebook, and two classify it with the rules in `report-format.md` as
they stand before this change. A `question` counts as disagreement, because the
run did not classify the finding.

## Scope

**In the first release:**

- A new rulebook, `packages/factory/rulebooks/conventions/finding-classification.md`,
  holds the values of a finding, the shared scale, the consequence tree, and one
  section per review class with two or three examples per level from
  `docs/findings/`.
- `report-format.md` § Category rules and § Severity, `finding-format.md`
  § When to file, and `owasp-top-10.md` link to the new rulebook instead of
  defining severity themselves.
- Each review skill and agent in the boundaries names its review class and
  links to its class section.
- The finding template and the review-report template carry the new fields.
  The finding file carries the status `waived`, `override_by`,
  `override_reason`, `stop_confirmed_by`, `stop_confirmed_reason`, and, on a
  `critical` finding, the section `## Possible damage`.
- The registers in `docs/findings/register/<class>/`, one JSON register file
  per `minor` finding, with one schema per class in
  `packages/factory/rulebooks/schemas/`. The review skills write each `minor`
  finding as a register file of its class, and the fixing commit sets its
  status to `resolved`.
- `finding-format.md` allows two removals of a finding file as the exceptions
  to "never delete": the migration of a `minor` finding and a lowering by the
  human. Each one leaves a register file under the same ID.
- `finding-lint` checks the rules in [`finding-lint`](#finding-lint).
  `validate` and pre-commit run it.
- `dispatch` and `premerge-check` hold the stop for an open, unconfirmed
  `critical` finding and print the stop notice. The orchestrator explains each
  stopping finding with `explain-review-finding`, and a headless run ends with
  the notice in its final summary.
- The hook `guard-human-fields` in `packages/factory/config/hooks/`, registered
  in every supported CLI for its edit, write, and shell calls (DEC-51,
  DEC-61).
- The first OpenCode plugin `packages/factory/config/plugins/agent-factory.ts`,
  which holds only the guard, and the change to `init-factory` that accepts
  the CLI name `opencode` and links the plugin into `.opencode/plugins/`
  (DEC-61).
- A `node:test` suite for the TypeScript tests in
  `packages/factory/config/**/*.test.ts`, on Node 22.6 or later and with no
  new dependency, declared in `docs/testing.yaml` (DEC-62).
- The pause point in `finding-format.md` and the final summary of each playbook
  with a review loop show every new `minor` finding with its `fails_purpose`
  sentence.
- The triage table of the QA strategy template states the consequence in a
  `Consequence` column, and its actions follow the computed severity.
- `proposal-review-agent.md` and the proposal template rate each review row
  with the two questions, end its Finding cell with the severity sentence, and
  know the status `waived`.
- `docs/spec/interface-contracts.md` keys `finding_counts` by the shared scale.
- The one-time migration of every open finding without `review_class` and of
  every line of the old `.jsonl` registers, after
  `docs/factory-settings.yaml` exists, as
  [Migration of open findings](#migration-of-open-findings) describes.
- The [agreement check](#agreement-check) on a fixed set of existing findings.
  The set and its results live in a review report in `docs/reviews/`.

**Explicitly deferred (do NOT plan stories for these):**

- Protection against an agent that hides an override or confirmation field from
  `guard-human-fields`. No local check tells a human from an agent with a
  shell, so the design waits for [gate-evidence.md](gate-evidence.md) (DEC-42).
- A review class for claim review. `adversarial-review` decides whether a
  claim survives, not how bad a defect is, and keeps its own scale (DEC-36).
- Migration of the 208 files that are not `open` (DEC-24).
- A script that runs the agreement check. The first release runs it once by
  hand. A script is worth building when the rulebook changes often enough that
  each change needs a new measurement.
- Environment data in the security rating, such as threat activity, deployment
  exposure, or business impact. A review of a diff has none of it. CVSS, SSVC,
  CWSS, and OWASP use such data where it exists.[^cvss4][^ssvc][^cwss][^owasp]
- Severity levels for the deterministic lint scripts (`error`, `warning`,
  `info`). Those levels belong to gate reports, not to review findings.
- A utility tree in arc42 chapter 10 with importance and difficulty rated H/M/L
  per scenario, and the changes to `scaffold-arc42` and `maintain-architecture`
  that would write it. The priority in § 10.2 is enough until a real case shows
  that two levels are too coarse (DEC-19).
- Numeric security scoring with CVSS, SSVC, CWSS, or OWASP factors. CVSS and
  SSVC rate deployed software, and SSVC decides priority, not
  severity.[^cvss4][^ssvc] CWSS scores weaknesses before release, but it asks
  for 16 factor judgments, and OWASP asks for 16, eight for
  likelihood and eight for impact.[^cwss][^owasp] Factor
  judgments cause the variance this proposal removes (DEC-05, DEC-20).

## Design Details

**Calibration examples.** Each class section in the rulebook lists two or three
real findings per level, with their basis. A reviewer reads them before the
first classification of a session. The examples come from `docs/findings/`. A
level with no real example yet carries one invented example that names real
project files.

**Severity is not priority.** Severity measures consequence. Priority decides
the order of work and stays with the dispatcher and the stakeholder. IEEE 1044
keeps the two as separate attributes, and the organization that resolves
the defect assigns the priority.[^ieee1044]

### Sources

The table shows which source each part of the design draws on, and whether the
source was read. The footnotes give the full citations. Where a source was not
accessible, the design does not quote it. The design then draws on the
source's general approach, as public secondary sources and common practice
describe it.

| Source                                  | What the design takes from it                                                                                                                 | Read                   |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| NASA handbook[^nasa]                    | Major and minor defined by what happens "if left uncorrected"                                                                                 | yes                    |
| JPL inspection study[^jpl]              | Severity kept apart from defect type and checklist category                                                                                   | yes                    |
| Gilb and Graham[^gilb]                  | Major defects and a tier above them, defined by downstream cost                                                                               | search excerpt only    |
| Chillarege, ODC[^odc]                   | Independent attributes, the code defect types, and the type chosen from the fix                                                               | yes                    |
| IEEE 1044-2009[^ieee1044]               | Severity as the highest impact, severity kept apart from priority, runtime levels                                                             | yes                    |
| ISO/IEC/IEEE 29148[^iso29148]           | The quality characteristics behind the document types                                                                                         | table of contents only |
| Conventional Comments[^cc]              | Label and blocking decoration as separate values                                                                                              | yes                    |
| Google Engineering Practices[^google]   | `Nit:`, `Optional:`, and `FYI:` for comments that do not block                                                                                | yes                    |
| OWASP Risk Rating Methodology[^owasp]   | Checked and not adopted. Its factor scoring is replaced by the bug bar (DEC-20)                                                               | yes                    |
| CVSS v3.1[^cvss31]                      | Impact combined like a logical OR. Checked and not adopted (DEC-20)                                                                           | yes                    |
| CVSS v4.0[^cvss4]                       | Fixed score bands. Checked and not adopted (DEC-05)                                                                                           | yes                    |
| Microsoft SDL bug bar[^sdl]             | Severity looked up from the effect class and the attacker's preconditions                                                                     | yes                    |
| Chromium severity guidelines[^chromium] | A level per attacker capability, lowered one step per mitigating factor                                                                       | yes                    |
| CWSS 1.0.1[^cwss]                       | Confidence kept as its own value. Checked and not adopted (DEC-05)                                                                            | yes                    |
| Semgrep rule metadata[^semgrep]         | `confidence` kept apart from `likelihood` and `impact`                                                                                        | yes                    |
| CodeQL `security-severity`[^codeql]     | Severity derived from the weakness type, as the 75th percentile of the CVSS scores of all CVEs under the query's CWE. Checked and not adopted | yes                    |
| OpenSSF Scorecard[^scorecard]           | Missing dependency pins rated as Medium risk, as a reference for SEC-0003                                                                     | yes                    |
| Wunder et al., CVSS study[^wunder]      | Evidence that numeric factor scoring is inconsistent, and the advice to give examples                                                         | yes                    |
| SEI, *Towards Improving CVSS*[^seicvss] | Critique of CVSS use, with SSVC as the proposed alternative                                                                                   | abstract only          |
| CERT SSVC[^ssvc]                        | A decision tree for priority. Checked and not adopted (DEC-05)                                                                                | yes                    |
| Kazman, Klein, Clements: ATAM[^atam]    | Risks, non-risks, sensitivity points, tradeoff points, and the utility tree ratings                                                           | yes                    |
| Bass, Clements, Kazman[^bass]           | Risk themes                                                                                                                                   | yes                    |
| `git blame`[^blame]                     | Line identity as commit plus original line number, followed across moves with `-M` and `-C`                                                   | yes                    |
| SARIF fingerprints[^sarif]              | `primaryLocationLineHash` as a rolling hash over a line. Checked and not adopted, because it removes duplicates and does not prove presence   | yes                    |
| Web Annotation text anchors[^anchor]    | Text plus prefix and suffix, found again by fuzzy matching. Checked and not adopted, because `in_use` asks for unchanged text                 | yes                    |
| IEEE 1028                               | Nothing yet. The design does not depend on it                                                                                                 | no                     |

## Open Questions

None.

## Completion Criteria

- `finding-classification.md` exists and defines the values of a finding, the
  shared scale, the consequence tree, and the five class sections, each with
  two or three examples per severity level. The examples are real findings. A
  level with no real finding yet has one invented example that names real
  project files.
- No other rulebook, skill, or agent in the boundaries defines a severity
  level. Each one links to the new rulebook.
- Each review skill and agent in the boundaries names its review class and
  links to its class section in `finding-classification.md`.
- `finding-lint` exits `1` on a finding whose `severity` does not match its
  `basis`, and the exit is covered by a test for each review class.
- `finding-lint` exits `1` on a code or security finding that records
  `in_use: false` while the lines its `artifact` names exist unchanged on
  `dev`. Tests cover a security finding, a range on `dev`, a range in the
  installed copy, a range whose lines shifted, a range that moved to another
  file, and a range in the installed copy whose lines git has no record of,
  which does not count as unchanged.
- `finding-lint` exits `1` and names the missing setting when the project
  defines no release-tag pattern, and checks only the tags that match it once
  it is set.
- `finding-lint` checks `in_use` only on a finding that is new against `HEAD`
  or whose `basis` or `artifact` differs from `HEAD`. A test merges the branch
  of a `major` finding into `dev`, then sets `status: waived` on it, and the
  lint still exits `0`. A second test runs `validate` on a new, uncommitted
  finding and shows that the check runs.
- `finding-lint` exits `1` on a finding with `status: waived` and an empty
  `override_by` or `override_reason`, and on a waived `critical` finding
  without `stop_confirmed_by`. A test shows that the loop `grep` of a playbook
  no longer lists a waived finding.
- `finding-lint` exits `1` on a `critical` finding without
  `## Possible damage`, and on a `stop_confirmed_by` without
  `stop_confirmed_reason`.
- A review that produces a `minor` finding writes one register file
  `docs/findings/register/<class>/<ID>.json` with `status: open` and files no
  finding file for it. `finding-lint` accepts the file against the schema of
  its class. It exits `1` on a register file whose `severity` does not match
  its `basis`, on a status other than `open`, `resolved`, or `waived`, on a
  waived register file without `override_by` or `override_reason`, and on a register
  file that `HEAD` holds and the commit removes without a finding file of the
  same ID.
- While an open `critical` finding has no `stop_confirmed_by`, `dispatch` and
  `premerge-check` exit `1` and print the stop notice with the finding's
  possible damage. A test covers each script, and a test shows that both run
  again once `stop_confirmed_by` and `stop_confirmed_reason` are set.
- `guard-human-fields` refuses an agent `Edit` that sets `stop_confirmed_by`
  in a finding file, and an agent `Bash` call that sets `status: waived`. Tests
  show that these pass: a new finding written from the template, a typo fix in
  a waived finding, an edit of the finding template, a read-only
  `grep "status: waived"`, and a heredoc that writes a test fixture.
- Each supported CLI runs `guard-human-fields` on the calls that
  [Fields only the human writes](#fields-only-the-human-writes) lists. For each
  patch call, `apply_patch` in Codex, Copilot CLI, and Pi and `patch` in
  OpenCode, a test shows that the CLI refuses a call that the guard cannot
  parse and whose text names a guarded path. In Pi and OpenCode, a test shows
  that a missing guard script blocks the call. `init-factory --cli opencode` links
  `agent-factory.ts` into `.opencode/plugins/`.
- `docs/testing.yaml` declares a `node:test` suite for
  `packages/factory/config/**/*.test.ts`, and the suite passes on Node 22.6 or
  later without a new dependency.
- At the pause point, the user sees every new `minor` finding with its
  `fails_purpose` sentence before any file is written.
- The final summary of a headless run lists each new register file with its
  `fails_purpose` sentence.
- The triage table in `rulebooks/templates/qa-strategy.md` has a
  `Consequence` column with the three values "harm if in use", "fails
  purpose", and "raises cost", and no severity column.
- Every row that the proposal-review agent writes in adversarial mode ends its
  Finding cell with a `Severity:` sentence, and the proposal template lists the
  status `waived` as set only by the stakeholder.
- A child-result envelope from any review carries the four keys `critical`,
  `major`, `minor`, and `note`.
- `finding-lint` exits `0` on `docs/findings/` after the migration. Every open
  finding carries `review_class`, and every resolved finding without it is
  skipped.
- No migrated finding is `open` with severity `minor`. The migration covers
  every open finding without `review_class` when it runs (DEC-54). Each
  migrated `minor` finding is a register file of its class under its old ID.
  Each line of the old `.jsonl` registers is a register file under its ID, and
  no `.jsonl` file remains in `docs/findings/register/`.
- After the migration commit, no open `critical` finding lacks
  `stop_confirmed_by`, and the migration review report states how many
  migrated findings are `critical`.
- The [agreement check](#agreement-check) passes when the two new runs agree on
  the severity of at least 16 of the 20 findings (DEC-08) and agree on more
  findings than the two old runs do. A review report in `docs/reviews/` records
  the quotas, the picks, the model, and both counts.

## Guiding Rule

The reviewer states the facts, and the rule states the severity.

# Appendix

## Decisions

| ID     | Date       | Kind       | Decided by  | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Raised by                                                          |
| ------ | ---------- | ---------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| DEC-01 | 2026-11-04 | decision   | stakeholder | Each review class gets its own classification criteria.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Chat discussion                                                    |
| DEC-02 | 2026-11-04 | decision   | stakeholder | Sources are named. The design does not copy standards that are not accessible and may draw on general domain knowledge instead.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Chat discussion                                                    |
| DEC-03 | 2026-11-04 | decision   | stakeholder | All classes record severity on one four-level scale (`critical`, `major`, `minor`, `note`) with one blocking threshold at `major`. Native ratings stay in `rating`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Grilling Q1                                                        |
| DEC-04 | 2026-11-04 | assumption | author      | The reviewer records a basis, a rule computes the severity, and `finding-lint` recomputes it.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Motivation                                                         |
| DEC-05 | 2026-11-04 | decision   | stakeholder | Security review does not use CVSS, SSVC, CWSS, or OWASP factor scoring. CVSS and SSVC need deployment and threat data, and factor judgments vary between runs. Superseded in its method by DEC-20.                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Grilling Q7b                                                       |
| DEC-06 | 2026-11-04 | decision   | stakeholder | Security impact uses the maximum of the four factors. OWASP allows an estimate instead of the mean, and IEEE 1044 and CVSS v3.1 treat impact as the worst case.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Source research. Superseded by DEC-20, which has no impact factors |
| DEC-07 | 2026-11-04 | assumption | author      | `finding-lint` skips findings without `review_class`, and migration of old findings is deferred. Superseded by DEC-24.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Design                                                             |
| DEC-08 | 2026-11-04 | assumption | author      | The agreement target is 80 %, that is 16 of 20 findings in the fixed set. It stays an assumption; the baseline condition in DEC-23 tests the proposal. Answers OQ-01.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Grilling Q11                                                       |
| DEC-09 | 2026-11-04 | decision   | stakeholder | In the document and code classes, the type follows from the fix that the finding demands, as ODC chooses it from the fix made.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Source research                                                    |
| DEC-10 | 2026-11-04 | decision   | stakeholder | Architecture severity uses the importance of the threatened scenario (source: DEC-19). Each non-risk names its assumptions.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Source research                                                    |
| DEC-11 | 2026-11-04 | decision   | stakeholder | The document class gains the type `compound` for a statement that bundles two requirements.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Source research                                                    |
| DEC-12 | 2026-11-04 | decision   | stakeholder | A `minor` finding becomes one row in the project register `docs/findings/register.md` and never blocks. Answers OQ-03. Storage changed by DEC-33.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | T-0016 grilling                                                    |
| DEC-13 | 2026-11-04 | decision   | stakeholder | Only the human overrides the computed blocking value, through `blocking_override`, `override_by`, and `override_reason`. The severity stays computed. Field replaced by the status `waived` in DEC-44.                                                                                                                                                                                                                                                                                                                                                                                                                                                        | T-0016 grilling                                                    |
| DEC-14 | 2026-11-04 | decision   | stakeholder | A `critical` finding stops the playbook run until the human confirms. A `major` finding loops back to its author.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Grilling Q2                                                        |
| DEC-15 | 2026-11-04 | decision   | stakeholder | `harms_downstream` asks whether the defective artifact is already in use (see DEC-16). The reviewer checks this fact and does not predict later gates.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Grilling Q3                                                        |
| DEC-16 | 2026-11-04 | decision   | stakeholder | An artifact is in use when something outside the current run depends on it: `dev`, `main`, the installed copy, a release, or an artifact the run did not produce. The feature branch of the run does not count.                                                                                                                                                                                                                                                                                                                                                                                                                                               | Grilling Q3b                                                       |
| DEC-17 | 2026-11-04 | decision   | stakeholder | `review_class` names the rule, not the review. A defect that ATAM review finds in an ADR or arc42 chapter belongs to the document class. The architecture class covers only findings measured against a quality scenario.                                                                                                                                                                                                                                                                                                                                                                                                                                     | Grilling Q4                                                        |
| DEC-18 | 2026-11-04 | decision   | stakeholder | The architecture matrix gives at most `major`. A risk becomes `critical` only when something built from the decision is in use (DEC-16).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Grilling Q5                                                        |
| DEC-19 | 2026-11-04 | decision   | stakeholder | Scenario importance comes from the priority in arc42 § 10.2: priority 1 is `high`, priority 2 is `medium`. A utility tree with H/M/L ratings is deferred.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Grilling Q6                                                        |
| DEC-20 | 2026-11-04 | decision   | stakeholder | Security severity comes from a bug bar: the effect class sets the level, each of four preconditions lowers it one step, and `critical` needs `in_use` and `proven` confidence.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Grilling Q7b                                                       |
| DEC-21 | 2026-11-04 | decision   | stakeholder | `finding-lint` checks `in_use` against `dev`, `main`, release tags, and the installed copy. Release tags refined by DEC-48. Every class records `in_use`, and `artifact` must resolve to a line range or a heading.                                                                                                                                                                                                                                                                                                                                                                                                                                           | Grilling Q9                                                        |
| DEC-22 | 2026-11-04 | decision   | stakeholder | The pause point shows each new `minor` finding with its `fails_purpose` sentence, so the user can raise a wrong downgrade. A headless run lists the rows in its final summary.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Grilling Q10                                                       |
| DEC-23 | 2026-11-04 | decision   | stakeholder | Agreement is measured by re-classifying a fixed set of 20 existing findings, twice with the new rulebook and twice with the old rules. The new rules must reach the target and beat the old ones.                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Grilling Q11                                                       |
| DEC-24 | 2026-11-04 | decision   | stakeholder | The 39 open findings are migrated once with the new rulebook; migrated `minor` findings become register rows under their old ID. The 208 resolved findings stay untouched. Corrected count: 208 files that are not `open`, 195 of them resolved (PROP-12). Answers OQ-02.                                                                                                                                                                                                                                                                                                                                                                                     | Grilling Q12                                                       |
| DEC-25 | 2026-11-04 | decision   | stakeholder | The override only sets a blocking finding to `false`. A `minor` finding never blocks, and no override raises it.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | review-loop-cap lector pass                                        |
| DEC-26 | 2026-11-04 | decision   | stakeholder | A document is in use only when stories or code outside the run encode its statement. The git check for `in_use` applies to code and runtime findings only. Extended to security by DEC-31.                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Lector pass C2                                                     |
| DEC-27 | 2026-11-04 | decision   | stakeholder | A `minor` finding carries one sentence for its "no" to `fails_purpose`, and `finding-lint` checks that the sentence exists.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Lector pass C4                                                     |
| DEC-28 | 2026-11-05 | decision   | stakeholder | `dispatch` and `premerge-check` hold the `critical` stop. The human confirms through `stop_confirmed_by` and `stop_confirmed_reason`; the finding then loops like a `major` one. A headless run ends with the stop notice.                                                                                                                                                                                                                                                                                                                                                                                                                                    | Review PROP-01, grilling Q1                                        |
| DEC-29 | 2026-11-05 | decision   | stakeholder | Only a `critical` finding carries `## Possible damage`, filled by the reviewer from git and the file tree, one check per item. The scripts print it in the stop notice, and the orchestrator explains the finding with `explain-review-finding`.                                                                                                                                                                                                                                                                                                                                                                                                              | Review PROP-01, grilling Q1b                                       |
| DEC-30 | 2026-11-05 | decision   | stakeholder | `finding-lint` compares line identities from `git blame -M -C --porcelain`, using `--contents` for the installed copy, and checks `in_use` only on finding files new or changed in the commit. Text matching and SARIF fingerprints are not used.                                                                                                                                                                                                                                                                                                                                                                                                             | Review PROP-02, grilling Q2                                        |
| DEC-31 | 2026-11-05 | decision   | stakeholder | The git check for `in_use` covers the security class as well as code and runtime. Document and architecture findings stay outside it.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Review PROP-03, grilling Q3                                        |
| DEC-32 | 2026-11-05 | decision   | stakeholder | Every finding, file or register line, gets its ID from `next-id` of the counter-ids proposal. Until it ships, the reviewer takes the next plausible number and avoids clashes by hand.                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Review PROP-16, grilling Q4                                        |
| DEC-33 | 2026-11-05 | decision   | stakeholder | `minor` findings go to one JSON Lines register per review class in `docs/findings/register/`, each with a JSON Schema. Blocking findings stay files. Removing a migrated `minor` file is the one exception to "never delete". Replaced by DEC-60.                                                                                                                                                                                                                                                                                                                                                                                                             | Review PROP-16, grilling Q4c and Q4d                               |
| DEC-34 | 2026-11-05 | decision   | stakeholder | The QA triage table states the consequence, not the severity. A defect that is not in use cannot harm production yet, so it is `major` and the automated loop fixes it; in use, it is `critical`.                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Review PROP-04, grilling Q5                                        |
| DEC-35 | 2026-11-05 | decision   | stakeholder | Migrated `critical` findings get `## Possible damage` from the migration agent and are confirmed by the human at the migration pause point, so no later run stops on them. The rarity claim based on old labels is replaced by the count in the migration report.                                                                                                                                                                                                                                                                                                                                                                                             | Review PROP-09, grilling Q6                                        |
| DEC-36 | 2026-11-05 | decision   | stakeholder | Claim review is not a review class. A refuted claim is a success, eliminating a bad argument, and harms nothing. `adversarial-review` keeps its scale; its envelope counts BLOCKER under `major`.                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Review PROP-05, grilling Q7                                        |
| DEC-37 | 2026-11-05 | decision   | stakeholder | The class follows the material for every source, not only reviews. Text that agents execute (playbooks, skills, agent definitions, rulebooks, hook configuration) is code. An observation without an artifact is not a finding; it becomes a retro action item or a todo entry.                                                                                                                                                                                                                                                                                                                                                                               | Review PROP-06, grilling Q8                                        |
| DEC-38 | 2026-11-05 | decision   | stakeholder | Proposal review rows stay in the Appendix. Severity comes from two questions, whether a planner must ask back (`major`) and whether a reader pays later (`minor`), with one severity sentence per row. A `major` row blocks acceptance; only the stakeholder sets `waived`. `finding-lint` skips proposals.                                                                                                                                                                                                                                                                                                                                                   | Review PROP-07, grilling Q9                                        |
| DEC-39 | 2026-11-05 | decision   | stakeholder | The agreement set is picked by class of material with fixed quotas (6 document, 5 code, 4 runtime, 2 architecture, 3 security). A `question` counts as disagreement. Each run is a fresh subagent with only the rules and the texts, on the review agents' model.                                                                                                                                                                                                                                                                                                                                                                                             | Review PROP-10, grilling Q10                                       |
| DEC-40 | 2026-11-05 | assumption | author      | The migration rewrites each `artifact` to the range of its fix. An open finding without an artifact moves into `todo.md`, and its file gets `status: deferred` with the todo ID.                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Review PROP-08                                                     |
| DEC-41 | 2026-11-05 | assumption | author      | A `question` is only a `todo.md` entry; no finding file and no register line carries the category.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Review PROP-17                                                     |
| DEC-42 | 2026-11-05 | decision   | stakeholder | The hook `guard-human-fields` refuses agent tool calls that set override or stop-confirmation fields or the row status `waived`. The design against an agent that hides the field name is deferred to gate-evidence.                                                                                                                                                                                                                                                                                                                                                                                                                                          | Review PROP-15, grilling Q11                                       |
| DEC-43 | 2026-11-05 | decision   | stakeholder | `finding-lint` checks `in_use` only when a commit adds the finding or changes its `basis` or `artifact`. Override, confirmation, status, and text changes do not trigger it.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Lector pass C4                                                     |
| DEC-44 | 2026-11-05 | decision   | stakeholder | The override is the status `waived` with `override_by` and `override_reason`; the field `blocking_override` is dropped. The loops keep `grep "status: open"`, so a waived finding drops out without playbook changes.                                                                                                                                                                                                                                                                                                                                                                                                                                         | Review PROP-19, grilling Q12                                       |
| DEC-45 | 2026-11-05 | decision   | stakeholder | `guard-human-fields` checks only finding files and proposal Appendix tables, and refuses only a value that was not there before: a non-null human field or the status `waived`. `Edit` and `Write` compare old and new; `Bash` checks the command text.                                                                                                                                                                                                                                                                                                                                                                                                       | Review PROP-20, grilling Q13                                       |
| DEC-46 | 2026-11-05 | decision   | stakeholder | `finding-lint` decides "new or changed" by comparing each finding file with its `HEAD` version: staged in pre-commit, working tree in `validate`. `validate --changed` is dropped.                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Review PROP-21, grilling Q14                                       |
| DEC-47 | 2026-11-05 | decision   | stakeholder | A `critical` finding can be waived only after its stop is confirmed with `stop_confirmed_by` and `stop_confirmed_reason`, so the damage checks run even when the finding stays unfixed. `finding-lint` checks this.                                                                                                                                                                                                                                                                                                                                                                                                                                           | Review pass 3, raised by the author                                |
| DEC-48 | 2026-11-06 | decision   | stakeholder | Each project defines which git tags count as release tags for the `in_use` check, as `release_tag_patterns` in the tracked file `docs/factory-settings.yaml`. No Factory default; without the file or the key, `finding-lint` exits `1` and names both. Refines DEC-21.                                                                                                                                                                                                                                                                                                                                                                                       | Requirements gaps FC-G07 and FC-C11                                |
| DEC-49 | 2026-11-06 | assumption | author      | Corrections from the QA strategy: the git check blames the `artifact` path plus the rename and copy sources of the branch diff, not the porcelain file name; the lint finds the installed copy through `_main_checkout.py`; the registers are `merge=union`; `finding-lint` validates register lines against their schemas. The two register parts are replaced by DEC-60.                                                                                                                                                                                                                                                                                    | QA strategy FC-QG03, QG04, QG07, QG08                              |
| DEC-50 | 2026-11-06 | decision   | stakeholder | The git check reads `dev` and `main` locally and as `origin/dev` and `origin/main`. A missing branch is skipped and named in the output.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Domain model Q3, QA strategy Q1                                    |
| DEC-51 | 2026-11-06 | decision   | stakeholder | `guard-human-fields` runs in every supported CLI: Claude Code, Codex, Copilot CLI, Pi, and OpenCode. Where a CLI lacks a hook for a call, the architecture names the gap and how the guard closes it.                                                                                                                                                                                                                                                                                                                                                                                                                                                         | QA strategy Q2                                                     |
| DEC-52 | 2026-11-06 | decision   | stakeholder | A `critical` finding becomes `resolved` only after its stop is confirmed. The stop holds until both confirmation fields hold text.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Domain model Q2, QA strategy Q5                                    |
| DEC-53 | 2026-11-06 | decision   | stakeholder | `finding-lint` also rejects an unknown status, an open `minor` or `note` file, and an ID that is both a file and a register line. The `fails_purpose` sentence carries the marker `no to fails_purpose`.                                                                                                                                                                                                                                                                                                                                                                                                                                                      | QA strategy Q3, Q4                                                 |
| DEC-54 | 2026-11-06 | decision   | stakeholder | The migration covers every open finding without `review_class`, 47 on 2026-11-06, not only the 39 counted on 2026-11-04.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Requirements gap FC-G01                                            |
| DEC-55 | 2026-11-06 | decision   | stakeholder | No agent sets `deferred` on a finding. Only the migration sets it, on an old finding without an artifact, and that file carries no `review_class`. `finding-lint` rejects `deferred` on a file that carries `review_class`. A person who sets a blocking finding aside uses `waived`.                                                                                                                                                                                                                                                                                                                                                                         | Spec review SPEC-0072, requirements gap FC-G09                     |
| DEC-56 | 2026-11-06 | decision   | stakeholder | Only the person lowers a filed finding. `finding-lint` compares each finding with `HEAD`; a falling severity, or a finding file that becomes a register line, needs `override_by` and `override_reason`, as a waiver does. Raising a severity stays free for agents (FC-G04).                                                                                                                                                                                                                                                                                                                                                                                 | Spec review note 4, requirements gap FC-G10                        |
| DEC-57 | 2026-11-06 | decision   | stakeholder | `dispatch` and `premerge-check` read each finding file in the working tree and at `HEAD`. A finding stops the run when either version is critical, and a confirmation in either version ends the stop. A change in the working tree that nobody commits does not end a stop.                                                                                                                                                                                                                                                                                                                                                                                  | Spec review SPEC-0071, requirements choice FC-C19                  |
| DEC-58 | 2026-11-06 | decision   | stakeholder | A `critical` finding is lowered only when its `HEAD` version holds text in `stop_confirmed_by` and `stop_confirmed_reason`. The human confirms the stop in one commit and lowers the finding in a later one.                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Spec review SPEC-0071, requirements choice FC-C20                  |
| DEC-59 | 2026-11-06 | decision   | stakeholder | A finding lowered from `critical` to `major` drops `stop_confirmed_by` and `stop_confirmed_reason`, because only a `critical` finding carries them. Its `HEAD` version keeps the confirmation in git history.                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Spec review SPEC-0071, requirements choice FC-C21                  |
| DEC-60 | 2026-11-07 | decision   | stakeholder | A `minor` finding is one register file `docs/findings/register/<class>/<ID>.json` with the status `open` or `resolved`. The reviewer agent writes `open`, and the fixing commit sets `resolved` instead of deleting the file. `finding-lint` runs `schema-validate` on each file and recomputes its severity. No union merge and no `.gitattributes` line. Lowering and the ID rule of DEC-53 become checks between two file paths, and `guard-human-fields` guards `docs/findings/register/**/*.json`. The migration moves each line of the old `.jsonl` registers into one file. Replaces DEC-33, the register parts of DEC-49, and the deletion of FC-C13. | Architecture decision 1, option C                                  |
| DEC-61 | 2026-11-07 | decision   | stakeholder | Claude Code registers `guard-human-fields` on `Edit`, `MultiEdit`, `Write`, `NotebookEdit`, and `Bash`. Codex refuses an `apply_patch` call that the guard cannot parse when its raw text names a guarded path. Copilot CLI uses `preToolUse` entries in a hook file under `.github/hooks/`. Pi and OpenCode block the call when the guard script is missing. This feature writes a first, guard-only OpenCode plugin at `packages/factory/config/plugins/agent-factory.ts`; `init-factory` links it into `.opencode/plugins/` and accepts the CLI name `opencode`. Refines DEC-51. Patch rule extended to every CLI by DEC-64.                               | Architecture decision 2                                            |
| DEC-62 | 2026-11-07 | decision   | stakeholder | The TypeScript tests in `packages/factory/config/**/*.test.ts` run as a `node:test` suite on Node 22.6 or later, with no new dependency. The test-strategy agent writes the entry in `docs/testing.yaml`. Answers FC-QG25.                                                                                                                                                                                                                                                                                                                                                                                                                                    | Architecture decision 3                                            |
| DEC-63 | 2026-11-07 | decision   | stakeholder | A register file may hold `open`, `resolved`, or `waived`. Only the stakeholder sets `waived`, with non-empty `override_by` and `override_reason`, as on a finding file (DEC-44). `guard-human-fields` refuses `waived` from an agent. `deferred` and a missing status still fail. A waived register file is a `minor` finding that nobody will fix, accepted as is. Changes FC-C23 and the register part of DEC-60.                                                                                                                                                                                                                                           | FC-C23                                                             |
| DEC-64 | 2026-11-07 | assumption | author      | Correction from the architecture review: the patch rule of DEC-61 covers every patch call, not only the Codex one. The OpenCode plugin guards the tools `edit`, `write`, `patch`, `shell`, and `execute`, and the guard checks the JavaScript of an `execute` call as the text of a shell call. Changes DEC-61.                                                                                                                                                                                                                                                                                                                                               | ATAM-0018                                                          |

## Review findings

| ID      | Pass | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Resolution                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ------- | ---- | -------- | ----- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | 1    | major    | 03    | resolved | § What a blocking finding does (L223-234) and Completion Criteria (L789-791): the stop for a `critical` finding has no mechanism. The review loops in the playbooks run only `grep -l "status: open"` (for example `playbooks/feature-addition.md:354`) and never read the severity. The proposal does not say which component reads the severity, where the human's confirmation is recorded, what a headless run does while it waits, or whether a confirmed `critical` finding then loops back like a `major` one. Name the component (playbook text or `scripts/dispatch`), the confirmation record, and the headless behavior.                                                                                                                                                                                                                                                                                                                                                                                                  | § What a blocking finding does now names the mechanism: `dispatch` and `premerge-check` refuse to run on an open, unconfirmed `critical` finding (DEC-28). The confirmation record is `stop_confirmed_by` and `stop_confirmed_reason`. A headless run ends with the stop notice, and a confirmed finding loops like a `major` one. The notice and `## Possible damage` are defined in DEC-29. Completion Criteria and Scope carry both.         |
| PROP-02 | 1    | major    | 03    | resolved | § `finding-lint` (L592-598, L617-622): the `in_use` check does not define its comparison. It does not say whether "unchanged" means the same path at the same line numbers or the same text anywhere in the file, how a common line such as `}` counts, how a `path#anchor` artifact is compared, or what "the installed copy" means in a consumer project. The result also changes with git state. Once the feature branch merges into `dev`, an open `major` code finding with `blocking_override: false` fails the lint on every later commit. Define the comparison, and say whether the lint checks `in_use` only when the finding is written or on every run.                                                                                                                                                                                                                                                                                                                                                                  | § `finding-lint` now defines the comparison in "Line identity": `git blame -M -C --porcelain` identities on `dev`, `main`, release tags, and the installed copy through `--contents`, which handles shifted lines, moved lines, and common lines. The lint checks only new or changed finding files, so a merge does not turn a correct answer false. A consumer project skips the installed copy (DEC-30). Completion Criteria name the tests. |
| PROP-03 | 1    | major    | 03    | resolved | § Class: security, step 4 (L418-420) and § `finding-lint` (L592, L604-606): a security Critical becomes `critical` only when `in_use` is `true`, but the git check covers only the code and runtime classes. So a security reviewer on a feature branch can record `in_use: false` for vulnerable lines that are already on `dev`, and the stop never fires. This is the same failure that the BUG-0037 example at L617-622 uses to justify the check. Extend the git check to the security class, or state why security is exempt.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | § `finding-lint` now runs the git check for code, runtime, and security findings, and explains why architecture stays out (DEC-31). Completion Criteria add a test for a security finding on lines that exist on `dev`.                                                                                                                                                                                                                         |
| PROP-04 | 1    | major    | 03    | resolved | § Class: runtime (L516-521): the QA strategy maps `blocking` to `critical`, and the triage table in `rulebooks/templates/qa-strategy.md:87` puts data loss under `blocking`. The consequence tree at L291-295 gives data loss on the feature branch `major`, because the code is not in use. A reviewer who follows the triage table records `critical`, and the lint rejects it. Say which rule wins, for example that `blocking` means `critical` when the code is in use and `major` otherwise.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | § Class: runtime now has the triage table state the consequence in a `Consequence` column, and the tree with `in_use` computes the severity (DEC-34). Data loss on the feature branch is `major`, on `dev` `critical`. Scope and Completion Criteria name the template change.                                                                                                                                                                  |
| PROP-05 | 1    | major    | 03    | resolved | § Class: claim (L523-529): the claim class has no `basis` shape, no meaning for `in_use`, and no finding files, because `adversarial-review` writes research-review records checked by `rulebooks/schemas/research-review.schema.json`. So the lint rule "`basis` has the shape its class requires" (L584) and the criterion "a test for each review class" (L775) cannot be met for this class. "BLOCKER becomes `critical`" conflicts with the meaning of `critical` at L202, and `adversarial-review` keeps its own scale against the criterion at L772. Define the claim basis, files, and stop behavior, or limit the class to the envelope mapping and exempt it in the lint and the criteria. The research-review template and schema are not in `impact.boundaries`.                                                                                                                                                                                                                                                         | The claim class is removed (DEC-36). § Claim review stays outside explains why and maps only the envelope counts, with BLOCKER under `major`. `adversarial-review` left the boundaries, the class list has five entries, and Deferred names the reason.                                                                                                                                                                                         |
| PROP-06 | 1    | major    | 02    | resolved | `impact.boundaries` (L14-36) and Scope (L659-661): several files that set filing thresholds lie outside the boundaries, so a planner cannot tell whether their stories are in. `agents/spec-review-agent.md:63` files "Major+ findings", `agents/architecture-review-agent.md:67` files "Medium+ risks", and `agents/reconciliation-agent.md` files `RECON` findings. The pre-commit hook is defined in `packages/factory/config/pre-commit-config.yaml` and `config/hook-metadata.yaml`, not in `scripts/`. Open findings also come from sources that no class names: `grilling`, `diagnosis`, `retro`, `onboarding`, and `dispatch-run`. Add these files to the boundaries or to the deferred list, and say which rule applies to findings from those sources.                                                                                                                                                                                                                                                                     | `impact.boundaries` now list spec-review-agent, architecture-review-agent, reconciliation-agent, `config/pre-commit-config.yaml`, and `config/hook-metadata.yaml`. § The values of a finding states that the class follows the material for every source, that agent-executed text is code, and that an observation without an artifact is not a finding (DEC-37).                                                                              |
| PROP-07 | 1    | major    | 03    | resolved | § Class: document (L321-340): proposal review writes its findings as rows in the proposal's Appendix, and `agents/proposal-review-agent.md` forbids finding files. The proposal does not say where such a row keeps its `basis` and its "Why this severity" sentence, whether a `minor` proposal finding goes to the register or stays in the table, or whether `finding-lint` and the override apply to it. The `Severity` column of `rulebooks/templates/proposal.md` is not in the boundaries. State how the document class applies to Appendix rows.                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | § Class: document now has "Proposal review rows": rows stay in the Appendix, severity from `fails_purpose` and `raises_cost` with a `Severity:` sentence per row, `minor` rows stay in the table, the stakeholder alone sets `waived`, and `finding-lint` skips proposals (DEC-38). The proposal template joined the boundaries; Scope and Completion Criteria carry the change.                                                                |
| PROP-08 | 1    | major    | 03    | resolved | § Migration of open findings (L635-642) and Completion Criteria (L779-781): the migration writes `review_class`, `basis`, and the "Why this severity" line, but not `artifact`. Many open findings name a whole file or folder, which the lint rule at L590 rejects. BUG-0016 names `docs/`, BUG-0086 names `packages/factory/scripts/dispatch`, RECON-cycle-retirement names `docs/ and packages/factory/`, and RETRO-0002 has no artifact. So "`finding-lint` exits `0` on `docs/findings/` after the migration" fails as written. Add the rewrite of `artifact` to the migration steps, or exempt migrated findings from that rule.                                                                                                                                                                                                                                                                                                                                                                                               | § Migration now rewrites `artifact` to the range of the fix and moves a finding without an artifact into `todo.md`, with its file set to `deferred` (DEC-37, DEC-40). So the lint can exit `0` after the migration.                                                                                                                                                                                                                             |
| PROP-09 | 1    | major    | 03    | resolved | § What a blocking finding does (L236-239): "Of the 247 existing findings, 15 are `critical`, so the stop is rare" counts the old labels, but the new `critical` means harm plus `in_use`. Most open code findings point at code that is already on `dev`, for example BUG-0086, BUG-0105, and BUG-0114, and BUG-0105 describes a wrong result. Under the new rule such findings are likely `critical`, so the migration itself may produce several stops. The proposal does not say which run a migrated `critical` finding stops. Replace the claim with a count from a trial classification of the 39 open findings, and state what a migrated `critical` finding stops.                                                                                                                                                                                                                                                                                                                                                           | The rarity claim is gone; the migration review report records the count. § Migration now has the migration agent fill `## Possible damage` for each migrated `critical` finding and the human confirm it at the pause point, so the migration commit holds no unconfirmed stop (DEC-35). A Completion Criterion checks this.                                                                                                                    |
| PROP-10 | 1    | major    | 01    | resolved | Completion Criteria, agreement check (L796-805): the fixed set cannot be built as written. `docs/findings/` holds no claim-class findings. The only resolved security finding with frontmatter is SEC-0003, which is a worked example of this proposal and so excluded, and SEC-0005 and SEC-0006 have no frontmatter. The criterion also does not say how a `question` result, which has no severity, counts toward agreement, or which agent and model make a "fresh run". Say how classes without eligible findings are handled, and define both points.                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | The claim class is gone (DEC-36). The set is now picked by class of material with fixed quotas; security draws on FAGAN-0021, SEC-0005, and SEC-0006, whose text suffices without frontmatter. A `question` counts as disagreement, and a fresh run is defined as a new subagent with only the rules and the texts, on the review agents' model (DEC-39).                                                                                       |
| PROP-11 | 1    | minor    | 01    | resolved | Completion Criteria (L769-806): three Scope items have no criterion: the headless final summary (L668-670), the QA strategy alignment (L661), and the class link in each review skill (L659-660). The criterion "at least two examples per severity level" (L771) also conflicts with Design Details (L721-722), which allows one invented example where no real one exists, and with Scope (L653), which says two or three. Add the three criteria and pick one example rule.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Completion Criteria now cover the class link in each review skill and agent, the headless final summary, and the QA triage table (DEC-34). The example rule reads the same in Scope, Design Details, and Completion Criteria: two or three per level, real where one exists, else one invented.                                                                                                                                                 |
| PROP-12 | 1    | minor    | 02    | resolved | Summary (L117-119), Migration (L644-645), and § `finding-lint` (L578-579): at HEAD, `docs/findings/` holds 195 `resolved` files, not 208. The other 13 are IMPL-0003 with `status: deferred` and 12 files without frontmatter. Of these, `BUG-HUNT.md`, `qa-handoff-envelope.md`, and `qa-review-summary.md` are not findings, and FAGAN-0029 says "Improvement opportunity". So "only resolved findings lack the field" is false. Motivation (L142-143) also leaves out the exception in `finding-format.md:16`: Minor findings are filed when the user asks. The other counts (247 files, 39 open, the severity spellings, and the tag breakdown) match. Correct the counts, and say how the lint and the migration treat deferred and frontmatter-less files.                                                                                                                                                                                                                                                                     | Summary, § `finding-lint`, § Migration, and Deferred now give 195 resolved, 1 deferred, and 12 files without frontmatter, three of them not findings. The lint skips every file without `review_class`. Motivation names the "unless the user asks" exception.                                                                                                                                                                                  |
| PROP-13 | 1    | minor    | 03    | resolved | § Class: document (L326-331): the design states that the nine document types "follow the quality characteristics of requirements from ISO/IEC/IEEE 29148" and cites § 5.2.5 and § 5.2.6. The Sources table (L744) and the footnote say that only the table of contents was read and that the list is unchecked. So the attribution goes beyond what was read. Present the types as the factory's own list, or read the two sections and check the list.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | § Class: document now presents the types as the factory's own list that draws on ISO/IEC/IEEE 29148 and says the list was not checked against the standard's text.                                                                                                                                                                                                                                                                              |
| PROP-14 | 1    | minor    | 03    | resolved | § What a blocking finding does (L236-238): "Gilb describes a further tier above it, whose downstream effect is an order of magnitude larger" attributes a quantity to Gilb and Graham. The Sources table (L741) and the footnote say that only a search excerpt of a different Gilb paper was read. The design also defines `critical` by `in_use`, not by the size of the downstream cost, so the citation does not support the split as designed. Drop the quantity, or name the excerpt as the only source and say what it supports.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | § What a blocking finding does drops the quantity. It names a tier above major from inspection practice and states that this design defines the tier by `in_use`, not by cost.                                                                                                                                                                                                                                                                  |
| PROP-15 | 1    | minor    | 06    | resolved | Open Questions (L765) and § Human override (L251-255): "None" hides one genuine open question. Nothing checks that only the human sets an override, and the design defers to `gate-evidence.md`, which is a `draft` stub that decides nothing. Record this as an open question or an explicit deferral, and say what the first release does until that proposal settles.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | § Human override now names the hook `guard-human-fields`, which refuses agent writes of the override and confirmation fields (DEC-42). The hidden-field path is an explicit deferral that points to gate-evidence, not a silent "None". Scope, boundaries, and Completion Criteria carry the hook.                                                                                                                                              |
| PROP-16 | 1    | major    | 03    | resolved | § Shared severity scale and blocking rule (L214-221) and Migration (L638-639): a new `minor` register row has no ID scheme; only migrated rows keep their old ID. `finding-format.md:22` allocates the next ID by scanning finding files, so removing a migrated file lets a later finding reuse its ID. `finding-format.md:43` also says a finding file is never deleted, and the Scope does not change that rule. Define the ID of a register row, make ID allocation read the register, and add both rule changes to the Scope.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Every finding gets its ID from `next-id`; until it ships, the reviewer takes the next plausible number and checks by hand (DEC-32), so a removed file cannot free an ID. `minor` findings go to one JSON Lines register per class with a schema each (DEC-33). Scope now carries the registers and the one exception to "never delete" for migrated `minor` files.                                                                              |
| PROP-17 | 1    | minor    | 03    | resolved | § The values of a finding (L186-188) and § `finding-lint` (L586): a `question` "goes to `docs/spec/work/todo.md`", but the lint rule "a `question` carries no severity" implies that question finding files exist. Say whether a question is a finding file, a todo entry, or both.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | § The values of a finding makes a `question` a `todo.md` entry only, and the lint rule now says no file or register line carries the category (DEC-41).                                                                                                                                                                                                                                                                                         |
| PROP-18 | 1    | minor    | 08    | resolved | Frontmatter estimate (L51-57): `normalized_tokens` of 25,000 to 50,000 is below a rough count of the edits. The rulebook with six class sections and about 60 calibration examples is about 13,000 tokens. `finding-lint` with the git comparison and its tests is about 10,000 to 15,000, the migration of 39 findings about 12,000, and the edits to some 25 files about 8,000. That gives about 45,000 to 80,000. Raise the range or set it to `unknown`. The multiplier of 20 fits the playbook.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | The estimate is now 55,000 to 95,000 normalized tokens, 1.1 to 1.9 million consumed, and 5 to 9 review hours, as of 2026-11-05. The range includes the grilling additions: the stop in two scripts, five register schemas, and the proposal-review rows.                                                                                                                                                                                        |
| PROP-19 | 2    | major    | 03    | resolved | § Human override (L623-629) and § Register of minor findings (L670-671): the override has no reader. The design says that the loop stops waiting for an overridden finding. But every review loop runs `grep -l "status: open"`, for example `playbooks/feature-addition.md:354` and `playbooks/bug-fix.md:88`, and an overridden finding stays `open`. Scope changes neither the playbook loops nor `finding-format.md` § How the orchestrator reads findings. No Completion Criterion tests the override. Name the component that skips a finding with `blocking_override: false`, add it to Scope, and add a criterion. Severity: `fails_purpose` is yes, because a planner would cut no story for the loop, and the override would then change nothing.                                                                                                                                                                                                                                                                          | The override is now the status `waived` with `override_by` and `override_reason` (DEC-44). The existing `grep "status: open"` in every loop skips it, so no playbook changes. § Human override, § Finding file, `finding-lint`, the guard, Scope, and Completion Criteria use the status; a criterion tests that the loop grep no longer lists a waived finding.                                                                                |
| PROP-20 | 2    | major    | 03    | resolved | § Fields only the human writes (L635-639): the hook `guard-human-fields` has no path scope and no rule for what "sets" means. The finding template at L717-721 writes `blocking_override: null` and `stop_confirmed_by: null` into every new finding. The rulebook, the templates, `proposal-review-agent.md`, and the `finding-lint` test fixtures also name these fields, and the fixtures set them. A text check on the field names refuses all of these writes, so the review agents and the stories of this feature cannot write their files. State which paths the hook guards, that only a non-null value counts as set, and where the hook story falls in the order. Severity: `fails_purpose` is yes, because a planner cannot cut or order the hook story without asking.                                                                                                                                                                                                                                                  | § Fields only the human writes now scopes the hook to finding files and proposal Appendix tables and defines "sets" as a new non-null value or the status `waived`, compared old against new for `Edit` and `Write` (DEC-45). Templates, the rulebook, and fixtures lie outside, so story order stays free. Completion Criteria test a template write, a typo fix, and a template edit.                                                         |
| PROP-21 | 2    | major    | 03    | resolved | § The git check for in use (L812-818): the trigger "when the commit adds the finding or changes its `basis` or its `artifact`" has no meaning outside a commit. The `validate` skill runs "without needing a git commit", and neither `skills/validate/SKILL.md` nor `scripts/validate` has a `--changed` option. So the reference to `validate --changed` is wrong, and Scope does not add the option. The criterion "`finding-lint` exits `0` on `docs/findings/` after the migration" (L1086) is a full run as well. Say what a run without a commit compares against, for example the merge base with `dev`, and add `--changed` to Scope or drop it. Severity: `fails_purpose` is yes, because a planner must ask whether a `validate` story exists and what a full run checks.                                                                                                                                                                                                                                                 | § The git check for in use now compares each finding file with its `HEAD` version, staged in pre-commit and working tree in `validate`, so the rule holds outside a commit (DEC-46). `validate --changed` is gone. A criterion tests `validate` on a new, uncommitted finding.                                                                                                                                                                  |
| PROP-22 | 2    | minor    | 03    | resolved | § Line identity, step 2 (L838), and Completion Criteria (L1051-1052): step 2 blames "the same path" on `dev`, `main`, and each release tag. A range that moved to another file on the feature branch does not exist at that path on `dev`. So the required test "a range that moved to another file" fails as the step is written. The `--porcelain` output names the original file of each line, so step 2 can blame that file instead. Severity: the planner can act, because the criterion names the test, but the step misleads the implementer.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | § Line identity step 2 now blames the original file that the porcelain output names for each line, so a range moved to another file is found in its old file.                                                                                                                                                                                                                                                                                   |
| PROP-23 | 2    | minor    | 04    | resolved | Frontmatter `impact.architecture_change: false` (L12): the design adds the hook `guard-human-fields`, the gate `finding-lint`, and a dependency of `dispatch` and `premerge-check` on `docs/findings/`. `docs/spec/architecture.dsl` models hooks and gates as components, for example `block-dangerous-git.sh` at L41. So the feature changes the module structure, by the rule in `playbooks/feature-addition.md` Step 1.4. Set the flag to `true`, or say why these parts stay outside the model. Severity: the planner can act, because the mechanical check in Step 1.4 corrects the flag, but the routing reads wrong until then.                                                                                                                                                                                                                                                                                                                                                                                              | `impact.architecture_change` is now `true`, and `docs/spec/architecture.dsl` joined the boundaries for the new hook, gate, and script dependency.                                                                                                                                                                                                                                                                                               |
| PROP-24 | 2    | minor    | 03    | resolved | § In use (L277-279): "no migration code is built from it yet" is false at the reviewed commit. `scripts/migrate-spec-layout` implements ADR-0026 and moves untracked files with a plain move, and ATAM-0004 is `resolved`. The example holds only for the time of that review. Say so, for example "when ATAM review filed ATAM-0004, no migration code was built from ADR-0026". Severity: the planner can act, but a reader who checks the example finds the code and doubts the rule.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | § In use now tells the ATAM-0004 example in the past tense: when ATAM review filed it, no migration code was built from ADR-0026.                                                                                                                                                                                                                                                                                                               |
| PROP-25 | 2    | minor    | 03    | resolved | Scope, Explicitly deferred (L978): "OWASP asks for eight" factor judgments is too low. The OWASP Risk Rating Methodology rates eight likelihood factors and eight impact factors, 16 in all, the same count the sentence gives for CWSS. Correct the number, or say that it counts the likelihood factors only. Severity: the planner can act, because the item is deferred, but the wrong number misleads a reader.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | The deferred item now says OWASP asks for 16 factor judgments, eight for likelihood and eight for impact.                                                                                                                                                                                                                                                                                                                                       |
| PROP-26 | 3    | minor    | 03    | fixed    | Primer (L117-119): the Primer says that the guard "refuses any agent edit that names these fields". § Fields only the human writes (L646-657) refuses only a value that was not there before, so an agent may write the template, the rulebook, the fixtures, and a typo fix in a waived finding (DEC-45). Change the Primer sentence to say that the guard refuses an agent edit that sets one of these fields. Severity: the planner can act, because the Design defines the rule, but a reader who starts with the Primer expects the opposite rule.                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | The Primer now says the guard refuses any agent edit that gives these fields a value, which matches the new-value rule of DEC-45.                                                                                                                                                                                                                                                                                                               |
| PROP-27 | 3    | minor    | 03    | fixed    | § Fields only the human writes (L646-657) and Completion Criteria (L1097-1100): the path scope and the meaning of "sets" are defined for `Edit` and `Write`, but not for `Bash`. A command does not always name the file it changes, and the Bash rule checks the command text for `waived` without a path. Read literally, the hook refuses a heredoc that writes a test fixture with `override_by: human`, and a read-only `grep "status: waived"`. That conflicts with L647-648, which leaves the fixtures free for the stories of this feature. The rule also does not say how the hook tells the Status cell `waived` in a proposal table from the same word in a Finding or Resolution cell. State the Bash match, for example an assignment in a command that names a guarded path, and add a Bash call to the tests that pass. Severity: the planner can cut and order the hook story, because `Edit` and `Write` are defined, but the implementer must pick the Bash match, and a literal match blocks legitimate commands. | § Fields only the human writes now limits the `Bash` rule to commands that write into a guarded path, and matches `waived` only in a `status:` line or the Status cell of a proposal row. Completion Criteria test that a read-only `grep` and a fixture heredoc pass.                                                                                                                                                                          |

## Review passes

| Pass | Date       | Reviewed commit                          | Disposition | Failed checks      | Summary                                                                                                                                                                                                                                                                                                                                                                                                               |
| ---- | ---------- | ---------------------------------------- | ----------- | ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | 2026-11-05 | db41f06e2dab91ac95e34ecbd09c00e597c7f2e9 | findings    | 01, 02, 03, 06, 08 | Checks 04, 05, and 07 pass: the impact flags fit the design, every boundary path resolves, and the motivation names a concrete cost. The design leaves the `critical` stop, the `in_use` comparison, the claim class, proposal-review rows, and register IDs undefined, so a planner would have to ask back (11 major, 7 minor). The reviewed text is HEAD plus an uncommitted change to `status` and `updated` only. |
| 2    | 2026-11-05 | db58284ba233ee6515a13718518ab50721505c40 | findings    | 03, 04             | All 18 pass-1 findings are resolved. Checks 01, 02, 05, 06, 07, and 08 pass. Check 03 fails: the override has no reader in the loop, the hook `guard-human-fields` has no path scope, and the `in_use` trigger needs a commit that `validate` does not have (3 major, 3 minor). Check 04 fails on `architecture_change` (1 minor).                                                                                    |
| 3    | 2026-11-05 | 117186cb6acd78ccd35f507cce1f46f5d37c3ee1 | clean       | 03 (minor only)    | All seven pass-2 findings, PROP-19 to PROP-25, are resolved. Checks 01, 02, and 04 to 08 pass, and check 04 now fits the design. Check 03 yields two minor rows on the guard `guard-human-fields`: PROP-26 for the Primer wording and PROP-27 for the `Bash` rule. No `major` row is open, so the rows do not block acceptance.                                                                                       |

______________________________________________________________________

[^odc]: Ram Chillarege et al., "Orthogonal Defect Classification – A Concept for In-Process Measurements", *IEEE Transactions on Software Engineering* 18(11), 1992, <https://chillarege.com/docs/Papers/concept>.

[^ieee1044]: IEEE Std 1044-2009, *IEEE Standard Classification for Software Anomalies*, Table 3 (defect attributes) and Annex A, Table A.1 (example values), <https://standards.ieee.org/ieee/1044/4607>.

[^cc]: Conventional Comments, <https://conventionalcomments.org/>.

[^gilb]: Tom Gilb and Dorothy Graham, *Software Inspection*, Addison-Wesley, 1993. The wording above comes from a search excerpt of Tom Gilb, *Planning to get the most out of inspection*, <https://www.researchgate.net/publication/228836546_Planning_to_get_the_most_out_of_inspection>. Neither text was read in full.

[^nasa]: NASA, *Software Engineering Handbook*, inspection defect classification, <https://swehb.nasa.gov/x/UQFiC>.

[^iso29148]: ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life cycle processes — Requirements engineering*, § 5.2.5 and § 5.2.6. Only the table of contents was read. The list of characteristics is unchecked.

[^google]: Google, *Engineering Practices: How to write code review comments*, <https://google.github.io/eng-practices/review/reviewer/comments.html>.

[^sdl]: Microsoft, *SDL Security Bug Bar (Sample)*, <https://learn.microsoft.com/en-us/security/engineering/security-bug-bar-sample>.

[^chromium]: The Chromium Projects, *Severity Guidelines for Security Issues*, <https://chromium.googlesource.com/chromium/src/+/HEAD/docs/security/severity-guidelines.md>.

[^wunder]: Wunder, Kurtz, Eichenmüller, Gassmann, Benenson, "Shedding Light on CVSS Scoring Inconsistencies: A User-Centric Study on Evaluating Widespread Security Vulnerabilities", *IEEE Symposium on Security and Privacy*, 2024, <https://arxiv.org/abs/2308.15259>.

[^cwss]: MITRE, *Common Weakness Scoring System (CWSS)*, version 1.0.1, <https://cwe.mitre.org/cwss/cwss_v1.0.1.html>.

[^semgrep]: Semgrep, *Contributing rules: rule metadata* (`likelihood`, `impact`, `confidence`), <https://docs.semgrep.dev/contributing/contributing-to-semgrep-rules-repository>.

[^scorecard]: OpenSSF, *Scorecard checks*, Pinned-Dependencies, <https://github.com/ossf/scorecard/blob/main/docs/checks.md>.

[^codeql]: GitHub, "CodeQL code scanning: new severity levels for security alerts", changelog, 2021-07-19, <https://github.blog/changelog/2021-07-19-codeql-code-scanning-new-severity-levels-for-security-alerts/>.

[^atam]: Rick Kazman, Mark Klein, Paul Clements, *ATAM: Method for Architecture Evaluation*, CMU/SEI-2000-TR-004, August 2000, § Step 5 (utility tree) and § Risks and Non-Risks, <https://www.sei.cmu.edu/documents/629/2000_005_001_13706.pdf>.

[^bass]: Len Bass, Paul Clements, Rick Kazman, *Software Architecture in Practice*, chapter on ATAM, <https://people.ece.ubc.ca/matei/EECE417/BASS/ch11lev1sec2.html>.

[^blame]: Git documentation, `git blame`, options `--porcelain`, `-M`, `-C`, and `--contents`, <https://git.github.io/htmldocs/git-blame.html>. Tried on `packages/factory/scripts/dispatch:120-122` against `dev` and the installed copy on 2026-11-05: both gave the same identities.

[^cvss4]: FIRST, *CVSS v4.0 Specification Document*, Table 22 (qualitative severity rating scale), <https://www.first.org/cvss/v4.0/specification-document>.

[^ssvc]: CERT/CC, *SSVC: Stakeholder-Specific Vulnerability Categorization*, supplier decision tree, <https://certcc.github.io/SSVC/howto/supplier_tree/>.

[^owasp]: OWASP, *OWASP Risk Rating Methodology*, Steps 2, 4, and 6, <https://community.owasp.org/OWASP_Risk_Rating_Methodology>.

[^jpl]: John C. Kelly, Joseph S. Sherif, Jonathan Hops, "An Analysis of Defect Densities Found During Software Inspections", *Proceedings of the 15th Annual Software Engineering Workshop*, NASA Goddard Space Flight Center, 1990, <https://ntrs.nasa.gov/api/citations/19920010193/downloads/19920010193.pdf>.

[^cvss31]: FIRST, *CVSS v3.1 Specification Document*, § 7.1 Base Metrics Equations, <https://www.first.org/cvss/v3.1/specification-document>.

[^seicvss]: Software Engineering Institute, Carnegie Mellon University, *Towards Improving CVSS*, <https://www.sei.cmu.edu/library/towards-improving-cvss/>.

[^sarif]: GitHub, `codeql-action`, `fingerprints.ts`, <https://github.com/github/codeql/discussions/5982> links the implementation. The collision count of 115 in 1,783 fingerprints comes from csdiff issue 98, <https://github.com/csutils/csdiff/issues/98>.

[^anchor]: W3C, *Web Annotation Extensions for Web Publications*, Text Quote Selector, <https://www.w3.org/TR/wpub-ann/>; Hypothesis, *Fuzzy Anchoring*, <https://web.hypothes.is/blog/fuzzy-anchoring/>.
