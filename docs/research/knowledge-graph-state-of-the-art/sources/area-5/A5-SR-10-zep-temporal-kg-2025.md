# A5-SR-10: Rasmussen et al., Zep: A Temporal Knowledge Graph Architecture for Agent Memory

```json
{
  "source_identity": "Preston Rasmussen, Pavlo Paliychuk, Travis Beauvais, Jack Ryan, Daniel Chalef, 'Zep: A Temporal Knowledge Graph Architecture for Agent Memory', arXiv:2501.13956v1, https://arxiv.org/abs/2501.13956",
  "author_or_issuing_body": "Zep AI (the authors are employees of the company that sells the system)",
  "publisher": "arXiv",
  "publication_date": "2025-01-20T00:00:00Z",
  "relevant_event_date": "2025-01-20",
  "source_family": "Primary for the model the system defines. Vendor-authored preprint, not peer reviewed in the version read. Overlaps area 6 (agent memory graphs), which owns its capability claims.",
  "precise_evidence_location": "Section 2.1 Episodes (bi-temporal model); Section 2.2.3 Temporal Extraction and Edge Invalidation; prompt appendix lines for valid_at and invalid_at",
  "method": "System description with benchmark results on Deep Memory Retrieval and a further benchmark. Only the description of the temporal model is used here.",
  "limitations": "Vendor paper. Its benchmark claims ('outperforms MemGPT') are excluded as evidence of capability. Shows how one system defines two timelines and invalidates edges with an LLM. Does not show how often the invalidation is right, and does not discuss earlier temporal RDF or SQL work. The statement that the approach is 'a novel advancement' is the authors' self-assessment.",
  "provenance": "PDF downloaded with curl from https://arxiv.org/pdf/2501.13956 on 2026-11-17 and extracted with pdftotext. Re-verify at the arXiv URL."
}
```

## Evidence

- Section 2.1: "Zep implements a bi-temporal model, where timeline T represents the chronological ordering of events, and timeline T' represents the transactional order of Zep's data ingestion. While the T' timeline serves the traditional purpose of database auditing, the T timeline provides an additional dimension for modeling the dynamic nature of conversational data and memory."
- Section 2.2.3: "the system tracks four timestamps: t'\_created and t'\_expired in T' monitor when facts are created or invalidated in the system, while t_valid and t_invalid in T track the temporal range during which facts held true."
- Section 2.2.3: an LLM compares new edges with existing edges; when it finds temporally overlapping contradictions it sets the affected edge's t_invalid to the t_valid of the invalidating edge. New information is preferred.
- Prompt appendix: valid_at is "when the relationship described by the edge fact became true"; invalid_at is "when ... stopped being true".
- Not shown: any citation of SQL:2011 or valid-time and transaction-time literature in the text read.
