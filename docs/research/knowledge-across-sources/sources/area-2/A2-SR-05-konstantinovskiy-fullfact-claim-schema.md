# A2-SR-05: Konstantinovskiy et al., Towards Automated Factchecking: An Annotation Schema for Claim Detection (Full Fact)

```json
{
  "source_identity": "Lev Konstantinovskiy, Oliver Price, Mevan Babakar, Arkaitz Zubiaga, 'Towards Automated Factchecking: Developing an Annotation Schema and Benchmark for Consistent Automated Claim Detection', ACM Digital Threats: Research and Practice (2021); arXiv:1809.08193 v2",
  "author_or_issuing_body": "Lev Konstantinovskiy, Mevan Babakar (Full Fact); Oliver Price (University of Warwick); Arkaitz Zubiaga (Queen Mary University of London)",
  "publisher": "ACM (Digital Threats: Research and Practice); preprint on arXiv",
  "publication_date": "2020-08-17T00:00:00Z",
  "relevant_event_date": "2018-09-01",
  "source_family": "Primary: the Full Fact claim-detection lineage, written by a fact-checking charity with academic partners. Criticises A2-SR-02. Its definition is reused by A2-SR-10.",
  "precise_evidence_location": "Section 1 Introduction; Section 2 Related work (Previous attempts at defining claims); Section 3.1 Our claim definition and process; Section 3.4 Agreement",
  "method": "Iterative design of an annotation schema with professional fact-checkers, crowd annotation of 5,571 sentences from UK political TV shows, and a classifier on sentence embeddings.",
  "limitations": "publication_date is the arXiv v2 date that was read. The paper was first posted in September 2018 (relevant_event_date, month only) and accepted in ACM DTRAP; the journal version was not read. Agreement on the seven categories is moderate.",
  "provenance": "PDF downloaded with curl on 2026-11-18 and extracted with pdftotext (poppler). Words split by a hyphen at a line break are rejoined in the quotes; no other change. Re-verify at https://arxiv.org/abs/1809.08193."
}
```

## Evidence

- Section 1: "Previous works on claim detection [12, 18] rely on definitions of claims that incorporate the concept of check-worthiness and/or importance. Our objective is instead to avoid these subjective concepts to come up with an objective way of determining what constitutes a claim that is checkable; rather than being important or worthy of checking which is bound to subjective interpretation."
- Section 2: ClaimBuster "produces a score of how important a claim is to factcheck. This has the caveat of then having to choose a cut-off score to determine the claims that will be considered worthy or important enough for factchecking."
- Section 2: "This definition of a claim includes the judgement of ‘importance’ which we avoid in our work. We believe it is an editorial judgement best left to factcheckers."
- Section 3.1: "Full Fact’s formal definition of a claim during the 2015 UK election, was “an assertion about the world that can be checked”." and "as we captured more and more claims, this definition proved insufficient."
- Section 3.1: "We chose to decouple the importance of the claim from the claim itself. We felt that importance was heavily subjective, reliant on context and best left to factcheckers."
- Section 3.4: "At the level of all the 7 granular categories the inter-annotator agreement is moderate, with a Krippendorff’s alpha [23] of 0.46."
- Shows: the criticism that check-worthiness mixes a checkable claim with an editorial judgement, and a replacement definition of a checkable claim. Does not show: that the binary checkable label is more useful to fact-checkers than a ranking; the paper reports user feedback only in general words.
