# A1-SR-10: Xiang et al., When to Use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

```json
{
  "source_identity": "Zhishang Xiang, Chuanjie Wu, Qinggang Zhang, Shengyuan Chen, Zijin Hong, Xiao Huang, Jinsong Su, 'When to Use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation', ICLR 2026; arXiv:2506.05690v3; https://arxiv.org/abs/2506.05690",
  "author_or_issuing_body": "Xiang, Wu, Su (Xiamen University); Zhang, Chen, Hong, Huang (The Hong Kong Polytechnic University)",
  "publisher": "arXiv (Cornell University); conference paper at ICLR 2026",
  "publication_date": "2025-06-06T00:00:00Z",
  "relevant_event_date": "2025-06-06",
  "source_family": "Primary for the GraphRAG-Bench benchmark and its token-cost figures. Secondary for the figures it takes from Han et al. (A1-SR-09) and Zhou et al. (2025, not read).",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 4.4 token cost (Obs. 8, Tables 6 and 7); Conclusion",
  "method": "Benchmark design and evaluation of several graph-based RAG systems, including GraphRAG local and global search, LightRAG, HippoRAG, and HippoRAG 2, against vanilla RAG across tasks of rising difficulty.",
  "limitations": "Date is arXiv v1; the text read is v3 of 22 February 2026. The accuracy figures in the introduction are quoted from other studies. Shows: by 2025 the field states that graph-based RAG often underperforms vector RAG, and that graph pipelines add prompt tokens. Does not show: update or consistency behaviour of any system.",
  "provenance": "PDF downloaded with curl from arXiv on 2026-11-18 and extracted with pdftotext; quotes copied from the extracted text, with line breaks and hyphenation joined. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "Despite its conceptual promise, recent studies report that GraphRAG frequently underperforms vanilla RAG on many real-world tasks."
- Section 1: "Specifically, the previous study (Han et al., 2025) demonstrates that GraphRAG achieves 13.4% lower accuracy on Natural Question compared to vanilla RAG, with particularly poor performance on timesensitive queries (e.g., 16.6% accuracy drop for questions requiring real-time knowledge updates)." Note: secondary figure from A1-SR-09.
- Section 4.4, Obs. 8: "These results highlight that GraphRAG’s structured pipeline incurs non-trivial token overhead." Note: the sentence start was split across a table in extraction; the quoted words are contiguous.
- Conclusion: "Specifically, we first conduct an extensive analysis on existing benchmark datasets and identify that they inadequately assess GraphRAG due to the lack of domain-specific corpora and oversimplified task granularity."
