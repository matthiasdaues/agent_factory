# A5-SR-13: Peeters, Steiner, Bizer, Entity Matching using Large Language Models

```json
{
  "source_identity": "Ralph Peeters, Aaron Steiner, Christian Bizer, 'Entity Matching using Large Language Models', arXiv:2310.11244v4, https://arxiv.org/abs/2310.11244",
  "author_or_issuing_body": "Data and Web Science Group, University of Mannheim",
  "publisher": "arXiv",
  "publication_date": "2024-10-18T00:00:00Z",
  "relevant_event_date": "2023-10-01",
  "source_family": "Primary. Empirical study; cites PLM-based matchers such as Ditto (A5-SR-12) as the baseline it criticises.",
  "precise_evidence_location": "Abstract; Section 1 Introduction (paragraphs on PLM drawbacks and on LLMs)",
  "method": "Evaluates hosted and local generative LLMs on entity matching benchmarks in zero-shot, in-context, rule-generation and fine-tuning settings, and compares them with PLM matchers.",
  "limitations": "Version 4 is dated 18 October 2024; the first version dates from October 2023 (inferred from the arXiv identifier 2310, not from the text). Results depend on the models and prompts tested and the benchmarks used. It shows no measure of cost beyond what the paper reports, and it was not checked by rerunning.",
  "provenance": "PDF downloaded with curl from https://arxiv.org/pdf/2310.11244 on 2026-11-17 and extracted with pdftotext. Re-verify at the arXiv URL."
}
```

## Evidence

- Abstract: "Two major drawbacks of these models for entity matching are that (i) the models require significant amounts of task-specific training data and (ii) the fine-tuned models are not robust concerning out-of-distribution entities."
- Introduction: generative LLMs "have the potential to address both of these shortcomings" and "often show a better zero-shot performance compared to PLMs and are more robust concerning unseen examples".
- Abstract: "We show that there is no single best prompt but that the prompt needs to be tuned for each model/dataset combination."
- Not shown: matching over knowledge graph entities with identity constraints such as owl:sameAs.
