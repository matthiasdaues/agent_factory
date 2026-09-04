# EPICs -- Agent Context

Proposal trace: [yaml-charter-lifecycle.md](../docs/proposals/yaml-charter-lifecycle.md)
Feature trace: [agent-context.feature](../docs/spec/agent-context.feature)

## EPIC 1: Validate agent-context YAML structure and references

### Why this EPIC exists

Without a deterministic validation gate, the four YAML files that make up the agent context can drift silently -- missing keys, broken source pointers, mixed formats. context-lint (the renamed validation script) is the single mechanical check that prevents agents from reading a corrupted routing table. It must exist before any skill can write or modify agent-context files, because every writing skill runs context-lint to confirm its output is valid.

### Actor Goals

- context-lint (deterministic gate) validates agent-context YAML structure, key presence, mode compliance, source-pointer integrity, and reading-guide references with CX-\* finding codes
- context-lint validates testing.yaml (the machine-readable test configuration peer file, written by detect-test-regime) with CX-PARSE only, exempting it from lifecycle checks
- context-lint falls back to CH-\* finding codes for legacy markdown charter projects
- context-lint detects and rejects mixed-format projects (YAML agent-context alongside markdown charter) with CX-FORMAT
- Factory governance codifies agent-context composition rules in a convention document and rules.md

### Demo

01. The operator copies the four YAML templates (stack, workflow, governance, reading-guides) into `docs/agent-context/` and runs `context-lint`.
02. context-lint reports CX-NULL warnings for every null placeholder field and a CX-MODE info message confirming `mode: primary`.
03. The operator introduces a YAML syntax error in `stack.yaml` and re-runs context-lint.
04. context-lint reports a CX-PARSE error for the malformed file.
05. The operator fixes the syntax, sets `mode: index`, removes a `source:` pointer from one field, and re-runs.
06. context-lint reports a CX-SRC warning for the field missing its source pointer.
07. The operator adds a reference `stack.yaml#frameworks.nonexistent` to `reading-guides.yaml` and re-runs.
08. context-lint reports a CX-GUIDE-REF warning for the unresolvable key path.
09. The operator creates a legacy `docs/charter/tech-stack.md` alongside `docs/agent-context/` and re-runs.
10. context-lint reports a CX-FORMAT error for the mixed locations.
11. The operator removes `docs/agent-context/`, keeps only `docs/charter/*.md`, and re-runs.
12. context-lint reports CH-\* findings using the existing charter-lint validation rules.

### Scope

**In:**

- Four YAML template files -- three index-file templates (`context-stack.yaml`, `context-workflow.yaml`, `context-governance.yaml`) with `mode: primary` and null placeholder values, plus one reading-guide template (`context-reading-guides.yaml`) with common concern entries referencing index-file sections via key-path notation (e.g. `stack.yaml#frameworks.backend`)
- `agent-context-composition.md` convention -- a new rulebook convention documenting the binding rules for agent-context composition: what is derived content, what modes mean, write-path ownership, format exclusivity, and source-pointer direction of truth
- `rules.md` entry -- a new "Agent context composition" section with MUST/MUST NOT rules referencing the convention, replacing the existing "MUST derive Epic 0 from the charter" wording
- context-lint script -- rename `factory/scripts/charter-lint` to `factory/scripts/context-lint`; add YAML validation for all CX-\* finding codes (CX-FILE, CX-PARSE, CX-KEYS, CX-NULL, CX-MODE, CX-MODE-INVALID, CX-SRC, CX-SRC-EXIST, CX-SRC-STALE, CX-GUIDE-REF, CX-FORMAT); retain CH-\* codes for legacy markdown fallback
- testing.yaml carve-out -- context-lint applies CX-PARSE only to testing.yaml, skipping CX-SRC, CX-MODE, and CX-NULL checks, because testing.yaml is lifecycle-exempt and written directly by detect-test-regime
- Format detection chain -- three-step resolution (agent-context YAML at `docs/agent-context/stack.yaml` first, then legacy YAML charter at `docs/charter/tech-stack.yaml`, then legacy markdown charter at `docs/charter/tech-stack.md`) with CX-FORMAT error when files exist at more than one location; testing.yaml resolution walks both `docs/agent-context/` and `docs/charter/` independently without triggering CX-FORMAT
- Pre-commit hook entry -- rename `charter-lint` hook id to `context-lint` in `.pre-commit-config.yaml`
- Test fixtures -- synthetic agent-context files under `tests/fixtures/agent-context/` covering both modes, all four file types, and the testing.yaml peer

