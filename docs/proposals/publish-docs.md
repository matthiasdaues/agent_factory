---
schema_version: 2
title: Publish arc42 documentation as PDF
status: accepted
owner: Agent Factory maintainers
created: 2026-10-15
updated: 2026-10-16
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: false
  boundaries:
    - packages/factory/scripts/structurizr
    - packages/factory/INDEX.yaml

governance:
  assurance: elevated
  risk_domains:
    - reliability
    - operations

estimate:
  as_of: 2026-10-15
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Publish arc42 documentation as PDF

## Primer

Does not apply: the proposal serves its stakeholder only, who needs no newcomer introduction (DEC-17).

## Summary

The factory gains a `publish-docs` capability. It compiles a project's arc42
chapters, supplementary documents and ADRs into one print-ready PDF in which
every diagram is a vector graphic. It answers a question the factory cannot
answer today: "Can I hand the architecture to someone who has no access to
the repository?" The first release produces a PDF with Quarkdown and nothing
else.

## Motivation

The factory produces arc42 documentation but cannot publish it. The output is
a Structurizr DSL file, prose chapters, ADRs and a folder of exported SVGs.
GitHub renders that set, and nothing else does. Auditors, external reviewers
and people in a meeting without the repository need one self-contained
document.

Nothing in the factory assembles these pieces. The obvious approaches break
in ways nobody notices. If a Mermaid diagram fails to render, the PDF still
builds and shows source code or an error graphic where the diagram belongs.
If the exported SVGs are older than `architecture.dsl`, the PDF shows an
outdated model.

## Core Principles

- **The sources stay as they are.** Every transformation happens in a
  disposable build directory. `docs/` stays valid GitHub Markdown that
  GitHub renders and that `mermaid-lint`, `statemachine-lint` and `spec-lint`
  can parse (DEC-07).
- **A failed render stops the build.** The pipeline checks the rendered
  document before it writes a PDF. Any sign of a failed diagram, a compile
  error or a dead link ends the run with a non-zero exit (DEC-10).
- **Diagrams come from the model.** Each run validates `architecture.dsl` and
  exports its views again before it assembles anything (DEC-09).
- **Docker only.** No tool is installed on the host, as with
  `packages/factory/scripts/structurizr` (DEC-08).

## Design

### Shape

The capability has four parts:

| Part                                            | Role                                                                    |
| ----------------------------------------------- | ----------------------------------------------------------------------- |
| `packages/factory/scripts/publish-docs`         | Bash entry point. Runs the stages, builds and runs the container.       |
| `packages/factory/scripts/_docs_assemble.py`    | Python. Reads the manifest, assembles and rewrites the documents.       |
| `packages/factory/docker/publish-docs/`         | Dockerfile, render script and `publish.css` for the render image.       |
| `packages/factory/skills/publish-docs/SKILL.md` | Tells an agent when to publish, how to call the script, what it checks. |

The developer or an agent runs one command in the project root:

```bash
.agent-factory/factory/scripts/publish-docs pdf
```

The command writes `docs/dist/<project>-architecture.pdf` and exits 0, or it
writes no PDF, names each failed check and exits non-zero.

### The manifest

A project states what goes into its PDF in `docs/publish-docs.yaml`. The
manifest is needed because the documents live in several folders. In the
reference project, the entity model lives under `docs/spec/`, not under
`docs/arc42/`.

```yaml
title: gigainstructions — Architecture
chapters:
  - arc42/01_*.md          # glob entries expand in sorted order
  - arc42/02_*.md
  # ... up to 12
  - spec/supplementary_specs/entity-model.md
appendix:
  title: Architecture decisions
  documents:
    - adr/*.md
```

Paths are relative to `docs/`. Each matched document becomes one top-level
entry in the table of contents, in manifest order. A missing file or a glob
without a match stops the run in Stage 0.

The manifest is required (DEC-11). When `docs/publish-docs.yaml` is missing,
the run exits 2 and prints a starter manifest to standard output. The starter
lists every `arc42/NN_*.md` file and `adr/*.md` as the appendix, so the
developer saves it, adds any document outside these folders, and runs again.

### Pipeline

| Stage       | What happens                                                                                                                                       |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0 Preflight | Docker is present. The manifest, `docs/spec/architecture.dsl` and every listed document exist.                                                     |
| 1 Model     | Copies `docs/arc42/` into the build directory. Runs `structurizr validate`, then `structurizr export-svg` with `STRUCTURIZR_DOCS` set to the copy. |
| 2 Assemble  | Reads the documents in manifest order.                                                                                                             |
| 3 Transform | Applies the rewrite rules below and writes `main.qd`.                                                                                              |
| 4 Render    | Quarkdown compiles `main.qd` to HTML. Chromium loads the HTML over a local HTTP server and waits for Mermaid and paged.js.                         |
| 5 Check     | Runs the render checks below on the live page and on the PDF.                                                                                      |
| 6 Emit      | Moves the PDF to `docs/dist/` only when every check passed.                                                                                        |

