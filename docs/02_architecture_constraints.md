[back to index](README.md)

# 2. Architecture Constraints

## 2.1 Technical Constraints

| Constraint                                                      | Reason                                                                                                                                                                                                                                    |
| --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Every `factory/scripts/*.py` gate is Python 3.8+ stdlib only    | Gates must run with no virtualenv setup — a project adopting the harness installs nothing beyond Python itself.                                                                                                                           |
| macOS and Linux only                                            | `init-factory` relies on native, git-tracked symlinks, which Windows does not support the same way.                                                                                                                                       |
| The marker is a single git-ignored file, not a distributed lock | `.agent-factory/playbook-state.yml` is local, single-machine state. Two operators racing it is a documented, accepted gap — see [T-02](spec/todos.md#t-02-no-concurrent-operator-lock-on-the-marker).                                     |
| No general YAML library                                         | `transition-lint`, `phase`, and `index-lint` each parse their own minimal indentation-based subset (block mappings, block sequences, inline comments) — enough for the `.fsm.yml` shape, no more, keeping the zero-dependency constraint. |
| Diagram export requires Docker                                  | `factory/scripts/structurizr` runs the Structurizr CLI inside a container — a documentation-toolchain dependency, not a runtime one for the gates themselves.                                                                             |

Source: [docs/spec/prd.md § 5 Constraints](spec/prd.md#5-constraints).

## 2.2 Organizational and Process Constraints

- **Monorepo, root-level docs.** This documentation lives at `docs/` (repo root), not inside `factory/` or `orchestrator/` — the established home for factory-level, cross-cutting architecture, alongside `docs/adr/`, `docs/concepts.md`, and `docs/findings/`. See [docs/adr/0001-precommit-monorepo-scoping.md](adr/0001-precommit-monorepo-scoping.md) for the precedent this follows for whole-repo, cross-cutting decisions.
- **Review-loop discipline.** Every repeat pass over a gate re-runs the deterministic check fresh and re-verifies every prior finding individually — never trusts a stale result. See [review-loop-discipline.md § Rule](../factory/rulebooks/conventions/review-loop-discipline.md#rule).
- **Findings drive gates.** A `no_open_findings` entry condition counts only files under `docs/findings/` whose YAML frontmatter `status` is exactly `open` — see [finding-format.md § When to file](../factory/rulebooks/conventions/finding-format.md#when-to-file).

## 2.3 Conventions

- [foundational-principles.md](../factory/rulebooks/conventions/foundational-principles.md) — plain prose, Eichhorst's Principle, YAGNI.
- [cross-reference-format.md](../factory/rulebooks/conventions/cross-reference-format.md) — every reference to another artifact is a full markdown link, anchored to its section.
- [markdown-formatting.md](../factory/rulebooks/conventions/markdown-formatting.md) — every written markdown file is formatted with `factory/scripts/mdformat --number` at write time, not deferred.
- [commit-conventions.md](../factory/rulebooks/conventions/commit-conventions.md) — every implementation commit carries a story/bug/spec ID.
- [state-machine-notation.md](../factory/rulebooks/conventions/state-machine-notation.md) — pseudocode is authoritative for state machines; Mermaid is derived, never authored first.

## Referenced from

- [docs/spec/prd.md § 5 Constraints](spec/prd.md#5-constraints)
- [docs/adr/0001-precommit-monorepo-scoping.md](adr/0001-precommit-monorepo-scoping.md)