**Out:**

- capture-context and update-context skills (EPICs 2 and 3 respectively)
- Consumer path updates in agents, skills, playbooks, and other scripts (EPIC 4)
- Automated migration tool (explicitly deferred per proposal)

### Dependencies

None. This is the foundational EPIC.

### Boundaries

- Validator: contextLint component (the renamed script)
- Catalog: YAML templates in `factory/rulebooks/templates/`, convention in `factory/rulebooks/conventions/`
- Git/pre-commit: `.pre-commit-config.yaml` hook entry rename

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                                                          | Tier     | Size | Basis                                                                                                       |
| ------- | ----------------------------------------------------------------------------------- | -------- | ---- | ----------------------------------------------------------------------------------------------------------- |
| ST-0190 | Create YAML templates and convention, validate with core CX-\* codes                | standard | L    | High effort (4 templates + convention + Python script with 6 CX-\* checks + test fixtures), low uncertainty |
| ST-0191 | Validate source pointers and reading-guide references with CX-SRC and CX-GUIDE-REF  | standard | M    | Medium complexity (key-path parser, mtime comparison, source-existence check), low uncertainty              |
| ST-0192 | Detect context format, validate legacy charters, and enforce testing.yaml carve-out | standard | L    | High complexity (three-step detection chain, testing.yaml independence, CH-\* fallback), medium uncertainty |

## EPIC 2: Initialize and onboard agent context

### Why this EPIC exists

The templates and validation from EPIC 1 let someone create agent-context files by hand, but no factory skill can do it yet. Without capture-context (the renamed capture-charter skill), greenfield projects have no automated way to scaffold the three index files, and brownfield projects have no structured process to discover existing documentation and populate source pointers. Every downstream skill -- update-context, detect-test-regime, and the reading-guide assembly -- depends on correctly initialized files.

### Actor Goals

