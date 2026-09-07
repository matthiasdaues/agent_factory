# Agent Factory

Without Agent Factory, every AI coding session starts from scratch. The model guesses your stack, invents a workflow, skips the review, and there is no record of what happened or why. You get code, maybe, but no process.

With Agent Factory, specialist agents handle requirements, architecture, planning, implementation, and QA in separate sessions. Authors and reviewers never share a session, so no agent approves its own work. Deterministic scripts check formatting, schemas, traceability, and architecture consistency before anything reaches human review. You approve the decisions that shape the product.

```
Creation is agentic. Validation is deterministic. Decisions remain human.
```

## Try it

Install into any project — new or existing. One command in, one command out.

```bash
# Install
git clone <agent-factory-repo-url> agent_factory
cd agent_factory
./init-factory /path/to/your-project

# Remove — everything the factory added, nothing else
your-project/factory/scripts/remove-factory
```

Removal is precise: a manifest records exactly what was created, and `remove-factory` reverses it. Your code, configuration, and git history are never modified by installation.

The installer asks which AI coding CLI you use and wires up only what you need. Currently supported: Claude Code, GitHub Copilot CLI, Pi, and Codex. It touches two tracked files:

- **`.pre-commit-config.yaml`** — factory hooks are added as a `- repo: local` block, prefixed `agent_factory_hook-` so they are easy to identify. If you already have a pre-commit config, your hooks are left untouched and the factory defers hook setup to the first session.
- **`.gitignore`** — a marker-delimited block is appended, listing the files Agent Factory added.

After installation, open your AI coding CLI in the project directory. If you have an existing codebase, the factory offers a short fitting — a few questions to learn your stack, confirm its guesses, and wire up the right hooks. Skip it if you want; come back to it any time.

For prerequisites (Git, Python 3.10+, uv, an AI coding CLI) and the full inventory of what init-factory creates, see the [factory setup guide](packages/factory/README.md).

## Contributing

To work on Agent Factory itself, clone the repo and run init-factory against it:

```bash
git clone <agent-factory-repo-url> agent_factory
cd agent_factory
./init-factory .
```

This installs a local `factory/` copy (gitignored) so the repo uses its own tooling. Product source lives under `packages/` — the installed `factory/` is the tool, `packages/factory/` is the code you edit. Run `factory/scripts/update-factory` after changes to refresh the installed copy.

## What is in the box

**Agents** are specialist roles — one for requirements, one for architecture, one for planning, and so on. Each runs in its own session with a defined scope, inputs, and outputs. They do not freelance.

**Skills** are focused techniques an agent can invoke: capture project context, run a Fagan inspection, derive a QA strategy from a Gherkin spec, design test scenarios. There are about sixty of them. You do not need to know them upfront — agents reach for the right skill when they need it.

**Playbooks** are step-by-step recipes for common situations: build something new, onboard an existing codebase, add a feature, fix a bug, run a research investigation. Pick the one that fits; it tells the agents what to do and in what order.

**Scripts** are deterministic checks: linting, schema validation, traceability gates, architecture consistency, pre-merge verification. They run automatically through git hooks and phase gates. When they fail, the output is specific and actionable.

**Agent context** is a small set of YAML files where your project declares its stack, workflow, and governance decisions. Agents read these instead of guessing or asking. You fill them in once; they stay current as decisions change.

## Products

This is a monorepo. Each product has its own documentation.

| Product                                                     | What it does                             | Status           |
| ----------------------------------------------------------- | ---------------------------------------- | ---------------- |
| [`packages/factory/`](packages/factory/README.md)           | The installable toolset. Start here.     | Usable           |
| [`packages/orchestrator/`](packages/orchestrator/README.md) | CLI for driving playbooks automatically. | Work in progress |

## Repository internals

Everything below supports this repository's own development. It is maintained using Agent Factory itself. You can ignore it if you are here to use the toolset.

| Directory  | Contents                                                                 |
| ---------- | ------------------------------------------------------------------------ |
| `docs/`    | Architecture (arc42), specifications, ADRs, proposals, findings, reviews |
| `backlog/` | Development story files                                                  |
| `tests/`   | Test suite for factory scripts                                           |
| `config/`  | Repository configuration                                                 |

## License

[MIT](LICENSE). Created by [Matthias Daues](AUTHORS.md).
