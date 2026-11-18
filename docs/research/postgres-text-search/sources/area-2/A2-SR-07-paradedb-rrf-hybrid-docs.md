# A2-SR-07: ParadeDB documentation on reciprocal rank fusion and hybrid search

```json
{
  "source_identity": "paradedb/paradedb, docs/reference/hybrid/rrf.mdx and docs/concepts/hybrid/overview.mdx at commit c0ffb135a234efc5e1cf67f68b9ca5c0e6a51723; published at https://www.paradedb.com/docs/reference/hybrid/rrf",
  "author_or_issuing_body": "ParadeDB, Inc.",
  "publisher": "GitHub (source of the docs site paradedb.com/docs)",
  "publication_date": "2026-11-18T19:01:11Z",
  "relevant_event_date": "2026-11-18",
  "source_family": "Primary: vendor documentation for stated syntax. Same lineage as A2-SR-03 to A2-SR-05. Its RRF formula descends from Cormack et al. (A2-SR-11), which the page does not cite.",
  "precise_evidence_location": "rrf.mdx: Note box, Reciprocal Rank Fusion Query Shape (SQL tab), Choosing the Rank Constant, Choosing the Branch Limit; overview.mdx: Note box and section Fusing by Rank; docs/reference/indexing/indexing-vectors.mdx lines 12 to 16",
  "method": "The vendor documents a SQL statement shape and the meaning of its parameters.",
  "limitations": "Documentation of syntax; the tuning advice is the vendor's and is not evidence of retrieval quality. The vector branch uses ParadeDB's own vector search, a beta feature from 0.25.0, not pgvector's own index (see the indexing-vectors.mdx item in Evidence). Whether the statement runs in one snapshot is not stated; I infer it from PostgreSQL semantics for a single statement.",
  "provenance": "Sparse shallow clone of https://github.com/paradedb/paradedb on 2026-11-18. Re-verify at the commit above."
}
```

## Evidence

- rrf.mdx, Note: "This section uses vector search, a beta feature available in versions `0.25.0` and above." (link text kept.)
- rrf.mdx, definition: "Each branch contributes `weight / (k + rank)`, and the contributions are added." and "`60` is the conventional value and the one used throughout this page."
- rrf.mdx, Reciprocal Rank Fusion Query Shape: "Each branch is an `ORDER BY ... LIMIT` with a `RANK()` window function over the same ordering. The `WITH` clause fuses them." The SQL tab, quoted in full:

```sql
WITH text AS (
    SELECT id, RANK() OVER (ORDER BY pdb.score(id) DESC, id) AS rank
    FROM mock_items
    WHERE description ||| 'running shoes'
    ORDER BY pdb.score(id) DESC, id
    LIMIT 20
),
vector AS (
    SELECT id, RANK() OVER (ORDER BY embedding <=> '[1,2,3,4,5,6,7,8]', id) AS rank
    FROM mock_items
    WHERE id @@@ pdb.all()
    ORDER BY embedding <=> '[1,2,3,4,5,6,7,8]', id
    LIMIT 20
),
fused AS (
    SELECT id, sum(weight) AS score
    FROM (
        SELECT id, 1.0 / (60 + rank) AS weight FROM text
        UNION ALL
        SELECT id, 0.7 / (60 + rank) AS weight FROM vector
    ) u
    GROUP BY id
)
SELECT m.id, m.description, f.score
FROM fused f
JOIN mock_items m USING (id)
ORDER BY f.score DESC, m.id
LIMIT 5;
```

- rrf.mdx, Choosing the Branch Limit: "The fused result can only contain rows that at least one branch returned."
- overview.mdx, Fusing by Rank: "BM25 scores and vector distances operate on different scales, so they cannot be added together directly." and "ParadeDB's hybrid examples use Reciprocal Rank Fusion, which discards raw scores and uses only each row's position, or rank, in each result list." (link text kept.)
- docs/reference/indexing/indexing-vectors.mdx, Note at lines 12 to 16: "ParadeDB uses pgvector's vector types, but not its HNSW or IVF indexes." The pgvector extension must be installed first.
- Not shown: a fusion by score (convex combination) in SQL, an evaluation of the weights, and the original source of RRF.
