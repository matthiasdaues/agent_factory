# A4-SR-08: Xu et al., In-Place Updates of a Graph Index for Streaming Approximate Nearest Neighbor Search

```json
{
  "source_identity": "Haike Xu, Magdalen Dobson Manohar, Philip A. Bernstein, Badrish Chandramouli, Richard Wen, Harsha Vardhan Simhadri, 'In-Place Updates of a Graph Index for Streaming Approximate Nearest Neighbor Search', arXiv:2502.13826v1; https://arxiv.org/pdf/2502.13826",
  "author_or_issuing_body": "Haike Xu (MIT), Magdalen Dobson Manohar (Microsoft Azure and Carnegie Mellon University), Philip A. Bernstein and Badrish Chandramouli (Microsoft Research), Richard Wen (University of Maryland), Harsha Vardhan Simhadri (Microsoft)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2025-02-19T00:00:00Z",
  "relevant_event_date": "2025-02-19",
  "source_family": "Primary for IP-DiskANN. Same research group as FreshDiskANN (A4-SR-06), so it is not independent of that line.",
  "precise_evidence_location": "Abstract",
  "method": "Algorithm design plus experiments on standard benchmark update patterns.",
  "limitations": "Preprint v1; peer-reviewed status was not checked. Only the abstract and the introduction were read. The authors compare against their own group's earlier algorithm.",
  "provenance": "PDF Downloaded with curl on 2026-11-18 and extracted with pdftotext; quotes taken from the extracted text, with line-end hyphens rejoined. Re-verify at https://arxiv.org/abs/2502.13826."
}
```

## Evidence

- Abstract: "Since the graph is singly-linked, deletions are hard because there is no fast way to find in-neighbors of a deleted vertex. Therefore, to update the graph, state-of-the-art algorithms such as FreshDiskANN accumulate deletions in a batch and periodically consolidate, removing edges to deleted vertices and modifying the graph to ensure recall stability."
- Abstract: "In this paper, we present IP-DiskANN (InPlaceUpdate-DiskANN), the first algorithm to avoid batch consolidation by efficiently processing each insertion and deletion in-place."
- Shows: why deletes are hard in a directed graph index, the criticism of batch consolidation, and the in-place response.
- Does not show: independent replication, or filtered search under updates.
