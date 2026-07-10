---
id: FAGAN-0010
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/chain_runner.py#run_all
status: resolved
traces: [BR-006]
---

# Phase sequencing uses run.phases not run.chain

**What is wrong:** `run_all()` iterates `run.phases` in list order. If the persisted `phases` list ever gets reordered (e.g., by a bug in serialization or a manual edit), the chain would execute phases out of the canonical order defined in `run.chain`, violating BR-006.

**Fix:** Drive sequencing from `run.chain` and look up the corresponding `PhaseRecord` by name, or validate that `run.phases` ordering matches `run.chain` before execution.
