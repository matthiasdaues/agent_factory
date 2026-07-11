# Factory Guide

What's inside `factory/`, and how its pieces fit together. If you just want to get running, go to [factory/README.md](../README.md) instead — this page is background, read it once you're set up.

## Agents

An agent is one job — "write requirements," "review the architecture," "implement one story." Each agent is a single markdown file in `factory/agents/`, read by your AI CLI at the start of a session.

Most phases have two agents: an **author** and a **reviewer**. The author produces an artifact (a spec, an architecture doc, code). The reviewer checks it in a separate session, without seeing the author's reasoning — only the artifact itself. This catches mistakes a self-review would miss, the same way a second pair of eyes catches things you can't see in your own pull request.

The full list, grouped by phase, is in [`factory/INDEX.yaml`](../INDEX.yaml).

## Skills

A skill is a how-to — a reusable procedure an agent (or you, directly) invokes to do one well-defined thing: run a structured interview, write an ADR, run a security review. Each skill is a folder in `factory/skills/` holding a `SKILL.md`. Agents call skills; skills don't call agents.

The full list is also in [`factory/INDEX.yaml`](../INDEX.yaml).

## Playbooks

A playbook is a step-by-step recipe in `factory/playbooks/` for a specific situation — which agents to run, in what order, with what to check in between. Pick the one that matches what you're doing; don't run the full phase chain when a smaller playbook fits.

### Beginner playbooks

Start with these. Small blast radius, few steps, nothing to set up first:

| Playbook                                                          | For                                                                                                                                                                   |
| ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`poc-spike.md`](../playbooks/poc-spike.md)                       | "Does this basic idea even work?" No spec, no architecture, no checks — one file, thrown away by default. The fastest way to see an agent and your CLI work together. |
| [`bug-fix.md`](../playbooks/bug-fix.md)                           | Fixing one reported defect. Four steps: file the bug, fix it with tests, QA validates, mark resolved.                                                                 |
| [`documentation-update.md`](../playbooks/documentation-update.md) | Syncing docs with code after they've drifted. Two steps: reconcile, validate.                                                                                         |

### Full-chain playbooks

Once you're comfortable, these drive some or all of the five-phase chain (requirements → architecture → planning → implementation → quality — see [docs/concepts.md § The phase chain](../../docs/concepts.md#the-phase-chain)):

| Playbook                                                              | For                                                                                                                                                              |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`greenfield-development.md`](../playbooks/greenfield-development.md) | A brand-new project, start to finish.                                                                                                                            |
| [`brownfield-onboarding.md`](../playbooks/brownfield-onboarding.md)   | Bringing Agent Factory into an existing codebase that has no spec or architecture docs yet.                                                                      |
| [`feature-addition.md`](../playbooks/feature-addition.md)             | Adding a feature to a project Agent Factory already manages. Skips straight to planning for small features; runs the full chain for large ones.                  |
| [`refactoring.md`](../playbooks/refactoring.md)                       | Restructuring code without changing behaviour, with a measured baseline and a safety net.                                                                        |
| [`technical-poc.md`](../playbooks/technical-poc.md)                   | A real technical risk question, usually comparing 2+ candidate approaches, feeding an actual decision. Heavier than `poc-spike.md`, lighter than the full chain. |
| [`architecture-review.md`](../playbooks/architecture-review.md)       | Reviewing existing architecture documentation against quality attributes.                                                                                        |

## Playbook phase gates

Playbooks above are prose: nothing stops staging an architecture file before the spec gate clears except the human remembering the playbook's own instructions. An optional structured harness, layered on top, catches phase-boundary mistakes mechanically instead.

A playbook can ship a `.fsm.yml` alongside its `.md` in `factory/playbooks/` — a state machine describing each phase's `outputs:` file globs and the `entry_conditions` required to advance into it. Only [`greenfield-development.fsm.yml`](../playbooks/greenfield-development.fsm.yml) exists today. This is opt-in, not a default every playbook must adopt.

| Component                           | What it does                                                                                                         |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `.agent-factory/playbook-state.yml` | Local, git-ignored marker recording which state the project is currently in.                                         |
| `factory/scripts/transition-lint`   | Pre-commit gate. Blocks staging a file whose `outputs:` glob belongs to a state other than the marker's current one. |
| `factory/scripts/phase advance`     | Subcommand that checks the next state's `entry_conditions` and, if satisfied, advances the marker.                   |