- Human Operator initializes agent context for a greenfield project by running `capture-context --init`, which creates three index-file templates with `mode: primary` and null placeholders (no reading guide, because no handbook exists yet)
- Human Operator onboards brownfield documentation into agent context by running `capture-context --init --scan`, which discovers documentation signals, runs a concern-based interview, populates index files with source pointers (`source:` fields pointing at the project's authoritative documents), and generates `reading-guides.yaml` (the Layer 1 routing file that maps work-type concerns to Layer 2 index sections)
- Human Operator uses legacy markdown charter projects without forced migration -- capture-context detects the format and operates on whatever it finds

### Demo

01. The operator runs `capture-context --init` in a new, empty project.
02. Three YAML files appear in `docs/agent-context/`: `stack.yaml`, `workflow.yaml`, `governance.yaml`, each with `mode: primary` and null placeholder values.
03. `reading-guides.yaml` is not created (greenfield projects have no handbook to route to).
04. The operator runs `context-lint` and gets CX-NULL warnings but no errors -- the files are structurally valid.
05. The operator runs `capture-context --init --scan` in a brownfield project that has `pyproject.toml`, `docs/adr/`, and `.github/workflows/`.
06. The scan discovers languages, frameworks, CI/CD configuration, and decision documentation from those files.
07. For each applicable concern (backend, testing, architecture), the concern interview asks the operator where conventions are documented and proposes source paths based on the scan.
08. After the interview completes, all four agent-context files are populated with source pointers from the discovered documentation.
09. The operator runs `context-lint` and the files pass validation.
10. If the scan achieves full source coverage (every non-null, non-deferred field has a `source:` pointer), capture-context proposes setting `mode: index`.

### Scope

**In:**

- capture-context skill -- rename `factory/skills/capture-charter/SKILL.md` to `factory/skills/capture-context/SKILL.md` with YAML support, concern-based brownfield onboarding, and format detection for backward compatibility with existing markdown charters
- Greenfield initialization (`--init`) -- creates three index-file templates from the EPIC 1 templates, does not create `reading-guides.yaml`, does not overwrite existing files
- Brownfield onboarding (`--init --scan`) -- five-phase process: discovery scan (identifies documentation signals from project files), concern interview (walks each applicable work-type concern), index completion (fills remaining fields), mode determination (proposes `mode: index` when full source coverage is achieved), reading-guide assembly (generates `reading-guides.yaml` from concern interview results)
- Stakeholder interview -- in greenfield mode, fills index-file values directly as inline content
- Format detection -- uses the three-step chain from EPIC 1 to handle projects with legacy markdown charters; offers migration as an optional step, never forces it

**Out:**

- update-context skill (EPIC 3)
- Automated migration tool (explicitly deferred per proposal)
- Gigacron pilot migration (explicitly deferred per proposal)

### Dependencies

EPIC 1 (templates and context-lint must exist for capture-context to copy templates and validate its output).

### Boundaries

- Catalog: capture-context skill (renamed from capture-charter, resolved through INDEX.yaml)
- Validator: contextLint (validates the files capture-context produces)
- State Files: agent-context YAML files created on disk in `docs/agent-context/`

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                          | Tier     | Size | Basis                                                                                                                                |
| ------- | ------------------------------------------------------------------- | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------ |
| ST-0193 | Initialize greenfield agent context with capture-context --init     | standard | S    | Low complexity (template copy, skip-if-exists guard), low uncertainty                                                                |
| ST-0194 | Onboard brownfield documentation with capture-context --init --scan | standard | XL   | High complexity (five-phase process: discovery, concern interview, index completion, mode check, guide assembly), medium uncertainty |

## EPIC 3: Update agent context and transition lifecycle

### Why this EPIC exists

After agent-context files are initialized (EPIC 2), the project evolves: decisions get made, conventions get documented, source pointers accumulate. Without update-context (the renamed update-charter skill), there is no controlled write path for modifying index files -- and without the mode-transition logic, the files never graduate from primary source to downstream routing table. The two-mode lifecycle (primary mode where values are written directly, index mode where every field carries a `source:` pointer to the authoritative document) is the core mechanism that prevents the agent context from becoming a stale second copy of the handbook.

### Actor Goals

- Human Operator updates agent-context fields as decisions emerge -- writing inline values when `mode: primary`, writing name-and-source pairs when `mode: index`, and recording deferred decisions with `deferred: "reason"` mappings
- Human Operator transitions the agent context from primary to index mode -- update-context checks the transition condition (every non-null, non-deferred leaf field across all three index files has a `source:` pointer), prompts the operator, and flips all three files atomically in a single commit
- update-context proposes creating `reading-guides.yaml` when the first `source:` pointer is written and no reading guide exists yet

### Demo

01. The operator has three index files in `mode: primary` with some null fields (status quo from EPIC 2).
02. The operator invokes `update-context` to record a technology choice for `stack.yaml#frameworks.backend`.
03. update-context writes the inline value `FastAPI 0.100` directly to the field.
04. The operator invokes `update-context` to add a source pointer for the same field, pointing at `docs/adr/004-use-fastapi.md`.
05. update-context writes both `name: FastAPI` and `source: docs/adr/004-use-fastapi.md` to the field.
06. Since this is the first source pointer and no `reading-guides.yaml` exists, update-context proposes creating the reading guide from the template.
07. The operator defers the `data_stores` decision with reason "evaluating options."
08. update-context writes `deferred: "evaluating options"` to the `data_stores` field, replacing any prior value.
09. The operator fills source pointers for all remaining non-null, non-deferred fields.
10. update-context detects that the transition condition is met and prompts: "All context fields now have sources. Switch to index mode?"
11. The operator confirms. update-context flips `mode` to `index` in all three files in a single commit, strips inline values to names only, and preserves source pointers.
12. The operator runs `context-lint` and the index-mode files pass validation.

### Scope

**In:**

- update-context skill -- rename `factory/skills/update-charter/SKILL.md` to `factory/skills/update-context/SKILL.md` with YAML support, mode-aware writing, and mode-transition logic
- Primary-mode writes -- update-context writes inline values directly to index-file fields when `mode: primary`
- Index-mode writes -- update-context writes both `name` and `source` together when `mode: index`; refuses writes without a source pointer in index mode
- Deferred-field handling -- records `deferred: "reason"` as the sole key at the field's leaf position; no coexistence with `name` or `source`
- Mode-transition logic -- checks transition condition (every non-null, non-deferred leaf across all three files has `source:`), prompts operator, executes atomic flip across all three files in one commit, strips inline values to names
- Reading-guide creation trigger -- when update-context writes the first `source:` pointer and no `reading-guides.yaml` exists, it proposes creating one from the template

**Out:**

- capture-context skill (EPIC 2)
- Consumer path updates (EPIC 4)
- Automated migration tool (explicitly deferred per proposal)

### Dependencies

EPIC 1 (context-lint must exist to validate post-update state; templates define the schema update-context writes to).

### Boundaries

- Catalog: update-context skill (renamed from update-charter, resolved through INDEX.yaml)
- Validator: contextLint (validates agent-context files after modification)
- State Files: agent-context YAML files modified through the lifecycle in `docs/agent-context/`

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                                 | Tier     | Size | Basis                                                                                                                                              |
| ------- | -------------------------------------------------------------------------- | -------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0195 | Update agent-context fields and manage source pointers with update-context | standard | M    | Medium complexity (mode-aware write logic, deferred handling, reading-guide trigger), low uncertainty                                              |
| ST-0196 | Transition agent context from primary to index mode                        | strong   | M    | Medium complexity (condition check across 3 files, atomic flip, value stripping), low uncertainty; data_integrity risk domain triggers strong tier |

## EPIC 4: Propagate format detection across factory consumers

### Why this EPIC exists

EPICs 1 through 3 deliver the agent-context machinery -- templates, validation, initialization, update, and lifecycle transition. But the rest of the factory still references `docs/charter/` in hardcoded paths. Until every consumer (agent, skill, playbook, script, hook, and configuration file) resolves context paths through the format-detection chain, a project that uses the new YAML agent-context will break on its first factory workflow. This EPIC is the wiring pass that makes the machinery usable end-to-end.

### Actor Goals

- Factory Consumer (any agent, skill, script, or hook that reads project context) resolves context file paths via the format-detection chain -- finding files at `docs/agent-context/` for new projects or falling back to `docs/charter/` for legacy projects
- Human Operator runs any factory workflow (greenfield-development, feature-addition, bug-fix) against a YAML agent-context project or a legacy markdown charter project without path errors
- Legacy projects continue working without migration -- format detection falls back transparently

### Demo

1. The operator has a project with `docs/agent-context/` YAML files (status quo from EPICs 1-3).
2. The operator runs `grep -r 'docs/charter' factory/agents/ factory/skills/ factory/playbooks/ factory/scripts/ factory/config/` across the active factory code.
3. Zero matches appear (legacy templates under `factory/rulebooks/templates/charter-*.md` are exempt -- retained for backward compatibility).
4. The operator triggers the `block-dangerous-git` hook (PreToolUse guard) in a project where `testing.yaml` lives at `docs/agent-context/testing.yaml`.
5. The hook resolves the test command from the new location and correctly allowlists it.
6. The operator runs `factory/scripts/phase advance` in the same project.
7. The script resolves `testing.yaml` via format detection and executes the test command.
8. The operator repeats steps 4 through 7 in a legacy project with `docs/charter/testing.yaml`.
9. Both the hook and the phase script resolve the test command from the old location -- legacy behavior is preserved.

### Scope

**In:**

- Script and hook path updates -- `factory/scripts/init-factory` (creates `testing.yaml` at the new path for new projects), `factory/scripts/crap-score` (resolves `testing.yaml` via format detection), `factory/scripts/phase` (resolves `testing.yaml` for FSM gate conditions), `factory/scripts/premerge-check` (resolves context path), `factory/config/hooks/block-dangerous-git.sh` and `.ts` (resolve `testing.yaml` via format detection for test-command allowlisting), FSM files (`greenfield-development.fsm.yml`, `bug-fix.fsm.yml`) update `testing.yaml` path references
- Agent and skill prose updates -- all agent markdown files (`virgil.md`, `developer-agent.md`, `implementation-agent.md`, `planning-agent.md`, `architecture-agent.md`, `requirements-agent.md`) update `inputs:`, `skills:`, body references, and descriptions to reference `docs/agent-context/` with format-detection fallback; all skill SKILL.md files that reference charter paths update to agent-context paths
- Playbook prose updates -- `feature-addition.md`, `greenfield-development.md`, `brownfield-onboarding.md` update charter references to agent-context
- INDEX.yaml regeneration -- run `index-lint` after frontmatter changes to regenerate `factory/INDEX.yaml` with updated descriptions

**Out:**

- factory-guide.md, README.md, and newcomer-tour content updates (EPIC 5 -- these carry user-facing guidance, not just path references)
- Backlog story path updates (explicitly deferred per proposal -- separate chore)
- SVG diagram regeneration (explicitly deferred per proposal)

### Dependencies

EPIC 1 (format-detection logic in context-lint establishes the resolution chain that consumers follow).

### Boundaries

- Dispatcher: trigger and indexLint components (INDEX.yaml descriptions updated, skill/agent resolution paths updated)
- Validator: blockDangerousGit component (resolves `testing.yaml` via format detection for test-command allowlisting), validate skill (calls `context-lint` by new name)
- State Manager: phaseAdvance component (resolves `testing.yaml` path for FSM gate conditions)
- Git/pre-commit: `.pre-commit-config.yaml` path references in hook scripts

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                               | Tier    | Size | Basis                                                                                                    |
| ------- | ------------------------------------------------------------------------ | ------- | ---- | -------------------------------------------------------------------------------------------------------- |
| ST-0197 | Update factory scripts, hooks, and configuration for agent-context paths | economy | M    | Medium complexity (format-detection logic in ~10 bash/Python files), low uncertainty                     |
| ST-0198 | Update factory agents, skills, and playbooks to reference agent-context  | economy | M    | Low complexity (mechanical find-replace), high effort (~25 markdown files + INDEX.yaml), low uncertainty |

## EPIC 5: Guide project owners to connect their workflow through agent-context

### Why this EPIC exists

EPICs 1 through 4 deliver working machinery, but a project owner who has not read the proposal has no way to understand what agent-context is, why it matters, or how to use it. The factory guide is the canonical entry point for project owners; without an agent-context section, the feature is invisible to its intended audience. Worse, without a design conversation (grilling session) that shapes the seam between the user's own workflow and the factory's machinery, the documentation risks explaining the implementation rather than the user's experience of control and connection.

### Actor Goals

- Human Operator understands how to connect their project's existing documentation, conventions, and practices to the factory through agent-context
- Human Operator understands what they control (their source documents, their concern list in the reading guide, the pace of mode transition) versus what the factory reads (the routing table, never modifying source documents)
- Human Operator customizes the reading guide for their project's concerns (adding, removing, or renaming concern keys)
- New user encounters agent-context during the newcomer-tour and understands where it fits in the factory workflow

### Demo

1. A new project owner opens the factory guide (`factory/docs/factory-guide.md`) and finds an "Agent Context" section.
2. The section explains that `docs/agent-context/` is a routing table pointing at the project's own documentation -- not a copy of it.
3. The guide walks through primary mode (values written directly during greenfield setup) and index mode (pure links to source documents after conventions exist).
4. The guide shows how to customize the reading guide by adding project-specific concerns (e.g. `pipeline:`, `ml:`) and mapping them to index-file sections.
5. The guide explains what the factory reads versus what the project owner controls -- the factory never writes to source documents, and mode transition requires explicit operator confirmation.
6. The operator opens the README and finds a cross-reference to the agent-context section in the factory guide.
7. A new user runs the newcomer-tour and the tour mentions agent-context as part of project setup, pointing at the factory guide for details.

### Scope

**In:**

- Stakeholder grilling session -- a structured design conversation (using the grill-with-docs skill) that shapes the interface between the user's own workflow and the factory's agent-context machinery; the grilling determines what vocabulary the guidance uses, which mental model it presents (routing table vs. knowledge base), what customization points it highlights, and how it explains control boundaries; this is a design step, not a review-after-the-fact
- Factory-guide.md update -- a new "Agent Context" section explaining the two-layer system (reading guide over index files), primary and index modes from the user's perspective, how to connect existing documentation through source pointers, how to customize concerns in the reading guide, and the control boundary (factory reads routing table, never writes source documents)
- README.md update -- cross-reference to the factory-guide agent-context section, replacing stale charter references
- newcomer-tour/SKILL.md update -- agent-context awareness in the onboarding flow, mentioning where agent-context fits in project setup

**Out:**

- Path-only find-replace updates in agents, skills, playbooks, scripts, and hooks (EPIC 4 -- those are mechanical path changes, not user-facing guidance)
- convention and rules.md entries (EPIC 1 -- those are governance documents for factory developers, not project-owner guidance)

### Dependencies

EPIC 1 (convention and templates must exist to reference accurately), EPIC 2 (capture-context skill must exist to document the initialization workflow), EPIC 3 (update-context skill must exist to document the update and transition workflow).

### Boundaries

- Factory documentation: `factory/docs/factory-guide.md` (the authoritative how-to guide for Human Operators) and `factory/README.md` (the entry-point document)
- Catalog: newcomer-tour skill content (resolved through INDEX.yaml, executed by VIRGIL during onboarding)

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                  | Tier     | Size | Basis                                                                                                              |
| ------- | ----------------------------------------------------------- | -------- | ---- | ------------------------------------------------------------------------------------------------------------------ |
| ST-0199 | Grill stakeholder to shape the agent-context user interface | strong   | S    | Low complexity (structured interview via grill-with-docs skill), high uncertainty (outcome depends on stakeholder) |
| ST-0200 | Write agent-context guidance in factory documentation       | standard | S    | Low complexity (structured writing from grilling output), moderate effort (3 files), low uncertainty               |
