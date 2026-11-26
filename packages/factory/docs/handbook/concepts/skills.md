---
title: Skills
type: concept
status: implemented
order: 50
description: What a skill is, and which skills you meet most often.
---

# Skills

A skill is a reusable procedure that an agent, or you, invokes to do one well-defined thing: run a structured interview, write an ADR, or run a security review. Each skill is a folder in `.agent-factory/factory/skills/` that holds a `SKILL.md`. Agents call skills, and skills do not call agents.

You meet these skills most often:

| Concern         | Skills                                                                                                                                                                        |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Idea to feature | `draft-proposal` turns an idea into a proposal. `capture-vision` captures a vision in six facets. `grilling`, `grill-me`, and `grill-with-docs` test a design under pressure. |
| Specification   | `derive-feature` writes Gherkin `.feature` files with one Rule per actor and goal. `reverse-map` builds the scope map from code and tests.                                    |
| Test practice   | `detect-test-regime` records the test suites in `docs/testing.yaml`. `qa-strategy-from-spec` writes the QA strategy of one feature. The test-strategy agent runs both.        |
| Onboarding      | `reverse-map` builds a scope map from code, tests, and other sources. `guided-tour` reorients a newcomer, or a user in the middle of a playbook run.                          |
| Quality gates   | `crap-score` computes a composite structural risk. `mutation-testing` runs mutation tests. `dependency-check` checks module import directions against `dependency-rules.dsl`. |
| Implementation  | `run-step` runs one step manifest inside its step boundary.                                                                                                                   |

The full list is in [`.agent-factory/factory/INDEX.yaml`](../../../INDEX.yaml), with the token count of each skill.
