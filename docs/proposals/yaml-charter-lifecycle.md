---
schema_version: 2
title: "Agent Context: Two-Layer Routing with Two-Mode Lifecycle"
status: accepted
owner: md@matthiasdaues.de
created: 2026-09-02
updated: 2026-09-03
supersedes:

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - docs/spec/supplementary_specs/interface-contracts.md
    - docs/spec/supplementary_specs/entity-model.md

governance:
  assurance: high
  risk_domains:
    - compatibility
    - reliability

estimate:
  as_of: 2026-09-04
  basis: story-level decomposition (11 stories across 5 EPICs)
  confidence: medium
  human_review_hours:
    min: 3.0
    max: 6.0
  normalized_tokens:
    min: 20000
    max: 45000
  estimated_consumption:
    min: 300000
    max: 900000
    overhead_multiplier: 20
    playbook: feature-addition
---

# Feature Request: Agent Context

## Summary

Replace `docs/charter/` with `docs/agent-context/` — a two-layer, YAML-based routing interface
between factory agents and project knowledge. Layer 1 (`reading-guides.yaml`) routes by work-type
concern to sections in Layer 2 index files (`stack.yaml`, `workflow.yaml`, `governance.yaml`).
Index files carry `source:` pointers to authoritative project documents. A two-mode lifecycle lets
greenfield projects write values directly (`mode: primary`) and mature projects maintain a pure
link index (`mode: index`).

## Motivation

The project charter (`docs/charter/`) was designed as the interface contract between the factory's
agents and a project's self-determined practices. Gigacron discovered that this model breaks when
a project's documentation matures: the charter becomes a stale second source of truth, duplicating
decisions already captured in a developer handbook, ADRs, and convention files.

The previous iteration of this proposal (2026-09-02) solved the staleness problem by converting
charter files to YAML indexes with `source:` pointers. But it left a second problem unresolved:
the charter indexes (keyed by decision domain — stack, workflow, governance) and Gigacron's
`agent-context.md` (keyed by work type — backend, frontend, testing) both route to the same
handbook documents along different axes. Maintaining two independent routing tables over one
document tree creates two places to drift.

This revision resolves both problems by replacing the charter with a unified **agent context** —
the factory-facing interface to all project knowledge, organized in two layers.

## Core Principles

- **Agent context is always derived content.** In steady state it links to sources; it is never the
  primary authority. The single exception is `mode: primary` during greenfield, before source
  documents exist.
- **Sources maintained in exactly one place.** Only the three index files carry `source:` pointers.
  The reading guide references index sections, never source documents directly.
- **Always consumed whole.** An agent reads all four files. The reading guide is a relevance filter
  for the current concern, not a file selector.
- **One routing table, two access patterns.** Layer 1 answers "what should I read for this kind of
  work?" Layer 2 answers "what was decided about this topic, and where is it documented?"

## Design

### Two-layer architecture

```
docs/agent-context/
  reading-guides.yaml   ← Layer 1: concern-based routing to index sections
  stack.yaml            ← Layer 2: what's it built with
  workflow.yaml         ← Layer 2: how to build, test, deploy
  governance.yaml       ← Layer 2: what rules apply
  testing.yaml          ← Peer file: machine-readable test config (no lifecycle)
```

#### Layer 1 — Reading guides

`reading-guides.yaml` is the entry point. It routes by **concern** (the kind of change the agent
is about to make) to sections in the Layer 2 index files. It contains **no `source:` pointers** —
only references to index-file sections using key-path notation.

The reading guide is inherently derived content. It only exists when project documentation exists.
Greenfield projects (pre-Epic 0) have the three index files only. The reading guide appears when
the handbook does, typically during or after Epic 0.

#### Layer 2 — Index files

Three YAML files, each covering a distinct domain of project knowledge. They carry `source:`
pointers to authoritative project documents. In steady state they hold names and links only — no
summaries, no duplicated values. These files participate in the two-mode lifecycle.

#### Peer file — `testing.yaml`

`testing.yaml` is a machine-readable test configuration file that lives in `docs/agent-context/`
as a peer, not as an index file. It does **not** participate in the two-mode lifecycle:

- It is always code-derived, written by `detect-test-regime`, not by `update-context`.
- It is consumed directly by scripts (`crap-score`), hooks (`block-dangerous-git.sh`), and FSMs
  (`bug-fix.fsm.yml`, `greenfield-development.fsm.yml`) as structured config with fields like
  `test_command`, `suites`, `gates`, `risk_classes`.
- The `MUST NOT hand-edit` rule does not apply — `detect-test-regime` hand-writes it by design.
- `context-lint` validates it separately: schema check and `CX-PARSE` only, no `CX-SRC` or `CX-MODE`
  checks.

