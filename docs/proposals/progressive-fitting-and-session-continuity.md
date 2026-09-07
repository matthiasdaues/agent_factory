---
schema_version: 2
title: Progressive Fitting and Session Continuity
status: accepted
owner: md@matthiasdaues.de
created: 2026-09-07
updated: 2026-09-07
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: false
  boundaries:
    - factory/agents/virgil.md
    - factory/skills/capture-context/SKILL.md
    - factory/config/session-menu.md
    - factory/skills/newcomer-tour/SKILL.md
    - factory/skills/explain-concept/SKILL.md
    - factory/skills/guided-tour/SKILL.md
    - factory/playbooks/poc-spike.md
    - factory/scripts/init-factory
    - factory/config/AGENTS.md
    - config/project-context.json

governance:
  assurance: elevated
  risk_domains:
    - compatibility
    - reliability

estimate:
  as_of: 2026-09-07
  basis: judgment
  confidence: low
  human_review_hours:
    min: 1.5
    max: 3
  normalized_tokens:
    min: 6000
    max: 15000
  estimated_consumption:
    min: 90000
    max: 225000
    overhead_multiplier: 15
    playbook: feature-addition
---

# Feature Request: Progressive Fitting and Session Continuity

## Summary

Fitting currently front-loads 30–60 minutes of configuration — 12 model
decisions, a 19-question stakeholder interview, test-regime detection, and
hook review — before the user has seen a single agent work. This proposal
restructures fitting into a minimum-viable pass and deferred deepening,
surfaces hidden navigation aids, resolves a persona conflict at the
VIRGIL/playbook transition, and adds session continuity so returning users
resume where they left off instead of re-navigating the menu tree.

## Motivation

The first-round onboarding improvements (newcomer-onboarding-and-incremental-
brownfield, `status: implemented`) addressed the session entrypoint, the
newcomer tour, and brownfield-lite. They did not touch the fitting procedure
itself or the skill seams around it. A critical UX appraisal of the
current onboarding journey reveals six structural problems that compound
into a single effect: the factory asks for commitment before demonstrating
capability.

Specific findings:

1. **Fitting inverts the trust-building sequence.** Step 0 asks the user to
   choose among model IDs per CLI per tier — 12 decisions — before they have
   seen what "economy," "standard," or "strong" means in practice. Step 2
   runs a 19-question stakeholder interview covering licensing, architecture
   governance, and scope boundaries — topics the user may not have decided
   yet. The total fitting time for a brownfield project is 30–60 minutes.

2. **capture-context treats all questions as equally urgent.** The 19
   questions span three YAML files (stack, workflow, governance) with no
   prioritisation. A handful — language, framework, running locally,
   testing, branching — are immediately useful; others (architecture
   governance, scope boundaries) could wait weeks. The `deferred` mechanism
   exists but gives no signal about which questions to defer.

3. **VIRGIL cannot run poc-spike.** The newcomer-tour finishes by offering
   poc-spike. But VIRGIL's boundaries say "MUST NOT write code" and "does
   not run those playbooks itself." poc-spike step 2 says "Build it
   yourself." The persona transition from VIRGIL to playbook executor is
   never made explicit, producing either a refusal or a silent constraint
   drop — both confusing.

4. **explain-concept is invisible.** The skill exists, handles "what is a
   gate?" questions with experience-calibrated answers, and is exactly the
   right tool for a confused newcomer. But it appears in no menu, no tour
   step, and no visible affordance. The user must know to ask the question
   to trigger the skill.

5. **The B menu is a wall of bare playbook names.** `poc-spike`,
   `technical-poc`, `greenfield-development` — a user who just completed
   the newcomer-tour knows five vocabulary words but has no catalog of what
   each playbook does. One-line descriptions are absent.

6. **Partial fitting progress is invisible.** A returning user with an
   incomplete fitting sees "want to walk through the fitting?" with no
   indication of progress (3/5 steps done, ~10 minutes remain). The
   fitting state is tracked but not surfaced.

## Core Principles

- Value before configuration. The user should see the factory do something
  useful before being asked to configure it in depth.
- Questions should be asked when the answers matter, not when the schema has
  a slot for them.
- Navigation aids that already exist must be visible at the points where
  confusion is most likely.
