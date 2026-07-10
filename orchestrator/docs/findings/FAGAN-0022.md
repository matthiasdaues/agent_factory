---
id: FAGAN-0022
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/adapters/model_matrix.py
status: resolved
traces: [FR-K4, VR-024]
---

# Matrix adapter does not validate semantic content

**What is wrong:** `FileModelMatrix` only parses syntax (sections, key=value pairs). It does not validate required policy keys, allowed tier values, or `on_missing ∈ {halt, auto}`. An invalid `on_missing` value silently behaves like the default fallback instead of halting as a configuration error.

**Fix:** Validate the matrix structure and enum values on load. `matrix-lint` exists but runs as a gate hook, not at adapter construction. The adapter should also reject obviously invalid matrices.
