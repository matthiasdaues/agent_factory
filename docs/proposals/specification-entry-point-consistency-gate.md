---
scope: global
schema_version: 2
status: open
owner: Agent Factory maintainers
created: 2026-09-15
updated: 2026-09-15
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - packages/factory/scripts/spec-lint
    - packages/factory/skills/derive-feature/SKILL.md
    - packages/factory/agents/requirements-agent.md
    - packages/factory/skills/inspect-spec/SKILL.md
    - packages/factory/agents/spec-review-agent.md
    - packages/factory/skills/create-backlog-epics/SKILL.md

governance:
  assurance: elevated
  risk_domains:
    - compatibility
    - reliability

estimate:
  as_of: 2026-09-15
  basis: decomposition
  confidence: medium
  human_review_hours:
    min: 2
    max: 4
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Specification Entry-Point Consistency Gate

## Summary

Add a deterministic specification gate for actor type, shipped entry points,
and unresolved interface gaps. The requirements workflow records missing
entry points before specification review. Planning copies verified references
and keeps affected EPICs blocked without stopping unrelated slicing work.

The first release extends the existing specification workflow. It does not add
a separate EPIC-slicing artifact or linter.

## Motivation

The cycle-based orchestration specification defines detailed delegation
behavior without naming the interface that creates, replaces, or revokes a
grant. The requirements gaps report did not identify this omission. EPIC
slicing found the omission only after trying to assign a shipped entry point.

Instructions alone cannot ensure that every requirements run detects this
class of defect. The existing `spec-lint` review boundary provides the correct
place for a deterministic completeness check.

`spec-lint` currently does not parse `.feature` files. Existing `# @`
annotations identify implementation traces, not shipped interfaces. Reusing
that syntax would merge two different contracts and conflict with
reconciliation.

## Core Principles

- Every person-facing goal names a shipped entry point or an explicit gap.
- Missing knowledge remains visible through a stable gap identifier.
- Draft specifications may record gaps. Review cannot approve unresolved gaps.
- Implementation traces and interface references remain separate concepts.
- Deterministic checks establish structure. Reviewers judge semantic fitness.
- One missing capability does not hide or halt unrelated planning work.

## Design

### Rule metadata

Every `Rule:` carries one primary actor and one actor type:

```gherkin
Rule: Human operator delegates a route sequence
# actor: Human operator
# actor-type: person
# gap: G-012
```

`actor-type` accepts `person`, `external-system`, or `internal-system`. A Rule
for a person or external system carries one or more `# entry-point:`
annotations or one `# gap:` annotation. A Rule cannot carry both forms.

An internal-system Rule does not require an entry point. Internal behavior
supports a person-facing capability or an external contract elsewhere in the
specification.

Existing Rules that name several actors select one primary actor when the goal,
entry point, and result are shared. A migration splits the Rule when actors use
different entry points or observe different results.

### Entry-point references

The new annotation names the shipped interface:

```gherkin
# entry-point: docs/spec/supplementary_specs/interface-contracts.md#cycle-select
# entry-point: packages/factory/config/session-menu.md#option-b
# entry-point: packages/factory/skills/run-step/SKILL.md
```

An anchored reference qualifies only when the target file is named
`interface-contracts.md` or `session-menu.md`. A skill reference may name its
`SKILL.md` because the complete skill is the interface. Every other reference
fails. Commands, schemas, and configuration files must have an anchored section
in `interface-contracts.md`.

Markdown anchor resolution uses the same rules as `link-check`. The
implementation shares the resolver or extracts a common helper. It does not
create a second anchor algorithm.

Existing `# @<path>::<symbol>` annotations retain their current meaning. They
trace specified behavior to existing or implemented code.

### Gap references

Each feature owns a companion gaps report. Entry-point gap identifiers use
`G-NNN` and are unique within that report. Rule-level `# gap:` metadata is
reserved for missing entry-point decisions. Other requirement gaps remain in
the report without replacing an entry-point reference.

The gaps report gains a structured table:

| ID    | Rule                                      | Missing decision                       | Status |
| ----- | ----------------------------------------- | -------------------------------------- | ------ |
| G-012 | Human operator delegates a route sequence | Choose the grant-management interface. | open   |

`spec-lint` verifies that every `# gap:` identifier resolves exactly once in
the companion gaps report. A resolved gap is replaced by an entry-point
reference in the feature file.

### Requirements workflow

`derive-feature` builds an actor-goal-interface-result matrix before writing
Rules. It writes `actor-type` for every Rule.

When a person-facing goal has a known interface, `derive-feature` writes its
exact entry-point reference. When the interface is unknown, `derive-feature`
allocates the next gap identifier and adds the decision to the gaps report.

The requirements agent writes or updates supplementary interface contracts
after feature derivation. The agent then revisits each entry-point gap, records
decisions reached during that work, and replaces resolved gaps with references.

The requirements agent cannot declare a specification ready while a
person-facing goal lacks both forms.

### Deterministic checks

