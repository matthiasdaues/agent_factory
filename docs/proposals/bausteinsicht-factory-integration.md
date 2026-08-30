---
schema_version: 2
title: "Bausteinsicht Factory Integration"
status: accepted
owner: agent-factory
created: 2026-08-17
updated: 2026-08-17
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - factory/scripts/structurizr
    - factory/scripts/arch-lint
    - factory/skills/scaffold-arc42/SKILL.md
    - factory/skills/maintain-architecture/SKILL.md
    - factory/skills/model-structurizr-slice/SKILL.md
    - factory/skills/validate/SKILL.md
    - factory/skills/atam-review/SKILL.md
    - factory/agents/architecture-agent.md
    - factory/agents/architecture-review-agent.md
    - factory/agents/reconciliation-agent.md
    - factory/playbooks/greenfield-development.md
    - factory/playbooks/brownfield-onboarding.md
    - factory/playbooks/architecture-review.md
    - factory/config/pre-commit-config.yaml

governance:
  assurance: high
  risk_domains:
    - compatibility
    - reliability

estimate:
  as_of: 2026-08-17
  basis: decomposition
  confidence: medium
  human_review_hours:
    min: 2.0
    max: 4.0
  normalized_tokens:
    min: 40000
    max: 80000
  estimated_consumption:
    min: 600000
    max: 2000000
    overhead_multiplier: 15
    playbook: feature-addition
---

# THIS PROPOSAL IS DONE BUT FEATURE BRANCH REMAINS UNMERGED

# Feature Request: Bausteinsicht Factory Integration

## Summary

Replace the Structurizr DSL and ephemeral Docker export pipeline with
Bausteinsicht's bidirectional JSONC-to-draw.io workflow as the Factory's
architecture modeling backend. The JSONC model becomes the single source of
truth for structure; the draw.io file is a tracked artifact that owns layout
and receives label edits via reverse sync. A new Docker image and wrapper
script provide the same zero-install experience the Structurizr wrapper
delivers today.

## Motivation

The current pipeline is unidirectional: agents write a Structurizr DSL file,
an ephemeral Docker container exports PNG/SVG images, and those images are
embedded in arc42 chapters. Visual review is read-only — a reviewer sees the
exported image but cannot adjust layout, correct a label, or annotate the
diagram without editing the DSL.

Bausteinsicht adds a bidirectional sync loop. The draw.io file is a live,
editable visual artifact. Reviewers (human or agent) can rearrange elements,
fix labels, and add annotations in draw.io. Reverse sync carries label and
description edits back into the JSONC model. This closes the feedback loop
between visual review and the canonical model without requiring reviewers to
learn a text DSL.

Bausteinsicht also provides capabilities the Structurizr pipeline lacks:
architectural constraint enforcement (`lint`), health scoring, graph analysis,
staleness detection, and overlay heatmaps. Only constraint enforcement is
included in this first release; the rest is additive.

## Core Principles

- JSONC is the single source of truth for structure (elements, relationships,
  views, constraints). The draw.io file owns layout and visual arrangement.
- Reverse sync is restricted to labels and descriptions. Structural changes
  (add, delete, rename elements or relationships) flow forward only, from
  JSONC to draw.io.
- Human draw.io edits are limited to layout and annotations. Deletion requests
  are expressed as draw.io notes ("remove this component") that feed back into
  the agentic workflow. Adding elements visually is deferred.
- The Factory does not install the Bausteinsicht binary directly. All
  operations run inside a Docker container via a thin wrapper script.
- Agents work in the JSONC model. They never edit the draw.io file directly.

## Design

### Source of truth and file locations

| File                  | Location              | Role                                             |
| --------------------- | --------------------- | ------------------------------------------------ |
| `architecture.jsonc`  | `docs/arc42/`         | Primary source of truth (structure)              |
| `architecture.drawio` | `docs/arc42/`         | Tracked artifact (layout, visual review)         |
| `.bausteinsicht-sync` | `docs/arc42/`         | Sync state (dot-file, auto-managed)              |
| `assets/styles/`      | `docs/arc42/`         | Custom draw.io templates (`.gitkeep` by default) |
| Exported images       | `docs/assets/images/` | Derived PNG/SVG for arc42 chapter embedding      |

