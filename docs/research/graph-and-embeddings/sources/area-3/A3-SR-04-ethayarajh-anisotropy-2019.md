# A3-SR-04: Ethayarajh, How Contextual are Contextualized Word Representations?

```json
{
  "source_identity": "Kawin Ethayarajh, 'How Contextual are Contextualized Word Representations? Comparing the Geometry of BERT, ELMo, and GPT-2 Embeddings', arXiv:1909.00512v1; https://arxiv.org/pdf/1909.00512",
  "author_or_issuing_body": "Kawin Ethayarajh (Stanford University)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2019-09-02T00:00:00Z",
  "relevant_event_date": "2019-09-02",
  "source_family": "Primary for the anisotropy measurement of contextual word representations. Cites Mu et al. 2018 on isotropy of static embeddings, which I did not read.",
  "precise_evidence_location": "Abstract; Section 1 Introduction (finding 1); Section 3.4 Adjusting for Anisotropy; Section 4.1 Contextualized representations are anisotropic",
  "method": "Measures the average cosine similarity between representations of randomly sampled words in each layer of ELMo, BERT, and GPT-2.",
  "limitations": "The paper studies word representations, not sentence embeddings. It does not test a similarity task. The link to sentence-level similarity is made by later work (A3-SR-05, A3-SR-06), not by this paper.",
  "provenance": "PDF downloaded from https://arxiv.org/pdf/1909.00512 with curl on 2026-11-18 and extracted with pdftotext. Quotes are copied from the extracted text; hyphens that the PDF inserted at line breaks are removed. Re-verify at the URL above."
}
```

## Evidence

- Section 1: "In all layers of all three models, the contextualized word representations of all words are not isotropic: they are not uniformly distributed with respect to direction. Instead, they are anisotropic, occupying a narrow cone in the vector space."
- Section 1: "The anisotropy in GPT-2’s last layer is so extreme that two random words will on average have almost perfect cosine similarity!"
- Section 3.4: "consider the scenario where word vectors are so anisotropic that any two words have on average a cosine similarity of 0.99."
- Shows: that a raw cosine value between contextual representations carries a high baseline, so a high cosine alone does not mean high similarity.
- Does not show: a remedy, or results for sentence embeddings.
