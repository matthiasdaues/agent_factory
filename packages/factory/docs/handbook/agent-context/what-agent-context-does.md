---
title: What the agent context does
type: concept
status: implemented
order: 10
description: How docs/agent-context.md routes agents to your project's own knowledge, and which parts of it you own.
---

# What the agent context does

An agent that works on your project needs your project's knowledge: how you branch, where the backend lives, which documents describe the domain. `docs/agent-context.md` tells the agent where to look. It never says what the agent will find there, so it is a switchboard, not a knowledge base. Its structure changes slowly, while the content it points to grows with the project.

The file does not exist after `init-factory`. VIRGIL creates it during onboarding with the `capture-context` skill, as part of a greenfield or brownfield playbook. [Set up and keep the agent context current](set-up-and-keep-current.md) describes that step.

```text
Story names its concerns
          |
          v
docs/agent-context.md
          |
          | Read: paths
          +--> Test commands in docs/testing.yaml
          +--> Team rules in the project documentation
          +--> Domain behavior in the specification
```

## Three categories of concern

The file has three concern categories, each under a `##` heading:

| Category      | Active                                  | Examples                                                           |
| ------------- | --------------------------------------- | ------------------------------------------------------------------ |
| Cross-cutting | Always, for every agent and every story | Branching, committing, testing discipline, review, scope, security |
| Technical     | Per story, set by the planning agent    | Backend, frontend, data storage, infrastructure                    |
| Domain        | Per story, set by the planning agent    | Taken from the areas of the scope map or the specification         |

Each concern is a `###` heading under its category. It holds a one-line description, one or more `Read:` lines with the paths of the files where the knowledge lives, and optional `Boundary:` lines that name interfaces to other concerns.

The cross-cutting concerns are the professional baseline, so they are always active. The technical and domain concerns narrow the context of one task. The planning agent writes a `concerns` field into the frontmatter of each story and picks its values from the concerns that `agent-context.md` defines.

## What you own

The factory owns the three category headings and the lint checks. You own everything beneath them: the names of the concerns, their descriptions, their `Read:` paths, and their `Boundary:` lines. You can add, rename, and remove concerns, and point them at any file in your project. The factory proposes, and you decide.
