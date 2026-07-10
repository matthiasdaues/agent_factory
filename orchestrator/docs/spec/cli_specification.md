---
version: 1.2.0
author: matthiasdaues
date: 2026-07-07
---

# CLI Specification

## Overview

The orchestrate CLI offers two interaction modes:

1. **Direct mode** — flat subcommands with flags (scripting-friendly)
2. **Menu mode** — interactive TUI with nested navigation (this specification)

When invoked without arguments (`orchestrate`), the CLI enters menu mode.
When invoked with a subcommand (`orchestrate run-phase architecture`), it runs in direct mode.

## Design rules

1. **Menus contain only menus.** Every non-leaf node is a menu of submenus.
2. **Functions are leaves.** Only leaf nodes execute something.
3. **Model sits below adapter.** You pick an adapter, then a model within it.
4. **Two-axis model resolution, at two levels.** The two axes never combine on one invocation; each governs a different level. **Agent tier** governs every invocation the orchestrator makes directly: agents declare a `tier` in frontmatter (economy / standard / strong) — the minimum model capability the agent requires — and each agent the orchestrator invokes (`run-step`'s named agent, and every phase author/reviewer in `run-phase`) resolves its own tier through the active adapter's dictionary. **Story classification** governs the developer sub-agents the implementation dispatcher commissions: during the implementation phase the `implementation-agent` acts as a dispatcher and assigns each ready story's developer sub-agent a model from the story's `classification` (trivial / standard / hard) alone. Developer agents declare no tier by design — the model for a unit of work is the dispatcher's decision, and the classification is its single source of truth. That selection happens below the adapter boundary (FR-M); the orchestrator sees one `implementation-agent` invocation.
5. **Configurable defaults.** Adapter, timeout, cap, and auto-approve are persisted in `.orchestrator/config.toml`. CLI flags override persisted defaults. Menu selections override both.
6. **Interactive by default.** Whenever a TTY is attached, invocations are interactive so the Operator watches what the agent does; a non-interactive terminal (no TTY) degrades to headless automatically. The built-in default is interactive. For phases, interactivity is **preconfigured** by each agent's `interactive` frontmatter (e.g. an agent that must run headless declares `interactive: false`). For a direct `run-step`, `--no-interactive` forces headless for that one invocation. There is no global unattended `--yes` mode — that returns with unattended execution (NG6).

## Settings resolution precedence

```
menu selection > CLI flag > config.toml > built-in default
```

| Setting      | Built-in default             | config.toml key                     | CLI flag                               |
| ------------ | ---------------------------- | ----------------------------------- | -------------------------------------- |
| adapter      | `copilot`                    | `adapter`                           | `--adapter`                            |
| timeout      | `1800`                       | `timeout`                           | `--timeout`                            |
| cap          | `3`                          | `cap`                               | `--cap`                                |
| auto-approve | `false`                      | `auto_approve`                      | — _(unattended `--yes` deferred, NG6)_ |
| model        | _(resolved from agent tier)_ | —                                   | `--model` (run-step only)              |
| interactive  | `true` _(TTY present)_       | _(per-agent, in agent frontmatter)_ | `--no-interactive`                     |
| tier         | —                            | _(per-agent, in agent frontmatter)_ | —                                      |

## Model resolution chain

```
run-step:  agent.tier ──→ adapter.dictionary[tier] ──→ concrete model
           (--model overrides entire chain)

run-phase: each orchestrator-invoked agent resolves independently:
           agent.tier ──→ adapter.dictionary[tier] ──→ concrete model
           (no phase-level override)

implementation dispatcher (below the adapter boundary, FR-M):
           story.classification ──→ tier ──→ adapter.dictionary[tier] ──→ developer model
           (developer agents are tier-less; classification is the sole axis)
```

Tier ordering: economy < standard < strong.

The agent's `tier` frontmatter key declares the model capability required for the agent's task. The per-adapter model dictionary (`configure > cli > {adapter}`) is the runtime single source of truth for the tier-to-model mapping. The model-matrix `[facts]` section is the operator-authored configuration artifact that populates these dictionaries. Model override (`--model`) is only available on run-step — phases and chains use agent-declared tiers exclusively.

## CLI menu tree

### Root

```
orchestrate => menu
  init        = initialise a new project
  configure   = configure adapters, models, and policy
  run-step    = run a single agent
  run-phase   = run a development phase
  status      = inspect current run state
  manage-run  = manage an active or halted run
  backlog     = view the story backlog
```

### Init

```
orchestrate + init => menu
  [list of target CLIs: copilot, claude, gemini, cursor, codex]

orchestrate + init + {cli} => function
  Scaffolds project in cwd: directories, tooling assets, git repo,
  instruction file for the selected CLI.
```

For a new directory, use direct mode: `orchestrate init <project> --cli copilot`.

### Configure

```
orchestrate + configure => menu
  defaults      = manage default settings
  cli-list      = manage installed CLI adapters
  cli           = manage adapter model dictionaries
  model-matrix  = manage classification-to-tier policy

orchestrate + configure + defaults => menu
  adapter      = default CLI adapter        (current: copilot)
  timeout      = per-invocation timeout     (current: 1800s)
  cap          = iteration cap              (current: 3)
  auto-approve = auto-approve on clean gate (current: off)

orchestrate + configure + defaults + adapter => menu
  [list of registered adapters, current default marked ★]

orchestrate + configure + defaults + adapter + {adapter} => function
  Sets the default adapter. Persisted to .orchestrator/config.toml.

orchestrate + configure + defaults + timeout => function
  Prompts: timeout in seconds. Persisted to .orchestrator/config.toml.

orchestrate + configure + defaults + cap => function
  Prompts: iteration cap. Persisted to .orchestrator/config.toml.

orchestrate + configure + defaults + auto-approve => function
  Toggles auto-approve on/off. Persisted to .orchestrator/config.toml.

orchestrate + configure + cli-list => menu
  auto-detect    = detect installed CLI adapters on $PATH
  add adapter    = register a CLI adapter manually
  remove adapter = unregister a CLI adapter

orchestrate + configure + cli-list + auto-detect => function
  Scans $PATH for known CLI binaries, registers found adapters.

orchestrate + configure + cli-list + add adapter => function
  Prompts: adapter name, binary path. Registers adapter.

orchestrate + configure + cli-list + remove adapter => menu
  [list of registered adapters]

orchestrate + configure + cli-list + remove adapter + {adapter} => function
  Unregisters the adapter and its model dictionary.

orchestrate + configure + cli => menu
  [list of registered adapters]

orchestrate + configure + cli + {adapter} => menu
  list models    = show registered models with their tiers
  auto-detect    = query adapter for available models
  add model      = register a model with its tier
  remove model   = unregister a model

orchestrate + configure + cli + {adapter} + list models => display
  [table: model id, tier (economy / standard / strong)]

orchestrate + configure + cli + {adapter} + auto-detect => function
  Queries the adapter for its available models, presents results,
  prompts to register each with a tier.

orchestrate + configure + cli + {adapter} + add model => function
  Prompts:
    1. model id (e.g. gpt-5.4-mini)
    2. tier     (economy / standard / strong)
  Writes entry to CLI dictionary.

orchestrate + configure + cli + {adapter} + remove model => menu
  [list of models registered for this adapter]

orchestrate + configure + cli + {adapter} + remove model + {model} => function
  Removes model entry from CLI dictionary.

orchestrate + configure + model-matrix => menu
  show      = display current policy table
  edit      = open model-matrix.conf in $EDITOR
  validate  = run matrix-lint to check consistency

orchestrate + configure + model-matrix + show => display
  [facts: adapter → tier → model]
  [policy: classification → tier, phase → tier, on_missing]

orchestrate + configure + model-matrix + edit => function
  Opens model-matrix.conf in $EDITOR.

orchestrate + configure + model-matrix + validate => function
  Runs matrix-lint. Displays errors or "valid".
```

### Run-step

```
orchestrate + run-step => menu
  [list of agents from agents/ registry, showing name + tier]

orchestrate + run-step + {agent} => menu
  all skills (default) = run the agent's full workflow
  [list of agent's declared skills, e.g. fagan-review, security-review, bug-hunt]

orchestrate + run-step + {agent} + {skill-or-all} => menu
  [list of registered adapters, default adapter marked ★]

orchestrate + run-step + {agent} + {skill-or-all} + {adapter} => menu
  [list of models for this adapter, tier-resolved default marked ★]

orchestrate + run-step + {agent} + {skill-or-all} + {adapter} + {model} => function
  Runs the agent with the selected scope, adapter, and model.
  When a single skill is selected, the agent executes only that skill's
  workflow step. Exits TUI, switches to streaming terminal output.
```

The happy path is four selections deep: agent → skill scope (pick all) → adapter (pick default) → model (pick default). Three Enter presses on ★ defaults.

Direct-mode equivalent: `orchestrate --adapter copilot run-step qa-agent --skill fagan-review`

### Run-phase

```
orchestrate + run-phase => menu
  [list of phases: requirements, architecture, planning, implementation]

orchestrate + run-phase + {phase} => menu
  [list of registered adapters, default adapter marked ★]

orchestrate + run-phase + {phase} + {adapter} => function
  Drives the phase through its agent invocation sequence.
  Each agent in the phase resolves its own model from its declared tier
  and the selected adapter's dictionary. No model override at phase level.
  Exits TUI, switches to streaming terminal output.
```

### Status

```
orchestrate + status => menu
  overview       = run summary (phase, iteration, mode, last gate)
  phase details  = per-phase breakdown
  findings       = open findings list
  log            = invocation log

orchestrate + status + overview => display
  [current phase, iteration, mode, open findings count, last gate result]

orchestrate + status + phase details => display
  [for each phase: name, author, reviewer, status, iteration, last_gate, halted_from]

orchestrate + status + findings => display
  [table: id, severity, artifact, message, status]

orchestrate + status + log => display
  [table: agent, role, model, exit_code, duration_ms, gate outcome]
```

### Manage run

```
orchestrate + manage-run => menu
  resume   = continue run from last checkpoint
  approve  = approve current phase gate
  reject   = reject current phase gate
  release  = restore a halted phase to pre-halt status
  abort    = terminate active run

orchestrate + manage-run + resume => function
  Continues the run from its last checkpoint.

orchestrate + manage-run + approve => function
  Approves the current phase gate and advances.

orchestrate + manage-run + reject => function
  Prompts: note (optional). Records rejection, halts run.

orchestrate + manage-run + release => function
  Restores halted phase to pre-halt status, resets iteration.

orchestrate + manage-run + abort => function
  Sets mode to complete, releases lock.
```

### Backlog

```
orchestrate + backlog => menu
  list        = all stories
  by-epic     = stories grouped by EPIC
  ready       = stories with all dependencies met
  view story  = single story detail

orchestrate + backlog + list => display
  [table: id, title, epic, classification, status, deps]

orchestrate + backlog + by-epic => display
  [stories grouped under EPIC headings with status indicators]

orchestrate + backlog + ready => display
  [stories whose deps are all done and status is pending]

orchestrate + backlog + view story => menu
  [list of story ids with titles]

orchestrate + backlog + view story + {story} => display
  [full frontmatter + prose body]
```

## Navigation conventions

- Menus are navigated with **↑ / ↓ arrow keys**; **Enter** selects the highlighted item
- The selection cursor is `-> ` (3 characters) replacing the 3-space indent of unselected items
- Items marked `★` are pre-selected when the menu opens (the cursor starts on them)
- `q` or `Esc` returns to the parent menu
- `qq` or Ctrl+C exits the TUI
- Display screens return to parent on any key
- Functions that start long-running operations exit the TUI and switch to streaming terminal output

### Example rendering

```
orchestrate > run-step

   requirements-agent       [strong]
   architecture-agent       [strong]
   planning-agent           [strong]
-> implementation-agent     [standard]
   qa-agent                 [strong]
   coaching-agent           [strong]
```

## Node types

| Type         | Behaviour                                                           |
| ------------ | ------------------------------------------------------------------- |
| **menu**     | Presents children, waits for selection                              |
| **display**  | Shows content, returns to parent on keypress                        |
| **function** | Executes an action, may prompt for input, then returns or exits TUI |

## Direct-mode equivalents

| Menu path                                             | Direct-mode command                                                      |
| ----------------------------------------------------- | ------------------------------------------------------------------------ |
| init > {cli}                                          | `orchestrate init [<project>] --cli {cli}`                               |
| run-step > {agent} > all skills > {adapter} > {model} | `orchestrate --adapter {a} --model {m} run-step {agent}`                 |
| run-step > {agent} > {skill} > {adapter} > {model}    | `orchestrate --adapter {a} --model {m} run-step {agent} --skill {skill}` |
| run-phase > {phase} > {adapter}                       | `orchestrate --adapter {a} run-phase {phase}`                            |
| status > overview                                     | `orchestrate status`                                                     |
| manage-run > resume                                   | `orchestrate resume`                                                     |
| manage-run > approve                                  | `orchestrate approve`                                                    |
| manage-run > reject                                   | `orchestrate reject [--note "..."]`                                      |
| manage-run > release                                  | `orchestrate release`                                                    |
| manage-run > abort                                    | `orchestrate abort`                                                      |
