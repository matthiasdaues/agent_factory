# A4-SR-07: Resource Shape 2.0, W3C Member Submission

```json
{
  "source_identity": "Arthur Ryman. 'Resource Shape 2.0'. W3C Member Submission, 11 February 2014. https://www.w3.org/submissions/2014/SUBM-shapes-20140211",
  "author_or_issuing_body": "Arthur Ryman, IBM Corporation (submission request by IBM, Fujitsu, and Universidad Politecnica de Madrid per a W3C submissions index entry)",
  "publisher": "World Wide Web Consortium (W3C)",
  "publication_date": "2014-02-11T00:00:00Z",
  "relevant_event_date": "2014-02-11",
  "source_family": "Primary. Member Submission that originates in the OSLC Resource Shape specification of the Open Services for Lifecycle Collaboration community. Record 9 analyses this document, so the two are not independent.",
  "precise_evidence_location": "Abstract; 'Status of This Document'; Section 1 (paragraph on RDFS and OWL); Section 5.1; Section 5.2; Section 6.23 (oslc:valueShape); Section 7.7",
  "method": "Fetched the page on 2026-11-17, converted it to plain text, and matched the quotes against that text.",
  "limitations": "A member submission with no W3C endorsement. It does not use the words 'closed world' or 'recursion'. The absence of a termination rule for cyclic references is the researcher's reading of the text, not a statement in it. The date is the date on the cover page. A W3C index entry gives a later publication date of 2014-04-09, which was not checked on a primary page.",
  "provenance": "Retrieved from https://www.w3.org/submissions/2014/SUBM-shapes-20140211 on 2026-11-17 with curl. Re-verify by searching the page for 'misapplication'."
}
```

## Evidence

### Criticism of RDFS and OWL for constraints

- Section 1: users "frequently start to use RDFS or OWL for this purpose. However, this is a misapplication of those technologies. It is well-known that the semantics of RDFS and OWL are defined in terms of inference rules, not constraints."

### The formulation

- Abstract: "This document defines a high-level RDF vocabulary for specifying the shape of RDF resources."
- Status of This Document: "It is being submitted to W3C so that it can inform the development of a future W3C Shape specification."
- Section 5.2: with no shape associated to a resource, "there are no implied constraints on that resource."
- Section 7.7: constraints are checked with SPARQL queries, and "If any fails, then the described resource does not satisify the shape."

### Shape references

- Section 6.23: oslc:valueShape links "to resource shape that describes the object resource."
- Section 5.1: an object resource "may itself be described by another shape."

### What this record supports

- It records a shape vocabulary that rejects OWL for constraints and allows shapes to refer to each other without a stated meaning for cycles (area index, concept 2, step 3; concept 3, step 1).
