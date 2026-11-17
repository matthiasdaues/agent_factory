# A2-SR-03: Defining N-ary Relations on the Semantic Web (2006)

```json
{
  "source_identity": "Defining N-ary Relations on the Semantic Web, W3C Working Group Note, 12 April 2006, https://www.w3.org/TR/swbp-n-aryRelations/",
  "author_or_issuing_body": "Natasha Noy and Alan Rector (editors); W3C Semantic Web Best Practices and Deployment Working Group",
  "publisher": "W3C",
  "publication_date": "2006-04-12T00:00:00Z",
  "relevant_event_date": "2006-04-12",
  "source_family": "Primary. W3C Semantic Web Best Practices Working Group notes.",
  "precise_evidence_location": "Section 1 (Issue 1), section 3.2 (Pattern 1, use cases 3.2.1 to 3.2.3), section 3.3 (Pattern 2), section 4 (reification)",
  "method": "W3C Working Group Note read with WebFetch. Section numbers come from the table of contents because the headings are unnumbered.",
  "limitations": "A Note is informative, not a standard. It shows the recommended patterns and why they avoid RDF reification. It does not show how often the patterns were adopted or how they performed.",
  "provenance": "Retrieved on 2026-11-17 with WebFetch, WebSearch or curl; re-verify at the URL, sections as listed."
}
```

## Evidence

- Issue 1 and use case 1: how to describe the instances of a relation, such as its certainty or strength.
- Pattern 1 (3.2): "create a new class and n new properties to represent an n-ary relation." Pattern 2 (3.3): represent the participants as a collection or ordered list.
- Section 4: the RDF reification vocabulary is for statements with extra information about the triple, such as its source. N-ary relations instead add arguments about the relation instance, such as a diagnosis. The Note avoids the word "reification" for Pattern 1 because the RDF and Topic Map communities use it differently.
