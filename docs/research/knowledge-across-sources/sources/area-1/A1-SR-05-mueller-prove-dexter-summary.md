# A1-SR-05: Müller-Prove, summary of the Dexter model in Vision and Reality of Hypertext and GUIs

```json
{
  "source_identity": "Matthias Müller-Prove, 'Vision and Reality of Hypertext and Graphical User Interfaces', section 2.2.2 'The Dexter Hypertext Reference Model'; https://mprove.de/visionreality/text/2.2.2_dexter.html",
  "author_or_issuing_body": "Matthias Müller-Prove",
  "publisher": "Department of Informatics, University of Hamburg, report FBI-HH-B-237/02 (master thesis); web edition on mprove.de",
  "publication_date": "2002-02-01T00:00:00Z",
  "relevant_event_date": "1994-01-01",
  "source_family": "Secondary. Summary of Halasz and Schwartz, CACM 1994; same family as A1-SR-04.",
  "precise_evidence_location": "Section 2.2.2, numbered definitions (4) specifier and (5) link, and the closing paragraph",
  "method": "Thesis chapter that paraphrases and summarises the Dexter definitions from the 1994 CACM paper.",
  "limitations": "Secondary summary; the wording is the author's, not Halasz and Schwartz's. publication_date is February 2002, month only, as the thesis index page states; set to 1 February 2002. The section page footer says 'Modified: 9/6/16'. relevant_event_date is the 1994 CACM publication, year only.",
  "provenance": "HTML page downloaded with curl on 2026-11-18; tags stripped with a local script; quotes checked against that text. Report number and date taken from https://mprove.de/visionreality/index.html, fetched the same day. Re-verify at the URLs above."
}
```

## Evidence

- Specifier: "A specifier is a tuple of UID, anchor ID, direction and presentation (4) specification. The direction value can be FROM, TO, BIDIRECT, or NONE."
- One-way links in Dexter: "The common case of uni-directional text links is modeled in the way that the first specifier has the direction value set to FROM and the second specifier the direction value set to TO."
- Link: "A link is a component that contains a sequence of at least 2 specifiers."
- "Concepts like trails, paths, tours or sequences can be represented by Dexter links with more than 2 specifiers."
- Link metadata: "meta-data like keywords for hyperlinks can be attached as special attributes of the component information section for link components."
- Closing paragraph: "it is possible to specify links to links."

What the source shows: in Dexter a link is a stored component of its own, with any number of ends, a direction per end, and attributes. Direction is a property of the link, not of where the link is stored.

What it does not show: Halasz and Schwartz's own wording. It names no required provenance attributes, such as author or date, on links.
