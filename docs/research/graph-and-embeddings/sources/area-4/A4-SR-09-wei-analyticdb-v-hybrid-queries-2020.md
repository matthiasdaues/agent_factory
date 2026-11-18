# A4-SR-09: Wei et al., AnalyticDB-V: A Hybrid Analytical Engine Towards Query Fusion for Structured and Unstructured Data

```json
{
  "source_identity": "Chuangxian Wei, Bin Wu, Sheng Wang, Renjie Lou, Chaoqun Zhan, Feifei Li, Yuanzhe Cai, 'AnalyticDB-V: A Hybrid Analytical Engine Towards Query Fusion for Structured and Unstructured Data', PVLDB 13(12) (2020) 3152-3165, doi:10.14778/3415478.3415541; https://www.vldb.org/pvldb/vol13/p3152-wei.pdf",
  "author_or_issuing_body": "Chuangxian Wei, Bin Wu, Sheng Wang, Renjie Lou, Chaoqun Zhan, Feifei Li, Yuanzhe Cai (Alibaba Group)",
  "publisher": "VLDB Endowment (Proceedings of the VLDB Endowment)",
  "publication_date": "2020-08-01T00:00:00Z",
  "relevant_event_date": "2020-08-01",
  "source_family": "Primary for the hybrid-query execution plans and the accuracy-aware cost-based plan choice in this paper. It describes a product of its authors' employer; product facts belong to area 2, and this record uses only the plan formulations.",
  "precise_evidence_location": "Abstract; Section 1 Introduction (hybrid queries); Section 5.1 Hybrid query execution (Plans A to D, Figure 9)",
  "method": "System design paper with experiments on public and in-house datasets.",
  "limitations": "Only the volume year and issue are known; the date is set to 1 August 2020. The paper is written by the vendor of the system it describes. Plans C and D were not read in detail.",
  "provenance": "PDF Downloaded with curl on 2026-11-18 and extracted with pdftotext; quotes taken from the extracted text, with line-end hyphens rejoined. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "All ANNS algorithms are implemented as physical operators in ADBV, meanwhile, accuracy-aware cost-based optimization techniques are proposed to identify effective execution plans."
- Section 1: "Developers have to rely on two separate engines to conduct hybrid query processing: a vector similarity search engine ([25, 8, 54]) for unstructured data and a database system for structured data."
- Section 5.1: "Then, brute-force search will be conducted to obtain exact top-k neighbors at the read node. This plan only works well on small datasets (e.g., thousands of points). Otherwise, it leads to unacceptable processing time due to its linear complexity."
- Section 5.1: "If approximate results satisfy the accuracy requirement and the number of tuples returned by a structured index scan reaches a certain level (e.g., ten thousands of points), ADBV tries to insert an anns scan node into physical plans to speedup the nearest neighbor search."
- Shows: the formulation of a hybrid query as a choice among physical plans (filter first then brute force, filter bitmap over compressed codes, and others) made by a cost model.
- Does not show: an index that is built with knowledge of the labels, or results on predicates outside this system.
