---
schema_version: 2
title: Finding Classification
status: draft
owner: agent-factory
created: 2026-11-04
updated: 2026-11-04
supersedes:

impact:
  scope: cross_component
  architecture_change: false
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
    - packages/factory/skills/adversarial-review/SKILL.md
    - packages/factory/skills/validate/SKILL.md
    - packages/factory/agents/code-review-agent.md
    - packages/factory/agents/proposal-review-agent.md
    - packages/factory/agents/qa-agent.md
    - packages/factory/scripts
    - docs/spec/interface-contracts.md
    - packages/factory/playbooks
    - packages/factory/skills/run-step/SKILL.md

governance:
  assurance: elevated
  risk_domains:
    - reliability
    - security

estimate:
  as_of: 2026-11-04
  basis: judgment
  confidence: low
  human_review_hours:
    min: 4.0
    max: 7.0
  normalized_tokens:
    min: 25000
    max: 50000
  estimated_consumption:
    min: 500000
    max: 1000000
    overhead_multiplier: 20
    playbook: feature-addition
---

# Feature Request: Finding Classification

## Primer

Agents review the work of other agents. Each problem a review
finds becomes a finding, a short record that says what is wrong and how to
fix it. Each finding's severity decides what happens next. The orchestrator is
the agent that starts each step of the work. It sends serious findings back to their author and waits for the fix.

The same review, run twice on the same work, rates its findings differently.
The levels are defined by adjectives such as "significant", and the reviews
use six different scales. So a borderline finding is sent back on one run and
dropped on the next, and the fix loop runs longer or shorter by chance.

The proposal gives each finding separate values. The category says what kind
of finding it is: a defect, a risk, a suggestion, or a question. The type says
which part of the work fails. The severity says how bad it is, on one shared
scale: critical, major, minor, or note. A review class, such as document,
code, or security, names the rule that sets the severity. The class follows
from the material, not from the review that found the problem.

The reviewer records facts, and a fixed rule computes the severity. For
documents, code, and runtime behavior, the reviewer answers three yes-or-no
questions in order. Does the problem cause harm, such as a wrong result or data
loss, and is the work already in use? Work is in use when something outside the current run
depends on it. Does the work fail its own purpose? Does it only make later
reading, change, or testing harder? The first "yes" gives critical, major, or
minor, and three "no" answers give a note. Each "yes" carries one sentence of
evidence. Take an architecture review that finds a decision record
silent on what happens to an untracked file. The gap is in a document, so the
document class applies. No code is built from the record yet, so it is not in
use. But a developer cannot act on it without asking the author, so the
finding is major. A checking script recomputes the severity and rejects any
mismatch.

An obvious alternative is a numeric score, as common security rating systems
use. Such scores ask for many fine judgments, and a study found that users
disagree on them. So security review uses a lookup table instead.

A major finding goes back to its author. A critical finding stops the run
until the human confirms, because the harm may already exist outside the
reviewed work. A minor finding never blocks. It becomes a row in the register,
the one table of every unfixed minor finding. A finding
rated too low escapes later review, so the human sees each new minor finding
with the reason the work still serves its purpose. Only the human
may lift the block from a finding, and the computed severity stays recorded.

Every filed finding keeps its answers, so a later reader can check them.

## Summary

The feature adds the rulebook `finding-classification.md` with one shared
severity scale and six review classes: document, code, security, architecture,
runtime, and claim. The new gate `finding-lint` recomputes each severity from
the recorded answers, so a reader can check why a finding has its severity.
Findings of severity `minor` go to the register `docs/findings/register.md`, and
a `critical` finding stops the run. The first release migrates the 39 open
findings and leaves the 208 resolved findings and an agreement-check script for
later.

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
`finding-format.md` says that Minor findings stay in the report.

The filing threshold makes the variance expensive. A finding between Major and
Minor is filed on one run and dropped on the next. The orchestrator loops on
filed findings, so the loop length depends on the run, not on the artifact.

