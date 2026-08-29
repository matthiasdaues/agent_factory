# Phase Handoff

## Boundary

Outgoing phase: planning
Incoming phase: implementation
Boundary: planning -> implementation

## Repository state

Checkout: /home/matthiasdaues/Documents/datenschoenheit/agent_factory
Branch: dev
HEAD: 00fd2ac6ce6940d6df30df3388291f4277a156f1
Upstream: agent_factory/dev
Upstream SHA: bc92ba14fbeb59281f4614f4bbb0582072ba3e40
Ahead: 15
Behind: 0
Working tree: modified `factory/config/AGENTS.md` (user-owned); untracked `docs/handoffs/handoff-test-framework-priority-fix-2026-08-28.md`, `docs/proposals/contract-traced-testing-strategy.md`, `docs/proposals/test-gate-presence-over-test-execution.md` (user-owned)
Retained work: worktree at `.current-work/worktrees/test-gate-presence-over-test-execution` on branch `test-gate-presence-over-test-execution` (HEAD 80c796d68b03d62684729e34080fbbeb824977a2, 8 commits, clean working tree); worktree at `.current-work/worktrees/feature/newcomer-onboarding-and-incremental-brownfield` (separate feature, do not touch)

## Decisions and open items

Decisions: two testing proposals must be merged into a single coherent initiative before implementation planning begins. The stakeholder decided this after reviewing both documents. The two proposals are:

1. **Test Gate Presence over Test Execution** (`docs/proposals/test-gate-presence-over-test-execution.md`, status: accepted). Factory stops owning test execution. `factory/scripts/run-tests` and `factory/scripts/mutation-analysis` are deleted. Projects declare test commands in `docs/charter/testing.yaml`. Factory reads the charter for FSM gates, agent allowlists, and hook wiring. Gate contract is exit-code-only. A `detect-test-regime` skill scans for existing test entrypoints during onboarding. This proposal has completed the feature-addition playbook through spec-review: specification updated across 7 documents, 2 new files (feature file with 29 scenarios, gaps report with 4 gaps), 6 spec-review findings resolved and committed. Full specification work is on branch `test-gate-presence-over-test-execution`.

2. **Sustainable Testing Regime** (`docs/proposals/sustainable-testing-regime.md`, status: open). Consolidates Factory's own ~1,000 pytest suite into a five-layer ownership model (deterministic linters, acceptance tests, contract tests, integration tests, end-to-end smoke). Targets ~300–420 cases with explicit contract ownership per layer. Seven consolidation rules, five verification steps. Scopes four domains: research (155 functions), usage-capture (128), dispatch (124), init-factory (52). Three review passes complete, all findings resolved, all 8 checks pass.

The interaction points that motivate the merge:

- Sustainable-testing-regime's boundary reference `factory/scripts/run-tests` is deleted by test-gate-presence. The boundary file and any consolidation stories referencing `run-tests` behavior need updating.
- The five-layer portfolio's acceptance-test layer aligns with the `.feature` files written during test-gate-presence specification (10 rules, 29 scenarios for the test-gate feature). These are the first `.feature` files in the repository.
- Test-gate-presence introduces `docs/charter/testing.yaml` as the project's test declaration. Factory itself needs a `testing.yaml` for its own test suite — this is where sustainable-testing-regime's consolidated suite gets declared.
- Mutation testing: test-gate-presence removes `factory/scripts/mutation-analysis` and moves mutation testing to project-owned responsibility. Sustainable-testing-regime explicitly defers mutation-testing infrastructure. These align and should be stated once.
- The dispatcher gate sequence was reduced from three gates (crap-score, mutation-analysis, dependency-check) to two (crap-score, dependency-check) by test-gate-presence. Sustainable-testing-regime's dispatch domain consolidation must account for this.

Open items: the incoming session must decide how to merge — options include folding sustainable-testing-regime into test-gate-presence as an expanded scope (one proposal, one feature branch, one planning pass), splitting into a sequenced pair (test-gate-presence implements first, sustainable-testing-regime follows and updates its boundary references), or extracting a new unified proposal that supersedes both. The stakeholder should be asked.

## Artifacts

- docs/proposals/test-gate-presence-over-test-execution.md
- docs/proposals/sustainable-testing-regime.md
- docs/spec/use_cases/UC-09-run-tests-via-hook.md
- docs/spec/prd.md
- docs/spec/supplementary_specs/validation-rules.md
- docs/spec/supplementary_specs/interface-contracts.md
- docs/spec/use_cases/UC-10-invoke-a-factory-agent-under-pi.md
- docs/adr/0003-test-execution-via-hooks.md
- docs/adr/0012-dispatcher-owned-semantic-gate-loop.md
- .current-work/worktrees/test-gate-presence-over-test-execution/docs/spec/test-gate-presence.feature
- .current-work/worktrees/test-gate-presence-over-test-execution/docs/spec/test-gate-presence-gaps.md
- docs/spec/actor-goal-list.md
- docs/spec/todos.md
- docs/spec/use_cases/UC-07-block-a-dangerous-git-command.md
- factory/rulebooks/conventions/testing-strategy.md
- docs/handoffs/handoff-test-framework-priority-fix-2026-08-28.md

## Gate and verification evidence

Gates: spec-lint clean on all specification updates; all pre-commit hooks pass (mdformat, ruff, link-check, spec-lint, arch-lint, statemachine-lint) at commits d8d4399 and 80c796d on the feature branch. Proposal review for test-gate-presence passed (10 findings, all resolved across two review passes). Proposal review for sustainable-testing-regime passed (3 findings, all resolved, 8/8 checks pass on final pass). Spec-review for test-gate-presence passed (6 findings SPEC-012 through SPEC-017, all resolved at 80c796d).

Verification: test-gate-presence specification verified against proposal completion criteria by spec-review-agent — traceability confirmed between proposal, spec docs, feature file, and gaps report. Sustainable-testing-regime reviewed at e4ea2c70e11ee827e24642d822ef56184ffe91c7 — five-layer portfolio reconciled with boundary convention, all completion criteria mechanically verifiable.

## Next action

Read both proposals in full, identify the merge strategy (ask the stakeholder if unclear), and produce a single planning-ready design that covers both the boundary fix (Factory stops owning test execution) and the suite consolidation (Factory's own tests reorganized under explicit contract ownership). Begin with the interaction points listed in Decisions; resolve each as a concrete design choice before proceeding to backlog breakdown.

## Semantic review

Reviewer: pending assignment
Status: pending
Evidence: pending
