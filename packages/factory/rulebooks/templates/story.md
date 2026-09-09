---
title: Backlog Story Template
version: 2.1.0
---

# Backlog Story Template

Skeleton for a single `backlog/ST-NNNN.md` file. Governed by [create-backlog skill](../../skills/create-backlog/SKILL.md) and validated by `factory/scripts/backlog-lint`.

## Frontmatter

```yaml
---
id: ST-0001                       # ST-NNNN, zero-padded, unique; matches the filename
epic: Domain Entities             # the EPIC this story belongs to (references a section in backlog/epics.md)
title: Define domain entity dataclasses
tier: economy                     # economy | standard | strong — the model tier this story's work needs
status: pending                   # pending | in_progress | review | blocked | done
risk_level: low                   # optional; low | medium | high — the risk class of this story
deps: [ST-0002]                   # story ids that block this one (optional)
traces: [scope-map#rule-name, ADR-0003]  # scope-map Rule / ADR / component ids this story implements (optional)
touches: [src/orchestrator/, tests/unit/orchestrator/]
                                  # directory prefixes the story is expected to work within;
                                  # used by the dispatcher for overlap detection and scope enforcement
concerns: {domain: [billing], technical: [backend, data-storage]}
                                  # optional; declares which domain and technical concerns the
                                  # story touches. Both keys are optional. Names must match ###
                                  # headings in docs/agent-context.md. Cross-cutting concerns
                                  # are never declared (always active).
quality-gates: [crap-score, mutation-analysis, dependency-check]
                                  # optional; list the semantic gates that apply to this story.
                                  # Default precedence: story field > house-rules.md
                                  # default_quality_gates > Factory hardcoded default.
                                  # If excluding a default gate, justify in Constraints.
tests: [tests/unit/test_widget.py, tests/integration/test_widget_seam.py]
                                  # optional; written by the developer agent at commit time.
                                  # Lists the test modules this story owns — authored during
                                  # TDD pass 1 and test-design pass 2. Not set at planning time.
test-design-pass: done            # optional; written by the developer agent at commit time.
                                  # done | skipped-feature-governed
                                  # Records whether the post-GREEN test-design pass ran.
---
```

## Body

````markdown
# <title>

<one-sentence summary of the story goal in domain language>

**Priority:** must-have          # MoSCoW — must-have | should-have | could-have | wont-have

## Goal

One paragraph. What user-visible or API-visible behavior must exist after this story ships. Plain domain language.

## Domain Rule

Bullet list. Mental model: entities, invariants, must-nevers. "Use this wording" guidance for implementing logic.

## Demo Scenario

Numbered step list (not paragraphs). Observable actions with concrete values.

1. Step with concrete values
2. Step showing outcome or edge case
3. (continue as needed)

## Affected Paths

Explicit file listing grouped by layer. Existing files that change, new files to create.

- `src/module/file.py` — existing file, change here
- `src/module/new_file.py` — new file to create
- `tests/unit/test_module.py` — existing test file

**Hygiene rule for `touches` field:** When populating the story's `touches` frontmatter field, the planning agent derives the list from Affected Paths by taking the directory prefix of each file, de-duplicating parents, and removing any entry that is a prefix of another. Each entry must resolve to an existing directory or one created by a story in `deps`. Never list both a parent and its child — the parent already covers it. A broad prefix like `packages/server/` forces the dispatcher to serialize every story that touches any server file, defeating overlap detection. Collapse sibling directories only when every sibling is touched. Speculative paths for modules that do not exist yet are not permitted — use the existing parent directory instead.

## Inputs

Reading manifest: deps deliverables, spec rules, architecture references, current implementation files. Point the developer-agent to the files and specs they must understand before coding.

## Outputs

Concrete deliverables per layer with behavioral detail in observable terms. List each module/file and what it produces or enforces.

## Required Behavior

(optional — include only if the Outputs section does not fully capture the behavior being implemented)

Primary delivery mechanism described concretely. Describes how the system components interact to satisfy the Goal.

