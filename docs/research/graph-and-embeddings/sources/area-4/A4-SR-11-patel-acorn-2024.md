# A4-SR-11: Patel et al., ACORN: Performant and Predicate-Agnostic Search Over Vector Embeddings and Structured Data

```json
{
  "source_identity": "Liana Patel, Peter Kraft, Carlos Guestrin, Matei Zaharia, 'ACORN: Performant and Predicate-Agnostic Search Over Vector Embeddings and Structured Data', arXiv:2403.04871v1; published in Proceedings of the ACM on Management of Data (SIGMOD 2024); https://arxiv.org/pdf/2403.04871",
  "author_or_issuing_body": "Liana Patel, Carlos Guestrin (Stanford University); Peter Kraft (DBOS, Inc.); Matei Zaharia (UC Berkeley)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2024-03-07T00:00:00Z",
  "relevant_event_date": "2024-03-07",
  "source_family": "Primary for ACORN. Secondary for its descriptions of pre-filtering, post-filtering, Filtered-DiskANN, HQANN, and NHQ. Independent of the DiskANN group.",
  "precise_evidence_location": "Abstract; Section 1 Introduction (three common methods and their limits)",
  "method": "Algorithm design that extends HNSW, plus experiments on benchmark datasets with simple predicates and on multi-modal datasets with complex predicates.",
  "limitations": "The arXiv v1 was read, not the SIGMOD print. The paper's use of the word selectivity follows its own definition, which was not checked; quotes keep its wording.",
  "provenance": "PDF Downloaded with curl on 2026-11-18 and extracted with pdftotext; quotes taken from the extracted text, with line-end hyphens rejoined. Re-verify at https://arxiv.org/abs/2403.04871."
}
```

## Evidence

- Section 1: "Pre-filtering first finds all records in the dataset that pass the query predicate, then performs brute force similarity-search over the filtered vector set. This approach scales poorly, becoming inefficient for medium to high selectivity predicates on large datasets."
- Section 1: "Since the database vectors closest to the query vector may not pass the predicate, post-filtering methods must typically expand the search scope. This is often expensive, particularly for search predicates with low selectivity or low correlation to the query vector, as we show in Figure 2."
- Section 1: "For example, Filtered-DiskANN [25] outperforms prior baselines, but restricts the cardinality of the predicate set to about 1,000 and only supports equality predicates."
- Abstract: "ACORN introduces the idea of predicate subgraph traversal to emulate a theoretically ideal, but impractical, hybrid search strategy."
- Shows: the criticism of pre-filtering, post-filtering, and label-specialized indexes such as Filtered-DiskANN, and the response of a predicate-agnostic HNSW variant.
- Does not show: an independent evaluation; that comes later in A4-SR-12. It does not cover updates to the filtered index.
