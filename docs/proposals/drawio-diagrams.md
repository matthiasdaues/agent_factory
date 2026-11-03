---
schema_version: 2
scope: global
title: Draw.io Diagrams
status: draft
owner: agent-factory
created: 2026-11-02
updated: 2026-11-02
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: false
  boundaries:
    - packages/factory/rulebooks/conventions/skill-authoring.md
    - packages/factory/scripts/structurizr
    - packages/factory/docker/publish-docs
    - docs/assets
    - packages/factory/INDEX.yaml

governance:
  assurance: routine
  risk_domains:
    - operations

estimate:
  as_of: 2026-11-02
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Draw.io Diagrams

## Primer

The primer is written last, by the `write-primer` skill, once the design is settled.

## Summary

The Factory gains a skill set for editable draw.io diagrams. An agent writes only the structure of a diagram: its shapes, its containers, and its edges. The draw.io layout engine places them, and the agent renders the result and looks at it before it hands the diagram over. Each diagram is one `.drawio.svg` file in `docs/assets/diagrams/`, which draw.io opens as a diagram and Markdown shows as an image. The first release covers flow and dependency diagrams that a Structurizr view or a Mermaid block cannot hold, such as the [project truth map](../../poc/workflow/project-truth-map.drawio).

## Motivation

Agents draw diagrams the Factory has no tool for. Structurizr covers the C4 views of `architecture.dsl`, and Mermaid covers the small diagrams inside arc42 chapters. A workflow map, an artifact dependency map, or a board for a stakeholder needs a format people can edit and rearrange. draw.io is that format.

Today an agent writes draw.io XML by computing every coordinate by hand. On 2026-11-02 that produced two layouts the stakeholder rejected as "horribly bad". The same diagram, written as structure only and laid out by draw.io's ELK engine, was accepted as "much better" (DEC-01). The difference came from the method, not from effort.

The Factory has no material that teaches this. It has no rule for draw.io XML, no wrapper for the draw.io command line, and no step that makes an agent look at its own diagram. The working method exists only in one session's notes.

## Core Principles

- **Structure, not coordinates.** The agent writes what is connected to what. The layout engine decides where it goes.
- **Look before handover.** No diagram reaches the stakeholder before the agent has rendered it and checked the picture.
- **Fix the model, not the picture.** When the layout looks wrong, the agent changes the edges, the containers, or their direction, and lays the diagram out again.
- **Zero install.** Like `structurizr`, the tool runs in a container, so a project needs only Docker.

## Design

### The skills

The set has two skills, because the check serves every diagram and the authoring rules serve only diagrams an agent writes (DEC-05).

- **`drawio-diagram`** writes a diagram. Its procedure: write the structure, lay it out, review it, and fix the model. It references its rules instead of inlining them, as `skill-authoring.md` requires. Its last step is always `review-diagram`.
- **`review-diagram`** checks a finished diagram, whoever drew it. It renders each page with `scripts/drawio render`, looks at the picture, and reports overlaps, crossing edges, edges that leave their container, and missing labels.

`drawio-diagram` runs rounds of layout and review. It stops when a round fixes no defect, and after five rounds at most (DEC-06). Then it shows the diagram to the stakeholder and names every defect it could not fix.

The authoring rules live in a new reference file, `packages/factory/rulebooks/references/drawio-authoring.md`:

- **Containers are real.** A group is a `swimlane` container, its members name it as `parent`, and their coordinates are relative to it.
- **Edges belong to the innermost container** that holds both ends, otherwise to the root.
- **No waypoints and no anchors.** The file sets no `exitX`, `entryX`, or edge points. The engine routes the edges.
- **One meaning per line style.** A dashed line means one thing in a diagram, and a legend says what.
- **Layering follows meaning.** A layered layout treats every edge as a constraint. An edge that points against the main direction, such as "checked against", runs in the main direction with its arrowhead at the start.
- **Fan-out collapses.** When one source feeds many nodes of a group, one edge goes to the group.
- **Sizes stay fixed.** The layout runs with `resizeNodes: false` and `useViewStateSizing: false`.
- **Titles and legends come last.** They are added after the layout, so the engine does not place them as loose nodes.

These rules come from the jgraph draw.io guidance and from the session that produced the truth map (DEC-01).

### The wrapper script

A new script, `packages/factory/scripts/drawio`, wraps the draw.io command line in a container, as `scripts/structurizr` does:

| Subcommand | What it does                                                                  |
| ---------- | ----------------------------------------------------------------------------- |
| `layout`   | Runs an ELK layout on a diagram and writes the laid-out `.drawio.svg`.        |
| `export`   | Writes a diagram as `.drawio.svg`, with the whole diagram embedded.           |
| `render`   | Exports one page as SVG and rasterises it to PNG, so an agent can look at it. |

