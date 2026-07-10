---
id: FAGAN-0003
source: fagan-review
severity: critical
category: defect
artifact: src/orchestrator/adapters/finding_ingest.py#_read_open_findings
status: resolved
traces: [VR-006, BR-019]
---

# Malformed open findings silently skipped

**What is wrong:** `_read_open_findings()` silently skips `docs/findings/*.md` files with missing frontmatter, missing required fields (severity, id, artifact), or unknown severity values. A real open reviewer finding with a typo in its severity or a missing field is dropped from the count, causing `open_count == 0` and a false-clean approval. This can advance a phase that has unaddressed defects.

**Fix:** Validate open finding files strictly and fail the ingest loudly (raise an error or return an error result) on malformed input instead of silently dropping entries. At minimum, log a warning and count malformed files as a gate error.
