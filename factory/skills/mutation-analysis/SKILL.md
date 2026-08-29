---
name: mutation-analysis
description: Set up project-owned mutation testing to verify behavioral coverage, classify survivors, and — when a QA strategy contract-owner table exists — classify each mutant's contract ownership.
category: quality
disable-model-invocation: true
---

# Mutation Analysis

Mutation testing changes production code in small, deterministic ways (an
operator flips `+` to `-`, a boundary `<` to `<=`, a condition `and` to `or`)
and checks whether the test suite notices. A test suite that hits every line
but does not notice these changes has line-hit coverage, not behavioral
coverage. This skill sets up that check as a project-owned gate and defines
how to classify what it finds.

## Setup guidance

Mutation testing is project-owned: choose and configure a mutation tool for
the project's language and test runner, then wire it into the project's own
gate scripts. This skill does not prescribe a tool chain.

1. **Choose a mutation tool for the stack.** Pick whatever the language and
   test framework support (for example, a Python mutator, a JVM mutator, a Go
   mutator, a JS/TS mutator). The tool must run the existing test suite
   against each mutant and report kill/survive per mutant.
2. **Configure it against production code only.** Point the tool at the
   project's source tree, excluding test files, fixtures, and generated code.
   Mutating test code produces meaningless results — a mutated test can only
   ever "survive" against itself.
3. **Scope to the diff when running per-story.** Full-module mutation runs
   are expensive and re-litigate code the story did not touch. When the gate
   runs per story, diff the story branch against its base ref, drop files
   matching the project's test-file conventions (`test_*`, `*_test.*`,
   `*.test.*`, `*.spec.*`, anything under a `tests/` or `__tests__/`
   directory), and mutate only the remaining production files. When the gate
   runs on the full module instead — for example, on a scheduled or
   pre-release run — mutate the project's declared source tree directly.
4. **Run it as part of CI or the pre-merge gate.** Wire the tool's exit
   status (or a wrapper script that inspects its report) into the same gate
   mechanism the project uses for other deterministic checks — the goal is a
   merge-blocking check, not a report nobody reads.
5. **Persist a machine-readable report.** Whatever the tool's native output
   format, normalize it to the JSON shape in [Report format](#report-format)
   so downstream tooling (resolution tracking, contract-ownership
   classification) can consume it without depending on the chosen tool's
   native format.

## Survivor classification

Every mutant the tool produces resolves to one of two statuses:

- **`killed`** — a test (or another deterministic check) detected the
  behavioral change. No follow-up action is required.
- **`survived`** — nothing detected the behavioral change. The mutant must be
  resolved before merge.

Every surviving mutant must be classified into one of three resolution
actions:

1. **`remove-dead-code`** — the mutant proves the code has no behavioral
   owner; remove the dead code rather than preserving it.
2. **`add-missing-test`** — the code is real behavior and a contract test is
   missing; add the test that kills the mutant.
3. **`file-qa-finding`** — the developer cannot resolve it inside the coding
   loop; file a QA finding and attach that resolution to the gate run.

A survivor without one of those three actions is `unresolved` and blocks
merge. Zero unresolved survivors is required for merge.

## Contract-ownership classification

When a feature's QA strategy defines a contract-owner table (see
[qa-strategy-from-spec](../qa-strategy-from-spec/SKILL.md)), classify each
killed mutant against that table instead of stopping at `killed`. This turns
"something caught it" into "the layer we intended to catch it, caught it" —
and surfaces the difference when it did not.

### Without a contract-owner table

If the feature has no contract-owner table, skip contract-ownership
classification entirely. Use survivor classification and its three
resolution actions only.

### The three statuses

For each mutant that a contract-owner table covers:

- **`owner_held`** — the declared contract owner's tests killed the mutant.
  This is the expected outcome. Tests from other layers that also killed the
  same mutant are overlap; they are safe to trim per
  [testing-strategy.md § Delete overlapping tests safely](../../rulebooks/conventions/testing-strategy.md#delete-overlapping-tests-safely).
- **`owner_failed`** — the declared contract owner's tests did *not* kill the
  mutant, but a test from another layer did. The gate held, but the wrong
  layer held it — the declared owner's tests are incomplete for that
  contract. File an `owner_failed` classification as a `spec-feedback`
  finding against the contract-owner row, naming the contract, the layer that
  actually caught it, and the gap in the owner's tests.
- **`uncaught`** — no layer's tests killed the mutant. Treat this as an
  ordinary surviving mutant and direct the existing resolution actions
  (`remove-dead-code`, `add-missing-test`, `file-qa-finding`) at the declared
  owner: the missing test belongs in the owner's layer, not wherever is
  convenient.

### Join mechanism — attributing a mutant to a contract

To classify a mutant, first find which contract it belongs to, then find
which test(s) killed it, then compare the killing test's layer against the
table's declared owner for that contract.

1. **Preferred: spec marker join.** When a killing test carries a
   `@pytest.mark.spec("<scope-ID>")` marker, look up `<scope-ID>` directly in
   the contract-owner table. The marker ties the test to its contract
   unambiguously, independent of file location.
2. **Fallback: file-path join.** When no killing test carries a spec marker,
   map the mutated source file to a contract via the contract-owner table's
   declared file patterns (or the mapping the project's QA strategy
   documents for that feature), and map the killing test's file to a layer
   the same way. This join is weaker — a shared file does not prove a shared
   contract — so prefer marker-based join wherever tests carry markers.

If neither join resolves a killed mutant to a table row, treat it as outside
the contract-owner table's scope: it stays `killed` under survivor
classification, but is not assigned a contract-ownership status.

## Report format

Normalize the mutation tool's native report into JSON entries with these
fields:

- `operator` — the detected source change, for example `+ -> -`
- `location` — `path:line` for the mutated source line
- `status` — `killed` or `survived`
- `resolution_action` — `none-required`, `unresolved`, `remove-dead-code`,
  `add-missing-test`, or `file-qa-finding`

When a contract-owner table is available and the mutant resolves against it,
add:

- `contract_owner` — the scope ID of the contract-owner row the mutant joined
  to (for example `DSP-01`), or `null` when no table row resolved
- `classification` — `owner_held`, `owner_failed`, or `uncaught`, present only
  when `contract_owner` is non-null

Keep whatever tool-specific identifiers help trace a report entry back to the
mutation tool's own output (a mutant ID, a raw status string) as additional
fields — they are useful for operator review but are not part of the
contract this skill enforces.