The script runs a Factory-built image, `packages/factory/docker/drawio/`, as `publish-docs` does (DEC-03). The image pins draw.io Desktop 31.3.1, the version whose `--layout` flag was verified on 2026-11-02, and adds xvfb, D-Bus, and CairoSVG. So `render` runs in one container.

The container needs a D-Bus session, a virtual display, an init process, the caller's user ID, and a writable home. Without them, draw.io Desktop hangs or fails. PNG export inside the container fails with "Empty export data", so `render` goes through SVG.

### Where diagrams live

Every diagram is one file, `docs/assets/diagrams/<name>.drawio.svg` (DEC-04). The file is the source and the image at once: draw.io opens it as an editable diagram, and a Markdown document shows it with an ordinary image link. The draw.io command line reads it back for `layout` and `export`. All pages of a diagram stay embedded in the file, and the picture shows one page.

The script exports with `--embed-svg-fonts false`. With font embedding, draw.io adds a PNG copy of every text label, and the truth map grew from 98 KB to 1.28 MB. A viewer without Noto Sans shows the labels in a fallback font.

A generator script that an agent wrote to produce a diagram is working output and is not tracked.

## Scope

**In the first release:**

- The skills `drawio-diagram` and `review-diagram`, and the reference file `drawio-authoring.md`.
- The wrapper script `scripts/drawio` with `layout`, `export`, and `render`.
- The Factory-built image under `packages/factory/docker/drawio/`.
- The folder `docs/assets/diagrams/` and the `.drawio.svg` format.
- Tests for the script's argument handling and its container call.

**Explicitly deferred (do NOT plan stories for these):**

- **Mermaid as the source format.** draw.io imports Mermaid and lays it out, but most of the Factory's diagrams need containers and styles that Mermaid cannot express.
- **The draw.io MCP server.** No CLI the Factory supports shows diagrams inline, so it would add a dependency without a use.
- **Export to Miro.** The board has its own authoring tools.
- **Bausteinsicht.** The C4 workflow from draw.io to JSONC belongs to its own proposal, [bausteinsicht-factory-integration.md](bausteinsicht-factory-integration.md).

## Design Details

- **Rendering.** The PNG comes from the SVG export through CairoSVG. CairoSVG does not draw straight edges whose bounding box has zero width, so a missing straight edge in the PNG is a renderer gap, not a diagram defect. The skill says so, and it checks the edge's label in the SVG instead.

## Open Questions

No question is open. The grilling settled the image, the location and format, the split into two skills, and the stop rule (DEC-03 to DEC-06).

## Completion Criteria

- `packages/factory/skills/drawio-diagram/SKILL.md` exists, carries the voice anchor, references `rulebooks/references/drawio-authoring.md`, ends with `review-diagram`, and states the stop rule: no fixed defect in a round, or five rounds.
- `packages/factory/skills/review-diagram/SKILL.md` exists and checks a diagram that no agent wrote.
- `packages/factory/docker/drawio/` builds an image with draw.io Desktop 31.3.1, xvfb, D-Bus, and CairoSVG.
- `packages/factory/scripts/drawio layout`, `export`, and `render` run against a sample diagram in the container and write their output files.
- `export` writes `docs/assets/diagrams/<name>.drawio.svg` with every page embedded and without embedded fonts, and `layout` and `export` read such a file back.
- `render` produces a PNG for a page of a multi-page file.
- The script's tests pass without Docker, by checking the container call it builds.
- `index-lint --check` and `voice-anchor-lint` pass.

# Appendix

## Decisions

| ID     | Date       | Kind     | Decided by  | Decision                                                                                                                              | Raised by                    |
| ------ | ---------- | -------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| DEC-01 | 2026-11-02 | decision | stakeholder | Diagrams are laid out by draw.io's layout engine from structure only; hand-computed coordinates are rejected.                         | project truth map            |
| DEC-02 | 2026-11-02 | decision | stakeholder | The skill set starts from a proposal; the proposal is written on `dev`, and the implementation runs in a worktree.                    | process question             |
| DEC-03 | 2026-11-02 | decision | stakeholder | The script runs a Factory-built image with draw.io Desktop 31.3.1 and CairoSVG, as `publish-docs` builds its own.                     | open question: image         |
| DEC-04 | 2026-11-02 | decision | stakeholder | Every diagram is one `docs/assets/diagrams/<name>.drawio.svg` file, editable in draw.io and usable as an image in Markdown.           | open question: location      |
| DEC-05 | 2026-11-02 | decision | stakeholder | The set has two skills: `drawio-diagram` writes diagrams, and `review-diagram` checks any diagram.                                    | open question: skill split   |
| DEC-06 | 2026-11-02 | decision | stakeholder | `drawio-diagram` stops when a round fixes no defect, and after five rounds at most, then shows the diagram and its remaining defects. | open question: render rounds |

## Review findings

No review has run yet.

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

No review has run yet.

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
