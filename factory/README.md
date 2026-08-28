# Factory

`factory/` is the Agent Factory toolset itself — agents, skills, playbooks, and checks. `init-factory` copies it wholesale into your own project. You never hand-edit the copy; run `update-factory` to bring it up to date when your `agent_factory` checkout moves forward.

Part of [Agent Factory](../README.md). See also: [orchestrator](../orchestrator/README.md), [architecture docs](../docs/README.md).

This page gets you from zero to a running first playbook. Never used Agent Factory — or any AI coding workflow — before? Read the [beginner's introduction](../docs/arc42/beginner-intro.md) first; it explains what you are about to do before you run any command. For what agents, skills, playbooks, and rulebooks actually are, and how the checks work, see the [factory guide](docs/factory-guide.md).

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

`init-factory` is a plain script — **it needs no AI to run it**, a shell is enough. It is built on two promises: it never disturbs what your project already has, and everything it adds can be removed without a trace. Here's exactly what it creates:

1. **`factory/`** — copied wholesale from agent_factory, containing all agents, skills, playbooks, scripts, and rulebooks
2. **`.claude/`**, **`.github/`**, and **`.pi/`** — created (or left alone if they exist), with symlinks into `factory/`:
   - `agents/`, `skills/`, `playbooks/`, `rulebooks/`, `scripts/`, `INDEX.yaml`
   - `.claude/CLAUDE.md` → `factory/config/AGENTS.md` (orientation file) — **if you already have one**, a marker-fenced `@`-include is prepended instead; your content is preserved below it
   - `.github/copilot-instructions.md` → `factory/config/AGENTS.md` — **if you already have one**, the full orientation content is inlined between markers at the top; your content is preserved below it
   - `AGENTS.md` → `factory/config/AGENTS.md` for Pi/Codex — **if you already have one**, the orientation content is inlined between markers; your content is preserved below it
   - `.claude/hooks/block-dangerous-git.sh` → `factory/config/hooks/block-dangerous-git.sh`
   - `.github/hooks/block-dangerous-git.sh` → `factory/config/hooks/block-dangerous-git.sh`
   - `.github/hooks/block-dangerous-git.json` → `factory/config/hooks/block-dangerous-git.json`
   - `.pi/extensions/block-dangerous-git.ts` → `factory/config/extensions/block-dangerous-git.ts`
   - `.pi/extensions/run-agent.ts` → `factory/config/extensions/run-agent.ts` (Pi's subagent mechanism — see the note below)
   - `.pi/extensions/dispatch-wave.ts` → `factory/config/extensions/dispatch-wave.ts` (Pi's parallel worktree dispatch — see the note below)
3. **`.claude/settings.json`** — created or updated with the git-safety guardrail PreToolUse hook
4. **Project configuration** — `config/model.conf` is copied as a starter, and
   `config/project.json` stores the stable generated project UUID plus the
   project name explicitly requested during initialization
5. **`.pre-commit-config.yaml`** — the one tracked change. Agent Factory's gates are added as a `- repo: local` block whose hook ids are all prefixed `agent_factory_hook-`, spliced in at the top of your `repos:` list (or written as a fresh file if you had none). Your own hooks are never touched, and the prefix makes the block extricable. An inert `.pre-commit-config.yml` is left alone — pre-commit only auto-reads `.yaml`.
6. **`.gitignore`** — a single marker-delimited block headed `agent_factory related`, listing exactly the footprint Agent Factory adds (`factory/`, `.claude/`, `.pi/`, `.agent-factory/`, `.current-work/`, `config/model.conf`, `config/project.json`, `AGENTS.md` when init-factory created it, session ephemera, and the specific `.github/*` entries). Note it ignores those `.github` entries **individually** — never all of `.github`, so your Actions workflows stay tracked.
7. **`.agent-factory/factory-install.json`** — a removal manifest recording exactly what this run did, so `remove-factory` can reverse it precisely
8. Runs `git init` if your target isn't already a git repo, then `uvx pre-commit install` to wire the hooks into git

**Safe to re-run**: every step is idempotent, and a re-run reads the prior manifest so it never loses track of what it owns. If `factory/` already exists, it's left untouched (use the update script instead).

Because the whole footprint is git-ignored, the only thing `init-factory` adds to your tracked history is that one `agent_factory related` `.gitignore` block and the prefixed pre-commit hooks. Check it worked, then commit:

```bash
git status                        # only .gitignore and .pre-commit-config.yaml show as changes
git add -A && git commit -m "init: wire up Agent Factory"
```

If the first commit modifies a few files, that's `mdformat`/`ruff` auto-fixing formatting — re-stage and commit again.

### Removing it again

`init-factory` is fully reversible. From the project root:

```bash
factory/scripts/remove-factory
```

It reads the manifest and takes everything back down to a clean `git status`: the git-ignored footprint is deleted, orientation blocks are stripped from existing orientation files, the `agent_factory related` `.gitignore` block is stripped (restoring your file's exact bytes), and the `agent_factory_hook-` pre-commit block is removed while your own hooks stay put. A project that already had its own orientation file, pre-commit config, or `.github/workflows` gets them back exactly as they were.

Now open your AI coding CLI in `my-project` and greet it. It should read `.claude/CLAUDE.md`, `.github/copilot-instructions.md`, or `AGENTS.md` (Pi) and confirm it understands the local-first rule.

**Pi caveat:** unlike Claude Code and Copilot CLI, Pi has no built-in PreToolUse hook file. Agent Factory therefore scaffolds a project-local Pi extension under `.pi/extensions/` that blocks the same dangerous commands when the project is trusted and project-local extensions are loaded. In non-interactive or untrusted-project runs, that extension may not load. For stronger Pi enforcement, install the extension globally under `~/.pi/agent/extensions/`, invoke Pi with `-e`, or run Pi in a sandbox/container.

**Running agents under Pi:** Agent Factory supports Pi in parallel with Claude Code and Copilot CLI — the same agents, skills, and playbooks run under all three. Claude Code and Copilot CLI spawn subagents natively; Pi has no native subagent, so `init-factory` also installs `.pi/extensions/run-agent.ts`, which registers a `run_agent` tool. Under Pi, run a factory agent by calling `run_agent` — it launches the agent in a separate `pi` session, preserving the author/reviewer independence the phase chain depends on. For parallel implementation, `.pi/extensions/dispatch-wave.ts` adds a `dispatch_wave` tool that runs a whole wave of agents at once, each in its own git worktree, merged through `premerge-check` — the Pi port of `implementation-agent`. See the [factory guide § Running an agent in a separate session](docs/factory-guide.md#running-an-agent-in-a-separate-session).

## Your first playbook

Once the CLI greets you, pick a playbook from `factory/playbooks/` — a step-by-step recipe for your situation. If this is your first time, try [`poc-spike.md`](playbooks/poc-spike.md): no spec, no architecture, no checks, just one idea turned into something you can run in minutes. It's the fastest way to see an agent and the CLI work together before committing to a real project.

For every other situation — a new project, an existing codebase, a bug, a feature — see the [factory guide § Playbooks](docs/factory-guide.md#playbooks) for which one fits.

### Running a playbook automatically

After completing the human-driven requirements phase, let the installed
orchestrator drive the remaining agent sessions and deterministic gates:

```bash
factory/scripts/run-playbook \
  --playbook greenfield-development \
  --from-state PHASE_2_ARCHITECTURE \
  --cli claude
```

It stops at human gates and records progress in
`.current-work/playbook-state.yml`; re-run the same command without
`--from-state` to resume. The launcher runs the pinned
`agent-factory-orchestrator` package through `uvx`, without changing the
project environment or installing a global tool. The default source is the
exact `orchestrator-v0.1.0` Git tag. Override `AF_ORCHESTRATOR_SOURCE` with
another exact version, a pinned Git source, or a local package path when
testing a release. Claude and Copilot are supported dispatch backends.

## Test execution hooks

Agent Factory runs tests through mechanically triggered gates, not by asking agents to run them. This enforces the core principle: **creation is agentic, validation is deterministic**. Tests run automatically at three points:

1. **Pre-commit hook** (bypassable with `--no-verify`) — runs tests on changed files only, fast feedback during development
2. **Pre-push hook** (human bypass: `git push --no-verify`) — runs the full test suite before an ordinary push and blocks that push if tests fail
3. **Phase advance gates** — FSM entry conditions check `tests_pass` before advancing to the QA phase

The canonical template does not yet install point 1 into consumer projects;
that remaining configuration drift is tracked as
[`RECON-0018`](../docs/findings/RECON-0018.md). This repository's own merged
configuration already contains the changed-only hook.

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
