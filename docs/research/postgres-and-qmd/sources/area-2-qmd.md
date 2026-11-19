# Area 2 Index: qmd and Its Components

This index covers assignment A2 of the survey plan. It lists what the 15 records in `sources/area-2/` document about qmd. The records are survey records: they report what each source states, and they form no claims.

## Tool identification

The stakeholder confirmed through the coordinator that qmd is `https://github.com/tobi/qmd`. The repository matches the brief's description of a local search tool for markdown documents (A2-SR-01, A2-SR-02). A web search also found two ports that describe themselves as ports of tobi/qmd: QMD-Py (`https://github.com/chengzhag/qmd-py`, PyPI package `qmd`) and a Rust crate `qmd` on crates.io. It also found an unrelated Python package, `pyqmd`. The stakeholder's confirmation settles the identification, so this survey records none of them.

## State of the art

qmd is a command-line tool, a Node.js library, and an MCP server over one SQLite file (A2-SR-12). It indexes markdown files from folders that the user registers as collections. It answers keyword, vector, and hybrid queries, all on the local machine (A2-SR-02).

**Storage.** All index data sits in one SQLite database, by default `~/.cache/qmd/index.sqlite` (A2-SR-02). Document text is content-addressed: table `content` keys each body by its hash. Table `documents` maps a collection and path to a hash and carries an `active` flag (A2-SR-03). Full-text search uses an FTS5 table with the `porter unicode61` tokenizer. Three SQLite triggers keep that table in step with `documents` (A2-SR-03). Vectors live in a sqlite-vec `vec0` table partitioned by collection, keyed back to content chunks through `vector_rows` (A2-SR-05). Collection configuration lives in a YAML file and is mirrored into table `store_collections` (A2-SR-03, A2-SR-10).

**Pipeline.** `qmd update` scans files and writes text and the FTS index. `qmd embed` cuts each document into chunks of about 900 tokens with 15 percent overlap and embeds them (A2-SR-02). A hybrid query first expands the user query with a fine-tuned local model into typed `lex`, `vec`, and `hyde` lines. Each line goes to one backend: `lex` to BM25, `vec` and `hyde` to vector search. Then reciprocal rank fusion (RRF) merges the ranked lists, a local reranker scores the top 30, and a position-aware blend mixes the two scores (A2-SR-02, A2-SR-08). The default models are EmbeddingGemma 300M, Qwen3-Reranker 0.6B, and a qmd-specific expansion model built on Qwen3 1.7B. All three run in-process through node-llama-cpp (A2-SR-02, A2-SR-15).

**Changed, renamed, and deleted files.** A re-index skips files whose modification time and size match the last scan. It reads a changed file, hashes it, and writes a new content row when the hash differs (A2-SR-04). A vanished or emptied file is soft-deleted: its `documents` row gets `active = 0`. A later cleanup hard-deletes such rows and removes content that no row references (A2-SR-04). No code detects a rename. A renamed file becomes a deactivated old path and a new path, and its content and vectors are reused through the hash (inferred, A2-SR-04). The index changes only when `qmd update` runs; no file watcher exists (A2-SR-04). Results for moved or deleted files fall back to the index copy until the next update (A2-SR-10).

**Provenance below the file level.** Each chunk stores its sequence number and character position (A2-SR-03). A hybrid result carries the best chunk and its character offset, and `qmd get` reads line ranges (A2-SR-02). No table records links between documents, citations, or anchors (A2-SR-03). Processors record which source file produced which generated document (A2-SR-07).

**What typed edges, decisions, and history would need.** The schema has no edge table, no decision table, and no append-only log (A2-SR-03). The nearest extension points are frontmatter metadata and processors. Metadata accepts strings, numbers, booleans, and flat arrays, and rejects nested objects (A2-SR-02, A2-SR-06). So a document can list target names under a key. qmd neither resolves such a value to a document nor checks it (inferred, A2-SR-06). Processors turn non-markdown input into index documents (A2-SR-07). History is not kept: content rows are deleted once no document references them (A2-SR-04). New tables would follow the numbered `PRAGMA user_version` migrations (A2-SR-05). Every statement in this paragraph is read from the schema; no source states a design for edges or history.

### Simplicity facts

