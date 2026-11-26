---
title: Update the page lists with handbook-index
type: how-to
status: implemented
order: 30
description: Run handbook-index after you add, change, or remove a page.
---

# Update the page lists with handbook-index

Every `index.md` holds a page list between two markers:

```markdown
<!-- handbook-index:start -->
<!-- handbook-index:end -->
```

The script `handbook-index` writes that list. Write the text of the chapter above the markers or below them. The script leaves it alone.

## Run it

From the repository root:

```bash
packages/factory/scripts/handbook-index
```

The script reads the frontmatter of every page in both handbooks. It groups the pages of a chapter by `type`, sorts them by `order` and then by `title`, and leaves out stubs. The top-level `index.md` lists each chapter that has an `index.md`.

To see which lists are out of date without writing them, add `--check`. The exit code is 1 when a list differs.

## When it refuses

The script writes nothing and exits with 1 when a page has a wrong frontmatter field, or when an `index.md` has no marker pair or a broken one. Add the two marker lines by hand. The script does not add them.
