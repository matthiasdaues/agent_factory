# A1-SR-10 OWL Web Ontology Language Overview (OWL 1 Recommendation)

```json
{
  "source_identity": "OWL Web Ontology Language Overview, W3C Recommendation, https://www.w3.org/TR/2004/REC-owl-features-20040210/",
  "author_or_issuing_body": "W3C Web Ontology Working Group",
  "publisher": "World Wide Web Consortium (W3C)",
  "publication_date": "2004-02-10T00:00:00Z",
  "relevant_event_date": "2004-02-10",
  "source_family": "Primary. W3C Recommendation; first formulation of OWL.",
  "precise_evidence_location": "Section 1.3 (The three sublanguages of OWL); section 3.3 (transitive properties).",
  "method": "Specification overview published by the working group.",
  "limitations": "Shows the design of OWL 1 and its three sublanguages with their guarantees. Does not show later criticism. The URL was fetched with a 2009 status note saying OWL 2 is available.",
  "provenance": "Fetched on 2026-11-17 with the WebFetch tool, which returns a model-written extract of the page, not the raw page. Re-verify by opening the URL and checking the quoted sections."
}
```

## Evidence

- 1.3: "OWL DL supports those users who want the maximum expressiveness while retaining computational completeness." OWL DL is decidable.
- 1.3: "OWL Full is meant for users who want maximum expressiveness and the syntactic freedom of RDF." It has no computational guarantees; complete reasoning support does not exist.
- 1.3: every OWL document is an RDF document; only some RDF documents are legal OWL Lite or OWL DL documents.
- 3.3: without a cardinality side-condition on transitive properties, OWL Lite and OWL DL would become undecidable.