The `$schema` field in `architecture.jsonc` points to the Bausteinsicht JSON
Schema on GitHub, giving IDE autocompletion and validation without local
tooling.

### Sync workflow

Sync runs at two points:

1. **After model edits** — skills and agents run `factory/scripts/bausteinsicht sync` after touching the JSONC (forward pass).
2. **Before commit (safety net)** — a pre-commit hook fires conditionally when
   `.jsonc` or `.drawio` files are staged. It runs `bausteinsicht validate` to
   verify consistency. The hook also enforces co-staging: if one of
   `architecture.jsonc` or `architecture.drawio` is staged without the other,
   the commit is rejected.

### Reverse sync boundaries

The reverse pass (draw.io to JSONC) carries back:

- **Label and description text** — edits to element titles and descriptions in
  draw.io flow back into the JSONC model.
- **Layout and positions** — remain in the draw.io file only; not modeled in
  JSONC.
- **Annotations and notes** — remain in the draw.io file. A note containing
  "remove this component" becomes a signal for the agentic workflow, not an
  automatic deletion.

The reverse pass does **not** create, delete, or rename elements or
relationships. Bausteinsicht's full reverse sync capability is available in the
product, but the Factory workflow relies on validation discipline to prevent
structural drift: `bausteinsicht validate` and `bausteinsicht lint` catch
inconsistencies introduced by draw.io edits.

A restricted reverse mode flag (`--reverse-mode=labels-only`) is a desirable
future Bausteinsicht product feature but is not required for this first release.

### Docker image and wrapper script

The Factory builds its own Docker image containing:

- Bausteinsicht binary (downloaded from GitHub releases for target arch)
- draw.io Desktop (`.deb`, headless via xvfb)
- xvfb, dbus, and Electron dependencies

The image is built from a Dockerfile in `factory/`. The Bausteinsicht project
does not publish a container image; the Factory owns the image lifecycle.

`factory/scripts/bausteinsicht` is a thin wrapper that calls `docker run` with
volume-mounted `docs/`. It delegates to the Bausteinsicht binary inside the
container for all operations.

Wrapper subcommands:

| Subcommand   | Operation                                  |
| ------------ | ------------------------------------------ |
| `sync`       | Forward + reverse sync (JSONC and draw.io) |
| `validate`   | Model validation + constraint lint         |
| `export-all` | Export all views as PNG + SVG              |
| `export-png` | Export PNG only                            |
| `export-svg` | Export SVG only                            |
| `import`     | One-time Structurizr DSL import            |
| `diff`       | Human-readable change summary              |

### Image export

`bausteinsicht export` renders each view to PNG/SVG in `docs/assets/images/`.
Arc42 chapters embed them with standard image references to `docs/assets/images/`,
identical to the current Structurizr pipeline. The wrapper script handles
environment setup (dbus, xvfb) inside the container.

### Agent and review workflow

- **Architecture agent** writes and updates `architecture.jsonc`. Runs
  `factory/scripts/bausteinsicht sync` and `factory/scripts/bausteinsicht export-all` after model changes.
- **Architecture-review agent** reads the JSONC model and exported images.
  Proposes structural changes by patching the JSONC directly, then syncs.
- **Human reviewers** open `architecture.drawio` in draw.io (desktop or VS
  Code extension). They adjust layout and annotate. The pre-commit hook
  catches their changes via validation.
- **Mermaid sequence diagrams** are generated automatically via
  `bausteinsicht export sequence` from `dynamicViews` in the JSONC. The
  manual Mermaid derivation rules in `maintain-architecture` are removed.

### draw.io diffs in code review

`.gitattributes` marks `.drawio` as binary to suppress noisy XML diffs for
human reviewers. Agents can bypass `.gitattributes` and compare when needed.
`bausteinsicht diff` produces a human-readable structural change summary for
PR descriptions.

### Constraint enforcement

`bausteinsicht lint` enforces architectural constraints defined in the
`constraints` array of the JSONC model. `arch-lint` delegates to
`bausteinsicht validate` and `bausteinsicht lint` for model consistency, and
retains its own Factory-specific checks (arc42 chapter coupling, ADR format,
image staleness).

### Migration path

Existing Factory projects migrate with a one-time import:

```bash
factory/scripts/bausteinsicht import docs/arc42/architecture.dsl
```

