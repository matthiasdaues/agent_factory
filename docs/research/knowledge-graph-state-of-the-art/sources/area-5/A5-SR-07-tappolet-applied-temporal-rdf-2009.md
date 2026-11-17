# A5-SR-07: Tappolet and Bernstein, Applied Temporal RDF (abstract)

```json
{
  "source_identity": "Jonas Tappolet, Abraham Bernstein, 'Applied Temporal RDF: Efficient Temporal Querying of RDF Data with SPARQL', ESWC 2009, LNCS 5554, pp. 308-322; https://2009.eswc-conferences.org/program-menu/accepted-papers/122-jonas-tappolet-and-abraham-bernstein-applied-temporal-rdf-efficient-temporal-querying-of-rdf-data-with-sparql468e.pdf",
  "author_or_issuing_body": "Jonas Tappolet, Abraham Bernstein (University of Zurich)",
  "publisher": "Springer (LNCS 5554); one-page abstract hosted on the ESWC 2009 site",
  "publication_date": "2009-01-01T00:00:00Z",
  "relevant_event_date": "2009-01-01",
  "source_family": "Primary (abstract of the original paper). Builds on Temporal RDF (A5-SR-06).",
  "precise_evidence_location": "The one-page abstract (page 1 of 1)",
  "method": "Proposes a syntax and storage format using named graphs, a shorthand query format T-SPARQL translated to SPARQL, and an index for time-point queries.",
  "limitations": "Only the abstract was reachable. The full text, the evaluation numbers and the paper's own criticism of earlier approaches were not read. Year only; date set to 1 January 2009. The abstract's efficiency claim ('vastly reduces the number of triples') is the authors' claim and was not checked.",
  "provenance": "PDF downloaded with curl on 2026-11-17 and extracted with pdftotext. Re-verify at the URL above or DOI 10.1007/978-3-642-02121-3_25."
}
```

## Evidence

- Abstract: "Until recently, the only way to incorporate time into Semantic Web models was as a data type property. Temporal RDF, however, considers time as an additional dimension in data preserving the semantics of time."
- Abstract: "we present a syntax and storage format based on named graphs to express temporal RDF. Given the restriction to preexisting RDF-syntax, our approach can perform any temporal query using standard SPARQL syntax only."
- Abstract: T-SPARQL is a shorthand that "can be translated to standard SPARQL".
- Not shown: why the authors chose named graphs over the labelled-triple syntax of A5-SR-06. The abstract names no criticism of that proposal.
