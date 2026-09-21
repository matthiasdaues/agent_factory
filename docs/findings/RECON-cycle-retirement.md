---
id: RECON-cycle-retirement
source: reconcile-spec
severity: major
category: defect
artifact: docs/ and packages/factory/
status: open
traces: [ST-0276, ST-0277, ST-0262, ST-0263, ST-0278]
---

# Stale Cycle-Orchestration References — Complete Inventory

Compiled: 2026-09-21

The cycle-based orchestration was retired in ST-0262 through ST-0278. This
inventory lists every stale reference that remains in the documentation.
No edits have been made. The user decides which items to update and which
to remove.

Exclusions applied per the task scope:

- Usage-capture cycle fields (optional nullable fields, intentionally retained)
- `phase advance/retry` and `transition-lint` (active mechanisms)
- `.fsm.yml` files (active)
- `research-orchestrator` (separate active concept, not the retired `packages/orchestrator/`)
- Files under `docs/adr/`, `docs/proposals/`, `docs/handoffs/`, `docs/reviews/` (historical records)

______________________________________________________________________

## docs/arc42/05_building_block_view.md

### F-01 (line 14)

**Stale text:** `| **State Adapter** | Thin command adapters that acquire locks, call the engine for decisions, write cycle state, and present recommendations |`

**Fix:** Replace "write cycle state" with "write playbook state markers." The State Adapter contains `phase advance/retry` and `run-step`. It does not write cycle state; it writes the playbook state marker.

**Rationale:** `cycle select`/`cycle retry` commands no longer exist. The adapter writes `.current-work/playbook-state.yml`, not cycle state files.

### F-02 (line 15)

**Stale text:** `| **Validator** | Enforces gates, permissions, cycle-model integrity, project-declared test gate presence, agent-context structure, and semantic quality checks |`

**Fix:** Replace "cycle-model integrity" with "playbook phase ordering." `transition-lint` validates playbook phase ordering via FSM output globs, not cycle model integrity.

**Rationale:** The cycle model is retired. `transition-lint` reads the FSM and playbook marker.

### F-03 (line 19)

**Stale text:** `| Delivery Model | Declarative YAML cycle graph with five delivery cycles, terminal DONE node, artifact declarations, trusted validators, and every route | YAML (storage) |`

**Fix:** Remove this row. `packages/factory/engine/models/delivery.yaml` exists on disk but nothing imports it. The delivery model is an orphaned artifact.

**Rationale:** All code that loaded or consumed the delivery model was removed in ST-0263.

### F-04 (line 20)

**Stale text:** `| Cycle Schemas | JSON Schema Draft 2020-12 definitions for cycle-model-v1 and cycle-state-v1 validation | JSON Schema (storage) |`

**Fix:** Remove this row. No code validates against these schemas.

**Rationale:** The cycle schemas are orphaned. No validator references them.

### F-05 (line 21)

**Stale text:** `| Cycle State Files | One YAML workstream state file per active workstream under .current-work/cycles/; tracks cycle, attempt, revision, work refs, and grant | YAML (storage) |`

**Fix:** Remove this row. No code reads or writes `.current-work/cycles/` for cycle state. Workstream state v2 lives under `.agent-factory/workstreams/` with an immutable four-field schema (`schema_version`, `workstream_id`, `topic`, `origin_ref`).

**Rationale:** Cycle state files with cycle/attempt/revision/work/grant fields are retired.

### F-06 (line 22)

**Stale text:** `| Session Bindings | Session-to-workstream navigation state under .current-work/session-bindings/<cli>/<session-id>.yaml |`

**Fix:** Update path to `.agent-factory/workstreams/sessions/<session-id>.yaml`. Session bindings v2 record `session_id`, `workstream_id`, and `bound_at` only. No revision, digest, or cycle fields.

**Rationale:** Session bindings moved from `.current-work/session-bindings/` to `.agent-factory/workstreams/sessions/`.

### F-07 (line 40)

**Stale text:** `| **transition-lint** | Pre-commit hook (git commit) | Cycle model integrity and workstream state files; reports failed recommendation evidence |`

**Fix:** Replace description with "Validates playbook phase ordering by mapping staged files to FSM output globs; blocks commits that stage files belonging to a non-current phase."

**Rationale:** `transition-lint` validates the playbook FSM, not cycle models. The current architecture.dsl already has the correct description for this component (line 41 of the DSL).

### F-08 (line 51)

**Stale text:** `Three additional on-demand validators enforce semantic code quality and architecture routing. Two are invoked by the implementation-agent dispatcher (not by hooks) and are described in section 5.2.3; one routes between cycles:`

**Fix:** Replace "one routes between cycles" with "one determines architecture routing." The `module-graph-check` routes between the architecture phase and skipping it, not between cycles.

**Rationale:** Cycles are retired. The module-graph-check determines whether the architecture phase is needed.

### F-09 (line 57)

**Stale text:** `| **module-graph-check** | Orchestrating session, at architecture boundary | Feature touches no new modules or inverted dependencies | 0 (skip architecture), 1 (enter) |`

**Fix:** The exit code descriptions say "skip architecture" and "enter" which is correct, but this is listed as "routing between cycles" in the preceding text. No change to this row itself, but the F-08 context must be fixed.

**Rationale:** Covered by F-08.

### F-10 (line 74)

**Stale text:** `- **Cycle-gate evaluation**: Trusted validators declared in the delivery model reference charter test commands. The Readiness Evaluator checks their results as artifact evidence for route recommendations. Blocks when the test configuration is absent or test_command is missing.`

**Fix:** Replace entire bullet with: "**Precondition evaluation**: The Eligibility Engine's precondition evaluator checks agent `inputs.required` declarations against the filesystem. Agents that require passing tests declare `testing.yaml` as a required input. Blocks when the test configuration is absent or `test_command` is missing."

**Rationale:** The delivery model, trusted validators, and Readiness Evaluator route recommendations are all retired concepts. The Eligibility Engine with precondition evaluation is the active mechanism.

### F-11 (line 186)

**Stale text:** `| **Workstream Resolver** | Resolves workstream identity from session binding and validates revision and digest consistency |`

**Fix:** Remove "and validates revision and digest consistency." Workstream v2 state files are immutable identity records. Session bindings v2 have no revision or digest fields.

**Rationale:** Revision and digest are cycle-era fields removed in v2.

### F-12 (line 217)

**Stale text:** `| phase | Human, orchestrator | ...`

**Fix:** Replace "Human, orchestrator" with "Human" in the Invoked by column.

**Rationale:** `packages/orchestrator/` is retired. Only humans invoke `phase advance/retry`.

### F-13 (line 220)

**Stale text:** `| trigger | Human, orchestrator, run-step skill | ...`

**Fix:** Replace "Human, orchestrator, run-step skill" with "Human, run-step skill."

**Rationale:** `packages/orchestrator/` is retired.

### F-14 (line 233)

**Stale text:** `| init-factory | Human, orchestrator | ...`

