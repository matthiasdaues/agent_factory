# Notes On Story A: The Store And Its Tests

Run on 2026-11-19 against `pgvector/pgvector:pg18`. All nine checks pass, twice in a row on a fresh volume, in about 30 seconds a run. `schema.sql` loads twice without error. Two results change the design position.

## Results

| Test | Result | What the check observed |
| --- | --- | --- |
| 1 | PASS | A row inserted earlier in the transaction is found by both branches of the fused search, keyword rank 1 and vector rank 1, through plans that use the HNSW and GIN indexes. Search-then-traverse reaches its source. With `hnsw.ef_search = 1` and a noisy query the row was still found. |
| 2 | PASS | After `ROLLBACK` the fused search finds no trace of the row. |
| 3 | PASS | The trigger refuses a wrong-kind edge at insert, and refuses a change of a node's kind that would break a live edge. |
| 4 | PASS | As the application role, update, delete, and `TRUNCATE` of edges and decisions fail on missing privileges; a change of a decision's kind fails in the trigger. An edge can be ended once, by setting `valid_to`, and not twice. |
| 5 | PASS | The listener heard the committed idea; the rolled-back idea left no outbox row; after a listener restart the outbox held both ideas written while it was down. |
| 6 | PASS | Two `SERIALIZABLE` transactions that each find no duplicate and then insert the same vector: one commits, one fails. But two writers of unrelated vectors also failed in 10 of 10 rounds. |
| 7 | PASS | Serialization failures in 20 rounds, crossing and disjoint writers: `fastupdate` on 20 and 20, off 20 and 0. |
| 8 | PASS | 7 of 8 German part-word queries miss in full-text search, such as "Verbindung" for "Datenbankverbindung". `pg_trgm` word similarity finds all 8. |
| 9 | PASS | No `tsvector` of the seven-sentence corpus differs between 18 and `19rc1`. Docker Hub had no final 19 image. The corpus is small, so this says little. |

## What surprised

- Test 6 contradicts pgvector issue #1055, which the postgres-and-qmd survey recorded: under `SERIALIZABLE`, both duplicates did not commit. The reason is coarse locking. pgvector's indexes take no fine-grained predicate locks, so a vector read conflicts with every concurrent insert. The duplicate is caught, and so is every unrelated writer.
- Test 7 shows the same for GIN. With `fastupdate` on, the pending list makes every concurrent writer conflict. With it off, only true conflicts fail.
- The first version of `hybrid_search` searched all vectors regardless of model. Story B exposed it, when stand-in and real vectors shared the table. The vector branch now filters by model, with `hnsw.iterative_scan` so the filter does not starve the index scan.
- `convert_to` is not immutable, so a generated hash column needs a wrapper function. Row-level triggers do not fire on `TRUNCATE`, but a statement-level `before truncate` trigger and withheld privileges both stop it.

## What it means for the design position

1. Do not run the import under `SERIALIZABLE`. Every writer would conflict with every vector reader. Use `READ COMMITTED`, and stop duplicates with a unique key or an advisory lock on the content hash.
2. If any path does use `SERIALIZABLE`, set `fastupdate = off` on the GIN index.
3. The vector branch must filter by model and version. Several models in one table need the iterative scan, or one partial HNSW index per model.
4. German compounds: keep `pg_trgm` in the fused search as a third branch, or as a fallback, until Hunspell is decided.
5. Test 9 needs a larger corpus and a final 19 image before it can say anything.
