---
name: capture-context
description: >-
  Initialize docs/agent-context/ — the YAML routing interface between agents
  and project knowledge — for a new project. capture-context --init scaffolds
  stack.yaml, workflow.yaml, and governance.yaml from templates in mode:
  primary, then runs a stakeholder interview that records the answers as
  inline values. Use when starting a new project's agent context.
category: requirements
version: 1.0.0
disable-model-invocation: false
---

# Capture Context

Lifecycle skill for `docs/agent-context/` — the YAML interface between
agents and a project's own knowledge. See
[Agent Context Composition](../../rulebooks/conventions/agent-context-composition.md)
for the binding structural rules this skill follows, and
[yaml-charter-lifecycle.md](../../../docs/proposals/yaml-charter-lifecycle.md),
[ADR-0013](../../../docs/adr/0013-yaml-agent-context-replaces-markdown-charter.md),
and [ADR-0014](../../../docs/adr/0014-two-layer-routing-with-two-mode-lifecycle.md)
for the design rationale.

**Runs in the orchestrating session, never as a spawned subagent.** The
stakeholder interview requires the stakeholder to be present to answer.

## Agent-context structure

Three Layer 2 index files, one template each at
`factory/rulebooks/templates/context-stack.yaml`, `context-workflow.yaml`,
`context-governance.yaml` — see
[Agent Context Composition § The four files](../../rulebooks/conventions/agent-context-composition.md#the-four-files)
for what each carries. A fourth file, `reading-guides.yaml`, is the Layer 1
routing table; it is not part of this mode because a greenfield project has
no populated sections yet to route to.

## Mode selection

| Invocation               | Mode                | When                                            |
| ------------------------ | ------------------- | ----------------------------------------------- |
| `capture-context --init` | Greenfield scaffold | Right after vision capture, before requirements |

Brownfield onboarding (`capture-context --init --scan`) is a separate mode,
covered once that behaviour ships.

## Mode 1 — `--init` (greenfield)

### Step 1 — Create the skeleton

For each of `stack.yaml`, `workflow.yaml`, `governance.yaml`: if
`docs/agent-context/<file>` already exists, skip it and leave it untouched
— this skip-if-exists guard protects any values a prior run already
recorded. Otherwise, copy the matching template
(`factory/rulebooks/templates/context-<file>`) to
`docs/agent-context/<file>` unchanged, keeping `mode: primary` and every
null placeholder exactly as authored.

Never create `reading-guides.yaml` in this mode. It routes to populated
index sections, and a fresh greenfield project has none yet —
`update-context` proposes creating it once the first `source:` pointer
exists.

### Step 2 — Stakeholder interview

Ask the stakeholder about the project's technology and process choices and
record every answer as an inline value directly on the matching field.
`mode: primary` means no `source:` pointer is required, or permitted, at
this stage.

| Ask                                                    | Field                                                      |
| ------------------------------------------------------ | ---------------------------------------------------------- |
| What language(s) and runtime version(s)?               | `stack.yaml#languages`                                     |
| What backend, frontend, and testing frameworks?        | `stack.yaml#frameworks.backend` / `.frontend` / `.testing` |
| What data stores?                                      | `stack.yaml#data_stores`                                   |
| What infrastructure (hosting, containers, cloud)?      | `stack.yaml#infrastructure`                                |
| Any existing systems this integrates with?             | `stack.yaml#existing_systems`                              |
| Licensing model and constraints?                       | `stack.yaml#licensing.project` / `.constraints`            |
| Anything explicitly out of scope?                      | `stack.yaml#exclusions`                                    |
| Repository layout convention?                          | `workflow.yaml#repository_layout`                          |
| How does a new contributor get started?                | `workflow.yaml#getting_started`                            |
| How is the project run locally?                        | `workflow.yaml#running`                                    |
| Testing approach?                                      | `workflow.yaml#testing`                                    |
| Linting and formatting tools?                          | `workflow.yaml#linting`                                    |
| CI/CD pipeline?                                        | `workflow.yaml#ci_cd`                                      |
| Branching model?                                       | `workflow.yaml#branching`                                  |
| Commit conventions?                                    | `governance.yaml#commits`                                  |
| Review process?                                        | `governance.yaml#review`                                   |
| Testing discipline (coverage expectations, TDD, etc.)? | `governance.yaml#testing_discipline`                       |
| Architecture governance (ADRs, review gates)?          | `governance.yaml#architecture_governance`                  |
| Scope boundaries and change process?                   | `governance.yaml#scope`                                    |

Leave a question the stakeholder cannot yet answer as `null` — do not
invent an answer to fill the gap. A later `capture-context` or
`update-context` pass fills it in.

### Step 3 — Validate

Run `factory/scripts/context-lint` (default mode) — confirms all three
files exist, parse, carry every required top-level key, and report
`mode: primary`. Every remaining null leaf reports as a `CX-NULL` warning,
expected at this stage, not an error. Fix any `CX-KEYS` or `CX-PARSE`
finding before proceeding — those indicate a corrupted template copy, not
an unanswered question.

### Step 4 — Commit

```
docs: initialize agent context (--init)
```

**Completion**: `stack.yaml`, `workflow.yaml`, and `governance.yaml` exist
under `docs/agent-context/` with `mode: primary`; `reading-guides.yaml` was
not created; any file that already existed was left untouched; stakeholder
answers are recorded as inline values; `context-lint` (default mode)
reports zero errors.

## Validation reference

| Script                         | Mode    | Checks                                                                             |
| ------------------------------ | ------- | ---------------------------------------------------------------------------------- |
| `factory/scripts/context-lint` | default | files exist, YAML parses, required keys present, `mode` is valid, null leaves warn |

`validate` runs `context-lint` automatically once `docs/agent-context/`
exists — invoking it here is a courtesy check during the interactive
session, not a replacement for that gate.
