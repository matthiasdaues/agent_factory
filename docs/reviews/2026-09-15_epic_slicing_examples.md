# Compare epic slicing examples

Prompt: Assume the planning agent role and do an epic slicing for the "cycle based orchestratioN"

## Copilot 5.6 Luna:

### initial result

┌───┬──────────────────────────────┬───────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────┐
│ # │ EPIC outcome — what a person │ Boundaries crossed │ Demo sentence │
│ │ or system can do after │ │ │
├───┼──────────────────────────────┼───────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ 1 │ Assess delivery evidence and │ Cycle Engine → Delivery Model and │ Run the cycle assessment against a sample workstream and see artifact │
│ │ recommend the next cycle │ Cycle Schemas → Validator │ checks, warnings, supported routes, and every available cycle. │
├───┼──────────────────────────────┼───────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ 2 │ Start, continue, and switch │ session menu → State Adapter → Cycle │ Start a named topic, reopen it from the workstream list, then confirm a │
│ │ delivery workstreams │ State Files and Session Bindings │ switch to another topic without changing workstreams automatically. │
├───┼──────────────────────────────┼───────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ 3 │ Select and retry cycles with │ State Adapter → Cycle Engine → Cycle │ Select a recommended or non-recommended cycle, retry it, and observe │
│ │ safe state transitions │ State Files and operating-system │ attempt resets, revision increments, stale-state conflicts, and │
│ │ │ locks │ lock-timeout results. │
├───┼──────────────────────────────┼───────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ 4 │ Delegate bounded route │ Delegation Evaluator and Retry │ Grant [CONCEPT, REFINE, REALIZE], run the workstream, observe evidence at │
│ │ execution and resume from │ Evaluator → run-step → Dispatcher and │ each transition, and see execution pause when the grant or retry limit is │
│ │ cycle state │ CLI agent sessions │ exhausted. │
├───┼──────────────────────────────┼───────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ 5 │ Establish canonical concept │ brownfield-onboarding → scope-map, │ Bootstrap a brownfield repository, create a linked research brief for a │
│ │ evidence and return research │ entity-model, and architecture.dsl → │ concept gap, and resume the declared delivery cycle after the validated │
│ │ results to delivery │ Research brief and Cycle Engine │ report returns. │
├───┼──────────────────────────────┼───────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ 6 │ Deliver selected work │ planning-agent → backlog artifacts → │ Select validated stories, complete their implementation and quality │
│ │ through realization and │ implementation-agent, Validator, and │ gates, then receive a DONE recommendation or a route back to the artifact │
│ │ reconcile changes │ reconciliation assessment │ that no longer matches the code. │
├───┼──────────────────────────────┼───────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ 7 │ Preserve factory contracts │ phase and playbook consumers → cycle │ Run the old phase advance and phase retry commands to receive diagnostic │
│ │ while replacing phase │ adapters → Dispatcher, Catalog, and │ replacement messages, while installed-shape and catalog checks confirm │
│ │ routing │ installed Factory copy │ existing agent and skill identities remain available. │
├───┼──────────────────────────────┼───────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ 8 │ Capture and analyze │ Session Bindings → Usage Capture → │ Capture records with and without a binding, then group analysis by │
│ │ workstream and cycle usage │ Usage Record Contract → Usage │ workstream and cycle while reporting unassigned records as unavailable │
│ │ │ Analysis Runtime │ rather than misattributing them. │
└───┴──────────────────────────────┴───────────────────────────────────────┴───────────────────────────────────────────────────────────────────────────┘

### after re-applying the write gate

