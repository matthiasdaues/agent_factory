# A1-SR-07: Berners-Lee, HyperText Design Issues: Topology

```json
{
  "source_identity": "Tim Berners-Lee, 'HyperText Design Issues: Topology'; https://www.w3.org/DesignIssues/Topology.html",
  "author_or_issuing_body": "Tim Berners-Lee (signed TimBL), with comments marked JFG",
  "publisher": "W3C Design Issues archive",
  "publication_date": "1992-11-03T00:00:00Z",
  "relevant_event_date": "1991-01-01",
  "source_family": "Primary. Berners-Lee design lineage; separate text from A1-SR-06.",
  "precise_evidence_location": "Sections 'Should the links be monodirectional or bidirectional ?', 'Should links be typed?' and 'Should links contain ancillary information?'",
  "method": "Design note. The author lists design questions for the hypertext web and states his position on each.",
  "limitations": "The page carries no date. It cites the Aquanet paper 'at HT91', so it was written in 1991 or later; relevant_event_date 1991-01-01 is that lower bound, year only. publication_date 1992-11-03 is the date of the W3C history snapshot the page links into, not a stated publication date. The page states design positions, not what browsers or servers implemented.",
  "provenance": "HTML page downloaded with curl on 2026-11-18; tags stripped with a local script; quotes checked against that text. Re-verify at the URL above."
}
```

## Evidence

- Direction: "If they are bidirectional, a link always exists in the reverse direction. A disadvantage of this being enforced is that it might constrain the author of a hypertext - he might want to constrain the reader."
- "KMS and hypercard have one-way links; Enquire has two-way links. There is a question of how one can make a two-way link to a protected database."
- Dangling links: "if a document is destroyed or moved, one is aware of what dangling links will be created, and can possibly fix them."
- The chosen compromise: "A compromise that links be one-way in the data model, but that a reverse link is created when any link is made, so long as this can be done without infringing protection. An alternative is for the reverse links to be gathered by a background process operating on a basically monodirectionally linked web."
- Link metadata: "Does the system allow dating, versioning, authorship, comment text on a link?"
- His answer: "Pretty soon, following this path leads to a link becoming a node in itself, annotatable and all. This perverts the data model significantly, and I cannot see that that is a good idea. Information about the link can always be put in the source node, or in an intermediate node, for example an annotation."
- "Perhaps one should make a link annotatable. I think not."

What the source shows: the Web link is one-way in the data model by choice. Berners-Lee names two ways to recover the reverse direction: create a reverse link on write, or gather back-links with a background process. He rejects dates, versions and authorship on the link itself and points them to an annotation node.

What it does not show: that either back-link method was built into the Web, or any measure of how often links dangle.
