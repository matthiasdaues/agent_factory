---
schema_version: 2
title: Concern-Oriented Agent Context
status: accepted
owner: Matthias Daues
created: 2026-09-08
updated: 2026-09-09
supersedes: docs/proposals/yaml-charter-lifecycle.md

impact:
  scope: cross_project
  architecture_change: true
  external_contract_change: true
  boundaries:
    # Rulebooks and templates
    - factory/rulebooks/conventions/agent-context-composition.md
    - factory/rulebooks/templates/context-*.yaml
    # Skills
    - factory/skills/capture-context/SKILL.md
    - factory/skills/update-context/SKILL.md
    - factory/skills/detect-test-regime/SKILL.md
    - factory/skills/validate/SKILL.md
    # Scripts and gates
    - factory/scripts/context-lint
    - factory/scripts/validate
    - factory/scripts/init-factory
    - factory/scripts/crap-score
    # Agent definitions
    - factory/agents/planning-agent.md
    - factory/agents/implementation-agent.md
    - factory/agents/developer-agent.md
    - factory/agents/virgil.md
    - factory/agents/reconciliation-agent.md
    - factory/agents/requirements-agent.md
    - factory/agents/architecture-agent.md
    - factory/agents/architecture-review-agent.md
    - factory/agents/qa-agent.md
    - factory/agents/spec-review-agent.md
    # Config
    - factory/config/AGENTS.md
    # Any additional skill or agent definition carrying project-native
    # paths (docs/handbook/, docs/spec/supplementary_specs/, docs/adr/)
    # discovered during implementation planning.

governance:
  assurance: elevated
  risk_domains:
    - compatibility
    - operations

estimate:
  as_of: 2026-09-08
  basis: decomposition
  confidence: medium
  human_review_hours:
    min: 1.5
    max: 3.0
  normalized_tokens:
    min: 12000
    max: 20000
  estimated_consumption:
    min: 180000
    max: 500000
    overhead_multiplier: 15
    playbook: feature-addition
---

# Feature Request: Concern-Oriented Agent Context

## Summary

Replace the YAML-based agent-context composition (stack.yaml, workflow.yaml, governance.yaml, reading-guides.yaml) with a concern-oriented routing model centered on a single CLI-agnostic markdown file: `docs/agent-context.md`. Agents discover what to read by concern name, not by file path. The planning-agent declares which concerns each story touches. The concern registry fills itself from the repository scan during fitting.

## Motivation

The current agent-context model uses four YAML files with strict key-per-field schemas and mandatory `source:` pointers. This design was built for agents that cannot read prose. In practice:

1. **The YAML drifts.** A gap analysis on a fitted production project found the entire specification chain (feature files, supplementary specs, scope map), all ADRs, cookbook recipes, concept documents, and onboarding guides had no agent-context representation. The YAML covered the development process ("how to build") but not the product domain ("what to build").

2. **The strictness invites neglect.** Every non-null, non-deferred leaf field requires a `source:` pointer when `mode: index`. Fields lacked pointers — a composition-rule violation that went unnoticed because maintaining the YAML felt like overhead rather than value.

3. **Agent definitions reference files, not concerns.** A developer-agent dispatched to build a new entity class receives a file shopping list. When files move, split, or merge, agent definitions and the YAML both need updating. The indirection layer (reading-guides.yaml mapping concern to YAML keys to files — three hops) adds coordination cost without adding stability.

4. **The concern is the stable unit, not the file.** A domain concept remains a valid concern even when its documentation splits across multiple files. File paths are where knowledge currently lives — an implementation detail. The concern is what the agent needs to understand.

5. **Strong models read prose.** Claude, GPT, and Gemini parse markdown natively. A prose-based routing file that humans also maintain naturally eliminates the translation layer between what agents read and what humans write.

