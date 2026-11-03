---
id: 0029
status: proposed
evaluation: none
---

# Per-story drift reports block the wave close

## Context

Take ST-0318. While implementing it, the developer agent finds that the
migration script must refuse a repository with uncommitted changes, and
`docs/spec/validation-rules.md` has no such rule. Today the developer agent may
edit the specification itself. Then the file has a second writer, and the fix
skips the owner's review. The reconciliation agent has the same problem after
implementation.

The developer agents of a wave run in parallel, and the dispatch contract gives
every concurrent assignment its own output path. So a single report per wave
would have several concurrent writers.

The accepted proposal
[core-artifact-ownership.md](../proposals/core-artifact-ownership.md) settles
the handling (DEC-17 to DEC-19, DEC-27, DEC-28, DEC-35), and the
[gaps report](../spec/work/core-artifact-ownership-gaps.md) settles the row
columns and the edge cases (CAO-G02 to CAO-G04, CAO-G13). The rejected options
are:

- **The developer agent fixes the specification.** The file would get a second
  writer, and no review would confirm the fix (DEC-18).
- **One report per wave.** Parallel developer agents would write the same file
  (DEC-27).
- **Separate finding files for reconciliation.** One consolidated report per
  run keeps every drift of a run in one table with its owner (DEC-17).
- **Every row waits for `confirmed`.** A row about a QA strategy or an ADR has no
  declared reviewer, so it could never reach `confirmed`, and the wave would
  stay open for good (DEC-35).
- **An empty report for every story.** The developer agent writes a row only
  when it finds drift, so a missing report counts as no rows (CAO-G13).

`evaluation: none`, because the proposal decided each point and no open
alternative is left to weigh.

## Decision

The developer agent and the implementation agent edit no specification file.
The developer agent writes each drift as a row of its story's report,
`docs/spec/work/spec-feedback-<story-id>.md`. A row has the columns Artifact,
Drift, Evidence, Owner, and Status. The status is `open`, `fixed`,
`confirmed`, or `rejected`.

After a story merges, the implementation agent dispatches each row's owner,
which changes the artifact and sets `fixed`. It then dispatches the owner's
reviewer, which sets `confirmed` or `rejected`. A `rejected` row becomes a
`BUG` finding against the code, with the developer agent as owner.

`dispatch close-wave` reads the reports of the wave's stories and the core
list. It fails while a row is `open`, or `fixed` on a core or seam artifact. A
`fixed` row on any other artifact passes. In manual mode the same rule holds
per story.

The reconciliation agent writes the same row shape into one report per run,
`docs/reviews/reconciliation-<date>.md`, and edits no core file.

## Consequences

- The specification lags the code by one wave at most.
- A wave takes longer to close, because owner and reviewer sessions run before
  `close-wave` passes.
- `close-wave` depends on the installed core list and on a fixed table shape in
  the reports. A report with other column headers cannot be parsed.
- `close-wave` does not wait for open `QA` findings. The implementation agent
  dispatches the test-strategy agent for each open `QA` finding it owns after
  the story merges.
- Every owner and reviewer declares both report paths, because each one changes
  a status in them.
