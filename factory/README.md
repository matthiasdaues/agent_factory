# Factory

`factory/` is the Agent Factory toolset itself — agents, skills, playbooks, and checks. `init-factory` copies it wholesale into your own project. You never hand-edit the copy; you re-run `init-factory` to update it.

This page gets you from zero to a running first playbook. For what agents, skills, playbooks, and rulebooks actually are, and how the checks work, see the [factory guide](docs/factory-guide.md).

## Prerequisites

You need five tools. Skip any line you already have.

| Tool                 | What it does                                        | Install                                                                                                                                                                     |
| -------------------- | --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Git**              | Version control                                     | macOS: `xcode-select --install`. Linux: `sudo apt install git` (Debian/Ubuntu) or `sudo dnf install git` (Fedora).                                                          |
| **Python ≥ 3.10**    | Runs the check scripts and the init script          | macOS: `brew install python@3.12`. Linux: `sudo apt install python3.12` or equivalent.                                                                                      |
| **uv**               | Runs `mdformat`, `ruff`, and `pre-commit` on demand | `curl -LsSf https://astral.sh/uv/install.sh \| sh` ([docs](https://docs.astral.sh/uv/))                                                                                     |
| **Docker**           | Renders architecture diagrams (optional)            | [Install Docker](https://docs.docker.com/get-docker/)                                                                                                                       |
| **An AI coding CLI** | Runs the agents and skills                          | e.g. [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (`npm install -g @anthropic-ai/claude-code`) or [GitHub Copilot CLI](https://docs.github.com/en/copilot) |

You do not need to separately install `ruff`, `mdformat`, or `pre-commit` — every check and hook runs them through `uvx`.

Verify you're ready:

```bash
git --version      # ≥ 2.x
python3 --version  # ≥ 3.10
uvx --version       # bundled with uv
```

## Quick start

```bash
# 1. Clone Agent Factory somewhere on disk. You only do this once per machine.
git clone <agent-factory-repo-url> agent_factory

# 2. Create your project directory (or use one you already have).
mkdir my-project && cd my-project

# 3. Run the init script against it.
../agent_factory/factory/scripts/init-factory
```

`init-factory` does the rest: it runs `git init` if needed, copies `factory/` into your project, wires it up for your AI CLI, installs a git-safety guardrail hook for both Claude Code and Copilot CLI, and installs the checks as a pre-commit hook. It's a plain script — **it needs no AI to run it**, a shell is enough.

Check it worked, then commit:

```bash
git status                        # .pre-commit-config.yaml and config/ are now untracked, ready to commit
git add -A && git commit -m "init: wire up Agent Factory"
```

If the first commit modifies a few files, that's `mdformat`/`ruff` auto-fixing formatting — re-stage and commit again.

Now open your AI coding CLI in `my-project` and greet it. It should read `.claude/CLAUDE.md` (or `.github/copilot-instructions.md`) and confirm it understands the local-first rule.

## Your first playbook

Once the CLI greets you, pick a playbook from `factory/playbooks/` — a step-by-step recipe for your situation. If this is your first time, try [`poc-spike.md`](playbooks/poc-spike.md): no spec, no architecture, no checks, just one idea turned into something you can run in minutes. It's the fastest way to see an agent and the CLI work together before committing to a real project.

For every other situation — a new project, an existing codebase, a bug, a feature — see the [factory guide § Playbooks](docs/factory-guide.md#playbooks) for which one fits.

## Using this in an existing repo

`init-factory` works the same way against a repo that already has its own history and its own `.pre-commit-config.yaml` — run it from inside that repo. It only adds what Agent Factory needs; it never rewrites or removes anything already there. Details, including what to do if it can't merge your existing `.pre-commit-config.yaml`, are in the [factory guide § Using this in an existing repo](docs/factory-guide.md#using-this-in-an-existing-repo).

## Troubleshooting

See the [factory guide § Troubleshooting](docs/factory-guide.md#troubleshooting) for fixes to the errors you're most likely to hit during setup.
