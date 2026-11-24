---
type: independence-review
title: "Independence review — sequences where one source creates a claim and supplies its check"
date: 2026-11-23
status: defects
reviewer: claude-code session, appraised by a colleague
findings_filed: 0
story:
scope: Factory agent, skill, playbook and rulebook definitions under packages/factory on dev at bcd4db465970edc73bb381ad93a37739ef770527, and the draft proposal docs/proposals/evidence-bound-findings.md
---

# Independence Review — Self-Adjudication, Oracle Leakage and Normative Backfeed

## Summary

The current factory has one serious self-adjudication loop: the bug hunt. The QA agent raises a bug, writes the test that shows it, fixes the code and closes the finding, and no other reader checks its reading of the contract. Brownfield onboarding has a limit by design: its specification describes the existing code and cannot show that code correct. Repeat review, test design and reconciliation carry smaller risks. Test design and reconciliation each already have an outside contract or a separate review stage, so neither is a closed loop. The draft proposal Evidence-Bound Findings names two further design risks, which are open questions there, not defects of the factory.

A first pass of this review called six sequences circular. A colleague's appraisal showed that two of them rested on summary lines, not on the steps that do the work. This report keeps only what the procedure text supports, and cites the line that does each step.

## Labels

A sequence is a chain of steps in which a claim is made and then checked. The review sorts each weak link by one of three labels:

| Label              | Meaning                                                                                |
| ------------------ | -------------------------------------------------------------------------------------- |
| Self-adjudication  | One agent raises, interprets, fixes or closes its own claim.                           |
| Oracle leakage     | The expected behaviour of a test comes from the implementation it checks.              |
| Normative backfeed | Behaviour observed in the code becomes the specification without independent approval. |

## Findings