**Fix:** Replace "Human, orchestrator" with "Human."

**Rationale:** `packages/orchestrator/` is retired.

### F-15 (line 234)

**Stale text:** `| update-factory | Human, orchestrator | ...`

**Fix:** Replace "Human, orchestrator" with "Human."

**Rationale:** `packages/orchestrator/` is retired.

### F-16 (line 235)

**Stale text:** `| remove-factory | Human, orchestrator | ...`

**Fix:** Replace "Human, orchestrator" with "Human."

**Rationale:** `packages/orchestrator/` is retired.

______________________________________________________________________

## docs/arc42/06_runtime_view.md

### F-17 (line 7-8)

**Stale text:** `This chapter describes key interaction sequences for Factory gates, cycle transitions, and local usage analysis.`

**Fix:** Replace "cycle transitions" with "playbook phase transitions" or remove the term.

**Rationale:** Cycle transitions are retired.

### F-18 (line 45)

**Stale text:** `Factory ensures test gates exist; the project decides what runs inside them. Testing is project-owned infrastructure declared in docs/testing.yaml. Factory's guardrails and cycle gates read that declaration.`

**Fix:** Replace "cycle gates" with "eligibility preconditions" or "the precondition evaluator."

**Rationale:** Cycle gates are retired.

### F-19 (lines 47-71)

**Stale text:** The entire section 6.3.1 "Sequence: Charter Declaration and Cycle Gate" uses `cycle select` as the entry point and shows the Eligibility Engine producing route recommendations for cycle transitions.

**Fix:** Rewrite this sequence to show the precondition-based eligibility flow via `intent select`/`intent assess` rather than `cycle select`. Remove `cycle select` participant and replace with `intent` CLI. Remove "cycle state" write step.

**Rationale:** `cycle select` is retired. The active mechanism is `intent select`.

### F-20 (line 188)

**Stale text:** `MG-->>S: Exit 0 — skip architecture cycle`

**Fix:** Replace "skip architecture cycle" with "skip architecture phase."

**Rationale:** "Cycle" as an orchestration concept is retired.

### F-21 (line 190)

**Stale text:** `MG-->>S: Exit 1 — enter architecture cycle`

**Fix:** Replace "enter architecture cycle" with "enter architecture phase."

**Rationale:** Same as F-20.

### F-22 (line 198)

**Stale text:** `Tests module-graph topology only: new modules, changed public interfaces, inverted dependency directions. A new entity in an existing module does not trigger the architecture cycle.`

**Fix:** Replace "architecture cycle" with "architecture phase."

**Rationale:** Same as F-20.

______________________________________________________________________

## docs/arc42/07_deployment_view.md

### F-23 (lines 14-20)

**Stale text:** `- **Cycle orchestration state** under .current-work/cycles/ holds one YAML workstream state file per active workstream, OS-level lock files under .current-work/cycles/.locks/, and session bindings under .current-work/session-bindings/<cli>/<session-id>.yaml. The delivery model at packages/factory/engine/models/delivery.yaml and JSON Schema definitions for cycle-model-v1 and cycle-state-v1 are read-only inputs to the Cycle Engine.`

**Fix:** Replace entire bullet with: "**Workstream state** under `.agent-factory/workstreams/` holds immutable workstream identity files. Session bindings under `.agent-factory/workstreams/sessions/` record session-to-workstream mappings. The Eligibility Engine reads agent definitions and the repository; it does not read a delivery model."

**Rationale:** The cycle orchestration state directory, paths, delivery model, cycle schemas, and Cycle Engine are all retired. Workstream state v2 and session bindings v2 use different paths and schemas.

### F-24 (lines 57-59)

**Stale text:** `Cycle orchestration state files under .current-work/cycles/ are local, git-ignored working state. They survive Factory updates and are removed only by explicit operator action or remove-factory.`

**Fix:** Replace "Cycle orchestration state files under `.current-work/cycles/`" with "Workstream state files under `.agent-factory/workstreams/`" and adjust the lifecycle description accordingly.

**Rationale:** Same path and concept retirement as F-23.

______________________________________________________________________

## docs/arc42/08_crosscutting_concepts.md

### F-25 (line 7)

**Stale text:** `Creation is agentic; validation is deterministic. Tests, cycle-model gates, and dangerous-command checks are triggered mechanically`

**Fix:** Replace "cycle-model gates" with "precondition checks" or "eligibility evaluation."

**Rationale:** Cycle-model gates are retired.

### F-26 (line 18)

**Stale text:** `| Commits gated | Pre-commit hook runs transition-lint | Validates workstream state files |`

**Fix:** Replace "Validates workstream state files" with "Validates playbook phase ordering via FSM output globs."

**Rationale:** `transition-lint` validates FSM output globs, not workstream state files.

### F-27 (line 31)

**Stale text:** `An agent reporting "tests passed" is unverified hearsay. A charter-declared test command exiting 0 from a cycle gate is a fact.`

**Fix:** Replace "from a cycle gate" with "from a precondition check" or "from a mechanically triggered gate."

**Rationale:** Cycle gates are retired.

### F-28 (line 38)

**Stale text:** `2. **Cycle gate resolves the declared command** -- the Readiness Evaluator checks trusted validators that reference charter test commands. Results are artifact evidence for route recommendations.`

**Fix:** Replace with: "2. **Precondition evaluation resolves the declared command** -- the Eligibility Engine evaluates `inputs.required` declarations against the repository, including test configuration presence."

**Rationale:** Readiness Evaluator, trusted validators, and route recommendations are all retired cycle-era concepts.

### F-29 (line 50)

**Stale text:** `| **Pre-commit** | git commit | transition-lint (cycle model and state validation) |`

**Fix:** Replace "cycle model and state validation" with "playbook phase ordering."

**Rationale:** `transition-lint` validates the FSM, not cycle models.

### F-30 (line 52)

**Stale text:** `| **Cycle gate** (eval) | cycle select invocation | Readiness Evaluator with trusted validator results | Manual invocation required | (recommendation) |`

**Fix:** Remove this row or replace with a row describing `intent select` / `intent assess` invocation. The cycle gate mechanism is retired.

**Rationale:** `cycle select` is retired. The active equivalent is `intent select`.

### F-31 (line 77)

**Stale text:** `If testing.yaml is absent or test_command is missing, the cycle gate blocks with a clear message.`

**Fix:** Replace "the cycle gate blocks" with "the precondition evaluator reports the gap."

**Rationale:** Cycle gates are retired.

### F-32 (lines 111-132)

**Stale text:** Section 8.5 "Single Source of Truth: Delivery Model and Workstream State" describes `packages/factory/engine/models/delivery.yaml` and `.current-work/cycles/<workstream-id>.yaml` as sources of truth.

**Fix:** Rewrite section 8.5 to describe the v2 workstream state (`.agent-factory/workstreams/`) and the precondition-based eligibility model as the active state model. Remove delivery model references.

**Rationale:** Delivery model and cycle state files under `.current-work/cycles/` are both retired.

