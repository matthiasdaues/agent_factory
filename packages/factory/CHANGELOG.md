# Changelog

## 0.10.0 — 2026-09-09

Agent-ready story format and test-design layer redistribution. Stories
produced by the planning agent are now directly implementable by a
developer-agent in a single pass — no post-hoc rewrite step. Test design
moves from planning time to implementation time, and the developer-agent
owns test authoring through a two-pass TDD model.

### Features

- **13-section story template.** Replaces the 7-section body (Demo,
  Acceptance Criteria, Scope, Terminology, Notes for the Implementer)
  with 13 sections: Goal, Domain Rule, Demo Scenario, Affected Paths,
  Inputs, Outputs, Required Behavior (conditional), Constraints,
  Suggested Agent Plan, Acceptance Criteria, Verification, Out of Scope,
  Agent Stop Conditions. Each section is defined so a developer-agent can
  implement the story without rereading the planning context.
- **`risk_level` frontmatter field.** Optional enum (`low | medium | high`) in the story template and backlog-lint. Validated with `BL-ENUM`
  error code. Three tests added.
- **`touches` hygiene rule.** Documented in the story template under
  Affected Paths. Rules: most specific existing directories only, no
  parent+child overlap, no speculative paths for directories that do not
  exist yet, every entry must resolve to an existing directory or one
  created by a story in `deps`.
- **Composition rules updated.** Rule 1 becomes "Goal First, then Demo"
  — write the Goal statement before the Demo Scenario. Rule 4 added:
  "Constraints Are Boundaries" — every must-not from ADRs, conventions,
  testing regime, and scope exclusions goes in Constraints.
- **Agent-answerability quality gate.** Eight concrete checks mapping
  each agent question to the story section that must answer it (Goal,
  Affected Paths, Domain Rule, Inputs, Acceptance Criteria, Verification,
  Out of Scope, Agent Stop Conditions).
- **International readability gate.** Six sentence-level checks: no
  idioms, no ambiguous pronouns, short sentences, active voice,
  consistent domain terms, abbreviations spelled out.
- **Goal column in write-epics.** Building-block inventory includes a
  Goal column (one sentence of concrete behavior per anticipated story).
  Domain Rules subsection per EPIC lists invariants that seed each
  story's Domain Rule section.
- **Goal column in story-slices.** Slice table expanded from 4 to 5
  columns with a Goal column between Capability and Boundaries crossed.
- **11 section-filling instructions.** Phase 4 story-writing skill
  (`create-backlog-stories`) rewritten with explicit instructions for
  each new section: Goal derivation, Domain Rule extraction, Demo as
  numbered steps, Affected Paths from codebase survey, Inputs as reading
  manifest, Outputs with behavioral detail, Required Behavior
  (conditional), Constraints from ADRs, Suggested Agent Plan,
  Verification from `testing.yaml`, Agent Stop Conditions from risk and
  ambiguity.
- **Plain-language pass.** Added to `create-backlog-stories` after the
  quality gate: reread Goal, Domain Rule, and Demo Scenario for
  understandability before presenting the backlog.
- **Developer-agent cue migration.** Step 1 completeness check uses Goal
  instead of Demo/Scope. Step 2 pre-existing test lookup reads from
  Inputs instead of Notes for the Implementer. Backward compatibility
  preserved: `#### Failure scenarios` and `#### Prior Tests` paths
  unchanged.
- **Testability probe.** New mandatory step 2.5 in the create-backlog
  sequence, between write-epics and story-slices. Writes a testability
  paragraph and ownership table per EPIC into `backlog/epics.md`.
  Replaces the former test-design skill's planning-time output.
- **Two-pass TDD model.** Developer-agent owns test authoring through
  two passes: pass 1 writes acceptance-criteria tests (Red-Green), pass 2
  invokes the `test-design` skill post-GREEN for integration and
  edge-case tests. `tests:` and `test-design-pass:` frontmatter fields
  populated by the developer-agent at commit time.
