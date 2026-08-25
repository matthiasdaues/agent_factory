---
title: Backlog Story Template
version: 1.0.0
---

# Backlog Story Template

Skeleton for a single `backlog/ST-NNNN.md` file. Governed by [create-backlog skill](../../skills/create-backlog/SKILL.md) and validated by `factory/scripts/backlog-lint`.

## Frontmatter

```yaml
---
id: ST-0001                       # ST-NNNN, zero-padded, unique; matches the filename
epic: Domain Entities             # the EPIC this story belongs to (a grouping label, not a separate file)
title: Define domain entity dataclasses
tier: economy                     # economy | standard | strong — the model tier this story's work needs
status: pending                   # pending | in_progress | review | blocked | done
deps: [ST-0002]                   # story ids that block this one (optional)
traces: [UC-02, ADR-0003]         # Use Case / ADR / component ids this story implements (optional)
outputs: [src/orchestrator/entities.py]   # files the story is expected to produce
tests: [tests/test_entities.py]   # pre-existing test files covering this story (optional)
risk_domains: [security, reliability]   # optional; closed enum: security, privacy, data_integrity,
                                       # compatibility, reliability, operations
strategy: direct                  # optional; closed enum: direct | seams-first; default: direct
---
```

## Body

```markdown
# <title>

<what the story delivers, in the domain's language>

**Priority:** must-have          # MoSCoW — must-have | should-have | could-have | wont-have

## Acceptance Criteria

- <criterion derived from the Gherkin scenarios / postconditions>

## Implementation Notes

<optional guidance, constraints, or context>
```

## Frontmatter Fields

### tests (optional)

Array of pre-existing test file paths that cover this story's acceptance criteria.\
When `tests:` is present and non-empty, the developer-agent reads these tests as the specification and implements code to make them pass (Green phase only, skipping Red). Test files may not exist at planning time (backlog-lint warns but does not error on missing test files).

## Referenced from

- [create-backlog § Step 2](../../skills/create-backlog/SKILL.md#step-2--break-epics-into-user-stories)
- [backlog-lint script](../../scripts/backlog-lint)