#### Reference syntax for reading-guide entries

Reading-guide entries use **key-path notation**: `<file>#<dotted.key.path>`.

Grammar:

```
reference     = file [ "#" key_path ]
file          = yaml_filename                    # e.g. "stack.yaml"
key_path      = segment ( "." segment )*         # e.g. "frameworks.backend"
segment       = yaml_key                         # top-level or nested YAML key name
```

Resolution rules:

- A bare file reference (`stack.yaml`) means "the entire file is relevant."
- A dotted path (`stack.yaml#frameworks.backend`) resolves to the YAML key at that nesting depth.
- Array-typed keys are referenced by their parent key (`stack.yaml#languages` means the entire
  languages list), not by index.
- `context-lint` validates `CX-GUIDE-REF` by parsing each reference, loading the named file, and
  confirming the key path exists in its YAML structure.

### Two-mode lifecycle

The index files have two modes, signalled by a top-level `mode` field. The reading guide and
`testing.yaml` do not participate.

#### Mode 1 — Primary source (`mode: primary`)

Active during greenfield setup, before Epic 0 delivers code and conventions. The index files are
the *upstream* source of project decisions. The stakeholder interview fills values directly. There
are no `source:` pointers because no handbook or conventions exist yet.

**Direction of truth:** Stakeholder → index YAML → code and conventions (produced by Epic 0).

**Typical timeline:** From `capture-context --init` until the end of Epic 0.

#### Mode 2 — Downstream index (`mode: index`)

Active after Epic 0, once conventions and a handbook exist. Each index file becomes a pure
**routing table** — every field holds a name (for lookup) and a `source:` pointer (for reading the
authoritative content). No summaries, no compressed values.

**Direction of truth:** Handbook, ADRs, code → index YAML (refreshed by `update-context`).

**Transition condition** (single, testable): every non-null leaf field across all three index files
has a `source:` pointer. `context-lint` verifies this mechanically via `CX-SRC`.

**Handling deferrals and not-applicable fields:** Fields that are genuinely not applicable to the
project (e.g. `data_stores` for a project with no persistence) stay `null`. They are excluded from
the transition condition — `null` fields need no `source:` pointer. Fields with pending decisions
use a `deferred:` mapping: `deferred: "reason"`. Deferred fields are also excluded from the
transition condition. They are not a lint finding — a deferral is a conscious decision, and the
transition condition already makes them visible by preventing mode advancement.

**Transition procedure:**

1. `update-context` is the sole owner. After writing a `source:` pointer, it checks whether every
   non-null, non-deferred leaf field across all three index files now has a `source:` pointer.
2. If yes, it prompts: *"All context fields now have sources. Switch to index mode?"*
3. User confirms → `update-context` flips `mode` to `index` in all three files atomically (single
   commit). The transition strips inline values to names only and preserves `source:` pointers.
4. `capture-context --init --scan` (brownfield) can also trigger the transition if its scan
   achieves full coverage.

#### Why two modes matter

Without two modes, greenfield projects have no primary source to capture decisions before code
exists. Without the transition, mature projects accumulate stale context that contradicts the
handbook. The two-mode lifecycle solves both: the context starts as a notepad and matures into an
index.

### Concern-based brownfield onboarding

When VIRGIL onboards a brownfield project (`capture-context --init --scan`), the flow is driven by
concerns rather than by file. VIRGIL walks the project's existing documentation and populates the
agent context concern by concern, building both the indexes and the reading guide together.

#### Onboarding procedure

**Phase 1 — Discovery.** VIRGIL scans the project for documentation signals:

| Signal                                                        | What it reveals                 |
| ------------------------------------------------------------- | ------------------------------- |
| `pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`      | Languages, frameworks, versions |
| `docker-compose.yml`, `Dockerfile`, `terraform/`, `k8s/`      | Infrastructure                  |
| `.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml`         | CI/CD                           |
| `pytest.ini`, `jest.config.*`, `vitest.config.*`              | Test framework                  |
| `.ruff.toml`, `.eslintrc.*`, `biome.json`                     | Linting                         |
| `docs/`, `docs/handbook/`, `docs/adr/`                        | Documentation structure         |
| `CONTRIBUTING.md`, `docs/conventions/`, `docs/house-rules.md` | Governance                      |
| Existing `docs/agent-context.md` or `docs/charter/`           | Prior agent context or charter  |

**Phase 2 — Concern interview.** For each concern in the reading-guide template (backend, frontend,
testing, architecture, packaging, and any the project adds), VIRGIL asks:

1. *"Does this project have [concern] work?"* — Skip concerns that don't apply.
2. *"Where are the conventions for [concern] documented?"* — VIRGIL proposes paths based on the
   discovery scan; the user confirms or corrects.