- **test-design skill rewrite.** Operates at implementation time, not
  planning time. Reads ownership assignments from the testability probe,
  classifies owned contracts by risk class, identifies untested
  integration paths, and authors test files.
- **test-design-verify gate.** Validates that stories with test-design
  output have consistent `tests:` and `test-design-pass:` fields.
  Implicitly enabled when the story contains Failure scenarios or Prior
  Tests sections.
- **Vue Best Practices skill.** New skill for Vue.js frontend
  implementation guidance, loaded by the developer-agent when a story's
  outputs touch `packages/server` (Vue frontend).

### Fixes

- **Stale Notes for the Implementer references.** Removed from story
  template, all four create-backlog skills, and developer-agent.
  Replaced with appropriate new sections (Inputs, Constraints,
  Verification).
- **Quality gate count.** Parent skill correctly states "Two quality
  gates" (Agent-Answerability and International Readability), not three.
- **Story template stray fences.** Removed trailing empty code fences
  from the template body.
- **Dispatch script scope.** Reverted out-of-scope modifications to the
  dispatch script made during implementation dispatch.
- **User-prompt questions restored.** MoSCoW priorities, missing stories,
  and dependency reordering prompts restored in `create-backlog-stories`
  after accidental removal during skill rewrite.
- **Hook search string.** Fixed wrong search string in
  `block-dangerous-git.sh`.
- **Reconciliation test traceability.** Added `tests:` field audit and
  contract ownership coverage check to the reconciliation agent.
- **Testing strategy documentation.** Two-pass test authoring model
  documented in `testing-strategy.md`.

### Documentation

- **Agent-ready story format proposal.** Full proposal at
  `docs/proposals/implemented/agent-ready-story-format.md` with two
  review rounds and all findings resolved.
- **Test-design layer redistribution proposal.** Full proposal at
  `docs/proposals/implemented/test-design-layer-redistribution.md`.
- **migrate-proposal script.** New script to move accepted proposals
  from `docs/proposals/` to `docs/proposals/implemented/`.
- **Campaign retrospective.** Filed at
  `docs/reviews/retro-2026-09-09-agent-ready-story-format.md`.

## 0.9.0 — 2026-09-09

Concern-oriented agent context and code-first planning. Agents discover
what to read by concern name, not by file path. Planning starts from the
codebase as ground truth and derives stories as deltas from existing code
to specified capabilities.

### Features

- **Concern-oriented agent context.** Replaces the four YAML agent-context
  files (`stack.yaml`, `workflow.yaml`, `governance.yaml`,
  `reading-guides.yaml`) with a single CLI-agnostic markdown file:
  `docs/agent-context.md`. Agents discover project-native knowledge
  (supplementary specs, ADRs, handbooks, architecture views) through
  concern sections carrying `Read:` paths. Three concern categories:
  cross-cutting (always active), technical (per story), domain (per
  story). Factory-canonical artifacts (`scope-map.md`, `.feature` files,
  `testing.yaml`) remain as concrete paths.
- **concern-lint.** New deterministic linter replacing `context-lint`.
  Four checks: CTX-SECTIONS (category headings and Read paths),
  CTX-PATHS (file resolution), CTX-REFS (story concern vocabulary
  matches registry), CTX-LEGACY (flags residual YAML files).
- **Concern declarations in story frontmatter.** Planning agent writes
  `concerns: {domain: [...], technical: [...]}` into each story.
  Developer and implementation agents follow matching sections in
  `agent-context.md`.
- **capture-context rewrite.** Greenfield (`--init`) and brownfield
  (`--init --scan`) modes produce concern sections instead of YAML files.
  Auto-detects old YAML format and offers interactive migration.
- **update-context retired.** Skill body replaced with a deprecation
  notice pointing to direct `agent-context.md` editing.
- **testing.yaml relocated.** Moved from `docs/agent-context/testing.yaml`
  to `docs/testing.yaml`. Resolution chain updated in `concern-lint`,
  `detect-test-regime`, `crap-score`, and all agent definitions.
