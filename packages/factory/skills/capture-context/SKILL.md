---
name: capture-context
description: >-
  Initialize docs/agent-context.md — the concern-based routing interface
  between agents and project knowledge. --init scans the repo, seeds
  cross-cutting concerns, proposes technical and domain concerns, and
  writes the file. --init --scan adds brownfield documentation discovery.
  Bare invocation (no flags) detects a legacy YAML agent-context and offers
  interactive migration to the concern model.
category: requirements
version: 5.0.0
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

| Invocation                      | When                                                         |
| ------------------------------- | ------------------------------------------------------------ |
| `capture-context --init`        | Right after vision capture, before requirements              |
| `capture-context --init --scan` | Existing project with documentation to discover              |
| `capture-context` (bare)        | Existing project with a legacy YAML agent-context to migrate |

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
separate, bare `capture-context` invocation — see
[Bare invocation (YAML migration)](#bare-invocation-yaml-migration) below.

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

## Bare invocation (YAML migration)

Migrates an existing YAML agent-context (`docs/agent-context/stack.yaml`,
`workflow.yaml`, `governance.yaml`, `reading-guides.yaml`) to
`docs/agent-context.md`. Interactive — the YAML-to-concern mapping requires
judgment, so nothing is written without the user confirming the proposed
structure first.

### Step 0 — Guard

If `docs/agent-context.md` already exists, stop and tell the user the
project is already on the concern model — nothing to migrate.

### Step 1 — Detect

Check for `docs/agent-context/stack.yaml`, `workflow.yaml`,
`governance.yaml`, or `reading-guides.yaml`. If none exist, tell the user
there is no legacy YAML agent-context to migrate and suggest
`capture-context --init` instead. If at least one exists, tell the user:
"I found YAML agent-context files. Want to migrate to the concern model?"
and wait for confirmation before reading further.

### Step 2 — Read the YAML files

Read every YAML file found in Step 1, plus `reading-guides.yaml` when
present (it carries no source pointers of its own but names the concern
groupings the project already uses).

### Step 3 — Propose concern sections

Map each source file to a concern category:

| Source                | Maps to                                                                                                                                                                                                                                                              |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `governance.yaml`     | Cross-cutting concerns. Match top-level keys to the six factory-default names (Branching, Committing, Testing discipline, Review, Scope discipline, Security) where the meaning overlaps; keys that do not match a default become additional cross-cutting concerns. |
| `workflow.yaml`       | Folds into the matching cross-cutting concern (e.g. a `testing` key strengthens Testing discipline, a `linting` key strengthens Committing) rather than forming its own concerns.                                                                                    |
| `stack.yaml`          | Technical concerns — one per top-level key group (e.g. `frameworks.backend`, `data_stores`).                                                                                                                                                                         |
| `reading-guides.yaml` | Concern names and groupings — a top-level key here (e.g. `backend`, `frontend`, `testing`) informs the technical or cross-cutting concern name it should be filed under, since it already groups related index-file keys together.                                   |

For each field:

- A `{name, source}` mapping → the field's value becomes part of the
  concern's description; `source:` becomes a `Read:` path.
- An inline scalar with no `source:` → the value informs the description;
  use a placeholder `Read:` path following the project's documentation
  convention, same as greenfield Step 3.
- A `{deferred: "reason"}` mapping → carry the deferral forward as a note
  in the concern's description; do not fabricate a `Read:` path for it.

The old YAML model has no domain-concern equivalent — leave the domain
section empty with the same placeholder note as greenfield Step 4, unless
a `reading-guides.yaml` concern name clearly matches an existing scope-map
area.

### Step 4 — Present for review

Show the user the fully assembled `docs/agent-context.md` content — every
category, concern name, description, and `Read:` path — before writing
anything. The user may rename, merge, split, or drop any proposed concern,
same latitude as greenfield Step 3. Do not proceed until the user confirms.

### Step 5 — Write and clean up

On confirmation:

1. Write `docs/agent-context.md` with the confirmed structure.
2. Move `docs/agent-context/testing.yaml` to `docs/testing.yaml` if it
   exists (`testing.yaml` is machine-consumed configuration, not part of
   the concern registry — see
   [Agent Context Composition § `testing.yaml` carve-out](../../rulebooks/conventions/agent-context-composition.md#testingyaml-carve-out)).
3. Delete `stack.yaml`, `workflow.yaml`, `governance.yaml`, and
   `reading-guides.yaml`.
4. Remove the now-empty `docs/agent-context/` directory.

### Step 6 — Validate

Run `factory/scripts/concern-lint` — confirms `docs/agent-context.md` has
the required structure and that no legacy YAML residue remains
(`CTX-LEGACY`). Fix any finding before proceeding.

### Step 7 — Commit

```
docs: migrate agent context from YAML to concern model
```

**Completion**: `docs/agent-context.md` exists with the migrated concern
sections; `docs/testing.yaml` exists if a `testing.yaml` was present;
`docs/agent-context/` no longer exists; `concern-lint` reports zero errors.

## Validation reference

| Script                         | Checks                                                                                     |
| ------------------------------ | ------------------------------------------------------------------------------------------ |
| `factory/scripts/concern-lint` | section structure (CTX-SECTIONS), path resolution (CTX-PATHS), legacy residue (CTX-LEGACY) |

`validate` runs `concern-lint` automatically once `docs/agent-context.md`
exists — invoking it here is a courtesy check during the interactive
session, not a replacement for that gate.
