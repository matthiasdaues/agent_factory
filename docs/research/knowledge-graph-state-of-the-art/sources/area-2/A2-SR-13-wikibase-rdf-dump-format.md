# A2-SR-13: Wikibase RDF Dump Format (statement nodes, truthy triples)

```json
{
  "source_identity": "Wikibase/Indexing/RDF Dump Format, MediaWiki documentation page, https://www.mediawiki.org/wiki/Wikibase/Indexing/RDF_Dump_Format",
  "author_or_issuing_body": "Wikimedia Foundation and community contributors (page authorship not individually recorded)",
  "publisher": "Wikimedia Foundation (mediawiki.org)",
  "publication_date": "2026-11-17T00:00:00Z",
  "relevant_event_date": "2026-11-17",
  "source_family": "Primary. Wikibase project documentation; same lineage as A2-SR-12.",
  "precise_evidence_location": "Sections on statements, qualifiers, references, rank, and truthy statements",
  "method": "Wiki page read with WebFetch. Dates are the retrieval date.",
  "limitations": "Shows today's encoding. It does not state why statement nodes exist; the fetched summary's explanation is the fetcher's inference and is not recorded as evidence. It does not show how the encoding changed since the 2014 export in A2-SR-08.",
  "provenance": "Retrieved on 2026-11-17 with WebFetch, WebSearch or curl; re-verify at the URL."
}
```

## Evidence

- Each full statement is its own node with prefix wds:, linked from the entity by p: predicates. The simple value uses ps:. Qualifiers use pq: predicates. References hang off prov:wasDerivedFrom as reference nodes.
- Rank: the predicate wikibase:rank takes wikibase:PreferredRank, NormalRank, or DeprecatedRank. The best-ranked statements also get the type wikibase:BestRank.
- Truthy statements: "Truthy statements represent statements that have the best non-deprecated rank for a given property." They use wdt: with the simple value and "The qualifiers are ignored."
