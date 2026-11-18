# A2-SR-14: FalkorDB repository, release 6.0.0, licence, and the RedisGraph end of life

```json
{
  "source_identity": "GitHub repository FalkorDB/FalkorDB, https://github.com/FalkorDB/FalkorDB: README.md, LICENSE.txt, .gitmodules, release notes of v6.0.0, releases list; README of https://github.com/RedisGraph/RedisGraph",
  "author_or_issuing_body": "FalkorDB Ltd. and contributors; Redis Ltd. for the RedisGraph README",
  "publisher": "GitHub",
  "publication_date": "2026-09-29T07:11:06Z",
  "relevant_event_date": "2023-07-20",
  "source_family": "Primary: source repository and release notes of FalkorDB, and the repository of its predecessor RedisGraph. Same vendor lineage as A2-SR-13.",
  "precise_evidence_location": "FalkorDB README introduction and sections 'OpenCypher Support' and 'LOADING FALKORDB INTO REDIS'; first lines of LICENSE.txt; .gitmodules entry deps/RediSearch; release v6.0.0 notes, sections opening and 'What's different from 4.20.7'; GitHub releases list; RedisGraph README header",
  "method": "Repository files and release notes read directly; release dates and repository metadata from the GitHub API.",
  "limitations": "publication_date is the date of release v6.0.0; relevant_event_date is the creation date of the FalkorDB repository. The repository is not marked as a GitHub fork of RedisGraph, so the lineage rests on the RedisGraph README, the shared client libraries named in the FalkorDB README, and the timing, not on a statement by FalkorDB read here. The RedisGraph end-of-life blog post linked from the README was not read.",
  "provenance": "Files downloaded with curl from raw.githubusercontent.com on 2026-11-18. Release notes and releases read with gh api repos/FalkorDB/FalkorDB/releases (all pages) on 2026-11-18. Repository metadata: created 2023-07-20, archived false, last push 2026-11-18, 847 open issues and pull requests. RedisGraph metadata: archived false, last push 2025-07-21."
}
```

## Evidence

- README, about FalkorDB: "is the first **queryable [Property Graph](https://github.com/opencypher/openCypher/blob/master/docs/property-graph-model.adoc) database to leverage sparse matrices** for representing the [adjacency matrix](https://en.wikipedia.org/wiki/Adjacency_matrix) in graphs and [linear algebra](https://en.wikipedia.org/wiki/Adjacency_matrix) for querying." The README opens the sentence with an emoji and a link named FalkorDB.
- README: "**OpenCypher Support:** Compatible with [OpenCypher](ttps://github.com/opencypher/openCypher/blob/master/docs/property-graph-model.adoc) query language, including proprietary extensions for advanced querying capabilities."
- README: "FalkorDB is hosted by [Redis](https://redis.io), so you'll first have to load it as a Module to a Redis server."
- .gitmodules: the submodule deps/RediSearch points to https://github.com/FalkorDB/RediSearch.git.
- LICENSE.txt, first line: "Server Side Public License"
- Release v6.0.0: "FalkorDB 6.0 is the first release of the new FalkorDB engine, written in Rust. It replaces the C engine that shipped in every 4.x release."
- Release v6.0.0: "**Don't mix 4.x and 6.0 in the same primary/replica set.**"
- Release v6.0.0: "**Replicas apply changes, they don't re-run queries.**"
- Releases between 2024-11-18 and 2026-11-18: 78. Five of them are on the 6.0 line (v6.0.0 of 2026-09-29 to v6.0.4 of 2026-11-05). The 4.x line still gets releases; the latest is v4.22.4 of 2026-11-12.
- RedisGraph README: "RedisGraph is no longer maintained."
- What the source shows: FalkorDB runs as a Redis module, takes openCypher with extensions, keeps vector and full-text indexes in a RediSearch fork, replaced its engine in September 2026, and maintains two release lines.
- What the source does not show: whether SSPL counts as open source; this record states the licence name only.
