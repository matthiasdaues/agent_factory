---
name: validate
description: Run every applicable deterministic gate on demand, mid-session — the custom lint scripts plus ruff and mdformat — without needing a git commit.
category: utility
disable-model-invocation: false
---

# Validate

Run the same deterministic gates pre-commit runs, callable any time during a session — after a draft edit, before offering to commit, or when the user just asks "does this pass?". Each gate is conditional on the artifact it checks existing in the project; skip cleanly and say so rather than failing on an artifact that was never expected to exist yet.

## Gates

Run in this order — cheap and universal first, project-specific last:

| #   | Gate              | Condition to run                                    | Command                                                                              |
| --- | ----------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------ |
| 1   | Markdown format   | Always (every project has *some* Markdown)          | `factory/scripts/mdformat --number .`                                                |
| 2   | Ruff check        | `pyproject.toml` or any `*.py` exists               | `ruff check --fix .`                                                                 |
| 3   | Ruff format       | Same as above                                       | `ruff format .`                                                                      |
| 4   | link-check        | Always (checks project Markdown links)              | \`git ls-files -z '\*.md' ':!factory/\*\*'                                           |
| 5   | mermaid-lint      | Always                                              | `factory/scripts/mermaid-lint`                                                       |
| 6   | spec-lint         | `docs/spec/` exists                                 | `factory/scripts/spec-lint --spec-dir docs/spec --graph docs/spec/traceability.json` |
| 7   | arch-lint         | `docs/arc42/architecture.dsl` or `docs/adr/` exists | `factory/scripts/arch-lint --docs-dir docs/arc42 --no-validate`                      |
| 8   | backlog-lint      | `backlog/` exists                                   | `factory/scripts/backlog-lint --backlog-dir backlog`                                 |
| 9   | matrix-lint       | `config/model.conf` exists                          | `factory/scripts/matrix-lint --matrix config/model.conf`                             |
| 10  | statemachine-lint | `docs/spec/` exists                                 | `factory/scripts/statemachine-lint --spec-dir docs/spec`                             |
| 11  | index-lint        | `factory/agents/` or `factory/skills/` exists       | `factory/scripts/index-lint --check`                                                 |

**Ruff is Python-specific, not universal.** Gates 2-3 are the one pair genuinely conditional on implementation language — the factory itself (agents/skills/playbooks/rulebooks, gates 1 and 4-11) is language-agnostic; only a Python target project pulls in ruff. A non-Python project should see gates 2-3 reported as skipped, not failed. `link-check` is the fast offline counterpart to tools such as lychee: it validates local files and images while deliberately leaving remote URLs to an online crawler. `mermaid-lint` rejects raw semicolons in fenced Mermaid blocks while allowing entity escapes such as `#59;`.

**index-lint uses `--check` here, not the default write mode.** `validate` reports pass/fail, it doesn't rewrite project files as a side effect of checking — if `INDEX.yaml` is stale, report `FAIL` and let the user (or `commit`, which already runs `validate` first) decide to regenerate via a plain `factory/scripts/index-lint`.

**Path convention.** Every script above lives in `factory/scripts/`; `config/model.conf` is the one exception, copied out to the project root at init time rather than staying inside `factory/` — see the portable `factory/config/pre-commit-config.yaml` template. Run `validate` from the project root.

## Step 1 — Detect applicable gates

Check for each condition column above before running its gate. Report which gates will run and which are skipped, with the reason (e.g. "matrix-lint: skipped, no config/model.conf — this project has no model matrix").

## Step 2 — Run each applicable gate

Run gates in the table's order. Capture each gate's exit code and output. Do not stop at the first failure — run every applicable gate and collect all results, so one pass surfaces everything, not one defect at a time.

## Step 3 — Report

One line per gate: `PASS`, `FAIL` (with the first few lines of its output), or `SKIP` (with the reason). If anything failed, say so plainly and do not offer to commit. If everything passed or was cleanly skipped, say so plainly and it's safe to offer `commit` next.

**Completion**: every applicable gate has run exactly once and its result is reported; nothing was silently skipped without a stated reason.
