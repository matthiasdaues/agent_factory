---
type: atam-review
title: ATAM review of the CRAP gate setup architecture
date: 2026-11-21
status: pass
reviewer: architecture-review-agent
findings_filed: 3
story: crap-gate-setup
scope: Uncommitted changes on dev — architecture.dsl (gate-setup-proof, Measuring Commands, the view CrapGate, the dynamic views GateCheckStep and PremergeStoryCheck), arc42 chapters 5, 6, 8, and 9, the fourth Amended section of ADR-0003, and the exports CrapGate.svg and CrapGate-key.svg, measured against the accepted proposal docs/proposals/crap-gate-setup.md and the reviewed spec
---

# ATAM review of the CRAP gate setup architecture

The architecture follows the proposal and the spec in every part this review checked. One risk blocks planning. Nothing in the architecture stops two runs of a service-backed measure from using one Compose stack at the same time, so the merge check can judge code that the stack does not serve (ATAM-0027). One `minor` document defect remains: chapter 5.12 and QS-25 do not name the exceptions register that the guard now protects (ATAM-0028). Eight notes follow, among them the answers to the three questions of the brief.

The stakeholder delegated the decisions to the parent session. The section [Decisions](#decisions) records them, and the proposal's Appendix holds them as DEC-43 to DEC-46.

## Reviewed architecture

- `docs/spec/architecture.dsl`: the new component `gate-setup-proof`, the new container Measuring Commands with the style `Project-owned`, the changed descriptions of `crap-score`, `guard-human-fields`, and `test-strategy-agent`, the new and changed relationships, the component view CrapGate, and the dynamic views GateCheckStep and PremergeStoryCheck.
- arc42 5.2, 5.2.3 with the new section "The CRAP gate", 5.13, 6.4, 6.24, 6.24.1, 8.3, 8.6, 8.7 with the new section "Gate Exit Codes", and 9.
- The fourth `## Amended` section of ADR-0003, dated 2026-11-21.
- The exports `docs/assets/images/CrapGate.svg` and `CrapGate-key.svg`.
- The spec as reference: BR-027, BR-091, BR-092, BR-124, BR-127 to BR-139, the contracts of `crap-score` and `gate-setup-proof`, the Ledger Entry Lifecycle, and `crap-gate-setup.feature`.

`arch-lint --docs-dir docs/arc42` found 0 errors, 1 warning, and 0 info, and exited `0`. `structurizr validate` exited `0`.

The SVG export renders in headless Chromium. ImageMagick draws an empty page, because it does not read the JointJS markup. The PNG renders lie in the session scratchpad, not in the repository. Every box and every label of CrapGate is legible at full size. Notes N3 and N4 describe what the render shows.

## Deterministic findings

| Check      | Severity | Verdict   | Reason                                                                                                                                                                                                                                                           |
| ---------- | -------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ARCH-PARSE | warning  | Dismissed | The change did not cause it. `arch-lint` on an export of `HEAD` gives the same warning. The DSL and chapter 5 describe ports as prose, not as a component named "Ports" or a parseable list. The review of 2026-11-18 dismissed the warning for the same reason. |

## Rules check

No mismatch. `docs/spec/dependency-rules.dsl` holds two rules, `factory must_not_depend_on usage` and the reverse. The change adds no rule. No new relationship crosses between Factory Flow Control and Usage Analysis.

## Quality scenarios

1. QS-28: A failing gate merges on neither way of driving a run (priority 1).
2. QS-30: A new session continues an interrupted run (priority 1). Its stimulus is a session that dies while `premerge-check` runs `crap-score`.
3. QS-6: Deterministic validation (priority 2). Its stimulus names the CRAP threshold.
4. QS-25: No agent writes a human field (priority 1). The guard now also refuses every write to the exceptions register.
5. QS-2: Human authority over agent selection (priority 1). A `blocked` unit of work waits for a person, and only a person writes the exceptions register.
6. QS-24: A critical finding stops every dispatch and merge (priority 1), for the new subcommand `dispatch resume-gates`.

## Findings

### QS-28: A failing gate merges on neither way

- **Approach.** `premerge-check` runs the `ready` commands and then `crap-score --base <target>` in its temporary worktree at the branch head. Each measuring command measures the code of the folder it runs in (BR-130). The verdict is the exit code (ADR-0003, fourth amendment).
- **Sensitivity point.** For a measure that tests against a service, the verdict depends on which folder the service runs at that moment. The proof checks this once, alone, in its own worktree ("Sees the folder", DEC-06).
- **Risk, ATAM-0027.** In an orchestrated run, stories run in parallel, and each gate-check step starts `crap-score` as a background job (BR-134). Take ST-0350 at its merge check and ST-0351 in its gate-check step, both with the measure `backend` against one Compose stack. Each measuring command makes the stack serve its own folder, so one of the two test runs hits the code of the other folder. Coverage then belongs to the wrong tree. That can fail a sound function and cost an attempt. It can also pass a function that has no test at the head of `story/ST-0350`, so a failing function merges. No document says whether the two runs can overlap, or whether a measure must isolate its service per folder. The same overlap arises under QS-30: a new session reruns the gate-check step while the background job of the dead session still runs.
- **Non-risk.** A measure without a service, such as the Python measure of this repository, runs coverage inside its own folder. Two such runs do not touch each other. Assumption: the measuring command writes its coverage data inside the folder it runs in.

### QS-30: A new session continues an interrupted run

- **Approach.** `premerge-check` removes a leftover worktree at its own path before it adds a new one (BR-123). A refused merge keeps the entry `dispatched`, and exit `3` sets it `blocked`. Both states lie in the ledger.
- **Non-risk.** A second `merge-story` after a session died during `crap-score` reaches the same result as an uninterrupted call. Assumptions: the measuring command points its service at the new worktree on every run, and `crap-score` writes no report on exit `2` and leaves the earlier report in place (DEC-17).
- **Sensitivity point.** A background job of `crap-score` outlives the session that started it. The overlap with a new run belongs to ATAM-0027.

### QS-6: Deterministic validation

- **Approach.** The gate keeps exit `1` for a failing function, and the stimulus and the response measure of QS-6 still hold. Exit `2` adds a third answer that starts no developer agent (8.7, DEC-03).
- **Tradeoff point.** The ADR-0003 amendment makes the Factory read rows that the project writes. The gate then works in every language, and the row format becomes a contract with every project that enables the gate. The amendment names both sides.
- **Sensitivity point.** The `ready` command is optional (BR-129). A measure that needs a service and has no `ready` command lets `premerge-check` run the test suite against a stopped stack. The suite fails, `premerge-check` exits `1`, and the unit of work pays an attempt for a fault in the setup. That is the case BR-136 sets out to prevent. `setup-crap-score` proposes the `ready` command (BR-139 step 4), and the proof does not check that a service-backed measure has one.
- **Non-risk.** A measuring command that hides a failed test run fails "Reports a gap" at setup. Assumption: nobody changes the measuring command after the proof. The amendment names this limit as a consequence.

### QS-25: No agent writes a human field

- **Approach.** BR-092 makes the whole file `docs/findings/exceptions.md` belong to the stakeholder. The DSL description of `guard-human-fields` refuses every call that writes it.
- **Defect, ATAM-0028.** Chapter 5.12 describes `guard-human-fields` with the three guarded areas from before the change and leaves out the exceptions register. QS-25 names finding files, register files, and the Appendix of a proposal, and no file whose every write is refused. ADR-0035 does not name the register either.
- **Non-risk.** The guard already covers `docs/findings/*.md` in every CLI, so the exceptions register needs no new hook entry. Assumption: the guard tells the register from a finding file by its name.

### QS-2: Human authority

- **Approach.** On exit `2`, the unit of work stops as `blocked` and waits for the User. Only the User restarts it, through the implementation agent and `dispatch resume-gates` (DEC-07). Only the stakeholder writes the exceptions register, and `crap-score` reads the register from `dev` only (DEC-25).
- **Tradeoff point.** A story branch cannot carry its own exception. The User must commit the row on `dev` before the merge check passes. The design chooses human control over a single-branch workflow.
- **Non-risk.** An agent cannot accept its own failing function. Assumption: the guard of QS-25 runs in every CLI that the project uses.

### QS-24: A critical finding stops every dispatch and merge

- **Non-risk.** During a stop, `merge-story` is refused, so a unit of work that `resume-gates` returns to `dispatched` still cannot merge. The response measure of QS-24 holds.
- **Note N7.** BR-091 lists the subcommands that a stop refuses and the ones it allows. `resume-gates` stands in neither list. An implementer has to guess whether a stop refuses it.

### Agreement of DSL, chapters, and views

The DSL, the tables of 5.2.3 and 5.13, the Mermaid sequences of 6.4 and 6.24, and the table of 8.7 agree step for step. The step numbers of PremergeStoryCheck match the DSL view after the insert of the `ready` step. The links to `#gate-exit-codes`, `#87-semantic-quality-gates`, and the `crap-score` contract resolve.

### YAGNI pass

No artificial complexity. `gate-setup-proof` is a separate component because it has its own call, its own worktree, and its own exit codes. The container Measuring Commands names a real boundary: the code that the project owns and the Factory only calls. `measured_minutes` is stored and not read by `crap-score`. DEC-19 decided this, so it is no finding.

## Notes

- **N1, ARCH-PARSE.** The change did not cause the warning. See the table of deterministic findings.
- **N2, the dynamic view for exit 2.** No quality scenario needs the view. No scenario in chapter 10 covers the path of a gate that cannot measure. QS-6 measures exit `1`, and QS-28 measures a failing gate. The path is complete in prose: 6.4, the table in 8.7, the refusal table in 6.24.1, and the `else` branch of the Mermaid sequence in 6.24. DEC-03, a gate that cannot measure costs no attempt, is the central promise of the feature, but no scenario measures it. Next, the stakeholder decides whether chapter 10 gets that scenario. With the scenario, the architecture agent adds a dynamic view: `crap-score` exits `2`, `mark-blocked`, `resume-gates`, and the gate-check step again. The review of 2026-11-18 treated the missing QS-30 the same way.
- **N3, the render of CrapGate.** Every element and every label is legible at full size. Several edges cross labels: the label "Runs the proof in setup-crap-score steps 5 and 7" and the `ready` label of `premerge-check` are crossed by two edges, and the label of `dispatch init` sits across the boundary of the software system. A reader finds each label on a second look.
- **N4, Measuring Commands in the Factory boundary.** The render draws Measuring Commands inside the boundary "Factory Flow Control", although the project owns the commands and they refer to nothing under `.agent-factory/`. The dashed grey style and the key "Container, Project-owned" mark the difference. Project Filesystem sits in the same software system, so the model is consistent with itself.
- **N5, gate-setup-proof in the table of gates.** 5.2 says "Four gates enforce semantic code quality", and the table of 5.2.3 now holds a fifth row, `gate-setup-proof`, which is no gate. A sentence that names the proof as the setup check of `crap-score` would remove the doubt.
- **N6, the worktree of the proof.** The contract names no path for the temporary worktree of `gate-setup-proof` and no removal of a worktree that a crash leaves. A person runs the setup and sees the crash, and no scenario covers the setup. `premerge-check` solved the same case with BR-123.
- **N7, `resume-gates` during a stop.** See QS-24. The fix belongs in BR-091, which the domain-modeling agent owns.
- **N8, BR-024 during setup.** The fourth amendment of ADR-0003 says "The implementation agent runs `crap-score`". The test-strategy agent also runs `crap-score --all` and `gate-setup-proof` during setup. BR-139 makes the agent try each candidate tool on a real file, and a bare `pytest --cov` falls under the deny patterns of BR-024. The agent can run the trial through a measuring command, which no deny pattern names.

## Filed findings

| ID        | Class        | Category | Type         | Basis                                                                                   | Severity | Scenario | Owner              |
| --------- | ------------ | -------- | ------------ | --------------------------------------------------------------------------------------- | -------- | -------- | ------------------ |
| ATAM-0027 | architecture | risk     | `risk`       | `importance: high`, `exposure: uncertain`, `in_use: false`                              | major    | QS-28    | architecture-agent |
| ATAM-0028 | document     | defect   | `incomplete` | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true` | minor    | QS-25    | architecture-agent |

**ATAM-0027, why this severity.** QS-28 has priority 1. Whether two runs of one service-backed measure overlap depends on the scheduling of gate-check steps and merge checks, and no document states it. No code is built from the design yet.

**ATAM-0028, why this severity.** BR-092 and the DSL state the rule, and chapter 5.12 and QS-25 are side texts that leave out one case. The hook follows BR-092, so an implementer builds the right guard (no to fails_purpose). A reader of 5.12 or QS-25 learns of the register only from the DSL or from BR-092. No story encodes the chapter text.

## Risk summary

| ID        | Severity | Scenario | Risk                                                                                                | Mitigation                                                                                                                                                                                       |
| --------- | -------- | -------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ATAM-0027 | major    | QS-28    | Two runs of one service-backed measure share a service, so the merge check can judge the wrong code | Decide one of two rules and write it into BR-129 or BR-130 and 8.7: `crap-score` holds a lock per measure across its `ready` and measuring command, or a measure isolates its service per folder |
| ATAM-0028 | minor    | QS-25    | 5.12, QS-25, and ADR-0035 omit the exceptions register                                              | Name `docs/findings/exceptions.md` in the guard row of 5.12 and in the stimulus of QS-25                                                                                                         |

## Tradeoff summary

| Tradeoff                                                          | Side chosen                        | Cost                                                                                |
| ----------------------------------------------------------------- | ---------------------------------- | ----------------------------------------------------------------------------------- |
| Exit code only, or rows in a format the Factory defines           | Rows (ADR-0003, DEC-02)            | The row format binds every project that enables the gate                            |
| A cannot-measure exit that blocks, or a failure that counts       | Block (DEC-03)                     | A person must act before the unit of work goes on                                   |
| `ready` commands before the suite and at `init`, or none          | Before (BR-136, BR-137)            | Each merge check and each run start take the time of every `ready` command          |
| Check the measuring command once at setup, or at every run        | At setup (BR-138)                  | A later change to the command goes unchecked until someone runs the proof again     |
| Exceptions read from `dev`, or from the branch under review       | `dev` (DEC-25)                     | A story cannot carry its own exception, and a project without `dev` has no register |
| Gate in the gate-check step and at the merge, or in a commit hook | Gate-check step and merge (DEC-05) | The developer agent commits while the gate cannot measure                           |
| Background job in the gate-check step, or a foreground call       | Background job (BR-134)            | The job outlives a dead session, which ATAM-0027 covers                             |

## Decisions

The parent session decided each candidate and note on 2026-11-21:

| Item      | Decision                                                                                                                                                                                                                                                                       | Next step                                                                         |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------- |
| ATAM-0027 | DEC-43: `crap-score` holds an exclusive lock per measure that has `ready` commands. The lock lies under the git common directory and is held from the `ready` commands through the measuring command. `crap-score` waits for it within the time limit and exits `2` on timeout | Finding file `docs/findings/ATAM-0027.md`; the architecture agent writes the lock |
| ATAM-0028 | Filed as `minor`                                                                                                                                                                                                                                                               | Register file `docs/findings/register/document/ATAM-0028.json`                    |
| N2        | DEC-45: chapter 10 gets a quality scenario for a gate that cannot measure, and no dynamic view                                                                                                                                                                                 | The architecture agent adds the scenario                                          |
| N3, N4    | They stay as they are. Diagrams get no hand-positioning, and the model is consistent with Project Filesystem                                                                                                                                                                   | None                                                                              |
| N5, N8    | Wording fixes                                                                                                                                                                                                                                                                  | The architecture agent fixes 5.2 and the fourth amendment of ADR-0003             |
| N6        | DEC-46: `gate-setup-proof` uses a fixed worktree path under `.current-work/gate-setup-proof/` and removes a leftover worktree first, as BR-123 does                                                                                                                            | The domain-modeling agent and the architecture agent                              |
| N7        | DEC-44: a stop refuses `resume-gates`, because the unit of work goes on to the merge                                                                                                                                                                                           | The domain-modeling agent adds `resume-gates` to BR-091                           |

## Readiness

The architecture is not ready for planning while ATAM-0027 is open. Next, the architecture agent writes DEC-43 to DEC-46 and the wording fixes into the architecture and resolves ATAM-0027 and ATAM-0028. A second pass of this review then checks the fixes.

## Pass 2

Pass 2 checks the fixes of ATAM-0027 and ATAM-0028 and the decisions DEC-43 to DEC-46. It is a narrow check of the text changed since pass 1, not a new review pass. `arch-lint --docs-dir docs/arc42` and `structurizr validate` ran again. `arch-lint` found 0 errors and the dismissed ARCH-PARSE warning and exited `0`, and `structurizr validate` exited `0`.

| ID        | Status   | Evidence                                                                                                                                                                                                                                                                                                                      |
| --------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ATAM-0027 | resolved | BR-129, the `crap-score` contract, 8.7, and the DSL relationship from `crap-score` to git hold the lock of DEC-43: one lock file per measure with a `ready` command under the git common directory, held from the `ready` command through the measuring command, waited for within `timeout_minutes`, and exit `2` on timeout |
| ATAM-0028 | resolved | The guard row of 5.12 and the stimulus of QS-25 name `docs/findings/exceptions.md`. ADR-0035 is unchanged. This pass drops that part of the fix, because ADR-0035 records the decision to guard every CLI, and BR-092 and the DSL hold the list of guarded files                                                              |

| Note | Status | Evidence                                                                                                                                                                                              |
| ---- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| N2   | closed | QS-31 "A gate that cannot measure costs no attempt" stands in chapter 10 with priority 2 and a measurable response: one counted attempt before and after, the same branch head, on both ways (DEC-45) |
| N5   | closed | 5.2 and 5.2.3 call `gate-setup-proof` the setup check of `crap-score`, not a gate                                                                                                                     |
| N6   | closed | BR-138 and the contract give the proof the fixed path `.current-work/gate-setup-proof/worktree` and remove a leftover worktree first, as BR-123 does (DEC-46)                                         |
| N7   | closed | BR-091 and the `resume-gates` contract refuse `resume-gates` during a stop (DEC-44)                                                                                                                   |
| N8   | closed | The fourth amendment of ADR-0003 names the setup runs of the test-strategy agent and its trial of candidate tools through a measuring command                                                         |
| N3   | kept   | Decided: no hand-positioning                                                                                                                                                                          |
| N4   | kept   | Decided: the model is consistent with Project Filesystem                                                                                                                                              |

### New point of this pass

One new point is a risk that a planner would hit. The fix of ATAM-0027 created it.

**Candidate A3: a run that dies can leave the lock behind.** BR-129 and the contract say "The lock is the file `crap-score/<measure>.lock`", and no text says what ends the lock. Take the stimulus of QS-30: the session dies while `premerge-check` runs `crap-score` for ST-0350. If the implementer builds the lock as a file whose existence locks, the file stays. The second `merge-story` waits for the whole `timeout_minutes`, `crap-score` exits `2`, and ST-0350 becomes `blocked` until a person deletes the file. QS-30 requires that nobody removes anything by hand. A lock that the operating system holds for the process, such as `flock`, ends with the process and leaves nothing behind.

| Candidate | Class        | Category | Type   | Basis                                                      | Severity | Scenario | Owner              |
| --------- | ------------ | -------- | ------ | ---------------------------------------------------------- | -------- | -------- | ------------------ |
| A3        | architecture | risk     | `risk` | `importance: high`, `exposure: uncertain`, `in_use: false` | major    | QS-30    | architecture-agent |

**A3, why this severity.** QS-30 has priority 1. Whether a dead run leaves the lock depends on how the lock is built, and no document states it. No code is built yet.

**Fix.** Add one sentence to BR-129, the contract, and 8.7: the lock is an operating-system lock on the file, such as `flock`, which ends when the process that holds it ends, so a run that dies leaves no lock. This candidate is not filed. The parent session decides, as in pass 1.

### Status of pass 2

ATAM-0027 and ATAM-0028 are resolved, and every note is closed or kept by decision. The report keeps the status `defects` while candidate A3 is open. When the parent session accepts the one-sentence fix and the text carries it, the architecture is ready for planning.

## Pass 3

Pass 3 files candidate A3 as ATAM-0029 and checks only the sentences of DEC-47.

| ID        | Status   | Evidence                                                                                                                                                                                                                                                                                    |
| --------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ATAM-0029 | resolved | BR-129, the `crap-score` contract, 8.7, and the DSL relationship from `crap-score` to git define the lock as an operating-system file lock, such as `flock`, which ends with its process, and the file may stay. A Scenario and the QA row CG-04-IT-16 check the next run after a `SIGKILL` |

The report status is `pass`. ATAM-0027, ATAM-0028, and ATAM-0029 are resolved, and no defect or risk blocks planning. Next, run the planning agent.
