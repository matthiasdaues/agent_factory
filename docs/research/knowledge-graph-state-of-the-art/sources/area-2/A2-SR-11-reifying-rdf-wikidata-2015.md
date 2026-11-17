# A2-SR-11: Reifying RDF: What Works Well With Wikidata? (2015)

```json
{
  "source_identity": "Hernandez, Hogan, Kroetzsch: Reifying RDF: What Works Well With Wikidata? Proceedings of the 11th International Workshop on Scalable Semantic Web Knowledge Base Systems (SSWS 2015), https://aidanhogan.com/docs/reification-wikidata-rdf-sparql.pdf",
  "author_or_issuing_body": "Daniel Hernandez, Aidan Hogan, Markus Kroetzsch",
  "publisher": "CEUR Workshop Proceedings (author copy hosted by Aidan Hogan)",
  "publication_date": "2015-01-01T00:00:00Z",
  "relevant_event_date": "2015-07-11",
  "source_family": "Primary. Empirical comparison paper; one author (Kroetzsch) is also an author of A2-SR-07 and A2-SR-08, so the sources are not independent of the Wikidata team.",
  "precise_evidence_location": "Abstract; section 4 Existing Reification Approaches; loading results (paragraph 'Loading data'); property path paragraph; section 6 Conclusions",
  "method": "PDF downloaded with curl and read with pdftotext. Event date is the retrieval date of the Wikidata data in the paper footnotes (2015-07-11).",
  "limitations": "Publication date is year only. Five SPARQL engines from 2015 and one Wikidata dump are tested, so results may not hold for current engines. Shows measured load and query behaviour of four models. Does not test RDF-star or any later model.",
  "provenance": "Retrieved on 2026-11-17 with WebFetch, WebSearch or curl; PDF read locally; re-verify at the URL."
}
```

## Evidence

- Abstract: four options compared on Wikidata data: standard reification, n-ary relations, singleton properties, named graphs.
- Loading data: 4store and GraphDB ran into problems loading singleton properties because "the indexing schemes used assume a low number of unique predicates." The authors did not index that dataset in those two engines. 4store also slowed to 24 triples per second on the full named graphs dataset.
- Property paths: paths cannot be expressed in the singleton-property or standard reification models. They work in the n-ary model with a pattern such as :P31s/:P31v/(:P279s/:P279v)\* and in the named graph model if the default graph is the union of all graphs.
- Section 6: singleton properties gave "the most concise representation on a triple level", but n-ary was the only model with built-in property path support. Otherwise the authors found "no clear winner between standard reification, n-ary predicates and named graphs."
