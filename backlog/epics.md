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

01. The user copies the four YAML templates (stack, workflow, governance, reading-guides) into `docs/agent-context/` and runs `context-lint`.
02. context-lint reports CX-NULL warnings for every null placeholder field and a CX-MODE info message confirming `mode: primary`.
03. The user introduces a YAML syntax error in `stack.yaml` and re-runs context-lint.
04. context-lint reports a CX-PARSE error for the malformed file.
05. The user fixes the syntax, sets `mode: index`, removes a `source:` pointer from one field, and re-runs.
06. context-lint reports a CX-SRC warning for the field missing its source pointer.
07. The user adds a reference `stack.yaml#frameworks.nonexistent` to `reading-guides.yaml` and re-runs.
08. context-lint reports a CX-GUIDE-REF warning for the unresolvable key path.
09. The user creates a legacy `docs/charter/tech-stack.md` alongside `docs/agent-context/` and re-runs.
10. context-lint reports a CX-FORMAT error for the mixed locations.
11. The user removes `docs/agent-context/`, keeps only `docs/charter/*.md`, and re-runs.
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

- User initializes agent context for a greenfield project by running `capture-context --init`, which creates three index-file templates with `mode: primary` and null placeholders (no reading guide, because no handbook exists yet)
- User onboards brownfield documentation into agent context by running `capture-context --init --scan`, which discovers documentation signals, runs a concern-based interview, populates index files with source pointers (`source:` fields pointing at the project's authoritative documents), and generates `reading-guides.yaml` (the Layer 1 routing file that maps work-type concerns to Layer 2 index sections)
- User uses legacy markdown charter projects without forced migration -- capture-context detects the format and operates on whatever it finds

### Demo

01. The user runs `capture-context --init` in a new, empty project.
02. Three YAML files appear in `docs/agent-context/`: `stack.yaml`, `workflow.yaml`, `governance.yaml`, each with `mode: primary` and null placeholder values.
03. `reading-guides.yaml` is not created (greenfield projects have no handbook to route to).
04. The user runs `context-lint` and gets CX-NULL warnings but no errors -- the files are structurally valid.
05. The user runs `capture-context --init --scan` in a brownfield project that has `pyproject.toml`, `docs/adr/`, and `.github/workflows/`.
06. The scan discovers languages, frameworks, CI/CD configuration, and decision documentation from those files.
07. For each applicable concern (backend, testing, architecture), the concern interview asks the user where conventions are documented and proposes source paths based on the scan.
08. After the interview completes, all four agent-context files are populated with source pointers from the discovered documentation.
09. The user runs `context-lint` and the files pass validation.
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

- User updates agent-context fields as decisions emerge -- writing inline values when `mode: primary`, writing name-and-source pairs when `mode: index`, and recording deferred decisions with `deferred: "reason"` mappings
- User transitions the agent context from primary to index mode -- update-context checks the transition condition (every non-null, non-deferred leaf field across all three index files has a `source:` pointer), prompts the user, and flips all three files atomically in a single commit
- update-context proposes creating `reading-guides.yaml` when the first `source:` pointer is written and no reading guide exists yet

### Demo

01. The user has three index files in `mode: primary` with some null fields (status quo from EPIC 2).
02. The user invokes `update-context` to record a technology choice for `stack.yaml#frameworks.backend`.
03. update-context writes the inline value `FastAPI 0.100` directly to the field.
04. The user invokes `update-context` to add a source pointer for the same field, pointing at `docs/adr/004-use-fastapi.md`.
05. update-context writes both `name: FastAPI` and `source: docs/adr/004-use-fastapi.md` to the field.
06. Since this is the first source pointer and no `reading-guides.yaml` exists, update-context proposes creating the reading guide from the template.
07. The user defers the `data_stores` decision with reason "evaluating options."
08. update-context writes `deferred: "evaluating options"` to the `data_stores` field, replacing any prior value.
09. The user fills source pointers for all remaining non-null, non-deferred fields.
10. update-context detects that the transition condition is met and prompts: "All context fields now have sources. Switch to index mode?"
11. The user confirms. update-context flips `mode` to `index` in all three files in a single commit, strips inline values to names only, and preserves source pointers.
12. The user runs `context-lint` and the index-mode files pass validation.

### Scope

**In:**

- update-context skill -- rename `factory/skills/update-charter/SKILL.md` to `factory/skills/update-context/SKILL.md` with YAML support, mode-aware writing, and mode-transition logic
- Primary-mode writes -- update-context writes inline values directly to index-file fields when `mode: primary`
- Index-mode writes -- update-context writes both `name` and `source` together when `mode: index`; refuses writes without a source pointer in index mode
- Deferred-field handling -- records `deferred: "reason"` as the sole key at the field's leaf position; no coexistence with `name` or `source`
- Mode-transition logic -- checks transition condition (every non-null, non-deferred leaf across all three files has `source:`), prompts the user, executes atomic flip across all three files in one commit, strips inline values to names
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
- User runs any factory workflow (greenfield-development, feature-addition, bug-fix) against a YAML agent-context project or a legacy markdown charter project without path errors
- Legacy projects continue working without migration -- format detection falls back transparently

### Demo

1. The user has a project with `docs/agent-context/` YAML files (status quo from EPICs 1-3).
2. The user runs `grep -r 'docs/charter' factory/agents/ factory/skills/ factory/playbooks/ factory/scripts/ factory/config/` across the active factory code.
3. Zero matches appear (legacy templates under `factory/rulebooks/templates/charter-*.md` are exempt -- retained for backward compatibility).
4. The user triggers the `block-dangerous-git` hook (PreToolUse guard) in a project where `testing.yaml` lives at `docs/agent-context/testing.yaml`.
5. The hook resolves the test command from the new location and correctly allowlists it.
6. The user runs `factory/scripts/phase advance` in the same project.
7. The script resolves `testing.yaml` via format detection and executes the test command.
8. The user repeats steps 4 through 7 in a legacy project with `docs/charter/testing.yaml`.
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

- User understands how to connect their project's existing documentation, conventions, and practices to the factory through agent-context
- User understands what they control (their source documents, their concern list in the reading guide, the pace of mode transition) versus what the factory reads (the routing table, never modifying source documents)
- User customizes the reading guide for their project's concerns (adding, removing, or renaming concern keys)
- New user encounters agent-context during the newcomer-tour and understands where it fits in the factory workflow

### Demo

1. A new project owner opens the factory guide (`factory/docs/factory-guide.md`) and finds an "Agent Context" section.
2. The section explains that `docs/agent-context/` is a routing table pointing at the project's own documentation -- not a copy of it.
3. The guide walks through primary mode (values written directly during greenfield setup) and index mode (pure links to source documents after conventions exist).
4. The guide shows how to customize the reading guide by adding project-specific concerns (e.g. `pipeline:`, `ml:`) and mapping them to index-file sections.
5. The guide explains what the factory reads versus what the project owner controls -- the factory never writes to source documents, and mode transition requires explicit user confirmation.
6. The user opens the README and finds a cross-reference to the agent-context section in the factory guide.
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

- Factory documentation: `factory/docs/factory-guide.md` (the authoritative how-to guide for Users) and `factory/README.md` (the entry-point document)
- Catalog: newcomer-tour skill content (resolved through INDEX.yaml, executed by VIRGIL during onboarding)

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                  | Tier     | Size | Basis                                                                                                              |
| ------- | ----------------------------------------------------------- | -------- | ---- | ------------------------------------------------------------------------------------------------------------------ |
| ST-0199 | Grill stakeholder to shape the agent-context user interface | strong   | S    | Low complexity (structured interview via grill-with-docs skill), high uncertainty (outcome depends on stakeholder) |
| ST-0200 | Write agent-context guidance in factory documentation       | standard | S    | Low complexity (structured writing from grilling output), moderate effort (3 files), low uncertainty               |

______________________________________________________________________

# EPICs -- Progressive Fitting and Session Continuity

Proposal trace: [progressive-fitting-and-session-continuity.md](../docs/proposals/progressive-fitting-and-session-continuity.md)

## EPIC 6: Complete a minimum-viable fitting in under 5 minutes

### Why this EPIC exists

Fitting currently front-loads 30-60 minutes of configuration before the user has seen a single agent work. Step 0 asks for 12 model decisions (4 CLIs x 3 tiers) when the user typically uses one CLI. Step 2 runs a 19-question stakeholder interview covering topics the user may not have decided yet. This EPIC restructures both steps so the user answers only what matters now -- 3 model tiers for their active CLI and 6 essential context questions -- and defers everything else to a later full pass. The result: the factory demonstrates capability before asking for commitment.

### Actor Goals

- User completes a minimum-viable fitting by answering 6 context questions instead of 19, with all other fields marked as deferred
- User configures model tiers (economy, standard, strong model assignments) for only the CLI they actually use, reducing step 0 from 12 decisions to 3
- VIRGIL (the session guide agent) defaults to the minimal pass for brownfield projects and offers the full pass as an explicit follow-up option
- A later `capture-context` run (without `--minimal`) detects deferred fields and presents only those for completion, without re-asking already-answered questions

### Demo

1. The user starts a brownfield fitting. VIRGIL's step 0 asks "Which CLI(s) do you use?" The user selects "Claude Code."
2. VIRGIL walks through 3 model tiers for Claude Code only. The other CLIs keep their defaults or `CONFIGURE-ME` placeholders.
3. VIRGIL's step 2 invokes `capture-context --init --scan --minimal`. The scan runs in full (detecting languages, frameworks, test runners from project files).
4. The interview presents 6 questions. For the 4 questions covered by scan auto-detection (languages, frameworks, testing, linting), the user confirms scan results. The user answers 2 questions manually (how to run locally, branching model).
5. All other agent-context fields are written as `deferred: "full context pass pending"`.
6. The user runs `context-lint` (the validation script) and the output is clean -- deferred values are valid, no nulls.
7. VIRGIL offers: "I have enough to work with. Want to fill in the rest now, or come back to it later?"

### Scope

**In:**

- `--minimal` flag for capture-context -- a new invocation mode (`--init --minimal` for greenfield, `--init --scan --minimal` for brownfield) that interviews on 6 fields only (language/runtime, backend framework, frontend framework, running locally, testing approach, branching model) and pre-fills all other fields with `deferred: "full context pass pending"` before the interview begins so context-lint sees deferred values rather than nulls
- `--minimal` composition with `--scan` -- the discovery scan runs in full; only the interview scope is reduced to the 6 minimal fields; scan results for minimal fields are proposed as answers for confirmation; scan results for non-minimal fields are held, not presented, and wait for the full pass; `reading-guides.yaml` is assembled from confirmed source pointers only, with concerns that have only deferred fields pruned
- Full-pass deferred-field detection -- when the user later runs `capture-context --init` or `--init --scan` without `--minimal`, the skill detects existing deferred fields and presents only those for completion; already-valued fields are shown for confirmation but not re-asked from scratch
- CLI-scoped model matrix -- VIRGIL's fitting step 0 asks "Which CLI(s) do you use?" first; only the selected CLI's three tiers are configured; other CLIs keep existing defaults or `CONFIGURE-ME` placeholders; `fitting.model_matrix_configured` is set to `true` once the active CLI is fully configured
- VIRGIL default invocation -- fitting step 2 invokes `--init --scan --minimal` for brownfield and `--init --minimal` for greenfield by default; VIRGIL offers the full pass as an explicit option after the minimal pass completes

**Out:**

- Changes to the full 19-question interview (the questions themselves are fine; only the default invocation path changes)
- Automatic detection of which questions to defer based on project signals (the 6-question set is fixed, not configurable)
- Cross-session memory or learning progress tracking

### Dependencies

None. This EPIC modifies the capture-context skill definition and VIRGIL's fitting steps, both of which exist and are stable.

### Boundaries

- Skill definition: capture-context SKILL.md (adds `--minimal` invocation mode and deferred-field semantics)
- Agent definition: virgil.md (fitting steps 0 and 2 change their default invocation behavior)

### Size

1 story.

### Building-Block Inventory

| Story   | Capability                                                                                   | Tier     | Size | Basis                                                                                                                       |
| ------- | -------------------------------------------------------------------------------------------- | -------- | ---- | --------------------------------------------------------------------------------------------------------------------------- |
| ST-0207 | Complete fitting with minimal configuration by answering 6 questions and configuring one CLI | standard | M    | Medium effort (two files with substantial text additions), medium complexity (behavioral spec in SKILL.md), low uncertainty |

## EPIC 7: Navigate the session menu with clear descriptions and discoverable help

### Why this EPIC exists

The session menu presents bare playbook names (`poc-spike`, `technical-poc`, `greenfield-development`) with no indication of what each one does. A user who just completed the newcomer tour knows five vocabulary words but has no catalog. Two existing skills -- explain-concept (plain-language explanations of factory concepts) and guided-tour (mid-session reorientation) -- work correctly but appear in no menu, no footer, and no visible affordance. This EPIC surfaces what already exists so the user can find it at the moments confusion is most likely.

### Actor Goals

- User sees one-line descriptions next to every playbook name in the B menu (derived from each playbook's opening paragraph -- the playbook file remains the source of truth)
- User sees a persistent footer in the session menu and B menu that says: "At any point, ask 'what is [concept]?' for a plain-language explanation"
- User can type "?" from the session menu to invoke the guided-tour skill for mid-session reorientation

### Demo

1. The user opens the session menu and sees option "?" after option D: "Where am I? What can I do next?"
2. The user picks B and sees the expanded tree. Each leaf has a one-line description: `a -- poc-spike: build the smallest thing that proves the idea, then throw it away`.
3. At the bottom of the B menu, a footer reads: "At any point, ask 'what is [concept]?' for a plain-language explanation."
4. The user types "what is a gate?" and gets an explain-concept response calibrated to their experience level.
5. The user types "?" and gets a guided-tour reorientation showing where they are and what they can do next.

### Scope

**In:**

- One-line descriptions for every B menu leaf -- each description is derived from the playbook's opening paragraph; descriptions are written into `session-menu.md` so they render as part of the menu presentation
- Explain-concept footer -- a single line added to the session menu and repeated in the B menu, making the existing explain-concept skill discoverable at the point where confusion is most likely
- Guided-tour `?` option -- a new line after option D in the session menu that invokes the existing guided-tour skill; the `?` mnemonic follows CLI convention for help

**Out:**

- Changes to the explain-concept or guided-tour skill definitions (both already work correctly; this EPIC only surfaces them)
- Automatic detection of user confusion to proactively offer explain-concept (explicitly deferred per proposal)

### Dependencies

None. All three skills (explain-concept, guided-tour, newcomer-tour) and the session menu exist and are stable.

### Boundaries

- Session configuration: session-menu.md (menu entries, descriptions, and footer text)
- Catalog: playbook files under `factory/playbooks/` (read to derive one-line descriptions; not modified)

### Size

1 story.

### Building-Block Inventory

| Story   | Capability                                                            | Tier    | Size | Basis                                                                                              |
| ------- | --------------------------------------------------------------------- | ------- | ---- | -------------------------------------------------------------------------------------------------- |
| ST-0208 | Surface navigation aids and playbook descriptions in the session menu | economy | S    | Low complexity (text additions to one file), low uncertainty (all referenced skills already exist) |

## EPIC 8: Resume a partially fitted project without losing progress

### Why this EPIC exists

Three related problems compound into one effect: a returning user or new collaborator cannot reliably resume or inherit a partial fitting. First, VIRGIL's persona constraints ("MUST NOT write code") have no exception clause for playbook transitions, so offering poc-spike after the newcomer tour produces either a refusal or a silent constraint drop. Second, fitting state in `config/project-context.json` is untracked and does not survive a fresh clone, even though the artifacts it describes (agent-context files, pre-commit hooks) are tracked. Third, a partially fitted project shows "want to walk through the fitting?" with no indication of progress. This EPIC fixes all three: the persona transition is made explicit, fitting state is derived from observable artifacts, and progress is surfaced.

### Actor Goals

- User who finishes the newcomer tour and accepts a playbook offer (e.g., poc-spike) sees the model drop the VIRGIL persona and follow the playbook's operational procedure without a refusal or silent constraint drop
- Collaborator who clones a fitted repo and runs init-factory gets fitting keys derived from tracked artifacts -- `agent_context_populated`, `fingerprint_confirmed`, `test_regime_detected`, and `hooks_decided` reflect the observable state of the filesystem, not a stale or missing cache
- Returning user with a partially complete fitting sees a progress summary ("Fitting is 3/5 done -- model matrix, fingerprint, and context populated. Test regime and hooks remain.") and can choose to continue or skip to the menu

### Demo

1. A newcomer completes the newcomer tour. VIRGIL offers poc-spike. The user accepts.
2. The model drops VIRGIL's constraints (including "MUST NOT write code") and reads the poc-spike playbook. The user sees code written without a refusal.
3. A collaborator clones a repo where another user completed the full fitting. The collaborator runs `init-factory`.
4. init-factory checks tracked artifacts: `docs/agent-context/stack.yaml` exists with non-deferred values, `.pre-commit-config.yaml` has the factory marker, `docs/agent-context/testing.yaml` exists. It derives `agent_context_populated: true`, `fingerprint_confirmed: true`, `test_regime_detected: true`, `hooks_decided: true`.
5. Only `model_matrix_configured` is `false` (model.conf is untracked -- model choice is user-specific).
6. `config/project-context.json` is written with `fitting.status: "fitting"` (4/5 keys true).
7. On the next session start, AGENTS.md routes to the `"fitting"` handler. VIRGIL reads the fitting keys and presents: "Fitting is 4/5 done (fingerprint, agent context, test regime, hooks). Model matrix remains. Continue the fitting, or skip to the menu?"
8. The user chooses to continue. VIRGIL resumes at step 0 (model matrix).

### Scope

**In:**

- Explicit persona-transition rule -- an exception clause added to VIRGIL's boundaries: VIRGIL's constraints apply while VIRGIL is the active persona; when the user selects a playbook from the session menu or accepts a playbook offer, the model drops the VIRGIL persona and follows the playbook's operational procedure; VIRGIL's MUST NOTs do not carry into the playbook session
- Newcomer-tour boundary update -- "Do not spawn agents or launch a playbook" becomes "Do not launch a playbook directly -- offer it and let the session menu handle the transition"
- Fitting-state derivation in init-factory -- when `config/project-context.json` exists or is being created, check tracked artifacts against derivation rules: `fingerprint_confirmed` from non-empty observations in project-context.json, `agent_context_populated` from `docs/agent-context/stack.yaml` with at least one non-deferred leaf, `test_regime_detected` from non-null testing fields in workflow.yaml or existence of testing.yaml, `hooks_decided` from factory marker block in `.pre-commit-config.yaml`; `model_matrix_configured` is non-derivable (model.conf is untracked in target projects); when cache disagrees with a derivable artifact, the artifact wins and the cache is overwritten silently; `fitting.status` is derived: `"fitted"` when all keys are true, `"unfitted"` when none are, `"fitting"` otherwise
- Fitting-progress surfacing in AGENTS.md -- handle `"fitting"` as a third state in the session-start flow; when status is `"fitting"`, present a progress summary with completed and remaining steps before offering to continue or skip; step names map to fitting keys: model matrix, project fingerprint, agent context, test regime, pre-commit hooks

**Out:**

- Persona-transition logic for skills invoked within VIRGIL's own session (explain-concept, capture-context, grilling run under VIRGIL's constraints as today -- only playbook selection triggers the transition)
- Cross-session memory or user profiles
- Playbook-level breadcrumbs (explicitly deferred per proposal until proven needed)

### Dependencies

None at the EPIC level. Story-level dependencies exist within this EPIC (fitting-progress surfacing depends on correct derivation).

### Boundaries

- Agent definition: virgil.md (persona-transition exception clause in boundaries section)
- Tour skill: newcomer-tour SKILL.md (boundary wording change)
- Installation script: init-factory (Python derivation logic for fitting keys from tracked artifacts)
- Session configuration: AGENTS.md (routing for `"fitting"` state with progress summary)
- Test suite: tests/factory/test_init_factory.py (derivation logic tests)

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                                      | Tier     | Size | Basis                                                                                                                                       |
| ------- | --------------------------------------------------------------- | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0209 | Add explicit persona transition at the VIRGIL/playbook boundary | economy  | S    | Low complexity (text additions to two files), low uncertainty (behavioral rule, not code)                                                   |
| ST-0210 | Derive fitting state from tracked artifacts in init-factory     | standard | M    | Medium complexity (Python derivation logic with 5 rules, test coverage for each), medium uncertainty (edge cases around artifact detection) |
| ST-0211 | Surface fitting progress when fitting is partially complete     | economy  | S    | Low complexity (text additions to two files), low uncertainty; depends on ST-0210 for correct derived state                                 |

______________________________________________________________________

# EPICs -- Concern-Oriented Agent Context

Proposal trace: [factory-concern-oriented-agent-context.md](../docs/proposals/factory-concern-oriented-agent-context.md)

Supersedes EPICs 1-5 (yaml-charter-lifecycle). Those EPICs delivered the YAML-based agent-context model (all stories done). The concern-oriented model replaces that model entirely -- YAML agent-context files and legacy charter files are both retired. No backward compatibility code for either format.

## EPIC 9: Define the concern model and build the validation gate

### Why this EPIC exists

The YAML-based agent-context model (four files, two modes, source pointers) created maintenance overhead that discouraged upkeep. The concern-oriented model replaces it with a single markdown file (`docs/agent-context.md`) where agents discover what to read by concern name. Before any skill can produce or consume that file, two things must exist: the binding rules that define its structure, and the deterministic validation gate that enforces them. Without these, every subsequent EPIC produces output no one can verify.

### Actor Goals

- `agent-context-composition.md` (the rulebook convention) describes the concern model -- three concern categories (cross-cutting, technical, domain), the `agent-context.md` structure, the controlled vocabulary rule, and the advisory nature of concern declarations
- `concern-lint` (the validation script replacing `context-lint`) validates the concern registry with CTX-\* finding codes: CTX-SECTIONS (category heading structure and concern section completeness), CTX-PATHS (file path resolution for `Read:` and `Boundary:` lines), CTX-LEGACY (flags residual YAML agent-context files or `docs/charter/` directories)
- `concern-lint` replaces `context-lint` in the validate skill (gate #12) and in `.pre-commit-config.yaml`

### Demo

1. The user creates a `docs/agent-context.md` with "Always (cross-cutting)", "Technical concerns", and "Domain concerns" category headings, each containing concern sections with description lines and `Read:` paths.
2. The user runs `concern-lint`. It reports zero findings -- the file is structurally valid (CTX-SECTIONS pass) and all paths resolve (CTX-PATHS pass).
3. The user removes the "Technical concerns" heading and re-runs. `concern-lint` reports a CTX-SECTIONS finding for the missing category.
4. The user restores the heading but changes a `Read:` path to a nonexistent file. `concern-lint` reports a CTX-PATHS finding.
5. The user creates a `docs/agent-context/stack.yaml` alongside `docs/agent-context.md`. `concern-lint` reports a CTX-LEGACY finding for the residual YAML file.
6. The user runs the validate skill. Gate #12 runs `concern-lint` instead of `context-lint`.

### Scope

**In:**

- `agent-context-composition.md` rewrite -- replace the YAML model description (four files, two modes, source pointers, field states, write-path ownership, format exclusivity) with the concern model description (three concern categories and when each is active, `agent-context.md` structure with category headings and concern sections, controlled vocabulary rule and how new concerns enter the registry, advisory nature of concern declarations, `concern-lint` check definitions)
- `concern-lint` script -- a new Python script replacing `context-lint` that validates `docs/agent-context.md` with three checks: CTX-SECTIONS (every expected category heading exists and each concern section has a description line and at least one `Read:` path), CTX-PATHS (every path in a `Read:` or `Boundary:` line resolves to an existing file or glob match), CTX-LEGACY (no YAML agent-context files other than `testing.yaml` or `docs/charter/` directory remain alongside the concern registry)
- Validate skill gate update -- gate #12 runs `concern-lint` instead of `context-lint`
- Pre-commit hook update -- `.pre-commit-config.yaml` hook entry changed from `context-lint` to `concern-lint`
- Test fixtures -- synthetic `agent-context.md` files and residual YAML/charter fixtures under `tests/fixtures/`

**Out:**

- CTX-REFS check (EPIC 11 -- requires `concerns:` field in story frontmatter, which does not exist until the planning-agent story)
- capture-context and update-context skill changes (EPIC 10)
- Agent and skill definition updates (EPICs 11 and 12)
- Deletion of old YAML files from this project (EPIC 12 -- cleanup after all consumers are updated)

### Dependencies

None. This is the foundational EPIC for the concern-oriented model.

### Boundaries

- Rulebook convention: `factory/rulebooks/conventions/agent-context-composition.md` (model definition)
- Validator: `concern-lint` script (Python, replacing `context-lint`)
- Validate skill: `factory/skills/validate/SKILL.md` (gate #12 update)
- Git/pre-commit: `.pre-commit-config.yaml` (hook entry update)

### Size

1 story.

### Building-Block Inventory

| Story   | Capability                                                                                       | Tier     | Size | Basis                                                                                                                          |
| ------- | ------------------------------------------------------------------------------------------------ | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------ |
| ST-0217 | Rewrite the rulebook for the concern model and build concern-lint with CTX-SECTIONS/PATHS/LEGACY | standard | L    | High effort (rulebook rewrite + Python script with 3 checks + gate integration + hook update + test fixtures), low uncertainty |

## EPIC 10: Create and migrate concern-based context

### Why this EPIC exists

The rulebook and lint from EPIC 9 define and enforce the concern model, but no factory skill can produce a concern-format `agent-context.md` yet. Without an updated `capture-context`, greenfield projects have no way to create the file from a repository scan, and existing YAML-based projects have no migration path. The `update-context` skill, which was the write path for YAML index files, has no target in the new model and must be retired.

### Actor Goals

- User creates a concern-based `agent-context.md` from a greenfield repository scan by running `capture-context --init` -- the skill seeds generic cross-cutting concern sections from factory templates, proposes project-specific technical concerns from the detected stack, and proposes domain concerns from the specification if one exists
- User creates a concern-based `agent-context.md` from a brownfield repository scan by running `capture-context --init --scan` -- the skill additionally discovers existing documentation (handbooks, ADRs, specs, cookbooks) and proposes `Read:` paths per concern through a concern-based interview
- User migrates an existing YAML-based agent context to the concern model -- `capture-context` auto-detects the old YAML files, proposes concern sections derived from the YAML content, and on confirmation writes `agent-context.md`, moves `testing.yaml` to `docs/testing.yaml`, and deletes the YAML files
- User who invokes `update-context` sees a deprecation notice pointing to direct `agent-context.md` editing

### Demo

1. The user runs `capture-context --init` in a new project that has `pyproject.toml` with FastAPI and Vue dependencies.
2. `agent-context.md` appears at `docs/agent-context.md` with six generic cross-cutting concern sections (Branching, Committing, Testing discipline, Review, Scope discipline, Security), plus proposed technical concerns ("backend", "frontend") derived from the detected stack.
3. The user runs `concern-lint` and the file passes validation.
4. The user runs `capture-context --init --scan` in a brownfield project that has `docs/handbook/backend/conventions.md` and `docs/adr/`.
5. The concern interview proposes `Read:` paths from the discovered documentation. The user confirms.
6. The user runs `capture-context` (bare, no flags) in a project that has `docs/agent-context/stack.yaml`. The skill detects the YAML format and offers migration.
7. The user confirms. `agent-context.md` is written with concern sections derived from the YAML content. `testing.yaml` moves to `docs/testing.yaml`. The old YAML files and `docs/agent-context/` directory are deleted.
8. The user invokes `update-context`. A deprecation notice appears, pointing to direct `agent-context.md` editing. No files are modified.

### Scope

**In:**

- capture-context skill rewrite for concern model -- `capture-context --init` (greenfield): scan repository for languages, frameworks, test runners, and documentation structure; seed generic cross-cutting concerns from factory; propose project-specific technical concerns from detected stack; propose domain concerns from scope-map areas if specification exists; write `docs/agent-context.md` with confirmed concerns, each section carrying a description line and resolved file paths
- capture-context brownfield mode -- `capture-context --init --scan`: same as greenfield plus documentation discovery (handbooks, ADRs, specs, cookbooks) and concern-based interview ("I found these docs for the backend concern -- anything missing?")
- YAML migration trigger -- bare `capture-context` invocation (no flags) auto-detects old YAML agent-context files; proposes concern sections derived from YAML content (cross-cutting from governance.yaml, technical from stack.yaml, routing from reading-guides.yaml); on confirmation writes `agent-context.md`, moves `testing.yaml` to `docs/testing.yaml`, deletes YAML files and `docs/agent-context/` directory
- `--minimal` variants dropped -- the concern model's simpler structure makes the minimal/full distinction unnecessary
- update-context retirement -- skill body replaced with a deprecation notice pointing to direct `agent-context.md` editing; invoking it produces no error and no side effects
- YAML template deletion -- `factory/rulebooks/templates/context-*.yaml` deleted (no longer needed; capture-context seeds concerns from factory-internal lists, not template files)

**Out:**

- Planning-agent and developer-agent concern consumption (EPIC 11)
- Agent and skill definition path updates (EPIC 12)
- testing.yaml resolution chain updates in other consumers (EPIC 12 -- capture-context handles it during migration, but crap-score, detect-test-regime, and init-factory need separate updates)

### Dependencies

EPIC 9 (concern-lint must exist to validate capture-context output; the rulebook defines what capture-context must produce).

### Boundaries

- Skill definition: `factory/skills/capture-context/SKILL.md` (rewrite from YAML to concern model)
- Skill definition: `factory/skills/update-context/SKILL.md` (body replaced with deprecation notice)
- State file: `docs/agent-context.md` (output artifact)
- YAML templates: `factory/rulebooks/templates/context-*.yaml` (deleted)

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                                                         | Tier     | Size | Basis                                                                                                                         |
| ------- | ---------------------------------------------------------------------------------- | -------- | ---- | ----------------------------------------------------------------------------------------------------------------------------- |
| ST-0218 | Rewrite capture-context greenfield mode to produce agent-context.md with concerns  | standard | M    | Medium complexity (scan + concern proposal + markdown output), low uncertainty (scan logic reused from existing skill)        |
| ST-0219 | Rewrite capture-context brownfield mode with documentation discovery and interview | standard | M    | Medium complexity (doc discovery + concern-based interview), low uncertainty (interview pattern reused from existing skill)   |
| ST-0220 | Auto-detect YAML format and offer interactive migration; retire update-context     | standard | M    | Medium complexity (YAML-to-concern mapping + file relocation + deletion), medium uncertainty (YAML content varies by project) |

## EPIC 11: Route agents by concern during planning and implementation

### Why this EPIC exists

The concern model exists (EPIC 9) and can be produced (EPIC 10), but no agent uses it yet. The core payoff of the concern-oriented model is that a planning-agent declares which concerns a story touches and a developer-agent reads only the matching context sections -- replacing hardcoded file lists with concern-driven routing. Without this EPIC, the concern registry is a document no agent consults.

### Actor Goals

- Planning-agent (the agent that breaks specifications into backlog stories) writes a `concerns:` field into each story's frontmatter, declaring which domain and technical concerns apply, drawn from the controlled vocabulary in `agent-context.md`
- Planning-agent proposes new concern sections for user confirmation when a story needs a concern not in the registry
- backlog-lint (the story validation script) validates the `concerns:` field schema and concern-lint validates that declared concern names match headings in `agent-context.md` (CTX-REFS check)
- Developer-agent (the agent that implements a single story) reads its story's `concerns:` field and follows the matching sections in `agent-context.md` instead of a hardcoded file list

### Demo

1. The planning-agent writes a story with `concerns: {domain: [billing], technical: [backend, data-storage]}` in its frontmatter.
2. The user runs `backlog-lint`. It accepts the `concerns:` field without error.
3. The user runs `concern-lint`. The CTX-REFS check confirms that "billing", "backend", and "data-storage" all have matching headings in `agent-context.md`.
4. The user changes "billing" to "invoicing" (which has no heading). `concern-lint` reports a CTX-REFS finding.
5. The planning-agent encounters an unregistered concern "payments". It proposes a new concern section (name, description, initial file list) for user confirmation instead of coining the name silently.
6. A developer-agent is dispatched with the story. It reads the `concerns:` field, follows the "billing", "backend", and "data-storage" sections in `agent-context.md`, and loads only the relevant conventions and specs.

### Scope

**In:**

- Planning-agent update -- write `concerns:` field into story frontmatter from the controlled vocabulary in `agent-context.md`; when a story needs a concern not in the registry, propose the new section (name, description, initial file list) for user confirmation before adding it
- backlog-lint schema extension -- accept `concerns:` as a valid frontmatter field with structure `{domain: [string], technical: [string]}` (both keys optional)
- Story template update -- add `concerns:` to the frontmatter schema in `factory/rulebooks/templates/story.md`
- CTX-REFS check in concern-lint -- validate that every concern name in any story's `concerns:` frontmatter has a matching heading in `agent-context.md`
- Developer-agent update -- read the story's `concerns:` field; for each declared domain and technical concern, follow the matching section in `agent-context.md` to discover which files to read; replace the current hardcoded project-native file list approach

**Out:**

- Implementation-agent (dispatcher) changes -- concern resolution is implicit via the include chain, no dispatcher logic needed
- Updates to other agents (virgil, reconciliation-agent, etc.) -- EPIC 12

### Dependencies

EPIC 9 (concern-lint must exist for CTX-REFS; the rulebook defines the concern categories and controlled vocabulary rule).

### Boundaries

- Agent definition: `factory/agents/planning-agent.md` (writes `concerns:` and proposes new concerns)
- Agent definition: `factory/agents/developer-agent.md` (reads `concerns:` and follows matching sections)
- Validator: `factory/scripts/backlog-lint` (schema extension for `concerns:` field)
- Validator: `concern-lint` (CTX-REFS check addition)
- Template: `factory/rulebooks/templates/story.md` (frontmatter schema update)

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                                           | Tier     | Size | Basis                                                                                                        |
| ------- | ------------------------------------------------------------------------------------ | -------- | ---- | ------------------------------------------------------------------------------------------------------------ |
| ST-0221 | Write concerns into story frontmatter and validate concern references                | standard | M    | Medium complexity (planning-agent behavioral change + backlog-lint schema + CTX-REFS check), low uncertainty |
| ST-0222 | Read story concerns in developer-agent and follow matching agent-context.md sections | economy  | S    | Low complexity (prose update to developer-agent definition + implementation-agent context), low uncertainty  |

## EPIC 12: Propagate concern model and relocate testing.yaml

### Why this EPIC exists

EPICs 9 through 11 deliver the concern model, its production tooling, and its consumption by planning and development agents. But the rest of the factory still references `docs/agent-context/*.yaml` paths, `docs/charter/` fallbacks, and project-native file lists in agent and skill definitions. Until every consumer resolves context through the concern registry and `testing.yaml` sits at its new location (`docs/testing.yaml`), a project using the concern model will break on its first factory workflow outside of planning and development. This EPIC is the wiring pass that makes the concern model usable end-to-end.

### Actor Goals

- `testing.yaml` resolves at `docs/testing.yaml` across all consumers -- `detect-test-regime` (the skill that writes it), `crap-score` (the gate script that reads it), `init-factory` (the setup script that scaffolds it), and every agent definition that references its path
- `virgil` (the session-guide agent) references `agent-context.md` instead of YAML files during fitting
- `reconciliation-agent` (the post-implementation documentation reconciler) replaces its YAML-based agent-context health check (Step 6: compare against `context-interview-guide.yaml`) with a concern-registry health check (verify that every concern section has valid `Read:` paths and that the concern vocabulary matches the project's documentation structure)
- `init-factory` generates the appropriate CLI-specific include directive for `docs/agent-context.md` (Claude Code: `@docs/agent-context.md` in CLAUDE.md; Copilot: reference from `.github/` instructions; Pi: reference from `.pi/` instructions; Codex: reference from `.codex/` instructions)
- All agent and skill definitions carry no project-native file lists (`docs/handbook/`, `docs/spec/supplementary_specs/`, `docs/adr/` paths in `inputs:` lists) -- they reference concerns or factory-canonical artifacts only
- Old YAML templates (`factory/rulebooks/templates/context-*.yaml`) are deleted and old YAML files can be deleted without breaking any factory agent, skill, or gate

### Demo

1. The user runs `detect-test-regime`. It writes `testing.yaml` at `docs/testing.yaml`.
2. The user runs `crap-score`. It resolves `testing.yaml` at `docs/testing.yaml`.
3. The user runs `init-factory`. It scaffolds `testing.yaml` at `docs/testing.yaml` and generates `@docs/agent-context.md` in the CLI orientation file.
4. The user runs `grep -rn 'docs/agent-context/\*.yaml\|docs/charter/' factory/agents/ factory/skills/`. Zero matches.
5. The user runs `grep -rn 'docs/handbook/\|docs/spec/supplementary_specs/' factory/agents/`. Zero matches in `inputs:` lists (factory-canonical paths like `docs/spec/scope-map.md` remain).
6. The user runs the reconciliation-agent. Its Step 6 validates concern sections in `agent-context.md` instead of comparing against `context-interview-guide.yaml`.
7. The user deletes `docs/agent-context/stack.yaml`, `workflow.yaml`, `governance.yaml`, `reading-guides.yaml`, and the `docs/agent-context/` directory. No factory workflow breaks.

### Scope

**In:**

- testing.yaml relocation -- move `testing.yaml` from `docs/agent-context/testing.yaml` (or `docs/charter/testing.yaml`) to `docs/testing.yaml`; update the resolution path in `detect-test-regime` skill, `crap-score` script, `init-factory` script, and all agent definitions that reference the old path; no fallback to legacy paths
- virgil update -- fitting logic references `agent-context.md` instead of YAML files; fitting step 2 invokes the concern-model `capture-context` instead of the YAML-model version
- reconciliation-agent update -- Step 6 replaced: instead of comparing against `context-interview-guide.yaml` template and YAML index files, validate that every concern section in `agent-context.md` has valid `Read:` paths and that the concern vocabulary matches the project's documentation structure
- init-factory update -- generate CLI-specific include directive for `docs/agent-context.md` per CLI type (Claude Code, Copilot CLI, Pi, Codex); scaffold `testing.yaml` at `docs/testing.yaml` instead of `docs/agent-context/testing.yaml`
- Agent and skill definition sweep -- replace project-native file lists (`docs/handbook/`, `docs/spec/supplementary_specs/`, `docs/adr/` in `inputs:` sections) with concern references ("follow the concerns relevant to your work in `agent-context.md`"); factory-canonical artifact paths (`docs/spec/scope-map.md`, `docs/arc42/architecture.dsl`, `backlog/ST-*.md`, etc.) stay as concrete paths
- YAML template deletion -- `factory/rulebooks/templates/context-*.yaml` (stack, workflow, governance, reading-guides, interview-guide) deleted
- YAML file cleanup -- old `docs/agent-context/*.yaml` files (stack, workflow, governance, reading-guides) deletable without breaking any factory consumer

**Out:**

- Automated concern derivation from code changes (explicitly deferred per proposal)
- Concern-level impact analysis (explicitly deferred per proposal)
- Cross-project concern federation (explicitly deferred per proposal)

### Dependencies

EPIC 9 (concern model must be defined and lint must exist). EPIC 10 (capture-context must produce the concern format; migration must handle testing.yaml relocation during project migration). EPIC 11 (planning-agent and developer-agent concern consumption must exist before the sweep removes their project-native file lists).

### Boundaries

- Skill definition: `factory/skills/detect-test-regime/SKILL.md` (testing.yaml path update)
- Script: `factory/scripts/crap-score` (testing.yaml resolution update)
- Script: `factory/scripts/init-factory` (testing.yaml path + CLI include directive generation)
- Agent definitions: `factory/agents/virgil.md`, `factory/agents/reconciliation-agent.md`, and all other agents (path updates + concern references)
- Skill definitions: all skills referencing agent-context or charter paths
- YAML templates: `factory/rulebooks/templates/context-*.yaml` (deletion)

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                                                              | Tier     | Size | Basis                                                                                                                               |
| ------- | --------------------------------------------------------------------------------------- | -------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------- |
| ST-0223 | Relocate testing.yaml to docs/testing.yaml and update all resolution chains             | standard | M    | Medium complexity (path updates in ~8 files across skills, scripts, and agent definitions), low uncertainty                         |
| ST-0224 | Update virgil, reconciliation-agent, and init-factory for the concern model             | standard | M    | Medium complexity (3 behavioral updates: fitting references, health check procedure, include directive generation), low uncertainty |
| ST-0225 | Replace project-native file lists with concern references and delete old YAML templates | economy  | M    | Low complexity (mechanical find-replace across ~15 agent/skill definitions), high effort (many files), low uncertainty              |
