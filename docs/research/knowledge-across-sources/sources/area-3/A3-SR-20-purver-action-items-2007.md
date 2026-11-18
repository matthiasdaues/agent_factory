# A3-SR-20: Purver et al., Detecting and Summarizing Action Items in Multi-Party Dialogue (2007)

```json
{
  "source_identity": "Matthew Purver, John Dowding, John Niekrasz, Patrick Ehlen, Sharareh Noorbaloochi, Stanley Peters, 'Detecting and Summarizing Action Items in Multi-Party Dialogue', Proceedings of the 8th SIGdial Workshop, pages 18-25, doi:10.18653/v1/2007.sigdial-1.4; https://aclanthology.org/2007.sigdial-1.4.pdf",
  "author_or_issuing_body": "Purver, Niekrasz, Ehlen, Noorbaloochi, Peters (Stanford University, CSLI); Dowding (University of California at Santa Cruz)",
  "publisher": "Association for Computational Linguistics",
  "publication_date": "2007-09-01T00:00:00Z",
  "relevant_event_date": "2005-01-01",
  "source_family": "Primary for its own annotation scheme and results. Secondary for Gruenstein et al. 2005 and Morgan et al. 2006, which it summarizes and which were not read.",
  "precise_evidence_location": "Abstract; Section 2 Background, 'Subdialogue Detection'; Section 3 data and annotation (inter-annotator agreement paragraph)",
  "method": "18 ICSI meetings annotated with four action-item dialogue act classes; hierarchical classifiers detect the classes and then the subdialogues.",
  "limitations": "The workshop took place in September 2007; the date is set to 1 September 2007. relevant_event_date stands for the 2005 flat annotation it criticizes and is year-only. The kappa of the 2005 work comes through this paper only.",
  "provenance": "PDF downloaded with curl from the URL above on 2026-11-18 and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "This paper addresses the problem of identifying action items discussed in open-domain conversational speech, and does so in two stages: firstly, detecting the subdialogues in which action items are proposed, discussed and committed to; and secondly, extracting the phrases that accurately capture or summarize the tasks they involve."
- Section 2: Morgan et al. on ICSI data found "performance was poor, with f-scores limited to approximately 0.3, even given manual transcripts and dialogue act tags."
- Section 2: "One major reason for this is the fragmented nature of conversational decision-making: in contrast to email text, the descriptions of tasks and their properties tend not to come in single sentences, but may be distributed over many utterances."
- Section 2: "human annotators also have trouble deciding which utterances are relevant: Gruenstein et al. (2005)’s inter-annotator agreement was as low as κ = 0.36."
- Section 2: the authors' classes are "task description, timeframe, ownership and agreement."
- Section 3: "Inter-annotator agreement improved significantly on (Gruenstein et al., 2005), with pairwise κ values for each individual AIDA class from 0.64 to 0.78."
- Section 2: "our job is to identify public commitments to tasks, rather than general decisions about strategy"
- Shows: the action-item task moved from one flat utterance label to four role classes, and the stated reason is low agreement and poor results with the flat label.
- Does not show: a check of the extracted summaries against what was done after the meeting.