┌───┬──────────────────────────┬─────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ # │ EPIC outcome — what a │ Boundaries crossed │ Demo sentence │
│ │ person or system can do │ │ │
│ │ after │ │ │
├───┼──────────────────────────┼─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 1 │ Assess repository │ Cycle Engine (decision logic) → Delivery Model │ Run an assessment for a workstream and see passed checks, │
│ │ evidence and recommend │ (declared cycle graph) → Validator (artifact checks) │ warnings, supported routes, and all available cycles. │
│ │ the next cycle │ │ │
├───┼──────────────────────────┼─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 2 │ Start, continue, and │ Session Menu (operator entry point) → State Adapter │ Start a named topic, reopen it from the workstream list, │
│ │ switch delivery │ (state-changing commands) → Cycle State Files and │ and confirm a switch without an automatic change. │
│ │ workstreams │ Session Bindings (workstream and session records) │ │
├───┼──────────────────────────┼─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 3 │ Select and retry cycles │ State Adapter → Cycle Engine → Cycle State Files and │ Select a recommended or unsupported cycle, retry it, and │
│ │ without losing valid │ lock handling │ see attempt resets, revision changes, stale-state │
│ │ state │ │ conflicts, and busy-workstream results. │
├───┼──────────────────────────┼─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 4 │ Delegate a bounded route │ Delegation Evaluator (grant rules) → run-step │ Grant [CONCEPT, REFINE, REALIZE], run the workstream, and │
│ │ and resume it from │ (next-action resolver) → Dispatcher (agent launcher) │ see execution pause when the grant or retry limit is │
│ │ recorded state │ │ exhausted. │
├───┼──────────────────────────┼─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 5 │ Bootstrap a brownfield │ brownfield-onboarding → Scope Map, Entity Model, and │ Start with an existing repository and receive the three │
│ │ repository into a │ Architecture Model → Validator and Cycle Engine │ canonical concept artifacts plus a readiness result that │
│ │ reviewed concept │ │ reports missing evidence. │
│ │ baseline │ │ │
├───┼──────────────────────────┼─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 6 │ Link research evidence │ Research Brief → Research Report → Cycle Engine and │ Create a research brief from a concept gap, validate its │
│ │ to a delivery cycle and │ State Adapter │ report, and resume the declared delivery cycle with the │
│ │ resume delivery │ │ report reference. │
├───┼──────────────────────────┼─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 7 │ Deliver selected work │ Planning Agent → backlog artifacts → Implementation │ Select validated stories, complete implementation checks, │
│ │ and reconcile │ Agent, Validator, and Reconciliation Agent │ and receive either a DONE recommendation or a route back to │
│ │ implementation changes │ │ the artifact that no longer matches the code. │
├───┼──────────────────────────┼─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 8 │ Preserve existing │ phase command → cycle command adapters → Dispatcher, │ Run the old phase commands and receive replacement │
│ │ factory contracts during │ Catalog, and installed Factory copy │ diagnostics while compatibility checks confirm that │
│ │ the routing cutover │ │ existing agent and skill names remain available. │
├───┼──────────────────────────┼─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 9 │ Capture and analyze │ Session Bindings → Usage Capture → Usage Record │ Capture records with and without a binding, then group them │
│ │ usage by workstream and │ Contract → Usage Analysis Runtime │ by workstream and cycle while reporting unassigned records │
│ │ cycle │ │ as unavailable. │
└───┴──────────────────────────┴─────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘

## Claude Code Opus 4.6

### before re-applying the write gate

Step 1 — EPIC slicing approach

┌─────┬──────────────────────────────┬────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ # │ EPIC outcome (what a person │ Boundaries crossed │ Demo sentence │
│ │ can do after) │ │ │
├─────┼──────────────────────────────┼────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ │ Validate a five-cycle │ │ Run transition-lint against delivery.yaml and see it accept │
│ 1 │ delivery model against │ Cycle Engine, Delivery Model, Cycle │ five cycles with DONE and all declared routes, or reject a │
│ │ versioned schemas │ Schemas, Validator (transition-lint) │ model with a missing node or an executable command in a │
│ │ │ │ validator field. │
├─────┼──────────────────────────────┼────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ │ Create, continue, and switch │ │ Select menu option B, create a workstream named │
│ 2 │ workstreams with safe │ State Adapter, Cycle State Files, │ "my-feature" at cycle IDEA, then from a second session │
│ │ concurrent access │ Session Bindings, Session Menu │ attempt to mutate the same workstream and see a │
│ │ │ │ stale_workstream_state conflict without data loss. │
├─────┼──────────────────────────────┼────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ │ Ask the engine what cycle to │ Cycle Engine (readiness, │ At CONCEPT with valid canonical artifacts, request a │
│ 3 │ enter next and see │ recommendations), Validator (artifact │ recommendation and see "recommend ROADMAP" with │
│ │ evidence-backed │ validators), Delivery Model │ per-artifact evidence; remove scope-map.md, ask again, and │
│ │ recommendations │ │ see "no recommendation" with the missing-artifact warning. │
├─────┼──────────────────────────────┼────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ │ Navigate cycles through │ Cycle Engine (delegation, decisions), │ Run cycle select to advance to REALIZE; create a delegation │
│ 4 │ human selection, delegation │ State Adapter, CLI │ grant through REALIZE, see automatic continuation while │
│ │ grants, and retry limits │ (.agent-factory/factory/scripts/cycle) │ evidence passes; hit the delegated retry limit and see the │
│ │ │ │ engine pause for human direction. │
├─────┼──────────────────────────────┼────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ │ │ Scripts (phase stub, cycle, │ Run phase advance and see exit 2 naming cycle select; run │
│ 5 │ Use existing commands with │ transition-lint), Skills (run-step), │ run-step on a cycle-state workstream and see it resolve the │
│ │ cycle state after migration │ Catalog (INDEX.yaml), Agent │ next agent from cycle state; run index-lint and confirm │
│ │ │ Definitions │ every agent and skill name preserved. │
├─────┼──────────────────────────────┼────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ │ │ Usage Capture, Usage Record Contract, │ Bind a session to workstream "my-feature" at CONCEPT, │
│ 6 │ Query usage records grouped │ Usage Analysis Runtime, Cycle Engine │ generate usage records, query by workstream dimension, and │
│ │ by workstream and cycle │ (workstream context) │ see grouped results; query null-workstream records and see │
│ │ │ │ attribution reported as unavailable. │
├─────┼──────────────────────────────┼────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ │ Define domain entities in │ Entity Model (LinkML), Pydantic │ Write entity-model.yaml with a value-object class, run │
│ 7 │ LinkML and validate │ (generated), Persistence │ linkml-lint, generate a Pydantic model, submit an invalid │
│ │ generated models │ (integration), Validator │ payload and see the validation error, then round-trip a │
│ │ │ │ valid object through persistence without field loss. │
├─────┼──────────────────────────────┼────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ │ Link a research brief to a │ Research Brief Schema, Brownfield │ Create a research brief from CONCEPT with origin_cycle and │
│ 8 │ delivery cycle and bootstrap │ Playbook, Cycle Engine (brownfield │ return_cycle fields; run a brownfield bootstrap assessment │
│ │ a brownfield concept │ assessment), Entity Model │ with a missing entity-model.yaml and see the specific │
│ │ baseline │ │ missing-evidence report. │
└─────┴──────────────────────────────┴────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘

