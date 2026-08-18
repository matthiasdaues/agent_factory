---
schema_version: 2
title: "Artifact Pipeline Discipline"
status: draft
owner: agent-factory
created: 2026-08-17
updated: 2026-08-17
supersedes:

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - factory/playbooks/feature-addition.md
    - factory/playbooks/greenfield-development.md
    - factory/playbooks/brownfield-onboarding.md
    - factory/playbooks/bug-fix.md
    - factory/playbooks/refactoring.md
    - factory/playbooks/documentation-update.md
    - factory/playbooks/architecture-review.md
    - factory/rulebooks/rules.md
    - factory/rulebooks/conventions/dispatch-contract.md
    - factory/rulebooks/templates/proposal.md
    - factory/config/hooks/block-dangerous-git.sh
    - factory/config/extensions/block-dangerous-git.ts
    - factory/scripts/step-guard
    - .claude/settings.json
    - .codex/hooks.json
    - .github/hooks/
    - .pi/extensions/

governance:
  assurance: high
  risk_domains:
    - compatibility
    - reliability
    - operations

estimate:
  as_of: 2026-08-17
  basis: judgment
  confidence: low
  human_review_hours:
    min: 4.0
    max: 8.0
  normalized_tokens:
    min: 30000
    max: 60000
  estimated_consumption:
    min: 300000
    max: 900000
    overhead_multiplier: 15
    playbook: feature-addition
---

# Feature Request: Artifact Pipeline Discipline

## Summary

Replace the Factory's stateful-session execution model with an artifact-pipeline
model where each playbook step is a cold-start agent that reads only declared
input artifacts and writes only declared output artifacts. A step manifest and
deterministic event hooks enforce the boundary mechanically across all four
supported CLIs (Claude Code, Codex, GitHub Copilot CLI, Pi). Context
accumulation is bounded per step instead of growing monotonically across an
agent's lifetime.

## Motivation

The 2026-08-17 bausteinsicht feature-addition consumed approximately 1.08 million
tokens in Phase 1 alone. The proposal estimated 40,000–80,000 normalized tokens
for all phases. Three structural patterns caused the overrun:

1. **Serial grilling inside a subagent.** The requirements-agent asked five
   design questions one at a time. Each question was a separate suspend/resume
   cycle. Each resume replayed the agent's full accumulated context — rules,
   INDEX, proposal, spec files, and all prior tool output. Five round-trips cost
   365,000 tokens; the productive content per round-trip was a one-sentence
   answer.

2. **Review-fix-review loop multiplication.** The spec was reviewed, found
   wanting, fixed, reviewed again, found wanting again, and fixed again. Each
   cycle cost 200,000–300,000 tokens because the fix agent was resumed (not
   restarted), carrying its entire grilling and spec-writing transcript forward
   into the fix work.

3. **Stale agent waste.** A new spec-review agent was launched while the prior
   instance was still running. The prior instance could not be cancelled; it
   consumed 217,000 tokens producing output from pre-fix state that was never
   used.

All three share a common cause: the agent's context grows monotonically across
its lifetime, and nothing mechanically prevents a long-lived agent from
accumulating far more context than the step's work requires.

Probabilistic mitigations were committed (batch grilling questions, spawn fresh
agents for fix cycles, grep-before-fix rule, no-supersede discipline). These
reduce waste but cannot guarantee a bound: they are conventions an agent can
ignore. The only way to mechanically cap context per step is to make step
boundaries physical — each step starts cold, reads only its declared inputs,
and exits.

## Core Principles

- A playbook step is the unit of execution. An agent runs one step, then exits.
  It does not carry context into the next step.
- Input and output artifacts are the only communication channel between steps.
  No transcript, tool output, or reasoning state crosses a step boundary.
- The step manifest is the single source of truth for what a step may read and
  write. It is a tracked file, not an in-memory convention.
- Enforcement is deterministic — event hooks, not agent instructions. An agent
  that tries to read outside its declared inputs is blocked before the read
  executes, not after it has already consumed context.
- The mechanism must work identically across Claude Code, Codex, GitHub Copilot
  CLI, and Pi. CLI-specific adapters translate the shared manifest and hook
  logic into each CLI's native event surface; the step contract itself is
  CLI-agnostic.

## Design

### Step manifest

Before spawning a step's agent, the orchestrating session writes a YAML file
that declares the step's boundaries:

