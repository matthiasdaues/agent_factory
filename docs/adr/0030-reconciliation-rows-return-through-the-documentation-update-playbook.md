---
id: 0030
status: accepted
evaluation: none
---

# Reconciliation rows return through the documentation-update playbook

## Context

Take the reconciliation run of 2026-11-03. The code adds a component that the
slice view of `docs/spec/architecture.dsl` does not show. The report
`docs/reviews/reconciliation-2026-11-03.md` gets an `open` row with the
architecture agent as owner.

[ADR-0029](0029-per-story-drift-reports-block-the-wave-close.md) gives the
reconciliation report the row shape of the spec-feedback report. It does not
say who dispatches the owner of a reconciliation row. A reconciliation run
belongs to no wave, so the implementation agent never sees the row, and
`dispatch close-wave` never reads it. Without a dispatcher, the row stays
`open`, and nobody notices.

A reader of ADR-0029 would expect a script gate here too, as `close-wave` is
for spec feedback. This decision deliberately has none.

The accepted proposal
[core-artifact-ownership.md](../proposals/core-artifact-ownership.md) and gap
CAO-G32 in the
[gaps report](../spec/work/core-artifact-ownership-gaps.md#cao-g32-who-carries-a-reconciliation-row-back-into-its-artifact-and-what-waits-for-it)
settle the design. The rejected options are:

- **The implementation agent dispatches the owner.** A reconciliation run
  belongs to no wave, so the implementation agent would need a new trigger.
- **Virgil dispatches through `run-step`.** The row would wait until a human
  starts a session, and `run-step` would need a precondition on report rows.
- **`premerge-check` refuses the merge into `dev` while a row is open.** A
  merge gate would stop feature work on a documentation drift, and it needs a
  new parser for `docs/reviews/`.
- **A `skill:` field on each entry of `core-artifacts.yaml`.** The core list
  would change shape, and one entry cannot name two skills for one artifact.

`evaluation: none`, because CAO-G32 decided each point and no open alternative
is left to weigh.

## Decision

The orchestrator of the `documentation-update` playbook carries every
reconciliation row back into its artifact. The orchestrator is the session that
runs the playbook. After the reconciliation run, its backfeed step reads every
reconciliation report, not only the new one.

The step dispatches the owner of each `open` row, one session at a time. The
dispatch names the row and the report and no skill. The owner takes the skill
or workflow step for the artifact from its own agent definition, changes the artifact, and sets
the row to `fixed` in the same commit.

The step then dispatches the reviewer of each `fixed` row on an artifact of the
core list. It reads `rulebooks/core-artifacts.yaml` to tell those rows from the
others, as `dispatch close-wave` does. The reviewer is the one the owner's declaration names in
`reviewed_by:`. It sets `confirmed` or `rejected`. When the reviewer is
`stakeholder`, the orchestrator presents the fix in its session and sets the
status itself. When `reviewed_by:` names an agent and `stakeholder`, the agent
reviews first. A `rejected` row becomes a `BUG` finding with the developer
agent as owner. A `fixed` row on any other artifact closes at `fixed`.

The owner and the reviewer commit on the branch that holds the reconciliation
report, normally the feature branch before its merge into `dev`.

A row stays in the report that first wrote it, and only its status changes. A
later run writes a new row only when the drift of a closed row appears again: a
`confirmed` row, or a `fixed` row outside the core list. A row that still waits
needs no record.

The playbook is done only when no row of any reconciliation report is `open`,
or `fixed` on an artifact of the core list. No script reads the reconciliation
reports.

## Consequences

- A row left by a stopped session is picked up by the next backfeed step,
  because the step reads every report.
- An unhandled reconciliation row blocks no merge and no reconciliation run.
  Only the playbook stays open, and it names the row.
- So a project that never finishes the playbook can carry an open
  reconciliation row for a long time. The DONE list is the only signal.
- The core list keeps its four fields, and each owner's agent definition stays
  the one place that maps an artifact to a skill.
- Spec feedback and reconciliation share the row shape, the statuses, and the
  reviewers, but have different dispatchers and different waits.
  [8.17](../arc42/08_crosscutting_concepts.md#817-artifact-ownership-one-producer-one-declared-review)
  compares the two loops.
- The backfeed follows BR-067 in
  [validation-rules.md](../spec/validation-rules.md#ownership-and-drift-reports-core-artifact-ownership-br-056br-066).
