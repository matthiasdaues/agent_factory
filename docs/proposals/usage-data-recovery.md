---
schema_version: 2
scope: usage-data-recovery
status: draft
owner: md@matthiasdaues.de
created: 2026-09-25
updated: 2026-09-25
supersedes:

impact:
  scope: single_component
  architecture_change: false
  external_contract_change: false
  boundaries:
    - packages/factory/scripts/usage-capture
    - packages/factory/scripts/usage-capture-lifecycle
    - packages/factory/scripts/init-factory
---

# Usage Data Recovery

## Problem

Four months of usage records (June through September 2026) were lost from `.agent-factory/usage/records/` and `.agent-factory/usage/transcripts/` during a reinstall on 2026-09-24. The directories were recreated empty by `initialize_usage_lifecycle`; their birth timestamps (2026-09-24 19:43) confirm no data was written after the reinstall.

The raw session transcripts that produced those records still exist in the CLI-specific storage directories. This proposal describes how to re-derive usage records from those transcripts.

## Raw transcript inventory

| CLI         | Location                                                  | Sessions (this project) | Format | Project scoping                                  |
| ----------- | --------------------------------------------------------- | ----------------------- | ------ | ------------------------------------------------ |
| Claude Code | `~/.claude/projects/-home-...-agent-factory/*.jsonl`      | 204                     | JSONL  | Scoped by directory name                         |
| Pi          | `~/.pi/agent/sessions/--home-...-agent_factory--/*.jsonl` | 87                      | JSONL  | Scoped by directory name                         |
| Codex       | `~/.codex/sessions/YYYY/MM/DD/*.jsonl`                    | 226 (of 275 total)      | JSONL  | `session_meta.payload.cwd` contains project path |
| Copilot     | `~/.copilot/sidebar-sessions-state/*.json`                | 1                       | JSON   | Needs format investigation                       |

**Total:** approximately 518 sessions for this project.

## Existing capture pipeline

The usage capture pipeline has two stages:

1. **Registration** (`usage-capture-runtime --lifecycle register`): takes a raw transcript path, snapshots it to `.agent-factory/usage/.capture/`, creates a pending marker, and detaches a supervisor process.

2. **Capture** (`usage-capture-runtime --cli <cli> --transcript <path>`): normalizes the transcript for the given CLI, tokenizes via `cl100k_base`, assembles a `UsageRecord`, and persists it via `JsonlLoggingAdapter` to `.agent-factory/usage/records/` with a transcript copy in `.agent-factory/usage/transcripts/`.

Each CLI has a normalizer class: `ClaudeCodeNormalizer`, `PiNormalizer`, `CodexNormalizer`, `CopilotNormalizer`.

## Recovery approach

### Option A: Direct capture invocation (simpler, less metadata)

Invoke `usage-capture-runtime` directly (bypassing the lifecycle registrar) for each transcript:

```bash
.agent-factory/factory/scripts/usage-capture-runtime \
  --cli claude-code \
  --transcript ~/.claude/projects/-home-...-agent-factory/<session-id>.jsonl \
  --session <session-id>
```

**Advantages:** Simple loop, one command per transcript, no lifecycle machinery involved.

**Limitations:**

- Branch and commit context will reflect the current HEAD, not the original session's state. The `--branch` and `--commit` flags could be omitted, leaving those fields empty.
- No parent-session or depth information (subagent hierarchy) — those are provided by the hook payload at session-end time and are not encoded in the transcript.
- SubagentStop granularity is lost. The hook fires separately for each subagent termination; replaying the main transcript produces one aggregate record, not per-subagent records.

### Option B: Batch replay script (recommended)

Write a dedicated `usage-replay` script that:

1. **Discovers** all session transcripts for this project across all four CLIs.
2. **Filters** by project path (Claude and Pi are pre-scoped by directory; Codex requires parsing `session_meta.payload.cwd`; Copilot needs format investigation).
3. **Extracts metadata** from each transcript where possible:
   - Session ID (from filename or `session_meta`)
   - CLI type (from source directory)
   - Timestamp (from filename or first record)
   - Model (from transcript content, if the normalizer extracts it)
