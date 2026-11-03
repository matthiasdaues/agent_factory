# Review Scrapbook: Agent Factory Process Flow

## What is reviewed

- **Board file:** [agent factory process flow - Frame 2.svg](agent%20factory%20process%20flow%20-%20Frame%202.svg)
- **Board date:** 2026-11-03, as stated in the board legend.
- **Dev commit at review start:** `a94ed69a13ae98ead9b9db842f7da4327a75b411`
- **Shape counts:** about 62 agent steps, 31 human steps, 47 gates or decisions,
  and 10 terminal failure states. The counts come from shape fill colours and
  are approximate, because Miro can draw one shape more than once.

## How entries are sorted

- **Good:** The process does something right, and a change should keep it.
  Example: authors and reviewers always run in separate sessions.
- **Bad:** The process works but makes a poor choice that costs time, tokens, or
  attention. Example: five review loops can repeat with no limit.
- **Faulty:** The process breaks, or it is undefined at that point. Example: a
  failed premerge-check leaves a story in `dispatched`, so close-wave never
  finishes.

If a step can fail or get stuck, the entry is faulty. If the step runs but
wastes something, the entry is bad.

"Where" uses the board's three left columns: phase, cluster, and step. Each
section is ordered by board position, from top to bottom. An entry keeps its ID
when it moves to another section.

## Inbox

Raw notes go here first. They are sorted into the sections below later.

- The board is 5,458 × 20,072 px and reads as one long scroll. It works as a
  reference to search in, not as an overview. A one-screen view with the four
  phases, the human stops per phase, and the red gaps would show the shape at a
  glance.
- The board may be drawn by hand or produced by
  [miro-generator/](miro-generator/). This was not checked. A hand-drawn board
  drifts from the playbooks.

## Good things

### GOOD-01: The gaps are on the board

- **Where:** whole board, red dashed boxes.
- **Observation:** The board marks the missing proposal-lint, the undefined
  premerge state, the missing gates in manual mode, and the missing owner for
  the merge into dev.
- **Why it matters:** A reader sees where the process is not defined yet,
  instead of assuming every path is covered.
- **Keep by:** Every regenerated board keeps the "Gap in the definitions"
  shape type.

### GOOD-02: Authors and reviewers run in separate sessions

- **Where:** Proposal › Review and acceptance; Specification › Review;
  Architecture › Review; Reconciliation › Code review.
- **Observation:** Each review runs in a fresh session, and fixes go back to
  the author agent in another fresh session.
- **Why it matters:** An agent never approves its own work, so the review does
  not inherit the author's blind spots.
- **Keep by:** No change merges author and reviewer into one session.

### GOOD-03: Agents create, scripts validate

- **Where:** Specification › spec-lint and validate; Architecture › Commit
  hooks; Building › verify-story and premerge-check.
- **Observation:** Deterministic checks sit between the agent steps.
  verify-story checks the reported commit SHA instead of the agent's report.
- **Why it matters:** The gates decide whether work is done, not the agent's
  self-report.
- **Keep by:** Every new agent step that produces an artifact is followed by a
  script check where one can exist.

### GOOD-04: The gate-check loop always ends

- **Where:** Implementation › Building › Gate-check loop.
- **Observation:** A failed gate goes to a fresh developer agent, up to three
  times. Then the next model tier gets three more tries. Then the story is
  marked failed.
- **Why it matters:** The loop has a known worst-case cost and cannot run
  forever.
- **Keep by:** The cap and the escalation stay in place when the loop changes.

### GOOD-05: Every step names its artifact and owner class

- **Where:** Artifacts column, right side of the board.
- **Observation:** Each step shows the file it leaves behind, tagged with a
  class such as Core, Derived view, Decision record, or Quality record.
- **Why it matters:** A reader can see what each step changes and which
  artifacts must never be edited by hand.
- **Keep by:** New steps get an artifact row and a class tag.

## Bad things

### BAD-01: No proposal-lint script exists

- **Where:** Proposal › Draft › Readiness checklist passes?
- **Observation:** The readiness checklist is checked by hand. No script under
  `packages/factory/scripts/` checks it.
- **Cost:** Human attention at every proposal, and checks that differ from one
  reviewer to the next.
- **Suggestion:** Write a proposal-lint for the checklist items a script can
  check, such as required sections and the status field.

### BAD-02: Human attention goes to low-value stops

