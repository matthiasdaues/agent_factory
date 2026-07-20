---
id: 0004
status: proposed
evaluation: pugh-matrix
---

# Pi runs a factory agent by spawning a separate `pi` subprocess

## Context

Agent Factory supports three CLIs: Claude Code, Copilot CLI, and Pi. Claude Code and Copilot spawn subagents natively, so a reviewer agent can run in a session that never saw the author's reasoning, and the `implementation-agent` dispatcher can fan work out to parallel, worktree-isolated `developer-agent` sessions. Pi provides neither. Its own documentation states it "intentionally does not include ... sub-agents," and that extensions "cannot define sub-agents or agent hierarchies." The sanctioned path is to spawn `pi` as a subprocess.

The Pi scaffold already committed on this branch makes Pi able to *find* factory content — `.pi/` is created, factory directories are symlinked, the guardrail extension is installed, and `AGENTS.md` wires orientation. It does not make Pi able to *run* agents as designed. The `AGENTS.md` line pointing the model at `.pi/agents/<name>.md` yields only in-context role-play: the model reads the file and acts it out in the *current* session. That destroys the two properties the factory's multi-agent design depends on — author/reviewer independence (the reviewer must work from the artifact alone, never the author's reasoning) and parallel dispatch.

The choice of invocation mechanism is hard to reverse once agents, playbooks, and the dispatcher depend on it; it is surprising without this context (a reader will reasonably assume in-context role-play is "good enough"); and it is the result of a real trade-off. All three bars the [`write-adr` skill](../../factory/skills/write-adr/SKILL.md) sets are met.

### Alternatives (Pugh Matrix)

**A**: in-context role-play — the status quo. `AGENTS.md` points the model at `.pi/agents/<name>.md`; the model reads the persona and acts it out in the caller's own session. **B**: a project-local Pi extension registers a model-callable tool that spawns a separate `pi` subprocess with the agent persona as its system prompt (what this ADR proposes). **C**: build a full agent-hierarchy orchestrator inside a Pi extension — a bespoke scheduler, session store, and message router layered over Pi.

Criterion weights follow the proposal's stated properties and this project's Clean Architecture/SOLID evaluation lens. Author/reviewer independence is a **must-have**: an option that cannot provide it is disqualified regardless of total.

