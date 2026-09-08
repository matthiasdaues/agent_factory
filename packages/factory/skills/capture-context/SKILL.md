---
name: capture-context
description: >-
  Initialize docs/agent-context.md — the concern-based routing interface
  between agents and project knowledge. --init scans the repo, seeds
  cross-cutting concerns, proposes technical and domain concerns, and
  writes the file. --init --scan adds brownfield documentation discovery.
category: requirements
version: 3.0.0
disable-model-invocation: false
---

# Capture Context

Lifecycle skill for `docs/agent-context.md` — the concern-based routing
interface between agents and a project's own knowledge. See
[Agent Context Composition](../../rulebooks/conventions/agent-context-composition.md)
for the binding structural rules this skill follows, and
[factory-concern-oriented-agent-context.md](../../../docs/proposals/factory-concern-oriented-agent-context.md)
for the design rationale.

**Runs in the orchestrating session, never as a spawned subagent.** The
concern confirmation requires the stakeholder to be present to answer.

## Concern model

Agent context is organized into three concern categories. Each concern
carries a description and `Read:` paths pointing to the knowledge an agent
should consult. See
[Agent Context Composition § The concern model](../../rulebooks/conventions/agent-context-composition.md#the-concern-model)
for the category definitions.

The output file is `docs/agent-context.md`. No YAML files are created
(`stack.yaml`, `workflow.yaml`, `governance.yaml`, `reading-guides.yaml`
belong to the retired YAML model).

## Invocation

| Invocation                      | When                                            |
| ------------------------------- | ----------------------------------------------- |
| `capture-context --init`        | Right after vision capture, before requirements |
| `capture-context --init --scan` | Existing project with documentation to discover |

## `--init` (greenfield)

### Step 0 — Guard

If `docs/agent-context.md` already exists, stop and tell the user:
"docs/agent-context.md already exists — skipping init to protect existing
content. Use `update-context` or edit the file directly." Do not overwrite.

### Step 1 — Repository scan

Scan the project for languages, frameworks, test runners, and
documentation structure. Look for these common markers:

| Signal                                                   | Indicates             |
| -------------------------------------------------------- | --------------------- |
| `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod` | Languages, frameworks |
| `pytest.ini`, `jest.config.*`, `.nycrc`                  | Testing setup         |
| `Dockerfile`, `docker-compose.yml`, `k8s/`               | Infrastructure        |
| `.eslintrc*`, `ruff.toml`, `.flake8`                     | Linting setup         |
| `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`    | CI/CD configuration   |

Report what was found to the user before proceeding.

### Step 2 — Seed cross-cutting concerns

Prepare the six generic cross-cutting concern sections. These are
factory-shipped defaults — every project gets them:

| Concern            | Description                                                                  | Default Read path(s)                                                             |
| ------------------ | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Branching          | Branching policy and worktree discipline.                                    | `factory/rulebooks/conventions/branching-policy.md`                              |
| Committing         | Commit message format and hook discipline.                                   | `factory/rulebooks/conventions/commit-conventions.md`, `.pre-commit-config.yaml` |
| Testing discipline | Risk-based testing, test admission, layer ownership, risk classes.           | `docs/handbook/testing/conventions.md`, `docs/handbook/testing/strategy.md`      |
| Review             | Peer review rules, architecture review triggers, creation/review separation. | `factory/rulebooks/conventions/review-policy.md`                                 |
| Scope discipline   | Build accepted scope only, YAGNI, deferred-feature boundaries.               | `factory/rulebooks/conventions/scope-policy.md`                                  |
| Security           | Security-focused review triggers, secret handling, authorization boundaries. | `factory/rulebooks/conventions/security-policy.md`                               |

For each default `Read:` path, check whether the file exists in the
project. If it does not, keep the path as a placeholder — the concern
section is still valid and the path can be updated later. Present the
cross-cutting concerns to the user for confirmation (usually accepted
as-is).

### Step 3 — Propose technical concerns

From the scan results, propose project-specific technical concerns. Map
detected signals to concern names:

- Backend framework detected (FastAPI, Django, Express, etc.) → propose
  a `backend` concern.
- Frontend framework detected (Vue, React, Angular, etc.) → propose a
  `frontend` concern.
- Database or ORM detected (SQLAlchemy, Prisma, TypeORM, etc.) → propose
  a `data-storage` concern.
- Infrastructure signals (Docker, k8s, Terraform) → propose an
  `infrastructure` concern.

Present the proposed technical concerns to the user: "I found \[framework
list\] — proposing technical concerns: [concern list]. Confirm or adjust?"

