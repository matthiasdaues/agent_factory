# A2-SR-09: qmd CHANGELOG.md, releases 0.1.0 to 1.1.6

```json
{
  "source_identity": "CHANGELOG.md of tobi/qmd at commit aa247d0ee2e5dc3b83e1270714c0f06ca94e2514, sections 0.1.0 (2025-12-07) to 1.1.6 (2026-03-09)",
  "author_or_issuing_body": "Tobi Lütke and contributors",
  "publisher": "GitHub (tobi/qmd)",
  "publication_date": "2026-11-17T00:00:00Z",
  "relevant_event_date": "2025-12-07",
  "source_family": "Primary: release notes of tobi/qmd, written by the project about its own changes. Same lineage as A2-SR-01 to A2-SR-08 and A2-SR-10 to A2-SR-12.",
  "precise_evidence_location": "CHANGELOG.md lines 1005-1050 (1.1.5, 1.1.6), 1112-1122 (1.1.0), 1234-1272 (0.9.0), 1275-1290 (0.8.0), 1310-1314 (0.7.0), 1343-1365 (0.6.0), 1367-1395 (0.5.0), 1397-1416 (0.4.0), 1418-1437 (0.3.0), 1439-1449 (0.2.0), 1451-1466 (0.1.0)",
  "method": "Read the sections in the clone at the stated commit.",
  "limitations": "The changelog states the project's own reasons for each change; no independent review of those reasons was found. Sections 0.1.0 to 0.8.0 and 1.1.0 have no git tag, GitHub release, or npm version (A2-SR-01), so their dates rest on the changelog alone. Retrospective sections may have been written after the fact. Quality claims such as noticeably better expansions were not checked.",
  "provenance": "Clone of https://github.com/tobi/qmd.git on 2026-11-18 at aa247d0ee2e5dc3b83e1270714c0f06ca94e2514. Re-verify with git show aa247d0ee2e5dc3b83e1270714c0f06ca94e2514:CHANGELOG.md."
}
```

## Evidence

- 0.1.0, lines 1458-1463: "Search: SQLite FTS5 with BM25 ranking. Chose SQLite over Elasticsearch because QMD is a personal tool — single binary, no server dependencies." and "Search: Reciprocal Rank Fusion to combine BM25 and vector results. RRF is parameter-free and handles missing signals gracefully."
- 0.2.0, lines 1448-1449: "Search: weighted RRF — original query gets 2x weight relative to expanded queries since the user's actual words are a more reliable signal."
- 0.3.0, lines 1420-1423: "A 5000-word document about many topics gets a single embedding that averages everything together, matching poorly for specific queries. Chunking produces one embedding per ~900-token section with focused semantic signal."
- 0.4.0, lines 1399-1400: "MCP server for AI agent integration. Without it, agents had to shell out to `qmd search` and parse CLI output."
- 0.5.0, lines 1369-1371: "Collections and contexts moved from SQLite tables to YAML at `~/.config/qmd/index.yml`. SQLite was overkill for config — you can't share it, and it's opaque. YAML is human-readable and version-controllable."
- 0.6.0, lines 1345-1348: "Replaced Ollama HTTP API with node-llama-cpp for all LLM operations. Ollama adds convenience but also a running server dependency."
- 0.6.0, lines 1352-1355: expansion becomes typed (lexical, vector, HyDE) "so each routes to the right backend instead of sending everything everywhere." Line 1358: "Search: conditional query expansion — when BM25 returns strong results, the expensive LLM expansion is skipped entirely."
- 0.8.0, lines 1277-1278: "Fine-tuned query expansion model trained with GRPO replaces the stock Qwen3 0.6B."
- 0.9.0, lines 1245-1247: "Search: type-routed query expansion preserves lex/vec/hyde type info and routes to the appropriate backend. Eliminates ~4 wasted backend calls per query (10.0 → 6.0 calls, 1278ms → 549ms)."
- 0.9.0, lines 1262-1265, whole entry: "BM25 score normalization — formula was inverted (`1/(1+|x|)` instead of `|x|/(1+|x|)`), so strong matches scored *lowest*. Broke `--min-score` filtering and made the "strong signal" short-circuit dead code. #76 (thanks @dgilperez)"
- 0.9.0, line 1271: "Reactivate deactivated documents on re-index instead of creating duplicates."
- 1.1.0, line 1114: query documents with typed lex, vec, and hyde lines; a plain query is still auto-expanded.
- 1.1.5, lines 1022-1025: an intent parameter "steers all five pipeline stages — expansion, strong-signal bypass, chunk selection, reranking, and snippet extraction — without searching on its own."
- 1.1.6, lines 1007-1009: "QMD can now be used as a library."
- Shows: the order of formulations of the search pipeline, the config store, and the model runtime, with the project's stated reason for each change. Does not show: measured retrieval quality before and after a change, except the call counts and latency at 0.9.0.