### F-33 (line 122)

**Stale text:** `If the workstream state file says phase: REFINE, then the workstream is in REFINE`

**Fix:** Remove this sentence. REFINE is a cycle name, not a phase.

**Rationale:** Cycle names (IDEA, CONCEPT, ROADMAP, REFINE, REALIZE) are retired.

### F-34 (lines 253-258)

**Stale text:** Section 8.13 "Precondition-Based Agent Eligibility" subsection "Delivery model on disk" and "Workstream concurrency" refer to the delivery model remaining on disk and workstream state files under `.current-work/cycles/`.

**Fix:** In the "Delivery model on disk" subsection, add that `delivery.yaml` is an orphaned artifact with no consumers and should be retired or archived. In "Workstream concurrency," update paths from `.current-work/cycles/` to `.agent-factory/workstreams/` and remove references to OS-level locks, revision history, and session binding revision tracking (cycle-era concepts).

**Rationale:** The delivery model has no consumers. Workstream state v2 is immutable (no locks needed). Session bindings v2 have no revision or digest fields.

______________________________________________________________________

## docs/arc42/09_architecture_decisions.md

### F-35 (line 34)

**Stale text:** `orchestrator/ is one possible trigger among peers (you at the terminal, orchestrator CLI).`

**Fix:** Replace with: "A human at the terminal or an automated script can trigger these mechanisms." Remove the orchestrator CLI reference.

**Rationale:** `packages/orchestrator/` is retired.

### F-36 (line 42)

**Stale text:** `FSM gates (script_exit_zero) resolve charter:test_command from docs/testing.yaml and integrate test execution into phase advance entry conditions.`

**Fix:** This accurately describes the still-active FSM gate behavior but is in a section that presents it alongside cycle concepts. Keep but consider noting that FSM gates remain active while cycle gates are retired.

**Rationale:** FSM gates and `phase advance` entry conditions are still active. The wording itself is accurate.

### F-37 (line 48)

**Stale text:** `ADR-0001 declares one root .pre-commit-config.yaml for the monorepo, with each subproject's hooks namespaced (e.g., -orchestrator suffix) and path-scoped (files: ^orchestrator/).`

**Fix:** Remove the orchestrator examples. Replace with a current subproject example or generalize.

**Rationale:** `packages/orchestrator/` is retired. Its pre-commit hooks no longer exist.

### F-38 (line 65)

**Stale text:** `the orchestrator does not duplicate CLI-owned capture.`

**Fix:** Remove this clause. There is no orchestrator to duplicate anything.

**Rationale:** `packages/orchestrator/` is retired.

### F-39 (lines 157-172)

**Stale text:** Section "Cycle-Based Orchestration" describes ADR-0017 and ADR-0018 as accepted decisions implementing the cycle-based delivery model.

**Fix:** Add a note that ADR-0017 and ADR-0018 describe the cycle-based orchestration that was subsequently retired in ST-0263. The Eligibility Engine with precondition-based agent selection replaced the cycle-based routing. The ADRs remain as historical records but the described architecture is no longer active.

**Rationale:** The cycle-based orchestration was retired. ADR-0017 and ADR-0018 describe a design that no longer exists in code.

______________________________________________________________________

## docs/arc42/10_quality_requirements.md

### F-40 (line 5)

**Stale text:** `This chapter defines testable quality scenarios for the cycle-based orchestration architecture.`

**Fix:** Rewrite to reflect the precondition-based eligibility architecture. Most scenarios in this chapter describe cycle-era behavior that no longer exists.

**Rationale:** The cycle-based orchestration is retired. Quality scenarios should describe the active architecture.

### F-41 (lines 9-19)

**Stale text:** QS-1 "Non-linear routing" describes route selection through the delivery model and cycle transitions.

**Fix:** Rewrite to describe the precondition-based model, where agent selection is driven by precondition evidence rather than cycle graph routes.

**Rationale:** Delivery model routes and cycle transitions are retired.

### F-42 (lines 21-31)

**Stale text:** QS-2 "Human routing authority" describes override of engine route recommendations.

**Fix:** Rewrite. The human now selects agents from the eligibility list (`intent select`), not cycles from route recommendations.

**Rationale:** Route recommendations and cycle selection are retired.

### F-43 (lines 33-43)

**Stale text:** QS-3 references "Cycle Engine container" and "section 5.3" which uses the heading "Level 2: Component View -- Cycle Engine."

**Fix:** Update reference to the Eligibility Engine container (section 5.3 heading was already updated to "Eligibility Engine" in the building block view, but the reference text here still says "Cycle Engine").

**Rationale:** The Cycle Engine container was renamed to Eligibility Engine.

### F-44 (lines 45-55)

**Stale text:** QS-4 "Concurrent workstreams" describes OS-level locks on `.current-work/cycles/` state files and session binding revision/digest conflicts.

**Fix:** Rewrite. Workstream v2 state files are immutable (no locks needed). Session bindings v2 have no revision or digest fields. Concurrency semantics have changed.

**Rationale:** Cycle-era concurrency model (OS locks, revision/digest checking) is retired.

### F-45 (lines 57-67)

**Stale text:** QS-5 "Delegation with bounded autonomy" describes `delegated_attempt_limit`, delegation grants, and cycle retry limits.

**Fix:** Remove or rewrite. Delegation grants and per-cycle attempt limits are retired concepts.

**Rationale:** All delegation and retry code was removed in ST-0263.

### F-46 (lines 69-79)

**Stale text:** QS-6 "Observable-state resume" references "the delivery model" and cycle-era state derivation.

**Fix:** Rewrite to describe observable-state resume from the precondition-based model (workstream state v2, agent definitions, repository evidence).

**Rationale:** The delivery model is retired. The principle of observable-state resume remains valid but should reference the active state model.

### F-47 (lines 81-91)

**Stale text:** QS-7 "Declarative model constraint" describes validation of `delivery.yaml` against the cycle-model-v1 JSON Schema.

**Fix:** Remove or archive. No code loads or validates `delivery.yaml`.

**Rationale:** The delivery model and its schemas are orphaned. No validator references them.

### F-48 (lines 93-103)

**Stale text:** QS-8 "Backward compatibility" describes `phase advance` as a diagnostic stub that exits 2 and names `cycle select` as the replacement.

**Fix:** Rewrite. `phase advance/retry` are the ACTIVE mechanisms, not diagnostic stubs. `cycle select/retry` no longer exist. The characterization tests described here verify behavior that is the opposite of reality.

**Rationale:** The relationship is inverted: `phase advance/retry` are active, `cycle select/retry` are retired.

### F-49 (lines 105-118)

**Stale text:** Section 10.2 "Quality Attribute Priority" references ADR-0017 Pugh Matrix weights and ties all scenarios to the cycle-based design.

**Fix:** Rewrite to reference the active design's quality attributes.

**Rationale:** The Pugh Matrix evaluated the now-retired cycle-based design.

______________________________________________________________________

## docs/arc42/12_glossary.md

