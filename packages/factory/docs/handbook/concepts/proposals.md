---
title: Proposals
type: concept
status: implemented
order: 60
description: The design origin of a feature, from draft to accepted, and the agent that reviews it.
---

# Proposals

A feature starts as a proposal. The proposal is the brief that opens a feature-addition run, and the planning agent turns it into a backlog. Proposals live in your repository's `docs/proposals/`, one Markdown file per feature, written to the [proposal template](../../../rulebooks/templates/proposal.md).

The frontmatter of a proposal is versioned. It records the lifecycle, the impact, the governance, and dated forecasts of active human review hours and normalized AI tokens. A forecast stays separate from the actuals and from the provider's bill. The actuals are only appended to. The body records the summary, the motivation, the design, the split into what is in scope and what is deferred, the open questions, and the completion criteria.

A proposal moves through the states `draft`, `open`, and `accepted`. [feature-addition.md](../../../playbooks/feature-addition.md) describes the lifecycle and the checks that route the work.

> Rule summary: **MUST** clarify or grill a feature proposal in place. A decision-complete interview may move it from `draft` to `open`, but only stakeholder approval moves it to `accepted`. **MUST** enter specification, architecture, or planning work from an `accepted` proposal.
> Source: [rules.md § Proposals](../../../rulebooks/rules.md#proposals)

> Rule summary: A material change after acceptance returns the proposal to `open` for reacceptance.
> Source: [proposal template § Feature Request](../../../rulebooks/templates/proposal.md#feature-request-)

A proposal is where a design comes from. It is not an artifact that agents read at run time.

> Rule summary: **MUST NOT** reference a `docs/proposals/*` file in a shipped agent's `inputs:`.
> Source: [rules.md § Proposals](../../../rulebooks/rules.md#proposals)

The `draft-proposal` skill turns an explored idea into a proposal file. It runs in the current session with the stakeholder present. It fills the template from the conversation, tests the result with `grilling`, and sets `status: open` only when the proposal is complete.

The `proposal-review-agent` then reviews the open proposal in a separate session. It advises on a draft and attacks an open proposal. It runs eight checks: testable criteria, a sharp scope, a design that splits into stories, a consistent impact, existing boundaries, real questions, a justified timing, and a plausible estimate.