| Fact                     | Value                                                                                                                                                                                                                                                              | Records                 |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------- |
| Components               | Node.js 22 or Bun; SQLite through better-sqlite3; FTS5; sqlite-vec 0.1.9; node-llama-cpp; three GGUF models; YAML config                                                                                                                                           | A2-SR-02, -12, -13, -14 |
| Query languages          | Line-typed query documents (`lex`, `vec`, `hyde`, `intent`); a JSON filter tree for metadata; SQL only inside the SQLite file                                                                                                                                      | A2-SR-02, -08           |
| Consistency boundaries   | FTS follows `documents` through triggers in the same database. Vectors are written by a separate `qmd embed` step under a per-index lock. The whole index lags the files until `qmd update` runs. YAML config and `store_collections` are synced by atomic publish | A2-SR-03, -04, -10, -12 |
| Kept in sync             | Files on disk and the index; YAML config and `store_collections`; content and vectors after a change of embedding model                                                                                                                                            | A2-SR-02, -03, -10      |
| Rebuildable derived data | All of the index. The files and the YAML config are the source; the README re-embeds after a model change, and `qmd embed -f` rebuilds vectors                                                                                                                     | A2-SR-02, -03, -10      |
| Release activity         | 17 npm versions from 0.9.0 (2026-02-15) to 2.9.0 (2026-11-18); a three-month gap between 2.8.3 and 2.9.0                                                                                                                                                           | A2-SR-01                |
| Project health           | MIT licence; the owner holds 557 of 809 commits; 17 author names since 2026-08-18; 134 open issues and 130 open pull requests; sqlite-vec is pre-v1 with no stable release since 2026-03-31                                                                        | A2-SR-01, -13           |
| Open source              | qmd, sqlite-vec, node-llama-cpp, better-sqlite3: yes. Qwen3-Reranker: Apache-2.0 tag. qmd expansion model: MIT tag. EmbeddingGemma: Gemma licence tag, gated base model, status not checked                                                                        | A2-SR-01, -13, -14, -15 |

## Hardened concepts

Five concepts went through several recorded rounds. Each step names the formulation, its date, and the criticism that led to the next step. Nearly all criticism comes from the project's own changelog. No independent review of any step was found.

### 1. Fusion of ranked lists (5 steps)

