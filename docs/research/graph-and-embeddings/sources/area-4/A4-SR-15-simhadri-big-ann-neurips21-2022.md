# A4-SR-15: Simhadri et al., Results of the NeurIPS'21 Challenge on Billion-Scale Approximate Nearest Neighbor Search

```json
{
  "source_identity": "Harsha Vardhan Simhadri, George Williams, Martin Aumüller, Matthijs Douze, Artem Babenko, Dmitry Baranchuk, Qi Chen, Lucas Hosseini, Ravishankar Krishnaswamy, Gopal Srinivasa, Suhas Jayaram Subramanya, Jingdong Wang, 'Results of the NeurIPS'21 Challenge on Billion-Scale Approximate Nearest Neighbor Search', arXiv:2205.03763v1 (Proceedings of Machine Learning Research); https://arxiv.org/pdf/2205.03763",
  "author_or_issuing_body": "Competition organisers from Microsoft Research, GSI Technology, IT University of Copenhagen, Meta AI Research, Yandex, Carnegie Mellon University, Baidu",
  "publisher": "arXiv (Cornell University); Proceedings of Machine Learning Research",
  "publication_date": "2022-05-08T00:00:00Z",
  "relevant_event_date": "2021-12-01",
  "source_family": "Primary for the competition design and results. Organisers include authors of FAISS, DiskANN, and ANN-Benchmarks, so it is not independent of those lines.",
  "precise_evidence_location": "Abstract; Section 5 Conclusion, Lessons learned",
  "method": "Report of an open competition with three tracks on standardised and specialised hardware at billion scale.",
  "limitations": "relevant_event_date stands for NeurIPS 2021 in December 2021 and is set to the first of the month. Only the abstract and the conclusion were read in detail.",
  "provenance": "PDF Downloaded with curl on 2026-11-18 and extracted with pdftotext; quotes taken from the extracted text, with line-end hyphens rejoined. Re-verify at https://arxiv.org/abs/2205.03763."
}
```

## Evidence

- Abstract: "Despite the broad range of algorithms for Approximate Nearest Neighbor Search, most empirical evaluations of algorithms have focused on smaller datasets, typically of 1 million points (Aumüller et al., 2020)."
- Abstract: "This competition1 compares ANNS algorithms at billion-scale by hardware cost, accuracy and performance."
- Note: the 1 after the word competition is a footnote mark in the source.
- Section 5: "The cost related to building indices in the cloud is a limit to frequently re-runn"
- Note: the quote above breaks at a page boundary in the extracted text; the sentence continues past it.
- Shows: the criticism of million-scale benchmarks such as ANN-Benchmarks, and the response of billion-scale tracks that count hardware cost.
- Does not show: filtered, streaming, or out-of-distribution workloads; those came in 2023 (A4-SR-16).
