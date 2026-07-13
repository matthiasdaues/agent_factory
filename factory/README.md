# Factory

`factory/` is the Agent Factory toolset itself — agents, skills, playbooks, and checks. `init-factory` copies it wholesale into your own project. You never hand-edit the copy; you re-run `init-factory` to update it.

Part of [Agent Factory](../README.md). See also: [orchestrator](../orchestrator/README.md), [architecture docs](../docs/README.md).

This page gets you from zero to a running first playbook. For what agents, skills, playbooks, and rulebooks actually are, and how the checks work, see the [factory guide](docs/factory-guide.md).

## Prerequisites

You need five tools. Skip any line you already have.

| Tool                 | What it does                                        | Install                                                                                                                                                                     |
| -------------------- | --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Git**              | Version control                                     | macOS: `xcode-select --install`. Linux: `sudo apt install git` (Debian/Ubuntu) or `sudo dnf install git` (Fedora).                                                          |
| **Python ≥ 3.10**    | Runs the check scripts and the init script          | macOS: `brew install python@3.12`. Linux: `sudo apt install python3.12` or equivalent.                                                                                      |
| **uv**               | Runs `mdformat`, `ruff`, and `pre-commit` on demand | `curl -LsSf https://astral.sh/uv/install.sh \| sh` ([docs](https://docs.astral.sh/uv/))                                                                                     |
| **tiktoken**         | Token counting for INDEX.yaml budget fields         | `pip install tiktoken` (optional — `index-lint` falls back to chars ÷ 4 without it)                                                                                         |
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

`init-factory` is a plain script — **it needs no AI to run it**, a shell is enough. Here's exactly what it creates:

1. **`factory/`** — copied wholesale from agent_factory, containing all agents, skills, playbooks, scripts, and rulebooks
2. **`.claude/`** and **`.github/`** — created (or left alone if they exist), with symlinks into `factory/`:
   - `agents/`, `skills/`, `playbooks/`, `rulebooks/`, `scripts/`, `INDEX.yaml`
   - `.claude/CLAUDE.md` → `factory/config/AGENTS.md` (orientation file)
   - `.github/copilot-instructions.md` → `factory/config/AGENTS.md`
   - `.claude/hooks/block-dangerous-git.sh` → `factory/config/hooks/block-dangerous-git.sh`
   - `.github/hooks/block-dangerous-git.sh` → `factory/config/hooks/block-dangerous-git.sh`
   - `.github/hooks/block-dangerous-git.json` → `factory/config/hooks/block-dangerous-git.json`
3. **`.claude/settings.json`** — created or updated with the git-safety guardrail PreToolUse hook
4. **`config/model.conf`** — copied (not symlinked) as a starter; you customize this per project
5. **`.pre-commit-config.yaml`** — symlinked to `factory/config/pre-commit-config.yaml` if missing, or merged if you already have one
6. **`.gitignore`** — appends Agent Factory lines (`.claude`, `.github`, session ephemera, Python cache folders) if not already present
7. Runs `git init` if your target isn't already a git repo
8. Runs `uvx pre-commit install` to wire the hooks into git

**Safe to re-run**: every step is idempotent. If `factory/` already exists, it's left untouched (use the update script instead). Existing `.pre-commit-config.yaml` with your own hooks? `init-factory` merges Agent Factory's hooks in without disturbing yours.

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

## Test execution hooks

Agent Factory runs tests through unavoidable hooks, not by asking agents to run them. This enforces the core principle: **creation is agentic, validation is deterministic**. Tests run automatically at three points:

1. **Pre-commit hook** (bypassable with `--no-verify`) — runs tests on changed files only, fast feedback during development
2. **Pre-push hook** (no bypass) — runs full test suite before sharing your work, blocks push if tests fail
3. **Phase advance gates** — FSM entry conditions check `tests_pass` before advancing to QA or DONE states

### Framework detection

`factory/scripts/run-tests` auto-detects your test framework from project structure:

- **pytest**: detected from `pyproject.toml`, runs via `uv run pytest`
- **jest**: detected from `package.json`, runs via `npm test`
- **go test**: detected from `go.mod`, runs via `go test ./...`
- **cargo test**: detected from `Cargo.toml`, runs via `cargo test`

No configuration needed for single-framework projects. Multi-framework monorepos are detected and fail loudly (not yet supported).

### Agent test iteration

Agents cannot run bare test commands (`pytest`, `npm test`) — these are blocked by the git safety hooks. But agents writing tests need a tight feedback loop. Use staged mode:

```bash
# Agent stages test file
git add tests/test_foo.py

# Agent runs tests on staged files
factory/scripts/run-tests --staged

# Agent sees results, fixes test, stages again, repeats
```

This preserves the "tests via factory mechanisms" principle while enabling TDD workflows.

See [ADR-0003](../docs/adr/0003-test-execution-via-hooks.md) for the architecture rationale and [UC-09](../docs/spec/use_cases/UC-09-run-tests-via-hook.md) for detailed behavior.

## Using this in an existing repo

`init-factory` works the same way against a repo that already has its own history and its own `.pre-commit-config.yaml` — run it from inside that repo. It only adds what Agent Factory needs; it never rewrites or removes anything already there. Details, including what to do if it can't merge your existing `.pre-commit-config.yaml`, are in the [factory guide § Using this in an existing repo](docs/factory-guide.md#using-this-in-an-existing-repo).

## Troubleshooting

See the [factory guide § Troubleshooting](docs/factory-guide.md#troubleshooting) for fixes to the errors you're most likely to hit during setup.
