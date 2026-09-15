# Epic Slicing on Cycle-Based Orchestration - Improving the skill instruction

## slicing attempt from GPT 5.6 SOL

› ❯ Perform the epic-Slicing on cycle-based-orchestration. Ignore the pre-existing documents epics-cycle-based-orchestration.md and ST-0252 and
ST-0253. This is a comparison test run on step 1 of the backlog creation.

• I’m using the local create-backlog-epics skill because this is explicitly a step-1 EPIC-slicing comparison run. I’ll treat epics-cycle-based-
orchestration.md, ST-0252, and ST-0253 as excluded evidence and won’t modify them.

• Explored
└ Read SKILL.md

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• The skill makes this a read-only planning pass: survey current behavior, compare it with the canonical specification, and present only an EPIC
slice table for approval. No backlog file will be written in this step.

• Explored
└ Read SKILL.md
Read writing-quality-gates.md
Read agent-context.md
List spec
List backlog
Read scope-map.md
Read cycle-based-orchestration.feature
Read cycle-based-orchestration-gaps.md
Read cycle-based-orchestration-qa-strategy.md
Search cycle|orchestrat|goal|continu|budget|terminal|turn in supplementary_specs
Search cycle-based-orchestration|Human operator starts|Human operator continues|switches workstreams|delivery model|route
recommendations|cycle-
based|workstream in scope-map.md
Read cycle-based-orchestration.feature
Read cycle-based-orchestration-gaps.md
Read cycle-based-orchestration-qa-strategy.md
Read interface-contracts.md
Search cycle-based orchestration|workstream|delivery cycle|delegation grant|cycle model|delivery.yaml in entity-model.md

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• The specification defines 23 actor goals, but EPICs must follow usable journeys, not one EPIC per rule. I’m now checking which parts already
exist so the proposed EPICs contain only the remaining delta.

• Ran printf '__SOURCE_MATCHES__\\n'; rg -n -i --hidden 'cycle[-\_ ]based|workstream_id|workstream_origin|delegation_grant|delivery.yaml|cycle
│ select|cycle retry|origin_cycle|return_cycle|cycle eligibility|cycles:' packages tests orchestrator 2>/dev/null; printf
│ '\\n\_\_CANDIDATE_FILES\_\_\\n'; rg --files --hidden packages tests orchestrator | rg '(phase|transition|usage|research|session-menu|run-step|
│ … +1 lines
└ __SOURCE_MATCHES__
tests/factory/test_backlog_lint.py:343:class TestDetectCycles:
… +303 lines (ctrl + t to view transcript)
tests/fixtures/concern-lint/missing_read/docs/agent-context.md
tests/fixtures/concern-lint/valid/docs/agent-context.md

• Ran rg -n -i --hidden 'cycle|orchestrat|session menu|usage|research|transition-lint|run-step|phase command|entity model|LinkML|factory scripts|
│ engine' docs/arc42/architecture.dsl docs/arc42/*.md docs/adr/*.md | sed -n '1,360p'; printf '\\n\_\_PACKAGE_LAYOUT\_\_\\n'; find packages/factory
│ -maxdepth 3 -type d | sort; printf '\\n\_\_TEST_LAYOUT\_\_\\n'; find tests/factory packages/usage/tests -maxdepth 2 -type f | sort | sed -n
│ … +1 lines
└ docs/arc42/08_crosscutting_concepts.md:7:**Principle**: Creation is agentic; validation is deterministic. Tests, cycle-model gates, and
dangerous-command checks are triggered mechanically rather than left to agent judgment. Agent guardrails prevent bypass in the managed
… +553 lines (ctrl + t to view transcript)
tests/factory/test_usage_capture.py
tests/factory/test_verify_base.py

• Explored
└ Read architecture.dsl, 05_building_block_view.md, 08_crosscutting_concepts.md, 07_deployment_view.md, 0017-cycle-based-orchestration-
supersedes-
linear-playbook-fsm.md, 0018-concept-internal-sequence-is-agent-owned.md

• Ran sed -n '1,70p' docs/proposals/cycle-based-orchestration.md; printf '\\n\_\_EXISTENCE\_\_\\n'; for p in packages/factory/engine packages/factory/
│ scripts/cycle packages/factory/engine/models/delivery.yaml packages/factory/engine/schemas/cycle-model-v1.schema.json packages/factory/
│ engine/schemas/cycle-state-v1.schema.json docs/spec/entity-model.yaml docs/spec/entity-model.md docs/assets/images/entity-model.svg; do if
│ … +3 lines
└ ---
schema_version: 2
… +773 lines (ctrl + t to view transcript)
is selected directly, adopt its role in the current session. Spawn it only when its definition requires a separate session or when the current
session has performed work from which that agent must remain independent.

