# Agent Factory

A structured, AI-assisted software development workflow that takes a project from rough idea to production-quality code. Built on [Semantic Anchors — Spec Driven Development](https://llm-coding.github.io/Semantic-Anchors/spec-driven-development) by Ralf D. Müller, adapted for [arc42](https://arc42.org/) architecture documentation and [Structurizr](https://structurizr.com/) DSL.

![Workflow diagram](docs/assets/images/workflow-diagram.svg)

## What this is

Agent Factory is a toolset of **agents**, **skills**, and **deterministic gates** that drive an AI coding CLI through a full development lifecycle:

1. **Requirements** — interview, PRD, Cockburn use cases, supplementary specs
2. **Architecture** — arc42 documentation, Structurizr C4 model, ADRs, ATAM review
3. **Planning** — backlog with INVEST stories, MoSCoW prioritisation, dependency links
4. **Implementation** — TDD per issue, spec feedback loop, spec reconciliation
5. **Quality** — Fagan inspection, OWASP security review, exploratory bug hunt

Each phase has an **author agent** that produces artifacts and a **reviewer agent** that independently evaluates them in a separate session. The pair loops until the review is clean — the same principle as not reviewing your own pull request.

```
requirements ↔ spec-review → architecture ↔ architecture-review → planning → implementation → reconciliation ↔ qa
```

### Key ideas

- **Semantic anchors** steer the AI toward well-known engineering methods (Cockburn, EARS, ATAM, Fagan, TDD) rather than relying on ad-hoc prompts.
- **Deterministic gates** catch provable defects before an LLM spends judgement on them. Cheap, reproducible, zero false positives. See below.
- **Session isolation** — each agent should be run in its own session. A reviewer never should see the author's reasoning.
- **Eichhorst's Principle** — an LLM is a noisy channel. Short transmissions with error correction (compiler → tests → review) beat one long, unchecked prompt. Each skill is one short transmission.

### Deterministic gates

In manual mode, the review agents invoke the linters directly as their first step.

| Gate                   | Fires at                        | What it checks                                                                                                                      |
| ---------------------- | ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/spec-lint`    | Phase 1 → 2 boundary            | Use-case coverage, traceability links between PRD → actor-goals → use cases → supplementary specs, ID uniqueness, required sections |
| `scripts/arch-lint`    | Phase 2 → 3 boundary            | arc42 chapters exist and cross-reference the Structurizr DSL, ADR index consistency, diagram file references                        |
| `scripts/backlog-lint` | Phase 3 → 4 boundary            | YAML frontmatter schema, dependency graph acyclicity, priority and status values                                                    |
| `scripts/matrix-lint`  | `config/model-matrix.conf` edit | `config/model-matrix.conf` syntax, required fields, valid tier/model mappings                                                       |

The scripts live in `scripts/`, are stdlib-only Python, and can be run standalone:

```bash
scripts/spec-lint docs/spec/
scripts/arch-lint --docs-dir docs/
scripts/backlog-lint backlog/
scripts/matrix-lint config/model-matrix.conf
```

______________________________________________________________________

## Setting up from scratch

Follow these steps on a fresh macOS or Linux machine.

### Step 0 — Install prerequisites

You need five tools. If any are already installed, skip that line.

| Tool                 | What it does                           | Install                                                                                                           |
| -------------------- | -------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Git**              | Version control                        | macOS: `xcode-select --install`; Linux: `sudo apt install git` (Debian/Ubuntu) or `sudo dnf install git` (Fedora) |
| **Python ≥ 3.10**    | Runs the orchestrator and lint scripts | macOS: `brew install python@3.12`; Linux: `sudo apt install python3.12` or equivalent                             |
| **uv**               | Fast Python package manager            | `curl -LsSf https://astral.sh/uv/install.sh \| sh` ([docs](https://docs.astral.sh/uv/))                           |
| **Docker**           | Runs Structurizr for diagram export    | [Install Docker](https://docs.docker.com/get-docker/)                                                             |
| **An AI coding CLI** | The agent runtime                      | See below                                                                                                         |

#### Exemplary AI coding CLIs

Install **one** (or more) of these. The examples in this README use GitHub Copilot CLI.

| CLI                                                           | Install docs                                 |
| ------------------------------------------------------------- | -------------------------------------------- |
| [GitHub Copilot CLI](https://docs.github.com/en/copilot)      | Requires a Copilot subscription and `gh` CLI |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | `npm install -g @anthropic-ai/claude-code`   |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli)     | `npm install -g @anthropic-ai/gemini-cli`    |
| [Codex / OpenCode](https://github.com/openai/codex)           | See vendor README                            |
| [Cursor](https://cursor.sh)                                   | Download from website                        |
| Any tool that reads `AGENTS.md`                               | —                                            |

#### Verify everything is ready

```bash
git --version          # ≥ 2.x
python3 --version      # ≥ 3.10
docker info            # daemon running
```
