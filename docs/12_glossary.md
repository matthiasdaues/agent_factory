[back to index](README.md)

# 12. Glossary

## Domain terms (from `docs/spec/`)

| Term                       | Definition                                                                                                                                                                      |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Marker**                 | `.agent-factory/playbook-state.yml` — the git-ignored, single-file record of which playbook and state a run is in. The sole source of truth for "where is this run."            |
| **Playbook**               | A named, end-to-end flow (e.g. `greenfield-development`) — a sequence of agents driven either by prose alone or by a companion `.fsm.yml`.                                      |
| **FSM (`.fsm.yml`)**       | `factory/playbooks/<name>.fsm.yml` — one playbook's states, `gate_conditions`, `entry_conditions`, and `halt_conditions`. Only `greenfield-development` has one today.          |
| **State**                  | One node in a playbook's FSM: a `description`, an `agent` (nullable for a human-approval state), declared `outputs:` globs, and `entry_conditions`.                             |
| **Transition**             | A state's `on:` event, resolving to a `to:` target, or an `if`/`else` pair where `if` is the sole forward/progress path.                                                        |
| **Entry condition**        | A named `gate_conditions` entry a state's transition target must satisfy before `phase advance` will move the marker there.                                                     |
| **Gate condition**         | One of four types: `file_exists`, `files_exist`, `no_open_findings`, `script_exit_zero` (stubbed — see [T-03](spec/todos.md#t-03-script_exit_zero-condition-type-is-stubbed)).  |
| **Halt condition**         | A per-state circuit breaker. Only `type: max_iterations` is currently enforced (see [T-04](spec/todos.md#t-04-halt_conditions-types-other-than-max_iterations-are-unenforced)). |
| **Iteration cap**          | The maximum number of times a state's author step may re-run after a failing gate, resolved from `halt_conditions` or `--default-max-iterations` (default 5).                   |
| **Catalog (`INDEX.yaml`)** | `factory/INDEX.yaml` — the generated list of every agent, skill, and playbook, grouped and cross-referenced from source frontmatter. Never hand-edited.                         |
| **Tier**                   | One of `economy \| standard \| strong` — an agent's or story's declared difficulty band, resolved to a concrete model via `model.conf`.                                         |
| **`model.conf`**           | The per-CLI tier → model routing table `trigger` resolves an agent's dispatch model against.                                                                                    |
| **Finding**                | A filed `docs/findings/<TAG>-NNNN.md`, with YAML frontmatter `status: open \| resolved`, counted by `no_open_findings` conditions.                                              |
| **Resume**                 | The decision `run-step` makes on every invocation — fresh start, re-dispatch, advance, or escalate — re-derived from disk, never from a persisted status.                       |
| **Trigger**                | The dispatch mechanism (`factory/scripts/trigger`) that resolves an agent/step and launches it in a CLI session, background or interactive.                                     |
| **Guardrail hook**         | `block-dangerous-git.sh` — the `PreToolUse` hook denying a fixed list of destructive or gate-bypassing commands before they run.                                                |

## Actors

| Term                        | Definition                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **Human Operator**          | A person driving Agent Factory directly by hand.                                                                                           |
| **Orchestrator-as-Trigger** | The nested `orchestrator/` Python CLI, invoking the same mechanisms programmatically in the Human Operator's place — a peer, not an owner. |
| **CLI-Invoked Agent**       | The Claude Code or Copilot CLI session `trigger` dispatches.                                                                               |

Full definitions: [docs/spec/actor-goal-list.md § Actors](spec/actor-goal-list.md#actors).

## Referenced from

- [docs/spec/supplementary_specs/entity-model.md](spec/supplementary_specs/entity-model.md)
- [docs/spec/supplementary_specs/validation-rules.md](spec/supplementary_specs/validation-rules.md)
