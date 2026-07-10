# Activation Guide

How to wire the agents and skills into your AI coding CLI and run the full development workflow.

## Prerequisites

- An AI coding CLI: Claude Code, GitHub Copilot, Gemini CLI, Cursor, Codex/OpenCode, or any tool that reads `AGENTS.md`
- Docker (for Structurizr diagram exports via `scripts/structurizr`)
- A GitHub repository with issues enabled (for backlog and bug tracking)

## Directory layout

```
agent_hq/
├── agents/                        8 phase agents + TEMPLATE.md
│   ├── requirements-agent.md
│   ├── spec-review-agent.md
│   ├── architecture-agent.md
│   ├── architecture-review-agent.md
│   ├── planning-agent.md
│   ├── implementation-agent.md
│   ├── reconciliation-agent.md
│   ├── qa-agent.md
│   └── TEMPLATE.md
├── orchestrator/                  Python CLI — this component
│   ├── src/orchestrator/              Ports-and-adapters source
│   ├── tests/
│   ├── docs/                          arc42 docs, ADRs, spec
│   ├── backlog/                       Internal issues (ST-*)
│   ├── CONTEXT.md
│   ├── USAGE.md                       ← you are here
│   ├── model-matrix.conf
│   └── pyproject.toml
├── prompts/                       Work instructions per step
│   ├── 1_requirements/
│   ├── 2_architecture/
│   ├── 3_planning/
│   ├── 4_implementation/
│   ├── 5_quality/
│   └── README.md
├── scripts/                       Deterministic linters and wrappers
│   ├── arch-lint
│   ├── backlog-lint
│   ├── matrix-lint
│   ├── spec-lint
│   └── structurizr                    Docker wrapper for diagram export
├── skills/                        19 skills (caveman sets communication style)
│   ├── atam-review/
│   ├── bug-hunt/
│   ├── capture-vision/
│   ├── caveman/
│   ├── clarify-requirements/
│   ├── create-backlog/
│   ├── derive-spec/
│   ├── dev-workflow/
│   ├── fagan-review/
│   ├── grill-me/
│   ├── grill-with-docs/
│   ├── implement-issue/
│   ├── inspect-spec/
│   ├── reconcile-spec/
│   ├── scaffold-arc42/
│   ├── security-review/
│   ├── spec-feedback/
│   ├── write-adr/
│   └── write-prd/
├── README.md
└── prompts/workflow.md            Full workflow reference
```

## Step 1 — Create your CLI instruction file

Create the instruction file your CLI reads. If the file already exists, add the content below to it.

| CLI              | File                              |
| ---------------- | --------------------------------- |
| Claude Code      | `CLAUDE.md`                       |
| GitHub Copilot   | `.github/copilot-instructions.md` |
| Gemini CLI       | `GEMINI.md`                       |
| Codex / OpenCode | `AGENTS.md`                       |
| Cursor           | `.cursor/rules/dev-workflow.md`   |
| Any other        | `AGENTS.md`                       |

If your CLI supports multiple files, `AGENTS.md` is the cross-CLI baseline — most tools read it natively.

## Step 2 — Wire in the active agent

Paste the following block into your instruction file. Change the agent path to match the phase you are starting.

