# System Use Cases — Agent Session Orchestrator

Technical requirements at the system's interfaces, expressed in **EARS** syntax (Ubiquitous / When / While / If-then / Where). Each requirement is atomic. Requirements reference the persona use cases (UC-##) and business rules (BR-###) they derive from.

Applying **Clean Architecture**: the orchestrator core depends on the CLI-adapter and store abstractions (see [interface-contracts](../supplementary_specs/interface-contracts.md)), never on a concrete CLI.

## Phase model

- The orchestrator shall define four phases, each with an author agent and an optional reviewer agent: requirements, architecture, planning, implementation (UC-03, BR-006).
- The orchestrator shall map the requirements phase to author `requirements-agent` and reviewer `spec-review-agent` (UC-03, BR-006).
- The orchestrator shall map the architecture phase to author `architecture-agent` and reviewer `architecture-review-agent` (UC-03, BR-006).
- The orchestrator shall map the planning phase to author `planning-agent` and no reviewer (UC-03, BR-006).
- The orchestrator shall map the implementation phase to author `implementation-agent` and reviewer `qa-agent` (UC-03, BR-006). The `implementation-agent` is a **dispatcher**: it reads the backlog dependency graph, groups ready stories into parallel waves, and spawns one `developer-agent` subagent per story with a model selected by the story's own `tier`. The orchestrator sees a single invocation; parallelism is below the adapter boundary (FR-M).
- Where a phase has no reviewer, the orchestrator shall treat a passing gate as sufficient to reach awaiting-approval (UC-02, BR-006).

## Phase artifacts

- The declared artifact paths a phase stages (BR-016) and completion-checks (FR-H1) are the author (and reviewer) agents' `outputs:` declared in their definitions under `agents/` — a single source of truth, not a duplicated list.
- The orchestrator shall stage and completion-check each phase against its author agent's declared `outputs` (UC-02, BR-016, FR-H1).

| Phase          | Author outputs (staged + completion-checked)                                                                                        | Reviewer outputs                                                                                  |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| requirements   | `docs/spec/` (prd, actor-goal-list, use_cases/, supplementary_specs/, todos.md)                                                     | `docs/reviews/spec-review-*.md`, findings store, `docs/spec/traceability.json`                    |
| architecture   | `docs/` arc42 chapters, `docs/architecture.dsl`, `docs/adr/`, `docs/assets/`                                                        | `docs/reviews/atam-review.md`, findings store                                                     |
| planning       | `backlog/ST-NNNN.md` — one story per file (markdown: strict YAML frontmatter + prose body), gated by `backlog-lint` (T-10 resolved) | — (gate-only phase)                                                                               |
| implementation | `src/**`, `tests/**`, updated `docs/spec/**`, `docs/adr/**`                                                                         | `docs/reviews/fagan-review-*.md`, `docs/reviews/security-review-*.md`, `tests/**`, findings store |

## Command interface (CLI)

- When the Operator runs `run-step <agent>`, the orchestrator shall run that agent exactly once and report the artifacts it produced (UC-01, BR-005).
- If the agent named to `run-step` is not found in the agent registry (resolved from the package-relative `agents/` path), then the orchestrator shall exit non-zero without launching a subprocess (UC-01, BR-011).
- When the Operator runs `run-phase <phase>`, the orchestrator shall drive that phase's author-reviewer loop until the loop condition is met or the iteration cap is reached (UC-02).
- The Operator shall drive the phases in their fixed dependency order by running `run-phase` for each in turn, approving each gate before the next (UC-03, BR-006).
- When the Operator runs `status`, the orchestrator shall report the current phase, iteration, open-findings count, last gate result, and run mode (UC-05).
- When the Operator runs `resume`, the orchestrator shall continue the run from its last checkpoint (UC-06).
- When the Operator runs `approve`, the orchestrator shall record the approval, advance `current_phase`, and set mode to `paused` — the operator runs `resume` to continue (UC-04, FAGAN-0035). For `empty-commit` phases, the gate-passed check is skipped (FAGAN-0038).
- When the Operator runs `reject`, the orchestrator shall record the rejection and halt the run (UC-04, BR-012).
- When the Operator runs `init`, the orchestrator shall scaffold the project directory with the required tooling structure (agents, skills, scripts, docs directories, `model.conf`, pre-commit config, and CLI instruction file).
- When the Operator runs `release`, the orchestrator shall restore a halted phase to its pre-halt status (`halted_from`), reset the iteration counter to zero, and set run mode to `paused` (ADR-0015, VR-029). It shall refuse if the run is not halted or `halted_from` is absent.
- When the Operator runs `abort`, the orchestrator shall terminate the active run, set run mode to `complete`, release the run lock, and exit. It shall refuse if no active run exists.

