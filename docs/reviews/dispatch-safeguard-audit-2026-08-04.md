---
title: Dispatch Safeguard Assurance Audit
date: 2026-08-04
baseline: 5219c64b6586b7606df346cac668d128bd3c21fe
requirements_head: 86c1d722708ad589d1a848c6edbd47145ea2fe50
assurance: high
risk_domains: [reliability, data_integrity]
---

# Dispatch Safeguard Assurance Audit

This completed audit applies UC-12 and BR-043 through BR-048 to the immutable
accepted-proposal baseline. Existing behavior remains the implementation
baseline. ST-0069 through ST-0071 supplied the missing automated assurance
without reopening or retrospectively reimplementing the six safeguards.

| Mechanism                               | Shipped contract                                                                                                                                           | Runtime implementation                                                                                                   | Passing automated evidence                                                                                                                                                                                                      | Disposition                                                                                                     |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Verify base before work                 | `branching-policy.md` requires `verify-base` as the first action and halt before reads, edits, or commits; `implementation-agent.md` carries the preamble. | `factory/scripts/verify-base`; commit denial in shell and Pi git guardrails.                                             | `test_UC_12_BR_045_stale_target_blocks_and_clears_old_marker` and `test_UC_12_BR_045_wrong_declared_base_blocks_and_clears_old_marker` in `test_dispatch_base_preflight.py`, plus existing marker-based commit-denial coverage. | **Pass:** ST-0069 added direct negative-path evidence; the shipped preflight remains in place.                  |
| Declared base SHA                       | `branching-policy.md`, `implementation-agent.md`, and `dispatch-wave.ts` pass an expected base.                                                            | `verify-base --expect-base`; `dispatch-wave.ts` freezes and injects the base.                                            | Exact, abbreviated, noncanonical, unknown, and valid object-name cases in `test_dispatch_base_preflight.py`, including `test_UC_12_BR_044_valid_exact_base_writes_matching_marker`.                                             | **Pass:** machine-consumed base declarations require exact lowercase 40-character SHAs.                         |
| Resolvable nested-agent addressing      | `dispatch-contract.md` and `reconciliation-agent.md` require a resolvable parent instance and forbid indefinite waiting.                                   | Prompt-enforced local fallback; no repository runtime router is required.                                                | `test_UC_12_BR_047_nested_dispatch_requires_resolvable_parent_instance` and `test_UC_12_BR_047_nested_dispatch_has_explicit_local_fallback` in `test_dispatch_contract_assurance.py`.                                           | **Pass:** ST-0071 proves every canonical nested-dispatch surface and preserves the intentional contract seam.   |
| Pre-merge diff against target           | `branching-policy.md`, `git-workflow.md`, and `implementation-agent.md` require the gate.                                                                  | `factory/scripts/premerge-check`; merge denial in shell and Pi git guardrails; `dispatch-wave.ts` invokes it.            | Stale/target-reverting, out-of-scope, file-count-blowout, clean marker, and invocation-error cases in `test_premerge_check.py`.                                                                                                 | **Pass:** ST-0069 supplies all required blocking modes without replacing the shipped gate.                      |
| Evidence-derived unattended permissions | UC-04/BR-011 and `trigger` comments prohibit blanket bypass and bare-interpreter wildcards.                                                                | `factory/scripts/trigger` builds scoped Claude and Copilot allow/deny argv.                                              | `TestBackgroundPermissionArgv` exercises the real public background path for both CLIs in `test_trigger_background_permissions.py`.                                                                                             | **Pass:** ST-0070 proves actual scoped argv, dangerous-Git denials, and allowed repository validation commands. |
| Dispatch scope cap and checkpoints      | `dispatch-contract.md`, `rules.md`, and `implementation-agent.md` require bounded file-disjoint outputs and checkpoints.                                   | `dispatch-wave.ts` requires per-item scopes and gates merges; checkpoint judgment remains intentionally prompt-enforced. | `test_UC_12_BR_048_whole_codebase_work_is_split_or_checkpointed`, `test_UC_12_BR_048_dispatch_wave_preserves_mechanical_scope_evidence`, and the no-live-budget test in `test_dispatch_contract_assurance.py`.                  | **Pass:** ST-0071 proves the non-mechanical rule and retains existing scoped-wave enforcement.                  |

## Completion-criterion reconciliation

- All six mechanisms retain one row with their shipped contract and runtime
  implementation plus passing automated evidence.
- ST-0069 supplies exact-full-SHA, halt-before-work, and four-mode pre-merge
  regression evidence; ST-0070 supplies actual permission-argv evidence;
  ST-0071 supplies nested-addressing and bounded-scope contract evidence.
- No delivered safeguard received a retrospective implementation story, and no
  live token-budget runtime was added.
- The dispatch proposal may move from `accepted` to `implemented` because every
  recorded assurance gap now has passing evidence reconciled in
  [`token-efficiency-completion.md`](token-efficiency-completion.md).
