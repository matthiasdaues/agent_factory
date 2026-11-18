# A4-SR-12: Hanselowski et al., A Retrospective Analysis of the Fake News Challenge Stance Detection Task

```json
{
  "source_identity": "Andreas Hanselowski, Avinesh PVS, Benjamin Schiller, Felix Caspelherr, Debanjan Chaudhuri, Christian M. Meyer, Iryna Gurevych, 'A Retrospective Analysis of the Fake News Challenge Stance-Detection Task', Proceedings of COLING 2018; https://aclanthology.org/C18-1158.pdf",
  "author_or_issuing_body": "Hanselowski, PVS, Schiller, Caspelherr, Meyer, Gurevych (Technische Universitaet Darmstadt); Chaudhuri (University of Bonn)",
  "publisher": "Association for Computational Linguistics (ACL Anthology)",
  "publication_date": "2018-08-01T00:00:00Z",
  "relevant_event_date": "2017-01-01",
  "source_family": "Primary for its reanalysis, the F1m metric, and the human agreement study. Secondary for the FNC-1 task definition (Pomerleau and Rao, 2017), which it describes; the FNC-1 site was not read.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 4 Performance evaluation, FNC metric and human upper bound (p. 1862); Section 5.1 Error analysis (pp. 1862-1863)",
  "method": "Reproduces the three top FNC-1 systems, analyses the official metric, asks five human raters to label 200 headline-article pairs, and runs an error analysis and feature ablation.",
  "limitations": "Month-only date; set to 1 August 2018 (COLING 2018 month). relevant_event_date stands for FNC-1 in 2017. The human study covers 200 pairs only. The stance is of an article towards a headline, so the reference text is a headline, not a primary report.",
  "provenance": "PDF downloaded with curl on 2026-11-18 from the ACL Anthology and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Section 1: "The goal of the FNC-1 challenge is to determine the perspective (or stance) of a news article relative to a given headline. An article's stance can either agree or disagree with the headline, discuss the same topic, or it is completely unrelated."
- Abstract: "We first find that FNC-1's proposed evaluation metric favors the majority class, which can be easily classified, and thus overestimates the true discriminative power of the methods. Therefore, we propose a new F1-based metric yielding a changed system ranking."
- Section 4: "Instead, we propose the class-wise and the macro-averaged F1 scores (F1 m) as a new metric for this task that is not affected by the large size of the majority class."
- Section 4: "A classifier that always predicts DSC for the related documents even reaches FNC = .833, which is even higher than the top-ranked system."
- Section 4: "The raters reach an overall inter-annotator agreement of Fleiss' κ = .686 (...). However, when ignoring the UNR class, the inter-annotator agreement dramatically drops to κ = .218. This indicates that differentiating between the three related classes AGR, DSG, and DSC is difficult even for humans."
- Section 5.1: "If there is lexical overlap between the headline and the document, the models classify the instance as one of the related classes, even in cases in which the two are unrelated."
- Section 5.1: "the systems fail when semantic relations between words need to be taken into account, complex negation instances are encountered, or the understanding of propositional content in general is required."
- Shows: a text-to-text stance scheme (agree, disagree, discuss, unrelated) and the criticism of its metric. Humans agree poorly on the three related classes, which bounds how well a "reframed" or "contradicted" class could be labelled.
- Does not show: whether the article was derived from the headline's source, so it does not separate reuse from independent reporting.
