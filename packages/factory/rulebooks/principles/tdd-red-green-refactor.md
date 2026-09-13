---
title: TDD Red-Green-Refactor
version: 1.0.0
---

# TDD Red-Green-Refactor

Test-Driven Development in its canonical three-phase cycle.

## Cycle

1. **Red.** Write a failing test that describes one unit of observable
   behavior. The test must fail for the right reason — a missing
   implementation, not a syntax error.
2. **Green.** Write the minimum code that makes the test pass. No
   design decisions beyond what the test requires.
3. **Refactor.** Improve structure without changing behavior. Refactor
   is its own phase — do not refactor mid-loop.

## Schools

- **London (mockist).** Isolate the unit under test with test doubles.
  Verify interactions. Suited to outside-in design.
- **Chicago (classicist).** Test through real collaborators. Verify
  state. Suited to domain-model-first design.

Choose the school that fits the story's architecture. The factory does
not prescribe one over the other.

## Vertical slices

Each test targets one observable behavior. Slice vertically through
layers rather than testing one layer at a time.
