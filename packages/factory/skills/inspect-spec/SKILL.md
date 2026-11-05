---
name: inspect-spec
description: Two-pass specification review — deterministic spec-lint then LLM semantic inspection. Files findings as local markdown files.
category: requirements
---

# Inspect Specification

Review the Phase-1 specification for defects **before** architecture consumes it. Two passes, strict division of labour:

Read [factory-voice.md](../../rulebooks/conventions/factory-voice.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates and clears the final pass.

- **Pass 1 — `spec-lint` (deterministic).** Catches provable defects — broken cross-references, missing Cockburn sections, undefined `BR-###`, unreachable states. Zero false-positive by design.
- **Pass 2 — semantic inspection (this LLM).** Only what a parser *cannot* decide: contradictions, ambiguity, testability, hidden assumptions, terminology drift.

Never re-check what Pass 1 already proved. Read `docs/spec/glossary.md` first.

## Step 1 — Run the deterministic linter

```bash
.agent-factory/factory/scripts/spec-lint --spec-dir docs/spec
```

`error` findings → Defect without debate. `warning`/`info` → confirm or dismiss during Pass 2.

## Step 2 — Semantic inspection

Read the full spec (`docs/spec/`), then evaluate against the Wiegers/INCOSE requirements-quality characteristics — assess only what Pass 1 could not:

1. **Consistent** — contradicting requirements, preconditions no use case establishes, prose ≠ diagram.
2. **Unambiguous** — vague terms ("fast", "user-friendly"), hidden actors, unclear pronouns.
3. **Verifiable** — postconditions and Gherkin scenarios concrete enough to assert in a test.
4. **Complete** — extensions cover real failure modes, not just the happy path; no PRD goal missing from use cases.
5. **Feasible** — no conflicting non-functional requirements.
6. **Necessary** — nothing specified that no actor goal justifies (gold-plating).
7. **Terminology** — terms conflict with `docs/spec/glossary.md`, or two terms for one concept.

### Check each structure file

Run one check for each structure file that exists. Skip the check of a file that does not exist. A missing optional structure file never stops the review. Only the feature files, the scope map, the glossary, and `docs/spec/entity-model.md` are required.

- **`docs/spec/entity-model.md`** — every entity that a feature file names is in the model. Its attributes and relationships agree with the Scenarios.
- **`docs/spec/state-machines.md`** — each machine belongs to an entity of the entity model. Its states and transitions agree with the Scenarios.
- **`docs/spec/validation-rules.md`** — each rule names an attribute of the entity model and a Scenario or `BR-###` that needs it.
- **`docs/spec/interface-contracts.md`** — each field of a DTO matches an attribute of the entity model. A Scenario reaches each operation.
- **`docs/spec/schemas/*`** — each schema agrees with its interface contract and with the entity model.
- **`docs/spec/areas/*.md`** — each area spec agrees with the feature files of its scope-map area.
- **`docs/spec/glossary.md`** — the checks under [Check the glossary](#check-the-glossary).

### Check the glossary

Compare the terms of `docs/spec/glossary.md` with the words the feature files and the structure files use. Look for three defects:

- **Two terms for one concept.** The glossary defines two terms for the same concept, such as `Batch` and `PaymentBatch`.
- **Term not defined.** A feature file or a structure file uses a domain term that the glossary does not define.
- **Avoided term in use.** A feature file or a structure file uses a word that the Avoid column of a glossary term names.

File each defect as a Minor `SPEC` finding with `owner: domain-modeling-agent`. File it even though Minor findings usually stay in the review report, so the owner receives it. It does not block: the blocking glossary gate stays deferred. The domain-modeling agent is the one producer of the glossary, so it fixes the defect. `spec-lint` rule `GLOSS001` already reports a glossary term that no file uses. Do not report an unused term again.

### Check the term candidates

Read `docs/spec/work/term-candidates.md` when it exists. A row with status `proposed` waits for the stakeholder's confirmation. File one Major `SPEC` finding with `owner: domain-modeling-agent` for each row with status `proposed`. Name the term and its domain area in the finding.

Terms in the glossary count as confirmed, among them the terms that `migrate-spec-layout` moved there. File no finding that a glossary term lacks the stakeholder's confirmation.

### Read the scope map only

Read `docs/spec/scope-map.md` to trace each Rule to its feature file. File no finding on the content of the scope map. The stakeholder reviews the scope map.

## Step 3 — Write the review report

Save as `docs/reviews/spec-review-YYYY-MM-DD.md` per [report-format.md](../../rulebooks/conventions/report-format.md), adding:

1. **Reviewed specification** — artifacts read, `spec-lint` summary line.
2. **Deterministic findings** — Pass-1 table, each row Confirmed or Dismissed.
3. **Semantic findings** — finding table with Characteristic column added.
4. **Structure checks** — one section for each file that Step 2 checked, the glossary and the term candidates included. Each section lists the file's findings or states that the check found none.
5. **Traceability summary** — orphans and gaps from the scope map and BR cross-reference checks.

File findings per [finding-format.md](../../rulebooks/conventions/finding-format.md) with tag `SPEC`.

Format both the report and any finding files via `.agent-factory/factory/scripts/mdformat --number` per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).

## Step 4 — Verify prior findings (repeat passes only)

Per [review-loop-discipline.md](../../rulebooks/conventions/review-loop-discipline.md): resolve or annotate each open `SPEC` finding, **and** re-run Steps 1-2 fresh against the full spec — not just the prior findings list — to catch new defects.
