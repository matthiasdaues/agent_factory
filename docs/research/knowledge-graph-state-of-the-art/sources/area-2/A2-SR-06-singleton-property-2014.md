# A2-SR-06: Singleton Property (Nguyen, Bodenreider, Sheth 2014)

```json
{
  "source_identity": "Nguyen, Bodenreider, Sheth: Don't Like RDF Reification? Making Statements about Statements Using Singleton Property. WWW 2014, pp. 759-770, DOI 10.1145/2566486.2567973",
  "author_or_issuing_body": "Vinh Nguyen, Olivier Bodenreider, Amit Sheth",
  "publisher": "ACM / International World Wide Web Conference Committee (copy hosted by US National Library of Medicine, https://www.lhncbc.nlm.nih.gov/LHC-publications/PDF/pub8934.pdf)",
  "publication_date": "2014-04-07T00:00:00Z",
  "relevant_event_date": "2014-04-07",
  "source_family": "Primary. Original singleton-property proposal.",
  "precise_evidence_location": "Abstract; section 1.1 Motivating example; section 1.2 Our approach; section 2.1",
  "method": "PDF downloaded through WebFetch and read with pdftotext. Date is the first day of WWW 2014 (7 to 11 April 2014, from the ACM anthology listing).",
  "limitations": "The authors argue for their own proposal, so the criticism of reification is one-sided. Shows the stated criticism and the design. Does not show independent performance results; the paper's own experiments use one knowledge base (BKR).",
  "provenance": "Retrieved on 2026-11-17 with WebFetch, WebSearch or curl; PDF text read locally; re-verify by downloading the PDF at the hosted URL."
}
```

## Evidence

- Abstract: reification "does not have formal semantics and is not commonly used in practice as described in the RDF Primer."
- Section 1.1: "The lack of formal semantics connecting a statement and the resource describing it is one of the main drawbacks of using reification." Reification needs four additional triples per statement per document, which would increase data size "by at least four times, which is not a scalable approach", and it makes queries lengthy.
- Section 1.2: a singleton property is a property instance for one relationship between two entities in one context. It is linked to its generic property by the new property singletonPropertyOf, defined as a sub property of rdf:type.
- Section 2.1: attaching one rdfs:subPropertyOf child per fact is rejected. The paper cites 23,770 YAGO facts using isMarriedTo.
