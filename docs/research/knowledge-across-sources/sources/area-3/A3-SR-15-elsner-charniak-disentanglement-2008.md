# A3-SR-15: Elsner and Charniak, You talking to me? Conversation disentanglement (2008)

```json
{
  "source_identity": "Micha Elsner, Eugene Charniak, 'You talking to me? A Corpus and Algorithm for Conversation Disentanglement', Proceedings of ACL-08: HLT, pages 834-842; https://aclanthology.org/P08-1095.pdf",
  "author_or_issuing_body": "Micha Elsner, Eugene Charniak (Brown University, BLLIP)",
  "publisher": "Association for Computational Linguistics",
  "publication_date": "2008-06-01T00:00:00Z",
  "relevant_event_date": "2008-06-01",
  "source_family": "Primary for its own corpus and task definition. Secondary for Aoki et al. 2003 and 2006, Camtepe et al. 2005, and Acar et al. 2005, which it criticizes but which were not read. Extended by Elsner and Charniak 2010 (Computational Linguistics 36(3)), which was read but not recorded because its task definition is the same.",
  "precise_evidence_location": "Abstract; Section 1 Motivation; Section 2 Related Work; Section 3.3 Discussion with Table 1 (annotator agreement)",
  "method": "Six annotators disentangled 800 lines of IRC chat; the paper defines one-to-one and local agreement metrics and a graph-based clustering model.",
  "limitations": "Only month and year are known; the date is set to 1 June 2008. The corpus is small and from one channel. The earlier systems it criticizes were not read, so the criticism is recorded as the authors' account.",
  "provenance": "PDF downloaded with curl from the URL above on 2026-11-18 and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "When multiple conversations occur simultaneously, a listener must decide which conversation each utterance is part of in order to interpret and respond to it appropriately. We refer to this task as disentanglement."
- Section 1: "Disentanglement is the clustering task of dividing a transcript into a set of distinct conversations."
- Section 1: "Previous attempts to solve the problem (Aoki et al., 2006; Aoki et al., 2003; Camtepe et al., 2005; Acar et al., 2005) have several flaws. They cluster speakers, not utterances, and so fail when speakers move from one conversation to another."
- Section 1: "there are no reliable annotation schemes, no standard corpora, and no agreed-upon metrics."
- Section 3.3: "Our annotators have high agreement on the local metric (average of 81.1%). On the 1-to-1 metric, they disagree more, with a mean overlap of 53.0% and a maximum of only 63.5%."
- Shows: the task defined as clustering utterances, not speakers, with the first public annotated chat corpus and two agreement metrics.
- Does not show: reply links between messages. The annotation assigns each line to a conversation and records no internal structure.
