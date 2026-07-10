[back to index](README.md)

# 8. Cross-cutting Concepts

Concerns that span multiple building blocks. Each is realized once and reused, keeping the core small.

## 8.1 Session isolation

Every agent invocation is a fresh OS subprocess with no inherited conversation context (NFR-2, BR-004, VR-004). Isolation is a **structural** guarantee (a process boundary), not a behavioural one (prompt discipline). The `CLIAdapter` port is the only place a subprocess is spawned; the core never shares state between an author and a reviewer invocation. See [ADR-0002](adr/0002-subprocess-session-isolation.md).

## 8.2 Determinism and the gate

The LLM's non-deterministic output is bracketed by deterministic checks (NFR-1). Agents commit their own work inside the CLI subprocess; the host's `.pre-commit-config.yaml` hooks fire on each `git commit`, providing deterministic gating at the point of commit — the same mechanism as ADR-0003, but the *commit responsibility* shifts from orchestrator to agent (ADR-0013).

The orchestrator's gate is a **working-tree cleanliness check** (`git status --porcelain`) after the agent process exits. The `(exit_code, tree_state)` pair determines the outcome:

- `exit 0 + clean` → passed (agent committed all work, hooks accepted it).
- `exit 0 + dirty` → **confabulation** — agent claimed success but left uncommitted changes; halt immediately (VR-025).
- `non-zero + dirty` → failed; clean tree before retry (VR-026).
- `non-zero + clean` → failed (infra/auth); classify per §8.9.

See [ADR-0003](adr/0003-pre-commit-as-gate-bus.md) (hook config) and [ADR-0013](adr/0013-working-tree-gate-model.md) (gate model).

## 8.3 Finding lifecycle and identity

- **Identity**: the orchestrator owns a monotonic allocator; every ingested finding gets a unique `FND-NNNN` id on ingest. Sources (`spec-lint`, reviewer) never mint ids (BR-019, VR-007).
- **Shape**: one schema for both sources (deterministic + semantic); every finding is validated on write (VR-006). Schema in [interface-contracts](spec/supplementary_specs/interface-contracts.md).
- **Ingest**: deterministic findings come from `spec-lint --format json`; the semantic reviewer's findings are read from its filed `docs/findings/*.md` (status `open`). A `FindingIngestor` port (concrete `DefaultFindingIngestor`) maps both onto the finding DTO and writes them to the store, so the core never imports the reader ([ADR-0012](adr/0012-ingest-findings-from-filed-markdown.md), superseding the stdout-block mechanism of ADR-0011). The reviewer reports on its own severity scale (`critical/major/minor`, or `high/medium/low` for security and ATAM); the ingestor maps every scale onto the store's `error/warning/info` so no finding is dropped. Reading the files, not stdout, means the loop works in interactive mode too (ST-0022).
- **Single source of truth**: the JSON store, not `docs/findings/*.md`, is authoritative for loop state — identity, lifecycle, and phase/iteration scoping. The filed markdown is the ingestion input the store is projected from, one-directionally; no finding's content is authored independently in both places ([ADR-0019](adr/0019-findings-store-remains-the-loop-source-of-truth.md), closing ST-0021).
- **Cycle tagging**: a finding is tagged with the 1-based cycle that must address it — `run-iteration + 1` (the run counter is 0-based). The reviewer's findings are counted as the just-produced cycle for the exit predicate, and read by the next author after the loop-back increment.
- **Lifecycle**: `open → superseded` (a newer iteration replaced it — auto, BR-014) or `open → resolved` (a human closed a surviving finding — T-05). The loop-exit predicate counts only `open` findings of the **latest** iteration (SF-04, VR-013). This is what guarantees the loop terminates: each iteration supersedes the prior iteration's open findings, so stale findings cannot keep the loop alive.

## 8.4 Loop control and termination

`LoopPolicy` is the single authority for termination (BR-001/003). The cap (default 3, VR-002) is checked at exactly one decision point — `RetryOrHalt` in the state machine — so the machine provably cannot cycle forever. Recoverable failures (author failed, reviewer failed, empty commit, open findings) route through `RetryOrHalt`; non-recoverable ones (gate error, adapter auth) bypass it straight to `Halted`.

## 8.5 State persistence and atomicity