Stage 1 never writes into `docs/`. The `structurizr` wrapper places SVGs under
`$STRUCTURIZR_DOCS/assets/images`, so pointing that variable at the build copy
needs no change to the wrapper.

### Rewrite rules (Stage 3)

| Source element                               | Output                                                                                    |
| -------------------------------------------- | ----------------------------------------------------------------------------------------- |
| ```` ```mermaid ```` block                   | Body written to `dN.mmd`. The block becomes `.mermaid` with the body `.read {dN.mmd}`.    |
| Image reference                              | File taken from the Stage 1 export when it is a Structurizr view, otherwise copied as is. |
| Link to a document in the manifest           | Internal anchor to that document's first heading.                                         |
| Link to a Markdown file outside the manifest | Plain text.                                                                               |
| Link to any other repository file            | Inline code with the link text, because a source path is a citation, not navigation.      |
| `[back to index](...)` line                  | Removed.                                                                                  |
| YAML frontmatter                             | Removed. An ADR's `status` becomes a line `**Status:** <value>` under its heading.        |

The `.read` form keeps the diagram text away from Quarkdown's parser.
Quarkdown treats a leading `.` as a function call. Without `.read`, a diagram
line that starts with a dot would change meaning.

Quarkdown derives a heading id from its text and puts `_` in front of an id
that starts with a digit. "5. Building Block View" becomes
`_5-building-block-view`. The anchor rule uses the same scheme, and the dead
anchor check in Stage 5 catches any difference.

`main.qd` sets `.doctype {paged}`, a table of contents, and Quarkdown
numbering `none` for headings, figures and tables, because arc42 chapters
carry their own numbers. It loads `publish.css` with
`.css {.read {publish.css}}`.

### Render checks (Stage 5)

Each check catches a failure that leaves a PDF that still looks plausible.
The probe saw every one of them (DEC-01).

| Check                                                             | Failure it catches                                                                       |
| ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Diagrams with an SVG = Mermaid blocks in the manifest documents   | A diagram that did not render.                                                           |
| No SVG contains "Syntax error"                                    | Mermaid draws an error graphic for a broken diagram, so counting SVGs alone passes.      |
| No uncaught page error                                            | A Mermaid parse error or a script failure.                                               |
| paged.js produced more than 0 pages                               | paged.js stops at a page error, and Chromium still prints an unpaginated PDF.            |
| No `.box.error` element                                           | Quarkdown prints a compile error, such as an unresolved link, into the page and exits 0. |
| Every `href="#…"` has a matching `id`                             | An internal link that points nowhere.                                                    |
| No `href` outside the document                                    | A repository link that slipped through the rewrite.                                      |
| Every image loaded                                                | A missing SVG.                                                                           |
| Raster images in the PDF ≤ PNG and JPEG references in the sources | A diagram that Chromium printed as a bitmap. A CSS filter on an SVG element causes this. |

The raster check counts only rows of type `image` in `pdfimages -list`.
A PNG with transparency adds a second row of type `smask`, which is not a
second picture. Stage 3 counts the PNG and JPEG files it copies into the
build directory, so a photo in a deployment chapter passes and a rasterized
diagram adds one image too many (DEC-15).

### Render image

The image holds Chromium, Node with `playwright-core`, `poppler-utils` for
`pdfimages`, and the Quarkdown
platform zip at a pinned version with its SHA-256 checksum. The Quarkdown zip
ships its own Java runtime. The script builds the image from the factory's
Dockerfile on first use and tags it with the Quarkdown version.
`PUBLISH_DOCS_IMAGE` overrides the image, as `STRUCTURIZR_IMAGE` does for the
`structurizr` wrapper. The container runs with `--user "$(id -u):$(id -g)"`.

### Page style

`publish.css` sets the house style on top of Quarkdown's LaTeX theme
(DEC-06):

- Body type 10 pt.
- A 0.5 pt dotted grey line between table body rows. The theme's solid top,
  header and bottom rules stay.
- `--qd-mermaid-node-filter: none`. The theme gives diagram boxes a drop
  shadow, and Chromium prints filtered elements as bitmaps.

paged.js rewrites CSS sibling selectors such as `tr + tr` into attributes
that never reach table cells. `publish.css` uses `:not(:first-child)` instead.

A project adjusts the style in its own `docs/publish-docs.css`. The file is
optional. When it exists, `main.qd` loads it after `publish.css`, so any rule
in it overrides the factory default, from the font size to the table lines
(DEC-16). The project file follows the same paged.js limit on sibling
selectors. The starter manifest output mentions the file, so a developer
learns that styling is possible.

### Title page

The first page shows the manifest `title` and one provenance line:

> Built from `<40-character SHA>` (branch `<branch>`), `<YYYY-MM-DD HH:MM>` UTC

Stage 3 reads the values with `git rev-parse HEAD`,
`git rev-parse --abbrev-ref HEAD` and `date -u`. The PDF is not committed
(DEC-03), so this line is the only link between a circulating copy and the
repository state it shows (DEC-12). The table of contents follows on the next
page.

When `git status --porcelain -- docs/` lists any file, tracked or untracked,
the line reads:

> Built from `<40-character SHA>` (branch `<branch>`) with uncommitted changes
> in docs/, `<YYYY-MM-DD HH:MM>` UTC

The run still produces the PDF, so a developer can check the layout of a draft
chapter. The mark tells every reader that the copy does not match the commit
exactly (DEC-13). `docs/dist/` is gitignored, so earlier output never counts as
a change.

## Scope

**In the first release:**

- The `publish-docs pdf` command with Stages 0 to 6.
- The manifest `docs/publish-docs.yaml` with glob entries and one appendix.
- The rewrite rules and render checks listed in the Design.
- The render image with pinned Quarkdown and its build on first use.
- `publish.css` with the house style.
- The optional project stylesheet `docs/publish-docs.css`, loaded after
  `publish.css`.
- The `publish-docs` skill and its `INDEX.yaml` entry.
- A test fixture project that exercises every rewrite rule and every render
  check. It embeds one PNG, so the raster check sees a legitimate image.
- The `.gitignore` entry for `docs/dist/` in the consuming project, added by
  the script when it is missing.

**Explicitly deferred (do NOT plan stories for these):**

- HTML or static-site output. The need is a document for people without the
  repository, and a PDF meets it.
- A second render engine. The probe compared Pandoc and Quarkdown, and
  Quarkdown was chosen (DEC-01).
- Wiring `publish-docs` into CI. The command runs without interaction, so a
  workflow can call it later. No project has asked for one.
- Making `arch-lint` check SVG freshness for the whole repository. The
  publish path already exports fresh SVGs; the general check is a separate
  change.
- Publishing change records such as topic folders, the scope map, the gaps
  report or `CONTEXT.md`. They are working artifacts, not reference
  documentation.

## Design Details

- **Build directory.** `.current-work/publish-docs/build/`, emptied at the
  start of each run. A failed run keeps it, so the developer can open
  `index.html` and see the failure.
- **Exit codes.** 0 when the PDF is written. 1 when a check fails. 2 when a
  precondition fails in Stage 0, such as a missing Docker or manifest.
- **Failure report.** Each failed check prints one line with the check name
  and the evidence, for example the error-box text or the dead anchor.
- **Determinism.** Two runs on unchanged inputs give the same page count.
  Byte-identical PDFs are not required, because the PDF carries a creation
  date.
- **Tests.** The rewrite rules are pure functions in `_docs_assemble.py` with
  unit tests that need no Docker. One end-to-end test builds the fixture
  project. It includes a broken Mermaid block and a dead link and expects a
  non-zero exit for each. The end-to-end test declares Docker as an explicit
  precondition: a shared `requires_docker` marker runs `docker info` and skips
  the test with the reason "Docker daemon not available" when the command
  fails. On a machine with a running Docker daemon, the test runs in the
  normal `pytest` call (DEC-14).

## Open Questions

None. Every question raised during drafting is decided and recorded in the
Decisions table.

## Completion Criteria

- `publish-docs pdf` on the fixture project exits 0 and writes the PDF to
  `docs/dist/`.
- The PDF contains every Mermaid diagram of the fixture as a vector graphic:
  `pdfimages -list` reports exactly one row of type `image`, the fixture's
  PNG, and no Mermaid source appears as text.
- Every Structurizr view referenced by the fixture comes from the export of
  the same run. The fixture's committed SVGs differ from the DSL, so a stale
  SVG fails the test.
- The table of contents lists the manifest entries in manifest order, with the
  ADRs under the appendix title.
- No repository path appears as a link. Source-file paths appear as inline
  code. Links to Markdown files outside the manifest appear as plain text.
- No `[back to index]` line and no frontmatter appear. Each ADR shows its
  status.
- `structurizr validate` passes before Stage 3 starts. An invalid DSL stops the
  run before rendering.
- Two runs on unchanged inputs give the same page count.
- The title page shows the full 40-character SHA of `HEAD`, the branch name
  and the UTC build time of the run.
- With an uncommitted change under `docs/` in the fixture, the run exits 0 and
  the provenance line says "with uncommitted changes in docs/". With a clean
  tree, the line does not say it.
- Without `docs/publish-docs.yaml`, the run exits 2, writes no PDF and prints
  a starter manifest that lists the fixture's arc42 chapters and ADRs.
- The fixture with one broken Mermaid block exits non-zero and writes no PDF.
- The fixture with one dead internal link exits non-zero and writes no PDF.
- `git status` shows no change under `docs/` after a run, except the ignored
  `docs/dist/`.
- With a fixture `docs/publish-docs.css` that sets the body type to 12 pt,
  the PDF body text is 12 pt. Without the file, it is 10 pt.
- On the reference project gigainstructions, the run exits 0 and the table of
  contents lists 18 document entries (chapters 1 to 12, the entity model and
  5 ADRs) and the appendix title.

## Guiding Rule

A PDF exists only if every diagram in it rendered from the current sources.

# Appendix

## Decisions

| ID     | Date       | Kind     | Decided by  | Decision                                                                                                                                                                                                                                                                              | Raised by                               |
| ------ | ---------- | -------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| DEC-01 | 2026-10-15 | decision | stakeholder | Quarkdown is the only engine. A probe on four gigainstructions documents produced an error-free PDF with 7 vector Mermaid diagrams and 4 Structurizr views. Pandoc cut the 170-line ER diagram off at the page bottom and needed extra glue for page numbers and code-tag unwrapping. | Brief D3, probe                         |
| DEC-02 | 2026-10-15 | decision | stakeholder | The entity model is in scope for the reference project, because chapter 5 links to it.                                                                                                                                                                                                | Brief, resolved question 1              |
| DEC-03 | 2026-10-15 | decision | stakeholder | The PDF goes to `docs/dist/`, which is gitignored. The PDF is a build artifact.                                                                                                                                                                                                       | Brief, resolved question 2              |
| DEC-04 | 2026-10-15 | decision | stakeholder | ADRs form an appendix after the last chapter, not inline under chapter 9.                                                                                                                                                                                                             | Brief, resolved question 3              |
| DEC-05 | 2026-10-15 | decision | stakeholder | Repository-source links become inline code. Links between published documents become internal anchors.                                                                                                                                                                                | Brief D6                                |
| DEC-06 | 2026-10-15 | decision | stakeholder | House style: 10 pt body type and 0.5 pt dotted lines between table rows.                                                                                                                                                                                                              | Probe review                            |
| DEC-07 | 2026-10-15 | decision | stakeholder | Sources are never changed. Mermaid fences stay valid for GitHub and the three lints that parse them.                                                                                                                                                                                  | Brief D1                                |
| DEC-08 | 2026-10-15 | decision | stakeholder | Docker only, modelled on the `structurizr` wrapper. No official Quarkdown image exists, so the factory builds its own.                                                                                                                                                                | Brief D2, E5                            |
| DEC-09 | 2026-10-15 | decision | stakeholder | Each run validates the DSL and exports the views again.                                                                                                                                                                                                                               | Brief D4, E6                            |
| DEC-10 | 2026-10-15 | decision | stakeholder | Each failed render check stops the build. The check list covers every silent failure the probe observed.                                                                                                                                                                              | Brief D5, probe                         |
| DEC-11 | 2026-10-16 | decision | stakeholder | A required manifest file states what is published and in which order, because the reference project keeps documents outside `docs/arc42/`. A missing manifest exits 2 and prints a starter.                                                                                           | Draft: counts must be derived           |
| DEC-12 | 2026-10-16 | decision | stakeholder | The title page carries a provenance line with the full commit SHA, the branch and the UTC build time.                                                                                                                                                                                 | Open question: provenance               |
| DEC-13 | 2026-10-16 | decision | stakeholder | A run with uncommitted changes under `docs/` still builds the PDF and marks the provenance line.                                                                                                                                                                                      | Open question: uncommitted changes      |
| DEC-14 | 2026-10-16 | decision | stakeholder | The end-to-end test declares Docker as an explicit precondition and is skipped, with the reason named, when no Docker daemon is available.                                                                                                                                            | Open question: Docker in the test suite |
| DEC-15 | 2026-10-16 | decision | stakeholder | The raster check fails only when the PDF holds more raster images than the sources reference as PNG or JPEG files.                                                                                                                                                                    | Grilling: raster images in the sources  |
| DEC-16 | 2026-10-16 | decision | stakeholder | A project can change the PDF style. An optional `docs/publish-docs.css` loads after the factory default and overrides it.                                                                                                                                                             | Stakeholder requirement                 |
| DEC-17 | 2026-10-16 | decision | stakeholder | The proposal is accepted for the stakeholder's own use. The lector passes, the primer and the proposal review are skipped.                                                                                                                                                            | Stakeholder                             |

## Review findings

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
