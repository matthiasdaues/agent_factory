# Open Questions — Agent Session Orchestrator

Open items surfaced during requirements clarification. Resolve before or during the spec/architecture phases. Referenced by [`prd.md`](prd.md).

| ID   | Question                                                                                                                                                                     | Notes / leaning                                                                                                                                                                                                                                                                                    |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T-01 | Exact non-interactive invocation for the **Copilot CLI** (and how per-CLI flags differ)                                                                                      | Adapter contract (FR-C) hides it; needs one confirmed working invocation for the MVP.                                                                                                                                                                                                              |
| T-02 | Implementation depth of the **Claude/Gemini** adapters in the MVP                                                                                                            | Leaning: interface + Copilot concrete; other adapters to the same contract, lightly exercised.                                                                                                                                                                                                     |
| T-03 | Redirect `inspect-spec` / `spec-review-agent` issue-filing from GitHub to the **local store**                                                                                | **Resolved**. Review agents/skills now file findings as `docs/findings/<TAG>-NNNN.md` (strict frontmatter) and emit a fenced `json` findings block that the orchestrator ingests into the findings store via the `FindingIngestor` (ADR-0011). Applies to all review agents, not just spec review. |
| T-04 | Design of the future **external-ticket adapter** (GitHub Issues / Jira)                                                                                                      | Explicitly deferred (NG3). Store schema should map cleanly to an issue.                                                                                                                                                                                                                            |
| T-05 | How a human **resolves** a finding (status → `resolved`)                                                                                                                     | **Decided (BR-014)**: each authoring iteration auto-supersedes prior findings; a human only manually closes a *surviving* finding.                                                                                                                                                                 |
| T-06 | Python **CLI framework + dependency policy**                                                                                                                                 | Leaning: stdlib `argparse` + `jsonschema`, consistent with `spec-lint`'s zero-dep style.                                                                                                                                                                                                           |
| T-07 | Confirm **project home** `orchestrator/`                                                                                                                                     | Keeps the tool beside the agents it drives.                                                                                                                                                                                                                                                        |
| T-08 | **Runtime environment** beyond MVP (CI / container)                                                                                                                          | Affects auth, cost ceilings, and how autonomous is safe.                                                                                                                                                                                                                                           |
| T-09 | **Retry cap** default (N=3) and whether it varies per phase                                                                                                                  | Safety stop for the loop-back policy (FR-F3).                                                                                                                                                                                                                                                      |
| T-10 | **Planning phase output** format under local-first                                                                                                                           | **Resolved** (grill + 08a). Story = `backlog/ST-NNNN.md`, markdown + strict frontmatter + prose body; `backlog-lint` gates it (BR-021, FR-K, StoryFrontmatter schema). See ADR-0008.                                                                                                               |
| T-11 | Add a **`config_error` signal** to `InvocationResult` and an `Authoring → Halted` edge for non-author-fixable author failures                                                | ATAM-R01 (High). **Resolved in architecture** (BR-020; interface-contracts, state-machines, UC-02) **and in code** (`config_error` on `InvocationResult`, Copilot adapter sets it, verified live: bogus `--model` now halts not loops). Loop wiring lands in Phase 4.                              |
| T-12 | Specify how `GateRunner` **distinguishes `errored` from `passed=false`** (pre-commit returns non-zero for both crash and findings)                                           | ATAM-R02 (Med). **Resolved in architecture**: output-based discriminator (parseable findings ⇒ loop; traceback/none ⇒ error/halt) in `GateResult` + ADR-0003. Implement in Phase 4.                                                                                                                |
| T-13 | Back up the **stderr-regex `auth_error` detection** with drift-pinning tests                                                                                                 | ATAM-R03 (Med). **Resolved in code**: auth/config precedence, generic-failure test, and a wording drift-pin test in `test_copilot_adapter.py`; ambiguous non-auth failures reuse the `config_error` path.                                                                                          |
| T-14 | Apply a **timeout to the gate subprocess**, treating a gate timeout as a gate error/halt                                                                                     | ATAM-R04 (Med). **Resolved in architecture**: `GateResult.timed_out` → halt (BR-020; ADR-0003). Implement in Phase 4.                                                                                                                                                                              |
| T-15 | Add a **`last_gate` field to the `run.json` phase record** so `status` can report the last gate result                                                                       | ATAM-R05 (Med). **Resolved in architecture**: `last_gate` added to the RunState schema (interface-contracts). Implement in Phase 4.                                                                                                                                                                |
| T-16 | Introduce an **invocation-log sink** for the per-invocation record                                                                                                           | ATAM-R06 (Med). **Resolved in architecture**: `Logger` port + `.orchestrator/log.jsonl` sink (interface-contracts, ch5/ch8). Implement in Phase 4.                                                                                                                                                 |
| T-17 | Define **resume idempotency at sub-phase granularity**                                                                                                                       | ATAM-R07 (Med). **Resolved in architecture**: run-branch HEAD + iteration findings are the checkpoint; skip an existing commit / already-ingested reviewer (state-machines, ADR-0005). Implement in Phase 4.                                                                                       |
| T-18 | Require each adapter to **force a clean session** (no resume/continue flag) so a fresh process cannot inherit a persisted session                                            | ATAM-R11 (Low). **Resolved in architecture** (VR-021, ADR-0002) **and in code** (clean-session test).                                                                                                                                                                                              |
| T-19 | Implement the **model matrix + its maintenance workstep**, `backlog-lint`, `matrix-lint`, and the `ModelResolver` (class/phase → tier → CLI model, precedence, `on_missing`) | Phase 4. Specified by FR-K, BR-020/021, ADR-0008/0009. The matrix is a first-class operator-curated artifact, not a chain output.                                                                                                                                                                  |
| T-20 | **Per-project model policy override** (a project supplies its own policy block over the shared matrix facts)                                                                 | **Resolved by obsolescence.** [ADR-0020](../adr/0020-tier-everywhere-model-config-router.md) removes the policy layer this would have overridden — a story declares `tier` directly, so there is no `[policy]` section left to supply a per-project override of.                                   |
| T-21 | **`arch-lint` gate for `docs/`** — DSL staleness, ch5↔DSL name coupling (core components + ports), and `structurizr validate`                                                | **Implemented** (`scripts/arch-lint`, stdlib) from the DSL-drift post-mortem. All 3 checks proven against injected drift; wired as a scoped pre-commit hook (`.pre-commit-config.yaml`, `--no-validate` at commit time). Same pattern as `spec-lint`/FR-D.                                         |