The originating proposal (`yaml-charter-lifecycle.md`) and its ADRs (`0013-yaml-agent-context-replaces-markdown-charter`, `0014-two-layer-routing-with-two-mode-lifecycle`) are phantom references — cited in the composition rules and capture-context skill but not present on disk. This itself illustrates the maintenance-overhead problem: the design-origin trail degraded because the YAML model's maintenance burden discouraged upkeep. This proposal supersedes that design intent.

## Core Principles

- Agents are routed by concern, not by file path.
- The concern registry is a single CLI-agnostic markdown file (`docs/agent-context.md`).
- Cross-cutting concerns are always active. Technical and domain concerns are declared per story by the planning-agent.
- Generic concerns ship with the factory. Project-specific concerns are derived from the repository scan during fitting.
- Machine-consumed configuration (test commands, gate thresholds, suite definitions) stays in `testing.yaml`. It is configuration, not routing.

## Design

### Concern categories

Three categories, distinguished by when they apply:

| Category      | When active                       | Examples                                                                       | Who declares                    |
| ------------- | --------------------------------- | ------------------------------------------------------------------------------ | ------------------------------- |
| Cross-cutting | Always. Every agent, every story. | Branching, committing, testing discipline, review, scope discipline, security. | Factory (generic)               |
| Technical     | Per story, set by planning-agent. | Backend, frontend, data-storage; or data-source, processing, visualization.    | Fitting scan (project-specific) |
| Domain        | Per story, set by planning-agent. | Varies by project — derived from scope map areas or specification structure.   | Fitting scan (project-specific) |

Cross-cutting concerns are the professional baseline — an agent is always aware of them, the way a human colleague always knows the branching policy. Technical concerns narrow the stack context per task. Domain concerns focus the product knowledge.

#### Generic cross-cutting concerns (factory-shipped)

The factory ships these generic concerns. Every project gets them during fitting:

| Concern            | Covers                                                                       |
| ------------------ | ---------------------------------------------------------------------------- |
| Branching          | Branching policy, worktree discipline, merge order.                          |
| Committing         | Commit message format, hook discipline, story-ID rule.                       |
| Testing discipline | Risk-based testing, test admission, layer ownership, risk classes.           |
| Review             | Peer review rules, architecture review triggers, creation/review separation. |
| Scope discipline   | Build accepted scope only, YAGNI, deferred-feature boundaries.               |
| Security           | Security-focused review triggers, secret handling, authorization boundaries. |

Projects may add project-specific cross-cutting concerns during fitting (for example, a regulatory-compliance concern in a financial project).

#### Domain concern grain

Domain concerns default to the scope-map structure when a scope map exists. Scope-map areas are the specification's own partitioning of the product — they are stable, stakeholder-meaningful, and already used by the planning-agent for story slicing. For projects without a scope map, the planning-agent defines domain concerns from the feature structure or the EPIC breakdown, subject to user confirmation during backlog review.

### Concern registry: `docs/agent-context.md`

Most projects already have a `docs/agent-context.md` that routes agents by task type. The migration to the concern model is a restructuring of this existing file, not a green-field creation. The current ad-hoc sections ("Backend Changes", "Frontend Changes") become formal concern entries.

The file is organized by category. Each concern is a markdown section carrying:

- A one-line description of what knowledge it covers.
- A file list: the current paths where that knowledge lives.
- Boundary notes where relevant (which cross-concern interfaces to respect).

Structure:

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
Risk-based testing, test admission, layer ownership.
Read: docs/handbook/testing/conventions.md, docs/handbook/testing/strategy.md

...

## Technical concerns

