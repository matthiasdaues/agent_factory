# A2-SR-12: Wikibase DataModel documentation (statements, qualifiers, references, ranks)

```json
{
  "source_identity": "Wikibase/DataModel, MediaWiki documentation page, https://www.mediawiki.org/wiki/Wikibase/DataModel",
  "author_or_issuing_body": "Wikimedia Deutschland and Wikimedia community contributors (page authorship not individually recorded)",
  "publisher": "Wikimedia Foundation (mediawiki.org)",
  "publication_date": "2026-11-17T00:00:00Z",
  "relevant_event_date": "2026-11-17",
  "source_family": "Primary. Project documentation for the Wikibase software that runs Wikidata. Same project lineage as A2-SR-07, A2-SR-08 and A2-SR-13.",
  "precise_evidence_location": "Sections Statements, Snaks, ReferenceRecords, Ranks of Statements, Goals and requirements",
  "method": "Wiki page read with WebFetch. Wiki pages change; the dates here are the retrieval date, not a revision date.",
  "limitations": "Living page: the publication and event dates are the retrieval date. It shows the model as documented now. It does not show how the model changed over time, and it states that it is not a formal semantics. The statement GUID is not defined on this page.",
  "provenance": "Retrieved on 2026-11-17 with WebFetch, WebSearch or curl; re-verify at the URL and check the page history for the revision."
}
```

## Evidence

- Statements: "Statements describe the claim of a statement and list references for this claim." A statement has a subject, a main snak, a rank, reference records, and qualifier snaks.
- Qualifiers: "qualifier Snaks (or 'qualifiers' for short) store additional information that does not directly refer to the subject."
- References: "intended to store information about some source, represented as a set of Snaks."
- Ranks: preferred ("the most important and most up-to-date information"), normal ("relevant information that is believed to be correct"), deprecated ("may not be considered reliable or that are even known to contain errors").
- Goals and requirements: the model does not mandate class structures, does not define export formats, and is not "a completely precise specification of how to interpret this data formally."
