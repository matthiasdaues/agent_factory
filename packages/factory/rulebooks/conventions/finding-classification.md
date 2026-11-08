---
title: Finding Classification
category: review
enforcement: finding-lint recomputes the severity from the basis of each finding file and register file; dispatch and premerge-check hold the stop of a critical finding
version: 1.0.0
---

# Finding Classification

A reviewer records facts about a finding, and a fixed rule computes its
severity. So two reviewers who record the same facts give the same finding the
same severity. This rulebook holds the scale, the blocking rule, and one rule
per review class, each with calibration examples. No other rulebook defines a
severity level. Read the class section of your review before the first
classification of a session.

## The values of a finding

| Value    | Question it answers           | Values                                     | Set by                                                                 |
| -------- | ----------------------------- | ------------------------------------------ | ---------------------------------------------------------------------- |
| Category | What kind of finding is it?   | `defect`, `risk`, `suggestion`, `question` | Reviewer                                                               |
| Type     | Which part of the work fails? | The vocabulary of the class                | Reviewer                                                               |
| Severity | How bad is it?                | `critical`, `major`, `minor`, `note`       | Computed from the basis                                                |
| Blocking | Does it stop the review?      | `true` or `false`                          | Computed from category and severity; only the stakeholder overrides it |

The basis is the set of answers that the reviewer records. The rule of the
review class computes the severity from it, so the shape of the basis depends
on the class. The reviewer records every field of the basis, also after the
first "yes".

The four categories mean this:

- A **defect** means the artifact is wrong as it stands.
- A **risk** means the artifact is not wrong today but may fail a stated
  requirement. Only the architecture class uses this category.
- A **suggestion** means the artifact works, but a change would improve it.
  A `suggestion` of the document, code, or runtime class describes material
  that works, so it answers "no" to `harms_downstream` and `fails_purpose`
  and is `minor` or `note`. A `suggestion` of the security or architecture
  class is at most `minor`: when the rule of its class gives `critical` or
  `major`, the severity is `minor`.
- A **question** means the reviewer needs the author's intent before
  classifying the finding. A `question` becomes an entry in
  `docs/spec/work/todo.md` only, as [todo-format.md](todo-format.md)
  describes. It gets no finding file and no register file, and it carries no
  severity.

## Review classes

The review class names the rule that classifies a finding, not the review that
found it. The reviewed material decides the class, for a review and for any
other source, such as a diagnosis, a bug report, or a dispatch run.