Definitions that agents execute belong to the code class ([finding-classification.md § Review classes](../../packages/factory/rulebooks/conventions/finding-classification.md#review-classes)). Every definition below is on `dev` and installed in projects, so `in_use` is true throughout.

| Finding                                                                                                                                                                                                                                                                                                                                                                                                                                            | Artifact                                                                                    | Category   | Severity | Filed as                          |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ---------- | -------- | --------------------------------- |
| F1. Self-adjudication in the bug hunt. One agent hunts, writes the red test, fixes, and sets `resolved`, with its own reading of the Scenario as the only check. Fix: give the claim one independent link before the code changes, for example a second reader who confirms that the cited Scenario states the expected behaviour.                                                                                                                 | `packages/factory/skills/bug-hunt/SKILL.md:33-45`, `packages/factory/agents/qa-agent.md:88` | Defect     | major    | not filed, awaits the stakeholder |
| F2. Oracle leakage in test design for edge cases the specification leaves open. Step 6 finds edge cases "visible in the implementation", and step 7 writes an expected outcome for each, without saying where the outcome comes from when no Scenario states it. Fix: take every expected outcome from the Rule or Scenario; an edge case whose outcome the specification does not state becomes an entry in `docs/spec/work/todo.md`, not a test. | `packages/factory/skills/test-design/SKILL.md:123`, `:140`, `:144`                          | Suggestion | minor    | not filed                         |
| F3. Self-adjudication in repeat review. The reviewer that raised a finding decides whether the fix resolves it. Steps 1 and 3 rerun the gates and the full inspection, so the risk is only that the same reviewer repeats a wrong reading. Fix: send a disputed or high-impact finding to a second reader on the repeat pass.                                                                                                                      | `packages/factory/rulebooks/conventions/review-loop-discipline.md:17`                       | Suggestion | note     | report only                       |
| F4. Normative backfeed in brownfield onboarding, by design. The scope map and the `.feature` file describe the code as found. The stakeholder confirms the draft by walking the domain grouping and the open questions, not each behaviour. Fix: state at the confirmation step that a confirmed row records behaviour as found, not as intended.                                                                                                  | `packages/factory/skills/reverse-map/SKILL.md:148`                                          | Suggestion | minor    | not filed                         |
| F5. Normative backfeed in reconciliation, outside the core list. A `spec-stale` row on an artifact outside the core list closes at `fixed` with no review. The owner's reading of the code then becomes the document.                                                                                                                                                                                                                              | `packages/factory/playbooks/documentation-update.md:101`                                    | Suggestion | note     | report only                       |

### F1. Self-adjudication in the bug hunt

**Sequence.** The QA agent runs `bug-hunt` with the `.feature` file as the contract source (`qa-agent.md:88`). The hunter files the bug with its violated Rule or Scenario in `traces` (`bug-hunt/SKILL.md:33`). In the fix phase the same agent writes a failing test, changes the code until the test passes, and sets the finding to `resolved` (`bug-hunt/SKILL.md:39-43`). It then hunts again (`:45`).

**What is outside the loop.** The `.feature` file and the existing tests (`bug-hunt/SKILL.md:41`, "Verify no existing tests broke"). Both are real outside evidence. Neither checks the hunter's reading of the Scenario, because the hunter writes the red test from that reading.

**Basis.** `in_use: true`. `harms_downstream: false`: no wrong result in an installed project has been traced to this sequence. `fails_purpose: true`: the bug hunt exists to find real defects, and a misread Scenario passes every step from the claim to the closed finding. `raises_cost: true`.

**Why this severity:** The sequence lets one agent's reading of a contract become a test and a code change with no other reader, which the foundational rule on separating creation from validation (`rules.md:33`) does not allow for agent judgments. The Karl+Charles experiment observed false hunter bugs and fixes that turned correct code into wrong code. It did not isolate this sequence as their cause, so the finding rests on the rule, not on the experiment.

### F2. Oracle leakage in test design

**Sequence.** `test-design` first reads the owned `.feature` Rules and Scenarios (step 3), then reads the implemented code to find seams and edge cases (step 6, `:123`), then writes tests with an expected outcome (step 7, `:140`, `:144`). For a Scenario-backed case, the outcome comes from the specification. For an edge case that the code reveals and no Scenario covers, the skill gives no source, so the outcome can only come from the code.

**Basis.** `in_use: true`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true`.

**Why this severity:** The skill writes correct tests for every specified behaviour, so it serves its purpose (no to fails_purpose). A test for an unspecified edge case fixes the code's current choice as a contract, so a later correct change to that case breaks a test that no requirement backs.

### F3. Self-adjudication in repeat review

**Basis.** `in_use: true`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false`. The repeat pass reruns the gates and the full inspection (`review-loop-discipline.md:16-18`). It is an appeal risk, not a closed loop.

### F4. Normative backfeed in brownfield onboarding

**Sequence.** `reverse-map` builds the scope map from tests and code. An unattended run writes it as a draft, and the Stage 1 exit fails on `SCOPE001` until a stakeholder confirms it (`reverse-map/SKILL.md:148`, `playbooks/brownfield-onboarding.md:139`). `derive-feature` refuses a draft map (`derive-feature/SKILL.md:34`). So the gate holds. What the confirmation covers is narrower than what later readers may assume: the domain grouping and the open questions.

**Basis.** `in_use: true`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true`.

**Why this severity:** Brownfield onboarding characterises existing behaviour on purpose, so the specification serves its job (no to fails_purpose). A later reviewer who treats a confirmed Scenario as intended behaviour cannot tell it from one the stakeholder chose, and must trace it back to the code.

### F5. Normative backfeed in reconciliation

**Sequence.** `reconcile-spec` changes no specification and writes one row per drift for the artifact's owner (`reconcile-spec/SKILL.md:39`). The owner changes the artifact; a reviewer confirms or rejects each fixed row on the core list (`documentation-update.md:85-99`). A row outside the core list closes at `fixed` without review (`:101`). The core list covers the scope map, the `.feature` files and the domain structure files, so the remaining gap is small.

**Basis.** `in_use: true`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false`.

## Not findings

- **Reconciliation on the core list.** The owner pass and the reviewer pass stand between a `spec-stale` row and the specification. The sequence is not self-confirming.
- **Test design for specified behaviour.** Expected outcomes come from the `.feature` file. Only F2 remains.
- **Finding Classification.** `finding-lint` checks that a severity follows from the recorded basis, not that the basis is true. That is a limit of the check, not a loop: the lint makes no claim about truth.
- **Evidence-Bound Findings, draft.** Two open questions are design risks of self-adjudication: who writes the refuting test (`evidence-bound-findings.md:179`) and whether the specification check needs a second reader (`:180`). The proposal assigns the test to the fix developer (`:120`). They stay in the proposal's Open Questions.

## Next Steps

1. F1 classifies as `major`. A blocking finding becomes a finding file through `next-id BUG` or `next-id IMPL`, per [finding-format.md](../../packages/factory/rulebooks/conventions/finding-format.md). The stakeholder decides whether to file it now or to let Evidence-Bound Findings carry the fix.
2. F2 and F4 are `minor` and become register files under `docs/findings/register/code/` when filed.
3. Evidence-Bound Findings can cite F1 as its strongest case for an independent link before the fix.
