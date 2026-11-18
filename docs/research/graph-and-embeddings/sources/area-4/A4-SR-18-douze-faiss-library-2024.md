# A4-SR-18: Douze et al., The Faiss Library

```json
{
  "source_identity": "Matthijs Douze, Alexandr Guzhva, Chengqi Deng, Jeff Johnson, Gergely Szilvasy, Pierre-Emmanuel Mazaré, Maria Lomeli, Lucas Hosseini, Hervé Jégou, 'The Faiss Library', arXiv:2401.08281v4; https://arxiv.org/pdf/2401.08281",
  "author_or_issuing_body": "Faiss authors at FAIR (Meta), Zilliz, DeepSeek, Skip Labs",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2025-10-23T00:00:00Z",
  "relevant_event_date": "2024-01-16",
  "source_family": "Primary for the Faiss library's design; secondary for its overview of HNSW, DiskANN, FreshDiskANN, and the BigANN 2023 filtered track. Shares an author with the product quantization paper (A4-SR-03).",
  "precise_evidence_location": "Section 6.1 Identifier-based operations (Index updates, Graph indexes); Section 6.2 Filtered search (vector-first or metadata-first)",
  "method": "Description of a software library and its algorithms, with benchmarks.",
  "limitations": "v4 of 23 October 2025 was read; v1 was posted in January 2024. Faiss is a library, so statements about its API are product facts for area 2; this record uses the statements about algorithms in general. Two-column extraction scrambles some lines, so quotes were checked against the layout-preserving extraction.",
  "provenance": "PDF Downloaded with curl on 2026-11-18 and extracted with pdftotext; quotes taken from the extracted text, with line-end hyphens rejoined. A second extraction with pdftotext -layout was used to read the two columns. Re-verify at https://arxiv.org/abs/2401.08281."
}
```

## Evidence

- Section 6.1: "Note that if the vector distribution changes significantly because of additions/removals or updates, then the efficiency of any technique that fits the data distribution degrades. This includes IVF and PQ compression."
- Note: the word significantly is split across two lines in the source column as signif- and icantly.
- Section 6.1: "The graph index HNSW does not support suppression and mutation, and NSG does not even support adding vectors incrementally."
- Section 6.2: "The metadata-first filtering generates a subset of vectors to compare with that can then be compared using brute force search."
- Note: the word generates is split across two lines in the source column as gen- and erates.
- Section 6.2: "Brute force search is slow but acceptable if the subset size is small, and the results are exact."
- Shows: that indexes trained on the data distribution (IVF, PQ) degrade when the distribution shifts under updates, and the choice between vector-first and metadata-first filtering by estimated subset size.
- Does not show: measured degradation figures for IVF under updates.
