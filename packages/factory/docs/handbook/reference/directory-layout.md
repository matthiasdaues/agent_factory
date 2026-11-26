---
title: Directory layout
type: reference
status: implemented
order: 10
description: The folders and files of an installed .agent-factory/factory/.
---

# Directory layout

After `init-factory` runs, `.agent-factory/factory/` holds the full toolset:

```
.agent-factory/factory/
├── agents/          One Markdown file per agent (requirements-agent.md and the others)
├── CHANGELOG.md     Release history
├── config/          Session menu, orientation templates, hook and extension files, pre-commit template
├── contracts/       Interface contracts between factory components
├── docker/          Container image of publish-docs
├── docs/            This handbook
├── engine/          Precondition evaluator and agent eligibility engine
├── fixtures/        Sample projects for the quality-gate demos
├── INDEX.yaml       Catalogue of every agent, skill, playbook, and rulebook
├── playbooks/       Workflow recipes (greenfield-development.md, bug-fix.md, and the others)
├── README.md        Prerequisites and installation
├── reports/         Output folder for review and research reports
├── rulebooks/       Cross-cutting conventions, templates, and schemas
├── scripts/         Gates, linters, and helper scripts
├── skills/          Reusable procedures, one folder per skill
├── tests/           The factory's own test suite
├── themes/          Themes of the remark-grid deck and of Structurizr diagrams
└── VERSION          Current factory version
```

The installer also writes local configuration under `.agent-factory/config/`, outside the factory folder. [Files that init-factory creates](local-configuration.md) lists those files.
