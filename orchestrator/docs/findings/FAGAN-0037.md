---
id: FAGAN-0037
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/cli.py#_build_runtime
status: resolved
traces: [BR-021, FR-K1, FR-K2, VR-023]
---

# Story classification not threaded into phase execution

**What is wrong:** Story classification is still not threaded from the backlog into real phase execution. Although `PhaseRunner` can accept `classification`, runtime construction always passes `None`, so `phase.implementation = by-class` in the model matrix cannot resolve per-story models. The `by-class` tier pivot is unreachable in real runs.

**Fix:** Load the active story classification from the backlog/planning output and pass it into implementation-phase execution, or make story selection explicit at the CLI boundary (e.g. `run-phase implementation --story ST-0001`).
