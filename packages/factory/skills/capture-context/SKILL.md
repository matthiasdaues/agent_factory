---
name: capture-context
description: >-
  Initialize docs/agent-context/ — the YAML routing interface between agents
  and project knowledge. capture-context --init scaffolds stack.yaml,
  workflow.yaml, and governance.yaml from templates, then runs a stakeholder
  interview that records the answers as inline values.
  capture-context --init --scan discovers existing documentation in a
  brownfield project, runs a concern-based interview, populates index files
  with name and source pointers, and generates reading-guides.yaml.
category: requirements
version: 2.0.0
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
routing table; it is not created during greenfield init because a fresh
project has no populated sections yet to route to.

## Invocation

| Invocation                      | When                                            |
| ------------------------------- | ----------------------------------------------- |
| `capture-context --init`        | Right after vision capture, before requirements |
| `capture-context --init --scan` | Existing project with documentation to discover |

## `--init` (greenfield)

### Step 1 — Create the skeleton

For each of `stack.yaml`, `workflow.yaml`, `governance.yaml`: if
`docs/agent-context/<file>` already exists, skip it and leave it untouched
— this skip-if-exists guard protects any values a prior run already
recorded. Otherwise, copy the matching template
(`factory/rulebooks/templates/context-<file>`) to
`docs/agent-context/<file>` unchanged.

Never create `reading-guides.yaml` in this invocation. It routes to
populated index sections, and a fresh greenfield project has none yet —
`update-context` proposes creating it once the first `source:` pointer
exists.

### Step 2 — Stakeholder interview

Ask the stakeholder about the project's technology and process choices and
record every answer. When the stakeholder provides both a value and a
source document, write `name:` and `source:` together. When only a value is
available, write it as inline text under `name:` (or directly for simple
scalar fields).

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

Mark a question the stakeholder cannot yet answer as
`deferred: "<reason>"` — do not leave it as `null` (null is always an
error) and do not invent an answer to fill the gap. A later
`capture-context` or `update-context` pass fills it in. Remove keys that
the stakeholder confirms do not apply to this project.

### Step 3 — Validate

Run `factory/scripts/context-lint` — confirms all three files exist, parse,
and carry no null leaves. Fix any `CX-NULL`, `CX-KEYS`, or `CX-PARSE`
finding before proceeding.

### Step 4 — Commit

```
docs: initialize agent context (--init)
```

**Completion**: `stack.yaml`, `workflow.yaml`, and `governance.yaml` exist
under `docs/agent-context/`; `reading-guides.yaml` was not created; any
file that already existed was left untouched; stakeholder answers are
recorded; `context-lint` reports zero errors.

## `--init --scan` (brownfield onboarding)

Discovers existing documentation signals in a project, runs a concern-based
interview, populates index files with name and source pointers, and
generates `reading-guides.yaml`. Legacy markdown charter projects are
detected via format detection and offered optional migration.

### Step 1 — Legacy detection

Run format detection (the three-step chain from context-lint). If the
project has `docs/charter/tech-stack.md` (legacy markdown charter) and no
`docs/agent-context/` directory:

1. Tell the user: "This project uses legacy markdown charter files.
   Would you like to migrate to YAML agent-context?"
2. If the user **declines**: stop here — leave the markdown charter
   unchanged, do not create `docs/agent-context/`, and exit. The project
   continues using its existing charter files.
3. If the user **confirms**: proceed to Step 2. The migration happens
   as a side effect of the brownfield scan populating the new YAML files.

If `docs/agent-context/` already exists, skip this step.

### Step 2 — Create the skeleton

Same as greenfield Step 1 — for each of `stack.yaml`, `workflow.yaml`,
`governance.yaml`: if `docs/agent-context/<file>` already exists, skip it.
Otherwise, copy the matching template to `docs/agent-context/<file>`.

### Step 3 — Discovery scan

Scan the project for documentation signals. Look for these common markers:

| Signal                                                   | Indicates                 | Maps to                                         |
| -------------------------------------------------------- | ------------------------- | ----------------------------------------------- |
| `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod` | Languages, frameworks     | `stack.yaml#languages`, `stack.yaml#frameworks` |
| `docs/adr/`, `docs/decisions/`                           | Architecture decisions    | `governance.yaml#architecture_governance`       |
| `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`    | CI/CD configuration       | `workflow.yaml#ci_cd`                           |
| `pytest.ini`, `jest.config.*`, `.nycrc`                  | Testing setup             | `workflow.yaml#testing`                         |
| `Dockerfile`, `docker-compose.yml`, `k8s/`               | Infrastructure            | `stack.yaml#infrastructure`                     |
| `.eslintrc*`, `ruff.toml`, `.flake8`                     | Linting setup             | `workflow.yaml#linting`                         |
| `CONTRIBUTING.md`, `docs/development.md`                 | Development practices     | `workflow.yaml#getting_started`                 |
| `.pre-commit-config.yaml`                                | Commit/review conventions | `governance.yaml#commits`                       |

Report what was found to the user before proceeding to the interview.

### Step 4 — Concern-based interview

For each applicable work-type concern (based on what the scan discovered),
ask the user where conventions are documented and propose source paths
from the scan results. The concerns follow the `reading-guides.yaml`
template structure:

**Backend** (if backend framework signals found):

- "The scan found [framework]. Where is the backend documented?"
- Propose source path based on discovered files.
- Write `name` and `source` to `stack.yaml#frameworks.backend`.

**Frontend** (if frontend framework signals found):

- Same pattern for `stack.yaml#frameworks.frontend`.

**Testing** (if test config signals found):

- "Where are testing conventions documented?"
- Write to `workflow.yaml#testing` and `governance.yaml#testing_discipline`.

**Architecture** (if ADR directory found):

- "The scan found ADRs at [path]. Is this the architecture decision record?"
- Write to `governance.yaml#architecture_governance`.

**CI/CD** (if CI config found):

- Write to `workflow.yaml#ci_cd`.

**Packaging/Infrastructure** (if Docker/k8s signals found):

- Write to `stack.yaml#infrastructure`.

For each field, the user may:

- **Confirm** the proposed source → write `name` and `source` together.
- **Override** with a different source path → write the override.
- **Defer** → write `deferred: "<reason>"`.
- **Remove** → delete the key entirely (not applicable to this project).

Fields with no applicable scan signal are presented at the end as "The scan
found no signals for [field]. Do you have documentation for this?" — the
user can provide a source, defer, or remove.

### Step 5 — Reading-guide assembly

After the interview, generate `docs/agent-context/reading-guides.yaml`
from `factory/rulebooks/templates/context-reading-guides.yaml`. Prune
concerns that have no populated sections (all their referenced fields are
still `deferred`). Keep concerns that have at least one populated
source pointer.

### Step 6 — Validate

Run `factory/scripts/context-lint` — confirm zero errors. Fix any
`CX-KEYS`, `CX-PARSE`, or `CX-FORMAT` finding before proceeding.

### Step 7 — Commit

```
docs: initialize agent context (--init --scan)
```

**Completion**: `stack.yaml`, `workflow.yaml`, `governance.yaml`, and
`reading-guides.yaml` exist under `docs/agent-context/`; source pointers
are populated from the discovery scan and concern interview;
`context-lint` reports zero errors.

## Validation reference

| Script                         | Checks                                                                                 |
| ------------------------------ | -------------------------------------------------------------------------------------- |
| `factory/scripts/context-lint` | files exist, YAML parses, null leaves are errors, deferred conflicts, source existence |

`validate` runs `context-lint` automatically once `docs/agent-context/`
exists — invoking it here is a courtesy check during the interactive
session, not a replacement for that gate.