3. *"Are there cookbooks, guides, or concept docs for [concern]?"* — These go into the index file
   as additional `source:` entries under the appropriate domain key.

For each confirmed doc, VIRGIL populates the relevant index-file field with a `source:` pointer and
adds the index-section reference to `reading-guides.yaml`.

**Phase 3 — Index completion.** VIRGIL walks any remaining `null` fields in the three index files
that the concern interview did not cover (e.g. licensing, exclusions). For each:

- If a source file was found in the scan, propose the `source:` pointer.
- If not, ask the user. Record the answer as a direct value (`mode: primary`) or a source pointer.
- Not-applicable fields stay `null`. Pending decisions record `deferred: "reason"`.

**Phase 4 — Mode determination.** If every non-null, non-deferred leaf field across all three index
files now has a `source:` pointer, propose `mode: index` immediately. If partial coverage remains,
set `mode: primary` — remaining fields transition organically via `update-context`.

**Phase 5 — Reading-guide assembly.** VIRGIL writes `reading-guides.yaml` from the concern
interview results. Each concern key lists the index-file sections that surfaced during that
concern's interview. Concerns with no applicable docs are omitted.

#### Greenfield variant

For greenfield projects (`capture-context --init`, no `--scan`):

1. Copy the three index-file templates with `mode: primary` and `null` values.
2. Do **not** create `reading-guides.yaml` — there is no handbook to route to yet.
3. The stakeholder interview fills index-file values directly.
4. `reading-guides.yaml` is created later: `update-context` detects when the first `source:`
   pointer is written and no reading guide exists, and proposes creating one from the template.
   Full assembly happens when enough sources accumulate or when the user invokes the brownfield
   scan after Epic 0.

## Scope

**In the first release:**

- Four YAML templates for `docs/agent-context/` (three index files + reading guide)
- `capture-context` skill (rename from `capture-charter`, YAML support, concern-based brownfield
  onboarding, format detection for markdown backward compatibility)
- `update-context` skill (rename from `update-charter`, YAML support, mode transition, reading-
  guide creation trigger)
- `context-lint` script (rename from `charter-lint`, `CX-` finding codes, YAML validation,
  `CX-GUIDE-REF` key-path validation, `testing.yaml` carve-out)
- `agent-context-composition.md` convention and `rules.md` entry
- Path updates in all factory consumers (agents, skills, playbooks, scripts, hooks, templates,
  INDEX.yaml, README, factory-guide)
- Migration support: format detection handles both `docs/charter/` and `docs/agent-context/`
  locations, in YAML or markdown

**Explicitly deferred (do NOT plan stories for these):**

- Automated migration tool (`docs/charter/` → `docs/agent-context/` rename + file transform)
- Spec, arc42, and ADR document updates (reconciliation pass after implementation)
- Backlog story path updates (bulk find-replace, separate chore)
- SVG diagram regeneration
- Gigacron pilot migration (done by Gigacron project, not factory)

## Design Details

### Why YAML instead of markdown

- Agents parse fields by key, not by heading regex.
- Placeholder detection is mechanical (`null` vs. a value) instead of string matching.
- Per-field `source:` pointers are natural in YAML, awkward in markdown.
- No temptation to write prose where a structured value belongs.
- In mode 2, the index carries only names and links — no values that can drift.
- Consistent with `testing.yaml`, which already uses this pattern successfully.
- The reading guide's section references (`stack.yaml#frameworks.backend`) are natural YAML lists.

### Schema: the four agent-context files

#### `reading-guides.yaml`

Routes by concern to index-file sections. No `source:` pointers. No `mode` field.

```yaml
backend:
  - stack.yaml#frameworks.backend
  - workflow.yaml#testing
  - workflow.yaml#linting
  - governance.yaml#review

frontend:
  - stack.yaml#frameworks.frontend
  - workflow.yaml#testing
  - governance.yaml#review

testing:
  - workflow.yaml#testing
  - governance.yaml#testing_discipline

architecture:
  - stack.yaml
  - governance.yaml#architecture_governance

packaging:
  - stack.yaml#frameworks
  - workflow.yaml#ci_cd
  - governance.yaml#scope
```

A project extends this with its own concerns. A project with no frontend deletes the `frontend:`
key. A project with a data pipeline adds a `pipeline:` key.

#### `stack.yaml`

```yaml
mode: primary

languages:
  - name: null
    version: null
    role: null
    source: null

frameworks:
  backend: null
  frontend: null
  testing: null

data_stores: null
infrastructure: null
existing_systems: null

licensing:
  project: null
  constraints: null

exclusions: null
```

#### `workflow.yaml`

