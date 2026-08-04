---
title: Dispatch Safeguard Assurance Audit
date: 2026-08-04
baseline: 5219c64b6586b7606df346cac668d128bd3c21fe
requirements_head: 86c1d722708ad589d1a848c6edbd47145ea2fe50
assurance: high
risk_domains: [reliability, data_integrity]
---

# Dispatch Safeguard Assurance Audit

This planning audit applies UC-12 and BR-043 through BR-048 to the immutable
accepted-proposal baseline. Existing behavior is treated as delivered. A
verified gap below means missing assurance evidence or the smallest validation
needed to make that evidence meaningful; it does not reopen the safeguard's
design.

| Mechanism                               | Shipped contract                                                                                                                                          | Runtime implementation                                                                                                  | Automated evidence                                                                                                                  | Disposition and smallest remediation                                                                                                    |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Verify base before work                 | `branching-policy.md` requires `verify-base` as the first action and halt before reads, edits, or commits; `implementation-agent.md` carries the preamble | `factory/scripts/verify-base`; commit denial in shell and Pi git guardrails                                             | `test_guardrail_verify_base.py` proves marker-based commit denial, but does not execute stale-target or wrong-base preflight paths  | **Verified gap:** add direct negative-path tests proving failure before a marker is written; do not reimplement the preflight           |
| Declared base SHA                       | `branching-policy.md`, `implementation-agent.md`, and `dispatch-wave.ts` pass an expected base                                                            | `verify-base --expect-base`; `dispatch-wave.ts` freezes and injects the base                                            | No direct test requires an exact lowercase 40-character SHA or rejects an abbreviated declaration                                   | **Verified gap:** validate exact machine-consumed SHA syntax and cover it directly                                                      |
| Resolvable nested-agent addressing      | `dispatch-contract.md` and `reconciliation-agent.md` require a resolvable parent instance and forbid indefinite waiting                                   | Prompt-authored discipline; no runtime router belongs to this repository                                                | No focused contract test proves required clauses remain on every nested-dispatch-capable surface                                    | **Verified gap:** add canonical contract fixtures only; do not invent routing runtime                                                   |
| Pre-merge diff against target           | `branching-policy.md`, `git-workflow.md`, and `implementation-agent.md` require the gate                                                                  | `factory/scripts/premerge-check`; merge denial in shell and Pi git guardrails; `dispatch-wave.ts` invokes it            | No focused test executes stale/target-reverting, out-of-scope, or file-count-blowout failures and marker behavior                   | **Verified gap:** add direct four-mode and marker regression evidence; retain the shipped implementation unless a test exposes a defect |
| Evidence-derived unattended permissions | UC-04/BR-011 and `trigger` comments prohibit blanket bypass and bare-interpreter wildcards                                                                | `factory/scripts/trigger` builds scoped Claude and Copilot allow/deny argv                                              | Parser-contract tests do not inspect the actual background child argv or deny lists                                                 | **Verified gap:** add direct argv and deny-list tests for both CLIs; do not redesign permissions                                        |
| Dispatch scope cap and checkpoints      | `dispatch-contract.md`, `rules.md`, and `implementation-agent.md` require bounded file-disjoint outputs and checkpoints                                   | `dispatch-wave.ts` requires per-item scopes and gates merges; checkpoint judgment remains intentionally prompt-enforced | Pi end-to-end coverage exercises scoped dispatch, but there is no focused canonical contract test for split/checkpoint instructions | **Verified gap:** add contract evidence for the non-mechanical rule and retain existing scoped-wave runtime                             |

## Completion-criterion reconciliation

- All six mechanisms have one row with contract, implementation, evidence, and
  disposition.
- Full-SHA, halt-before-work, four-mode pre-merge, nested-addressing, actual
  permission argv, and scope/checkpoint evidence gaps are bounded to regression
  or contract tests plus exact-SHA validation.
- No delivered safeguard receives a retrospective implementation story.
- Proposal status remains `accepted` until the gap stories pass and final
  evidence is reconciled.
