# A2-SR-12: Memgraph release notes, GitHub releases and licence

```json
{
  "source_identity": "Memgraph release notes, https://memgraph.com/docs/release-notes; GitHub releases and LICENSE of https://github.com/memgraph/memgraph",
  "author_or_issuing_body": "Memgraph Ltd.",
  "publisher": "Memgraph Ltd., memgraph.com; GitHub",
  "publication_date": "2026-10-21T11:05:17Z",
  "relevant_event_date": "2024-11-27",
  "source_family": "Primary: vendor release record and source repository of Memgraph. Same lineage as A2-SR-11.",
  "precise_evidence_location": "Release notes sections Memgraph v2.22.0 (Nov 27, 2024), v3.0.0 (Jan 29th, 2025), v3.8.0 (February 11th, 2026) and v3.11.0 (June 17th, 2026); GitHub releases list; LICENSE file on master",
  "method": "Release notes written by the vendor; release dates and licence from the GitHub API and the repository.",
  "limitations": "publication_date is the date of the latest GitHub release, v3.14.0. relevant_event_date is the first vector search release. Release notes say what changed, rarely why; reasons are inferred by nobody here. The section a note belongs to was found by the nearest preceding version heading in the converted text.",
  "provenance": "Release notes downloaded with curl on 2026-11-18 and converted from HTML to text. GitHub releases read with gh api repos/memgraph/memgraph/releases (all pages) on 2026-11-18. LICENSE downloaded from https://raw.githubusercontent.com/memgraph/memgraph/master/LICENSE. Repository metadata: archived false, last push 2026-11-18, 986 open issues and pull requests."
}
```

## Evidence

- v2.22.0 (Nov 27, 2024): "The first version of the vector search feature was added. To enable and configure the feature, use --experimental-enabled=vector-search and --experimental-config flags."
- v3.0.0 (Jan 29th, 2025): "Vector search has been removed from the experimental feature set. The API has changed and it’s stable now."
- v3.8.0 (February 11th, 2026): "Optimized vector property storage by eliminating data duplication between the property store and vector index. Vector data is now stored only once in the index, significantly reducing memory usage for vector-indexed properties."
- v3.11.0 (June 17th, 2026): "Vector indexes now support multi-label and wildcard filters."
- GitHub releases: 29 releases between 2024-11-18 and 2026-11-18; the latest is v3.14.0 of 2026-10-21. Releases come about once or twice a month.
- LICENSE: "Source code in this repository is variously licensed under the Business Source License 1.1 (BSL), the Memgraph Enterprise License (MEL)."
- What the source shows: the vector index went from experimental to stable in two months, then changed its storage layout in 2026; Memgraph releases often.
- What the source does not show: the reason for the API change in v3.0.0. Whether the Business Source License counts as open source is a licence question this record does not settle.