- **YAML migration path.** `capture-context` auto-detects old YAML
  agent-context format and offers interactive migration to the concern
  model.
- **Code-first planning.** Planning agent and all five backlog skills
  reworked. New principle "Code Is Ground Truth" — planning starts from
  the codebase as it stands, not from an aspirational architecture. EPIC
  decomposition is the delta between existing code and specified
  capabilities. Step 0 (codebase survey) elevated to foundation;
  Step 1 reframed as gap analysis.
- **Concern-routed inputs.** Planning agent and skills discover project-
  native knowledge through `docs/agent-context.md` concern sections
  instead of hardcoded file paths. Technical concerns route to source
  directories, architecture views, and conventions. Domain concerns route
  to supplementary specs and domain vocabulary.
- **Agent definitions updated.** Project-native file lists replaced with
  concern references across requirements-agent, architecture-agent,
  architecture-review-agent, qa-agent, spec-review-agent, developer-
  agent, implementation-agent, virgil, and reconciliation-agent.

### Fixes

- **spec-lint required artifacts.** Removed `prd.md` and
  `supplementary_specs/validation-rules.md` from `REQUIRED_ARTIFACTS` —
  neither is produced by the current requirements workflow. Tests updated.
- **dispatch-ledger path.** Corrected path reference in `rules.md`.
- **Reconciliation findings.** Resolved 16 RECON findings from the
  concern-oriented context implementation.
- **QA findings.** Fixed hook `testing.yaml` resolution and `concern-lint`
  exit code.

### Documentation

- **Writing rules.** Added "international team English" to writing
  conventions.
- **Concern-oriented context proposal.** Full proposal at
  `docs/proposals/factory-concern-oriented-agent-context.md` with two
  review rounds and all findings resolved.

## 0.8.0 — 2026-09-08

Progressive fitting and session continuity. Reduces the fitting interview
from 19 questions to 6 for the minimum-viable pass, surfaces navigation
aids in the session menu, resolves the VIRGIL/playbook persona conflict,
and derives fitting state from tracked artifacts so collaborators who
clone a fitted repo inherit the team's fitting decisions.

### Features

- **Minimal fitting pass.** `capture-context --init --scan --minimal`
  limits the interview to 6 questions (languages, frontend/backend
  frameworks, testing, running locally, branching model). Remaining
  fields are set to `deferred: "full context pass pending"` and
  completed in an optional full pass. `--init --minimal` (without
  `--scan`) covers greenfield projects.
- **Artifact-derived fitting state.** `init-factory` re-derives four of
  five fitting keys (`fingerprint_confirmed`, `agent_context_populated`,
  `test_regime_detected`, `hooks_decided`) from tracked artifacts
  (`docs/agent-context/`, `.pre-commit-config.yaml`,
  `config/project-context.json`) on every run. A collaborator who clones
  a fitted repo and runs `init-factory` inherits the team's fitting
  decisions instead of seeing everything reset to false.
  `model_matrix_configured` is cache-only — `config/model.conf` is
  gitignored and user-specific.
- **Fitting progress display.** When `fitting.status` is `"fitting"`,
  the AGENTS.md orientation file counts completed vs. remaining steps
  and offers to resume or skip. A note clarifies that the summary
  trusts the cached values and suggests `init-factory --update .` after
  pulls to reconcile.
- **Session menu descriptions.** Each B-menu playbook entry now shows a
  one-line description drawn from the playbook's opening paragraph.
  `explain-concept` is surfaced as a footer hint. The `?` option
  launches a guided-tour reorientation skill.

### Fixes

- **VIRGIL persona transition.** VIRGIL's boundaries section now
  includes an exception clause: when a playbook is selected, the model
  drops the VIRGIL persona and follows the playbook's operational
  procedure. Resolves the conflict where VIRGIL's "MUST NOT write code"
  boundary blocked playbook execution.
