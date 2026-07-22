# Token usage tracking reconciliation — 2026-07-22

## Scope

- Exact reviewed base:
  `a658cfc5b3d8a23bb86535323b5d96e154dbbe72`, after the implementation and
  evidence fixes for RECON-0006 through RECON-0008.
- Code compared: the shared `usage-capture` record, tokenizer, normalizers, and
  JSONL adapter; Claude, Copilot, Codex, and Pi lifecycle adapters;
  `init-factory` and `remove-factory`; focused normalizer, installed-path,
  installation, removal, and end-to-end tests.
- Documentation compared: the token-usage proposal, factory guide, ADR-0007,
  architecture building-block and decision chapters, ST-0035 through ST-0044,
  prior reconciliation findings, and live Codex/Claude acceptance evidence.
- This is a full fresh repeat pass. It preserves the historical
  [2026-07-21 reconciliation](reconciliation-2026-07-21.md), verifies each of
  that pass's open findings individually, and rebuilds the complete truth map
  to catch defects introduced or exposed by the fixes.

## Discrepancy table

| Finding                                                                                                                                          | Artifact                                | Classification | Severity | Action                                                                                            |
| ------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------- | -------------- | -------- | ------------------------------------------------------------------------------------------------- |
| Pi descendant records written inside a dispatched worktree are deleted when that worktree is removed.                                            | [RECON-0009](../findings/RECON-0009.md) | Code defect    | Major    | Filed; implementation pending.                                                                    |
| Pi capture synchronously waits up to thirty seconds on human shutdown and child tool-result paths.                                               | [RECON-0010](../findings/RECON-0010.md) | Code defect    | Major    | Filed; implementation pending.                                                                    |
| Pi subprocess spend is not included in its parent root; total spend must add the root and each distinct descendant once.                         | Proposal, guide, ADR-0007, ST-0044      | Spec stale     | Major    | Updated the conservation rule and required regression coverage.                                   |
| The guide still described resolved Pi parent-session propagation as unresolved.                                                                  | `factory/docs/factory-guide.md`         | Spec stale     | Minor    | Replaced with the implemented active-session resolution order.                                    |
| Copilot emits cumulative root snapshots on repeated `agentStop` events, but the contract did not say to select only the latest session snapshot. | Proposal and guide                      | Spec stale     | Major    | Defined snapshot records, latest-root selection, and repeated-turn conservation coverage.         |
| RECON-0006: Pi child records could lose their human parent session.                                                                              | [RECON-0006](../findings/RECON-0006.md) | Prior finding  | Major    | Verified resolved by shared active-session resolution and executable installed-path tool tests.   |
| RECON-0007: Codex hooks were installed without activation guidance or trusted live evidence.                                                     | [RECON-0007](../findings/RECON-0007.md) | Prior finding  | Major    | Verified resolved by installer output tests and the trusted live Codex acceptance record.         |
| RECON-0008: Claude root and child records lacked a proven conservation rule and captured the wrong child transcript.                             | [RECON-0008](../findings/RECON-0008.md) | Prior finding  | Major    | Verified resolved by adapter/conservation tests and the controlled live Claude acceptance record. |

## Prior finding verification

- **RECON-0006 remains resolved.** `activeSessionId()` prefers the active Pi
  session file, then the explicit child-session environment, then a
  process-stable fallback. Human shutdown, `run_agent`, and `dispatch_wave` use
  that resolver. Installed-path tests execute both child tools and inspect the
  persisted parent/depth fields.
- **RECON-0007 remains resolved.** Fresh and repeat initialization both report
  that Codex capture is inactive until the current project hooks are reviewed
  and trusted through `/hooks`. The live acceptance record proves a trusted
  Codex lifecycle produced canonical usage and transcript artifacts.
- **RECON-0008 remains resolved.** Claude `SubagentStop` requires
  `agent_transcript_path`, never falls back to the main transcript, and totals
  compose as the latest cumulative root plus each distinct child once. Both
  deterministic and controlled live evidence cover the rule.

## Specification and architecture files updated

- `factory/docs/proposals/token-usage-tracking.md` — defined native capture
  records as snapshots, latest-root Copilot selection, and Pi
  root-plus-descendants conservation.
- `factory/docs/factory-guide.md` — removed stale RECON-0006 wording and aligned
  Copilot/Pi aggregation guidance with the executable adapters.
- `docs/adr/0007-normalize-runtime-usage-through-cli-adapters.md` — recorded
  Pi's non-inclusive subprocess boundary and Copilot cumulative-root rule.
- `backlog/ST-0044.md` — corrected the completed Pi story's attribution claim
  and added conservation coverage to its documented test surface.

## Code defects filed

- [RECON-0009](../findings/RECON-0009.md) — preserve nested Pi usage outside
  disposable dispatch worktrees.
- [RECON-0010](../findings/RECON-0010.md) — remove synchronous Pi capture from
  measured lifecycle and tool-result paths.

## Validation results

- Focused usage, four-CLI end-to-end, initialization, and removal tests:
  **85 passed** before documentation updates.
- `spec-lint --spec-dir docs/spec`: exit 0; 0 errors, 0 warnings, 7 info.
- `arch-lint --docs-dir docs/`: exit 0; 0 errors, 2 pre-existing parse warnings.
- Post-update focused usage, four-CLI end-to-end, initialization, and removal
  tests: **85 passed**.
- `mdformat` and `git diff --check`: passed for every updated Markdown file.
