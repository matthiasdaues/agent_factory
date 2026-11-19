# A3-SR-01: Conneau et al., Supervised Learning of Universal Sentence Representations from Natural Language Inference Data (InferSent)

```json
{
  "source_identity": "Alexis Conneau, Douwe Kiela, Holger Schwenk, Loic Barrault, Antoine Bordes, 'Supervised Learning of Universal Sentence Representations from Natural Language Inference Data', arXiv:1705.02364v5; https://arxiv.org/pdf/1705.02364",
  "author_or_issuing_body": "Conneau, Kiela, Schwenk, Bordes (Facebook AI Research); Barrault (LIUM, Universite Le Mans)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2017-05-01T00:00:00Z",
  "relevant_event_date": "2017-05-01",
  "source_family": "Primary for the InferSent encoder and its training on SNLI. Independent of the other area-3 records, which cite it.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 3.1 The Natural Language Inference task; Table 2",
  "method": "Trains several sentence encoder architectures on the SNLI natural language inference data and transfers the fixed encoder to other tasks, including semantic textual similarity, through the SentEval tasks.",
  "limitations": "publication_date is the first day of the month of the first arXiv version, taken from the arXiv identifier; the exact day was not checked. The version read is v5 of 8 July 2018. The paper evaluates transfer tasks; it does not test claim matching, text reuse, or near-duplicate detection. The text extraction interleaves the two columns, so quotes were taken from the layout extraction. It does not show how the encoder handles negation or length.",
  "provenance": "PDF downloaded from https://arxiv.org/pdf/1705.02364 with curl on 2026-11-18 and extracted with pdftotext. Quotes are copied from the extracted text; hyphens that the PDF inserted at line breaks are removed. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "Efforts to obtain embeddings for larger chunks of text, such as sentences, have however not been so successful."
- Abstract: "we show how universal sentence representations trained using the supervised data of the Stanford Natural Language Inference datasets can consistently outperform unsupervised methods like SkipThought vectors (Kiros et al., 2015) on a wide range of transfer tasks."
- Abstract: "our work tends to indicate the suitability of natural language inference for transfer learning to other NLP tasks."
- Section 3.1 and Table 2: the training signal is SNLI, with the labels entailment, neutral, and contradiction. Paraphrase in my words; the table holds example pairs.
- Shows: the step from unsupervised sentence encoders to an encoder trained on natural language inference labels.
- Does not show: any comparison with BERT, which appeared later, or any check of what the vectors miss.
