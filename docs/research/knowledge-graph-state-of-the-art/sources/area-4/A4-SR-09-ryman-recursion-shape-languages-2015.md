# A4-SR-09: Ryman: Recursion in RDF Data Shape Languages

```json
{
  "source_identity": "Arthur Ryman. 'Recursion in RDF Data Shape Languages'. arXiv:1505.04972v2 [cs.DB]. https://arxiv.org/abs/1505.04972",
  "author_or_issuing_body": "Arthur Ryman (IBM, as in the Resource Shape submission)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2015-11-01T00:00:00Z",
  "relevant_event_date": "2015-11-01",
  "source_family": "Primary. Single-author preprint by the author of Resource Shape 2.0 (record 7). It was not read as peer reviewed, and no venue is named on the page.",
  "precise_evidence_location": "Section 1; Section 2; Section 7.1 (Relation to Resource Shape 2.0); Section 7.2 (Relation to ShEx); Section 7.3; Section 8",
  "method": "Fetched the HTML version on 2026-11-17, converted it to plain text, and matched the quotes against that text.",
  "limitations": "The date is that of version 2 stamped on the page, 1 November 2015. The date of version 1 was not found. The preprint states no venue. It covers Resource Shape 2.0 in depth and ShEx only in outline. It says nothing about SHACL 1.0, which was not yet published. It gives no complexity result.",
  "provenance": "Retrieved from https://arxiv.org/html/1505.04972 on 2026-11-17 with curl. Re-verify by searching the text for 'precise definition of recursion'."
}
```

## Evidence

### Criticism of the member submissions

- Section 2: "Neither of the member submissions included a precise definition of recursion."
- Section 2.1 shows that a naive reading of cyclic constraints has several solutions: the consistency condition "does not uniquely determine the values of the propositional variables."

### The formulation

- Introduction: "This article provides a precise definition of the meaning of recursion as used in Resource Shape 2.0."
- Section 7.1: Resource Shape 2.0 "allows recursive shapes via the property oslc:valueShape," and "this recursion has a well-defined meaning and causes no difficulties."
- Section 6.1: a labelling procedure that terminates because there are "a finite number of nodes and a finite number of names."

### Relation to ShEx

- Section 7.2: "ShEx also allows recursion via reference to named shapes." The paper says it is "not clear" whether ShEx usage can be expressed in the same framework and that "More analysis is required" (Section 8).

### What this record supports

- It records the first explicit statement that the 2014 shape proposals left recursion undefined, and a first definition (area index, concept 3, step 3).