- **`_fitting_status` missing-key safety.** Uses `.get(k, False)`
  instead of direct key access, preventing `KeyError` on hand-edited
  `project-context.json` with missing fitting keys.
- **`_reconcile_project_context` conditional write.** Only writes
  `project-context.json` when derived keys actually changed, avoiding
  unnecessary file touches.
- **Minimal interview defer removed.** The 6 minimal fields no longer
  offer "defer" as an action — all 6 must be answered per the design
  intent.
- **Session menu qa-agent format.** Reformatted to the `name: description` style matching all other B-menu entries.
- **`dispatch_lib` YAML document marker.** `_stdlib_load` now skips
  `---` lines instead of treating them as key-value pairs.

### Documentation

- **`_parse_simple_yaml_mapping` docstring.** Documents the known
  limitation that comment stripping via `split('#')` does not respect
  quoted strings.
- **virgil.md line-break fix.** Corrected a mid-sentence line break in
  the minimal fitting step description.

## 0.7.0 — 2026-09-07

Hardens the update path and closes the documentation gap between script
mechanism and user-facing reference.

### Features

- **Update-factory modification detection.** `update-factory` now
  compares the installed `factory/` against per-file SHA-256 checksums
  recorded at install time (`.agent-factory/factory-checksums.json`).
  Modified, added, and removed files are reported individually. The
  update stops (exit 2) when user changes are detected. `--force`
  preserves changed files under
  `.agent-factory/factory-user-changes/<timestamp>/` and proceeds;
  `--check` reports without touching anything. Rollback on failure
  restores the previous `factory/` automatically.
- **`--add` / `--remove` CLI management.** Incrementally add or remove
  CLI wiring after install — dot-directories, symlinks, guardrails,
  step guards, usage capture, freshness hooks, and generated agents —
  without re-running the full installer. The root `init-factory` wrapper
  now forwards `--add` and `--remove` to the underlying script.
- **Factory fitting completed.** Agent-context YAML files populated
  (`stack.yaml`, `workflow.yaml`, `governance.yaml`,
  `reading-guides.yaml`) and `config/model.conf` configured with
  concrete model IDs for the Agent Factory project itself.

### Fixes

- **step-guard bail-early.** Guard-existence and jq-availability checks
  now run before stdin/event parsing, so missing infrastructure exits 0
  instead of crashing the session with "hook errored".

### Documentation

- **README reference tables expanded.** CLI flag tables for both scripts;
  "What init-factory creates" table extended from 8 to 16 rows covering
  step guard hooks, freshness check, usage capture hooks, generated
  agents, hook config, project-context.json, test regime, usage runtime,
  usage lifecycle, and install checksums.
- **Factory guide expanded.** "What init-factory put on your disk"
  section adds `config/project-context.json` and
  `docs/agent-context/testing.yaml`. "Updating it again" section now
  documents `--check`, `--force`, and `--add`/`--remove` with code
  examples. New troubleshooting entry for dangling `origin/HEAD` repair.
- **Install section rewritten.** Explains wrapper delegation, update
  workflow, and CLI add/remove in dedicated subsections.

## 0.6.0 — 2026-09-07

Documentation release. Closes the gap between running `init-factory` and
starting your first playbook, and hardens the hooks and rulebook for
day-to-day use.

### Documentation

- **Onboarding bridge.** Getting Started now explains what `init-factory`
  put on disk — `project-context.json`, `model.conf`, `agent-context/` —
  so newcomers are not surprised when a playbook references them. Context
  added as a fifth vocabulary entry; INDEX.yaml positioned as a human
  reference, not just a machine lookup.
- **Newcomer tour expanded.** Tour steps now cover config artifacts and
  the fitting session, with greenfield model-matrix awareness in VIRGIL.
- **READMEs refreshed.** Root and `packages/factory/` READMEs updated
  for current structure.