`transition-lint` deliberately does not evaluate `entry_conditions` — by its own docstring, it "governs ordering *between* phases," not within one, and "does not evaluate a state's `entry_conditions`" because "that is `phase advance`'s job." It only checks whether a staged file belongs to the current state, naming the offending path and pointing at `phase advance` when a file belongs to a later one. This is a deliberate design choice, not a gap: condition-checking lives in one place only.

`phase advance` reads the next state's `entry_conditions`, evaluates each against a small `gate_conditions` library, and refuses — non-zero exit, marker unchanged — if any is unmet. Implemented condition types: `file_exists`, `files_exist`, `no_open_findings`, and `script_exit_zero` (stubbed to always pass in this proof of concept). On success it writes the marker with `recorded_at` taken from `phase advance`'s own process clock, never agent-supplied.

If the marker file is absent, both tools are no-ops — a project not using the harness sees no behavior change.

See [Structured Playbooks as a Deterministic Harness](proposals/playbook-structured-harness-strategy.md) for the full design rationale and the proof of concept's scope.

## Rulebooks

A rulebook is a cross-cutting convention that applies across agents and skills — commit message format, how to cross-reference other documents, ADR style, branch scoping. [`factory/rulebooks/rules.md`](../rulebooks/rules.md) states each rule in one line; the matching file in `factory/rulebooks/conventions/` carries the reasoning, examples, and edge cases. Agents and skills cite these rules rather than restating them.

## Linting and gating

A gate is a deterministic script — no LLM judgement involved — that catches a provable defect before a reviewer agent spends time on it: a broken cross-reference, a missing required section, an inconsistent ID. Cheap, reproducible, no false positives.

| Gate                           | Fires at                 | What it checks                                                                                                                      |
| ------------------------------ | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| `factory/scripts/spec-lint`    | Phase 1 → 2 boundary     | Use-case coverage, traceability links between PRD → actor-goals → use cases → supplementary specs, ID uniqueness, required sections |
| `factory/scripts/arch-lint`    | Phase 2 → 3 boundary     | arc42 chapters exist and cross-reference the Structurizr DSL, ADR index consistency, diagram file references                        |
| `factory/scripts/backlog-lint` | Phase 3 → 4 boundary     | YAML frontmatter schema, dependency graph acyclicity, priority and status values                                                    |
| `factory/scripts/matrix-lint`  | `config/model.conf` edit | Syntax, required fields, valid tier/model mappings                                                                                  |

In manual mode (driving each agent by hand, one session at a time), the reviewer agent for that phase runs its gate as its first step. Run any gate yourself the same way:

```bash
factory/scripts/spec-lint docs/spec/
factory/scripts/arch-lint --docs-dir docs/
factory/scripts/backlog-lint backlog/
factory/scripts/matrix-lint config/model.conf
```

These scripts are stdlib-only Python — no install needed to run them.

Separately, `pre-commit` runs `mdformat` and `ruff` on every commit, formatting markdown and Python automatically. Both run through `uvx`, so nothing needs installing locally beyond `uv` itself — the same zero-local-install pattern `factory/scripts/structurizr` uses for its Docker dependency.

## CLI safety guardrails

`init-factory` also installs a `PreToolUse` hook, `factory/config/hooks/block-dangerous-git.sh`, that blocks a fixed list of dangerous git invocations before they run — for both Claude Code and Copilot CLI. Two groups:

- **Commands that discard or overwrite work or history**: `git push`, `git reset --hard`, `git clean -f`/`-fd`, `git branch -D`, `git checkout .`, `git restore .`, and bare `push --force` / `reset --hard` fragments anywhere in a longer command line.
- **Commands that bypass this repo's own commit gates**: `--no-verify`, `git commit -n`, reassigning `core.hooksPath`, `pre-commit uninstall`, and `SKIP=...` environment overrides on `git commit` or `pre-commit`.

One script serves both CLIs: it reads the shell command from either CLI's `PreToolUse` JSON shape, and both CLIs treat the hook's exit code 2 as "deny."

The hook is installed automatically for every project — not opt-in, not a skill you invoke by hand. `init-factory` symlinks the script into both `.claude/hooks/` and `.github/hooks/`, and wires each CLI's own hook-config shape to it: `.claude/settings.json` as a `PreToolUse`/`Bash` hook for Claude Code, `.github/hooks/block-dangerous-git.json` (`matcher: "bash"`) for Copilot CLI. Since `.claude/` and `.github/` both stay gitignored, this is pure local machine state, re-created fresh by `init-factory` in every clone.

Treat it as a backstop, not a security boundary. It catches an accidental or under-pressure bypass — a background agent routing around a failing gate, for instance — not a determined one. A user with shell access outside the CLI, or anyone who edits the CLI's own configuration, can always route around it.

