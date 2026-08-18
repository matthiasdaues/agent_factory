---
schema_version: 2
title: Project Charter
status: open
owner: md@matthiasdaues.de
created: 2026-08-18
updated: 2026-08-18
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: false
  boundaries:
    - factory/playbooks/greenfield-development.md
    - factory/playbooks/feature-addition.md
    - factory/playbooks/brownfield-onboarding.md
    - factory/agents/planning-agent.md
    - factory/agents/developer-agent.md
    - factory/agents/implementation-agent.md
    - factory/agents/architecture-agent.md
    - factory/agents/requirements-agent.md
    - factory/skills/create-backlog/SKILL.md
    - factory/skills/validate/SKILL.md
    - factory/rulebooks/templates/story.md
    - factory/rulebooks/rules.md
    - factory/scripts/backlog-lint

governance:
  assurance: routine
  risk_domains:
    - compatibility

estimate:
  as_of: 2026-08-18
  basis: judgment
  confidence: medium
  human_review_hours:
    min: 1.0
    max: 2.0
  normalized_tokens:
    min: 8000
    max: 15000
  estimated_consumption:
    min: 200000
    max: 375000
    overhead_multiplier: 25
    playbook: feature-addition
---

# Feature Request: Project Charter

## Summary

Introduce a project charter — three practical documents that answer what a developer needs to know before writing the first line of code: what's the stack, how do we work, and what are the rules. The charter is scaffolded early, filled incrementally across phases, and approved by the stakeholder before planning begins. It produces Epic 0 — the mise en place of setup stories that must be complete before any feature story starts.

## Motivation

A builder arrives at a construction site with a blueprint. Before laying the first brick, two things must happen: the materials must be chosen (concrete or quarried limestone?) and the site must be prepared (scaffolding up, tools laid out, safety rules posted). The blueprint does not specify these — it describes the structure, not the materials or the work practices.

In software, this is the same gap. The architecture says "an API gateway talks to a persistence layer." It does not say "FastAPI, PostgreSQL 16, pytest, ruff, GitHub Actions, Docker on Hetzner." Those are material and tooling decisions that must be made explicitly, and each one produces setup work that must be done before any feature can be built.

Today these decisions float through conversation. The planning-agent writes stories like "implement the user endpoint" without knowing whether that means FastAPI or Express, pytest or Jest. The developer-agent starts coding without knowing the linter, the test runner, or the repo layout. Both discover these things mid-flight, guess, or re-ask — wasting sessions and producing inconsistent results.

The deeper problem: there is no Epic 0. Every backlog starts with feature stories, but nobody has scaffolded the project. There is no `pyproject.toml`, no `Makefile`, no CI pipeline, no test harness, no `.env.example`. The first developer-agent trips over missing infrastructure that should have been laid out before any feature work began.

A line cook does not start cooking when the first order comes in. They prepare the mise en place — every ingredient prepped, every tool in its place, every station ready. Epic 0 is the mise en place of a software project.

## Core Principles

- Architecture stays technology-agnostic — it describes structure, not materials.
- The charter is what a developer reads on day one. It answers three questions: what's the stack, how do we work, what are the rules.
- The charter is scaffolded early and filled incrementally. Different documents fill at different rates across phases. A stakeholder approval gate before planning confirms the charter is decision-complete and correct.
- The charter produces Epic 0 — concrete scaffolding stories derived during the completeness sweep before planning. Epic 0 must be complete before feature stories begin.
- Three documents because three concerns change at different rates: tech-stack with major pivots, development conventions with tooling evolution, house-rules with team composition.
- Templated so it is lintable. But the template is a checklist of questions to answer, not a form to fill.

## Design

### Charter folder: `docs/charter/`

Three documents. Each reads like a practical reference page.

#### 1. `docs/charter/tech-stack.md` — What we build with

The technologies. Names and versions. What you would put on a job posting. A developer reads this and knows what to install, what versions to pin, and what is off the table.

Sections:

- **Languages & Runtimes** — which languages, which versions, why. ("Python 3.12 — team expertise, existing codebase. No Java.")
- **Frameworks** — application framework, API framework, ORM. ("FastAPI for HTTP, SQLAlchemy for ORM. No Django — too heavy for this scope.")
- **Data Stores** — databases, caches, queues, object stores, and what role each plays. ("PostgreSQL 16 for primary data. Redis for session cache. No managed NoSQL.")
- **Infrastructure** — cloud provider, compute model, container runtime, region constraints. ("Hetzner Cloud, Docker, EU-only.")
- **Existing Systems** — things that already exist and must be integrated. ("Auth via existing Keycloak at auth.example.com. Payment via Stripe API v2.")
- **Licensing & Exclusions** — what is ruled out and why. ("No AGPL dependencies. No vendor lock-in to a single cloud provider's managed services.")

