# Design Spec: Survey/Synthesis Research Mode

Status: lightweight spec (design, not yet implemented). Derived from the
[research-workflow-efficiency-and-atomicity](../proposals/research-workflow-efficiency-and-atomicity.md)
proposal, Change 3.

## Purpose

Give the research workflow a second, lighter gear for questions that do not need
the full falsification apparatus. The falsification playbook exists to make a
small number of contested, high-stakes claims survive a genuine, auditable
refutation attempt. Landscape and discovery questions — "what open-source tools
exist for these stages," "summarise the options," "what is the state of X" — do
not have contested claims to refute; running them through independent
researchers, three-reviewer voting, a claim register, and resolution loops pays
a large cost for rigor the question never asked for.

Survey mode produces a **cited synthesis** cheaply. It is the shape of the
built-in deep-research capability, expressed within the factory's brief-and-report
framing.

## Mode selection

The research brief gains an optional `mode` field: `"survey"` (default) or
`"falsification"`. Falsification is opt-in. The playbook selects the path at the
front gate using this rubric:

| Choose **survey** when…                                                        | Choose **falsification** when…                                                                   |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| The question is "what exists / what is the landscape / summarise the options." | There are a few specific, contestable claims whose truth is in dispute.                          |
| A wrong synthesis costs little to moderate and is cheap to correct.            | Being wrong is expensive, adversarial, or hard to reverse (safety, security, regulatory, money). |
| The value is coverage and a sourced overview.                                  | The value is an auditable "this claim survived refutation within its scope."                     |
| Sources are public and self-verifiable.                                        | Independence between author, reviewer, and voter is worth paying for.                            |

When the brief is unsure, default to survey; a survey can surface the two or
three claims that actually merit escalation to falsification mode afterwards.

## Survey playbook shape

Five steps, no conjectures/tests/reviews/votes/register:

1. **Validate the brief** — same brief schema, `mode: survey`. Orchestrator.
2. **Plan** — research questions and the search angles per question (reuses
   `research-planning`, but produces questions + source targets, not competing
   conjectures or a review protocol).
3. **Gather sources** — a bounded fan-out of sourced searches; each material
   source is recorded with `source-research` against the existing
   source-record schema (provenance is still required).
4. **Synthesise** — one writer produces a cited report: per-question findings,
   each citing the source records it rests on, plus an explicit
   uncertainties/gaps section and a "what would merit deeper (falsification)
   study" note. Reuses `research-reporting`.
5. **Validate the report** — orchestrator checks every finding cites at least
   one recorded source and that no finding overstates its support.

Dispatch follows the [dispatch-contract](../../rulebooks/conventions/dispatch-contract.md):
cheap tier by default, waves of six, pre-flight estimate.

## Reuse and drop

- **Reuses:** the brief schema (+ `mode`), `research-planning`,
  `source-research`, the source-record schema, `research-reporting`.
- **Drops:** `claim-formulation`, `refutation-design`, conjectures, test
  records, adversarial review, votes, the claim register, and resolution loops.

## Guardrails

- A survey report **cites sources** for every finding and **flags uncertainty**
  where evidence is thin or one-sided; it is a sourced synthesis, not a set of
  verified claims.
- Survey mode **must not use the language of falsification.** It may not say a
  finding "survived refutation," was "admitted," or is "validated" in the
  claim-register sense. Those terms are reserved for falsification mode, where a
  claim actually faced independent tests and votes. A survey states what the
  sources say and how strongly.
- A light self-verification pass (the writer re-checks its load-bearing sources)
  is expected, but it is not the independent, separate-session review of
  falsification mode and must not be presented as such.

## Non-goals

- Not a replacement for falsification mode; the two coexist and the brief
  chooses.
- Not a new schema family: survey mode reuses the source-record and (a lighter
  use of the) final-report schema rather than inventing artifacts.
- Not a change to the Claim-Admission or Role-Separation policies, which govern
  falsification mode only.

## Open questions for implementation

- Whether survey mode is a branch inside `research-topic.md` or a sibling
  `research-survey.md` playbook (the proposal leans sibling for clarity).
- Whether the final-report schema needs a lighter survey variant or can be
  reused as-is with `refuted_conjectures`/`unresolved_alternatives` left empty.
