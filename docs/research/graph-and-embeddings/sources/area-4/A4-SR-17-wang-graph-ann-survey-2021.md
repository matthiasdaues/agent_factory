# A4-SR-17: Wang et al., A Comprehensive Survey and Experimental Comparison of Graph-Based Approximate Nearest Neighbor Search

```json
{
  "source_identity": "Mengzhao Wang, Xiaoliang Xu, Qiang Yue, Yuxiang Wang, 'A Comprehensive Survey and Experimental Comparison of Graph-Based Approximate Nearest Neighbor Search', arXiv:2101.12631v2; published in PVLDB 14(11), 2021; https://arxiv.org/pdf/2101.12631",
  "author_or_issuing_body": "Mengzhao Wang, Xiaoliang Xu, Qiang Yue, Yuxiang Wang (Hangzhou Dianzi University)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2021-05-10T00:00:00Z",
  "relevant_event_date": "2021-05-10",
  "source_family": "Secondary survey of 13 graph-based algorithms; primary for its own uniform experiments.",
  "precise_evidence_location": "Abstract; Section 3 (algorithm descriptions A1 to A13, including HNSW and NSG)",
  "method": "Survey with a taxonomy and a uniform experimental comparison on 8 real and 12 synthetic datasets.",
  "limitations": "The arXiv v2 was read; the PVLDB venue is taken from general knowledge and was not checked. Only the abstract and parts of Section 3 were read in detail.",
  "provenance": "PDF Downloaded with curl on 2026-11-18 and extracted with pdftotext; quotes taken from the extracted text, with line-end hyphens rejoined. Re-verify at https://arxiv.org/abs/2101.12631."
}
```

## Evidence

- Abstract: "In the past decade, graph-based ANNS algorithms have been the leading paradigm in this domain, with dozens of graph-based ANNS algorithms proposed."
- Section 3: "Although DPG’s search performance is comparable to HNSW, it suffers from a large index [38]."
- Section 3: "This has become even truer with the advent of frequently updated databases [60]."
- Shows: that by 2021 graph indexes were the leading family, and that their index size and construction cost were known criticisms.
- Does not show: filtered search or disk-resident update methods.