## Constraints

Explicit must-not list from ADRs, conventions, testing regime, scope exclusions.

- No breaking changes to existing API contracts
- No direct database queries (use repository layer)
- (continue as needed)

## Suggested Agent Plan

Numbered implementation steps in dependency order, referencing Affected Paths and Outputs. Helps the developer-agent understand optimal execution sequence and dependencies between implementation tasks.

1. Write RED test covering [Affected Path X] behavior
2. Implement [Affected Path Y]
3. (continue as needed)

## Acceptance Criteria

Checkbox list of falsifiable invariants (unchanged format, but checkboxes replace dashes).

- [ ] <falsifiable invariant — "X produces Y", "X never Y", or "when X then Y" (RULE-ID)>
- [ ] <another criterion>

## Verification

Exact shell commands grouped by suite from testing.yaml.

**Unit tests:**
```bash
pytest tests/unit/test_module.py -v
```

**Integration tests:**

```bash
pytest tests/integration/test_module_seam.py -v
```

## Out of Scope

Dash-prefixed list of explicit exclusions.

- No changes to authentication layer
- No database schema migration
- (continue as needed)

## Agent Stop Conditions

Dash-prefixed list of halt-and-ask triggers. When any of these conditions arise during implementation, the developer-agent should stop and ask the human.

- If new architecture dependencies are discovered not mentioned in Inputs
- If the work requires changes to [specific critical system]
- (continue as needed)

````

## Frontmatter Fields

### risk_level (optional)

One of `low`, `medium`, or `high`. Indicates the risk classification of this story for planning and review purposes. When absent, the story is treated as risk-unclassified. Does not affect implementation gates; used for organizational and historical tracking.

### touches (required)

Array of directory prefixes the story is expected to work within. Each entry is a directory path ending in `/` or a root-level filename. The dispatcher uses these for overlap detection (stories with overlapping touches serialize) and scope enforcement (`premerge-check` verifies the developer stayed within declared directories). Example: `[src/orchestrator/, tests/unit/orchestrator/]`.

### concerns (optional)

Mapping with optional `domain` and `technical` keys, each a list of strings. Declares which registered concerns from `docs/agent-context.md` the story touches. Names must match `###` headings under "Technical concerns" or "Domain concerns". Cross-cutting concerns are never declared because they are always active. Omit the field when no registered concern applies.

### quality-gates (optional)

List the semantic gates that apply to the story: `crap-score`, `mutation-analysis`, and `dependency-check`.
When the field is absent, the dispatcher falls back to `docs/charter/house-rules.md`'s
`default_quality_gates`, then to the Factory hardcoded default of all three gates.
If the story excludes any default gate, justify the exclusion in the body's Constraints section.

### tests (optional, written at implementation time)

Array of test module paths this story owns — test files authored during TDD pass 1 (acceptance-criteria tests) and test-design pass 2 (integration and edge-case tests). Written by the developer agent at commit time, not set during planning. Lists only modules this story created or extended, not prior tests inherited from dependency stories. Used by the QA agent for contract-to-test cross-referencing and by the reconciliation agent for traceability audits. Example: `[tests/unit/test_widget.py, tests/integration/test_widget_seam.py]`.

### test-design-pass (optional, written at implementation time)

Records whether the developer agent ran the post-GREEN `test-design` skill (pass 2). Written at commit time. Valid values:

- `done` — the developer agent invoked `test-design` and authored any additional tests it identified (or confirmed no additional tests were needed).
- `skipped-feature-governed` — the story is `.feature`-governed; pass 2 was correctly skipped because the `.feature` file is the test design.

A non-`.feature`-governed story with no `test-design-pass` field is a QA finding — the developer skipped the step. The `test-design-verify` gate checks this field.

## Referenced from

- [create-backlog § Step 2](../../skills/create-backlog/SKILL.md#step-2--break-epics-into-user-stories)
- [backlog-lint script](../../scripts/backlog-lint)
