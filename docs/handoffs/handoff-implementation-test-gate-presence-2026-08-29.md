# Phase Handoff

## Boundary

Outgoing phase: planning
Incoming phase: implementation
Boundary: planning -> implementation

## Repository state

Checkout: /home/matthiasdaues/Documents/datenschoenheit/agent_factory
Branch: dev
HEAD: b2a53cdcb69d2b61c823a65066923d34c5ebb680
Upstream: agent_factory/dev
Upstream SHA: bc92ba14fbeb59281f4614f4bbb0582072ba3e40
Ahead: 16
Behind: 0
Working tree: modified `factory/INDEX.yaml`, `factory/config/AGENTS.md` (user-owned); untracked `backlog/ST-0147.md` through `backlog/ST-0158.md` (12 new story files, pending commit); untracked `docs/handoffs/handoff-merge-testing-initiatives-2026-08-28.md`, `docs/handoffs/handoff-test-framework-priority-fix-2026-08-28.md`, `docs/proposals/test-gate-presence-over-test-execution.md`
Retained work: worktree at `.current-work/worktrees/test-gate-presence-over-test-execution` on branch `test-gate-presence-over-test-execution` (HEAD ebf85c51543bc2b3fd497d4b5db0457390fbaf44, clean working tree); worktree at `.current-work/worktrees/feature/newcomer-onboarding-and-incremental-brownfield` (separate feature, do not touch)

## Decisions and open items

Decisions: the stakeholder approved the 12-story backlog (ST-0147 through ST-0158) without changes. MoSCoW priorities (10 must-have, 2 should-have) and dependency order were accepted as presented. The instruction is to hand off to the implementation-agent for dispatch.

The feature merges two proposals:

1. **Test Gate Presence over Test Execution** — Factory stops owning test execution. Deletes `factory/scripts/run-tests` and `factory/scripts/mutation-analysis`. Projects declare test commands in `docs/charter/testing.yaml`. Gates are exit-code-only. Proposal at `.current-work/worktrees/test-gate-presence-over-test-execution/docs/proposals/test-gate-presence-over-test-execution.md`.

2. **Contract-Traced Testing Strategy** — superseded and folded into test-gate-presence. Wires qa-strategy-from-spec, kit-manager, developer-agent, and mutation-analysis skill into a closed loop where the charter is authority and the repo is ground truth. Proposal at `docs/proposals/contract-traced-testing-strategy.md` (status: superseded, committed on dev at b2a53cd).

The specification work (feature file with 14 Rules and 49 Scenarios, gaps report, updates to UC-09, ADR-0003, ADR-0012, prd.md, UC-10, interface-contracts, validation-rules) is complete and committed on the feature branch at ebf85c5. Five proposal reviews resolved all 17 findings (PROP-01 through PROP-17).

Open items: the 12 new story files in `backlog/` are untracked — the incoming session should commit them before dispatching. The earlier handoff `docs/handoffs/handoff-test-framework-priority-fix-2026-08-28.md` is superseded by this feature (it proposed fixing `run-tests` to defer to project config; this feature deletes the script entirely).

## Backlog

12 stories, 4 EPICs, 5 dispatch waves.

### Epic: Test Gate Infrastructure (6 stories)

| ID      | Title                                                               | Tier     | Priority  | Deps    |
| ------- | ------------------------------------------------------------------- | -------- | --------- | ------- |
| ST-0147 | Delete run-tests and mutation-analysis scripts                      | economy  | must-have | —       |
| ST-0148 | Create charter-testing.yaml template and Factory's own testing.yaml | economy  | must-have | ST-0147 |
| ST-0149 | Remove test hook from pre-commit config                             | economy  | must-have | ST-0148 |
| ST-0150 | Update block-dangerous-git.sh to read charter allowlist             | standard | must-have | ST-0148 |
| ST-0151 | Update FSM gate conditions to resolve test_command from charter     | standard | must-have | ST-0148 |
| ST-0152 | Update implementation-agent for two-gate default                    | economy  | must-have | ST-0147 |

### Epic: Test Regime Detection (2 stories)