## Session logging

Session logging is an opt-in, append-only audit trail of gate-script runs. It exists to reconcile what an agent claims it did in a session against what actually happened on disk — not to replace or gate anything by default.

**Enable it.** Set the `AF_SESSION_LOG` environment variable to a log-file path before running gates. `factory/scripts/_session_log.py` reads it fresh on each run: unset, logging is a no-op and nothing is written; set, it appends one line per wrapped run to that path, creating the parent directory if needed.

**What gets recorded.** Each JSON Lines entry has: `ts` (UTC timestamp from the script's own process clock, not agent-supplied), `script` (the gate's name), `argv` (its invocation arguments), `exit_code`, and `files_changed` (a `git status --porcelain` diff taken before and after the run — the ground truth for what moved on disk). A `summary` field is added when the wrapped gate supplies one (`spec-lint` folds in its `--format json` error/warning/info counts).

**Current scope.** Only `spec-lint` is instrumented today. No other gate writes to the log yet.

**Reconcile.** `factory/scripts/session-reconcile` compares the log against real git state: `--log` points at the log file (default `.agent-factory/session-log.jsonl`), `--base`/`--head` bound the commit range to diff (omit `--base` to check the working tree alone). It reports three finding codes: `RECON-UNEXPLAINED` (error) — a working-tree change no logged run or commit accounts for; `RECON-DRIFT` (warning) — a run logged a change that is now neither committed nor present in the working tree; `RECON-STALE` (warning) — `docs/spec/` changed but `spec-lint` never ran this session. Exit code is the error-finding count, unless `--report-only`.

The log file lives under `.agent-factory/`, which is gitignored — local machine state, not portable, not meant to be reviewed.

See [factory/docs/proposals/session-log-addendum.md](proposals/session-log-addendum.md) for the full design rationale.

## Using this in an existing repo

`init-factory` works the same way against a repo that already has its own history, `.gitignore`, and `.pre-commit-config.yaml`. Run it from inside that repo:

```bash
cd /path/to/existing-project
/path/to/agent_factory/factory/scripts/init-factory
```

What it does differently here, compared to a fresh project:

- **`.gitignore`** — appends only the lines Agent Factory needs. It never rewrites or duplicates what's already there.
- **`.pre-commit-config.yaml`** — if the file doesn't exist, it's added exactly as in a fresh project. If it already exists, `init-factory` hands off to `factory/scripts/merge-precommit-config`, which splices Agent Factory's hooks into your existing `repos:` list, leaving your existing hooks untouched.
- **Everything else** — your `docs/`, your scripts, your configuration — is left alone. `init-factory` never touches a file or directory it didn't create.

The script is idempotent: run it again any time, and anything already correctly in place is skipped. If it finds something it can't safely work around, it stops immediately and names the exact path — it never partially applies a run.

To trigger the same script conversationally instead of from a shell, use the `init-factory` skill (`factory/skills/init-factory/SKILL.md`): it confirms the target with you, runs the script, and relays its output.

## Troubleshooting

**`init-factory: STOPPED — <path> already exists and is not a symlink to <dest>`**
Something real is already at that path. Move, rename, or remove it, then re-run `init-factory`.

**`merge-precommit-config` reports it cannot merge your `.pre-commit-config.yaml`**
This happens when the file has no top-level `repos:` list in block style, or its existing hooks aren't indented at 2 spaces. Merge Agent Factory's hooks in by hand: copy the `- repo: local` block from `factory/config/pre-commit-config.yaml` into your file's `repos:` list.

**`uvx: command not found`**
Install `uv` — see [factory/README.md § Prerequisites](../README.md#prerequisites). Every gate, and `pre-commit` itself, runs through `uvx`.

**`docker info` fails, or diagram export fails**
Start Docker Desktop (macOS) or the Docker daemon (Linux). This only blocks `factory/scripts/structurizr` — nothing else needs Docker.

**Your first commit fails, or modifies files you didn't touch**
Expected — the `mdformat` and `ruff` hooks auto-fix formatting on commit. Re-stage and commit again:

```bash
git add -u
git commit -m "<same message>"
```

**`factory/` looks out of date after you update your `agent_factory` checkout**
`init-factory` only copies `factory/` in once. There's no update script yet — delete your project's `factory/` directory and re-run `init-factory` to refresh it.

**Symlinks don't work on Windows**
Agent Factory targets macOS and Linux only. Both rely on native, git-tracked symlinks, which Windows doesn't support the same way.

## Referenced from

- [factory/README.md](../README.md)