**Principle**: tech-stack is what ships. If you removed it, the application would not run.

#### 2. `docs/charter/development.md` — How we work here

How you use the technologies to work. The composition, the wiring, the commands, the workflow. A developer reads this and can set up, run, test, and ship code on day one.

Sections:

- **Repository Layout** — where things live. ("Monorepo. `src/` for application code, `tests/` mirrors `src/`, `infra/` for Terraform, `docs/` for documentation.")
- **Getting Started** — how to set up a development environment. ("Clone, `make setup`, requires Python 3.12 and Docker. `.env.example` → `.env`.")
- **Running the Project** — how to start it locally. ("`make run` or `docker compose up`. Five containers: app, agent, db, toxiproxy, redis. Shared network. Persistent volume for db data. API at localhost:8000.")
- **Testing** — what framework, how to run tests, what coverage means here. ("pytest. `make test`. Coverage target: meaningful coverage of business logic, not a percentage.")
- **Linting & Formatting** — what tools, how to run them. ("ruff for linting and formatting. `make lint`. Config in `pyproject.toml`. Pre-commit hook enforces.")
- **CI/CD** — where it runs, what the pipeline does, how to deploy. ("GitHub Actions. `.github/workflows/ci.yml`. Merges to main auto-deploy to staging. Prod is manual promote.")
- **Branching** — anything beyond Factory defaults. ("Factory branching policy applies. Release branches: `release/vX.Y.Z` cut from main.")

**Principle**: development is what supports the work. If you removed it, the application still runs but you cannot develop it effectively. The same technology may appear in both documents in different roles: tech-stack says "Docker" (the choice); development says "five containers, shared network, persistent volume, `make up`" (the arrangement).

**Two-phase nature**: before Epic 0, development.md records decisions ("pytest for testing," "ruff for linting"). After Epic 0, the actual commands and paths are known. The completeness sweep derives an explicit Epic 0 story — "Update development.md with actual commands and paths" — that depends on all other Epic 0 stories. This is the last story in Epic 0; when it is done, development.md is fact, not intent.

#### 3. `docs/charter/house-rules.md` — How we work together

The team rules. Apply to whoever is doing the work — human or AI. Each rule states who it binds and what it means for the workflow. Not organized by actor (human vs AI) but by concern.

Sections:

- **Commits & PRs** — size, frequency, WIP limits, branch protection. ("Commits and PRs must be small enough to review. No more than 5 PRs open. Dev and main branches are protected.")
- **Review & Approval** — who reviews what, role-based gates, SLAs. ("PRs must be explained verbally to the reviewer. Design guide PRs reviewed by Michelle. Frontend architecture reviewed by RB or SCN. Risky PRs reviewed by two humans. Max 2 days between opening a PR and feedback.")
- **Testing Discipline** — who writes tests, when, relationship to implementation, relationship between Factory and CI. ("Test cases written manually before the code is implemented. Tests also run in CI. Factory process and CI use the same test triggers. Does the default TDD workflow apply, or is there a different testing discipline?")
- **Architecture Governance** — docs as truth, ADR discipline, architect approval. ("Architecture docs are truth. The agent factory must identify architecture decisions and commit them as ADRs reviewed by two humans. Proposed or unavoidable architecture changes must be reviewed and approved by the architect.")
- **Scope & Boundaries** — what requires human involvement, Factory-context mandate. ("AI coding must be done in the Factory context. Missing capability can be added; missing consistency is hard to remedy.")

### Incremental filling

The charter is not captured in one step. It is scaffolded early and filled as decisions emerge across phases:

- **Vision capture**: stakeholder often knows languages, maybe framework, some house rules. `capture-charter --init` creates the skeleton; initial answers fill what is known.
- **Requirements / specification**: requirements work may reveal data store needs, integration constraints, licensing restrictions. Agents invoke `update-charter` to record decisions.
- **Architecture**: infrastructure decisions solidify. Deployment topology clarifies cloud provider, container strategy, region constraints. Architecture-agent invokes `update-charter` for tech-stack entries it settles.
- **Planning gate**: `capture-charter` (completeness sweep) fills remaining gaps, derives Epic 0, stakeholder approves.

