---
schema_version: 2
title: "Artifact Pipeline Discipline"
status: superseded
owner: agent-factory
created: 2026-08-17
updated: 2026-08-19
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
    - factory/scripts/write-step-manifest
    - factory/docs/factory-guide.md
    - factory/scripts/init-factory
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
- Enforcement is layered. Dedicated tool calls (`Read`, `Edit`, `Write`) are
  guarded deterministically by event hooks. Shell commands (`Bash`) are guarded
  best-effort by path extraction from the command string — inherently incomplete,
  since arbitrary shell syntax cannot be fully parsed. The hard cap is the
  context guard at spawn: the orchestrator measures declared inputs before the
  agent starts and denies the spawn if the total exceeds the step's budget.
- The context bound targets project artifacts (specifications, architecture
  documents, source code), not factory machinery. Skills, agents, playbooks,
  rulebooks, and scripts under `factory/` are prompt infrastructure that every
  agent needs; they are always allowed.
- The mechanism must work identically across Claude Code, Codex, GitHub Copilot
  CLI, and Pi. CLI-specific adapters translate the shared manifest and hook
  logic into each CLI's native event surface; the step contract itself is
  CLI-agnostic.

## Design

### Step manifest

Before spawning a step's agent, the orchestrating session writes a YAML file
that declares the step's boundaries:

```yaml
# .agent-factory/current-step.yml  (relative to working-directory root)
schema_version: 1
step: derive-use-cases
playbook: feature-addition
phase: 1

inputs:
  - docs/spec/prd-architecture-modeling.md
  - docs/spec/actor-goal-list.md
  - docs/proposals/bausteinsicht-factory-integration.md

outputs:
  - docs/spec/use_cases/UC-*.md

max_input_tokens: 40000             # hard cap on sum of input file sizes
```

The manifest lives at `.agent-factory/current-step.yml` relative to the working
directory root (resolved via `git rev-parse --show-toplevel`). It is git-ignored
— local runtime state, never committed. The orchestrating session writes it
before spawning the step agent; the hooks read it; the agent never edits it; the
orchestrator removes it after the agent completes.

**Worktree isolation.** In linked worktrees (Phase 4 dispatch),
`--show-toplevel` returns the worktree path, not the main checkout. Each
worktree therefore gets its own manifest at its own root. No coordination is
needed — filesystem isolation provides per-instance separation.

**Lifecycle-based scoping.** There is no `role` field. The manifest's existence
is the activation signal: when it exists, guards apply to all tool calls in that
working directory; when it does not, tool calls are unrestricted. The
orchestrator operates *between* steps — it writes the manifest, spawns the
agent, waits for completion, removes the manifest, then validates outputs.
During the step the orchestrator makes no file reads or writes; between steps no
manifest exists and no guards fire.

