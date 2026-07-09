---
name: capture-vision
description: Capture a project vision through structured interview.
category: requirements
disable-model-invocation: true
---

# Capture Vision

Interview the user to capture their project idea with enough structure for meaningful clarification to follow.

## Step 1 — Elicit the six facets

Ask about each. Accept partial answers — gaps feed `clarify-requirements`.

- **Problem**: the problem to solve
- **Target audience**: who will use it
- **Desired outcome**: what success looks like
- **Constraints**: budget, timeline, tech stack, platform
- **Boundaries**: what the project is _not_ — explicit scope fences
- **Inspiration**: similar tools or approaches the user has seen

Don't move on until every facet has a response, even "unknown."

**Completion**: all six facets have a response (including explicit "unknown").

## Step 2 — Mirror and surface gaps

Summarise the vision back in your own words. Below it, list every gap, ambiguity, or assumption you noticed — one bullet each.

Ask: _"Does this match your intent? Anything I misread?"_

**Completion**: the user confirms the summary or corrects it, and acknowledges the gap list.

## Output

No files. The vision and gap list live in conversation context — they feed directly into `clarify-requirements` or `write-prd`.
