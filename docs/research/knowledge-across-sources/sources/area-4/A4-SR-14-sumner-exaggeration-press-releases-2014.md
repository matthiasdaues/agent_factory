# A4-SR-14: Sumner et al., The Association Between Exaggeration in Health Related Science News and Academic Press Releases

```json
{
  "source_identity": "Petroc Sumner et al., 'The association between exaggeration in health related science news and academic press releases: retrospective observational study', BMJ 2014;349:g7015, doi:10.1136/bmj.g7015; full text PMC4262123 via https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4262123/fullTextXML",
  "author_or_issuing_body": "Petroc Sumner and colleagues (Cardiff University and others)",
  "publisher": "BMJ Publishing Group; full text mirrored by Europe PMC",
  "publication_date": "2014-12-01T00:00:00Z",
  "relevant_event_date": "2011-01-01",
  "source_family": "Primary for its content analysis of press releases, papers, and news, and for its seven-point scale of causal claim strength.",
  "precise_evidence_location": "Abstract (Objective, Sample, Results, Conclusions); Methods, coding of causal statements; Discussion, 'Caveats for our observational approach'",
  "method": "Retrospective content analysis of 462 press releases from 20 UK universities in 2011, their peer-reviewed papers, and 668 news stories. Coders compare advice, causal claims, and inference from animal to human between the three versions.",
  "limitations": "Month-only date; set to 1 December 2014 (issue month of BMJ volume 349). relevant_event_date stands for the 2011 press releases. The full author list was not copied. The bmj.com page was blocked by a bot check, so the Europe PMC XML was read instead. Manual coding; correlational design; health science only.",
  "provenance": "Full-text XML downloaded with curl on 2026-11-18 from the Europe PMC REST API and stripped of tags with a Python script. Re-verify through the DOI above."
}
```

## Evidence

- Objective: "To identify the source (press releases or news) of distortions, exaggerations, or changes to the main conclusions drawn from research that could potentially influence a reader's health related behaviour."
- Methods: "We used a seven point scale to rate increasing levels of determinism, where the presence of stronger statements trumped weaker ones: no statement (...), explicit statement of no relation, correlational (for example, “drinking wine is associated with increased cancer rates”), ambiguous (for example, “drinking wine linked to cancer risk”), conditional causal (for example, “drinking wine might increase cancer risk”), can cause (for example, “drinking wine can increase cancer risk”), and unconditionally causal (for example, “drinking wine increases cancer risk”)."
- Results: "33% (26% to 40%) contained exaggerated causal claims".
- Conclusions: "Exaggeration in news is strongly associated with exaggeration in press releases."
- Discussion: "Our study was correlational, so does not demonstrate a causal relation between inflated statements in press releases and inflated news. For example, if journalists did not read the press releases, associated exaggeration could nevertheless emerge between the press release and news because of features in the journal articles that might naturally lead to such exaggerations."
- Shows: a manual method for the "altered" class that records the direction of change: a claim gets stronger along an ordered scale between paper, press release, and news.
- Does not show: an automatic method, or proof that a news story copied the press release rather than reporting from the paper on its own.
