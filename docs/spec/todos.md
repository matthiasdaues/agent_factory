# Todos — Factory Flow Control

Deferred decisions and named gaps found while reverse-engineering this specification from `factory/`'s code, per [rules.md § Todos](../../.agent-factory/factory/rulebooks/rules.md#todos). None of these block the mechanisms documented in [../~archive/spec/use_cases/](../~archive/spec/use_cases/) — each is a known, intentional gap in the current implementation, not a defect this spec papers over.

## T-01: No CLI-failure classification in `trigger`

`factory/scripts/trigger` returns the invoked CLI's raw exit code. It does not distinguish an auth failure from a config error from a genuine task failure, the way `orchestrator`'s `CopilotAdapter` does (regex-matched stderr, `orchestrator` ADR-0002). A non-zero exit today means: read the output, do not auto-retry. Named in [`factory/skills/run-step/SKILL.md` § What this deliberately does not do (yet)](../../.agent-factory/factory/skills/run-step/SKILL.md#what-this-does-not-read). Fold classification in if it turns out to matter in practice — not built ahead of a real case (YAGNI).

- [ ] Decide whether `trigger` should classify failures itself, or whether that stays a caller-side concern.

## T-02: No concurrent-user lock on the marker

- status: resolved

Workstream state uses immutable identity records under `.agent-factory/workstreams/`. No mutable marker file exists; concurrency is handled by the filesystem.

## T-03: `script_exit_zero` condition type — resolved

- status: resolved

The precondition evaluator in `engine/eligibility.py` resolves `test_command` from `docs/testing.yaml` directly. Exit-code-only contract: zero passes, nonzero fails.

## T-04: `halt_conditions` types other than `max_iterations` are unenforced

- status: resolved

No halt conditions exist in the current model. The eligibility engine uses precondition evaluation, not iteration-capped retry loops.

## T-05: Copilot CLI's three-word `shell(...)` wildcard syntax unconfirmed

`trigger`'s `COPILOT_ALLOW_TOOLS`/`COPILOT_DENY_TOOLS` include entries like `shell(uv run pytest:*)`. The two-word-prefix form (`shell(git commit:*)`) is confirmed against GitHub's own documented example; the three-word form follows the same pattern but has not been verified against Copilot CLI itself.

- [ ] Verify the three-word form against a real Copilot CLI invocation; adjust the allowlist syntax if it is rejected.

## T-06: Multi-framework test orchestration not yet supported

- status: superseded

Superseded by the Test Gate Presence over Test Execution feature ([proposal](../proposals/test-gate-presence-over-test-execution.md)). Factory no longer detects or constructs test commands; `.agent-factory/factory/scripts/run-tests` is deleted. Framework selection is entirely the project's responsibility, declared in `docs/testing.yaml`. Multi-framework orchestration, if needed, is the project's own test entrypoint's concern.

## T-07: `verify-base` and `premerge-check` were prompt-required, not hook-enforced

- status: resolved

`.agent-factory/factory/scripts/verify-base` and `.agent-factory/factory/scripts/premerge-check` now write a marker file on success; `block-dangerous-git.sh` denies `git commit` in a marker-less worktree and `git merge <branch>` without a matching `premerge-check-ok` marker. Mechanical enforcement, not a prompt instruction. Still open: `Edit`/`Write` inside a marker-less worktree aren't gated, only `git commit` — a subagent can still read/edit before verifying, just can't persist a commit.

## T-08: Pi guardrail is an extension, weaker than the native hook path

Under Pi the git-safety guardrail is a project-local extension loaded only after project trust resolves, not a native `PreToolUse` hook. A non-interactive run that has not saved trust (or is not launched with `-a`) can skip it. `run_agent` passes `-a` on every spawn so its children load the guardrail, but the parent Pi session's own guardrail still depends on trust. Documented in [factory/docs/factory-guide.md § CLI safety guardrails](../../.agent-factory/factory/docs/factory-guide.md#cli-safety-guardrails).

- [ ] Decide whether to recommend the global `~/.pi/agent/extensions/` install or a container as the stronger default for Pi.

## T-09: `run_agent` tier resolution duplicates or shells the Python resolver

`run-agent.ts` is TypeScript; the canonical tier→model resolver (`matrix-lint.parse_matrix`, reused by `trigger`) is Python. `run-agent.ts` must either re-implement the `model.conf` parse in TS or shell out to a small Python resolver to keep a single source of truth. See [ADR-0004](../adr/0004-pi-subagent-invocation-via-subprocess-spawn.md).

- [ ] Confirm the chosen resolution path holds up once OpenRouter model IDs (ADR-0005) populate `pi.*`.

## T-10: `dispatch_wave` built after the `run_agent` primitive reaches readiness

Per the build order, the `run_agent` single-agent primitive shipped and was validated first; `dispatch_wave` (parallel, worktree-isolated dispatch with `premerge-check` integration, FR-J4) followed. The tool takes one caller-planned, file-disjoint wave — output-file overlap and dependency ordering stay with the calling agent, as `implementation-agent` documents.

- [x] Land `dispatch_wave` and its two-parallel-agent validation.

## T-11: PRD does not reflect the factory's current state

`docs/spec/prd.md` was written during the initial Factory Flow Control specification pass. The factory has grown substantially since then (Pi invocation, dispatch safeguards, research playbooks, token-usage tracking, newcomer onboarding). The PRD needs a reconciliation pass to reflect the system as-built. Not blocking current feature work — the accepted proposal serves as the requirements source for newcomer onboarding.

- [ ] Reconcile `docs/spec/prd.md` with the factory's current capabilities and shipped features.

## Referenced from

- [validation-rules.md](supplementary_specs/validation-rules.md)
- [entity-model.md](supplementary_specs/entity-model.md)
- [docs/findings/ATAM-0002-monorepo-multi-framework-blind-spot.md](../findings/ATAM-0002-monorepo-multi-framework-blind-spot.md)
