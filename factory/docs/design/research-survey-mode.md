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

Survey mode produces a **cited synthesis** cheaply. It uses only portable
Factory capabilities: bounded source searches, source records, synthesis, and
deterministic validation.

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

1. **Validate the brief** — shared brief schema, `mode: survey`.
   Research Orchestrator.
2. **Plan** — research questions and the search angles per question (reuses
   `research-planning`, but validates against the survey-plan schema:
   questions, search angles, source targets, assignments, and stop conditions.
3. **Gather sources** — a bounded fan-out of sourced searches; each material
   source is recorded with `source-research` against the existing
   source-record schema (provenance is still required).
4. **Synthesise** — a Research Synthesizer produces a cited report:
   per-question findings, each citing the source records it rests on, plus
   uncertainties/gaps and a "what would merit falsification study" note. It
   uses the dedicated `research-synthesis` skill; the existing
   `research-reporting` skill remains restricted to frozen claim registers.
5. **Validate the report** — orchestrator checks every finding cites at least
   one recorded source and that no finding overstates its support.

Dispatch follows the [dispatch-contract](../../rulebooks/conventions/dispatch-contract.md):
economy tier by default, waves of at most six, and a pre-flight estimate.
Every assignment declares a unique output path before dispatch.

## Reuse and drop

- **Reuses:** the brief schema (+ `mode`), `research-planning`,
  `source-research`, and the source-record schema.
- **Adds:** a survey-plan schema and template, a survey-report schema and
  template, a `research-synthesis` skill, and a Research Synthesizer agent.
- **Drops:** `claim-formulation`, `refutation-design`, conjectures, test
  records, adversarial review, votes, the claim register, and resolution loops.

## CLI portability

Research semantics do not depend on a CLI. The orchestrator dispatches a
logical request containing `agent`, `tier`, `task`, `output`, and whether an
independent session is required. The active CLI maps that request to its
supported mechanism:

| CLI                | Separate agent session           | Bounded fan-out                            |
| ------------------ | -------------------------------- | ------------------------------------------ |
| Claude Code        | Native agent dispatch            | Native concurrent dispatch                 |
| GitHub Copilot CLI | Native custom-agent dispatch     | Native concurrent dispatch                 |
| Codex              | Generated native custom agent    | Native parallel-agent threads              |
| Pi                 | `run_agent` subprocess extension | `dispatch_wave` with file-disjoint outputs |

Before planning a run, the orchestrator verifies that the active environment
can access required sources and, for falsification mode, create independent
agent sessions. Survey mode may gather sequentially when parallel fan-out is
unavailable; lack of source access is a blocker. Falsification mode must stop
when independent identities cannot be established.

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

## Implementation decisions

- Survey is a sibling `research-survey.md` playbook. `research-topic.md` remains
  the falsification playbook and routes `mode: survey` briefs to its sibling at
  the front gate.
- The shared research brief gains optional `mode` with default `survey`.
- Survey uses dedicated plan and report schemas. The falsification plan and
  final-report schemas retain their stronger claim/test/register contracts.
- Survey synthesis uses a dedicated agent and skill rather than weakening the
  frozen-register boundary of the Research Report Writer.
- CLI portability is covered by canonical-artifact tests and installed-consumer
  smoke tests for Claude Code, Copilot, Codex, and Pi.
