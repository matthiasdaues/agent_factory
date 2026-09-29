# Value-First Onboarding Usability Protocol

This protocol guides a quality researcher through a moderated usability session with a participant who did not build Agent Factory. The session records the participant's journey through the complete onboarding sequence: installation, first session, and first task execution.

## Session Metadata

| Field                      | Value                                  |
| -------------------------- | -------------------------------------- |
| **Date**                   |                                        |
| **Session Time Start**     |                                        |
| **Session Time End**       |                                        |
| **Participant Identifier** | (anonymous ID only; no names)          |
| **Moderator Name**         |                                        |
| **Moderator Email**        |                                        |
| **Recording Method**       | (screen recording, notes, audio, etc.) |

## Participant Prerequisite

**REQUIRED CONFIRMATION BEFORE STARTING:**

The participant must not have built Agent Factory before. The moderator must confirm this before beginning the session.

- [ ] I have confirmed the participant has not built Agent Factory.
- [ ] I have explained the purpose of this session: to observe how a newcomer experiences the onboarding journey.
- [ ] I have explained that I will not guide the participant unless they ask for help.

______________________________________________________________________

## Journey Phases

### Phase 1: Installation

**Phase Duration:** Start time: \_\_\_\_\_ | End time: \_\_\_\_\_

This phase covers the steps the participant takes from discovering Agent Factory through receiving an installation receipt.

#### Steps Observed

- [ ] Preflight (reading readiness report)
- [ ] Consent (reviewing planned changes)
- [ ] Installation (running the installation)
- [ ] Receipt (receiving and reading the installation receipt)

#### Notes

