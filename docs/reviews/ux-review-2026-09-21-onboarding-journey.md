# Agent Factory Onboarding Journey UX Review

Date: 2026-09-21

## Executive Summary

Agent Factory meets a newcomer like a mature engineering framework, not like
a product. Its core promise is strong: visible steps, independent review,
deterministic checks, and human approval. The writing is unusually clear for
infrastructure tooling. However, the onboarding asks for substantial
commitment and conceptual learning before the user experiences value.

The trust model is sound, but the activation journey is weak.

The Factory already contains the right onboarding components. These include
[`poc-spike`](../../packages/factory/playbooks/poc-spike.md),
[`VIRGIL`](../../packages/factory/agents/virgil.md), reversible installation,
repository scanning, and progressively rigorous playbooks. The main gap is
their sequence. The newcomer should experience one small, safe success before
configuring the system.

## Scope and Method

This review traces the current journey from initial repository contact to real
project work. It covers installation, fitting, orientation, and the first
experiment. It uses these user experience criteria:

- discoverability;
- time to first value;
- cognitive load;
- progressive disclosure;
- consistency and trust;
- feedback and recovery;
- sensible defaults;
- recognition rather than recall.

Primary evidence came from these sources:

- the [root README](../../README.md);
- the [Factory setup guide](../../packages/factory/README.md);
- the [Getting Started guide](../../packages/factory/docs/factory-guide.md#getting-started);
- the [installer](../../packages/factory/scripts/init-factory);
- the [session menu](../../packages/factory/config/session-menu.md);
- the [VIRGIL definition](../../packages/factory/agents/virgil.md);
- the [newcomer-tour skill](../../packages/factory/skills/newcomer-tour/SKILL.md).

This report follows the earlier
[new-user journey review](ux-review-2026-09-09-new-user-journey.md). It focuses
on the current onboarding sequence and its remaining inconsistencies.

## Journey Map

| Moment           | What the newcomer experiences                                      | UX appraisal                            |
| ---------------- | ------------------------------------------------------------------ | --------------------------------------- |
| Discovery        | A clear problem statement and a human-control principle            | Strong                                  |
| Evaluation       | A large repository with many agents, skills, scripts, and records  | Intimidating                            |
| Installation     | Clone, install prerequisites, run a script, choose CLI wiring      | High commitment before proof            |
| Install receipt  | Target, selected CLI, and uninstall command                        | Missing a strong next action            |
| First session    | Fitting interruption or a four-lane menu                           | Context-aware but process-first         |
| Orientation      | A conversational tour through terminology and machinery            | Clear but too much before doing         |
| First experiment | `poc-spike` produces a small runnable result                       | Correct activation device, reached late |
| Real work        | Workstreams, intent selection, playbooks, agents, and gates expand | Complexity rises abruptly               |

## Strengths

### The trust story is credible

The [root README](../../README.md) opens with the user problem rather than the
architecture. Its central promise—agentic creation, deterministic validation,
and human decisions—is concise and useful.

Reversible installation, controlled updates, explicit artifacts, independent
review, and visible gates reduce adoption risk. They show what the system will
do to the user's project. The author-reviewer separation explains a concrete
quality mechanism. It does not claim that artificial intelligence output is
inherently reliable.

### The basic mental model is clear

The
[Getting Started guide](../../packages/factory/docs/factory-guide.md#the-five-words-you-will-keep-hearing)
defines five core terms. It explains agent, skill, playbook, gate, and context
in plain language. The explanations are clear.

### Fitting is contextual and recoverable

The Factory scans an existing repository before asking questions. The fitting
procedure in the [VIRGIL definition](../../packages/factory/agents/virgil.md#fitting)
is resumable. The user may also skip it. These choices support recovery.

### The first-spike concept is excellent

The [`poc-spike` playbook](../../packages/factory/playbooks/poc-spike.md) is
small, disposable, visible, and runnable. It lets the Factory earn trust
before the user commits to a production workflow. Its problem is placement,
not design.

## Findings

### UX-01: The install command is not ready to copy

**Severity: High**

The install example in the [root README](../../README.md#try-it) contains the
placeholder `<agent-factory-repo-url>`. A newcomer cannot copy the primary
install command without first finding the repository location.

There is no pre-install product preview. The user must clone the repository
and run a script before seeing the interaction model.

**Recommendation:** publish one canonical install command and place a short,
read-only demonstration before the installation request.

### UX-02: The repository exposes internal scale before user value

**Severity: Medium**

The repository contains the Factory product and its development records. The
records include a backlog, findings, proposals, reviews, specifications, and
research. The
[root README](../../README.md#repository-internals) explains that these are
internal. However, users see the records before they read that explanation.

The product currently contains 17 agents, 57 skills, 11 playbooks, and 54
scripts. Experts may see capability. Newcomers may see a large learning cost.

**Recommendation:** make the distributable product, a quick demonstration,
and a short conceptual overview the dominant public surface. Keep development
history clearly secondary.

### UX-03: The trust promise contains contradictions

**Severity: High**

The [root README](../../README.md#try-it) says installation never modifies the
project's configuration. The same section says installation changes
`.pre-commit-config.yaml` and `.gitignore`. The intended scope may exclude
these files, but the text does not say so.

The [Factory setup guide](../../packages/factory/README.md#test-execution)
documents `--no-verify` as a bypass. The
[Factory rules](../../packages/factory/rulebooks/rules.md#git-workflow) forbid
bypassing a failing hook. Safety guidance must be consistent.

**Recommendation:** describe installation effects with exact scope and remove
documented bypass advice that contradicts the operating rules.

### UX-04: CLI selection has a surprising default

**Severity: High**

When no CLI is detected, the
[installer](../../packages/factory/scripts/init-factory) asks which CLIs to
wire. Blank input resolves to all CLIs, and non-interactive execution also
falls back to all CLIs. This conflicts with the README's promise that the
installer wires only what the user needs.

Blank input should not create the broadest integration footprint.

**Recommendation:** default to one detected or active CLI. Require an explicit
choice for “all,” and cancel or ask again when no safe default exists.

### UX-05: Installation ends without bridging into use

**Severity: High**

The installer receipt reports the target, selected CLI, and uninstall command.
It does not prominently tell the newcomer to:

1. enter the target directory;
2. open the selected coding CLI;
3. start the Factory session;
4. choose the recommended first action.

The installer completes its own task but leaves the user's next task unclear.
This is the largest activation gap in the current journey.

**Recommendation:** end with one exact next command, the expected first
screen, an approximate time to first result, and a reversible first exercise.

### UX-06: The first encounter is administrative

**Severity: High**

For an existing project, the first conversation begins with a fitting
decision. The
[Codex session orientation](../../packages/factory/config/AGENTS.codex.md#session-start)
requires this behavior. Fitting can cover model tiers, fingerprint
confirmation, agent context, test detection, and hook decisions.

The model matrix shows the problem clearly. It asks the newcomer to choose
economy, standard, and strong model identifiers before running an agent. This
is an advanced decision.

**Recommendation:** begin with a read-only scan summary and offer a tiny
demonstration first. Defer model-tier optimization until differentiated model
routing is required.

### UX-07: The greenfield path is internally inconsistent

**Severity: Critical**

Three sources describe different behavior:

- The [Codex session orientation](../../packages/factory/config/AGENTS.codex.md#session-start)
  treats `greenfield` as ready and opens the session menu.
- The [VIRGIL definition](../../packages/factory/agents/virgil.md#fitting) says
  greenfield projects must still configure model-matrix step 0.
- The [Getting Started guide](../../packages/factory/docs/factory-guide.md#what-init-factory-put-on-your-disk)
  says greenfield projects receive sensible defaults.

The [installer](../../packages/factory/scripts/init-factory) writes
`CONFIGURE-ME` entries and sets `on_missing = halt`. The interface can report
readiness and later stop at dispatch.

**Recommendation:** define one greenfield contract. Either provide working
defaults or require configuration before the menu reports the project ready.
Do not defer the failure until dispatch.

### UX-08: The session menu offers navigation but little guidance

**Severity: Medium**

The four lanes in the
[session menu](../../packages/factory/config/session-menu.md) reduce the
initial choice set. However:

- “Housekeeping” is internal language;
- “Open Stage” is evocative but not self-explanatory;
- “Project Work” expands into workstream administration and another large
  choice tree;
- no option is clearly recommended from observed project state.

The menu groups complexity. It still asks the newcomer to classify their
intent using Factory concepts.

**Recommendation:** lead with one contextual recommendation and retain the
four lanes as secondary navigation.

### UX-09: The newcomer tour teaches too much before action

**Severity: Medium**

The [newcomer-tour skill](../../packages/factory/skills/newcomer-tour/SKILL.md)
requires plain language, short explanations, and pauses. Its content still
covers many concepts before the user completes a task. These include execution
mode, reviewer isolation, installed files, five phases, playbooks, and safety
habits.

The opening question mentions `poc-spike`, agent context, and playbooks. A
first-time user may not understand these terms.

The procedure requires a complete Getting Started walkthrough. It then
requires another explanation of installed artifacts. The section already
explains those artifacts. This conflicts with the instruction to avoid
repetition.

**Recommendation:** teach only human approval, playbook-guided specialization,
and automatic checks before the first spike. Explain other concepts when the
user encounters them.

### UX-10: Learning by doing is advocated but not practiced

**Severity: High**

The [Getting Started guide](../../packages/factory/docs/factory-guide.md#where-to-go-next)
correctly says the Factory rewards learning by doing. The operational order is
closer to:

```text
install → configure → choose lane → learn vocabulary → choose workflow → act
```

The stronger order is:

```text
preview → one tiny success → explain what happened → configure when needed
```

**Recommendation:** use `poc-spike` as the main newcomer activity. Do not make
the spike the final step after conceptual instruction.

### UX-11: The beginner journey exposes workstream machinery

**Severity: Medium**

The [Project Work procedure](../../packages/factory/config/session-menu.md#p--project-work)
asks the user to start or continue a workstream. It then creates a workstream
record and session binding. It runs intention selection before presenting
another decision tree. These control concepts are unnecessary for a first
task.

**Recommendation:** accept an ordinary-language goal, create or select the
workstream invisibly when unambiguous, and ask only when the choice changes the
outcome.

### UX-12: Onboarding is verified structurally, not experientially

**Severity: Medium**

The current tests verify installer parsing, fitting-state derivation, and menu
content. This review found no complete newcomer journey test. It also found no
recorded usability measure for:

- time to first runnable result;
- number of decisions before value;
- abandonment points;
- understanding of the next action;
- recovery after skipping fitting;
- comprehension without prior Factory vocabulary.

**Recommendation:** add a scripted first-run acceptance journey and test it
with people unfamiliar with the Factory. Track decisions and elapsed time to
the first runnable result.

## Priority Recommendations

### Immediate

1. Resolve the greenfield model-matrix contradiction.
2. Add an explicit next-action handoff to the installer receipt.
3. Stop treating blank or non-interactive CLI selection as “all.”
4. Replace the repository URL placeholder with the canonical URL.

### Next

1. Make a ten-minute disposable spike the primary onboarding path.
2. Replace the neutral first-session menu with a contextual recommendation.
3. Defer model-tier decisions until the first dispatch that needs them.
4. Reduce the newcomer tour to three ideas taught through the spike.
5. Hide workstream and session-binding concepts until they become relevant.

### Then

1. Add a pre-install, read-only preview.
2. Present expected outputs, decisions, cost, and duration before each
   playbook.
3. Create one progress view for phase, artifacts, findings, next decision,
   and recovery.
4. Run observed usability sessions with people who have not contributed to
   Agent Factory.

## Target Journey

The target experience should be:

```text
discover → preview → install → inspect changes → run tiny spike
         → understand what happened → configure only what the next task needs
```

The product should communicate:

> Describe an outcome in ordinary language. The Factory will show the smallest
> credible route. It will explain the risk and begin with a reversible step.

Today the user must understand the Factory before choosing how to use it. A
better journey starts with one small success. It explains each system concept
when that concept becomes useful.