The user may:

- **Confirm** the proposed concerns.
- **Rename** a concern (e.g., "api" instead of "backend").
- **Add** a concern the scan missed.
- **Remove** a concern that does not apply.

For each confirmed technical concern, construct a description line and
resolve `Read:` paths from the scan results. When no project-specific
documentation exists yet for a concern, use a placeholder path that
follows the project's documentation convention (e.g.,
`docs/handbook/<concern>/conventions.md`).

### Step 4 — Propose domain concerns

Check whether a scope map exists (`docs/spec/scope-map.md` or equivalent).

**If a scope map exists:** extract the areas from the scope map and propose
one domain concern per area. Present to the user for confirmation.
Resolve `Read:` paths from any matching specification files
(`docs/spec/<area>.feature`, `docs/spec/supplementary_specs/<area>-*.md`).

**If no scope map exists:** leave the domain section empty with this note:

```markdown
## Domain concerns

<!-- Domain concerns are derived from scope-map areas. The planning-agent
     populates this section during backlog creation once a scope map
     exists. -->
```

### Step 5 — Write `docs/agent-context.md`

Assemble the confirmed concerns into `docs/agent-context.md` with this
structure:

```markdown
# Agent Context

## Always (cross-cutting)

### Branching
Branching policy and worktree discipline.
Read: factory/rulebooks/conventions/branching-policy.md

### Committing
Commit message format and hook discipline.
Read: factory/rulebooks/conventions/commit-conventions.md, .pre-commit-config.yaml

### Testing discipline
Risk-based testing, test admission, layer ownership, risk classes.
Read: docs/handbook/testing/conventions.md, docs/handbook/testing/strategy.md

### Review
Peer review rules, architecture review triggers, creation/review separation.
Read: factory/rulebooks/conventions/review-policy.md

### Scope discipline
Build accepted scope only, YAGNI, deferred-feature boundaries.
Read: factory/rulebooks/conventions/scope-policy.md

### Security
Security-focused review triggers, secret handling, authorization boundaries.
Read: factory/rulebooks/conventions/security-policy.md

## Technical concerns

### <confirmed-concern>
<description>
Read: <resolved-paths>

## Domain concerns

### <scope-map-area>
<description>
Read: <resolved-paths>
```

Each concern section MUST have:

- A `###` heading with the concern name.
- A one-line description immediately below the heading.
- At least one `Read:` line with file path(s).

Do NOT create any YAML files. Do NOT create a `docs/agent-context/`
directory.

### Step 6 — Validate

Run `factory/scripts/concern-lint` — confirms the output file has the
required category headings, each concern section has a description and
`Read:` paths, and no legacy YAML residue exists. Fix any `CTX-SECTIONS`
or `CTX-PATHS` finding before proceeding.

### Step 7 — Commit

```
docs: initialize agent context (--init)
```

**Completion**: `docs/agent-context.md` exists with three category
headings (Always, Technical, Domain); six cross-cutting concerns are
seeded; technical concerns are populated from the scan; domain concerns
are populated from the scope map or left empty with a note;
`concern-lint` reports zero errors; no YAML files were created.

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

| Script                         | Checks                                                                                     |
| ------------------------------ | ------------------------------------------------------------------------------------------ |
| `factory/scripts/concern-lint` | section structure (CTX-SECTIONS), path resolution (CTX-PATHS), legacy residue (CTX-LEGACY) |

`validate` runs `concern-lint` automatically once `docs/agent-context.md`
exists — invoking it here is a courtesy check during the interactive
session, not a replacement for that gate.