**No-supersede enforcement.** There is no `running_agents` list.
[`factory/scripts/write-step-manifest`](#orchestrator-role) refuses to write if
a manifest already exists at the target path, preventing a second agent from
being spawned for the same working directory while the first is still running.
After the agent completes (detected via `SubagentStop` or equivalent), the
orchestrator removes the manifest, unblocking the next write.

### Enforcement hooks

Five hooks enforce the manifest. The first three (read, write, Bash) are
deterministic for their tool surface; the Bash guard is best-effort because
shell syntax cannot be fully parsed. Each hook is a single shared
implementation with CLI-specific wiring.

#### 1. Read guard

**Event**: `PreToolUse` on `Read` (Claude Code, Codex), custom-agent
`pre_tool_use` (Copilot CLI), `pre_tool_use` extension (Pi).

**Logic**: Resolve the manifest at `$(git rev-parse --show-toplevel)/.agent-factory/current-step.yml`.
If the manifest does not exist, allow (no active step). If it exists, read the
`inputs` list. The file path in the tool call must match at least one declared
input glob or an always-allowed prefix. If it does not, deny the tool call with
an explanation naming the step, the file, and the declared inputs.

Always-allowed prefixes (not subject to input matching):

- `factory/` — prompt infrastructure: skills, agents, playbooks, rulebooks,
  scripts, and configuration. Every agent needs these to function; restricting
  them would break skill invocation (see [Open Questions](#open-questions),
  resolved).
- `.claude/`, `.github/`, `.pi/`, `.codex/` — CLI index files and local skill
  directories.
- `.agent-factory/` — runtime state, including the manifest itself.

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

#### 3. Bash guard (best-effort)

**Event**: `PreToolUse` on `Bash` (Claude Code, Codex), custom-agent
`pre_tool_use` on `bash` (Copilot CLI), `pre_tool_use` extension (Pi).

**Logic**: Same manifest resolution as the read guard. Extract file path
arguments from the command string using regex patterns for common read commands
(`cat`, `head`, `tail`, `less`, `rg`, `grep`, `find`, `fd`) and write commands
(shell redirects `>`, `>>`, `tee`, `cp`, `mv`). Check each extracted path
against the declared `inputs` (for reads) or `outputs` (for writes) and the
always-allowed prefixes. Deny if a path violates.

**Limitations**: Shell syntax is Turing-complete; the guard cannot catch
variable expansion, subshells, or obfuscated paths. It handles the common
patterns that account for the vast majority of agent tool calls. The context
guard at spawn is the hard cap — the Bash guard is defense-in-depth. This
follows the precedent of
[`block-dangerous-git.sh`](../../../factory/config/hooks/block-dangerous-git.sh),
which already parses `Bash` commands by pattern matching rather than full shell
interpretation.

**Exit codes**: `0` = allow, `2` = deny with reason.

#### 4. Context guard

**Event**: `PreToolUse` on `Agent` (Claude Code, Codex), custom-agent dispatch
(Copilot CLI), `run_agent` extension (Pi).

**Logic**: Before a step agent is spawned, the orchestrator hook sums the byte
sizes of all declared `inputs` files, converts to an approximate token count
(bytes ÷ 4), and compares against `max_input_tokens`. If the sum exceeds the
cap, deny the spawn with the measured total and the cap.

This hook runs in the orchestrating session, not in the step agent.

#### 5. No-supersede guard

**Event**: Not a hook — enforced by
`factory/scripts/write-step-manifest`.

**Logic**: Before writing a new manifest, the script checks whether one already
exists at the target path. If it does, the write is refused with an error
naming the existing step and the target path. The orchestrator must remove the
old manifest (after the prior agent completes) before writing a new one. This
turns the existing MUST NOT in
[rules.md § Dispatch](../../../factory/rulebooks/rules.md#dispatch) ("MUST NOT
launch a new agent for the same role while a prior instance is still running")
into a mechanical gate.

### CLI-specific wiring

The shared logic lives in a single script (`factory/scripts/step-guard`) that accepts
the tool event as JSON on stdin and the guard type as an argument (`read`,
`write`, `bash`, `context`). The no-supersede guard is enforced by
[`factory/scripts/write-step-manifest`](#orchestrator-role), not by a hook.
CLI-specific adapters normalize the tool input JSON before calling the shared
script:

| CLI                | Matchers                        | Tool input field           | Hook config location           | Adapter            |
| ------------------ | ------------------------------- | -------------------------- | ------------------------------ | ------------------ |
| Claude Code        | `Read`, `Edit`, `Write`, `Bash` | `.tool_input.file_path`    | `.claude/settings.json`        | Shell (inline jq)  |
| Codex              | `Read`, `Edit`, `Write`, `Bash` | `.tool_input.file_path`    | `.codex/hooks.json`            | Shell (inline jq)  |
| GitHub Copilot CLI | `Read`, `Edit`, `Write`, `Bash` | `.toolArgs.file_path`      | `.github/hooks/`               | JSON + shell       |
| Pi                 | `Read`, `Edit`, `Write`, `Bash` | Extension API `args` field | `.pi/extensions/step-guard.ts` | TypeScript wrapper |

This follows the established pattern of
[`block-dangerous-git.sh`](../../../factory/config/hooks/block-dangerous-git.sh),
which already normalizes across Claude Code, Copilot CLI, and Codex using a
`jq` expression that tries each CLI's field path.

Pi requires a TypeScript extension because its `pre_tool_use` surface is an
extension API, not a shell hook. The extension calls the shared script via
`execFileSync`, identical to how
[`block-dangerous-git.ts`](../../../factory/config/extensions/block-dangerous-git.ts)
delegates to its shell counterpart.

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
   remove the manifest, validate outputs exist.
3. At review decision points: check for open findings, route to the next step.
4. At manual decision points: present the decision to the stakeholder.

This is what the orchestrating session already does, but with the manifest
lifecycle as an additional mechanical step around each spawn. No new
orchestrator code is required in the first release. A
`factory/scripts/write-step-manifest` helper script reduces boilerplate:

```bash
# Write — before spawn
factory/scripts/write-step-manifest \
  --playbook feature-addition \
  --step derive-use-cases

# Remove — after agent completes
factory/scripts/write-step-manifest --clear
```

The `write` subcommand reads the step declaration from the playbook, resolves
glob patterns to concrete file lists, validates the context cap against
`max_input_tokens`, and writes `.agent-factory/current-step.yml` relative to the
working directory root. If a manifest already exists (a prior agent has not
completed), the script exits non-zero — the no-supersede guard.

The `--clear` subcommand removes the manifest, unblocking the next write. The
orchestrator calls it after the step agent completes and before validating
outputs. If an agent crashes or is cancelled without cleanup, a stale manifest
blocks subsequent writes; `--clear --force` removes it regardless, with a
warning naming the orphaned step.

Note: the write-refusal guard blocks *any* concurrent step in the same working
directory, not only a same-role duplicate. This is intentionally broader than
the MUST NOT it mechanizes — one manifest per directory, one agent per
directory — because concurrent agents in the same directory would overwrite each
other's outputs.

For worktree dispatches, the script accepts `--worktree <path>` to write the
manifest into a specific worktree's root instead of the current working
directory.

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
  Bash, and context guards.
- `factory/scripts/write-step-manifest` — helper to write and clear the
  manifest from a playbook's step declarations; enforces no-supersede.
- CLI-specific wiring for all four CLIs:
  - Claude Code: `PreToolUse` entries in `.claude/settings.json` for `Read`,
    `Edit`, `Write`, and `Bash`.
  - Codex: `PreToolUse` entries in `.codex/hooks.json` for `Read`, `Edit`,
    `Write`, and `Bash`.
  - GitHub Copilot CLI: hook files in `.github/hooks/` for the same matchers.
  - Pi: `step-guard.ts` extension in `.pi/extensions/`.
- Step declarations for the
  [`feature-addition`](../../../factory/playbooks/feature-addition.md) playbook
  (the reference implementation).
- Updated [`feature-addition.md`](../../../factory/playbooks/feature-addition.md)
  with `steps:` block.
- Updated [`rules.md`](../../../factory/rulebooks/rules.md) with step-boundary
  rules.
- Updated
  [`dispatch-contract.md`](../../../factory/rulebooks/conventions/dispatch-contract.md)
  with manifest and guard conventions.
- Updated [`init-factory`](../../../factory/scripts/init-factory) to install the
  step-guard wiring alongside existing hooks.
- Updated [`factory-guide.md`](../../../factory/docs/factory-guide.md) with
  pipeline discipline documentation.
- Epic-0 spike story verifying the GitHub Copilot CLI `pre_tool_use` event
  surface for `Read`/`Edit`/`Write` matchers (currently unverified — recorded
  assumption until the spike confirms).

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

All resolved — no open questions remain.

- ~~Should the read guard deny or warn by default?~~ **Resolved:** deny by
  default. The always-allowed prefixes (`factory/`, CLI directories,
  `.agent-factory/`) cover legitimate runtime reads. If a step needs an
  unanticipated project file, the step declaration is updated — not the guard
  weakened. `read_guard: warn` exists as an opt-in escape hatch for exploratory
  steps, mirroring `write_guard: warn`.

- ~~Should the always-allowed read paths include the full `factory/` directory
  or only the specific files the step's agent needs?~~ **Resolved:** always-allow
  the full `factory/` directory, plus CLI directories (`.claude/`, `.github/`,
  `.pi/`, `.codex/`) and `.agent-factory/`. These are prompt infrastructure, not
  project artifacts. The context bound targets project documentation and source
  code. Skills, agents, and playbooks must be readable at runtime for skill
  invocation to work; restricting them would break every skill-invoking agent.
  See [Read guard § Always-allowed prefixes](#1-read-guard).

- ~~What is the right `max_input_tokens` default when a step declaration omits
  it?~~ **Resolved:** no default — the field is required.
  `max_input_tokens` is a budget; implicit budgets defeat the purpose of
  bounding context. `write-step-manifest` exits non-zero if the field is missing
  from the step declaration.

- ~~What glob flavor do manifest `inputs` and `outputs` patterns use?~~
  **Resolved:** gitignore-style semantics (globset in Rust, picomatch with
  `dot: true` in TypeScript, `pathspec` in Python, `rg -g` in shell). `*`
  matches within a single path segment; `**` matches zero or more path segments
  (recursive). No dotfile special-casing — `**/*.md` matches files under hidden
  directories, unlike fnmatch/bash defaults. Globs match the path string, not
  the filesystem — output globs match new files whose path satisfies the
  pattern, even if the file does not yet exist at manifest-write time.

  **Consistency requirement.** The guard (string-matching a candidate path) and
  the resolver (`write-step-manifest` expanding globs to sum file sizes for
  `max_input_tokens`) must share one pinned semantics. If they diverge — the
  resolver undercounts because it skips hidden directories while the guard
  matches them — the context cap leaks silently, which is the exact failure mode
  the proposal exists to prevent. Concretely: one shared matching
  implementation in `step-guard` used by both the guard and
  `write-step-manifest`, and the resolver must use explicit flags (e.g.
  `rg --files --hidden --no-ignore -g '<pattern>'`), never ambient shell
  defaults (`shopt -s dotglob`) which are fragile across hook invocations.

## Completion Criteria

- `.agent-factory/current-step.yml` manifest schema is documented and validated
  by a lint script.
- `factory/scripts/step-guard` enforces read, write, Bash (best-effort), and
  context guards from the manifest.
- `factory/scripts/write-step-manifest` writes a valid manifest from a
  playbook's step declarations and refuses to overwrite an existing manifest
  (no-supersede).
- All four CLIs (Claude Code, Codex, GitHub Copilot CLI, Pi) wire the step
  guard into their native `PreToolUse` event surfaces for `Read`, `Edit`,
  `Write`, and `Bash` matchers.
- [`init-factory`](../../../factory/scripts/init-factory) installs the step-guard
  wiring alongside existing hooks.
- The [`feature-addition`](../../../factory/playbooks/feature-addition.md) playbook
  has a complete `steps:` block covering all phases.
- A step agent is blocked from reading project files outside its declared inputs
  via `Read` tool calls (verified by test). Factory machinery under `factory/`,
  CLI directories, and `.agent-factory/` are always allowed.
- A step agent is blocked (or warned) when writing files outside its declared
  outputs via `Edit`/`Write` tool calls (verified by test).
- A step agent's `Bash` tool calls are checked best-effort for file-path
  references outside declared inputs and outputs (verified by test against
  common commands: `cat`, `rg`, `grep`, shell redirects).
- `write-step-manifest` blocks when declared inputs exceed `max_input_tokens`
  (verified by test).
- `write-step-manifest` blocks when a manifest already exists at the target
  path (verified by test).
- When no manifest exists (between steps), tool calls are unrestricted —
  the orchestrator is not guarded.
- In linked worktrees, each worktree resolves its own manifest independently
  (verified by test with two concurrent worktrees).
- Declared inputs under hidden directories are matched and counted identically
  by guard and resolver (verified by test with a dot-directory input).

## Guiding Rule

Context is bounded by physical step boundaries and deterministic hooks, not by
agent discipline or convention.
