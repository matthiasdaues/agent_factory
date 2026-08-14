# Codex usage-capture trusted smoke test — 2026-07-22

## Scope

- Finding: [RECON-0007](../findings/RECON-0007.md).
- Codex CLI: `0.144.6`.
- Disposable repository: `agent-factory-codex-smoke.GlVrBx`.
- Trust path: the user reviewed and trusted the project `Stop` and
  `SubagentStop` hooks through `/hooks`.
- Trust bypass: not used.

No prompt, transcript content, absolute filesystem path, or session identifier
is retained in this evidence record.

## Procedure

1. Initialize the disposable consumer repository with `init-factory`.
2. Start interactive Codex in that repository without a hook-trust bypass.
3. Use `/hooks` to review and trust the installed project hooks.
4. Complete one real Codex turn and exit normally.
5. Inspect the generated usage record and its referenced transcript copy.

## Observations

- Exactly one JSONL record was appended under
  `.agent-factory/usage/<session-id>.jsonl`.
- The record matched the canonical usage schema and identified `cli` as
  `codex`.
- `usage_granularity` was `full`.
- The record's `transcript_ref` resolved to an existing persisted transcript
  copy. Its value is intentionally omitted.

| Usage field            | Observed value |
| ---------------------- | -------------- |
| `reported_input`       | 17380          |
| `reported_output`      | 6              |
| `reported_cache_read`  | 9984           |
| `reported_cache_write` | 0              |
| `normalized_input`     | 6675           |
| `normalized_output`    | 2              |
| `normalized_total`     | 6677           |

## Result

Pass. A user-trusted project hook executed during a real Codex lifecycle and
created the canonical usage and transcript artifacts required by RECON-0007.