### after re-application of the write gate

┌─────┬─────────────────────────────────────┬───────────────────────────┬───────────────────────────────────────────────────────────────────┐
│ # │ EPIC outcome (what a person can do │ Boundaries crossed │ Demo sentence │
│ │ after) │ │ │
├─────┼─────────────────────────────────────┼───────────────────────────┼───────────────────────────────────────────────────────────────────┤
│ │ Validate a five-cycle delivery │ Cycle Engine, Delivery │ Run transition-lint against delivery.yaml. It accepts five cycles │
│ 1 │ model against versioned schemas │ Model, Cycle Schemas, │ with DONE and all declared routes, or rejects a model with a │
│ │ │ Validator │ missing node. │
├─────┼─────────────────────────────────────┼───────────────────────────┼───────────────────────────────────────────────────────────────────┤
│ │ Create, continue, and switch │ State Adapter, Cycle │ Select menu option B and create a workstream. From a second │
│ 2 │ workstreams without data loss under │ State Files, Session │ session, write to the same workstream and see a conflict that │
│ │ concurrent writes │ Bindings │ prevents data loss. │
├─────┼─────────────────────────────────────┼───────────────────────────┼───────────────────────────────────────────────────────────────────┤
│ │ Evaluate artifact readiness and │ Cycle Engine, Delivery │ At CONCEPT with valid canonical artifacts, request a │
│ 3 │ recommend the next cycle │ Model, Validator │ recommendation. See "recommend ROADMAP" with evidence, or │
│ │ │ │ warnings when an artifact is missing. │
├─────┼─────────────────────────────────────┼───────────────────────────┼───────────────────────────────────────────────────────────────────┤
│ │ Select and advance through cycles │ Cycle Engine, State │ Run cycle select to advance to REALIZE. Create a delegation │
│ 4 │ using delegation grants and retry │ Adapter, Cycle State │ grant, see automatic continuation. Hit the retry limit and see │
│ │ limits │ Files │ the engine pause. │
├─────┼─────────────────────────────────────┼───────────────────────────┼───────────────────────────────────────────────────────────────────┤
│ │ Use existing commands with cycle │ Validator, Catalog, State │ Run phase advance and see exit 2 naming cycle select. Run │
│ 5 │ state after the playbook-to-cycle │ Adapter │ run-step on a workstream and see it resolve the next agent from │
│ │ cutover │ │ cycle state. │
├─────┼─────────────────────────────────────┼───────────────────────────┼───────────────────────────────────────────────────────────────────┤
│ │ Query usage records grouped by │ Usage Capture, Usage │ Bind a session to a workstream, generate usage records, and query │
│ 6 │ workstream and cycle │ Record Contract, Usage │ by workstream. Records without a workstream report attribution │
│ │ │ Analysis Runtime │ as unavailable. │
├─────┼─────────────────────────────────────┼───────────────────────────┼───────────────────────────────────────────────────────────────────┤
│ │ Define domain entities in LinkML │ Validator, project │ Write entity-model.yaml and run linkml-lint. Submit an invalid │
│ 7 │ and validate generated Pydantic │ persistence layer │ payload to the generated Pydantic model and see the validation │
│ │ models │ │ error. Store and retrieve a valid object without field loss. │
├─────┼─────────────────────────────────────┼───────────────────────────┼───────────────────────────────────────────────────────────────────┤
│ │ Create a research brief linked to a │ │ Create a research brief from CONCEPT with origin_cycle and │
│ 8 │ delivery cycle │ Validator, Cycle Engine │ return_cycle fields. Schema validation accepts the linked brief │
│ │ │ │ and rejects one with an invalid return_cycle. │
├─────┼─────────────────────────────────────┼───────────────────────────┼───────────────────────────────────────────────────────────────────┤
│ │ Bootstrap a brownfield concept │ │ Run a brownfield assessment with entity-model.yaml missing. See │
│ 9 │ baseline with three canonical │ Validator, Cycle Engine │ the missing-evidence report recommending CONCEPT completion. │
│ │ artifacts │ │ │
└─────┴─────────────────────────────────────┴───────────────────────────┴───────────────────────────────────────────────────────────────────┘

## Codex GPT-5.6-Sol

### initial result

# EPIC outcome Boundaries crossed Demo

