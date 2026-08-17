# PRD — Architecture Modeling Pipeline

**Status**: Specified
**Date**: 2026-08-17
**Domain**: `factory/` — the Docker-wrapped, bidirectional architecture modeling pipeline that maintains JSONC models, draw.io diagrams, and exported images for arc42 documentation

______________________________________________________________________

## 1. Problem Statement

The Factory's current architecture modeling pipeline is unidirectional: agents write a Structurizr DSL file, an ephemeral Docker container exports PNG/SVG images, and those images are embedded in arc42 chapters. Visual review is read-only — a reviewer sees the exported image but cannot adjust layout, correct a label, or annotate the diagram without editing the DSL.

This specification replaces the Structurizr DSL pipeline with Bausteinsicht's bidirectional JSONC-to-draw.io workflow. The JSONC model becomes the single source of truth for structure; the draw.io file is a tracked artifact that owns layout and receives label edits via reverse sync. A Docker image and wrapper script provide the same zero-install experience the Structurizr wrapper delivered.

## 2. Goals and Non-Goals

### Goals

- **G-AM1** — Synchronize a JSONC architecture model with a draw.io diagram bidirectionally: forward sync propagates structural changes, reverse sync carries back all draw.io changes (the Factory workflow restricts permitted reverse changes to labels and descriptions; enforcement is via validate).
- **G-AM2** — Validate model/diagram consistency and enforce architectural constraints declared in the JSONC model, via Docker-containerized Bausteinsicht.
- **G-AM3** — Export architecture views as PNG and SVG images for arc42 chapter embedding, replacing Structurizr's export pipeline.
- **G-AM4** — Migrate existing Factory projects from Structurizr DSL to the JSONC + draw.io workflow via a one-time import.
- **G-AM5** — Block commits that contain inconsistent or improperly co-staged architecture artifacts, via a conditional pre-commit hook.

### Non-Goals

- **NG-AM1** — No restricted reverse mode flag (`--reverse-mode=labels-only`) in the first release. Enforcement of the labels-only restriction relies on `bausteinsicht validate` catching structural drift, not on a Bausteinsicht product feature.
- **NG-AM2** — No visual element creation in draw.io with kind/constraint validation. Adding elements flows through JSONC only.
- **NG-AM3** — No integration of Bausteinsicht `health`, `graph`, `overlay`, or `stale` features into Factory skills in the first release.
- **NG-AM4** — No watch mode integration for interactive authoring sessions.
- **NG-AM5** — No Bausteinsicht-published container image. The Factory owns the Docker image lifecycle.

## 3. Target Actors

- **Architecture Author** (primary) — a factory agent (architecture-agent, architecture-review-agent) or human creating and maintaining the JSONC architecture model. Works in JSONC exclusively; never edits the draw.io file directly.
- **Architecture Reviewer** (primary) — a factory agent or human reviewing the architecture model for correctness and constraint satisfaction. May propose structural changes by patching the JSONC model directly, then syncing.
- **Human Reviewer** (secondary) — a person who opens the draw.io file in draw.io Desktop or VS Code extension to adjust layout, annotate, or fix labels. Does not edit JSONC directly; label and description edits flow back via reverse sync.
- **Human Operator** (secondary, shared with [prd.md](prd.md)) — drives migration from Structurizr DSL and runs wrapper script commands by hand.

## 4. Functional Requirements

### FR-AM-A — Bidirectional sync (`bausteinsicht sync`)

- **FR-AM-A1** — Forward sync propagates structural changes (elements, relationships, views) from the JSONC model to the draw.io diagram.
- **FR-AM-A2** — Reverse sync carries all draw.io changes — including label, description, and structural edits — back into the JSONC model. The Factory workflow permits only label and description changes via this path; structural drift is detected by `bausteinsicht validate` after the fact (BR-051).
- **FR-AM-A3** — No `--reverse-mode=labels-only` flag exists in the first release. Enforcement of the labels-only workflow restriction relies on `bausteinsicht validate` catching structural drift and on the pre-commit hook blocking commits that contain such drift (BR-051, BR-056).
- **FR-AM-A4** — The wrapper script runs Bausteinsicht inside a Docker container; no local binary installation is required (BR-053).

### FR-AM-B — Model validation (`bausteinsicht validate`, `bausteinsicht lint`)

