# PRD — Factory Flow Control

**Status**: Documented (retroactive — reverse-engineered from code, per [brownfield-onboarding.md § Overview](../../.agent-factory/factory/playbooks/brownfield-onboarding.md#overview))
**Date**: 2026-07-11
**Domain**: `.agent-factory/factory/` — the state-machine harness, dispatch mechanism, and generated catalog that govern how Agent Factory playbooks run

______________________________________________________________________

## 1. Problem Statement

`.agent-factory/factory/` began as a library of agents, skills, and playbooks — prose read by a human or an AI CLI, with no enforcement. It has since grown a precondition-based eligibility engine, a CLI-agnostic dispatch mechanism, deterministic validators, and a generated catalog. This PRD documents `factory/` as the flow-control owner it has become.

## 2. Goals and Non-Goals

### Goals

- **G1** — Evaluate agent preconditions against the repository and classify agents by eligibility (`intent select`/`intent assess`).
- **G2** — Dispatch a named agent or one playbook step to a CLI session — interactive or unattended — resolving the model from a tier, under a hardcoded, scoped permission allowlist (`trigger`).
- **G3** — Resolve "what's next" and "is this a resume" from observable state every time — agent definitions, gate results, open findings — never from a separately persisted execution status (`run-step` skill).
- **G4** — Keep the machine-readable catalog of every agent, skill, and playbook (`.agent-factory/factory/INDEX.yaml`) generated from source frontmatter, never hand-edited (`index-lint`).
- **G5** — Block a fixed list of destructive or gate-bypassing git commands before they run across all supported CLIs (`block-dangerous-git.sh` for native-hook runtimes; the equivalent Pi extension).
- **G6** — Wire all of the above into a new or existing project, idempotently, without disturbing what is already there (`init-factory`).
- **G7** — Ensure project-owned test gates exist: every project declares its test commands in `docs/testing.yaml`; Factory's guardrails and eligibility preconditions read that declaration; Factory never owns test execution.
- **G10** — Keep multi-phase workflow input cost bounded by ending the session at every phase transition and restarting from a complete, validated handoff and canonical tracked artifacts.
- **G11** — Prevent avoidable child-dispatch spend by maintaining auditable evidence that each delivered dispatch safeguard has a contract, implementation point, and automated coverage, without reimplementing proven baseline behavior.

### Non-Goals

- **NG1** — Not a parallel Python orchestration CLI. `.agent-factory/factory/` provides its own flow-control mechanisms directly.
- **NG2** — Not a general CI system. `pre-commit` and the CLIs do the work; these scripts sequence and gate them.
- **NG3** — No CLI-failure classification (auth vs. config vs. task failure) at the dispatch layer — a known, named gap. See [T-01](todos.md#t-01-no-cli-failure-classification-in-trigger).
- **NG4** — No run lock or single-active-run invariant across concurrent users. Workstream state files are immutable identity records; concurrency is handled by the filesystem.
- **NG5** — No playbook execution engine. Playbooks are prose; the execution model is pending redesign.
- **NG6** — No in-place transcript compaction, live token-budget stop, universal cache-miss detector, prose-only cache-restabilisation ritual, or unified cross-CLI transcript format.
- **NG7** — No retrospective reimplementation of dispatch safeguards already proven by the baseline audit; only verified gaps, missing tests, and contradictory documentation are remediated.

## 3. Target Actors

- **User** (primary) — a person driving Agent Factory directly: running scripts by hand, committing code, approving agent selections.
- **CLI-Invoked Agent** (secondary) — the Claude Code, GitHub Copilot CLI, Codex, or Pi agent session that `trigger` dispatches, operating under the scoped permission controls available in that runtime. Under Pi, which has no native subagent concept, this actor is also the caller of the `run_agent` tool: it spawns a fresh Pi session to run another factory agent with separate-session semantics (FR-J).
- **Workflow Participant** (primary) — a human or factory agent completing one workflow step and handing the next step to a fresh CLI session without replaying the prior transcript.
- **Assurance Auditor** (primary) — a requirements, planning, or quality participant who maps accepted dispatch safeguards to observable delivery evidence and files only verified gaps.
- **Handoff Semantic Reviewer** (secondary) — a designated human or agent who compares the handoff with the outgoing phase's artifacts and decisions for omissions that structural validation cannot infer.

## 4. Functional Requirements

### FR-A — Precondition-based agent eligibility (`intent`)

- **FR-A1** — `intent select` loads all agent definitions, evaluates each agent's `inputs.required` declarations against the filesystem, and classifies agents into eligible and blocked groups.
- **FR-A2** — `intent assess` validates governed artifacts for a specific agent and reports assessment results.
- **FR-A3** — The Eligibility Engine returns immutable decisions without writing state, acquiring locks, or importing scripts.

### FR-B — Dispatch (`trigger`)

- **FR-D1** — Resolves an agent name, or one playbook step by name or index, from `.agent-factory/factory/INDEX.yaml`'s own source data.
- **FR-D2** — Resolves a tier to a concrete model via `.agent-factory/config/model.conf`, honouring `on_missing`.
- **FR-D3** — Background mode invokes the CLI non-interactively under a hardcoded, scoped tool allowlist — never a blanket permission bypass.
- **FR-D4** — Interactive mode prints the composed prompt and launches a live CLI session; it does not seed the message programmatically.

### FR-E — Catalog generation (`index-lint`)

- **FR-E1** — Regenerates `.agent-factory/factory/INDEX.yaml` from `agents/*.md`, `skills/*/SKILL.md`, `playbooks/*.md`, and `rulebooks/**/*.md` (excluding templates) frontmatter and prose. Each entry carries a `tokens` field (tiktoken cl100k_base, chars ÷ 4 fallback). Agents carry `total_tokens` (body + referenced skills + referenced rulebooks). Playbooks carry `total_tokens` (body + unique agent totals).
- **FR-E2** — `--check` mode verifies without writing; exits `1` if the catalog is stale.
- **FR-E3** — Warns when an agent's `total_tokens` exceeds 20 000.

### FR-F — Resume decision (`run-step` skill)

- **FR-F1** — Evaluates agent eligibility via the Eligibility Engine to determine available next steps.
- **FR-F2** — Resolves the agent from `INDEX.yaml`'s derived `agents:` list and eligibility evidence.
- **FR-F3** — Decides fresh-start, resume, done, or escalate from the agent's declared outputs on disk and gate results.

### FR-G — Guardrail hook (`block-dangerous-git.sh`)

- **FR-G1** — Reads the shell command from the Claude Code, GitHub Copilot CLI, or Codex `PreToolUse` JSON shape; Pi's extension reads the equivalent tool call.
- **FR-G2** — Denies a command matching any pattern in a fixed list; the three native-hook CLIs treat exit `2` as deny, and Pi's extension rejects the tool call.

### FR-H — Installation (`init-factory`)

- **FR-H1** — Idempotent: copies `.agent-factory/factory/`, merges `.gitignore`, and installs Factory surfaces for Claude Code (`.claude/`), GitHub Copilot CLI (`.github/`), Codex (`.codex/` and `.agents/`), and Pi (`.pi/`). The first three receive the native guardrail hook; Pi receives the equivalent project-local extension. It copies `.agent-factory/config/model.conf` once and merges or symlinks `.pre-commit-config.yaml`.
- **FR-H2** — Collision-safe: any step that finds something unexpected at a destination path stops the whole run before touching anything later.

### FR-I — Project-Owned Test Gates (testing declaration)

- **FR-I1** — Every project (including Factory) declares its test commands in `docs/testing.yaml`: `test_command` (required, full suite), `test_staged_command` (optional, agent TDD iteration), `test_changed_command` (optional, fast feedback on changed files).
- **FR-I2** — The precondition evaluator resolves `test_command` from `docs/testing.yaml` when an agent declares it as a required input. If the configuration is absent or `test_command` is missing, the evaluator reports the gap.
- **FR-I3** — The gate contract is exit-code-only: zero means pass, nonzero means fail. Factory does not parse structured test output; test counts and reporting are the project's concern.
- **FR-I4** — `block-dangerous-git.sh` reads `docs/testing.yaml` and allowlists all declared command fields (`test_command`, `test_staged_command`, `test_changed_command`) with exact-string matching. Bare test commands remain blocked for agents.
- **FR-I5** — Factory does not inject test hooks into `.pre-commit-config.yaml`. Test hooks are project-owned infrastructure: the project decides when and how tests trigger on commit, push, or other events.
- **FR-I6** — During onboarding, the `detect-test-regime` skill scans for existing test entrypoints and records the result in `docs/testing.yaml`. When multiple entrypoints are detected, Factory asks for disambiguation instead of guessing.

### FR-J — Pi agent invocation (`run_agent`, `dispatch_wave`)

Pi has no native subagent concept, so a factory agent cannot run in a separate Pi session the way Claude Code spawns a subagent. `run_agent` supplies that missing invocation layer as a project-local extension tool.

- **FR-J1** — The extension `.pi/extensions/run-agent.ts` registers a model-callable tool `run_agent(agent, task, model?)` that resolves `.agent-factory/factory/agents/<agent>.md`, resolves the model (`model` argument, else `.agent-factory/config/model.conf` `pi.<tier>`, honoring `on_missing`), and spawns a separate `pi` subprocess (`--no-session -a --mode json --model <m> --append-system-prompt <agent> -p <task>`), returning the child's final text and token usage parsed from `message_end`.
- **FR-J2** — The spawn is a genuinely separate session that never receives the caller's context, preserving author/reviewer independence; on a resolution, recursion, or spawn error the tool returns a diagnostic result and launches nothing.
- **FR-J3** — A fixed recursion-depth bound, carried in an environment variable the parent sets and the child reads, caps nested `run_agent` spawns.
- **FR-J4** — The dispatcher tool `dispatch_wave`, layered on the `run_agent` primitive, spawns several agents in parallel — each in its own git worktree, each under a per-story model tier — and integrates `premerge-check`; it ports `implementation-agent`, whose current prose depends on Claude Code's native Agent-tool worktree isolation.
- **FR-J5** — `run-agent.ts` lives in `.agent-factory/factory/config/extensions/`, is symlinked into the git-ignored `.pi/extensions/` by `init-factory`, and is reversed by `remove-factory` to a clean `git status`; it adds no tracked project state.

### FR-K — Session-transcript token control

- **FR-K1** — Every transition between Factory workflow phases is a hard session boundary: the outgoing session creates a handoff and stops; a fresh session begins the next phase. Work that remains within one phase is exempt.
- **FR-K2** — A Factory-owned, CLI-agnostic `handoff` skill writes dense, unambiguous prose without dropping any decision, open item, artifact path, exact 40-character SHA, branch/upstream state, gate result, verification evidence, or next action.
- **FR-K3** — `handoff-lint` deterministically blocks phase closure for mechanically observable defects in required structure, declared referenced paths, full SHA syntax, declared repository-state fields, declared verification fields, and next-action presence. A designated semantic reviewer separately checks that the handoff did not omit or distort material decisions, open items, evidence, or artifact references.
- **FR-K4** — Before a child agent returns, it persists its complete result in canonical tracked report and finding artifacts. The parent receives only a bounded envelope containing disposition, finding counts by severity, the complete artifact-path list, and a one-to-three-sentence next action.
- **FR-K5** — Agents read large artifacts in bounded chunks and request further chunks only when needed for the current task.
- **FR-K6** — At session end, usage capture derives cache-miss turn count and cache-miss input-token total only when the provider exposes input and cache-read tokens for every eligible assistant-response turn. It independently derives the late-versus-early input ratio when per-turn input is complete, using the deterministic BR-042 partition and formula, and records CLI/provider identity and capability class with nullable results.
- **FR-K7** — Retrospectives consume the derived usage signals as evidence of friction; the signals never act as live controls in the first release.

### FR-L — Dispatch safeguard assurance audit

- **FR-L1** — The audit maps each accepted dispatch mechanism—base verification before work, declared base SHA, resolvable nested-agent addressing, pre-merge diff checking, evidence-derived unattended permissions, and bounded/checkpointed scope—to its shipped contract, implementation point, and automated evidence or to a gap requiring remediation.
- **FR-L2** — Machine-consumed base and dispatch state uses exact 40-character Git SHAs. Automated evidence covers wrong or stale bases, stale/out-of-scope/file-blowout/target-reverting diffs, nested reply routing, background permission argv and deny lists, and enforceable scope/checkpoint rules where feasible.
- **FR-L3** — The audit amends stale documentation only when it contradicts observable behavior and creates no implementation work for a safeguard whose contract, implementation, and automated evidence are complete.

## 5. Constraints

- Every `.agent-factory/factory/scripts/*.py` gate has zero third-party dependencies — Python 3.8+ stdlib only — so gates run without a virtualenv.
- macOS and Linux only. `init-factory` relies on native, git-tracked symlinks, which Windows does not support the same way.
- Workstream state files under `.agent-factory/workstreams/` are immutable identity records — not mutable execution state.
- Dispatch safeguard assurance interprets the accepted design from immutable proposal baseline `5219c64b6586b7606df346cac668d128bd3c21fe`; later observable implementation evidence may prove a mechanism complete but may not rewrite that design origin.

## 6. Success Criteria

- `.agent-factory/factory/INDEX.yaml` always matches what `index-lint` would generate from current frontmatter (`index-lint --check` exits `0`) — no hand-edit drift.
- A conversational Pi session can invoke a factory agent by name via `run_agent` and receive its result from a separate `pi` session that never saw the caller's context, and `dispatch_wave` can run at least two `developer-agent` sessions in parallel worktrees merged through `premerge-check`.
- Every cross-phase continuation restarts from a `handoff-lint`-clean handoff and canonical artifacts, while child results enter parent transcripts only through bounded envelopes.
- A retrospective on a multi-step session reports a lower late-step versus early-step input ratio than the measured 11.3× baseline, qualified by CLI/provider.
- Every accepted dispatch safeguard has a traceable contract, implementation point, and passing automated evidence, or a verified gap explicitly identified for remediation.

## 7. Assumptions

- Every project using this harness has run `init-factory` at least once, so
  `.agent-factory/factory/` is present, the selected runtime surfaces are installed, and the
  corresponding native guardrail hook or Pi extension is wired in.
- Playbooks are prose-driven. The execution model for playbook steps is pending redesign.

## Referenced from

- [actor-goal-list.md](../~archive/spec/actor-goal-list.md)
- [../README.md § Table of Contents](../README.md#table-of-contents) — the arc42 architecture documentation and Structurizr C4 model built from this specification.
- [Accepted dispatch-efficiency proposal](../proposals/implemented/agent-dispatch-token-efficiency.md) — design origin for FR-L's assurance audit.
- [Accepted session-control proposal](../proposals/implemented/proposal-session-transcript-token-control.md) — design origin for FR-K's external workflow contract.