## T-23 — Per-agent file permission enforcement

**Status**: stub
**Origin**: session observation — copilot explores beyond what an agent needs; no write-boundary enforcement exists.

### Problem

All agents run with `--allow-all-tools` (full file-system access). Nothing prevents a reviewer from writing to `src/` or an implementer from editing `docs/spec/`. The only isolation is session separation (ADR-0002), which prevents context bleed but not write trespass.

### Proposed design

1. **Permission source** — each agent's frontmatter already declares `inputs` (read) and `outputs` (write) as glob patterns. Use these as the permission boundary.
2. **Enforcement point** — post-invocation gate, not OS sandbox. After the agent subprocess exits, run `git diff --name-only` on the run branch. Any file outside the agent's declared `outputs` globs is a gate failure.
3. **Fits existing architecture** — this is a new validation rule (VR-025?) checked by the gate runner alongside pre-commit hooks. Deterministic, zero false positives.

| Role                      | Write boundary                              |
| ------------------------- | ------------------------------------------- |
| requirements-agent        | `docs/spec/**`                              |
| spec-review-agent         | `docs/reviews/**`, `docs/spec/todos.md`     |
| architecture-agent        | `docs/**`, `docs/adr/**`                    |
| architecture-review-agent | `docs/reviews/**`                           |
| planning-agent            | `backlog/**`                                |
| implementation-agent      | `src/**`, `tests/**`                        |
| reconciliation-agent      | `docs/spec/**`, `docs/adr/**`, `CONTEXT.md` |
| qa-agent                  | `docs/reviews/**`, `tests/**`               |

### Open questions

- Should `CONTEXT.md` be writable by all agents or only specific ones?
- Should violations be hard-fail (block) or warning (report but continue)?
- Does this need an ADR, or is a validation rule sufficient?

## T-24 — Inject a call-to-action into composed prompts

**Status**: designed (decisions captured in `agent_hq/tmp/orchestrator-cli-enhancement-decisions.md`)
**Origin**: session observation — `copilot -p` receives the agent definition and context but no imperative instruction to act; the CLI remains inert without an explicit "go" signal.