- **FR-AM-B1** — `bausteinsicht validate` checks structural consistency between the JSONC model and the draw.io diagram (BR-056).
- **FR-AM-B2** — `bausteinsicht lint` checks architectural constraints declared in the JSONC model's `constraints` array (BR-056).
- **FR-AM-B3** — `arch-lint` delegates model-specific checks to `bausteinsicht validate` and `bausteinsicht lint`, retaining its own Factory-specific checks (BR-059).

### FR-AM-C — Image export (`bausteinsicht export-all`, `export-png`, `export-svg`)

- **FR-AM-C1** — `export-all` renders every view defined in the JSONC model to both PNG and SVG in `docs/assets/images/` (BR-057).
- **FR-AM-C2** — `export-png` and `export-svg` render to a single format.
- **FR-AM-C3** — The wrapper script handles Docker environment setup (dbus, xvfb) inside the container.

### FR-AM-D — Migration (`bausteinsicht import`)

- **FR-AM-D1** — `import` reads an existing Structurizr DSL file and produces an initial `architecture.jsonc` and `architecture.drawio` (BR-058).
- **FR-AM-D2** — After verification, the actor deletes the `.dsl` file manually; `import` does not delete it.

### FR-AM-E — Pre-commit validation

- **FR-AM-E1** — The pre-commit hook fires conditionally: only when `.jsonc` or `.drawio` files appear in the staging area (BR-055).
- **FR-AM-E2** — Co-staging enforcement: the hook rejects a commit when `architecture.jsonc` is staged without `architecture.drawio`, or vice versa (BR-054).
- **FR-AM-E3** — Consistency check: the hook runs `bausteinsicht validate` and rejects the commit if validation fails (BR-056).

### FR-AM-F — Human-readable diff (`bausteinsicht diff`)

- **FR-AM-F1** — `diff` produces a human-readable structural change summary comparing the current JSONC model state against its last synced state, suitable for PR descriptions.

## 5. Constraints

- All Bausteinsicht operations run inside a Docker container via `factory/scripts/bausteinsicht`. The Factory builds its own image from a Dockerfile in `factory/` containing the Bausteinsicht binary, draw.io Desktop (headless via xvfb), and Electron dependencies.
- Agents work in the JSONC model exclusively. They never edit the draw.io file directly (BR-052).
- The JSONC model is the single source of truth for structure. The draw.io file owns layout (BR-050).
- The pre-commit hook for architecture validation is wired through the same `factory/config/pre-commit-config.yaml` infrastructure that the flow-control specification covers in [UC-08](use_cases/UC-08-initialize-agent-factory-into-a-project.md). `init-factory` installs it as part of the same pre-commit configuration.
- macOS and Linux only, matching [prd.md § Constraints](prd.md#5-constraints).

## 6. Success Criteria

- `factory/scripts/structurizr` is deleted; `factory/scripts/bausteinsicht` handles all architecture modeling operations via Docker.
- `scaffold-arc42` produces `architecture.jsonc`, `architecture.drawio`, and exported images in a new project.
- `maintain-architecture` operates JSONC-first with automated Mermaid sequence export from `dynamicViews`.
- `model-slice` replaces `model-structurizr-slice` for delivery increment modeling.
- `arch-lint` delegates model checks to `bausteinsicht validate` and `bausteinsicht lint`.
- The pre-commit hook validates and enforces co-staging of `.jsonc` and `.drawio` files.
- An existing project with `architecture.dsl` can migrate via `factory/scripts/bausteinsicht import` and produce a valid, synced model.
- All Structurizr references are removed from Factory skills, agents, playbooks, scripts, and documentation.

## 7. Assumptions

- Docker is available on the host machine. The wrapper script requires a running Docker daemon.
- Every project using this pipeline has run `init-factory` at least once, which wires the pre-commit hook and copies `factory/` — the same assumption as [prd.md § Assumptions](prd.md#7-assumptions).
- The Bausteinsicht binary is available as a GitHub release artifact for the target architecture (amd64/arm64).

## Referenced from

- [actor-goal-list.md](actor-goal-list.md)
- [Accepted Bausteinsicht Factory Integration proposal](../proposals/bausteinsicht-factory-integration.md) — design origin for this specification.
- [prd.md](prd.md) — flow-control specification, cross-referenced for shared pre-commit infrastructure (UC-08) and `arch-lint` integration.
