---
id: FAGAN-0001
source: fagan-review
artifact: docs/adr/0012-definition-time-validation-scope.md:13
traces: [ST-0001A, ADR-0012, DEF-01]
---

# The documents describe the wrong validation design

**What is wrong:** ST-0001A uses direct checks on the `execution` dictionary. The code checks each
value's type, length, allowed number range, and regular-expression pattern. This is the design that
the project owner approved.

ADR-0012 says that the code must instead use a Pydantic model named `ExecutionConfig`. A Pydantic
model is a typed Python object that validates data. The ST-0001 refinement and the transcript
comparison repeat this requirement. The documents and the approved code therefore describe two
different designs.

This is not only a wording problem. During this review, the developer agent followed the documents
and changed the code to use Pydantic. That work then had to be undone after the project owner
clarified the intended design. The same mistake can happen again while the documents remain wrong.

**Fix:** Update ADR-0012 and `docs/refinements/ST-0001-refinement.md` so that they describe direct
validation of the raw dictionary. Also correct or mark as superseded the conflicting statement in
`docs/transcripts/2026-09-09_onboarding-gigacron-and-factory-vs-state.md`. Keep the current
validation rules, including these rules for `run_as`:

- The value is optional.
- When present, it must be a string.
- Its length must be between 1 and 128 characters.
- Every character must match `[a-zA-Z0-9_.-]+`.

Remove the requirement for a Pydantic `ExecutionConfig` unless the project owner makes a new design
decision that replaces the direct validator.
