# A2-SR-07: Wikidata: a free collaborative knowledgebase (2014)

```json
{
  "source_identity": "Vrandecic, Kroetzsch: Wikidata: a free collaborative knowledgebase. Communications of the ACM 57(10):78-85, DOI 10.1145/2629489, https://iccl.inf.tu-dresden.de/w/images/8/89/Wikidata-CACM-2014.pdf",
  "author_or_issuing_body": "Denny Vrandecic, Markus Kroetzsch",
  "publisher": "ACM (author copy hosted by TU Dresden)",
  "publication_date": "2014-10-01T00:00:00Z",
  "relevant_event_date": "2012-10-29",
  "source_family": "Primary. Wikidata project design paper by two of its designers.",
  "precise_evidence_location": "Section 'Not-So-Simple Data' (qualifiers); section 'Citation Needed' (references, ranks); statistics table",
  "method": "PDF downloaded with curl and read with pdftotext.",
  "limitations": "Issue date is October 2014; the first day is used. The event date marks the Wikidata launch stated in the article as October 2012; the day is approximate. Shows the design as its authors described it in 2014. Does not show when ranks or qualifiers were added or in what order, nor how the model changed after 2014.",
  "provenance": "Retrieved on 2026-11-17 with WebFetch, WebSearch or curl; PDF read locally; re-verify at the URL."
}
```

## Evidence

- 'Not-So-Simple Data': property-value pairs "are too simple in many cases", for example the population of Rome "as of 2010" from an Istat estimate. The pairs refer to the assertion, so the model gets subordinate property-value pairs, "qualifiers".
- Qualifiers carry context such as validity time and can encode ternary relations (cast member Meryl Streep with qualifier role = Margaret Thatcher). The authors say this "should not, however, be misunderstood as a workaround to represent relations of higher arity", because Wikidata statements have no fixed arity.
- 'Citation Needed': a reference is a list of property-value pairs. Wikidata "does not automatically record provenance but does provide for the structural representation of references."
- Same section: contributors may mark statements "preferred" or "deprecated". Deprecated statements can record erroneous claims of a source. Wikidata "intends to represent all views rather than choose one 'true' claim."
- Statistics table (August 2014): 43,189,145 statements, 23,242,779 with a reference.
