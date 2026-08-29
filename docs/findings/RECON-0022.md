---
id: RECON-0022
source: reconcile-spec
severity: major
category: defect
artifact: tests/orchestrator/test_init_factory_prepush_hook.py
status: resolved
traces: [UC-09, ST-0149]
---

# Two tests assert deleted run-tests-full hook is present

**What is wrong:** `tests/orchestrator/test_init_factory_prepush_hook.py` defines a `HOOK` constant (lines 30-37) containing the `agent_factory_hook-run-tests-full` entry and two tests (`test_UC_09_fresh_init_installs_pre_push_full_suite_gate` and `test_UC_09_merge_carries_pre_push_gate_and_remains_idempotent`) assert that string is present in the installed pre-commit config. ST-0149 removed this hook from `factory/config/pre-commit-config.yaml`. These tests now assert the opposite of the correct behavior.

**Fix:** Update both tests to assert the hook is absent, not present. The test file's docstring ("UC-09 contracts for installing the pre-push full-suite test gate") should also be updated to reflect the new UC-09 semantics (project-owned test gates via charter declaration). Consider renaming the test file and functions to reflect the changed contract. The third test (`test_UC_09_init_installs_pre_commit_and_pre_push_hook_types`) checks that `pre-commit install` is called with both `--hook-type pre-commit` and `--hook-type pre-push`; verify whether this is still the intended behavior given that Factory no longer owns test hooks.