```yaml
mode: primary

repository_layout: null
getting_started: null
running: null
testing: null
linting: null
ci_cd: null
branching: null
```

#### `governance.yaml`

```yaml
mode: primary

commits: null
review: null
testing_discipline: null
architecture_governance: null
scope: null
```

### Design principle: index, not summary

In mode 2, index files carry **names and links only**. No version strings, no role descriptions,
no compressed summaries. A summary drifts the moment the source changes. A link does not.

In mode 1 (greenfield), values are written directly because no source document exists yet. The
transition to mode 2 strips those values to names and replaces them with `source:` pointers.

### Populated examples (mode: index)

`stack.yaml`:

```yaml
mode: index

languages:
  - name: Python
    source: packages/server/pyproject.toml
  - name: TypeScript
    source: packages/server/package.json

frameworks:
  backend:
    name: FastAPI
    source: docs/adr/004-use-fastapi-for-http-and-websocket-apis.md
  frontend:
    name: React
    source: docs/adr/009-frontend-skeleton-and-state-boundaries.md
  testing:
    name: pytest
    source: docs/agent-context/testing.yaml

data_stores:
  name: PostgreSQL
  source: docs/adr/005-use-postgresql-for-persistence.md

infrastructure:
  source: docs/handbook/infrastructure/conventions.md

existing_systems: null

licensing:
  project:
    name: MIT
    source: LICENSE
  constraints: null

exclusions: null
```

`workflow.yaml`:

```yaml
mode: index

repository_layout:
  source: docs/handbook/getting-started/repo-layout.md

getting_started:
  source: docs/handbook/getting-started/dev-environment.md

running:
  source: docs/handbook/getting-started/dev-environment.md

testing:
  source: docs/agent-context/testing.yaml

linting:
  source: docs/handbook/backend/conventions.md

ci_cd:
  source: docs/handbook/infrastructure/ci.md

branching:
  source: docs/handbook/conventions/branching.md
```

`governance.yaml`:

```yaml
mode: index

commits:
  source: docs/handbook/conventions/commits.md

review:
  source: docs/handbook/conventions/review.md

testing_discipline:
  source: docs/handbook/testing/conventions.md

architecture_governance:
  source: docs/handbook/decisions/index.md

scope:
  source: docs/handbook/conventions/scope.md
```

### Naming overlap with arc42 CONTEXT.md

A project may have both `docs/arc42/CONTEXT.md` (domain vocabulary, bounded contexts) and
`docs/agent-context/` (factory-facing project knowledge interface). The `agent-` prefix
disambiguates. `docs/arc42/CONTEXT.md` is domain modelling; `docs/agent-context/` is agent
routing. The two serve different audiences and neither references the other.

### Format detection and backward compatibility

Format detection logic, shared across all consumers:

1. If `docs/agent-context/stack.yaml` exists → YAML agent-context mode.
2. Else if `docs/charter/tech-stack.yaml` exists → legacy YAML charter mode (path migration
   needed).
3. Else if `docs/charter/tech-stack.md` exists → legacy markdown charter mode.
4. If files exist in more than one location → `CX-FORMAT` error.

`testing.yaml` is always YAML regardless of the charter format. A project with markdown charter
files plus `docs/charter/testing.yaml` is legal (this is the current state). Format detection
treats `testing.yaml` independently — it does not trigger the "mixed formats" error.

### Convention: agent-context composition

**Location:** `factory/rulebooks/conventions/agent-context-composition.md`

**Binding rules:**

- `docs/agent-context/` is the factory-facing interface to all project knowledge.
- Content is always derived — the agent context links to sources, it is never the primary authority
  in steady state.
- `mode: primary` means the index files are the primary source (greenfield, pre-Epic 0).
- `mode: index` means the index files are downstream routing tables.
- The reading guide routes by concern to index-file sections. It carries no `source:` pointers.
- Direction of truth flows from source documents to index files, never the reverse.
- `update-context` is the only write path for index files when `mode: index`. Hand-editing is
  forbidden. `testing.yaml` is exempt — `detect-test-regime` writes it directly.
- A project uses one context format (agent-context YAML or legacy markdown charter), not both.
- `source:` pointers prefer project-local conventions over factory rulebook defaults.

**Entry in `factory/rulebooks/rules.md`:**