4. **Invokes** `usage-capture` (the Python module directly, not via the lifecycle shell script) for each transcript, passing extracted metadata.
5. **Reports** a summary: total sessions processed, records created, failures.
6. **Deduplicates** against existing records to make replay idempotent.

### Metadata quality

| Field                 | Recoverable?          | Source                                                             |
| --------------------- | --------------------- | ------------------------------------------------------------------ |
| `record_id`           | Generated fresh       | `RecordIdSequencer`                                                |
| `session_id`          | Yes                   | Filename (Claude, Pi) or `session_meta` (Codex)                    |
| `cli`                 | Yes                   | Source directory                                                   |
| `normalized_input`    | Yes                   | Transcript content via normalizer + `cl100k_base`                  |
| `normalized_output`   | Yes                   | Transcript content via normalizer + `cl100k_base`                  |
| `reported_input`      | Yes (where available) | Transcript usage events                                            |
| `reported_output`     | Yes (where available) | Transcript usage events                                            |
| `reported_cache_read` | Yes (where available) | Transcript usage events                                            |
| `model`               | Partial               | Normalizer extracts from transcript if present                     |
| `branch`              | No                    | Not encoded in transcript                                          |
| `commit_id`           | No                    | Not encoded in transcript                                          |
| `parent_session_id`   | Partial               | Codex `session_meta.forked_from_id`; Claude subagents not linkable |
| `depth`               | No                    | Not encoded in transcript                                          |
| `agent`               | Partial               | Codex `session_meta`; Claude subagent type not in transcript       |
| `exit_status`         | No                    | Runtime-only                                                       |
| `project_id`          | Yes                   | From `.agent-factory/config/project.json`                          |

### Copilot format

Copilot stores sessions in `~/.copilot/session-store.db` (SQLite) with sidebar state in JSON files. The `CopilotNormalizer` exists in `usage-capture` but its input format needs investigation — the sidebar JSON may not be the raw transcript format the normalizer expects. Only 1 session exists for this project, so manual handling is acceptable.

## Limitations

1. **Record IDs will differ** from the originals. Any downstream analysis keyed on `record_id` will see the replayed records as new entries, not replacements.
2. **Branch and commit context is unrecoverable.** Those fields will be empty or reflect current HEAD. Historical git context cannot be reconstructed from the transcripts.
3. **Subagent-level granularity is lost.** The original capture fired per-subagent via `SubagentStop` hooks. Replay from the main transcript produces one record per session, not per-subagent records. Codex's `forked_from_id` in `session_meta` provides partial hierarchy for Codex sessions.
4. **Timestamps will reflect replay time**, not original session time. The `UsageRecord.timestamp` is set at creation. A recovery script should override this with the transcript's own timestamp where available.
5. **Idempotency.** Running the replay twice without deduplication will create duplicate records. The replay script must either check for existing records by session ID or use a replay-run marker.

## Recommendations

1. Build Option B (batch replay script) as `packages/factory/scripts/usage-replay`.
2. Start with Claude Code (204 sessions) — the largest set, best-understood format, and the normalizer is the most mature.
3. Add Pi (87 sessions) second — similar JSONL format, directory-scoped.
4. Add Codex (226 sessions) third — requires `cwd` filtering from `session_meta`.
5. Defer Copilot (1 session) — investigate format manually.
6. Run the replay against the development install first, verify record counts and spot-check a few records, then run against the production install.

## Prevention

The `backup_preserved_dirs` / `offer_restore_preserved_dirs` guard added to `init-factory` in this session prevents future data loss during reinstalls. The guard:

- Backs up non-empty `usage/` and `user-changes/` to a temp directory before any install work.
- After the install, compares the subdirectory structure of the backup against the new install.
- If the structure matches, offers to restore (interactive) or restores automatically (non-interactive).
- If the structure does not match, prints the backup path for manual recovery.

This guard is tested in `tests/factory/test_init_factory.py` (`TestBackupPreservedDirs`, `TestOfferRestorePreservedDirs`).
