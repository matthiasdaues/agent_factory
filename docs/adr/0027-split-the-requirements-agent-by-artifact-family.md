---
id: 0027
status: proposed
evaluation: none
---

# Split the requirements agent by artifact family

## Context

Take the state machine file `docs/spec/state-machines.md`. Today the
requirements agent declares it as an output, and the architecture agent also
writes it through Step 5 of `maintain-architecture`. So the file has two
writers. Three other core files, `dependency-rules.dsl`, `schemas/*`, and
`areas/*.md`, have no writer at all.

The requirements agent also does too much. It declares eight outputs and eight
skills, loads about 20,000 tokens, and has three entry modes. It runs
interviews, maps scope, writes behaviour, models data, writes the QA strategy,
and captures the agent context.

The accepted proposal
[core-artifact-ownership.md](../proposals/core-artifact-ownership.md) settles
the split (DEC-02 to DEC-04, DEC-07, DEC-10 to DEC-13, DEC-23, DEC-24,
DEC-30, DEC-36). It builds on the core artifact layout of
[ADR-0025](0025-core-artifact-layout-under-docs-spec.md). The rejected options
are:

- **The architecture agent keeps writing state machines.** A state machine
  describes an entity's lifecycle and derives from the entity model, so it
  belongs to domain structure. The architecture agent only reads it (DEC-03).
- **The planning agent owns the QA strategy and `testing.yaml`.** The planning
  agent already carries the whole backlog sequence (DEC-10).
- **The QA agent owns the QA strategy.** The QA agent reviews code against the
  strategy, so it would review against its own artifact.
- **A cheaper test-strategy agent split by skill.** The scan of the test suites
  needs no judgment, but the layer assignment does. Three agents work from the
  strategy, so a wrong assignment spreads (DEC-13).
- **The test-strategy agent runs the test guardrails.** Running a gate needs no
  judgment, and a gate must block before the merge. So the implementation agent
  keeps running them (DEC-23).

`evaluation: none`, because the proposal decided each point and no open
alternative is left to weigh.

## Decision

Ownership follows the artifact family, not a playbook step. Each family has
one producing agent:

- **Scope and behaviour** stays with the requirements agent: the scope map,
  the feature files, and the area specs. It loses step 1d, step 2, and the
  skills `qa-strategy-from-spec` and `capture-context`. Its handoff names the
  domain-modeling agent.
- **Domain structure** goes to a new domain-modeling agent at the strong tier:
  the glossary, the entity model, state machines, validation rules, interface
  contracts, and schemas. It always writes `glossary.md` and
  `entity-model.md`. It presents term definitions to the stakeholder one domain
  area at a time.
- **Architecture** stays with the architecture agent, which now also declares
  `dependency-rules.dsl`. It reads `entity-model.md` and `state-machines.md`
  as context inputs and files an `ARCH` finding on a contradiction.
- **Test practice**, outside the core, goes to a new test-strategy agent at the
  strong tier: `docs/testing.yaml` and the QA strategies. It owns the test
  guardrails `crap-score`, `mutation-testing`, and `test-design-verify`, and
  sets their thresholds in the `gates` section of `testing.yaml`. The
  implementation agent runs them after each story, together with the project's
  command from `gates.mutation_testing.command`. The mutation tool's
  configuration stays in the project's own files.

Virgil keeps `docs/agent-context.md` and gives up `docs/testing.yaml`. In step
2b of the fitting, the session takes the test-strategy agent's role.
`dependency-check` stays with the architecture agent, because it checks the
rules that agent owns.

This decision amends [ADR-0012](0012-dispatcher-owned-semantic-gate-loop.md):
mutation testing now runs as a gate through the project's command, instead of
staying outside the gate loop.

## Consequences

- Each agent definition loads less context, and each core file has one agent to
  ask when it is wrong.
- The specification phase gains a step. The order is requirements agent, then
  domain-modeling agent, then spec-review agent. `run-step` still decides
  eligibility by the existence of input files (DEC-21), so the test-strategy
  agent can run before the spec review ends. A contract that the review changes
  then needs a revised QA strategy, and no check enforces that revision.
- The architecture agent can build its baseline before the domain structure
  exists. `run-step` does not start it again when the entity model changes, so
  the domain-modeling agent's handoff starts the component pass.
- The four playbooks that name a moved responsibility, the `INDEX.yaml`
  preconditions, and `intent` must name the new owners.
- Existing projects keep their files. The domain-modeling agent takes over the
  structure files on its next run.