(Record any observations about this phase that don't fit other sections)

______________________________________________________________________

### Phase 2: First Session

**Phase Duration:** Start time: \_\_\_\_\_ | End time: \_\_\_\_\_

This phase covers the participant's first interaction with Factory after installation, including project insight, context capture decision, gate demonstration, and hook configuration.

#### Steps Observed

- [ ] Project insight (viewing stack detection and recommendations)
- [ ] Context capture gate (deciding whether to scan the project)
- [ ] Gate demonstration (viewing a gate example)
- [ ] Hook configuration (deciding which hooks to enable)

#### Notes

(Record any observations about this phase that don't fit other sections)

______________________________________________________________________

### Phase 3: First Task

**Phase Duration:** Start time: \_\_\_\_\_ | End time: \_\_\_\_\_

This phase covers the participant's execution of one isolated task: previewing it, running it, and selecting an outcome.

#### Steps Observed

- [ ] Task preview (reading goal, duration, artifacts)
- [ ] Sandbox execution (running the task)
- [ ] Outcome selection (choosing to discard, retain, or promote)

#### Notes

(Record any observations about this phase that don't fit other sections)

______________________________________________________________________

## Recording Fields

### 1. Elapsed Time

| Phase                      | Start Time | End Time | Duration |
| -------------------------- | ---------- | -------- | -------- |
| Installation               |            |          |          |
| First Session              |            |          |          |
| First Task                 |            |          |          |
| **Total Session Duration** |            |          |          |

______________________________________________________________________

### 2. Decision Count

Record each decision point where the participant made a choice.

| Phase | Decision | How Decided | Time (approx) |
| ----- | -------- | ----------- | ------------- |
|       |          |             |               |
|       |          |             |               |
|       |          |             |               |
|       |          |             |               |
|       |          |             |               |

**Total Decisions:** \_\_\_\_\_

______________________________________________________________________

### 3. Unclear Terms

Record any Factory terms or interface language the participant found unclear or asked about. Write the participant's verbatim language whenever possible.

| Term or Phrase | Participant's Exact Words | Context | Phase |
| -------------- | ------------------------- | ------- | ----- |
|                |                           |         |       |
|                |                           |         |       |
|                |                           |         |       |
|                |                           |         |       |

______________________________________________________________________

### 4. Abandonment Points

Record any step or decision where the participant stopped, did not complete, or expressed intent to give up.

| Step Name | What Happened | Participant's Reason (verbatim) | Phase | Recovered? |
| --------- | ------------- | ------------------------------- | ----- | ---------- |
|           |               |                                 |       | Yes / No   |
|           |               |                                 |       | Yes / No   |
|           |               |                                 |       | Yes / No   |

______________________________________________________________________

### 5. Recovery Attempts

Record situations where the participant encountered an error, confusion, or blocker, and what they tried to resolve it.

| What Failed | What Participant Tried | Result                     | Moderator Intervention? |
| ----------- | ---------------------- | -------------------------- | ----------------------- |
|             |                        | Success / Partial / Failed | Yes / No                |
|             |                        | Success / Partial / Failed | Yes / No                |
|             |                        | Success / Partial / Failed | Yes / No                |
|             |                        | Success / Partial / Failed | Yes / No                |

**Notes on Interventions:** (When did the moderator help? What did they say?)

______________________________________________________________________

### 6. Stated Next Action

At the end of the session, ask: "What would you do next with Agent Factory?" Record the participant's verbatim response.

**Participant's Exact Words:**

______________________________________________________________________

## Moderator Guidelines

**CRITICAL CONSTRAINT: Do not intervene or guide the participant except when they explicitly ask for help.**

- **Observe only** — Do not point out features, buttons, or options the participant has not yet discovered.
- **Wait for questions** — If the participant is stuck or confused, wait to see if they try to solve the problem themselves (e.g., reading help text, clicking buttons, re-reading instructions).
- **Respond only when asked** — If the participant asks a direct question ("How do I...?" "What does this mean?"), you may clarify. Keep clarifications brief and factual.
- **Do not apologize for the tool** — Do not say "I know this is confusing" or "This step is difficult." Record the confusion and let the participant's actions speak for themselves.
- **Record, don't judge** — If the participant makes an unexpected choice or skips a step, record what happened without commentary.
- **Voice your presence minimally** — Soft verbal signals ("Mm-hmm," "I see") are acceptable to show you're listening, but avoid leading comments.

______________________________________________________________________

## Terminology Glossary

### Agent Factory / Factory

The entire system being tested: a framework for building and managing Claude AI agents, skills, and workflows in a Git repository.

### Agent

A Claude AI assistant configured with specific capabilities, instructions, and access to project context. Agents can be launched by skills, workflows, or directly via the CLI.

### Skill

A reusable, standalone task that an agent or user can invoke. Skills have clear inputs and outputs and often automate a common workflow step (e.g., "code review," "documentation update").

### Playbook

A multi-step workflow that chains together agents and skills to accomplish a larger goal. Playbooks define the sequence, decisions, and handoffs between steps.

### Rulebook

A set of documented conventions, constraints, or best-practice rules that guide development, testing, or process. Rulebooks are references, not executable code.

### Preflight / Readiness Check

An automated diagnostic that verifies the host machine has the required tools and configuration before installation begins. It does not make changes; it only reports whether installation can proceed.

### Consent

Explicit approval from the user before any changes are made to the project. Factory prompts for consent at each major step.

### Installation Receipt

A record printed after Factory is installed that lists all changes made, how to verify the installation, and the command to run next.

### Project Insight / Stack Detection

An automated scan that identifies the programming languages, frameworks, test tools, and CI/CD setup of the project. Presented to the user at the start of the first session.

### Context Capture / Agent Context

An optional scan of the project that collects domain language, architecture patterns, and business rules, storing them in `docs/agent-context.md` for agents to reference.

### Gate / Pre-commit Hook

An automated check that runs before each Git commit. Gates validate code quality, prevent dangerous operations, or enforce style rules.

### Gate Demonstration

A one-minute walkthrough showing how a gate works: a sample mistake intentionally introduced to a disposable file, the gate catches and reports it, the fix is applied, and the gate passes. The demonstration uses only Factory-owned temporary files.

### Hook Configuration

A step where the user chooses which gates (pre-commit hooks) to enable in their project. Not all gates apply to every project type.

### Worktree / Sandbox

An isolated copy of the Git repository where work can happen without affecting the main branch or working tree. Used for the first task to contain experimentation.

### First Task / Onboarding Task

An isolated, low-stakes task assigned during onboarding to help the participant get comfortable with Factory before working on real project tasks. The task result can be discarded, saved as reference, or promoted to real work.

### Task Outcome

The participant's choice after completing the first task: (1) Discard the sandbox, (2) Save selected artifacts to `docs/spikes/` for reference, or (3) Promote to real work by creating a feature branch.

### Moderator / Quality Researcher

The person conducting this usability session. The moderator observes, records, and does not guide the participant.

### Participant

The person using Agent Factory for the first time. The participant has not built Agent Factory before.

______________________________________________________________________

## Post-Session Notes

After the session, use this space to record observations that did not fit the structured fields above: overall impressions, patterns you noticed, or recommendations for follow-up.

(Write freely here)

______________________________________________________________________

## Completion Checklist

Before finalizing this session record, verify:

- [ ] All six recording fields contain at least partial data
- [ ] Elapsed time is recorded for each phase
- [ ] At least one decision was recorded (or note that none occurred)
- [ ] Unclear terms are recorded verbatim when the participant used them
- [ ] Any abandonment points are recorded with participant reasoning
- [ ] Recovery attempts show what the participant tried and whether it worked
- [ ] Stated next action is recorded verbatim
- [ ] All three journey phases have start and end times
- [ ] Participant prerequisite confirmation is checked
- [ ] Moderator name and date are recorded