### F-50 (line 9)

**Stale text:** `| **Agent** | ... referenced in a cycle's agent sequence. |`

**Fix:** Remove "or referenced in a cycle's agent sequence." Agents are now selected by precondition evaluation, not cycle sequences.

**Rationale:** Cycle agent sequences are retired.

### F-51 (line 12)

**Stale text:** `| **Artifact Declaration** | A named artifact within a cycle declaration in the delivery model, with trusted validators... |`

**Fix:** Remove this row. Artifact declarations as a concept tied to cycle declarations are retired.

**Rationale:** No code uses artifact declarations from the delivery model.

### F-52 (line 13)

**Stale text:** `| **Charter (testing)** | ... Factory's cycle gates and guardrails read this charter. |`

**Fix:** Replace "cycle gates" with "eligibility preconditions" or "guardrails."

**Rationale:** Cycle gates are retired.

### F-53 (line 15)

**Stale text:** `| **Cycle** | A named node in the delivery model's directed graph... IDEA, CONCEPT, ROADMAP, REFINE, or REALIZE... |`

**Fix:** Mark as "(Retired)" or remove. Cycles as orchestration nodes are retired.

**Rationale:** The cycle graph is retired. No code reads cycle names.

### F-54 (line 16)

**Stale text:** `| **Cycle Engine** | The pure domain-logic container that loads the delivery model, evaluates artifact readiness... |`

**Fix:** Replace with the Eligibility Engine definition: "The pure domain-logic container that evaluates agent preconditions against the repository, derives per-agent readiness, and classifies agents by eligibility. Returns immutable decisions without writing state."

**Rationale:** The Cycle Engine was replaced by the Eligibility Engine.

### F-55 (line 17)

**Stale text:** `| **Cycle State File** | A YAML file under .current-work/cycles/<workstream-id>.yaml tracking the workstream's current cycle, attempt number, revision... |`

**Fix:** Mark as "(Retired)" or remove. Replace with a "Workstream State File" entry describing the v2 immutable identity record under `.agent-factory/workstreams/`.

**Rationale:** Cycle state files are retired.

### F-56 (line 18)

**Stale text:** `| **Delegation Grant** | An operator-issued authorization that allows agents to advance a workstream through cycles without pausing... |`

**Fix:** Mark as "(Retired)" or remove. Delegation grants are retired.

**Rationale:** All delegation code was removed in ST-0263.

### F-57 (line 19)

**Stale text:** `| **Delegated Attempt Limit** | The per-cycle maximum number of retry attempts... |`

**Fix:** Mark as "(Retired)" or remove. Delegated attempt limits are retired.

**Rationale:** Same as F-56.

### F-58 (line 20)

**Stale text:** `| **Delivery Model** | The declarative YAML file (packages/factory/engine/models/delivery.yaml) that defines the five delivery cycles... Validated against the cycle-model-v1 JSON Schema on every load. |`

**Fix:** Mark as "(Retired, orphaned on disk)" or remove. Nothing loads or validates this file.

**Rationale:** The delivery model is orphaned. No code imports it.

### F-59 (line 23)

**Stale text:** `| **Entry Condition** | (Legacy) ... Superseded by artifact readiness evaluation in the cycle model. |`

**Fix:** Remove the "(Legacy)" and "Superseded" language. Entry conditions are still active in the FSM (`phase advance` evaluates them). The cycle model is what was superseded, not entry conditions.

**Rationale:** Entry conditions remain active; the cycle model that was supposed to supersede them is itself retired.

### F-60 (line 25)

**Stale text:** `| **FSM** | (Legacy) Finite State Machine. A .fsm.yml file... Superseded by the delivery model's cycle graph. |`

**Fix:** Remove "(Legacy)" and "Superseded by the delivery model's cycle graph." The FSM is the ACTIVE mechanism. The cycle graph that was supposed to supersede it is itself retired.

**Rationale:** The FSM and `.fsm.yml` files are active. The cycle-based delivery model is retired.

### F-61 (line 26)

**Stale text:** `| **Gate Condition** | (Legacy) ... Superseded by trusted validators and artifact declarations in the cycle model. |`

**Fix:** Remove "(Legacy)" and "Superseded" language. Gate conditions remain active in the FSM. Trusted validators and artifact declarations in the cycle model are retired.

**Rationale:** Same pattern as F-59 and F-60.

### F-62 (line 29)

**Stale text:** `| **User** | ... approving cycle transitions. Primary actor, peer to Orchestrator-as-Trigger. |`

**Fix:** Replace "approving cycle transitions" with "approving agent selections." Remove "peer to Orchestrator-as-Trigger."

**Rationale:** Cycle transitions and Orchestrator-as-Trigger are both retired.

### F-63 (line 31)

**Stale text:** `| **Marker** | (Legacy) ... Superseded by per-workstream cycle state files. |`

**Fix:** Remove "(Legacy)" and "Superseded by per-workstream cycle state files." The marker (`.current-work/playbook-state.yml`) is still the active mechanism for `phase advance/retry` and `transition-lint`. The cycle state files that were supposed to supersede it are themselves retired.

**Rationale:** The playbook marker is active. The cycle state files are retired.

### F-64 (line 32)

**Stale text:** `| **Observable-State Resume** | ... from files on disk (delivery model, workstream state, outputs, findings)... |`

**Fix:** Remove "delivery model" from the list. The delivery model is retired.

**Rationale:** No code reads the delivery model for state derivation.

### F-65 (line 33)

**Stale text:** `| **Orchestrator-as-Trigger** | The orchestrator/ Python CLI (work in progress -- not yet operational)... |`

**Fix:** Mark as "(Retired)" or remove. `packages/orchestrator/` is retired.

**Rationale:** `packages/orchestrator/` was retired in ST-0276.

### F-66 (line 34)

**Stale text:** `| **Phase** | (Legacy) Informal term for a state in a playbook's FSM. Superseded by "cycle" in the delivery model. |`

**Fix:** Remove "(Legacy)" and "Superseded by 'cycle' in the delivery model." Phase is the active term. The cycle concept is retired.

**Rationale:** Phases are active; cycles are retired.

### F-67 (line 35)

**Stale text:** `| **Playbook** | ... The playbook concept coexists with cycles; playbooks may reference cycles rather than FSM states. |`

**Fix:** Remove "The playbook concept coexists with cycles; playbooks may reference cycles rather than FSM states." Playbooks reference FSM states. Cycles are retired.

**Rationale:** The playbook-cycle coexistence was the cycle-era model. Playbooks now reference FSM states only.

### F-68 (line 37)

**Stale text:** `| **Readiness Evidence** | The result of evaluating trusted validators against a cycle's artifact declarations... |`

**Fix:** Rewrite to describe precondition evidence from the Eligibility Engine, or mark as "(Retired)."

**Rationale:** Trusted validators and cycle artifact declarations are retired.

### F-69 (line 38)

**Stale text:** `| **Route** | A directed edge in the delivery model connecting one cycle to another... The 19 declared routes... |`

