# A2-SR-14: RDF-star and SPARQL-star community group report (editors' draft)

```json
{
  "source_identity": "RDF-star and SPARQL-star, RDF-DEV Community Group draft report, https://w3c.github.io/rdf-star/cg-spec/editors_draft.html (moved to https://w3c-cg.github.io/rdf-star/cg-spec/editors_draft.html)",
  "author_or_issuing_body": "W3C RDF-DEV Community Group, RDF-star task force",
  "publisher": "W3C Community Group",
  "publication_date": "2026-11-17T00:00:00Z",
  "relevant_event_date": "2021-12-17",
  "source_family": "Primary. Successor of A2-SR-09; predecessor of the RDF 1.2 work in A2-SR-17. Not a W3C standard.",
  "precise_evidence_location": "Section 2 Quoted and Asserted Triples (common misconceptions); section 6 Referential opacity and Other alternatives to referential opacity; Historical remarks (SA-mode and PG-mode, The seminal example)",
  "method": "HTML downloaded with curl, converted to text with a script, and read. The respec config shows status CG-DRAFT; no publication date or editor list was in the fetched text.",
  "limitations": "Publication date is the retrieval date of a living draft. The event date is the date of A2-SR-09 v3, whose note first shows a report existed. The editors' draft may differ from any published report version. Shows the formulation and the group's own account of its history. Does not show who raised each objection or the dates of each design change.",
  "provenance": "Retrieved on 2026-11-17 with WebFetch, WebSearch or curl; re-verify at the URL; check repository history for dated versions."
}
```

## Evidence

- Section 2: "A quoted triple is a triple used as the subject or object of another triple." A triple that is an element of a graph is asserted. A quoted triple need not be asserted. RDF-star is not shorthand for standard reification and the two can be used together.
- Section 6: quoted triples are referentially opaque. Two quoted triples with distinct but coreferent terms count as different. The report lists drawbacks of opacity, discusses transparency-enabling properties, and says of alternatives that "No clear consensus was reached".
- Historical remarks, SA-mode and PG-mode: in PG-mode every quoted triple was also asserted. In SA-mode a quoted triple was not asserted unless asserted separately. SA-mode "was more flexible, but induced redundancy in the use-cases that PG-mode was designed to address." Turtle-star annotation syntax was introduced "to remove the need for different modes."
- Historical remarks, The seminal example: the original provenance example set wrong expectations. It breaks once several creators and sources are attached to one triple, and RDF-star cannot represent distinct quoted triples with the same subject, predicate and object.