Different documents fill at different rates:

- **tech-stack.md** — starts filling during vision, sharpens during requirements, solidifies during architecture.
- **development.md** — mostly records decisions close to the planning gate, because it is about how you work, not what you build.
- **house-rules.md** — accumulates opportunistically. A rule may surface during any phase when human intervention yields a norm for the project.

### Skill: `capture-charter`

Lifecycle skill with two modes:

**`capture-charter --init`** (greenfield): creates the three files from templates. Optionally fills answers already known from the vision conversation. Sections without answers get "To be decided."

**`capture-charter --init --scan`** (brownfield): scans the codebase before creating the skeleton. Pre-populates from what it finds:

- `pyproject.toml` / `package.json` / `go.mod` → tech-stack languages and frameworks
- `docker-compose.yml` → development topology
- `.github/workflows/` / `.gitlab-ci.yml` → CI/CD
- `ruff.toml` / `.eslintrc` / `pyproject.toml [tool.ruff]` → linting
- `pytest.ini` / `conftest.py` / `jest.config` → test framework
- `.pre-commit-config.yaml` → pre-commit setup

Presents findings for stakeholder confirmation: "I found Python 3.11, FastAPI, PostgreSQL, ruff, pytest, GitHub Actions. Confirm, correct, or add what I missed." No Epic 0 derivation — the mise en place already exists.

**`capture-charter`** (no flag — completeness sweep): walks through every "To be decided" entry and forces a decision or explicit deferral. For each charter decision, checks whether the corresponding artifact already exists in the project — if it does, no setup story (or a smaller "verify/adapt" story). If it does not, derives an Epic 0 story. The stakeholder can point at existing work: "use this pre-commit config I prepared," "adapt this Makefile from the other project."

The skill runs in the orchestrating session, not a spawned subagent — the stakeholder must be present.

### Skill: `update-charter`

Shared skill, invokable by any agent during any phase — same pattern as `domain-modeling` maintains `docs/CONTEXT.md`. The skill owns the write target (`docs/charter/*.md`), not the invoking agent. Agents do not need `docs/charter/*.md` in their `outputs:`.

Workflow: read the current charter state, update the relevant section, preserve what is already there, commit. One commit per update, attributable to the phase that made the decision. Commit message format: `docs: update charter <document> — <section> (<ID>)` where `<ID>` is the story, finding, or phase context that triggered the update (e.g., `SPEC-0003`, `ATAM-0001`). When no ID applies (e.g., during initial vision capture), use `docs: update charter <document> — <section>`.

### Epic 0 — The mise en place

Every concrete decision in the charter that requires a file, configuration, or infrastructure to exist maps to a setup story. The `capture-charter` completeness sweep derives Epic 0 stories and writes them to `backlog/ST-NNNN.md`. Epic 0 stories use the lowest available ST numbers (starting from ST-0001 in a new project). The planning-agent, which runs after the completeness sweep, allocates subsequent ST numbers for feature stories — it reads the existing backlog to find the next available ID, same as it does today when stories already exist.

Epic 0 stories use the standard story format:

- `epic: "Epic 0 — Project Setup"`
- `tier: economy`
- `status: pending`
- MoSCoW: all `must-have`
- `traces:` left empty — the epic label is sufficient identification
- Acceptance criteria describe setup verification ("pyproject.toml exists with pinned dependencies and `pip install -e .` succeeds")

The derivation is direct but accounts for existing artifacts:

| Charter decision                 | If missing                                                                            | If exists                                     |
| -------------------------------- | ------------------------------------------------------------------------------------- | --------------------------------------------- |
| Python 3.12, FastAPI, SQLAlchemy | Story: initialize `pyproject.toml` with core dependencies and version pins            | No story, or: verify versions match charter   |
| pytest, `make test`              | Story: set up test harness — `conftest.py`, Makefile test target, directory structure | No story                                      |
| ruff, pre-commit                 | Story: configure linter, formatter, and pre-commit hooks                              | No story, or: verify config matches charter   |
| PostgreSQL 16, Redis             | Story: create `docker-compose.yml` with database and cache services                   | No story, or: verify topology matches charter |
| GitHub Actions CI                | Story: create `.github/workflows/ci.yml` — lint, test, build stages                   | No story                                      |
| Monorepo layout                  | Story: scaffold `src/`, `tests/`, `infra/`, `docs/` directory structure               | No story                                      |

