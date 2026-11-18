# A2-SR-07: Shaar et al., That is a Known Lie: Detecting Previously Fact-Checked Claims

```json
{
  "source_identity": "Shaden Shaar, Nikolay Babulkov, Giovanni Da San Martino, Preslav Nakov, 'That is a Known Lie: Detecting Previously Fact-Checked Claims', ACL 2020; arXiv:2005.06058",
  "author_or_issuing_body": "Shaden Shaar, Giovanni Da San Martino, Preslav Nakov (Qatar Computing Research Institute); Nikolay Babulkov (Sofia University)",
  "publisher": "Association for Computational Linguistics; preprint on arXiv",
  "publication_date": "2020-05-12T00:00:00Z",
  "relevant_event_date": "2020-07-05",
  "source_family": "Primary: the claim-retrieval lineage of the CheckThat! organisers. Criticised by A2-SR-10. Its task is run as CheckThat! 2020 Task 2 (A2-SR-08).",
  "precise_evidence_location": "Abstract; Section 1 Introduction (Figure 1 pipeline); Section 2 Related work (Fact Check Explorer, ClaimReview); Section 3 Task definition",
  "method": "Formulates the task, builds datasets from PolitiFact and Snopes, and runs learning-to-rank experiments.",
  "limitations": "relevant_event_date stands for the ACL 2020 conference and is approximate. The datasets cover English and mainly US politics.",
  "provenance": "PDF downloaded with curl on 2026-11-18 and extracted with pdftotext (poppler). Words split by a hyphen at a line break are rejoined in the quotes; no other change. Re-verify at https://arxiv.org/abs/2005.06058."
}
```

## Evidence

- Abstract: "it is important to try to save this effort and to avoid wasting time on claims that have already been fact-checked. Interestingly, despite the importance of the task, it has been largely ignored by the research community so far."
- Section 3: "We define the task as follows: Given a check-worthy input claim and a set of verified claims, rank those verified claims, so that the claims that can help verify the input claim, or a sub-claim in it, are ranked above any claim that is not helpful to verify the input claim."
- Section 1: "It has been argued that checking against a database of previously fact-checked claims should be an integral step of an end-to-end automated fact-checking pipeline (Hassan et al., 2017)."
- Section 2: Google Fact Check Explorer searches "a number of fact-checking websites (those that use ClaimReview from schema.org)" (footnote marker removed) but "the tool cannot handle a complex claim, as it runs Google search, which is not optimized for semantic matching of long claims."
- Shows: the first formal task definition for matching a claim against already fact-checked claims, and its link to ClaimReview data. Does not show: performance outside English or outside US politics.