```yaml
# .agent-factory/current-step.yml
schema_version: 1
step: derive-use-cases
playbook: feature-addition
phase: 1
role: step-agent                    # step-agent | orchestrator

inputs:
  - docs/spec/prd-architecture-modeling.md
  - docs/spec/actor-goal-list.md
  - docs/proposals/bausteinsicht-factory-integration.md
  - factory/rulebooks/rules.md

outputs:
  - docs/spec/use_cases/UC-*.md

max_input_tokens: 40000             # hard cap on sum of input file sizes

running_agents: []                  # populated by spawn guard, cleared on exit
```

The manifest lives at `.agent-factory/current-step.yml` and is git-ignored —
local runtime state, never committed. The orchestrating session writes it; the
hooks read it; the agent never edits it.

`role: orchestrator` exempts the orchestrating session from read guards. The
orchestrator reads broadly to assemble inputs and validate outputs; it is not
bound by a single step's input list. Only `role: step-agent` activates the read
and write guards.

### Enforcement hooks

Four deterministic hooks enforce the manifest. Each hook is a single shared
implementation with CLI-specific wiring.

#### 1. Read guard

**Event**: `PreToolUse` on `Read` (Claude Code, Codex), custom-agent
`pre_tool_use` (Copilot CLI), `pre_tool_use` extension (Pi).

**Logic**: If `.agent-factory/current-step.yml` exists and `role` is
`step-agent`, read the `inputs` list. The file path in the tool call must match
at least one declared input glob. If it does not, deny the tool call with an
explanation naming the step, the file, and the declared inputs.

Always-allowed paths (not subject to input matching):

- `factory/rulebooks/rules.md` — binding session rules, required by every agent.
- `factory/rulebooks/conventions/*.md` — rulebook expansions.
- `.claude/INDEX.yaml`, `.github/INDEX.yaml`, `.pi/INDEX.yaml`,
  `.codex/INDEX.yaml` — local-first resolution.
- `.agent-factory/current-step.yml` — the manifest itself.

**Exit codes**: `0` = allow, `2` = deny with reason.

#### 2. Write guard

**Event**: `PreToolUse` on `Edit` and `Write` (Claude Code, Codex),
`pre_tool_use` (Copilot CLI), `pre_tool_use` extension (Pi).

**Logic**: Same manifest check. The file path must match at least one declared
`outputs` glob. Deny with explanation if it does not.

Always-allowed write paths:

- `.agent-factory/` — runtime state.
- `docs/findings/*` — review agents must be able to file findings regardless of
  step scope.

**Severity**: Deny by default. If the step manifest sets
`write_guard: warn`, the hook emits a warning to stderr but allows the write.
This supports exploratory steps where the output set is not fully known in
advance.

#### 3. Context guard

**Event**: `PreToolUse` on `Agent` (Claude Code, Codex), custom-agent dispatch
(Copilot CLI), `run_agent` extension (Pi).

**Logic**: Before a step agent is spawned, the orchestrator hook sums the byte
sizes of all declared `inputs` files, converts to an approximate token count
(bytes ÷ 4), and compares against `max_input_tokens`. If the sum exceeds the
cap, deny the spawn with the measured total and the cap.

This hook runs in the orchestrating session, not in the step agent.

#### 4. No-supersede guard

**Event**: `PreToolUse` on `Agent` (Claude Code, Codex), custom-agent dispatch
(Copilot CLI), `dispatch_wave` extension (Pi).

**Logic**: Read `running_agents` from the manifest. If an agent with the same
`role` (agent type name) is already listed, deny the spawn with an explanation.
The orchestrator appends the agent's instance ID to `running_agents` on
successful spawn and removes it when the agent completes (via `SubagentStop` /
equivalent hook).

### CLI-specific wiring

The shared logic lives in a single script (`factory/scripts/step-guard`) that
accepts the tool event as JSON on stdin and the guard type as an argument
(`read`, `write`, `context`, `supersede`). CLI-specific adapters normalize the
tool input JSON before calling the shared script:

| CLI                | Tool input field           | Hook config location           | Adapter            |
| ------------------ | -------------------------- | ------------------------------ | ------------------ |
| Claude Code        | `.tool_input.file_path`    | `.claude/settings.json`        | Shell (inline jq)  |
| Codex              | `.tool_input.file_path`    | `.codex/hooks.json`            | Shell (inline jq)  |
| GitHub Copilot CLI | `.toolArgs.file_path`      | `.github/hooks/`               | JSON + shell       |
| Pi                 | Extension API `args` field | `.pi/extensions/step-guard.ts` | TypeScript wrapper |

