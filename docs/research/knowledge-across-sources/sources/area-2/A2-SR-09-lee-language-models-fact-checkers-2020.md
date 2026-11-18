# A2-SR-09: Lee et al., Language Models as Fact Checkers?

```json
{
  "source_identity": "Nayeon Lee, Belinda Z. Li, Sinong Wang, Wen-tau Yih, Hao Ma, Madian Khabsa, 'Language Models as Fact Checkers?', FEVER workshop 2020; arXiv:2006.04102 v2",
  "author_or_issuing_body": "Nayeon Lee (Hong Kong University of Science and Technology); Li, Wang, Yih, Ma, Khabsa (Facebook AI)",
  "publisher": "Association for Computational Linguistics (FEVER 2020 workshop); preprint on arXiv",
  "publication_date": "2020-07-24T00:00:00Z",
  "relevant_event_date": "2020-07-09",
  "source_family": "Primary: the first closed-book language-model fact-checking work, by its own statement. Evaluated on FEVER (A2-SR-03).",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 3 (masking procedure, Figure 2 pipeline)",
  "method": "Masks a token in each FEVER claim, lets BERT predict it, and compares the prediction with the masked token through an entailment model.",
  "limitations": "publication_date is the arXiv v2 date that was read. relevant_event_date stands for the FEVER 2020 workshop and is approximate. The model is a masked language model, not a large generative model.",
  "provenance": "PDF downloaded with curl on 2026-11-18 and extracted with pdftotext (poppler). Words split by a hyphen at a line break are rejoined in the quotes; no other change. Re-verify at https://arxiv.org/abs/2006.04102."
}
```

## Evidence

- Abstract: "we leverage this implicit knowledge to create an effective end-to-end fact checker using a solely a language model, without any external knowledge or explicit retrieval components."
- Abstract: "Though we do not ultimately outperform methods which use explicit knowledge bases, we believe our exploration shows that this method is viable and has much room for exploration."
- Section 3: "If predicted token matches the masked token, the claim is supported, otherwise it is refuted."
- Shows: the 2020 formulation of a language model as a closed-book fact checker, and that it stays below retrieval-based systems. Does not show: behaviour on real-world claims or on claims newer than the training data.