| Criterion                                                                                                       | Weight | A: in-context role-play | B: subprocess spawn via extension tool | C: custom hierarchy in an extension |
| --------------------------------------------------------------------------------------------------------------- | ------ | ----------------------- | -------------------------------------- | ----------------------------------- |
| Author/reviewer independence (reviewer never sees the author's reasoning)                                       | 3      | 0 (datum — fails it)    | +2                                     | +2                                  |
| Parallel, worktree-isolated dispatch                                                                            | 2      | 0                       | +1                                     | +1                                  |
| Faithfulness to Pi's platform design (spawn is sanctioned; a hierarchy in an extension is explicitly disavowed) | 2      | 0                       | +1                                     | -1                                  |
| Implementation cost / YAGNI                                                                                     | 2      | 0                       | 0                                      | -2                                  |
| Traceless removal, no tracked project state                                                                     | 1      | 0                       | 0                                      | -1                                  |
| Guardrail inheritance across the session boundary                                                               | 2      | 0                       | +1                                     | 0                                   |
| **Weighted total**                                                                                              |        | **0**                   | **+12**                                | **+1**                              |

B wins decisively. A is the datum at 0, but its 0 on the must-have independence criterion — a +2 gap below both alternatives — is disqualifying on its own: one shared context cannot give a reviewer a view free of the author's reasoning, no matter how the total lands. C reaches independence and parallelism too, but it fights Pi's explicit stance that extensions must not define agent hierarchies, and it pays a large build cost to re-create what a subprocess already provides — a plain YAGNI violation. B layers one thin extension over the mechanism Pi itself sanctions.

## Decision

A project-local Pi extension, `factory/config/extensions/run-agent.ts`, symlinked to `.pi/extensions/run-agent.ts` by `init-factory`, registers one model-callable tool:

```
run_agent(agent: string, task: string, model?: string)
```

It resolves `factory/agents/<agent>.md`, resolves the model (the `model` argument, else `config/model.conf` `pi.<tier>` where the tier is read from the agent's own frontmatter, honoring `on_missing`), and spawns:

```
pi --no-session -a --mode json --model <m> --append-system-prompt <agent.md> -p <task>
```

in the project directory, returning the child's final text and token usage parsed from the `message_end` event. `--no-session` keeps the child throwaway; `-a` grants project trust per spawn (BR-031) so the child loads the factory skills, the guardrail, and `AGENTS.md`; `--append-system-prompt` layers the persona over Pi's own tool guidance (BR-032); `--mode json` yields structured output (BR-034). The spawn is a genuinely separate session, so author/reviewer independence holds (BR-030).

**Tier resolution stays single-sourced.** `run-agent.ts` is TypeScript; the canonical tier→model resolver (`matrix-lint.parse_matrix`, reused by `trigger`) is Python. Rather than re-implement `model.conf` parsing in TypeScript, `run-agent.ts` shells a small stdlib-only Python resolver so `model.conf` has exactly one parser (SOLID SRP; see [todos.md T-09](../spec/todos.md)). The extra in-process Python call is negligible against the cost of spawning `pi` itself.

**Recursion is bounded.** The child also loads `run-agent.ts` and could spawn its own subagents. The parent sets `PI_RUN_AGENT_DEPTH`; the child reads it and refuses to spawn past a fixed bound (BR-035), so a runaway chain cannot fork unbounded `pi` processes.

**The dispatcher (`dispatch_wave`) is a later layer, not this decision.** The parallel, worktree-isolated port of `implementation-agent` builds on this `run_agent` primitive once it reaches readiness (FR-J4, [todos.md T-10](../spec/todos.md)). This ADR settles only the single-agent invocation mechanism the dispatcher will reuse.

## Consequences

**Positive**

- Author/reviewer independence and parallel dispatch — the properties that make the factory's multi-agent design work under Claude Code — become available under Pi, over the exact mechanism Pi's own docs sanction.
- The child is a full factory citizen: it loads the guardrail (so subagents are bound by the same git-safety block, BR-033), the skills, and local-first orientation, without re-wiring any of it.
- `run-agent.ts` lives in `factory/config/extensions/`, is symlinked into the git-ignored `.pi/`, and is reversed by `remove-factory` (FR-J5) — no tracked project state, consistent with the guardrail-extension precedent.
- `model.conf` keeps one parser; tier semantics stay identical across `trigger` and `run_agent`.

**Negative / risks**

- Each `run_agent` call spawns a fresh `pi` process — heavier than an in-process subagent. For the author/reviewer pairs this is fine; for wide fan-out the dispatcher must cap concurrency itself.
- The guardrail binds the child only because the child is launched with `-a`. A future change that dropped `-a`, or a Pi run whose trust is unresolved, would load the child without the guardrail — the same trust-dependency caveat that already applies to Pi generally ([todos.md T-08](../spec/todos.md)).
- Spawn depth is bounded by an environment variable, not a compiled invariant. A child that unset `PI_RUN_AGENT_DEPTH` could evade the bound; the guard defends against accidental recursion, not a determined bypass — matching the guardrail's own "backstop, not a security boundary" posture.
- Structured-JSON parsing couples `run-agent.ts` to Pi's `--mode json` event shape (`message_end`). A Pi release that changed that shape would break parsing; the contract is pinned to Pi 0.80.8.

## Referenced from

- [09_architecture_decisions.md](../09_architecture_decisions.md)
- [docs/spec/use_cases/UC-10-invoke-a-factory-agent-under-pi.md](../spec/use_cases/UC-10-invoke-a-factory-agent-under-pi.md)
- [docs/spec/prd.md § FR-J](../spec/prd.md#4-functional-requirements)
- [factory/docs/proposals/pi-invocation-layer.md](../../factory/docs/proposals/pi-invocation-layer.md)
