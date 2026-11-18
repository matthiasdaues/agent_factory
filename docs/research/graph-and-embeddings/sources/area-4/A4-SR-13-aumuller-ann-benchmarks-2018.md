# A4-SR-13: Aumüller, Bernhardsson, Faithfull, ANN-Benchmarks: A Benchmarking Tool for Approximate Nearest Neighbor Algorithms

```json
{
  "source_identity": "Martin Aumüller, Erik Bernhardsson, Alexander Faithfull, 'ANN-Benchmarks: A Benchmarking Tool for Approximate Nearest Neighbor Algorithms', arXiv:1807.05614v2; journal version in Information Systems 87 (2020); https://arxiv.org/pdf/1807.05614",
  "author_or_issuing_body": "Martin Aumüller, Alexander Faithfull (IT University of Copenhagen); Erik Bernhardsson (Better Inc.)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2018-07-17T00:00:00Z",
  "relevant_event_date": "2018-07-17",
  "source_family": "Primary for the design of ANN-Benchmarks.",
  "precise_evidence_location": "Abstract; Section 3.4 Dataset size; Section 3.5 Multi-threading and batched queries",
  "method": "Description of a benchmarking framework and an evaluation of algorithms run in it.",
  "limitations": "The arXiv v2 was read, not the Information Systems journal version, which may differ. The benchmark results in the paper reflect algorithms as of 2018.",
  "provenance": "PDF Downloaded with curl on 2026-11-18 and extracted with pdftotext; quotes taken from the extracted text, with line-end hyphens rejoined. Re-verify at https://arxiv.org/abs/1807.05614."
}
```

## Evidence

- Abstract: "This paper describes ANN-Benchmarks, a tool for evaluating the performance of in-memory approximate nearest neighbor algorithms."
- Section 3.4: "In practice, this means that the framework can handle datasets with millions of points of dimensionality up to a few thousand dimensions."
- Section 3.5: "The experiment loop is, by default, run on a single CPU in a single thread."
- Shows: what ANN-Benchmarks measures: in-memory, single-thread, million-scale, static datasets, compared by quality and speed.
- Does not show: billion-scale or disk-resident indexes, filtered queries, or updates.
