# Factory

The installable toolset: agents, skills, playbooks, and checks. `init-factory` copies it into your project. `update-factory` refreshes the copy later.

Part of [Agent Factory](../../README.md).

## Prerequisites

| Tool                 | Why                                                           | Install                                                                                  |
| -------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **Git ≥ 2.x**        | Version control                                               | macOS: `xcode-select --install`. Linux: `sudo apt install git` / `sudo dnf install git`. |
| **Python ≥ 3.10**    | Runs init and check scripts                                   | macOS: `brew install python@3.12`. Linux: `sudo apt install python3.12` or equivalent.   |
| **uv**               | Runs check tools and pre-commit hooks without global installs | `curl -LsSf https://astral.sh/uv/install.sh \| sh` ([docs](https://docs.astral.sh/uv/))  |
| **An AI coding CLI** | Runs agents and skills                                        | Claude Code, GitHub Copilot CLI, Pi, or Codex                                            |

Optional: **tiktoken** (`pip install tiktoken`) for token counting in INDEX.yaml; **Docker** for rendering architecture diagrams.

## Install

```bash
git clone <agent-factory-repo-url> agent_factory
cd agent_factory
./init-factory your-project
```

The wrapper accepts a target directory as its first argument. It delegates to `packages/factory/scripts/init-factory --target <dir>`, which you can also call directly with any of its flags (see [§ CLI flags](#cli-flags) below). Additional arguments after the target are forwarded: `./init-factory your-project --cli claude --project-name "My App"`.

The script copies a `.agent-factory/factory/` directory into your project and asks which CLI you use. It touches two tracked files:

- **`.pre-commit-config.yaml`** — adds a `- repo: local` block at the top. All hook ids start with `agent_factory_hook-`. Your hooks are not touched.
- **`.gitignore`** — appends a marker-delimited block listing everything Agent Factory added. `.github/` entries are listed individually so your workflows stay tracked.

Everything else is git-ignored. Your code, config, and history are not modified.

```bash
git status   # .gitignore and .pre-commit-config.yaml are the only tracked changes
git add -A && git commit -m "init: wire up Agent Factory"
```

If the first commit reformats files, that is the pre-commit hooks auto-fixing — re-stage and commit again.

Works the same against an existing repo with its own pre-commit config. Details in [Install into an existing repository](docs/handbook/installation-and-updates/existing-repository.md).

### Update

```bash
.agent-factory/factory/scripts/update-factory
```

Refreshes the installed `.agent-factory/factory/` to match the current checkout. Before replacing, it compares per-file checksums to detect local changes you made. If changes are found, the update stops (exit 2) unless you pass `--force`, which preserves changed files in `.agent-factory/user-changes/<timestamp>/`. Use `--check` to see the report without touching anything. On failure, the previous `.agent-factory/factory/` is restored automatically.

### Add or remove CLIs

```bash
.agent-factory/factory/scripts/init-factory --add copilot      # wire a new CLI
.agent-factory/factory/scripts/init-factory --add               # interactive menu
.agent-factory/factory/scripts/init-factory --remove pi         # unwire a CLI
.agent-factory/factory/scripts/init-factory --remove            # interactive menu
```

Incrementally adds or removes CLI wiring — dot-directories, symlinks, guardrails, step guards, usage capture, freshness hooks, and generated agents — without re-running the full installer. Updates the `.gitignore` block and install manifest.

### Remove

```bash
.agent-factory/factory/scripts/remove-factory
```

Reads the install manifest and reverses everything. Your pre-commit hooks, orientation files, and workflows come back as they were.

## Everything else

The [user handbook](docs/handbook/index.md) covers every other topic. It lives at `.agent-factory/factory/docs/handbook/` in an installed project.

- [Run your first session](docs/handbook/getting-started/first-session.md): meet VIRGIL and run a first `poc-spike`.
- [Choose a playbook](docs/handbook/playbooks/choose-a-playbook.md): pick the playbook for a new project, an existing codebase, a bug, a feature, or research.
- [Local configuration](docs/handbook/reference/local-configuration.md): the files `init-factory` creates and the ones you edit.
- [Model matrix](docs/handbook/reference/model-matrix.md): how `.agent-factory/config/model.conf` maps tiers to models.
- [What the agent context does](docs/handbook/agent-context/what-agent-context-does.md): the routing file `docs/agent-context.md`.
- [Directory layout](docs/handbook/reference/directory-layout.md): what each directory of `.agent-factory/factory/` holds.
- [Dispatch runs](docs/handbook/branches-and-dispatch/dispatch-runs.md) and [session log](docs/handbook/usage-capture/session-log.md): the working state in `.current-work/`.
- [Gates](docs/handbook/quality-and-review/gates.md) and [pre-commit hooks](docs/handbook/quality-and-review/pre-commit-hooks.md): how tests run through hooks and gates.
- [Install into an existing repository](docs/handbook/installation-and-updates/existing-repository.md): the same install against a repository with its own pre-commit config.

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

| Flag             | Effect                                                                                                  |
| ---------------- | ------------------------------------------------------------------------------------------------------- |
| `--target <dir>` | Project directory (default: cwd)                                                                        |
| `--source <dir>` | Agent Factory checkout (default: `factory_source` from install manifest)                                |
| `--check`        | Report user modifications and exit without updating                                                     |
| `--force`        | Update despite user modifications; preserve changed files in `.agent-factory/user-changes/<timestamp>/` |

### What init-factory creates

[Files that init-factory creates](docs/handbook/reference/local-configuration.md) lists every file and folder the setup writes, with the install manifest, the checksums, and the usage control paths.

### Test execution

[Gate scripts](docs/handbook/quality-and-review/gate-scripts.md#test-execution) describes when tests run and the test commands of `docs/testing.yaml`.
