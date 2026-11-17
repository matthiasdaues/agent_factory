# A4-SR-05: SPIN overview and motivation, W3C Member Submission

```json
{
  "source_identity": "Holger Knublauch, James A. Hendler, Kingsley Idehen. 'SPIN - Overview and Motivation'. W3C Member Submission, 22 February 2011. https://www.w3.org/submissions/spin-overview/",
  "author_or_issuing_body": "Holger Knublauch (TopQuadrant), James A. Hendler (Rensselaer Polytechnic Institute), Kingsley Idehen (OpenLink Software)",
  "publisher": "World Wide Web Consortium (W3C)",
  "publication_date": "2011-02-22T00:00:00Z",
  "relevant_event_date": "2011-02-22",
  "source_family": "Primary. Member Submission by the vendors of the SPIN products. The W3C does not endorse it. The later SHACL Recommendation (record 11) shares an editor with it.",
  "precise_evidence_location": "Abstract and the 'Overview and Motivation' text, which carries no section numbers",
  "method": "Fetched the page on 2026-11-17, converted it to plain text, and matched the quoted sentences against that text.",
  "limitations": "A short overview, not the specification. It describes constraints as SPARQL queries linked to classes. It does not mention the closed-world assumption and does not discuss validation as a separate problem from inference. The SPIN modeling vocabulary and syntax documents were not read.",
  "provenance": "Retrieved from https://www.w3.org/submissions/spin-overview/ on 2026-11-17 with curl. Re-verify by searching the page for 'spin:constraint'."
}
```

## Evidence

### What SPIN offers for constraints

- Abstract: "SPIN is a SPARQL-based rule and constraint language for the Semantic Web."
- Overview: "One of the basic ideas of SPIN is to link class definitions with SPARQL queries to capture constraints and rules."
- The overview gives `spin:constraint` linking a class to a SPARQL ASK query as its example.

### Relation to RDFS and OWL

- Overview: RDFS and OWL "define axiomatic definitions of data structures," and "describing general computational behavior of objects is not within the scope of these standards."

### What this record supports

- It is the first source in concept 2, "Shape languages for RDF validation": validation as SPARQL queries attached to classes, with no separate shape vocabulary (area index, concept 2, step 1).
