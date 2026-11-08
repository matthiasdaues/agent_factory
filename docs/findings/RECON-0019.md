---
id: RECON-0019
source: implementation
review_class: code
category: defect
type: documentation
severity: note
basis:
  in_use: true
  harms_downstream: false
  fails_purpose: false
  raises_cost: false
rating:
override_by:
override_reason:
stop_confirmed_by:
stop_confirmed_reason:
artifact: packages/factory/playbooks/greenfield-development.md:39
status: resolved
owner: developer-agent
traces: [ST-0083]
---

# Greenfield FSM missing charter states

**What is wrong:** `.agent-factory/factory/playbooks/greenfield-development.fsm.yml` is derived from the greenfield playbook and consumed by the `run-step` skill. ST-0083 added Steps 1.0 (charter init), 2.5 (completeness sweep), and 2.6 (planning gate) to the playbook, but the FSM was not updated. The `run-step` skill cannot route through the new charter steps.

**Why this severity:** The file `greenfield-development.fsm.yml` no longer exists, so the missing states have no place and nothing remains to change.

**Fix:** Add states and transitions for Steps 1.0, 2.5, and 2.6 to `greenfield-development.fsm.yml`, keeping the FSM in exact correspondence with the playbook per [state-machine-notation.md](../../.agent-factory/factory/rulebooks/conventions/state-machine-notation.md).
