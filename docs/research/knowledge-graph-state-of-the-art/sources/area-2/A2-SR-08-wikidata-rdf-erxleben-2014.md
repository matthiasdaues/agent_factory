# A2-SR-08: Introducing Wikidata to the Linked Data Web (2014)

```json
{
  "source_identity": "Erxleben, Guenther, Kroetzsch, Mendez, Vrandecic: Introducing Wikidata to the Linked Data Web. ISWC 2014, LNCS 8796, pp. 50-65, DOI 10.1007/978-3-319-11964-9_4, https://ddll.inf.tu-dresden.de/w/images/3/3a/Wikidata-RDF-export-2014.pdf",
  "author_or_issuing_body": "Fredo Erxleben, Michael Guenther, Markus Kroetzsch, Julian Mendez, Denny Vrandecic",
  "publisher": "Springer (LNCS); author copy hosted by TU Dresden",
  "publication_date": "2014-01-01T00:00:00Z",
  "relevant_event_date": "2014-10-21",
  "source_family": "Primary. Wikidata RDF export design paper by Wikidata team members.",
  "precise_evidence_location": "Section 2 (annotations, ranks); section 4.1 Design Principles; section 4.2 Alternatives to Reification",
  "method": "Author-copy PDF downloaded with curl and read with pdftotext. Event date is the ISWC 2014 talk (21 October 2014, from the search result listing the slides).",
  "limitations": "Publication date is year only. The hosted copy was not compared with the Springer version. Shows how the Wikidata team reasoned about RDF encodings in 2014. Singleton properties are discussed in one paragraph and not tested. The authors designed the export they defend.",
  "provenance": "Retrieved on 2026-11-17 with WebFetch, WebSearch or curl; PDF read locally; re-verify at the URL."
}
```

## Evidence

- Section 2: the boundary "between context annotation and n-ary relation is fuzzy", shown with P553 website account on plus P554 account name, and with Star Trek: The Next Generation cast member with two character-role qualifiers.
- Section 2.3: statements have one of three ranks: normal (default), preferred, deprecated.
- Section 4.1: the export reifies Wikidata statements, complex values, and references as resources. The authors say RDF's own reification vocabulary "has been discussed controversially since it is rather inefficient (using four triples to represent one reified triple), and since it lacks a formal semantics". They state they reify Wikidata objects, not RDF triples.
- Section 4.2: quads were suggested for RDF in 2001 by Sean B. Palmer, and similar ideas date to 1993 (Loom). RDF 1.1 gives named graphs "minimal semantics", so entailment is not defined. Using named graphs would lose OWL compatibility and put essential data in annotations on graph names "for which no current standard provides any semantics."
- Section 4.2 on singleton properties: they "would work for our setting, but, again, the semantic relationship between triples with singleton properties and their annotations are not captured by standard semantics."
