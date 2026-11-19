# A2-SR-14: node-llama-cpp and better-sqlite3 repository metadata

```json
{
  "source_identity": "GitHub repositories withcatai/node-llama-cpp and WiseLibs/better-sqlite3, REST API endpoints repos/<repo> and repos/<repo>/releases",
  "author_or_issuing_body": "withcatai (Gilad S.) and contributors; WiseLibs and contributors",
  "publisher": "GitHub",
  "publication_date": "2026-11-18T00:00:00Z",
  "relevant_event_date": "2026-11-14",
  "source_family": "Primary: repository and release metadata of two qmd dependencies. Independent of the tobi/qmd lineage.",
  "precise_evidence_location": "API fields description, license, pushed_at, open_issues_count, archived; releases tag_name and published_at (latest eight each)",
  "method": "Read with gh api on 2026-11-18.",
  "limitations": "Metadata only; no source or documentation of either project was read. publication_date is the read date. relevant_event_date is the better-sqlite3 13.2.0 release that qmd pins.",
  "provenance": "gh api repos/withcatai/node-llama-cpp and gh api repos/WiseLibs/better-sqlite3 on 2026-11-18."
}
```

## Evidence

- node-llama-cpp description: "Run AI models locally on your machine with node.js bindings for llama.cpp. Enforce a JSON schema on the model output on the generation level"
- node-llama-cpp: license MIT; archived false; pushed_at 2026-11-18; 48 open issues; eight releases from v3.19.1 (2026-07-20) to v3.22.3 (2026-11-05). qmd pins 3.22.3.
- better-sqlite3 description: "The fastest and simplest library for SQLite3 in Node.js."
- better-sqlite3: license MIT; archived false; pushed_at 2026-11-14; 74 open issues; releases from v12.12.0 (2026-07-15) to v13.2.0 (2026-11-14). qmd pins 13.2.0.
- Shows: both runtime dependencies are open source and had releases in the last two weeks. Does not show: their quality or their fit with qmd beyond the pinned versions.