- **Where:** Architecture › Author (Chapters approved, Pugh matrix, Each ADR
  approved); Planning › Once per backlog (Slicing approved, EPICs approved,
  Slices approved); every review cluster (Findings shown first).
- **Observation:** The human approves many intermediate artifacts before the
  first story is dispatched. Four review clusters each ask the human to triage
  findings.
- **Cost:** Human attention is the scarcest resource in the process, and these
  stops use it where a wrong call is cheap to correct later.
- **Suggestion:** Keep the stops with the most weight: proposal acceptance,
  story decisions, and the final diff. Batch or sample the rest.

### BAD-03: Small changes have no fast lane

- **Where:** whole board.
- **Observation:** The board shows one path for every change. "Architecture
  change?" lets a change skip one block, but specification and planning look
  mandatory.
- **Cost:** A one-file bug fix pays the full ceremony of a feature.
- **Suggestion:** Show the path a one-file fix takes. If that path does not
  exist, define it.

### BAD-04: Review loops have no cap

- **Where:** Proposal › Review and acceptance; Specification › Review;
  Architecture › Review; Reconciliation › Alignment; Reconciliation › QA.
- **Observation:** Each loop returns with "re-review" and has no iteration
  limit. Only the gate-check loop has a cap.
- **Cost:** Tokens and time, mostly in late passes whose findings are edge
  cases that an earlier fix created.
- **Suggestion:** Give each review loop a cap and an escalation, as the
  gate-check loop has. A separate proposal sets the threshold a finding must
  pass to block. It uses quantifiable measures: a named failure case, a risk
  assessment, and an expected cost, that is, the probability times the cost of
  the failure. The proposal is not written yet.

### BAD-05: The same diff gets two Fagan reviews

- **Where:** Reconciliation › Code review (code-review agent, fagan-review);
  Reconciliation › QA (Fagan and security review).
- **Observation:** The code-review agent runs fagan-review on the diff. Then
  the QA agent runs a Fagan review again.
- **Cost:** A second review pass whose added value is not known.
- **Suggestion:** Check whether the second Fagan pass finds anything the first
  one missed. If it finds nothing new, drop one of them.

### BAD-06: The board shows no cost

- **Where:** whole board.
- **Observation:** The board names a model tier only at "Escalate to next
  tier". It shows no tier, token budget, or time per step.
- **Cost:** A practitioner cannot see where the tokens and the time go.
- **Suggestion:** Add the model tier per agent step, and later measured cost
  per phase from usage capture.

## Faulty things

### FAULT-01: A failed premerge-check deadlocks the wave

- **Where:** Implementation › Building › merge-story › premerge passes?
- **Observation:** On a failed premerge-check, the story stays `dispatched`.
  That state is not terminal.
- **Failure case:** One story in a wave fails premerge-check. close-wave waits
  for every story to be terminal, so the wave never closes and no later wave
  starts.
- **Evidence:** [BUG-0114](../../docs/findings/BUG-0114.md), open, severity
  major; `packages/factory/scripts/dispatch:1849`.
- **Fix direction:** Follow the three failure paths that
  [BUG-0114](../../docs/findings/BUG-0114.md) defines, and record each one in
  the ledger.

### FAULT-02: Manual mode has no quality gates

- **Where:** Implementation › Building › Manual: serial stories.
- **Observation:** The board marks "No quality gates in manual mode" as a gap.
  The human commits after the developer agent, with only the pre-commit hooks
  and a code review in between.
- **Failure case:** A story in manual mode is committed without crap-score,
  mutation, test-design-verify, or dependency-check. Teams usually start in
  manual mode, so their first stories are the least checked.
- **Evidence:** [manual-mode-gates.md](../../docs/proposals/manual-mode-gates.md).
- **Fix direction:** The human cuts the story branch from dev. The developer
  agent implements, gets a review, fixes the findings, and passes crap-score and
  mutation testing on that branch. Then it hands the branch back as done. A gate
  refuses `done` while a finding for the story is open. The proposal records
  this as DEC-04 to DEC-07.

### FAULT-03: Nobody owns the merge into dev

- **Where:** Reconciliation › Close the feature › Merge feature into dev.
- **Observation:** The board marks "No defined owner for this merge" as a gap.
- **Failure case:** A feature passes reconciliation and QA. No agent and no
  playbook step merges it into dev, so the finished work can sit on its branch
  with no next step.
- **Evidence:** Board gap shape only. No playbook reference was checked.
- **Fix direction:** Name an owner for the merge, and state the gate it runs:
  premerge-check and the full test suite.