### CLI flags

- `--model <id>` — explicit model override; takes precedence over `model.conf` (FR-K3).
- `--story <ST-NNNN>` — story ID for tier-based model selection; resolves the story's `tier` from the backlog store and passes it to `ModelResolver` (FAGAN-0037).
- `--no-interactive` — force headless invocation for this run, overriding the interactive default (ADR-0010).
- `--adapter <name>` — select the CLI adapter (default `copilot`).
- `--cap <n>` — iteration cap (default 3, VR-002).
- `--timeout <seconds>` — per-invocation timeout in seconds (default 1800, NFR-6).

## Session and adapter

- The orchestrator shall run every agent invocation in a fresh CLI subprocess with no inherited session context (UC-02, BR-004).
- The orchestrator shall obtain agent invocation from a CLI-adapter interface rather than a concrete CLI binary (UC-01).
- Where the target adapter is Copilot, the orchestrator shall invoke it through the Copilot adapter implementation (UC-02).
- If an agent subprocess exceeds its configured timeout, then the orchestrator shall terminate it and treat the step as a failed iteration (UC-02).
- If the adapter reports an authentication or availability failure, then the orchestrator shall halt without counting an author iteration (UC-02, BR-018).
- By default, and whenever a TTY is attached, the adapter shall inherit the terminal's stdio so the Operator can watch and converse with the agent; in interactive mode, an empty-commit gate result shall pause for approval rather than retry (ADR-0010). Where `--no-interactive` is set, or no TTY is attached, the adapter shall run the agent headlessly.

## Model selection

- The planning agent shall assign each story a `tier` of `economy`, `standard`, or `strong` (FR-K1, BR-021) — the model strength its work needs.
- For `run-step`, the orchestrator shall resolve the model by looking up the agent's declared tier directly against `model.conf` for the active CLI. An explicit `--model` flag overrides this resolution entirely (FR-K3, FR-R11).
- For `run-phase`, the orchestrator shall resolve each orchestrator-invoked agent independently from that agent's declared tier against `model.conf` (FR-R12).
- During the implementation phase, the `implementation-agent` dispatcher shall select each developer sub-agent's model from the story's own `tier` alone, below the adapter boundary; developer agents declare no tier of their own, and the two axes never combine on one invocation (FR-K2, FR-M, FR-R12).
- When an explicit `--model` is given on `run-step`, the orchestrator shall not consult `model.conf` (FR-K3).
- If `model.conf` has no model for the agent's effective tier and active CLI, the orchestrator shall halt as a configuration error, unless `on_missing` is set to the adapter default (FR-K4, BR-020).
- `model.conf` is the operator-authored artifact model resolution reads directly (FR-K5, ADR-0020, ADR-0021). The per-adapter model dictionary (`.orchestrator/config.toml`) is a separate, local cache used for menu-mode display, populated from `model.conf` on a gap-fill basis — not read at resolution time.

## Gate (pre-commit)

- When an author agent completes, the orchestrator shall stage the phase's declared artifact paths and commit against the run branch so the pre-commit hooks run as the gate (UC-02, BR-016).
- The phase gate hook shall exit non-zero if and only if at least one error-severity finding exists (UC-02, BR-002).
- If a committed artifact set produces an error-severity finding, then the orchestrator shall ingest the deterministic findings and re-run the author agent (UC-02, BR-002).
- If the gate hook errors rather than reports findings, then the orchestrator shall halt without counting an author iteration (UC-02, BR-015).
- If the commit is empty because the artifacts are unchanged, then the orchestrator shall treat the iteration as no-progress (UC-02, BR-016).

## Findings store

- The orchestrator shall assign each finding a unique identifier from a monotonic allocator on ingest (UC-02, BR-019).
- The orchestrator shall write each finding as one JSON file, validated against the finding schema, under the findings directory (UC-02).
- At the start of each authoring iteration, the orchestrator shall mark the phase's prior open findings superseded (UC-02, BR-014).
- The orchestrator shall treat a phase as unfinished while any latest-iteration finding has status open (UC-02, BR-014).

## Loop control and approval

- While the iteration count for a phase is below the cap, the orchestrator shall loop back to the author agent when the latest review has open findings (UC-02, BR-001).
- If the iteration cap is reached with findings still open, then the orchestrator shall halt and summon the Operator (UC-02, BR-003).
- When a phase reaches a clean gate and review, the orchestrator shall persist awaiting-approval and exit rather than block (UC-02, BR-003).
- While a phase is awaiting approval, the orchestrator shall not start the next phase (UC-03, UC-04).
- The orchestrator shall present a phase gate only when the gate passed and open findings equal zero (UC-04, BR-007).

## State, resume, observability

