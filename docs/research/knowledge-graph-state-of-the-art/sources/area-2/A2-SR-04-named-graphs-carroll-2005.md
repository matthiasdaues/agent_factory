# A2-SR-04: Named Graphs, Provenance and Trust (2005)

```json
{
  "source_identity": "Carroll, Bizer, Hayes, Stickler: Named Graphs, Provenance and Trust. WWW 2005, pp. 613-622, https://archives.iw3c2.org/www2005/proceedings/docs/p613.pdf",
  "author_or_issuing_body": "Jeremy J. Carroll, Christian Bizer, Pat Hayes, Patrick Stickler",
  "publisher": "International World Wide Web Conference Committee (WWW 2005 proceedings)",
  "publication_date": "2005-01-01T00:00:00Z",
  "relevant_event_date": "2005-01-01",
  "source_family": "Primary. Original named-graphs paper; a journal version exists (Web Semantics 3(4), 2005) and is not recorded.",
  "precise_evidence_location": "Abstract; introduction paragraph on quads; section 4.2 RDF Reification",
  "method": "PDF downloaded with curl and read with pdftotext.",
  "limitations": "Date is year only; the month is not recorded. Shows the proposal and its stated case against reification. Does not show later use; the model-theoretic semantics sections were not read in full. The proposal is an academic one, not a standard.",
  "provenance": "Retrieved on 2026-11-17 with WebFetch, WebSearch or curl; PDF at the URL; pdftotext layout text, section 4.2."
}
```

## Evidence

- Introduction: "RDF reification has well-known problems in addressing these use cases." Several authors proposed quads, with a fourth element naming sources, statement IDs, or contexts, and the proposals vary widely in what that element means.
- Abstract: extending RDF to named graphs gives a formally defined framework for the trust layer.
- Section 4.2: a reified statement can be thought of as a named graph holding a single triple, "a useful connection with the traditional use of reification and a potential migration path." The semantics of a single-triple graph differ from the "(lack of) semantics" the RDF recommendation gives a reified statement.
