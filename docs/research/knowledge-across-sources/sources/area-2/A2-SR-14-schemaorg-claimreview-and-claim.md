# A2-SR-14: Schema.org, ClaimReview and Claim types

```json
{
  "source_identity": "Schema.org type pages https://schema.org/ClaimReview and https://schema.org/Claim, schema.org release V30.1 (2026-09-16)",
  "author_or_issuing_body": "Schema.org community (steering group and contributors); term proposals in GitHub issues 1061 (ClaimReview) and 1828 (Claim)",
  "publisher": "Schema.org",
  "publication_date": "2026-09-16T00:00:00Z",
  "relevant_event_date": "2026-09-16",
  "source_family": "Primary: the schema.org vocabulary definition itself. A2-SR-15 is Google's profile of the same type; A2-SR-16 is its sibling type.",
  "precise_evidence_location": "ClaimReview page: definition and property table (claimReviewed, itemReviewed, reviewRating, associatedMediaReview); Claim page: definition and properties appearance, firstAppearance",
  "method": "Vocabulary definition maintained through public GitHub issues.",
  "limitations": "The page shows the current release only; the history of each property was not traced through the GitHub issues. Usage figures on the page come from Google's web index and are given as ranges.",
  "provenance": "HTML page fetched with curl on 2026-11-18 and stripped of tags with a local script. Re-verify at the URLs above; the page states the release number."
}
```

## Evidence

- ClaimReview definition: "A fact-checking review of claims made (or reported) in some creative work (referenced via itemReviewed)."
- ClaimReview property: "claimReviewed Text A short summary of the specific claims reviewed in a ClaimReview."
- ClaimReview page header: "Usage: 1K - 10K Domains Based on monthly aggregations from Google's web index. (Google - August 2026)".
- Claim definition: "A Claim in Schema.org represents a specific, factually-oriented claim that could be the itemReviewed in a ClaimReview." and "Variations on well known claims can have their common identity indicated via sameAs links, and summarized with a name."
- Claim properties: "appearance CreativeWork Indicates an occurrence of a Claim in some CreativeWork." and "firstAppearance CreativeWork Indicates the first known occurrence of a Claim in some CreativeWork."
- Claim page: "At this time, Schema.org does not define any types of relationship between claims. This is a natural area for future exploration."
- Shows: what a ClaimReview record holds (a summary of the claim, the reviewed item, a rating) and that a Claim can carry its appearances and first appearance. Does not show: how many fact-checkers fill the Claim properties.