- Fitting state is derived from artifacts, not declared by metadata. The
  observable state of the project — populated agent-context files, a
  configured model matrix, wired hooks — is the source of truth.
  `project-context.json` caches the derived state for performance; it is
  never authoritative over what the filesystem shows.

## Design

### 1. Split capture-context into minimum-viable and full passes

Introduce a `--minimal` flag alongside the existing `--init` and
`--init --scan`. The minimal pass asks only the questions whose answers are
needed before the first playbook run:

**Minimum-viable questions (6):**

| Ask                                      | Field                            |
| ---------------------------------------- | -------------------------------- |
| What language(s) and runtime version(s)? | `stack.yaml#languages`           |
| What backend framework?                  | `stack.yaml#frameworks.backend`  |
| What frontend framework (if any)?        | `stack.yaml#frameworks.frontend` |
| How is the project run locally?          | `workflow.yaml#running`          |
| Testing approach and test runner?        | `workflow.yaml#testing`          |
| Branching model?                         | `workflow.yaml#branching`        |

All other fields are written as `deferred: "full context pass pending"`.
The minimal pass produces valid YAML (context-lint clean) and gives agents
enough to route work.

The full pass (`--init` without `--minimal`) remains unchanged — 19
questions, used when the stakeholder wants to populate everything upfront.

**`--minimal` composes with `--scan`.** For brownfield projects the
invocation is `capture-context --init --scan --minimal`. The scan runs
in full — it discovers languages, frameworks, test runners, linters, CI,
and infrastructure signals exactly as today. The difference is which
fields the interview covers: only the 6 minimal fields are presented for
confirmation or correction. The scan's auto-detection covers 4 of them
(languages, frameworks, testing, linting), so the user typically confirms
those from scan results and answers 2 real questions (running locally,
branching). All other fields are written as
`deferred: "full context pass pending"` — the scan evidence is not
discarded, it simply waits for the full pass to present it.
`reading-guides.yaml` is assembled from whatever source pointers the
minimal interview confirmed; concerns with only deferred fields are
pruned as today.

For greenfield projects (no existing codebase to scan), the invocation
is `capture-context --init --minimal` — 6 questions, no scan.

VIRGIL's fitting step 2 invokes `--init --scan --minimal` for brownfield
and `--init --minimal` for greenfield by default. VIRGIL offers the full
pass as an explicit option: "I have enough to work with. Want to fill in
the rest now, or come back to it later?"

### 2. Defer model-matrix entries for unused CLIs

Step 0 currently walks all 4 CLIs × 3 tiers. Change: VIRGIL asks "Which
CLI(s) do you use?" first. Only the selected CLI's three tiers are
configured. Other CLIs are left with their existing defaults or
`CONFIGURE-ME` placeholders. The fitting key
`model_matrix_configured` is set to `true` once the user's active CLI is
configured — the others can be configured later via `update-context` or
direct file edit.

This reduces the typical step 0 from 12 decisions to 3.

### 3. Explicit VIRGIL/playbook persona transition

Add an exception clause to VIRGIL's boundaries and to the newcomer-tour:

> VIRGIL's constraints — including "MUST NOT write code" and "does not run
> those playbooks itself" — apply while VIRGIL is the active persona. When
> the user selects a playbook from the session menu or accepts a playbook
> offer (e.g., poc-spike at the end of the newcomer tour), the model drops
> the VIRGIL persona, reads the playbook's markdown file, and follows its
> operational procedure per session-menu.md. VIRGIL's MUST NOTs do not
> carry into the playbook session.

The newcomer-tour's boundary "Do not spawn agents or launch a playbook"
becomes "Do not launch a playbook directly — offer it and let the session
menu handle the transition."

Today session-menu.md already says "read the playbook's markdown file and
follow its operational procedure," but VIRGIL's MUST NOTs have no
exception clause, creating a contradiction when poc-spike follows the
newcomer tour. This change makes the persona boundary explicit.

### 4. Surface explain-concept as a persistent affordance

Add a footer line to the session menu and to the B menu:

> At any point, ask "what is [concept]?" for a plain-language explanation.

This costs nothing — explain-concept already exists and works. The footer
makes it discoverable at the moments confusion is most likely: when the
user faces a menu of unfamiliar terms.

### 5. Add one-line descriptions to B menu entries

Each leaf in the B menu gets a one-sentence description after the playbook
name:

```
1. Create something new
   a — poc-spike: build the smallest thing that proves the idea, then
       throw it away
   b — technical-poc: validate a technical risk with a decision-grade
       prototype
   c — greenfield-development: build a real production system from
       requirements through deployment

2. Onboard an existing project
   → brownfield-onboarding: understand an inherited codebase well
     enough to change it safely
```

Descriptions are derived from each playbook's opening paragraph — the
source of truth stays in the playbook file.

### 6. Surface guided-tour from the session menu

Add a line after option D:

> **?** — Where am I? What can I do next?

This invokes the guided-tour skill, which already handles both "inside an
active playbook" and "outside an active playbook" states. The `?` mnemonic
is conventional for help in CLI environments.

### 7. Derive fitting state from artifacts

`config/project-context.json` is untracked in target projects — it does
not survive a fresh clone or a new `init-factory` run. Some of the
artifacts it describes are git-tracked and do survive:
`docs/agent-context/` and `.pre-commit-config.yaml` are tracked;
`config/model.conf` is gitignored in target projects (model choice is
user-specific). When a collaborator pulls a fitted repo and runs
`init-factory`, the metadata says "unfitted" while the tracked artifacts
say "fitted." The metadata must not contradict the artifacts.

**Derivation rules** (applied by init-factory's scan and by VIRGIL's
session-start check):

| Fitting key               | Derivable? | Derived from                                                                                                                                                                                                                                                        |
| ------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `fingerprint_confirmed`   | Yes        | `config/project-context.json` exists with non-empty `languages` or `frameworks`                                                                                                                                                                                     |
| `agent_context_populated` | Yes        | `docs/agent-context/stack.yaml` exists with at least one non-deferred leaf                                                                                                                                                                                          |
| `model_matrix_configured` | No         | `config/model.conf` is untracked — does not survive clone. Cache-only; defaults to `false` when cache is absent. This is correct: model choice is user-specific, each collaborator configures their own tiers.                                                      |
| `test_regime_detected`    | Yes        | `docs/agent-context/workflow.yaml#testing` is non-null and non-deferred, or `testing.yaml` exists under `docs/agent-context/`                                                                                                                                       |
| `hooks_decided`           | Yes        | `.pre-commit-config.yaml` is tracked. Factory marker block present → `true` (team-wide decision, survives clone). Marker absent → `false`; the collaborator is asked, which is correct — if the original author declined, a new team member may decide differently. |
| `status`                  | Yes        | `"fitted"` when all keys are true; `"unfitted"` when none are; `"fitting"` otherwise                                                                                                                                                                                |

`project-context.json` caches the derived state. When the cache disagrees
with a derivable artifact, the artifact wins — the cache is overwritten
silently. The only non-derivable key is `model_matrix_configured` —
`config/model.conf` is untracked because model choice is user-specific.
A collaborator who pulls a fitted repo and runs init-factory inherits the
team's agent-context, test regime, and hook decisions (all tracked), but
is asked to configure their own model tiers.

### 8. Surface fitting progress on session start

When `fitting.status` is `"fitting"` (partially complete), VIRGIL's
session-start check surfaces a progress summary before offering to
continue. The check reads the fitting keys from `project-context.json`
(re-derived per item 7) and reports:

> "Fitting is 3/5 done (model matrix, fingerprint, and context populated).
> Test regime and hooks remain. Continue the fitting, or skip to the
> menu?"

This requires a change to the session-start flow in `factory/config/AGENTS.md`
(the canonical orientation content consumed by all CLIs). Today the
session-start check handles only `fitting.status == "unfitted"` and offers
the fitting or the menu. The change: handle `"fitting"` as a third state.
When `"fitting"`, present the progress summary with completed and
remaining steps. The step names map directly to the fitting keys:

| Fitting key               | Step name shown to user |
| ------------------------- | ----------------------- |
| `model_matrix_configured` | Model matrix            |
| `fingerprint_confirmed`   | Project fingerprint     |
| `agent_context_populated` | Agent context           |
| `test_regime_detected`    | Test regime             |
| `hooks_decided`           | Pre-commit hooks        |

VIRGIL reads the fitting keys, counts completed vs. remaining, and
presents the summary. No new file or skill — this is a routing change
in the session-start instructions.

## Scope

**In the first release:**

