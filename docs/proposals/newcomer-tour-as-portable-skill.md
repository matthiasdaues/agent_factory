---
schema_version: 2
title: "VIRGIL: Portable Newcomer Tour and Unified Session Agent"
status: accepted
owner: md@matthiasdaues.de
created: 2026-08-30
updated: 2026-08-30
accepted: 2026-08-30
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: false
  boundaries:
    - factory/agents/chat-agent.md
    - factory/agents/kit-manager.md
    - factory/skills/guided-tour/SKILL.md
    - factory/skills/draft-proposal/SKILL.md
    - factory/skills/detect-test-regime/SKILL.md
    - factory/docs/factory-guide.md
    - factory/config/AGENTS.md
    - factory/scripts/init-factory
    - factory/INDEX.yaml
    - factory/README.md
    - docs/arc42/beginner-intro.md

governance:
  assurance: standard
  risk_domains:
    - compatibility

estimate:
  as_of: 2026-08-30
  basis: judgment
  confidence: high
  human_review_hours:
    min: 1
    max: 2
  normalized_tokens:
    min: 3000
    max: 8000
  estimated_consumption:
    min: 30000
    max: 80000
    overhead_multiplier: 10
    playbook: documentation-update
---

# VIRGIL: Portable Newcomer Tour and Unified Session Agent

## Summary

The newcomer walkthrough (session entrypoint option A) is broken in every
downstream project. The accepted proposal "Newcomer Onboarding and
Incremental Brownfield" hardcoded the tour as "read
`docs/arc42/beginner-intro.md`" — a file that lives in the agent-factory
repository's own `docs/` directory, which is project-specific content.
`init-factory` copies `factory/` into the target project but never copies
`docs/arc42/`. A new user who installs the factory into their own project,
opens their CLI, and picks option A gets a missing-file error.

This proposal fixes the packaging gap and, in doing so, unifies the three
adopt-pattern Phase 0 agents — chat-agent, kit-manager, and the newcomer
tour — into a single session agent: **VIRGIL** (Versatile Interactive
Resource: Guide, Instructor, Liaison). VIRGIL is a thin agent that
reaches for skills on demand. From the user's seat, there is one agent
they talk to. It shows them around, sets up their workspace, explains the
tools, talks things through, and routes to the right playbook when the
idea finds its shape.

## Motivation

**The immediate bug.** Option A points at a file that does not exist in
downstream projects. The newcomer path — the front door to adoption — is
broken.

**The deeper problem.** Factory knowledge has no owner. The kit-manager
owns project knowledge (charter, requirements, project-specific
decisions). But no agent owns the complementary domain: what the factory
itself is, how its agents, skills, playbooks, and gates work, and how a
newcomer should approach them.

**The structural problem.** Three Phase 0 agents — chat-agent,
kit-manager, and the (missing) newcomer guide — all use the adopt
pattern, all run in the current session, and all face the same user.
From the user's perspective they are the same interaction: "I'm talking
to my assistant." The distinction between them is framework-internal
and forces a routing decision the user should never have to make.

A junior developer in their first week should be able to say "help" and
get the right response whether they need a tour, a charter, or just a
conversation. One agent, many skills, loaded on demand.

## Design

### 1. VIRGIL: one agent, many skills

Rename and expand `chat-agent` to `virgil`. Phase 0 utility agent,
adopt pattern (runs in the current session). The agent definition is
thin — a role statement, a knowledge-base pointer, and a list of skills
it can reach for:

**Name:** VIRGIL — Versatile Interactive Resource: Guide, Instructor,
Liaison.

**Role:** The single human-facing session agent. Starts formless — just
talking — and reaches for the right skill when the conversation needs
structure. The counterpart pairing with specialist agents:

| Agent       | Domain              | Mode                           |
| ----------- | ------------------- | ------------------------------ |
| **VIRGIL**  | Session companion   | Adopt pattern, current session |
| Specialists | Phase-specific work | Spawned as subagents           |