```markdown
## Agent context composition

→ [agent-context-composition.md](conventions/agent-context-composition.md)

- **MUST** populate `docs/agent-context/` as the factory-facing interface to project knowledge.
- **MUST** set `mode: primary` when the index files are the primary source of decisions.
- **MUST** set `mode: index` when the index files are projections of existing documentation.
- **MUST** include a `source:` pointer on every non-null, non-deferred leaf field when
  `mode: index`.
- **MUST NOT** hand-edit an index file that carries `mode: index` (use `update-context`).
- **MUST NOT** write upstream — `update-context` writes only to `docs/agent-context/*.yaml`,
  never to source documents.
- **MUST NOT** place `source:` pointers in `reading-guides.yaml`.
- **MUST NOT** mix YAML agent-context and markdown charter formats in one project.
- **MUST** point `source:` at the project-local convention when it exists, not at the factory
  rulebook default it overrides.
```

This replaces the existing Coding section rule "MUST derive Epic 0 from the charter" with "MUST
derive Epic 0 from the agent context" (or equivalent wording).

## Affected factory consumers — complete inventory

Derived from `rg 'docs/charter'` across the factory tree. Grouped by change type.

### Rename + full rewrite

| Artifact                | Current path                              | New path                                  | Notes                                                                |
| ----------------------- | ----------------------------------------- | ----------------------------------------- | -------------------------------------------------------------------- |
| `capture-charter` skill | `factory/skills/capture-charter/SKILL.md` | `factory/skills/capture-context/SKILL.md` | YAML support, concern-based brownfield, format detection             |
| `update-charter` skill  | `factory/skills/update-charter/SKILL.md`  | `factory/skills/update-context/SKILL.md`  | YAML support, mode transition, reading-guide creation                |
| `charter-lint` script   | `factory/scripts/charter-lint`            | `factory/scripts/context-lint`            | `CX-` codes, YAML validation, `CX-GUIDE-REF`, testing.yaml carve-out |

### Path update + format detection

These read charter files and need both path updates and format-detection logic to handle YAML vs.
markdown:

| Artifact                                             | Change                                                                        |
| ---------------------------------------------------- | ----------------------------------------------------------------------------- |
| `factory/agents/virgil.md`                           | `inputs:`, `skills:`, `outputs:`, `triggers:`, `description`, body references |
| `factory/agents/developer-agent.md`                  | `inputs:`, body references                                                    |
| `factory/agents/implementation-agent.md`             | `inputs:`, body references                                                    |
| `factory/agents/planning-agent.md`                   | `inputs:`, body references                                                    |
| `factory/agents/architecture-agent.md`               | `skills:` frontmatter (`update-charter` → `update-context`)                   |
| `factory/agents/requirements-agent.md`               | `skills:` frontmatter (`update-charter` → `update-context`)                   |
| `factory/playbooks/feature-addition.md`              | Charter update steps                                                          |
| `factory/playbooks/greenfield-development.md`        | Charter as expected output                                                    |
| `factory/playbooks/greenfield-development.fsm.yml`   | `testing.yaml` path                                                           |
| `factory/playbooks/brownfield-onboarding.md`         | Charter onboarding step                                                       |
| `factory/playbooks/bug-fix.fsm.yml`                  | `testing.yaml` path                                                           |
| `factory/skills/create-backlog-epics/SKILL.md`       | Reads charter for Epic 0                                                      |
| `factory/skills/create-backlog/SKILL.md`             | References charter                                                            |
| `factory/skills/create-backlog-stories/SKILL.md`     | Reads `testing.yaml`                                                          |
| `factory/skills/create-backlog-write-epics/SKILL.md` | References charter for Epic 0                                                 |
| `factory/skills/implement-issue/SKILL.md`            | Reads `testing.yaml`                                                          |
| `factory/skills/crap-score/SKILL.md`                 | Reads `testing.yaml`                                                          |
| `factory/skills/test-design/SKILL.md`                | Reads `testing.yaml`                                                          |
| `factory/skills/qa-strategy-from-spec/SKILL.md`      | Reads charter/testing                                                         |
| `factory/skills/process-transcript/SKILL.md`         | References charter                                                            |
| `factory/skills/newcomer-tour/SKILL.md`              | References charter                                                            |
| `factory/skills/validate/SKILL.md`                   | Runs `charter-lint` → `context-lint`                                          |
| `factory/skills/detect-test-regime/SKILL.md`         | Writes `testing.yaml` path                                                    |

### Path update only (no format detection needed)

These reference charter paths in strings, commands, or config — simple find-replace:

| Artifact                                            | Change                                        |
| --------------------------------------------------- | --------------------------------------------- |
| `factory/scripts/init-factory`                      | Creates `testing.yaml` at new path            |
| `factory/scripts/crap-score`                        | Walks tree for `testing.yaml`                 |
| `factory/scripts/phase`                             | Charter path reference                        |
| `factory/scripts/premerge-check`                    | Charter path reference                        |
| `factory/config/hooks/block-dangerous-git.sh`       | `testing.yaml` path                           |
| `factory/config/extensions/block-dangerous-git.ts`  | `testing.yaml` path                           |
| `.pre-commit-config.yaml`                           | `charter-lint` → `context-lint` hook id       |
| `factory/rulebooks/rules.md`                        | "charter" → "agent context" in existing rules |
| `factory/rulebooks/conventions/testing-strategy.md` | `docs/charter/testing.yaml` path              |
| `factory/rulebooks/templates/story.md`              | Charter file references                       |
| `factory/INDEX.yaml`                                | Skill descriptions mentioning charter         |
| `factory/README.md`                                 | Charter references                            |
| `factory/docs/factory-guide.md`                     | Charter references                            |

### New files

| Artifact                                                     | Notes                             |
| ------------------------------------------------------------ | --------------------------------- |
| `factory/rulebooks/templates/context-stack.yaml`             | Template with `null` placeholders |
| `factory/rulebooks/templates/context-workflow.yaml`          | Template with `null` placeholders |
| `factory/rulebooks/templates/context-governance.yaml`        | Template with `null` placeholders |
| `factory/rulebooks/templates/context-reading-guides.yaml`    | Template with common concerns     |
| `factory/rulebooks/conventions/agent-context-composition.md` | Binding rules                     |

### Retained for legacy backward compatibility

| Artifact                                             | Notes                                                                                                                                             |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `factory/rulebooks/templates/charter-tech-stack.md`  | Markdown charter template — kept for legacy projects                                                                                              |
| `factory/rulebooks/templates/charter-development.md` | Markdown charter template — kept for legacy projects                                                                                              |
| `factory/rulebooks/templates/charter-house-rules.md` | Markdown charter template — kept for legacy projects                                                                                              |
| `factory/rulebooks/templates/charter-testing.yaml`   | Testing template — path referenced by `init-factory`; retained as-is, `init-factory` copies to `docs/agent-context/testing.yaml` for new projects |

### `context-lint` validation codes

| Code           | Severity                            | Check                                                                                                                                 |
| -------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `CX-FILE`      | error                               | Each required file exists (`reading-guides.yaml` required only when `mode: index` in any index file, or when the file already exists) |
| `CX-PARSE`     | error                               | Each file parses as valid YAML                                                                                                        |
| `CX-KEYS`      | error                               | Required top-level keys present per template schema                                                                                   |
| `CX-NULL`      | warning / error (`--planning-gate`) | `null` values in `stack.yaml` and `workflow.yaml`                                                                                     |
| `CX-MODE`      | info                                | `mode` field is `primary` or `index`                                                                                                  |
| `CX-SRC`       | warning                             | When `mode: index`, every non-null, non-deferred leaf has `source:`                                                                   |
| `CX-SRC-EXIST` | warning                             | Each `source:` pointer resolves to an existing file                                                                                   |
| `CX-SRC-STALE` | info                                | Source file modified more recently than index file                                                                                    |
| `CX-GUIDE-REF` | warning                             | Each reading-guide reference resolves to an existing index-file key                                                                   |
| `CX-FORMAT`    | error                               | Mixed YAML/markdown or mixed charter/agent-context locations                                                                          |

## Open Questions

All resolved.

- ~~**Reading-guide extensibility.**~~ Resolved: projects add concerns as plain top-level keys.
  The key name is the anchor — a well-named concept (`pipeline:`, `ml:`, `data_quality:`) is
  enough for an LLM to match it to the task at hand. No meta-key namespace or collision-prevention
  machinery needed.
- ~~**Mode transition atomicity.**~~ Resolved: all three files advance together. The transition
  condition requires coverage across all three index files, and the transition procedure specifies
  an atomic single-commit flip. Per-file partial transitions are not supported.
- ~~**Deferred field expiry.**~~ Resolved: no lint finding at all. A deferral is a conscious
  decision, not a defect. The mode-transition condition already prevents advancing while deferrals
  remain — that is sufficient pressure. No `CX-DEFERRED` code.

## Completion Criteria

- `docs/agent-context/` with four YAML files is the documented, tested, and lint-validated
  interface for new projects.
- `capture-context --init` creates the three index-file templates for greenfield projects.
- `capture-context --init --scan` runs the concern-based brownfield onboarding and populates all
  four files.
- `update-context` writes index fields, manages `source:` pointers, triggers mode transition,
  and proposes reading-guide creation when it does not exist.
- `context-lint` validates all four files with the `CX-` finding codes, including `CX-GUIDE-REF`
  key-path resolution and the `testing.yaml` carve-out.
- `agent-context-composition.md` convention exists and `rules.md` carries the corresponding
  MUST/MUST NOT entries.
- All factory consumers listed in the inventory above have updated paths and, where needed, format
  detection.
- Legacy markdown charter projects continue to work without changes (format detection falls back).
- `testing.yaml` is explicitly excluded from the two-mode lifecycle in documentation and lint.

## Guiding Rule

The agent context is a routing table, not a knowledge base — it tells agents where to look, never
what they will find.

## Reference: Gigacron

Gigacron has these files today, which map to the new structure:

| Gigacron current                | New location                                    |
| ------------------------------- | ----------------------------------------------- |
| `docs/charter/tech-stack.yaml`  | `docs/agent-context/stack.yaml`                 |
| `docs/charter/development.yaml` | `docs/agent-context/workflow.yaml`              |
| `docs/charter/house-rules.yaml` | `docs/agent-context/governance.yaml`            |
| `docs/charter/testing.yaml`     | `docs/agent-context/testing.yaml`               |
| `docs/agent-context.md`         | `docs/agent-context/reading-guides.yaml`        |
| `docs/charter/COMPOSITION.md`   | Project-side reference for the composition rule |

## Migration path

1. **No breaking change.** Projects using markdown charters under `docs/charter/` continue to work.
   Format detection checks both locations.
2. **New projects default to YAML agent-context** when `capture-context --init` runs.
3. **Existing YAML charter projects** (e.g. Gigacron) migrate by renaming `docs/charter/` to
   `docs/agent-context/` and renaming files per the table above. `capture-context --init --scan`
   can do this automatically when it finds the old layout.
4. **Existing markdown charter projects** migrate by running `capture-context --init --scan` after
   removing the markdown charter files.
5. **Gigacron is the pilot.** Their existing YAML charter files and `agent-context.md` merge into
   the new structure.

## Testing the changes

**In-repo test fixtures.** Create `factory/tests/fixtures/agent-context/` with synthetic files
covering both modes, all four file types, and the `testing.yaml` peer.

- `context-lint` on fixtures passes in default and `--planning-gate` modes.
- `context-lint` validates `CX-GUIDE-REF` references against index-file keys.
- `context-lint` on `testing.yaml` applies `CX-PARSE` only, not `CX-SRC` or `CX-MODE`.
- `context-lint` on a project with markdown charter files continues to pass unchanged.
- `context-lint` on a project with mixed formats reports `CX-FORMAT` error.
- `context-lint` on `mode: index` fixtures with missing `source:` pointers reports `CX-SRC`.
- `context-lint` does not flag deferred fields (deferrals are conscious decisions, not defects).
- `capture-context --init` in an empty project creates three index-file templates (no reading
  guide).
- `capture-context --init --scan` in a brownfield project populates index files and generates
  `reading-guides.yaml` via concern-based interview.
- `update-context` preserves `source:` pointers and validates source file existence.
- `update-context` proposes reading-guide creation when first `source:` pointer is written and no
  reading guide exists.
- `update-context` triggers mode transition when all non-null, non-deferred fields have sources.
- Markdown charter backward compatibility: format detection falls back correctly.
- `testing.yaml` in a markdown-charter project does not trigger `CX-FORMAT`.

## Stakeholder Grilling Results (2026-09-05)

Grilling session for ST-0199, conducted in conversation with the project stakeholder. The
decisions below refine or override the design described in earlier sections of this proposal. Where
a conflict exists, this section governs.

### 1. Stable endpoint, flexible interior

The agent context is a routing switchboard with a stable interface. The top-level key structure
(stack, workflow, governance, and concern names in the reading guide) is a slowly-changing dimension
owned by the factory. Everything below the top-level keys is project-specific, created by VIRGIL
during the interview, and owned by the project operator. The operator may add, rename, or remove
second-level keys at any time.

### 2. Mode concept eliminated

The `mode` field (`primary` / `index`) and all associated machinery are removed:

- No `mode:` field in index files.
- No transition condition, transition procedure, or atomic flip.
- No `CX-MODE` or `CX-MODE-INVALID` lint codes.
- No `CX-SRC` as a mode-gated coverage check.

Each field is self-describing. `name:` is always a display label for humans scanning the YAML.
`source:` is always the authority — either inline prose (the value itself, when no external
document exists) or a file path to the authoritative document. `context-lint` determines which:
`CX-SRC-EXIST` tries to resolve `source:` as a local file path; if it resolves, the source is a
pointer and the link is validated; if it does not resolve, the source is inline prose and no
finding is raised. URLs, verbal references, and other non-file-path values are the operator's
responsibility — the lint checks what it can and does not perform theater on what it cannot.

### 3. Two field states only

A key in an index file has exactly two valid states:

| State    | Shape                | Meaning                                   |
| -------- | -------------------- | ----------------------------------------- |
| Valued   | `name:` + `source:`  | Decision recorded                         |
| Deferred | `deferred: "reason"` | Applies to this project, decision pending |

Key absence means the concept does not apply to this project. VIRGIL creates only keys the
operator confirms as relevant during the interview. There is no `null` state — a `null` value in
any index file is an error (`CX-NULL`), always, in every lint mode. `null` indicates that VIRGIL
created a key without recording an answer, which is a defect in the interview flow.

`deferred:` must be the sole key at that field — it must not coexist with `name:` or `source:`.
Deferred fields pass the planning gate. They are conscious decisions with a recorded reason, not
unresolved placeholders.

### 4. No governance leniency

All three index files receive the same lint treatment at `--planning-gate`. The original design
gave `governance.yaml` special leniency (allowing `null` past the planning gate). This exception
is removed. The `deferred:` mechanism handles pending governance decisions — the operator records
the reason, and the planning gate accepts it. No file-level behavioral differences in the linter.

### 5. Templates and interview guide separated

Templates serve one purpose: file skeletons with top-level keys only. They do not carry
second-level keys with `null` placeholders, and they do not structure the interview.

A separate interview guide (`factory/rulebooks/templates/context-interview-guide.yaml`) structures
VIRGIL's conversation: what to ask, in what order, and what the answers map to. VIRGIL reads the
guide, asks the questions, and creates only the keys the operator confirms. This eliminates the
double-duty problem where templates were both file skeleton and interview script.

### 6. Concern-by-concern interview, no bulk

VIRGIL presents scan results and interview questions concern by concern. There is no bulk-confirm
option. The deliberation at each concern is the point — it forces the operator to consider each
piece of project knowledge individually. Rubber-stamping a bulk dump risks wrong source pointers
that go undetected for months.

### 7. Functional framing

The guidance uses functional language: "VIRGIL sets up your agent context." No extra role concepts
(such as "kit manager"). The action explains itself. The stakeholder does not need to learn a
named role to understand what is happening.

### 8. Reading guide maintained through project life

The reading guide is the index of project knowledge, not a one-time creation artifact.
`update-context` maintains it: when a key is added or a source pointer changes, `update-context`
asks the operator which concern the key belongs to ("Which concern does this belong to? Here are
your current concerns: [list]. Pick one, or name a new one.") and updates the reading guide
immediately. One question per change, asked in the moment when the operator has context.

### 9. Skills discover structure through the reading guide

Skills MUST NOT hardcode second-level field paths (such as `stack.yaml#frameworks.backend`). They
read the reading guide to discover which index-file sections are relevant to their concern, then
read those sections and find the facts they need by inspecting what is there. This costs a few
more tokens per skill invocation but keeps skills decoupled from project-specific key structures.

### 10. Reconciliation surfaces new suggested keys

When the factory adds new suggested keys in a future version, existing projects do not have those
keys. The reconciliation agent, during its regular passes, compares the project's agent context
against the factory's current interview guide and surfaces new suggested keys to the operator.
This prevents amnesia — concepts the operator rejected are re-examined when the factory evolves,
and the operator can confirm or dismiss them.

### Revised `context-lint` codes

| Code           | Severity | Check                                                                                                                             |
| -------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `CX-FILE`      | error    | Each required file exists (reading-guides.yaml required when any index file has source pointers, or when the file already exists) |
| `CX-PARSE`     | error    | Each file parses as valid YAML                                                                                                    |
| `CX-KEYS`      | error    | Required top-level keys present per template schema; `deferred:` does not coexist with `name:` or `source:`                       |
| `CX-NULL`      | error    | Any `null` value in any index file, in any lint mode                                                                              |
| `CX-SRC-EXIST` | warning  | Each `source:` value that resolves as a local path points to an existing file                                                     |
| `CX-SRC-STALE` | info     | Source file modified more recently than index file                                                                                |
| `CX-GUIDE-REF` | warning  | Each reading-guide reference resolves to an existing index-file key                                                               |
| `CX-FORMAT`    | error    | Mixed YAML/markdown or mixed charter/agent-context locations                                                                      |

Removed codes: `CX-MODE`, `CX-MODE-INVALID`, `CX-SRC` (mode-gated coverage check).

### Impact on merged implementation

The nine stories merged into `feature/agent-context` (ST-0190 through ST-0198) contain mode
logic throughout `context-lint`, `capture-context`, `update-context`, index-file templates, and
the `agent-context-composition` convention. The decisions in this section require rework:

- Strip `mode:` field and mode-branching from all artifacts.
- Replace `null`-placeholder templates with top-level-only skeletons.
- Create the interview guide as a separate artifact.
- Rewrite `update-context` to maintain the reading guide on every key/source change.
- Rewrite skills to discover structure through the reading guide.
- Update `context-lint` to remove mode codes and make `CX-NULL` an unconditional error.
- Update the reconciliation agent to surface new suggested keys.

These changes should be planned as follow-up stories after ST-0200.
