---
schema_version: 2
title: Orchestrator Consumer Integration
status: accepted
owner: agent-factory
created: 2026-07-30
updated: 2026-07-30
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - factory/scripts/init-factory
    - factory/scripts/run-playbook
    - orchestrator/pyproject.toml
    - orchestrator/src/agent_factory_orchestrator/cli.py

governance:
  assurance: high
  risk_domains:
    - compatibility
    - reliability
    - operations

estimate:
  as_of: 2026-07-30
  basis: decomposition
  confidence: high
  human_review_hours:
    min: 0.5
    max: 1.5
  normalized_tokens:
    min: 20000
    max: 50000
---

# Feature Request: Orchestrator Consumer Integration

## Summary

Distribute the existing orchestrator as a versioned Python tool package and
give initialized projects a thin `uvx` launcher. A consumer obtains one
canonical implementation in an isolated environment instead of receiving a
mutable copy. Claude is the first reference CLI; Codex orchestration remains a
separate capability gap.

## Motivation

The accepted `run-playbook` design names `factory/scripts/run-playbook` as the
delivery boundary, but the implementation currently exists only at
`orchestrator/src/run_playbook.py`. `init-factory` deliberately copies
`factory/` and not the authoring repository's nested `orchestrator/` project.
Consequently, consumer projects receive the FSM, gates, and trigger but not the
executable that connects them.

## Core Principles

- One canonical implementation owns orchestration behavior.
- Orchestrator releases are versioned independently of copied project assets.
- Tool dependencies remain isolated from the consumer project.
- Existing authoring-repository invocations remain compatible.
- Initialization does not mutate global tool state.

## Design

Package the canonical implementation as `agent-factory-orchestrator`, exposing
the `agent-factory-orchestrate` console entry point. Invoke it through `uvx`,
which creates an isolated, cached tool environment.

Ship `factory/scripts/run-playbook` only as a small launcher. It resolves an
exact package source from `AF_ORCHESTRATOR_SOURCE`, defaulting to the
`orchestrator-v0.1.0` tag and `orchestrator/` subdirectory in the Agent Factory
GitHub repository, then delegates to:

```bash
uvx --from "$AF_ORCHESTRATOR_SOURCE" agent-factory-orchestrate
```

The environment override permits development checkouts and pinned Git sources
without changing the consumer repository. `init-factory` copies the launcher
as part of `factory/` but neither installs nor uninstalls a global tool.

Document the consumer command:

```bash
factory/scripts/run-playbook \
  --playbook greenfield-development \
  --from-state PHASE_2_ARCHITECTURE \
  --cli claude
```

## Scope

**In the first release:**

- Package the canonical orchestrator and expose a console entry point.
- Ship a thin, version-pinned `uvx` launcher inside `factory/scripts/`.
- Preserve the existing `orchestrator/src/run_playbook.py` command path.
- Test that a fresh `init-factory` target can invoke the local package through
  the installed launcher.
- Update consumer-facing documentation.
- Exercise the installed path in the standalone Claude reference demo.

**Explicitly deferred (do NOT plan stories for these):**

- A `--cli codex` trigger/orchestrator backend.
- Publishing credentials and release automation for PyPI.
- Automating the human-driven requirements phase.
- Changing FSM, marker, gate, retry, or audit semantics.

## Design Details

The authoring compatibility launcher imports the package from the adjacent
`orchestrator/src/` tree. It contains no orchestration logic.

The Factory launcher contains no orchestration logic and does not create a
persistent tool installation. Its default source is an exact Git tag, never an
implicit branch head or latest release. `AF_ORCHESTRATOR_SOURCE` accepts any
`uvx --from` source, including a local package directory, exact package
version, or other pinned Git URL.

The packaged executable resolves the FSM and helper scripts relative to the
consumer project's current working directory. Invocation from outside the
project root remains unsupported.

## Open Questions

None.

## Completion Criteria

- `uv build orchestrator` produces a valid wheel and source distribution.
- The package exposes `agent-factory-orchestrate`.
- A fresh `init-factory` target contains executable
  `factory/scripts/run-playbook`, whose default source pins an exact Git tag.
- With `AF_ORCHESTRATOR_SOURCE` set to the local package, running the installed
  launcher's `--help` exits zero and advertises Claude and Copilot.
- The existing orchestrator unit tests exercise the packaged implementation.
- The legacy `orchestrator/src/run_playbook.py --help` path still exits zero.
- Factory and orchestrator documentation use the installed command path.
- The standalone demo repository can invoke the packaged CLI with
  `--cli claude` through an explicit local package source and, after the Git
  tag is published, through the default without an authoring-checkout
  reference.

## Guiding Rule

Install the rails; fetch a versioned train when it is time to run.