### backend
Server-side application code: routes, models, services, repositories.
Read: docs/handbook/backend/conventions.md, docs/handbook/backend/cookbook/*.md
Boundary: docs/spec/supplementary_specs/interface-contracts.md

### frontend
Client-side application code: components, composables, views.
Read: docs/handbook/frontend/conventions.md, docs/handbook/frontend/cookbook/*.md
Boundary: docs/spec/supplementary_specs/interface-contracts.md

### data-storage
Database schema, migrations, query patterns.
Read: docs/handbook/concepts/async-first.md
Boundary: docs/spec/supplementary_specs/entity-model.md

## Domain concerns

### <scope-map-area>
<one-line description>
Read: <relevant spec files, supplementary specs, state machines>
```

No YAML nesting. No `source:` pointer ceremony. A moved file is a one-line edit in one file.

### Concern declaration in story frontmatter

The planning-agent writes a `concerns` field into each story's frontmatter:

```yaml
concerns:
  domain: [<scope-map-area>]
  technical: [backend, frontend, data-storage]
```

Cross-cutting is absent because it is always active — no need to declare it. The planning-agent picks from the controlled vocabulary in the concern registry. If a story needs a concern that does not exist, the planning-agent flags it as a registry update rather than coining a name silently.

### Concern resolution at dispatch time

No explicit resolution step. `docs/agent-context.md` is included in every CLI's instruction chain via the native include mechanism:

- Claude Code: `@docs/agent-context.md` in CLAUDE.md
- GitHub Copilot CLI: reference from `.github/` instructions
- Pi: reference from `.pi/` instructions
- Codex: reference from `.codex/` instructions

The file is CLI-agnostic — no CLI-specific syntax, no tool-specific directives. Each CLI's `init-factory` output generates the appropriate include directive. The agent reads its story's `concerns` field and follows the matching sections in `agent-context.md`. The mechanism is "read the heading that matches your concern."

The concerns field is advisory — it tells the agent what is relevant, not what is permitted. The agent always has access to the full registry via the include chain. This is intentional: cross-cutting concerns are always visible, and peripheral awareness of adjacent technical or domain concerns helps the agent respect boundaries it does not own.

### Two kinds of input: factory-canonical vs project-native

Agent and skill definitions reference two distinct kinds of files:

**Factory-canonical artifacts** have fixed names, fixed structure, and a factory-defined contract. Examples: `architecture.dsl`, `scope-map.md`, `*.feature`, `backlog/ST-*.md`, `docs/spec/prd.md`, `testing.yaml`. Every factory project either has them or does not yet. These stay as concrete paths in agent and skill definitions — the path *is* the contract.

**Project-native knowledge** varies by project in shape, location, and quantity. Examples: handbook conventions, cookbook recipes, concept docs, ADRs, supplementary specs. These are exactly what the concern registry exists for. Agent definitions replace their project-native file lists with concern references — "follow the concerns relevant to your work in `agent-context.md`" — and the registry provides the paths.

This distinction applies across all factory phases, not only implementation:

- A **requirements-agent** writing a feature spec reads factory-canonical inputs (scope map, feature files) by path and reads project-native domain knowledge (supplementary specs, concept docs) via domain concerns.
- An **architecture-agent** reads factory-canonical inputs (architecture.dsl, ADR index) by path and reads project-native technical knowledge (handbook conventions, infrastructure docs) via technical concerns.
- A **QA agent** reads factory-canonical inputs (testing.yaml, story frontmatter) by path and reads project-native testing knowledge (test strategy, test cookbooks) via the testing-discipline concern.
- A **developer-agent** reads its story (factory-canonical) by path and reads project-native conventions via the concerns declared in the story frontmatter.

The `concerns:` field in story frontmatter is a focusing mechanism for implementation, where the planning-agent narrows the relevant concerns per task. Pre-backlog phases (requirements, architecture, QA) do not carry story frontmatter — these agents read the full concern registry by judgment, because their work surveys the landscape rather than narrowing it.

The implementation discovers which definitions need updating by searching for project-native paths (`docs/handbook/`, `docs/spec/supplementary_specs/`, etc.) in agent and skill definitions. Factory-canonical references remain untouched.

### Fitting and the concern scan

During fitting, `capture-context` scans the repository and proposes concerns:

- **Generic cross-cutting concerns** are seeded from the factory. They apply to every project.
- **Project-specific technical concerns** are derived from the detected stack. A web-application repo gets concerns for its server, client, and storage layers. A data-science repo gets concerns for its data sources, processing, and visualization layers.
- **Project-specific domain concerns** are derived from the specification if it exists (scope-map areas, feature-file rule groups), or left empty for the planning-agent to populate during backlog creation.

The scan proposes, the user confirms — same interactive fitting pattern as today. The vocabulary is frozen after confirmation until the next scan.

### Maintenance after fitting

After initial fitting, `docs/agent-context.md` is maintained by the team — the same people who maintain the documentation it points to. When a file moves, the human edits the path in the concern entry. When a new concern emerges (a new scope-map area, a new technical layer), the human or the planning-agent adds a section.

The current `update-context` skill is retired. It was the write-path for YAML index files — adding source pointers, updating deferrals, maintaining reading-guides.yaml. With the YAML files gone, the skill has no target. Editing a markdown section is simpler than invoking a skill to set a YAML key with a source pointer.

The staleness lint (see Validation below) is the safety net that catches forgotten path updates.

### Validation: concern-lint replaces context-lint

The current `context-lint` validates seven properties of the YAML files (CX-FILE, CX-PARSE, CX-KEYS, CX-NULL, CX-SRC-EXIST, CX-SRC-STALE, CX-GUIDE-REF, CX-FORMAT). Most are YAML-structural checks that do not apply to the markdown format. The replacement, `concern-lint`, validates four properties of `agent-context.md`:

| Check                       | ID           | What it validates                                                                                                                                       |
| --------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Section structure           | CTX-SECTIONS | Every expected category heading exists (Always, Technical, Domain). Each concern section has a description line and at least one `Read:` path.          |
| Path resolution             | CTX-PATHS    | Every path in a `Read:` or `Boundary:` line resolves to an existing file or glob match.                                                                 |
| Concern-reference integrity | CTX-REFS     | Every concern name in a story's `concerns:` frontmatter has a matching heading in `agent-context.md`.                                                   |
| No legacy residue           | CTX-LEGACY   | No YAML agent-context files (`docs/agent-context/*.yaml` other than `testing.yaml`) or `docs/charter/` directory remain alongside the concern registry. |

`concern-lint` runs as part of `validate`, replacing `context-lint` in the gate sequence. It also runs on demand.

**Legacy formats retired.** The charter format (`docs/charter/`) and the YAML agent-context format (`docs/agent-context/*.yaml`) are both obsolete. `concern-lint` does not validate either. The CTX-LEGACY check flags their presence as residue that should be removed or migrated.

### What stays as YAML

`testing.yaml` remains as machine-consumed configuration: test commands, suite definitions, gate thresholds, marker registrations. Scripts parse it for values. It is not a routing artifact and agents do not read it for context navigation.

`testing.yaml` moves from `docs/agent-context/testing.yaml` to `docs/testing.yaml`. The `docs/agent-context/` directory is deleted entirely — leaving it as a container for a single file would look like an incomplete migration. The resolution chain in `concern-lint`, `detect-test-regime`, and gate scripts (`crap-score`, etc.) updates to resolve `docs/testing.yaml` as the single location. No fallback to legacy paths.

### What is deleted

- `docs/agent-context/stack.yaml`
- `docs/agent-context/workflow.yaml`
- `docs/agent-context/governance.yaml`
- `docs/agent-context/reading-guides.yaml`
- `docs/agent-context/` directory (after `testing.yaml` moves to `docs/`)
- `factory/rulebooks/templates/context-*.yaml` (YAML templates used by the old `capture-context`)

Their knowledge migrates into `docs/agent-context.md` concern sections during the transition.

The `update-context` skill is retired (see Maintenance after fitting).

The `context-lint` script is replaced by `concern-lint` (see Validation).

### Migration for already-fitted projects

`capture-context` auto-detects the old YAML format on its next invocation. When it finds `docs/agent-context/stack.yaml` (or any of the four YAML files), it offers interactive migration:

1. Read existing YAML files and `reading-guides.yaml`.
2. Propose concern sections derived from the YAML content — cross-cutting from governance.yaml, technical from stack.yaml, workflow routing from reading-guides.yaml.
3. Present the proposed `agent-context.md` structure for user confirmation.
4. On confirmation: write the restructured `agent-context.md`, move `testing.yaml` to `docs/testing.yaml`, delete the YAML files and the `docs/agent-context/` directory.

The migration is interactive because the YAML-to-concern mapping requires judgment — a YAML key like `frameworks.backend` maps to a `backend` technical concern, but the concern's file list may need enrichment beyond what the YAML `source:` pointers carried. The user confirms the result.

The project count using the YAML model is low, so a dedicated migration script is not warranted. The interactive path through `capture-context` is sufficient.

### Capture-context procedure shape (new model)

The current `capture-context` has four invocation modes (`--init`, `--init --scan`, `--init --minimal`, `--init --scan --minimal`). The new model simplifies to two full modes plus a migration trigger:

**`capture-context --init` (greenfield or first fitting)**

1. Scan repository for languages, frameworks, test runners, and documentation structure (same detection as today).
2. Seed generic cross-cutting concern sections from factory templates.
3. Propose project-specific technical concerns from the detected stack. Present to user: "I found FastAPI, Vue, PostgreSQL — proposing concerns: backend, frontend, data-storage. Confirm or adjust?"
4. If a specification exists (scope map, feature files): propose domain concerns from scope-map areas. If no specification: leave the domain section empty with a note that the planning-agent populates it during backlog creation.
5. Write `docs/agent-context.md` with confirmed concerns. Each section gets a description line and file paths resolved from the scan.

**`capture-context --init --scan` (brownfield)**

Same as above, plus:

1. Discover existing documentation (handbooks, ADRs, specs, cookbooks) and propose additional `Read:` paths per concern.
2. Run a concern-based interview: "I found these docs for the backend concern — anything missing? Any concerns I missed entirely?"

The `--minimal` variants are dropped — the concern model's simpler structure makes the minimal/full distinction unnecessary. A bare invocation (no flags) triggers migration detection for already-fitted YAML projects (see Migration above).

Interview flow: instead of confirming YAML field values one at a time, the user confirms concern names and their file lists in batches by category. Cross-cutting first (usually accepted as-is), then technical (may need renaming), then domain (most project-specific, most discussion).

## Open Questions

1. **concern-lint scope relative to testing.yaml.** Resolved: concern-lint does not validate `testing.yaml`. It is machine config, not a concern artifact. `detect-test-regime` and the gate scripts own its validation. Mixing testing.yaml checks into concern-lint would conflate routing validation with configuration validation.

2. **update-context retirement method.** Resolved: option (b). The skill file stays in the factory with its body replaced by a deprecation notice pointing to direct `agent-context.md` editing. No hard error for projects that invoke it, no silent no-op that hides the transition. The notice is the migration signal.

3. **Handling concerns not yet in registry.** Resolved: option (a). The planning-agent proposes the new concern section (name, description, initial file list) and the user confirms before it enters the registry. This matches the interactive pattern used throughout fitting. Blocking story creation is too heavy for a vocabulary gap. Silent provisional addition without confirmation violates the controlled-vocabulary principle.

4. **Phase coverage of concern-based routing.** Resolved. All phases consume the concern registry, but through two distinct mechanisms. Implementation agents use the `concerns:` field in story frontmatter to narrow focus. Pre-backlog agents (requirements, architecture, QA) read the full registry by judgment — their work surveys rather than narrows. Agent and skill definitions distinguish factory-canonical artifacts (concrete paths) from project-native knowledge (concern references). See "Two kinds of input" in Design.

## Scope

**In the first release:**

- New `agent-context-composition` rulebook defining the concern model, categories, the `agent-context.md` structure, the controlled vocabulary rule, and the advisory nature of concern declarations.
- Updated `capture-context` skill: scan proposes concerns, writes `agent-context.md` sections instead of YAML files.
- `update-context` skill body replaced with a deprecation notice pointing to direct `agent-context.md` editing.
- Updated `planning-agent`: writes `concerns` field into story frontmatter from the controlled vocabulary. When a story needs a concern not in the registry, the planning-agent proposes the new section for user confirmation.
- Updated `developer-agent`: reads story concerns, follows matching sections in `agent-context.md`.
- Updated `implementation-agent` (dispatcher): no concern resolution logic needed — resolution is implicit via the include chain.
- Updated `virgil`: fitting logic references `agent-context.md` instead of YAML files.
- Updated `reconciliation-agent`: input references updated from YAML to concern sections. The current Step 6 (compare against `context-interview-guide.yaml` template and YAML index files) is replaced by a concern-registry health check: verify that every concern section in `agent-context.md` still has valid `Read:` paths and that the concern vocabulary matches the project's current documentation structure.
- `concern-lint` replaces `context-lint` in `validate`.
- Updated `init-factory`: generates CLI-specific include directives for `docs/agent-context.md`.
- Updated `detect-test-regime` skill and gate scripts (`crap-score`, etc.): resolve `testing.yaml` at `docs/testing.yaml`.
- Updated agent definitions that reference `docs/agent-context/testing.yaml`: path updated to `docs/testing.yaml`.
- Agent and skill definitions updated: project-native file lists replaced with concern references; factory-canonical artifact paths retained.
- Migration guide: how to convert an existing YAML-based agent-context to the concern model.

**Explicitly deferred (do NOT plan stories for these):**

- Automated concern derivation from code changes (detect when a new module implies a new concern).
- Concern-level impact analysis (which concerns does this PR touch).
- Cross-project concern federation (shared concerns across repos in a multi-repo setup).

## Completion Criteria

- `agent-context-composition.md` rulebook describes the concern model with three categories, the `agent-context.md` structure, the controlled vocabulary rule, the advisory nature of concern declarations, and the `concern-lint` checks (CTX-SECTIONS, CTX-PATHS, CTX-REFS, CTX-LEGACY).
- `capture-context` produces `agent-context.md` concern sections from a repo scan instead of the four YAML files.
- `update-context` skill body is a deprecation notice pointing to direct `agent-context.md` editing; invoking it produces no error and no side effects.
- `planning-agent` writes `concerns:` into story frontmatter.
- `developer-agent` reads its story's concerns and follows matching `agent-context.md` sections.
- `virgil` references `agent-context.md` instead of YAML files.
- `reconciliation-agent` references `agent-context.md` instead of YAML files. Its agent-context health check (formerly Step 6 comparing against `context-interview-guide.yaml`) validates that every concern section has valid `Read:` paths and that the concern vocabulary matches the project's documentation structure.
- `testing.yaml` lives at `docs/testing.yaml` and continues to work as machine config. The resolution chain in `detect-test-regime`, gate scripts (`crap-score`, etc.), and agent definitions resolves the new path.
- `concern-lint` replaces `context-lint` in `validate`. It runs CTX-SECTIONS, CTX-PATHS, CTX-REFS, CTX-LEGACY. No legacy format validation — charter and YAML agent-context are retired.
- `init-factory` generates the appropriate include directive per CLI.
- Agent and skill definitions carry no project-native file lists; they reference concerns or factory-canonical artifacts only.
- `planning-agent` proposes new concern sections for user confirmation when a story needs a concern not in the registry.
- `capture-context` auto-detects old YAML agent-context format and offers interactive migration to the concern model. Running it on an already-fitted YAML project produces a valid `agent-context.md`, moves `testing.yaml` to `docs/testing.yaml`, and deletes the YAML files.
- The old YAML files can be deleted without breaking any factory agent, skill, or gate.

## Guiding Rule

Route agents by what they need to understand, not by where the files happen to be.

## Review — 2026-09-08

Reviewer: proposal-review-agent
Reviewed commit: f2558e9a59e286658ee108d7f1b92244e14abf05
Disposition: findings

### Findings

| ID      | Severity | Check | Status | Finding                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------- | -------- | ----- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | minor    | 05    | fixed  | Boundary path `factory/scripts/detect-test-regime` does not exist. The actual path is `factory/skills/detect-test-regime/SKILL.md` — detect-test-regime is a skill, not a script.                                                                                                                                                                                                                                                |
| PROP-02 | major    | 01    | fixed  | Completion criterion 7 says "testing.yaml continues to work as machine config, unchanged" but the Design describes moving it from `docs/agent-context/testing.yaml` to `docs/testing.yaml` and updating the resolution chain in concern-lint, detect-test-regime, gate scripts, and all agent definitions. The criterion contradicts the design.                                                                                 |
| PROP-03 | major    | 02    | fixed  | Scope's "In the first release" does not list updating the testing.yaml resolution chain in `detect-test-regime`, gate scripts (`crap-score`, etc.), or the five agent definitions that currently hardcode `docs/agent-context/testing.yaml` as a path. The Design describes this work but the Scope omits it, leaving a planning agent to infer the stories.                                                                     |
| PROP-04 | minor    | 03    | fixed  | Reconciliation-agent Step 6 reads `factory/rulebooks/templates/context-interview-guide.yaml` and compares against YAML index files. The `context-*.yaml` template glob deletes the interview guide. The Scope says "input references updated" but the Design does not describe the replacement reconciliation procedure for agent-context health. A planning agent cannot write a story for this without re-deriving the design. |
| PROP-05 | major    | 02    | fixed  | context-lint currently validates both YAML agent-context (CX-\* codes) and legacy markdown charter (CH-\* codes) via format detection. The proposal says concern-lint "replaces context-lint" and describes only four CL-\* checks for the concern model. No provision is made for legacy charter validation. Projects using `docs/charter/*.md` would lose their validation gate entirely when context-lint is replaced.        |

### Summary

Five of eight checks pass cleanly: impact classification, open questions, motivation, estimate, and design decomposability (with caveats on the reconciliation-agent procedure). Three checks produced findings. The major issues are: (1) a completion criterion that contradicts the design on testing.yaml's location change, (2) scope that omits the testing.yaml resolution chain updates described in the design, and (3) the silent loss of legacy charter validation when context-lint is replaced by concern-lint. These three must be addressed before a planning agent can decompose this into stories without coming back to ask what was meant.

## Review — 2026-09-08 (Round 4)

Reviewer: proposal-review-agent
Reviewed commit: f2558e9a59e286658ee108d7f1b92244e14abf05
Disposition: findings

### Prior findings

| ID      | Severity | Check | Status | Finding                                                    |
| ------- | -------- | ----- | ------ | ---------------------------------------------------------- |
| PROP-01 | minor    | 05    | fixed  | Boundary path detect-test-regime resolved.                 |
| PROP-02 | major    | 01    | fixed  | Testing.yaml completion criterion now matches design.      |
| PROP-03 | major    | 02    | fixed  | Scope now includes testing.yaml resolution chain updates.  |
| PROP-04 | minor    | 03    | fixed  | Reconciliation-agent procedure replacement specified.      |
| PROP-05 | major    | 02    | fixed  | Legacy charter validation retained in concern-lint design. |

### Checks

| Check | Name                         | Result                                |
| ----- | ---------------------------- | ------------------------------------- |
| 01    | Completion criteria testable | PASS with findings (PROP-07, PROP-10) |
| 02    | Scope boundary sharp         | PASS with finding (PROP-08)           |
| 03    | Design decomposable          | PASS with finding (PROP-09)           |
| 04    | Impact classification        | PASS                                  |
| 05    | Boundary references exist    | PASS with major finding (PROP-06)     |
| 06    | Open questions genuine       | PASS                                  |
| 07    | Motivation justifies timing  | PASS                                  |
| 08    | Estimate plausible           | PASS                                  |

### Findings

| ID      | Severity | Check | Status | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ------- | -------- | ----- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-06 | major    | 05    | fixed  | Boundary list incomplete. The Scope item "Agent and skill definitions updated" and "Updated detect-test-regime skill and gate scripts (crap-score, etc.)" cover files not listed in `impact.boundaries`. At minimum: 5 agents (`requirements-agent`, `architecture-agent`, `architecture-review-agent`, `qa-agent`, `spec-review-agent`) carry project-native paths (`docs/handbook/`, `docs/spec/supplementary_specs/`, `docs/adr/`) in their `inputs:` lists. The `crap-score` script hardcodes `docs/agent-context/testing.yaml` at line 101 and is explicitly named in the Scope but absent from boundaries. The `validate` skill references `context-lint` at gate #12 and needs the `concern-lint` update. At least 10 additional skills reference `docs/agent-context/` or `testing.yaml` paths. A reviewer cannot verify the proposal accounts for these files when they are not listed as boundaries. |
| PROP-07 | major    | 01    | fixed  | Completion Criterion 8 says "concern-lint replaces context-lint in validate with four checks: CL-SECTIONS, CL-PATHS, CL-REFS, CL-FORMAT." The Design explicitly requires concern-lint to also retain CH-\* checks for charter-format projects and CX-\* checks for YAML-format projects during transition. CC8 enumerates only CL-\* checks. A verifier testing CC8 passes the criterion while missing two contractual design requirements. This is the same CC-doesn't-cover-Design gap pattern from prior rounds — the round 3 fix for PROP-05 added CH-\*/CX-\* retention to the Design but did not propagate it to the Completion Criteria.                                                                                                                                                                                                                                                                |
| PROP-08 | minor    | 02    | fixed  | No completion criterion covers the migration path for existing YAML-format projects. The Scope lists "Migration guide" as a deliverable and the Design describes an interactive migration procedure through `capture-context`. Neither the guide nor the procedure has a corresponding completion criterion.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| PROP-09 | minor    | 03    | fixed  | The Design's "Capture-context procedure shape" section states: "The current capture-context has four invocation modes (--init, --init --scan, --update, bare)." The actual `capture-context` SKILL.md defines four modes: `--init`, `--init --scan`, `--init --minimal`, and `--init --scan --minimal`. There is no `--update` mode (that is the separate `update-context` skill) and no bare invocation. The baseline misstatement makes the "simplifies to two" framing misleading.                                                                                                                                                                                                                                                                                                                                                                                                                          |
| PROP-10 | minor    | 01    | fixed  | Completion Criterion 6 ("virgil and reconciliation-agent reference agent-context.md instead of YAML files") does not cover the reconciliation-agent's Step 6 health check replacement described in both the Scope and Design. A verifier satisfies CC6 by confirming file references changed without verifying the health check procedure is implemented.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |

### Summary

Five of eight checks pass cleanly. Three checks produce findings — two major, three minor. The major issues are: (1) the boundary list omits at least 20 files the Scope commits to changing, including the `crap-score` script it names explicitly (PROP-06), and (2) Completion Criterion 8 again fails to cover what the Design requires — CH-\* and CX-\* check retention was added to the Design in round 3 but never reached the CC (PROP-07). The recurring pattern across four rounds is that Design fixes do not propagate to Completion Criteria. The "Two kinds of input" section is internally consistent with the rest of the proposal, all four resolved Open Questions align with their Design references, and the estimate remains plausible. The two major findings must be addressed before a planning agent can decompose this into stories with confidence that the boundary list and completion criteria match the actual scope of work.