Epic 0 stories are the first wave of implementation — no feature story may begin until all `must-have` Epic 0 stories are done. The implementation-agent schedules them as wave 1. Feature stories carry `deps:` on the final Epic 0 story (the "update development.md" story) to enforce sequencing mechanically — the implementation-agent's existing dependency resolution handles the rest.

### Planning gate

Before planning begins, three conditions must be met:

1. **`charter-lint --planning-gate` passes** — tech-stack and development are decision-complete (no "To be decided" entries). House-rules may have open items without blocking planning.
2. **Stakeholder approves** charter and Epic 0 stories together — "these are the decisions, this is the setup work they imply, begin."
3. **`charter-lint` structural check passes** — all three files exist, required sections present, no section empty, frontmatter parses.

This is the same approval pattern as backlog approval in the greenfield playbook Step 3.3.

### Deterministic gate: `charter-lint`

Script at `factory/scripts/charter-lint`. Two modes:

**Default mode** — structural validation:

- All three files exist under `docs/charter/`
- Required sections present per template
- No section is empty (must have content, even if "No constraint" or "To be decided")
- YAML frontmatter parses cleanly

**`--planning-gate` mode** — stricter check:

- All default checks pass
- tech-stack.md has no "To be decided" entries
- development.md has no "To be decided" entries
- house-rules.md may have "To be decided" entries (they do not block planning)

Exit 0 = pass, non-zero = findings on stderr. Integrated into the `validate` skill.

Minimal for the first release. Grow from practice — if specific mechanical checks would have caught real problems, add them later.

### Templates

Three templates at:

- `factory/rulebooks/templates/charter-tech-stack.md`
- `factory/rulebooks/templates/charter-development.md`
- `factory/rulebooks/templates/charter-house-rules.md`

Each is the skeleton of its document — headings with one-line comment prompts describing what belongs there. The prompts are HTML comments so they disappear from the finished document.

### Story template: `tests:` field

Add an optional `tests:` field to `backlog/ST-NNNN.md` frontmatter. Lists pre-existing test files that cover this story's acceptance criteria.

When `tests:` is present and non-empty, the developer-agent reads the listed test files as its specification and implements code to make them pass (Green, not Red-Green). When `tests:` is absent or empty, the developer-agent follows the default TDD workflow.

`backlog-lint` validates that `tests:` is an array (when present) and that listed files exist.

**Timing and ownership**: when house-rules mandate "test cases written manually before code," humans write the tests before planning begins — the tests are part of the approved mise en place, like any other pre-existing artifact. The planning-agent, when creating stories, checks whether tests already exist for the acceptance criteria and records them in `tests:`. If tests arrive after backlog approval (e.g., the human writes them between planning and implementation), the story is amended with the test paths before implementation dispatch — same as any other story amendment. The planning-agent owns populating `tests:` at story creation time; the orchestrating session owns amendments after backlog approval.

### Workflow insertion

**Greenfield**:

| When                                   | What                                                                                                                              |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| New Step 1.0 (before current Step 1.1) | `capture-charter --init` — scaffold skeleton, fill what is known                                                                  |
| During requirements, architecture      | Agents invoke `update-charter` as decisions emerge                                                                                |
| After architecture review passes       | `capture-charter` completeness sweep — fill gaps, derive Epic 0                                                                   |
| Before planning                        | Planning gate: `charter-lint --planning-gate` + stakeholder approval of charter and Epic 0                                        |
| Planning                               | Planning-agent finds Epic 0 stories in backlog, derives feature stories, marks feature stories' `deps:` on the final Epic 0 story |
| Implementation wave 1                  | Epic 0 stories implemented. No feature stories until wave 1 complete                                                              |

**Feature-addition**: at proposal intake (Step 0.1), ask: "Does this feature require charter amendments?" If yes, amend via `update-charter`, re-run the planning gate for changed documents, derive any additional Epic 0 stories for new setup work. If no, proceed — the feature works within the settled mise en place.

