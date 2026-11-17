# A2-SR-17: RDF 1.2 Concepts and Abstract Data Model, Candidate Recommendation Draft (16 November 2026)

```json
{
  "source_identity": "RDF 1.2 Concepts and Abstract Data Model, W3C Candidate Recommendation Draft, 16 November 2026, https://www.w3.org/TR/rdf12-concepts/",
  "author_or_issuing_body": "Gregg Kellogg (until 2025-09-06), Olaf Hartig, Pierre-Antoine Champin, Andy Seaborne (editors); W3C RDF and SPARQL Working Group",
  "publisher": "W3C",
  "publication_date": "2026-11-16T00:00:00Z",
  "relevant_event_date": "2026-11-16",
  "source_family": "Primary. W3C RDF 1.2 specification family; area 1 owns standards status.",
  "precise_evidence_location": "Section 1.5 Triple Terms and Reification; section 3.6 Triple Terms; Appendix I Changes between RDF 1.1 and RDF 1.2",
  "method": "HTML downloaded with curl, converted to text, and read; first part also read through WebFetch.",
  "limitations": "A draft, and the page says it is inappropriate to cite as other than work in progress. Shows the current formulation. Appendix I lists the addition of triple terms but gives no reasons or criticism. The earlier working drafts of 2025 were seen only as search result titles and a summary, not read.",
  "provenance": "Retrieved on 2026-11-17 with WebFetch, WebSearch or curl; re-verify at the URL; dated versions are linked from the page."
}
```

## Evidence

- Section 1.5: "A triple term is an RDF triple used as an RDF term within another triple." A reifying triple has predicate rdf:reifies and a triple term as object. Its subject is a reifier, which "can be the subject or object of other triples."
- Section 1.5: a triple term may be unasserted. The proposition counts as claimed true only if the same triple is also asserted in the graph. A reifier plus triples about it is a triple annotation.
- Section 1.5: "RDF terms that appear in a triple term have the same denotation as when they appear in an asserted triple ... For this reason, we say that triple terms are transparent."
- Appendix I: "Added 1.5 Triple Terms and Reification and definitions for triple term and asserted triple and extended the definition of RDF triple to permit triple terms as objects." The same appendix lists base direction, quads and a version announcement.
