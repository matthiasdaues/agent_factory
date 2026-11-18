# A2-SR-13: Quelle and Bovet, The Perils and Promises of Fact-checking with Large Language Models

```json
{
  "source_identity": "Dorian Quelle, Alexandre Bovet, 'The Perils & Promises of Fact-checking with Large Language Models', Frontiers in Artificial Intelligence 7 (2024); arXiv:2310.13549 v2",
  "author_or_issuing_body": "Dorian Quelle, Alexandre Bovet (University of Zurich)",
  "publisher": "Frontiers Media (Frontiers in Artificial Intelligence); preprint on arXiv",
  "publication_date": "2024-02-07T00:00:00Z",
  "relevant_event_date": "2023-10-01",
  "source_family": "Primary: an independent evaluation of large-language-model agents for fact-checking.",
  "precise_evidence_location": "Abstract; Section 1 Introduction (summary of findings); Section 2.2.1 experimental conditions",
  "method": "Runs GPT-3.5 and GPT-4 agents that write search queries, retrieve context and give a verdict with cited sources, with and without retrieval, on PolitiFact and a multilingual set of fact-checks.",
  "limitations": "publication_date is the arXiv v2 date that was read; the journal version was not read. relevant_event_date is October 2023 from the paper header (month only). The study uses commercial models whose versions change.",
  "provenance": "PDF downloaded with curl on 2026-11-18 and extracted with pdftotext (poppler). Words split by a hyphen at a line break are rejoined in the quotes; no other change. Re-verify at https://arxiv.org/abs/2310.13549."
}
```

## Evidence

- Abstract: "Our results show the enhanced prowess of LLMs when equipped with contextual information. GPT-4 outperforms GPT-3, but accuracy varies based on query language and claim veracity. While LLMs show promise in fact-checking, caution is essential due to inconsistent accuracy."
- Section 1: "We find that incorporating contextual information significantly improves accuracy. This highlights the importance of gathering external evidence during automated verification."
- Section 2.2.1: "When the model is able to retrieve contextual information, any results from PolitiFact are excluded from the results."
- Shows: that closed-book language-model checking (the setup of A2-SR-09) does worse than the same model with retrieval, in this study. Does not show: results on claims newer than the models' training data, which the study does not separate.
