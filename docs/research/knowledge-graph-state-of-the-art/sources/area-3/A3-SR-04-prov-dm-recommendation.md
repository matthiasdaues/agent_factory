# A3-SR-04 — PROV-DM: The PROV Data Model (W3C Recommendation, 2013)

```json
{
  "source_identity": "PROV-DM: The PROV Data Model, W3C Recommendation, 30 April 2013, https://www.w3.org/TR/prov-dm/",
  "author_or_issuing_body": "W3C Provenance Working Group",
  "publisher": "World Wide Web Consortium (W3C)",
  "publication_date": "2013-04-30T00:00:00Z",
  "relevant_event_date": "2013-04-30",
  "source_family": "Primary. W3C Recommendation, the normative conceptual model of the PROV family. Later versions of the same text are not independent copies.",
  "precise_evidence_location": "Abstract; Section 2.1 and Table 2 (core structures and relation names); Appendix B (change log: B.1 since Proposed Recommendation, B.2 since Candidate Recommendation, B.3 since Last Call).",
  "method": "The Working Group specifies the model and records its own changes by issue number.",
  "limitations": "Two extractions covered the whole page (characters 0 to 100,000, then 100,000 to the end of 155,327). Quotes and issue numbers come from model-assisted extractions and were not compared with the raw HTML. The change log lists the changes and issue numbers but not the argument behind them; the argument sits in a separate 'Responses to Public Comments' document that this record did not read. Neither extraction found a mention of the Open Provenance Model.",
  "provenance": "Fetched 2026-11-17 with the WebFetch tool from the URL above. Re-verify by opening Appendix B of the page and following the link to the public-comment responses."
}
```

## Evidence

- Abstract: "PROV-DM is the conceptual data model that forms a basis for the W3C provenance (PROV) family of specifications." The model has six components and separates core from extended structures.
- Section 2.1, Table 2: general concepts map to relation names: Generation to `wasGeneratedBy`, Usage to `used`, Communication to `wasInformedBy`, Derivation to `wasDerivedFrom`, Attribution to `wasAttributedTo`, Association to `wasAssociatedWith`, Delegation to `actedOnBehalfOf`.
- Section 2.1: "Names of relations have a verbal form in the past tense to express what happened in the past."
- Appendix B.3 (changes since Last Call), as reported by the extraction: ISSUE-506 changed "author" to "contributor"; ISSUE-525 made clear that Membership, Alternate and Specialization are not Influence; the feature-at-risk "Mention" moved to a separate note, prov-mention. Appendix B.3 points to "Responses to Public Comments on the Last Call Working Draft" for the reasoning.

## What the source shows

It shows the final 2013 formulation of the model and that the Working Group changed it after public comment, with issue numbers.

## What the source does not show

It does not show the reasoning behind each change, who raised each issue, or how the model differs from OPM. It does not cover post-2013 criticism.

## Failed searches and gaps

The public-comment responses document was not fetched.
