# A2-SR-08: Barrón-Cedeño et al., Overview of CheckThat! 2020

```json
{
  "source_identity": "Alberto Barrón-Cedeño, Tamer Elsayed, Preslav Nakov, Giovanni Da San Martino, Maram Hasanain, Reem Suwaileh, Fatima Haouari, Nikolay Babulkov, Bayan Hamdan, Alex Nikolov, Shaden Shaar, Zien Sheikh Ali, 'Overview of CheckThat! 2020: Automatic Identification and Verification of Claims in Social Media', CLEF 2020; arXiv:2007.07997",
  "author_or_issuing_body": "CheckThat! lab organisers (Università di Bologna, Qatar University, Qatar Computing Research Institute, Sofia University)",
  "publisher": "CLEF 2020 (Springer LNCS); preprint on arXiv",
  "publication_date": "2020-07-15T00:00:00Z",
  "relevant_event_date": "2020-09-22",
  "source_family": "Primary: the CLEF CheckThat! task-definition lineage, third edition. Follows A2-SR-04.",
  "precise_evidence_location": "Abstract; Section 1 Introduction (task list); Section 2 (evolution over three editions, Figure 2); Section 3.1 Arabic Task 1 annotation; Section 4.1 English Task 1 annotation questions Q1 to Q5",
  "method": "Shared-task overview with annotation guidelines for tweet datasets in Arabic and English.",
  "limitations": "relevant_event_date stands for the CLEF 2020 conference and is approximate. The 2021 overview (arXiv 2109.12987) was read in its 6-page form only; it keeps the auxiliary-question approach and adds three languages. Later editions (2022 to 2025) were not read.",
  "provenance": "PDF downloaded with curl on 2026-11-18 and extracted with pdftotext (poppler). Words split by a hyphen at a line break are rejoined in the quotes; no other change. Re-verify at https://arxiv.org/abs/2007.07997."
}
```

## Evidence

- Section 1: "Task 1 Check-worthiness estimation for tweets. Predict which tweet from a stream of tweets on a topic should be prioritized for fact-checking."
- Section 1: "Task 2 Verified claim retrieval: Given a check-worthy tweet, and a set of previously-checked claims, determine whether the claim in the tweet has been fact-checked already."
- Section 2: "In 2020, we unfolded the claim verification pipeline into four differentiated tasks. Regarding data, all tasks in 2020 turned to micro-blogging with focus on Twitter".
- Section 3.1 (Arabic): "Due to the subjective nature of check-worthiness, we chose to represent the check-worthiness criteria by several questions, to help annotators think about different aspects of check-worthiness."
- Section 4.1 (English): "Q1: Does the tweet contain a verifiable factual claim? This is an objective question." and "Q5: Do you think that a professional fact-checker should verify the claim in the tweet? This question asks for a subjective judgment."
- Section 4.1: "For the purpose of the task, we consider as worth fact-checking the tweets that received a positive answer both to Q1 and to Q5".
- Shows: the move from one fact-checker's selection to a split of check-worthiness into an objective verifiable-claim question and a subjective priority question, and the pipeline order detect, match, retrieve, verify. Does not show: whether the split raised annotator agreement; the passages read give no agreement figure for it.
