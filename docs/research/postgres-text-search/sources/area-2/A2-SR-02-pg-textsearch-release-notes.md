# A2-SR-02: pg_textsearch release notes v0.0.4 to v1.5.1

```json
{
  "source_identity": "timescale/pg_textsearch GitHub releases, v0.0.1 (2025-10-14) to v1.5.1 (2026-10-02); https://github.com/timescale/pg_textsearch/releases",
  "author_or_issuing_body": "Tiger Data (formerly Timescale), pg_textsearch maintainers",
  "publisher": "GitHub",
  "publication_date": "2026-05-29T20:42:07Z",
  "relevant_event_date": "2026-05-12",
  "source_family": "Primary: release notes of the extension repository. Same lineage as A2-SR-01 and A2-SR-17.",
  "precise_evidence_location": "Release bodies of v0.0.4 (2025-11-20), v0.6.1 (2026-03-12), v1.0.0 (2026-03-27), v1.2.0 (2026-05-12), v1.3.0 (2026-05-29); release list and repository metadata from the GitHub API",
  "method": "Maintainers' release notes; counts of releases, commits, and contributors from the GitHub API.",
  "limitations": "Release notes are the maintainers' own account. publication_date is the v1.3.0 note and relevant_event_date the v1.2.0 note, the two notes on the WAL redesign; the other notes carry their own dates in the location field. The v1.2.0 custom WAL design is described only in the v1.3.0 note; its code was not read. Counts were taken on 2026-11-18 and change over time.",
  "provenance": "Fetched with `gh api repos/timescale/pg_textsearch/releases/tags/<tag>`, `gh api repos/timescale/pg_textsearch/releases`, `/commits?since=2024-11-18T00:00:00Z`, `/contributors`, and `gh api repos/timescale/pg_textsearch` on 2026-11-18. Re-verify at the URL above."
}
```

## Evidence

- v0.0.4 release note (2025-11-20): "Memtable-based architecture with shared memory storage" and "Crash recovery via document ID tracking". The same note says: "This is prerelease software and should not be used in production."
- v0.6.1 release note (2026-03-12): "**Fix crash on ROLLBACK after error in transaction block** (#279)" and "**Add transaction abort test suite** — 8 scenarios covering ROLLBACK, SAVEPOINT, and error recovery with and without BM25 indexes." It also lists "**Add physical and logical replication tests** (#263)".
- v1.0.0 (2026-03-27) is the first generally available release. Its change list includes a fix for a crash-recovery failure, pull request #292 for issue #291 (paraphrase of the change list).
- v1.2.0 release note (2026-05-12): "This release introduces proper support for physical replication, which was essentially broken in previous releases, along with correctness fixes for update-heavy workloads."
- v1.3.0 release note (2026-05-29): "v1.2.0 had introduced custom WAL entries to fix an issue with physical replication keep the memtable on the replica in sync with the primary). These however are not compatible with the stateless WAL redo used in the systems mentioned earlier. v1.3.0 replaces the shared-memory memtable with a paged version plus a shared-memory cache." The systems named earlier in the note are AWS Aurora, Google AlloyDB, Neon, and Microsoft HorizonDB. The unbalanced bracket is in the source.
- Release activity: 23 releases between 2025-10-14 and 2026-10-02, none a release candidate; 364 commits since 2024-11-18; 17 contributors; repository created 2025-07-06 (GitHub API, 2026-11-18).
- Not shown: any independent test of replication or crash safety, and pg_dump behaviour.