## Core Principles

- **Kind, size, and action are separate.** The category says what kind of
  finding it is. The severity says how bad it is. The blocking rule says what
  happens. No value stands in for another.[^odc][^ieee1044][^cc]
- **The reviewer records facts, and a rule computes the severity.** A fact is a
  yes/no answer or a choice from a fixed list. Each "yes" carries one sentence
  of evidence, and a `minor` finding also carries one for its "no" to
  `fails_purpose`.
  The rule is fixed per review class. So variance can come only from the
  answers, and a reader can check each answer.
- **One shared scale for action, a class-specific basis for judgment.** Every
  class maps onto the same four severities, so blocking and counting work the
  same everywhere. Each class keeps the questions that fit its material.
- **Agents classify, scripts verify.** `finding-lint` recomputes the severity
  from the recorded basis. The
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

The four categories mean this:

- A **defect** means the artifact is wrong as it stands.
- A **risk** means the artifact is not wrong today but may fail a stated
  requirement. Only architecture review uses this category.
- A **suggestion** means the artifact works, but a change would improve it. A
  suggestion is at most `minor`.
- A **question** means the reviewer needs the author's intent before
  classifying the finding. A question goes to `docs/spec/work/todo.md` and
  carries no severity.

The review class of a finding names the rule that classifies it, not the review
that found it (DEC-17). The class follows from the reviewed material. Take
ATAM-0004: ATAM review found that ADR-0026 does not define what happens to an
untracked file in the path table. The gap is in a document, so the finding
belongs to the document class, with type `incomplete`. It carries
`source: atam-review` and `review_class: document` together. Each class section
below names the reviews that usually produce its findings.

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

A `minor` finding is recorded as one row in the register,
`docs/findings/register.md`, and never blocks (DEC-12). The register is one
table for the whole project, so a reader finds every recorded, unfixed finding
in one place. Each row holds the review report, the review class, the
category, the type, the artifact, the story, the finding, and the
`**Why this severity:**` sentence. A `note` stays in the review report only.
The register has no frontmatter, so `finding-lint` and the orchestrator loop
skip it.

### What a blocking finding does

A `critical` finding stops the playbook run, and a `major` finding loops back to
its author (DEC-14). Take BUG-0037: an empty story passes `verify-story`, and a
red suite then resets earlier merges away. The merges are lost before the bug
hunt finds the cause, and no author agent can bring them back. So the
orchestrator dispatches nothing more and merges nothing more. It tells the
human which finding stopped the run and which artifacts outside the reviewed
one may already be damaged. The run continues after the human confirms.

A `major` finding such as ATAM-0004 loops back to its author without a stop.
The loop runs until no blocking finding is open.

The split between `critical` and `major` follows inspection practice. A major
defect causes larger costs downstream. Gilb describes a further tier above it,
whose downstream effect is an order of magnitude larger.[^gilb] Of the 247
existing findings, 15 are `critical`, so the stop is rare.

### Human override

Only the human may override the computed blocking value (DEC-13). Take a
`major` finding on wave-0 handling that the human decides not to fix. The human
sets `blocking_override: false` in the finding file, with `override_by` and
`override_reason`. The finding keeps its computed severity, so the severity
stays checkable, and the loop stops waiting for it. The override only lowers a
blocking finding. A `minor` finding never blocks, and no override raises it
(DEC-25).

`finding-lint` checks that an override carries both companion fields. It
cannot check who wrote them, because an agent with a shell can write any
field. Gate receipts have the same fault, as
[gate-evidence.md](gate-evidence.md) describes. The override follows whatever
rule that proposal settles.

### In use

Some severities depend on whether the defective artifact is already in use.
An artifact is in use when something outside the current playbook run depends
on it. That holds when the artifact is merged into `dev` or `main`, installed,
or released. It also holds when an artifact that the current run did not
produce reads it. The feature branch of the run does not count. It is the run's
own workspace, and fixing a defect there is the normal review loop (DEC-16).
Every finding records the answer in the field `in_use` (DEC-21).