### Problem

`FilePromptComposer.compose()` builds a prompt with `# Agent Definition`, `# Project Context`, and optionally `# Findings from Prior Iteration`. This describes *who the agent is* but never tells it to *start working*.

### Decided design

1. **Composer owns it** — `FilePromptComposer.compose()` appends a `# Call to Action` section as the final prompt block (after findings).
2. **`InvocationContext` dataclass** — new frozen dataclass (`phase: str`, `role: AgentRole`, `iteration: int`) passed as a **required** parameter to `compose()`. Breaking protocol change.
3. **Five call-to-action templates** (hardcoded f-strings in the composer):
   - Author, iteration 0: `"Begin the {phase} phase. Execute the workflow defined in your Agent Definition above, starting at Step 1."`
   - Author, iteration 1+: `"This is iteration {n} of the {phase} phase. Address the findings listed above, then re-execute your workflow."`
   - Reviewer, iteration 0: `"Review the {phase} artifacts. Follow the review workflow in your Agent Definition. File findings per the specified format."`
   - Reviewer, iteration 1+: `"This is iteration {n} of the {phase} review. The author has addressed prior findings. Re-review the artifacts and file any remaining issues."`
   - Standalone (`run-step`): `"Execute the workflow defined in your Agent Definition above."`
4. Agent definitions, `AgentInfo`, and `CopilotAdapter` are unchanged.

### Open questions

None — all design branches resolved (see decisions doc).

## T-25 — Gating model: agents commit, orchestrator verifies working tree

**Status**: designed (decisions in `agent_hq/tmp/orchestrator-cli-enhancement-decisions.md`)
**Origin**: state-machine walk-through — pre-commit gating conflicts with agent-internal commits; parallelism discussion confirmed agents own their commits.

### Decided design

1. **Agents commit their own work.** Pre-commit hooks fire on each `git commit` inside the agent subprocess. The agent's commit loop IS the quality gate.
2. **Orchestrator verifies working tree.** After the agent exits, `git status --porcelain`: clean = pass, dirty = fail.
3. **Confabulation detection.** Exit 0 + dirty tree = agent lied → Halted (VR-025).
4. **Clean tree before retry.** Non-zero + dirty → `git checkout`/`git clean` → RetryOrHalt (VR-026).
5. **`PreCommitGateRunner` replaced** by a working-tree cleanliness check. `GateResult` semantics updated.
6. **Run branch** created by orchestrator, agents commit on it.
7. **`run-step`** commits on current branch (independent of run state).
8. **Parallelism** below the adapter boundary — CLI agent owns story-level parallelism (FR-M).

Likely warrants its own ADR — hard to reverse, surprising without context, real trade-off.

## T-26 — Story-commit consistency gate (`backlog-lint` enhancement)

**Status**: designed (decisions in `agent_hq/tmp/orchestrator-cli-enhancement-decisions.md`)
**Origin**: retry reliability — ensuring only genuinely-done stories survive a dirty-tree retry.

### Decided design

1. **Rule 1 (error, blocks commit):** `status: done` requires ≥1 file matching the story's `outputs` globs on the branch (same or prior commit). VR-027.
2. **Rule 2 (warning, does not block):** committed files match a story's outputs or commit message references `(ST-NNNN)` but status ≠ `done`. VR-028.
3. **Association signals:** both outputs-glob match AND conventional-commit reference `(ST-NNNN)`.

## T-27 — `release` command for halted runs

**Status**: designed (decisions in `agent_hq/tmp/orchestrator-cli-enhancement-decisions.md`)
**Origin**: state-machine walk-through — no recovery path for halted runs without `abort` + restart.

### Decided design

1. `PhaseRecord` gains `halted_from: PhaseStatus | None`. Set by `_halt()`, read and cleared by `release`.
2. `release` restores `status = halted_from`, resets iteration count, sets mode = PAUSED. VR-029.
3. On cap-exhaustion halts, `release` resets the iteration count so the loop has room to run.
4. Operator runs `resume` after `release` to re-enter the state machine.

## T-35 — Implementation-agent branching & QA model

