# Factory

The installable toolset: agents, skills, playbooks, and checks. `init-factory` copies it into your project. `update-factory` refreshes the copy later.

Part of [Agent Factory](../../README.md).

## Prerequisites

| Tool                 | Why                                                           | Install                                                                                                                               |
| -------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **Git ≥ 2.x**        | Version control                                               | macOS: `xcode-select --install`. Linux: `sudo apt install git` / `sudo dnf install git`.                                              |
| **Python ≥ 3.10**    | Runs init and check scripts                                   | macOS: `brew install python@3.12`. Linux: `sudo apt install python3.12` or equivalent.                                                |
| **uv**               | Runs check tools and pre-commit hooks without global installs | `curl -LsSf https://astral.sh/uv/install.sh \| sh` ([docs](https://docs.astral.sh/uv/))                                               |
| **An AI coding CLI** | Runs agents and skills                                        | [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [GitHub Copilot CLI](https://docs.github.com/en/copilot), Pi, or Codex |

Optional: **tiktoken** (`pip install tiktoken`) for token counting in INDEX.yaml; **Docker** for rendering architecture diagrams.

## Install

```bash
git clone <agent-factory-repo-url> agent_factory
cd agent_factory
./init-factory your-project
```

The wrapper accepts a target directory as its first argument. It delegates to `packages/factory/scripts/init-factory --target <dir>`, which you can also call directly with any of its flags (see [§ CLI flags](#cli-flags) below). Additional arguments after the target are forwarded: `./init-factory your-project --cli claude --project-name "My App"`.

The script copies a `factory/` directory into your project and asks which CLI you use. It touches two tracked files:

- **`.pre-commit-config.yaml`** — adds a `- repo: local` block at the top. All hook ids start with `agent_factory_hook-`. Your hooks are not touched.
- **`.gitignore`** — appends a marker-delimited block listing everything Agent Factory added. `.github/` entries are listed individually so your workflows stay tracked.

Everything else is git-ignored. Your code, config, and history are not modified.

```bash
git status   # .gitignore and .pre-commit-config.yaml are the only tracked changes
git add -A && git commit -m "init: wire up Agent Factory"
```

If the first commit reformats files, that is the pre-commit hooks auto-fixing — re-stage and commit again.

Works the same against an existing repo with its own pre-commit config. Details in the [factory guide § Using this in an existing repo](docs/factory-guide.md#using-this-in-an-existing-repo).

### Update

```bash
factory/scripts/update-factory
```

Refreshes the installed `factory/` to match the current checkout. Before replacing, it compares per-file checksums to detect local changes you made. If changes are found, the update stops (exit 2) unless you pass `--force`, which preserves changed files in `.agent-factory/factory-user-changes/<timestamp>/`. Use `--check` to see the report without touching anything. On failure, the previous `factory/` is restored automatically.

### Add or remove CLIs

```bash
factory/scripts/init-factory --add copilot      # wire a new CLI
factory/scripts/init-factory --add               # interactive menu
factory/scripts/init-factory --remove pi         # unwire a CLI
factory/scripts/init-factory --remove            # interactive menu
```

Incrementally adds or removes CLI wiring — dot-directories, symlinks, guardrails, step guards, usage capture, freshness hooks, and generated agents — without re-running the full installer. Updates the `.gitignore` block and install manifest.

### Remove

```bash
factory/scripts/remove-factory
```

Reads the install manifest and reverses everything. Your pre-commit hooks, orientation files, and workflows come back as they were.

## What you configure

The installer creates two local config files (git-ignored) and one directory is created later during onboarding:

- **`config/project.json`** — project identity: a stable UUID, the human-readable name you gave at install time, your declared test command, and `safety_critical_paths` (file globs that route work to the strongest AI model tier). Every usage record carries the project id.
- **`config/model.conf`** — maps agent tiers (`economy`, `standard`, `strong`) to concrete AI model ids, per CLI. If a dispatch requests a tier with no mapping, `on_missing = halt` stops it — no silent fallback. Claude Code resolves models natively and has no entries here. See the [factory guide § Model matrix and tiers](docs/factory-guide.md#model-matrix-and-tiers).
- **`docs/agent-context/`** — a YAML routing switchboard that tells agents where your project's knowledge lives. Created during your first real playbook run (greenfield or brownfield), when VIRGIL walks you through the `capture-context` interview. See the [factory guide § Agent Context](docs/factory-guide.md#agent-context).

All three are local configuration, not project source. Edit them directly any time.

## Runtime directories

Two git-ignored directories appear as you work. You never create them by hand.

- **`.agent-factory/`** — the factory's private runtime area. Holds the install manifest (`factory-install.json`), the usage-capture runtime (tokenizer, adapters), and all recorded usage data (`usage/*.jsonl` and `usage/transcripts/`). Created by `init-factory`; removed cleanly by `remove-factory`. You read usage records here; you never edit them.
- **`.current-work/`** — ephemeral working state for the active playbook run. Holds the phase-gate marker (`playbook-state.yml`), per-story step manifests, the dispatch ledger, and session logs. Scoped to your local machine and the current piece of work — not portable, not meant to be committed. Disappears when the work is done.

## First playbook

Open your AI coding CLI in the project directory. **VIRGIL** — the built-in guide — greets you with four options: a newcomer tour (A), a situation-based playbook picker (B), direct agent/playbook access (C), or open conversation (D). If you have an existing codebase, VIRGIL first offers a short **fitting** — a few questions to confirm its guesses about your stack and wire up the right hooks. Skip it any time.

To see things work before committing to a real project, pick [`poc-spike`](playbooks/poc-spike.md). One idea in, one runnable prototype out.

For other situations — new project, existing codebase, bug, feature, research — see the [factory guide § Playbooks](docs/factory-guide.md#playbooks).

## How it works

Your AI assistant reads an orientation file that loads the factory's agents, skills, and rules. **VIRGIL** — the default session persona — greets you, helps you choose a playbook, and guides you through setup. On your first real project session, VIRGIL walks you through the `capture-context` skill, which creates `docs/agent-context/` — a YAML routing switchboard that tells agents where your project's knowledge lives without duplicating it.

The [factory guide](docs/factory-guide.md) covers the full picture:

- [Factory directory layout](docs/factory-guide.md#factory-directory-layout) — what each subdirectory of `factory/` contains
- [Agent context](docs/factory-guide.md#agent-context) — how the YAML routing switchboard connects agents to project knowledge, and when it gets created
- [Model matrix and tiers](docs/factory-guide.md#model-matrix-and-tiers) — how `config/model.conf` maps economy/standard/strong tiers to concrete AI models per CLI
- What agents, skills, playbooks, and rulebooks are
- How the check scripts and phase gates work
- Test execution through hooks and gates
- CLI-specific notes (Pi subagent support, Codex agent generation)
- Troubleshooting

## Reference

### CLI flags

**`init-factory`** (or the root `./init-factory` wrapper):

| Flag                                      | Effect                                                                                 |
| ----------------------------------------- | -------------------------------------------------------------------------------------- |
| `--target <dir>`                          | Project directory (default: cwd)                                                       |
| `--source <dir>`                          | Agent Factory checkout to copy from (default: auto-detected from script location)      |
| `--cli claude copilot pi codex`           | Which CLIs to wire (default: auto-detect from existing dot-dirs, or ask interactively) |
| `--project-name <name>`                   | Project name for non-interactive installs (prompted otherwise)                         |
| `--usage-transcript-retention full\|omit` | Whether usage capture stores full transcript text or only token totals                 |
| `--add [cli ...]`                         | Add CLI wiring to an existing install (interactive menu if no CLIs given)              |
| `--remove [cli ...]`                      | Remove CLI wiring from an existing install (interactive menu if no CLIs given)         |

**`update-factory`**:

| Flag             | Effect                                                                                                          |
| ---------------- | --------------------------------------------------------------------------------------------------------------- |
| `--target <dir>` | Project directory (default: cwd)                                                                                |
| `--source <dir>` | Agent Factory checkout (default: `factory_source` from install manifest)                                        |
| `--check`        | Report user modifications and exit without updating                                                             |
| `--force`        | Update despite user modifications; preserve changed files in `.agent-factory/factory-user-changes/<timestamp>/` |

### What init-factory creates

| What                 | Where                                                                                                                                                        | Tracked? |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------- |
| Toolset copy         | `factory/`                                                                                                                                                   | No       |
| CLI symlinks         | `.claude/`, `.github/`, `.pi/`, `.codex/`, `.agents/` — pointing into `factory/`                                                                             | No       |
| Git safety guardrail | `.claude/hooks/block-dangerous-git.sh`, `.github/hooks/`, `.pi/extensions/`, `.codex/hooks/`                                                                 | No       |
| Step guard hooks     | `.claude/hooks/step-guard.sh`, `.github/hooks/step-guard.*`, `.pi/extensions/step-guard.ts`, `.codex/hooks/step-guard.sh`                                    | No       |
| Freshness check      | `.claude/hooks/check-factory-freshness.sh`, `.github/hooks/`, `.pi/extensions/`, `.codex/hooks/` — auto-runs `update-factory` when `factory/` is stale       | No       |
| Usage capture hooks  | `.claude/hooks/capture-usage.sh` (Stop/SubagentStop), `.github/hooks/capture-*.sh`, `.pi/extensions/capture-usage.ts`, `.codex/hooks/capture-codex-usage.sh` | No       |
| Orientation file     | `.claude/CLAUDE.md`, `.github/copilot-instructions.md`, `AGENTS.md` — prepends a marker block if the file exists                                             | No       |
| Generated agents     | `.github/agents/*.md` (Copilot, with tools: frontmatter), `.codex/agents/*.toml` (Codex, native format)                                                      | No       |
| Hook config          | `.claude/settings.json` (hook entries), `.codex/hooks.json` (hook entries)                                                                                   | No       |
| Pre-commit hooks     | `.pre-commit-config.yaml` — `agent_factory_hook-*` block                                                                                                     | Yes      |
| Gitignore block      | `.gitignore` — `agent_factory related` section                                                                                                               | Yes      |
| Project config       | `config/project.json` (name + UUID), `config/model.conf`, `config/project-context.json` (scan results)                                                       | No       |
| Test regime          | `docs/agent-context/testing.yaml` — `test_command` if a single unambiguous entrypoint is detected                                                            | No       |
| Usage runtime        | `.agent-factory/usage-runtime/` — hash-verified tokenizer venv                                                                                               | No       |
| Usage lifecycle      | `.agent-factory/usage-control/` — registration fence and capture state                                                                                       | No       |
| Install manifest     | `.agent-factory/factory-install.json`                                                                                                                        | No       |
| Install checksums    | `.agent-factory/factory-checksums.json` — per-file SHA-256 for modification detection by `update-factory`                                                    | No       |

Re-running is safe. If `factory/` exists, it is left alone — use `factory/scripts/update-factory` instead.

### Test execution

Tests run through gates, not agents:

1. **Pre-commit** — changed files only (`--no-verify` to bypass)
2. **Pre-push** — full suite (`git push --no-verify` to bypass)
3. **Phase advance** — FSM entry conditions check `tests_pass`

Projects declare test commands in `docs/agent-context/testing.yaml`:

- `test_command` — full suite (gates, pre-push)
- `test_staged_command` — staged files (agent TDD loop)
- `test_changed_command` — changed files (pre-commit)

See [ADR-0003](../../docs/adr/0003-test-execution-via-hooks.md).

### Automated playbook execution

The orchestrator (work in progress) drives agent sessions and gates after the human-driven requirements phase:

```bash
factory/scripts/run-playbook \
  --playbook greenfield-development \
  --from-state PHASE_2_ARCHITECTURE \
  --cli claude
```

Stops at human gates. Re-run without `--from-state` to resume. See the [orchestrator README](../orchestrator/README.md).
