# A4-SR-13: Wright et al., Modeling Information Change in Science Communication with Semantically Matched Paraphrases

```json
{
  "source_identity": "Dustin Wright, Jiaxin Pei, David Jurgens, Isabelle Augenstein, 'Modeling Information Change in Science Communication with Semantically Matched Paraphrases', Proceedings of EMNLP 2022; https://aclanthology.org/2022.emnlp-main.117.pdf",
  "author_or_issuing_body": "Wright, Augenstein (University of Copenhagen); Pei, Jurgens (University of Michigan)",
  "publisher": "Association for Computational Linguistics (ACL Anthology)",
  "publication_date": "2022-12-01T00:00:00Z",
  "relevant_event_date": "2022-01-01",
  "source_family": "Primary for the SPICED dataset, the Information Matching Score, and its trend analysis. Secondary for the earlier exaggeration and certainty studies it cites (Sumner et al. 2014, A4-SR-14; Pei and Jurgens 2021; Wright and Augenstein 2021).",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 2 Related Work; Section 3 SPICED, annotation and Information Matching Score; Section 6 trend analysis; Limitations section",
  "method": "Pairs 6,000 scientific findings from papers with sentences from news and tweets. Crowd annotators rate each pair on a five-point Information Matching Score. Models trained on the data are applied to unlabelled news and tweets.",
  "limitations": "Month-only date; set to 1 December 2022 (EMNLP 2022 month). relevant_event_date is approximate. Four scientific fields, Twitter only for social media, and only tweets linked to a paper through Altmetric. The score measures sameness of information, not the direction of change.",
  "provenance": "PDF downloaded with curl on 2026-11-18 from the ACL Anthology and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "we present the SCIENTIFIC PARAPHRASE AND INFORMATION CHANGE DATASET (SPICED), the first paraphrase dataset of scientific findings annotated for degree of information change. SPICED contains 6,000 scientific finding pairs extracted from news stories, social media discussions, and full texts of original papers."
- Section 1: "Though efforts exist to track and flag when popular media misrepresent science, the sheer volume of new studies, reporting, and online engagement make purely manual efforts both intractable and unattractive."
- Section 1: "However, these studies skip over the key first step needed to compare scientific texts for information change: automatically identi[fying]" paired findings. The quote breaks at a footnote in the extracted text; the word after "identi" is not checked.
- Section 3: "The information in the findings is...” (1): Completely different (2): Mostly different (3): Somewhat similar (4): Mostly the same, or (5): Completely the same."
- Section 3: "annotators were instructed to mark how similar the information in the findings was, as opposed to how similar the sentences are."
- Table 1 caption: "These examples demonstrate that simple similarity scores may not reflect whether the two sentences are covering the same scientific finding."
- Section 1: "media tend to exaggerate findings in the limitations sections of papers; (2) press releases and SciTech tend to have less informational change than general news outlets".
- Shows: a method for the "altered" class at the level of meaning: a graded score of information change between a source finding and its downstream versions. It records the criticism that earlier exaggeration and certainty studies need paired findings that were matched by hand.
- Does not show: the direction of the change (stronger or weaker claim), a frame label, or whether the downstream text used the paper directly.