`spec-lint` parses every `.feature` file under the selected specification
directory. It accepts the repository's current indented and escaped comment
forms during migration.

The linter adds these error conditions:

- `SL-ACTOR-TYPE`: a Rule lacks `actor-type` or uses an unsupported value.
- `SL-ENTRY`: a person or external-system Rule has no entry point or gap.
- `SL-ENTRY-CONFLICT`: a Rule carries both an entry point and a gap.
- `SL-ENTRY-REF`: an entry-point path or required anchor does not resolve.
- `SL-GAP-REF`: a gap identifier is missing, duplicated, or resolved already.

Default linting checks structure and reports open gaps without blocking draft
commits. A `--gate-gaps` option treats each open referenced gap as an error.
Specification review runs `spec-lint --gate-gaps`.

### Architecture and planning

Architecture review confirms that each specified entry point maps to an
architecture component. This remains a semantic review because file and anchor
resolution cannot establish architectural fitness.

An unresolved entry-point gap blocks progression at specification review.
Architecture does not receive a specification whose person-facing interface is
undecided.

EPIC slicing still checks the entry-point reference before forming an EPIC.
During an ad hoc run or after later drift, a capability with an open gap enters
the table with status `gap`. The affected EPIC remains blocked and retains the
gap reference. Unrelated EPICs may still be proposed.

No `backlog/epic-slicing.yaml` or `epic-slicing-lint` script is introduced.

## Scope

**In the first release:**

- Add `.feature` Rule parsing to `spec-lint`.
- Add `actor-type`, `entry-point`, and `gap` validation.
- Add Markdown path and heading-anchor resolution for entry points.
- Add gap-report cross-reference validation and review-time gap gating.
- Update `derive-feature` and the requirements agent to emit the metadata.
- Update specification review to reject unresolved entry-point gaps.
- Update EPIC slicing to retain gaps on affected capabilities and EPICs.
- Migrate all current feature files to the new metadata contract.
- Add tests for valid, missing, conflicting, and broken annotations.

**Explicitly deferred (do NOT plan stories for these):**

- Automatically proving that an interface implements the Rule's semantics.
  Semantic correspondence remains review work.
- Automatically mapping entry points to Structurizr components. Architecture
  review owns this judgment.
- A general specification-to-code traceability checker. Existing `# @`
  lifecycle work remains separate.
- An EPIC-slicing YAML artifact or dedicated linter. Existing artifacts are
  sufficient for this failure mode.
- Choosing the cycle delegation command. The cycle-based orchestration
  specification must resolve that product decision.

## Design Details

The migration covers all current `.feature` files in one change. Mixed
contracts would make lint results depend on file age and weaken the gate.

The parser treats metadata as Rule-level only when it appears after a `Rule:`
line and before the first `Scenario:` or next `Rule:`. Scenario-level `# @`
implementation traces remain unaffected.

The linter reports the feature path, Rule line, Rule name, and unresolved
reference. JSON output includes the same fields for review automation.

An open gap is not a substitute for an entry point after approval. The review
gate fails until the gap is resolved and the Rule names its interface.

The expected implementation effort is three to five focused engineering days.
The estimate includes six existing feature files and 77 current Rules.

## Open Questions

None. The proposal is ready for independent review.

## Completion Criteria

- `derive-feature` emits `actor`, `actor-type`, and either `entry-point` or
  `gap` for every person or external-system Rule.
- Every Rule names exactly one primary actor.
- Rules with different actor entry points or results are separate Rules.
- `spec-lint` parses all repository `.feature` files without changing Scenario
  semantics.
- `spec-lint` rejects every missing or invalid actor type with
  `SL-ACTOR-TYPE`.
- `spec-lint` rejects a person or external-system Rule that has neither an
  entry point nor a gap with `SL-ENTRY`.
- `spec-lint` rejects a Rule that carries both forms with
  `SL-ENTRY-CONFLICT`.
- `spec-lint` rejects broken entry-point paths and required anchors with
  `SL-ENTRY-REF`.
- `spec-lint` accepts only `SKILL.md` as a whole-file entry-point reference.
- Anchored entry points resolve only in `interface-contracts.md` or
  `session-menu.md`.
- `spec-lint` rejects missing, duplicate, and resolved gap references with
  `SL-GAP-REF`.
- Rule-level `# gap:` metadata represents only missing entry-point decisions.
- Default linting permits a structurally valid draft with an open gap.
- `spec-lint --gate-gaps` exits non-zero while any referenced gap remains open.
- The requirements workflow revisits entry-point gaps after writing
  supplementary interface contracts.
- Specification review invokes `spec-lint --gate-gaps` before semantic review.
- EPIC slicing marks a gap-bearing capability and its EPIC as blocked.
- EPIC slicing continues to propose unaffected EPICs.
- Existing `# @` implementation references retain their current meaning.
- All current feature files pass the new metadata checks after migration.
- The full repository test suite passes without disabled or bypassed checks.

## Guiding Rule

A person-facing requirement names how the person uses it or records that the
interface remains undecided.
