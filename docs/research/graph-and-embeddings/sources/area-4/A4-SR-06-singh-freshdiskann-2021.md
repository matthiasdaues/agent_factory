# A4-SR-06: Singh et al., FreshDiskANN: A Fast and Accurate Graph-Based ANN Index for Streaming Similarity Search

```json
{
  "source_identity": "Aditi Singh, Suhas Jayaram Subramanya, Ravishankar Krishnaswamy, Harsha Vardhan Simhadri, 'FreshDiskANN: A Fast and Accurate Graph-Based ANN Index for Streaming Similarity Search', arXiv:2105.09613v1; https://arxiv.org/pdf/2105.09613",
  "author_or_issuing_body": "Aditi Singh, Ravishankar Krishnaswamy, Harsha Vardhan Simhadri (Microsoft Research India); Suhas Jayaram Subramanya (Carnegie Mellon University)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2021-05-20T00:00:00Z",
  "relevant_event_date": "2021-05-20",
  "source_family": "Primary for FreshVamana and FreshDiskANN. Secondary for its statements about HNSW, NSG, and periodic rebuilds in industry.",
  "precise_evidence_location": "Section 1 Introduction (contributions list, rebuild cost); Section 3.3 (recall drop under updates); Section 4 (lazy deletion, DeleteList, delete consolidation)",
  "method": "Experiments that run cycles of deletes and re-inserts on HNSW, NSG, and Vamana, then algorithm design and system experiments at billion scale.",
  "limitations": "Preprint v1; peer-reviewed publication status was not checked. The rebuild-time figure for HNSW is the authors' own estimate. Industry practice is stated by the authors, not documented by a cited survey.",
  "provenance": "PDF Downloaded with curl on 2026-11-18 and extracted with pdftotext; quotes taken from the extracted text, with line-end hyphens rejoined. Re-verify at https://arxiv.org/abs/2105.09613."
}
```

## Evidence

- Section 1: "As a result, the current practice in industry is to periodically re-build such indices from scratch [18] to manifest recent changes to the underlying dataset. However, this is a very expensive operation."
- Section 1: "It would take about 1.5-2 hours on a dedicated high-end 48-core machine to build a good quality HNSW index [47] over 100M points."
- Section 1: "We demonstrate how simple graph update rules result in degradation of index quality over a stream of insertions and deletions for popular graph-based algorithms such as HNSW [43] and NSG [28]."
- Section 4: "It turns out that the graph becomes sparse (lesser average degree) as we update it, and hence it becomes less navigable."
- Section 4: "FreshVamana employs a lazy deletion strategy – when a point 𝑝 is deleted, we add 𝑝 to a DeleteList without changing the graph."
- Shows: the cost of periodic rebuilds, measured recall loss of graph indexes under update streams, and the response of lazy deletion with later batch consolidation.
- Does not show: in-place deletion without batch consolidation, or filtered search.
