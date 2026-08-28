---
name: mutation-analysis
description: Run mutmut against production code, scope mutations to a story diff when requested, and block unresolved surviving mutants.
category: quality
disable-model-invocation: true
---

# Mutation Analysis

Run deterministic mutation testing so line-hit coverage is not mistaken for
behavioral coverage. The gate blocks until every surviving mutant is resolved.

## What the gate enforces

- **Killed mutant** — a test or another deterministic check detected the
  behavioral change. No follow-up action is required.
- **Surviving mutant** — behavior changed and nothing detected it. The mutant
  must be resolved before merge.
- **Zero unresolved survivors** — the merge gate passes only when no surviving
  mutant remains unresolved.

## Diff-scoping contract

Use `factory/scripts/mutation-analysis --diff-base <ref>` when the gate should
inspect only the production files changed by the story.

The script runs:

```bash
git diff --name-only --diff-filter=ACMR <ref> HEAD
```

It then excludes test files matching any of:

- `test_*.py`
- `*_test.py`
- `*_test.go`
- `*.test.ts`
- `*.test.js`
- `*.spec.ts`
- `*.spec.js`
- any path under `tests/`
- any path under `__tests__/`

The remaining changed files are treated as production files. For the Python
reference implementation, only the Python subset of those production files is
sent to `mutmut`.

When `--diff-base` is omitted, the script falls back to the full module: use
explicit source paths, or let the selected project directory's `src/` tree act
as the mutation scope.

## Survivor classification

For each mutant the script writes a JSON entry with these required fields:

- `operator` — the detected source change, for example `+ -> -`
- `location` — `path:line` for the mutated source line
- `status` — `killed` or `survived`
- `resolution_action` — `none-required`, `unresolved`,
  `remove-dead-code`, `add-missing-test`, or `file-qa-finding`

The report also carries `mutant` and `raw_status` for operator review and for
feeding a later fix iteration.

## Resolution actions for survivors

Every surviving mutant must be classified into one of three outcomes:

1. **`remove-dead-code`** — the mutant proves the code has no behavioral owner;
   remove the dead code rather than preserving it.
2. **`add-missing-test`** — the code is real behavior and a contract test is
   missing; add the test that kills the mutant.
3. **`file-qa-finding`** — the developer cannot resolve it inside the coding
   loop; file a QA finding and attach that resolution to the gate run.

Any survivor without one of those actions is emitted as `unresolved` and blocks
merge.

## Resolution input

Pass `--resolutions <path>` to supply a JSON object that maps either a mutant
identifier or a `path:line` location to one of the three survivor actions above.
Example:

```json
{
  "calc.x_adjust_balance__mutmut_1": "add-missing-test",
  "src/calc.py:2": "file-qa-finding"
}
```

Mutant identifiers take precedence over location keys when both are present.

## Report and log location

The script writes the JSON report to:

```text
.current-work/mutation-analysis/<story-id>.json
```

`<story-id>` is inferred from the current Git branch name (`story/ST-0102` →
`ST-0102`) unless `--story-id` overrides it.

## Typical invocations

Run the full module in a self-contained fixture:

```bash
factory/scripts/mutation-analysis \
  --project-dir factory/fixtures/quality-gates/surviving-mutant \
  src/calc.py
```

Run only Python production files changed since the story branch diverged:

```bash
factory/scripts/mutation-analysis --diff-base <merge-base>
```

Resolve a known survivor via a QA finding record:

```bash
factory/scripts/mutation-analysis \
  --project-dir factory/fixtures/quality-gates/surviving-mutant \
  --resolutions /tmp/mutation-resolutions.json \
  src/calc.py
```
