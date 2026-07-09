---
name: dev-workflow
description: Semantic-anchor-driven software development workflow. A router skill that maps phases to skills and agents.
disable-model-invocation: true
---

# Dev Workflow

A router for the **Semantic Anchor driven** development lifecycle. See [orchestrator/USAGE.md](../../orchestrator/USAGE.md) for how to wire agents into your CLI and run the full chain.

Two ways to use this workflow:

- **With agents** — activate one agent per session, follow the handoff chain. The agent invokes skills automatically.
- **Without agents** — invoke skills directly by name. You are the orchestrator.

## Agent chain

Eight agents, each in its own session. Each author/reviewer pair (spec, architecture) loops until its review is clean. Reconciliation precedes formal code review.

```
requirements ↔ spec-review → architecture ↔ architecture-review → planning → implementation → reconciliation ↔ qa
 (session 1)    (session 2)    (session 3)     (session 4+)        (session N)  (session N+1)   (session N+2)  (session N+3)
```

| Agent                                                                    | Phase | Skills used                                                                                             |
| ------------------------------------------------------------------------ | ----- | ------------------------------------------------------------------------------------------------------- |
| [`requirements-agent`](../../agents/requirements-agent.md)               | 1     | `capture-vision`, `clarify-requirements` (→ `grill-me` / `grill-with-docs`), `write-prd`, `derive-spec` |
| [`spec-review-agent`](../../agents/spec-review-agent.md)                 | 1     | `inspect-spec` — **separate session from author**                                                       |
| [`architecture-agent`](../../agents/architecture-agent.md)               | 2a    | `scaffold-arc42`, `write-adr`                                                                           |
| [`architecture-review-agent`](../../agents/architecture-review-agent.md) | 2b    | `atam-review` — **separate session from architect**                                                     |
| [`planning-agent`](../../agents/planning-agent.md)                       | 3     | `create-backlog`                                                                                        |
| [`implementation-agent`](../../agents/implementation-agent.md)           | 4     | — (dispatcher: spawns developer-agents in parallel waves)                                               |
| [`developer-agent`](../../agents/developer-agent.md)                     | 4     | `implement-issue`, `spec-feedback` — spawned per story by dispatcher                                    |
| [`reconciliation-agent`](../../agents/reconciliation-agent.md)           | 4     | `reconcile-spec` — **separate session from implementer**                                                |
| [`qa-agent`](../../agents/qa-agent.md)                                   | 5     | `fagan-review`, `security-review`, `bug-hunt`                                                           |

## Skill index

### Phase 1 — Requirements Discovery

| Skill                  | When to use                                                                                                                                |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `capture-vision`       | Starting a new project — capture the idea before clarifying                                                                                |
| `clarify-requirements` | Select the clarification branch — runs **Socratic Method** inline, or delegates to `grill-me` / `grill-with-docs`                          |
| `grill-me`             | Deep clarification — greenfield (no existing docs). Delegates to `grilling`.                                                               |
| `grill-with-docs`      | Deep clarification — brownfield (existing `CONTEXT.md`/ADRs). Delegates to `grilling` + `domain-modeling`.                                 |
| `write-prd`            | Formalise clarified requirements as a PRD                                                                                                  |
| `derive-spec`          | Derive the full specification chain from the PRD: actor-goals → **Cockburn Use Cases** → system use cases (**EARS**) → supplementary specs |
| `inspect-spec`         | Review the spec — deterministic `spec-lint` + semantic inspection against requirements-quality characteristics (**separate session**)      |

### Phase 2 — Architecture

| Skill                   | When to use                                                                                      |
| ----------------------- | ------------------------------------------------------------------------------------------------ |
| `scaffold-arc42`        | Create **arc42** documentation and **Structurizr** **C4** model from the spec                    |
| `write-adr`             | Document a single architecture decision (**ADR according to Nygard** + **Pugh Matrix**)          |
| `maintain-architecture` | Update architecture documentation to address review findings on subsequent passes                |
| `atam-review`           | Evaluate architecture against quality attributes (**ATAM**) — **must run in a separate session** |

### Phase 3 — Planning

| Skill            | When to use                                                                        |
| ---------------- | ---------------------------------------------------------------------------------- |
| `create-backlog` | Break spec + architecture into `backlog/ST-*.md` stories (**INVEST** + **MoSCoW**) |

### Phase 4 — Implementation

| Skill             | When to use                                                                 |
| ----------------- | --------------------------------------------------------------------------- |
| `implement-issue` | Pick an issue, analyse it, implement with **TDD**, commit                   |
| `spec-feedback`   | After implementing — check whether spec or architecture needs updating      |
| `reconcile-spec`  | After full implementation phase — comprehensive code-vs-spec reconciliation |

### Phase 5 — Quality Assurance

| Skill             | When to use                                              |
| ----------------- | -------------------------------------------------------- |
| `fagan-review`    | Structured code review (**Fagan Inspection**)            |
| `security-review` | **OWASP Top 10** security review                         |
| `bug-hunt`        | Exploratory testing → bug filing → bug fix → retest loop |

### Phase 0 — Utility

Composable primitives invoked by name from other skills, not tied to one phase:

| Skill             | When to use                                                                                                               |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `grilling`        | Interview mechanics behind `grill-me` / `grill-with-docs`                                                                 |
| `domain-modeling` | Maintain `CONTEXT.md` / `docs/adr/` — used by `grill-with-docs` and by `reconcile-spec`'s terminology-drift step          |
| `retrospective`   | Run via [`coaching-agent`](../../agents/coaching-agent.md) — on-demand session retrospective, not part of the phase chain |

## Derivation chain

Each phase feeds the next. The traceability chain is:

```
CONTEXT.md → PRD → Actor-Goal List → Persona Use Cases
  → System Use Cases → Supplementary Specs → arc42 → Backlog → Code → Reviews
```

All downstream artifacts trace back to their source via Use Case IDs.

## Why small steps

**Eichhorst's Principle** (Shannon's noisy channel theorem applied to LLM coding): an LLM is a noisy, non-deterministic channel. Short transmissions with error correction (compiler → tests → review) are far more reliable than one long, unchecked transmission. Each skill in this workflow is one short transmission. Better tests beat better prompts.

**YAGNI**, combined: build only what's specified, in the smallest verified step that specification allows.