**Status**: backlog
**Origin**: design decision captured 2026-07-07; granularity revised 2026-07-08 after dispatching the TUI addendum backlog by hand surfaced that epic membership does not predict merge conflicts (see `docs/reviews/retro-2026-07-08.md`)

### Requirement

1. **Invocation branch:** The implementation agent MUST create a new branch from `main` at the start of each invocation, and record the **branch root** — the SHA on `main` it was cut from.
2. **Feature branches, one per story:** The agent creates a separate feature branch **per story**, off the invocation branch — not per EPIC. EPIC remains a backlog/reporting label only; it is not the branching key. Rationale: in the TUI addendum dispatch, 14 stories touching the shared composition root (`cli.py`) spanned 5 different epics — epic-scoped branches would each edit that file independently and collide five ways at merge-back, instead of the incremental, one-at-a-time conflicts that per-story branching with ordered merges produces.
3. **Merge order is overlap-aware, not epic-aware or dependency-only:** Before dispatching a wave of ready stories, group them by declared (or inferred) `outputs:` file overlap — this is in addition to, not a replacement for, ordinary `deps:` dependency-readiness:
   - Stories whose outputs are file-disjoint from every other story in the wave: dispatch and merge in parallel (any order).
   - Stories that share an output file with another story in the wave: dispatch and merge as a serial chain, one at a time, in dependency order — each story's subagent starts from the previous one's already-merged state.
   - After every merge (parallel or serial), run the full test suite before proceeding to the next merge; a red suite blocks further merges until resolved.
4. **Merge-back:** At the end of a wave, all of that wave's feature branches are merged into the invocation branch per the order established in (3).
5. **QA trigger:** All QA and review measures (Fagan review, spec review, test runs) are performed only after the last merge commit that unifies all feature branches across all waves.
6. **SHA tracking:** Two commit IDs must be tracked per invocation:
   - **branch root** — the SHA on `main` from which the invocation branch was created (captured in step 1).
   - **branch head** — the SHA of the last merge commit on the invocation branch.
7. **Review contract:** All QA/review agents must be invoked with `--base <branch-root>` and `--head <branch-head>` so they inspect exactly the delta introduced by this implementation run.

## T-36 — Automated and unattended chain execution (deferred)

**Status**: deferred (NG6)
**Origin**: scope decision 2026-07-08

The single-command automated full-chain run (`run-all`) and unattended execution (a Scheduler running the chain headlessly with `--yes`, auto-approving clean gates) are **removed from current scope**. Every run is human-attended: the Operator drives the phases one at a time via `run-phase`, approving each gate (UC-03, AG-03).

These capabilities **return together** when the orchestrator gains a **messaging channel or Web-UI** through which a human can observe a running chain and approve its gates remotely — restoring the "watch what is happening" guarantee that the interactive default provides locally. At that point, revisit: the `run-all` command and a chain sequencer, the Scheduler actor and AG-07, UC-07, the `--yes` / auto-approve flag (FR-G2, VR-009), and the auto-approve business rule that lived in UC-07.

## T-37 — Decouple pre-commit/formatting gates from `orchestrator/` for framework portability

**Status**: stub
**Origin**: session observation 2026-07-08 — `agents/`, `skills/`, `rulebooks/`, `scripts/` already live at `agent_hq/` root as a project-agnostic framework, but `.git/hooks/pre-commit` hardcodes `--config=orchestrator/.pre-commit-config.yaml`, and `mdformat`/`ruff` are only invoked via pre-commit (`uv run --project orchestrator ...`), never as direct script/workflow steps the way `spec-lint`/`arch-lint`/etc. are.

### Problem

1. The git-level pre-commit hook is orchestrator-coupled even though the framework itself (`agents/`, `skills/`, `rulebooks/`, `scripts/`) is generic. A second project under `agent_hq/` (or one bootstrapped elsewhere via `orchestrate init`) has no equivalent root-level wiring.
2. `mdformat` and `ruff` formatting are enforced *only* at commit time via pre-commit — no skill invokes them directly the way `inspect-spec` / `atam-review` / `maintain-architecture` invoke their lint scripts. Without pre-commit installed, formatting silently regresses even though the deterministic content gates (`spec-lint`, `arch-lint`, `backlog-lint`, `matrix-lint`, `statemachine-lint`) keep working, since skills call those explicitly.

### Open questions

