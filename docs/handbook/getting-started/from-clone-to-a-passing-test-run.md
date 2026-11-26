---
title: From clone to a passing test run
type: tutorial
status: implemented
order: 10
description: Clone the repository, install the factory on itself, change a script, refresh the installed copy, and run the tests.
---

# From clone to a passing test run

You will clone the repository, install the factory into your clone, change one script, and run the tests for it. Each step ends with a checkpoint. Do not go on before the checkpoint holds.

You need `git`, Python 3.10 or newer, and [uv](https://docs.astral.sh/uv/).

## 1. Clone the repository

Copy the clone URL from the repository page and store it in a shell variable. Then clone:

```bash
REPO_URL='paste the clone URL here'
git clone "$REPO_URL" agent_factory
cd agent_factory
```

Checkpoint: `ls` shows `init-factory`, `packages/`, and `docs/`.

## 2. Install the factory on itself

```bash
./init-factory .
```

The script asks for a project name. Type any name, for example `agent_factory`.

The repository uses its own tools this way. The script copies `packages/factory/` into `.agent-factory/factory/`, a folder that git ignores. Your AI CLI reads the factory tools from that copy.

The repository already tracks a `.pre-commit-config.yaml`, so the script leaves it alone and installs no Git hooks. Install them once with `uvx pre-commit install --hook-type pre-commit --hook-type pre-push`. The hooks then run `handbook-lint` from `packages/factory/scripts/` and the tests that a commit affects.

Checkpoint: the output ends with a line that starts with `undo:`, and `.agent-factory/factory/scripts/` exists.

## 3. Change a script under `packages/`

Factory source lives under `packages/factory/`, and `.agent-factory/factory/` is the installed copy that the next refresh overwrites. The concern [Factory source and packaging](../../agent-context.md#factory-source-and-packaging) records this split. So edit the source, not the copy.

For this tutorial, add one comment line to the script `handbook-lint`. Insert it directly above the line `from __future__ import annotations` in `packages/factory/scripts/handbook-lint`:

```python
# Tutorial change.
```

Checkpoint: `git diff --stat` lists `packages/factory/scripts/handbook-lint` with one added line.

## 4. Refresh the installed copy

The installed copy still holds the old script. Refresh it:

```bash
.agent-factory/factory/scripts/update-factory --target .
```

The script shows what it will change and asks for approval. Answer `yes`.

Checkpoint: the last line is `update-factory: done, .agent-factory/factory/ is now current`, and `grep "Tutorial change" .agent-factory/factory/scripts/handbook-lint` finds your line.

## 5. Run the tests for your change

```bash
python3 tests/select_tests.py --run packages/factory/scripts/handbook-lint
```

The selector picks the test files that name the script and runs them. The first run installs the test dependencies, so it takes longer.

Checkpoint: the output ends with a line such as `145 passed in 8.01s`, and the exit code is 0. The count differs as tests are added.

## 6. Keep or drop the change

To drop the tutorial change, restore the script and refresh the installed copy again:

```bash
git checkout HEAD -- packages/factory/scripts/handbook-lint
.agent-factory/factory/scripts/update-factory --target .
```

To keep a real change, write the commit message as [commit-conventions.md](../../../packages/factory/rulebooks/conventions/commit-conventions.md) sets out. Once you installed the hooks in step 2, they run the tests that the change affects.

Next, read the [contributing chapter](../contributing/index.md) before you write a handbook page.
