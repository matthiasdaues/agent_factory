---
name: capture-context
description: >-
  Initialize docs/agent-context.md — the concern-based routing interface
  between agents and project knowledge. --init scans the repo, seeds
  cross-cutting concerns, proposes technical and domain concerns, and
  writes the file. --init --scan adds brownfield documentation discovery.
category: requirements
version: 4.0.0
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

Runs the full greenfield `--init` flow (Steps 0–4 above: guard, repository
scan, cross-cutting seeding, technical proposals, domain proposals) and
adds one thing: discovery of existing project documentation, folded into
a concern-based interview that enriches each concern's `Read:` paths
before the file is written. Migrating an already-populated YAML
agent-context (`docs/agent-context/*.yaml`) to the concern format is a
separate, bare `capture-context` invocation — out of scope here.

### Step 1 — Guard, scan, and proposals

Run greenfield Steps 0–4 exactly as written: guard against an existing
`docs/agent-context.md`, scan the repository, seed the six cross-cutting
concerns, and propose technical and domain concerns from the detected
stack and scope map. Do not ask for confirmation yet — Step 3 below
confirms each concern together with its discovered `Read:` paths in one
pass.

### Step 2 — Documentation discovery

Scan the project for existing documentation. Look for these common
patterns:

| Pattern                                      | Indicates                                                            | Candidate concern match                                                                                 |
| -------------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `docs/handbook/<name>/**/*.md`               | Handbook conventions for the `<name>` area                           | Technical concern named `<name>` (match by directory name)                                              |
| `docs/handbook/<name>/cookbook/*.md`         | Cookbook recipes for the `<name>` area                               | Same technical concern as its handbook, appended `Read:` entry                                          |
| `docs/adr/**/*.md`, `docs/decisions/**/*.md` | Architecture decision records                                        | Any concern named or described by the ADR's title keywords; offer as a candidate, do not force a match  |
| `docs/spec/supplementary_specs/*.md`         | Entity models, state machines, interface contracts, validation rules | Domain concern matching the scope-map area named in the file, or a technical concern's `Boundary:` line |
| `docs/spec/*.feature`                        | Executable specification for one area                                | Domain concern matching the feature file's area name                                                    |

Report the full discovery inventory to the user before the interview
begins.

### Step 3 — Concern-based interview

Walk concerns in category order: **cross-cutting first, then technical,
then domain.** Within a category, walk one concern at a time — confirm
each concern before moving to the next; do not batch-confirm a whole
category.

For each concern:

1. State the concern's name, description, and any factory-default or
   stack-derived `Read:` paths already proposed for it (from Step 1).
2. List discovered paths (Step 2) that match this concern.
3. Ask: "I found [discovered paths] for the `<concern>` concern — add
   to `Read:`? Anything missing?"
4. Record the answer. The user may confirm all discovered paths, drop
   some, add paths the scan missed, or — for technical and domain
   concerns — rename or remove the concern entirely, same as greenfield
   Step 3.
5. Move to the next concern in category order.

A concern with no discovered paths still gets asked: "Anything missing?"
before moving on — the interview does not skip concerns just because the
scan found nothing for them.

### Step 4 — Write `docs/agent-context.md`

Same as greenfield Step 5, using each concern's confirmed `Read:` list
(factory defaults plus discovered enrichments from Step 3).

### Step 5 — Validate

Same as greenfield Step 6: run `factory/scripts/concern-lint` and fix any
`CTX-SECTIONS` or `CTX-PATHS` finding before proceeding.

### Step 6 — Commit

```
docs: initialize agent context (--init --scan)
```

**Completion**: `docs/agent-context.md` exists with three category
headings; cross-cutting concerns are seeded and enriched with any
matching discovered documentation; technical and domain concerns are
proposed, confirmed, and enriched with discovered `Read:` paths through
the concern-based interview walked in category order (cross-cutting,
technical, domain); `concern-lint` reports zero errors; no YAML files
were created.

## Validation reference

| Script                         | Checks                                                                                     |
| ------------------------------ | ------------------------------------------------------------------------------------------ |
| `factory/scripts/concern-lint` | section structure (CTX-SECTIONS), path resolution (CTX-PATHS), legacy residue (CTX-LEGACY) |

`validate` runs `concern-lint` automatically once `docs/agent-context.md`
exists — invoking it here is a courtesy check during the interactive
session, not a replacement for that gate.
