[back to index](README.md)

# 8. Cross-cutting Concepts

## 8.1 Independent scripts over a shared core

`transition-lint`, `phase`, and `index-lint` each carry their own copy of the same minimal indentation-based YAML-subset parser (block mappings, block sequences, inline comments, scalars). This duplication is deliberate, not an oversight: factoring it into a shared library would add an import dependency between scripts that today are each independently invocable with zero setup. See [docs/spec/supplementary_specs/entity-model.md § Notes](spec/supplementary_specs/entity-model.md#notes) and [foundational-principles.md § YAGNI](../factory/rulebooks/conventions/foundational-principles.md#yagni) — the duplication is the smaller cost next to a coupling nobody has asked for yet.

## 8.2 Observable-state resumability

No mechanism persists "what step are we on" beyond the marker itself, and even the marker is corroborated, not trusted: `run-step` always re-checks a state's declared `outputs:` against what is actually on disk and re-runs that phase's own gate before deciding fresh start, resume, advance, or escalate (see [06_runtime_view.md § 6.4](06_runtime_view.md#64-resume-and-dispatch-uc-05-uc-04)). A crash between two commands leaves nothing to reconcile — the next invocation reads the same files and reaches the same answer.

## 8.3 Deterministic gates before judgement

`transition-lint`'s glob-ownership check and `phase advance`'s `entry_conditions` evaluation are both pure functions of files already on disk — no LLM judgement call sits in the gate path itself. This is the same principle [docs/concepts.md § Key ideas](concepts.md#key-ideas) states for the whole Agent Factory toolset: catch provable defects before an agent spends judgement on them.

## 8.4 Two independent safety layers

`block-dangerous-git.sh`'s dangerous-pattern list and `trigger`'s own background-mode deny list are two independent, deliberately mirrored layers (BR-020) — not one point of failure. A background session denied by `trigger`'s allowlist never sees the verb as available in the first place; a command that somehow bypasses that scoping is still caught by the `PreToolUse` hook before it runs. Neither layer is a security boundary against a determined bypass — both are backstops against an accidental or under-pressure one. See [docs/spec/use_cases/UC-07-block-a-dangerous-git-command.md § Business Rules](spec/use_cases/UC-07-block-a-dangerous-git-command.md#business-rules).

## 8.5 Iteration cap and review-loop discipline

`phase retry` is the loop killer: called before every re-dispatch of a state whose gate found open findings, never after. The cap resolves against the loop-back target's own `halt_conditions` entry if the FSM declares one, `--default-max-iterations` (default `5`) otherwise — every state gets a hard stop, even one nobody thought to author a per-state limit for. Every retried pass re-runs the deterministic check fresh and re-verifies every prior finding individually, per [review-loop-discipline.md § Rule](../factory/rulebooks/conventions/review-loop-discipline.md#rule) — a retry never just re-reads a stale findings list.

## 8.6 CLI-agnostic dispatch

`trigger` is the only mechanism aware that more than one CLI exists. It builds a separate command per `--cli` value — Claude Code's `Bash(<cmd> *)` glob syntax versus Copilot CLI's colon-wildcard `shell(<cmd>:*)` syntax — from the same resolved agent, tier, and prompt. Every other mechanism (`transition-lint`, `phase`, `index-lint`, `run-step`) has no CLI awareness at all; they operate purely on files.

## 8.7 Idempotent installation

`init-factory` treats every destination path the same way: missing → write it; already the expected symlink → skip; anything else → stop the entire run and name the exact colliding path (BR-021). `config/model.conf` is the one path `init-factory` never diffs once it exists (BR-022) — it is meant to diverge per project. Re-running `init-factory` against an already-initialized target reports every step as already satisfied.

## 8.8 The marker is the single source of truth, with a known limit

`.agent-factory/playbook-state.yml` is the one place "where is this run" is answered from. It is git-ignored, local, single-machine state — not a distributed lock. Two operators (a human and `orchestrator/`, or two humans) racing an advance/retry against the same marker can interleave incorrectly; this is a documented, accepted gap for the current single-operator-at-a-time usage pattern, not an oversight. See [T-02](spec/todos.md#t-02-no-concurrent-operator-lock-on-the-marker) and [11_risks_and_technical_debt.md](11_risks_and_technical_debt.md).

## Referenced from

- [docs/spec/supplementary_specs/validation-rules.md](spec/supplementary_specs/validation-rules.md)
- [docs/concepts.md § Key ideas](concepts.md#key-ideas)