All persisted state is written **atomically** via write-then-rename (NFR-3, BR-017): `run.json` (VR-010) and every finding file (VR-006). A crash therefore never leaves a half-written record; a resume always reads a consistent checkpoint. `run.json` + the findings store together are a complete, resumable snapshot (FR-I, UC-06). See [ADR-0005](adr/0005-run-state-lock-and-branch.md).

## 8.6 Concurrency and the run branch

A `RunLock` enforces a single active run (BR-017, VR-017); the orchestrator refuses to start while a lock is held or `run.json` shows `mode: running`. The orchestrator creates a **dedicated run branch** from a clean tree (BR-016); **agents commit on this branch** inside their subprocess — the orchestrator never commits on behalf of agents (ADR-0013). The operator's working branch is never mutated behind their back; force-push is forbidden (NFR-3).

## 8.7 Completion detection

Completion is inferred from the working-tree state, requiring no change to agent definitions (FR-H, VR-019): a **gated phase** is done when the agent exits with code 0 and the working tree is clean (all work committed, hooks passed — ADR-0013); a **`run-step`** applies the same working-tree gate (single pass, no loop); a **clean reviewer** is done when its session exits zero having written no findings. The expected artifacts are the agent's declared `outputs:`, read via `AgentRegistry` — a single source of truth, never a duplicated list.

## 8.8 Prompt composition and call-to-action

`PromptComposer` builds each agent's prompt from the agent definition file (resolved from the package-relative `agents/` path) plus project/root context, and — on loop-back — the open findings/gate output as extra instruction (FR-B2, UC-02 ext. 5a/8a). Composition is CLI-agnostic; how the composed prompt is passed non-interactively is the adapter's concern.

The composer accepts an `InvocationContext(phase, role, iteration)` frozen dataclass (ADR-0014) and appends a role-specific **call-to-action** as the final `# Call to Action` section. Five templates cover every invocation path:

| Template              | When used                              |
| --------------------- | -------------------------------------- |
| **author-first**      | First iteration of an authoring phase  |
| **author-loopback**   | Author re-addressing reviewer findings |
| **reviewer-first**    | First review of authored work          |
| **reviewer-loopback** | Re-reviewing after author remediation  |
| **standalone**        | `run-step` — no phase context          |

Templates are hardcoded f-strings in the composer. The call-to-action is the imperative signal that moves agents from passive context-reading to active work.

## 8.9 Error handling, safe halt, and release

`Halted` is a designed terminal state, distinct from `Complete` (OC-3). Every halt records its reason to `run.json` and surfaces it to the operator: cap exhaustion (BR-003), gate error or gate timeout (BR-015/BR-020), adapter auth failure (BR-018), adapter config error (BR-020), confabulation (VR-025), or rejection (BR-012). The **failure-classification** rule is the safety hinge: a failure that is not author-fixable and would repeat identically on retry — a bad model id, a gate timeout, confabulation — halts at once rather than looping the author to the cap and then halting with a misleading "cap exhausted". These halt edges are checked before the generic author-failed edge (state-machines.md; ATAM-R01/R02/R03).

**Recovery via `release`** (ADR-0015, FR-A7): `PhaseRecord` gains `halted_from: PhaseStatus | None`, set by `_halt()` before writing `HALTED`. The `release` command reads `halted_from`, restores the phase to its pre-halt status, resets the iteration counter, and sets `mode: paused`. The operator then runs `resume` to continue. If `halted_from` is absent, `release` refuses (VR-029). This replaces the abort-and-rerun workflow for transient failures.

## 8.10 Observability

Every subprocess invocation is logged with agent, role, adapter, duration, exit status, the failure flags, and gate outcome (FR-J, UC-03). The core writes through a `Logger` port; the default sink is an append-only `.orchestrator/log.jsonl`, one line per invocation, matching the `AGENT_INVOCATION` entity (ATAM-R06). Logs are for the operator's post-hoc understanding; they are never parsed to make control-flow decisions (that is the gate's and the findings store's job — §8.2).

## 8.11 Dependency management

stdlib-first (`argparse`), with `jsonschema` as the one justified runtime dependency for schema validation (NFR-7, T-06). This mirrors `spec-lint`'s zero-dependency ethos and keeps the tool trivially installable. See [ADR-0006](adr/0006-stdlib-first-dependency-policy.md).

## 8.12 Model selection

