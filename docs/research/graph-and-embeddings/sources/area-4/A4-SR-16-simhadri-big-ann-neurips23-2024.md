# A4-SR-16: Simhadri et al., Results of the Big ANN: NeurIPS'23

```json
{
  "source_identity": "Harsha Vardhan Simhadri, Martin Aumüller, Amir Ingber, Matthijs Douze, George Williams, Magdalen Dobson Manohar, Dmitry Baranchuk, Edo Liberty, Frank Liu, Ben Landrum, and others, 'Results of the Big ANN: NeurIPS'23', arXiv:2409.17424v1; https://arxiv.org/pdf/2409.17424",
  "author_or_issuing_body": "Competition organisers and track winners from Microsoft, IT University of Copenhagen, Pinecone, Meta, Yandex, Zilliz, University of Maryland, Carnegie Mellon University, Fudan University, Shanghai Jiao Tong University, Baidu, and others",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2024-09-25T00:00:00Z",
  "relevant_event_date": "2023-12-01",
  "source_family": "Primary for the 2023 competition tracks and baselines. Overlaps in organisers with A4-SR-15.",
  "precise_evidence_location": "Abstract; Section 2.3 Streaming Track; Section 4.1 Filtered Search Track",
  "method": "Report of an open competition with filtered, out-of-distribution, sparse, and streaming tracks on limited hardware.",
  "limitations": "relevant_event_date stands for NeurIPS 2023 in December 2023 and is set to the first of the month. The author list in the JSON is shortened. Vendor employees are among the organisers; vendor facts belong to area 2.",
  "provenance": "PDF Downloaded with curl on 2026-11-18 and extracted with pdftotext; quotes taken from the extracted text, with line-end hyphens rejoined. Re-verify at https://arxiv.org/abs/2409.17424."
}
```

## Evidence

- Abstract: "Unlike prior challenges that emphasized scaling up classical ANN search [21], this competition addressed filtered search, out-of-distribution data, sparse and streaming variants of ANNS."
- Section 2.3: "In this track, the underlying databases evolved over time, and participants were to design an index that supports insertions, deletions and searches."
- Section 4.1: "In vector-first mode, the search is performed with a Faiss IVF index and vector results that do not satisfy the word constraint are removed from the result list."
- Shows: how the benchmark lineage added filtered search and update streams after the 2021 billion-scale tracks, and the vector-first baseline for filtered search.
- Does not show: range predicates or high-cardinality predicates in its filtered track; the track uses word tags.
