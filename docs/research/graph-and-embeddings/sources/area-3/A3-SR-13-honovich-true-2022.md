# A3-SR-13: Honovich et al., TRUE: Re-evaluating Factual Consistency Evaluation

```json
{
  "source_identity": "Or Honovich, Roee Aharoni, Jonathan Herzig, Hagai Taitelbaum, Vered Cohen, Doron Kukliansky, Thomas Scialom, Idan Szpektor, Avinatan Hassidim, Yossi Matias, 'TRUE: Re-evaluating Factual Consistency Evaluation', arXiv:2204.04991v3; https://arxiv.org/pdf/2204.04991",
  "author_or_issuing_body": "Honovich (Tel Aviv University); Aharoni, Herzig, Taitelbaum, Cohen, Kukliansky, Szpektor, Hassidim, Matias (Google Research); Scialom (Meta AI)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2022-04-01T00:00:00Z",
  "relevant_event_date": "2022-04-01",
  "source_family": "Primary for the TRUE meta-evaluation. Includes FEVER and VitaminC as datasets.",
  "precise_evidence_location": "Abstract; Section 3.3 Natural Language Inference Metrics; Section 4 results (Table 3); Section 5 Analysis (input length)",
  "method": "Compares factual consistency metrics, including an NLI model (T5-11B fine-tuned on ANLI), question-answering metrics, and embedding-based BERTScore, on 11 annotated datasets by ROC AUC per example.",
  "limitations": "publication_date is the first day of the month of the first arXiv version, taken from the arXiv identifier; the exact day was not checked. The task is consistency of generated text with a grounding text, not claim matching between two stored claims. The NLI model is large (11 billion parameters). The authors measured the scores and I did not repeat them.",
  "provenance": "PDF downloaded from https://arxiv.org/pdf/2204.04991 with curl on 2026-11-18 and extracted with pdftotext. Quotes are copied from the extracted text; hyphens that the PDF inserted at line breaks are removed. Re-verify at the URL above."
}
```

## Evidence

- Section 3.3: "we compute the entailment probability with the grounding text as the premise and the generated text as the hypothesis and use it as the examplelevel factual consistency score."
- Section 4: "The results show that the NLI-based models (ANLI, SCZS) outperformed the other approaches on 6 datasets, with average AUC of 81.5 and 81.4 for ANLI and SCZS, respectively."
- Table 3: BERTScore, an embedding-based metric, reaches an average ROC AUC of 71.4. Read from the table; the number is mine to transcribe, not a quoted sentence.
- Section 5: "We find that there is a consistent degradation for texts longer than 200 tokens for all metrics"
- Shows: an NLI check is directional (premise and hypothesis) and scores higher than embedding similarity for consistency; NLI degrades with length too.
- Does not show: NLI as a filter on candidates from a vector search; that pipeline is not tested.
- Note: the footnote number after SCZS in the Section 4 quote is dropped.