- The orchestrator shall hold a single-run lock and refuse to start while a lock is held or a run is running (UC-03, BR-017).
- The orchestrator shall create or select a dedicated run branch at the start of a run (UC-03, BR-016).
- The orchestrator shall record the run's branch, current phase, iteration, and mode in `.orchestrator/run.json`, written atomically (UC-06, BR-017).
- The orchestrator shall not repeat an already-completed phase when resuming (UC-06, BR-009).
- If tracked artifacts changed since the checkpoint, then the orchestrator shall re-run the gate before continuing (UC-06, BR-013).
- The orchestrator shall log each subprocess invocation with agent, role, adapter, duration, exit status, and gate outcome (UC-03).

## TUI presentation and navigation

- When the Operator runs `orchestrate` with no subcommand in a supported interactive terminal, the orchestrator shall enter the root TUI menu rather than treat the invocation as a usage error (UC-08, FR-P1, FR-V1, BR-030, BR-035).
- If the Operator runs `orchestrate` with no subcommand in a non-interactive or unsupported terminal, then the orchestrator shall print a diagnostic with direct-mode guidance and exit cleanly without mutating run state (UC-08, FR-V4, BR-031, BR-033).
- While menu mode is active, the orchestrator shall render exactly one menu node at a time, mark the active item with `-> `, and pre-select the `★` item when one is declared (UC-08, FR-P2, FR-P5, BR-032).
- When the Operator presses `↑` or `↓` in a menu node, the orchestrator shall move the active selection within that node and shall invoke no action (UC-08, FR-P3, BR-033).
- When the Operator presses Enter on a menu item, the orchestrator shall open the selected child node; when the Operator presses Enter on a function leaf, the orchestrator shall dispatch the corresponding application action (UC-08, FR-P4, BR-036).
- When the Operator presses `q` or `Esc` in a non-root menu, the orchestrator shall return to the parent menu (UC-08, FR-P6, BR-034).
- When the Operator presses `qq` or `Ctrl+C` at any menu depth, the orchestrator shall exit menu mode immediately, dispatch no function, and mutate no run state (UC-08, FR-P6, BR-033, BR-034).
- When the Operator opens a display node, the orchestrator shall render read-only content and return to the parent node on the next keypress (UC-08, FR-P8, BR-033, BR-034).
- When a function leaf starts a long-running operation, the orchestrator shall exit menu mode before invoking the operation and shall hand control to the existing streaming terminal-output path (UC-08, FR-P7, BR-036).
- Ubiquitously, menu navigation, menu entry, display viewing, back navigation, and TUI exit shall not mutate `.orchestrator/run.json`, findings, or logs unless a function leaf is dispatched (UC-08, BR-033).
- If the Operator supplies a subcommand, then the orchestrator shall bypass menu mode and preserve the existing direct-mode command semantics unchanged (UC-08, FR-V2, BR-035).
- Ubiquitously, every TUI function leaf shall dispatch to the same application service or handler as its direct-mode equivalent (UC-08, FR-V3, BR-036).

## Configuration management

- The orchestrator shall persist operator defaults in `.orchestrator/config.toml`, including at least `adapter`, `timeout`, `cap`, and `auto_approve` (UC-09, FR-Q1, FR-Q2, BR-037).
- When the orchestrator resolves an invocation setting, it shall apply the precedence order `menu selection > CLI flag > config.toml > built-in default` (UC-09, FR-Q3, BR-040).
- If `.orchestrator/config.toml` is absent, then the orchestrator shall continue with built-in defaults and shall create the file only on the first successful persist (UC-09, FR-Q5, BR-037).
- When the orchestrator persists a configuration change, it shall write `.orchestrator/config.toml` atomically (UC-09, FR-Q4, BR-038).
- If `.orchestrator/config.toml` is malformed or contains an invalid stored value, then the orchestrator shall refuse the affected action and report the offending file and key (UC-09, FR-Q6, BR-041).
- When the Operator changes a persisted setting, the orchestrator shall validate the submitted value before writing it (UC-09, FR-Q4, BR-039).

## CLI adapter management

