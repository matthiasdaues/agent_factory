# The Factory Process on Miro

This note records how the Factory's process illustration on the Miro board was built: what it shows, the rules behind the layout and the colours, and how to regenerate or change it. The scripts are in [miro-generator/](miro-generator/).

Board: [agent factory sdlc flow](https://miro.com/app/board/uXjVESrJp_A=/), built on 2026-11-03.

## What Is on the Board

| Piece         | Where                                                             | What it shows                                                                                                       |
| ------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| First version | x 6236 to 7800, next to the user's four hand-drawn cluster shapes | Cluster, phase and step columns, condensed from page 3 of the truth map. Kept for comparison.                       |
| Detailed flow | Frame 2, x 8190 to 13649                                          | 150 steps, gates and decisions; failure lanes; group shapes in three columns; the artifact column with class chips. |
| Lying 8       | x 14500 to 20000                                                  | The ten change phases as a figure eight, Initiation as a lead-in, each phase linked to its section in Frame 2.      |

The source of every step is the current Factory definition in `packages/factory/`: agents, skills, playbooks and scripts. The Planning and Building rows follow page 4 of [project-truth-map.drawio](project-truth-map.drawio). The changes from the accepted core-artifact-ownership proposal are not drawn yet.

## Principles

- **Generic to specific, left to right.** Column 1 holds the cluster, column 2 the phase, column 3 the sub-phase, column 4 the step. The artifacts sit right of the flow.
- **The flow decides the size.** Steps are placed first. Each grouping shape is then sized to the span of the shapes to its right: sub-phase from its steps, phase from its sub-phases, cluster from its phases. Nothing is squeezed into a fixed height.
- **One direction of reading.** The main path runs straight down one spine. Failure paths branch to the right; loops back are dashed and run on the left.
- **Gates are shapes.** Every check is a diamond or a yellow gate box with its outcomes labelled, so a loop is visible as a loop.
- **Gaps are marked, not hidden.** Where the definitions leave a path undefined, a dashed red box names the gap: no proposal-lint script, the premerge-check failure (BUG-0114), no quality gates in manual mode, and no owner for merging a feature branch into `dev`.
- **The board shows the Factory as it is.** Planned changes go in only after they are implemented.

## Layout Rules

All measures are board pixels. The constants live in `layout.py`.

### Columns

| Column               | x                                         | Width                        |
| -------------------- | ----------------------------------------- | ---------------------------- |
| Cluster              | 8240                                      | 469                          |
| Phase                | 8757                                      | 380                          |
| Sub-phase            | 9185                                      | 320                          |
| Flow spine           | 9633                                      | 380 (steps), 270 (decisions) |
| Failure lanes 1 to 3 | 10093, 10503, 10913                       | 330                          |
| Artifacts            | 10503 at creation; moved to 11467 by hand | 400                          |

A phase without sub-phases spans the phase and sub-phase columns, so no column has holes.

### Rows and Gaps

- **Shapes:** a step is 84 high, a decision 104. Rows sit 40 apart.
- **Group changes:** a new sub-phase adds 104 before its first row, a new phase 152, a new cluster 216. That leaves room for the padding of the boxes on both sides.
- **Padding:** each group box adds padding around its content: 32 for a sub-phase, 52 for a phase, 76 for a cluster. Nested boxes therefore never touch.
- **Side items:** a failure-lane item sits on the row of the decision that triggers it. Chained side items (fix, escalate, mark-failed) go into lanes 1, 2 and 3 on that same row.

### Connectors

| Kind               | Sides         | Style          | Use                                                    |
| ------------------ | ------------- | -------------- | ------------------------------------------------------ |
| Forward            | bottom to top | solid, elbowed | next step on the spine                                 |
| Branch             | right to left | solid          | decision to a failure-lane item                        |
| Loop back          | left to left  | dashed         | decision back to an earlier step                       |
| Return from a lane | top to right  | dashed         | fix step back to the step it repeats                   |
| Long jump          | left to left  | solid          | skips: greenfield, manual mode, no architecture change |

Decision outcomes are always labelled ("yes", "no", "fail", "cap reached").

## Shape Styles

| Kind             | Fill              | Border    | Meaning                                       |
| ---------------- | ----------------- | --------- | --------------------------------------------- |
| Agent step       | `#f0f5fd`         | `#305bab` | an agent or script does the work              |
| Human step       | `#fff5ed`         | `#9b4a08` | the stakeholder decides or acts               |
| Gate or decision | `#fffbed`         | `#af7e04` | a check with outcomes; diamonds for decisions |
| Terminal failure | `#fff0f0`         | `#bd0a0a` | mark-failed, mark blocked, stop               |
| Gap              | `#fff0f0`, dashed | `#bd0a0a` | the definitions leave this undefined          |
| End              | `#ffffff`         | `#1a1a1a` | a story or feature is done                    |

Steps are rounded rectangles (radius 12) with a bold name and one line naming the agent, skill or script. The font is Noto Sans throughout: 16 for steps, 14 for decisions, 22, 33 and 64 for sub-phase, phase and cluster labels.

## Artifacts

Each artifact box sits on the row of the step that produces it. There are no connectors: they would cross the failure lanes, and the row alignment carries the relation. Steps that write no file have no box. A box shows a file or a section of a file, never a state change; status fields, the baseline SHA and `impact.architecture_change` were removed for that reason.

Each box carries one chip per class in its top-left corner. A box with mixed content gets several chips.

| Class           | Chip                    | Meaning                              | Examples                                                             |
| --------------- | ----------------------- | ------------------------------------ | -------------------------------------------------------------------- |
| Core            | `#dedaff` / `#6631d7`   | project truth, one owner each        | scope map, feature files, glossary, entity model, `architecture.dsl` |
| Seam            | `#c6dcff` / `#305bab`   | project knowledge the Factory reads  | `agent-context.md`, `testing.yaml`                                   |
| Setup           | `#e7e7e7` / `#313131`   | Factory wiring, no project knowledge | `.agent-factory/`, `model.conf`, pre-commit configuration            |
| Derived view    | `#fff6b6` / `#af7e04`   | generated from Core, never edited    | arc42 chapters, exported diagrams                                    |
| Decision record | `#f8d3af` / `#9b4a08`   | why it is so, append-only            | proposal, ADRs, Pugh matrix                                          |
| Plan            | `#adf0c7` / `#067429`   | what gets built, in which order      | `epics.md`, story files, dispatch ledger                             |
| Quality record  | `#ffc6c6` / `#bd0a0a`   | checks, reviews and findings         | review reports, findings, gate reports, retro                        |
| Working         | white, dashed `#595959` | scaffolding for one change           | gaps report, QA strategy, cut plan, worktrees                        |
| Product         | `#313131` / white       | code, tests, commits                 | only in the Building rows                                            |

Borderline cases: the QA strategy is Working by location, but moves to Seam if it outlives the change. ADRs are Decision records, not Core, because the DSL defines the structure.

## Colouring the Group Shapes

Each cluster has a parent hue. Its phases and sub-phases derive from that hue, so a cluster reads as one family while each level stays distinct.

| Level     | Lightness | Saturation | Hue                                                   |
| --------- | --------- | ---------- | ----------------------------------------------------- |
| Cluster   | 0.74      | 0.50       | parent hue                                            |
| Phase     | 0.84      | 0.55       | parent hue, spread evenly over ±14° across the phases |
| Sub-phase | 0.92      | 0.60       | phase hue, spread over ±6° across its siblings        |

Parent hues: Initiation 205° (blue), Specification 265° (violet), Implementation 145° (green), Reconciliation 28° (orange). Border and label text take the shape's own hue at low lightness: 0.38 to 0.48 for the border, 0.22 to 0.26 for the text. `colors.py` computes all values.

Known weak spot: Building has seven sub-phases inside ±6°, so they look almost alike. Widen the sub-phase spread if they must be told apart.

## The Lying 8

The 8 is an overview at phase level; the detail stays in Frame 2.

- **Left lobe, "Define":** Retrospective, Proposal, Specification, Architecture, Planning.
- **Right lobe, "Deliver":** Building, Code review, Alignment, QA, Close the feature.
- **Waist:** two straight connectors cross it: "backlog ready" from Planning to Building, and "next change" from Close the feature to Retrospective.
- **Initiation:** not part of the loop. It runs once per project as a lead-in row (Setup, Fitting, then Brownfield or Greenfield) and enters at Proposal.

The phases sit on a lemniscate of Bernoulli: x = a·cos t / (1 + sin² t), y = a·sin t·cos t / (1 + sin² t), with a = 2200 and centre (17500, 1400). Five points per lobe, π/6 apart, with t falling continuously so the path crosses the waist twice. Two ellipses in faint violet and faint green mark the lobes. Each phase name links to its phase shape in Frame 2 (`?moveToWidget=<id>`).

The 8 shows one gap against the DevOps original: the Deliver loop ends at "merged into dev". The Factory has no release, operate or monitor phase.

## Generator and Pipeline

| File                                        | Does                                                                                                                                 |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| [overview.py](miro-generator/overview.py)   | First version: three columns, fixed to the user's cluster heights.                                                                   |
| [detail.py](miro-generator/detail.py)       | The flow data: clusters, phases, sub-phases, steps with kind and lane, and edges. Writes `detail.json`.                              |
| [layout.py](miro-generator/layout.py)       | Places the flow, derives the group boxes from right to left, renders shapes and connectors. Writes `detail.svg` and `clusters.json`. |
| [split.py](miro-generator/split.py)         | Splits `detail.svg` into one chunk per cluster plus the cross-cluster connectors.                                                    |
| [artifacts.py](miro-generator/artifacts.py) | Artifact boxes on the rows of their producing steps.                                                                                 |
| [colors.py](miro-generator/colors.py)       | Colour update for the cluster, phase and sub-phase shapes.                                                                           |
| [eight.py](miro-generator/eight.py)         | The lying 8.                                                                                                                         |

Run order: `python3 detail.py`, then `layout.py`, then `split.py`. Upload each chunk with the Miro connector's `canvas_create_from_svg`. Then add the cross-cluster connectors with `canvas_update_from_svg`, using stub elements that carry the widget ids returned by the create calls. The class chips and the shape colours were applied as updates on the live board; `colors.py` reproduces the colour step, while the chip mapping is recorded in the table above.

### Miro Gotchas

- **Read the format first.** The Canvas Composer skill (`canvas_get_canvas_composer_skill`, step `design`, then `dsl`) defines the SVG dialect. The `dsl` step is too large for one tool result; save it and read the sections you need.
- **Payload size.** A create call takes at most 200,000 characters, and long payloads are costly. Split by cluster.
- **Auto-placement.** When a batch's bounding box overlaps existing content, Miro moves the whole batch, once by 19,834 px. Check the result, then move the items back with position-only updates (`x`, `y` and the full box for shapes).
- **Frames.** Once shapes sit in a frame, every update that moves or resizes them must wrap them in the frame's group, with `data-frame` and the frame's background rect. Child coordinates are relative to the frame origin.
- **Literal angle brackets.** Shape labels are HTML. A literal `<name>` must be written as `&amp;lt;name&amp;gt;`, or Miro reads it as a tag and drops it.
- **Deletion needs consent.** Confirm with the board owner before sending `data-deleted="true"`.
- **Unconfirmed updates.** Miro sometimes reports an update as unconfirmed. Resend it: "0 updated" means it had already applied.
- **Rendering for review.** CairoSVG drops straight connectors when it rasterises a Miro export, so the arrows between steps are missing in those images. Judge connectors on the board itself.

## Open Points

- The cluster label "Implementation" wraps at 64 pt in the 469 px column. Use 48 pt or a wider column.
- Some long-jump connectors route far right, between the flow and the artifacts, instead of along the left gap. Fix their sides or give them a lane of their own.
- The core-artifact-ownership changes (domain-modeling and test-strategy agents, spec-feedback report rows) are not drawn yet.
- The widget ids in `colors.py` and the cross-connector stubs tie the scripts to this board. A rebuild on another board needs fresh ids.