A document is in use only when stories or code outside the run encode its
statement. Being merged on `dev` is not enough, because a document does harm
only through what is built from it (DEC-26). Take ATAM-0004 again: ADR-0026 is
accepted and on `dev`, but no migration code is built from it yet. So the gap
is not in use, and the finding is `major`.

The reviewer checks "in use" as a fact, for example in the git state, and does
not predict which later gate might catch the defect (DEC-15). Take the
`verify-story` defect behind BUG-0037 again. Suppose a story introduced the
defect, and code review finds it after the story was merged into
`feature/core-artifact-ownership`. `dev` does not carry the defect, and only
this run uses that branch. So the finding is `major` and loops back to the
developer. The same defect in the installed copy in
`.agent-factory/factory/scripts/` is `critical` and stops the run, because a
real dispatch may already have reset merges.

### The consequence tree

Document, code, and runtime reviews share one decision tree. The reviewer
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
Each class section below defines what the three questions mean for its
material.

### Type from the fix

In the document and code classes, the reviewer picks the type from the change
that the `**Fix:**` line demands. The reviewer does not guess where the defect
came from. ODC chooses the type from the fix that was made, because a fix is
an observable event and a guess about the cause is an opinion.[^odc] A review
has no finished fix yet, so the demanded fix takes its place (DEC-09).

### Class: document

The document class covers findings in specifications, proposals, ADRs, and arc42
chapters. They come from spec review (`inspect-spec`), proposal review
(`proposal-review-agent`), spec reconciliation (`reconcile-spec`), and the
document defects of ATAM review (DEC-17).

The types follow the quality characteristics of requirements from
ISO/IEC/IEEE 29148:[^iso29148] `incorrect`, `ambiguous`, `incomplete`,
`inconsistent`, `unverifiable`, `infeasible`, `untraced`, `unnecessary`, and
`compound`. A `compound` statement bundles two requirements in one, so neither
can be checked or traced alone (DEC-11). Reconciliation adds its four existing
kinds: `code-defect`, `spec-stale`, `undocumented`, and `speculative`.

| Question           | What "yes" means for a document                                                                                                                                                                                 |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `harms_downstream` | The statement contradicts an accepted ADR, an interface contract, or an accepted specification, or it states a rule that makes the implementation wrong, and stories or code outside the run already encode it. |
| `fails_purpose`    | A planner or implementer cannot act on the statement without asking the author. Two statements in the reviewed artifact contradict each other. A requirement has no check.                                      |
| `raises_cost`      | The reader can act, but only after a second reading. Examples are an unclear sentence, a missing cross-link, or two terms for one concept.                                                                      |

The proposal review keeps its consultative pass. That pass writes only `note`
rows, because a draft is not yet expected to be complete.

### Class: code

The code class covers Fagan inspection (`fagan-review`) and implementation code
review (`code-review-agent`).

