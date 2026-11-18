# A3-SR-05: Li et al., On the Sentence Embeddings from Pre-trained Language Models (BERT-flow)

```json
{
  "source_identity": "Bohan Li, Hao Zhou, Junxian He, Mingxuan Wang, Yiming Yang, Lei Li, 'On the Sentence Embeddings from Pre-trained Language Models', arXiv:2011.05864v1; https://arxiv.org/pdf/2011.05864",
  "author_or_issuing_body": "Li, Zhou, Wang, Lei Li (ByteDance AI Lab); Li, He, Yang (Language Technologies Institute, Carnegie Mellon University)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2020-11-02T00:00:00Z",
  "relevant_event_date": "2020-11-02",
  "source_family": "Primary for BERT-flow. Cites SBERT (A3-SR-03) for the poor similarity of raw BERT embeddings.",
  "precise_evidence_location": "Abstract; Section 1 Introduction",
  "method": "Analyses BERT sentence embeddings and maps them to an isotropic Gaussian distribution with a normalizing flow trained without labels; evaluates on STS tasks.",
  "limitations": "Only the abstract, introduction, and the comparison set-up were read closely. The evaluation uses STS tasks; it does not test retrieval or the five tasks of this survey.",
  "provenance": "PDF downloaded from https://arxiv.org/pdf/2011.05864 with curl on 2026-11-18 and extracted with pdftotext. Quotes are copied from the extracted text; hyphens that the PDF inserted at line breaks are removed. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "the sentence embeddings from the pre-trained language models without fine-tuning have been found to poorly capture semantic meaning of sentences."
- Abstract: "We find that BERT always induces a non-smooth anisotropic semantic space of sentences, which harms its performance of semantic similarity."
- Abstract: "we propose to transform the anisotropic sentence embedding distribution to a smooth and isotropic Gaussian distribution through normalizing flows that are learned with an unsupervised objective."
- Section 1: "the sentence embeddings from BERT without finetuning are significantly inferior in terms of semantic textual similarity (Reimers and Gurevych, 2019) – for example, they even underperform the GloVe (Pennington et al., 2014) embeddings which are not contextualized and trained with a much simpler model."
- Shows: the step that links the SBERT criticism to anisotropy at sentence level and answers it with a post-processing transform.
- Does not show: whether the transform helps outside STS.