| Class        | Material                                                     | Reviews that usually produce it                                                                    | Rule                                                                                                | Basis fields                                                 |
| ------------ | ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| document     | Specifications, proposals, ADRs, and arc42 chapters          | `inspect-spec`, `proposal-review-agent`, `reconcile-spec`, and the document defects of ATAM review | [Consequence tree](#the-consequence-tree); [proposal rows](#proposal-review-rows) use two questions | `in_use`, `harms_downstream`, `fails_purpose`, `raises_cost` |
| code         | Code, and the text that agents execute                       | `fagan-review` and `code-review-agent`                                                             | [Consequence tree](#the-consequence-tree)                                                           | `in_use`, `harms_downstream`, `fails_purpose`, `raises_cost` |
| security     | Code and configuration lines                                 | `security-review` and the security step of `qa-agent`                                              | [Bug bar](#class-security)                                                                          | `effect`, the four preconditions, `confidence`, `in_use`     |
| architecture | Architectural decisions, measured against a quality scenario | `atam-review`                                                                                      | [Matrix of importance and exposure](#class-architecture), raised by `in_use`                        | `importance`, `exposure`, `in_use`                           |
| runtime      | Observed behavior                                            | `bug-hunt` and the exploratory testing of `qa-agent`                                               | [Consequence tree](#the-consequence-tree)                                                           | `in_use`, `harms_downstream`, `fails_purpose`, `raises_cost` |

Text that agents execute is code: playbooks, skills, agent definitions,
rulebooks, and hook configuration. Take a diagnosis that finds a playbook step
telling the orchestrator to merge before the premerge check. The playbook runs
in every session from the installed copy, so the finding belongs to the code
class and is `critical`.

ATAM review can also find a defect in a document.
[ATAM-0004](../../../../docs/findings/ATAM-0004.md) says that
[ADR-0026](../../../../docs/adr/0026-layout-migration-runs-inside-the-factory-update.md) does not define what happens to an untracked file. The gap is in a
document, so the finding belongs to the document class, with type
`incomplete`. It carries `source: atam-review` and `review_class: document`
together.

An observation that names no artifact is not a finding. It becomes an action
item of its retrospective or an entry in `docs/spec/work/todo.md`.

## Shared severity scale and blocking rule

| Severity   | Meaning in one sentence                                                                       | Recorded as        | Blocks        |
| ---------- | --------------------------------------------------------------------------------------------- | ------------------ | ------------- |
| `critical` | The defective artifact is already [in use](#in-use), so the harm may already exist elsewhere. | finding file       | stops the run |
| `major`    | The reviewed artifact fails its own purpose.                                                  | finding file       | yes           |
| `minor`    | The artifact works, but the finding raises the cost of later work.                            | register file      | no            |
| `note`     | Preference, context, or information. Nothing needs to change.                                 | review report only | no            |

A finding is blocking when its category is `defect` or `risk` and its severity
is `critical` or `major`. One threshold applies to every class. A blocking
finding becomes a finding file `docs/findings/<ID>.md`, as
[finding-format.md](finding-format.md) describes. A `minor` finding becomes
one register file `docs/findings/register/<class>/<ID>.json` and never blocks.
A `note` stays in the review report. Every finding takes its ID from
`next-id`, as a finding file and as a register file.

A class-native rating, such as the bug-bar level of a security finding, stays
in the `rating` field. Only the four severities above enter the `severity`
field.

A `critical` finding stops the playbook run, and a `major` finding loops back
to its author. The loop runs until no blocking finding is open.

## In use

Some severities depend on whether the defective artifact is already in use.
An artifact is in use when something outside the current playbook run depends
on it. That holds when the artifact is merged into `dev` or `main`, installed,
or released. It also holds when an artifact that the current run did not
produce reads it. The feature branch of the run does not count, because it is
the run's own workspace. Every finding records the answer in the field
`in_use`.

A document is in use only when stories or code outside the run encode its
statement. Being merged on `dev` is not enough, because a document does harm
only through what is built from it. When ATAM review filed [ATAM-0004](../../../../docs/findings/ATAM-0004.md), ADR-0026
was accepted and on `dev`, but no migration code was built from it yet. So the
gap was not in use.

The reviewer checks "in use" as a fact, for example in the git state. The
reviewer does not predict which later gate might catch the defect. For a code,
runtime, or security finding, `finding-lint` checks the answer against git:
when every line of the artifact range exists unchanged on `dev`, `main`, their
remote branches, a release tag, or the installed copy, `in_use` must be true.

## The consequence tree

The document, code, and runtime classes share one decision tree. The reviewer
answers three questions in order. The severity is the level of the first
"yes". Three "no" answers give `note`. Each question asks what happens if the
finding is left uncorrected.

1. **`harms_downstream`**: Does the finding cause a wrong result, data loss, a
   security breach, or a broken contract, and is the defective artifact
   already [in use](#in-use)? A "yes" gives `critical`. Before the artifact is
   in use, for example on the feature branch of the run, the same consequence
   answers "yes" to `fails_purpose`.
2. **`fails_purpose`**: Does the reviewed artifact fail the job it exists for?
   A "yes" gives `major`.
3. **`raises_cost`**: Does the artifact work, but the finding makes later
   reading, change, or testing measurably harder? A "yes" gives `minor`.

A reviewer who answers "yes" to `harms_downstream` still records the other two
answers, so a reader sees the complete reasoning. Each "yes" carries one
sentence of evidence in the `**Why this severity:**` line that names the
concrete consequence. A `minor` finding also gives the reason for its "no" to
`fails_purpose`, marked with the text `no to fails_purpose`, because the pause
point shows that sentence to the stakeholder. Each class section below defines
what the three questions mean for its material.

## Type from the fix

In the document and code classes, the reviewer picks the type from the change
that the `**Fix:**` line demands. The reviewer does not guess where the defect
came from. A fix is an observable change, and a guess about the cause is an
opinion.

## Class: document

The document class covers findings in specifications, proposals, ADRs, and
arc42 chapters: the text that people and agents read but do not execute.

The types are `incorrect`, `ambiguous`, `incomplete`, `inconsistent`,
`unverifiable`, `infeasible`, `untraced`, `unnecessary`, and `compound`. A
`compound` statement bundles two requirements in one, so neither can be
checked or traced alone. Reconciliation adds its four kinds: `code-defect`,
`spec-stale`, `undocumented`, and `speculative`.

| Question           | What "yes" means for a document                                                                                                                                                                                 |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `harms_downstream` | The statement contradicts an accepted ADR, an interface contract, or an accepted specification, or it states a rule that makes the implementation wrong, and stories or code outside the run already encode it. |
| `fails_purpose`    | A planner or implementer cannot act on the statement without asking the author. Two statements in the reviewed artifact contradict each other. A requirement has no check.                                      |
| `raises_cost`      | The reader can act, but only after a second reading. Examples are an unclear sentence, a missing cross-link, or two terms for one concept.                                                                      |

`finding-lint` does not check `in_use` of a document against git. So the
`**Why this severity:**` line names the story or code that encodes the
statement, or says that none does.

### Proposal review rows

Proposal review records its findings as rows in the proposal's Appendix, and
the rows stay there. Their `PROP-NN` numbers count within the proposal. A
proposal under review has no stories built from it, so it is never in use, and
a row is never `critical`.

The purpose of a proposal is that a planning agent cuts stories from it
without asking back. So the reviewer asks two questions for each row, in
order:

1. **`fails_purpose`**: Would a planning agent have to ask the author, or cut
   a wrong story? A "yes" gives `major`.
2. **`raises_cost`**: Can the planner act, while a reader pays later through a
   second reading, a wrong number, or a source that does not hold? A "yes"
   gives `minor`.

Two "no" answers give `note`. The Finding cell ends with one sentence that
starts with `Severity:` and names the deciding answer, for example "Severity:
the planner can act, because the migration counts its own files, but the wrong
number misleads a reader." An open `major` row blocks the transition to
`accepted`. `minor` and `note` rows stay in the table and enter no register.
The consultative pass on a draft writes only `note` rows. `finding-lint` does
not read proposals.

### Calibration examples

| Severity   | Finding                                                                   | Basis                                                                                    | Why this severity                                                                                                                                                                                                                                                  |
| ---------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `critical` | Invented: the claim contract hands out one number twice                   | `in_use: true`, `harms_downstream: true`, `fails_purpose: true`, `raises_cost: false`    | `packages/factory/scripts/next-id` on `dev` implements the statement, so code outside the run already encodes it. Suppose `docs/spec/interface-contracts.md` § next-id let two claims of one prefix return the same number. Two clones then hand out one ID twice. |
| `major`    | [SPEC-0071](../../../../docs/findings/SPEC-0071.md)                       | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: true`   | The stop contract and the Finding Lifecycle contradict each other, so the implementer of the stop cannot tell which one to build without asking. No story encodes the specification yet.                                                                           |
| `major`    | [RECON-0030](../../../../docs/findings/RECON-0030.md)                     | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: true`   | A Rule of the acceptance specification still puts the counter back, which the counter-ids-fitting proposal forbids. An agent that checks the code against it reads a correct refusal as a code defect.                                                             |
| `major`    | [SPEC-0059](../../../../docs/findings/SPEC-0059.md)                       | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: true`   | Two Scenarios of the specification contradict each other, so the implementer cannot satisfy both without asking which Rule wins.                                                                                                                                   |
| `minor`    | [SPEC-0061](../../../../docs/findings/register/document/SPEC-0061.json)   | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true`  | Every missing case of the move can end with the Failure row, so an implementer can act (no to fails_purpose). The implementer and the test writer must still invent four messages.                                                                                 |
| `minor`    | [RECON-0027](../../../../docs/findings/register/document/RECON-0027.json) | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true`  | Each git call still stops at 30 seconds, so a claim ends with a named cause (no to fails_purpose). A reader who plans a timeout from the stated bound gets a third of the real worst case.                                                                         |
| `minor`    | [SPEC-0065](../../../../docs/findings/register/document/SPEC-0065.json)   | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true`  | An implementer can follow the Failure row and send messages to standard error (no to fails_purpose). The tests must still guess where to read the warning.                                                                                                         |
| `note`     | Invented: a list that could be a table                                    | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | A reviewer prefers a table to a list of five terms in `docs/arc42/12_glossary.md`. A reader acts on the list at the first reading, so the finding is a `suggestion` and nothing needs to change.                                                                   |

## Class: code

The code class covers Fagan inspection (`fagan-review`) and implementation
code review (`code-review-agent`). Its material includes the text that agents
execute, as [Review classes](#review-classes) describes.

The types follow Orthogonal Defect Classification (ODC): `function`,
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
`suggestion:`, `question:`, or `nitpick:`. The label maps onto the category,
and `nitpick` always gives `note`. The label helps the author read the review.
The category and the basis decide the classification.

### Calibration examples

The `critical` row uses the case of [BUG-0037](../../../../docs/findings/BUG-0037.md): an empty story passes
`verify-story`, and a red suite then resets earlier merges away. Suppose a
story introduced that defect, and code review finds it.

| Severity   | Finding                                                               | Basis                                                                                   | Why this severity                                                                                                                                                                                                                                             |
| ---------- | --------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `critical` | Invented: the BUG-0037 case in the installed copy                     | `in_use: true`, `harms_downstream: true`, `fails_purpose: true`, `raises_cost: false`   | The lines of `packages/factory/scripts/dispatch` exist unchanged in the installed copy, so a real dispatch may already have reset merges. On `feature/core-artifact-ownership` only, the same lines give `in_use: false`, `fails_purpose: true`, and `major`. |
| `major`    | [FAGAN-0033](../../../../docs/findings/FAGAN-0033.md)                 | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: false` | Step 4 of an agent definition exists to start the one counter of a project, and on this path it starts a second one. The text exists only on the feature branch.                                                                                              |
| `major`    | [IMPL-0005](../../../../docs/findings/IMPL-0005.md)                   | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: true`  | A rule in `rules.md` tells agents to number `PROP` rows with a script that refuses them, so the rulebook fails its job. A rulebook is code, because agents execute it.                                                                                        |
| `major`    | [IMPL-0004](../../../../docs/findings/IMPL-0004.md)                   | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: false` | A claim fails for a user whose SSH key comes from the global git config, a credential source that the contract names. Nothing on `dev` calls the code yet.                                                                                                    |
| `minor`    | [FAGAN-0032](../../../../docs/findings/register/code/FAGAN-0032.json) | `in_use: true`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true`  | The wrong commit lands in the ledger only when a ref is named like a hex prefix, which the repository's naming does not produce (no to fails_purpose). The operator must then find and correct a recorded SHA.                                                |
| `minor`    | [IMPL-0007](../../../../docs/findings/register/code/IMPL-0007.json)   | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true` | Each producer file names its own prefix, so an agent still claims those IDs (no to fails_purpose). A reader who follows the link sees an incomplete list and must search for the rest.                                                                        |
| `minor`    | [BUG-0117](../../../../docs/findings/register/code/BUG-0117.json)     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true` | Every required behavior holds and the tests drive the claim loop (no to fails_purpose). A second counter backend must fit a port shape that the architecture does not describe.                                                                               |
| `note`     | Invented: a nitpick on a variable name                                | `in_use: true`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | A reviewer writes `nitpick:` on a local variable in `packages/factory/scripts/next-id` that could be shorter. The label `nitpick` gives `note`, so the finding stays in the report.                                                                           |

## Class: security

The security class covers `security-review` and the security step of the
`qa-agent`. The type is the OWASP Top 10 category from `A01` to `A10`, as
[owasp-top-10.md](../principles/owasp-top-10.md) lists them. A CWE identifier
goes into the `**What is wrong:**` line when one fits.

The class uses a bug bar, not a score. A bug bar is a lookup table: the effect
of an attack sets a starting level, and each precondition of the attack lowers
it by one step. Numeric scores ask the reviewer for many fine judgments, and
those judgments disagree between reviewers.

**Step 1: effect.** The reviewer picks the effect class that describes what
the attacker gains. The effect sets the starting level.

| Effect class  | What the attacker gains                                                                                                              | Starting level |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------ | -------------- |
| `execution`   | Runs code or writes arbitrary files with the privileges of the developer or the CI job.                                              | Critical       |
| `secrets`     | Reads credentials, tokens, keys, or all project data.                                                                                | Critical       |
| `gate-bypass` | Lands a change that a factory gate should stop, such as the git guard hook, `premerge-check`, `step-guard`, or a consent gate.       | High           |
| `tampering`   | Changes project artifacts persistently in the default setup, such as specifications, backlog stories, findings, or git history.      | High           |
| `disclosure`  | Reads chosen data from a known location, such as personal data or a private file.                                                    | High           |
| `limited`     | Reads or changes data only in a specific, non-default setup, or causes a denial of service that needs a reinstall or manual repair.  | Medium         |
| `leak`        | Learns untargeted information, such as paths or versions, or causes a denial of service that a rerun fixes.                          | Low            |
| `hardening`   | Gains nothing today. The finding names a missing defense in depth. It is a `suggestion` of severity `note`, and `rating` stays null. | none           |

**Step 2: preconditions.** The reviewer answers four yes/no questions. Each
"yes" lowers the level by one step. The level never falls below Low.

| Precondition     | "Yes" when the attack needs …                                                                       |
| ---------------- | --------------------------------------------------------------------------------------------------- |
| `second_breach`  | another compromise first: a malicious upstream release, a stolen account, or a second flaw.         |
| `trusted_access` | a local shell, write access to the repository, or an account in the project.                        |
| `non_default`    | a configuration or an opt-in feature that the factory does not enable by default.                   |
| `user_action`    | the user to do something unusual, such as run a command the attacker supplied or confirm a warning. |

An attack that needs the capability it gains is not a finding, because the
attacker gains nothing. Take an attacker with write access to the repository
who edits `block-dangerous-git.sh` to let a merge through. Write access
already lets that attacker land the change, so the reviewer records nothing.

**Step 3: confidence.** The reviewer records `proven` when the attack path is
reproduced or traced from the input to the sink in the code. Otherwise the
reviewer records `plausible`. A weakness that nobody has shown to be reachable
must not count like one that someone has.

**Step 4: mapping.** The level maps onto the shared scale:

- **Critical** becomes `critical` only when the vulnerable code is
  [in use](#in-use) and the confidence is `proven`. Otherwise Critical becomes
  `major`.
- **High** and **Medium** become `major`.
- **Low** becomes `minor`.

The finding keeps the level in its `rating` field as `Critical`, `High`,
`Medium`, or `Low`, so the report still shows High and Medium apart.

### Calibration examples

| Severity   | Finding                                                | Basis                                                                                                                                                 | Why this severity                                                                                                                                                                                                                                                                                                                       |
| ---------- | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `critical` | Invented: a capture hook runs text from the transcript | `effect: execution`, all four preconditions `false`, `confidence: proven`, `in_use: true`                                                             | The default install runs `packages/factory/config/hooks/capture-usage.sh`, so the code is in use. Suppose the hook passed a field of the session transcript to `eval`. A web page that the agent reads during normal work puts a command into the transcript, and the hook runs it with the developer's privileges. The path is traced. |
| `major`    | [SEC-0003](../../../../docs/findings/SEC-0003.md)      | `effect: execution`, `second_breach: true`, `trusted_access: false`, `non_default: false`, `user_action: false`, `confidence: proven`, `in_use: true` | A malicious `tiktoken` release would run in every lifecycle hook with the developer's privileges, so the bar starts at Critical. The attacker must first publish that release, so `second_breach` lowers it to High, and High gives `major`.                                                                                            |
| `major`    | [SEC-0007](../../../../docs/findings/SEC-0007.md)      | `effect: secrets`, `second_breach: true`, `trusted_access: false`, `non_default: true`, `user_action: false`, `confidence: proven`, `in_use: false`   | A printed remote URL reveals a token, so the bar starts at Critical. The attacker must first read the log where the message lands (`second_breach`), and a token inside the URL is not the default setup (`non_default`). Medium gives `major`.                                                                                         |
| `minor`    | Invented: an error message prints an absolute path     | `effect: leak`, all four preconditions `false`, `confidence: proven`, `in_use: true`                                                                  | Suppose `packages/factory/scripts/next-id` printed the absolute path of the main checkout into a CI log. A reader of the log learns a path and nothing else, so the bar starts at Low, and Low gives `minor`.                                                                                                                           |
| `note`     | Invented: no size limit on a schema input              | `effect: hardening`, all four preconditions `false`, `confidence: plausible`, `in_use: true`                                                          | `packages/factory/scripts/schema-validate` reads a file of any size. No attack gains anything from that today, so the finding is a `suggestion` of severity `note`, with `rating` null.                                                                                                                                                 |

## Class: architecture

The architecture class covers what only ATAM review produces: findings
measured against a quality scenario. The types are the kinds of decisions that
ATAM sorts: `risk`, `non-risk`, `sensitivity-point`, and `tradeoff-point`. A
defect that ATAM review finds in an architecture document belongs to the
[document class](#class-document). An `arch-lint` error also enters the review
as a document defect, usually of type `inconsistent`.

A `risk` gets its severity from two facts. The first fact is the importance of
the quality scenario that it threatens. Chapter 10 of arc42, § 10.2 "Quality
Attribute Priority", gives each scenario a priority of 1 or 2. Priority 1
becomes importance `high`, and priority 2 becomes `medium`. The row `low`
serves projects that rank scenarios on three levels. If a risk against a
priority-2 scenario should block, the stakeholder raises the scenario to
priority 1.

The second fact is the exposure, which is the reviewer's own analysis:

- `fails` means the analysis shows that the decision cannot meet the
  scenario's response measure.
- `uncertain` means no evidence exists either way, or the result depends on an
  assumption that nobody has checked.

| Scenario importance \\ Exposure | `fails` | `uncertain` |
| ------------------------------- | ------- | ----------- |
| `high`                          | `major` | `major`     |
| `medium`                        | `major` | `minor`     |
| `low`                           | `minor` | `note`      |

The matrix gives at most `major`. A third fact, `in_use`, raises a `major`
risk to `critical` and changes no other level. It holds when something built
from the decision is in use, as [In use](#in-use) defines.

Non-risks, sensitivity points, and tradeoff points are recorded in the report
with severity `note`. They support the analysis and do not demand a change. A
non-risk is a good decision that rests on assumptions, so each non-risk names
its assumptions. If an assumption changes, the non-risk is judged again.

### Calibration examples

| Severity   | Finding                                                                     | Basis                                                        | Why this severity                                                                                                                                                                                                                                                                                                    |
| ---------- | --------------------------------------------------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `critical` | Invented: a released installer skips its preflight                          | `importance: high`, `exposure: fails`, `in_use: true`        | A release ships `packages/factory/scripts/install-agent-factory`, so installed copies may already act on the flawed design. QS-9 in `docs/arc42/10_quality_requirements.md`, "Read-only preflight before installation", has priority 1. Suppose the analysis shows that the script writes before its preflight ends. |
| `major`    | [ATAM-0018](../../../../docs/findings/ATAM-0018.md)                         | `importance: high`, `exposure: uncertain`, `in_use: false`   | QS-25 has priority 1. Whether two CLIs pass the patch text in a form that the guard can parse is an assumption nobody has checked. No code is built from [ADR-0035](../../../../docs/adr/0035-guard-human-fields-in-every-cli.md) yet.                                                                               |
| `major`    | [ATAM-0019](../../../../docs/findings/ATAM-0019.md)                         | `importance: high`, `exposure: uncertain`, `in_use: false`   | QS-24 has priority 1, and its response depends on `finding-lint` at every commit. The consent class and the update path of that hook are not designed yet.                                                                                                                                                           |
| `major`    | [ATAM-0014](../../../../docs/findings/ATAM-0014.md)                         | `importance: high`, `exposure: uncertain`, `in_use: false`   | QS-22 has priority 1. The analysis shows the path to a double ID, but how often a move dies between two git calls is unchecked.                                                                                                                                                                                      |
| `minor`    | [ATAM-0015](../../../../docs/findings/register/architecture/ATAM-0015.json) | `importance: medium`, `exposure: uncertain`, `in_use: false` | The nearest scenario, QS-20, has priority 2. Whether the agent shell hangs on a credential prompt depends on a setup that nobody has checked.                                                                                                                                                                        |
| `minor`    | [ATAM-0016](../../../../docs/findings/register/architecture/ATAM-0016.json) | `importance: medium`, `exposure: uncertain`, `in_use: false` | QS-23 has priority 2. Every ordering checked fails loudly and hands out no ID twice; only a message and a fitting key may mislead.                                                                                                                                                                                   |
| `minor`    | [ATAM-0017](../../../../docs/findings/register/architecture/ATAM-0017.json) | `importance: medium`, `exposure: uncertain`, `in_use: false` | The outcome is a false collision under QS-23, which has priority 2. Whether other clones claim inside the window is unknown.                                                                                                                                                                                         |
| `note`     | Invented: a non-risk of the register design                                 | type `non-risk`, no importance or exposure                   | `docs/adr/0034-one-register-file-per-minor-finding.md` gives each `minor` finding its own file, so two branches merge without a conflict. The non-risk names its assumption: no two branches edit the same register file.                                                                                            |

## Class: runtime

The runtime class covers `bug-hunt` and the exploratory testing of the
`qa-agent`. The types name the observed effect: `crash`, `hang`,
`wrong-result`, `data-loss`, `security`, `performance`, `usability`, and
`cosmetic`.

| Question           | What "yes" means for observed behavior                                                                                                                               |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `harms_downstream` | Data is lost or corrupted, a security boundary breaks, the system crashes or hangs, or the primary actor-goal path fails with no workaround, and the code is in use. |
| `fails_purpose`    | The primary actor-goal path fails but has a workaround, or any path returns a wrong result.                                                                          |
| `raises_cost`      | A secondary path degrades and has a workaround, a message misleads, or an observability gap hides a failure from the operator.                                       |

The QA strategy of a feature keeps a triage table. The table states the
consequence, not the severity: its `Consequence` column holds "harm if in
use", "fails purpose", or "raises cost". The tree and `in_use` compute the
severity. Severity measures consequence. Priority decides the order of work
and stays with the dispatcher and the stakeholder.

### Calibration examples

The bug hunt of [2026-10-15](../../../../docs/reviews/bug-hunt-2026-10-15.md)
ran on `dev`, so every real example below has `in_use: true`.

| Severity   | Finding                                           | Basis                                                                                   | Why this severity                                                                                                                                                                                  |
| ---------- | ------------------------------------------------- | --------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `critical` | [BUG-0035](../../../../docs/findings/BUG-0035.md) | `in_use: true`, `harms_downstream: true`, `fails_purpose: true`, `raises_cost: false`   | The code is on `dev`, and every capture fails with `No such file or directory`, so no usage record is written. The primary path fails with no workaround, and the records are lost.                |
| `critical` | [BUG-0073](../../../../docs/findings/BUG-0073.md) | `in_use: true`, `harms_downstream: true`, `fails_purpose: true`, `raises_cost: false`   | The code is on `dev`. A failed run of `build-release` deleted an existing output directory and its `important.txt`, which is data loss.                                                            |
| `major`    | [BUG-0054](../../../../docs/findings/BUG-0054.md) | `in_use: true`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: false`  | `arch-lint` and three similar gates exit 0 on a directory that does not exist. The gate returns a wrong result; nothing crashes and no data is lost.                                               |
| `major`    | [BUG-0063](../../../../docs/findings/BUG-0063.md) | `in_use: true`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: false`  | `test-design-verify` reports a valid block list as `empty_tests_field`. The result is wrong, and an author can write the list inline as a workaround.                                              |
| `minor`    | [BUG-0058](../../../../docs/findings/BUG-0058.md) | `in_use: true`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true`  | An empty or missing handoff still fails with a non-zero exit, so the gate does its job (no to fails_purpose). A caller that tells findings from usage errors by the exit code reads the wrong one. |
| `minor`    | [BUG-0081](../../../../docs/findings/BUG-0081.md) | `in_use: true`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true`  | The first merge of the hooks works (no to fails_purpose). A rerun, a secondary path, adds duplicate hooks that the user must delete by hand.                                                       |
| `note`     | Invented: an extra blank line in a summary        | `in_use: true`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | `packages/factory/scripts/housekeeping-about` prints two blank lines before its summary. The type is `cosmetic`, and nobody reads or acts differently because of it.                               |

## Claim review stays outside

Claim review is not a review class. `adversarial-review` decides whether a
research claim survives, not how bad a defect in an artifact is. So
`adversarial-review` keeps its own scale of BLOCKER, MAJOR, MINOR, and NOTE in
its records.

Only its envelope follows the shared scale, because every child-result
envelope carries the four keys, as
[report-format.md § Child-result envelope](report-format.md#child-result-envelope)
shows. A BLOCKER counts under `major`, because it blocks the claim as a
`major` finding blocks a review. MAJOR, MINOR, and NOTE count under their
namesakes. Claim review counts nothing under `critical`, because no claim
review finds harm that already exists elsewhere.

## Waiver and confirmation

Only the stakeholder overrides the computed blocking value. Take a `major`
finding on wave-0 handling that the stakeholder decides not to fix. The
stakeholder sets `status: waived` in the finding file, with text in
`override_by` and `override_reason`. Every review loop lists only
`status: open`, so the waived finding drops out of the loop. The finding keeps
its computed severity, so its severity stays checkable against its basis.

The stakeholder sets a blocking finding aside with `waived`, never with
`deferred` and never by a lowering to a `note`. Only the one-time migration
sets `deferred`, on a finding file without `review_class`.

No override raises a `minor` finding. A `minor` finding never blocks. To make
it block, an agent or the stakeholder changes an answer of its basis, removes
its register file, and files a finding file under the same ID.

Nobody fixes some `minor` findings, such as an unclear sentence in a document
that a later feature replaces. The stakeholder sets such a register file to
`waived`, with text in `override_by` and `override_reason`, and the register
file stays as the record.

A `critical` finding stops the run until the stakeholder confirms the stop.
The stakeholder runs the checks of its `## Possible damage` section and then
writes `stop_confirmed_by` and `stop_confirmed_reason` into the finding file.
A `critical` finding is waived or resolved only after the stakeholder has
confirmed its stop, so the damage is checked even when the finding stays
unfixed. A confirmed finding keeps severity `critical` and loops back to its
author like a `major` one.

Agents never write these fields. The hook `guard-human-fields` refuses an
agent's call that sets a non-null `override_by`, `override_reason`,
`stop_confirmed_by`, or `stop_confirmed_reason`, or the status `waived`.

## Referenced from

- [report-format.md § Category rules](report-format.md#category-rules)
- [report-format.md § Severity](report-format.md#severity)
- [finding-format.md § When to file](finding-format.md#when-to-file)
- [owasp-top-10.md § Application in security review](../principles/owasp-top-10.md#application-in-security-review)
- [rules.md § Findings](../rules.md#findings)