- Move (or generate) `.pre-commit-config.yaml` at `agent_hq/` root so pre-commit finds it without a `--config` override. Scope: does it govern the framework repo itself only (mdformat/ruff on `agents/`/`skills/`/`rulebooks/`/`scripts/`), or become a merged multi-project config? `orchestrator/pre-commit-config.yaml` (the `orchestrate init` template) already assumes a per-project-copy shape — should the dev config follow that same pattern instead of living at the monorepo root?
- Add a generic `scripts/mdformat` wrapper (`uvx --with mdformat-gfm --with mdformat-ruff --with mdformat-frontmatter mdformat`) so mdformat is callable by name like the other gate scripts, independent of `orchestrator`'s pinned venv.
- Wire `ruff check --fix` / `ruff format` (already a global binary, no wrapper needed) and the new `scripts/mdformat` into the skill workflow steps that actually produce Python/Markdown (`implement-issue` for ruff; doc-writing skills — `write-prd`, `derive-spec`, `scaffold-arc42`, `maintain-architecture`, `write-adr`, `reconcile-spec`, `retrospective` — for mdformat) rather than relying solely on the pre-commit backstop.
- Tradeoff to resolve: global `ruff` / `uvx mdformat` gives portability across projects but loses the version pin `uv run --project orchestrator ...` currently guarantees.

## T-38 — Classification-driven, dispatcher-based bug fixing in `qa-agent`

**Status**: stub
**Origin**: session observation 2026-07-09 — live-testing the TUI surfaced BUG-0001 (`docs/findings/BUG-0001.md`); discussion of who fixes it exposed that `bug-hunt`'s "Fix" phase runs inline inside `qa-agent`'s own session at `qa-agent`'s one fixed `tier: strong`, regardless of the bug's actual complexity.

### Problem

Every bug currently costs the same to fix — a one-line typo and a state-machine/render-layer interaction bug (BUG-0001) both get fixed inline by `qa-agent` at `tier: strong`. This is inconsistent with the two-axis model-resolution principle already established for stories (VR-023): story `classification ∈ {trivial, standard, hard}` is the sole axis for tier-less `developer-agent` sub-agents the `implementation-agent` dispatcher spawns, letting cost scale with complexity. Bugs have no equivalent lever.

### Proposed design (from session discussion, not yet decided)

1. **Reuse the existing taxonomy.** BUG findings get a `classification ∈ {trivial, standard, hard}` field in their frontmatter — the identical enum `interface-contracts.md:146` already defines for stories, not a new bug-specific scale. Assigned by `qa-agent` at filing time during the Hunt phase.
2. **`qa-agent` becomes a second dispatcher.** Instead of self-fixing bugs inline, the Fix phase dispatches one `developer-agent` sub-agent per bug (or per coordinated batch), resolving each sub-agent's model from the bug's `classification` alone — mirroring `implementation-agent`'s dispatch exactly (VR-023's second sentence), not a new resolution mechanism.
3. **Batching mirrors T-35.** Bugs whose fixes touch disjoint files dispatch/merge in parallel; bugs sharing an output file serialize — the same overlap-aware wave grouping `implementation-agent` already does for stories (`rulebooks/branching-policy.md`).
4. **Open question:** does every bug get its own feature branch regardless of `classification`, or only `standard`/`hard` (with `trivial` staying inline in `qa-agent`, no dispatch, no branch, to avoid branch/worktree overhead on one-line fixes)?

### Touches, if implemented

