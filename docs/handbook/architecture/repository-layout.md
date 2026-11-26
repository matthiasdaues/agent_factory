---
title: Repository layout
type: reference
status: implemented
order: 10
description: The top-level folders of the factory repository, with the source of the factory and its installed copy.
---

# Repository layout

You look for a folder of the factory repository. `packages/factory/` is the source of the factory. `init-factory` copies it to `.agent-factory/factory/` in a project, and that installed copy is never edited by hand. In this repository, edit the source and run `update-factory` to refresh the installed copy.

```
agent_factory/
├── packages/
│   ├── factory/                 The source of the factory
│   │   ├── agents/              One .md file per agent
│   │   ├── skills/              One folder per skill, each holding a SKILL.md
│   │   ├── playbooks/           Flows for common situations, such as a bug fix or a feature
│   │   ├── rulebooks/           conventions/, templates/, and schemas/
│   │   ├── scripts/             The gate scripts and the setup scripts, such as init-factory and update-factory
│   │   ├── config/              Templates such as AGENTS.md, the pre-commit config, and model.conf
│   │   ├── docs/handbook/       The user handbook
│   │   └── INDEX.yaml           The generated catalogue of agents, skills, playbooks, and rulebooks
│   └── usage/                   The optional usage add-on
├── .agent-factory/factory/      The installed copy of packages/factory/, git-ignored
├── backlog/                     Epics and stories
├── docs/
│   ├── README.md                The table of contents of the arc42 documentation
│   ├── agent-context.md         The routing file: one concern per topic
│   ├── testing.yaml             The test suites and the gate settings
│   ├── handbook/                The contributor handbook
│   ├── spec/                    The specification: scope map, glossary, entity model, contracts, architecture.dsl
│   │   ├── features/            One Gherkin .feature file per feature
│   │   ├── areas/               Area specifications
│   │   └── work/                Working output: gaps reports, QA strategies, prd.md, to-do lists
│   ├── arc42/                   The arc42 chapters
│   ├── adr/                     Architecture decision records
│   ├── findings/                Filed findings
│   ├── reviews/                 Review, retrospective, and reconciliation reports
│   └── assets/                  Exported images and the Structurizr themes
├── tests/                       The test suite of the repository
└── README.md
```

[Usage add-on structure](usage-add-on-structure.md) shows the tree of `packages/usage/`. The bounded contexts are in [docs/agent-context.md](../../agent-context.md).
