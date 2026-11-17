# A3-SR-14 — Chesñevar et al., "Towards an argument interchange format" (2006)

```json
{
  "source_identity": "Chesñevar, C., McGinnis, J., Modgil, S., Rahwan, I., Reed, C., Simari, G., South, M., Vreeswijk, G., Willmott, S., 'Towards an argument interchange format', The Knowledge Engineering Review 21(4), 293-316, DOI 10.1017/S0269888906001044",
  "author_or_issuing_body": "Nine authors from universities in Spain, the United Kingdom, Argentina, the Netherlands and the United Arab Emirates, and Cancer Research UK",
  "publisher": "Cambridge University Press; the copy read is hosted at cs.uns.edu.ar",
  "publication_date": "2006-12-01T00:00:00Z",
  "relevant_event_date": "2005-09-01",
  "source_family": "Primary. Original AIF specification paper. A3-SR-15 and A3-SR-17 share authors (Rahwan, Reed) and are not independent of it.",
  "precise_evidence_location": "Abstract; Section 1 'Introduction and background', paragraphs on argument mark-up languages and their two limitations; the passage beginning 'There are two types of node' that defines I-nodes and S-nodes.",
  "method": "A consensus draft specification of an abstract model, with a use case and three concrete reifications.",
  "limitations": "Publication date is month-only (issue 21:4, December 2006) and was taken from a search result, not from the PDF. The event date is the AgentLink meeting in Budapest in September 2005, from a footnote, month-only. The paper calls itself 'a starting point for further discussion' and not a definitive model. It criticizes earlier mark-up languages in two paragraphs and does not review them in depth. The section number of the node definitions was not captured.",
  "provenance": "Fetched 2026-11-17 with curl from http://cs.uns.edu.ar/~grs/Publications/2006-Chesnevaretal-KER.pdf and converted with pdftotext. Quotes are exact and were checked against the extracted text."
}
```

## Evidence

- Abstract: "one major barrier to the development and practical deployment of argumentation systems is the lack of a shared, agreed notation or 'interchange format' for argumentation and arguments." The specification "represents a consensus 'abstract model'" and "is intended as a starting point for further discussion and elaboration by the community, rather than an attempt at a definitive, all-encompassing model."
- Section 1, on earlier mark-up languages (for example the Araucaria tool's AML and the Compendium tool): "These various attempts at providing AMLs share two major limitations. First, each particular language is designed for use with a specific tool [...] rather than for facilitating inter-operability of arguments among a variety of tools."
- Section 1: "Another limitation of the above AMLs is that they are primarily aimed at enabling users to structure arguments through diagrammatic linkage of natural language sentences [...] Hence, these mark-up languages are not designed to process formal logical statements such as those used within multi-agent systems."
- Model: "There are two types of node, namely information nodes (I-nodes) and scheme application nodes or scheme nodes (S-nodes for short)." I-nodes "represent claims that depend on the domain of discourse". S-nodes are applications of schemes, with subtypes inference application (RA), preference application (PA) and conflict application (CA) nodes.
- Footnote 1: the article "started life as a skeleton for contributions from participants at an AgentLink Technical Forum Group meeting in Budapest in September 2005".

## What the source shows

It shows the first AIF formulation (2006): an abstract node-and-edge model for argument, built because earlier mark-up languages were tied to single tools and lacked a semantic model.

## What the source does not show

It gives no adoption evidence and no serialization in RDF. It does not show how the model handles dialogue (A3-SR-16).

## Failed searches and gaps

The earlier mark-up languages (Araucaria AML, Compendium, ASCE) were not read first-hand.