The types follow Orthogonal Defect Classification (ODC):[^odc] `function`,
`interface`, `checking`, `assignment`, `timing`, `algorithm`, `build`, and
`documentation`. Two types cover findings that ODC does not name. `structure`
covers a dependency rule, layering, or a SOLID violation with a concrete
cost. `test` covers a missing or weak test for an owned contract.

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
guidelines work this way.[^sdl][^chromium] Numeric scoring asks the reviewer
for many fine judgments, and those judgments disagree. In a study of 196 CVSS
users, no case was scored consistently. Nine months later, 68 % of the 59
participants who scored again changed their own severity.[^wunder] The least
agreement was on abstract metrics such as Scope and Attack Vector. The
authors recommend central guidance with examples for hard cases. A bug bar is
that guidance in the form of a table.

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
document, such as ATAM-0004, belongs to the
[document class](#class-document). An `arch-lint` error also enters
the review as a document defect, usually of type `inconsistent`.

A `risk` gets its severity from two facts. The first fact is the importance of
the quality scenario it threatens. ATAM rates each scenario in the utility tree
on two dimensions: its importance to the success of the system, and the
perceived risk of achieving it. Both ratings are `high`, `medium`, or `low`,
because "stakeholders cannot reliably and repeatably make finer distinctions
than High, Medium, and Low".[^atam] The factory does not keep a utility tree.
Chapter 10, § 10.2 "Quality Attribute Priority", gives each scenario a priority
of 1 or 2, set by the stakeholder. The severity maps that priority: priority 1
becomes `high`, and priority 2 becomes `medium` (DEC-10, DEC-19). The row `low`
stays in the matrix for projects that rank scenarios on three levels. If a
risk against a priority-2 scenario should block, the stakeholder raises the
scenario to priority 1. The second fact is the exposure, which is the
reviewer's own analysis:

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
DEC-16 defines (DEC-18). Take a risk against QS-9, "Read-only preflight before
installation". While the design exists only in an ADR, the risk is `major` and
loops back to the architecture author. Once an installer built from that
design is released, the same risk is `critical` and stops the run, because
installed copies may already act on the flawed design.

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

The QA strategy keeps its per-feature triage table and aligns its three actions
with the scale. `blocking` means `critical`, which stops the run.
`fix-in-same-story` means `major`, which blocks and loops back to the author.
`defer` means `minor`. The table supplies the feature-specific examples for
the three questions. The reviewer records severity, not priority, as
[Design Details](#design-details) explains.

### Class: claim

The claim class covers `adversarial-review` and keeps its defined scale. For
counting and envelopes, BLOCKER becomes `critical`, MAJOR becomes `major`,
MINOR becomes `minor`, and NOTE becomes `note`. The survival rule of
`adversarial-review` stays unchanged, because its votes decide on a claim, not
on a review pass.

### Finding file

The finding template gains seven fields and one body line. The new fields are
`review_class`, `type`, `basis`, `rating`, `blocking_override`, `override_by`,
and `override_reason`:

```markdown
---
id: FAGAN-0042
source: fagan-review
review_class: code            # document | code | security | architecture | runtime | claim
category: defect              # defect | risk | suggestion | question
type: checking                # vocabulary of the review class
severity: major               # critical | major | minor | note — computed from basis
basis:                        # shape depends on review_class
  in_use: false               # every class; checked against git
  harms_downstream: false
  fails_purpose: true
  raises_cost: true
rating: null                  # security: bug-bar level; claim: BLOCKER|MAJOR|MINOR|NOTE
blocking_override: null       # false only — set only by the human
override_by: null             # required when blocking_override is set
override_reason: null         # required when blocking_override is set
artifact: packages/factory/scripts/premerge-check:120
status: open
traces: [ST-0351]
---

# <one-line finding title>

**What is wrong:** <the defect, stated concretely>

**Why this severity:** <one sentence per "yes" answer, per precondition, or for the effect class>

**Fix:** <the concrete remediation>
```

A security finding records `basis` as `effect`, the four preconditions,
`confidence`, and `in_use`. An architecture finding records `basis` as
`importance`, `exposure`, and `in_use`.

The child-result envelope keys `finding_counts` by the shared scale:
`critical`, `major`, `minor`, and `note`. Every key is always present.

### `finding-lint`

`finding-lint` is a new deterministic gate in `packages/factory/scripts/`. It
reads every `docs/findings/*.md` that carries `review_class`. After the
migration below, only resolved findings lack the field. The lint checks these
rules:

- `review_class`, `category`, and `type` hold values from the vocabulary of
  their class.
- `basis` has the shape its class requires.
- The severity computed from `basis` equals the recorded `severity`.
- A `suggestion` is at most `minor`, and a `question` carries no severity.
- The body holds a `**Why this severity:**` line.
- A set `blocking_override` comes with a non-empty `override_by` and
  `override_reason`.
- `artifact` resolves to a line range (`path:line` or `path:start-end`) or to a
  Markdown heading (`path#anchor`).
- For a finding of the code or runtime class, `in_use` agrees with git
  (DEC-21). The lint reads the lines that `artifact` names. It compares them
  with `dev`, with `main`, with every release tag, and with the installed copy.
  In this repository, the installed copy of `packages/factory/` is
  `.agent-factory/factory/`. If the text exists unchanged in any of these
  places, `in_use` must be `true`. The lint then exits `1` with a message such
  as "artifact lines exist unchanged on dev".
- In the document, code, and runtime classes, `harms_downstream` is `true` only
  when `in_use` is `true`.
- A `minor` finding holds one sentence for its "no" answer to `fails_purpose`
  in its `**Why this severity:**` line (DEC-27).

For code and runtime findings, `in_use` is the one answer that git settles
without judgment, and it is the answer that stops the run. So the lint checks
it (DEC-21).

The git check does not apply to documents. A document is in use only through
the stories or code built from it (DEC-26), and git cannot tell whether code
encodes a statement. So the reviewer answers `in_use` for a document and names
the encoding story or code in the `**Why this severity:**` line.

The git check sets a lower bound only. When git finds no match, the reviewer
may still answer `in_use: true`, for example when another project already
reads the artifact. The `**Why this severity:**` line then names who reads it.

Take the `verify-story` defect behind BUG-0037 from [In use](#in-use), but
suppose the story did not touch the defective lines. Then `dev` carries the
same lines. A Fagan review on `feature/core-artifact-ownership` answers
`in_use: false`, because the review runs on the feature branch. The lint finds
the lines unchanged on `dev` and rejects the finding. After the correction, the
finding is `critical`, and the run stops.

The script exits `1` on any violation and names the file and the rule. The
`validate` skill and the pre-commit configuration run it.

### Migration of open findings

The 39 findings that are `open` today are migrated once (DEC-24). They are 20
`major`, 1 `high`, and 18 `minor` findings. By tag they are 25 BUG, 5 PROP,
4 RECON, 4 RETRO, and 1 SEC. The orchestrator loops on every `open` file. So
without the migration, the 18 `minor` findings would keep blocking, against
DEC-12.

An agent classifies each open finding with the new rulebook. It writes
`review_class`, `basis`, and the `**Why this severity:**` line. Then:

- A finding that comes out `minor` becomes a register row that keeps its ID,
  for example BUG-0067. The file is removed, and git history keeps its text.
- Any other finding stays a file and is checked by the lint from then on, for
  example BUG-0105.
- The user reviews all 39 results at one pause point before any file changes.

The 208 resolved findings stay as they are. They carry no future action, so
their old format costs nothing.

## Scope

**In the first release:**

- A new rulebook, `packages/factory/rulebooks/conventions/finding-classification.md`,
  holds the values of a finding, the shared scale, the consequence tree, and one
  section per review class with two or three examples per level from
  `docs/findings/`.
- `report-format.md` § Category rules and § Severity, `finding-format.md`
  § When to file, and `owasp-top-10.md` link to the new rulebook instead of
  defining severity themselves.
- The finding template and the review-report template carry the new fields.
- Each review skill and agent in the boundaries names its review class and
  links to its class section.
- The QA strategy template aligns its triage actions with the scale.
- `finding-lint` checks the rules in [`finding-lint`](#finding-lint).
  `validate` and pre-commit run it.
- The register `docs/findings/register.md` exists, and the review skills write
  each `minor` finding into it.
- The finding file carries the fields `blocking_override`, `override_by`, and
  `override_reason`.
- The pause point in `finding-format.md` and the final summary of each playbook
  with a review loop show every new `minor` finding with its `fails_purpose`
  sentence.
- The orchestrator and every playbook with a review loop apply the stop rule
  for `critical` findings.
- `docs/spec/interface-contracts.md` keys `finding_counts` by the shared scale.
- The one-time migration of the 39 open findings, as
  [Migration of open findings](#migration-of-open-findings) describes.
- An agreement check on a fixed set of existing findings, as the Completion
  Criteria describe. The set and its results live in a review report in
  `docs/reviews/`.

**Explicitly deferred (do NOT plan stories for these):**

- Migration of the 208 resolved findings (DEC-24).
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
  for 16 factor judgments, and OWASP asks for eight.[^cwss][^owasp] Factor
  judgments cause the variance this proposal removes (DEC-05, DEC-20).

## Design Details

**Evidence over labels.** A "yes" answer without a sentence of evidence fails
review, not the lint. The lint checks structure and `in_use`. The next review
pass checks whether the other evidence holds.

**Downgrades are shown to a person.** A finding classified too high blocks, so
someone looks at it. A finding classified too low becomes a register row that
no lint and no repeat pass reads again. So the pause point in
`finding-format.md` shows each `minor` finding with its "no" sentence for
`fails_purpose` (DEC-22). Take an ATAM review that records "an implementer can
pick the obvious behavior" for the gap in ADR-0026. The user reads the sentence
and can raise the finding to `major` by changing the answer. In a headless run,
the orchestrator's final summary lists the new register rows with the same
sentence. That summary comes only after the loop ends, so a headless run can
still carry a wrong downgrade into implementation.

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
| IEEE 1028                               | Nothing yet. The design does not depend on it                                                                                                 | no                     |

## Open Questions

None.

## Completion Criteria

- `finding-classification.md` exists and defines the values of a finding, the shared
  scale, the consequence tree, and the six class sections, each with at least
  two examples per severity level.
- No other rulebook, skill, or agent in the boundaries defines a severity
  level. Each one links to the new rulebook.
- `finding-lint` exits `1` on a finding whose `severity` does not match its
  `basis`, and the exit is covered by a test for each review class.
- `finding-lint` exits `1` on a finding that records `in_use: false` while the
  lines its `artifact` names exist unchanged on `dev`. A test covers a line
  range on `dev` and a line range in the installed copy.
- `finding-lint` exits `0` on `docs/findings/` after the migration. Every open
  finding carries `review_class`, and every resolved finding without it is
  skipped.
- None of the 39 migrated findings is `open` with severity `minor`. Each
  migrated `minor` finding is a row in `docs/findings/register.md` under its
  old ID.
- A review that produces a `minor` finding adds one row to
  `docs/findings/register.md` and files no finding file for it.
- `finding-lint` exits `1` on a finding with `blocking_override` set and an
  empty `override_by` or `override_reason`.
- When a review files an open `critical` finding, the orchestrator dispatches
  and merges nothing until the human confirms. It names the finding and the
  artifacts that may be damaged.
- At the pause point, the user sees every new `minor` finding with its
  `fails_purpose` sentence before any file is written.
- A child-result envelope from any review carries the four keys `critical`,
  `major`, `minor`, and `note`.
- An agreement check on a fixed set passes (DEC-23). The set holds 20 resolved
  findings from `docs/findings/`, none of them migrated, spread across the six
  review classes. Each finding keeps only its "What is wrong" and "Fix" text.
  No finding in the set is a calibration example of the rulebook or a worked
  example of this proposal. Two fresh runs classify the set with the new
  rulebook. Two more fresh runs classify it with the rules in
  `report-format.md` as they stand before this change. The check passes when
  the two new runs agree on the severity of at least 16 of the 20 findings
  (DEC-08) and agree on more findings than the two old runs do. A review report
  in `docs/reviews/` records the set and both counts.

## Guiding Rule

The reviewer states the facts, and the rule states the severity.

# Appendix

## Decisions

| ID     | Date       | Kind       | Decided by  | Decision                                                                                                                                                                                                                  | Raised by                                                          |
| ------ | ---------- | ---------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| DEC-01 | 2026-11-04 | decision   | stakeholder | Each review class gets its own classification criteria.                                                                                                                                                                   | Chat discussion                                                    |
| DEC-02 | 2026-11-04 | decision   | stakeholder | Sources are named. The design does not copy standards that are not accessible and may draw on general domain knowledge instead.                                                                                           | Chat discussion                                                    |
| DEC-03 | 2026-11-04 | decision   | stakeholder | All classes record severity on one four-level scale (`critical`, `major`, `minor`, `note`) with one blocking threshold at `major`. Native ratings stay in `rating`.                                                       | Grilling Q1                                                        |
| DEC-04 | 2026-11-04 | assumption | author      | The reviewer records a basis, a rule computes the severity, and `finding-lint` recomputes it.                                                                                                                             | Motivation                                                         |
| DEC-05 | 2026-11-04 | decision   | stakeholder | Security review does not use CVSS, SSVC, CWSS, or OWASP factor scoring. CVSS and SSVC need deployment and threat data, and factor judgments vary between runs. Superseded in its method by DEC-20.                        | Grilling Q7b                                                       |
| DEC-06 | 2026-11-04 | decision   | stakeholder | Security impact uses the maximum of the four factors. OWASP allows an estimate instead of the mean, and IEEE 1044 and CVSS v3.1 treat impact as the worst case.                                                           | Source research. Superseded by DEC-20, which has no impact factors |
| DEC-07 | 2026-11-04 | assumption | author      | `finding-lint` skips findings without `review_class`, and migration of old findings is deferred. Superseded by DEC-24.                                                                                                    | Design                                                             |
| DEC-08 | 2026-11-04 | assumption | author      | The agreement target is 80 %, that is 16 of 20 findings in the fixed set. It stays an assumption; the baseline condition in DEC-23 tests the proposal. Answers OQ-01.                                                     | Grilling Q11                                                       |
| DEC-09 | 2026-11-04 | decision   | stakeholder | In the document and code classes, the type follows from the fix that the finding demands, as ODC chooses it from the fix made.                                                                                            | Source research                                                    |
| DEC-10 | 2026-11-04 | decision   | stakeholder | Architecture severity uses the importance of the threatened scenario (source: DEC-19). Each non-risk names its assumptions.                                                                                               | Source research                                                    |
| DEC-11 | 2026-11-04 | decision   | stakeholder | The document class gains the type `compound` for a statement that bundles two requirements.                                                                                                                               | Source research                                                    |
| DEC-12 | 2026-11-04 | decision   | stakeholder | A `minor` finding becomes one row in the project register `docs/findings/register.md` and never blocks. Answers OQ-03.                                                                                                    | T-0016 grilling                                                    |
| DEC-13 | 2026-11-04 | decision   | stakeholder | Only the human overrides the computed blocking value, through `blocking_override`, `override_by`, and `override_reason`. The severity stays computed.                                                                     | T-0016 grilling                                                    |
| DEC-14 | 2026-11-04 | decision   | stakeholder | A `critical` finding stops the playbook run until the human confirms. A `major` finding loops back to its author.                                                                                                         | Grilling Q2                                                        |
| DEC-15 | 2026-11-04 | decision   | stakeholder | `harms_downstream` asks whether the defective artifact is already in use (see DEC-16). The reviewer checks this fact and does not predict later gates.                                                                    | Grilling Q3                                                        |
| DEC-16 | 2026-11-04 | decision   | stakeholder | An artifact is in use when something outside the current run depends on it: `dev`, `main`, the installed copy, a release, or an artifact the run did not produce. The feature branch of the run does not count.           | Grilling Q3b                                                       |
| DEC-17 | 2026-11-04 | decision   | stakeholder | `review_class` names the rule, not the review. A defect that ATAM review finds in an ADR or arc42 chapter belongs to the document class. The architecture class covers only findings measured against a quality scenario. | Grilling Q4                                                        |
| DEC-18 | 2026-11-04 | decision   | stakeholder | The architecture matrix gives at most `major`. A risk becomes `critical` only when something built from the decision is in use (DEC-16).                                                                                  | Grilling Q5                                                        |
| DEC-19 | 2026-11-04 | decision   | stakeholder | Scenario importance comes from the priority in arc42 § 10.2: priority 1 is `high`, priority 2 is `medium`. A utility tree with H/M/L ratings is deferred.                                                                 | Grilling Q6                                                        |
| DEC-20 | 2026-11-04 | decision   | stakeholder | Security severity comes from a bug bar: the effect class sets the level, each of four preconditions lowers it one step, and `critical` needs `in_use` and `proven` confidence.                                            | Grilling Q7b                                                       |
| DEC-21 | 2026-11-04 | decision   | stakeholder | `finding-lint` checks `in_use` against `dev`, `main`, release tags, and the installed copy. Every class records `in_use`, and `artifact` must resolve to a line range or a heading.                                       | Grilling Q9                                                        |
| DEC-22 | 2026-11-04 | decision   | stakeholder | The pause point shows each new `minor` finding with its `fails_purpose` sentence, so the user can raise a wrong downgrade. A headless run lists the rows in its final summary.                                            | Grilling Q10                                                       |
| DEC-23 | 2026-11-04 | decision   | stakeholder | Agreement is measured by re-classifying a fixed set of 20 existing findings, twice with the new rulebook and twice with the old rules. The new rules must reach the target and beat the old ones.                         | Grilling Q11                                                       |
| DEC-24 | 2026-11-04 | decision   | stakeholder | The 39 open findings are migrated once with the new rulebook; migrated `minor` findings become register rows under their old ID. The 208 resolved findings stay untouched. Answers OQ-02.                                 | Grilling Q12                                                       |
| DEC-25 | 2026-11-04 | decision   | stakeholder | The override only sets a blocking finding to `false`. A `minor` finding never blocks, and no override raises it.                                                                                                          | review-loop-cap lector pass                                        |
| DEC-26 | 2026-11-04 | decision   | stakeholder | A document is in use only when stories or code outside the run encode its statement. The git check for `in_use` applies to code and runtime findings only.                                                                | Lector pass C2                                                     |
| DEC-27 | 2026-11-04 | decision   | stakeholder | A `minor` finding carries one sentence for its "no" to `fails_purpose`, and `finding-lint` checks that the sentence exists.                                                                                               | Lector pass C4                                                     |

## Review findings

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |

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

[^cvss4]: FIRST, *CVSS v4.0 Specification Document*, Table 22 (qualitative severity rating scale), <https://www.first.org/cvss/v4.0/specification-document>.

[^ssvc]: CERT/CC, *SSVC: Stakeholder-Specific Vulnerability Categorization*, supplier decision tree, <https://certcc.github.io/SSVC/howto/supplier_tree/>.

[^owasp]: OWASP, *OWASP Risk Rating Methodology*, Steps 2, 4, and 6, <https://community.owasp.org/OWASP_Risk_Rating_Methodology>.

[^jpl]: John C. Kelly, Joseph S. Sherif, Jonathan Hops, "An Analysis of Defect Densities Found During Software Inspections", *Proceedings of the 15th Annual Software Engineering Workshop*, NASA Goddard Space Flight Center, 1990, <https://ntrs.nasa.gov/api/citations/19920010193/downloads/19920010193.pdf>.

[^cvss31]: FIRST, *CVSS v3.1 Specification Document*, § 7.1 Base Metrics Equations, <https://www.first.org/cvss/v3.1/specification-document>.

[^seicvss]: Software Engineering Institute, Carnegie Mellon University, *Towards Improving CVSS*, <https://www.sei.cmu.edu/library/towards-improving-cvss/>.