━━━━━ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
E1 Start independent workstreams without Operator → Session Menu → State Adapter → Start two workstreams and see a stale
losing concurrent changes Cycle State Files → Session Bindings update pause without corrupting either.
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
E2 Continue a workstream and select a cycle Operator → State Adapter → Cycle Engine → See supported routes, select one, and
from repository evidence Delivery Model → Validator update workstream state with warnings.
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
E3 Delegate cycle execution within retry Operator → Cycle Engine → Dispatcher → Delegate through REALIZE, pause on
limits Cycle State Files ambiguity, and stop at the retry limit.
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
E4 Execute and resume the correct agent for a run-step → Cycle Engine → Catalog → Resume an interrupted cycle using
cycle Dispatcher → Agent workstream state and repository evidence.
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
E5 Switch workstreams with accurate usage Operator → Session Menu → Usage Capture → Switch from W1 to W2 and query usage by
attribution Usage Records → Analysis workstream and cycle.
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
E6 Return delivery-linked research evidence Cycle State → Research Brief → Research Complete linked research and return its
to its requesting cycle Playbooks → Validator → Cycle Engine validated report to CONCEPT.
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
E7 Define and validate canonical domain Modeler → LinkML → Validator → Pydantic Generate models, reject invalid JSON, and
entities with LinkML Models → Persistence Adapter round-trip a valid value object.
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
E8 Bootstrap a brownfield repository into the Operator → Brownfield Playbook → Concept Produce the canonical artifacts and report
canonical concept model Model → Validator → Cycle Engine missing evidence without blocking other
cycles.
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
E9 Complete the compatibility cutover from Maintainer → Phase Stub → transition-lint Show phase replacement guidance and
phases to cycles → Cycle State → Catalog preserve characterized legacy contracts.

### after re-applying the write gate

# EPIC outcome Boundaries crossed Demo

━━━━━ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
E1 Start a Workstream (independently tracked Human Operator → Session Menu → Cycle The operator starts two named Workstreams.
delivery objective) in its first Cycle State Files → Session Bindings Each file records IDEA, revision 1, attempt
(delivery stage) 1, and a Session Binding.
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
E2 Continue and redirect a Workstream from Human Operator → Session Menu → State The operator reviews possible next Cycles,
repository evidence without losing Adapter → Cycle Engine → Delivery Model → selects one, and sees a stale update pause
concurrent changes Validator → Cycle State Files without changing state.
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
E3 Execute and resume the eligible Agent for run-step → Cycle Engine → Catalog → After an interruption, the operator runs
a Cycle Dispatcher → command-line Agent run-step. The eligible Agent resumes from
Workstream state and current repository
evidence.
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
E4 Delegate Cycle execution within retry Human Operator → State Adapter → Cycle The operator delegates through REALIZE. One
limits Engine → Dispatcher → Cycle State Files supported Cycle advances, ambiguity pauses,
and a retry after five attempts returns
control.
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
E5 Switch Workstreams with accurate usage Human Operator → Session Menu → Usage The operator switches from W1 to W2, closes
attribution Capture → Usage Record Contract → Raw W1’s usage interval, and queries records by
Usage Spool → Usage Analysis Runtime Workstream, Cycle, or both.
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
E6 Return delivery-linked research evidence Cycle State Files → Research Brief → A user opens research from CONCEPT. The
to its requesting Cycle research-survey and research-topic → validated report returns to CONCEPT without
E7 Create a canonical entity source with Entity Modeler → LinkML Artifact → The modeler generates projections, rejects
LinkML (machine-readable entity-model Validator → Cycle Engine Readiness invalid data, and retrieves valid versioned
language) Evaluator → unresolved persistence data unchanged after storage.
boundary
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
E8 Bootstrap the Canonical Concept Model for Brownfield Operator → brownfield- The operator receives architecture, scope-
a brownfield repository onboarding → Validator → Cycle Engine map, and LinkML artifacts. Missing evidence
Readiness Evaluator → canonical concept remains visible without removing routing
artifacts authority.
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
E9 Retire phase routing while keeping named Maintainer → phase diagnostic stub → The maintainer receives replacement
Factory contracts transition-lint → Delivery Model → Cycle guidance, validates Cycle state, and checks
State Files → Catalog retained command and catalog contracts
against the acceptance commit.

## Copilot Claude Opus 5

### initial result

