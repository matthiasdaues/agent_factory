# Story Frontmatter Fields

Detailed documentation for optional and implementation-time frontmatter fields
in `backlog/ST-NNNN.md` files. See the
[story template](../templates/story.md) for the full schema.

## risk_level (optional)

Must match a key in `docs/testing.yaml` → `risk_classes`. The detect-test-regime skill populates that section from the project's testing strategy document during fitting; projects that define their own risk classes (e.g. `cluster-a`, `cluster-b`) override the factory defaults. When `risk_classes` is absent from testing.yaml, `backlog-lint` falls back to `low | medium | high`. When the field itself is absent from a story, the story is treated as risk-unclassified. Does not affect implementation gates; used for organizational and historical tracking.

## touches (required)

Array of directory prefixes the story is expected to work within. Each entry is a directory path ending in `/` or a root-level filename. The dispatcher uses these for overlap detection (stories with overlapping touches serialize) and scope enforcement (`premerge-check` verifies the developer stayed within declared directories). Example: `[src/orchestrator/, tests/unit/orchestrator/]`.

## concerns (optional)

Mapping with optional `domain` and `technical` keys, each a list of strings. Declares which registered concerns from `docs/agent-context.md` the story touches. Names must match `###` headings under "Technical concerns" or "Domain concerns". Cross-cutting concerns are never declared because they are always active. Omit the field when no registered concern applies.

## quality-gates (filled by planner)

Semantic gates that apply to this story: `crap-score`, `mutation-testing`, and `dependency-check`.
The template defaults to `[]`; the planner fills it from the `gates` section of `testing.yaml` (enabled gates only). Prose-only stories keep the empty list.
When the field is absent from an older story, the dispatcher falls back to `docs/charter/house-rules.md`'s
`default_quality_gates`, then to the Factory hardcoded default of all three gates.
If the story excludes a gate that is enabled in `testing.yaml`, justify the exclusion in the body's Constraints section.

## tests (optional, written at implementation time)

Array of test module paths this story owns — test files authored during TDD pass 1 (acceptance-criteria tests) and test-design pass 2 (integration and edge-case tests). Written by the developer agent at commit time, not set during planning. Lists only modules this story created or extended, not prior tests inherited from dependency stories. Used by the QA agent for contract-to-test cross-referencing and by the reconciliation agent for traceability audits. Example: `[tests/unit/test_widget.py, tests/integration/test_widget_seam.py]`.

## test-design-pass (optional, written at implementation time)

Records whether the developer agent ran the post-GREEN `test-design` skill (pass 2). Written at commit time. Valid values:

- `done` — the developer agent invoked `test-design` and authored any additional tests it identified (or confirmed no additional tests were needed).
- `skipped-feature-governed` — the story is `.feature`-governed; pass 2 was correctly skipped because the `.feature` file is the test design.

A non-`.feature`-governed story with no `test-design-pass` field is a QA finding — the developer skipped the step. The `test-design-verify` gate checks this field.
