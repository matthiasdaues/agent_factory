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

| Gate                           | Fires at                                | What it checks                                                                                                                      |
| ------------------------------ | --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `factory/scripts/spec-lint`    | Phase 1 → 2 boundary                    | Use-case coverage, traceability links between PRD → actor-goals → use cases → supplementary specs, ID uniqueness, required sections |
| `factory/scripts/arch-lint`    | Phase 2 → 3 boundary                    | arc42 chapters exist and cross-reference the Structurizr DSL, ADR index consistency, diagram file references                        |
| `factory/scripts/backlog-lint` | Phase 3 → 4 boundary                    | YAML frontmatter schema, dependency graph acyclicity, priority and status values                                                    |
| `factory/scripts/matrix-lint`  | `factory/config/model-matrix.conf` edit | `factory/config/model-matrix.conf` syntax, required fields, valid tier/model mappings                                               |

The scripts live in `factory/scripts/`, are stdlib-only Python, and can be run standalone:

```bash
factory/scripts/spec-lint docs/spec/
factory/scripts/arch-lint --docs-dir docs/
factory/scripts/backlog-lint backlog/
factory/scripts/matrix-lint factory/config/model-matrix.conf
```

______________________________________________________________________

## Setting up from scratch

Follow these steps on a fresh macOS or Linux machine.

### Step 0 — Install prerequisites

You need five tools. If any are already installed, skip that line.

| Tool                 | What it does                                                                                                   | Install                                                                                                           |
| -------------------- | -------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Git**              | Version control                                                                                                | macOS: `xcode-select --install`; Linux: `sudo apt install git` (Debian/Ubuntu) or `sudo dnf install git` (Fedora) |
| **Python ≥ 3.10**    | Runs the orchestrator and lint scripts                                                                         | macOS: `brew install python@3.12`; Linux: `sudo apt install python3.12` or equivalent                             |
| **uv**               | Runs `mdformat`, `ruff`, and `pre-commit` on demand via `uvx` — nothing else to install for linting/formatting | `curl -LsSf https://astral.sh/uv/install.sh \| sh` ([docs](https://docs.astral.sh/uv/))                           |
| **Docker**           | Runs Structurizr for diagram export                                                                            | [Install Docker](https://docs.docker.com/get-docker/)                                                             |
| **An AI coding CLI** | The agent runtime                                                                                              | See below                                                                                                         |

You do **not** need to separately install `ruff`, `mdformat`, or `pre-commit` — every gate script and hook runs them through `uvx`, matching `factory/scripts/structurizr`'s zero-local-install pattern (Docker there, `uvx` here).

#### Exemplary AI coding CLIs

Install **one** (or more) of these. The examples in this README use GitHub Copilot CLI.

| CLI                                                           | Install docs                                 |
| ------------------------------------------------------------- | -------------------------------------------- |
| [GitHub Copilot CLI](https://docs.github.com/en/copilot)      | Requires a Copilot subscription and `gh` CLI |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | `npm install -g @anthropic-ai/claude-code`   |

#### Verify everything is ready

```bash
git --version          # ≥ 2.x
python3 --version      # ≥ 3.10
uvx --version           # bundled with uv
docker info            # daemon running
```

### Step 1 — Wire the factory into a project

`factory/scripts/init-factory` does the rest: `git init` if needed, symlinks `factory/{agents,skills,playbooks,rulebooks,scripts,INDEX.md}` and `factory/config/AGENTS.md` into `.claude/` and `.github/` (both, always — no CLI-choice prompt), copies `factory/config/model-matrix.conf` in as an editable starter, and wires up `.pre-commit-config.yaml` (symlinked if none exists yet, merged in alongside whatever hooks a project already has otherwise). It's a normal, standalone, idempotent Python script — **no AI required to run it**:

```bash
git clone <agent-factory-repo-url> /path/to/agent_factory
/path/to/agent_factory/factory/scripts/init-factory --target /path/to/your/project
```

Works the same whether `--target` is empty or an existing repo with its own history, `.gitignore`, and pre-commit hooks — every step states its own fresh-vs-existing behavior in `init-factory --help`. Safe to re-run: nothing already correctly in place gets touched twice. If it finds something it can't safely work around (a real, non-Agent-Factory file already sitting where a symlink needs to go; a `.pre-commit-config.yaml` structure it doesn't recognize), it stops immediately and names the exact path — it never partially applies a run or silently overwrites existing content.

If you'd rather trigger it conversationally, the `init-factory` skill (`factory/skills/init-factory/SKILL.md`) is a thin wrapper that confirms the target with you, runs the same script, and relays its output — same mechanism, same idempotency, just invoked through the AI CLI instead of a shell. On the very first run in a project, there's no installed skill yet to invoke by name — point the CLI at the file directly (e.g. "read `factory/skills/init-factory/SKILL.md` in the agent_factory checkout and follow it").
