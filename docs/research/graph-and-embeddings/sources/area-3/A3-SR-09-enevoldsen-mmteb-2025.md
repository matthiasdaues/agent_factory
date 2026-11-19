# A3-SR-09: Enevoldsen et al., MMTEB: Massive Multilingual Text Embedding Benchmark

```json
{
  "source_identity": "Kenneth Enevoldsen, Isaac Chung, Imene Kerboua, Marton Kardos, et al., Niklas Muennighoff, 'MMTEB: Massive Multilingual Text Embedding Benchmark', ICLR 2025, arXiv:2502.13595v4; https://arxiv.org/pdf/2502.13595",
  "author_or_issuing_body": "Enevoldsen (Aarhus University) and over 80 co-authors from universities and companies, with Muennighoff as last author",
  "publisher": "arXiv (Cornell University); the PDF header states publication as an ICLR 2025 conference paper",
  "publication_date": "2025-02-01T00:00:00Z",
  "relevant_event_date": "2025-02-01",
  "source_family": "Primary for MMTEB and the zero-shot English benchmark MTEB(eng, v2). Same lineage as MTEB (A3-SR-08) and shares its last author, so it is not independent criticism.",
  "precise_evidence_location": "Abstract; the paragraph that constructs MTEB(eng, v2); the results paragraph MTEB(eng, v1) vs. zero-shot MTEB(eng, v2); Limitations (English Leakage)",
  "method": "Community-built expansion of MTEB to over 500 tasks; builds smaller benchmarks by task selection and compares model rankings across the versions.",
  "limitations": "publication_date is the first day of the month of the first arXiv version, taken from the arXiv identifier; the exact day was not checked. The version read is v4 of 13 November 2025. The criticism of MTEB(eng, v1) is stated by the maintainers of the same benchmark.",
  "provenance": "PDF downloaded from https://arxiv.org/pdf/2502.13595 with curl on 2026-11-18 and extracted with pdftotext. Quotes are copied from the extracted text; hyphens that the PDF inserted at line breaks are removed. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "Text embeddings are typically evaluated on a limited set of tasks, which are constrained by language, domain, and task diversity."
- Construction of MTEB(eng, v2): "To prevent overfitting, we intend it as a zero-shot benchmark, excluding tasks like MS MARCO (Nguyen et al., 2016) and Natural Questions (Kwiatkowski et al., 2019), which are frequently used in fine-tuning."
- Results, MTEB(eng, v1) vs. zero-shot MTEB(eng, v2): "We see that notably, the smaller English models (all-MiniLM-L12, all-MiniLM-L6, all-mpnet-base) perform worse on the new benchmark. This is likely because they were trained on MS MARCO and Natural questions, which were removed as part of the benchmark conversion to a zero-shot benchmark."
- Limitations: "the benchmark may inadvertently encourage model developers to favor English or translated content by increasing their proportion in pre-training data."
- Shows: that the maintainers changed MTEB because training data overlapped with test tasks, and that rankings move when this overlap is removed.
- Does not show: an independent audit of leaderboard results.
