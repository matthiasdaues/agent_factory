---
title: Check the pages with handbook-lint
type: how-to
status: implemented
order: 40
description: Run handbook-lint to find page errors before the commit hook does.
---

# Check the pages with handbook-lint

The script `handbook-lint` checks both handbooks and writes nothing.

## Run it

From the repository root:

```bash
packages/factory/scripts/handbook-lint
```

The commit hook of this repository runs the same script on every commit.

## What it reports

It prints one line per failure and exits with 1. It reports:

- a page without `title`, `type`, or `status`, or with a value that [the page format](page-format.md) does not allow;
- a folder that holds pages but no `index.md`;
- an `index.md` without its marker pair;
- two implemented pages of one chapter with the same `title`;
- a page list that differs from what `handbook-index` writes.

Fix a stale list by running [handbook-index](handbook-index.md). The script checks no link. Run `packages/factory/scripts/link-check` on the pages for that.
