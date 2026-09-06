---
name: adversarial-review
description: Test a claim, its evidence, and refutation attempts against ten review checks, classify defects, and produce a vote tied to exact claim hash.
category: research
---

# Adversarial Review

This skill provides a capability to conduct an adversarial review of a claim within a falsification-driven research workflow. The skill does not control the sequence of the research process — the playbook controls sequence.

## Purpose

Apply a structured set of ten review checks to assess whether a claim is defensible given its evidence, tests, and attempted refutations. Classify any defects found, and produce a review artifact and a corresponding vote tied to the exact claim hash. The review determines whether a claim may survive and advance to the final report.

## Input Artifacts

- **Conjecture** — the claim to be reviewed, including its scope, assumptions, and evidence.
- **Source records** — the cited sources, with provenance and limitations.
- **Test records** — the completed refutation tests, with methods and outcomes.

## Output Artifacts

- **Review** — structured assessment against the ten checks, with classified defects (from `rulebooks/templates/research-review.md` and validated by `rulebooks/schemas/research-review.schema.json`).
- **Vote** — a vote decision tied to the reviewed claim hash (from `rulebooks/templates/research-vote.md` and validated by `rulebooks/schemas/research-vote.schema.json`).

## The Ten Review Checks

Each review must systematically check:

01. **Is the claim testable?** The claim must state conditions under which it would be false. An unfalsifiable claim cannot proceed.

02. **Were credible alternatives considered?** The review must verify that competing explanations were explored and rejected with justification.

03. **Were the tests severe?** A test is severe if it stands a real chance of refuting the claim. Weak or biased tests do not raise confidence.

04. **Did the claim survive without being changed?** If the claim was modified after a failed test, reviews and votes based on prior versions no longer count.

05. **Do the sources support the exact wording?** Quote carefully from the sources. Paraphrase must be precise. Unsupported inferences disqualify a claim.

06. **Are the sources independent?** Copies or paraphrases of one source family count as one source, not corroboration. Multiple independent families are required.

07. **Are assumptions explicit?** Every unstated assumption is a hidden inference. Identify all assumptions and verify they are disclosed in the claim.

08. **Does the claim exceed the tested scope?** A claim must not assert more than its tests can support. Scope creep is a common failure mode.

09. **Is contrary evidence still unexplained?** Unexplained contrary evidence weakens confidence. The review must document which contrary findings remain unaddressed.

10. **What evidence could still overturn the claim?** Identify remaining refutation paths. Claims that have survived all available tests but depend on an untested assumption remain provisional.

## Defect Classification

Defects found during review are classified into four levels:

- **BLOCKER** — A defect that prevents the claim from surviving. Examples: the claim is untestable, evidence does not support it, a severe test refuted it, a blocker blocks survival regardless of voting margin.

- **MAJOR** — A significant flaw that undermines confidence but does not formally block survival. Examples: assumptions not explicit, sources not independent, minor scope creep, unexplained contrary evidence.

- **MINOR** — A small issue that should be noted and addressed but does not substantially affect the claim's standing. Examples: a source reference is imprecise but the intended meaning is clear, a minor wording improvement would strengthen the claim.

- **NOTE** — Observations, suggestions, or neutral information that do not constitute defects. Examples: related open questions, suggestions for future research, clarifications that do not change the claim's meaning.

Only a BLOCKER prevents survival. MAJOR, MINOR, and NOTE defects are recorded but do not automatically disqualify a claim if other votes support it. However, a blocker in any review prevents survival.

## Vote Tied to Claim Hash

Each vote must refer to:

- The exact content hash of the claim being reviewed (to ensure the vote applies to the current version, not a later revision).
- One completed review by the voting reviewer.
- One eligible reviewer (who did not author the claim and is not in a conflicting role).

Allowed vote values are:

- `SURVIVE` — The claim met the process standard and should advance.
- `REFUTE` — The claim should not survive; a defect or refutation evidence is decisive.
- `UNRESOLVED` — The claim cannot be assessed without additional evidence or clarification.
- `ABSTAIN` — The reviewer chooses not to vote.

A claim survives only when:

- All required tests were run.
- Evidence requirements were met.
- Quorum was reached (sufficient reviewers assessed it).
- `SURVIVE` received a strict majority of decisive votes (excluding abstentions).
- No blocker remains.
- No material refutation remains unanswered.
- All votes refer to the current claim hash.

## Capability, Not Sequence

This skill provides a capability for one reviewer to conduct one adversarial review. It does not decide when reviews occur, how many reviewers assess a claim, how votes are tallied, or what happens next. The research playbook controls the sequence of reviews, the number of reviewers required, and the decision rules for survival.
