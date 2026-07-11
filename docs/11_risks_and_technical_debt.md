[back to index](README.md)

# 11. Risks and Technical Debt

## 11.1 Deliberate, named gaps carried from the spec

Full detail: [docs/spec/todos.md](spec/todos.md). None of these block the mechanisms this documentation describes — each is a known, intentional gap, not a defect the architecture papers over.

| ID                                                                                          | Gap                                                                                                                                 | Risk if untouched                                                                                                       |
| ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| [T-01](spec/todos.md#t-01-no-cli-failure-classification-in-trigger)                         | `trigger` returns the invoked CLI's raw exit code — no auth-vs-config-vs-task-failure distinction.                                  | An automated caller (`run-step`, `orchestrator/`) cannot tell "retry this" from "escalate this" without reading output. |
| [T-02](spec/todos.md#t-02-no-concurrent-operator-lock-on-the-marker)                        | The marker is a single flat file with no locking.                                                                                   | Two operators racing an advance/retry against the same marker can interleave incorrectly.                               |
| [T-03](spec/todos.md#t-03-script_exit_zero-condition-type-is-stubbed)                       | `script_exit_zero` entry conditions always evaluate to true — the named script never actually runs.                                 | An FSM author who declares a `script_exit_zero` condition gets no real gating from it; a false sense of enforcement.    |
| [T-04](spec/todos.md#t-04-halt_conditions-types-other-than-max_iterations-are-unenforced)   | `script_failure` and `circular_dependency` `halt_conditions` are declared in `greenfield-development.fsm.yml` but enforced nowhere. | Only the iteration cap actually stops a loop; the other two declared circuit breakers are aspirational text.            |
| [T-05](spec/todos.md#t-05-copilot-clis-three-word-shellcommand-wildcard-syntax-unconfirmed) | Copilot CLI's three-word `shell(...)` wildcard syntax in `trigger`'s allowlist is unconfirmed against a real invocation.            | `trigger --cli copilot` could silently fail to scope as intended if Copilot rejects the flag syntax.                    |

## 11.2 Architectural risks

- **No re-implementation boundary is enforced in code.** [NG1](spec/prd.md#non-goals) states `factory/` does not duplicate `orchestrator/`'s run-state model — but nothing prevents a future change from quietly re-introducing a second, competing notion of "current phase." The [09_architecture_decisions.md § ADR-0002](09_architecture_decisions.md) boundary is a documented convention, not a compiled one.
- **Single-playbook coverage.** Only `greenfield-development.fsm.yml` exists ([NG4](spec/prd.md#non-goals)). Every other playbook runs on prose alone; the harness's actual behaviour under a second, differently-shaped FSM is untested by construction.
- **Stale path reference in the FSM's own audit config.** `greenfield-development.fsm.yml`'s `audit.output_file` still points at `.orchestrator/audit.log` — a naming leftover from before the flow-control inversion this documentation records. No script in `factory/scripts/` currently writes to it (the `audit:` block is declared, not enforced — the same shape as [T-04](spec/todos.md#t-04-halt_conditions-types-other-than-max_iterations-are-unenforced)), so this is presently inert rather than actively misleading, but it should be repointed or removed the next time this FSM file is touched, so it doesn't imply factory writes into orchestrator's own state directory.

## 11.3 Deliberate technical debt (accepted, not oversight)

- **No shared YAML-parsing library.** [08_crosscutting_concepts.md § 8.1](08_crosscutting_concepts.md#81-independent-scripts-over-a-shared-core) — duplication across `transition-lint`, `phase`, and `index-lint` is a chosen cost, not an unnoticed one.
- **`orchestrator/` still keeps its own run-state bookkeeping** (`RUN`, `RUN_LOCK`, single-active-run invariant) even though it no longer owns phase sequencing. This is an intentional narrowing of `orchestrator/`'s responsibility, not full absorption into `factory/` — see [09_architecture_decisions.md § ADR-0002 § Consequences](09_architecture_decisions.md).

## Referenced from

- [docs/spec/todos.md](spec/todos.md)
- [docs/spec/prd.md § 2 Non-Goals](spec/prd.md#2-goals-and-non-goals)
