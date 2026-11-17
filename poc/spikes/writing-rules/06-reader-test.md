# Reader test: run lifecycle

This test checks whether a reader of one version of the run-lifecycle proposal can answer what the user decided. The answer key comes from `input/conversation-run-lifecycle.md`. Each source quotes the user's own words at the final decision. Where the user answered a letter, the source names the option the letter chose.

A reader serves one of two people. The builder implements the run. The approver decides whether the proposal is accepted.

The kind marks a question as `decided`, `override` (an earlier decision was replaced), or `open` (not decided, or deferred).

## Questions for the builder

### Q01

- Question: When a human drives a run by hand, from which branch is each story branch cut?
- Answer key: From the feature branch of the run, not from `dev`.
- Variants: "from the feature branch, as in an orchestrated run".
- Source: 2026-11-15T20:13, "yes. We would have to provide the user with thorough guidance, but yes." (accepts one frame for both ways, with story branches cut from the feature branch)
- Reader: builder
- Kind: decided

### Q02

- Question: When does `dispatch init` refuse to start a run because another run exists?
- Answer key: When the same feature branch already has a ledger, or when a by-hand run starts while another by-hand run is active.
- Variants: "one run per feature branch, and only one by-hand run at a time".
- Source: 2026-11-17T08:41, "yes." (accepts: "`init` refuses only when the same feature branch already has a ledger, or when you start a run by hand while another run by hand is active")
- Reader: builder
- Kind: decided

### Q03

- Question: Which step sets a story's status to `done`, and when?
- Answer key: `dispatch merge-story` writes `done` into the merge commit, on both ways. The developer agent never sets `done`.
- Variants: "the merge into the feature branch sets done".
- Source: 2026-11-15T21:14, "A" (option A: "the merge sets `done`, on both ways")
- Reader: builder
- Kind: decided

### Q04

- Question: In a by-hand run, who runs the command that starts a story?
- Answer key: The implementation agent runs `dispatch prepare-story`, after the human says go.
- Variants: none.
- Source: 2026-11-17T07:19, "'who starts a story' -> also in manual mode the implementation agent actually starts a story."
- Reader: builder
- Kind: override. At 2026-11-15T21:46 the human ran this command and the guardrail refused it to agents.

### Q05

- Question: In a by-hand run, who runs `dispatch merge-story` to merge a story into the feature branch?
- Answer key: The implementation agent, after the human has seen the merge-check output and said go.
- Variants: none.
- Source: 2026-11-17T07:20, "1. Yes" (to option A: "you say go, and the agent runs `merge-story` as well"). The assistant confirmed this reading at 08:36 and the user did not object.
- Reader: builder
- Kind: override. At 2026-11-15T21:14 and 21:46 the human ran `dispatch merge-story`.

### Q06

- Question: Which commands does the git guardrail refuse to agents because of this design, and in which runs?
- Answer key: Only `dispatch return-story` and `dispatch close --drop`, in every run on both ways, because both destroy work.
- Variants: "only the commands that destroy work: return-story and close --drop".
- Source: 2026-11-16T22:40, "yes." (accepts the smaller set: "In every run, refuse agents `dispatch return-story` and `dispatch close --drop`")
- Reader: builder
- Kind: override. At 2026-11-15T21:46 a by-hand run refused agents `merge-story`, `prepare-story` and the return.

### Q07

- Question: Does the design rely on Claude Code's "ask" hook answer, which shows the human a command and waits for approval?
- Answer key: No. Every mechanism must work in all five supported agent tools, so the design rests on refusing commands, not on "ask".
- Variants: "no, because ask exists only in Claude Code".
- Source: 2026-11-15T21:44, "This must either work for all CLIs or we must design it differently." Final choice at 21:46, "A".
- Reader: builder
- Kind: override. At 2026-11-15T21:42 the user had accepted the "ask" mechanism.

### Q08

- Question: How is the git guardrail implemented across the five agent tools?
- Answer key: One shell script that all five tools call. pi's TypeScript copy becomes a thin wrapper. OpenCode's plugin calls the same script, checked in a real OpenCode session.
- Variants: "one script, as guard-human-fields works".
- Source: 2026-11-16T22:46, "yes." (accepts "one guard script that all five tools call")
- Reader: builder
- Kind: decided

### Q09

- Question: By default, how many developer-agent attempts does a story get when its gates fail?
- Answer key: Three on the story's model tier (first attempt plus two retries), then three on the stronger tier. Six in all.
- Variants: "3 + 3".
- Source: 2026-11-17T19:06, "We have first attempt and two retries, three runs each on indicated and escalated tier."
- Reader: builder
- Kind: decided

### Q10