- **Nine broken doc links repaired.** `orchestrator/` →
  `packages/orchestrator/`, `tests/orchestrator/` → `tests/factory/`,
  `spec/use_cases/` → `~archive/spec/use_cases/`, and one dead README
  anchor removed.

### Features

- **Factory-freshness check.** A new hook warns (never blocks) on the
  first tool call of each session when the installed `factory/` is out of
  sync with `packages/factory/`. Implemented for all CLIs: bash hook
  (Claude/Copilot/Codex), TypeScript extension (Pi), and Copilot hook
  config. `init-factory` stamps and `update-factory` refreshes the tree
  hash.

### Fixes

- **step-guard: no manifest, no restriction.** The empty-path rejection
  fired before checking whether a step manifest was loaded, blocking
  sessions without `.current-work/current-step.yml`. Reordered: no
  manifest means no restrictions. Adds a debug dump for path-extraction
  misses.
- **Codex skill resolution path.** The rulebook's INDEX.yaml resolution
  example said `.codex/skills/` but init-factory installs skills to
  `.agents/skills/`.

## 0.5.0 — 2026-09-07

First versioned release. Factory version is tracked in `factory/VERSION`
and recorded in the install manifest (`.agent-factory/factory-install.json`
→ `factory_version`).

### Fitting lifecycle

The factory now learns your project before it starts working. When
init-factory runs against an existing codebase, it scans for languages,
frameworks, package managers, CI, linters, test runners, and docs
structure. The results go into `config/project-context.json` with a
fitting state that tracks what has been confirmed.

- **Brownfield projects** get `fitting.status = "unfitted"`. The first
  session offers a guided fitting — a short walk-through to confirm the
  scan, populate agent context, configure the model matrix, and decide on
  hooks.
- **Greenfield projects** (no signals detected) get
  `fitting.status = "greenfield"` and skip the fitting entirely.
- Fitting progress persists across sessions. Stop any time; the next
  session picks up where you left off.

### Selective CLI wiring

`init-factory` now asks which CLIs you use and wires up only those. Pass
`--cli claude copilot` or choose interactively. Add a CLI later with
`init-factory --add copilot`; remove one with `init-factory --remove pi`.

### One-hop orientation

The CLI orientation file (`AGENTS.md` / `CLAUDE.md` /
`copilot-instructions.md`) is self-contained for the model's first turn.
It checks fitting state and presents the session menu without chaining to
a second file. Weak models that read only the orientation file still do
the right thing.

VIRGIL is demoted from mandatory session persona to optional enrichment.
Strong models that chain to `virgil.md` get richer guidance; weak models
skip it and still work.

### Model matrix

`config/model.conf` is now generated with only the installed CLIs'
stanzas, using `CONFIGURE-ME` placeholders instead of real model IDs. The
file includes a howto header with per-CLI model ID examples and validation
instructions. VIRGIL's fitting step 0 walks through configuration.

### Orientation non-interference

init-factory never overwrites an existing instruction file. Four cases:
no file → symlink; our symlink → skip; foreign symlink → leave it;
existing file → prepend a marker-fenced block. `remove-factory` reverses
all of them.

### Hooks

- `step-guard.sh` exits 0 gracefully when `factory/scripts/step-guard` is
  absent (fresh clone, partial install).
- Brownfield projects with an existing `.pre-commit-config.yaml` get no
  automatic hook merge — deferred to the fitting session.

### Documentation

- README rewritten: before/after value contrast, reversibility as
  first-class promise, fitting mention for brownfield.
- All eight newcomer-path doc gaps closed (model matrix, tiers, stale ruff
  refs, project.json, directory layout, factory README, agent context).
- Pre-commit hook comments rewritten for clarity.
- "Operator" → "user" across 127 files.
- Editorial pass over all 58 skills.
- Orientation architecture documented in the init-factory proposal.

### Monorepo

Product source lives under `packages/factory/`. The root `factory/` is
the installed copy (git-ignored), synced by `update-factory`. Root
`init-factory` is a thin wrapper.
