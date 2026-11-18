# A3-SR-14: Kazemi et al., Claim Matching Beyond English to Scale Global Fact-Checking

```json
{
  "source_identity": "Ashkan Kazemi, Kiran Garimella, Devin Gaffney, Scott A. Hale, 'Claim Matching Beyond English to Scale Global Fact-Checking', arXiv:2106.00853v1; https://arxiv.org/pdf/2106.00853",
  "author_or_issuing_body": "Kazemi (University of Michigan and Meedan); Garimella (MIT); Gaffney (Meedan); Hale (University of Oxford and Meedan)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2021-06-01T00:00:00Z",
  "relevant_event_date": "2021-06-01",
  "source_family": "Primary for the claim matching definition, dataset, and threshold experiments. Cites Shaar et al. 2020 on detecting previously fact-checked claims, which I read but did not record.",
  "precise_evidence_location": "Abstract; Section 2.1 semantic textual similarity versus claim matching; the Threshold Classifier paragraph (Table 5, Figure 2)",
  "method": "Annotates WhatsApp tipline messages and fact-checks in five languages for claim matching; trains a multilingual embedding model by knowledge distillation; classifies pairs by a cosine threshold.",
  "limitations": "Data come from one fact-checking context (India). The threshold of 0.71 is fitted on this data. Some sentences hold inner quotation marks and are paraphrased.",
  "provenance": "PDF downloaded from https://arxiv.org/pdf/2106.00853 with curl on 2026-11-18 and extracted with pdftotext. Quotes are copied from the extracted text; hyphens that the PDF inserted at line breaks are removed. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "We define claim matching as the task of identifying pairs of textual messages containing claims that can be served with one fact-check."
- Section 2.1: "While semantic textual similarity is similar to claim matching, the nuances in the latter require special attention. Claim matching is the task of matching messages with claims that can be served with the same fact-check and that does not always translate to message pairs having the same meanings. Moreover, claim matching requires working with content of variable length."
- Threshold Classifier, paraphrase in my words: the first classifier is a plain threshold on cosine similarity; pairs above it count as matches.
- Threshold Classifier: "The English-only SBERT model performs slightly better with a maximum F1 score of 0.90±0.09 at a threshold of 0.71 on English data"
- Threshold Classifier: "We find the models have comparable performance to I-XLM-R on English & Hindi while F1 scores for other languages are between 0.17 and 0.61."
- Shows: claim matching differs from meaning similarity, and a cosine threshold works in English and fails in lower-resource languages.
- Does not show: a check that confirms a match beyond the threshold.
