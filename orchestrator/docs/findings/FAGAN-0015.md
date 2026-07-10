---
id: FAGAN-0015
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/adapters/gate_runner.py#_classify_output
status: resolved
traces: [ADR-0003, ATAM-R02]
---

# Error count regex instead of structured findings parse

**What is wrong:** The findings-vs-error discriminator uses an English regex `r"(\d+)\s+error(?:s?\b)"` to distinguish lint findings from infrastructure errors. This is brittle: it cannot parse the machine-readable `spec-lint --format json` findings, it misclassifies any output that lacks the word "error" as infra failure, and it cannot distinguish warning/info findings for recording.

**Fix:** Parse hook-specific structured output (e.g., the JSON findings array from `spec-lint`) per ADR-0003 and interface-contracts.md. Fall back to the regex only for unknown hooks.