┌────┬────────────────────────────┬───────────────────────────────────────────────┬────────────────────────────────────────────────────────────────────┐
│ # │ EPIC outcome — what a │ Boundaries crossed │ Demo sentence │
│ │ person can do after │ │ │
├────┼────────────────────────────┼───────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ 1 │ Traverse one workstream │ Session menu (human entry point) → State │ Start a workstream on an accepted proposal, see the route from │
│ │ from a topic to a chosen │ Adapter → Cycle Engine → Delivery Model and │ IDEA to CONCEPT recommended with its evidence, select it, and read │
│ │ next cycle │ workstream state files │ CONCEPT at attempt 1 in the state file. │
├────┼────────────────────────────┼───────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ 2 │ Resume and manage several │ Session menu → session bindings │ Reopen a workstream from the list in a fresh session, see its │
│ │ workstreams across │ (session-to-workstream records) → State │ cycle and recommendations, then decline a suggested switch and │
│ │ sessions │ Adapter and run-step → Dispatcher │ confirm it is not offered a second time. │
├────┼────────────────────────────┼───────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ 3 │ Keep concurrent sessions │ Session A and session B (two actor │ Race two sessions on one workstream: the first writes revision 6, │
│ │ from overwriting newer │ touchpoints) → State Adapter → workstream │ the second receives stale_workstream_state and writes nothing. │
│ │ workstream state │ state files and lock files │ │
├────┼────────────────────────────┼───────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ 4 │ Retry a cycle under │ State Adapter (cycle retry) → Cycle Engine │ Retry REALIZE to its declared limit as a delegated caller and see │
│ │ delegated and human │ (retry evaluation) → Delivery Model limits │ paused; retry once more as a human and see allowed_with_warning at │
│ │ authority │ and workstream state files │ attempt 6. │
├────┼────────────────────────────┼───────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ 5 │ Delegate a bounded route │ Cycle Engine (delegation evaluation) → State │ Grant the route [CONCEPT, REFINE, REALIZE], watch each transition │
│ │ and let it run unattended │ Adapter → run-step → Dispatcher and CLI agent │ show its evidence, and see execution pause when the grant is │
│ │ │ sessions │ exhausted. │
├────┼────────────────────────────┼───────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ 6 │ See complete artifact │ Cycle Engine (readiness evaluation) → │ Assess a repository where the scope map passes but the entity │
│ │ evidence behind every │ Validator commands → repository artifacts and │ model is missing, and see per-artifact checks, warnings, and which │
│ │ recommendation │ commit history │ routes lose support. │
├────┼────────────────────────────┼───────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ 7 │ Define domain entities │ LinkML source file → validation and │ Validate entity-model.yaml, regenerate its Markdown and diagram │
│ │ once and generate every │ generation tooling → generated Pydantic │ projections, and watch a generated model reject an invalid payload │
│ │ other representation │ models and derived diagram projections │ before it reaches storage. │
├────┼────────────────────────────┼───────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ 8 │ Bootstrap an inherited │ Brownfield onboarding procedure → the three │ Run the bootstrap on an existing codebase and receive the │
│ │ repository into a reviewed │ canonical concept artifacts → Cycle Engine │ architecture model, scope map, and entity model plus an assessment │
│ │ concept baseline │ assessment │ naming any missing evidence. │
├────┼────────────────────────────┼───────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ 9 │ Send a delivery question │ Research brief schema → research playbooks → │ Open a linked brief from CONCEPT, validate its report, and resume │
│ │ to research and bring the │ Cycle Engine and State Adapter │ at CONCEPT with the report reference available. │
│ │ answer back │ │ │
├────┼────────────────────────────┼───────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ 10 │ Move the whole factory off │ phase and transition-lint commands → agent │ Run phase advance and get exit 2 naming cycle select, then confirm │
│ │ phase routing without │ definitions and the generated catalog → │ every agent and skill name from the acceptance commit still │
│ │ losing any command │ installed factory copy │ resolves in the catalog. │
├────┼────────────────────────────┼───────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ 11 │ Attribute token usage to a │ Session bindings → Usage Capture → usage │ Capture records with and without a binding, then group usage by │
│ │ workstream and a cycle │ record contract → Usage Analysis Runtime │ workstream and by cycle while unbound records report as │
│ │ │ │ unavailable. │
└────┴────────────────────────────┴───────────────────────────────────────────────┴────────────────────────────────────────────────────────────────────┘

Gate results

1. Two boundaries and a concrete demo — pass. Every row crosses at least two boundaries and names a showable result.

2. Distinct layers or actor touchpoints — pass. EPIC 3 is the borderline case: it earns its second boundary through two concurrent sessions as distinct actor touchpoints, not through adapter-plus-storage.

3. Usable without the next EPIC — pass. EPIC 1 is deliberately the thin end-to-end tracer: menu, state file, model load, recommendation, and selection. EPIC 6 then widens evidence coverage from one artifact to the full table. Neither waits on the other to become usable.

4. No layer grouping — pass. An earlier cut placed "assess evidence" first as its own EPIC. That failed check 3, because recommendations need a workstream to assess. EPIC 1 now carries a working slice of both.

5. Serial chain — pass, with parallelism. EPICs 1, 7, and 11 start together. EPICs 2, 3, 4, 6, and 9 then run in parallel behind EPIC 1. EPIC 5 follows 4; EPIC 8 follows 7 and 6; EPIC 10 follows 1 and 2.

______________________________________________________________________

## Assessment

Prompt given to all four models: "Assume the planning agent role and do an epic slicing for the cycle-based orchestration." Each model read the same specification (`docs/spec/cycle-based-orchestration.feature`, 23 Rules across 10 actors) and the same skill instructions (`create-backlog-epics/SKILL.md`). Each produced an initial result, then was asked to re-apply the writing quality gates. Copilot Opus 5 produced one version with a self-assessment instead of a second pass.

### Assessment criteria

1. **Five hard gates** from `create-backlog-epics/SKILL.md` — two boundaries, distinct layers, usable alone, no layer grouping, not fully serial.
2. **Spec coverage** — which of the 23 .feature Rules has a home in the slicing?
3. **Vertical slice completeness** — does the EPIC trace from where the user touches the system, through the logic that decides, to where the result lands?
4. **Writing quality gates** — Junior Clarity, Senior Acceptance, International Readability, No Pretense.
5. **Planability** — could a team start story-level decomposition from this table?

