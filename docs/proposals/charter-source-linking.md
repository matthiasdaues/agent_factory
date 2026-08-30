---
schema_version: 2
title: Charter Source Linking for LLM Depth Access
status: draft
owner: matthiasdaues
created: 2026-08-25
updated: 2026-08-25
supersedes:

impact:
  scope: local
  architecture_change: false
  external_contract_change: false
  boundaries:
    - docs/charter/tech-stack.md
    - docs/charter/development.md
    - docs/charter/house-rules.md

governance:
  assurance: routine
  risk_domains:
    - reliability

estimate:
  as_of: 2026-08-25
  basis: judgment
  confidence: medium
  human_review_hours:
    min: 0.5
    max: 1.0
  normalized_tokens:
    min: 2000
    max: 5000
  estimated_consumption:
    min: 20000
    max: 50000
    overhead_multiplier: 10
    playbook: feature-addition
---

# Feature Request: Charter Source Linking for LLM Depth Access

## Summary

Give LLM agents a fast path from charter prose to the canonical config files that express the same decisions in detail, without duplicating information in two places. The charter stays human-readable; the machine gets pointers to go deeper.

## Motivation

Today the kit-manager extracts decisions from config files (`pyproject.toml`, `.pre-commit-config.yaml`, `package.json`, etc.) and writes them as prose into charter sections. This creates double bookkeeping: the config file is the source of truth, but the charter restates it in summary form. When configs change, the prose drifts silently.

A colleague's observation: the extracts are largely correct but already exist in compressed form in the config files themselves. Maintaining sync between charter prose and config files is fragile — experience shows LLMs struggle to keep derived documentation consistent over time.

## Core Principles

- The charter is a **human document** — prose stays for human consumption.
- Config files are the **single source of truth** for implementable detail.
- LLM agents should reach detail by **dereferencing**, not by relying on copied summaries.
- The solution must not create a new maintenance burden that reproduces the sync problem at a meta level.

## Design

Three candidate approaches are presented. **No decision has been made** — this proposal exists to frame the tradeoffs for stakeholder review.

### Option A: Frontmatter `sources` array

Add a `sources` field to each charter file's YAML frontmatter:

```yaml
---
title: Tech Stack
sources:
  - path: pyproject.toml
    informs: [languages, dependencies, build-system]
  - path: .python-version
    informs: [languages]
  - path: docker-compose.yml
    informs: [data-stores, infrastructure]
---
```

**Pro:**

- Structured, machine-parseable, lintable (validate paths exist).
- Consistent with existing frontmatter conventions across agents, skills, stories.
- Kit-manager can update programmatically.
- Per-file granularity with explicit section mapping.

**Con:**

- The `informs` mapping is itself a maintenance artifact that can drift — config files gain new tool sections, nobody updates frontmatter.
- Adds coupling: adding/removing config files can break charter-lint.
- Frontmatter becomes a secondary data model (config file → frontmatter mapping → prose) — three layers instead of two.

### Option B: Agent instruction (no artifact change)

Teach the kit-manager and downstream agents (via skill or rulebook instruction) to always check canonical config files before answering questions about tech decisions. No links stored in the charter at all.

```
# In kit-manager or relevant skill:
Before answering questions about tech stack, CI, or tooling,
read the project's config files directly.
```

**Pro:**

- Zero maintenance burden — no new artifact to keep in sync.
- LLM already has filesystem access; explicit links are a crutch for behavior that should be a standing instruction.
- No false sense of completeness (a link list can never be exhaustive).
- Simplest possible change.

**Con:**

- Relies on agent behavior being consistent across sessions and models — no guarantee the instruction is followed every time.
- No discoverability for humans — a new team member reading the charter gets no hint that `pyproject.toml` is the authority for the languages section.
- Harder to validate mechanically (no lint can check "did the agent actually read the config?").

### Option C: Hybrid — flat path list in frontmatter, no `informs` mapping

A middle ground: list source paths in frontmatter without mapping them to specific sections. The LLM decides which file is relevant to which question.

```yaml
---
title: Tech Stack
sources:
  - pyproject.toml
  - .python-version
  - package.json
  - docker-compose.yml
  - .pre-commit-config.yaml
---
```

**Pro:**

- Machine-parseable and lintable (path existence only).
- Lower maintenance than Option A — no section-mapping to drift.
- Provides discoverability for humans and agents alike.
- Simple for the kit-manager to emit during scaffold/scan.

**Con:**

- Still a list that can become stale (though less fragile than Option A).
- LLM must infer relevance per query — trivial for current models, but adds a (small) reasoning step.
- Doesn't solve the fundamental question: if the LLM can find these files anyway, why list them?

## Scope

**In the first release:**

- Decision on which option (or combination) to adopt.
- Implementation in charter templates and kit-manager workflow.
- Update to `charter-lint` if the chosen option requires validation.

**Explicitly deferred (do NOT plan stories for these):**

- Automated drift detection between charter prose and config file contents.
- Bidirectional sync (config changes auto-updating charter prose).

## Open Questions

- Is the maintenance cost of any link list justified given that LLMs have direct filesystem access?
- Should `charter-lint` enforce source-list freshness, or is a stale list acceptable (still better than no list)?
- Does the answer differ by charter file? (`tech-stack.md` has many linkable sources; `house-rules.md` may have few or none.)

## Completion Criteria

- Stakeholder decision recorded (option chosen or hybrid defined).
- Charter templates updated to reflect the chosen approach.
- Kit-manager emits source references (if an artifact-based option is chosen) during scaffold and scan modes.
- `charter-lint` updated if validation is part of the chosen option.

## Guiding Rule

The charter is for humans; config files are for machines. Any bridge between them must cost less to maintain than the drift it prevents.
