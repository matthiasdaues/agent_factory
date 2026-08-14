# Claude root-and-child usage conservation smoke test — 2026-07-22

## Scope

- Finding: [RECON-0008](../findings/RECON-0008.md).
- Claude Code CLI: `2.1.217`.
- Disposable repository: `agent-factory-claude-smoke.iJ1fUo`.
- Session shape: one root turn with exactly one foreground `general-purpose`
  subagent.

No prompt, transcript content, absolute filesystem path, session identifier,
or hash is retained in this evidence record.

## Procedure

1. Initialize the disposable consumer repository with `init-factory`.
2. Start interactive Claude Code and approve the project hooks.
3. Complete one turn that delegates to exactly one foreground
   `general-purpose` subagent, then exit normally.
4. Inspect the canonical usage records and their referenced transcript copies.
5. Sum the final cumulative root record and the distinct child record
   fieldwise.

## Observations

- Exactly two canonical records were written for one session.
- The child record identified `agent` as `general-purpose`, used `full`
  granularity, and was emitted from the nested `SubagentStop` path.
- The root record used `agent: null`, used `full` granularity, and was emitted
  from `Stop`.
- The records had distinct transcript references, and both references resolved
  to persisted transcript copies. Their values are intentionally omitted.

| Usage field            | Child |  Root | Conserved total |
| ---------------------- | ----: | ----: | --------------: |
| `reported_input`       |     2 |     8 |              10 |
| `reported_output`      |    43 |  1426 |            1469 |
| `reported_cache_read`  |     0 | 92278 |           92278 |
| `reported_cache_write` | 16410 | 34369 |           50779 |
| `normalized_input`     |    13 |   136 |             149 |
| `normalized_output`    |    33 |    81 |             114 |
| `normalized_total`     |    46 |   217 |             263 |

## Result

Pass. The installed hooks captured the root and distinct child transcript
through their correct lifecycle events. Summing the latest cumulative root
record and the child record exactly once conserved every provider-reported and
normalized usage field, satisfying RECON-0008.