This follows the established pattern of `block-dangerous-git.sh`, which already
normalizes across Claude Code, Copilot CLI, and Codex using a `jq` expression
that tries each CLI's field path.

Pi requires a TypeScript extension because its `pre_tool_use` surface is an
extension API, not a shell hook. The extension calls the shared
`factory/scripts/step-guard` script via `execFileSync`, identical to how
`block-dangerous-git.ts` delegates to its shell counterpart.

### Playbook step declarations

Playbooks gain an optional `steps` block that declares each step's inputs,
outputs, and context cap. The existing prose workflow remains; the `steps` block
adds machine-readable boundaries alongside it:

```yaml
# In feature-addition.md frontmatter or a companion .steps.yml
steps:
  - name: grill-proposal
    phase: 0
    agent: null                      # orchestrator does this directly
    inputs:
      - docs/proposals/<name>.md
    outputs:
      - docs/proposals/<name>.md     # amended in place
    max_input_tokens: 20000

  - name: derive-prd
    phase: 1
    agent: requirements-agent
    inputs:
      - docs/proposals/<name>.md
      - docs/spec/prd.md             # existing, if updating
    outputs:
      - docs/spec/prd-*.md
    max_input_tokens: 30000

  - name: derive-use-cases
    phase: 1
    agent: requirements-agent
    inputs:
      - docs/spec/prd-*.md
      - docs/spec/actor-goal-list.md
    outputs:
      - docs/spec/use_cases/UC-*.md
      - docs/spec/actor-goal-list.md
    max_input_tokens: 40000

  - name: spec-review
    phase: 1
    agent: spec-review-agent
    inputs:
      - docs/spec/**/*.md
      - docs/spec/traceability.json
    outputs:
      - docs/findings/SPEC-*.md
      - docs/reviews/spec-review-*.md
    max_input_tokens: 80000

  - name: fix-spec-findings
    phase: 1
    agent: requirements-agent
    inputs:
      - docs/findings/SPEC-*.md       # only the findings
      - docs/spec/**/*.md             # the files to fix
    outputs:
      - docs/spec/**/*.md
    max_input_tokens: 60000
```

The orchestrator reads the step declaration, writes the manifest, and spawns
the agent. The hooks enforce the manifest. The agent does not need to know about
the pipeline model — it just works within whatever reads and writes are allowed.

### Orchestrator role

The orchestrator is not a new binary or service. It is the human session — the
user, or the top-level Claude/Codex/Copilot/Pi session that runs the playbook.
Its responsibilities are:

1. Read the playbook's step declarations.
2. For each step: write the manifest, spawn a fresh agent, wait for completion,
   validate outputs exist.
3. At review decision points: check for open findings, route to the next step.
4. At manual decision points: present the decision to the stakeholder.

This is what the orchestrating session already does, but with the manifest write
as an additional mechanical step before each spawn. No new orchestrator code is
required in the first release. A `factory/scripts/write-step-manifest` helper
script reduces boilerplate:

```bash
factory/scripts/write-step-manifest \
  --playbook feature-addition \
  --step derive-use-cases \
  --role step-agent
```

It reads the step declaration from the playbook, resolves glob patterns to
concrete file lists, validates the context cap, and writes
`.agent-factory/current-step.yml`.

### Context budget model

Each step's context consumption is bounded:

```
step_cost ≤ sum(input_sizes) + agent_overhead + output_size
```

Where:

- `sum(input_sizes)` is capped by `max_input_tokens` (enforced by context
  guard).
- `agent_overhead` is the agent definition, rules, and skill instructions
  (~5,000–15,000 tokens, relatively fixed).