**Skills available to VIRGIL:**

| Skill             | Loaded when                                | Source             |
| ----------------- | ------------------------------------------ | ------------------ |
| `newcomer-tour`   | "show me around", option A                 | new                |
| `explain-concept` | "what is a gate?", "how do playbooks work" | new                |
| `capture-charter` | "set up the project"                       | existing (kit-mgr) |
| `update-charter`  | "change the tech stack"                    | existing (kit-mgr) |
| `grilling`        | vague answers need sharpening              | existing (kit-mgr) |
| `validate`        | check the charter                          | existing (kit-mgr) |
| `draft-proposal`  | idea crystallizes into a proposal          | existing (chat)    |
| `comic-relief`    | moment of levity warranted                 | new                |
| open conversation | option D, or anything unstructured         | existing (chat)    |

**Boundaries:**

- Reads `factory/docs/factory-guide.md` and `factory/INDEX.yaml` for
  factory knowledge.
- Reads charter files for project knowledge (via charter skills).
- Does not advance playbook state (that is the guided-tour skill's
  reorientation role, and the orchestrator's job).
- Does not spawn subagents — it runs in the current session so the
  user can answer questions directly.
- Routes to playbooks and specialist agents when the conversation
  finds its shape: a feature proposal goes to `feature-addition`, a
  spike goes to `poc-spike`, a research question goes to
  `research-topic`.

**Triggers:** "show me around", "set up the project", "capture the
charter", "explain the factory", "what is a \<factory-concept>",
"help", "I have an idea", or simply starting a conversation.

### 2. Merge beginner content into factory-guide.md

Add a "Getting Started" section at the top of
`factory/docs/factory-guide.md`, before the existing "Agents" section.
The content is adapted from `docs/arc42/beginner-intro.md`:

**Subsections preserved:**

- Who this is for
- The one idea to hold onto
- The four words you will keep hearing
- Two ways to run it — and why you start by hand (manual mode only)
- Why two agents, not one
- Your very first session
- The bigger picture: five phases
- Which playbook, when
- Three habits that keep you safe
- Where to go next

**Content removed:**

- The "Graduating to automatic mode" section. The orchestrator does
  not ship with the factory and is not part of the newcomer experience.
- Links to `orchestrator/README.md` (does not ship with factory).
- Links to `docs/arc42/concepts.md` (project-specific arc42 content).

**Content adapted:**

- Internal links rewritten to `factory/`-relative paths.
- The guide's existing opening line ("If you are brand new, start with
  the beginner's introduction") replaced with a direct lead-in to the
  new "Getting Started" section.
- A clear seam between beginner and reference material: "Everything
  below is reference material. You don't need it yet."

### 3. New skills: newcomer-tour and explain-concept

**`newcomer-tour`** (`factory/skills/newcomer-tour/SKILL.md`):

> Read the "Getting Started" section of `factory/docs/factory-guide.md`
> and walk the user through it conversationally, one subsection at a
> time, pausing for questions after each subsection. Before starting,
> check for signs of prior work (a completed poc-spike, a charter,
> prior playbook outputs). If found, acknowledge what the user has
> done and offer to skip ahead or start fresh. At the end, offer to
> run `poc-spike`.

**`explain-concept`** (`factory/skills/explain-concept/SKILL.md`):

> Look up the requested concept in `factory/docs/factory-guide.md` and
> `factory/INDEX.yaml`. Explain it in plain language, calibrated to the
> user's apparent experience level. A junior in their first week gets
> the one-sentence version; a senior who asks about gate semantics gets
> the precise contract. If the concept spans multiple guide sections,
> synthesize rather than reciting. If the concept is not in the guide,
> say so.

### 4. Demote kit-manager from agent to skill

The kit-manager agent definition (`factory/agents/kit-manager.md`) is
retired. Its role — charter scaffolding, structured interview, ad-hoc
reference ingestion — becomes a workflow that VIRGIL executes by loading
the existing charter skills (`capture-charter`, `update-charter`,
`grilling`, `validate`).

The kit-manager's workflow documentation (assess → fill → validate) is
absorbed into VIRGIL's agent definition as procedural guidance for
project setup. The individual charter skills remain unchanged.

Existing references to kit-manager and chat-agent in skills
(`draft-proposal`, `detect-test-regime`) are updated to reference
VIRGIL.

### 5. Update CLI orientation files

`factory/config/AGENTS.md` contains five references to chat-agent and
kit-manager that must all update to VIRGIL:

- **Option A** (line 45): replace `docs/arc42/beginner-intro.md`
  walkthrough with: adopt VIRGIL, load `newcomer-tour` skill.
- **Option B7** (line 80): `→ chat-agent` becomes `→ virgil`.
- **Option D** (line 104): adopt `chat-agent` becomes adopt VIRGIL.
- **Adopt-pattern routing** (line 108): the list `chat-agent, kit-manager, coaching-agent` becomes `virgil, coaching-agent`.
- **Codex example** (line 22): `agents/chat-agent.md` becomes
  `agents/virgil.md`.

The orientation block is generated by `init-factory`'s
`_orientation_block()` function, which reads `factory/config/AGENTS.md`.
The change to `AGENTS.md` propagates to all CLIs — a single change
point.

### 6. Update the guided-tour skill

The existing `guided-tour` SKILL.md "Outside an active playbook"
section (line 29) hardcodes `docs/arc42/beginner-intro.md` in its
option A description. Rewrite to reference VIRGIL and the
`newcomer-tour` skill.

The guided-tour skill retains its reorientation role: "where am I?",
"what do I do next?" inside an active playbook. It does not absorb the
newcomer walkthrough — that belongs to `newcomer-tour`, loaded by
VIRGIL.

### 7. Retire the project-local copy

`docs/arc42/beginner-intro.md` in the agent-factory repository becomes
a redirect stub pointing to the new canonical location:

> This content has moved to
> [`factory/docs/factory-guide.md` § Getting Started](../../factory/docs/factory-guide.md).

This preserves existing links from `README.md` (root),
`docs/arc42/concepts.md`, proposals, and backlog items without
requiring updates to those historical documents.

### 8. Update factory-shipped references

Two files inside `factory/` currently link to the old location:

- `factory/README.md` — rewrite to point to
  `factory/docs/factory-guide.md` (Getting Started section).
- `factory/docs/factory-guide.md` — the opening line that says "start
  with the beginner's introduction" is replaced by the Getting Started
  section itself.

## Scope

**In this release:**

- `factory/agents/virgil.md` — new agent definition. Rename and expand
  chat-agent. Adopt pattern, skill-aware, thin role statement.
- `factory/skills/newcomer-tour/SKILL.md` — new skill for the
  newcomer walkthrough.
- `factory/skills/explain-concept/SKILL.md` — new skill for
  on-demand factory concept explanations.
- `factory/skills/comic-relief/SKILL.md` — new skill for
  context-aware nerdy humor (Dilbert × XKCD × South Park triangle).
- `factory/docs/factory-guide.md` — add "Getting Started" section;
  remove orchestrator and project-specific references; add seam
  between beginner and reference material.
- `factory/config/AGENTS.md` — all chat-agent and kit-manager
  references updated to VIRGIL (options A, B7, D, adopt-pattern
  routing, Codex example).
- `factory/skills/guided-tour/SKILL.md` — update option A description
  to reference VIRGIL; retain reorientation role.
- `factory/README.md` — beginner-intro link updated to factory-guide
  Getting Started section.
- `docs/arc42/beginner-intro.md` — replaced with redirect stub.
- `factory/agents/kit-manager.md` — retired; workflow absorbed into
  VIRGIL's agent definition.
- `factory/agents/chat-agent.md` — retired; superseded by VIRGIL.
- `factory/skills/draft-proposal/SKILL.md` — chat-agent references
  updated to VIRGIL.
- `factory/skills/detect-test-regime/SKILL.md` — kit-manager references
  updated to VIRGIL.
- `factory/INDEX.yaml` — register VIRGIL agent and new skills; remove
  retired agent entries.

**Explicitly deferred:**

- Rewriting the walkthrough content itself. This proposal moves it;
  editorial improvements are a separate concern.
- Absorbing coaching-agent into VIRGIL. Retrospectives and process
  improvement are a different audience (the team lead reviewing how
  work went, not the developer doing the work).
- Automatic newcomer detection (already deferred in the parent
  proposal).
- Localisation or per-project customisation of the walkthrough.

## CLI Agnosticism

VIRGIL lives in `factory/agents/`, which ships with the factory. Its
knowledge base is `factory/docs/factory-guide.md`, also inside
`factory/`. Both are available in any project after `init-factory`.
The agent runs in the current session (adopt pattern), so no
CLI-specific subagent spawning mechanism is needed.

The new skills (`newcomer-tour`, `explain-concept`) live in
`factory/skills/` and are symlinked into each CLI's skill directory
by `init-factory`, the same as every other skill.

## Relationship to Parent Proposal

This proposal is a point fix to the "Newcomer Onboarding and
Incremental Brownfield" proposal (accepted 2026-08-28). It corrects a
packaging oversight where the walkthrough content was placed in
project-specific space instead of factory-shipped space, and extends
the design by unifying the adopt-pattern agents into a single
skill-aware session companion. The parent proposal's completion
criteria ("A user who has never seen Agent Factory can pick option A,
walk through the tour, and run a poc-spike without encountering
undefined vocabulary") is not met today precisely because of this gap.

## Completion Criteria

- A fresh project with only `factory/` installed (no `docs/arc42/`
  directory) can run option A successfully.
- VIRGIL walks a newcomer through "Getting Started" conversationally,
  in plain language a junior developer in their first week would
  understand.
- VIRGIL explains advanced factory concepts on demand from the
  reference sections of `factory/docs/factory-guide.md`.
- VIRGIL loads charter skills and runs the kit-manager workflow when
  asked to set up a project.
- VIRGIL starts an open conversation for option D and routes to the
  right playbook when the idea finds its shape.
- `factory/docs/factory-guide.md` opens with a "Getting Started"
  section and has a clear seam before the reference material.
- The walkthrough content covers manual mode only — no orchestrator
  references, no automatic-mode graduation section.
- All four CLI orientation files adopt VIRGIL for options A and D.
- The `guided-tour` skill retains its reorientation role and no longer
  references `docs/arc42/beginner-intro.md`.
- `factory/README.md` links to the factory-guide Getting Started
  section.
- `factory/agents/chat-agent.md` and `factory/agents/kit-manager.md`
  are retired, with all factory-shipped references (AGENTS.md,
  `draft-proposal`, `detect-test-regime`, `guided-tour`, INDEX.yaml)
  updated to VIRGIL.

## Open Questions

None. The kit-manager workflow (assess → fill → validate) is absorbed
into VIRGIL's agent definition as procedural guidance for project
setup. The individual charter skills remain unchanged.

## Review History

### Consult Review — 2026-08-30

Reviewer: proposal-review-agent (consultative)
Reviewed commit: 20fdbaea20941e26086015110126f609a3ae7671

Observations 1–8 addressed in subsequent revisions. See prior version
for full observation text and resolutions.

### Adversarial Review — 2026-08-30

Reviewer: proposal-review-agent
Reviewed commit: 20fdbaea20941e26086015110126f609a3ae7671
Disposition: findings

| ID      | Severity | Check | Status   | Finding                                                                                    |
| ------- | -------- | ----- | -------- | ------------------------------------------------------------------------------------------ |
| PROP-01 | major    | 02    | resolved | Deleting beginner-intro.md breaks repo-local links. Resolution: redirect stub, not delete. |
| PROP-02 | major    | 04    | resolved | Invalid `scope` value. Resolution: changed to `cross_component`.                           |
| PROP-03 | major    | 05    | resolved | Nonexistent file in boundaries. Resolution: removed; source file added instead.            |
| PROP-04 | minor    | 03    | resolved | SKILL.md line 29 hardcodes old path. Resolution: called out in design.                     |
| PROP-05 | minor    | 08    | resolved | Arithmetic inconsistency in estimate. Resolution: corrected.                               |
| PROP-06 | minor    | 08    | resolved | Multiplier/playbook mismatch. Resolution: changed to `documentation-update`.               |

### Design Evolution (stakeholder session, 2026-08-30)

The proposal evolved through stakeholder conversation:

1. **Initial design:** Move `beginner-intro.md` into a `WALKTHROUGH.md`
   co-located with the guided-tour skill.
2. **Stakeholder direction:** The orchestrator does not ship with the
   factory; remove all references. The walkthrough is for a newcomer
   who just ran `init-factory`.
3. **Simplification:** Merge beginner content into
   `factory/docs/factory-guide.md` as a "Getting Started" section.
   One progressive document, beginner to advanced.
4. **Agent design:** Introduce a factory-guide agent as the counterpart
   to kit-manager — one owns factory knowledge, the other project
   knowledge.
5. **Unification:** Wrap chat-agent and kit-manager into one agent.
   Kit-manager becomes a skill. The chat-agent expands to load skills
   on demand.
6. **Naming:** VIRGIL — Versatile Interactive Resource: Guide,
   Instructor, Liaison. Named after Dante's guide through unfamiliar
   territory. The acronym resolves to the agent's three roles.

## Review — 2026-08-30 (pass 2)

Reviewer: proposal-review-agent
Reviewed commit: 20fdbaea20941e26086015110126f609a3ae7671
Disposition: findings

### Findings

| ID      | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ------- | -------- | ----- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | major    | 02    | resolved | Deleting beginner-intro.md breaks repo-local links. Resolution: redirect stub, not delete.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| PROP-02 | major    | 04    | resolved | Invalid `scope` value. Resolution: changed to `cross_component`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| PROP-03 | major    | 05    | resolved | Nonexistent file in boundaries. Resolution: removed; source file added instead.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| PROP-04 | minor    | 03    | resolved | SKILL.md line 29 hardcodes old path. Resolution: called out in design.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| PROP-05 | minor    | 08    | resolved | Arithmetic inconsistency in estimate. Resolution: corrected.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| PROP-06 | minor    | 08    | resolved | Multiplier/playbook mismatch. Resolution: changed to `documentation-update`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| PROP-07 | major    | 02    | resolved | Design section 4 claims playbook references to kit-manager exist in greenfield-development step 1 and brownfield-onboarding step 1; they do not (zero matches in either playbook). Three skills that DO reference these agents are not in scope: `factory/skills/draft-proposal/SKILL.md` (lines 5, 15: "chat-agent"), `factory/skills/detect-test-regime/SKILL.md` (lines 35, 81, 189: "kit-manager"), and `factory/skills/guided-tour/SKILL.md` (line 30: "chat-agent" in option D description). Resolution: removed phantom playbook claims; added `draft-proposal`, `detect-test-regime`, and `INDEX.yaml` to scope and boundaries. |
| PROP-08 | major    | 03    | resolved | Design section 4 contains an unresolved "or": kit-manager workflow preserved "as procedural guidance inside VIRGIL's agent definition, or as a dedicated `kit-manager` skill." Resolution: resolved to single option — workflow absorbed into VIRGIL's agent definition.                                                                                                                                                                                                                                                                                                                                                                |
| PROP-09 | major    | 05    | resolved | Three boundary files missing: `factory/INDEX.yaml`, `factory/skills/draft-proposal/SKILL.md`, `factory/skills/detect-test-regime/SKILL.md`. Resolution: added all three to boundaries list and scope.                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| PROP-10 | minor    | 06    | resolved | Open Questions states "None" but design contains an unresolved alternative (see PROP-08). Resolution: PROP-08 resolved the "or"; Open Questions "None" is now accurate.                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

### Summary

Checks 1 (completion criteria), 4 (impact classification), 7 (motivation), and 8 (estimate) passed clean. The four open findings cluster around one structural issue: the proposal evolved significantly through stakeholder conversation and the scope, design, and boundaries did not fully catch up. The phantom playbook references (PROP-07), the missing skill and INDEX.yaml boundaries (PROP-09), and the unresolved kit-manager "or" (PROP-08/PROP-10) must be resolved before a planning agent can decompose this into stories without coming back to ask what was meant.

## Review — 2026-08-30 (pass 3)

Reviewer: proposal-review-agent
Reviewed commit: 20fdbaea20941e26086015110126f609a3ae7671
Disposition: findings

### Prior findings

All prior findings (PROP-01 through PROP-10) verified resolved at this commit. No regressions.

### Findings

| ID      | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                                                                    |
| ------- | -------- | ----- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-11 | minor    | 01    | resolved | Completion criterion (line 357) says "all playbook references updated" but zero playbooks reference chat-agent or kit-manager. The actual references are in skills and AGENTS.md. Resolution: reworded to "all factory-shipped references" with explicit file list.                                        |
| PROP-12 | major    | 02    | resolved | AGENTS.md scope entry says "options A and D adopt VIRGIL" but AGENTS.md has three additional chat-agent/kit-manager references: line 22 (Codex example), line 80 (option B7), line 108 (adopt-pattern routing). Resolution: widened design section 5 and scope to enumerate all five AGENTS.md references. |

### Check results

| Check | Name                             | Result | Notes                                                                                          |
| ----- | -------------------------------- | ------ | ---------------------------------------------------------------------------------------------- |
| 01    | Completion criteria testable     | pass   | Minor: "playbook" wording misdirects (PROP-11).                                                |
| 02    | Scope boundary sharp             | fail   | AGENTS.md changes under-scoped — three references outside options A/D not addressed (PROP-12). |
| 03    | Design decomposable              | fail   | No design guidance for AGENTS.md references outside A/D; same root cause as PROP-12.           |
| 04    | Impact classification consistent | pass   |                                                                                                |
| 05    | Boundary references exist        | pass   | All 11 boundary paths resolve at reviewed commit.                                              |
| 06    | Open questions genuine           | pass   |                                                                                                |
| 07    | Motivation justifies timing      | pass   |                                                                                                |
| 08    | Estimate plausible               | pass   |                                                                                                |

### Notes

**init-factory (in boundaries, not in scope):** Correctly placed. init-factory auto-discovers agents via directory iteration (Codex/Copilot generators) and skills via directory iteration (symlinks). AGENTS.md content propagates to all CLIs through `@`-include (Claude Code) or inline injection (Copilot/Pi). No init-factory code change is needed.

**Playbook references (confirming PROP-07 resolution):** `greenfield-development.md` and `brownfield-onboarding.md` contain zero matches for `chat-agent` or `kit-manager`. The original PROP-07 finding was correct: the phantom playbook claims were removed from the design. The residual issue is only in the completion criterion's wording (PROP-11).

### Summary

Six of eight checks pass clean. Two fail on the same root cause: the scope and design address AGENTS.md "options A and D" but the file contains three additional chat-agent/kit-manager references (option B7, general routing, Codex example) that would survive the change and leave broken instructions in every downstream CLI session. PROP-12 must be addressed — either widen the scope/design to cover all AGENTS.md references, or explicitly defer the non-A/D references with rationale. PROP-11 is a minor wording fix in the completion criteria.
