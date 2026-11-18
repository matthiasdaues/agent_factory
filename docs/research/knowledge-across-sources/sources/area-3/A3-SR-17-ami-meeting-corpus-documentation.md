# A3-SR-17: AMI Meeting Corpus, overview and annotation documentation

```json
{
  "source_identity": "AMI Corpus web documentation: 'AMI Corpus Overview' (web version of J. Carletta, 'Announcing the AMI Meeting Corpus', ELRA Newsletter 11(1), 2006, pages 3-5) and 'Annotation'; https://groups.inf.ed.ac.uk/ami/corpus/overview.shtml, https://groups.inf.ed.ac.uk/ami/corpus/annotation.shtml",
  "author_or_issuing_body": "Jean Carletta and the AMI project consortium (FP6-506811)",
  "publisher": "University of Edinburgh, School of Informatics (corpus site)",
  "publication_date": "2006-01-01T00:00:00Z",
  "relevant_event_date": "2006-01-01",
  "source_family": "Primary for the corpus contents and annotation schemes as the corpus maintainers describe them. The peer-reviewed corpus paper (Carletta et al. 2005, MLMI) was not read.",
  "precise_evidence_location": "Overview page, paragraphs on corpus size and annotations; Annotation page, sections 'Dialogue Acts', 'Topic Segmentation', 'Abstractive and Extractive Summaries'",
  "method": "Corpus documentation by the team that recorded and annotated the meetings.",
  "limitations": "The overview reproduces a January to March 2006 newsletter; the date is set to 1 January 2006. The annotation page has no date and may have been edited since. Several sections state that reliability results are not available. Carletta et al. 2005 was not read.",
  "provenance": "HTML downloaded with curl on 2026-11-18 and tags stripped locally. Re-verify at the URLs above."
}
```

## Evidence

- Overview: "One AMI focus is on developing meeting browsers that improve work group effectiveness by giving better access to the group's history."
- Overview: "This might mean, for instance, spotting topic boundaries, decisions, intense discussions, or places where a specific person or subject was mentioned."
- Overview: "The AMI Meeting Corpus consists of 100 hours of meeting recordings." and the meetings "include mostly non-native speakers."
- Overview: the corpus has "manually produced orthographic transcription for each individual speaker, including word-level timings that have derived by using a speech recognizer in forced alignment mode."
- Annotation, summaries: "Abstractive summaries consist of around 200 words; do not include abbreviations; feature the organizational headings ABSTRACT, DECISIONS, PROBLEMS/ISSUES, and 'ACTIONS'"
- Annotation, summaries: extractive summaries "identify a set of dialogue acts that jointly convey specific information from the abstractive summary, thereby functioning as indices into the meeting's video and audio streams."
- Annotation, dialogue acts: "Reliability test results are not currently available for this scheme."
- Shows: speaker attribution in AMI comes from one close-talking channel per speaker, and decisions and actions are recorded as headings of a human summary linked to dialogue acts.
- Does not show: a decision or action-item annotation of its own. Decisions enter through the summary links that A3-SR-20 builds on.