**Fix:** Mark as "(Retired)" or remove. Routes in the cycle graph are retired.

**Rationale:** No code reads routes from the delivery model.

### F-70 (line 39)

**Stale text:** `| **Route Recommender** | A Cycle Engine component... |`

**Fix:** Mark as "(Retired)" or remove. The Route Recommender was a Cycle Engine component that was retired.

**Rationale:** All Cycle Engine components were removed.

### F-71 (line 40)

**Stale text:** `| **Session Binding** | A YAML file under .current-work/session-bindings/<cli>/<session-id>.yaml that tracks which workstream a CLI session is observing, at which revision, and with which SHA-256 digest. |`

**Fix:** Update path to `.agent-factory/workstreams/sessions/<session-id>.yaml`. Remove "at which revision, and with which SHA-256 digest." Session bindings v2 record `session_id`, `workstream_id`, and `bound_at` only.

**Rationale:** Session bindings moved and simplified. No revision or digest fields exist.

### F-72 (line 41)

**Stale text:** `| **State Adapter** | The container of thin command adapters (cycle select, cycle retry, phase stub, run-step)... write cycle state, and present recommendations. |`

**Fix:** Replace `cycle select`, `cycle retry`, `phase stub` with `phase advance/retry`. Replace "write cycle state" with "write playbook state markers." Remove "present recommendations."

**Rationale:** `cycle select/retry` are retired. `phase` is not a stub. The State Adapter contains `phase advance/retry` and `run-step`.

### F-73 (line 43)

**Stale text:** `| **transition-lint** | ... validates cycle model integrity and workstream state files. Finding codes: TL-CYCLE-MODEL (error), TL-CYCLE-STATE (error), TL-ROUTE-EVIDENCE (warning). |`

**Fix:** Replace description with: "validates playbook phase ordering by mapping staged files to FSM output globs; blocks commits that stage files belonging to a non-current phase." Remove the cycle-era finding codes (`TL-CYCLE-MODEL`, `TL-CYCLE-STATE`, `TL-ROUTE-EVIDENCE`).

**Rationale:** `transition-lint` validates the FSM, not cycle models. The finding codes reference retired concepts.

### F-74 (line 45)

**Stale text:** `| **Trusted Validator** | A deterministic check declared in the delivery model... |`

**Fix:** Mark as "(Retired)" or remove. Trusted validators declared in the delivery model are retired.

**Rationale:** No code reads trusted validator declarations from the delivery model.

### F-75 (line 46)

**Stale text:** `| **Workstream** | ... with its own cycle state file, revision history, and OS-level lock. |`

**Fix:** Replace "cycle state file, revision history, and OS-level lock" with "immutable state file recording schema version, ID, topic, and origin reference."

**Rationale:** Workstream state v2 is immutable (four fields). No revision history or OS-level locks.

### F-76 (line 47)

**Stale text:** `| **Workstream Resolver** | A Cycle Engine component... |`

**Fix:** Replace "Cycle Engine" with "Eligibility Engine."

**Rationale:** The Cycle Engine was renamed to Eligibility Engine.

### F-77 (line 54)

**Stale text:** `| **module-graph-check** | ... Exit 0 skips the architecture cycle; exit 1 enters it. |`

**Fix:** Replace "architecture cycle" with "architecture phase."

**Rationale:** Cycles are retired.

### F-78 (line 105)

**Stale text:** `| FSM | Finite State Machine (legacy; superseded by cycle-based delivery model) |`

**Fix:** Remove "(legacy; superseded by cycle-based delivery model)." The FSM is active. The cycle-based delivery model is retired.

**Rationale:** Same as F-60.

______________________________________________________________________

## docs/arc42/architecture.dsl

### F-79 (line 11)

**Stale text:** `orchestrator = softwareSystem "Orchestrator CLI" "Python CLI that invokes factory mechanisms programmatically" "External"`

**Fix:** Remove this element. `packages/orchestrator/` is retired.

**Rationale:** The Orchestrator CLI no longer exists.

### F-80 (line 73)

**Stale text:** `deliveryModel = container "Delivery Model" "Declarative YAML cycle graph with delivery cycles, terminal DONE node, artifact declarations, trusted validator references, and declared routes" "YAML file" "Storage"`

**Fix:** Remove this container. The delivery model is orphaned.

**Rationale:** No code reads this file.

### F-81 (line 74)

**Stale text:** `cycleStateFiles = container "Workstream State Files" "One YAML workstream state file per active workstream under .current-work/cycles/; each tracks cycle, attempt, revision, work references, and optional delegation grant" "YAML files" "Storage"`

**Fix:** Rewrite to describe v2 workstream state: `workstreamState = container "Workstream State" "Immutable workstream identity records under .agent-factory/workstreams/; each records schema_version, workstream_id, topic, and origin_ref" "YAML files" "Storage"`

**Rationale:** Cycle state files with cycle/attempt/revision fields are retired. Workstream state v2 uses a different path and schema.

### F-82 (line 75)

**Stale text:** `sessionBindings = container "Session Bindings" "Session-to-workstream navigation state under .current-work/session-bindings/<cli>/<session-id>.yaml; tracks observed revision and SHA-256 digest" "YAML files" "Storage"`

**Fix:** Update path to `.agent-factory/workstreams/sessions/`. Remove "tracks observed revision and SHA-256 digest." Session bindings v2 record `session_id`, `workstream_id`, and `bound_at`.

**Rationale:** Session bindings moved and simplified.

### F-83 (lines 142-144)

**Stale text:** Three `orchestrator ->` relationships: `orchestrator -> intentCli`, `orchestrator -> phaseAdvance`, `orchestrator -> trigger`.

**Fix:** Remove all three relationships. The Orchestrator CLI is retired.

**Rationale:** `packages/orchestrator/` is retired. These relationships have no implementation.

### F-84 (line 166)

**Stale text:** `eligibilityEngine -> deliveryModel "Loads delivery graph and route declarations"`

**Fix:** Remove this relationship. The Eligibility Engine does not read the delivery model.

**Rationale:** The delivery model is orphaned. The Eligibility Engine reads agent definitions and the repository, not a delivery graph.

### F-85 (line 171)

**Stale text:** `phaseAdvance -> cycleStateFiles "Reads workstream state for entry condition checks"`

**Fix:** Remove or replace. `phaseAdvance` reads the playbook marker (`.current-work/playbook-state.yml`), not cycle state files.

**Rationale:** Cycle state files are retired. The playbook marker is the active state source.

### F-86 (line 173)

**Stale text:** `runStep -> cycleStateFiles "Reads workstream state and delegation grant"`

**Fix:** Remove or replace with a relationship to the v2 workstream state and session bindings. `run-step` should read from `.agent-factory/workstreams/` and `.agent-factory/workstreams/sessions/`.

**Rationale:** Cycle state files and delegation grants are retired.

### F-87 (line 180)

**Stale text:** `transitionLint -> cycleStateFiles "Maps staged files against FSM output globs"`

