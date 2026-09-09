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
                                  # If excluding a default gate, justify in Notes for the Implementer.
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

```markdown
# <title>

<what the story delivers, in the domain's language>

**Priority:** must-have          # MoSCoW — must-have | should-have | could-have | wont-have

## Demo

<2–4 sentences. Walkthrough of what a person can show after the story ships.
Concrete values, not placeholders. Happy path plus one meaningful edge case.>

## Acceptance Criteria

- <falsifiable invariant — "X produces Y", "X never Y", or "when X then Y" (RULE-ID)>

## Scope

**Status quo:** <what exists now — tables, routes, views — including deliverables of depended-on stories>
**Delivers:** <what capability this story adds, across all layers>
**Out of scope:** <what explicitly does not change>

## Terminology

<optional — define project-specific terms used in this story. One term per line,
"Term: definition" format. Source definitions from docs/arc42/12_glossary.md or
docs/CONTEXT.md; include only terms the reader needs to understand this story.>

## Notes for the Implementer

<optional guidance, constraints, or context. Also the home for:
- Pre-existing tests: file paths that already cover this story's criteria
- Suggested approach: direct or seams-first
- Risk domains: security, privacy, data_integrity, compatibility, reliability, operations
- Gate exclusion justification: why a default quality gate was omitted>
```

## Frontmatter Fields

### touches (required)

Array of directory prefixes the story is expected to work within. Each entry is a directory path ending in `/` or a root-level filename. The dispatcher uses these for overlap detection (stories with overlapping touches serialize) and scope enforcement (`premerge-check` verifies the developer stayed within declared directories). Example: `[src/orchestrator/, tests/unit/orchestrator/]`.

### concerns (optional)

Mapping with optional `domain` and `technical` keys, each a list of strings. Declares which registered concerns from `docs/agent-context.md` the story touches. Names must match `###` headings under "Technical concerns" or "Domain concerns". Cross-cutting concerns are never declared because they are always active. Omit the field when no registered concern applies.

### quality-gates (optional)

List the semantic gates that apply to the story: `crap-score`, `mutation-analysis`, and `dependency-check`.
When the field is absent, the dispatcher falls back to `docs/charter/house-rules.md`'s
`default_quality_gates`, then to the Factory hardcoded default of all three gates.
If the story excludes any default gate, justify the exclusion in the body's Notes for the Implementer section.

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
