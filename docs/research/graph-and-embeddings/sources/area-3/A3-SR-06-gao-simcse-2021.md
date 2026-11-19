# A3-SR-06: Gao, Yao, and Chen, SimCSE

```json
{
  "source_identity": "Tianyu Gao, Xingcheng Yao, Danqi Chen, 'SimCSE: Simple Contrastive Learning of Sentence Embeddings', arXiv:2104.08821v4; https://arxiv.org/pdf/2104.08821",
  "author_or_issuing_body": "Gao, Chen (Princeton University); Yao (Tsinghua University)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2021-04-01T00:00:00Z",
  "relevant_event_date": "2021-04-01",
  "source_family": "Primary for SimCSE. Compares against InferSent (A3-SR-01), SBERT (A3-SR-03), and BERT-flow (A3-SR-05).",
  "precise_evidence_location": "Abstract; Section 5 Connection to Anisotropy; Section 6 Experiments (Table 5)",
  "method": "Trains sentence encoders with a contrastive objective: unsupervised with dropout noise as the only augmentation, supervised with NLI entailment pairs as positives and contradiction pairs as hard negatives. Evaluates on seven STS tasks and seven transfer tasks.",
  "limitations": "publication_date is the first day of the month of the first arXiv version, taken from the arXiv identifier; the exact day was not checked. The version read is v4 of 18 May 2022. The evaluation is on STS and transfer tasks; MTEB (A3-SR-08) names this narrow evaluation as a limit. The abstract sentence on NLI pairs holds inner quotation marks and is given as a paraphrase.",
  "provenance": "PDF downloaded from https://arxiv.org/pdf/2104.08821 with curl on 2026-11-18 and extracted with pdftotext. Quotes are copied from the extracted text; hyphens that the PDF inserted at line breaks are removed. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "We first describe an unsupervised approach, which takes an input sentence and predicts itself in a contrastive objective, with only standard dropout used as noise."
- Abstract, paraphrase in my words: the supervised variant uses NLI entailment pairs as positives and contradiction pairs as hard negatives.
- Abstract: "our unsupervised and supervised models using BERTbase achieve an average of 76.3% and 81.6% Spearman’s correlation respectively, a 4.2% and 2.2% improvement compared to the previous best results."
- Abstract: "We also show—both theoretically and empirically—that the contrastive learning objective regularizes pre-trained embeddings’ anisotropic space to be more uniform, and it better aligns positive pairs when supervised signals are available."
- Section 5: "Compared to post-processing methods in Li et al. (2020); Su et al. (2021), which only aim to encourage isotropic representations, contrastive learning also optimizes for aligning positive pairs by the first term in Eq. 6, which is the key to the success of SimCSE."
- Shows: the criticism of post-processing for anisotropy and the step to a training objective.
- Does not show: behaviour on retrieval, negation, or long texts.
