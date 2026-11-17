# A4-SR-01: OWL 2 Primer: open-world assumption and absent unique name assumption

```json
{
  "source_identity": "OWL 2 Web Ontology Language Primer (Second Edition), W3C Recommendation, https://www.w3.org/TR/owl2-primer/",
  "author_or_issuing_body": "W3C OWL Working Group; editors Pascal Hitzler, Markus Kroetzsch, Bijan Parsia, Peter F. Patel-Schneider, Sebastian Rudolph",
  "publisher": "World Wide Web Consortium (W3C)",
  "publication_date": "2012-12-11T00:00:00Z",
  "relevant_event_date": "2012-12-11",
  "source_family": "Primary. W3C Recommendation text for OWL 2. Independent of the integrity-constraint papers and the shape-language papers, which cite OWL's semantics but do not copy this text.",
  "precise_evidence_location": "Section 2 'What is OWL 2?' (paragraph contrasting OWL 2 documents with databases); Section 4.7 'Equality and Inequality of Individuals'",
  "method": "Fetched the page on 2026-11-17, converted it to plain text, and searched for the passages. Quotes below were matched against that text.",
  "limitations": "A tutorial, not the normative semantics. It states the open-world assumption and the absent unique name assumption in plain words. It does not define them formally and does not discuss validation, integrity constraints, or any critique of OWL for data checking. It is the Second Edition of 2012; the first OWL 2 Recommendation of 2009 was not read.",
  "provenance": "Retrieved from https://www.w3.org/TR/owl2-primer/ on 2026-11-17 with curl. Re-verify by fetching the same URL and searching for 'open-world assumption'."
}
```

## Evidence

### Open-world assumption

- Section 2: "in the case of an OWL 2 document it may simply be missing (but possibly true), following the open-world assumption." The sentence compares a missing fact in OWL 2 with a missing fact in a database.

### No unique name assumption

- Section 4.7: "OWL does not make the assumption that different names are names for different individuals."
- The same paragraph calls the missing "unique names assumption" well suited to Semantic Web applications where names may be coined by different parties.

### What this record supports

- It gives the baseline that every later validation proposal in this area departs from: OWL treats missing data as unknown, and it does not treat different names as different things.
- It is the earliest source in the concept history "Constraint semantics for OWL axioms" (area index, concept 1, step 1).
