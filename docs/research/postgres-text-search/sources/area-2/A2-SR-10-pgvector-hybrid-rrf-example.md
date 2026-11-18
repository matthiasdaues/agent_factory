# A2-SR-10: pgvector README section Hybrid Search and pgvector-python examples/hybrid_search/rrf.py

```json
{
  "source_identity": "pgvector/pgvector README.md section Hybrid Search at commit 7c7345e0121d69f5a6e2a6a41357ad5a9a10156e (2026-11-18); pgvector/pgvector-python examples/hybrid_search/rrf.py at commit d2ace87ca497517b73ffa2c88a50896f65a2b17a (2026-11-05), file last changed in commit 7e7a851d413d (2024-08-28); https://github.com/pgvector/pgvector and https://github.com/pgvector/pgvector-python/blob/master/examples/hybrid_search/rrf.py",
  "author_or_issuing_body": "pgvector maintainers (Andrew Kane)",
  "publisher": "GitHub",
  "publication_date": "2024-08-28T20:35:47Z",
  "relevant_event_date": "2024-08-28",
  "source_family": "Primary: repository documentation and example code. pgvector itself is recorded in the postgres-and-qmd survey as A1-SR-10; this record covers only the hybrid example. The RRF formula descends from Cormack et al. (A2-SR-11), which the example does not cite.",
  "precise_evidence_location": "pgvector README.md lines 633 to 642 (Hybrid Search); rrf.py, the sql string assigned before query = 'growling bear'",
  "method": "The maintainers give an SQL statement that fuses a pgvector ranking and a PostgreSQL full-text ranking in one statement.",
  "limitations": "Example code, not a tested reference implementation. The publication_date is the last change to rrf.py, not its first version. The keyword side uses built-in ts_rank_cd, which area 1 records. The example opens the connection with autocommit and runs no other statement in the transaction.",
  "provenance": "Read with `gh api repos/pgvector/pgvector/readme` and `gh api repos/pgvector/pgvector-python/contents/examples/hybrid_search/rrf.py` on 2026-11-18; file history from `gh api repos/pgvector/pgvector-python/commits?path=examples/hybrid_search/rrf.py`. Re-verify at the commits above."
}
```

## Evidence

- pgvector README, Hybrid Search: "Use together with Postgres full-text search for hybrid search." and "You can use Reciprocal Rank Fusion or a cross-encoder to combine results." (link text kept.)
- rrf.py, the statement as written in the file:

```sql
WITH semantic_search AS (
    SELECT id, RANK () OVER (ORDER BY embedding <=> %(embedding)s) AS rank
    FROM documents
    ORDER BY embedding <=> %(embedding)s
    LIMIT 20
),
keyword_search AS (
    SELECT id, RANK () OVER (ORDER BY ts_rank_cd(to_tsvector('english', content), query) DESC)
    FROM documents, plainto_tsquery('english', %(query)s) query
    WHERE to_tsvector('english', content) @@ query
    ORDER BY ts_rank_cd(to_tsvector('english', content), query) DESC
    LIMIT 20
)
SELECT
    COALESCE(semantic_search.id, keyword_search.id) AS id,
    COALESCE(1.0 / (%(k)s + semantic_search.rank), 0.0) +
    COALESCE(1.0 / (%(k)s + keyword_search.rank), 0.0) AS score
FROM semantic_search
FULL OUTER JOIN keyword_search ON semantic_search.id = keyword_search.id
ORDER BY score DESC
LIMIT 5
```

- rrf.py, fusion lines: "COALESCE(1.0 / (%(k)s + semantic_search.rank), 0.0) +" and "COALESCE(1.0 / (%(k)s + keyword_search.rank), 0.0) AS score".
- rrf.py: "k = 60". The keyword index is "CREATE INDEX ON documents USING GIN (to_tsvector('english', content))".
- The fusion uses a `FULL OUTER JOIN` and `COALESCE`, so a row found by one branch only still gets a score. ParadeDB's form (A2-SR-07) uses `UNION ALL` and `GROUP BY` instead and adds branch weights.
- The cross-encoder example in the same folder reranks in Python outside SQL (file name only; not read).
- Not shown: weighted fusion, a BM25 keyword side, or an evaluation.
