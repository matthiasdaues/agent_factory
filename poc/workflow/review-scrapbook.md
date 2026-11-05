# Review Scrapbook: Agent Factory Process Flow

## What is reviewed

- **Board file:** [agent factory process flow - Frame 2.svg](agent%20factory%20process%20flow%20-%20Frame%202.svg)
- **Board date:** 2026-11-03, as stated in the board legend.
- **Dev commit at review start:** `a94ed69a13ae98ead9b9db842f7da4327a75b411`
- **Shape counts:** about 62 agent steps, 31 human steps, 47 gates or decisions,
  and 10 terminal failure states. The counts come from shape fill colours and
  are approximate, because Miro can draw one shape more than once.

## Overall assessment

The board is a strong current-state map. Its map score measures coverage,
traceability, and navigation separately from the quality of the mapped process.

| View                        | Score |
| --------------------------- | ----: |
| Governance and traceability |  8/10 |
| Daily Agentic Coding use    |  5/10 |
| Lead developer control      |  7/10 |
| Full lifecycle coverage     |  5/10 |
| Visual overview             |  4/10 |

The overall assessment is 6/10 as a process design and 8/10 as a map of the
current Factory. The process favours control over short feedback cycles.

## Cargo-cult verdict

The Factory is not pure cargo cult. Its core addresses real failure modes of
coding agents: false completion claims, inherited assumptions, conflicting
parallel edits, stale project context, and unbounded retry loops.

The cargo-cult risk begins when an artifact, review, or agent role counts as
quality without evidence that it prevents a named failure. More ceremony then
creates coordination work without making the delivered change safer.

The valuable core is verifiable delegation. Agents work inside explicit
boundaries, scripts check observable results, independent sessions challenge
the work, and implementation findings return to project truth.

## What the map needs for 10/10

### 1. An explicit boundary

The map states where the Factory begins and ends. It marks delivery, operation,
and other external work as included or outside its scope.

The map also states whether it represents the current state, the target state,
or both. Current and target paths use different visual treatments.

### 2. Three zoom levels

The map has three connected views:

1. A one-screen overview shows phases, entry points, human stops, and terminal
   states.
2. One map per phase shows clusters, actors, gates, and main artifacts.
3. Execution maps show transitions, loops, failure paths, and detailed
   artifacts.

The overview links to the phase maps. A phase map links to each execution map.

### 3. Routes that start with intent

A developer can start with a goal such as fixing a bug, adding a feature,
resolving a finding, or making an architecture decision.

Each route names its first step, required inputs, human decisions, expected
artifacts, and terminal state.

### 4. A visible current position

Every step has a stable ID. A running workstream can use that ID to highlight
its current position.

From that position, a reader can identify the owner, next step, completion
condition, and failure route within 30 seconds.

### 5. Links to binding sources

Each agent step links to its agent definition. Each flow links to its playbook.
Each gate links to its script and checked contract.

Artifacts link to their schema or template. Known gaps link to their finding,
bug, or proposal.

### 6. Mechanically checked currency

The map records the full Git SHA of the state it represents. A documented
generator or maintenance source owns the map.

A deterministic check detects drift between the map and the Factory's agents,
playbooks, gates, and artifact declarations.

### 7. Distinct status types

The map distinguishes an existing path, a planned path, a known defect, and an
intentional boundary. A red gap never leaves the reader guessing which type it
represents.

### 8. A small visual grammar

The map keeps its current distinction between human steps, agent steps, gates,
failures, and gaps. It adds only the status and scope markers needed above.

Details such as cost, model tier, and artifact metadata belong in a linked
detail view when they make the main route harder to read.

The map reaches 10/10 when a new lead developer can understand the boundary,
choose a route, locate current work, follow every source, and trust its
currency without asking the author.

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
  The loop now runs the gates through `story-gates`, the script that manual mode
  uses too
  ([manual-mode-gates.md](../../docs/proposals/manual-mode-gates.md) DEC-14).

### GOOD-05: Every step names its artifact and owner class

- **Where:** Artifacts column, right side of the board.
- **Observation:** Each step shows the file it leaves behind, tagged with a
  class such as Core, Derived view, Decision record, or Quality record.
- **Why it matters:** A reader can see what each step changes and which
  artifacts must never be edited by hand.
- **Keep by:** New steps get an artifact row and a class tag.

### GOOD-06: Implementation findings flow back into project truth

- **Where:** Implementation › Building › Commit and spec feedback;
  Reconciliation › Alignment and Backfill and traceability.
- **Observation:** `spec-feedback` and reconciliation return implementation
  discoveries to the specification, architecture, scope map, and test links.
- **Why it matters:** The documents do not stay frozen while the code reveals
  missing or inaccurate rules.
- **Keep by:** Every implementation path ends with a check for specification,
  architecture, and traceability changes.

### GOOD-07: Automated stories use isolated workspaces and exact commits

- **Where:** Implementation › Building › Automated: wave setup and
  verify-story.
- **Observation:** Each story receives its own branch and worktree.
  `verify-story` checks the reported commit SHA before later gates trust it.
- **Why it matters:** Parallel agents cannot silently overwrite one another,
  and a completion claim points to an exact change.
- **Keep by:** Every automated change stays isolated until its commit and gate
  results have been checked.

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
- **Suggestion:** Keep human stops for product intent, irreversible
  architecture, accepted residual risk, and the final change. Batch or sample
  intermediate artifact approvals.

### BAD-03: Small changes have no fast lane

- **Where:** whole board.
- **Observation:** The board shows one path for every change. "Architecture
  change?" lets a change skip one block, but specification and planning look
  mandatory.