• Explored
└ Search ^epic:|^status:|^title:|^# in backlog
Search epic 0|foundation|status: pending|status: in_progress
Search ^epic:.\*(epic[ -]?0|foundation) in backlog
Read ST-0018.md
Read ST-0025.md
Read ST-0035.md
Read ST-0036.md
Search Epic 0|cross-cutting|foundation in backlog
Search workstream|cycle|properties|required in v1.schema.json
Search origin_cycle|origin_ref|return_cycle|decision_needed|required|properties in research-brief.schema.json
Search ^(phase|phase_name|phase-name|cycles|cycle): in agents
Search architecture.dsl|scope-map|entity-model|three|anchor|bootstrap|concept in brownfield-onboarding.md
Read v1.schema.json, usage_by_dimension.py, research-brief.schema.json, brownfield-onboarding.md

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• The codebase still uses linear playbook orchestration. No cycle engine, cycle command, workstream state, session binding, or LinkML entity model
exists.

Current reusable foundations include usage capture, usage analysis, research workflows, Factory validators, dispatch, and brownfield onboarding.
No active “Epic 0 — Project Setup” stories exist, so no Epic 0 dependency applies.

I excluded epics-cycle-based-orchestration.md, ST-0252.md, and ST-0253.md from the analysis.

# What the user can do after Path through the system Demo sentence

━━━━━ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1 Create a canonical concept model during brownfield-onboarding → LinkML validation The operator receives three valid canonical
brownfield bootstrap and generated Pydantic validation → objects, generates both projections, and
entity-model.yaml, derived projections, round-trips a typed value object.
persisted value object, and readiness
result
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
2 Start, reopen, and switch workstreams Session Menu B/C → Workstream Resolver and The operator creates Alpha, reopens it,
safely State Adapter → Cycle State Files, Session then switches to Beta without overwriting
Bindings, and shown recommendations newer workstream state.
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
3 Select and retry cycles using artifact cycle select or cycle retry → Cycle Model The operator reviews evidence, chooses any
evidence Loader, Readiness Evaluator, Route cycle, and sees delegated retries pause at
Recommender, and Retry Evaluator → updated the configured limit.
Cycle State File and shown result
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
4 Delegate a route or destination with run-step with a delegation grant (human The operator delegates through REALIZE;
bounded autonomy permission for transitions) → Delegation execution advances on unambiguous evidence
Evaluator and Dispatch Eligibility → and pauses on ambiguity, failure, conflict,
dispatched agent, updated Cycle State or exhaustion.
File, or shown pause
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
5 Use cycle-native commands while preserving Git hooks, phase, transition-lint, and The operator receives replacement guidance
Factory contracts index-lint → Validator, phase stub, and from phase, validates cycle state, and
Dispatcher → diagnostics, exit codes, and finds every existing agent and skill name
Catalog unchanged.
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
6 Capture and query usage by workstream and CLI agent invocation and usage-query → The analyst groups parent and child usage
cycle Usage Capture reads Session Bindings; by workstream and cycle while unattributed
Usage Analysis aggregates records → Raw records remain explicitly unavailable.
Usage Spool and query results
───── ──────────────────────────────────────────── ──────────────────────────────────────────── ─────────────────────────────────────────────
7 Send a delivery evidence gap through Linked research-brief creation → research The user opens research from CONCEPT and
research and return validators, Research Orchestrator, and returns the validated report to CONCEPT
Cycle Engine → validated brief, report without changing standalone research.
reference, and resumed workstream

The dependency shape is not fully serial:

- EPIC 1 supplies the canonical domain contract.
- EPIC 2 establishes workstream identity and safe state.
- EPIC 3 adds evidence-based navigation.
- EPICs 4–7 branch from that operational core.
- Atomicity and concurrency remain invariants inside EPIC 2, not horizontal infrastructure EPICs.
- Reconciliation remains part of EPIC 3 because it informs route recommendations.

No files were written. Please confirm or adjust this slicing before phase 2 writes the EPIC artifact.

─ Worked for 4m 08s ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

─ Conversation recap ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Objective: perform epic slicing for cycle-based orchestration while ignoring the existing epic and ST-0252/ST-0253 documents. The codebase
currently has only linear orchestration; next, define and slice the missing cycle engine, command, workstream state, session binding, and LinkML
model.

## Result analysis and reflection

› Did you even once stop and consider applying the write-quality gate? Where is the "seen from the user using the factory viewshed direction" in
your slicing principle? where is the "each epic must reach from the user into the backend"?

• You are right. I checked sentence mechanics, but I missed the substantive gate. Several rows begin with maintainers or internal commands, so
they are actor-goal groupings, not user-to-result vertical slices. I’ll recut them from the human operator’s visible journeys.

• Explored
└ Search viewshed|view shed|user.\*backend|front.\*back|vertical slice|user touches|seen from the user in factory

