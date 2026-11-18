# A3-SR-19: Hsueh and Moore, What Decisions Have You Made (2007)

```json
{
  "source_identity": "Pei-Yun Hsueh, Johanna Moore, 'What Decisions Have You Made: Automatic Decision Detection in Conversational Speech', Proceedings of NAACL-HLT 2007; https://aclanthology.org/N07-1004.pdf",
  "author_or_issuing_body": "Pei-Yun Hsueh, Johanna Moore (University of Edinburgh, School of Informatics)",
  "publisher": "Association for Computational Linguistics",
  "publication_date": "2007-04-01T00:00:00Z",
  "relevant_event_date": "2007-04-01",
  "source_family": "Primary. Decision detection lineage on the AMI corpus (A3-SR-17); criticized by Fernandez et al. 2008 (A3-SR-21).",
  "precise_evidence_location": "Abstract; Section 4.1 Decision Annotation and 4.1.1 Decision-Making Dialogue Acts; Section 7 Discussion",
  "method": "MaxEnt classifiers on 50 AMI scenario meetings (about 37,400 dialogue acts), with decision labels derived from the AMI summary links.",
  "limitations": "The conference took place in April 2007; the date is set to 1 April 2007. Fernandez et al. cite a 'Hsueh and Moore (2007b)' with an F-score of 0.35, which may be this paper or a companion paper; this record did not settle which.",
  "provenance": "PDF downloaded with curl from the URL above on 2026-11-18 and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "We formulate the problem as classifying decision-making units at two levels of granularity: dialogue acts and topic segments."
- Section 4.1.1: "In fact, it is difficult to determine whether a dialogue act contains information relevant to any decision point without knowing what decisions have been made in the meeting."
- Section 4.1.1: "if a dialogue act is related to any sentence in the decision section, a "decision link" from the dialogue act to the decision sentence is added." and "We then label the dialogue acts that have one or more decision links as DM DAs."
- Section 4.1.1: "Overall, 554 out of 37,400 dialogue acts have been annotated as DM DAs, accounting for 1.4% of all dialogue acts in the data set"
- Section 7: "the two-phase decision annotation procedure (as described in Section 4.1) may have caused annotators to select dialogue acts that serve different functional roles in a decision-making process in the set of DM DAs."
- Shows: decisions defined as one flat class of dialogue acts, derived from summary links, with the authors naming the mixed roles inside that class as a problem.
- Does not show: what was decided. The label marks utterances, not the content of the decision.
