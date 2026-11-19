# Story A: The Store And Its Tests

## Goal

Show that one PostgreSQL server with pgvector, `pg_trgm`, and `unaccent` holds the schema of the design position and passes its nine pilot tests, or show which test fails.

## Why this is a candidate

The design position chose plain PostgreSQL for the fewest moving parts. The postgres-and-qmd and postgres-text-search surveys found no source for several behaviours the design relies on: a transaction finds its own new rows through HNSW and GIN, append-only holds against `TRUNCATE`, and events survive a listener restart. The surveys mark these as inferred. This story tests them.

## What to build

- A container with PostgreSQL 18 and pgvector.
- `schema.sql`: `node`, `edge_type`, `edge`, `embedding`, and `outbox` as the design position describes; the type triggers on `edge` and `node`; append-only rules for edges and decisions; an application role without update, delete, or truncate rights; a generated `tsvector` per node language; GIN, trigram, and HNSW indexes; and SQL functions for the fused search and for search-then-traverse.
- `checks.py`: one check per pilot test, run against the container, printing PASS or FAIL with the evidence.

## Definition of done

1. `docker compose up -d` starts the database on port 55432, and `schema.sql` loads without error twice in a row on a fresh volume.
2. `uv run --script checks.py` runs all nine checks and prints one line per test: its number, PASS or FAIL, and what it observed.
3. Test 1: inside one transaction, a row inserted earlier is found by the HNSW branch and by the GIN branch of the fused search, and by search-then-traverse. The check also lowers `hnsw.ef_search` and reports whether the new row drops out.
4. Test 2: after `ROLLBACK`, neither branch finds the row.
5. Test 3: the trigger rejects a wrong-kind edge at insert, and rejects a change of a node's kind that would break an existing edge.
6. Test 4: as the application role, `UPDATE`, `DELETE`, and `TRUNCATE` on a confirmed edge or a decision fail.
7. Test 5: a listener gets an outbox event for each committed idea and none for a rolled-back one; after a restart it reads the events it missed from the outbox.
8. Test 6: two concurrent `SERIALIZABLE` transactions that each check for a similar vector and then insert do not both commit; the check reports what happened.
9. Test 7: the check records the serialization failures with GIN `fastupdate` on and off, over the same workload.
10. Test 8: a German sample corpus lists which compound queries the `german` configuration misses without Hunspell.
11. Test 9: the same German and English corpus is stemmed by PostgreSQL 18 and by PostgreSQL 19, and the check lists which `tsvector` values differ. Docker Hub had no final 19 image on 2026-11-19, so the check uses `postgres:19rc1` and says so. It does not run `pg_upgrade`; a stored generated column keeps its old value until it is recomputed, so the difference is what a recompute after the upgrade would change.
12. The whole run passes twice in a row on a fresh volume.

Write a short comparison note, `notes-a.md`: each test's result, what surprised, and what it means for the design position.
