# 0006. stdlib-first dependency policy — argparse + jsonschema

**Status**: Accepted

## Context

The PRD prefers the Python standard library and asks that any third-party dependency be justified (NFR-7), consistent with `spec-lint`'s zero-dependency style (C5). T-06 leaves the CLI framework and dependency policy open, leaning `argparse` + `jsonschema`. Two hard needs shape the choice: an argument parser for the command surface (FR-A), and robust validation of findings and run state against JSON Schema (VR-006, VR-010).

This ADR resolves T-06.

### Alternatives (Pugh Matrix)

Baseline **A**: stdlib `argparse` + `jsonschema` (one pure-Python dependency). **B**: `typer`/`click` + `pydantic`. **C**: pure stdlib including a hand-rolled JSON-Schema validator (zero dependencies).

| Criterion                                      | Weight | A: argparse + jsonschema | B: typer + pydantic | C: pure stdlib |
| ---------------------------------------------- | ------ | ------------------------ | ------------------- | -------------- |
| Validation correctness (Q1)                    | 3      | 0                        | +1                  | -1             |
| Implementation cost / risk (Q4)                | 2      | 0                        | 0                   | -1             |
| Consistency with spec-lint zero-dep style (Q4) | 2      | 0                        | -1                  | +1             |
| Installability / portability (Q5)              | 2      | 0                        | -1                  | 0              |
| Minimal dependencies (Q7)                      | 1      | 0                        | -1                  | +1             |
| **Weighted total**                             |        | **0**                    | **-2**              | **-2**         |

A is the best (baseline wins). This is a **close call between A and C**: hand-rolling a validator (C) achieves true zero dependencies and maximum consistency with `spec-lint`, but re-implementing JSON Schema draft-2020-12 validation is exactly the kind of subtle, correctness-critical code the store's integrity rules (VR-006/010) depend on — so validation correctness (weight 3) is the tie-breaker in A's favour. `jsonschema` is pure-Python with no build step, so choosing it barely dents the minimal-dependency goal. The heavier stack (B) loses on both consistency and install footprint without buying anything the tool needs.

## Decision

Use the **standard library `argparse`** for the command surface and **`jsonschema`** as the single justified runtime dependency for validating findings and run state. No other third-party runtime dependency is added without a follow-up ADR justifying it against this policy.

## Consequences

**Positive**

- The tool installs and runs on the Python stdlib plus one small, pure-Python dependency (QS-17); no compiler, no heavy framework.
- Schema validation is delegated to a correct, well-tested implementation rather than hand-rolled — protecting store and run-state integrity (VR-006, VR-010).
- Matches `spec-lint`'s ethos, keeping the Agent HQ toolchain coherent.

**Negative / risks**

- `argparse` is more verbose than `typer`/`click` for a growing command set; acceptable for six commands (FR-A), revisited only if the surface expands substantially.
- One runtime dependency to track for security/updates — a deliberate, bounded exception to the zero-dependency preference.
