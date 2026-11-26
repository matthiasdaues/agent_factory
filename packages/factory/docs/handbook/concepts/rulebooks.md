---
title: Rulebooks
type: concept
status: implemented
order: 70
description: Where the factory keeps the conventions that hold across agents and skills, and how the rulebook folders are sorted.
---

# Rulebooks

When two agents both write commit messages, they need the same format. A rulebook holds such a convention once, for every agent and skill: the format of a commit message, how to reference another document, the style of an ADR, or the scope of a branch.

[`.agent-factory/factory/rulebooks/rules.md`](../../../rulebooks/rules.md) states each rule in one line. The matching file in `.agent-factory/factory/rulebooks/conventions/` holds the reasons, the examples, and the edge cases. Agents and skills cite these rules instead of repeating them.

The rulebooks are sorted by kind, one folder per kind. `index-lint` reads the `category` of each rulebook from the name of its parent folder:

| Folder                                            | Holds                                                                                    | In `INDEX.yaml`? |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------- | ---------------- |
| [`conventions/`](../../../rulebooks/conventions/) | The prose conventions, and the four research policies `research-*.md`                    | Yes              |
| [`templates/`](../../../rulebooks/templates/)     | Skeletons for artifacts: ADRs, and the ten research artifact templates `research-*.md`   | Yes              |
| [`schemas/`](../../../rulebooks/schemas/)         | JSON Schema data contracts `research-*.schema.json`, which the research validators check | No               |

The research files sit in all three folders and carry the filename prefix `research-` instead of a folder of their own. The ADR "Research flat storage and validation pipeline" (ADR-0006) in the Agent Factory repository explains this choice. Two consequences follow from it:

- The four research policies live under `conventions/`. So `index-lint` lists them with `category: conventions`, although their own frontmatter reads `category: policies`. That label describes what they are. No `policies/` folder exists.
- `schemas/` holds machine-readable data, not prose. Its `.schema.json` files are not in `INDEX.yaml`, because `index-lint` reads only the frontmatter of Markdown files. The validators find each schema by its path, never by a name in the catalogue.
