[back to index](README.md)

# 5. Building Block View

## 5.1 Whitebox — Level 1 (Containers)

Factory Flow Control is not one process with internal layers — it is a set of independently invocable stdlib scripts and one prose-driven skill, plus the flat files they read and write. Each row below is independently runnable; none imports another's control flow (see [04_solution_strategy.md § 4.3](04_solution_strategy.md#43-decomposition-strategy)).

![Containers](assets/images/Containers.png)

| Building block             | Responsibility                                                                                                                                                                                             | Depends on                                |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| **transition-lint**        | Phase-ordering gate: maps every staged file to its owning state via `outputs:` globs; blocks a file owned by a state other than the marker's current one. Never evaluates `entry_conditions`.              | Marker, Playbook FSM                      |
| **phase**                  | `advance`: resolves the current state's forward transition, checks the target's `entry_conditions`, writes the marker on success. `retry`: caps a loop-back state's re-attempts against `halt_conditions`. | Marker, Playbook FSM, Findings            |
| **trigger**                | Resolves an agent or playbook step from the catalog, resolves its tier to a model, and dispatches it to a CLI session under a scoped allowlist.                                                            | INDEX.yaml, model.conf, CLI-Invoked Agent |
| **index-lint**             | Regenerates `factory/INDEX.yaml` from `agents/*.md`, `skills/*/SKILL.md`, and `playbooks/*.md` frontmatter and prose. Never hand-edited.                                                                   | —                                         |
| **run-step** (skill)       | Resolves fresh-start / resume / advance / escalate from the marker, the current state's declared outputs, and its gate's result — never a persisted status.                                                | Marker, INDEX.yaml, phase, trigger        |
| **block-dangerous-git.sh** | `PreToolUse` hook: denies a fixed list of destructive or gate-bypassing git commands, reading either supported CLI's own JSON shape.                                                                       | —                                         |
| **init-factory**           | Idempotently wires `factory/`, the guardrail hook, and gate config into a new or existing project; stops the whole run at the first unexpected collision.                                                  | block-dangerous-git.sh, model.conf        |
| **Marker** (data)          | `.agent-factory/playbook-state.yml` — git-ignored, single-file run state: `playbook`, `state`, `gate`, `result`, `open_findings`, `next`, `iteration`, `recorded_by`, `recorded_at`.                       | —                                         |
| **Playbook FSM** (data)    | `factory/playbooks/<name>.fsm.yml` — states, `gate_conditions`, `entry_conditions`, `halt_conditions` for one playbook. Only `greenfield-development` has one today.                                       | —                                         |
| **INDEX.yaml** (data)      | Generated catalog: agents grouped by phase, skills by category, playbooks with their derived agent sequence and `fsm:` pointer.                                                                            | —                                         |
| **model.conf** (data)      | Per-CLI tier → model routing table `trigger` resolves an agent's dispatch model against.                                                                                                                   | —                                         |
| **Findings** (data)        | `docs/findings/<TAG>-NNNN.md` — YAML frontmatter `status: open\|resolved`, counted by `no_open_findings` conditions.                                                                                       | —                                         |

The **dependency rule** at this granularity: every arrow points from a mechanism to the flat file or the actor it reads, writes, or dispatches — never mechanism-to-mechanism control flow except where a skill (`run-step`) explicitly calls another script (`phase`, `trigger`) as a subprocess, exactly as a human would from the shell.

## 5.2 Whitebox — Key containers (Components)

Two containers have enough spec detail to justify a component breakdown; the rest are single-purpose scripts with no internal seams worth naming separately.

### `phase` (two subcommands, one shared FSM/marker layer)

| Component             | Responsibility                                                                                                                                                                                                                                                                                                          | Business rules                 |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| **advance**           | Resolves the current state's forward transition (`if` branch on a conditional transition); checks the target's `entry_conditions` against the `gate_conditions` library; refuses and leaves the marker untouched on any unmet condition.                                                                                | BR-004, BR-005, BR-006, BR-007 |
| **retry**             | Resolves the loop-back target (`else` transition, or the current state itself); resolves its iteration limit from `halt_conditions` or the default; refuses once the incremented count exceeds the limit.                                                                                                               | BR-008, BR-009, BR-010         |
| **FSM/marker parser** | The shared minimal indentation-based YAML subset parser both subcommands use to read `.fsm.yml` and the marker — duplicated in `transition-lint` too, deliberately not factored into a shared library (see [08_crosscutting_concepts.md § 8.1](08_crosscutting_concepts.md#81-independent-scripts-over-a-shared-core)). | —                              |

### `trigger` (resolution, then dispatch)

| Component                  | Responsibility                                                                                                                | Business rules |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | -------------- |
| **Agent/step resolver**    | Resolves a bare agent name, or a playbook step by agent name or 1-based index, from the catalog's own source data.            | BR-014         |
| **Tier resolver**          | Resolves the agent's declared `tier` to a concrete model via `model.conf`, honouring `on_missing`.                            | —              |
| **Prompt composer**        | Concatenates the full agent definition file with a standalone call-to-action section.                                         | —              |
| **Background dispatcher**  | Builds the CLI-specific command under the hardcoded, scoped allowlist; runs it as a subprocess; returns its exit code.        | BR-011, BR-012 |
| **Interactive dispatcher** | Prints the composed prompt for the actor to paste, then launches a live CLI session — never seeds a message programmatically. | BR-013         |

## Referenced from

- [docs/spec/supplementary_specs/entity-model.md](spec/supplementary_specs/entity-model.md)
- [docs/spec/supplementary_specs/interface-contracts.md](spec/supplementary_specs/interface-contracts.md)
