---
name: claim-formulation
description: Produce one precise, testable claim from recorded evidence with scope, assumptions, and content hash.
category: research
disable-model-invocation: false
---

# Claim Formulation

Formulate a single precise and testable claim from recorded evidence. This skill provides a capability; it does not control the sequence or rhythm of the research workflow — the playbook does.

## Purpose

Transform evidence collected during a research assignment into one clear, atomic claim that can be refuted. The output conjecture embodies the claim against a template and schema, recording its scope, assumptions, supporting evidence, contrary evidence, and content hash for use in subsequent validation and review steps.

## Inputs

- Research question
- Source records (evidence collected during research)
- Competing explanations or alternative hypotheses

## Output

Conjecture artifact containing:

- one claim (atomic statement)
- scope (boundaries of applicability)
- assumptions (preconditions for the claim)
- supporting evidence (sources cited with precise locations)
- contrary evidence (sources showing limitation or contradiction)
- possible refuting evidence (what evidence would disprove it)
- planned tests (methods to expose the refutation conditions)
- qualifications (caveats, confidence, or remaining uncertainty)
- content hash (deterministic fingerprint for tracking changes)

## Core Process

1. **Review the evidence.** Read source records in full, noting both supporting and contrary findings. Identify gaps, limitations, and assumptions embedded in the sources themselves.

2. **State one claim.** Write a single declarative sentence that captures the core finding. The claim must be testable — it must specify conditions under which it could be disproved.

3. **Define scope.** State the boundaries: what populations, places, times, or contexts the claim applies to. Scope binds the claim to the evidence actually collected.

4. **List assumptions.** Record every precondition required for the claim to hold. Examples: "assumes source author had access to the event," "assumes no systematic reporting bias," "assumes definitions have remained stable." Assumptions are not weakness; unexamined assumptions are.

5. **Record evidence.** For supporting evidence, cite each source by family, author, date, and the precise passage or finding that supports the claim. For contrary evidence, record sources that contradict, limit, or complicate the claim.

6. **Identify refutation conditions.** Specify what evidence or observations would count against the claim. These are the conditions that, if true, would force revision or rejection. Example: "If a primary source shows the author was not present, the claim is refuted."

7. **Plan tests.** Design specific tests that attempt to expose the refutation conditions. Tests should be severe — they should have a real chance of finding the claim wrong. Examples: seeking contrary sources by family, re-examining chronology, checking for selection bias in the evidence.

8. **Compute hash.** Generate a content hash from the claim text, scope, and assumptions. This hash is used to detect whether a claim has been changed semantically after review or voting has begun.

## When Formulation Is Complete

- The claim is stated in a single sentence.
- Scope clearly limits applicability.
- Assumptions are explicit and numbered.
- Each source citation includes family, author, date, and location.
- Refutation conditions are stated in the "possible refuting evidence" section.
- Planned tests are specific and achievable.
- Content hash is recorded and reproducible.
- The conjecture artifact is valid against its schema.

## Key Principle

A claim without refutation conditions is not ready for review. Ensure every claim carries forward a clear "what would refute this" statement. This condition is enforced at validation; formulation must respect it from the start.
