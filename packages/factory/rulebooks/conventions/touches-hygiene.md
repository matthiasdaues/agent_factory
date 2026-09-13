# Touches Hygiene

Rules for populating the `touches` frontmatter field in backlog stories.

The planning agent derives the list from Affected Paths by taking the directory
prefix of each file, de-duplicating parents, and removing any entry that is a
prefix of another. Each entry must resolve to an existing directory or one
created by a story in `deps`.

- Never list both a parent and its child — the parent already covers it.
- A broad prefix like `packages/server/` forces the dispatcher to serialize
  every story that touches any server file, defeating overlap detection.
- Collapse sibling directories only when every sibling is touched.
- Speculative paths for modules that do not exist yet are not permitted — use
  the existing parent directory instead.