- `output_size` is the text the agent writes (bounded by the step's scope).

Total playbook cost is the sum of individual step costs — linear in the number
of steps, not exponential in context accumulation.

For the bausteinsicht Phase 1, this model predicts:

| Step                 | Input (tokens) | Overhead | Output | Total        |
| -------------------- | -------------- | -------- | ------ | ------------ |
| grill (orchestrator) | 12,000         | 0        | 0      | 12,000       |
| derive-prd           | 12,000         | 10,000   | 8,000  | 30,000       |
| derive-actor-goals   | 20,000         | 10,000   | 3,000  | 33,000       |
| derive-use-cases     | 23,000         | 10,000   | 15,000 | 48,000       |
| derive-supp-specs    | 38,000         | 10,000   | 10,000 | 58,000       |
| spec-review          | 50,000         | 10,000   | 5,000  | 65,000       |
| fix-findings         | 55,000         | 10,000   | 10,000 | 75,000       |
| spec-review (repeat) | 55,000         | 10,000   | 2,000  | 67,000       |
| **Total**            |                |          |        | **~388,000** |

Compared to 1,080,000 tokens actually consumed — a 2.8× reduction from the
pipeline model alone, before any other optimization.

## Scope

**In the first release:**

- Step manifest schema (`current-step.yml` format) and validation script.
- `factory/scripts/step-guard` — shared enforcement logic for read, write,
  context, and no-supersede guards.
- `factory/scripts/write-step-manifest` — helper to write the manifest from a
  playbook's step declarations.
- CLI-specific wiring for all four CLIs:
  - Claude Code: `PreToolUse` entries in `.claude/settings.json`.
  - Codex: `PreToolUse` entries in `.codex/hooks.json`.
  - GitHub Copilot CLI: hook files in `.github/hooks/`.
  - Pi: `step-guard.ts` extension in `.pi/extensions/`.
- Step declarations for `feature-addition` playbook (the reference
  implementation).
- Updated `feature-addition.md` with `steps:` block.
- Updated `rules.md` with step-boundary rules.
- Updated `dispatch-contract.md` with manifest and guard conventions.
- Updated `init-factory` to install the step-guard hook wiring.
- Updated `factory-guide.md` with pipeline discipline documentation.

**Explicitly deferred (do NOT plan stories for these):**

- Step declarations for other playbooks (greenfield, brownfield, bug-fix,
  refactoring, documentation-update, architecture-review). These adopt the
  pattern incrementally after feature-addition proves it.
- Automated orchestrator that reads step declarations and drives the playbook
  without human intervention. The human session remains the orchestrator.
- Output format validation (schema-checking that a step's outputs conform to a
  declared format like cockburn-use-case). The guards enforce file-path
  boundaries, not content structure.
- Token counting integration with the usage-capture pipeline. The context guard
  uses a byte-based approximation (÷4), not the fixed tokenizer.
- Step-level cost reporting or dashboards.

## Open Questions

- Should the read guard deny or warn by default? Deny is safer but may block
  agents that legitimately need to read a file not anticipated in the step
  declaration. A `read_guard: warn` mode (like `write_guard: warn`) would allow
  the read but log a violation for the orchestrator to review.

- Should the always-allowed read paths include the full `factory/` directory
  (all skills, agents, and scripts) or only the specific files the step's agent
  needs? Allowing all of `factory/` simplifies step declarations but weakens the
  context bound; restricting it requires listing every skill and agent file the
  agent might invoke.

- What is the right `max_input_tokens` default when a step declaration omits
  it? Options: no default (force explicit declaration), a conservative default
  (50,000), or a permissive default (200,000).

## Completion Criteria

- `.agent-factory/current-step.yml` manifest schema is documented and validated
  by a lint script.
- `factory/scripts/step-guard` enforces read, write, context, and no-supersede
  guards from the manifest.
- `factory/scripts/write-step-manifest` writes a valid manifest from a
  playbook's step declarations.
- All four CLIs (Claude Code, Codex, GitHub Copilot CLI, Pi) wire the step
  guard into their native event surfaces.
- `init-factory` installs the step-guard wiring alongside existing hooks.
- The `feature-addition` playbook has a complete `steps:` block covering all
  phases.
- An agent spawned as a step agent is blocked from reading files outside its
  declared inputs (verified by test).
- An agent spawned as a step agent is blocked (or warned) when writing files
  outside its declared outputs (verified by test).
- A spawn is blocked when declared inputs exceed `max_input_tokens` (verified by
  test).
- A spawn is blocked when another agent with the same role is already running
  (verified by test).
- The orchestrating session (role: orchestrator) is exempt from read and write
  guards.

## Guiding Rule

Context is bounded by physical step boundaries and deterministic hooks, not by
agent discipline or convention.
