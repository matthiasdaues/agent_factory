# A4-SR-12: Iff et al., Benchmarking Filtered Approximate Nearest Neighbor Search Algorithms on Transformer-based Embedding Vectors

```json
{
  "source_identity": "Patrick Iff, Paul Brügger, Marcin Chrapek, Maciej Besta, Torsten Hoefler, 'Benchmarking Filtered Approximate Nearest Neighbor Search Algorithms on Transformer-based Embedding Vectors', arXiv:2507.21989v1; https://arxiv.org/pdf/2507.21989v1",
  "author_or_issuing_body": "Patrick Iff, Paul Brügger, Marcin Chrapek, Maciej Besta, Torsten Hoefler (ETH Zurich)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2025-07-29T00:00:00Z",
  "relevant_event_date": "2025-07-29",
  "source_family": "Primary for its survey, taxonomy, dataset, and benchmark of filtered approximate nearest neighbour search (FANNS). Independent of the ACORN and DiskANN authors.",
  "precise_evidence_location": "Abstract",
  "method": "Literature survey and taxonomy, plus a benchmark of FANNS methods on a new dataset of embeddings of 2.7 million arXiv abstracts with 11 attributes.",
  "limitations": "Preprint v1; peer-reviewed status was not checked. Only the abstract was read in detail. A second 2025 filtered-search benchmark (arXiv:2509.07789) was found by search but not read.",
  "provenance": "PDF Downloaded with curl on 2026-11-18 and extracted with pdftotext; quotes taken from the extracted text, with line-end hyphens rejoined. Re-verify at https://arxiv.org/abs/2507.21989."
}
```

## Evidence

- Abstract: "By doing so, we identify a key challenge in the current FANNS landscape: the lack of diverse and realistic datasets, particularly ones derived from the latest transformer-based text embedding models."
- Abstract: "ACORN, for example, supports various filter types and performs reliably across dataset scales but is often outperformed by more specialized methods."
- Abstract: "Filtered-DiskANN and UNG excel on the medium-scale dataset but fail on the large-scale dataset, highlighting the challenge posed by transformer-based embeddings, which are often more than an order of magnitude larger than earlier embeddings. We conclude that no universally best method exists."
- Shows: an independent criticism of both ACORN and Filtered-DiskANN, and of the datasets used to benchmark filtered search.
- Does not show: a method that resolves the criticism, or results under updates.
