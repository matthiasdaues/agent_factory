# A2-SR-06: Schuster et al., Towards Debiasing Fact Verification Models

```json
{
  "source_identity": "Tal Schuster, Darsh J Shah, Yun Jie Serene Yeo, Daniel Filizzola, Enrico Santus, Regina Barzilay, 'Towards Debiasing Fact Verification Models', EMNLP-IJCNLP 2019; arXiv:1908.05267 v2",
  "author_or_issuing_body": "Schuster, Shah, Filizzola, Santus, Barzilay (MIT CSAIL); Yeo (DSO National Laboratories)",
  "publisher": "Association for Computational Linguistics; preprint on arXiv",
  "publication_date": "2019-08-31T00:00:00Z",
  "relevant_event_date": "2019-11-03",
  "source_family": "Primary: an independent criticism of the FEVER dataset (A2-SR-03).",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 2 (claim-only classification, idiosyncrasies)",
  "method": "Trains a claim-only BERT classifier on FEVER, measures n-gram and label correlation, and builds a symmetric evaluation set.",
  "limitations": "publication_date is the arXiv v2 date that was read. relevant_event_date stands for the EMNLP 2019 conference and is approximate. The paper tests one dataset.",
  "provenance": "PDF downloaded with curl on 2026-11-18 and extracted with pdftotext (poppler). Words split by a hyphen at a line break are rejoined in the quotes; no other change. Re-verify at https://arxiv.org/abs/1908.05267."
}
```

## Evidence

- Abstract: "Fact verification requires validating a claim in the context of evidence. We show, however, that in the popular FEVER dataset this might not necessarily be the case. Claim-only classifiers perform competitively with top evidence-aware models."
- Section 1: "The resulting system achieves 61.7%, far above the majority baseline (33.3%)."
- Section 1: "the presence of negation phrasing highly correlates with the REFUTES label, independently of provided evidence." The label is printed in small capitals and joined here.
- Section 2: "these idiosyncrasies are induced by the way annotators altered the original claims to generate fake claims."
- Shows: that FEVER labels can be predicted without evidence, traced to the mutation step of A2-SR-03. Does not show: the same bias in datasets of real-world claims.