- The orchestrator shall maintain an adapter registry that records each registered adapter's logical name and executable path (UC-10, FR-R1, BR-042, BR-043).
- When the Operator selects adapter auto-detect, the orchestrator shall scan `$PATH` for known adapter binaries and register only candidates that pass validation as supported adapters (UC-10, FR-R2, BR-042, BR-048).
- When the Operator adds an adapter manually, the orchestrator shall validate the supplied name and binary path and persist the registration atomically (UC-10, FR-R3, BR-042, BR-043, BR-048).
- When the Operator removes an adapter, the orchestrator shall remove the adapter and its model dictionary in the same atomic change (UC-10, FR-R4, BR-044, BR-048).
- The orchestrator shall maintain, for each registered adapter, a model dictionary that maps the abstract tiers `economy`, `standard`, and `strong` to concrete model identifiers (UC-10, FR-R5, BR-044, BR-045).
- When the Operator opens `list models` for an adapter, the orchestrator shall render that adapter's registered model identifiers and their tier assignments (UC-10, FR-R6, BR-045).
- When the Operator adds or removes a model mapping for an adapter, the orchestrator shall persist the change atomically in that adapter's model dictionary (UC-10, FR-R7, BR-045, BR-048).
- When the selected adapter supports model discovery, the orchestrator shall query the adapter for available models and shall leave configuration unchanged if discovery is unsupported or fails validation (UC-10, FR-R8, BR-047, BR-048).
- The agent registry shall parse each agent's `tier` frontmatter and expose it to model resolution as first-class metadata (UC-10, FR-R10, BR-049).
- When the Operator runs `run-step` without an explicit `--model`, the orchestrator shall resolve the default model from the selected agent's declared tier against `model.conf` for the selected adapter (UC-10, UC-11, FR-R11, BR-046, BR-049).
- When the Operator runs `run-phase` without an explicit `--model`, the orchestrator shall resolve each invoked agent independently from that agent's declared tier against `model.conf` (UC-10, UC-02, FR-R12, BR-046, BR-049).
- When the Operator opens `configure > model-matrix`, the orchestrator shall provide show, edit, and validate actions for the matrix and shall reuse the existing validation workflow (UC-10, FR-R9, BR-048).

## Skill-scoped execution

- When the Operator runs `run-step <agent> --skill <skill>`, the orchestrator shall treat `--skill` as a request to execute one named skill rather than the full workflow (UC-11, FR-S1, BR-051).
- If the Operator supplies `--skill`, then the orchestrator shall verify that the requested skill is declared by the selected agent before launching any adapter subprocess (UC-11, FR-S2, BR-050).
- When a skill-scoped step is selected, the orchestrator shall compose an invocation that instructs the agent to execute only the named skill (UC-11, FR-S3, BR-051).
- In menu mode, when the Operator selects `run-step` for an agent, the orchestrator shall present `all skills` plus that agent's declared skills, with `all skills` pre-selected by default (UC-11, FR-S4, BR-052).
- The agent registry shall parse optional `interactive: true|false` frontmatter and expose it as agent metadata (UC-11, FR-S5, BR-054).
- Where no explicit interactive override is supplied by menu or CLI flag, the orchestrator shall use the selected agent's declared `interactive` policy; when an explicit override is supplied, it shall apply only to that invocation (UC-11, FR-S6, BR-054).

## Enhanced status views

- In menu mode, the orchestrator shall expose `overview`, `phase details`, `findings`, and `log` as distinct read-only status views (UC-08, AG-13, FR-T1, BR-033).
- When the Operator opens `status > overview`, the orchestrator shall render the status projection returned by `StatusService.get_status()` (UC-05, AG-13, FR-T2, BR-033).
- When the Operator opens `status > phase details`, the orchestrator shall render a per-phase table containing phase name, author, reviewer, status, iteration, last gate result, and `halted_from` (UC-08, AG-13, FR-T3, BR-033).
- When the Operator opens `status > findings`, the orchestrator shall render a table of open findings for the active run, including at least finding id, severity, artifact, message, and status (UC-08, AG-13, FR-T4, BR-033).
- When the Operator opens `status > log`, the orchestrator shall render the invocation log, including agent, role, model, exit code, duration, and gate outcome (UC-08, AG-13, FR-T5, BR-033).
- Ubiquitously, status views shall be read-only and shall not mutate run state, findings, or log data (UC-08, AG-13, FR-T6, BR-033).

## Backlog views

- In menu mode, the orchestrator shall expose `list`, `by-epic`, `ready`, and `view story` as read-only backlog views (UC-12, FR-U1, BR-056).
- When the Operator opens `backlog > list`, the orchestrator shall render every story with `id`, `title`, `epic`, `tier`, `status`, and `deps` (UC-12, FR-U2, BR-059).
- When the Operator opens `backlog > by-epic`, the orchestrator shall group stories under epic headings and retain each story's status indicator (UC-12, FR-U3, BR-059).
- When the Operator opens `backlog > ready`, the orchestrator shall render only stories whose `status` is `pending` and whose dependencies all resolve to stories with `status: done` in the same loaded snapshot (UC-12, FR-U4, BR-057).
- When the Operator opens `backlog > view story`, the orchestrator shall present a selectable story list and, after selection, display the story's full frontmatter and prose body (UC-12, FR-U5, BR-060).
- Ubiquitously, backlog views shall be observational only and shall not edit, reorder, create, or delete backlog data (UC-12, FR-U6, BR-056).
