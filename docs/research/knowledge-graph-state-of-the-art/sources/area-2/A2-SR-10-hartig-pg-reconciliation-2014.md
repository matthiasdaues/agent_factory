# A2-SR-10: Reconciliation of RDF\* and Property Graphs (Hartig 2014)

```json
{
  "source_identity": "Hartig: Reconciliation of RDF* and Property Graphs. arXiv:1409.3288 (v1 11 September 2014; v2 13 November 2014), https://arxiv.org/abs/1409.3288",
  "author_or_issuing_body": "Olaf Hartig",
  "publisher": "arXiv",
  "publication_date": "2014-09-11T00:00:00Z",
  "relevant_event_date": "2014-09-11",
  "source_family": "Primary. Same author as A2-SR-09; companion paper that ties RDF* to property graphs.",
  "precise_evidence_location": "Abstract (arXiv listing)",
  "method": "arXiv abstract page read with WebFetch. The full text was not read.",
  "limitations": "Only the abstract was read. It shows that the paper claims a formal bridge between RDF* and property graphs, which have edge properties. It does not show the transformation rules, the property graph definition used, or any criticism. No property-graph-side source on how edge properties arose (Cypher, Gremlin, TinkerPop) is recorded for this area.",
  "provenance": "Retrieved on 2026-11-17 with WebFetch, WebSearch or curl; abstract only; re-verify at the arXiv URL."
}
```

## Evidence

- Abstract: property graphs and RDF are both widely used. Existing converters between them are incompatible and lack a formal basis, and the property graph model has no commonly accepted formal definition.
- Abstract: the paper proposes a formalization of the property graph model and transformations between property graphs and RDF, so users can run Gremlin or Cypher over RDF data and SPARQL over property graph content.
