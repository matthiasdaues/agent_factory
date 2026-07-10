---
id: FAGAN-0017
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/adapters/finding_ingest.py
status: resolved
traces: [ADR-0001]
---

# Ingestor depends on concrete FilesystemFindingsStore

**What is wrong:** `DefaultFindingIngestor` imports and type-hints `FilesystemFindingsStore` (the concrete adapter) instead of the `FindingsStore` port. It calls `store.next_id()` which is not on the port interface. This violates Dependency Inversion (ADR-0001) and makes the ingestor non-substitutable for testing or alternate store implementations.

**Fix:** Depend on the `FindingsStore` port. Move `next_id()` into the port contract (it's a legitimate store responsibility), or have the ingestor receive pre-allocated IDs.
