---
id: SPEC-002
title: UC-07 business rules do not acknowledge test command blocking added by BR-024
status: resolved
severity: Minor
category: Consistency
date: 2026-07-12
found_by: spec-review-agent
resolved_by: requirements-agent
resolution_date: 2026-07-12
tags: [SPEC, UC-07, UC-09, BR-024]
---

# SPEC-002: UC-07 business rules do not acknowledge test command blocking added by BR-024

## Summary

UC-09 introduces BR-024, which extends `block-dangerous-git.sh` (the subject of UC-07) to block test commands. However, UC-07's business rules section does not acknowledge this extension of scope, creating an incomplete picture of the hook's pattern list.

## Location

- **Use Case**: docs/spec/use_cases/UC-07-block-a-dangerous-git-command.md
- **Business Rule**: docs/spec/supplementary_specs/validation-rules.md § BR-024
- **Extending Use Case**: docs/spec/use_cases/UC-09-run-tests-via-hook.md

## Evidence

**UC-07 Business Rules** describes the pattern list as two groups:

> The pattern list covers two groups: commands that discard or overwrite work or history (`git push`, `git reset --hard`, `git clean -f`/`-fd`, `git branch -D`, `git checkout .`, `git restore .`, bare `push --force`/`reset --hard` fragments), and commands that bypass this repo's own commit gates (`--no-verify`, `git commit -n`, reassigning `core.hooksPath`, `pre-commit uninstall`, `SKIP=...` on `git commit`/`pre-commit`).

**But BR-024** (introduced by UC-09) adds a third group:

> **BR-024**: Test commands are blocked for agent execution via `block-dangerous-git.sh` deny patterns: `pytest`, `npm test`, `go test`, `cargo test`, and common variants (`python -m pytest`, `uv run pytest`, `yarn test`). Agents receive exit `2` denial at `PreToolUse` with message directing them to hook-triggered execution instead.

**And BR-020** (in UC-07) states:

> **BR-020**: the hook's deny list is a second, independent layer on top of `trigger`'s own `--disallowedTools`/`--deny-tool` (see [UC-04 § Business Rules](UC-04-dispatch-an-agent-via-trigger.md#business-rules)) — belt-and-suspenders, not a single point of failure; a background session denied by one layer is denied before the verb is even offered as available, not merely rejected after asking.

BR-020 references UC-04 but does not cross-reference UC-09's extension of the deny list.

## Impact

**Specification incompleteness**: Readers of UC-07 cannot discover from that use case alone that test commands are also blocked. The pattern list description is incomplete. UC-09's Extension 1a is effectively adding new behavior to UC-07's mechanism, but UC-07 itself is not updated to reflect this.

A reader trying to understand what `block-dangerous-git.sh` blocks would read UC-07 and see two groups (history-discarding and gate-bypassing), but would miss the third group (test commands) unless they also read UC-09.

## Recommended Fix

Add a cross-reference to UC-07's business rules section acknowledging the extension by UC-09:

```markdown
## Business Rules

- **BR-019**: `block-dangerous-git.sh` denies a command if it matches any pattern in its fixed list, regardless of which CLI's JSON shape supplied it; both supported CLIs treat exit code `2` as deny.
- **BR-020**: the hook's deny list is a second, independent layer on top of `trigger`'s own `--disallowedTools`/`--deny-tool` (see [UC-04 § Business Rules](UC-04-dispatch-an-agent-via-trigger.md#business-rules)) — belt-and-suspenders, not a single point of failure; a background session denied by one layer is denied before the verb is even offered as available, not merely rejected after asking.
- The pattern list covers **three groups**:
  1. Commands that discard or overwrite work or history (`git push`, `git reset --hard`, `git clean -f`/`-fd`, `git branch -D`, `git checkout .`, `git restore .`, bare `push --force`/`reset --hard` fragments)
  2. Commands that bypass this repo's own commit gates (`--no-verify`, `git commit -n`, reassigning `core.hooksPath`, `pre-commit uninstall`, `SKIP=...` on `git commit`/`pre-commit`)
  3. Test commands that must run via hooks only (see UC-09, BR-024): `pytest`, `npm test`, `go test`, `cargo test`, and their common variants
- This is a backstop, not a security boundary: it catches an accidental or under-pressure bypass, not a determined one — a user with shell access outside the CLI, or anyone who edits the CLI's own configuration, can always route around it.
```

This makes the extension explicit and provides a forward reference to UC-09 where the test-blocking rationale is explained.

## References

- docs/spec/use_cases/UC-07-block-a-dangerous-git-command.md
- docs/spec/use_cases/UC-09-run-tests-via-hook.md
- docs/spec/supplementary_specs/validation-rules.md § BR-020, BR-024

## Category Rationale

**Consistency**: UC-07 describes `block-dangerous-git.sh`'s pattern list incompletely — it does not acknowledge the third group of patterns added by BR-024 in UC-09.
