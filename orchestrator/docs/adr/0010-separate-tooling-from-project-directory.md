# 10. Separate Tooling from Project Directory

**Status**: Accepted

> **Amended 2026-07-12 (PhaseRunner collapse):** `orchestrate init` and the tooling-copy layout remain in the orchestrator; the `run-phase` execution the examples below invoke moved to `factory/`. See the repo-root `docs/spec/prd.md` and `docs/adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md`.

**Context**:

The current bootstrap clones Agent HQ into `.ai_tooling/` inside the project directory and gitignores it. This works but has a significant drawback: AI coding CLIs scan the working directory tree for context, so every agent session reads 19 skills, 8 agent definitions, the orchestrator source code, and its 190+ tests as part of "understanding the codebase." This is noise that wastes tokens and occasionally leads agents off-script — they explore the tooling instead of the project.

**Decision**:

Separate the tooling from the project. Agent HQ is cloned once to a user-chosen location. The project directory never contains the tooling source — only symlinks to the active ingredients.

### Installation

```bash
git clone https://github.com/matthiasdaues/agent_hq.git ~/agent_hq
cd ~/agent_hq/orchestrator && uv tool install .
```

This puts `orchestrate` on PATH. The CLI resolves `agents/`, `skills/`, and `scripts/` relative to its own package path (`__file__` → `../`). No environment variable, no config file. Updating the tooling:

```bash
cd ~/agent_hq && git pull
cd orchestrator && uv tool install .
```

### Project bootstrapping

```bash
orchestrate init my-project --cli copilot
cd my-project
orchestrate --interactive run-phase requirements
```

`orchestrate init [project-name]` does the following:

1. **Create the project directory** from the positional argument. If omitted, use cwd.
2. **`git init`** if no `.git/` exists.
3. **Create symlinks** in the project directory, gitignored:
   - `agents → <package-path>/../agents`
   - `skills → <package-path>/../skills`
   - `scripts → <package-path>/../scripts`
4. **Scaffold project directories**: `docs/spec/use_cases/`, `docs/spec/supplementary_specs/`, `docs/adr/`, `docs/reviews/`, `backlog/`.
5. **Copy `model-matrix.conf`** from the package as a per-project template.
6. **Create the CLI instruction file** based on `--cli` flag:
   - `--cli copilot` → `.github/copilot-instructions.md`
   - `--cli claude` → `CLAUDE.md`
   - `--cli gemini` → `GEMINI.md`
   - `--cli cursor` → `.cursor/rules/dev-workflow.md`
   - `--cli codex` → `AGENTS.md`
   - If `--cli` is omitted, present an interactive picker. Default to `AGENTS.md`.
   - If the file already exists, print what to add instead of overwriting.
7. **Update `.gitignore`** with `agents/`, `skills/`, `scripts/`, `.orchestrator/`.

### What `init` does NOT do

- **No `CONTEXT.md`** — created lazily by `grill-with-docs` when the first term is resolved. Avoids muddying the greenfield/brownfield decision.
- **No `prompts/` symlink** — agents never reference prompts. They are human reference material, accessed in the cloned repo or on GitHub.
- **No `.ai_tooling/` clone** — the tooling lives outside the project entirely.

### Behavioural properties

- **Idempotent** — running `init` again re-creates missing symlinks, adds missing dirs, skips what already exists. No `--force` flag needed.
- **macOS and Linux only** — symlinks on Windows require developer mode. Not supported.

**Consequences**:

- Agents no longer scan the tooling source during sessions — cleaner context, fewer wasted tokens.
- Instruction file paths simplify: `agents/requirements-agent.md` (not `.ai_tooling/agents/...`).
- One global clone serves all projects. Per-project config lives in `model-matrix.conf`.
- `uv tool install` makes `orchestrate` a first-class CLI command — no `uv run --project` gymnastics.
- The existing `_resolve_agents_dir` logic in `cli.py` must change: package-relative first, then symlink in cwd, then fail.
- All README, USAGE.md, and instruction file examples must be updated to reflect the new paths.
