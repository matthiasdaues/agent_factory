# Mutation Testing Setup

Reference material for setting up project-owned mutation testing. Used by
[mutation-testing](../../skills/mutation-testing/SKILL.md).

## What mutation testing is

Mutation testing changes production code in small, deterministic ways (an
operator flips `+` to `-`, a boundary `<` to `<=`, a condition `and` to `or`)
and checks whether the test suite notices. A test suite that hits every line
but does not notice these changes has line-hit coverage, not behavioral
coverage.

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
   format, normalize it to the JSON shape in the mutation-testing skill's
   Report format section so downstream tooling can consume it without
   depending on the chosen tool's native format.