### Spec Rules for reference

The .feature file declares 23 Rules. Every EPIC slicing must give each Rule a home.

| #   | Rule                                                          | Actor                  |
| --- | ------------------------------------------------------------- | ---------------------- |
| 1   | Human operator starts a new workstream                        | Human operator         |
| 2   | Human operator continues an existing workstream               | Human operator         |
| 3   | Human operator switches workstreams mid-session               | Human operator         |
| 4   | Engine loads and validates the delivery model                 | Cycle engine           |
| 5   | Engine evaluates artifact readiness for route recommendations | Cycle engine           |
| 6   | Engine recommends routes based on artifact evidence           | Cycle engine           |
| 7   | Human operator selects the next cycle                         | Human operator         |
| 8   | Human operator delegates a route sequence                     | Human operator         |
| 9   | Human operator delegates through a destination                | Human operator         |
| 10  | Engine enforces delegated retry limits                        | Cycle engine           |
| 11  | Adapter transitions workstream state atomically               | State adapter          |
| 12  | Adapter handles concurrent workstream access                  | State adapter          |
| 13  | Reconciliation runs when a cycle changes code or artifacts    | Transition recommender |
| 14  | Usage records carry workstream and cycle context              | Usage system           |
| 15  | Usage analyst queries by workstream and cycle dimensions      | Usage analyst          |
| 16  | Brownfield operator bootstraps the canonical concept model    | Brownfield operator    |
| 17  | Delivery cycle creates a linked research brief                | Research user          |
| 18  | Agent definitions carry cycle eligibility                     | Agent maintainer       |
| 19  | run-step executes cycle steps instead of playbook steps       | run-step skill         |
| 20  | phase command exits as a diagnostic stub                      | phase command          |
| 21  | transition-lint validates cycle models and state files        | transition-lint        |
| 22  | Kept contracts preserve acceptance-commit behavior            | Compatibility verifier |
| 23  | LinkML entity model serves as canonical domain source         | Entity modeler         |

### What counts as a vertical slice

Each EPIC must trace a path from where the user touches the system (command, menu, skill invocation), through what decides or transforms (engine, validator, evaluator), to where the result lands (state file, index, report, screen output). An EPIC whose path stays inside one layer — engine-only, persistence-only — is a horizontal, not a vertical.

### What counts as a "boundary"

The four models interpret "boundaries crossed" differently. This interpretation drives the slicing shape.

| Model    | Boundary means                            | Notation                         | Vertical tendency |
| -------- | ----------------------------------------- | -------------------------------- | ----------------- |
| Luna 5.6 | Data-flow hop between processing stages   | Arrow chains (A → B → C)         | Medium            |
| Opus 4.6 | Component that participates               | Comma-separated lists            | Low               |
| Sol 4.6  | Hop in the call chain from actor to state | Arrow chains starting with actor | High              |
| Opus 5   | Architectural layer with role label       | Arrows with parenthetical roles  | High              |

Models that start their boundary column with the actor (Sol, Opus 5) produce verticals. Models that start with an engine component (Luna, Opus 4.6) produce horizontals. The notation choice is upstream of the slicing quality.

### 1. Copilot 5.6 Luna

**Initial (8 EPICs)**

Gate results:

- Gate 1 (two boundaries + demo): pass.
- Gate 2 (distinct layers): pass.
- Gate 3 (usable alone): **fail.** EPIC 5 bundles brownfield bootstrap, research brief linkage, and entity model — three independently usable capabilities in one row.
- Gate 4 (no layer grouping): pass.
- Gate 5 (not fully serial): unclear — no dependency information given.

Vertical slice check:

| EPIC | Entry point           | Decision logic                        | Result lands                              | Vertical?                       |
| ---- | --------------------- | ------------------------------------- | ----------------------------------------- | ------------------------------- |
| 1    | none                  | Engine + Model + Validator            | none                                      | no — engine-only horizontal     |
| 2    | Session menu          | State Adapter                         | Cycle State Files + Session Bindings      | yes                             |
| 3    | none (State Adapter)  | Cycle Engine                          | Cycle State Files + locks                 | no — no interaction layer       |
| 4    | run-step              | Delegation + Retry Evaluators         | CLI agent sessions                        | partial                         |
| 5    | brownfield-onboarding | Research brief + Cycle Engine         | scope-map, entity-model, architecture.dsl | forced — three verticals in one |
| 6    | planning-agent        | implementation-agent + Validator      | backlog artifacts + reconciliation        | yes but too wide — three phases |
| 7    | phase commands        | cycle adapters + Dispatcher + Catalog | installed Factory copy                    | yes                             |
| 8    | Session Bindings      | Usage Capture + Usage Record Contract | Usage Analysis Runtime                    | yes                             |

Spec coverage: all 23 Rules have a plausible home, but entity model (Rule 23) is implicit in EPIC 5, not explicitly named.

