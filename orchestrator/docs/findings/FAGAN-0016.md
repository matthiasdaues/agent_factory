---
id: FAGAN-0016
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/adapters/findings_store.py#_FINDING_SCHEMA
status: resolved
traces: [VR-006]
---

# Local schema stricter than published contract

**What is wrong:** The local `_FINDING_SCHEMA` in `findings_store.py` requires `created_by` and `resolved_by` fields, but the published Finding schema in `interface-contracts.md` does not list them as required. The adapter therefore rejects contract-valid finding JSON that omits these fields.

**Fix:** Align `_FINDING_SCHEMA` with `interface-contracts.md`: make `created_by` and `resolved_by` optional (with defaults) or update the published contract to require them.
