# Token usage tracking reconciliation — 2026-07-21

## Scope

- Range: `af81d0a..0652870613460c0f34ff749f85a4a64a954b5306`.
- Code compared: `factory/scripts/{usage-capture,init-factory,remove-factory}`;
  Claude, Copilot, Codex, and Pi hook/extension adapters; focused usage,
  installation, removal, and end-to-end tests.
- Documentation compared: the token-usage proposal, ST-0035 through ST-0044,
  the factory guide, arc42 building-block and decision chapters, and ADR-0001
  through ADR-0006.
- Prior discrepancies were rechecked from a fresh truth map after ST-0042,
  ST-0043, and ST-0044 merged.

## Discrepancy table

| Finding                                                                                                                                      | Artifact                                                                | Category   | Severity | Disposition                                                                               |
| -------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | ---------- | -------- | ----------------------------------------------------------------------------------------- |
| Pi child records can lose their human parent session; establish the active parent at the tool boundary and test persisted attribution.       | [RECON-0006](../findings/RECON-0006.md)                                 | Defect     | Major    | Filed; implementation pending.                                                            |
| Codex project hooks remain inactive until trusted, but installation does not report activation; add the `/hooks` instruction and live proof. | [RECON-0007](../findings/RECON-0007.md)                                 | Defect     | Major    | Filed; implementation pending.                                                            |
| Claude root and child records have no conservation rule; verify platform semantics before aggregation.                                       | [RECON-0008](../findings/RECON-0008.md)                                 | Defect     | Major    | Filed; implementation pending.                                                            |
| `usage_granularity` omitted the implemented null state.                                                                                      | `docs/proposals/implemented/token-usage-tracking.md`                    | Defect     | Major    | Updated to `full \| aggregate \| null`.                                                   |
| `record_id` remained an open choice after implementation settled it.                                                                         | `docs/proposals/implemented/token-usage-tracking.md`                    | Defect     | Major    | Documented session sequence, line-count seed, UUID fallback, and one-writer assumption.   |
| Capture-site wording assumed two hook kinds, which does not describe Pi.                                                                     | `docs/proposals/implemented/token-usage-tracking.md`                    | Defect     | Minor    | Reworded around native capture sites.                                                     |
| Failure wording promised stderr visibility that lifecycle adapters suppress.                                                                 | `docs/proposals/implemented/token-usage-tracking.md`                    | Defect     | Minor    | Distinguished direct invocation from native adapters.                                     |
| The factory guide lacked one shared four-CLI usage contract and Claude coverage.                                                             | `factory/docs/factory-guide.md`                                         | Defect     | Major    | Added unified storage, schema, trigger, accounting, trust, removal, and failure guidance. |
| ST-0044 called Pi provider usage cumulative although code sums per-response values.                                                          | `backlog/ST-0044.md`                                                    | Defect     | Minor    | Corrected the completed-story analysis.                                                   |
| The cross-cutting capture design had no durable architecture rationale.                                                                      | [ADR-0007](../adr/0007-normalize-runtime-usage-through-cli-adapters.md) | Defect     | Major    | Added ADR and architecture links; no Pugh Matrix warranted.                               |
| Same-session line-count ID allocation is not atomic.                                                                                         | `docs/proposals/implemented/token-usage-tracking.md`                    | Suggestion | Minor    | Documented the MVP one-writer-per-session assumption.                                     |

## Prior discrepancy verification

- Four supported CLI normalizers and native capture paths: resolved by
  ST-0042 through ST-0044, with the three operational/accounting defects above
  remaining open.
- Claude removal from pre-existing settings: resolved and covered by focused
  round-trip tests.
- `.agent-factory/usage/` ignore coverage: resolved by the existing
  `/.agent-factory/` entry; no narrower rule is needed.
- `usage_granularity`, `record_id`, factory-guide coverage, and ADR rationale:
  reconciled in this update.

## Specification and architecture files updated

- `docs/proposals/implemented/token-usage-tracking.md` — synchronized nullable
  usage, record IDs, capture wording, failure visibility, and concurrency
  assumptions.
- `factory/docs/factory-guide.md` — added the unified four-CLI operational
  guide and linked open defects.
- `backlog/ST-0044.md` — corrected Pi per-response provider accounting.
- `docs/adr/0007-normalize-runtime-usage-through-cli-adapters.md` — recorded
  normalization, adapter, lifecycle-ownership, persistence, privacy, and
  conservation decisions.
- `docs/arc42/09_architecture_decisions.md` and `docs/arc42/05_building_block_view.md` —
  indexed ADR-0007 and described the runtime usage component.

## Code defects filed

- [RECON-0006](../findings/RECON-0006.md) — Pi parent-session propagation.
- [RECON-0007](../findings/RECON-0007.md) — Codex trust activation.
- [RECON-0008](../findings/RECON-0008.md) — Claude root/child conservation.

## Validation results

- Focused usage, four-CLI end-to-end, init, and removal tests: **80 passed**.
- `spec-lint --spec-dir docs/spec`: exit 0; 0 errors, 0 warnings, 7 info.
- `arch-lint --docs-dir docs/`: exit 0; 0 errors, 2 parse warnings, 2 info.
  The informational export step regenerated unchanged architecture diagrams;
  those incidental exports were restored and are not part of this update.
