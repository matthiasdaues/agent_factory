# A5-SR-12: Li et al., Deep Entity Matching with Pre-Trained Language Models (Ditto)

```json
{
  "source_identity": "Yuliang Li, Jinfeng Li, Yoshihiko Suhara, AnHai Doan, Wang-Chiew Tan, 'Deep Entity Matching with Pre-Trained Language Models', PVLDB 14(1), 2021; arXiv:2004.00584v3, https://arxiv.org/abs/2004.00584",
  "author_or_issuing_body": "Megagon Labs; University of Wisconsin-Madison",
  "publisher": "arXiv; PVLDB",
  "publication_date": "2020-09-02T00:00:00Z",
  "relevant_event_date": "2020-09-02",
  "source_family": "Primary. System paper by authors whose group also authored DeepMatcher (reference [34] in the paper).",
  "precise_evidence_location": "Abstract; Section 1; paragraph 'Heterogeneous schemas' and footnote 2 (about DeepMatcher)",
  "method": "Fine-tunes pre-trained Transformer models as a sequence-pair classifier and evaluates on benchmark datasets and on two company datasets.",
  "limitations": "The paper compares itself with DeepMatcher and reports its own gains ('up to 29% F1', 'up to 9.8%'), which were not reproduced. Benchmark datasets only, apart from one company task. Its schema criticism of DeepMatcher is qualified by its own footnote.",
  "provenance": "PDF downloaded with curl from https://arxiv.org/pdf/2004.00584 on 2026-11-17 and extracted with pdftotext. Re-verify at the arXiv URL."
}
```

## Evidence

- Abstract: "a straightforward application of language models such as BERT, DistilBERT, or RoBERTa pre-trained on large text corpora already significantly improves the matching quality and outperforms previous state-of-the-art (SOTA), by up to 29% of F1 score on benchmark datasets."
- Abstract: "Ditto can achieve the previous SOTA results with at most half the number of labeled data."
- 'Heterogeneous schemas': Ditto "does not require data entries to adhere to the same schema ... which is a sharp contrast to other EM systems such as DeepER or DeepMatcher".
- Footnote 2: "In DeepMatcher, the requirement that both entries have the same schema can be removed by treating the values in all columns as one value under one attribute."
- Not shown: results on data the model never saw in training. A5-SR-13 raises that point.
