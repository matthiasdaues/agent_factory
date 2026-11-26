---
title: Quote a rule in a page
type: how-to
status: implemented
order: 30
description: Copy a rule from a rulebook into a handbook page as a rule summary with a source line.
---

# Quote a rule in a page

[BR-149](../../spec/validation-rules.md) defines where a binding rule lives and how a page repeats it. `handbook-lint` does not check rule summaries, so the code review checks them.

1. Find the section of the rulebook that states the rule.
2. Write a `> Rule summary:` line with the rule in your own words.
3. Write a `> Source:` line directly below it, with a link to that section.
4. Run `packages/factory/scripts/handbook-lint`.

This example quotes the rule about markdown formatting:

```markdown
> Rule summary: **MUST** run `.agent-factory/factory/scripts/mdformat --number <path>` immediately after writing any markdown file.
> Source: [rules.md § Markdown formatting](../../../packages/factory/rulebooks/rules.md#markdown-formatting)
```

A rule without a rulebook home goes to its owner as a spec-feedback row before a page quotes it.