Model selection has **two axes that operate at two levels and never combine** (ADR-0018). An agent declares the `tier` its task needs (`economy`, `standard`, `strong`) in its front-matter; a story declares its `classification` (`trivial`, `standard`, `hard`). Both resolve to a concrete model through the **active adapter's model dictionary**, which is the runtime single source of truth for the tier→model mapping. The operator-curated **model matrix** remains the authoring artifact: its `[facts]` populate each adapter's dictionary at startup and on `configure > model-matrix > edit` (the runtime never reads the matrix file directly).

The two levels:

- **Agent tier — orchestrator-invoked agents.** For every agent the orchestrator invokes directly, `ModelResolver` resolves that agent's own tier. On `run-step` the named agent's tier resolves directly and an explicit `--model` overrides the whole chain; on `run-phase` each phase author/reviewer resolves independently from its own tier, with no phase-level `--model`.
- **Story classification — developer sub-agents.** During the implementation phase the `implementation-agent` acts as a dispatcher and assigns each ready story's developer sub-agent a model from the story's `classification` **alone**. Developer agents declare **no tier** by design — the model for a unit of work is the dispatcher's decision, and the classification is its single source of truth. This happens below the adapter boundary (FR-M); the orchestrator sees one `implementation-agent` invocation, resolved from that agent's own tier.

A **null tier** resolves as `standard` (VR-041) for orchestrator-invoked agents, so every such agent resolves a model even before all definitions carry an explicit tier; developer sub-agents are exempt, being tier-less by design. When the adapter dictionary has no model for a required tier, the run halts as a configuration error unless adapter-default fallback is enabled (BR-020, FR-K4). There is no per-story model field, so the backlog stays CLI-agnostic. See [ADR-0009](adr/0009-task-classification-and-tier-pivot-model-matrix.md) (superseded in part) and [ADR-0018](adr/0018-two-axis-tier-model-resolution.md).

## 8.13 Settings resolution and persisted defaults

Operator defaults — `adapter`, `timeout`, `cap`, `auto_approve` — plus the adapter registry and per-adapter model dictionaries live in `.orchestrator/config.toml`, written atomically via write-then-rename (UC-09, UC-10, ADR-0017). When the file is absent the orchestrator runs on built-in defaults and creates it only on the first successful persist (FR-Q5).

`SettingsResolver` centralises the fixed four-layer precedence so direct mode and menu mode produce identical effective settings (FR-Q3, SF-07, VR-034):

```
menu selection > CLI flag > config.toml > built-in default
```

A missing or `None` value at any layer means "continue to the next layer," never "stop with null." A persisted `adapter` default must name a registered adapter at the time of persistence (VR-033); a malformed file or invalid stored value makes the orchestrator refuse the affected action and report the offending file and key (FR-Q6). The Python-baseline TOML decision is tracked as T-28.

## 8.14 Presentation layer and dual-mode entry

Menu mode is a **presentation layer over the existing core, not a second orchestration engine** (NFR-10, ADR-0016). The composition root chooses the entry path: a subcommand runs direct mode unchanged; a bare `orchestrate` on an interactive terminal hands control to `MenuController`. Every function leaf dispatches to the same application service its direct-mode command uses (FR-V3), so exit codes, gate behaviour, run-state mutation, findings ingestion, and logging are identical across modes.

Navigation state is independent of run state (VR-030): cursor movement, menu entry, back navigation (`q`/`Esc`), display viewing, and exit (`qq`/`Ctrl+C`) mutate no `run.json`, findings, or logs — only a dispatched leaf may. Long-running leaves exit the TUI before streaming output begins (FR-P7). The `MenuRenderer` port isolates the terminal framework, which is deferred (T-29); a non-interactive terminal never enters menu mode and receives a direct-mode diagnostic instead (FR-V4, T-30). The navigation state machine is in [`spec/supplementary_specs/state-machines.md`](spec/supplementary_specs/state-machines.md#tui-menu-navigation-state-machine).

### Skill-scoped execution

`run-step <agent> --skill <skill>` (or the menu equivalent) runs a single declared skill rather than the full workflow. The skill is validated against the agent's declared front-matter skills **before** any adapter subprocess launches (VR-038); an undeclared skill is rejected. Scoping is a **prompt-composition rule, not an agent-definition rewrite** (BR-051): `PromptComposer` keeps the agent definition and appends a skill-scoped call to action instructing the agent to execute only that skill's step. `all skills` is the full-workflow sentinel. Interactivity follows the agent's `interactive` front-matter default unless an explicit `--interactive` or menu override applies for that one invocation (FR-S5, FR-S6).