- Question: In which file and under which keys are those attempt counts configured?
- Answer key: In `docs/testing.yaml`, as `gates.attempts` and `gates.attempts_escalated`, each with default 3.
- Variants: none.
- Source: 2026-11-17T19:13, "1. yes" (accepts the names `gates.attempts` and `gates.attempts_escalated`). The file was decided at 2026-11-16T15:29, "A. Testing yaml seems a good fit."
- Reader: builder
- Kind: override. At 2026-11-16T15:29 the keys were `gates.fix_rounds` and `gates.fix_rounds_escalated`.

### Q11

- Question: Two stories in one wave both use up their attempts on their own tier. Does the second story also get its escalated attempts?
- Answer key: Yes. The limit of one escalation per wave is dropped.
- Variants: "every story gets its escalated attempts".
- Source: 2026-11-17T19:13, "2. drop it."
- Reader: builder
- Kind: decided

### Q12

- Question: A story merges into the feature branch, and then the full test suite fails. What happens to the branch and the story?
- Answer key: The script moves the feature branch back to the commit before the merge. No revert commit is made. The story becomes `blocked`.
- Variants: "reset to the pre-merge commit".
- Source: 2026-11-15T21:20, "A"
- Reader: builder
- Kind: decided

### Q13

- Question: When may wave 2 of a run start, and what counts as a wave in a by-hand run?
- Answer key: Only after `dispatch close-wave 1` has succeeded. By hand, each story is a wave of its own.
- Variants: none.
- Source: 2026-11-15T21:23, "A"
- Reader: builder
- Kind: decided

### Q14

- Question: When do the sessions that fix rows of a story's spec-feedback report run?
- Answer key: At the close of the wave, not after each story merge. The wave close waits for their commits and checks that no row is open.
- Variants: none.
- Source: 2026-11-15T21:39, "BZ" (read by the assistant as option B, with no objection from the user)
- Reader: builder
- Kind: decided

### Q15

- Question: Who runs the gates in a by-hand run?
- Answer key: The implementation agent, as in an orchestrated run. The developer agent never runs a gate script.
- Variants: none.
- Source: 2026-11-15T21:25, "A"
- Reader: builder
- Kind: decided

### Q16

- Question: At a story merge, does the merge check reuse the coverage file from the earlier gate run?
- Answer key: No. It reruns each gate's full measuring command, tests included.
- Variants: "fresh test run, no stored result".
- Source: 2026-11-16T15:17, "A"
- Reader: builder
- Kind: decided

### Q17

- Question: At the gate rerun before a story merge, what happens to untracked files in the story's checkout?
- Answer key: `premerge-check` stashes them under a telling name, runs the gates, and puts them back. If they cannot be put back, the stash stays and is named.
- Variants: none.
- Source: 2026-11-16T17:46, "Both points." The idea came from the user at 15:32: "put untracked files into a stash with a telling name".
- Reader: builder
- Kind: override. At 2026-11-16T15:19 the user said "Untracked files will be ignored."

### Q18

- Question: Does an open minor finding block a story merge?
- Answer key: No. Only a finding with category `defect` or `risk` and severity `critical` or `major` blocks, as the finding-classification rule defines.
- Variants: "minor findings never block".
- Source: 2026-11-16T15:21, "No. We take B. Minor findings do not block by definition." At 15:22 the user had the rule cited from the review scoring: "Minor findings do not block should be specified there."
- Reader: builder
- Kind: override. At 2026-11-16T15:20 the user answered "A", under which a minor finding blocked.

### Q19

- Question: What is the file name of a story's code-review report?
- Answer key: `docs/reviews/code-review-<story-id>-YYYY-MM-DD.md`, with `-2` for a second review of that story on the same day.
- Variants: the end-of-feature review uses the feature branch name with the slash replaced by a hyphen.
- Source: 2026-11-16T15:25, "A"
- Reader: builder
- Kind: decided

### Q20

