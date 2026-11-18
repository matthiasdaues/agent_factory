# A2-SR-15: Google Search Central, Fact Check (ClaimReview) structured data

```json
{
  "source_identity": "Google Search Central documentation, 'Fact check (ClaimReview) structured data', https://developers.google.com/search/docs/appearance/structured-data/factcheck (last updated 2026-09-08)",
  "author_or_issuing_body": "Google",
  "publisher": "Google (Search Central documentation)",
  "publication_date": "2026-09-08T00:00:00Z",
  "relevant_event_date": "2026-09-08",
  "source_family": "Primary: Google's own documentation of how it consumes ClaimReview. Profiles the schema.org type in A2-SR-14.",
  "precise_evidence_location": "Page introduction (phase-out notice); section Structured data type definitions: ClaimReview required properties (claimReviewed, reviewRating, url), recommended properties (author, itemReviewed), backwards compatibility note",
  "method": "Vendor documentation of supported markup.",
  "limitations": "Vendor documentation describes what Google reads, not what fact-checkers publish. The date of the phase-out notice is not given on the page.",
  "provenance": "HTML page fetched with curl on 2026-11-18 and stripped of tags with a local script. Re-verify at the URL above."
}
```

## Evidence

- Introduction: "We're phasing out support for ClaimReview markup in Google Search. However, this markup remains supported by the Factcheck Explorer Tool."
- Required property reviewRating: "Different fact-checking projects have a variety of rating schemes which can have subtle differences, particularly for intermediate values. It is important to document such rating schemes to clarify the meaning of the numeric ratings."
- Required property claimReviewed: "Don't include the rating in the claimReviewed field. Instead, specify the rating in the reviewRating field."
- Recommended property author: "The publisher of the fact check article, not the publisher of the claim."
- Backwards compatibility: "Upon the initial launch of fact check, Google Search recommended CreativeWork as the itemReviewed ." The current profile recommends Claim.
- Shows: the fields Google requires, that ratings are not standardised across fact-checkers, and that Google Search is withdrawing the display of ClaimReview while Fact Check Explorer keeps it. Does not show: when the phase-out started or why.
