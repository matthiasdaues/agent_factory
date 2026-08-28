# Todos — Factory Flow Control

Deferred decisions and named gaps found while reverse-engineering this specification from `factory/`'s code, per [rules.md § Todos](../../factory/rulebooks/rules.md#todos). None of these block the mechanisms documented in [use_cases/](use_cases/) — each is a known, intentional gap in the current implementation, not a defect this spec papers over.

## T-01: No CLI-failure classification in `trigger`

`factory/scripts/trigger` returns the invoked CLI's raw exit code. It does not distinguish an auth failure from a config error from a genuine task failure, the way `orchestrator`'s `CopilotAdapter` does (regex-matched stderr, `orchestrator` ADR-0002). A non-zero exit today means: read the output, do not auto-retry. Named in [`factory/skills/run-step/SKILL.md` § What this deliberately does not do (yet)](../../factory/skills/run-step/SKILL.md#what-this-deliberately-does-not-do-yet). Fold classification in if it turns out to matter in practice — not built ahead of a real case (YAGNI).

- [ ] Decide whether `trigger` should classify failures itself, or whether that stays a caller-side concern.

## T-02: No concurrent-operator lock on the marker

`.current-work/playbook-state.yml` is a single flat file with no locking. Two operators (human and `orchestrator/`, or two humans) racing an advance/retry against the same marker can interleave incorrectly. Out of scope for the current single-operator-at-a-time usage pattern.

- [ ] Decide whether a lock file (or an atomic compare-and-swap on `recorded_at`) is worth adding, or whether this stays a documented usage constraint.

## T-03: `script_exit_zero` condition type is stubbed

`factory/scripts/phase`'s `evaluate_condition` always returns `(True, "script_exit_zero <script> (stubbed pass)")` for this condition type — it never actually runs the named script. See [validation-rules.md § Entry conditions](supplementary_specs/validation-rules.md#entry-conditions-gate_condition).

- [ ] Implement the real subprocess run + exit-code check, or remove the condition type if nothing ends up needing it.

## T-04: `halt_conditions` types other than `max_iterations` are unenforced

`greenfield-development.fsm.yml` declares `script_failure` and `circular_dependency` halt conditions. `phase retry` only reads and enforces `max_iterations`; the other two types are parsed nowhere.

- [ ] Implement enforcement for `script_failure` and `circular_dependency`, or remove the declarations if they remain aspirational.

## T-05: Copilot CLI's three-word `shell(...)` wildcard syntax unconfirmed

`trigger`'s `COPILOT_ALLOW_TOOLS`/`COPILOT_DENY_TOOLS` include entries like `shell(uv run pytest:*)`. The two-word-prefix form (`shell(git commit:*)`) is confirmed against GitHub's own documented example; the three-word form follows the same pattern but has not been verified against Copilot CLI itself.

- [ ] Verify the three-word form against a real Copilot CLI invocation; adjust the allowlist syntax if it is rejected.

## T-06: Multi-framework test orchestration not yet supported

`run-tests` detects all framework markers but fails loudly (exit 2) when multiple frameworks are present, rather than running all detected frameworks in sequence. This prevents silent partial coverage in monorepo contexts but blocks multi-framework projects entirely. Long-term solution: detect all frameworks, run each, aggregate results, exit 0 only if all pass. See ATAM-0002 resolution.

- [ ] Implement multi-framework orchestration: detect all, run all, aggregate results (passed/failed counts sum across frameworks).
- [ ] Add optional explicit config (`.current-work/test-config.yml`) to override auto-detection for complex monorepo cases.

## T-07: `verify-base` and `premerge-check` were prompt-required, not hook-enforced

- status: resolved

`factory/scripts/verify-base` and `factory/scripts/premerge-check` now write a marker file on success; `block-dangerous-git.sh` denies `git commit` in a marker-less worktree and `git merge <branch>` without a matching `premerge-check-ok` marker. Mechanical enforcement, not a prompt instruction. Still open: `Edit`/`Write` inside a marker-less worktree aren't gated, only `git commit` — a subagent can still read/edit before verifying, just can't persist a commit.

## T-08: Pi guardrail is an extension, weaker than the native hook path

Under Pi the git-safety guardrail is a project-local extension loaded only after project trust resolves, not a native `PreToolUse` hook. A non-interactive run that has not saved trust (or is not launched with `-a`) can skip it. `run_agent` passes `-a` on every spawn (BR-031) so its children load the guardrail, but the parent Pi session's own guardrail still depends on trust. Documented in [factory/docs/factory-guide.md § CLI safety guardrails](../../factory/docs/factory-guide.md#cli-safety-guardrails).

- [ ] Decide whether to recommend the global `~/.pi/agent/extensions/` install or a container as the stronger default for Pi.

## T-09: `run_agent` tier resolution duplicates or shells the Python resolver

`run-agent.ts` is TypeScript; the canonical tier→model resolver (`matrix-lint.parse_matrix`, reused by `trigger`) is Python. `run-agent.ts` must either re-implement the `model.conf` parse in TS or shell out to a small Python resolver to keep a single source of truth. See [ADR-0004](../adr/0004-pi-subagent-invocation-via-subprocess-spawn.md).

- [ ] Confirm the chosen resolution path holds up once OpenRouter model IDs (ADR-0005) populate `pi.*`.

## T-10: `dispatch_wave` built after the `run_agent` primitive reaches readiness

Per the build order, the `run_agent` single-agent primitive shipped and was validated first; `dispatch_wave` (parallel, worktree-isolated dispatch with `premerge-check` integration, FR-J4) followed. The tool takes one caller-planned, file-disjoint wave — output-file overlap and dependency ordering stay with the calling agent, as `implementation-agent` documents.

- [x] Land `dispatch_wave` and its two-parallel-agent validation.

## Referenced from

- [validation-rules.md](supplementary_specs/validation-rules.md)
- [entity-model.md](supplementary_specs/entity-model.md)
- [docs/findings/ATAM-0002-monorepo-multi-framework-blind-spot.md](../findings/ATAM-0002-monorepo-multi-framework-blind-spot.md)
