---
type: classification-test
title: Blind test of the finding classification on gigacron findings
date: 2026-11-18
status: defects
reviewer: main session with ten rater subagents
findings_filed: 0
scope: The finding classification rulebook at dev 2bda28cfe9ede93e443c4d9905c82e7758fd8b8c, applied blind to 38 findings of the gigacron repository
---

# Blind test of the finding classification on gigacron findings

Two raters who read the same finding with the
[finding classification](../../packages/factory/rulebooks/conventions/finding-classification.md)
gave it the same severity in all 53 valid pairs. Across pairs, one finding
split: a wrong result in code that only unusual API input reaches came out
`minor` from one pair and `major` from the other. Review class and basis
agreed less often than severity. Two rule changes decided the cases where
raters split, and they survived a second test. They are listed in
[Recommendations](#recommendations). Five other candidates failed and are removed. One of them, a default importance for an unranked quality scenario,
passed its test but was wrong: the current rules already make such a finding a
`question` when the ranking decides its severity, and no rater saw that.

All of that holds for one model, `claude-opus-5-5`. A fifth run put R1 and
R2 into the rulebook and gave all 38 findings to raters on
`claude-sonnet-5-5` and on `gpt-5.6-sol`. Within each model, the raters
agreed on severity in 37 of 38 findings. Across the two models, they agreed
in only 30 to 32 of 38, so the rulebook's claim fails for reviewers on
different models. Most of the gap comes from one rule: when a story or code
encodes the statement of a document. Three more runs tested designs for that
rule. A list of named cases, built from four stakeholder decisions, aligned
both models on `in_use` for all 28 document findings. A rule for side
texts, such as summaries and comments, then aligned the last two splits.
With both rules, two Sonnet and two Codex raters agree on severity and
category for 28 of 28 document findings. The rules are R3 and R4 in
[Recommendations](#recommendations), and they are in the rulebook with R1
and R2. See [Cross-model run](#cross-model-run).

The test files no finding in this repository. Every number below comes from
the rater output files listed in [Data](#data).

## What was tested

The rulebook claims that two reviewers who record the same facts give a
finding the same severity
([§ Finding Classification](../../packages/factory/rulebooks/conventions/finding-classification.md#finding-classification)).
The test checks that claim on real findings that were written before the
rulebook existed.

The material is the 38 findings in `docs/findings/` of the gigacron repository:
26 SPEC, 8 ATAM, 3 FAGAN, and 1 RECON. Their original ratings used the old
format, with a severity and a category but no basis. `ATAM-001.md` is a review
report, not a finding, and is left out.

## Method

### First run

For each finding, I removed `severity`, `category`, `status`, and the
resolution text, and kept the rest. Three batches of 12 or 13 findings each
went to two raters, so six raters in all. Each rater read the rulebook,
classified each finding, and wrote one JSON line per finding: class,
category, type, basis, severity, blocking, confidence, and an optional
`rule_gap` sentence.

Raters judged `in_use` as of the commit that added the finding, with read-only
git commands. They were not allowed to read gigacron's `docs/findings/` or
`docs/reviews/`.

### Second run

The first run left open questions about rule gaps. The second run tested four
candidate rule changes against a control. Two control raters (K1, K2) used the
current rulebook. Two treatment raters (T1, T2) used the rulebook with the
four changes. Both arms got the same ten findings, rebuilt this time from the
text as filed. The rule files were named `rules-1.md` and `rules-2.md`, so the
raters did not know which arm they were in. I wrote the predictions down
before the run.

All ten raters ran on `claude-opus-5-5`, checked in the transcripts.

## Errors in the setup

I made three errors. Each of them spoiled data, so each is listed with what it
spoiled.

1. **The first-run copies used the current text, not the filed text.** Three
   findings carried text that was added after the review. ATAM-0006 carried
   the stakeholder's decision. ATAM-0009 carried a note that an accepted
   proposal settles it. FAGAN-0003 was rewritten and almost doubled in
   length. These three are left out of every first-run number. Seven more had
   small later edits, such as an ADR number, a link, or a note on a cancelled
   epic: ATAM-0007, ATAM-0008, FAGAN-0001, RECON-0001, SPEC-0012, SPEC-0019,
   and SPEC-0025. None of these edits touches a fact that the basis depends
   on.
2. **The answer key sat in the raters' folder at first.** Rater B2 reported
   it. I moved the key out of the folder and checked every rater's tool calls.
   No rater read the key.
3. **The second-run script cut text at any heading that starts with
   `**Decision`.** ATAM-0006 opens with `**Decision case:**`, so its blind copy
   kept only the title. ATAM-0009 lost its closing section, "Decision for the
   stakeholder", but kept its What-is-wrong and Fix sections. ATAM-0006
   therefore has no valid data in either run. ATAM-0009 stays in the second
   run, with that loss noted.

The cause of errors 1 and 3 is the same: I stripped text by pattern and did not
compare the result with the filed text. Before dispatch, a blind set needs one
check: each blind copy must match the filed text minus the named fields.

The raters also found two partial leaks. Four raters (C1, C2, K2, and T2) read
the gigacron handoff `docs/handoff/2026-10-16-folder-architecture.md`, which
lists the quality scenarios. That handoff calls ATAM-0002 to ATAM-0005 defects
and ATAM-0006 a question, which gives away categories. At a later commit, it
calls ATAM-0009 `major`, and T2 read that line. So T2's rating of ATAM-0009 is
not blind.

A third leak sat in the second-run copy of FAGAN-0003, and I found it only
after the report was written. The copy keeps the line "If ST-0003E is deferred
or dropped, this finding returns to major". The second-run script removed only
lines that contain the word "severity", so this line stayed. All four
second-run raters could read from it that the filed rating is not `major`.
K1 and K2 rated `minor`, which the line may have pushed. T1 and T2 rated
`major` against it. So the FAGAN-0003 split is no weaker for the leak, but the
`minor` votes are not blind.

## Results

### Agreement within a pair

| Run             | Valid findings | Severity | Blocking | Class | Basis | Type  |
| --------------- | -------------- | -------- | -------- | ----- | ----- | ----- |
| First run       | 35             | 35/35    | 35/35    | 32/35 | 31/35 | 24/35 |
| Second, control | 9              | 9/9      | 9/9      | 9/9   | 5/9   | n/a   |
| Second, changed | 9              | 9/9      | 9/9      | 9/9   | 9/9   | n/a   |

The pairs agree on severity in every case. Severity is a coarse value, so the
pairs reach it even when they record different facts. In the first run, the
two C raters put ATAM-0002, ATAM-0003, and ATAM-0007 in different classes. C1
called them architecture risks, and C2 called them document defects. Both
raters reached `major` on all three, by different routes.

Type is the loosest value. For example, one rater picks `incomplete` and the
other picks `inconsistent` for the same finding. Type does not enter the
severity, so this split has no effect on blocking.

### The one split in severity

Four raters read FAGAN-0003 as filed. A Task Draft whose `logical_task_id`
names no Task drops out of `GET /api/v1/tasks`. The product itself never
sends such a Draft. Only a hand-written API call produces one.

| Rater      | Severity | Deciding answer        | Confidence |
| ---------- | -------- | ---------------------- | ---------- |
| K1 control | `minor`  | `fails_purpose: false` | low        |
| K2 control | `minor`  | `fails_purpose: false` | low        |
| T1 changed | `major`  | `fails_purpose: true`  | low        |
| T2 changed | `major`  | `fails_purpose: true`  | medium     |

The four changes do not touch the code class. So the split comes from the
raters, not from the changes. All four named the same gap. The `fails_purpose`
row of the code class counts any wrong required behavior. The calibration
example
[FAGAN-0032](../findings/register/code/FAGAN-0032.json)
gives `minor` to a wrong result that only an input the product never produces
reaches. The rules do not say which of the two applies. The original rating
was `minor`.

### Against the original ratings

Both raters of a pair gave the original category and severity to 27 of the 35
valid first-run findings. The other eight changed as follows.

| Finding                         | Original           | New, both raters  | What changed                                                                                                                                              |
| ------------------------------- | ------------------ | ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SPEC-0003, SPEC-0010, SPEC-0014 | `question`/`major` | `defect`/`major`  | The rulebook gives a question no severity. The raters found a wrong result that a test or an implementer reaches, so each finding is a defect.            |
| SPEC-0026                       | `defect`/`minor`   | `defect`/`major`  | Two definitions of one error code in one file contradict each other, which the document class counts as `fails_purpose`. Both raters gave low confidence. |
| RECON-0001                      | `defect`/`minor`   | `defect`/`note`   | The Scenario is ahead of the code by plan, a planned story owns it, and a reader acts correctly.                                                          |
| ATAM-0002, ATAM-0003, ATAM-0007 | `defect`/`major`   | split on category | C1 rated them `risk`, and C2 rated them `defect`. The severity stays `major` in both.                                                                     |

Under the new rules, SPEC-0003, SPEC-0010, SPEC-0014, and SPEC-0026 block. I
did not check whether the old rules let a `major` question block.

## Recommendations

Each recommendation below states the change, the case it decides, the test
that could have refuted it, and the result. A recommendation stays only when
its prediction held in the second run and no calibration example of the
rulebook contradicts it.

### R1: In use names the text that the Fix changes

**Change.** Add to
[§ In use](../../packages/factory/rulebooks/conventions/finding-classification.md#in-use),
after "a document does harm only through what is built from it":

> The statement is the text that the `**Fix:**` line changes. A syntax defect
> is in use only when a tool outside the run reads that syntax, such as a
> Gherkin runner in CI.

**Case.** SPEC-0007 is a Gherkin `Or` step that the official parser refuses.
The code implements the Scenario's meaning, and no tool parses the feature
file. The current text, "encode its statement", splits the raters. In the
first run, A1 answered `in_use: true` and A2 answered `false`. In the control
arm, K1 answered `false` and K2 answered `true`.

**Test and result.** The prediction was that T1 and T2 would both answer
`false` for SPEC-0007 and SPEC-0013. Both did. The control split on SPEC-0007
again, so the change is needed and does not only restate the rule.

**Calibration check.** The `critical` example of the document class is
`next-id` implementing the statement that the Fix would change, so it stays in
use. [ATAM-0004](../findings/ATAM-0004.md) has no code built from it, so it
stays not in use. Neither example changes.

**Limit.** The split changed the basis, not the severity. Both answers give
`major`, because the code is correct and `harms_downstream` is "no" either
way.

### R2: An ATAM finding is architecture class when it names a quality scenario

**Change.** Add to
[§ Review classes](../../packages/factory/rulebooks/conventions/finding-classification.md#review-classes),
after the ATAM-0004 paragraph:

> An ATAM finding belongs to the architecture class when it names a quality
> scenario and shows how a decision threatens that scenario's response. Every
> other ATAM finding belongs to the document class. A Scenario of a `.feature`
> file is a requirement, not a quality scenario.

**Case.** ATAM-0002, ATAM-0003, and ATAM-0007 each name a numbered
quality-attribute scenario from the review handoff. ATAM-0009 names only a
feature Scenario, PLN-02. Today the rulebook says both that the architecture
class covers findings measured against a quality scenario, and that an ATAM
defect in an architecture document belongs to the document class. A missing
lock fits both statements. In the first run, C1 and C2 split on three of these
four findings. ATAM-0009 went to the architecture class in both control ratings.
In the first run, it went to the document class in both ratings, but that
run used the spoiled text.

**Test and result.** The prediction was that T1 and T2 would put ATAM-0002,
ATAM-0003, and ATAM-0007 in the architecture class and ATAM-0009 in the
document class. Both did.

**Calibration check.** ATAM-0004 names no quality scenario and is a document
defect.
[ATAM-0014](../findings/ATAM-0014.md),
[ATAM-0018](../findings/ATAM-0018.md), and
[ATAM-0019](../findings/ATAM-0019.md) name QS-22, QS-25, and QS-24 and are
architecture risks. All four match the test.

An earlier candidate failed this check, so it is not recommended. It said "a
missing decision is a document defect", and ATAM-0019 is a missing design that
the rulebook rates as an architecture risk.

**Limit.** T2 noted that ATAM-0009 threatens one of the handoff's scenarios
without naming it, and the change does not say whether an implied scenario
counts. In this set, both classes give `major`.

R2 decides the class, not the category. Where a finding names a scenario
without a priority, the category can be `question`, as
[Candidates that failed](#candidates-that-failed) describes.

### R3: Named cases decide whether a document is in use

**Change.** Add to
[§ In use](../../packages/factory/rulebooks/conventions/finding-classification.md#in-use)
an ordered list of seven cases: `syntax`, `built`, `done-story`,
`other-side`, `deferral`, `open-story`, and `none`. The reviewer takes the
first case that applies and records it. When the Fix offers options, the
statement is in use only when it is in use under every option. Add to
[§ Class: document](../../packages/factory/rulebooks/conventions/finding-classification.md#class-document)
that a `code-defect` finding whose Scenario is correct, and whose story is
planned but not done, is a `suggestion` with severity `note`.

**Case.** In the fifth run, Sonnet and Codex split on `in_use` for
SPEC-0013, SPEC-0014, SPEC-0015, and RECON-0001. Codex counted a story that
defers to the faulty text, and code that follows the other side of a
contradiction, as encoding the statement. Sonnet did not. Three wordings of
the principle failed in the sixth run. Each moved a split and removed none.
The stakeholder then decided four policy points: a deferral does not count,
a Fix with options counts only when every option is in use, code on the
other side gives no harm, and a correct Scenario ahead of its planned story is
a note.

**Test and result.** The seventh run tested the cases on the six findings
they were written for, and the eighth run on all 28 document findings, with
two Sonnet and two Codex raters per batch. In the eighth run, all four raters
agreed on `in_use` for 28 of 28 findings, against 23 of 27 in the fifth run.
They agreed on severity and category for 26 of 28, against 21 of 27. The
invented control SPEC-0027, a statement that delivered code implements, came
out in use and `critical` from all four raters. The 22 findings that the
cases were not written for all kept `in_use: false`.

**Limit.** The seventh run found a wording defect: "the changed text" read as
the text after the Fix. The eighth run used "the text that the Fix replaces,
as that text stands now", and the defect did not recur. The 22 new findings
were easy for `in_use`, so the eighth run shows that the cases do no harm, not
that they decide a new hard case.

### R4: A side text counts by what it does to the reader

**Change.** Add to
[§ Class: document](../../packages/factory/rulebooks/conventions/finding-classification.md#class-document),
after the table of the consequence tree: a side text repeats a main rule,
for example a summary, a table or column comment, a diagram label, or a
component description. When the main rule is correct, a side text that leaves
out a case answers `raises_cost`, and a side text that states something the
main rule contradicts, or names something that does not exist, answers
`fails_purpose`. A link that points to the wrong target answers
`raises_cost`. A table or list that states the rule itself is a main rule.

**Case.** With R3, the models still split on SPEC-0023: five summaries leave
out `COMMAND_REJECTED`, which the main rule names. Codex read two texts that
disagree as a contradiction and gave `major`. Sonnet read a correct main rule
and a second look and gave `minor`. SPEC-0024, a column comment that names a
column `TASK_INSTANCE` does not have, split within Codex. The stakeholder
decided: an omission is `minor`, a false statement `major`.

**Test and result.** The ninth run tested the paragraph without its last two
sentences. SPEC-0023 and SPEC-0024 agreed on both models, but the rule moved
two other findings: a wrong glossary link (SPEC-0025) split by model, and
one rater read a main rule table (SPEC-0011) as a side text. The stakeholder
decided that a wrong link costs a second look. The tenth run added the two
sentences. Two Sonnet and two Codex raters per batch agreed on severity,
category, and `in_use` for 28 of 28 document findings, and every prediction
held.

**Limit.** The paragraph was written for SPEC-0011, SPEC-0023, SPEC-0024, and
SPEC-0025. The tenth run shows that it decides these and moves no other
gigacron finding, not that it decides the findings of another project.

## Candidates that failed

- **Harm needs the encoded statement to be wrong.** This candidate added to
  the document `harms_downstream` row: "When the Fix leaves open which of two
  contradicting statements is wrong, answer no." It aimed at SPEC-0015. The
  four ratings of SPEC-0015 under the current rules (B1, B2, K1, K2) already
  answered "no" without it. The low confidence of the first-run pair did not repeat in
  the control (K1 high, K2 medium). The candidate restates what the raters
  already did, so it is removed.

- **"Any option" for a Fix with options.** R1 was tested with two more
  sentences. One said that a Fix with options changes the text that any
  option changes. The other said that code on the other side of a
  contradiction does not encode the statement. T2 showed that the two
  sentences disagree on SPEC-0014 and SPEC-0015. On SPEC-0014, one option of
  the Fix rewrites the text that the delivered code follows. Both sentences
  are removed. R1 keeps only the sentences that the test supports.

- **A missing decision is a document defect.** The ATAM-0019 calibration
  example refutes this candidate, as R2 describes.

- **An unranked quality scenario has importance `high`.** This candidate
  aimed at ATAM-0002, ATAM-0003, and ATAM-0007. Their scenarios come from a
  gigacron handoff and have no priority in § 10.2. Every rater who used the architecture class under the current rules named
  the gap (C1, K1, and K2) and chose `high`. With the
  candidate, T1 and T2 both chose `high` and named no gap, so its prediction
  held. It is still removed, for two reasons:

  - Any fixed default makes raters agree. The test shows that a default
    removes the guess. It does not show that `high` is the right default.
  - The current rules already decide the case.
    [§ The values of a finding](../../packages/factory/rulebooks/conventions/finding-classification.md#the-values-of-a-finding)
    makes a finding a `question` when the reviewer needs the author's intent
    before classifying it. The priority of a scenario is the stakeholder's
    decision, and the candidate made that decision for the stakeholder.

  The priority matters only when it changes the severity. In a project that
  ranks scenarios on two levels, exposure `fails` gives `major` at either
  priority, so the finding stays a `risk`. Exposure `uncertain` gives `major`
  at priority 1 and `minor` at priority 2, so the finding is a `question`.
  Every rater gave ATAM-0002 exposure `fails`, so its rating as a `major`
  risk stands. On ATAM-0003 and ATAM-0007, raters split between `uncertain`
  and `fails`. Those who chose `uncertain` should have filed a `question`.
  None did.

- **A traced path needs a stimulus that the scenario names.** This candidate
  aimed at the exposure split on ATAM-0003 and ATAM-0007. It said that a path
  shows a failure only when the scenario's own stimulus starts it, and that a
  path that also needs an event the scenario does not name gives
  `uncertain`. I wrote it after reading the findings and predicted
  `uncertain` for ATAM-0003. In the fourth run, E1 and E4 gave `uncertain`,
  and E2 and E3 gave `fails`. Without the candidate, in the third run, all four
  raters had given `fails`. The candidate turned agreement into a split that
  decides whether the finding blocks, so it is removed. All four raters named
  the same cause: the rule cannot say whether a boundary tick inside a
  publication belongs to scenario 7. The stakeholder judged ATAM-0003 a badly written finding about an edge case,
  so no rule follows from it.

## Draft calibration examples

These two rows are drafts for the calibration table of
[§ Class: architecture](../../packages/factory/rulebooks/conventions/finding-classification.md#calibration-examples-3).
They add no rule. They show how the current rules apply to a scenario without
a priority. They are not recommendations, because the row for `uncertain` has
not held.

The third and fourth runs used them
([run-3-results.md](../../poc/spikes/finding-classification/key/run-3-results.md),
[run-4-results.md](../../poc/spikes/finding-classification/key/run-4-results.md)).
Twenty-two ratings gave exposure `fails`, and each one is a `major` risk, as the
second row says. That row follows from the matrix, so this is weak evidence.
Two ratings gave `uncertain`. E4 filed a `question`. E1 removed the severity
and the blocking but kept category `risk`. So the first row did not carry the
category for one of two raters. Two raters are too few to judge the row.

| Severity         | Finding                                                                    | Basis                                                   | Why this severity                                                                                                                                                                                                                                                                                                              |
| ---------------- | -------------------------------------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| none, `question` | Invented: a cache decision threatens a response-time scenario from a brief | importance open, `exposure: uncertain`, `in_use: false` | The scenario has no priority in § 10.2. The matrix gives `major` at priority 1 and `minor` at priority 2, so the severity needs the stakeholder's ranking. The reviewer files a `question` in `docs/spec/work/todo.md` that names the scenario and both outcomes.                                                              |
| `major`          | Invented: the same cache decision, shown to fail                           | importance open, `exposure: fails`, `in_use: false`     | The scenario has no priority. Without a ranking of its own, the project uses the two levels of § 10.2. Exposure `fails` gives `major` at priority 1 and at priority 2, so the ranking changes nothing. The finding is a `risk`. A project that ranks on three levels has a `low` row, and there the same case is a `question`. |

## Open gaps without a recommendation

These gaps are real in the rule text, but no candidate rule has been tested
for them yet.

| Gap                                                                                            | Finding    | Observed effect                                                              | Next step                                                                                               |
| ---------------------------------------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Code class: a wrong result that only unusual input to a public API reaches, against FAGAN-0032 | FAGAN-0003 | Severity split, two `minor` and two `major`. Blocking flips.                 | Write a rule that decides the case, then retest with four raters on FAGAN-0003 as filed and FAGAN-0032. |
| Document `fails_purpose`: does a parser that refuses the whole file give a "wrong result"?     | SPEC-0007  | None. All raters gave `major`.                                               | None until a case splits.                                                                               |
| Security: effects `secrets` and `disclosure` both fit an arbitrary file read                   | FAGAN-0002 | None. Both raters chose `secrets` and `critical`.                            | None until a case splits.                                                                               |
| Class table lists code under both the code and the security class                              | FAGAN-0002 | None. Both raters chose security.                                            | None until a case splits.                                                                               |
| No calibration for a specification that runs ahead of planned code                             | RECON-0001 | In the fifth run, Sonnet gave `note` and Codex gave `major`. Blocking flips. | Decide with the `in_use` rule for documents.                                                            |
| Contradiction with a row that describes an open proposal                                       | SPEC-0026  | None. Both raters gave `major`, with low confidence.                         | None until a case splits.                                                                               |

## Cross-model run

The fifth run rebuilt all 38 findings from the filed text with the spike's
`build-blind.py`, so ATAM-0006, ATAM-0009, and FAGAN-0003 are valid there.
The rules were the rulebook with R1 and R2. Each of the three batches went to
two raters on `claude-sonnet-5-5`, as Claude Code subagents, and to two
raters on `gpt-5.6-sol`, through `codex exec` with the project instructions
switched off.

| Field    | Sonnet pairs | Codex pairs | Sonnet against Codex |
| -------- | ------------ | ----------- | -------------------- |
| Severity | 37/38        | 37/38       | 30 to 32 of 38       |
| Blocking | 37/38        | 38/38       | 35 to 36 of 38       |
| Class    | 38/38        | 38/38       | 38/38                |

The prediction was at least 34 of 38 in every comparison. It held within each
model and failed across models. The models split on seven findings, and on
six of them both raters of a model gave the same answer. So each model reads
the rules its own way, and the splits are not noise.

- Four of the seven splits turn on `in_use` for a document: SPEC-0013,
  SPEC-0014, SPEC-0015, and RECON-0001. Codex counts code that follows the
  other side of a contradiction, a story that defers to the faulty text, or a
  pending story as encoding the statement. Sonnet does not. R1 leaves these
  cases open.
- Two findings flip blocking: RECON-0001 (`note` against `major`) and
  SPEC-0023 (`minor` against `major`, on `fails_purpose`).
- ATAM-0006 came out a `minor` risk from Sonnet and a `note` suggestion from
  Codex. Sonnet's own basis, exposure `uncertain` against a scenario without
  a priority, makes it a `question` under the rules. No rater chose
  `question`.
- One Codex rater rated FAGAN-0003 `critical` on a wrong git fact. The
  filing commit was not on `dev` at filing time.

The full table is in
[run-5-results.md](../../poc/spikes/finding-classification/key/run-5-results.md).
The runs that followed, and R3, are described in
[R3](#r3-named-cases-decide-whether-a-document-is-in-use), with their data
in `run-6/` to `run-8/`. R4 followed in `run-9/` and `run-10/`.

## Limits of the test

- The first four runs used one model. The fifth run used two others and
  refuted cross-model agreement. It used one prompt per model, so a part of
  the gap may come from the harness rather than the model.
- Each pair rated a batch once. The second run repeated only ten findings, so
  the effects of R1 and R2 rest on few cases: one split in `in_use` and four
  class decisions.
- Agreement does not show that the answer is right. In the first two runs,
  all raters who chose exposure `uncertain` for an unranked scenario rated a
  `major` risk, where
  the rules give a `question`. The test compared raters with each other and
  with the original rating, and both comparisons missed this.
- ATAM-0006 has no valid rating, so the line between a question and a risk
  was tested on no finding that was filed as a question.
- The four changes were tested together. The test does not show that each
  change works alone.

## Data

The test is set up as a spike in
[poc/spikes/finding-classification/](../../poc/spikes/finding-classification/README.md).
The spike holds the briefs, the blind copies, the ratings, the answer key,
the predictions, both rule files, and two scripts. One script builds a blind
set from the filing commits and logs every line it removes. The other
compares rater pairs.

- `run-1/out/{A1,A2,B1,B2,C1,C2}.jsonl`: first-run ratings.
- `run-2/out/{K1,K2,T1,T2}.jsonl`: second-run ratings.
- `run-2/rules/rules-2.md`: the changed rulebook as tested.
- `key/answer-key.tsv` and `key/retest-predictions.md`: the original ratings
  and the predictions written before the second run.
- `run-5/`: the cross-model run, with its predictions and results in `key/`.
- `run-6/` to `run-8/`: the designs for the `in_use` rule. Run 6 tested three
  wordings, run 7 the case list, and run 8 the case list with corrected
  wording on all 28 document findings.
- `run-9/` and `run-10/`: the side-text rule. Run 9 tested it without the
  sentences on links and main rules, run 10 with them.
- `run-3/` and `run-4/`: the retests of the draft calibration rows and of the
  exposure candidate, with their predictions and results in `key/`.

## Next steps

1. R1 to R4 are in
   [finding-classification.md](../../packages/factory/rulebooks/conventions/finding-classification.md).
   R3 and R4 were written for the gigacron findings. A run on the findings of
   another project, with raters on both models, would test whether they
   decide new findings.
2. The raters recorded the deciding case in a field `in_use_case`. The
   finding format and `finding-lint` do not know that field yet. Adding it is
   a separate change.
3. Keep the draft calibration rows out of the rulebook until the first row
   holds on more raters. The next test needs a finding whose exposure is
   clearly `uncertain`, such as an unchecked assumption about a tool, and a row
   that names the category in its own column.
4. Write a rule for the FAGAN-0003 gap and retest it, as the open-gap table
   describes. Build the blind set with the spike's `build-blind.py`, which
   removes the line "returns to major" from FAGAN-0003.
