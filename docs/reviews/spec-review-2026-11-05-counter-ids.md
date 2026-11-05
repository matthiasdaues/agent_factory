---
type: inspect-spec
title: Spec review of counter-ids
date: 2026-11-05
status: defects
reviewer: spec-review-agent
findings_filed: 20
story: counter-ids
scope: the counter-ids specification at commit 6cd2c11fb1f2b49a6265fa5b104cb307fc7b1f0a on dev, read against docs/proposals/counter-ids.md
---

# Spec review of counter-ids

The specification follows the accepted proposal closely, and the structure files agree with the feature file. Three Major defects block architecture: the feature file does not parse as Gherkin, and one Scenario and one QA row specify behaviour of the draft proposal manual-mode-gates. Eight term candidates also wait for the stakeholder. Next, the requirements agent fixes SPEC-0039 and SPEC-0040, the test-strategy agent fixes SPEC-0041, and the domain-modeling agent presents the eight terms.

## Reviewed specification

The review ran in full auto mode, without the stakeholder, as the brief orders. It read these files at commit `6cd2c11f`:

- `docs/spec/features/counter-ids.feature`
- `docs/spec/work/counter-ids-gaps.md`
- `docs/spec/work/counter-ids-qa-strategy.md`
- the counter-ids sections of `docs/spec/entity-model.md`, `docs/spec/interface-contracts.md`, `docs/spec/validation-rules.md` (BR-068 to BR-075), and `docs/spec/state-machines.md`
- the counter-ids rows of `docs/spec/work/term-candidates.md`
- the counter-ids rows of `docs/spec/scope-map.md`, read only
- `docs/spec/glossary.md`
- `docs/proposals/counter-ids.md`, including the Decisions table DEC-01 to DEC-23

`spec-lint`: `0 error(s), 0 warning(s), 59 info across 53 spec file(s).`

## Deterministic findings

| Rule     | Finding                                           | Disposition                                                                      |
| -------- | ------------------------------------------------- | -------------------------------------------------------------------------------- |
| GLOSS001 | Glossary terms that no spec file uses             | Dismissed. No counter-ids term is among them.                                    |
| TODO001  | Open entries in `todo.md` and `todos.md`          | Dismissed. Not part of counter-ids.                                              |
| TRACE003 | BR-011 to BR-055 are defined but never referenced | Dismissed. These rules predate counter-ids. BR-068 to BR-075 are all referenced. |
| TRACE004 | `EPIC_BUILDING_BLOCK` has no attribute block      | Dismissed. This entity predates counter-ids.                                     |

`spec-lint` reports no line about counter-ids. It does not parse the feature file as Gherkin, so it did not catch SPEC-0039.

## Semantic findings

| ID        | Severity | Category | Characteristic | Location                                   | Finding                                                                                                                                          |
| --------- | -------- | -------- | -------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| SPEC-0039 | major    | defect   | Verifiable     | `counter-ids.feature`                      | Code fences and `\#` comments break the Gherkin parse, so a parser sees one Rule and an open doc string. Rewrite in the `derive-feature` layout. |
| SPEC-0040 | major    | defect   | Necessary      | `counter-ids.feature`, CID-08              | The manual-mode code review Scenario specifies draft manual-mode-gates behaviour. Replace it with a two-branch ID Scenario.                      |
| SPEC-0041 | major    | defect   | Necessary      | `counter-ids-qa-strategy.md`, CID-08-LN-02 | The QA strategy tests `code-review-agent.md`, which counter-ids does not change, and calls two committed sections missing.                       |
| SPEC-0051 | minor    | defect   | Unambiguous    | `counter-ids.feature`, CID-07 to CID-10    | Four Rules name an actor that does not act in their Scenarios or that the glossary gives no goal.                                                |
| SPEC-0052 | minor    | defect   | Complete       | `validation-rules.md`, BR-069 and BR-070   | The seed accepts `9999` and two pairs for one prefix, which the claim commit contract cannot hold.                                               |
| SPEC-0053 | minor    | defect   | Complete       | `state-machines.md`, Claim Lifecycle       | A remote that answers but refuses the fetch has no event and no error row.                                                                       |
| SPEC-0054 | minor    | question | Feasible       | `interface-contracts.md`, `next-id`        | The stale-lease check matches English git messages that git may translate. Not checked here.                                                     |

### The conflict of CID-G01

