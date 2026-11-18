# A3-SR-16: Kummerfeld et al., A Large-Scale Corpus for Conversation Disentanglement (2019)

```json
{
  "source_identity": "Jonathan K. Kummerfeld et al., 'A Large-Scale Corpus for Conversation Disentanglement', Proceedings of ACL 2019, pages 3846-3856; https://aclanthology.org/P19-1374.pdf",
  "author_or_issuing_body": "Kummerfeld, Gouravajhala, Peper, Athreya (University of Michigan); Gunasekara, Ganhotra, Patel, Polymenakos (IBM Research AI); Lasecki (University of Michigan)",
  "publisher": "Association for Computational Linguistics",
  "publication_date": "2019-07-28T00:00:00Z",
  "relevant_event_date": "2019-07-28",
  "source_family": "Primary for its corpus, task definition, and evaluation of Lowe et al. Secondary for Lowe et al. 2015 and 2017 and for Shen et al. 2006, which were not read.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 2 Task Definition; Section 3 Related Work; Table 2 (inter-annotator agreement)",
  "method": "77,563 IRC messages from the #Ubuntu channel, annotated with reply-to links, with adjudication of disagreements; evaluation of a heuristic disentanglement used to build a widely used dialogue corpus.",
  "limitations": "publication_date is the first day of the conference as printed (28 July 2019). The data come from one technical support channel. The 80% error figure applies to the Lowe et al. heuristic corpus, which this record did not check directly.",
  "provenance": "PDF downloaded with curl from the URL above on 2026-11-18 and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "We created a new dataset of 77,563 messages manually annotated with reply-structure graphs that both disentangle conversations and define internal conversation structure."
- Abstract: "finding that 80% of conversations in a widely used dialogue corpus are either missing messages or contain extra messages."
- Section 1: "Even when structure is provided it often has limited depth, such as threads in Slack, which provide one layer of branching."
- Section 1: research uses "datasets that are either small (2,500 messages, Elsner and Charniak, 2008) or not released (Adams and Martell, 2008)."
- Section 2: "We label this data with a graph in which messages are nodes and edges indicate that one message is a response to another. Each connected component is a conversation."
- Section 3: removing platform-provided structure to create test data "risks introducing a bias, as people write differently when explicit structure is defined"
- Shows: the task restated as reply-graph prediction, with conversations derived as connected components, and a documented criticism of small and heuristic datasets.
- Does not show: results outside IRC. The corpus is one channel and one language.
