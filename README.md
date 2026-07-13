# Agent Factory

Agent Factory turns a rough idea into production-quality code. An AI coding assistant does the work; you approve each step. Agent Factory gives that assistant **agents** (jobs, like "write requirements" or "review the architecture"), **skills** (how-tos an agent follows), and **playbooks** (step-by-step recipes for common situations) — plus automated checks that catch mistakes before you spend time reviewing them.

![Workflow diagram](docs/assets/images/workflow-diagram.svg)

## What's in this repo

- **[`factory/`](factory/README.md)** — the toolset itself: agents, skills, playbooks, checks. This is what you install into your own project. **Start here.**
- **[`orchestrator/`](orchestrator/README.md)** — an optional CLI that automates running the toolset, instead of you driving each agent by hand. Still a work in progress.
- **[`docs/`](docs/concepts.md)** — this repo's own documentation, including how Agent Factory works under the hood and the [arc42 architecture documentation](docs/README.md) for factory flow control.
- **`backlog/`, `config/`** — this repo's own backlog and configuration, built using the factory tooling above.

## Getting started

New to Agent Factory? Go to [factory/README.md](factory/README.md) — it walks you through installing the toolset and running your first playbook.

## How it works

For the ideas behind Agent Factory — why agents work in pairs, what a deterministic gate is, the full phase chain — see [docs/concepts.md](docs/concepts.md).

## License

MIT — see [LICENSE](LICENSE).

Authored by Matthias Daues — see [AUTHORS.md](AUTHORS.md).