- `capture-context` gains a `--minimal` flag with the 6-question subset.
  VIRGIL's fitting step 2 defaults to `--minimal` for brownfield projects.
- Model-matrix step asks which CLIs are in use; only active CLIs are
  configured.
- Explicit persona-transition rule added to session-menu.md and VIRGIL's
  boundaries section.
- explain-concept footer added to session menu and B menu.
- One-line descriptions added to each B menu leaf.
- guided-tour surfaced from the session menu as option `?`.
- Fitting state derived from artifacts, not solely from metadata.
  init-factory and VIRGIL re-derive fitting keys from observable state
  on every run.
- VIRGIL surfaces fitting progress (completed/remaining steps) when
  fitting is partially complete. AGENTS.md checks for `"fitting"` state.

**Explicitly deferred (do NOT plan stories for these):**

- Automatic detection of "the user seems confused" to proactively offer
  explain-concept. The footer is passive discovery; proactive invocation
  is a later refinement.
- Cross-session memory (user profiles, learning progress tracking).
- Changes to the full capture-context interview (the 19 questions are fine;
  only the default invocation path changes).
- Session continuity beyond fitting progress. The fitting state in
  `project-context.json` already tracks partial fitting across sessions;
  playbook-level breadcrumbs are deferred until proven needed.

## Design Details

### capture-context --minimal interaction model

The `--minimal` flag composes with both `--init` and `--init --scan`:

- **`--init --minimal`** (greenfield): scaffold the three YAML files,
  interview on 6 fields, defer the rest. No scan, no source pointers.
- **`--init --scan --minimal`** (brownfield): run the full discovery scan,
  then interview on 6 fields only. Scan results for the minimal fields are
  proposed as answers — the user confirms or corrects. Scan results for
  non-minimal fields are held but not presented; they wait for the full
  pass. `reading-guides.yaml` is assembled from confirmed source pointers
  only; concerns with only deferred fields are pruned.

In both cases the remaining fields are pre-filled with
`deferred: "full context pass pending"` before the interview begins, so
context-lint sees deferred values (valid) rather than nulls (errors).

When the user later runs `capture-context --init` or `--init --scan`
(without `--minimal`), the skill detects existing deferred fields and
presents only those for completion. For brownfield, held scan results are
proposed alongside the deferred fields. Fields already valued are shown
for confirmation but not
re-asked from scratch.

### Persona-transition scope

The transition rule applies only when a playbook is selected through the
session menu or offered by a skill (newcomer-tour → poc-spike). It does not
apply to skills invoked within VIRGIL's own session (explain-concept,
capture-context, grilling) — those run under VIRGIL's constraints as today.

## Open Questions

None. Resolved during review:

- `--minimal` question set: fixed at 6 questions, not configurable.
  Rationale: covers every playbook's needs; configurability is YAGNI.

## Completion Criteria

- `capture-context --init --scan --minimal` asks at most 6 questions and
  produces context-lint-clean YAML with all other fields deferred.
- A user who finishes the newcomer-tour and accepts poc-spike sees code
  written without a refusal or unexplained constraint drop.
- The explain-concept footer appears in session-menu.md and in the B menu.
- Each B menu leaf has a one-line description derived from its playbook.
- VIRGIL surfaces fitting progress (completed/remaining steps) when
  `project-context.json` shows a partially completed fitting.
- A collaborator who clones a fitted repo and runs init-factory gets
  `agent_context_populated`, `fingerprint_confirmed`, `test_regime_detected`,
  and `hooks_decided` derived from tracked artifacts — not reset to
  `false`. Only `model_matrix_configured` requires fresh configuration.

## Guiding Rule

Ask for commitment after demonstrating capability, not before.

## Review — 2026-09-07

Reviewer: proposal-review-agent
Reviewed commit: cbbf15c7777f1f0407442d3ed60232354429f5b3
Disposition: findings

### Prior findings (first pass)

All 7 findings from the first review pass were verified as addressed in
the current text. No prior findings remain open.

### Findings

