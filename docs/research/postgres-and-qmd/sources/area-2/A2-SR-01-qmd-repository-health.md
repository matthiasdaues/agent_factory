# A2-SR-01: tobi/qmd repository metadata and git history

```json
{
  "source_identity": "GitHub repository tobi/qmd, https://github.com/tobi/qmd, REST API endpoints repos/tobi/qmd, repos/tobi/qmd/releases, repos/tobi/qmd/contributors, search/issues; git history of a clone at commit aa247d0ee2e5dc3b83e1270714c0f06ca94e2514",
  "author_or_issuing_body": "Tobi Lütke (repository owner) and contributors",
  "publisher": "GitHub",
  "publication_date": "2026-11-18T00:00:00Z",
  "relevant_event_date": "2025-12-07",
  "source_family": "Primary: repository metadata and git history of tobi/qmd. Same lineage as A2-SR-02 to A2-SR-12, which are files of this repository.",
  "precise_evidence_location": "API fields description, license, created_at, pushed_at, archived, open_issues_count; release list tag_name and published_at; git log authors and commit months; git tag dates; npm view @tobilu/qmd versions",
  "method": "Read the API responses with gh api and the clone with git log, git tag, and git shortlog-style counts on 2026-11-18. Read npm registry versions with npm view.",
  "limitations": "Snapshot on 2026-11-18; counts change daily. publication_date is the read date, not a publication date. Contributor counts differ by method: the API returned 100 entries on one page with no second page, and git log shows 105 distinct author names, which include several spellings of the owner's name. Star and fork counts are popularity, not health, and are recorded only as context. Issue and pull request counts come from the GitHub search API and were not checked by hand.",
  "provenance": "Cloned with git clone https://github.com/tobi/qmd.git on 2026-11-18; HEAD aa247d0ee2e5dc3b83e1270714c0f06ca94e2514 (2026-11-17 22:37:06 -0500, tag v2.9.0). Re-verify with gh api repos/tobi/qmd and git log at that commit."
}
```

## Evidence

- API field description: "mini cli search engine for your docs, knowledge bases, meeting notes, whatever. Tracking current sota approaches while being all local"
- API fields: license MIT; created_at 2025-12-08T14:22:57Z; pushed_at 2026-11-18T03:45:15Z; archived false; open_issues_count 264 (issues and pull requests together).
- Search API counts on 2026-11-18: 134 open issues, 130 open pull requests, 21 pull requests merged since 2026-08-18, 9 issues closed since 2026-08-18.
- First commit 39193ea, 2025-12-07, message "Initial commit: QMD - Quick Markdown Search". The tool was first named Quick Markdown Search; package.json now names it Query Markup Documents (A2-SR-02).
- Commits per month (git log, author date): 2025-12: 98, 2026-01: 70, 2026-02: 118, 2026-03: 104, 2026-04: 73, 2026-05: 82, 2026-06: 37, 2026-07: 1, 2026-08: 92, 2026-09: 94, 2026-10: 15, 2026-11: 25.
- Commit share: 809 commits in total. The owner's three name spellings hold 557 commits; the next author holds 60; most other authors hold 1 to 13. Since 2026-08-18, 17 distinct author names committed.
- GitHub releases: v1.0.5 to v2.9.0, 15 entries, latest v2.9.0 on 2026-11-18T03:48:03Z, previous v2.8.3 on 2026-08-16. npm versions of @tobilu/qmd: 0.9.0 to 2.9.0, 17 versions. CHANGELOG.md has sections 0.1.0 to 0.8.0, 1.1.0, 2.5.0 and 2.6.3 with no npm version (A2-SR-09, A2-SR-10).
- Shows: activity, release cadence, licence, ownership concentration. Does not show: maintainer response times, test pass rates, or adoption.
