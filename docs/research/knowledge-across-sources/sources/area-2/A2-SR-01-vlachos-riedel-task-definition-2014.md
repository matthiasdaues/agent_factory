# A2-SR-01: Vlachos and Riedel, Fact Checking: Task Definition and Dataset Construction

```json
{
  "source_identity": "Andreas Vlachos, Sebastian Riedel, 'Fact Checking: Task definition and dataset construction', Proceedings of the ACL 2014 Workshop on Language Technologies and Computational Social Science, pages 18-22; https://aclanthology.org/W14-2508.pdf",
  "author_or_issuing_body": "Andreas Vlachos, Sebastian Riedel (University College London)",
  "publisher": "Association for Computational Linguistics (ACL Anthology)",
  "publication_date": "2014-06-26T00:00:00Z",
  "relevant_event_date": "2014-06-26",
  "source_family": "Primary: the first task definition of fact-checking in natural language processing in this area. Later work cites it as the origin (A2-SR-11, A2-SR-12).",
  "precise_evidence_location": "Section 2 Task definition; Section 3 Dataset construction",
  "method": "Position paper. Defines the task and builds a small dataset from fact-checks published by PolitiFact and Channel 4 FactCheck.",
  "limitations": "Short workshop paper. The dataset holds a few hundred statements. The paper defines the task; it does not test a system. It covers verification only, not claim detection.",
  "provenance": "PDF downloaded with curl on 2026-11-18 and extracted with pdftotext (poppler). Words split by a hyphen at a line break are rejoined in the quotes; no other change. Re-verify at the URL above."
}
```

## Evidence

- Section 2: "We define fact-checking to be the assignment of a truth value to a claim made in a particular context."
- Section 2: "it is often the case that the statements are not completely true or false." The authors therefore treat the task as ordinal classification, not binary classification.
- Section 2: "we restrict the task to be a prediction problem so that we can evaluate performance automatically." The analysis behind a verdict is left out of the task.
- Section 2: "We consider all of the aspects mentioned (time, speaker, multiple sources and interpretations) as part of the task of fact checking. However, we want to restrict the task to statements that can be fact-checked objectively, which is not always true for the statements assessed by journalists."
- Shows: the first formulation of fact-checking as a prediction task over claims in context. Does not show: any evidence annotation or system result.
