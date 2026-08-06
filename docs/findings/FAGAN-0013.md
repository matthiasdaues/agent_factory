---
id: FAGAN-0013
source: fagan-review
severity: minor
category: suggestion
artifact: orchestrator/tests/test_update_factory.py:46
status: resolved
traces: [ADR-0010]
---

# Real `_run_init` subprocess delegation seam is never exercised

**What is wrong:** Every test relies on the autouse `_isolate_install` fixture
that monkeypatches `update_factory._run_init` with a fast mirror-copy. The
real `_run_init` — which builds the argv
`[sys.executable, str(source/"factory"/"scripts"/"init-factory"), "--source", ..., "--target", ...]`, runs it via `subprocess.run(..., check=False)`, and
propagates `result.returncode` — is therefore never executed by the suite.
`test_delegates_reinstall_to_sourced_init_factory` only checks the patched
seam receives `(src.resolve(), target.resolve())`; it does not verify the
subprocess argv shape or return-code propagation. A regression in argv
construction (wrong script path, dropped flag) would not be caught.

**Fix:** Add one test that leaves the real `_run_init` in place (patching only
init-factory's networked steps) to assert a true end-to-end update round trip,
or assert the exact argv the subprocess receives by intercepting
`subprocess.run` and checking the command list and return-code mapping.

## Resolution

Verified on `798d95b`. `test_real_run_init_builds_correct_argv_and_propagates_returncode`
restores `REAL_RUN_INIT`, intercepts `update_factory.subprocess.run`, and
asserts the argv is exactly
`[sys.executable, str(src/factory/scripts/init-factory), "--source", str(src), "--target", str(target)]`, that `check=False`, and that a `returncode` of 7
propagates straight through `_run_init`. A regression in argv construction or
return-code handling would now fail the suite.
