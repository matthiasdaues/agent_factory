---
title: Quote a rule in a page
type: how-to
status: implemented
order: 30
description: Copy a rule from a rulebook into a handbook page as a rule summary with a source line.
---

# Quote a rule in a page

A rule has one home, a rulebook under `packages/factory/rulebooks/`. A handbook page that needs the rule shows a summary and links to the home, so the page never becomes a second source of the rule.

1. Find the section of the rulebook that states the rule.
2. Write a `> Rule summary:` line with the rule in your own words.
3. Write a `> Source:` line directly below it, with a link to that section.
4. Run `packages/factory/scripts/handbook-lint`.

This example quotes the rule about markdown formatting:

```markdown
> Rule summary: **MUST** run `.agent-factory/factory/scripts/mdformat --number <path>` immediately after writing any markdown file.
> Source: [rules.md § Markdown formatting](../../../packages/factory/rulebooks/rules.md#markdown-formatting)
```

When no rulebook holds the rule, write the fact as an explanation and link to the page that records it. Do not write the fact as a rule summary.
