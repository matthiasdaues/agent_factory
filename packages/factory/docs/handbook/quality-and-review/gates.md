---
title: Gates
type: concept
status: implemented
order: 10
description: What a gate checks, when the structural gates and the semantic gates run, and how a story's gates are picked.
---

# Gates

A reviewer agent's time is expensive, so a cheap check runs first. A gate is a deterministic script that catches a provable defect before a reviewer agent spends time on it: a broken cross-reference, a missing required section, or an inconsistent ID. No LLM judges anything in a gate, so a gate is cheap, gives the same result every time, and reports no false positives.

The gate scripts are stdlib-only Python, so you install nothing to run them. [Gate scripts](gate-scripts.md) lists each gate and its command.

## Structural gates

Each structural gate fires at the end of one kind of work: `spec-lint` after specification work, `arch-lint` after architecture work, `backlog-lint` after planning. `concern-lint` fires when `agent-context.md` changes, and `matrix-lint` when `.agent-factory/config/model.conf` changes. When you drive each agent by hand, one session at a time, the reviewer agent runs its gate as its first step. You can run any gate yourself too.

## Semantic gates

Four semantic gates fire between a developer's commit and the merge of the story branch. The implementation agent's gate-check step runs them. `premerge-check` refuses the merge when a gate that applies to the story has no passing result.

> Rule summary: **MUST** run `premerge-check` before merging a branch; a non-zero exit blocks the merge until investigated.
> Source: [rules.md § Branching](../../../rulebooks/rules.md#branching)

Two of the four, `crap-score` and `mutation-testing`, are test guardrails. The planning agent fills each story's `quality-gates` field from the enabled entries of the `gates` section of `docs/testing.yaml`.

> Rule summary: A test guardrail runs only when an enabled entry of the `gates` section of `docs/testing.yaml` or the story's `quality-gates` field names it. No default picks a gate, and `docs/charter/house-rules.md` is not a source of gates.
> Source: [story-frontmatter-fields.md § quality-gates](../../../rulebooks/references/story-frontmatter-fields.md#quality-gates-filled-by-planner)

When neither source names a built-in gate, `premerge-check` runs none. It prints one line that names each built-in gate without an entry and the skill that sets it up: `setup-crap-score` for `crap-score`, and `mutation-testing` for `mutation-testing`.

`dispatch` counts the attempts of the gate-check step, as [Attempts and escalation](../../../agents/implementation-agent.md#attempts-and-escalation) in the implementation agent's definition describes. A story gets `gates.attempts` attempts on its tier, and then `gates.attempts_escalated` attempts on the next tier. Both values come from `docs/testing.yaml` and default to `3`. `gates.attempts_escalated: 0` turns the escalation off.