**Fix:** `transition-lint` maps staged files against the FSM, not cycle state files. Update this relationship to reference `stateFiles` (which contains the playbook marker) instead of `cycleStateFiles`.

**Rationale:** `transition-lint` reads the playbook marker and the FSM, not cycle state files.

______________________________________________________________________

## docs/arc42/CONTEXT-MAP.md

### F-88 (line 7)

**Stale text:** `... a State Adapter (intent select, run-step) that owns state writes and lock acquisition...`

**Fix:** `intent select` does not own state writes or lock acquisition. The State Adapter contains `phase advance/retry`. Replace "(intent select, run-step)" with "(phase advance/retry, run-step)."

**Rationale:** `intent select` is in the Eligibility Engine and is read-only. The State Adapter owns `phase advance/retry`.

______________________________________________________________________

## docs/spec/prd.md

### F-89 (line 11)

**Stale text:** `... without requiring the orchestrator/ Python CLI that used to own this job.`

**Fix:** Replace "that used to own this job" with "which has since been retired."

**Rationale:** The `orchestrator/` Python CLI is retired.

### F-90 (line 13)

**Stale text:** `orchestrator/ used to run its own PhaseRunner, an independent state machine for driving the agent chain. That ownership has inverted. orchestrator/ is now one possible trigger of factory/'s mechanisms...`

**Fix:** Rewrite this paragraph to note that `orchestrator/` has been retired entirely. It is no longer "one possible trigger" -- it does not exist.

**Rationale:** `packages/orchestrator/` was retired in ST-0276.

### F-91 (line 33)

**Stale text:** `- **NG1** -- Not a re-implementation of orchestrator/'s PhaseRunner. orchestrator/ may call these same mechanisms...`

**Fix:** Rewrite to note that `orchestrator/` is retired. NG1 should state that Factory does not maintain a parallel Python orchestration CLI.

**Rationale:** `packages/orchestrator/` is retired.

### F-92 (line 44)

**Stale text:** `- **Orchestrator-as-Trigger** (secondary) -- the nested orchestrator/ Python CLI (work in progress -- not yet operational), a peer of the User.`

**Fix:** Remove this actor entirely or mark as "(Retired)."

**Rationale:** `packages/orchestrator/` is retired. It is not a target actor.

### F-93 (line 141)

**Stale text:** `- You can drive greenfield-development.fsm.yml end to end using only transition-lint, phase advance, phase retry, and trigger -- no orchestrator/ CLI involved.`

**Fix:** Remove the "no orchestrator/ CLI involved" clause. The orchestrator CLI is retired, so this criterion is trivially met.

**Rationale:** The success criterion compares against a CLI that no longer exists.

### F-94 (line 142)

**Stale text:** `- orchestrator/ can drive the identical playbook run through the same four mechanisms, adding no flow-control logic of its own.`

**Fix:** Remove this criterion entirely. `packages/orchestrator/` is retired.

**Rationale:** Cannot verify a criterion against retired code.

______________________________________________________________________

## docs/spec/scope-map.md

### F-95 (line 87)

**Stale text:** `| Orchestrator package is dormant (cancelled, may be revisited later) | deferred | | [activity-graph-orchestration.feature](...) |`

**Fix:** Update status to "implemented" -- the orchestrator package has been retired (not just dormant). The implementation evidence is ST-0276.

**Rationale:** The orchestrator was retired in ST-0276, not just deferred.

### F-96 (line 88)

**Stale text:** `| Cycle-based orchestration proposal is superseded | specified | | [activity-graph-orchestration.feature](...) |`

**Fix:** Update status to "implemented" -- the proposal was superseded per ST-0277.

**Rationale:** The cycle-based proposal was superseded with characterization tests in ST-0277.

### F-97 (line 93)

**Stale text:** `| Human operator switches workstreams mid-session | deferred | | [cycle-based-orchestration.feature](...) |`

**Fix:** Update the feature link from `cycle-based-orchestration.feature` to `activity-graph-orchestration.feature` (if the rule migrated) or leave deferred with a note that the source feature file describes retired behavior.

**Rationale:** `cycle-based-orchestration.feature` specifies the retired cycle-based model.

### F-98 (line 94)

**Stale text:** `| Reconciliation runs when an activity changes code or canonical artifacts | deferred | | [cycle-based-orchestration.feature](...) |`

**Fix:** Same as F-97. Update the feature link away from the retired feature file.

**Rationale:** Same as F-97.

### F-99 (line 97)

**Stale text:** `| Brownfield operator bootstraps the canonical concept model | deferred | | [cycle-based-orchestration.feature](...) |`

**Fix:** Same as F-97.

**Rationale:** Same as F-97.

### F-100 (line 98)

**Stale text:** `| LinkML entity model serves as canonical domain source | specified | | [cycle-based-orchestration.feature](...) |`

**Fix:** Same as F-97. The LinkML decision may still be valid but should not link to the retired feature file.

**Rationale:** Same as F-97.

______________________________________________________________________

## docs/spec/cycle-based-orchestration.feature

### F-101 (entire file)

**Stale text:** The entire file (approximately 310 lines) specifies cycle-based orchestration behavior that is retired.

**Fix:** Archive to `docs/~archive/spec/` or delete. The activity-graph-orchestration model has superseded this specification. Scope-map rows that reference this file (F-97 through F-100) must be updated first.

**Rationale:** All code described in this feature file was retired in ST-0262 through ST-0278. The file specifies `cycle select`, `cycle retry`, delivery model loading, cycle state files, delegation grants, and attempt limits -- none of which exist.

______________________________________________________________________

## docs/spec/test-gate-presence-gaps.md

### F-102 (line 11)

**Stale text:** `| User, Orchestrator-as-Trigger | Resolve test command from charter for FSM gates |`

**Fix:** Replace "User, Orchestrator-as-Trigger" with "User."

**Rationale:** Orchestrator-as-Trigger is retired.

### F-103 (line 19)

**Stale text:** `| User, Orchestrator-as-Trigger | Gate contract is exit-code-only |`

**Fix:** Replace "User, Orchestrator-as-Trigger" with "User."

**Rationale:** Same as F-102.

______________________________________________________________________

## docs/spec/todo.md

### F-104 (line 57)

**Stale text:** `- source: discussion of [PROP-09](../proposals/cycle-based-orchestration.md#review--2026-09-14)`

**Fix:** The PROP-09 reference links to the cycle-based orchestration proposal. This todo item (T-0006) is marked resolved, so the stale link is a historical record. Add a note that the source proposal is superseded.

**Rationale:** The cycle-based orchestration proposal is superseded.

### F-105 (line 71)

**Stale text:** `[Cycle-Based Orchestration proposal](../proposals/cycle-based-orchestration.md#linkml-entity-model-contract) owns migration of live scenarios...`

**Fix:** This resolution text references a superseded proposal as owning migration work. Add a note that the proposal is superseded; the migration ownership should be reassigned.

