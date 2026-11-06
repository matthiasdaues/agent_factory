---
id: ATAM-0008
source: atam-review
severity: medium
category: defect
artifact: docs/adr/0029-per-story-drift-reports-block-the-wave-close.md#consequences
status: resolved
resolution_summary: ADR-0029, section 6.12, the dispatch component, and the Core List now state that close-wave fails and names the file on wrong headers, an unknown status, or a missing core list, read under the Factory root.
traces: [ADR-0029, QS-17, BR-062, BR-063, CAO-G04, CAO-G13]
---

# close-wave has no defined result when it cannot read a report or the core list

**What is wrong:** `close-wave` decides on two inputs, and the architecture defines neither failure. ADR-0029 says only that "a report with other column headers cannot be parsed". It does not say whether `close-wave` then fails or passes. BR-063 lets a missing report pass, so an implementation that treats an unreadable report like a missing one is consistent with the text. Then take `spec-feedback-ST-0318.md` with the header `Artifact | Mismatch | Evidence | Owner | Status`, or a row with the status `done`. The `open` row on `validation-rules.md` is never seen, and the wave closes.

The core list has the same gap. The Core List container, section 5.1, and section 8.17 place the file at `packages/factory/rulebooks/core-artifacts.yaml`. That path exists only in the factory repository. An installed project has it under `.agent-factory/factory/rulebooks/`, which only the `close-wave` contract says ("as installed"). When `close-wave` cannot read the list, every `fixed` row looks like a row on a non-core artifact and passes.

**Fix:** State in ADR-0029, section 6.12, and the `dispatch close-wave` contract that `close-wave` fails, and names the file, when a spec-feedback report of the wave exists but lacks the five columns, when a row carries a status outside `open`, `fixed`, `confirmed`, and `rejected`, or when the installed core list is missing or unreadable. Name the installed path `.agent-factory/factory/rulebooks/core-artifacts.yaml` in the Core List container and in section 8.17 next to the source path. The requirements agent then adds the three failure cases to the `close-wave` Scenario Outline.
