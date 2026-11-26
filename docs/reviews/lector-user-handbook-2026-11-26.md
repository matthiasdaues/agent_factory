---
type: lector-review
date: 2026-11-26
story: ST-0457
run: feature/handbooks
branch_head: 29bdf7c07af646c61abf2feea34d25d443dbc1cb
---

# Lector report, ST-0457 sentence pass

Scope: 55 pages. Words: 18,440 before, 18,438 after. 16 edits in 12 pages. Code spans and links are unchanged (script-checked). Nothing is staged or committed.

**Paragraph check:** one paragraph rewritten (`concepts/proposals.md` l.13).

**Most common fault: sentence over 25 words or two ideas (Gate 2).**

- Before: "The harness also caps the review loops: when one activity needs too many rounds of review and fix, the run stops and hands the decision to you."
- After: "The harness also caps the review loops. When one activity needs too many rounds of review and fix, the run stops and hands the decision to you."

Other fixes: announcing, flourish, one history word ("as before"), "also" for "including", one garbled clause.

**Left alone, unclear meaning:**

- `usage-capture/usage-capture.md` l.52 "Codex on its own needs no Node."
- `usage-capture/usage-capture.md` l.66 "An explicit cancellation by an uninstall is harmless."

**Possible contradictions:**

- `existing-repository.md` l.28 "never touches a file it did not create" against l.22-26, which change `.gitignore`, `.pre-commit-config.yaml`, and orientation files.
- `gate-scripts.md` l.55 "tests of the changed files" at pre-commit against l.69 `test_staged_command`.
- `configure-transcript-retention.md` l.11 "a copy of each transcript" against `usage-capture.md` l.17-22, where each chain is stored once.

**Binding rule in ordinary prose (BR-149), for the owners:**

- `gates.md` l.21 (BR-066), l.23, l.27 (BR-114)
- `dispatch-runs.md` l.30 (BR-064)
- `usage-capture-reference.md` l.17, 18, 20

**Page type against content:**

- `usage-capture-reference.md` l.22 explains inside a `reference` page.
- `usage-capture-reference.md` l.24-42, the test-ownership table, is contributor material.
- `run-dispatch-by-hand.md` l.27-29: a link sits inside the rule callout and breaks its Source line.

**Cuts for the structural pass:**

- `pre-commit-hooks.md` l.38 last sentence and l.43 repeat l.33-37.
- `skills.md`: the `reverse-map` row repeats the Specification row.
- `author-and-reviewer.md` l.15 repeats l.11-13.
- The pre-commit rule callout appears in three pages.

No instruction stopped a needed fix.