The proposal's ten-rejections criterion builds the case with a `pre-receive` hook that refuses every update. Under DEC-23, that refusal is not a stale lease, so `next-id` fails after one try. The conflict sits in the proposal and goes to the parent, not into a SPEC finding.

The specification handles it correctly. The Scenario "Ten stale claims in a row end the claim" states the behaviour of DEC-15 and DEC-23: ten stale leases end the claim. The gaps report records the conflict as CID-G01 and the choice as CID-C04. The QA strategy picks a different setup: a `pre-receive` hook that moves the ref, so every try meets a real stale lease. It marks that setup as unchecked (CID-QG01) and names a fallback, a `git` wrapper on `PATH`. A story can test the behaviour either way, so no SPEC finding follows.

## Structure checks

### Entity model

No finding. Every entity the feature file names is in the model: the counter ref, the claim commit, the prefix line, the ID prefix, the ID, the indexed artifact, the remote, and the throwaway repository. The attributes agree with the Scenarios. The four-digit form of a line that a claim writes is a choice of the model. The proposal's example `ST=1012` shows the same form.

### State machines

SPEC-0053. The Claim Lifecycle belongs to the claim commit and the counter ref. Its states and transitions agree with the retry, refusal, and failure Scenarios of CID-03 and CID-04.

### Validation rules

SPEC-0052. Each rule from BR-068 to BR-075 names an attribute of the model and a decision or Scenario that needs it.

### Interface contracts

SPEC-0054. The contract of `next-id`, the claim commit message, the `init-factory` check, and the guardrail hook each have a Scenario that reaches them. The two error tables match the proposal row for row. The order of the checks, prefix before remote, matches the proposal's steps.

### Schemas and area specs

No counter-ids schema and no counter-ids area spec exist. The gaps report records the missing area spec as choice CID-C01.

### Glossary

SPEC-0050. "Producer" and "Claim" have glossary meanings that differ from their use in the feature file. "factory maintainer", "the human", and "caller" have no glossary entry.

### Term candidates

Eight rows of `term-candidates.md` in the domain area counter-ids have the status `proposed`. Each one has a Major finding for the domain-modeling agent: SPEC-0042 Counter, SPEC-0043 Claim Commit, SPEC-0044 ID Claim, SPEC-0045 ID Prefix, SPEC-0046 Indexed Artifact, SPEC-0047 Seed, SPEC-0048 Stale Lease, and SPEC-0049 Factory Producer. SPEC-0046 also proposes a wider definition, because ST-0327 does not meet the proposed one.

## Traceability summary

- The scope map holds one row for each of the 11 Rules, and each row links `counter-ids.feature`. No Rule lacks a row, and no row lacks a Rule.
- Each completion criterion of the proposal traces to a Rule or a gap in the gaps report. The `index-lint --check` criterion is a gate (CID-G08).
- Each Rule has a contract row in the QA strategy. CID-08-LN-02 traces to the Scenario that SPEC-0040 asks to replace.
- BR-068 to BR-075 are each referenced from the contracts, the state machine, or the gaps report.
- No Scenario contradicts a decision of the proposal.

## Verdict

The specification is not ready for architecture. SPEC-0039 to SPEC-0049 are Major and block the next step. SPEC-0050 to SPEC-0054 are Minor and do not block.

## Pass 2

Pass 2 read the specification at commit `97584ca1` on dev, in full auto mode. All 16 findings of pass 1 hold their fixes and are resolved. The fresh inspection found one Major and three Minor defects. The Major one, SPEC-0055, is a QA strategy row that still tests the seed range of 0 to 9999. Next, the test-strategy agent fixes SPEC-0055, and the spec then goes to architecture.

### Reviewed specification in pass 2

Pass 2 read the same files as pass 1, at commit `97584ca1`, and the new section `glossary.md` § Counter IDs Vocabulary. `gherkin-official` parses `counter-ids.feature` into 11 Rules and 39 Scenarios.

`spec-lint`: `0 error(s), 0 warning(s), 59 info across 53 spec file(s).` The info lines are the same as in pass 1, and none concerns counter-ids, so the dispositions of pass 1 stand.

### Verification of the pass-1 findings