**Brownfield-onboarding**: `capture-charter --init --scan` after the Phase 5 ATAM architecture review passes (the brownfield playbook's final architecture quality gate). Scans codebase, pre-populates skeleton, stakeholder confirms. No Epic 0 — the mise en place already exists in code. The planning gate (`charter-lint --planning-gate` + stakeholder approval) runs before any specification or planning work that follows onboarding.

### Relationship to arc42 chapter 2

Arc42 ch.02 (Architecture Constraints) captures constraints that shaped the architecture — the "why" behind structural decisions. The charter captures constraints that shape implementation — the "what with" and "how." Where they overlap (e.g., "EU-only" is both an architectural constraint and a tech-stack constraint), ch.2 references the charter entry. One direction: ch.2 may reference charter, charter does not reference ch.2.

### Downstream consumers

- **planning-agent**: reads `docs/charter/*.md`. Finds Epic 0 stories already in backlog. Derives feature stories with concrete acceptance criteria that name the actual test framework, deployment target, and API framework. Checks for pre-existing tests when house-rules mandate it.
- **developer-agent**: reads charter before writing code. Knows what to install, how to run tests, what conventions to follow. When `tests:` field is present on a story, reads those test files as the spec and implements to pass. Epic 0 stories are implemented like any other story.
- **implementation-agent**: reads charter to inform model selection and dispatch. Schedules Epic 0 as wave 1 — no feature stories until wave 1 is complete.
- **architecture-agent**: does NOT read charter during initial architecture creation (architecture stays abstract). May read on remediation passes to check consistency. Ch.2 references charter entries where they overlap.

### Charter amendments

No mechanical versioning or amendment tracking for the first release. Git history tracks changes. Team discipline ensures stakeholder re-approval before affected stories proceed. If practice shows drift is a real problem, add a mechanical gate later.

## Scope

**In the first release:**

- `docs/charter/` folder with three documents
- Three templates at `factory/rulebooks/templates/charter-*.md`
- Skill `capture-charter` with three modes: `--init`, `--init --scan`, completeness sweep
- Skill `update-charter` as shared skill invokable by any agent
- Script `factory/scripts/charter-lint` with default and `--planning-gate` modes
- Story template updated: optional `tests:` field added to frontmatter
- `backlog-lint` updated: validates `tests:` is an array when present, verifies listed files exist
- `requirements-agent.md` updated: `update-charter` added to `skills:`
- `architecture-agent.md` updated: `update-charter` added to `skills:`
- `planning-agent.md` and `create-backlog` skill updated: read charter, acknowledge pre-existing tests when creating stories
- `developer-agent.md` updated: `docs/charter/*.md` in `inputs:`, respects `tests:` field for pre-existing test workflow
- `implementation-agent.md` updated: `docs/charter/*.md` in `inputs:`, schedule Epic 0 as wave 1
- Greenfield playbook: charter init after vision, completeness sweep + planning gate before planning
- Feature-addition playbook: charter review question at proposal intake
- Brownfield-onboarding playbook: `--init --scan` after the ATAM architecture review passes
- Rule in `rules.md` Coding section: planning MUST derive Epic 0 from charter; implementation MUST complete Epic 0 before feature stories; agents MUST read house-rules and adjust workflow accordingly
- `validate` skill: runs `charter-lint` when charter exists

**Explicitly deferred (do NOT plan stories for these):**

- Charter-vs-code drift detection (automated consistency checking post-implementation)
- Charter amendment mechanical gate (versioning, re-approval enforcement)
- Automated Epic 0 derivation script (capture-charter does this; a standalone script may follow if the mapping proves mechanical enough)
- Cross-document consistency checks in charter-lint beyond structural validation

## Open Questions

Resolved during grilling and subsequent proposal review. No open questions remain — the four Major findings (PROP-0001 through PROP-0004) have been addressed in this revision.

## Completion Criteria

- Three charter documents producible from `capture-charter --init`
- Brownfield scan pre-populates charter via `capture-charter --init --scan`
- `update-charter` usable by any agent to fill charter incrementally
- Completeness sweep fills remaining gaps and derives Epic 0 stories, including a final "update development.md" story that depends on all other Epic 0 stories
- Templates exist and `charter-lint` validates against them
- `charter-lint --planning-gate` enforces decision-completeness for tech-stack and development
- Stakeholder approval gate before planning covers charter and Epic 0 together
- Planning-agent finds Epic 0 in backlog and schedules feature stories after it
- Implementation-agent schedules Epic 0 as wave 1
- Story template supports `tests:` field; `backlog-lint` validates it
- Developer-agent respects `tests:` field — reads pre-existing tests as spec when present
- Greenfield, feature-addition, and brownfield playbooks route through charter at the appropriate points
- `rules.md` records Epic 0 derivation, sequencing, and house-rules compliance rules
- `validate` runs `charter-lint` when charter exists
- A project running greenfield reaches implementation with Epic 0 complete before the first feature story starts

## Guiding Rule

No feature story starts until the mise en place is done. The charter decides the materials and the workbench; Epic 0 sets them up; then the real cooking begins.
