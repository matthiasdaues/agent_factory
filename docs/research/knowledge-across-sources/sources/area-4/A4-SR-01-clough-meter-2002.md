# A4-SR-01: Clough et al., METER: MEasuring TExt Reuse

```json
{
  "source_identity": "Paul Clough, Robert Gaizauskas, Scott S.L. Piao, Yorick Wilks, 'METER: MEasuring TExt Reuse', Proceedings of the 40th Annual Meeting of the ACL, Philadelphia, July 2002, pp. 152-159; https://aclanthology.org/P02-1020.pdf",
  "author_or_issuing_body": "Clough, Gaizauskas, Piao, Wilks (Department of Computer Science, University of Sheffield)",
  "publisher": "Association for Computational Linguistics (ACL Anthology)",
  "publication_date": "2002-07-01T00:00:00Z",
  "relevant_event_date": "1999-07-01",
  "source_family": "Primary for the METER classification scheme and its classifier results. Secondary for the METER corpus paper (Gaizauskas et al., 2001), which it summarises and cites.",
  "precise_evidence_location": "Abstract; Section 2 Journalistic reuse of a newswire; Section 3 A conceptual framework; Section 3.1 The METER corpus; Section 5, Table 3 confusion matrix; Section 7 Future work",
  "method": "Builds a corpus of UK Press Association copy and nine British newspapers, July 1999 to June 2000. Trained journalists label each newspaper story at document level and a subset at word-sequence level. Compares n-gram overlap, Greedy String Tiling, and sentence alignment as classifiers against the labels.",
  "limitations": "Month-only date; set to 1 July 2002 (conference month). relevant_event_date is the start of the corpus period. Two domains only (court reporting and show business) and one agency. The labels rest on journalists' judgement, not on an explicit lexical definition. The best ternary F1 is 0.664, and the partially-derived class is hard to separate. The 2001 corpus paper was not read.",
  "provenance": "PDF downloaded with curl on 2026-11-18 from the ACL Anthology and extracted with pdftotext. Ligatures lost in extraction were restored in the quotes. Re-verify at the URL above."
}
```

## Evidence

- Section 3, document level: "1) wholly-derived (WD): all text in the newspaper article is rewritten only from news agency copy; 2) partially-derived (PD): some text is derived from the news agency, but other sources have also been used; and 3) non-derived (ND): news agency has not been used as the source of the article; although words may still co-occur between the newspaper article and news agency copy on the same topic, the journalist is confident the news agency has not been used."
- Section 3, lexical level: "1) verbatim: text appearing word-for-word to express the same information; 2) rewrite: text paraphrased to create a different surface appearance, but express the same information and 3) new: text used to express information not appearing in agency copy (can include verbatim/rewritten text, but being used in a different context)."
- Section 3: "This framework rests upon the intuitions of trained journalists to judge text reuse, and not on an explicit lexical/syntactic definition of reuse (which would presuppose what we are setting out to discover)."
- Section 2, example of a rewrite: "The rewrite makes use of slang and exaggeration to capture its readers' attention (e.g. DRUNK, limo, ploughed)."
- Section 3.1: "They include 300 wholly-derived, 438 partially-derived and 206 non-derived (i.e. 77% are thought to have used PA in some way)."
- Section 5: "Note the high misclassification of PD as both WD and ND, reflecting the difficulty of separating this class."
- Shows: a three-class document scheme and a three-class lexical scheme for agency reuse, with automatic detection by string overlap. The ND class is the closest match to "independently reported".
- Does not show: any class for a change of frame or stance. The scheme records whether words come from the agency, not whether their meaning or emphasis changed.
