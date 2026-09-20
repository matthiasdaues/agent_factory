---
scope: global
schema_version: 2
status: draft
owner: md@matthiasdaues.de
created: 2026-09-16
updated: 2026-09-16
supersedes:

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: false
  boundaries:
    - packages/factory/scripts/init_factory.py
    - factory/rulebooks/rules.md
    - factory/rulebooks/conventions/dispatch-contract.md
    - .claude/INDEX.yaml

governance:
  assurance: elevated
  risk_domains:
    - compatibility
    - operations

estimate:
  as_of: 2026-09-16
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Hermes Host Adapter

## Summary

Agent Factory gains Hermes as a fifth host alongside Claude Code, GitHub
Copilot CLI, Pi, and Codex. Factory's Markdown agent definitions, skills,
playbooks, and gate scripts run inside Hermes's runtime. Subagent
separation uses Hermes profile isolation. An MCP server provides
discovery. The first release proves that a Factory playbook can run to
completion on Hermes without modifying Hermes's core.

## Motivation

Factory's four current hosts are IDE-bound or CLI-bound. Each starts a
session, runs a workflow, and ends. Between sessions, state transfers via
git commits and handoff files. No host provides persistent cross-session
memory, container-level process isolation, unattended scheduling, or
multi-platform messaging.

Hermes provides all four. It is an open-source (MIT) autonomous agent
framework by Nous Research with persistent memory (SQLite, FTS5 full-text
search, Honcho user profiles), seven sandbox backends (local, Docker, SSH,
Singularity, Modal, Daytona, Vercel), built-in cron scheduling, and
gateway integration across Telegram, Discord, Slack, WhatsApp, Signal,
and email. It supports 300+ models via Nous Portal and speaks MCP.

Hermes lacks structured software engineering process. It auto-generates
skills from completed tasks but has no quality gates, no phased workflows,
no author/reviewer separation, and no deterministic validation. Factory
provides all of these. The integration is complementary: Hermes supplies
runtime capabilities Factory lacks; Factory supplies process governance
Hermes lacks.

## Core Principles

- **Git stays authoritative.** Code artifacts, process state (dispatch
  ledger, gate results, story status), and Factory definitions live in
  git. Hermes's SQLite stores execution memory and user profiles — not
  process state.

- **Markdown ships unmodified.** Factory agent definitions and playbooks
  run on Hermes without format translation. The host adapter reads them;
  it does not rewrite them.

- **Hermes core stays unpatched.** The first release uses only documented
  Hermes capabilities (profiles, delegate tool, MCP, terminal, command
  approval). A future Hermes PR (adding `system_prompt` and `model`
  parameters to the delegate tool) would simplify the adapter, but it is
  not a prerequisite.

- **Additive, not replacing.** Hermes's persistent memory, scheduling,
  and sandbox backends extend Factory. They do not replace git state,
  handoff files, or worktree isolation in the first release.

## Design

### Host entry in init-factory

`init-factory` gains a `hermes` host alongside existing hosts. It creates
`.hermes/` with symlinks to Factory content and generates `INDEX.yaml`
with `.hermes/`-prefixed path resolution.

| Constant           | Value for Hermes                 |
| ------------------ | -------------------------------- |
| `CLI_DOT_DIRS`     | `.hermes`                        |
| `ORIENTATION_FILE` | `.hermes/FACTORY.md`             |
| Skill directory    | `.hermes/skills/<name>/SKILL.md` |
| Agent directory    | `.hermes/agents/<name>.md`       |

The orientation file is `.hermes/FACTORY.md`, not `SOUL.md`. SOUL.md is
Hermes's persona file and belongs to the user. FACTORY.md contains the
Factory session protocol (fitting check, session menu, rules reference)
and is injected into SOUL.md via an include or appended as a context file.

### Profile-based subagent spawning

Hermes's `delegate` tool spawns a fresh `AIAgent` but provides no
documented way to inject a custom system prompt. The adapter works around
this with profile isolation: each Factory agent role becomes a Hermes
profile with its own SOUL.md, model config, and memory space.

`init-factory` generates profiles:

```
~/.hermes/profiles/
  factory-requirements-agent/
    SOUL.md          # generated from factory/agents/requirements-agent.md
    config.yaml      # model: <tier-mapped model>
  factory-architecture-agent/
    SOUL.md
    config.yaml
  factory-qa-agent/
    SOUL.md
    config.yaml
  ...
```

Each profile's SOUL.md contains the full Factory agent Markdown definition
as behavioral instructions. The profile's `config.yaml` sets the model
from the Factory model matrix: `tier: strong` maps to the configured
strong model, `tier: standard` to the configured standard model.

Dispatch invokes `hermes -p factory-<agent-name>` to spawn a subagent in
the correct profile. Each profile has its own conversation, memory, and
terminal — satisfying Factory's author/reviewer session independence.

### MCP discovery server

An MCP server exposes Factory's INDEX.yaml, agent definitions, skills,
playbooks, and gate scripts as tools and resources. Hermes connects to it
as a standard MCP server.

Tools:

- `factory_list_agents`, `factory_list_skills`, `factory_list_playbooks`
  — discovery from INDEX.yaml
