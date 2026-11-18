# A2-SR-19: Schema.org, correction property and CorrectionComment type

```json
{
  "source_identity": "Schema.org pages https://schema.org/correction and https://schema.org/CorrectionComment, release V30.1 (2026-09-16); term proposal in GitHub issue 1950",
  "author_or_issuing_body": "Schema.org community, based on work by The Trust Project",
  "publisher": "Schema.org",
  "publication_date": "2026-09-16T00:00:00Z",
  "relevant_event_date": "2026-09-16",
  "source_family": "Primary: the schema.org vocabulary definition.",
  "precise_evidence_location": "correction page: definition, value types, acknowledgement; CorrectionComment page: definition",
  "method": "Vocabulary definition maintained through public GitHub issues.",
  "limitations": "Current release only. The Trust Project's own documentation was not read. The page reports usage below 1,000 domains.",
  "provenance": "HTML page fetched with curl on 2026-11-18 and stripped of tags with a local script. Re-verify at the URLs above."
}
```

## Evidence

- correction: "Indicates a correction to a CreativeWork , either via a CorrectionComment , textually or in another document." The spaces before the commas come from the page markup.
- correction: "This term and its definition is based upon the work of The Trust Project ."
- CorrectionComment: "A comment that corrects CreativeWork ."
- correction page header: "Usage: < 1K Domains".
- Shows: the one schema.org field for a correction to a news article, with no field for its kind or severity. Does not show: how news sites use it, or any link from a correction to the ClaimReview of the corrected claim.
