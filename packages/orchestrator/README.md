# Orchestrator

The `agent-factory-orchestrator` package replaces you pressing "enter" between
agent sessions. Nothing more.

Part of [Agent Factory](../../README.md). See also: [factory](../factory/README.md), [architecture docs](../../docs/README.md).

When you run a playbook by hand, you do the same thing every time: check the marker, figure out which agent goes next, open a CLI session, wait for it to finish, check whether the gate passes, advance the marker, repeat. You aren't making decisions — you're turning a crank. The orchestrator turns it for you.

## What it does

One thing: it reads a playbook's state machine and steps through it.

```
read marker → resolve agent → dispatch → wait → check gate → advance → next step
```

At every step, it calls the same scripts you would call by hand:

- `factory/scripts/phase advance` — checks whether the gate passes and moves the marker forward.
- `factory/scripts/trigger` — launches an AI CLI session with the right agent and model.
- `factory/scripts/phase retry` — checks whether another attempt is allowed before re-dispatching.

The orchestrator holds no opinions. It does not evaluate gates, compose prompts, pick models, or decide what to retry. It delegates all of that to the scripts above. If a script says no, the orchestrator stops.

## When it stops

Three situations:

1. **Done.** The playbook reached its final state. Exit 0.
2. **Human gate.** The current state has no agent (`agent: null` in the FSM). You need to do something — approve a backlog, resolve a finding, file a bug. Do it, then re-run. Exit 0.
3. **Halt.** The iteration cap was hit (an agent keeps failing the gate), or a configuration error made dispatch impossible. Exit 1 or 2. Read the message, fix the problem, re-run.

## How to use it

### Prerequisites

You need a project that already has Agent Factory set up (`factory/` exists, `.pre-commit-config.yaml` is wired). If not, run `factory/scripts/init-factory` first — see the [factory README](../factory/README.md).

### After finishing requirements by hand

The requirements phase is always human-driven — the requirements agent interviews you, and the specs exist because you participated. Once specs are written and reviewed (no open `SPEC-*.md` findings), start the orchestrator from Phase 2:

```bash
factory/scripts/run-playbook \
  --playbook greenfield-development \
  --from-state PHASE_2_ARCHITECTURE \
  --cli claude
```

It will dispatch the architecture agent, wait, check the gate, dispatch the architecture review agent, and so on — pausing at `PHASE_3_APPROVAL` for you to review the backlog, then continuing through implementation, reconciliation, and QA.

### Bug fix workflow

File the bug first (`docs/findings/BUG-NNNN.md`), then:

```bash
factory/scripts/run-playbook \
  --playbook bug-fix \
  --from-state IMPLEMENT_FIX \
  --cli claude
```

### Resuming after a stop

Just re-run the same command without `--from-state`. The orchestrator reads the marker (`.current-work/playbook-state.yml`) and picks up where it left off:

```bash
factory/scripts/run-playbook --playbook greenfield-development --cli claude
```

Kill the process at any point — the marker is the only truth, and it was written by `phase advance` before the orchestrator moved on. Nothing is lost.

### Switching between Claude and Copilot

```bash
--cli claude    # default
--cli copilot
```

The agent receives the same prompt either way. The model is resolved from `config/model.conf` based on the agent's tier.

## How to test it

```bash
uvx pytest orchestrator/tests/test_run_playbook.py -v
```

18 tests cover all five use cases: normal dispatch, human gates, final states, retry loops, halt on cap, config errors, audit log format, and marker bootstrap. Tests mock the subprocess calls to `phase` and `trigger`, so they run in under a second and don't need a real AI CLI.

## What it does not do

- **Drive requirements.** Phase 1 is human-driven. Always.
- **Run agents in parallel.** One at a time, sequentially. (The implementation agent parallelizes internally, but the orchestrator doesn't know or care.)
- **Retry with different models.** If an agent fails and hits the cap, the orchestrator stops. Picking a different model or prompt is your call.
- **Parse CLI output.** A non-zero exit from trigger means "something went wrong." The gate is the real arbiter of whether the work succeeded, not the exit code.

## Files

```
orchestrator/
├── pyproject.toml             # agent-factory-orchestrator package metadata
├── src/
│   ├── agent_factory_orchestrator/
│   │   ├── __init__.py
│   │   └── cli.py            # canonical packaged implementation
│   └── run_playbook.py       # compatibility launcher for authoring checkouts
├── tests/                    # 50 test files: run-playbook, trigger, usage capture,
│                             # research, init/remove/update-factory, guards, schemas
│   └── test_run_playbook.py  # 18 tests covering the five orchestrator use cases
├── docs/
│   ├── spec/                 # PRD, use cases, entity model
│   ├── adr/                  # ADR-0001: pure delegation
│   ├── 05_building_block_view.md
│   ├── 06_runtime_view.md
│   ├── 09_architecture_decisions.md
│   └── architecture.dsl      # C4 model (Structurizr)
└── backlog/                  # 6 stories, all done
```

## Audit log

Every step writes a JSON line to `.current-work/audit.log`:

```json
{"timestamp": "2026-07-13T00:05:00+00:00", "playbook": "greenfield-development", "state": "PHASE_2_ARCHITECTURE", "agent": "architecture-agent", "action": "advance", "trigger_exit": 0, "phase_advance_exit": 0, "phase_retry_exit": null, "iteration": 1, "duration_seconds": 342.5}
```

Parse it with `jq`:

```bash
# How long did each agent session take?
jq -r 'select(.action=="advance") | "\(.state): \(.duration_seconds)s"' .current-work/audit.log

# Which states needed retries?
jq -r 'select(.action=="retry") | .state' .current-work/audit.log
```
