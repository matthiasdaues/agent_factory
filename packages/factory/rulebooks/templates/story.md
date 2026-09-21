---
title: Backlog Story Template
version: 2.2.0
---

# Backlog Story Template

Skeleton for a single `backlog/ST-NNNN[A-Z].md` file. Governed by [create-backlog skill](../../skills/create-backlog/SKILL.md) and validated by `factory/scripts/backlog-lint`.

## Frontmatter

```yaml
---
id: ST-0001                       # ST-NNNN (new) or ST-NNNNA (split); zero-padded, unique; matches the filename
epic: Domain Entities             # the EPIC this story belongs to (references a section in backlog/epics.md)
title: Define domain entity dataclasses
tier: economy                     # economy | standard | strong — the model tier this story's work needs
status: pending                   # pending | in-progress | review | blocked | done
risk_level: low                   # optional; must match a key in testing.yaml risk_classes (defaults: low | medium | high)
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
quality-gates: []                  # semantic gates that apply to this story; filled by planner.
                                  # Precedence: story field > house-rules.md
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

## Demo Data

The seeded records the Demo Scenario depends on, stated as data rather than as a task.

When the story seeds rows: a table with one row per seeded record and one column per field, carrying literal values. Name the seeding script by path. State whether the story extends an existing row or adds a new one, which rows must be written directly through the model because no API delivers them yet, and what the script's idempotency guard and existing output must preserve.

When the story seeds nothing: say so and name the predecessor story whose seed set it depends on, plus the specific rows and states the flow needs.

Every identifier used in the Demo Scenario must resolve to a row in a Demo Data table — in this story or a predecessor.

## Affected Paths

Grouped by layer, at the coarsest honest granularity. Name a file only when that exact file already exists and the story changes it. For new work, name the directory that will hold the files and say what is added — a path invented at planning time ages badly and constrains the developer agent for no benefit.

- `src/module/file.py` — existing file, change here
- `src/module/` — new `dtos.py`, `errors.py`
- `tests/unit/test_module.py` — existing test file

Follow the [`touches` hygiene rules](../../rulebooks/conventions/touches-hygiene.md) when populating the `touches` frontmatter field. Written this way, the directory prefixes are already present.

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

## Resolve Before Implementation

Numbered list of contract-level decisions the planning agent could not resolve.
Each item names the specific field, operation, or behavior. Resolved during the
grilling session; answers recorded as blockquotes beneath each question. "None —
contracts are fully specified" when nothing is open.

1. <contract question>
2. <contract question>

And add one row to the Hygiene/template commentary:

The `## Resolve Before Implementation` section is present in every story, even
when empty ("None"). Original stories carry this section through grilling and
operationalisation. Implementation stories sliced from the original do not
inherit it — they inherit the resolved answers in their home sections.

````

## Frontmatter Fields

See [story-frontmatter-fields.md](../references/story-frontmatter-fields.md) for detailed documentation of `risk_level`, `touches`, `concerns`, `quality-gates`, `tests`, and `test-design-pass`.

## Referenced from

- [create-backlog § Operational sequence](../../skills/create-backlog/SKILL.md#operational-sequence)
- [backlog-lint script](../../scripts/backlog-lint)
