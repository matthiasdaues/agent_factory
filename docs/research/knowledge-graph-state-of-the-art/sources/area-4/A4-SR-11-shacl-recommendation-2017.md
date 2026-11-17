# A4-SR-11: SHACL, W3C Recommendation 2017

```json
{
  "source_identity": "Holger Knublauch, Dimitris Kontokostas (editors). 'Shapes Constraint Language (SHACL)'. W3C Recommendation, 20 July 2017. https://www.w3.org/TR/shacl/",
  "author_or_issuing_body": "W3C RDF Data Shapes Working Group; editors Holger Knublauch (TopQuadrant) and Dimitris Kontokostas (University of Leipzig)",
  "publisher": "World Wide Web Consortium (W3C)",
  "publication_date": "2017-07-20T00:00:00Z",
  "relevant_event_date": "2017-07-20",
  "source_family": "Primary. Normative W3C Recommendation. Records 5 and 7 are earlier inputs from the same field. The Recommendation does not cite ShEx or SPIN in the text read.",
  "precise_evidence_location": "Abstract; Section 3.4.3 'Handling of Recursive Shapes'; Section 1.5 (entailment); Section 4.8.1 (sh:closed)",
  "method": "Fetched the page on 2026-11-17, converted it to plain text, and matched the recursion sentence against that text.",
  "limitations": "The Recommendation text does not discuss SPIN, ShEx, or the closed-world assumption as a general principle. 'Closed' appears only as the sh:closed constraint. The Working Group's reasons for leaving recursion undefined are not in the 2017 text read. The Acknowledgements and Revision History appendices were not read. Other W3C working group records, such as the issue tracker and minutes, were not reached.",
  "provenance": "Retrieved from https://www.w3.org/TR/shacl/ on 2026-11-17 with curl. Re-verify by searching the page for 'Handling of Recursive Shapes'."
}
```

## Evidence

### The formulation

- Abstract: SHACL is "a language for describing and validating RDF graphs."
- Section 1.5: processors may validate over graphs enlarged by RDFS entailment.

### Recursion

- Section 3.4.3: "The validation with recursive shapes is not defined in SHACL and is left to SHACL processor implementations." Processors "may support recursion scenarios or produce a failure when they detect recursion."

### What this record supports

- It records the standard formulation of 2017: a shape language whose recursion is left to implementations (area index, concept 2, step 5; concept 3, step 5). Its sources of criticism are in records 12 to 15.
