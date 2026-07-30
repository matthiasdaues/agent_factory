# Reconciliation report — 2026-07-26 (delta pass)

## Scope

- **Reviewed range:** base `5d73a5108f3a21225079e346445886296dfefba9`
  through head `ba874ae9dcfeb062426d289bb5ee3ffda59c36ba` on branch `dev`
  (8 commits: `086d491`, `6c94217`, `488f44d`, `1bf179b`, `3819920`,
  `9726a89`, `07f5cce`, `04256d9`, plus `ba874ae`).

- **Prior pass:** [reconciliation-2026-07-26.md](reconciliation-2026-07-26.md)
  (range `3cd1f35..5d73a51`); resolved RECON-0001 through RECON-0014.

- **Delta file list** (39 paths):

  ```
  .gitignore
  HANDOFF.md
  config/model.conf
  docs/05_building_block_view.md
  docs/06_runtime_view.md
  docs/08_crosscutting_concepts.md
  docs/09_architecture_decisions.md
  docs/12_glossary.md
  docs/CONTEXT-MAP.md
  docs/adr/0004-pi-subagent-invocation-via-subprocess-spawn.md
  docs/adr/0005-openrouter-model-discovery-for-model-conf.md
  docs/adr/0006-research-flat-storage-and-validation-pipeline.md
  docs/adr/0007-normalize-runtime-usage-through-cli-adapters.md
  docs/findings/BUG-0002.md
  docs/findings/BUG-0003.md
  docs/findings/RECON-0013.md
  docs/findings/RECON-0014.md
  docs/findings/SEC-0004.md
  docs/reviews/reconciliation-2026-07-26.md
  docs/spec/prd.md
  docs/spec/supplementary_specs/interface-contracts.md
  docs/spec/traceability.json
  docs/spec/use_cases/UC-07-block-a-dangerous-git-command.md
  docs/spec/use_cases/UC-08-initialize-agent-factory-into-a-project.md
  docs/spec/use_cases/system-use-cases.md
  factory/config/extensions/pi-usage.ts
  factory/config/hooks/capture-codex-usage.sh
  factory/config/hooks/capture-copilot-usage.sh
  factory/config/hooks/capture-usage.sh
  factory/docs/factory-guide.md
  factory/docs/proposals/factory-cli-security-hardening.md
  factory/docs/proposals/token-usage-tracking.md
  factory/docs/proposals/usage-processing-and-storage.md
  factory/scripts/usage-capture
  factory/scripts/usage-capture-lifecycle
  orchestrator/tests/test_init_factory_usage_capture.py
  orchestrator/tests/test_usage_capture.py
  orchestrator/tests/test_usage_capture_e2e.py
  ```

- **Focus areas (per request):** usage-capture schema tightening (BUG-0003
  raw capture schema + transcript-provided models), model tier config
  (`config/model.conf` Codex and Pi rows), Pi extension exports
  (`pi-usage.ts` extension-factory contract), and re-verification of the
  RECON-0013/0014 fixes landed in `086d491`.

- **Out of scope by request:** surfaces unchanged in the delta were not
  re-walked. Prior findings RECON-0001 through RECON-0012 were not re-checked
  individually because none of their touched files recur in this delta; they
  remain `resolved` from the 2026-07-26 pass.

## Truth-map summary (delta contract surfaces)

| Contract surface           | Code source (delta)                                                                               | Spec source                                                                                      | Result                                                     |
| -------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ---------------------------------------------------------- |
| Usage record schema        | `factory/scripts/usage-capture` (`UsageRecord`, `NormalizedTranscript`)                           | `entity-model.md`; `token-usage-tracking.md`; `interface-contracts.md`                           | Match (see note on `MODEL_MATRIX_ENTRY` below)             |
| Model attribution (BR-036) | `usage-capture` normalizers + `_capture` (`args.model or transcript.model`)                       | `system-use-cases.md § Usage capture attribution`; `interface-contracts.md`; `traceability.json` | Match                                                      |
| Git context enrichment     | `usage-capture _git_context`; `pi-usage.ts gitContext`; `capture-*.sh`; `usage-capture-lifecycle` | `token-usage-tracking.md` Outcome table                                                          | Match                                                      |
| Model tier router          | `config/model.conf` (`copilot.*`, `codex.*`, `pi.*`)                                              | `ADR-0005`; `entity-model.md MODEL_MATRIX_ENTRY`                                                 | **Drift — RECON-0015, RECON-0016**                         |
| Pi extension-factory       | `factory/config/extensions/pi-usage.ts` (default export)                                          | `test_init_factory_usage_capture.py` (new contract test)                                         | Match                                                      |
| Four-CLI guardrail         | `factory/config/hooks/block-dangerous-git.sh` (unchanged in delta)                                | `05/06/08/12`, `factory-guide.md`, PRD, UC-07/08, `interface-contracts.md`                       | Match (RECON-0013 holds)                                   |
| ADR status                 | `docs/adr/0004..0007` frontmatter + `09_architecture_decisions.md`                                | same                                                                                             | Match (RECON-0014 holds); ADR-0005 body stale — RECON-0015 |

## Discrepancy table

| Finding                                                                                                              | Artifact                                | Classification | Severity | Action (proposed — not committed)                                                                                                   |
| -------------------------------------------------------------------------------------------------------------------- | --------------------------------------- | -------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| ADR-0005 Context says only `copilot.*` rows exist; `model.conf` ships `copilot.*`, `codex.*`, and `pi.*`.            | [RECON-0015](../findings/RECON-0015.md) | Spec stale     | Minor    | Refresh ADR-0005 Context to name all three configured CLI tier blocks and drop the "adding Pi" future tense.                        |
| Entity-model `MODEL_MATRIX_ENTRY.cli` lists `claude \| copilot`; `model.conf` row keys are `copilot \| codex \| pi`. | [RECON-0016](../findings/RECON-0016.md) | Spec stale     | Minor    | Set the `cli` enum to `copilot \| codex \| pi` (the `model.conf` row keys), with a note that Claude Code resolves outside the file. |

