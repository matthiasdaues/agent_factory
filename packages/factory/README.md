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

### Remove

```bash
factory/scripts/remove-factory
```

Reads the install manifest and reverses everything. Your pre-commit hooks, orientation files, and workflows come back as they were.

## First playbook

Open your AI coding CLI in the project directory. It reads the orientation file and presents a menu.

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

### What init-factory creates

| What             | Where                                                                                                            | Tracked? |
| ---------------- | ---------------------------------------------------------------------------------------------------------------- | -------- |
| Toolset copy     | `factory/`                                                                                                       | No       |
| CLI symlinks     | `.claude/`, `.github/`, `.pi/` — pointing into `factory/`                                                        | No       |
| Git safety hooks | `.claude/hooks/`, `.github/hooks/`, `.pi/extensions/`                                                            | No       |
| Orientation file | `.claude/CLAUDE.md`, `.github/copilot-instructions.md`, `AGENTS.md` — prepends a marker block if the file exists | No       |
| Pre-commit hooks | `.pre-commit-config.yaml` — `agent_factory_hook-*` block                                                         | Yes      |
| Gitignore block  | `.gitignore` — `agent_factory related` section                                                                   | Yes      |
| Project config   | `config/project.json` (name + UUID), `config/model.conf`                                                         | No       |
| Install manifest | `.agent-factory/factory-install.json`                                                                            | No       |

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
