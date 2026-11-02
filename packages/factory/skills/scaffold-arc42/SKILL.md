---
name: scaffold-arc42
description: Create arc42 architecture documentation and a Structurizr C4 model from the specification.
category: architecture
---

# Scaffold arc42

Create architecture documentation from the specification using the **arc42** template and **Structurizr DSL** for **C4** models. Apply **Clean Architecture** for layer and component boundaries.

Read [factory-voice.md](../../rulebooks/conventions/factory-voice.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates and clears the final pass.
Read `docs/spec/glossary.md` if it exists — use the project's domain vocabulary throughout.

## Step 1 — Create the arc42 file structure

Create the following under `docs/`. Add no file directly in `docs/` except
`README.md`. The arc42 chapters live in `docs/arc42/`, the Structurizr source in
`docs/spec/`, and its theme in `docs/assets/themes/`. Existing files stay where
they are:

```
docs/
├── README.md                          ← TOC linking to all 12 chapters
├── arc42/
│   ├── 01_introduction_and_goals.md
│   ├── 02_architecture_constraints.md
│   ├── 03_system_scope_and_context.md
│   ├── 04_solution_strategy.md
│   ├── 05_building_block_view.md
│   ├── 06_runtime_view.md
│   ├── 07_deployment_view.md
│   ├── 08_crosscutting_concepts.md
│   ├── 09_architecture_decisions.md   ← index linking to docs/adr/*
│   ├── 10_quality_requirements.md
│   ├── 11_risks_and_technical_debt.md
│   └── 12_glossary.md                 ← one line linking to docs/spec/glossary.md
├── spec/
│   └── architecture.dsl
├── adr/
└── assets/
    ├── images/
    └── themes/
        └── default/
            └── theme.json
```

Rules:

- Every chapter file starts with `[back to index](../README.md)` as its first line.

- Fill each chapter from the specification in `docs/spec/` — **no placeholder text**.

- In chapter 5, list components in tables under `## 5.2` and later headings. Head the first column `Component`, and write each name exactly as in `architecture.dsl`, plain or bold. `arch-lint` reads these names and compares them with the model. It also counts a bold first cell in any other table. When the model declares components and chapter 5 names none, the gate fails.

  ```markdown
  | Component  | Responsibility |
  | ---------- | -------------- |
  | API routes | Serve requests |
  ```

Template reference: [`matthiasdaues/arc42-markdown-template`](https://github.com/matthiasdaues/arc42-markdown-template).

Format every chapter file and `docs/README.md` via `.agent-factory/factory/scripts/mdformat --number <path>` per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).

**Completion**: all 12 chapter files exist with substantive content, every chapter starts with the back-link, `docs/README.md` links to all chapters and all links resolve.

## Step 2 — Define the C4 model

Copy the default Structurizr theme from `.agent-factory/factory/themes/structurizr/default/` into `docs/assets/themes/default/`. The DSL's `theme` line points there: `theme ../assets/themes/default/theme.json`.

Create `docs/spec/architecture.dsl` using **Structurizr DSL** — see [STRUCTURIZR.md](STRUCTURIZR.md) for syntax reference.

The workspace `properties` block must include `"arc42.projected" "false"` by default. This property is set to `"true"` by the architecture-agent only when the user requests arc42 chapter projection from the DSL.

Define **C4** System Context and Container views; add a Component view for key containers where the spec provides enough detail.

Validate the model:

```bash
.agent-factory/factory/scripts/structurizr validate
```

**Completion**: `docs/spec/architecture.dsl` validates without errors, views cover system context and containers at minimum.

## Step 3 — Export and embed diagrams

```bash
.agent-factory/factory/scripts/structurizr export-all
```

Exports SVG and PNG to `docs/assets/images/` (requires Docker; see [STRUCTURIZR.md](STRUCTURIZR.md) for individual-format and `list-views` commands). Embed in the relevant arc42 chapters using relative paths:

```markdown
![System Context](../assets/images/SystemContext.svg)
```

**Completion**: architecture reflects Clean Architecture boundaries from the spec, diagrams exported to `docs/assets/images/` and embedded in chapters.
