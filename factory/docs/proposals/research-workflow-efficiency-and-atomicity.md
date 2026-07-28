# Feature Request: Research Workflow — Early Atomicity, Test-Count Alignment, Survey Mode, and Dispatch Economy

## Summary

Four changes to the falsification-driven research workflow, each aimed at a
specific, observed source of waste. The changes move two existing admission
requirements from late enforcement to early enforcement, add a lighter research
mode for survey questions, and make subagent dispatch economical by default.

1. **Catch compound claims at conjecture formation (Step 6), not at review
   (Step 8).** The Claim-Admission Policy already requires "One Assertion," but
   nothing checks it until adversarial review or register assembly — after the
   costly test and review sessions have already run.
2. **Align `planned_tests` count with the review protocol.** Admission requires
   every planned test to have a test record. When a conjecture plans more tests
   than the protocol executes, the claim fails admission through no fault of its
   substance.
3. **Add a survey/synthesis research mode.** The full falsification apparatus is
   built for a small number of contested, high-stakes claims. Landscape and
   discovery questions do not need it, and paying for it on such questions is the
   dominant cost.
4. **Make dispatch economical by default.** Route research subagents to a
   cheaper model tier, cap concurrent fan-out, and estimate spend before a wave.

## Motivation

A real research run (open-source tooling for a German paper-archive ingestion
pipeline) exercised the `research-topic` playbook end to end. It produced correct
findings, but at a cost far out of proportion to the question, and it collided
with the organisation's monthly spend limit several times. A retrospective
isolated the causes:

- **Wrong tier.** Every subagent inherited the session's strongest model. A
  landscape survey does not need the strongest tier across ~60–80 sessions;
  this was a roughly five-fold overspend fixed at the first dispatch.
- **Wrong instrument.** The falsification playbook was applied to a survey
  question ("which open-source tools exist for these stages"). Most of the
  adversarial machinery confirmed the obvious.
- **Late atomicity rejection.** Conjectures were authored as compound
  "capability whereas gap" claims. Reviewers correctly flagged them non-atomic,
  which forced a full resolution pass — re-authoring ten atomic claims and
  running thirty more reviews.
- **Test-count mismatch.** Conjectures planned four or five tests; the review
  protocol ran three (one per reviewer). Every claim then failed the
  "Required Tests Run" admission condition.
- **Oversized waves.** Twenty-wide dispatch waves exhausted the spend limit in a
  single burst; the failures landed mid-write, so whole sessions were lost and
  repeated.

Changes 1 and 2 remove the two design traps. Change 3 removes the instrument
mismatch. Change 4 removes the tier and wave-size costs.

## Change 1 — Early atomicity gate at Step 6

**Problem.** The Claim-Admission Policy's "One Assertion" requirement is
evaluated at semantic review and at register assembly. By then the claim has
already consumed its test, review, and vote sessions. A compound claim discovered
there forces a split, which restarts the claim at Step 5 with fresh tests,
reviews, and votes.

**Fix.**

- Add a deterministic compound-claim heuristic to conjecture validation
  (`scripts/schema-validate` companion lint, or a new `scripts/conjecture-lint`)
  that flags a `claim` field carrying more than one assertion: coordinating
  conjunctions joining independent predicates ("whereas", "but", "; ",
  " and " between full clauses), a capability assertion and a gap assertion in
  one sentence, or multiple main verbs across distinct subjects. The heuristic
  raises a warning, not a hard block — a human or the orchestrator confirms — but
  it fires at Step 6, before any test runs.
- Strengthen the `claim-formulation` skill so the author states one disposition
  per conjecture (one capability claim, or one gap claim — never both), and
  splits a bundled finding at formation time.
- Update `research-topic.md` Step 6 to name the atomicity check explicitly among
  the conditions the orchestrator verifies before Step 7.

**Effect.** A compound claim is caught before it consumes a single test session,
not after it consumes a full test-review-vote cycle.

## Change 2 — Align planned tests with the review protocol

