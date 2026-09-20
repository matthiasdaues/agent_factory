# Phase Handoff

## Boundary

Outgoing phase: requirements
Incoming phase: review
Boundary: requirements -> review

## Repository state

Checkout: /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/local-usage-processing-and-analysis
Branch: feature/local-usage-processing-and-analysis
HEAD: 1a7a27d833b4037c4a2612fa1eb97465c90835c4
Upstream: none
Upstream SHA: none
Ahead: 0
Behind: 0
Working tree: no tracked modifications; untracked `docs/handoffs/handoff-local-usage-processing-and-analysis-requirements-remediation-repeat.md`, `docs/handoffs/handoff-local-usage-processing-and-analysis-requirements-remediation.md`, `docs/handoffs/handoff-local-usage-processing-and-analysis-requirements.md`, `docs/handoffs/handoff-local-usage-processing-and-analysis-spec-review.md`, and local `factory` convenience symlink only
Retained work: `dev` is at 7e88a413264bcc2de5540b02888a217ccabe6eed with unrelated user changes; `feature/test-design-layer-redistribution` remains at 4926554398098019550f5e466f9d21c412cf24dc

## Decisions and open items

Decisions: The obsolete live `charter-lint` interface contract was removed; `concern-lint`, `docs/agent-context.md`, and `docs/testing.yaml` are now the only live context and test-configuration contracts. The usage-record contract, producer invocation, specified fixture contract, and accounting registry require the exact CLI values `claude-code`, `copilot`, `codex`, and `pi`; implementation fixtures do not exist yet. Before latest-snapshot selection, all evidence for one `(cli, session_id, run_id)` key must carry one invariant `parent_run_id`, treating null as a value. Disagreement classifies every snapshot for that key as `USAGE_ANCESTRY_PARENT_CONFLICT`; no snapshot establishes or overrides the parent. LU-05 owns this preflight contract. The proposal now requires deterministic coverage for that conflict plus the five rooted-tree failures: six exact ancestry codes total. The entity model requires every logical run to have exactly one latest-run snapshot. These remedies are committed at 1a7a27d833b4037c4a2612fa1eb97465c90835c4.
Open items: [SPEC-0021](../findings/SPEC-0021.md) and [SPEC-0022](../findings/SPEC-0022.md) remain open pending independent review. [SPEC-0015](../findings/SPEC-0015.md), [SPEC-0016](../findings/SPEC-0016.md), [SPEC-0017](../findings/SPEC-0017.md), [SPEC-0018](../findings/SPEC-0018.md), [SPEC-0019](../findings/SPEC-0019.md), and [SPEC-0020](../findings/SPEC-0020.md) are resolved. Architecture has not started.

## Artifacts

- docs/handoffs/handoff-local-usage-processing-and-analysis-requirements-remediation-repeat.md
- docs/reviews/spec-review-2026-09-13-repeat.md
- docs/findings/SPEC-0015.md
- docs/findings/SPEC-0016.md
- docs/findings/SPEC-0017.md
- docs/findings/SPEC-0018.md
- docs/findings/SPEC-0019.md
- docs/findings/SPEC-0020.md
- docs/findings/SPEC-0021.md
- docs/findings/SPEC-0022.md
- docs/proposals/usage-processing-and-storage.md
- docs/spec/agent-context.feature
- docs/spec/local-usage-processing-and-analysis.feature
- docs/spec/local-usage-processing-and-analysis-gaps.md
- docs/spec/local-usage-processing-and-analysis-qa-strategy.md
- docs/spec/prd.md
- docs/spec/scope-map.md
- docs/spec/test-design.feature
- docs/spec/test-gate-presence.feature
- docs/spec/test-design-qa-strategy.md
- docs/spec/supplementary_specs/entity-model.md
- docs/spec/supplementary_specs/interface-contracts.md
- docs/spec/supplementary_specs/validation-rules.md
- docs/spec/todos.md

## Gate and verification evidence

Gates: `.agent-factory/factory/scripts/handoff-lint docs/handoffs/handoff-local-usage-processing-and-analysis-requirements-remediation-repeat.md --repo-root .` passes. `.agent-factory/factory/scripts/spec-lint --spec-dir docs/spec` passes with 0 errors, 0 warnings, and 27 pre-existing informational notices across 18 files. `.agent-factory/factory/scripts/statemachine-lint docs/spec/supplementary_specs/state-machines.md` passes with 0 errors, 0 warnings, and 0 information findings. Changed-artifact `.agent-factory/factory/scripts/link-check` passes. `git diff --check` passes. Commit hooks repeated mdformat, link-check, spec-lint, Mermaid lint, and statemachine-lint successfully.
Verification: the proposal's operational-preflight proof and completion criterion require all six ancestry codes, including `USAGE_ANCESTRY_PARENT_CONFLICT`. The entity diagram and prose both require exactly one latest snapshot per logical run. Requirements changed no finding status.

## Next action

Start a fresh specification-review-agent session. Read this handoff first, verify its Git and working-tree claims, rerun deterministic `spec-lint`, verify [SPEC-0021](../findings/SPEC-0021.md) and [SPEC-0022](../findings/SPEC-0022.md) individually, recheck the previously resolved findings, and perform a fresh semantic inspection. Update finding statuses only from evidence and publish the final disposition. Do not enter Architecture unless the review passes.

## Semantic review

Reviewer: pending independent semantic reviewer
Status: pending
Evidence: pending comparison of this handoff with the committed remediation, open findings, changed specification artifacts, gate results, repository state, and next action
