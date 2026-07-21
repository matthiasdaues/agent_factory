---
name: refutation-design
description: Define refuting evidence, conditions for refutation, and severe tests to expose them.
category: research
disable-model-invocation: false
---

# Refutation Design

Design tests and evidence conditions that would refute or falsify a claim. This skill provides a capability; it does not control the sequence or rhythm of the research workflow — the playbook does.

## Purpose

Specify what evidence or observations would count as refutation, then design severe tests to attempt to find that evidence. The output is a set of test records and planned tests — structured artifacts that drive the refutation phase of the research workflow. This step embodies the principle that a hypothesis with no conceivable refutation is not science; it is dogma.

## Inputs

- Conjecture artifact (the claim, its scope, assumptions, and refutation conditions)
- Source records (evidence already collected)
- Alternative explanations or competing conjectures

## Output

Test records and planned tests containing:

- claim ID and version
- test question (specific question to be answered)
- result that would refute the claim (the success condition for refutation)
- method (how the test will be run)
- evidence examined (sources or data to be reviewed)
- observed result (what was actually found)
- limitations (scope or confidence bounds of the test)
- outcome (`SURVIVED`, `REFUTED`, `INCONCLUSIVE`, or `INVALID_TEST`)

## Core Process

1. **Identify refutation conditions.** Examine the conjecture's "possible refuting evidence" section. These are the conditions stated in the claim itself as the criteria for refutation.

2. **Break refutation into testable steps.** For each refutation condition, design specific, achievable tests. Example: if refutation condition is "a primary source from an independent observer contradicts the account," design tests that:

   - search for independent observers who were present,
   - verify their independence and access,
   - examine their recorded statements about the event.

3. **Make tests severe.** Each test should have a real chance of finding the claim wrong. Severity means:

   - The test is not rigged to succeed.
   - Evidence is sought from sources and methods that could contradict the claim.
   - The test is designed to expose the most vulnerable assumptions.
   - Multiple independent sources are checked, not just convenient ones.

4. **Plan without pre-judgment.** Before running a test, write down exactly what result would count as refutation. Do not decide the outcome in advance or rationalize away adverse findings. The test succeeds if it falsifies the claim; it fails if it does not. Inconclusive results must be recorded as such, not rounded to "probably survived."

5. **Run planned tests.** For each planned test:

   - State the research question precisely.
   - Execute the method as designed.
   - Record the exact evidence examined (with dates, sources, families).
   - Note the observed result.
   - Compare to the refutation condition.
   - Classify the outcome: `SURVIVED`, `REFUTED`, `INCONCLUSIVE`, or `INVALID_TEST`.

6. **Keep failed tests visible.** Do not hide inconclusive or failed tests. Record all of them in the test-record artifacts. These form the audit trail for review and voting.

## Key Constraints

**A claim without refutation conditions is not ready for review.** If the conjecture does not state what would count against it, the claim cannot be falsified. No test can be designed. Do not proceed with test design until the claim includes explicit refutation conditions. This is enforced at the validation gate; refutation design must not work around it.

Tests cannot be *designed* after the fact to salvage a claim. If a refutation condition emerges only after tests have run, the assumption has changed. Any semantic change to the claim requires new reviews and votes.

## When Refutation Design Is Complete

- Each refutation condition is mapped to one or more tests.
- Tests are designed to be severe, not decorative.
- The exact success condition for refutation is stated before execution.
- All test records are recorded, including failed and inconclusive outcomes.
- Test records are valid against their schema.
- The audit trail preserves both successful and failed tests for review.

## Guiding Principle

Ask not only "Did we find evidence the claim is true?" but "Did we expose the claim to a serious, designed attempt at refutation? What would have disproved it, and did we look?"
