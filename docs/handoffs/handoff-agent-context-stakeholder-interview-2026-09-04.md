# Handoff: Agent Context — Stakeholder Interview Preparation

Date: 2026-09-04
Feature: agent-context (two-layer YAML routing with two-mode lifecycle)
Playbook: feature-addition, Phase 4 (held at ST-0199)
Branch: `feature/agent-context`
Tip: `c7dba03e022a06e6745add376704852d13cb03b5`
Base: `dev` at `060c10b` (includes testing strategy reframe)
Ahead of dev: 27 commits (implementation only; dev has moved independently)
Tests: 287 passing on feature branch

## What is done

All 9 implementation stories (ST-0190 through ST-0198) dispatched, tested, and merged into `feature/agent-context`. Dispatch ledger at `.current-work/feature/agent-context/dispatch-ledger.yaml` records every story as `status: done`.

Key artifacts built:

- YAML templates for stack, workflow, governance, reading-guides under `factory/rulebooks/templates/`
- `factory/scripts/context-lint` — format detection chain, legacy validation, CX-FORMAT
- `factory/skills/capture-context/SKILL.md` v1.1.0 — brownfield onboarding mode
- `factory/skills/update-context/SKILL.md` — mode-aware writes, transition logic
- All agents, skills, and playbooks updated from hardcoded `docs/charter/` to `docs/agent-context/` with format-detection fallback

## What is held

**ST-0199 — Stakeholder grilling session.** This story requires a live interview with the project stakeholder. It was explicitly excluded from the automated dispatch run.

**ST-0200** depends on ST-0199 and remains blocked.

## What changed on dev since dispatch

Two commits on `dev` after the dispatch run, both relevant to the interview:

1. `ebfc14d` — Testing strategy reframed around dual-purpose model:

   - **Agent-adversary detection** (catch what agents get wrong) and **team assurance** (give the team confidence) as the two test-suite purposes
   - Three-layer model: base (structural gates), middle (contract tests), top (behavioral verification)
   - Factory backs down when team already has linting/formatting
   - Developer-agent updated to fill contract-test gaps and write smoke tests
   - New admit-a-test criterion: catches a semantic change no linter can see

2. `060c10b` — Prose edit pass on the above for clarity

These changes are on `dev` and are not yet on the feature branch. They inform the interview but do not block it.

## Interview context

The stakeholder interview (ST-0199) should cover at minimum:

1. **Agent-context design validation.** Does the two-layer YAML structure (stack/workflow/governance + reading-guides) match how the stakeholder thinks about project context? Are there concerns or concepts missing?

2. **Mode lifecycle.** Primary mode (inline values) → index mode (name+source pointers). Does the transition trigger make sense? Is the deferred-field mechanism clear?

3. **Testing strategy alignment.** The reframed testing strategy introduces the dual-purpose model and three-layer band structure. Does the stakeholder agree with the framing? Are there project-specific risk areas the strategy should call out?

4. **Brownfield onboarding.** The capture-context skill now has a `--init --scan` mode for existing projects. Does the discovery-scan approach match the stakeholder's expectations for onboarding?

5. **Format-detection chain.** Every factory consumer now resolves context paths through a three-step chain (agent-context YAML → legacy YAML charter → legacy markdown charter). Is backward compatibility handled as the stakeholder expects?

## Suggested skills

- `grilling` — run the stakeholder interview for ST-0199
- `handoff` — read this document to pick up context
- `validate` — run lints on the feature branch before or after the interview
- `run-step` — resume the feature-addition playbook after the interview

## Files to read before starting

- `backlog/ST-0199.md` — the story itself
- `docs/proposals/yaml-charter-lifecycle.md` — the originating proposal
- `docs/spec/agent-context.feature` — the behavioral spec
- `factory/rulebooks/conventions/testing-strategy.md` — the reframed testing strategy (on dev)
- `.current-work/feature/agent-context/dispatch-ledger.yaml` — dispatch completion record

## Note on agent prose edit

An agent prose edit pass across all 17 agent files is in progress on `dev` (two forks running). Those edits are independent of the stakeholder interview and will be committed separately.
