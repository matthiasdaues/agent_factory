---
title: Mechanized Dispatch Implementation Issues
status: resolved
reviewed_story: ST-0086
reviewed_commit: 56a5407c7a5ecb778c67bd63713d7cb3e27dd184
reviewed_against: bb6849e7600dc7974031128cdcc7f0a343fc082f
---

# Mechanized Dispatch Implementation Issues

This document consolidates implementation issues found while reviewing
[ST-0086](../../backlog/ST-0086.md) against the
[Mechanized Dispatch QA Strategy](../spec/supplementary_specs/mechanized-dispatch-qa-strategy.md).
It replaces individual finding files for this review.

## Current disposition

ST-0086 is not ready to merge. The full test suite passes, but three acceptance
and quality-strategy obligations remain unmet. A fourth blocking issue is that
the implementation commit changes files outside the story's declared outputs.

## Verification evidence

- Reviewed commit: `56a5407c7a5ecb778c67bd63713d7cb3e27dd184`.
- Declared base: `bb6849e7600dc7974031128cdcc7f0a343fc082f`.
- `factory/scripts/run-tests`: 47 tests passed.
- `git diff --check`: passed before this document was added.
- Worktree residue: one uncommitted dead-code repair in
  `factory/scripts/dispatch_lib.py` and one untracked `uv.lock`.

Passing tests do not establish conformance because the missing cases are not
exercised by the current suite.

## Enhanced-strategy repeat pass

The review was repeated after hardening the
[Mechanized Dispatch QA Strategy](../spec/supplementary_specs/mechanized-dispatch-qa-strategy.md).
The repeat pass exercised the newly explicit boundaries directly.

| Strategy check                             | Result                   | Evidence                                                                                                                            |
| ------------------------------------------ | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| Complete lifecycle matrix                  | Implementation passes    | All 49 ordered pairs classified: 9 valid, 7 idempotent, 33 invalid; no behavioral mismatch                                          |
| SHA constructor boundary                   | Fails                    | `StoryEntry(id="ST-X", base_sha="abc123")` is accepted                                                                              |
| SHA save boundary                          | Fails                    | `Ledger.save()` serializes `abc123` without rejection                                                                               |
| SHA load boundary                          | Fails                    | `Ledger.load()` accepts and exposes `abc123`                                                                                        |
| Status with valid ledger                   | Passes                   | Exit 0; ID, wave, status, branch, and full SHA rendered                                                                             |
| Status with missing ledger                 | Passes                   | Exit 1; diagnostic names the missing path                                                                                           |
| Status with structurally invalid ledger    | Passes                   | Exit 1; malformed-ledger diagnostic, no traceback                                                                                   |
| Status with syntactically malformed ledger | Fails                    | Input `this is not yaml` exits 0 and reports an empty ledger                                                                        |
| Declared-output audit                      | Fails                    | Four changed paths are outside the story's declared outputs; the backlog status update is the only mandatory control-file exception |
| Full test suite                            | Passes but is incomplete | 47 tests passed                                                                                                                     |
| Backlog linter                             | Passes                   | 0 errors, warnings, or informational findings across 86 stories                                                                     |

The repeat pass confirms that the transition implementation is correct. The
remaining transition issue is a defect in the committed owning test suite,
which does not mechanically preserve that result against regression.

## Blocking issues

### 1. Ledger SHA validation is bypassable

**Severity:** Major