This produces `architecture.jsonc` and an initial `architecture.drawio`. After
verification, the `.dsl` file is deleted.

### Starter specification

`scaffold-arc42` includes a recommended starter `specification` block covering
three kind categories:

- **C4 structural core** — actor, system, container, component
- **Infrastructure/runtime** — datastore, queue, ui, mobile, filestore
- **Deployment/network** — deployment node, network zone, load balancer

Projects trim unused kinds. The specification is user-defined; these are
defaults, not hard-coded types.

### Reference documentation

`BAUSTEINSICHT.md` replaces `STRUCTURIZR.md` as a bundled reference for the
`scaffold-arc42` skill. It documents JSONC syntax with C4-flavored examples,
the starter specification, and wrapper script commands.

## Scope

**In the first release:**

- Replace `factory/scripts/structurizr` with `factory/scripts/bausteinsicht`
  (Docker wrapper).
- Create the Dockerfile for the Bausteinsicht container image.
- Rewrite `scaffold-arc42` skill for JSONC + sync + export workflow.
- Replace `STRUCTURIZR.md` with `BAUSTEINSICHT.md` (reference + starter spec).
- Rewrite `maintain-architecture` skill for JSONC-first workflow with automated
  Mermaid export.
- Rewrite `model-structurizr-slice` as `model-slice` targeting JSONC
  view/tag/constraint primitives.
- Update `validate` skill gate #7 condition to `architecture.jsonc`.
- Update `atam-review` skill description.
- Update `arch-lint` to delegate model checks to `bausteinsicht validate` and
  `bausteinsicht lint`.
- Update `architecture-agent`, `architecture-review-agent`, and
  `reconciliation-agent` (skills list, inputs, outputs, commands).
- Update `greenfield-development`, `brownfield-onboarding`, and
  `architecture-review` playbooks.
- Update `greenfield-development.fsm.yml`.
- Update `factory/config/pre-commit-config.yaml`.
- Update `factory/docs/factory-guide.md`.
- Update `caveman` skill asset list reference.
- Regenerate `factory/INDEX.yaml` via `index-lint`.
- Add `.drawio` binary marker to `.gitattributes`.
- Create `docs/arc42/assets/styles/.gitkeep` in scaffold output.
- Pre-commit hook: conditional validation and co-staging enforcement for
  `.jsonc` and `.drawio` files.

**Explicitly deferred (do NOT plan stories for these):**

- Restricted reverse mode flag in Bausteinsicht (`--reverse-mode=labels-only`).
- Adding elements visually in draw.io with validation of element kinds and
  relationship constraints.
- Integration of Bausteinsicht `health`, `graph`, `overlay`, or `stale`
  features into Factory skills.
- Publishing a container image from the Bausteinsicht product repository.
- Watch mode integration for interactive authoring sessions.

## Open Questions

- ~~What Bausteinsicht release version should the Dockerfile pin?~~ **Deferred
  to implementation**: the developer-agent resolves the concrete version tag
  from the latest stable GitHub release at build time. The Dockerfile pins
  that version explicitly; it is not left floating.

## Completion Criteria

- `factory/scripts/structurizr` is deleted; `factory/scripts/bausteinsicht`
  handles all architecture modeling operations via Docker.
- A Dockerfile in `factory/` builds a working image with Bausteinsicht,
  draw.io, xvfb, and dbus.
- `scaffold-arc42` produces `architecture.jsonc`, `architecture.drawio`, and
  exported images in a new project.
- `maintain-architecture` operates JSONC-first with automated Mermaid sequence
  export.
- `model-slice` replaces `model-structurizr-slice` for delivery increment
  modeling.
- `arch-lint` delegates model validation to `bausteinsicht validate` and
  `bausteinsicht lint`.
- Pre-commit hook validates and enforces co-staging of `.jsonc` and `.drawio`.
- An existing project with `architecture.dsl` can migrate via
  `factory/scripts/bausteinsicht import` and produce a valid, synced model.
- All Structurizr references are removed from Factory skills, agents,
  playbooks, scripts, and documentation.
- `index-lint --check` passes after all changes.

## Guiding Rule

The Factory's architecture modeling pipeline must be bidirectional, Docker-only,
and leave structural authority in the JSONC model at all times.
