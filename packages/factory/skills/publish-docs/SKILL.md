---
name: publish-docs
description: Publish a project's arc42 documentation as one checked PDF with vector diagrams. Use when someone needs the architecture outside the repository, or asks for a PDF of the docs.
category: architecture
---

# Publish Docs

Run `.agent-factory/factory/scripts/publish-docs pdf` in the project root. The
command writes `docs/dist/<project>-architecture.pdf` and exits 0, or it writes
no PDF and prints one `FAIL <check>: <evidence>` line per failed check.

Read [factory-voice.md](../../rulebooks/conventions/factory-voice.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates and clears the final pass.

## Inputs the project owns

- `docs/publish-docs.yaml` lists what is published, in order: `title`,
  `chapters` (paths or globs relative to `docs/`), and an optional `appendix`
  with `title` and `documents`. Without it the command exits 2 and prints a
  starter manifest. Show the starter to the user and ask which documents
  outside `arc42/` and `adr/` belong in it before saving it.
- `docs/publish-docs.css` is optional. It loads after the factory style, so
  any rule in it overrides the default: 10 pt body type, dotted table rules.
  Avoid CSS sibling selectors such as `tr + tr`; paged.js rewrites them and
  they stop matching. Use `:not(:first-child)` instead.
- Every listed document starts with a top-level `# ` heading. A document
  without one stops the run, because it would vanish from the contents.
- The Structurizr model is `docs/spec/architecture.dsl`. Its themes live in
  `docs/assets/themes/`. Without the DSL the command exits 2 and names
  `docs/spec/architecture.dsl`.
- Where the manifest selects `arc42/12_glossary.md`, by name or by glob, the
  PDF shows `docs/spec/glossary.md` when that file exists. The manifest needs
  no change.

## What the command guarantees

- The sources under `docs/` never change. Only `docs/dist/` is written, and
  the command adds it to `.gitignore` when it is missing.
- Every run validates `docs/spec/architecture.dsl` and exports its views
  again, so the PDF never shows a stale diagram.
- A diagram that fails to render, a Quarkdown compile error, a dead internal
  link or a diagram printed as a bitmap fails the run. Do not work around a
  failed check; fix the source it names and run again.
- The title page names the commit, the branch and the UTC build time. It
  says "with uncommitted changes in docs/" when the working tree is dirty.

## Exit codes

| Code | Meaning                                                                                                                 |
| ---- | ----------------------------------------------------------------------------------------------------------------------- |
| 0    | PDF written.                                                                                                            |
| 1    | A check failed. Read the `FAIL` lines; the build directory stays at `.current-work/publish-docs/build/` for inspection. |
| 2    | A precondition failed: Docker, `docs/`, the manifest, a document, or `docs/spec/architecture.dsl`.                      |

The first run builds the render image, which takes a few minutes.
`PUBLISH_DOCS_IMAGE` selects another image.
