# A1-SR-12 OWL 2 Web Ontology Language: New Features and Rationale, Second Edition

```json
{
  "source_identity": "OWL 2 Web Ontology Language: New Features and Rationale (Second Edition), W3C Recommendation, https://www.w3.org/TR/owl2-new-features/",
  "author_or_issuing_body": "W3C OWL Working Group (editors Christine Golbreich and Evan K. Wallace)",
  "publisher": "World Wide Web Consortium (W3C)",
  "publication_date": "2012-12-11T00:00:00Z",
  "relevant_event_date": "2012-12-11",
  "source_family": "Primary. W3C Recommendation; succeeds OWL 1.",
  "precise_evidence_location": "Sections 2.1 to 2.6 (F1 to F14), section 3 (profiles), section 4 (syntax).",
  "method": "Working group rationale document.",
  "limitations": "Shows the OWL 1 limitations the working group lists as motivation and the features OWL 2 adds. Does not name the sources of each complaint and does not show that OWL 1.1 was the direct input. The second edition is dated 2012; the first OWL 2 Recommendation is earlier and was not fetched. Only the first 100,000 of 158,345 characters were read.",
  "provenance": "Fetched on 2026-11-17 with the WebFetch tool, which returns a model-written extract of the page, not the raw page. Re-verify by opening the URL and checking the quoted sections."
}
```

## Evidence

- 2.3.1 (F10): OWL 1 supported only integers and strings and no subsets of them.
- 2.2.2 (F5): OWL 1 could count property values but not restrict the class of the values counted (qualified cardinality).
- 2.2.3 (F6) and 2.2.4 (F7): "impossible to assert that the property is reflexive, irreflexive or asymmetric"; "impossible to state that properties are disjoint."
- 2.2.5 (F8): no property chains. 2.2.6 (F9): no keys.
- 2.4.1 (F12): OWL 1 DL required strict separation of names; OWL 2 adds punning.
- 3: OWL 1 DL, Full, and Lite were "not sufficient" for later deployments, which led to the EL, QL, and RL profiles.
- 4.2: OWL Lite was not re-specified for OWL 2.
