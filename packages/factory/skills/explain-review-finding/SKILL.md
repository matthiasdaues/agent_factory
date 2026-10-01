---
name: explain-review-finding
description: When the user asks what a review finding, bug report, failing test, or architecture concern means, explain it to a newcomer, starting with a short chain of cause and effect.
category: quality
---

# Explain a Review Finding

Read [factory-voice.md](../../rulebooks/conventions/factory-voice.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates and clears the final pass.

Turn an abstract technical finding into a short conversation that builds an accurate mental model.

## Aim

Help the user identify the first point at which information, control, or an assumption is lost or changed. Do not begin with framework jargon, a solution pattern, or a long list of files.

## Inputs

The skill reads one of these:

- a finding file, `docs/findings/<TAG>-NNNN.md`
- a review report, `docs/reviews/*.md`
- a PR comment that the user pastes
- the output of a failing test

## Workflow

1. Inspect the finding and the smallest relevant code or contract context. Verify claims; do not infer runtime behaviour from a review sentence alone.

2. Build a causal dependency tree with 3–6 nodes:

   ```text
   source or input
           ↓
   transformation or decision
           ↓
   first layer where something is lost, changed, or undocumented
           ↓
   affected consumer
           ↓
   user-visible or maintenance consequence
   ```

3. Explain the tree in plain language. Lead with the outcome: what is wrong for a user, caller, or future developer.

4. Give one concrete request, value, or code-path example if it clarifies the issue.

5. Only then explain the smallest appropriate fix and the layer where it belongs.

6. Answer follow-up questions one step at a time. Keep each answer short unless the user asks for depth.

## Explanation order

Use this order whenever it fits:

1. **Actual behaviour** — what the system does now.
2. **Expected contract or intent** — what callers, documentation, or the design assume.
3. **Gap** — where the two diverge.
4. **Consequence** — who receives incomplete, wrong, or unrepresentable information.
5. **Cause** — why the relevant framework or code path produces the gap.
6. **Fix** — the smallest layer that can restore the contract.

## Adapt to the finding type

- For data flow, validation, API, event, cache, or documentation drift: use the dependency tree.
- For a local readability or typing concern, a dependency tree would add noise. Explain it in four steps instead: the purpose of the code, the current code, the maintenance risk, and the small improvement.
- For a question in a review rather than a defect: distinguish facts already verified from the product or architectural decision that still needs an owner.

## Communication rules

- Match the user's language and their apparent technical level.
- Define terms as the [factory voice](../../rulebooks/conventions/factory-voice.md) requires. For example, describe OpenAPI as the API contract used to generate frontend types before mentioning schemas or unions.
- Separate two similar concepts when they arise from different layers, such as technical input validation versus business-rule validation.
- State whether the current behaviour is intentionally desirable, accidentally wrong, or correct but undocumented.
- Do not imply that a code change is authorized merely because you explained it.

## Compact response shape

Start with two or three sentences. Use a small tree only when it makes the relationship clearer. End with the next natural question or the proposed smallest fix, not a broad implementation plan.

## Example

For an API contract finding, explain:

```text
Backend emits a custom error response
        ↓
Global handler maps it to HTTP JSON
        ↓
Route does not declare that response
        ↓
OpenAPI omits it
        ↓
Generated frontend types cannot represent it
```

Then say: the backend works at runtime, but the published contract is incomplete; declare the response on the route and regenerate the contract.
