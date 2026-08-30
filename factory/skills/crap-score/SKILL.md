---
name: crap-score
description: Compute CRAP (Change Risk Anti-Patterns) per function and block when any exceeds the threshold.
category: implementation
disable-model-invocation: false
---

# CRAP Score

Run a deterministic CRAP metric gate that combines cyclomatic complexity
with test coverage into a single risk score per function.

## What it enforces

- Formula: `CRAP(m) = comp(m)^2 * (1 - cov(m)/100)^3 + comp(m)`
- Default threshold: **30** per function (industry standard)
- Threshold overrides from `docs/charter/house-rules.md` when present
  (key: `crap-threshold: <number>`)
- One JSON result per function: name, file, complexity, coverage,
  CRAP score, pass/fail
- Logged output at `.current-work/crap-score/<story-id>.json`
- Non-zero exit on any function exceeding the threshold

## Dependencies

The script depends on `radon` for cyclomatic complexity analysis and
reads pre-computed `coverage.json` (coverage.py JSON format) for
per-line test coverage data. Both are resolved automatically via the
`uv run --script` shebang.

## Usage

Run from the repository root:

```bash
factory/scripts/crap-score
```

Optional arguments:

```bash
factory/scripts/crap-score \
  --story-id ST-0101 \
  --source-root factory/fixtures/quality-gates/high-crap \
  --coverage-json factory/fixtures/quality-gates/high-crap/coverage.json
```

- `--source-root` defaults to the current directory
- `--coverage-json` path to a coverage.py JSON report; when omitted,
  all functions are scored with 0% coverage
- `--threshold` overrides the default and house-rules value
- `--story-id` defaults to `STORY_ID` env, then the current git branch,
  then `adhoc`

## Report contract

The script writes a JSON array with this shape:

```json
[
  {
    "file": "src/module.py",
    "function": "complex_untested",
    "complexity": 11,
    "coverage_pct": 0.0,
    "crap_score": 132.0,
    "pass_fail": "fail"
  },
  {
    "file": "src/module.py",
    "function": "simple_add",
    "complexity": 2,
    "coverage_pct": 100.0,
    "crap_score": 2.0,
    "pass_fail": "pass"
  }
]
```

## Fixture

`factory/fixtures/quality-gates/high-crap/` contains a self-contained
test project with:

- `src/module.py` — one function with complexity >= 10 and 0% coverage
  (expected FAIL), one function with complexity 2 and full coverage
  (expected PASS)
- `tests/test_module.py` — covers only the simple function
- `coverage.json` — pre-computed coverage data matching the test suite
