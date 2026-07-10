# Orchestrator

Orchestrator is Agent Factory's deterministic external wrapper — a Python CLI that automates the same phase chain the [root README](../README.md) describes (requirements → spec-review → architecture → architecture-review → planning → implementation → reconciliation → qa), instead of driving each agent by hand, one session at a time. It runs a step, a phase, or the whole chain, with deterministic gates enforced automatically via `pre-commit` and human judgement reserved for phase-gate approval.

**This is still a work in progress.** The CLI, its test suite, and its own architecture documentation are real and substantial (see below), but the packaging and distribution story — how a project outside this monorepo installs and runs `orchestrate` day to day — is not yet settled. See [`orchestrator/docs/spec/todos.md`](docs/spec/todos.md) for the open questions, and [`docs/adr/0010-separate-tooling-from-project-directory.md`](docs/adr/0010-separate-tooling-from-project-directory.md) for the distribution model currently on record (flagged there as needing supersession once the real design lands).

## What exists today

- A CLI (`orchestrate`) with direct-mode subcommands and an interactive menu mode — see [`docs/spec/cli_specification.md`](docs/spec/cli_specification.md).
- Session isolation per agent invocation, CLI-agnostic adapters (Copilot first), a findings store, loop-back with a retry cap, run state and resume — see the arc42 documentation in [`docs/`](docs/README.md) and the domain glossary in [`CONTEXT.md`](CONTEXT.md).
- A backlog of its own (`backlog/`), tracking orchestrator's own development, independent of the root `backlog/` and `orchestrator/`'s own docs being a separate bounded context from the rest of the repo (see the root [`docs/CONTEXT-MAP.md`](../docs/CONTEXT-MAP.md)).

## Running it here

From inside `orchestrator/`:

```bash
uv sync              # install dependencies into orchestrator/.venv
uv run pytest        # run the test suite
uv run orchestrate --help
```

Orchestrator resolves the agent/skill definitions it drives relative to the repo it's running inside — it expects `factory/agents/` and `factory/skills/` one level up from `orchestrator/`, which is exactly this repo's own layout.

## Troubleshooting

No orchestrator-specific troubleshooting entries yet. File one here as real issues surface running `orchestrate` — this section should only ever hold things that actually happened, not anticipated problems.
