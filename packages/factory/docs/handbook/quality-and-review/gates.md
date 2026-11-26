---
title: Gates
type: concept
status: implemented
order: 10
description: What a gate checks, when the structural gates and the semantic gates run, and how a story's gates are picked.
---

# Gates

A gate is an automated check with defined rules. It can flag a broken cross-reference, a missing required section, or an inconsistent ID. A failed gate reports which rule the work needs to satisfy before it can proceed.

The gate scripts are stdlib-only Python, so you install nothing to run them. [Gate scripts](gate-scripts.md) lists each gate and its command.

## Structural gates

Each structural gate fires at the end of one kind of work: `spec-lint` after specification work, `arch-lint` after architecture work, `backlog-lint` after planning. `concern-lint` fires when `agent-context.md` changes, and `matrix-lint` when `.agent-factory/config/model.conf` changes. When you drive each agent by hand, one session at a time, the reviewer agent runs its gate as its first step. You can run any gate yourself too.

```text
Specification ready for review
              |
              v
     spec-lint checks structure
              |
              +-- fails --> Fix the reported rule and rerun
              |
              +-- passes -> Reviewer reads for meaning
```

## Semantic gates

For project-specific setup, see [Fit the quality gates to the code](../getting-started/fitting.md#fit-the-quality-gates-to-the-code).

After independent story review clears the blocking findings, the implementation agent runs the applicable gates. `premerge-check` refuses the merge when a required gate has no passing result.

- `dependency-check` runs after every story.
- `test-design-verify` runs when the story has a Test Design or Prior Tests section.
- `crap-score` and `mutation-testing` run when selected by the story or project configuration.

> Rule summary: **MUST** run `premerge-check` before merging a branch; a non-zero exit blocks the merge until investigated.
> Source: [rules.md § Branching](../../../rulebooks/rules.md#branching)

Two of the four, `crap-score` and `mutation-testing`, are test guardrails. Which of them runs for a story is set before the story starts, so the developer never picks a gate.

> Rule summary: The planning agent fills each story's `quality-gates` field from the enabled entries of the `gates` section of `docs/testing.yaml`. A test guardrail runs only when such an entry or the field names it. No default picks a gate, and `docs/charter/house-rules.md` is not a source of gates.
> Source: [story-frontmatter-fields.md § quality-gates](../../../rulebooks/references/story-frontmatter-fields.md#quality-gates-filled-by-planner)

When neither source names a test guardrail, `premerge-check` skips that guardrail. It prints one line that names each built-in gate without an entry and the skill that sets it up: `setup-crap-score` for `crap-score`, and `mutation-testing` for `mutation-testing`.

[implementation-agent.md § Attempts and escalation](../../../agents/implementation-agent.md#attempts-and-escalation) describes what happens after a gate fails.
