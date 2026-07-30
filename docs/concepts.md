# How Agent Factory Works

The theory behind Agent Factory, and a map of this repo. If you are brand new, start with the [beginner's introduction](beginner-intro.md) — a plain-language on-ramp. If you want to start using the toolset, go to [factory/README.md](../factory/README.md) instead. This page is background, not a tutorial.

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

Alongside this production chain runs one standalone workflow that is not a step in it: **Research** (phase 6). The `research-topic` playbook drives a falsification-driven research effort — from an approved brief to a validated report — with its own agents (`research-orchestrator`, `researcher`, `claim-reviewer`, `research-report-writer`) and a three-stage schema → policy → semantic validation gate. A claim reaches the report only after surviving a serious attempt to refute it. See [factory/docs/factory-guide.md § The research workflow](../factory/docs/factory-guide.md#the-research-workflow).

`factory/` itself — the state-machine harness, dispatch mechanism, and generated catalog that enforce phase order and cap review loops — has its own specification and its own arc42 architecture documentation. See [docs/spec/prd.md](spec/prd.md) and [docs/README.md](README.md).

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
│   ├── rulebooks/                    # conventions/ (prose rules + research policies), templates/ (artifact skeletons), schemas/ (JSON-Schema data contracts)
│   ├── scripts/                      # Deterministic gates (*-lint, plus schema-validate/policy-validate) and setup tooling (init-factory, mdformat, ...)
│   ├── config/                       # Templates: AGENTS.md, pre-commit-config.yaml, model.conf
│   └── INDEX.yaml                     # Generated catalog of every agent, skill, playbook, and rulebook with token counts — regenerate with index-lint
├── orchestrator/                     # Versioned Python tool package; invoked from consumer projects through factory/scripts/run-playbook and uvx
│   ├── src/                          # CLI source code
│   ├── tests/                        # CLI tests
│   ├── docs/                         # CLI documentation (own arc42 set, own docs/adr/, own docs/spec/)
│   ├── backlog/                      # CLI backlog and stories
│   └── pyproject.toml                # CLI package configuration
├── backlog/                          # Whole-repo backlog — cross-cutting stories, distinct from orchestrator/backlog/
├── docs/                             # This repo's own whole-repo, cross-cutting docs — distinct from orchestrator/docs/
│   ├── beginner-intro.md             # Plain-language on-ramp for first-time users — read before any command
│   ├── concepts.md                   # This file
│   ├── CONTEXT-MAP.md                # Bounded-context map for this multi-context repo (orchestrator, factory, factory_api)
│   ├── README.md                     # arc42 architecture documentation for Factory Flow Control — table of contents
│   ├── 01_introduction_and_goals.md  # ...through 12_glossary.md — the 12 arc42 chapters
│   ├── architecture.dsl              # Structurizr C4 model — versioned source of truth for the diagrams
│   ├── spec/                         # Factory Flow Control's specification (PRD, use cases, supplementary specs)
│   ├── adr/                          # Whole-repo Architecture Decision Records — own sequence, separate from orchestrator/docs/adr/
│   ├── findings/                     # Filed findings (e.g. RECON-*.md, FAGAN-*.md), created lazily as needed
│   ├── reviews/                      # Retrospective and reconciliation reports
│   └── assets/                       # Diagrams and exported images
├── config/                           # This project's own copy of model.conf — diverges from factory/
└── README.md
```

See [docs/CONTEXT-MAP.md](CONTEXT-MAP.md) for the bounded-context map.

## Referenced from

- [README.md § How it works](../README.md#how-it-works)
- [docs/spec/prd.md § Problem Statement](spec/prd.md#1-problem-statement)
