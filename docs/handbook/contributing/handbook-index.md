---
title: Update the page lists with handbook-index
type: how-to
status: implemented
order: 30
description: Run handbook-index after you add, change, or remove a page.
---

# Update the page lists with handbook-index

Write the introduction to a chapter in its `index.md`. The generator owns the page list between these two markers:

```markdown
<!-- handbook-index:start -->
<!-- handbook-index:end -->
```

Put your prose above the start marker or below the end marker. The generator leaves text outside the markers unchanged.

## Regenerate the lists

After adding, changing, or removing a page, run this command from the repository root:

```bash
packages/factory/scripts/handbook-index
```

Review the diff and include the updated `index.md` files in the same commit as the page changes.

## How the lists are built

The generator reads the [frontmatter](page-format.md) of every Markdown page in `packages/factory/docs/handbook/` and `docs/handbook/`, including each `index.md`.

- A chapter index groups its implemented pages under **Tutorials**, **Concepts**, **How-to guides**, **Reference**, and **Learning**, in that order. Within each group, pages sort by `order`, then `title`, then file path. An omitted `order` counts as 100. Each link uses the page title and shows the description if one is present.
- A handbook's top-level index links to every chapter with an `index.md`, including chapters whose content is all stubs. It sorts chapters by their index's `order`, then `title`, then chapter path.
- Pages marked `status: stub` stay out of chapter lists. Set the status to `implemented` when the page is ready, then regenerate.

## Check the lists

Run `packages/factory/scripts/handbook-index --check` to see which lists are stale. Check mode writes nothing. The repository's pre-commit hook runs the same comparison through [handbook-lint](handbook-lint.md) on every commit, including one that only deletes a page. A stale list blocks the commit.

If any page has invalid frontmatter or any index has broken markers, generation stops before writing either handbook. Fix the file named in the error and rerun the command. Each index needs exactly one start marker followed by exactly one end marker. Add or repair the markers by hand.

[Handbook validation rules](../../spec/validation-rules.md#factory-handbooks-handbook-index-handbook-lint-br-140br-152) define the page metadata and generation contract.
