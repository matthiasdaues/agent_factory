---
title: Page format
type: reference
status: implemented
order: 10
description: The frontmatter fields and the page types of both handbooks.
---

# Page format

Every page of both handbooks starts with a frontmatter block.

| Field         | Values                                                | Required | Effect                                                                              |
| ------------- | ----------------------------------------------------- | -------- | ----------------------------------------------------------------------------------- |
| `title`       | Text                                                  | Yes      | Page title and link text in the generated lists                                     |
| `type`        | `tutorial`, `concept`, `how-to`, `reference`, `learn` | Yes      | Group heading in the chapter's page list                                            |
| `status`      | `implemented`, `stub`                                 | Yes      | A `stub` page stays out of the generated lists                                      |
| `description` | One sentence                                          | No       | Shown after the link in the generated lists                                         |
| `order`       | A number, default 100                                 | No       | Sorts pages in a group, and chapters in the top-level `index.md`; lower comes first |

The `type` sets what a page holds.

| `type`      | The reader wants to           | The page holds                                          | The page leaves out                |
| ----------- | ----------------------------- | ------------------------------------------------------- | ---------------------------------- |
| `tutorial`  | be guided through a first run | A fixed path with checkpoints and few choices           | Background and alternatives        |
| `concept`   | understand how it works       | A mental model, the terms, and why it is built this way | Rules and step-by-step recipes     |
| `how-to`    | get one task done             | The task as the title, steps with real commands         | Unrelated rules and long rationale |
| `reference` | look something up             | Lists, tables, flags, and signatures                    | Teaching prose and rationale       |
| `learn`     | learn a technology            | A longer text with running examples                     | New rules                          |

A rule has one home, in `packages/factory/rulebooks/`. A page that needs a rule repeats it in a callout and links to the home:

```markdown
> Rule summary: **MUST** run `.agent-factory/factory/scripts/mdformat --number <path>` immediately after writing any markdown file.
> Source: [rules.md § Markdown formatting](../../../packages/factory/rulebooks/rules.md#markdown-formatting)
```

Ordinary prose states no rule. Nothing checks this, so the author and the reviewer do.
