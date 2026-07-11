# Todos — Factory Flow Control

Deferred decisions and named gaps found while reverse-engineering this specification from `factory/`'s code, per [rules.md § Todos](../../factory/rulebooks/rules.md#todos). None of these block the mechanisms documented in [use_cases/](use_cases/) — each is a known, intentional gap in the current implementation, not a defect this spec papers over.

## T-01: No CLI-failure classification in `trigger`

`factory/scripts/trigger` returns the invoked CLI's raw exit code. It does not distinguish an auth failure from a config error from a genuine task failure, the way `orchestrator`'s `CopilotAdapter` does (regex-matched stderr, `orchestrator` ADR-0002). A non-zero exit today means: read the output, do not auto-retry. Named in [`factory/skills/run-step/SKILL.md` § What this deliberately does not do (yet)](../../factory/skills/run-step/SKILL.md#what-this-deliberately-does-not-do-yet). Fold classification in if it turns out to matter in practice — not built ahead of a real case (YAGNI).

- [ ] Decide whether `trigger` should classify failures itself, or whether that stays a caller-side concern.

## T-02: No concurrent-operator lock on the marker

`.agent-factory/playbook-state.yml` is a single flat file with no locking. Two operators (human and `orchestrator/`, or two humans) racing an advance/retry against the same marker can interleave incorrectly. Out of scope for the current single-operator-at-a-time usage pattern.

- [ ] Decide whether a lock file (or an atomic compare-and-swap on `recorded_at`) is worth adding, or whether this stays a documented usage constraint.

## T-03: `script_exit_zero` condition type is stubbed

`factory/scripts/phase`'s `evaluate_condition` always returns `(True, "script_exit_zero <script> (stubbed pass)")` for this condition type — it never actually runs the named script. See [validation-rules.md § Entry conditions](supplementary_specs/validation-rules.md#entry-conditions).

- [ ] Implement the real subprocess run + exit-code check, or remove the condition type if nothing ends up needing it.

## T-04: `halt_conditions` types other than `max_iterations` are unenforced

`greenfield-development.fsm.yml` declares `script_failure` and `circular_dependency` halt conditions. `phase retry` only reads and enforces `max_iterations`; the other two types are parsed nowhere.

- [ ] Implement enforcement for `script_failure` and `circular_dependency`, or remove the declarations if they remain aspirational.

## T-05: Copilot CLI's three-word `shell(...)` wildcard syntax unconfirmed

`trigger`'s `COPILOT_ALLOW_TOOLS`/`COPILOT_DENY_TOOLS` include entries like `shell(uv run pytest:*)`. The two-word-prefix form (`shell(git commit:*)`) is confirmed against GitHub's own documented example; the three-word form follows the same pattern but has not been verified against Copilot CLI itself.

- [ ] Verify the three-word form against a real Copilot CLI invocation; adjust the allowlist syntax if it is rejected.

## Referenced from

- [validation-rules.md](supplementary_specs/validation-rules.md)
- [entity-model.md](supplementary_specs/entity-model.md)
