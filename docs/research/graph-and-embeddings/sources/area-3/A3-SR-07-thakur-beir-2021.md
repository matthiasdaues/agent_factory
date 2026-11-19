# A3-SR-07: Thakur et al., BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models

```json
{
  "source_identity": "Nandan Thakur, Nils Reimers, Andreas Rueckle, Abhishek Srivastava, Iryna Gurevych, 'BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models', arXiv:2104.08663v4; https://arxiv.org/pdf/2104.08663",
  "author_or_issuing_body": "Thakur, Reimers, Rueckle, Srivastava, Gurevych (UKP Lab, Technische Universitaet Darmstadt)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2021-04-01T00:00:00Z",
  "relevant_event_date": "2021-04-01",
  "source_family": "Primary for BEIR and its zero-shot results. Shares an author with SBERT (A3-SR-03) and MTEB (A3-SR-08), so these are not independent of each other.",
  "precise_evidence_location": "Abstract; section Results and Analysis (findings 3 and 4); Appendix on annotation and lexical bias",
  "method": "Evaluates ten retrieval systems (lexical, sparse, dense, late-interaction, re-ranking) on 18 public datasets without training on them.",
  "limitations": "publication_date is the first day of the month of the first arXiv version, taken from the arXiv identifier; the exact day was not checked. The version read is v4 of 21 October 2021. The benchmark measures retrieval, not pair classification or claim matching. The authors report that many datasets were annotated from lexical candidates, which favours lexical systems.",
  "provenance": "PDF downloaded from https://arxiv.org/pdf/2104.08663 with curl on 2026-11-18 and extracted with pdftotext. Quotes are copied from the extracted text; hyphens that the PDF inserted at line breaks are removed. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "Our results show BM25 is a robust baseline and re-ranking and late-interaction based models on average achieve the best zeroshot performances, however, at high computational costs."
- Abstract: "dense and sparse-retrieval models are computationally more efficient but often underperform other approaches, highlighting the considerable room for improvement in their generalization capabilities."
- Results and Analysis, finding 3: "dense retrievers are observed to underperform on datasets with a large domain shift compared from what they have been trained on, like in BioASQ, or task-shifts like in Touché-2020."
- Results and Analysis, finding 4: "The cross-attentional re-ranking model (BM25+CE) performs the best and is able to outperform BM25 on almost all (16/18) datasets."
- Results and Analysis, finding 4: "It appears that cross-attention and cross-attentional like operations are important for a good out-of-distribution generalization."
- Appendix: "Many BEIR datasets are found to be subject to a lexical bias, i.e. a lexical based retrieval system like TF-IDF or BM25 has been used to retrieve the candidates for annotation."
- Shows: domain shift as a limit of single-vector embeddings, and a cross-encoder second stage as the better-generalising check.
- Does not show: results for claim matching or same-idea detection as such; FEVER and Climate-FEVER appear only as retrieval datasets.
