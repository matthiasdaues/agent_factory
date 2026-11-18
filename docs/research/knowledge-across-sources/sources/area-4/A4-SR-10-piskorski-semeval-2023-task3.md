# A4-SR-10: Piskorski et al., SemEval-2023 Task 3

```json
{
  "source_identity": "Jakub Piskorski, Nicolas Stefanovitch, Giovanni Da San Martino, Preslav Nakov, 'SemEval-2023 Task 3: Detecting the Category, the Framing, and the Persuasion Techniques in Online News in a Multi-lingual Setup', Proceedings of SemEval-2023; https://aclanthology.org/2023.semeval-1.317.pdf",
  "author_or_issuing_body": "Piskorski (Polish Academy of Sciences), Stefanovitch (European Commission Joint Research Centre), Da San Martino (University of Padova), Nakov (MBZUAI)",
  "publisher": "Association for Computational Linguistics (ACL Anthology)",
  "publication_date": "2023-07-01T00:00:00Z",
  "relevant_event_date": "2023-01-01",
  "source_family": "Primary for the SemEval-2023 Task 3 framing subtask. Secondary for the Media Frames Corpus dimensions (A4-SR-09), which it reuses.",
  "precise_evidence_location": "Abstract; Section 2 task definition, Subtask 2; Related work, Framing Detection; Section on annotation quality (Krippendorff's alpha); Section 5.1 evaluation measures",
  "method": "Shared task on news articles in nine languages. Subtask 2 asks systems to assign one or more of 14 generic frames to each article. Annotations were made in INCEpTION and consolidated by curators.",
  "limitations": "Month-only date; set to 1 July 2023 (SemEval workshop month). relevant_event_date is the year the task ran and is approximate. The reported Krippendorff's alpha of 0.342 is given for the annotation as a whole before consolidation; the text does not separate it by subtask. Frames are labelled per article only.",
  "provenance": "PDF downloaded with curl on 2026-11-18 from the ACL Anthology and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Section 2: "Subtask 2 (ST2): Framing Detection. Given a news article, identify one or more frames used in the article from a pool of 14 generic framing dimensions (introduced in Card et al. (2015))".
- Section 2: "This is a multi-class multi-label classification task at the article level."
- Related work: "Framing is a strategic device and a central concept in political communication for representing different salient aspects and perspectives for the purpose of conveying the latent meaning about an issue (Entman, 1993)."
- Annotation quality: "we computed the Inter-Annotator Agreement (IAA) using Krippendorf's α: the value was 0.342, which is lower than the recommended threshold of 0.667, but we should note that this value represents the agreement before the consolidation".
- Abstract: "a total of 181 teams registered to participate, and 41 eventually made an official submission on the test set."
- Shows: the multilingual, multi-label successor of the Media Frames Corpus scheme, and low raw agreement on the annotation.
- Does not show: a pairwise frame-change task between a source and its downstream versions.
