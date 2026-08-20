---
id: RECON-0019
source: implementation
severity: minor
category: defect
artifact: factory/playbooks/greenfield-development.fsm.yml
status: open
traces: [ST-0083]
---

# Greenfield FSM missing charter states

**What is wrong:** `factory/playbooks/greenfield-development.fsm.yml` is derived from the greenfield playbook and consumed by the `run-step` skill. ST-0083 added Steps 1.0 (charter init), 2.5 (completeness sweep), and 2.6 (planning gate) to the playbook, but the FSM was not updated. The `run-step` skill cannot route through the new charter steps.

**Fix:** Add states and transitions for Steps 1.0, 2.5, and 2.6 to `greenfield-development.fsm.yml`, keeping the FSM in exact correspondence with the playbook per [state-machine-notation.md](../../factory/rulebooks/conventions/state-machine-notation.md).
