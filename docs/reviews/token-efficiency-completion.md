---
title: Token-Efficiency Completion Evidence
date: 2026-08-04
session_control:
  assurance: elevated
  risk_domains: [reliability, operations]
dispatch:
  assurance: high
  risk_domains: [reliability, data_integrity]
---

# Token-Efficiency Completion Evidence

This report closes two separately traceable design origins without combining
their scope or governance. The session-control origin is
[`proposal-session-transcript-token-control.md`](../proposals/proposal-session-transcript-token-control.md),
with elevated assurance for reliability and operations. The dispatch origin is
[`agent-dispatch-token-efficiency.md`](../proposals/agent-dispatch-token-efficiency.md),
with high assurance for reliability and data integrity. All accepted criteria
below have passing observable evidence; deferred live token controls remain
deferred.

## Session-transcript proposal criteria

Each accepted completion criterion is assigned exactly once in this table.

| Criterion | Accepted outcome                                                                                                     | Passing observable evidence                                                                                                                                                                                                                          |
| --------- | -------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| STC-01    | The handoff convention defines the phase-boundary set, required handoff contents, and mandatory invocation.          | `factory/rulebooks/conventions/handoff-format.md`; `test_UC_11_contract_defines_boundaries_restart_and_same_phase_exemption` and the playbook boundary tests in `orchestrator/tests/test_handoff_contract.py` and `test_phase_boundary_contract.py`. |
| STC-02    | The Factory handoff skill is installed for every supported CLI and preserves dense, unambiguous information.         | `factory/skills/handoff/SKILL.md`; `test_UC_11_skill_preserves_dense_restart_contract_and_semantic_gate` and `test_UC_11_installation_exposes_handoff_skill_for_every_supported_cli`.                                                                |
| STC-03    | Handoff lint blocks missing or malformed structure, paths, exact SHAs, state, evidence, decisions, and next action.  | `factory/scripts/handoff-lint`; `test_UC_11_lint_reports_every_detectable_defect_in_one_run`, `test_UC_11_machine_consumed_shas_require_exact_lowercase_40_hex`, and the valid-handoff tracer in `test_handoff_contract.py`.                         |
| STC-04    | Agent results use summary-plus-path injection.                                                                       | `factory/rulebooks/conventions/report-format.md`; `test_report_convention_defines_exact_bounded_json_envelope` plus the `run_agent` and `dispatch_wave` runtime tests in `orchestrator/tests/test_child_result_envelope.py`.                         |
| STC-05    | Cache hygiene requires on-demand chunked reads, provider-qualified measurement, and no prose-restabilisation ritual. | `factory/rulebooks/conventions/cache-hygiene.md`; `test_UC_11_FR_K5_cache_hygiene_is_bounded_and_measurement_first`.                                                                                                                                 |
| STC-06    | Every listed multi-phase agent invokes handoff at exit and reads handoff artifacts on fresh entry.                   | The eight canonical agents listed in the proposal; `test_UC_11_agent_declares_handoff_skill`, `test_UC_11_agent_enters_fresh_session_from_bounded_durable_context`, and `test_UC_11_agent_exits_through_reviewed_handoff_and_stops`.                 |
| STC-07    | Greenfield and feature-addition playbooks mark every phase transition as a handoff.                                  | `factory/playbooks/greenfield-development.md` and `feature-addition.md`; `test_UC_11_playbook_marks_every_routed_transition` and `test_UC_11_playbook_phase_boundary_is_reviewed_hard_stop`.                                                         |
| STC-08    | Usage capture stores the three nullable derived signals with CLI/provider identity and capability.                   | `factory/scripts/usage-capture`; BR-042 derivation, nullability, persistence, and normalizer coverage in `orchestrator/tests/test_session_usage_signals.py`.                                                                                         |
| STC-09    | Retrospective guidance consumes the signals only in Caused Friction.                                                 | `factory/skills/retrospective/SKILL.md`; `test_UC_11_FR_K7_retrospective_consumes_signals_only_as_friction_evidence`.                                                                                                                                |
| STC-10    | A phase-gated session reports a late/early input ratio below the 11.3x baseline.                                     | The post-adoption retrospective in [Measured phase-gated retrospective](#measured-phase-gated-retrospective): 1.736x for the qualified capture, 84.6% below 11.3x.                                                                                   |

## Dispatch proposal criteria

Each accepted completion criterion is assigned exactly once in this table.

| Criterion | Accepted outcome                                                                                                    | Passing observable evidence                                                                                                                                                                                                 |
| --------- | ------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DTE-01    | All six mechanisms map to shipped contracts, runtime points, and passing evidence.                                  | The six passing rows in [`dispatch-safeguard-audit-2026-08-04.md`](dispatch-safeguard-audit-2026-08-04.md), reconciled by ST-0072 after ST-0069 through ST-0071.                                                            |
| DTE-02    | Wrong target or declared base halts before work, with exact 40-character machine state.                             | `factory/scripts/verify-base`; exact-SHA, stale-target, wrong-base, marker-clearing, and clean-success tests in `orchestrator/tests/test_dispatch_base_preflight.py`.                                                       |
| DTE-03    | Pre-merge blocks stale/target-reverting, out-of-scope, and file-count-blowout diffs.                                | `factory/scripts/premerge-check`; all blocking modes and clean marker success in `orchestrator/tests/test_premerge_check.py`.                                                                                               |
| DTE-04    | Nested dispatch uses resolvable parent instances and never waits indefinitely for an unreachable child.             | Canonical dispatch surfaces; `test_UC_12_BR_047_nested_dispatch_requires_resolvable_parent_instance` and `test_UC_12_BR_047_nested_dispatch_has_explicit_local_fallback`.                                                   |
| DTE-05    | Claude and Copilot unattended launches use scoped permissions without blanket bypass or bare-interpreter wildcards. | Actual `factory/scripts/trigger` child argv exercised by both tests in `TestBackgroundPermissionArgv` in `orchestrator/tests/test_trigger_background_permissions.py`.                                                       |
| DTE-06    | Whole-codebase work is split or checkpointed with independently verifiable scopes.                                  | Canonical dispatch contracts; `test_UC_12_BR_048_whole_codebase_work_is_split_or_checkpointed` and `test_UC_12_BR_048_dispatch_wave_preserves_mechanical_scope_evidence`.                                                   |
| DTE-07    | Proposal status and references reflect delivery without retrospective safeguard reimplementation.                   | ST-0072 changes both proposal statuses only after the mappings above pass; the dispatch audit retains the shipped contract/runtime points and replaces gap dispositions with test evidence rather than new implementations. |

## Measured phase-gated retrospective

The real Codex session `019fcc1a-1421-7862-8039-f649f3cf030b` entered the
Implementation phase by reading the authoritative Planning-to-Implementation
handoff and its named artifacts before dispatch. After the ST-0071 merge, the
capture event at `2026-08-04T11:00:28Z` persisted this qualified evidence in
`.agent-factory/usage/019fcc1a-1421-7862-8039-f649f3cf030b.jsonl`:

| Qualifier or signal    | Persisted value                                                  |
| ---------------------- | ---------------------------------------------------------------- |
| CLI                    | `codex`                                                          |
| Provider               | unavailable (`null`); not inferred from the model name           |
| Model                  | `gpt-5.6-sol`                                                    |
| Capability             | `full-cache`                                                     |
| Late/early input ratio | `1.7358340957174099` (1.736x rounded)                            |
| Baseline comparison    | 84.6% below 11.3x; the baseline is 6.51 times the observed ratio |

The provider qualifier is deliberately explicit even though unavailable:
BR-042 and ST-0068 require nullable provider metadata to remain null rather
than be guessed. The ratio itself is non-null and provider-native input data
has full-cache capability. This comparison is a retrospective observation,
not a causal attribution and never an input to a live stop, budget, dispatch,
or cache-restabilisation control.

## Closure

The evidence introduces no architecture decision and no scope expansion. The
specification already matches the delivered BR-042 nullable-provider behavior,
phase handoff contracts, bounded result envelopes, and dispatch assurance
rules. The two proposals remain separate design origins and can now truthfully
carry `implemented` status.