- Question: A story cannot be fixed and goes back to the backlog. Which status does it get?
- Answer key: `pending`, in the ledger and in the backlog. No new state such as `returned` is added.
- Variants: "open" (the user's word, read as `pending`).
- Source: 2026-11-16T22:52, "A. But we do not need a new state 'returned'. It returns to 'open'." Confirmed at 2026-11-17T07:10, "yes".
- Reader: builder
- Kind: decided

### Q21

- Question: After a story returns to the backlog, which other stories of the run may still start?
- Answer key: Only stories that do not depend on it. Stories that depend on it, directly or through a chain, must not start.
- Variants: none.
- Source: 2026-11-16T22:55, "All runs depending on this story MUST NOT be dispatched. Only work that is independent of this story can continue."
- Reader: builder
- Kind: decided

### Q22

- Question: A story in the run depends on a story that is not part of the run. How is that dependency checked?
- Answer key: Once, at `dispatch init`, against the backlog. `init` refuses the story if the dependency is not done. During the run, only ledger states count.
- Variants: none.
- Source: 2026-11-17T08:37, "yes." after the user asked at 08:36, "Why do we have to look up stories in the mid of the run?"
- Reader: builder
- Kind: override. At 2026-11-17T07:10 the user accepted that a dependency outside the ledger counts as not done during the run.

### Q23

- Question: Which story states let `dispatch close` and the check before the merge into `dev` pass, and which make them refuse?
- Answer key: `done` and `pending` pass. `failed` and `blocked` make them refuse.
- Variants: none.
- Source: 2026-11-17T07:10, "yes"
- Reader: builder
- Kind: decided

### Q24

- Question: A story is `failed`, and its root cause can be fixed. How does it continue?
- Answer key: The human fixes the cause and tells the agent to continue. The agent runs `re-dispatch`, and the story carries on in the same run.
- Variants: none.
- Source: 2026-11-16T22:54, "the story run would be sent off by the operator's intervention and prompt to continue the run."
- Reader: builder
- Kind: decided

### Q25

- Question: Which ledger fields are dropped, and how does a check tell that a run is active?
- Answer key: `gate_results` and `closed` are dropped. A run is active while its feature branch has a ledger.
- Variants: none.
- Source: 2026-11-15T21:40, "A" (option A: "every ledger field must have a command that reads it")
- Reader: builder
- Kind: decided

### Q26

- Question: How does the check before the merge into `dev` know that a finding from the end-of-feature review belongs to this run?
- Answer key: The finding carries a new field `run` with the feature branch name. Findings whose `story` names a story of the run count too.
- Variants: none.
- Source: 2026-11-17T08:42, "A"
- Reader: builder
- Kind: decided

### Q27

- Question: How is a blocking finding from the end-of-feature review or QA fixed inside the run?
- Answer key: The finding itself is the unit of work. `dispatch add <id>` adds it as a new wave, it runs on `story/<id>`, and `merge-story` sets `status: resolved`.
- Variants: "no separate fix story is written".
- Source: 2026-11-17T08:56, "Yes." after the user asked at 08:55, "Why can't the finding itself be the 'story'?"
- Reader: builder
- Kind: decided

### Q28

- Question: What does `dispatch close` remove, and does it keep a tracked record of the run?
- Answer key: Ledger, worktrees, gate results, markers, briefs and merged branches. No tracked record is written; git history and the story status hold the outcome.
- Variants: untracked files of each worktree go into named stashes first.
- Source: 2026-11-15T20:15, "A". Stash at close: 2026-11-16T17:46, "Both points."
- Reader: builder
- Kind: decided

### Q29

- Question: How are the old ledgers of this repository handled whose feature branch no longer exists?
- Answer key: `dispatch close --orphans` finds them, nested ones included. It removes those whose stories are all `done` and lists the rest. It ignores `mode`.
- Variants: none.
- Source: 2026-11-17T18:22, "yes."
- Reader: builder
- Kind: decided

### Q30

- Question: Does the new vocabulary also rename code identifiers, such as the ledger field `invocation_branch` and the mode value `automated`?
- Answer key: Yes. Code identifiers and error messages are renamed. Accepted ADRs, superseded proposals and file names keep their old terms.
- Variants: "`invocation_branch` becomes `feature_branch`, `automated` becomes `orchestrated`".
- Source: 2026-11-17T19:00, "B"
- Reader: builder
- Kind: decided

### Q31

- Question: A story's `quality-gates` field names one gate. Does it add to the gates that `docs/testing.yaml` enables, or replace them?
- Answer key: Not decided. The review raised it as minor finding 10, and the conversation ended before the user decided it.
- Variants: "open".
- Source: none. The finding was presented at 2026-11-16T18:08, and no user answer follows.
- Reader: builder
- Kind: open

## Questions for the approver

### Q32

- Question: Who merges a finished feature branch into `dev`?
- Answer key: The human, on both ways, after the check command passes. The agent runs the check and shows the result.
- Variants: none.
- Source: 2026-11-15T20:14, "B"
- Reader: approver
- Kind: decided

### Q33

- Question: Which work must be finished inside the run before the merge into `dev`, and what runs only after it?
- Answer key: Story work, gates, the end-of-feature code review and QA run inside the run. Reconciliation of the documents runs on `dev` after the merge.
- Variants: none.
- Source: 2026-11-15T21:31, "yes. Development -> Test -> Code Review -> CRAP -> Mutaiton Testing -> QA and their fixing loops belong inside one run."
- Reader: approver
- Kind: override. At 2026-11-15T21:29 the user chose "A", under which reconciliation also ran inside the run.

### Q34

- Question: After a run is closed, what is left for the human to handle?
- Answer key: Unmerged branches, which the human deletes with `git branch -D`, and the named stashes the close listed, from which the human keeps what is needed.
- Variants: none.
- Source: 2026-11-15T20:16, "A"; 2026-11-16T17:46, "Both points."
- Reader: approver
- Kind: decided

### Q35

- Question: In a by-hand run, what is the safeguard against an agent that merges a story too early?
- Answer key: The human, who watches each step and can undo a merge. The guard does not refuse merges.
- Variants: none.
- Source: 2026-11-16T22:39, "If I run it by hand, I'm there to watch what's happening, aren't I?" Accepted at 22:40, "yes."
- Reader: approver
- Kind: decided

### Q36

- Question: What extra cost does the gate rerun at each story merge bring?
- Answer key: A second test run per story, because the rerun runs each gate's full command with the tests.
- Variants: none.
- Source: 2026-11-16T15:17, "A" (the option stated "The cost is a second test run per story")
- Reader: approver
- Kind: decided

### Q37

- Question: Does the first release build the security scanner pre-commit hook and its configuration?
- Answer key: No. The hook and the scanner's configuration go to a separate setup proposal. This proposal keeps the scan only as a step of the story workflow.
- Variants: "deferred".
- Source: 2026-11-17T10:01, "A"
- Reader: approver
- Kind: override. At 2026-11-15T21:34 the user placed a scanner hook on every commit in this work: "A - the security scanning should be configurable per project and need."

### Q38

- Question: What is the effort estimate for building this proposal?
- Answer key: Not decided. The review noted that every estimate value is `unknown`, and the user never answered that note.
- Variants: "unknown", "open".
- Source: none. Review note 18, presented at 2026-11-16T18:08.
- Reader: approver
- Kind: open

### Q39

- Question: In a by-hand run, is there a rule that keeps the human's own unrelated untracked files in the primary checkout out of the merge-check stash?
- Answer key: Not decided. The review raised it as minor finding 12, and the conversation ended before the user decided it.
- Variants: "open".
- Source: none. The finding was presented at 2026-11-16T18:08, and no user answer follows.
- Reader: approver
- Kind: open

### Q40

- Question: If the backlog later lives in Jira, how does returning a story reach Jira?
- Answer key: Deferred to the Jira backlog proposal. This proposal says only that the return reaches the backlog.
- Variants: "out of scope", "left to `jira-backlog-projection.md`".
- Source: 2026-11-17T08:37, "yes." (accepts "I would leave that to the Jira proposal, and only state here that the return reaches the backlog.")
- Reader: approver
- Kind: open

## Method

The key comes only from user turns in the conversation. An assistant recommendation counts from the user turn that accepted it. The handoff and the two subagent reports served to locate decisions, not as answers.

These decisions were left out:

- The rule that documents follow the code where no design question lies behind a disagreement (21:27). It is a working rule, and a reader cannot answer it in one checkable phrase.
- The per-story and per-feature split of the steps, and the conditional move of mutation testing (21:33). The move depends on a trial, so the answer is not stable.
- The scope of a story merge (15:23), the `dependency-check` notice without a rules file (15:27), the uncommitted tracked-file refusal (15:19), the init worktree by hand (08:41), and the subcommand table with the removal of `mark-done` (07:16). They are settled, and they were cut to stay within 40 questions.
- The vocabulary table itself (21:48). It is a list, not one answer.
- Minor findings 9 to 16 and notes 17 to 19, except those used as open questions. The conversation ends at 19:13 on minor 8.

Five points could not be settled cleanly:

- "BZ" at 21:39 is read as B, as the assistant read it. The user did not object.
- "1. Yes" at 07:20 answers a question with two options. The assistant read it as A at 08:36, and the user did not object.
- The handoff says `0 escalated = no escalation`. No user turn says this, so the key does not use it.
- At 17:59 the user approved a lector fix that sends open QA findings at wave close to the test-strategy agent. Review minor 9 later challenged that routing, and the user did not decide it. No question asks about it.
- Who runs a finished `dispatch close` by hand is unclear. At 21:52 the assistant said the agent may run it. At 07:19 the assistant said the human runs `close`, and the user said yes. No question asks about it.

## User clarifications, 2026-11-17

The user settled the five points above after the input was frozen. Points 1 and 2 read answers that lie inside the input window, so questions may rest on them. Points 3 to 5 add facts that are not in the input. No contestant can know them, so no question rests on them.

1. "BZ" at 2026-11-15T21:39 means B.
2. "1. Yes" at 2026-11-17T07:20 chose the first option.
3. The handoff's "0 escalated = no escalation" is wrong as a decision. It is only a consequence: with 0 escalated attempts left, no escalation happens. The handoff is part of the input, so a writer that copies its phrasing states a non-decision as a decision.
4. QA findings go to the implementation agent as tickets, which it dispatches with the next wave.
5. The user recalls that the implementation agent runs `dispatch close` by hand. The frozen proposal says the human runs it in both modes (line 173), and the conversation does not settle it. This point stays open.