**Rationale:** The cycle-based orchestration proposal no longer owns anything.

______________________________________________________________________

## packages/factory/README.md

No stale cycle-orchestration references found. The README correctly describes the active mechanisms.

______________________________________________________________________

## packages/factory/docs/factory-guide.md

### F-106 (line 584)

**Stale text:** `Three semantic gates fire between a developer's commit and merge, enforced by the gate-check loop in feature-addition:`

**Fix:** Replace "Three" with "Two." Mutation testing is project-owned infrastructure, not a Factory gate.

**Rationale:** ADR-0012 was amended to reduce from three to two gates.

### F-107 (line 589)

**Stale text:** `| Mutation testing | .agent-factory/factory/scripts/mutation-testing | Mutation testing -- verifies that tests detect injected faults, not just that they run. |`

**Fix:** Remove this row. There is no `scripts/mutation-testing` gate. Mutation testing is project-owned infrastructure that Factory encourages via the `mutation-analysis` skill.

**Rationale:** Mutation testing was removed as a Factory-owned gate per ADR-0012 amendment.

### F-108 (line 590)

**Stale text:** `| Dependency check | .agent-factory/factory/scripts/dependency-check | Dependency vulnerability scan against known advisories. |`

**Fix:** Replace description with: "Validates that module import directions match declarations in `architecture.dsl`." The current description confuses this with a security vulnerability scanner.

**Rationale:** `dependency-check` validates architecture dependency rules, not security vulnerabilities.

______________________________________________________________________

## packages/factory/skills/run-step/SKILL.md

### F-109 (line 3)

**Stale text:** `description: Resolve the next agent from the workstream's current cycle and agent eligibility, then dispatch it.`

**Fix:** Replace "from the workstream's current cycle and agent eligibility" with "from agent eligibility preconditions."

**Rationale:** Cycles are retired. Agent resolution is precondition-based.

### F-110 (line 9)

**Stale text:** `Dispatches one agent invocation... Re-derives "what's next" from the workstream state file and agent eligibility`

**Fix:** Remove "from the workstream state file" or update to reference the v2 workstream state.

**Rationale:** The cycle-era workstream state file format is retired.

### F-111 (line 13)

**Stale text:** `Read the session binding (.current-work/session-bindings/<session-id>.yaml) to find the active workstream, then read its state file (.current-work/cycles/<workstream-id>.yaml) for the current cycle.`

**Fix:** Update paths. Session binding is at `.agent-factory/workstreams/sessions/<session-id>.yaml`. Workstream state is at `.agent-factory/workstreams/<workstream-id>.yaml`. Remove "for the current cycle" -- workstream state v2 has no cycle field.

**Rationale:** Paths and schema changed in v2.

### F-112 (line 15)

**Stale text:** `run .agent-factory/factory/scripts/cycle list --dir .current-work/cycles/`

**Fix:** The `cycle list` command does not exist. Replace with guidance to list workstreams via `engine/workstream.py::list_workstreams` scanning `.agent-factory/workstreams/`.

**Rationale:** `cycle list` command is retired.

### F-113 (line 23)

**Stale text:** `| None | Tell the user no agents are eligible for this cycle. Offer to list available cycles. |`

**Fix:** Replace "for this cycle" with "given current preconditions." Replace "Offer to list available cycles" with "Offer to run `intent select` to see agent eligibility."

**Rationale:** Cycles are retired.

### F-114 (line 24)

**Stale text:** `| One | Confirm with the user: "Agent X is eligible for cycle Y. Dispatch?" |`

**Fix:** Replace "for cycle Y" with "based on precondition evidence."

**Rationale:** Cycles are retired.

### F-115 (line 29)

**Stale text:** `Check the current cycle's expected outputs against what is on disk`

**Fix:** Replace "the current cycle's expected outputs" with "the current phase's expected outputs" or "the agent's declared outputs."

**Rationale:** Cycles are retired.

### F-116 (line 34)

**Stale text:** `| Outputs exist, gate passes clean, no open findings | Step is done -- offer .agent-factory/factory/scripts/cycle select to advance to the next cycle. |`

**Fix:** The `cycle select` command does not exist. Replace with guidance to use `phase advance` or `intent select` for the next step.

**Rationale:** `cycle select` is retired.

### F-117 (line 48)

**Stale text:** `This skill does not read .current-work/playbook-state.yml. The workstream state file is the single source of truth for which cycle the workstream is in.`

**Fix:** This statement is now inverted. The playbook state marker IS the active source of truth. The workstream state file (v2) is an immutable identity record with no cycle field. Rewrite to reflect the active state model.

**Rationale:** The cycle-era state file is retired. The playbook marker is active.

### F-118 (line 53)

**Stale text:** `- [.agent-factory/factory/scripts/cycle](../../scripts/cycle)`

**Fix:** Remove. The `cycle` script does not exist.

**Rationale:** `cycle` command is retired.

______________________________________________________________________

## packages/factory/playbooks/greenfield-development.md

### F-119 (line 16)

**Stale text:** `- [ ] Orchestrator configured OR manual session management ready`

**Fix:** Remove "Orchestrator configured OR." The orchestrator is retired.

**Rationale:** `packages/orchestrator/` is retired.

### F-120 (lines 67-68)

**Stale text:** `capture-charter --init ... Expected outputs: docs/agent-context/stack.yaml, docs/agent-context/workflow.yaml, docs/agent-context/governance.yaml`

**Fix:** Replace `capture-charter` with `capture-context` and update expected outputs to `docs/agent-context.md`. The YAML agent context files are retired.

**Rationale:** The YAML agent context was replaced by `docs/agent-context.md` in 0.9.0.

### F-121 (lines 75, 90, 111, 124, 140, 161, 201, 235, 250, 271, 282, 303, 316, 337)

**Stale text:** `orchestrator run-phase <phase-name>` (14 occurrences)

**Fix:** Remove the `orchestrator run-phase` lines. Keep only the "OR manual:" alternative, which is the only working invocation method.

**Rationale:** `packages/orchestrator/` is retired. There is no `orchestrator` command.

### F-122 (line 82-85)

**Stale text:** `records it in docs/agent-context/stack.yaml (falls back to docs/charter/tech-stack.md) incrementally`

**Fix:** Replace with `records it in docs/agent-context.md`. The YAML files and charter are retired.

**Rationale:** The YAML agent context was replaced by `docs/agent-context.md`.

### F-123 (line 135)

**Stale text:** `the architecture agent invokes update-charter to record it in docs/agent-context/stack.yaml (falls back to docs/charter/tech-stack.md)`

**Fix:** Same as F-122.

**Rationale:** Same as F-122.

### F-124 (lines 177-179)

**Stale text:** References to `docs/agent-context/stack.yaml`, `docs/agent-context/workflow.yaml`, `docs/agent-context/governance.yaml`, `docs/charter/tech-stack.md`, `docs/charter/development.md`, `docs/charter/house-rules.md`.

**Fix:** Replace with references to `docs/agent-context.md`.

