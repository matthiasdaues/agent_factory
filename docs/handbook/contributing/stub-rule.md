---
title: Add a chapter stub and fill it later
type: how-to
status: implemented
order: 20
description: Write a stub page for a chapter that has no content yet, and turn it into a full page.
---

# Add a chapter stub and fill it later

A stub holds a place for a page that does not exist yet. The chapter stays visible in the handbook while it is empty.

## Write a stub

1. Create the file in the chapter folder, for example `docs/handbook/release/sources.md`.
2. Set `status: stub` in the frontmatter, together with `title` and `type`.
3. Write the stub as the proposal's [§ Page format](../../proposals/factory-handbooks.md#page-format) defines it.
4. Run `packages/factory/scripts/handbook-index`.

A stub stays out of the generated page lists. A chapter whose `index.md` exists appears in the top-level list, even when it holds only stubs.

## Fill a stub

1. Fill the stub as the proposal's [§ Page format](../../proposals/factory-handbooks.md#page-format) defines it.
2. Write the page for its `type`, as [the page format](page-format.md) describes.
3. Set `status: implemented`.
4. Run `packages/factory/scripts/handbook-index`. The page joins the list.