**After write gate (9 EPICs):** splits brownfield from research (5 → 5+6). Does not fix EPICs 1 and 3 (engine-only horizontals) or EPIC 7 (overbundled: planning + implementation + reconciliation). Entity model still implicit.

**Verdict: C+.** Three genuine verticals out of eight. Two engine-only horizontals survive both passes. Covers all Rules but distributes them poorly.

### 2. Claude Code Opus 4.6

**Initial (8 EPICs)**

Gate results:

- Gate 1: pass.
- Gate 2: borderline on EPIC 1. Delivery Model and Cycle Schemas are inputs to the same validation step — same-stage components. transition-lint saves it as a second layer.
- Gate 3: **fail.** EPIC 8 bundles brownfield + research. Independently usable.
- Gate 4: pass.
- Gate 5: pass.

Vertical slice check:

| EPIC | Entry point                                | Decision logic                                  | Result lands                         | Vertical?                        |
| ---- | ------------------------------------------ | ----------------------------------------------- | ------------------------------------ | -------------------------------- |
| 1    | none                                       | Engine + Model + Schemas + Validator            | delivery.yaml (read only)            | no — engine-only horizontal      |
| 2    | Session Menu                               | State Adapter                                   | Cycle State Files + Session Bindings | yes                              |
| 3    | none                                       | Engine (readiness, recommendations) + Validator | none (read only)                     | no — engine-only horizontal      |
| 4    | CLI (.agent-factory/factory/scripts/cycle) | Cycle Engine + State Adapter                    | Cycle State Files                    | yes — but bundles four use cases |
| 5    | Scripts (phase, cycle, transition-lint)    | Catalog + Agent Definitions                     | INDEX.yaml                           | yes                              |
| 6    | Session binding                            | Usage Capture + Usage Record Contract           | Usage Analysis Runtime               | yes                              |
| 7    | Entity Model authoring                     | Pydantic generation + Validator                 | Persistence integration              | yes                              |
| 8    | Research Brief + Brownfield Playbook       | Cycle Engine (assessment)                       | Entity Model + architecture.dsl      | forced — two verticals in one    |

Spec coverage: Rules 13 (reconciliation) and 18 (agent cycle eligibility) have no explicit home.

**After write gate (9 EPICs):** splits research from brownfield (8 → 8+9). Boundaries regress to shorter, less specific lists — "Validator, Cycle Engine" appears on three rows, making EPICs architecturally indistinguishable.

**Verdict: B−.** Four genuine verticals. Best entity model coverage (own EPIC). EPIC 4 bundles four Rules (select, delegate explicit, delegate destination, retry) — hard to parallelize stories within it. Two engine-only horizontals persist.

### 3. Codex GPT-5.6-Sol

**Initial (9 EPICs)**

Gate results:

- Gate 1: pass.
- Gate 2: pass.
- Gate 3: pass. Each EPIC is independently demonstrable.
- Gate 4: pass.
- Gate 5: pass. Multiple parallel tracks.

Vertical slice check:

| EPIC | Entry point                    | Decision logic                            | Result lands                         | Vertical? |
| ---- | ------------------------------ | ----------------------------------------- | ------------------------------------ | --------- |
| E1   | Operator → Session Menu        | State Adapter                             | Cycle State Files + Session Bindings | yes       |
| E2   | Operator → State Adapter       | Cycle Engine → Delivery Model → Validator | Workstream state update              | yes       |
| E3   | Operator → Cycle Engine        | Dispatcher                                | Cycle State Files                    | yes       |
| E4   | run-step → Cycle Engine        | Catalog → Dispatcher                      | Agent session                        | yes       |
| E5   | Operator → Session Menu        | Usage Capture → Usage Records             | Analysis output                      | yes       |
| E6   | Cycle State                    | Research Brief → Playbooks → Validator    | Cycle Engine state update            | yes       |
| E7   | Modeler → LinkML               | Validator → Pydantic Models               | Persistence Adapter                  | yes       |
| E8   | Operator → Brownfield Playbook | Concept Model → Validator                 | Cycle Engine readiness               | yes       |
| E9   | Maintainer → Phase Stub        | transition-lint → Cycle State             | Catalog                              | yes       |

All nine EPICs trace from actor through engine to persistence. This is the only attempt where every row is a full vertical slice.

Spec coverage: Rule 4 (delivery model load/validation) and Rule 13 (reconciliation) have no explicit home. Model validation is implied in E2's path but not named as a deliverable.

**After write gate (9 EPICs):** adds inline glosses. **Formatting defect** — E6 and E7 run together without a separator, E6's demo sentence is truncated. The table is physically broken. Without that defect, this would be the strongest after-gate result.

**Verdict: B (initial), C (after gate).** Best structural result — all verticals, all gates pass on first try. The formatting defect in the after-gate version makes it undeliverable. E2 is a thick vertical (four Rules) that could be hard to story-slice.

### 4. Copilot Claude Opus 5

**Initial only (11 EPICs, no after-gate version)**

Gate results:

