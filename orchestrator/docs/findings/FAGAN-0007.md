---
id: FAGAN-0007
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/phase_runner.py#run_phase
status: resolved
traces: [BR-021, FR-K1, FR-K2]
---

# Story classification never threaded into phase execution

**What is wrong:** `PhaseRunner` always calls `model_resolver.resolve(phase)` with no `classification` argument. `ModelResolver` treats `phase.implementation = by-class` as "no tier found" and falls back to adapter default. Story classifications (`trivial|standard|hard`) from the backlog can never drive model selection for implementation, breaking BR-021/FR-K1/FR-K2.

**Fix:** Thread story classification into phase execution. `PhaseRunner` (or the caller) must receive the current story's classification and pass it to `resolve(phase, classification=...)`. Treat missing classification for a `by-class` phase as a configuration error.
