# A3-SR-21: Fernandez et al., Modelling and Detecting Decisions in Multi-party Dialogue (2008)

```json
{
  "source_identity": "Raquel Fernandez, Matthew Frampton, Patrick Ehlen, Matthew Purver, Stanley Peters, 'Modelling and Detecting Decisions in Multi-party Dialogue', Proceedings of the 9th SIGdial Workshop, pages 156-163; https://aclanthology.org/W08-0125.pdf",
  "author_or_issuing_body": "Raquel Fernandez, Matthew Frampton, Patrick Ehlen, Matthew Purver, Stanley Peters (Stanford University, CSLI)",
  "publisher": "Association for Computational Linguistics",
  "publication_date": "2008-06-01T00:00:00Z",
  "relevant_event_date": "2008-06-01",
  "source_family": "Primary for its decision dialogue act scheme. Secondary for Hsueh and Moore (A3-SR-19), which it summarizes. Same research group as A3-SR-20.",
  "precise_evidence_location": "Abstract; Section 2 Related Work; Section 3 Decision Dialogue Acts with Table 1",
  "method": "Annotation of AMI meetings with decision dialogue act classes; hierarchical classifier, F-score 58% for decision regions.",
  "limitations": "Only month and year are known; the date is set to 1 June 2008. The authors compare against their own reading of Hsueh and Moore; the F-score of 0.35 they cite was not matched to a table in A3-SR-19.",
  "provenance": "PDF downloaded with curl from the URL above on 2026-11-18 and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "we propose a structured approach that takes into account the different roles utterances play in the decision-making process. We show that this structured approach outperforms the accuracy achieved by existing decision detection systems based on flat annotations"
- Section 2: Hsueh and Moore "trained a Maximum Entropy classifier to recognize this single DA class" and "The F-score they achieved was 0.35, which gives a good indication of the difficulty of this task."
- Section 3: "These tags are however very general and do not capture the distinction between decisions and more general suggestions and commitments."
- Section 3: "Our scheme distinguishes among three main decision dialogue act (DDA) classes: issue (I), resolution (R), and agreement (A). Class R is further subdivided into resolution proposal (RP) and resolution restatement (RR)."
- Section 3: "A topic or issue that requires some sort of conclusion is initially raised. (b) One or more proposals are considered. And (c) once some sort of agreement is reached upon a particular resolution, a decision is adopted."
- Shows: the decision task restated from one flat class to issue, resolution, and agreement roles, with the flat approach named as the criticized step.
- Does not show: tracking of a decision across meetings or its later reversal.
