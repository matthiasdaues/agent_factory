# A3-SR-03: Reimers and Gurevych, Sentence-BERT

```json
{
  "source_identity": "Nils Reimers, Iryna Gurevych, 'Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks', arXiv:1908.10084v1; https://arxiv.org/pdf/1908.10084",
  "author_or_issuing_body": "Reimers, Gurevych (UKP Lab, Technische Universitaet Darmstadt)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2019-08-01T00:00:00Z",
  "relevant_event_date": "2019-08-01",
  "source_family": "Primary for SBERT and for its measurement of raw BERT embeddings. Builds on InferSent (A3-SR-01) and evaluates on the STS tasks (A3-SR-02).",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 4.1 Unsupervised STS (Table 1); Section 4.2 Supervised STS (Table 2)",
  "method": "Fine-tunes BERT and RoBERTa in a siamese network on NLI and STS data and compares the cosine similarity of pooled embeddings with human STS scores (Spearman rank correlation).",
  "limitations": "publication_date is the first day of the month of the first arXiv version, taken from the arXiv identifier; the exact day was not checked. The comparison uses STS and SentEval tasks only; it does not test retrieval, claim matching, or negation. The authors measured the timings and I did not repeat them.",
  "provenance": "PDF downloaded from https://arxiv.org/pdf/1908.10084 with curl on 2026-11-18 and extracted with pdftotext. Quotes are copied from the extracted text; hyphens that the PDF inserted at line breaks are removed. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "Finding the most similar pair in a collection of 10,000 sentences requires about 50 million inference computations (~65 hours) with BERT. The construction of BERT makes it unsuitable for semantic similarity search as well as for unsupervised tasks like clustering."
- Abstract: "we present Sentence-BERT (SBERT), a modification of the pretrained BERT network that use siamese and triplet network structures to derive semantically meaningful sentence embeddings that can be compared using cosine-similarity."
- Section 1: "The most commonly used approach is to average the BERT output layer (known as BERT embeddings) or by using the output of the first token (the [CLS] token). As we will show, this common practice yields rather bad sentence embeddings, often worse than averaging GloVe embeddings (Pennington et al., 2014)."
- Section 4.1: "The results shows that directly using the output of BERT leads to rather poor performances. Averaging the BERT embeddings achieves an average correlation of only 54.81, and using the CLStoken output only achieves an average correlation of 29.19. Both are worse than computing average GloVe embeddings."
- Section 4.2: "This two-step approach had an especially large impact for the BERT cross-encoder, which improved the performance by 3-4 points."
- Shows: the criticism of raw BERT embeddings for similarity, the bi-encoder answer, and the cost of a cross-encoder on all pairs.
- Does not show: why raw BERT embeddings perform poorly. The geometric explanation comes from A3-SR-04 and A3-SR-05.
