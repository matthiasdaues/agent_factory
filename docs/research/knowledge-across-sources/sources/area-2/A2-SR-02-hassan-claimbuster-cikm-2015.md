# A2-SR-02: Hassan et al., Detecting Check-worthy Factual Claims in Presidential Debates (ClaimBuster)

```json
{
  "source_identity": "Naeemul Hassan, Chengkai Li, Mark Tremayne, 'Detecting Check-worthy Factual Claims in Presidential Debates', CIKM 2015; https://ranger.uta.edu/~cli/pubs/2015/claimbuster-cikm15-hassan.pdf",
  "author_or_issuing_body": "Naeemul Hassan, Chengkai Li, Mark Tremayne (University of Texas at Arlington)",
  "publisher": "ACM (CIKM 2015 proceedings); PDF hosted on the author's university page",
  "publication_date": "2015-10-19T00:00:00Z",
  "relevant_event_date": "2015-10-19",
  "source_family": "Primary: the ClaimBuster lineage. Cited as the first check-worthiness work by A2-SR-04, A2-SR-05 and A2-SR-11.",
  "precise_evidence_location": "Abstract; Section 1 Introduction (class definitions NFS, UFS, CFS); Section 2 Related work",
  "method": "Builds a labelled set of sentences from US presidential debates of 2004, 2008 and 2012 and trains supervised classifiers over three classes.",
  "limitations": "Short paper. The definitions rest on a judgement of public interest, which the paper does not operationalise beyond annotator instructions. Annotator agreement is not reported in the passages read. The later full ClaimBuster dataset (Arslan et al., 2020, arXiv 2004.14425) was read only for its definitions, which are unchanged.",
  "provenance": "PDF downloaded with curl on 2026-11-18 and extracted with pdftotext (poppler). Words split by a hyphen at a line break are rejoined in the quotes; no other change. Re-verify at the URL above."
}
```

## Evidence

- Section 1, class Non-Factual Sentence: "Subjective sentences (opinions, beliefs, declarations) and many questions fall under this category. These sentences do not contain any factual claim."
- Section 1, class Unimportant Factual Sentence: "These are factual claims but not check-worthy. In other words, the general public will not be interested in knowing whether these sentences are true or false."
- Section 1, class Check-worthy Factual Sentence: "These sentences contain factual claims and the general public will be interested in knowing whether the claims are true or false. Journalists look for these type of claims for fact checking."
- Section 2: "not all objective sentences are check-worthy important factual claims." The authors separate check-worthiness from subjectivity analysis.
- Note: Arslan et al. 2020 (the ClaimBuster benchmark dataset, arXiv 2004.14425, Section 3) keeps the same three classes, in the words "Check-worthy Factual Sentence (CFS): These sentences contain factual claims that the general public will be interested in learning about their veracity."
- Shows: the first formulation of a check-worthy claim, tied to public interest. Does not show: how stable annotators are on the public-interest judgement.
