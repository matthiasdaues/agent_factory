# Handoff — Specification Review to Requirements Agent

**Date**: 2026-08-17
**From**: Specification Review Agent (Phase 1.2)
**To**: Requirements Agent
**Disposition**: Open findings -- 1 MAJOR, 3 MINOR (report-only)

## Current State

Phase 1.2 (Specification Review) of the feature-addition playbook for Bausteinsicht Factory Integration is complete. The review found 1 Major finding that requires remedy before architecture can proceed. The project owner confirmed mid-review that Bausteinsicht has no inbuilt restriction on reverse sync -- the labels-only restraint is a work practice, not a tool guardrail.

### Repository State

- **Branch**: `dev`
- **Local HEAD**: `747d0fa79bbcf7fb916bf0a214232b42c06b7aa1`
- **Upstream**: `agent_factory/dev`
- **Ahead/behind**: 2 ahead, 0 behind
- **Working tree**: clean

### Gate Results

- **spec-lint**: 0 errors, 0 warnings, 21 info. Clean.
- **Prior findings**: SPEC-001 through SPEC-006, all `status: resolved`. No regressions.

## Open Finding (MAJOR)

### Reverse sync scope inconsistency -- UC-13, BR-051, T-11, and PRD FR-AM-A3

**Characteristic**: Consistent
**Severity**: Major

**What is wrong**: Multiple spec artifacts describe Bausteinsicht's reverse sync as restricted to labels and descriptions, but the tool has no such restriction. The project owner confirmed: Bausteinsicht performs full, unrestricted reverse sync. The labels-only restraint is a work practice, not a tool guardrail.

Contradicting artifacts:

- UC-13 MSS step 5: "label and description text edits from the draw.io diagram propagate back to the JSONC model" -- presents restricted behavior as a system fact.
- UC-13 extension 5a2: "The structural addition remains in draw.io only; it does not appear in JSONC (BR-051)" -- false. The structural addition DOES flow into JSONC.
- UC-13 extension 5a3: "bausteinsicht validate will report the structural inconsistency" -- invalid. After unrestricted reverse sync, both files are consistent; validate passes. The safety net does not work as described.
- BR-051 in validation-rules.md: "Reverse sync carries back only label and description text" -- contradicts the tool's actual behavior.
- PRD FR-AM-A3: "Reverse sync does not create, delete, or rename elements or relationships in the JSONC model" -- false.
- PRD FR-AM-A2: "Reverse sync carries label and description text edits" -- understates behavior.
- T-11 is actually correct: "bausteinsicht sync performs a full reverse sync -- it carries back whatever Bausteinsicht's reverse pass produces, not just labels and descriptions."

**Why this matters**: An implementer reading UC-13, BR-051, or the PRD FRs would build or test for restricted reverse sync that does not exist. A tester writing scenarios for extension 5a would expect structural additions to stay in draw.io only, but they would flow into JSONC. The safety-net claim (validate catches drift) is also invalid -- after full reverse sync, both files agree, so validate passes even if structural changes were unintentional.

**Fix direction**:

1. Rewrite UC-13 step 5 to state that `bausteinsicht sync` performs a full, unrestricted reverse pass. All draw.io changes -- structural, labels, descriptions -- propagate to JSONC.
2. Rewrite extension 5a to reflect actual behavior: structural additions in draw.io DO flow into JSONC. Clarify that the workflow discipline (Architecture Authors add elements via JSONC only) is the primary mitigation, not a tool restriction.
3. Reconsider extension 5a3: validate cannot catch structural drift that has already been synced into both files. Specify what the actual safety mechanism is (pre-sync validation? workflow discipline? review?).
4. Rewrite BR-051 to describe the tool's actual behavior and the work-practice convention separately. Currently it states "carries back only" as though the tool enforces it.
5. Update PRD FR-AM-A2 and FR-AM-A3 to match.
6. Check interface-contracts.md sync subcommand description for the same issue.
7. Regenerate traceability.json after updates.

## Minor Findings (report-only, no filing)

1. **UC-17 missing Docker unavailability extension**: UC-17 step 5 runs `bausteinsicht validate` which requires Docker (BR-053). UC-13, UC-14, UC-15, UC-16 all have Docker-unavailability extensions; UC-17 does not. Add one.

2. **SF-04 (bausteinsicht diff) orphaned subfunction**: Defined in actor-goal list, EARS-specified, listed in interface contracts, but no use case references it. The claimed consumers (PR descriptions, review workflows) are not part of the current specification.

3. **BR-055 trigger scope ambiguity**: The hook fires for any `.jsonc` or `.drawio` file in the staging area, but co-staging (BR-054) and validation (BR-056) logic is specific to `architecture.jsonc` and `architecture.drawio`. Behavior for non-architecture `.jsonc`/`.drawio` files is unspecified.

## Decisions Made

- Separate PRD for architecture modeling: appropriate (distinct domain from flow control).
- Actor taxonomy (Architecture Author / Architecture Reviewer / Human Reviewer): clean, well-bounded, distinct permission envelopes.
- Pre-commit hook integration via existing UC-08 infrastructure: no UC-08 modification needed.
- T-11 and T-12 are properly bounded as deferred items.

## Open Decisions

- None beyond the Major finding.

## Artifacts Requiring Update

- `docs/spec/use_cases/UC-13-synchronize-model-and-diagram.md` -- step 5, extension 5a
- `docs/spec/supplementary_specs/validation-rules.md` -- BR-051
- `docs/spec/prd-architecture-modeling.md` -- FR-AM-A2, FR-AM-A3
- `docs/spec/supplementary_specs/interface-contracts.md` -- sync subcommand description
- `docs/spec/traceability.json` -- regenerate after updates

## Artifacts Reviewed (no modification needed)

- `docs/spec/prd-architecture-modeling.md` (except FRs noted above)
- `docs/spec/actor-goal-list.md`
- `docs/spec/use_cases/UC-14-validate-model-consistency.md`
- `docs/spec/use_cases/UC-15-export-architecture-views.md`
- `docs/spec/use_cases/UC-16-migrate-from-structurizr-dsl.md`
- `docs/spec/use_cases/UC-17-validate-architecture-at-commit.md`
- `docs/spec/use_cases/system-use-cases.md`
- `docs/spec/supplementary_specs/entity-model.md`
- `docs/spec/todos.md`

## Standing Action Item (user directive, carries forward)

**At the next phase end**: Compare real token use for this feature-addition run against the proposal estimate (`docs/proposals/bausteinsicht-factory-integration.md`, `estimate.normalized_tokens: 40000-80000`). Analyse root cause for the mismatch. Provide remedy suggestions. This directive applies to whichever agent closes the next phase boundary -- do not defer further.

## Next Action

Requirements agent: address the Major reverse-sync inconsistency. Bausteinsicht's reverse sync is unrestricted -- the spec must describe the tool's actual behavior and specify the labels-only restriction as a work-practice convention, not a system fact. Update UC-13, BR-051, PRD FRs, and interface contracts accordingly. Consider the three Minor gaps. Then re-request spec review (Phase 1.2 repeat pass).

## Suggested Skills

- `derive-spec` -- for updating use case scenarios and business rules
- `inspect-spec` -- for the repeat spec review after remediation
- `handoff` -- for the subsequent phase boundary crossing after clean review
- `retrospective` -- for the token-usage analysis at next phase end