- **Cost:** A one-file bug fix pays the full ceremony of a feature.
- **Suggestion:** Classify each change before specification work. Use at least
  three paths: small reversible work, normal feature work, and high-risk work.
  Show the path a one-file fix takes.

### BAD-04: Review loops have no cap

- **Where:** Proposal › Review and acceptance; Specification › Review;
  Architecture › Review; Reconciliation › Alignment; Reconciliation › QA.
- **Observation:** Each loop returns with "re-review" and has no iteration
  limit. Only the gate-check loop has a cap.
- **Cost:** Tokens and time, mostly in late passes whose findings are edge
  cases that an earlier fix created.
- **Suggestion:** Give each review loop a cap and an escalation, as the
  gate-check loop has.
- **Proposals:** [finding-classification.md](../../docs/proposals/finding-classification.md)
  (accepted) decides which finding blocks. A rule computes each finding's
  severity, only a `critical` or `major` defect or risk blocks, a `minor`
  finding becomes a register row, and only the human overrides a blocking
  finding. [review-loop-cap.md](../../docs/proposals/review-loop-cap.md) (open)
  stops every review loop after three passes. If a blocking finding is still
  open, the human chooses: fix it, override it, or grant more passes.

### BAD-05: The same diff gets two Fagan reviews

- **Where:** Reconciliation › Code review (code-review agent, fagan-review);
  Reconciliation › QA (Fagan and security review).
- **Observation:** The code-review agent runs fagan-review on the diff. Then
  the QA agent runs a Fagan review again.
- **Cost:** A second review pass whose added value is not known.
- **Suggestion:** Measure the unique defect classes and findings from each
  pass. Merge the reviews when the second pass adds no distinct evidence.

### BAD-06: The board shows no cost

- **Where:** whole board.
- **Observation:** The board names a model tier only at "Escalate to next
  tier". It shows no tier, token budget, or time per step.
- **Cost:** A practitioner cannot see where the tokens and the time go.
- **Suggestion:** Add the model tier per agent step, and later measured cost
  per phase from usage capture.

### BAD-07: The boundary after the merge into dev is unclear

- **Where:** Reconciliation › Close the feature.
- **Observation:** The last delivery step merges the feature into `dev`. The
  board does not say whether build, release, deployment, observation, rollback,
  and incident feedback are absent or outside the Factory.
- **Cost:** A lead cannot tell whether the map is incomplete or the Factory's
  responsibility ends at `dev`.
- **Suggestion:** Draw and name the Factory boundary. Add a delivery and
  operation phase only if those responsibilities belong inside it.

### BAD-08: Security arrives after implementation

- **Where:** Reconciliation › QA › Fagan and security review.
- **Observation:** The explicit security review runs after code and
  reconciliation. Earlier stages do not show data classification, threat
  analysis, secret handling, dependency trust, or agent tool permissions.
- **Cost:** A late review can discover a design-level security problem after
  specification, architecture, and implementation have finished.
- **Suggestion:** Add a small security screen during change classification.
  Keep the late review for code-level findings. Require deeper analysis for
  high-risk changes.

### BAD-09: Artifact production does not name the later decision

- **Where:** Artifacts column and all authoring clusters.
- **Observation:** The board names the artifact produced by each step, but it
  does not consistently name the later decision or gate that consumes it.
- **Cost:** A document can survive because the process produces it, not because
  another step needs its information.
- **Suggestion:** Give every artifact a named consumer and decision. Remove an
  artifact when no later step would fail or lose information without it.

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
  mutation testing on that branch. Then it hands the branch back as done. The
  `story-done-gate` hook reruns `story-gates` on the closing commit and refuses
  `done` while a gate fails or a blocking finding for the story is open. The
  automated gate-check loop calls the same `story-gates` script. The proposal
  records this as DEC-04 to DEC-07, DEC-13, and DEC-14. The hook reruns the
  gates because an untracked pass marker can be forged.
  [gate-evidence.md](../../docs/proposals/gate-evidence.md) (draft) takes up
  that fault for every gate receipt.

### FAULT-03: Nobody owns the merge into dev

- **Where:** Reconciliation › Close the feature › Merge feature into dev.
- **Observation:** The board marks "No defined owner for this merge" as a gap.
- **Failure case:** A feature passes reconciliation and QA. No agent and no
  playbook step merges it into dev, so the finished work can sit on its branch
  with no next step.
- **Evidence:** Board gap shape only. No playbook reference was checked.
- **Fix direction:** Name an owner for the merge, and state the gate it runs:
  premerge-check and the full test suite.

## Recommended target shape

Keep one short backbone for every change:

1. Set the intent, observable result, and risk class.
2. Load the relevant project context.
3. Define a test or another executable acceptance check.
4. Implement the change in an isolated workspace.
5. Run the deterministic gates required by the risk class.
6. Add an independent review when the risk class requires one.
7. Let a named owner merge, release, and deploy the change.
8. Observe production and return findings to the specification or backlog.

Proposal work, full specification, ATAM, Pugh matrices, and full reconciliation
extend this backbone when risk warrants their cost. They are not the default
for every change.

Apply changes in this order:

1. Give manual mode the same quality outcomes as automated mode.
2. Define an owner and terminal state for every story and merge path.
3. Add change classification and a fast lane for reversible work.
4. Add delivery, operation, rollback, and production feedback.
5. Split the board into an overview, executable runbooks, and an artifact map.

Use these removal tests whenever the process grows:

- An artifact stays only when a named consumer uses it for a named decision.
- A review stays only when it owns a distinct defect class or finds unique
  defects.
- A gate stays only when it checks an observable contract and can block work.
- A human stop stays only for intent, irreversibility, or accepted risk.
- An optional phase runs only when the change's risk class triggers it.
