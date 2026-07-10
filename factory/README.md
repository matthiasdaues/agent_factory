# Factory

`factory/` is Agent Factory's canonical content — agents, skills, playbooks, rulebooks, and deterministic gate scripts — used as a pluggable, agent-driven tool in a project folder. It is copied wholesale into a project by `init-factory` and never hand-edited there; the copy in your project and the source here stay in sync by re-running `init-factory`, not by editing the copy.

See the [root README](../README.md) for what Agent Factory is and its prerequisites. This file covers installing and using `factory/` itself.

## Deterministic Gates

In manual mode, the review agents invoke these linters directly, as their first step.

| Gate                           | Fires at                        | What it checks                                                                                                                      |
| ------------------------------ | ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `factory/scripts/spec-lint`    | Phase 1 → 2 boundary            | Use-case coverage, traceability links between PRD → actor-goals → use cases → supplementary specs, ID uniqueness, required sections |
| `factory/scripts/arch-lint`    | Phase 2 → 3 boundary            | arc42 chapters exist and cross-reference the Structurizr DSL, ADR index consistency, diagram file references                        |
| `factory/scripts/backlog-lint` | Phase 3 → 4 boundary            | YAML frontmatter schema, dependency graph acyclicity, priority and status values                                                    |
| `factory/scripts/matrix-lint`  | `config/model-matrix.conf` edit | `config/model-matrix.conf` syntax, required fields, valid tier/model mappings                                                       |

These scripts live in `factory/scripts/`. They are stdlib-only Python and run standalone:

```bash
factory/scripts/spec-lint docs/spec/
factory/scripts/arch-lint --docs-dir docs/
factory/scripts/backlog-lint backlog/
factory/scripts/matrix-lint config/model-matrix.conf
```

## Quick Start

This sets up a brand-new project from scratch.

```bash
# 1. Clone Agent Factory somewhere on disk. You only do this once per machine.
git clone <agent-factory-repo-url> agent_factory

# 2. Create your project directory (or use one you already made).
mkdir my-project && cd my-project

# 3. Run the init script against it.
../agent_factory/factory/scripts/init-factory
```

`init-factory` does the rest of the work: it runs `git init` if needed, copies `factory/` into your project, symlinks its content into `.claude/` and `.github/`, copies `config/model-matrix.conf` in as an editable starter, wires up `.pre-commit-config.yaml`, and runs `pre-commit install`. It is a plain, standalone Python script. **It needs no AI to run it** — a shell is enough.

Check it worked:

```bash
git status                        # .pre-commit-config.yaml and config/ are now untracked, ready to commit
git add -A && git commit -m "init: wire up Agent Factory"
```

The first commit may modify a few files (`mdformat`/`ruff` auto-fixing formatting). If it does, re-stage and commit again — see [Troubleshooting](#troubleshooting).

Open your AI coding CLI in `my-project` and greet it. It should read `.claude/CLAUDE.md` (or `.github/copilot-instructions.md`) and confirm it understands the local-first rule.

### Next steps — run the workflow

Once the CLI greets you, pick the runbook in `factory/playbooks/` that matches your situation (`greenfield-development.md` for a new project, `brownfield-onboarding.md` for an existing one, `feature-addition.md`, `bug-fix.md`, and so on). Each playbook walks the phase chain — requirements → spec-review → architecture → architecture-review → planning → implementation → reconciliation → qa — step by step, for manual, one-agent-per-session use. An automated CLI wrapper for this same chain exists too, still a work in progress — see [orchestrator/README.md](../orchestrator/README.md).

## Use in an Already Existing Repo

`init-factory` works the same way against a repo that already has its own history, its own `.gitignore`, and its own `.pre-commit-config.yaml`. Run it from inside that repo:

```bash
cd /path/to/existing-project
/path/to/agent_factory/factory/scripts/init-factory
```

What it does differently here, compared to a fresh project:

- **`.gitignore`** — appends only the lines Agent Factory needs (`.claude`, `.github`, and so on). It never rewrites or duplicates what is already there.
- **`.pre-commit-config.yaml`** — if the file does not exist, it is symlinked in, exactly as in a fresh project. If it already exists as a real file, `init-factory` hands off to `factory/scripts/merge-precommit-config`, which splices Agent Factory's hooks into your existing `repos:` list. Your existing hooks are left untouched.
- **Everything else** — `docs/`, your own scripts, your own configuration — is left alone. `init-factory` never touches a file or directory it did not create.

The script is idempotent. Run it again at any time; anything already correctly in place is skipped, not redone. If it finds something it cannot safely work around — a real file already sitting where a symlink needs to go, or a `.pre-commit-config.yaml` shape it does not recognize — it stops immediately and names the exact path. It never partially applies a run.

To trigger the same script conversationally instead of from a shell, use the `init-factory` skill (`factory/skills/init-factory/SKILL.md`). It confirms the target with you, runs the script, and relays its output. On the very first run in a project, there is no installed skill yet to call by name — point the CLI at the file directly: "read `factory/skills/init-factory/SKILL.md` in the agent_factory checkout and follow it."

## Troubleshooting

**`init-factory: STOPPED — <path> already exists and is not a symlink to <dest>`**
Something real is already at that path — not one of Agent Factory's own symlinks. Move, rename, or remove it, then re-run `init-factory`. The script never overwrites a file it does not recognize as its own.

**`merge-precommit-config` reports it cannot merge your `.pre-commit-config.yaml`**
This happens when the file has no top-level `repos:` list in block style, or when its existing hooks are indented differently than 2 spaces. Merge Agent Factory's hooks in by hand: copy the `- repo: local` block from `factory/config/pre-commit-config.yaml` into your own file's `repos:` list.

**`uvx: command not found`**
Install `uv` — see the [root README's Prerequisites](../README.md#prerequisites). Every gate, and `pre-commit` itself, runs through `uvx`.

**`docker info` fails, or Structurizr export fails**
Start Docker Desktop (macOS) or the Docker daemon (Linux). This only blocks diagram export (`factory/scripts/structurizr`) — nothing else in Agent Factory needs Docker.

**Your first commit fails, or modifies files you did not touch**
Expected. The `mdformat` and `ruff` hooks auto-fix formatting on commit. Re-stage the files they changed and commit again:

```bash
git add -u
git commit -m "<same message>"
```

**`factory/` looks out of date after you update the agent_factory checkout**
`init-factory` only copies `factory/` in once — if it already exists in your project, it is left alone. There is no update script yet. For now, delete your project's `factory/` directory and re-run `init-factory` to refresh it.

**Symlinks do not work on Windows**
Agent Factory targets macOS and Linux only. Both rely on native, git-tracked symlinks (`git` stores a symlink as a blob of mode `120000`), which Windows does not support the same way.
