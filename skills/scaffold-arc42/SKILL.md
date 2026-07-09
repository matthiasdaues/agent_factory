---
name: scaffold-arc42
description: Create arc42 architecture documentation and a Structurizr C4 model from the specification.
category: architecture
disable-model-invocation: true
---

# Scaffold arc42

Create architecture documentation from the specification using the **arc42** template and **Structurizr DSL** for **C4** models. Apply **Clean Architecture** for layer and component boundaries.

Read `docs/CONTEXT.md` if it exists — use the project's domain vocabulary throughout.

## Step 1 — Create the arc42 file structure

Create the following under `docs/`:

```
docs/
├── README.md                          ← TOC linking to all 12 chapters
├── 01_introduction_and_goals.md
├── 02_architecture_constraints.md
├── 03_system_scope_and_context.md
├── 04_solution_strategy.md
├── 05_building_block_view.md
├── 06_runtime_view.md
├── 07_deployment_view.md
├── 08_crosscutting_concepts.md
├── 09_architecture_decisions.md       ← index linking to docs/adr/*
├── 10_quality_requirements.md
├── 11_risks_and_technical_debt.md
├── 12_glossary.md
├── architecture.dsl
├── adr/
└── assets/
    └── images/
```

Rules:

- Every chapter file starts with `[back to index](README.md)` as its first line.
- Fill each chapter from the specification in `docs/spec/` — **no placeholder text**.

Template reference: [`matthiasdaues/arc42-markdown-template`](https://github.com/matthiasdaues/arc42-markdown-template).

Format every chapter file and `docs/README.md` via `scripts/mdformat --number <path>` per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).

**Completion**: all 12 chapter files exist with substantive content, every chapter starts with the back-link, `docs/README.md` links to all chapters and all links resolve.

## Step 2 — Define the C4 model

Create `docs/architecture.dsl` using **Structurizr DSL** — see [STRUCTURIZR.md](STRUCTURIZR.md) for syntax reference.

Define **C4** System Context and Container views; add a Component view for key containers where the spec provides enough detail.

Validate the model:

```bash
scripts/structurizr validate
```

**Completion**: `docs/architecture.dsl` validates without errors, views cover system context and containers at minimum.

## Step 3 — Export and embed diagrams

```bash
scripts/structurizr export-all
```

Exports SVG and PNG to `docs/assets/images/` (requires Docker; see [STRUCTURIZR.md](STRUCTURIZR.md) for individual-format and `list-views` commands). Embed in the relevant arc42 chapters using relative paths:

```markdown
![System Context](assets/images/SystemContext.png)
```

**Completion**: architecture reflects Clean Architecture boundaries from the spec, diagrams exported to `docs/assets/images/` and embedded in chapters.
