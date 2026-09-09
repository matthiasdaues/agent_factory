# Agent Context

## Always (cross-cutting)

### Branching

Factory branching policy and worktree discipline.
Read: factory/rulebooks/conventions/branching-policy.md

### Committing

Commit rules, pre-commit hooks, linting, and formatting.
Read: factory/rulebooks/conventions/commit-conventions.md, .pre-commit-config.yaml, pyproject.toml

### Testing discipline

Pytest and test-driven development under the Factory testing conventions.
Read: docs/testing.yaml, factory/rulebooks/conventions/testing-strategy.md

### Review

Human review and repeat-review discipline for implementation, proposals, and architecture.
Read: factory/rulebooks/conventions/review-loop-discipline.md

### Scope discipline

Proposal-led feature changes governed by the feature-addition playbook.
Read: factory/playbooks/feature-addition.md

### Security

Security review, secret handling, and authorization boundaries.
Read: factory/skills/security-review/SKILL.md

### Architecture governance

Architecture decisions and arc42 documentation.
Read: docs/adr/*.md, docs/arc42/*.md, docs/arc42/architecture.dsl

## Technical concerns

### Python toolchain

Python 3.10 or newer, pytest, Ruff, and uv-based project tooling.
Read: pyproject.toml, packages/orchestrator/pyproject.toml, docs/testing.yaml

### CLI integrations

Generated integrations for Claude Code, GitHub Copilot CLI, Pi, and Codex.
Read: .claude/INDEX.yaml, .github/INDEX.yaml, .pi/INDEX.yaml, .codex/INDEX.yaml

### Factory source and packaging

Agent Factory source lives under `packages/factory/`; `factory/` is an installed copy and MUST NOT be edited.
Read: README.md, packages/factory/README.md, pyproject.toml

### Licensing

Project licensing terms.
Read: LICENSE

## Domain concerns

<!-- Domain concerns are derived from scope-map areas. The planning-agent
     populates this section during backlog creation once explicit domain
     areas exist. -->
