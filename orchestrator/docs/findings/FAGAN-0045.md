---
id: FAGAN-0045
status: resolved
severity: major
category: contract
artifact: orchestrator/src/orchestrator/adapters/finding_ingest.py
pass: 3
---

# Gate findings ingestion drops mixed pre-commit stdout

`ingest_gate_output()` passes raw pre-commit stdout to `map_spec_lint()`, but `map_spec_lint()` only accepts a pure JSON document. Real pre-commit output is commonly mixed text (hook banner + JSON), so deterministic gate findings can be dropped. Undermines FAGAN-0034.

**Suggested fix**: Extract embedded JSON findings from pre-commit stdout (reuse the line/JSON-scanning approach already used in gate classification or semantic parsing).