`rulebooks/finding-format.md` (schema + a `finding-lint`-style enum check, mirroring `backlog-lint`'s VR-022), `docs/spec/supplementary_specs/validation-rules.md` (new VR), `agents/qa-agent.md` (dispatcher role), `skills/bug-hunt/SKILL.md` (Fix phase rewrite), possibly `rulebooks/branching-policy.md` (scope question above). Likely warrants its own ADR — hard to reverse, surprising without context, real trade-off (same bar T-25/T-35 used).

### Next step (per 2026-07-09 decision)

Not designing this now. Planned as a `grill-with-docs` practice session — specify this as a new feature against the existing orchestrator codebase (brownfield), rather than writing the ADR/spec directly.

## T-39 — Native CLI availability for the factory (agents/skills/playbooks/rulebooks)

**Status**: stub
**Origin**: session observation 2026-07-09, alongside the factory/orchestrator split (see T-40 and the same day's factory-structure draft).
**Note**: this is a factory-level concern, not orchestrator-specific — filed here only because this is the sole todos ledger that currently exists. Revisit its location if the factory ever gets its own spec/todos home.

### Problem

Right now the agent/skill/playbook/rulebook methodology is only usable from inside this monorepo, or wherever `factory-init` (see T-40's sibling discussion) has copied it into a target project. There's no "native," per-user, cross-project availability — every project needs its own copy.

### Idea floated in session

Symlink `agents/`, `skills/`, `playbooks/`, `rulebooks/` into a CLI's home directory (e.g. `~/.claude/agents`, `~/.claude/skills` — generically, `~/<user>/.cli-home/`), so any project opened with that CLI sees the factory without a per-project copy step.

### Open question

Are there better alternatives than symlinking into a single CLI's home directory?

- **Symlink per-CLI home dir** — simplest, but ties availability to one CLI's config location; multiple CLIs (Claude Code, Copilot, etc.) each need their own link, and a global link doesn't compose with per-project overrides (a project wanting a modified skill would need to break the symlink).
- **A CLI-agnostic env var / discovery convention** (e.g. `AGENT_HQ_FACTORY_HOME`, or a well-known `.factory-home` marker file CLIs could be taught to look for) — more portable across CLIs, but requires each CLI to actually support the convention; none currently do.
- **Package-manager distribution** (publish the factory as an installable package — e.g. a `uv tool`/npm-style global install with its own update mechanism) — gets versioning and update propagation for free, but is the heaviest option and reintroduces a packaging/release process for content that's currently just markdown files.
- **Keep per-project copies (`factory-init`), skip global availability entirely** — simplest to reason about, no cross-project drift risk, but every project pays the copy step and updates don't propagate without re-running init.

No decision made; needs its own design pass (possibly a `grill-me`/`grill-with-docs` session, same as T-38).

## T-40 — Orchestrator init: lead with "what do you want to do" and select a playbook

**Status**: stub
**Origin**: session observation 2026-07-09.

### Idea

The most interesting first question when starting the orchestrator (bare `orchestrate`, or a new `init` flow) isn't a menu of subcommands — it's **"what do you want to do?"**, with the answer being a `playbooks/*.md` selection (bug-fix, feature-addition, refactoring, brownfield-onboarding, greenfield-development, documentation-update, architecture-review). Selecting a playbook makes the AI aware of the operational procedure it should follow for the rest of the session, instead of the operator having to know which agent/phase to invoke by name.

### Open questions

- Does this replace or sit alongside the existing bare-invocation menu (`init`/`configure`/`run-step`/`run-phase`/`status`/`manage-run`/`backlog`)? Likely a new root-level item or the default landing screen on first-ever run (no `.orchestrator/` yet) rather than a full replacement.
- How does a selected playbook's procedure actually get "loaded" into the session — passed as context to the first agent invocation, or does it drive `run-phase` selection directly?
- `greenfield-development.fsm.yml` already exists as a formal state-machine representation for one playbook — should playbook selection require that formalization for all playbooks before this is buildable, or can prose-only playbooks (the other 6) work too?

## T-41 — ADR-0010 distribution model requires supersession

**Status**: stub
**Origin**: architecture milestone 2026-07-10 — factory structure stabilization (ST-0062, ST-0064).

### Problem

`orchestrator/docs/adr/0010-separate-tooling-from-project-directory.md` documents the pre-pivot agent_hq distribution model: a global clone of the factory, installed via `uv tool install`, with symlinks into each project directory. This model no longer matches agent_factory's current architecture, where the entire `factory/` directory is copied wholesale into a project by `init-factory` — the factory is distributed as part of the project, not as a global tool.

### Trigger for resolution

Once orchestrator's real shipping/distribution mechanism is designed and documented, supersede ADR-0010 with a new ADR reflecting the actual distribution model used to ship orchestrator and its factory.

### Open questions

- What is orchestrator's long-term distribution model (global tool, per-project copy, package-manager-published CLI, or other)? This is out of scope for the current factory-stabilization round.
- Should the new ADR address the factory's distribution separately from orchestrator's own distribution, or as a single unified mechanism?