**Rationale:** The YAML agent context and charter files are retired.

### F-125 (line 208)

**Stale text:** `reads the project context from docs/agent-context/*.yaml (falls back to docs/charter/*.md)`

**Fix:** Replace with "reads the project context from `docs/agent-context.md`."

**Rationale:** Same as F-122.

### F-126 (lines 397-399)

**Stale text:** `Current phase: Check orchestrator state OR manually track in session notes ... Loop count: Track manually or via orchestrator iteration counter`

**Fix:** Remove "Check orchestrator state OR" and "or via orchestrator iteration counter."

**Rationale:** `packages/orchestrator/` is retired.

______________________________________________________________________

## packages/factory/playbooks/feature-addition.md

### F-127 (lines 118, 123, 135, 153, 158, 172)

**Stale text:** `'orchestrator/**/*.py'` in the step inputs/outputs frontmatter (6 occurrences).

**Fix:** Remove these path entries. `packages/orchestrator/` is retired. No implementation stories should read or write orchestrator files.

**Rationale:** The orchestrator package is retired.

### F-128 (lines 374, 386, 462, 471, 492, 531, 539, 560, 581)

**Stale text:** `orchestrator run-phase <phase-name>` (9 occurrences)

**Fix:** Remove the `orchestrator run-phase` lines. Keep only the "OR manual:" alternative.

**Rationale:** Same as F-121.

______________________________________________________________________

## packages/factory/playbooks/refactoring.md

### F-129 (line 99)

**Stale text:** `**OR via orchestrator:**`

**Fix:** Remove this heading and the orchestrator code block that follows (lines 99-119).

**Rationale:** `packages/orchestrator/` is retired.

### F-130 (line 119)

**Stale text:** `orchestrator run-phase implementation`

**Fix:** Remove.

**Rationale:** Same as F-129.

### F-131 (line 145)

**Stale text:** `orchestrator run-phase qa`

**Fix:** Remove.

**Rationale:** Same as F-129.

______________________________________________________________________

## packages/factory/playbooks/bug-fix.md

### F-132 (line 54)

**Stale text:** `**Orchestrator approach**:`

**Fix:** Remove this heading and the orchestrator code block that follows (lines 54-74).

**Rationale:** `packages/orchestrator/` is retired.

### F-133 (line 74)

**Stale text:** `orchestrator run-phase implementation`

**Fix:** Remove.

**Rationale:** Same as F-132.

### F-134 (line 100)

**Stale text:** `orchestrator run-phase qa`

**Fix:** Remove.

**Rationale:** Same as F-132.

### F-135 (line 142)

**Stale text:** `For **critical production bugs**, skip orchestrator:`

**Fix:** Replace "skip orchestrator" with "use the fast-track approach."

**Rationale:** No orchestrator exists to skip.

______________________________________________________________________

## packages/factory/playbooks/documentation-update.md

### F-136 (lines 34, 78, 116, 133)

**Stale text:** `orchestrator run-phase <phase-name>` (4 occurrences)

**Fix:** Remove the `orchestrator run-phase` lines. Keep only the "OR manual:" alternative.

**Rationale:** Same as F-121.

______________________________________________________________________

## packages/factory/playbooks/architecture-review.md

### F-137 (lines 69, 137, 146)

**Stale text:** `orchestrator run-phase <phase-name>` (3 occurrences)

**Fix:** Remove the `orchestrator run-phase` lines. Keep only the "OR manual:" alternative.

**Rationale:** Same as F-121.

______________________________________________________________________

## packages/factory/skills/create-backlog-epics/SKILL.md

### F-138 (line 96)

**Stale text:** `Bad: "Validate the delivery model against versioned schemas"`

**Fix:** Replace with a current bad example. The delivery model is retired.

**Rationale:** The bad example references a retired artifact.

### F-139 (lines 98-101)

**Stale text:** Bad example table row mentioning "Delivery model schema validation", "transition-lint -> Cycle Model Loader -> diagnostics", and "Run transition-lint and see validation results."

**Fix:** Replace with a current bad example that illustrates the same anti-pattern (internal rule masquerading as user capability) using active system concepts.

**Rationale:** The Cycle Model Loader and delivery model schema validation are retired.

### F-140 (lines 102-106)

**Stale text:** Good example mentions "Check which cycle the evidence supports and choose the next one", "`cycle select`", "Readiness Evaluator recommends routes", "chosen cycle and evidence appear in workstream state", and "Run `cycle select`, choose REALIZE despite its warning."

**Fix:** Replace with a current good example using the active eligibility model: e.g., "See which agents are eligible for the workstream and dispatch one" using `intent select`.

**Rationale:** `cycle select`, the Readiness Evaluator, and cycle-based routing are retired.

______________________________________________________________________

## packages/factory/skills/create-backlog-story-slices/SKILL.md

### F-141 (line 28)

**Stale text:** `"Start a workstream and select any cycle", not "Workstream creation and cycle selection."`

**Fix:** Replace with a current example: "Start a workstream and see eligible agents", not "Workstream creation and agent selection."

**Rationale:** "select any cycle" references the retired cycle selection mechanism.

______________________________________________________________________

## packages/factory/skills/dependency-check/SKILL.md

### F-142 (line 38)

**Stale text:** `factory must_not_depend_on orchestrator`

**Fix:** Remove this example rule. `packages/orchestrator/` is retired. The dependency rule is moot.

**Rationale:** No `orchestrator` module exists for `factory` to depend on.

______________________________________________________________________

## packages/factory/skills/grilling/SKILL.md

### F-143 (line 23)

**Stale text:** `- **Subagent session** (you were spawned by an orchestrator or another agent)`

**Fix:** Replace "by an orchestrator or another agent" with "by another agent." This is a generic use of "orchestrator" but may confuse readers into thinking the retired `packages/orchestrator/` is meant.

**Rationale:** Clarity. The retired orchestrator should not appear in active skill definitions.

______________________________________________________________________

## packages/factory/engine/models/delivery.yaml

### F-144 (on disk, not referenced)

**Stale text:** The entire file exists at `packages/factory/engine/models/delivery.yaml` (6,646 bytes).

**Fix:** Archive or delete. No code imports, loads, or validates this file. It is an orphaned artifact from the retired cycle-based orchestration.

**Rationale:** All code that consumed the delivery model was removed in ST-0263.

______________________________________________________________________

## Summary

| Category                                            |   Count |
| --------------------------------------------------- | ------: |
| Architecture documentation (arc42 chapters)         |      88 |
| Architecture DSL                                    |      10 |
| Specification (PRD, scope map, feature files, gaps) |      16 |
| Playbooks                                           |      20 |
| Skills                                              |       7 |
| Factory guide                                       |       3 |
| Orphaned artifact                                   |       1 |
| **Total**                                           | **145** |

All findings are classified as **Spec stale** (documentation does not match the code-as-built). No code defects were found -- the code correctly implements the precondition-based eligibility model. The documentation has not caught up.