### Advisory (pre-existing, not filed — unchanged in delta)

`config/model.conf` header comment cites `ADR-0020, ADR-0021`, but
`docs/adr/` contains only `0001`–`0007`; no `ADR-0020` or `ADR-0021`
exists. The header line was not modified in this delta (only the
`codex.*` block and `pi.*` values were), so it is out of the requested
delta scope and is **not** filed as a RECON finding. Recommended for the
implementation agent to retarget the reference to `ADR-0005`
(the governing decision for the tier router) and/or `ADR-0007` as
applicable.

## Prior finding verification (repeat pass, delta-scoped)

Only the prior findings whose touched files recur in the delta were
re-verified, per the scoping instruction. A fresh truth-map diff was run
across the delta contract surfaces (table above), not merely the prior
list.

- **RECON-0013 — still resolved.** The four-CLI guardrail language landed
  in `086d491` (glossary, arc42 05/06/08, factory-guide, PRD, UC-07/08,
  interface-contracts) is intact. The usage-capture changes in this delta
  (adding `--branch`/`--commit` git detection to the three native hooks
  and the Pi extension) are orthogonal to the guardrail and introduced no
  regression: `block-dangerous-git.sh` is unchanged, still reads all three
  native JSON shapes, and Pi still enforces via its extension.
- **RECON-0014 — still resolved.** ADR-0004 through ADR-0007 frontmatter
  and the `09_architecture_decisions.md` Decision Index all read
  `accepted`. The delta did not regress the statuses. The ADR-0005 *body*
  drift is filed separately as RECON-0015 (a new finding, not a regression
  of the status field itself).
- **RECON-0001 through RECON-0012 — not re-checked.** None of their
  touched files recur in this delta; they remain `resolved` from the
  2026-07-26 full pass.

## New-claim verification (BUG-0003, SEC-0004, BUG-0002)

- **BUG-0003 — resolved, verified accurate.** Every transcript normalizer
  (`ClaudeCodeNormalizer`, `CopilotNormalizer`, `CodexNormalizer`,
  `PiNormalizer`) now returns the latest non-empty native model id on
  `NormalizedTranscript.model`; `_capture` persists
  `args.model or transcript.model`, so explicit invocation context takes
  precedence and transcript-derived attribution is the fallback. The
  contract test `test_every_supported_cli_extracts_latest_transcript_model`
  asserts `set(fixtures) == set(usage_capture.SUPPORTED_CLIS)`
  (`SUPPORTED_CLIS = ("claude-code", "copilot", "codex", "pi")`), so
  adding a CLI without a model fixture fails. Capture-boundary tests
  `test_capture_persists_transcript_model_when_not_explicit` and
  `test_explicit_model_overrides_transcript_model` cover both branches.
  `system-use-cases.md § Usage capture attribution` (BR-036) and the
  new `interface-contracts.md` usage-capture row describe this exactly;
  `traceability.json` carries BR-036. No drift.
- **SEC-0004 — open, not in code-fix scope of this delta.** The finding
  (path traversal in `run_agent`/`dispatch_wave` agent-name resolution) is
  newly filed (`07f5cce`) and `status: open`. No code in the delta
  addresses it; `run-agent.ts`/`dispatch-wave.ts` were not modified. The
  spec does not yet describe the required canonical-loader containment
  control. This remains an open handoff to the implementation agent; it is
  not a reconciliation discrepancy (the spec correctly does not yet claim
  a control the code lacks).
- **BUG-0002 — open, not addressed by this delta.** Caller-side
  persona/model resolution in `dispatch_wave` remains `open`; no code in
  the delta changes `dispatch-wave.ts`. The model-tier delta
  (`config/model.conf`) does not affect it. Still an open handoff.

## Specification and architecture files proposed for update (not committed)

Per the reconciliation pause point, no doc edits were committed. Proposed
fix directions live in the finding files.

- `docs/adr/0005-openrouter-model-discovery-for-model-conf.md` — refresh
  the Context paragraph to name `copilot.*`, `codex.*`, and `pi.*` as
  shipped tier blocks (RECON-0015).
- `docs/spec/supplementary_specs/entity-model.md` — correct the
  `MODEL_MATRIX_ENTRY.cli` enum to `copilot | codex | pi` (RECON-0016).

## Code defects filed

None. Both new findings are spec-stale (documentation lagged the
`config/model.conf` delta); the proposed remediation is a documentation
update, not a code change. The model-conf header ADR-0020/0021 reference
is an advisory code-comment defect left for the implementation agent
(see Advisory above).

## New finding files

- [RECON-0015](../findings/RECON-0015.md) — `open`. ADR-0005 Context
  stale against the shipped `model.conf` tier blocks.
- [RECON-0016](../findings/RECON-0016.md) — `open`. Entity-model
  `MODEL_MATRIX_ENTRY.cli` enum stale against `model.conf` row keys.

## Linter results

- `spec-lint --spec-dir docs/spec/`: exit 0; 0 errors, 0 warnings,
  10 info across 19 spec files (up from 7 info — the three new infos are
  the FMT001 non-EARS heuristic on the BR-036 attribution requirements in
  `system-use-cases.md`; still informational, not warnings).
- `arch-lint --docs-dir docs/`: exit 0; 0 errors, 2 pre-existing
  `ARCH-PARSE` warnings, 0 info — unchanged from the prior pass.
- No files were modified or formatted in this pass (pause point); the
  linted tree is the delta head as-is.