■ Conversation interrupted - tell the model what to do differently. Something went wrong? Hit `/feedback` to report the issue.

› This is in the skill instructions, isn't it?

• Yes. Explicitly.

The skill says every EPIC must:

- start where the user touches the system;
- pass through the logic that decides or transforms;
- end where the result is stored or shown;
- be demonstrable through the shipped interface.

I read those instructions and still violated them. Rows such as “create a canonical concept model” and “preserve Factory contracts” started from
internal concerns, not the user’s viewshed. I treated backend capabilities as EPICs instead of folding them into user-facing journeys.

That was my error, not an instruction gap.

› what must be done to improve the "irresistability" of the instructions?

• The rule already exists, but it competes with a code-first workflow and an actor-goal matrix containing internal actors. Stronger wording alone
will not fix that. The instruction must make viewshed-first slicing the only permitted procedure.

Required changes:

1. Insert a mandatory “user viewshed map” before EPIC grouping.

   For every human goal, record:

   - named human;
   - shipped entry point;
   - action;
   - visible outcome;
   - persisted or displayed result.

2. Prohibit internal rules from originating EPICs.

   State explicitly:

   > Engine, adapter, validator, schema, migration, compatibility, and persistence rules MUST NOT seed an EPIC. Assign each to the human journey
   > it enables. If no journey owns it, report a specification gap.

3. Reverse the grouping procedure.

   Current pressure is effectively:

   > inventory components → find gaps → group gaps

   Replace it with:

   > identify human journeys → form demonstrable outcomes → trace each journey through the architecture → absorb required internal gaps

4. Require every row to use this exact path grammar:

   > Human uses <shipped interface> → <decision or transformation component> decides/transforms → <visible or persisted result> changes

   A component name alone cannot occupy the first position.

5. Add hard rejection questions before presenting each row:

   - Does a human initiate the demo through a shipped interface?
   - Can the human describe the new capability without naming implementation components?
   - Does the path enter decision logic?
   - Does the path end in visible or persisted behavior?
   - Can the demo run without source inspection or test output?
   - Did this EPIC originate from a human goal rather than an internal rule?

   Any “no” rejects the row.

6. Require an internal-rule allocation check.

   Each backend rule must appear under exactly one user-facing EPIC as supporting scope. This prevents “model validation,” “LinkML,” or
   “compatibility” from escaping into horizontal EPICs.

7. Add contrasting examples directly beside the generation step.

   Bad:

   > Validate the delivery model
   > transition-lint → Cycle Model Loader → diagnostics

   Good:

   > Choose the next delivery cycle with evidence
   > Human runs cycle select → Readiness Evaluator recommends routes → the chosen cycle and evidence appear in workstream state and output

8. Make the viewshed audit visible in the answer.

   Add columns such as:

   | Human | Shipped entry point | New observable capability | Backend rules absorbed |

   A visible proof obligation is harder to satisfy cosmetically than an instruction kept in hidden reasoning.

The central instruction should become:

> Slice from the human’s viewshed inward. Never begin with components, internal actors, schemas, migrations, or specification Rules. Begin with
> a human using a shipped Factory interface and observing a useful result. Then include every backend change required to make that journey work.

That would have rejected several rows in my previous answer before they reached you.

─ Conversation recap ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Objective: make the instructions irresistibly enforce viewshed-first slicing. We learned stronger wording is insufficient because code-first
workflow and internal actors compete; next, make viewshed-first slicing the sole mandatory procedure and align conflicting sections.

## Opus 4.6 Appraisal and remediation approach

Good data. I've read the skill, the writing-quality-gates rulebook, the four-model comparison review, and the existing epic file. Here's my appraisal.

______________________________________________________________________

The model's self-diagnosis is accurate. It read the instructions, processed the gates, and still sliced from internal capabilities inward. The self-correction conversation correctly identifies why.

The skill already says the right thing. After your earlier revision (documented at the bottom of the review), the skill says "starts where the user touches the system," prescribes a three-part path starting with the user, and has five hard gates that reject horizontals. The model that produced this transcript was operating under those revised instructions and still failed. That's the finding worth addressing.

Why the instructions don't stick:

The procedure in Step 1 says:

▎ "Compare the spec target against the codebase inventory. The gap — what the spec requires that the code does not yet do — is the work to decompose. Group related gaps into EPICs."

This is gap-first grouping. By the time the model reaches the gate in Step 1.5a, the mental model is already component-shaped. The gates then have to reject and recut — which is exactly the failure mode in the transcript. The model ran the gates late, after the grouping was done, and produced cosmetic fixes rather than structural recuts.

Appraising the 8 proposals:

