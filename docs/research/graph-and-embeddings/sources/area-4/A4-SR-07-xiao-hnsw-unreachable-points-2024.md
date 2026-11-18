# A4-SR-07: Xiao et al., Enhancing HNSW Index for Real-Time Updates: Addressing Unreachable Points and Performance Degradation

```json
{
  "source_identity": "Wentao Xiao, Yueyang Zhan, Rui Xi, Mengshu Hou, Jianming Liao, 'Enhancing HNSW Index for Real-Time Updates: Addressing Unreachable Points and Performance Degradation', arXiv:2407.07871v2; https://arxiv.org/pdf/2407.07871",
  "author_or_issuing_body": "Wentao Xiao, Yueyang Zhan, Rui Xi, Mengshu Hou, Jianming Liao (University of Electronic Science and Technology of China)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2024-07-15T00:00:00Z",
  "relevant_event_date": "2024-07-15",
  "source_family": "Primary for the MN-RU update algorithm and the authors' observation of unreachable points in HNSW. Independent of the Microsoft DiskANN group.",
  "precise_evidence_location": "Abstract; Section I Introduction (markDelete and replaced update)",
  "method": "Experiments with long sequences of deletes, inserts, and queries on an HNSW implementation, then a modified update algorithm.",
  "limitations": "Preprint v2; peer-reviewed publication status was not checked. The criticism targets one HNSW implementation's markDelete and replaced-update routines, so it may not hold for every HNSW implementation. Only the abstract and the introduction were read in detail.",
  "provenance": "PDF Downloaded with curl on 2026-11-18 and extracted with pdftotext; quotes taken from the extracted text, with line-end hyphens rejoined. Re-verify at https://arxiv.org/abs/2407.07871."
}
```

## Evidence

- Abstract: "However, the performance of HNSW and most graph-based indices become unacceptable when faced with a large number of real-time deletions, insertions, and updates."
- Section I: "The first and primary concern arises from the utilization of the markDelete algorithm and the replaced update insertion algorithm (hereafter referred to as replaced update for brevity), leading to a scenario where specific data points may become inaccessible"
- Shows: an independent criticism of HNSW updates: delete marks and replaced updates can leave points that no search reaches.
- Does not show: results for DiskANN-family indexes, or a comparison with full rebuilds.
