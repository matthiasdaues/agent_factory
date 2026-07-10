---
id: RECON-0002
source: reconcile-spec
severity: minor
category: defect
artifact: src/orchestrator/approval_service.py#reject
status: resolved
traces: [UC-04]
---

# reject command does not support optional note

**What is wrong:** UC-04 extension 2a specifies "The Operator runs reject (optionally with a note)" and the `Approval` entity includes a `note` field, but neither the CLI's `reject` subcommand nor `ApprovalService.reject()` accepts a note parameter. The rejection reason is lost.

**Fix:** Add an optional `--note` argument to the `reject` CLI subcommand. Pass it through to `ApprovalService.reject(note: str = "")`. Persist the note in `.orchestrator/run.json` (e.g., in a `rejection_note` field on the phase record, or by materialising the `Approval` entity which already has a `note` field).
