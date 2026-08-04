# Reconciliation report — 2026-07-26

## Scope

- **Reviewed range:** base `3cd1f35e3cb884f7a99fabba06a9659f14652333`
  through QA-final head `5d73a5108f3a21225079e346445886296dfefba9` on
  branch `dev`, followed by this documentation-only reconciliation pass.
- **Code compared:** `factory/` (scripts, agents, skills, playbooks,
  `config/extensions`, `config/hooks`), `orchestrator/`, `config/`, and the
  installed `.pi/extensions/`, `.codex/hooks/`, `.claude/hooks/`,
  `.github/hooks/` wiring produced by `init-factory`.
- **Documentation compared:** arc42 chapters `05_building_block_view.md`,
  `06_runtime_view.md`, `08_crosscutting_concepts.md`,
  `09_architecture_decisions.md`, `12_glossary.md`, `README.md`,
  `beginner-intro.md`, `concepts.md`; ADRs `0001`–`0007`;
  `factory/docs/factory-guide.md` and the `docs/proposals/` and
  `docs/proposals/implemented/` guides; repo-root `README.md` and `AGENTS.md`; and the
  `backlog/` stories referenced by docs.
- **Repeat pass.** This is a fresh full truth-map rebuild, not only a check of
  the prior findings list. All fourteen prior RECON findings were re-verified
  against the code and documentation.

## Discrepancy table

| Finding                                                                                    | Artifact                                | Classification                 | Severity | Action                                                                         |
| ------------------------------------------------------------------------------------------ | --------------------------------------- | ------------------------------ | -------- | ------------------------------------------------------------------------------ |
| PreToolUse guardrail and `run-step` described as a two-CLI surface, omitting Codex and Pi. | [RECON-0013](../findings/RECON-0013.md) | Spec stale / terminology drift | Major    | Resolved across arc42, Factory guide, PRD, use cases, and interface contracts. |
| ADRs 0004–0007 marked `proposed` though fully implemented and load-bearing.                | [RECON-0014](../findings/RECON-0014.md) | Spec stale                     | Major    | Resolved; ADR frontmatter and decision index now say `accepted`.               |
| `05_building_block_view.md` §5.5 run-tests entry point omitted `--staged`.                 | `docs/05_building_block_view.md` §5.5   | Spec stale                     | Minor    | Resolved; interface row now lists all three modes.                             |
| `06_runtime_view.md` §6.2.5 deny-pattern list was an incomplete normative subset.          | `docs/06_runtime_view.md` §6.2.5        | Spec stale                     | Minor    | Resolved; the script is canonical and the prose list is explicitly exemplary.  |

## Prior finding verification (repeat pass)

A fresh diff of the contract surfaces — port interfaces, entity model, state
machines, validation rules, CLI/API surface, and building-block components —
was rebuilt from code and re-compared to the arc42 chapters and ADRs. The
prior fourteen findings are resolved; no regression was introduced by the
fixes that closed them.

- **RECON-0001 — resolved.** `merge-precommit-config` now derives the no-op
  marker from `--template` via `extract_marker_id()` (lines 75–103) rather
  than the hardcoded `id: index-lint`. The bidirectional splice ADR-0001
  documents is now true of the code.
- **RECON-0002 through RECON-0008 — resolved.** Re-confirmed: no broken
  `../factory/rulebooks/` links remain in `factory/agents/`; the
  cross-reference-format violation in `branching-policy.md` is fixed; the
  orchestrator test collection paths point at `factory/scripts`; the
  `technical-poc.md` anchors resolve; Pi child parent-correlation, Codex
  trust activation, Claude child conservation, the installer/remover
  ownership, the usage schema, and the four-CLI accounting rules all hold.
- **RECON-0009 — resolved.** Pi derives the canonical primary checkout from
  Git's shared common directory and propagates it to every child; nested
  records survive outer-worktree removal.
- **RECON-0010 — resolved.** Pi performs only the durable local staging write
  synchronously, then detaches persistence; human shutdown, `run_agent`, and
  `dispatch_wave` return before persistence.
- **RECON-0011 — resolved.** Copilot repeated-turn conservation coverage
  exists in `orchestrator/tests/test_usage_capture_copilot_e2e.py`.
- **RECON-0012 — resolved.** `remove-factory` coordinates with detached Pi
  captures via `--pending-usage=drain`/`--pending-timeout`, with a generation
  fence preventing late workers from recreating `.agent-factory/`.
- **RECON-0013 — resolved.** Canonical specifications, arc42 chapters, the
  glossary, and the Factory guide now describe Claude Code, GitHub Copilot CLI,
  and Codex as native-hook runtimes and Pi as the equivalent extension runtime.
- **RECON-0014 — resolved.** ADR-0004 through ADR-0007 and the decision index
  now consistently record their implemented status as `accepted`.

## Specification and architecture files updated

- `docs/05_building_block_view.md` — four-CLI guardrail and complete run-tests
  interface.
- `docs/06_runtime_view.md` — native-hook/Pi-extension split and exemplary
  deny-list wording.
- `docs/08_crosscutting_concepts.md` and `docs/12_glossary.md` — runtime input
  shapes and canonical four-CLI vocabulary.
- `factory/docs/factory-guide.md` — installation and guardrail wiring for all
  four runtimes.
- `docs/spec/prd.md`, UC-07, UC-08, and `interface-contracts.md` — aligned the
  normative installation and guardrail contracts.
- ADR-0004 through ADR-0007 and `docs/09_architecture_decisions.md` — status
  changed from `proposed` to `accepted`.

## Code defects filed

None. RECON-0013 and RECON-0014 are spec-stale/terminology-drift findings;
their proposed remediation is a documentation update, not a code change.

## New finding files

- [RECON-0013](../findings/RECON-0013.md) — resolved after the four-CLI
  terminology and contract updates.
- [RECON-0014](../findings/RECON-0014.md) — resolved after accepting the four
  implemented ADRs.

## Linter results

- `spec-lint --spec-dir docs/spec/`: exit 0; 0 errors, 0 warnings, 7 info
  across 19 spec files.
- `arch-lint --docs-dir docs/`: exit 0; 0 errors, 2 pre-existing
  `ARCH-PARSE` warnings, 0 info.
- Every updated Markdown file was formatted with
  `factory/scripts/mdformat --number`; `git diff --check` passed.
