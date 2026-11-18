# A2-SR-11: Guo, Schlichtkrull and Vlachos, A Survey on Automated Fact-Checking

```json
{
  "source_identity": "Zhijiang Guo, Michael Schlichtkrull, Andreas Vlachos, 'A Survey on Automated Fact-Checking', Transactions of the Association for Computational Linguistics 10 (2022); arXiv:2108.11896 v3",
  "author_or_issuing_body": "Zhijiang Guo, Michael Schlichtkrull, Andreas Vlachos (University of Cambridge)",
  "publisher": "MIT Press (TACL); preprint on arXiv",
  "publication_date": "2022-06-06T00:00:00Z",
  "relevant_event_date": "2021-08-26",
  "source_family": "Secondary for the works it surveys, such as A2-SR-02, A2-SR-04 and A2-SR-08; primary for its own three-stage framework.",
  "precise_evidence_location": "Section 1 Introduction (Figure 2 framework); Section 2 Task definition; Section 2.1 Claim detection",
  "method": "Literature survey that sorts datasets and methods into one framework.",
  "limitations": "publication_date is the arXiv v3 date that was read; relevant_event_date is the first arXiv posting (month known, day approximate). A survey reports what others found; claims about individual works are second-hand.",
  "provenance": "PDF downloaded with curl on 2026-11-18 and extracted with pdftotext (poppler). Words split by a hyphen at a line break are rejoined in the quotes; no other change. Re-verify at https://arxiv.org/abs/2108.11896."
}
```

## Evidence

- Section 2: "Figure 2 shows a NLP framework for automated fact-checking consisting of three stages: (i) claim detection to identify claims that require verification; (ii) evidence retrieval to find sources supporting or refuting the claim; (iii) claim verification to assess the veracity of the claim based on the retrieved evidence."
- Section 2: claim verification "can be decomposed into two parts that can be tackled separately or jointly: verdict prediction, where claims are assigned truthfulness labels, and justification production, where explanations for verdicts must be produced."
- Section 1, on the earlier survey by Thorne and Vlachos (2018): "However, their proposed framework does not include work on determining which claims to verify (i.e. claim detection), nor does their survey include the recent work on producing explainable, convincing verdicts (i.e. justification production)." Thorne and Vlachos (2018) was not read.
- Section 2.1: "Commonly, detection relies on the concept of check-worthiness. Hassan et al. (2015) defined check-worthy claims as those for which the general public would be interested in knowing the truth."
- Section 2.1: "Check-worthiness and rumourousness can be subjective." and "The check-worthiness of each claim also varies over time".
- Shows: the consolidated pipeline formulation and the criticism of check-worthiness as subjective and time-bound. Does not show: a resolved definition; the survey lists the problem.