| ID      | Severity | Check | Status | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------- | -------- | ----- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| PROP-01 | major    | 03    | open   | Design item 7 contradicts itself on model.conf tracking status. Line 249 lists model.conf among artifacts that are "git-tracked and do survive." The derivation table says model.conf is "untracked — does not survive clone." Ground truth: model.conf IS tracked in the factory repo (`git ls-files` confirms); init-factory gitignores it in target projects (init-factory line 2507). The proposal conflates factory-repo and target-project contexts. A planning agent cannot resolve which behavior to implement for the derivation logic. |
| PROP-02 | minor    | 05    | open   | `factory/scripts/init-factory` is an implementation target for Design item 7 ("applied by init-factory's scan") but is not listed in `impact.boundaries`. A planning agent decomposing item 7 would need to inspect init-factory to understand the change surface.                                                                                                                                                                                                                                                                               |
| PROP-03 | minor    | 03    | open   | Completion criterion 5 requires VIRGIL to surface fitting progress (completed/remaining steps) for partial fittings. Motivation item 6 identifies the problem. No design item specifies the implementation: where in the session-start flow the check occurs, what the progress display looks like, or whether it modifies CLAUDE.md (which handles only `fitting.status == "unfitted"`, not `"fitting"`) or VIRGIL's definition.                                                                                                                |

### Check results

| #   | Check                            | Result     |
| --- | -------------------------------- | ---------- |
| 01  | Completion criteria testable     | pass       |
| 02  | Scope boundary sharp             | pass       |
| 03  | Design decomposable              | fail       |
| 04  | Impact classification consistent | pass       |
| 05  | Boundary references exist        | pass/minor |
| 06  | Open questions genuine           | pass       |
| 07  | Motivation justifies timing      | pass       |
| 08  | Estimate plausible               | pass       |

### Summary

Six of eight checks pass. Check 03 fails on two counts: an internal
contradiction about model.conf's tracking status in Design item 7
(major — blocks derivation logic implementation), and a completion
criterion for fitting-progress surfacing with no corresponding design
item (minor — forces the planning agent to design rather than
decompose). The missing init-factory boundary reference is
housekeeping. All first-pass findings are addressed. Three open
findings remain: address PROP-01 (resolve the model.conf context
ambiguity), PROP-02 (add init-factory to boundaries), and PROP-03
(add a design item for fitting-progress display) before this proposal
is ready to plan from.

## Review — 2026-09-07 (pass 3)

Reviewer: proposal-review-agent
Reviewed commit: cbbf15c7777f1f0407442d3ed60232354429f5b3
Disposition: clean

### Prior findings (passes 1 and 2)

All 10 findings from the first two review passes (7 from pass 1, 3 from
pass 2) have been verified as resolved in the current text:

- PROP-01 (major, check 03): model.conf tracking contradiction →
  resolved. Lines 250–277 now distinguish tracked artifacts
  (docs/agent-context/, .pre-commit-config.yaml) from gitignored
  artifacts (config/model.conf) in target projects. The derivation table
  marks model_matrix_configured as non-derivable with explicit rationale.
  Confirmed against init-factory source (line 2792: ignore_model_conf
  adds /config/model.conf to the target's gitignore block).

- PROP-02 (minor, check 05): init-factory missing from boundaries →
  resolved. Both factory/scripts/init-factory and factory/config/AGENTS.md
  appear in impact.boundaries.

- PROP-03 (minor, check 03): no design item for fitting-progress display →
  resolved. Design item 8 specifies the session-start routing change in
  AGENTS.md, provides an example progress display, and includes the
  step-name mapping table.

### Findings

No new findings.

### Check results

| #   | Check                            | Result |
| --- | -------------------------------- | ------ |
| 01  | Completion criteria testable     | pass   |
| 02  | Scope boundary sharp             | pass   |
| 03  | Design decomposable              | pass   |
| 04  | Impact classification consistent | pass   |
| 05  | Boundary references exist        | pass   |
| 06  | Open questions genuine           | pass   |
| 07  | Motivation justifies timing      | pass   |
| 08  | Estimate plausible               | pass   |

### Observation

Design items 2 (defer model-matrix for unused CLIs) and 6 (surface
guided-tour as ?) have no explicit completion criteria. Both are specific
enough in the design that a planning agent can derive acceptance criteria
without ambiguity. Not a blocking finding.

### Summary

All eight checks pass. The ten findings from the first two passes are
fully resolved. The proposal is internally consistent, the design is
decomposable into stories, the scope boundary is sharp, and the estimate
is plausible. This proposal is ready for acceptance and planning.
