# Token usage tracking final reconciliation — 2026-07-22

## Scope

- Exact reviewed base:
  `d0001003130404604dd5c19e199264fa0911d08d`, after RECON-0009 and
  RECON-0010 were implemented and merged.
- Code compared: Pi canonical-root derivation and propagation, detached
  persistence and guarded source cleanup, `remove-factory`, the shared capture
  entrypoint, and Claude, Copilot, Codex, and Pi conservation adapters and
  installed-path tests.
- Documentation compared: the token-usage proposal, factory guide, ADR-0007,
  ST-0042 through ST-0044, all RECON finding files, the
  [initial 2026-07-22 reconciliation](reconciliation-2026-07-22.md), and live
  Codex/Claude acceptance evidence.
- This report is a separate final repeat pass. It preserves both earlier
  reconciliation reports as historical snapshots and rebuilds the affected
  truth map after the two Pi fixes.

## Discrepancy table

| Finding                                                                                                                    | Artifact                                | Classification             | Severity | Action                         |
| -------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- | -------------------------- | -------- | ------------------------------ |
| Copilot latest-cumulative-root selection is specified but lacks an installed repeated-turn conservation test.              | [RECON-0011](../findings/RECON-0011.md) | Speculative / missing test | Major    | Filed; implementation pending. |
| `remove-factory` can lose pending Pi usage or allow a detached capture to recreate Factory paths after successful removal. | [RECON-0012](../findings/RECON-0012.md) | Code defect                | Major    | Filed; implementation pending. |
| RECON-0009: nested Pi usage could be deleted with a successful dispatch worktree.                                          | [RECON-0009](../findings/RECON-0009.md) | Prior finding              | Major    | Verified resolved.             |
| RECON-0010: Pi normalization and persistence could block measured lifecycle and tool-result paths for thirty seconds.      | [RECON-0010](../findings/RECON-0010.md) | Prior finding              | Major    | Verified resolved.             |
| RECON-0001 through RECON-0008.                                                                                             | `docs/findings/RECON-0001.md`–`0008.md` | Prior findings             | —        | Verified resolved.             |

## Prior finding verification

- **RECON-0009 is resolved.** Pi derives the canonical primary checkout from
  Git's shared common directory, validates inherited context, propagates the
  root to every child, and resolves the capture executable from that root. The
  installed nested regression proves depth-one and depth-two records and
  transcripts survive successful outer-worktree removal with correct lineage.
- **RECON-0010 is resolved on measured lifecycle paths.** Pi performs only the
  durable local staging write synchronously, then detaches persistence with
  ignored streams and releases the child handle. Gated installed tests prove
  human shutdown, `run_agent`, and `dispatch_wave` return before persistence,
  followed by eventual records, transcripts, and staged-source cleanup.
- **RECON-0001 through RECON-0008 remain resolved.** The final fresh audit found
  no regression in parent correlation, Codex trust activation, Claude child
  conservation, installer/remover ownership, schema, transcript persistence,
  or the documented four-CLI accounting rules.

## Specification and architecture files updated

None. The authoritative contracts already require latest-root Copilot
selection and clean, reversible Factory removal. The new findings describe
missing implementation evidence and a code race rather than intended behavior,
so weakening those contracts would make the documentation less truthful.

## Code defects filed

- [RECON-0011](../findings/RECON-0011.md) — add installed repeated-turn Copilot
  conservation coverage.
- [RECON-0012](../findings/RECON-0012.md) — coordinate Factory removal with
  pending detached Pi captures.

## Validation results

- Focused usage, four-CLI end-to-end, initialization, and removal tests:
  **94 passed**.
- `spec-lint --spec-dir docs/spec`: exit 0; 0 errors, 0 warnings, 7 info.
- `arch-lint --docs-dir docs/`: exit 0; 0 errors, 2 pre-existing parse warnings.
- `mdformat` and `git diff --check`: passed for every new review artifact.
