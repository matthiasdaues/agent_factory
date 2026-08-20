---
name: update-charter
description: >-
  Update a section in the project charter (tech-stack, development, or house-rules).
  Invokable by any agent during any phase. Owns the write target docs/charter/*.md.
category: utility
version: 1.0.0
---

# Update Charter

Actively update the project charter as decisions emerge across phases — recording technology choices, development practices, and team rules directly into the appropriate charter documents. Merely *reading* `docs/charter/*.md` for reference is not this skill; any agent can do that. This skill is for *changing* the charter, not just consulting it.

Charter updates happen incrementally. Different documents fill at different rates:

- **tech-stack.md** — starts filling during vision, sharpens during requirements, solidifies during architecture.
- **development.md** — mostly records decisions close to the planning gate.
- **house-rules.md** — accumulates opportunistically.

The skill owns the write target (`docs/charter/*.md`) — invoking agents do not need charter files in their `outputs:`.

## When to update the charter

Use this skill when:

- A technology choice has been decided (language, framework, database, cloud provider, etc.)
- A development practice has been established (test framework, CI/CD pipeline, branching strategy, etc.)
- A team rule needs recording (review protocol, approval gates, testing discipline, etc.)
- An existing entry needs updating or clarification based on new information

Do not use this skill when merely consulting the charter for context — read the documents directly.

## Charter structure

Three documents exist under `docs/charter/`:

1. **tech-stack.md** — What we build with. Languages, frameworks, databases, infrastructure, existing systems, licensing constraints.
2. **development.md** — How we work here. Repository layout, getting started, running the project, testing, linting, CI/CD, branching.
3. **house-rules.md** — How we work together. Commits & PRs, review & approval, testing discipline, architecture governance, scope & boundaries.

Each document is organized by sections. Preserve existing sections when updating — add to or clarify them, do not replace.

## Workflow

### 1. Read the current charter state

Read the relevant charter document (`docs/charter/tech-stack.md`, `docs/charter/development.md`, or `docs/charter/house-rules.md`). Locate the section where the decision belongs. If the section exists, understand the current content. If it does not exist, check the template at `factory/rulebooks/templates/charter-<document>.md` to see where it should go.

### 2. Update the relevant section

Add or modify the section to record the decision. Follow these principles:

- **Preserve existing content.** Do not overwrite or remove what is already there — enhance it.
- **Be concrete.** Name specific versions, tools, paths, commands. "Python 3.12" not "a dynamic language." "FastAPI with pytest" not "some framework and testing."
- **Record the why.** When a choice excludes alternatives, explain briefly. "PostgreSQL 16 for primary data (team expertise, existing codebase)."
- **Be practical.** Charter reads like a reference page that a developer consumes on day one. Focus on what matters for development, not academic exhaustiveness.

### 3. Commit

Commit the change with format:

```
docs: update charter <document> — <section> (<ID>)
```

Where:

- `<document>` is `tech-stack`, `development`, or `house-rules`
- `<section>` is the section name (e.g., "Languages & Runtimes", "Testing", "Architecture Governance")
- `(<ID>)` is the story, finding, or phase context that triggered the update (e.g., `(ST-0042)`, `(ATAM-0001)`)

When no ID applies (e.g., during initial vision capture), omit the ID suffix:

```
docs: update charter <document> — <section>
```

One commit per update. Each commit is attributable to the phase that made the decision.

### 4. Format

After writing or modifying charter files, run:

```bash
factory/scripts/mdformat --number docs/charter/<document>.md
```

Per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md), mdformat must be run immediately after writing any markdown file.

## Example

**Scenario:** The requirements-agent settles on PostgreSQL 16 as the primary database. The tech-stack.md file already exists with a "Data Stores" section, but it says "To be decided."

**Workflow:**

1. Read `docs/charter/tech-stack.md` and locate the "Data Stores" section.
2. Replace "To be decided" with:
   ```
   PostgreSQL 16 for primary data (team expertise, existing migrations). Redis for session cache.
   ```
3. Commit:
   ```
   docs: update charter tech-stack — Data Stores (SPEC-0003)
   ```
4. Run mdformat:
   ```
   factory/scripts/mdformat --number docs/charter/tech-stack.md
   ```

## Cross-referencing

Do not add the charter to agents' `outputs:` — the skill owns it. If another agent needs to reference charter entries (e.g., in an ADR explaining why a technology was chosen), link to the relevant section: "See [tech-stack.md § Data Stores](../charter/tech-stack.md#data-stores)."

## Templates

When a section does not exist yet, refer to templates at `factory/rulebooks/templates/charter-*.md` to understand the expected structure. Templates are skeletons with headings and one-line comment prompts. Preserve the section heading; discard the prompt comment, replace with the actual decision.
