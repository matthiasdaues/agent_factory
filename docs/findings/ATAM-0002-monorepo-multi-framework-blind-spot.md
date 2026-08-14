---
id: ATAM-0002
title: Monorepo multi-framework blind spot - only first detected framework runs
status: resolved
severity: Major
category: Correctness
date: 2026-07-12
found_by: architecture-review-agent
resolved_by: architecture-agent
resolved_at: 2026-07-12T11:21:00Z
resolution_summary: Changed framework detection from first-match to fail-loud when multiple frameworks detected. `run-tests` now scans for ALL framework markers and exits 2 with error listing all found markers when multiple present. Prevents silent partial coverage. Long-term multi-framework orchestration deferred as T-06. Documented in ADR-0003 Amendment, BR-023.
tags: [ATAM, test-hooks, framework-detection, monorepo, resolved]
---

# ATAM-0002: Monorepo multi-framework blind spot - only first detected framework runs

## Summary

`run-tests` framework detection is "first match wins" (BR-023). In a monorepo with multiple test frameworks (e.g., Python backend with pytest + TypeScript frontend with jest), only the first detected framework runs. The other framework's tests are silently skipped. No error, no warning, just partial coverage presented as complete.

## Evaluated Quality Attributes

**Determinism** - State transitions are reproducible
**Fail-safe** - Invalid transitions are impossible

## Architecture Context

Per BR-023:

> Framework detection checks in order: `pyproject.toml` (pytest), `package.json` (jest/npm test), `go.mod` (go test), `Cargo.toml` (cargo test). First match wins; unrecognized frameworks report "no framework detected." Projects must use a supported framework or extend `run-tests`. Not every test setup auto-detects.

**Current behavior**:

1. `run-tests` scans repo root for framework markers
2. First marker found determines framework
3. Only that framework's tests run
4. Other frameworks' tests are not discovered, not run, not reported

## Sensitivity Point

Monorepo test coverage correctness depends on running ALL test frameworks present. First-match detection creates a silent failure mode.

## Scenario: Multi-Language Monorepo

Project structure:

```
repo/
├── pyproject.toml          # pytest for backend
├── backend/
│   └── tests/test_api.py
├── frontend/
│   ├── package.json        # jest for frontend
│   └── src/__tests__/ui.test.ts
```

**What happens**:

1. Pre-commit hook runs `run-tests --changed-only`
2. `run-tests` detects `pyproject.toml` → pytest
3. `uv run pytest --lf` runs (backend tests only)
4. Frontend jest tests never run
5. Hook reports `{"passed": N, "failed": 0}` — incomplete picture
6. Commit succeeds with untested frontend code

**Developer sees**: "Tests passed ✓"
**Reality**: Only backend tests ran

## Impact

**Silent partial coverage**:

- Developers believe all tests passed
- CI/hooks report success
- Broken frontend code reaches main branch
- Only discovered later (manual testing, production, or external CI)

**Violation of quality attributes**:

- **Determinism**: Test results are not reproducible across environments. Local hook runs pytest only; a CI config might run both frameworks.
- **Fail-safe**: Invalid transitions ARE possible - phase advance with half the test suite failing would succeed if only the other half was detected.

## Risk Classification

**Major** - This is a correctness risk. Incomplete test coverage presented as complete is a safety violation. Projects using multiple frameworks will have false confidence in test passage.

## Proposed Mitigation

**Option 1: Multi-framework detection and orchestration** (comprehensive fix)

Detect ALL present frameworks and run them in sequence:

1. Scan for all markers: `pyproject.toml` AND `package.json` AND `go.mod` AND `Cargo.toml`
2. Run each detected framework's tests
3. Aggregate results: `{"passed": N_total, "failed": M_total, ...}`
4. Exit 0 only if ALL frameworks exit 0

**Implementation**:

```python
frameworks = detect_all_frameworks()  # returns list, not first match
if not frameworks:
    exit(2, "No test framework detected")

results = []
for fw in frameworks:
    result = run_framework_tests(fw, mode)
    results.append(result)

emit_aggregate_json(results)
exit(max(r.exit_code for r in results))  # fail if any framework fails
```

**Trade-off**: More complex, but correct. Runtime increases (sum of all framework runs).

**Option 2: Explicit framework list in config** (explicit opt-in)

Add `.agent-factory/test-config.yml`:

```yaml
frameworks:
  - pytest
  - jest
```

`run-tests` reads this and runs all listed frameworks. Errors if config missing in monorepo context.

**Trade-off**: Requires manual config, but explicit > implicit for multi-framework case.

**Option 3: Fail loudly on multi-framework detection** (safety without full solution)

Detect multiple framework markers and refuse:

```
ERROR: Multiple test frameworks detected (pyproject.toml, package.json).
       run-tests does not support multi-framework projects yet.
       Please configure explicit framework or split tests.
```

**Trade-off**: Blocks monorepo workflows entirely, but prevents silent partial coverage. Forces users to address the gap explicitly.

## Recommended Action

**Short-term (immediate)**: Option 3 - Fail loudly on multi-framework detection. Better to block the workflow explicitly than to silently skip tests.

**Long-term**: Option 1 - Multi-framework orchestration. This is the correct behavior for monorepo support.

**Implementation steps**:

1. Add detection logic to find ALL framework markers
2. If `len(frameworks) > 1` and no explicit config: fail with clear error
3. Document monorepo limitation in ADR-0003 and BR-023
4. Plan Option 1 implementation as T-XX (new todo)

## References

- docs/spec/supplementary_specs/validation-rules.md § BR-023
- docs/adr/0003-test-execution-via-hooks.md (Context § Consequences)
- docs/arc42/05_building_block_view.md § 5.2.1 (run-tests component)

## Category Rationale

**Correctness**: Silent partial test coverage is a correctness defect. The system reports "tests passed" when only a subset ran. This violates the fail-safe quality attribute (invalid transitions should be impossible, but broken code can advance phases if only one framework's tests run).