```markdown
## Active Agent

Follow the instructions in [requirements-agent](agents/requirements-agent.md).

## Skills

The agent references skills in [skills/](skills/).
Read the SKILL.md in each skill directory when the agent invokes it.

## Domain Context

Read [CONTEXT.md](CONTEXT.md) if it exists — use the project's domain vocabulary throughout.

## Communication Style

This workflow runs in **caveman mode** by default — terse, no filler, full technical accuracy. See [skills/caveman/](skills/caveman/).

Two things are the exception and are always written in **Plain English after Strunk & White**:

1. **Specification prose** — everything under `docs/spec/**`.
2. **Documentation prose** — arc42 chapters (`docs/*.md`), ADRs (`docs/adr/**`), review reports (`docs/reviews/**`), READMEs, `CONTEXT.md`.

Everything else uses caveman: chat replies, handoff messages, status, commit messages, analysis comments, and any returned asset that is not well-formed prose (code, tests, JSON, Structurizr DSL, config, backlog items). The caveman skill's Auto-Clarity Exception (security warnings, irreversible-action confirmations, ambiguous multi-step sequences) always applies.

Rule of thumb: **the deliverable prose an agent authors is Strunk & White; the talk around it is caveman.**
```

That's it. The agent file contains the full workflow, skill references, and handoff instructions.

## Step 3 — Run the workflow

### The agent chain

```
requirements ──► spec-review ──► architecture ──► architecture-review ──► planning ──► implementation ──► reconciliation ──► qa
    agent    ◄──    agent          agent      ◄──      agent               agent          agent      ◄──      agent       ◄── agent
      ▲       (open issues)          ▲         (open issues)                                 ▲         (code defects)          │
      └───────────────┘              └───────────────┘                                       └─────────────────────────────────┘
                                                                                                          (defects)

Each author/reviewer pair loops until its review is clean:
  requirements ↔ spec-review      (spec consistency, traceability, quality)
  architecture ↔ architecture-review   (ATAM quality attributes)
  implementation ↔ reconciliation ↔ qa (spec alignment, Fagan, security, bug hunt)
```

### Session protocol

Each agent runs in its own session. When an agent finishes, it prints a handoff message. To continue:

1. **End the current session** (or start a new one)
2. **Update your instruction file** — change the agent path to the next agent:

```markdown
## Active Agent

Follow the instructions in [architecture-agent](agents/architecture-agent.md).
```

3. **Start the new session** and paste the handoff message as your first prompt

### Phase-by-phase

#### Phase 1 — Requirements

**Agent**: `requirements-agent`
**Sessions**: 1
**What to say**: _"I want to build [your idea]. Run the requirements agent."_

The agent will interview you (vision → clarification → PRD → spec chain). It pauses for your approval at each major step.

**When done**: the agent prints:

> _"The specification is complete. Start a new session and run the spec review agent against `docs/spec/`."_

#### Phase 1 — Specification Review

**Agent**: `spec-review-agent`
**Sessions**: 1 new session per review pass (separate from the requirements author)
**What to say**: _"Review the specification in `docs/spec/`."_

The reviewer runs `spec-lint` (deterministic traceability and consistency checks, writing `docs/spec/traceability.json`) then a semantic inspection against the requirements-quality characteristics, and files findings as `docs/findings/SPEC-*.md`. If open findings remain:

> _"Spec review found [N] open findings. Start a new session and run the requirements agent to address them."_

Switch back to `requirements-agent`, address the findings, then switch back to `spec-review-agent`. Loop until:

> _"Specification review is clean. Run the architecture agent against `docs/spec/`."_

#### Phase 2 — Architecture (create)

**Agent**: `architecture-agent`
**Sessions**: 1 new session
**What to say**: _"The specification is complete. Create the architecture."_

The agent scaffolds arc42, writes the C4 model, exports diagrams, and writes ADRs.

**When done**:

> _"Architecture is documented. Start a new session and run the architecture review agent against `docs/`."_

#### Phase 2 — Architecture (review loop)

**Agent**: `architecture-review-agent`
**Sessions**: 1 new session per review pass

**What to say**: _"Review the architecture in `docs/`."_

The reviewer runs ATAM, files findings as `docs/findings/ATAM-*.md` for risks. If open findings remain:

> _"Review found [N] open risks. Start a new session and run the architecture agent to address them."_

Switch back to `architecture-agent`, address the findings, then switch back to `architecture-review-agent`. Loop until:

> _"Architecture review is clean. Run the planning agent to create the backlog."_

#### Phase 3 — Planning

**Agent**: `planning-agent`
**Sessions**: 1 new session
**What to say**: _"Create the backlog from the spec and architecture."_

Creates `backlog/ST-*.md` stories (grouped by `epic:` value) with INVEST, MoSCoW (in the story body), classification, and `deps` links.

#### Phase 4 — Implementation

**Agent**: `implementation-agent`
**Sessions**: 1 new session per EPIC (or per issue for large EPICs)
**What to say**: _"Implement issue #[number]."_

Picks an issue, analyses it, implements with TDD, commits, checks for spec drift.

#### Phase 4 — Reconciliation

**Agent**: `reconciliation-agent`
**Sessions**: 1 new session (separate from implementation)
**What to say**: _"Reconcile the spec against the implemented code."_

Builds truth maps from code and spec, diffs them, classifies discrepancies, updates stale docs, and files code defects. Pauses for your approval before committing spec changes.

If code defects are found, switch back to `implementation-agent` to fix them, then return to `reconciliation-agent`. When clean, proceed to QA.

#### Phase 5 — Quality Assurance

**Agent**: `qa-agent`
**Sessions**: 1 new session (separate from implementation)
**What to say**: _"Review the PR for EPIC [name]."_

Runs Fagan inspection, security review, and exploratory testing. Files bugs, loops until clean.

If defects are found, switch back to `implementation-agent` to fix them, then return to `qa-agent`.

## Tips

- **One agent per session** — never activate two agents in the same session. The separation prevents blind spots.
- **Handoff messages are copy-paste prompts** — each agent ends with a message you can paste into the next session verbatim.
- **Skills fire automatically** — you don't invoke skills directly. The agent knows which skills to use and when. The `dev-workflow` router skill is for humans who want to invoke a skill without an agent.
- **`CONTEXT.md` is shared state** — all agents read it. Update it when domain vocabulary changes.
- **`docs/spec/todos.md` tracks open questions** — the requirements agent creates it, other agents append to it.
