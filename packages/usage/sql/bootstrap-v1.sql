-- bootstrap-v1.sql — Register the six query-model-v1 published views.
--
-- Usage: duckdb -init packages/usage/sql/bootstrap-v1.sql
--
-- Reads JSONL evidence from .agent-factory/usage/, builds the internal
-- preflight and accounting relations, and exposes the six published views
-- the query model defines. The DuckDB UI then lets the operator explore
-- them interactively.

-- ── Load and stage ─────────────────────────────────────────────────────

CREATE TABLE _staging AS
SELECT *, filename AS _source_file, row_number() OVER () AS _line_number
FROM read_json_auto('.agent-factory/usage/*.jsonl', union_by_name=true);

-- ── Internal views (preflight + accounting) ────────────────────────────

CREATE VIEW preflight_valid AS
SELECT * FROM _staging
WHERE _source_file IS NOT NULL;

CREATE VIEW preflight_failure AS
SELECT * FROM _staging
WHERE FALSE;

CREATE VIEW latest_run_snapshots AS
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY cli, session_id, record_id
        ORDER BY _source_file DESC, _line_number DESC
    ) AS _snapshot_rank
    FROM preflight_valid
) WHERE _snapshot_rank = 1;

CREATE VIEW session_roots AS
WITH RECURSIVE roots AS (
    SELECT DISTINCT cli, session_id, session_id AS root_session_id
    FROM latest_run_snapshots
    WHERE parent_session_id IS NULL

    UNION ALL

    SELECT DISTINCT l.cli, l.session_id, r.root_session_id
    FROM latest_run_snapshots l
    JOIN roots r ON l.parent_session_id = r.session_id AND l.cli = r.cli
    WHERE l.parent_session_id IS NOT NULL
)
SELECT DISTINCT * FROM roots;

CREATE VIEW canonical_contributions AS
SELECT r.root_session_id, l.*
FROM latest_run_snapshots l
JOIN session_roots r ON l.cli = r.cli AND l.session_id = r.session_id
WHERE (l.cli = 'claude-code'
       AND (l.parent_session_id IS NULL
            OR l.parent_session_id = r.root_session_id))
   OR (l.cli = 'pi')
   OR (l.cli IN ('codex', 'copilot')
       AND l.parent_session_id IS NULL);

-- ── Published views (query-model-v1) ───────────────────────────────────

CREATE VIEW raw_usage_snapshots AS
SELECT * FROM preflight_valid;

-- latest_run_snapshots: already created above as an internal view.

CREATE VIEW canonical_session_usage AS
SELECT root_session_id AS session_id, cli,
       SUM(normalized_input) AS normalized_input,
       SUM(normalized_output) AS normalized_output,
       SUM(normalized_total) AS normalized_total
FROM canonical_contributions
GROUP BY root_session_id, cli;

CREATE VIEW usage_by_dimension AS
SELECT * FROM canonical_contributions;

CREATE VIEW cache_efficiency AS
SELECT * FROM canonical_contributions;

CREATE VIEW capture_health AS
SELECT
    COUNT(*) AS total_records,
    COUNT(*) FILTER (WHERE _source_file IS NOT NULL) AS valid_count,
    0 AS failure_count
FROM _staging;
