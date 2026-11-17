# A1-SR-08 What's New in RDF 1.1 (Working Group Note)

```json
{
  "source_identity": "What's New in RDF 1.1, W3C Working Group Note, https://www.w3.org/TR/rdf11-new/",
  "author_or_issuing_body": "W3C RDF Working Group",
  "publisher": "World Wide Web Consortium (W3C)",
  "publication_date": "2014-02-25T00:00:00Z",
  "relevant_event_date": "2014-02-25",
  "source_family": "Primary. W3C Note; same working group as the RDF 1.1 Recommendations.",
  "precise_evidence_location": "Sections 2.1 to 2.4, 3, and 4 (change table).",
  "method": "Editorial summary of changes between RDF 1.0 and RDF 1.1.",
  "limitations": "Shows the list of changes from RDF 1.0 to 1.1. States a rationale for few of them. Does not name any critic or complaint document. A Note is informative and not normative.",
  "provenance": "Fetched on 2026-11-17 with the WebFetch tool, which returns a model-written extract of the page, not the raw page. Re-verify by opening the URL and checking the quoted sections."
}
```

## Evidence

- 2.1: identifiers are IRIs, not URI references. Blank node identifiers are "not persistent or portable identifiers"; Skolemization is recommended.
- 2.2: language-tagged literals get datatype `rdf:langString`; simple literals become a synonym for `xsd:string`.
- 2.2: `rdf:HTML` and `rdf:XMLLiteral` are non-normative. Stated reason: the HTML literal follows the unfinished DOM4 specification.
- 2.3: RDF datasets are introduced. Section 3: RDF/XML is no longer the only recommended serialization; Turtle, TriG, N-Triples, N-Quads, and JSON-LD are added. Reason given: RDF is the data model, not a serialization.
- 4: the one change that affects entailment is that graphs with invalid literals such as `"a"^^xsd:integer` are inconsistent for recognized datatypes.
- For most other rows the fetch extract found no stated rationale.