- `factory_read_agent(name)`, `factory_read_skill(name)`,
  `factory_read_playbook(name)` — load full Markdown definitions
- `factory_run_gate(gate, args)` — execute a gate script, return
  pass/fail and output

The MCP server is a Python package under `packages/factory-mcp/`,
managed with uv, using the same toolchain as Factory.

### Skill frontmatter bridge

Factory skills use Factory-specific frontmatter (`name`, `category`,
`description`). Hermes skills use agentskills.io frontmatter (`name`,
`description`, `version`, `platforms`, `metadata.hermes`). Both formats
use `SKILL.md` as the file name.

The adapter generates agentskills.io frontmatter from Factory frontmatter
during `init-factory` wiring. The generated frontmatter is a superset:
it preserves Factory fields and adds agentskills.io fields. Hermes's
skill discovery reads the agentskills.io fields; Factory agents read the
Factory fields. Both coexist in one file.

Project-local Factory skills placed in `.hermes/skills/` require explicit
trust via `hermes skills trust`.

### Guardrail hooks

Factory requires interception of dangerous git commands (`git checkout .`,
`--no-verify`, `git reset --hard`). Claude Code uses `PreToolUse` hooks
in `settings.json`. Hermes uses a command-approval workflow.

The adapter registers Factory-specific approval rules that block
destructive git operations. The exact mechanism depends on Hermes's
command-approval configuration format — the adapter writes rules during
`init-factory` wiring.

### Dispatch contract mechanism row

| Logical operation    | Hermes mechanism                                                   |
| -------------------- | ------------------------------------------------------------------ |
| Spawn typed subagent | `hermes -p factory-<agent>` via delegate tool                      |
| Independent session  | Profile isolation: separate HERMES_HOME, memory, conversations     |
| Model tier           | Per-profile `config.yaml` with model mapped from Factory matrix    |
| Worktree isolation   | `git worktree add -b` via terminal (same as Claude Code)           |
| Gate execution       | Shell: `factory/scripts/premerge-check`, `verify-base`, `validate` |
| Guardrail hooks      | Hermes command-approval rules                                      |

## Scope

**In the first release:**

- `init-factory --host hermes .` creates `.hermes/` with symlinks,
  INDEX.yaml, FACTORY.md, and generated agent profiles
- MCP discovery server (`packages/factory-mcp/`) with list, read, and
  gate-run tools
- Skill frontmatter bridge generating agentskills.io fields from Factory
  fields
- Guardrail rules for dangerous git commands
- Dispatch contract mechanism row for Hermes in
  `dispatch-contract.md`
- Hermes host conventions in `rules.md` (CLI integration section)
- Profile generation script (`packages/factory-hermes/profile_gen.py`)

**Explicitly deferred (do NOT plan stories for these):**

- Hermes delegate tool PR (`system_prompt`, `model` parameters) — would
  replace profile isolation with direct injection; depends on Hermes
  maintainer acceptance
- Persistent memory replacing handoff files — requires a state-boundary
  protocol that defines which fields live in git vs SQLite; design work
  not done
- Auto-generated skill promotion via Factory QA pipeline — requires a
  trust boundary and review workflow; separate proposal
- Hermes cron triggering Factory playbooks — requires the host adapter to
  be stable first
- Container-based isolation replacing git worktrees — Hermes's Docker and
  Modal backends could provide stronger isolation, but the dispatch
  contract changes are non-trivial

## Open Questions

- Hermes's command-approval configuration format is not fully documented.
  The guardrail rules need to match whatever Hermes accepts. This may
  require reading Hermes source code.
- SOUL.md injection: does Hermes load FACTORY.md as a secondary context
  file, or must it be appended to SOUL.md? The mechanism determines
  whether Factory's session protocol coexists with or overwrites the
  user's persona.
- Profile disk footprint: generating a profile per Factory agent role
  creates 16+ directories under `~/.hermes/profiles/`. Is this acceptable
  to Hermes's profile manager?
- `hermes skills trust` scope: does trust apply per-profile or globally?
  Factory skills must be trusted in every agent profile that uses them.

## Completion Criteria

- `init-factory --host hermes .` produces a functional `.hermes/`
  directory with all symlinks, INDEX.yaml, FACTORY.md, and generated
  agent profiles.
- The MCP discovery server starts, lists all Factory agents and skills,
  and returns correct Markdown content for each.
- `factory_run_gate("premerge-check", {target, branch})` executes the
  gate script and returns pass/fail with output.
- A Factory playbook (bug-fix, as the simplest) runs to completion on
  Hermes: the developer-agent profile receives the story, implements with
  TDD, and the qa-agent profile reviews — in separate sessions.
- Gate scripts block a merge when they fail. The merge proceeds only
  after the gate passes.
- Model matrix tier assignments are reflected in each agent profile's
  `config.yaml`. A `tier: strong` agent uses the configured strong model.
- Guardrail rules prevent `git checkout .`, `--no-verify`, and
  `git reset --hard` without explicit user approval.
- Skill frontmatter contains both Factory and agentskills.io fields.
  Hermes discovers the skill; Factory agents read the Factory fields.

## Guiding Rule

Hermes is a runtime; Factory is a process. The adapter connects them
without blurring the boundary.
