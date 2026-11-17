# A1-SR-07 RDF 1.1 Concepts and Abstract Syntax (Recommendation)

```json
{
  "source_identity": "RDF 1.1 Concepts and Abstract Syntax, W3C Recommendation, https://www.w3.org/TR/rdf11-concepts/",
  "author_or_issuing_body": "W3C RDF Working Group",
  "publisher": "World Wide Web Consortium (W3C)",
  "publication_date": "2014-02-25T00:00:00Z",
  "relevant_event_date": "2014-02-25",
  "source_family": "Primary. W3C Recommendation; lineage: RDF 1.0 Concepts (2004).",
  "precise_evidence_location": "Header; Status of This Document; sections 1.5, 3.2, 3.3, 4, 5, Appendix A.",
  "method": "Specification text published by the working group.",
  "limitations": "Shows the RDF 1.1 data model: IRIs, literals, graphs, datasets. Does not contain a changes section; Appendix A points to the separate 'What's New' note (record A1-SR-08). Gives no criticism of RDF 1.0.",
  "provenance": "Fetched on 2026-11-17 with the WebFetch tool, which returns a model-written extract of the page, not the raw page. Re-verify by opening the URL and checking the quoted sections."
}
```

## Evidence

- Header: "W3C Recommendation 25 February 2014". Status: "It is a stable document and may be used as reference material or cited from another document."
- Status: "A new concept in RDF 1.1 is the notion of an RDF dataset to represent multiple graphs."
- Section 1.5: RDF graphs are static snapshots of information. Section 3.3: "Simple literals are syntactic sugar for abstract syntax literals."
- Section 4: a dataset has one default graph and zero or more named graphs; graphs can be named by an IRI or a blank node, which differs from SPARQL 1.1.
