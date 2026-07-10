---
id: FAGAN-0034
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/phase_runner.py#run_phase
status: resolved
traces: [FR-E3, UC-02, VR-001, VR-014]
---

# Deterministic gate findings not ingested into findings store

**What is wrong:** On `passed=False`, `PhaseRunner` calls `ingest_open_findings()`, but that adapter only reads reviewer-filed markdown findings from `docs/findings/*.md`. The deterministic spec-lint/pre-commit output (which produces JSON findings on stdout) never reaches the findings store or the next author prompt. The `map_spec_lint()` function exists in `finding_ingest.py` but is never called in the gate-failure path.

**Fix:** Extend the gate contract to return deterministic findings payloads (or a retrievable gate-output channel) and ingest them as `source=spec-lint` before loop-back. Wire `map_spec_lint()` into the gate-failure path in `PhaseRunner`.
