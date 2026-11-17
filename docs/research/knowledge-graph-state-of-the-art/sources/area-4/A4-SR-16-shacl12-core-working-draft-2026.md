# A4-SR-16: SHACL 1.2 Core, W3C Working Draft

```json
{
  "source_identity": "Holger Knublauch, Thomas Bergwinkl, Yousouf Taghzouti, Jesse Wright (editors). 'SHACL 1.2 Core'. W3C Working Draft, 16 November 2026. https://www.w3.org/TR/shacl12-core/",
  "author_or_issuing_body": "W3C Data Shapes Working Group; editors Holger Knublauch and Thomas Bergwinkl (TopQuadrant), Yousouf Taghzouti (Inria), Jesse Wright (University of Oxford); former editor Dimitris Kontokostas",
  "publisher": "World Wide Web Consortium (W3C)",
  "publication_date": "2026-11-16T00:00:00Z",
  "relevant_event_date": "2026-11-16",
  "source_family": "Primary. Draft on the Recommendation track and successor to record 11. A draft can change or be withdrawn at any time.",
  "precise_evidence_location": "Section 6.7.3 'Handling of Recursive Shapes' and its non-normative remainder; Section 6.18 'Changes between the original SHACL Core and SHACL 1.2 Core'",
  "method": "Downloaded the page on 2026-11-17, converted it to plain text, and matched the recursion paragraphs and the change list against that text.",
  "limitations": "A Working Draft, not a Recommendation. The draft shows the Working Group's position on 16 November 2026 and may change. The change list was read in part. The reasons for the 2017 choice are given only in the non-normative paragraph quoted below. Working Group minutes and issue threads were not read.",
  "provenance": "Downloaded from https://www.w3.org/TR/shacl12-core/ on 2026-11-17 with curl. Re-verify by searching the page for 'The recursion policy above'."
}
```

## Evidence

### Recursion in SHACL 1.2

- Section 6.7.3: "The validation with recursive shapes is not defined in SHACL and is left to SHACL processor implementations. For example, SHACL processors may support recursion scenarios or produce a failure when they detect recursion."
- Non-normative remainder: "By leaving recursion undefined, implementations may choose to not support recursion so that they can issue a static set of SPARQL queries (against SPARQL end points) without having to support cycles."
- Same passage: "The expectation is that future work, for example in W3C Community Groups, will lead to the definition of specific dialects of SHACL where recursion is well-defined."

### Other changes

- Section 6.18 lists additions such as node expressions, `sh:someValue`, `sh:reifierShape`, and the move of SPARQL-based validators to an appendix of SHACL-SPARQL. The list read does not contain a recursion semantics.

### What this record supports

- It records that the 2017 position on recursion still stands in the 2026 draft (area index, concept 2, step 6; concept 3, step 10).
