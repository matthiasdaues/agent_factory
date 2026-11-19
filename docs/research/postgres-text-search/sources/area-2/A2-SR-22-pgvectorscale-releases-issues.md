# A2-SR-22: pgvectorscale release notes and issues #109, #110, #257, #281

```json
{
  "source_identity": "timescale/pgvectorscale GitHub releases 0.0.1-dev.1 to 0.9.1, with release notes of 0.7.0, 0.8.0, 0.9.0, and 0.9.1; issues #109, #110, #257, and #281; https://github.com/timescale/pgvectorscale/releases and https://github.com/timescale/pgvectorscale/issues",
  "author_or_issuing_body": "Tiger Data maintainers (release notes, issue replies); issue reporters, who are users outside the maintainer team",
  "publisher": "GitHub",
  "publication_date": "2026-09-04T12:19:57Z",
  "relevant_event_date": "2026-09-04",
  "source_family": "Primary: release notes from the maintainers and issue threads from users and maintainers. Release notes share the lineage of A2-SR-20 and A2-SR-21; the issue reports come from independent users.",
  "precise_evidence_location": "Release notes: 0.9.1 (sections Security hardening and Behavior changes), 0.9.0 (What's Changed), 0.8.0 (opening list), 0.7.0 (first item). Issue #257 body and state. Issue #281 title, environment line, and first paragraph. Issue #109 comment of 2024-07-15T01:02:03Z. Issue #110 last comment. Release dates, contributor count, and open-item count from the GitHub API.",
  "method": "Maintainers describe changes per release; users report problems and requests. Counts come from the GitHub API.",
  "limitations": "publication_date is the 0.9.1 release, the latest. Issue searches used the GitHub search API with the keywords replication, replica, standby, pg_dump, WAL, crash, rollback, restore, and filter; reports with other words may be missing. The searches for replication, replica, standby, pg_dump, WAL, and rollback in titles found no issue. The contributor count is the API count and may include bots. Issue #281 is a user's claim about a port that is not merged.",
  "provenance": "Fetched on 2026-11-19 with `gh api repos/timescale/pgvectorscale/releases`, `gh api repos/timescale/pgvectorscale/releases/tags/<tag>`, `gh api repos/timescale/pgvectorscale/issues/<n>`, `.../issues/<n>/comments`, `gh api repos/timescale/pgvectorscale/contributors`, and `gh api -X GET search/issues`. Re-verify at the URLs above."
}
```

## Evidence

The quotes are copied from the API responses. They are the source's own words, not a fetch-tool summary.

- Release activity: 13 tagged releases from 0.0.1-dev.1 (2023-09-15) to 0.9.1 (2026-09-04). Seven fall between 2024-11-18 and 2026-11-18: 0.5.1 (2024-11-19), 0.6.0 (2025-02-28), 0.7.0 (2025-03-21), 0.7.1 (2025-04-22), 0.8.0 (2025-07-02), 0.9.0 (2025-11-04), and 0.9.1 (2026-09-04). The last commit on main is dated 2026-10-14. The API counts 15 contributors and 20 open issues and pull requests.
- 0.7.0, label filtering: "Support for Filtered DiskANN, as described in the updated README.md!" (link markup removed).
- 0.8.0, stability: "This release fixes a number of major stability issues:" followed by "Fix for issue #193: crash on concurrent insertions" and "Fix for issue #238: crash when scanning index with NULL value".
- 0.9.0, versions: "Added support for PG18" and "Removed support for PG13".
- 0.9.1, security: "Together these could let attacker-controlled bytes reach native DiskANN code paths and cause a backend crash, memory disclosure, or out-of-bounds write." Behaviour change: "Columns without a valid `vector(N)` typmod can no longer be indexed with DiskANN." Upgrade: "run `ALTER EXTENSION vectorscale UPDATE TO '0.9.1'`". Some old indexes "must be dropped and recreated; `REINDEX` cannot repair them."
- Issue #257, opened 2025-11-15, closed 2026-02-26 with state reason "not_planned": "Right now you can only efficiently check logical OR and there are common use cases for wanting logical AND." Its title is "Conjunctive overlap: Ability to combine label overlap conditions".
- Issue #281, opened 2026-08-25 and open on 2026-11-19, titled "PostgreSQL 19 support: 5 API changes, 6 latent double-locks that PG19 turns into backend aborts, and 2 planner findings". The reporter writes: "I have a working port of pgvectorscale to PostgreSQL 19 and I would like to contribute it."
- Issues #109 and #110, 2024: an index scan with post-filtering returned too few rows. A reporter found "ok, so the 51 was just `1 + num_neighbors`, or at least the default value of 50." A maintainer closed #110 with "The fix to this has been released in 0.3.0".
- Not shown: any issue on replication, standbys, `pg_dump`, or rollback. No release note mentions WAL.