1. Plain RRF over BM25 and vector lists, 2025-12-07 (A2-SR-09, A2-SR-11). Criticism: expanded queries count as much as the user's own words, though "the user's actual words are a more reliable signal" (A2-SR-09).
2. Weighted RRF with weight 2 for the original query, 2025-12-08 (A2-SR-09). Criticism: "Pure RRF can dilute exact matches when expanded queries don't match" (A2-SR-02).
3. Top-rank bonus and position-aware blending with the reranker (A2-SR-02). Date: gap; no changelog entry or commit was traced. Criticism: the weight landed on the first lexical expansion and not on the original evidence (A2-SR-10, #591).
4. Weights assigned by query type, 2026-05-19 (A2-SR-10). Criticism: duplicate expansions each ran a search and counted again in fusion (A2-SR-10, #921).
5. Duplicate expansions dropped before search, 2026-11-17 (A2-SR-10). No later criticism recorded.

### 2. Query expansion (6 steps)

1. Untyped expansion through Ollama, 2025-12-07 (A2-SR-09). Criticism: every variant went to every backend, "sending everything everywhere" (A2-SR-09).
2. Typed expansion (lexical, vector, HyDE) under a JSON grammar, skipped when BM25 is strong, 2025-12-28 (A2-SR-09). Criticism: gap. The changelog states only the benefit of the next step, better handling of proper nouns and technical terms.
3. GRPO-fine-tuned expansion model, 2026-01-28 (A2-SR-09, A2-SR-15). Criticism: the type was lost on the way to the backends, which cost "~4 wasted backend calls per query" (A2-SR-09).
4. Type-routed expansion, 2026-02-15 (A2-SR-09). Criticism: no way to disambiguate an overloaded term (A2-SR-09, 1.1.0 entry, paraphrase).
5. User-written query documents with typed lines, phrases, and negation, 2026-02-20 (A2-SR-08, A2-SR-09). Criticism: ambiguous queries still ranked poorly when the caller knew the meaning (A2-SR-09, 1.1.5).
6. An `intent` line that steers expansion, chunk selection, reranking, and snippets, 2026-03-07 (A2-SR-09). Later change: intent left the expansion prompt again in 2.8.3 (A2-SR-10, line 375, not quoted in the record). Its criticism is a gap in the records.

### 3. Unit and layout of vector storage (5 steps)

1. One vector per document in `vectors_vec`, keyed by hash, 2025-12-07 (A2-SR-11). Criticism: one embedding "averages everything together, matching poorly for specific queries" (A2-SR-09).
2. Chunks of about 900 tokens, keyed by hash and sequence, 2025-12-08 (A2-SR-09, A2-SR-11). Criticism: small collections were "crowded out of the global ANN candidate pool" (A2-SR-10).
3. Exact scan for collections within 20,000 vectors, 2026-08-16 (A2-SR-10). Criticism: the same crowding for larger collections, and a whole-index pre-filter (A2-SR-10).
4. Vectors partitioned by collection, 2026-09-24 in code and 2026-11-17 in release (A2-SR-05, A2-SR-10). Criticism: deletes leave holes that "every brute-force scan still reads" (A2-SR-10).
5. Repack of mostly empty chunks in `qmd cleanup`, 2026-11-17 (A2-SR-10). No later criticism recorded.

### 4. Where collection configuration lives (4 steps)

1. SQLite tables `collections` and `path_contexts`, 2025-12-07 (A2-SR-11). Criticism: "SQLite was overkill for config — you can't share it, and it's opaque" (A2-SR-09).
2. YAML file `~/.config/qmd/index.yml`, 2025-12-13 (A2-SR-09). Criticism: gap. The code gives only the aim of the next step: to make "the DB self-contained" (A2-SR-03).
3. YAML plus a mirror in `store_collections`, commit 839d774 of 2026-03-10 (A2-SR-03, A2-SR-01). Criticism: concurrent writers could lose edits or leave a database-only change, and an interrupted rename lost its evidence (A2-SR-10).
4. Serialised, atomic config publishing with pending-rename markers, 2026-11-17 (A2-SR-10). No later criticism recorded.

### 5. Model runtime (3 steps)

1. Ollama over HTTP, 2025-12-07 (A2-SR-09, A2-SR-11). Criticism: Ollama "adds convenience but also a running server dependency" (A2-SR-09).
2. In-process GGUF models through node-llama-cpp, 2025-12-28 (A2-SR-09). Criticism: gap; no recorded reason for the next step.
3. Optional remote embedding and remote reranking next to local models, 2026-11-17 (A2-SR-10). No later criticism recorded.

## Gaps

- No source outside the tobi/qmd repository describes qmd's internals. All design reasons come from the project's own changelog and comments. Third-party pages found by search were skill wrappers and listings, so they were not recorded.
- The sources conflict on whether sqlite-vec `vec0` search is exhaustive. The changelog says "ANN candidate pool" in 2.8.3 and "brute-force scan" in 2.9.0 (A2-SR-10). The sqlite-vec README and KNN page say neither (A2-SR-13).
- The README contradicts itself on the number of expansions (two or one) and lists two tables the code drops (A2-SR-02, A2-SR-03).
- Missing dates: the top-rank bonus and the position-aware blend have no traced date. Changelog sections 0.1.0 to 0.8.0, 1.1.0, 2.5.0, and 2.6.3 have no npm version, and most have no tag (A2-SR-01).
- Missing criticism: concept 2 step 2, concept 2 step 6, concept 4 step 2, and concept 5 step 2.
- No source states how qmd would hold typed edges, decisions, or append-only history. The survey states this only as inference from the schema (A2-SR-03, A2-SR-06).
- The licence status of EmbeddingGemma was not checked against the OSI list, and no model card was read (A2-SR-15).
- Contributor counts differ: the GitHub API returns 100 and git log 105 author names. Neither count merges name variants (A2-SR-01).
- The graph-and-embeddings survey holds no record on qmd, sqlite-vec, FTS5, or RRF. So this index cites none of its records.
- Failed searches: the sqlite-vec KNN page has no statement on index type. A grep for a file watcher in `src/` found none. No GitHub release exists for v0.9.0, v1.0.0, or v2.5.0.