**Problem.** Admission requires a test record for every entry in `planned_tests`.
Research planning decides how many reviewers and tests a claim receives, but
nothing constrains the conjecture author to plan that many tests. A conjecture
that plans five tests under a three-test protocol is unadmittable regardless of
merit.

**Fix.**

- In the `research-planning` skill, state the review protocol as an explicit
  parameter: reviewers-per-claim and tests-per-claim (for the standard and
  high-risk tiers). The plan records these numbers.
- In the `claim-formulation` / `refutation-design` skills, instruct the author
  to plan exactly the number of severe tests the protocol will execute — no
  aspirational extras. Fewer, severe, and executed beats many and unrun.
- Add a cross-check to conjecture validation: `len(planned_tests)` must equal the
  plan's tests-per-claim for the claim's tier. Mismatch warns at Step 6.

**Effect.** The "Required Tests Run" condition becomes satisfiable by
construction, instead of an after-the-fact failure.

## Change 3 — Survey/synthesis research mode

**Problem.** The playbook has one gear: full falsification. For a landscape or
discovery question the independent-researcher, three-reviewer, vote, and register
apparatus is overkill, and its cost is the dominant expense.

**Fix.**

- Add a mode-selection front-gate to `research-topic.md` (or a sibling
  `research-survey.md` playbook) with a short decision rubric:
  - **Survey/synthesis mode** when the question is "what exists / what is the
    landscape / summarise the options" and the cost of a wrong synthesis is low
    to moderate. Runs a single fan-out of sourced searches, a light
    self-verification pass, and a cited synthesis — no independent voting, no
    register. This requires only portable source-search and synthesis
    capabilities.
  - **Falsification mode** (the current playbook) when there are a few contested,
    high-stakes claims and an auditable "survived refutation" trail justifies the
    cost.
- The brief gains a `mode` field, defaulting to survey; falsification is opt-in.

**Effect.** The expensive path is reserved for the questions that need it.

## Change 4 — Economical dispatch by default

**Problem.** Subagents inherited the session's strongest model and were
dispatched in waves large enough to exhaust the spend limit in one burst.

**Fix.**

- In the dispatch contract (`rulebooks/conventions/dispatch-contract.md`) and
  the playbook, default research subagents to the economy or standard tier and
  reserve the strong tier for explicitly flagged hard sessions.
- Cap concurrent fan-out to a small batch (default six) and dispatch in waves,
  so a spend-limit or infrastructure failure degrades gracefully rather than
  losing a twenty-wide burst mid-write.
- Add a pre-flight estimate: sessions × tier × rough tokens, surfaced before a
  wave launches, as a spend gate.
- Cross-reference the existing `agent-dispatch-token-efficiency.md` proposal.

**Effect.** The same rigor at a fraction of the spend, with failures that cost
one small batch instead of a whole wave.

## Non-Goals

- Changing the Claim-Admission Policy's requirements themselves. One Assertion
  and Required Tests Run stay; only their point of enforcement moves earlier.
- Weakening role separation or independence in falsification mode.
- Replacing the deep-research capability; survey mode adopts its shape within the
  factory's brief-and-report framing.

## Implementation Surface

- `playbooks/research-topic.md` — Step 6 atomicity + test-count checks; mode
  gate.
- New `playbooks/research-survey.md` (or a mode branch) — the survey path.
- `skills/claim-formulation/SKILL.md`, `skills/refutation-design/SKILL.md` — one
  disposition per conjecture; plan exactly the executed tests.
- `skills/research-planning/SKILL.md` — protocol parameters (reviewers/tests per
  tier); brief `mode` field.
- `scripts/` — a `conjecture-lint` (atomicity heuristic + planned-test-count
  cross-check) invoked at Step 6.
- `rulebooks/conventions/dispatch-contract.md` — default tier, batch cap,
  pre-flight estimate.
- `rulebooks/templates/research-brief.md` + `research-brief.schema.json` — add
  the optional `mode` field.

## Origin

Derived from the retrospective on the binder-to-OCR research run
(see `paper-ingestion-research/RESUME.md` for that run's artifacts and the
memory note `project_binder-ocr-research-run`).
