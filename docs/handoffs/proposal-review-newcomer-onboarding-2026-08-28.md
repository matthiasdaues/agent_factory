# Handoff: Newcomer Onboarding Proposal — Address Review Findings

**Date:** 2026-08-28
**From:** proposal-review-agent
**To:** proposal author (next session)

## Current State

**Branch:** `dev`
**Local tip:** `e8c9c4a93e6ab7d1b8118e6f905dd72b71ff198a`
**Upstream:** `agent_factory/dev` — even (0 ahead, 0 behind)
**Working tree:** proposal and 7 finding files are untracked; test files show
staged modifications from prior work (unrelated to this review).

The adversarial review of the newcomer-onboarding proposal is complete. Seven
findings (2 major, 5 minor) are filed and the review section is appended to the
proposal. No findings have been addressed yet.

## Artifacts

| Artifact          | Path                                                               | State                              |
| ----------------- | ------------------------------------------------------------------ | ---------------------------------- |
| Proposal          | `docs/proposals/newcomer-onboarding-and-incremental-brownfield.md` | Review section appended; untracked |
| Finding PROP-0013 | `docs/findings/PROP-0013.md`                                       | open, major                        |
| Finding PROP-0014 | `docs/findings/PROP-0014.md`                                       | open, major                        |
| Finding PROP-0015 | `docs/findings/PROP-0015.md`                                       | open, minor                        |
| Finding PROP-0016 | `docs/findings/PROP-0016.md`                                       | open, minor                        |
| Finding PROP-0017 | `docs/findings/PROP-0017.md`                                       | open, minor                        |
| Finding PROP-0018 | `docs/findings/PROP-0018.md`                                       | open, minor                        |
| Finding PROP-0019 | `docs/findings/PROP-0019.md`                                       | open, minor                        |

## What the Next Session Must Do

Address all seven findings in the proposal, then re-submit for a repeat review
pass. The two majors must be fixed before the proposal is planning-ready.

### Major findings (must fix)

1. **PROP-0013** — Add CONTEXT.md to Completion Criterion 3. The Scope section
   lists it as a prerequisite but CC-3 omits it. One-line fix.
2. **PROP-0014** — Wire reverse-map to Stage 1. Design Section 3 says
   "scope-map.md populated with existing Rules" but never names the reverse-map
   skill (Section 4) as the mechanism. Add an explicit cross-reference.

### Minor findings (should fix)

3. **PROP-0015** — Remove or mark Open Question 3 as resolved (it was answered
   by Design Section 4).
4. **PROP-0016** — Add `.claude/CLAUDE.md` to `impact.boundaries`.
5. **PROP-0017** — Fix `estimated_consumption.min`: either 120,000 (8,000 x 15)
   or adjust the multiplier.
6. **PROP-0018** — Rephrase CC-4 to remove "optionally deepens" and state
   a mechanically testable outcome.
7. **PROP-0019** — Specify the output path for the factory glossary stub.

### After fixing

Re-submit the proposal for a repeat adversarial review pass. The repeat pass
must re-run all eight checks (not only verify prior findings), and will append a
new review section below the existing one.

## Suggested Skills

- **grilling** — resolve the two remaining genuine Open Questions (OQ-1:
  guided tour as standalone skill vs. entrypoint-only; OQ-2: Stage 1/2 gate
  marker) before the repeat review, since they remain undecided despite
  accepted status.
- **validate** — run after edits to catch mdformat and lint issues before
  re-submitting.
- **handoff** — write a new handoff if the repeat review produces further
  findings requiring another session.