- Gate 1: pass. Most specific demos of all attempts.
- Gate 2: borderline on EPIC 3. Self-assessment justifies "two concurrent sessions" as distinct actor touchpoints. Defensible.
- Gate 3: pass. Self-assessment tests each EPIC with explicit reasoning.
- Gate 4: pass. Self-assessment notes an earlier cut failed this gate and was revised.
- Gate 5: pass with explicit parallelism stated.

Vertical slice check:

| EPIC | Entry point           | Decision logic                                      | Result lands                             | Vertical?                      |
| ---- | --------------------- | --------------------------------------------------- | ---------------------------------------- | ------------------------------ |
| 1    | Session menu          | State Adapter → Cycle Engine → Delivery Model       | Workstream state files                   | yes                            |
| 2    | Session menu          | State Adapter + run-step → Dispatcher               | Session bindings                         | yes                            |
| 3    | Session A + B         | State Adapter                                       | Workstream state files + lock files      | thin — no engine logic         |
| 4    | CLI invocation        | Cycle Engine (retry)                                | Delivery Model limits + workstream state | yes                            |
| 5    | Human grant           | Cycle Engine (delegation) → run-step → Dispatcher   | Agent sessions                           | yes                            |
| 6    | Assessment invocation | Cycle Engine (readiness) → Validators               | Repository artifacts (read only)         | partial — no persistence write |
| 7    | Entity authoring      | Validation + generation                             | Pydantic models + projections            | yes                            |
| 8    | Brownfield onboarding | Three canonical artifacts → Cycle Engine assessment | Artifact files on disk                   | yes                            |
| 9    | Brief creation        | Research brief schema → playbooks                   | Cycle Engine + State Adapter             | yes                            |
| 10   | phase command         | transition-lint → agent definitions → catalog       | Installed factory copy                   | yes                            |
| 11   | Session bindings      | Usage Capture → usage record contract               | Usage Analysis Runtime                   | yes                            |

Nine full verticals, one thin (EPIC 3: concurrency — no engine logic, just adapter + persistence), one partial (EPIC 6: evidence assessment — reads artifacts but writes no state).

Spec coverage: Rules 4 (delivery model validation), 13 (reconciliation), and 21 (transition-lint) have no explicit home.

The self-assessment is unique. No other attempt tests itself against the gates and provides reasoning. This is the single most valuable addition — it forces justification for each EPIC's independence.

EPIC 3 (concurrency as standalone): the demo "race two sessions" is a test scenario, not a use case. Nobody's goal is to race sessions. Concurrent safety is a quality attribute of the workstream EPIC, not a capability a user performs. The spec separates Rules 11 and 12, which gives some support, but the EPIC still lacks a user-facing entry point with engine logic.

**Verdict: B+.** Most thorough, most honest, best demo sentences. Nine full verticals with two partial. The concurrency EPIC is the one wrong call. Three Rules without explicit homes.

### Summary

| Rank | Model    | Score | EPICs | Full verticals | Horizontals | Gates (initial) | Missing Rules |
| ---- | -------- | ----- | ----- | -------------- | ----------- | --------------- | ------------- |
| 1    | Sol 4.6  | B / C | 9     | 9              | 0           | 5/5             | 4, 13         |
| 2    | Opus 5   | B+    | 11    | 9              | 0           | 5/5             | 4, 13, 21     |
| 3    | Opus 4.6 | B−    | 8→9   | 4              | 2           | 4/5             | 13, 18        |
| 4    | Luna 5.6 | C+    | 8→9   | 3              | 2           | 4/5             | 23 (implicit) |

Sol ranks first on vertical slice structure — every row is a full vertical. Opus 5 ranks first on thoroughness, demos, and self-assessment. Luna and Opus 4.6 share the same structural flaw: engine-only EPICs (model validation, readiness evaluation) that have no user entry point.

### Cross-cutting findings

1. **No attempt explicitly covers reconciliation** (Rule 13). All four omit it or imply it within assessment EPICs.
2. **Delivery model validation** (Rule 4) gets absorbed into larger EPICs in every attempt. The spec gives it five scenarios and its own Rule.
3. **The write gate helps with the obvious bundling problem** (brownfield + research) but does not catch engine-only horizontals or boundary regression.
4. **Self-assessment against the gates** (Opus 5 only) is the single most valuable practice. It forces the model to justify each EPIC's independence. The other three present tables without reasoning.
5. **The boundary interpretation drives the slicing.** Models that start their boundary column with the user produce verticals. Models that start with an engine component produce horizontals. The column header "Boundaries crossed" does not prescribe direction or layering, which leaves the interpretation open.

### Instruction change

The skill instruction has been revised based on this analysis. Key changes:

- Column renamed: "Boundaries crossed" → "Path through the system."
- Path column instruction added: name three things in order — (1) what the user touches, (2) what decides or transforms, (3) where the result lands.
- Vertical slice defined up front: "starts where the user touches the system, passes through the logic that decides, and ends where the result is stored or shown."
- Gate 1 reworded: "traces a path from user entry through decision logic to a stored or shown result."
- Gate 2 reworded: explicitly calls out engine-only and persistence-only as horizontals.
- Gate 3 reworded: "Can someone do the demo with only this EPIC built?"
- Lore terms removed: no "actor," no "actor touchpoints," no "architectural layers," no "system boundaries."