**What is wrong:** `StoryEntry.set_sha()` validates a SHA, but callers can set
`base_sha` through the dataclass constructor, direct assignment, or YAML
deserialization without invoking it. `StoryEntry.to_dict()` and `Ledger.save()`
then serialize that unchecked value. A ledger can therefore store a SHA that
is not exactly 40 lowercase hexadecimal characters, contrary to
[ST-0086 acceptance criterion 3](../../backlog/ST-0086.md#ledger-model).

The tests validate only calls to `set_sha()` and themselves assign a SHA
directly during the round-trip test. They do not exercise validation at the
ledger load or save boundary.

**Fix:** Make the ledger boundary enforce the invariant. Validate every
non-null SHA during construction/deserialization and before serialization, or
make unchecked assignment impossible. Add tests proving invalid SHAs are
rejected when loaded and when saved, not only when passed to `set_sha()`.

### 2. Invalid-transition coverage is not exhaustive

**Severity:** Major

**What is wrong:** The
[Layer 2b strategy](../spec/supplementary_specs/mechanized-dispatch-qa-strategy.md#2b-story-lifecycle-state-machine)
sets "Every invalid pair" as the boundary. The current test list samples 15
invalid transitions and separately checks outbound transitions from `DONE`.
It does not derive and test the complete complement of valid and idempotent
state pairs.

The implementation table currently matches the specified nine valid edges,
but the owning test layer does not guard the whole invalid-transition
contract.

**Fix:** Generate all ordered pairs of `StoryState`. Classify the nine allowed
edges and seven same-state pairs separately, then assert that every remaining
pair raises `TransitionError` and names both states in its diagnostic.

### 3. The `dispatch status` tracer bullet accepts malformed input and has no owning test

**Severity:** Major

**What is wrong:**
[ST-0086 acceptance criteria 11 and 12](../../backlog/ST-0086.md#dispatch-status-subcommand)
require human-readable output for a valid ledger, exit zero for valid input,
and non-zero exits for missing and malformed ledgers. The executable returns
exit zero and `No stories in ledger.` for the syntactically malformed input
`this is not yaml`. The stdlib fallback parser silently ignores the invalid
line and produces an empty mapping.

No test invokes `cmd_status` or the `dispatch status` command, so the defect
was invisible to the 47-test suite. The previous review described this as
Layer 3 scope, but the original QA strategy assigned no later owner to this
ST-0086 contract. The enhanced strategy now assigns the executable boundary to
`tests/test_dispatch_status_integration.py`.

**Fix:** Give the command boundary an explicit owner. Add focused subprocess
contract tests for a valid ledger, a missing ledger, syntactically malformed
YAML, and structurally invalid YAML. Make the fallback parser reject any
non-empty unrecognized line and invalid top-level or `stories` shapes. Assert
exit codes, required table fields, and diagnostic output without duplicating
the pure state-machine assertions.

### 4. The commit exceeds the story's declared outputs

**Severity:** Major

**What is wrong:** [ST-0086 frontmatter](../../backlog/ST-0086.md) declares only
`factory/scripts/dispatch` and `tests/test_dispatch_lifecycle.py` as outputs.
The implementation commit also changes:

- `factory/scripts/dispatch_lib.py`
- `factory/playbooks/greenfield-development.fsm.yml`
- `pyproject.toml`
- `backlog/ST-0086.md`

The backlog status change is required by the dispatch rules, but the companion
library and project/playbook changes are not declared story outputs. This
breaks output-scope verification and hides unrelated policy/configuration
changes inside the implementation commit.

**Fix:** Add the necessary companion module to the story's declared outputs
before implementation, or keep the implementation within the declared script.
Treat changes to project configuration and the greenfield playbook as separate,
explicitly justified work unless the story is amended to require them. Keep
the mandatory story-status update in the implementation commit.

## Repaired issue

### Duplicate unreachable return

The reviewed commit contained a duplicate `return result` at the end of
`_stdlib_load()`. The second return was unreachable. It has been removed in the
worktree, and the full suite still passes. The repair is currently uncommitted.

## Worktree cleanup required

- Decide whether `uv.lock` is a required project artifact. If not, remove the
  generated untracked file before pre-merge verification.
- Commit the dead-code repair together with the substantive ST-0086
  remediation, following the required story-ID commit convention.
- Re-run the complete test suite and `factory/scripts/premerge-check` after all
  fixes and scope declarations are settled.