┌─────┬─────────────────────┬───────────────┬──────────────────────────────────────────────────────────────────────────────────────────────┐
│ # │ Proposal │ Verdict │ Reason │
├─────┼─────────────────────┼───────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1 │ Mandatory viewshed │ Adopt │ Highest leverage. Forces human-journey enumeration before any grouping. Moves the viewshed │
│ │ map before grouping │ │ check upstream of the failure point. │
├─────┼─────────────────────┼───────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ │ Prohibit internal │ Adopt, │ The prohibition is genuinely absent. One sentence in the gate section suffices — no need for │
│ 2 │ rules from │ compressed │ a standalone rule block. │
│ │ originating EPICs │ │ │
├─────┼─────────────────────┼───────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ │ Reverse the │ Adopt — this │ Step 1 currently runs gap→group→gate. Reversing to journey→outcome→trace→absorb changes │
│ 3 │ grouping procedure │ is the core │ where the model commits. The gates become verification, not recutting. │
│ │ │ fix │ │
├─────┼─────────────────────┼───────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ │ │ │ The three-part path instruction already exists and is clear. Enforcing sentence grammar adds │
│ 4 │ Exact path grammar │ Skip │ compliance cost without structural benefit. Models that start from the user already produce │
│ │ │ │ the right shape. │
├─────┼─────────────────────┼───────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ │ Hard rejection │ Adopt 2, skip │ "Can the human describe the new capability without naming implementation components?" and │
│ 5 │ questions (6 │ 4 │ "Did this EPIC originate from a human goal rather than an internal rule?" are new and │
│ │ checks) │ │ useful. The other four restate existing gates. │
├─────┼─────────────────────┼───────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ │ Internal-rule │ │ Good completeness check. Prevents orphan backend rules from spawning horizontal EPICs. One │
│ 6 │ allocation check │ Adopt │ sentence: "Every backend rule must appear under exactly one user-facing EPIC as supporting │
│ │ │ │ scope." │
├─────┼─────────────────────┼───────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ 7 │ Contrasting │ Adopt │ The skill has zero examples. A bad/good pair next to the gate section is the cheapest │
│ │ examples │ │ high-impact change. The model's own examples are usable. │
├─────┼─────────────────────┼───────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ │ │ │ Adding "Human / Shipped entry point / New observable capability / Backend rules absorbed" as │
│ 8 │ Visible audit │ Consider │ columns makes the proof obligation visible — but the table already has three columns and │
│ │ columns │ carefully │ adding four more creates a wall. A better approach: require the viewshed map as a separate │
│ │ │ │ artifact (proposal #1), then keep the existing three-column table for the EPIC slice. │
└─────┴─────────────────────┴───────────────┴──────────────────────────────────────────────────────────────────────────────────────────────┘

What I'd actually change in the skill:

1. Split Step 1 into two steps. Current Step 1 (gap inventory) becomes Step 1a. New Step 1b: "Enumerate human journeys" — for each named human actor in the spec, list what they can do after that they cannot do now, naming the shipped entry point and the observable result. No component names. This is the viewshed map from proposal #1, but as a named procedural step rather than a new artifact.
2. Rewrite the grouping instruction. Replace "Group related gaps into EPICs" with: "Group each human journey into an EPIC. Then trace the journey through the architecture and absorb every backend change it requires. A backend rule (engine, adapter, validator, schema, migration) that no journey owns is a specification gap — report it, don't create an EPIC for it."
3. Add two gate checks to the existing five. Gate 6: "A person can describe this EPIC's result without naming implementation components." Gate 7: "This EPIC originated from a human goal, not from an internal rule, validator, or schema."
4. Add one bad/good example pair right after the gate list. Use the model's own examples — they're apt.
5. Add one line to the quality-gate callout: "Every backend rule in the specification must appear as supporting scope under exactly one EPIC. An unallocated rule is either a missing journey or a specification gap."

These five changes move the viewshed check upstream of the grouping step, make it procedural rather than corrective, and add the minimum instruction mass to prevent the failure mode without bloating the skill.

______________________________________________________________________

## Epic slicing with Codex GPT 5.6 Sol

found a specification gap and stopped the slicing process

› Perform the epic-Slicing on cycle-based-orchestration. Ignore the pre-existing documents epics-cycle-based-orchestration.md and ST-0252 and
ST-0253. This is a comparison test run on step 1 of the backlog creation.

• Ran sed -n '1,240p' factory/rulebooks/rules.md && sed -n '241,520p' factory/rulebooks/rules.md && sed -n '1,260p' .codex/INDEX.yaml && if \[ -f
│ config/project-context.json \]; then sed -n '1,220p' config/project-context.json; fi
└ # Rules

```
… +525 lines (ctrl + t to view transcript)
  }
}
```

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• I’m using the local create-backlog-epics skill because this is specifically phase 1 of backlog creation. I’ll treat the named existing epic/
story artifacts as out of scope and stop at the approval-ready slicing proposal.

• Explored
└ Read session-menu.md, SKILL.md, planning-agent.toml
Read SKILL.md
Read writing-quality-gates.md
Read agent-context.md
List docs
Search cycle-based-orchestration|scope-map.md$|testing.yaml$|architecture.dsl$|CONTEXT.md$|step.manifest|manifest
Search epics-cycle-based-orchestration.md|ST-0252.md|ST-0253.md
Search step manifest|step-manifest|manifest schema|active step manifest|max_input_tokens in factory
Read feature-addition.md, dispatch_lib.py, step-guard

• Ran git branch --show-current && git status --short && find .current-work -name current-step.yml -o -name playbook-state.yml 2>/dev/null | sort
│ | head -80
└ dev
M backlog/epics-cycle-based-orchestration.md
… +2 lines (ctrl + t to view transcript)
?? docs/reviews/2026-09-15_epic_slicing_examples.md
?? docs/reviews/2026-09-16_epic_slicing_analysis_and_improvement.md

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• The worktree contains unrelated user changes, including the comparison artifacts you told me to ignore. I will not read or modify those files.
I’m activating a bounded step manifest for this phase, then I’ll inspect only the canonical specification, architecture, and implementation
evidence.

• Added .current-work/cycle-based-orchestration/epic-slicing-comparison/current-step.yml (+21 -0)
1 +schema_version: 1
2 +step: create-backlog-epics
3 +playbook: create-backlog
4 +phase: epic-slicing-approach
5 +inputs:
6 + - docs/agent-context.md
7 + - docs/CONTEXT.md
8 + - docs/spec/scope-map.md
9 + - docs/spec/cycle-based-orchestration.feature
10 + - docs/spec/cycle-based-orchestration-gaps.md
11 + - docs/spec/cycle-based-orchestration-qa-strategy.md
12 + - docs/testing.yaml
13 + - docs/adr/**/\*.md
14 + - docs/arc42/**/*.md
15 + - packages/factory/\*\*/*.md
16 + - packages/factory/**/\*.py
17 + - packages/orchestrator/**/*.py
18 + - orchestrator/tests/\*\*/*.py
19 + - tests/\*\*/\*.py
20 +outputs: []
21 +max_input_tokens: 40000

• Explored
└ Read cycle-based-orchestration.feature, scope-map.md, CONTEXT.md, cycle-based-orchestration-gaps.md, cycle-based-orchestration-qa-strategy.md,
testing.yaml, 0017-cycle-based-orchestration-supersedes-linear-playbook-fsm.md, 12_glossary.md, CONTEXT-MAP.md, architecture.dsl
List factory
Search (cycle|workstream|delivery|phase|transition|run-step|usage|research|entity|linkml|index|session-menu)

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• The specification defines 23 rules, but several are internal support rules rather than user capabilities. The implementation scan shows no cycle
engine, workstream model, or cycle command yet; existing phase, transition-lint, run-step, usage capture, research, and usage-analysis
interfaces are migration starting points. I’m now mapping each rule to one user journey and checking whether those starting points make each
capability partial or absent.

• Explored
└ Read session-menu.md, phase, transition-lint, SKILL.md, usage-capture, research-brief.schema.json

• Ran rg --hidden -n "workstream_id|workstream_origin|origin_cycle|return_cycle|decision_needed|cycle_eligibility|cycle-eligibility|entity-model|
│ LinkML|usage_by_dimension|dimension" packages/factory packages/orchestrator tests packages/usage 2>/dev/null | head -360
└ packages/usage/tests/test_cli_unit.py:32: "usage_by_dimension",
packages/usage/tests/test_cli_unit.py:35: "--dimensions", "cli,model",
… +100 lines (ctrl + t to view transcript)
packages/factory/skills/model-structurizr-slice/SKILL.md:63:Use independent tag dimensions:
packages/factory/skills/model-structurizr-slice/SKILL.md:110:separate tag dimensions. Inspect the legend. See

• Edited .current-work/cycle-based-orchestration/epic-slicing-comparison/current-step.yml (+3 -1)
17 - packages/orchestrator/**/\*.py
18 - - orchestrator/tests/**/*.py
18 + - packages/usage/\*\*/*.md
19 + - packages/usage/**/\*.py
20 + - packages/usage/**/*.sql
21 - tests/\*\*/*.py

• Explored
└ Search class UsageRecord|def to_dict|SUPPORTED|DIMENSION|\_DIMENSIONS|usage_by_dimension|properties|required in usage-capture
Read usage-capture
Read usage_by_dimension.py
Read v1.schema.json
Read architecture.dsl
Search ^phase:|^phase_name:|^phase-name:|^cycles:|cycle in agents
Search architecture.dsl|scope-map|entity-model|three canonical|anchor|Output in brownfield-onboarding.md
Read brownfield-onboarding.md
Search ^(Rule:|Scenario:) in cycle-based-orchestration.feature

• Edited .current-work/cycle-based-orchestration/epic-slicing-comparison/current-step.yml (+1 -0)
20 - packages/usage/**/*.sql
21 + - backlog/ST-*.md
22 - tests/**/\*.py

• Ran rg --hidden -l '^epic:\\s\*["'"']?Epic 0|^epic:\\s\*["'"']?EPIC 0|^epic:\\s\*["'"']?Foundation' backlog/ST-*.md | rg -v 'ST-0252.md|ST-0253.md'
│ | sort | tail -30
└ /bin/bash: line 1: ^epic:s*[']?Foundation: command not found
rg: 0: IO error for operation on 0: No such file or directory (os error 2)

• Ran rg --hidden -n '^epic:' backlog/ST-\*.md | rg -i 'epic 0|foundation' | rg -v 'ST-0252.md|ST-0253.md' | sort | tail -40
└ backlog/ST-0018.md:3:epic: Research Foundation
backlog/ST-0025.md:3:epic: Research Foundation
backlog/ST-0035.md:3:epic: Usage Capture Foundation
backlog/ST-0036.md:3:epic: Usage Capture Foundation

• Ran rg --hidden --files tests packages | rg '(character|compat|installed|index_lint|verify_base|premerge|phase|transition_lint)' | sort && rg
│ --hidden -n "acceptance commit|characterization|verify-base|premerge-check|phase advance|phase retry" tests packages/factory/tests packages/
│ factory 2>/dev/null | head -260
└ packages/factory/scripts/phase
packages/factory/scripts/premerge-check
… +119 lines (ctrl + t to view transcript)
tests/factory/test_verify_base.py:10:vb = load_script("verify-base")
tests/factory/test_verify_base.py:68: marker = git_repo / ".current-work" / "verify-base-ok"

• Explored
└ Search grant|delegat|cycle select|cycle retry|entry point|command in 0017-cycle-based-orchestration-supersedes-linear-playbook-fsm.md

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• Epic slicing is blocked by one specification gap: neither the feature nor architecture defines the shipped interface for creating, replacing, or
revoking delegation grants. The architecture only exposes cycle select, cycle retry, phase, and run-step.

Which shipped interface should manage delegation grants?

─ Worked for 5m 01s ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

› How is it described in the proposal?

• I’ll check the proposal’s delegation decisions and command/interface sections, without consulting the excluded comparison artifacts.

• Edited .current-work/cycle-based-orchestration/epic-slicing-comparison/current-step.yml (+1 -0)
12 - docs/testing.yaml
13 + - docs/proposals/cycle-based-orchestration.md
14 - docs/adr/\*\*/\*.md

• Explored
└ Search delegat|grant|route \[|through |cycle select|cycle retry|human-authored in cycle-based-orchestration.md
Read cycle-based-orchestration.md

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• The proposal defines the grant’s data and behavior, but not how the human changes it:

- Grants live in the workstream state as either delegation.route or delegation.through.
- Only the human may create, replace, or revoke a grant.
- The engine may execute a grant but cannot broaden it.
- cycle select only specifies cycle and work arguments; no delegation argument or separate grant command is defined.

See docs/proposals/cycle-based-orchestration.md:696 and the command replacement table at line 349 (docs/proposals/cycle-based-
orchestration.md:349).

So the proposal confirms the gap: it defines semantics and YAML shape, but no shipped interface for grant management. Directly editing the state
file would also conflict with its revision-and-digest protections.

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

› what is the interface for the other cycle operations?

• I’ll map each defined cycle operation to its stated human-facing interface so the missing grant operation is clear by comparison.

• Explored
└ Search ^### Session menu|option B|option C|starts? a new workstream|continue|reopen|switch|factory/scripts/cycle|run-step|transition-lint|
phase.\*stub in cycle-based-orchestration.md

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• The proposal uses these interfaces:

Operation Interface
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Start a workstream Session menu option B
───────────────────────────────── ───────────────────────────────────────────────────────────────────────────────────────
Continue/reopen a workstream Session menu option C
───────────────────────────────── ───────────────────────────────────────────────────────────────────────────────────────
Switch workstreams Factory detects a topic boundary and asks for human confirmation; no command is named
───────────────────────────────── ───────────────────────────────────────────────────────────────────────────────────────
Select a cycle or change work factory/scripts/cycle select --state STATE TARGET [--work REF ...]
───────────────────────────────── ───────────────────────────────────────────────────────────────────────────────────────
Retry the current cycle factory/scripts/cycle retry --state STATE
───────────────────────────────── ───────────────────────────────────────────────────────────────────────────────────────
Resume/execute cycle work run-step skill
───────────────────────────────── ───────────────────────────────────────────────────────────────────────────────────────
Validate cycle models and state transition-lint, normally through pre-commit
───────────────────────────────── ───────────────────────────────────────────────────────────────────────────────────────
Use an obsolete phase command factory/scripts/phase, which exits 2 and names the replacement
───────────────────────────────── ───────────────────────────────────────────────────────────────────────────────────────
View recommendations Automatically after reopening a workstream and at cycle exit
───────────────────────────────── ───────────────────────────────────────────────────────────────────────────────────────
Manage delegation grants No interface specified

The command definitions are in the compatibility table (docs/proposals/cycle-based-orchestration.md:341). Menu behavior appears under Session
menu (docs/proposals/cycle-based-orchestration.md:516).

The closest established pattern would be extending factory/scripts/cycle, for example with a delegate subcommand. The proposal does not make
that decision.

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

› delegation should be deferred.

• For this comparison run, I’ll exclude explicit-route grants, destination grants, and delegated retry limits. I’ll retain human cycle retry
behavior: increment the attempt, reset it when cycle or work changes, reject invalid state, and keep consumed attempts after failures. The
specification will need that split before Phase 2; I will not edit it during this test run.

• Deleted .current-work/cycle-based-orchestration/epic-slicing-comparison/current-step.yml (+0 -25)
1 -schema_version: 1
2 -step: create-backlog-epics
3 -playbook: create-backlog
4 -phase: epic-slicing-approach
5 -inputs:
6 - - docs/agent-context.md
7 - - docs/CONTEXT.md
8 - - docs/spec/scope-map.md
9 - - docs/spec/cycle-based-orchestration.feature
10 - - docs/spec/cycle-based-orchestration-gaps.md
11 - - docs/spec/cycle-based-orchestration-qa-strategy.md
12 - - docs/testing.yaml
13 - - docs/proposals/cycle-based-orchestration.md
14 - - docs/adr/**/\*.md
15 - - docs/arc42/**/*.md
16 - - packages/factory/\*\*/*.md
17 - - packages/factory/**/\*.py
18 - - packages/orchestrator/**/*.py
19 - - packages/usage/\*\*/*.md
20 - - packages/usage/**/\*.py
21 - - packages/usage/**/*.sql
22 - - backlog/ST-*.md
23 - - tests/\*\*/\*.py
24 -outputs: []
25 -max_input_tokens: 40000

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• Delegation is excluded from this comparison run. Human retry remains in scope. The active specification must later separate human retry from
delegated retry rules.

### Capability survey

ID CAP-01
Person Human operator
Shipped entry point Session menu B
User action Start a named workstream from a topic or proposal
Observable result IDEA becomes current, and the session binds to the new workstream
Status quo Absent
Supporting rules Start workstream; atomic state mutation; concurrent access
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
ID CAP-02
Person Human operator
Shipped entry point Session menu C
User action Reopen a selected workstream
Observable result The current cycle and evidence-based recommendations appear
Status quo Absent
Supporting rules Continue workstream; readiness evaluation; route recommendation
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
ID CAP-03
Person Human operator
Shipped entry point In-session switch confirmation
User action Confirm a switch to another objective
Observable result The target workstream becomes active, and later usage receives its context
Status quo Absent
Supporting rules Switch workstreams; atomic mutation; usage context
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
ID CAP-04
Person Human operator
Shipped entry point cycle select
User action Select any cycle and work list
Observable result State records the selection and shows failed or missing evidence as warnings
Status quo Absent
Supporting rules Cycle selection; readiness; recommendation; reconciliation
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
ID CAP-05
Person Human operator
Shipped entry point cycle retry
User action Retry the current cycle
Observable result Attempt increases, invalid state remains unchanged, and accepted attempts survive later failures
Status quo Absent
Supporting rules Human retry subset of the current retry rule; atomic mutation
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
ID CAP-06
Person Human operator
Shipped entry point run-step skill
User action Resume or continue cycle work
Observable result Repository evidence selects an eligible agent, which starts for the current cycle
Status quo Partial
Supporting rules Cycle-native run-step; readiness; dispatch eligibility
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
ID CAP-07
Person Usage analyst
Shipped entry point usage-query usage_by_dimension
User action Group usage by workstream, cycle, or both
Observable result Results show attributed totals and report unavailable attribution honestly
Status quo Partial
Supporting rules Usage-record context; workstream and cycle dimensions
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
ID CAP-08
Person Brownfield operator
Shipped entry point Brownfield onboarding
User action Bootstrap the canonical concept baseline
Observable result Architecture, scope, and LinkML entity artifacts exist with a readiness recommendation
Status quo Partial
Supporting rules Brownfield bootstrap; canonical LinkML model
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
ID CAP-09
Person Research user
Shipped entry point Research workflow started from a delivery cycle
User action Create a linked research brief
Observable result A validated report returns to the declared delivery cycle
Status quo Partial
Supporting rules Delivery-linked research brief
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
ID CAP-10
Person Agent maintainer
Shipped entry point Agent definitions and index-lint
User action Replace phase ordinals with cycle eligibility
Observable result The catalog retains every accepted agent and skill identity
Status quo Partial
Supporting rules Cycle eligibility; kept-contract verification
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
ID CAP-11
Person Human operator
Shipped entry point Legacy phase command
User action Invoke phase advance or phase retry
Observable result The command exits 2 and names the corresponding cycle command
Status quo Partial
Supporting rules Diagnostic phase stub
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
ID CAP-12
Person Project maintainer
Shipped entry point transition-lint
User action Check the cycle model and workstream state
Observable result Structural errors fail; failed recommendation evidence produces warnings at exit zero
Status quo Partial
Supporting rules Delivery-model validation; cycle-model and state validation

No active rule remains unallocated. The three delegation rules are excluded:

- Delegate an explicit route.
- Delegate through a destination.
- Enforce delegated retry limits.

### Proposed EPIC slicing

# 1

Capabilities CAP-01, CAP-02, CAP-03
Primary backend rules Workstream lifecycle; atomic replacement; revision, digest, and lock conflicts
What the user can do after Start, reopen, and switch between independent workstreams
Path through the system Session menu or switch confirmation → Workstream Resolver and State Adapter → Cycle State Files, Session Bindings,
terminal output, and Raw Usage Spool
Demo sentence Start W1, reopen it through C, confirm a switch to W2, then see W2 bound with recommendations and new usage
attribution.
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

# 2

Capabilities CAP-04, CAP-05, CAP-06
Primary backend rules Readiness evaluation; route cardinality; human selection; reconciliation; manual retry; dispatch eligibility
What the user can do after Choose, retry, and resume cycle work from repository evidence
Path through the system cycle select, cycle retry, or run-step → Cycle Engine evaluators → Cycle State Files, Session Bindings, Trigger,
and terminal output
Demo sentence Select REALIZE despite warnings, retry it, run run-step, then see the increased attempt and a REALIZE-eligible
agent start.
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

# 3

Capabilities CAP-07
Primary backend rules Workstream context capture; null attribution; workstream and cycle grouping
What the user can do after Compare usage across workstreams and delivery cycles
Path through the system usage-query → Input Snapshot, Operational Preflight, Accounting Registry, and Query Model → Result Adapters
Demo sentence Query W1 by cycle and see separate CONCEPT and REALIZE totals while unattributed records remain explicitly
unavailable.
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

# 4

Capabilities CAP-08
Primary backend rules Brownfield baseline assessment; LinkML validation; derived projections; generated-model persistence validation
What the user can do after Create a delivery-ready canonical concept baseline
Path through the system Brownfield onboarding → concept validation and model generation → architecture.dsl, scope map, entity model,
projections, and recommendation output
Demo sentence Run brownfield onboarding and see all three canonical objects plus a recommendation to begin feature delivery.
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

# 5

Capabilities CAP-09
Primary backend rules Delivery-context fields; research validation; return-cycle routing
What the user can do after Send a delivery question through research and return its evidence
Path through the system Delivery research action → schema and policy validation → linked brief, validated report, and resumed workstream
Demo sentence From CONCEPT, create a linked brief and validate its report, then see CONCEPT resume with the report reference.
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

# 6

Capabilities CAP-10
Primary backend rules Cycle eligibility; catalog generation; acceptance-commit compatibility
What the user can do after Maintain cycle-eligible agents without losing public identities
Path through the system Agent definition edit → index-lint and compatibility checks → Catalog and terminal results
Demo sentence Migrate an architecture agent, run the checks, and see cycle eligibility with every accepted agent and skill name
retained.
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

# 7

Capabilities CAP-11
Primary backend rules Retired phase-transition behavior
What the user can do after Identify the replacement for an obsolete phase command
Path through the system phase advance or phase retry → phase diagnostic adapter → exit status and terminal message
Demo sentence Run phase advance and see exit code 2 with cycle select named as its replacement.
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

# 8

Capabilities CAP-12
Primary backend rules Delivery-model schema; reference resolution; trusted validators; recommendation warnings
What the user can do after Detect invalid cycle configuration before it affects work
Path through the system transition-lint → Cycle Model Loader and cycle schemas → terminal findings
Demo sentence Run transition-lint against an invalid model, then see the structural error and a non-zero exit.

Dependency shape:

- EPIC 8 enables EPIC 1.
- EPICs 1 and 6 enable EPIC 2.
- EPIC 1 enables EPIC 3.
- EPICs 1 and 2 enable EPIC 5.
- EPICs 4, 6, 7, and 8 can begin independently.

No backlog or excluded comparison document was written or modified. This is the Phase 1 approval point.
