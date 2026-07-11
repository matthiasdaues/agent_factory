# PRD — Factory Flow Control

**Status**: Documented (retroactive — reverse-engineered from code, per [brownfield-onboarding.md § Overview](../../factory/playbooks/brownfield-onboarding.md#overview))
**Date**: 2026-07-11
**Domain**: `factory/` — the state-machine harness, dispatch mechanism, and generated catalog that govern how Agent Factory playbooks run

______________________________________________________________________

## 1. Problem Statement

`factory/` began as a library of agents, skills, and playbooks — prose read by a human or an AI CLI, with no enforcement. Nothing stopped a file from a later phase being staged before its predecessor's gate cleared. Nothing capped a review loop, so a stuck gate could churn forever. `factory/` has since grown its own deterministic state-machine harness, a CLI-agnostic dispatch mechanism, and a generated catalog to close both gaps — without requiring the `orchestrator/` Python CLI that used to own this job.

`orchestrator/` used to run its own `PhaseRunner`, an independent state machine for driving the agent chain. That ownership has inverted. `orchestrator/` is now one possible trigger of `factory/`'s mechanisms — a stand-in for a human manually running `factory/scripts/trigger`, `phase advance`, and `phase retry` by hand. A human typing commands and the orchestrator CLI are peers; both only invoke `factory/` tooling. This PRD documents `factory/` as the flow-control owner it has become, superseding the informal descriptions in [docs/concepts.md § The phase chain](../concepts.md#the-phase-chain) and [factory/docs/factory-guide.md § Playbook phase gates](../../factory/docs/factory-guide.md#playbook-phase-gates) with a rigorous specification.

## 2. Goals and Non-Goals

### Goals

- **G1** — Gate which files may be staged in which playbook phase, deterministically, from a git-ignored local marker (`transition-lint`).
- **G2** — Advance a playbook run to its next phase only when that phase's declared entry conditions hold, and record the advance in the marker (`phase advance`).
- **G3** — Cap how many times a phase's author step re-runs after a failing gate, per-state configurable, with a default backstop (`phase retry`).
- **G4** — Dispatch a named agent or one playbook step to a CLI session — interactive or unattended — resolving the model from a tier, under a hardcoded, scoped permission allowlist (`trigger`).
- **G5** — Resolve "what's next" and "is this a resume" from observable state every time — the marker, gate results, open findings — never from a separately persisted execution status (`run-step` skill).
- **G6** — Keep the machine-readable catalog of every agent, skill, and playbook (`factory/INDEX.yaml`) generated from source frontmatter, never hand-edited (`index-lint`).
- **G7** — Block a fixed list of destructive or gate-bypassing git commands before they run, for both supported CLIs (`block-dangerous-git.sh`).
- **G8** — Wire all of the above into a new or existing project, idempotently, without disturbing what is already there (`init-factory`).

### Non-Goals

- **NG1** — Not a re-implementation of `orchestrator/`'s `PhaseRunner`. `orchestrator/` may call these same mechanisms; `factory/` does not duplicate its run-state model (`RUN`, `RUN_LOCK`, single-active-run invariant).
- **NG2** — Not a general CI system. `pre-commit` and the CLIs do the work; these scripts sequence and gate them.
- **NG3** — No CLI-failure classification (auth vs. config vs. task failure) at the dispatch layer — a known, named gap. See [T-01](todos.md#t-01-no-cli-failure-classification-in-trigger).
- **NG4** — No state machine for every playbook. Only `greenfield-development.fsm.yml` exists today; the harness is opt-in per playbook (see [UC-01 § Preconditions](use_cases/UC-01-advance-a-playbook-phase.md#preconditions)).
- **NG5** — No run lock or single-active-run invariant across concurrent operators. The marker is a single flat file; two operators racing the same marker is out of scope. See [T-02](todos.md#t-02-no-concurrent-operator-lock-on-the-marker).

## 3. Target Actors

- **Human Operator** (primary) — a person driving Agent Factory directly: running scripts by hand, committing code, approving phase gates.
- **Orchestrator-as-Trigger** (secondary) — the nested `orchestrator/` Python CLI, a peer of the Human Operator. It invokes the same `factory/scripts/*` mechanisms programmatically instead of a human typing them.
- **CLI-Invoked Agent** (secondary) — the Claude Code or Copilot CLI agent session that `trigger` dispatches, operating under the scoped permission allowlist `trigger` constructs for it.

## 4. Functional Requirements

### FR-A — Phase-ordering gate (`transition-lint`)

- **FR-A1** — Reads the git-ignored marker. No marker present → no-op, one info-severity finding.
- **FR-A2** — Blocks a staged file whose declared `outputs:` glob belongs to a state other than the marker's current state.

### FR-B — Phase advance (`phase advance`)

- **FR-B1** — Resolves the current state's forward transition from the playbook's `.fsm.yml`.
- **FR-B2** — Evaluates the target state's `entry_conditions` against the `gate_conditions` library; refuses to advance if any condition is unmet.
- **FR-B3** — On success, writes the marker with `iteration` reset to `1` and `recorded_at` from `phase advance`'s own process clock.

### FR-C — Iteration cap (`phase retry`)

- **FR-C1** — Resolves the iteration limit for the loop-back target state: the FSM's own `halt_conditions` first, `--default-max-iterations` otherwise.
- **FR-C2** — Refuses (exit 2) once the incremented iteration count exceeds the limit; the marker is written only on an allowed retry.

### FR-D — Dispatch (`trigger`)

- **FR-D1** — Resolves an agent name, or one playbook step by name or index, from `factory/INDEX.yaml`'s own source data.
- **FR-D2** — Resolves a tier to a concrete model via `config/model.conf`, honouring `on_missing`.
- **FR-D3** — Background mode invokes the CLI non-interactively under a hardcoded, scoped tool allowlist — never a blanket permission bypass.
- **FR-D4** — Interactive mode prints the composed prompt and launches a live CLI session; it does not seed the message programmatically.

### FR-E — Catalog generation (`index-lint`)

- **FR-E1** — Regenerates `factory/INDEX.yaml` from `agents/*.md`, `skills/*/SKILL.md`, and `playbooks/*.md` frontmatter and prose.
- **FR-E2** — `--check` mode verifies without writing; exits `1` if the catalog is stale.

### FR-F — Resume decision (`run-step` skill)

- **FR-F1** — Derives the current playbook and state from the marker; bootstraps one via `phase advance` if the marker is absent.
- **FR-F2** — Resolves the state to an agent from the FSM's `agent:` field, or from `INDEX.yaml`'s derived `agents:` list when no FSM exists.
- **FR-F3** — Decides fresh-start, resume, done, or escalate from the state's declared outputs on disk and its gate's result.

### FR-G — Guardrail hook (`block-dangerous-git.sh`)

- **FR-G1** — Reads the shell command from either CLI's `PreToolUse` JSON shape.
- **FR-G2** — Denies (exit `2`) a command matching any pattern in a fixed list; both CLIs treat exit `2` as deny.

### FR-H — Installation (`init-factory`)

- **FR-H1** — Idempotent: copies `factory/`, merges `.gitignore`, symlinks factory content and the guardrail hook into both `.claude/` and `.github/`, copies `config/model.conf` once, merges or symlinks `.pre-commit-config.yaml`.
- **FR-H2** — Collision-safe: any step that finds something unexpected at a destination path stops the whole run before touching anything later.

## 5. Constraints

- Every `factory/scripts/*.py` gate has zero third-party dependencies — Python 3.8+ stdlib only — so gates run without a virtualenv.
- macOS and Linux only. `init-factory` relies on native, git-tracked symlinks, which Windows does not support the same way.
- The marker (`.agent-factory/playbook-state.yml`) is git-ignored, local, single-file state — not a distributed or multi-operator lock.

## 6. Success Criteria

- A Human Operator can drive `greenfield-development.fsm.yml` end to end using only `transition-lint`, `phase advance`, `phase retry`, and `trigger` — no `orchestrator/` CLI involved.
- `orchestrator/` can drive the identical playbook run through the same four mechanisms, adding no flow-control logic of its own.
- `factory/INDEX.yaml` always matches what `index-lint` would generate from current frontmatter (`index-lint --check` exits `0`) — no hand-edit drift.

## 7. Assumptions

- Every project using this harness has run `init-factory` at least once, so `factory/` is present, symlinked into `.claude/` and/or `.github/`, and the guardrail hook is wired in.
- A playbook without a `.fsm.yml` is driven by prose alone; `transition-lint` and `phase advance`/`retry` are no-ops for it (marker absent, or its `playbook` field names a playbook with no `.fsm.yml`).

## Referenced from

- [actor-goal-list.md](actor-goal-list.md)
