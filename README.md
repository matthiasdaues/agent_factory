# Agent Factory

Agent Factory is a structured, AI-assisted software development workflow. It takes a project from a rough idea to production-quality code. It is built on [Semantic Anchors — Spec Driven Development](https://llm-coding.github.io/Semantic-Anchors/spec-driven-development) by Ralf D. Müller, adapted for [arc42](https://arc42.org/) architecture documentation and [Structurizr](https://structurizr.com/) DSL.

![Workflow diagram](docs/assets/images/workflow-diagram.svg)

## Purpose

Agent Factory is a toolset of **agents**, **skills**, and **deterministic gates**. Together they drive an AI coding CLI through a full development lifecycle:

1. **Requirements** — interview, PRD, Cockburn use cases, supplementary specs
2. **Architecture** — arc42 documentation, Structurizr C4 model, ADRs, ATAM review
3. **Planning** — backlog with INVEST stories, MoSCoW prioritisation, dependency links
4. **Implementation** — TDD per issue, spec feedback loop, spec reconciliation
5. **Quality** — Fagan inspection, OWASP security review, exploratory bug hunt

Each phase has an **author agent** and a **reviewer agent**. The author produces artifacts. The reviewer evaluates them independently, in a separate session. The pair loops until the review is clean. This is the same principle as not reviewing your own pull request.

```
requirements ↔ spec-review → architecture ↔ architecture-review → planning → implementation → reconciliation ↔ qa
```

### Key ideas

- **Semantic anchors** steer the AI toward well-known engineering methods — Cockburn, EARS, ATAM, Fagan, TDD — instead of ad-hoc prompts.
- **Deterministic gates** catch provable defects before an LLM spends judgement on them. They are cheap, reproducible, and free of false positives. See [factory/README.md § Deterministic Gates](factory/README.md#deterministic-gates).
- **Session isolation.** Run each agent in its own session. A reviewer should never see the author's reasoning.
- **Eichhorst's Principle.** An LLM is a noisy channel. Short transmissions with error correction — compiler, tests, review — beat one long, unchecked prompt. Each skill is one short transmission.

______________________________________________________________________

## Prerequisites

You need five tools. Skip any line you already have.

| Tool                 | What it does                                                                                                    | Install                                                                                                            |
| -------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Git**              | Version control                                                                                                 | macOS: `xcode-select --install`. Linux: `sudo apt install git` (Debian/Ubuntu) or `sudo dnf install git` (Fedora). |
| **Python ≥ 3.10**    | Runs the lint scripts and the init script                                                                       | macOS: `brew install python@3.12`. Linux: `sudo apt install python3.12` or equivalent.                             |
| **uv**               | Runs `mdformat`, `ruff`, and `pre-commit` on demand, via `uvx` — nothing else to install for linting/formatting | `curl -LsSf https://astral.sh/uv/install.sh \| sh` ([docs](https://docs.astral.sh/uv/))                            |
| **Docker**           | Runs Structurizr, for diagram export only                                                                       | [Install Docker](https://docs.docker.com/get-docker/)                                                              |
| **An AI coding CLI** | The agent runtime                                                                                               | See below                                                                                                          |

You do not need to separately install `ruff`, `mdformat`, or `pre-commit`. Every gate script and hook runs them through `uvx`. This matches the zero-local-install pattern `factory/scripts/structurizr` already uses for Docker.

### Pick an AI coding CLI

Install one, or more. This README's examples use GitHub Copilot CLI.

| CLI                                                           | Install docs                                 |
| ------------------------------------------------------------- | -------------------------------------------- |
| [GitHub Copilot CLI](https://docs.github.com/en/copilot)      | Requires a Copilot subscription and `gh` CLI |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | `npm install -g @anthropic-ai/claude-code`   |

### Verify everything is ready

```bash
git --version      # ≥ 2.x
python3 --version  # ≥ 3.10
uvx --version       # bundled with uv
docker info         # daemon running
```

______________________________________________________________________

## Using Agent Factory

To use the factory as a pluggable, agent-driven tool in a project folder — install, wire it into a new or existing repo, run the workflow, troubleshoot — see [factory/README.md](factory/README.md).

Agent Factory also has a deterministic external wrapper: a CLI that automates the phase chain instead of driving each agent by hand, one session at a time. This is still a work in progress. Learn more in [orchestrator/README.md](orchestrator/README.md).

______________________________________________________________________

## Project Directory Tree

**`orchestrator/`** is a permanent, nested sub-project — see [orchestrator/README.md](orchestrator/README.md). Unlike `factory/` (copied wholesale into consumer projects by `init-factory`), it is not distributed — `init-factory` does not touch it.

```
agent_factory/
├── factory/                          # Canonical content. Copied wholesale into any project; never hand-edited there.
│   ├── agents/                       # One .md file per agent
│   ├── skills/                       # One folder per skill, each holding a SKILL.md
│   ├── playbooks/                    # End-to-end flows for common scenarios (bug fix, feature addition, ...)
│   ├── rulebooks/                    # Cross-cutting conventions: commit format, cross-references, ADR style, ...
│   ├── scripts/                      # Deterministic gates (*-lint) plus setup tooling (init-factory, mdformat, ...)
│   ├── config/                       # Templates: AGENTS.md, pre-commit-config.yaml, model-matrix.conf
│   └── INDEX.md                      # Generated catalog of every agent and skill — regenerate with index-lint
├── orchestrator/                     # Python CLI that drives agent sessions (run-step, run-phase, etc.) — nested sub-project, not distributed by init-factory
│   ├── src/                          # CLI source code
│   ├── tests/                        # CLI tests
│   ├── docs/                         # CLI documentation (own arc42 set, own docs/adr/, own docs/spec/)
│   ├── backlog/                      # CLI backlog and stories
│   └── pyproject.toml                # CLI package configuration
├── backlog/                          # Whole-repo backlog — cross-cutting stories, distinct from orchestrator/backlog/
├── docs/                             # This repo's own whole-repo, cross-cutting docs — distinct from orchestrator/docs/
│   ├── CONTEXT-MAP.md                # Bounded-context map for this multi-context repo (orchestrator, factory, factory_api)
│   ├── adr/                          # Whole-repo Architecture Decision Records — own sequence, separate from orchestrator/docs/adr/
│   ├── reviews/                      # Retrospective and reconciliation reports
│   └── assets/                       # Diagrams and exported images
├── config/                           # This project's own copy of model-matrix.conf — diverges from factory/
│   └── model-matrix.conf
├── .claude/                          # Local only, gitignored. Symlinks into factory/, for Claude Code.
├── .github/                          # Local only, gitignored. Symlinks into factory/, for GitHub Copilot CLI.
├── .pre-commit-config.yaml           # Real, merged file — factory's generic hooks plus orchestrator-scoped ones (see docs/adr/0001-precommit-monorepo-scoping.md)
├── .gitignore
└── README.md
```

`docs/spec/` and `docs/findings/` don't exist at root yet — created lazily, as needed, once `factory/` grows its own spec (see `docs/CONTEXT-MAP.md`).

______________________________________________________________________

## License

MIT — see [LICENSE](LICENSE).

Authored by Matthias Daues — see [AUTHORS.md](AUTHORS.md).