| ID        | Status   | Check                                                                                                                    |
| --------- | -------- | ------------------------------------------------------------------------------------------------------------------------ |
| SPEC-0039 | resolved | The parser reads 11 Rules and 39 Scenarios. The file has no code fences.                                                 |
| SPEC-0040 | resolved | A two-branch Scenario with `next-id IMPL` replaces the code-review Scenario.                                             |
| SPEC-0041 | resolved | Row CID-08-LN-02 is gone, and the "Generated from" list names both structure sections.                                   |
| SPEC-0042 | resolved | The stakeholder confirmed **Counter**. It is in the glossary.                                                            |
| SPEC-0043 | resolved | The stakeholder confirmed **Claim Commit**. It is in the glossary.                                                       |
| SPEC-0044 | resolved | The stakeholder confirmed **ID Claim**. It is in the glossary, and the feature file uses it. See SPEC-0057.              |
| SPEC-0045 | resolved | The stakeholder confirmed **ID Prefix**. It is in the glossary.                                                          |
| SPEC-0046 | resolved | The stakeholder confirmed **Indexed Artifact** with the proposed definition. The review accepts that choice.             |
| SPEC-0047 | resolved | The stakeholder confirmed **Seed**. It is in the glossary.                                                               |
| SPEC-0048 | resolved | The stakeholder confirmed **Stale Lease**. It is in the glossary.                                                        |
| SPEC-0049 | resolved | The stakeholder confirmed the term as **ID Producer**. It is in the glossary.                                            |
| SPEC-0050 | resolved | The feature file uses "ID producer" and "ID claim", and the three undefined words are gone. See SPEC-0057.               |
| SPEC-0051 | resolved | Ten Rules name the User, CID-11 names the Stakeholder, and the Actor-Goal Matrix matches.                                |
| SPEC-0052 | resolved | BR-069, BR-070, the entity model, and the seed error table bound the seed. See SPEC-0055 and SPEC-0056.                  |
| SPEC-0053 | resolved | The event `FetchRefused` and its error row exist. See SPEC-0058.                                                         |
| SPEC-0054 | resolved | The contract, BR-072, and the state machine notes state `LC_ALL=C`. GitHub's message language stays marked as unchecked. |

### Semantic findings of pass 2

| ID        | Severity | Category | Characteristic | Location                                       | Finding                                                                                                                    |
| --------- | -------- | -------- | -------------- | ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| SPEC-0055 | major    | defect   | Consistent     | `counter-ids-qa-strategy.md`, CID-01-CT-01     | The QA strategy expects `--seed 9999` to pass, which BR-069 refuses, and has no row for a second pair or a refused fetch.  |
| SPEC-0056 | minor    | defect   | Complete       | `counter-ids.feature`, CID-01; gaps report     | The seed Outline lacks rows for `9999` and `ST=5 ST=7`, and no choice row records the narrower range against the proposal. |
| SPEC-0057 | minor    | defect   | Terminology    | structure files, `glossary.md` **Stale Lease** | The structure files use "claim" alone, which the glossary says to avoid, and **Stale Lease** uses the undefined "caller".  |
| SPEC-0058 | minor    | defect   | Consistent     | `interface-contracts.md`, the two error tables | The claim and seed error tables name a refusal by the remote in two different ways.                                        |

### Structure checks in pass 2

- **Entity model.** No finding. The seed range reads 0 to 9998, and `ID.number` stays 1 to 9999, which a seed pair of 0 still meets.
- **State machines.** No finding. `FetchRefused` leads from `READING` to `FAILED`, and the notes name `LC_ALL=C`.
- **Validation rules.** SPEC-0056 for the missing Scenario rows. BR-069 and BR-070 agree with each other.
- **Interface contracts.** SPEC-0058.
- **Schemas and area specs.** None exist for counter-ids, as in pass 1.
- **Glossary.** SPEC-0057. The new section defines each term once, and no two terms name one concept.
- **Term candidates.** `term-candidates.md` holds no row, so no term waits for the stakeholder.

### Traceability in pass 2

- The scope map holds one row for each of the 11 renamed Rules, and each row links `counter-ids.feature`.
- Each Rule has a contract row in the QA strategy. CID-08 traces the two-branch Scenario.
- BR-068 to BR-075 are each referenced from the contracts, the state machine, or the gaps report.
- The seed range of BR-069 differs from the proposal's step 1 by one value. SPEC-0056 asks for a record of the change.

### Verdict of pass 2

The specification is not ready for architecture until SPEC-0055 is fixed. The fix changes two rows of the QA strategy and touches no specification file. SPEC-0056 to SPEC-0058 are Minor and do not block.
