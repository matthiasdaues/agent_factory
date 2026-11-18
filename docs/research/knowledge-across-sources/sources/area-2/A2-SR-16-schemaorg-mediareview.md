# A2-SR-16: Schema.org, MediaReview type and MediaManipulationRatingEnumeration

```json
{
  "source_identity": "Schema.org pages https://schema.org/MediaReview and https://schema.org/MediaManipulationRatingEnumeration, release V30.1 (2026-09-16); term proposal in GitHub issue 2450",
  "author_or_issuing_body": "Schema.org community; the term was developed with the Duke Reporters' Lab (A2-SR-17)",
  "publisher": "Schema.org",
  "publication_date": "2026-09-16T00:00:00Z",
  "relevant_event_date": "2026-09-16",
  "source_family": "Primary: the schema.org vocabulary definition. A2-SR-17 is the developer's account of the same work.",
  "precise_evidence_location": "MediaReview page: definition, status note, properties mediaAuthenticityCategory, originalMediaContextDescription, originalMediaLink, associatedClaimReview; enumeration page: definition and members",
  "method": "Vocabulary definition maintained through public GitHub issues.",
  "limitations": "Current release only. The page calls the definition a work in progress, so the field list may change.",
  "provenance": "HTML page fetched with curl on 2026-11-18 and stripped of tags with a local script. Re-verify at the URLs above."
}
```

## Evidence

- Definition: "A MediaReview is a more specialized form of Review dedicated to the evaluation of media content online, typically in the context of fact-checking and misinformation."
- Status note: "This definition is a work in progress." and "best practices for the relationship between MediaReview and ClaimReview markup have not yet been finalized."
- Property: "mediaAuthenticityCategory MediaManipulationRatingEnumeration Indicates a MediaManipulationRatingEnumeration classification of a media object (in the context of how it was published or shared)."
- Property: "originalMediaLink MediaObject or URL or WebPage Link to the page containing an original version of the content".
- Enumeration members as listed: "DecontextualizedContent EditedOrCroppedContent OriginalMediaContent SatireOrParodyContent StagedContent TransformedContent".
- Enumeration page: "Note that the application of these codes is with regard to a piece of media shared or published in a particular context."
- Shows: the fields that record a fact-check of an image or video, including a link to the original. Does not show: adoption; the page header reports "Usage: < 1K Domains".
