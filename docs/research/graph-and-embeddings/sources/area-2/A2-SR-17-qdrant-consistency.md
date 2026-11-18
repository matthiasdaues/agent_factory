# A2-SR-17: Qdrant documentation on point writes and consistency, and Qdrant releases

```json
{
  "source_identity": "Qdrant documentation sources in https://github.com/qdrant/landing_page, master branch: qdrant-landing/content/documentation/manage-data/points.md and qdrant-landing/content/documentation/scaling/consistency-guarantees.md; GitHub releases of https://github.com/qdrant/qdrant",
  "author_or_issuing_body": "Qdrant Solutions GmbH (documentation team)",
  "publisher": "GitHub, repositories qdrant/landing_page and qdrant/qdrant; rendered at qdrant.tech",
  "publication_date": "2026-11-18T00:00:00Z",
  "relevant_event_date": "2026-11-16",
  "source_family": "Primary: vendor documentation and source repository of Qdrant.",
  "precise_evidence_location": "points.md opening of 'Points' and section 'Awaiting Result'; consistency-guarantees.md list of options and section 'Write Ordering'; releases list",
  "method": "Vendor documentation read from its source files; release dates and metadata from the GitHub API.",
  "limitations": "Living documentation; the date is the retrieval date. relevant_event_date is the latest release, v1.20.2. Qdrant is one example of a separate vector store; Milvus and Weaviate were not read. The documentation read here says nothing about transactions that span several requests; a search of the fundamentals FAQ for the word transaction found nothing.",
  "provenance": "Markdown files downloaded with curl from raw.githubusercontent.com/qdrant/landing_page/master on 2026-11-18. Releases read with gh api repos/qdrant/qdrant/releases (all pages) on 2026-11-18. Repository metadata: archived false, last push 2026-11-18, licence Apache-2.0."
}
```

## Evidence

- points.md: "Any point modification operation is asynchronous and takes place in 2 steps."
- points.md: "This response does not mean that the data is available for retrieval yet. This uses a form of eventual consistency."
- points.md: "If the logic of your application requires a guarantee that the vector will be available for searching immediately after the API responds, then use the flag `?wait=true`."
- consistency-guarantees.md: "`weak` _(default)_ ordering does not provide any additional guarantees, so write operations can be freely reordered."
- consistency-guarantees.md: "`strong` ordering serializes all write operations through the permanent leader, which provides strong consistency, but write operations may be unavailable if the leader is down."
- Releases between 2024-11-18 and 2026-11-18: 34. The latest is v1.20.2 of 2026-11-16.
- What the source shows: a write to Qdrant is acknowledged before it is searchable unless the client waits, and ordering across replicas is a per-request option. A graph store beside Qdrant therefore has two separate write paths.
- What the source does not show: any way to commit a Qdrant write and a graph write together.
