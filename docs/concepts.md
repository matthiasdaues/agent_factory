# How Agent Factory Works

The theory behind Agent Factory, and a map of this repo. If you want to start using the toolset, go to [factory/README.md](../factory/README.md) instead — this page is background, not a tutorial.

## The phase chain

Agent Factory drives an AI coding CLI through five phases, from idea to production-quality code:

1. **Requirements** — interview, PRD, Cockburn use cases, supplementary specs
2. **Architecture** — arc42 documentation, Structurizr C4 model, ADRs, ATAM review
3. **Planning** — backlog with INVEST stories, MoSCoW prioritisation, dependency links
4. **Implementation** — TDD per issue, spec feedback loop, spec reconciliation
5. **Quality** — Fagan inspection, OWASP security review, exploratory bug hunt

Each phase has an **author agent** and a **reviewer agent**. The author produces an artifact. The reviewer evaluates it independently, in a separate session, until the review comes back clean — the same principle as not reviewing your own pull request.

```
requirements ↔ spec-review → architecture ↔ architecture-review → planning → implementation → reconciliation ↔ qa
```

Not every task needs the full chain. See [factory/docs/factory-guide.md § Playbooks](../factory/docs/factory-guide.md#playbooks) for the shorter paths.

## Key ideas

- **Semantic anchors** steer the AI toward well-known engineering methods — Cockburn, EARS, ATAM, Fagan, TDD — instead of ad-hoc prompts. Agent Factory is built on [Semantic Anchors — Spec Driven Development](https://llm-coding.github.io/Semantic-Anchors/spec-driven-development) by Ralf D. Müller, adapted for [arc42](https://arc42.org/) architecture documentation and [Structurizr](https://structurizr.com/) DSL.
- **Deterministic gates** catch provable defects before an LLM spends judgement on them. They are cheap, reproducible, and free of false positives. See [factory/docs/factory-guide.md § Linting and gating](../factory/docs/factory-guide.md#linting-and-gating).
- **Session isolation.** Each agent runs in its own session. A reviewer never sees the author's reasoning — only the artifact.
- **Eichhorst's Principle.** An LLM is a noisy channel. Short transmissions with error correction — compiler, tests, review — beat one long, unchecked prompt. Each skill is one short transmission.

## Project directory tree

```
agent_factory/
├── factory/                          # Canonical toolset. Copied wholesale into any project; never hand-edited there.
│   ├── agents/                       # One .md file per agent
│   ├── skills/                       # One folder per skill, each holding a SKILL.md
│   ├── playbooks/                    # End-to-end flows for common scenarios (bug fix, feature addition, ...)
│   ├── rulebooks/                    # Cross-cutting conventions: commit format, cross-references, ADR style, ...
│   ├── scripts/                      # Deterministic gates (*-lint) plus setup tooling (init-factory, mdformat, ...)
│   ├── config/                       # Templates: AGENTS.md, pre-commit-config.yaml, model-matrix.conf
│   └── INDEX.md                      # Generated catalog of every agent and skill — regenerate with index-lint
├── orchestrator/                     # Python CLI that drives agent sessions — nested sub-project, not distributed by init-factory
│   ├── src/                          # CLI source code
│   ├── tests/                        # CLI tests
│   ├── docs/                         # CLI documentation (own arc42 set, own docs/adr/, own docs/spec/)
│   ├── backlog/                      # CLI backlog and stories
│   └── pyproject.toml                # CLI package configuration
├── backlog/                          # Whole-repo backlog — cross-cutting stories, distinct from orchestrator/backlog/
├── docs/                             # This repo's own whole-repo, cross-cutting docs — distinct from orchestrator/docs/
│   ├── concepts.md                   # This file
│   ├── CONTEXT-MAP.md                # Bounded-context map for this multi-context repo (orchestrator, factory, factory_api)
│   ├── adr/                          # Whole-repo Architecture Decision Records — own sequence, separate from orchestrator/docs/adr/
│   ├── reviews/                      # Retrospective and reconciliation reports
│   └── assets/                       # Diagrams and exported images
├── config/                           # This project's own copy of model-matrix.conf — diverges from factory/
└── README.md
```

`docs/spec/` and `docs/findings/` don't exist at root yet — created lazily, as needed, once `factory/` grows its own spec. See [docs/CONTEXT-MAP.md](CONTEXT-MAP.md).

## Referenced from

- [README.md § How it works](../README.md#how-it-works)
