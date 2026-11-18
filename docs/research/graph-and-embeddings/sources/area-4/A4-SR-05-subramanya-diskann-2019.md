# A4-SR-05: Subramanya et al., DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node

```json
{
  "source_identity": "Suhas Jayaram Subramanya, Devvrit, Rohan Kadekodi, Ravishankar Krishaswamy, Harsha Vardhan Simhadri, 'DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node', NeurIPS 2019; https://proceedings.neurips.cc/paper_files/paper/2019/file/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Paper.pdf",
  "author_or_issuing_body": "Subramanya (Carnegie Mellon University), Devvrit and Kadekodi (University of Texas at Austin), Krishaswamy and Simhadri (Microsoft Research India)",
  "publisher": "Curran Associates / NeurIPS Foundation (Advances in Neural Information Processing Systems 32)",
  "publication_date": "2019-12-08T00:00:00Z",
  "relevant_event_date": "2019-12-08",
  "source_family": "Primary for DiskANN and the Vamana graph. Secondary for its statements about IVF with product quantization, HNSW, and NSG.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 2 (Vamana, GreedySearch and RobustPrune algorithms)",
  "method": "Algorithm design plus experiments on SIFT1B and other datasets on one workstation with an SSD.",
  "limitations": "publication_date is set to the first day of the NeurIPS 2019 conference; the exact proceedings date was not checked. The paper builds a static index; it does not treat inserts or deletes.",
  "provenance": "PDF Downloaded with curl on 2026-11-18 and extracted with pdftotext; quotes taken from the extracted text, with line-end hyphens rejoined. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "Current state-of-the-art approximate nearest neighbor search (ANNS) algorithms generate indices that must be stored in main memory for fast high-recall search. This makes them expensive and limits the size of the dataset."
- Section 1: "While these schemes have a small memory footprint – less than 64 GB for storing an index on billion points in 128 dimensions – and can retrieve results in < 5 ms using GPUs or other hardware accelerators, their 1-recall@1 is rather low (around 0.5) since the data compression is lossy."
- Section 1: "The scalability of both these classes of algorithms is limited by the fact that they construct indices meant to be served from main memory."
- Shows: the criticism of in-memory graph indexes (memory cost) and of compressed inverted-file indexes (low recall), and the response of a graph index served from an SSD.
- Does not show: how the index behaves under updates or deletes, or filtered queries.
