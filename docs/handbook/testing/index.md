---
title: Testing
type: concept
status: implemented
order: 60
description: This chapter explains how the repository tests itself.
---

# Testing

From the repository root, pass a changed source path to the test selector. For example, to check a change to the handbook linter:

```bash
python3 tests/select_tests.py --run packages/factory/scripts/handbook-lint
```

Use [testing.yaml](../../testing.yaml) to find the current full-suite command and the commands for individual suites. Python tests live in `tests/`, `packages/factory/tests/`, and `packages/usage/tests/`. The TypeScript tests under `packages/factory/config/` cover integration code such as CLI extensions.

Choose a check that exercises the change. For a linter rule, run the linter on a representative input and its focused tests. For CLI wiring, test the installation and the action that triggers the hook. For an instruction change, try the affected procedure and inspect the result it asks the AI to produce.

<!-- handbook-index:start -->

## Reference

- [Usage check scripts](usage-check-scripts.md): The three gate scripts in packages/usage/scripts/, what each checks, and how to run them.

<!-- handbook-index:end -->