| ID      | Title                                     | Tier     | Priority  | Deps    |
| ------- | ----------------------------------------- | -------- | --------- | ------- |
| ST-0153 | Create detect-test-regime skill           | standard | must-have | ST-0148 |
| ST-0154 | Wire detect-test-regime into init-factory | standard | must-have | ST-0153 |

### Epic: Charter Layer Bindings (1 story)

| ID      | Title                                         | Tier     | Priority    | Deps    |
| ------- | --------------------------------------------- | -------- | ----------- | ------- |
| ST-0155 | Update kit-manager to populate layer bindings | standard | should-have | ST-0148 |

### Epic: QA Strategy Traceability (3 stories)

| ID      | Title                                                                  | Tier     | Priority    | Deps             |
| ------- | ---------------------------------------------------------------------- | -------- | ----------- | ---------------- |
| ST-0156 | Rewrite qa-strategy-from-spec for charter-grounded contract ownership  | strong   | must-have   | ST-0148, ST-0155 |
| ST-0157 | Update developer-agent for test-harness mismatch feedback              | economy  | should-have | ST-0156          |
| ST-0158 | Rewrite mutation-analysis skill with setup guidance and classification | standard | must-have   | ST-0156          |

### Dispatch waves

- **Wave 1:** ST-0147
- **Wave 2:** ST-0148, ST-0152
- **Wave 3:** ST-0149, ST-0150, ST-0151, ST-0153, ST-0155
- **Wave 4:** ST-0154, ST-0156
- **Wave 5:** ST-0157, ST-0158

## Artifacts

- `.current-work/worktrees/test-gate-presence-over-test-execution/docs/proposals/test-gate-presence-over-test-execution.md`
- `.current-work/worktrees/test-gate-presence-over-test-execution/docs/spec/test-gate-presence.feature`
- `.current-work/worktrees/test-gate-presence-over-test-execution/docs/spec/test-gate-presence-gaps.md`
- `docs/proposals/contract-traced-testing-strategy.md` (superseded)
- `backlog/ST-0147.md` through `backlog/ST-0158.md`
- `docs/spec/use_cases/UC-09-run-tests-via-hook.md`
- `docs/spec/prd.md`
- `docs/spec/supplementary_specs/validation-rules.md`
- `docs/spec/supplementary_specs/interface-contracts.md`
- `docs/spec/use_cases/UC-10-invoke-a-factory-agent-under-pi.md`
- `docs/adr/0003-test-execution-via-hooks.md`
- `docs/adr/0012-dispatcher-owned-semantic-gate-loop.md`

## Gate and verification evidence

Gates: backlog-lint reports 0 errors, 16 warnings (all VR-028: outputs match existing files — expected since most stories modify existing files). Proposal review passed (5 review passes, 17 findings PROP-01 through PROP-17, all resolved). Spec-review passed (6 findings SPEC-012 through SPEC-017, all resolved at ebf85c5). All pre-commit hooks pass on the feature branch.

Verification: backlog covers all 14 actor-goal rows from the gaps report. All 27 completion criteria from the proposal are traceable to at least one story's acceptance criteria. No stories created for explicitly deferred scope. Dependency graph is a DAG (backlog-lint acyclicity check passed).

## Suggested skills

- `implement-issue` — the skill invoked by each developer-agent subagent to implement individual stories via TDD
- `commit` — compose conventional commit messages for story implementations
- `spec-feedback` — invoked by developer-agent when implementation reveals spec drift (especially relevant for ST-0156, ST-0157)
- `validate` — run all deterministic gates mid-session without committing
- `handoff` — create handoff document if context runs out mid-implementation

## Next action

Commit the 12 backlog story files (ST-0147 through ST-0158) on the feature branch. Then spawn the implementation-agent with the backlog, starting from Wave 1 (ST-0147). The implementation-agent reads the backlog, resolves the dependency graph, and dispatches developer-agent subagents wave by wave. Each subagent implements one story using TDD on its own feature branch.

## Semantic review

Reviewer: pending assignment
Status: pending
Evidence: pending
