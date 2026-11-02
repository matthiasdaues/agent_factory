---
name: validate
description: Run every applicable deterministic gate on demand, mid-session — the custom lint scripts plus ruff and mdformat — without needing a git commit.
category: utility
---

# Validate

Read [factory-voice.md](../../rulebooks/conventions/factory-voice.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates and clears the final pass.

Run the same deterministic gates pre-commit runs, callable any time during a session — after a draft edit, before offering to commit, or when the user just asks "does this pass?". Each gate is conditional on the artifact it checks existing in the project; skip cleanly and say so rather than failing on an artifact that was never expected to exist yet.

## Gates

Run in this order — cheap and universal first, project-specific last:

| #   | Gate              | Condition to run                                                            | Command                                                                                                 |
| --- | ----------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| 1   | Markdown format   | Always (every project has *some* Markdown)                                  | `.agent-factory/factory/scripts/mdformat --check --number .`                                            |
| 2   | Ruff check        | `pyproject.toml` or any `*.py` exists                                       | `ruff check .`                                                                                          |
| 3   | Ruff format       | Same as above                                                               | `ruff format --check .`                                                                                 |
| 4   | link-check        | Always (checks project Markdown links)                                      | `git ls-files -z '*.md' ':!.agent-factory/**' \| xargs -0 .agent-factory/factory/scripts/link-check`    |
| 5   | mermaid-lint      | Always                                                                      | `.agent-factory/factory/scripts/mermaid-lint`                                                           |
| 6   | spec-lint         | `docs/spec/` exists                                                         | `.agent-factory/factory/scripts/spec-lint --spec-dir docs/spec`                                         |
| 7   | arch-lint         | `docs/spec/architecture.dsl` or `docs/adr/` exists                          | `.agent-factory/factory/scripts/arch-lint --docs-dir docs/arc42 --no-validate --allow-missing-docs-dir` |
| 8   | backlog-lint      | `backlog/` exists                                                           | `.agent-factory/factory/scripts/backlog-lint --backlog-dir backlog`                                     |
| 9   | matrix-lint       | `.agent-factory/config/model.conf` exists                                   | `.agent-factory/factory/scripts/matrix-lint --matrix .agent-factory/config/model.conf`                  |
| 10  | statemachine-lint | `docs/spec/` exists                                                         | `.agent-factory/factory/scripts/statemachine-lint --spec-dir docs/spec`                                 |
| 11  | index-lint        | `.agent-factory/factory/agents/` or `.agent-factory/factory/skills/` exists | `.agent-factory/factory/scripts/index-lint --check`                                                     |
| 12  | concern-lint      | `docs/agent-context.md` exists                                              | `.agent-factory/factory/scripts/concern-lint`                                                           |
| 13  | voice-anchor-lint | `packages/factory/agents/` exists (the factory source repository)           | `packages/factory/scripts/voice-anchor-lint`                                                            |

**Ruff is Python-specific, not universal.** Gates 2-3 are the one pair genuinely conditional on implementation language — the factory itself (agents/skills/playbooks/rulebooks, gates 1 and 4-13) is language-agnostic; only a Python target project pulls in ruff. A non-Python project should see gates 2-3 reported as skipped, not failed. `link-check` is the fast offline counterpart to tools such as lychee: it validates local files and images while deliberately leaving remote URLs to an online crawler. `mermaid-lint` rejects raw semicolons in fenced Mermaid blocks while allowing entity escapes such as `#59;`. `concern-lint` validates the concern-oriented agent context structure (`docs/agent-context.md`). `voice-anchor-lint` checks that every agent and every prose-producing skill contains the fixed sentence that loads the factory voice. It runs only in the factory source repository, from the source copy.

**index-lint uses `--check` here, not the default write mode.** `validate` reports pass/fail, it doesn't rewrite project files as a side effect of checking — if `INDEX.yaml` is stale, report `FAIL` and let the user (or `commit`, which already runs `validate` first) decide to regenerate via a plain `.agent-factory/factory/scripts/index-lint`. Gates 1 to 3 follow the same rule: they run in check mode, and the user fixes drift with `mdformat --number`, `ruff check --fix`, or `ruff format`.

**Path convention.** Every script above except `voice-anchor-lint` lives in `.agent-factory/factory/scripts/`. `init-factory` installs the model matrix at `.agent-factory/config/model.conf`, beside the factory rather than inside `.agent-factory/factory/`. The portable `.agent-factory/factory/config/pre-commit-config.yaml` template uses the same path. Run `validate` from the project root.

## Step 1 — Detect applicable gates

Check for each condition column above before running its gate. Report which gates will run and which are skipped, with the reason (e.g. "matrix-lint: skipped, no .agent-factory/config/model.conf — this project has no model matrix").

## Step 2 — Run each applicable gate

Run gates in the table's order. Capture each gate's exit code and output. Do not stop at the first failure — run every applicable gate and collect all results, so one pass surfaces everything, not one defect at a time.

## Step 3 — Report

One line per gate: `PASS`, `FAIL` (with the first few lines of its output), or `SKIP` (with the reason). If anything failed, say so plainly and do not offer to commit. If everything passed or was cleanly skipped, say so plainly and it's safe to offer `commit` next.

**Completion**: every applicable gate has run exactly once and its result is reported; nothing was silently skipped without a stated reason.
