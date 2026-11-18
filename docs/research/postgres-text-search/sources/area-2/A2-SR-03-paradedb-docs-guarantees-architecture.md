# A2-SR-03: ParadeDB documentation on guarantees, editions, and architecture at commit c0ffb13

```json
{
  "source_identity": "paradedb/paradedb, docs/concepts/guarantees.mdx, docs/operate/deploy/enterprise.mdx, docs/concepts/architecture.mdx, docs/operate/deploy/self-hosted/extension.mdx, docs/start/load-data.mdx, README.md, and pg_search/Cargo.toml at commit c0ffb135a234efc5e1cf67f68b9ca5c0e6a51723 (2026-11-19 +0530); published at https://www.paradedb.com/docs/concepts/guarantees",
  "author_or_issuing_body": "ParadeDB, Inc.",
  "publisher": "GitHub (source of the docs site paradedb.com/docs)",
  "publication_date": "2026-11-18T19:01:11Z",
  "relevant_event_date": "2026-11-18",
  "source_family": "Primary: vendor documentation and build files in the extension repository. Vendor documentation counts here only for stated features and syntax. Same lineage as A2-SR-04, A2-SR-05, A2-SR-07, A2-SR-18.",
  "precise_evidence_location": "guarantees.mdx sections ACID, Concurrency, Replication Safety; enterprise.mdx Feature Comparison table and footnotes 1 to 3; architecture.mdx sections Custom Index, LSM Tree, Dependencies; extension.mdx line 20; load-data.mdx lines 8 to 15; README section License; pg_search/Cargo.toml [features]",
  "method": "The vendor describes the transaction, replication, and storage behaviour of its index and the split between the Community and Enterprise editions.",
  "limitations": "Vendor documentation; the ACID and MVCC statements are the vendor's claims, not tests. Open issues in A2-SR-06 report behaviour that differs in edge cases. The publication_date is the commit time converted to UTC. The docs do not say how the Community edition writes WAL; the changelog in A2-SR-04 and A2-SR-18 covers that.",
  "provenance": "Sparse shallow clone of https://github.com/paradedb/paradedb on 2026-11-18 (docs folder only) and `gh api` reads of README.md and pg_search/Cargo.toml. Re-verify at the commit above."
}
```

## Evidence

- README: "Built as a Postgres extension, it keeps your application data and search engine in one database with standard SQL and ACID transactions." and "ParadeDB Community is licensed under the GNU Affero General Public License v3.0" (link text kept, link removed). ParadeDB Enterprise is commercially licensed.
- guarantees.mdx, ACID: "All reads and writes go through Postgres’ transaction engine. This means that inserts, updates, and deletes to indexed columns are atomic, consistent, and respect Postgres' isolation levels" (link text kept).
- guarantees.mdx, Correctness vs. Performance: facets can skip visibility checks with `visibility => 'raw'`, so results can be stale by choice.
- guarantees.mdx, Replication Safety: "ParadeDB Community supports logical replication, but not physical replication" and "The ParadeDB index does not get physically replicated and won't be available on other nodes in a high availability setup."
- enterprise.mdx, Feature Comparison: Crash recovery and Point-in-time recovery are marked yes for both editions; High availability and Read replica support are marked no for Community and yes for Enterprise. Footnote 1: "The index reflects the current state of the underlying table at all times, changes to the index are atomic, and queries are transactionally consistent with the table."
- architecture.mdx, Custom Index: "When a table row is inserted or updated, the ParadeDB index is immediately notified. These changes are recorded as part of the current transaction, ensuring that index updates are real-time."
- architecture.mdx, LSM Tree: "Incoming writes are appended to a mutable segment, which buffers rows across statements." The segment is frozen at `mutable_segment_rows`, 1,000 rows by default, and later merged.
- architecture.mdx, Dependencies: pgrx, Tantivy ("the Rust-based full-text and vector search library inspired by Lucene"), and Apache DataFusion.
- README feature list: "Tokenizers & Token Filters" (link text kept). The index uses its own tokenizers, not PostgreSQL text search configurations (my reading of the feature list and architecture page).
- architecture.mdx, Custom Operators: search uses its own operators, such as `|||` for match disjunction and `###` for phrase, beside SQL.
- extension.mdx line 20: "ParadeDB provides prebuilt binaries of our extension for Postgres 15+". pg_search/Cargo.toml defines build features pg15, pg16, pg17, and pg18.
- load-data.mdx: "The easiest way to copy data from another Postgres into ParadeDB is with the `pg_dump` and `pg_restore` utilities." The page does not say how a ParadeDB index itself is dumped.
- Not shown: whether a dump of a ParadeDB database restores its indexes without manual steps, and any measured test of the ACID claim.
