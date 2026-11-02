---
name: dependency-check
description: Enforce dependency-rules.dsl dependency rules by scanning source imports and writing a JSON gate report.
category: implementation
---

# Dependency Check

Run a deterministic architectural integrity gate that compares forbidden
dependencies declared in `docs/spec/dependency-rules.dsl` against source
imports.

## What it enforces

- Rules written as `<module> must_not_depend_on <module>` in
  `dependency-rules.dsl`
- Default threshold: **0 violations**
- One JSON result per rule outcome, including the violating file, line,
  and imported module when a violation exists
- Logged output at `.current-work/dependency-check/<story-id>.json`
- Non-zero exit on any violation

## Current parser scope

The initial release parses the dependency-rule DSL directly and inspects
Python imports via the standard-library `ast` module. The gate stays
wrapper-friendly for future language-specific engines such as `deptrack`,
`dependency-cruiser`, or `arch-pkg`, but this story implements the
deterministic Python baseline needed by the Factory fixture and gate loop.

## Rule format

Add dependency rules to `docs/spec/dependency-rules.dsl`, one plain
statement per line:

```text
module_a must_not_depend_on module_b
engine must_not_depend_on scripts
```

The left-hand side is the importing module boundary. The right-hand side
is the forbidden dependency target. The script treats the first path
segment of a Python module import as the boundary name.

The rules live in their own file because rule lines are not valid
Structurizr DSL. Keep them out of `architecture.dsl`.

## Usage

Run from the repository root:

```bash
.agent-factory/factory/scripts/dependency-check
```

Optional arguments:

```bash
.agent-factory/factory/scripts/dependency-check   --story-id ST-0103   --dsl-path factory/fixtures/quality-gates/dependency-violation/architecture.dsl   --source-root factory/fixtures/quality-gates/dependency-violation
```

- `--dsl-path` defaults to `docs/spec/dependency-rules.dsl`
- `--source-root` defaults to the current directory
- `--story-id` defaults to `STORY_ID`, then the current git branch, then
  `adhoc`

## Report contract

The script writes a JSON array with this shape:

```json
[
  {
    "rule_name": "module_a must_not_depend_on module_b",
    "pass_fail": "fail",
    "violating_import": {
      "file": "module_a/main.py",
      "line": 3,
      "imported_module": "module_b"
    }
  },
  {
    "rule_name": "conforming must_not_depend_on forbidden",
    "pass_fail": "pass",
    "violating_import": null
  }
]
```

When a rule has multiple violations, the report contains one failing entry
per violating import. A passing rule produces a single `pass` entry with
`violating_import: null`.

A file that cannot be read or parsed fails every rule that governs its
module, because its imports cannot be checked. Its entry names the parse
error, and `imported_module` is `null`:

```json
{
  "rule_name": "module_a must_not_depend_on module_b",
  "pass_fail": "fail",
  "violating_import": {
    "file": "module_a/broken.py",
    "line": 2,
    "imported_module": null,
    "parse_error": "invalid syntax (module_a/broken.py, line 2)"
  }
}
```
