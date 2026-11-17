# A2-SR-15: RDF-star Working Group mailing list, F. Franconi on triple term opacity, 18 April 2024

```json
{
  "source_identity": "Re: proposal: a reifier should reify only one \"thing\", message of 18 April 2024, https://lists.w3.org/Archives/Public/public-rdf-star-wg/2024Apr/0104.html",
  "author_or_issuing_body": "Enrico Franconi, member of the W3C RDF-star Working Group",
  "publisher": "W3C (public-rdf-star-wg mailing list archive)",
  "publication_date": "2024-04-18T13:37:57Z",
  "relevant_event_date": "2024-04-18",
  "source_family": "Primary. Working group deliberation record; a single participant's position.",
  "precise_evidence_location": "Message body, argument against the proposal of P.-A. Champin",
  "method": "Mailing list archive page read with WebFetch (summarized by the tool; direct quotes are short).",
  "limitations": "Shows one member's argument in a debate, not a group decision. The member argues for full opacity, the opposite of the transparent semantics in the later drafts (A2-SR-17). It does not show how the group resolved the question or what drove that resolution.",
  "provenance": "Retrieved on 2026-11-17 with WebFetch, WebSearch or curl; re-verify at the archive URL."
}
```

## Evidence

- Franconi argues that "full opacity" is "the only way out": two triple terms denote the same resource only if they have the same canonical syntactic form.
- He states that under the transparent option "simple entailment and therefore SPARQL BGPs have to rely on more complex reasoning mechanisms", and that the other reading produces unexpected entailments such as owl:sameAs links.
- He accepts that full opacity limits reification in RDF 1.2 to syntactic triples, which still serves syntactic annotation, syntactic provenance, and labeled property graphs.
