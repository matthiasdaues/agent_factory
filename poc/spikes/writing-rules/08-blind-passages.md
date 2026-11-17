# Blind passages

Each passage is text an agent wrote in a chat or a file. Apply the rules to each passage on its own.

## P01

> **My recommendation.** Keep `critical`, because the rule computes it and I should not lower it myself.

## P02

> The other proposals carry `scope: global` on the first line of their frontmatter. Should I add `scope: global` to the two committed proposals in a separate commit, `docs: declare the scope of two proposals`? Then I would retry the fix commit. If either proposal has a narrower scope, tell me the value.

## P03

> A project on `v0.12.0` may also have no `install.json`, and then the update stops with "not an init-factory'd project".

## P04

> How should I go on with BUG-0048?
>
> - **(a)** Correct the finding to a latent defect, with no incident, and finish the fix through the usual cycle.
> - **(b)** Drop it, delete the worktree and the branch, and withdraw the finding. Then I move on to I-1.
>
> I recommend (a). Today showed how hard it is to get out of a wrong install record: three runs, and each one needed a manual cleanup.

## P05

> Three of these fixes are small choices of my own: fail fast on any other refusal (PROP-14), a fixed committer (PROP-15), and only a warning from `init-factory` (PROP-16). The other two only correct the text.
>
> Should I write these four fixes into the proposal?

## P06

> A person accepts it with a small commit on `dev`, and the story then passes without a rebase.

## P07

> I recommend the simple version. A stale function name is cheap to notice, and only 41 references carry one. The change withdraws DEC-02, DEC-04, DEC-07, DEC-10 and DEC-12, and DEC-06 needs rewording. DEC-01, DEC-03, DEC-05, DEC-08, DEC-09 and DEC-11 stay.
>
> Shall I rewrite the proposal to the simple version?

## P08

> I recommend confirming all seven, because each one matches what we discussed and I have no reason to doubt any of them. After that, three steps remain before `status: open`: a fresh agent writes the primer, the lector agent edits the prose, and I run the readiness check.
>
> Do you confirm all seven, or do you want to change one?

## P09

> Part B of wave 4 is still running. The implementation agent is waiting on the ST-0358 and ST-0365 developers, so there's no result yet. When it reports, I'll check the merges and `close-wave 4` against git.
>
> Your answer on `--write-glossary` is still open. I recommended keeping the name and adding the argument in ST-0351.

## P10

> **What it settles:**
>
> - The format of `glossary.md`.
> - The change to `domain-modeling` and the template.
> - `GLOSS001` reading `glossary.md` in that format. It stays an `info` finding, so the core table names `spec-lint GLOSS001 (info)` as the glossary's check instead of "none yet."
>
> Do you choose A?

## P11

> Not available. The text was factory output in another project's onboarding run; that project's transcripts are out of scope.

## P12

> The glossary cleanup is a follow-up step the script names in its output, the same way as the fold. It does not write an entry into the project's `work/todo.md`. If you want the script to record both follow-ups there, so they outlast the terminal output, say so and I'll add it.
>
> Next steps:
>
> 1. Commit the fixes as `docs: fix review pass 4 findings on the layout proposal`.
> 2. Start review pass 5 in a fresh session.

## P13

> 1. The other session fixes the three failures.
> 2. Commit the staged files: the wrapper first, then the proposal.
> 3. Run the grilling round on the eight assumptions: DEC-07 to DEC-11, DEC-13, and DEC-14.
> 4. Run the lector passes, write the primer, and check the gate before the proposal goes to `status: open`.
>
> Should I write this as a handoff in `docs/handoffs/` before you go? Then a fresh session can start tomorrow from the file instead of from this conversation.

## P14

> Your answers decide the Design and the Decisions table of the new proposal, `docs/proposals/finding-threshold.md`. They also decide whether the proposal changes `finding-format.md`, `report-format.md`, and the finding template. After this theme I'll ask whether to go deeper (the actual table cells) or start writing.

## P15

> I recommend one guard script that all five tools call, the way `guard-human-fields` already works. pi's TypeScript copy becomes a thin wrapper that hands the command to that script. A completion criterion then checks OpenCode against a real session, not a mock.
>
> Do you accept this?

## P16

> 1. You confirm that the 21:08 run is yours, or a run you started. I won't commit or discard changes whose origin I can't place.
> 2. If it is, I run `statemachine-lint` to close CAO-04-AC-01. Then I commit the two files after `verify-base feature/core-artifact-ownership`, and I move `branch_head` by hand.
> 3. Then we do CAO-05-AC-01. You pick one domain area, which here means "Core artifact ownership". We go through its nine terms, and the domain-modeling agent moves the ones you confirm into the glossary.
>
> Is the 21:08 run yours, and should I go ahead with step 2?

## P17

> The project's git guard refused my `uv run pytest` call. I won't work around it.

## P18

> - **`finding-threshold.md` (T-0016)** holds the risk table and the line (Q1, Q6), the cap of 3 passes (Q2), the human-only override (Q4), and the three required fields. It also says that a finding below the line is recorded, not left `open`.
> - **A separate finding-format proposal** settles Q3's register, Q5, Q7, and Q8. The threshold proposal lists it as deferred and links it. I'll also file it as a todo entry, T-0017.
>
> Should I split it this way? If yes, the next step is your answer on Q6, and then I write the draft.

## P19

> **Not done: checking `poc/workflow/workflow.svg`.**
>
> - ImageMagick cannot render the export as it is.
> - I inlined the embedded SVG, but it holds only 797 characters, which is not the shapes. The render came out nearly blank.
> - The shapes must be stored elsewhere in the file. The next step is to find where, or to render the file with a browser or Inkscape.
> - `poc/workflow/` is untracked, and I have not changed it.
>
> When your limit resets, tell me what you want me to check in that export, or a specific problem you saw. I can then pick it up from there.

## P20

> **Waiting on you, because the guard or ownership stops me**

## P21

> - The Gigacron findings from `expected-differences.md` aren't filed yet.

## P22

> IMPL-0014 is still `open` and waits for you. Tell me why it isn't a defect, or write the waiver.

## P23

> The two reviews overlap more than they seem to, because several majors come from parts the skeptical review wanted deleted.

## P24

> 1. **BUG-0111:**
>    - the template lookup with the key check;
>    - `init-factory` sets the key and `remove-factory` unsets it;
>    - tests for both paths (key set → exit 1 with the message; key unset → exit 0, no output).
> 2. **BUG-0110:**
>    - `update-factory` runs the refresh after `init-factory` succeeds;
>    - it shows the diff and asks y/N before it writes, and writes nothing on no;
>    - it skips a project that never merged the factory hooks;
>    - tests for yes, no, unchanged and not merged.
> 3. **This repo's own hooks:**
>    - I move the `stages:` lines into the template, so a refresh here loses nothing;
>    - I leave the `backlog-lint` "$@" difference as the template has it, unless you prefer the repo's variant.
>
> Tests run only through `pre-commit run run-tests --all-files`. When they pass, I show you the diff before anything gets committed.
>
> Shall I build it this way?

## P25

> - The layer key `end_to_end` doesn't match the skill's vocabulary, `e2e_smoke_test`. A test, `test_testing_yaml_declares_end_to_end_layer`, and the value-first onboarding QA strategy both depend on the current key. Renaming it would break both, so a story should change all three together.
> - `layers.deterministic_linter.entry_point` names only `usage-contract-check`. The factory's lint gates actually run through pre-commit.
>
> Do you confirm the proposal as it stands? Or do you have commands for the two orphan suites?

## P26

> If each measuring command gets an optional `ready` command in `docs/testing.yaml`, the setup skill writes it, for example a check that the app container is up.

## P27

> 1. **G10:** what status does a `QA` finding get when a test is missing? I recommend keeping it `open` and moving its `owner:` from the test-strategy agent to the planning agent. The finding becomes `resolved` when a story adds the test. That way the finding stays visible and goes to the agent that can act on it.
> 2. **The twelve defaults:** G02 to G07, G09, and G11 to G16. The specification already follows my recommendation for each one.
>
> If you accept both, I'll record them, commit step 1 on `dev`, and start the spec-review agent for step 2.

## P28

> - **Next run:** the brief-storage run, then the gate proposal.

## P29

> For the entity model, LinkML is a medium job: about 8 to 13 ideal person-days.

## P30

> **My proposal:** one small commit on the integration branch, `git update-index --chmod=+x packages/factory/scripts/_docs_assemble.py`, as `fix: make _docs_assemble.py executable`. Then the suite runs again, followed by the final merge into `dev`. The file is yours, from the publish-docs work, which is why I ask first.
>
> Shall I do it?

## P31

> | `second_breach` | | | | | x | | A "yes" lowers the level one step. |

## P32

> **What it means for the proposal:**
>
> - **Option B from the last question gains weight.** A note travels to the database, and a comment never does.
> - **Generating DDL stays deferred.** Producing the comments is the job of the project's migrations or ORM. The proposal keeps DBML as the model, not as a code generator.
> - **A new question for later in the grilling:** whether `compare` also reports comment drift. Where a project sets comments, a changed note becomes visible. Where it doesn't, every note would show up as a difference. So I'll suggest making it optional.
>
> The pending decision is still: B, with prose in notes, a lint that rejects comments carrying prose, notes free in length and position, and the review rule for behaviour. Do you choose B?

## P33

> Should the line stay as drawn, or do you want a different cell?

## P34

> What is a Payout? My proposal is "One amount owed to one recipient, which a payment batch sends to the bank together with other payouts."

## P35

> **What you decide:**
>
> - **Option A, my recommendation:** only failing rows carry `owner:`. The contract gets corrected to match the story.
> - **Option B:** every row carries `owner:`. Then the field means "who owns this rule" rather than "who must act", and the code has to change.
>
> A is the better fit, because elsewhere in this proposal `owner:` already means the agent that acts next. That is the meaning for findings, CAO-G26. B would give the same field two meanings.

## P36

> **One more point, from the review loop:** PROP-12 arose from my fix in pass 2. The findings are now moving into cases that earlier fixes created. I'd do these two fixes, have pass 4 check only them, and then end the loop: primer, lector, and your acceptance.
>
> Should I go ahead like that?

## P37

> **My recommendation:** fail with that message. A project without a remote has one person on one clone, and creating a GitHub repository first takes a minute. Then the counter has one home from the first ID on.
>
> **What the answer settles:** PROP-06, one row in the error table, one completion criterion, and the `init-factory` message for a project without `origin`.
>
> Should `next-id` fail in a project without a remote?

## P38

> One open point remains here: the line between the exposures `fails` and `uncertain`. I think the draft defines it well enough, so I recommend moving on to the security factors. The eight factor anchors are my own invention. They decide every security severity, and none of them has met a real finding yet. I would test them against SEC-0003, the unpinned `tiktoken` dependency.

## P39

> `owner:` names the agent that acts next, and a passing check leaves nobody anything to do.

## P40

> This is the layout release. It reorganises the core artifacts of a
> project (ST-0318 to ST-0345). The work ends with the merge of
> `feature/core-artifact-layout` into dev, commit
> `e62ac0b077a6d90635b028bdd0e624e1809cde1a`.

## P41

> The gap report then follows as the detail behind the sentence "I cannot yet check". I recommend making this paragraph the opening of the proposal. Shall I start `draft-proposal` with it, the three-part profile, and the gap report as one feature?

## P42

> no factory specific docs folders found

## P43

> The gap is in what the repo can confirm. It confirms the end-of-turn event for Claude Code, Copilot, Codex, and OpenCode. It confirms the per-prompt event only for Claude Code. Pi is unconfirmed on both: its usage capture runs only at `session_shutdown`, which is too late for speech. The adapter table marks each unconfirmed cell "to verify".
>
> I suggest a short documentation survey of those cells before the grilling. Otherwise the grilling would argue about events nobody has looked up yet. Should I run that survey now?

## P44

> 1. **Where gate result files live.** ST-0359 makes `dependency-check` mandatory for every story.

## P45

> Removing the check for open findings leaves one gap. In an orchestrated run, the criterion "the merge waits until no finding for the story is open" is an instruction to the agent, and no script enforces it yet.

## P46

> One answer is still open: do you approve the lector's plan items, all 27 or only some? You answered my two decision questions, but not that one. As soon as you approve, I write the round-2 brief. It carries the approved items, my ten author fixes for U1 to U6 and C1 to C6, and a note that the proposal has changed since `a19d383b`. Then I start the lector.

## P47

> # How a finding gets its severity
>
> The reviewer records facts. A fixed rule computes the severity.

## P48

> I recommend A for now. It is simple, it gives every project full control, and the update script already moves changes it finds aside. B is worth building once several projects make the same kind of small change. Your answer decides how playbooks are stored in a project and what `update-factory` has to do with them.

## P49

> I recommend sending the corrections back to the same report writer, because it still holds its reading of the sources and a fix costs one round. Then a fresh validator runs the full check again, as the review-loop rules require. Two concepts may lose their top ranks.
>
> Should I send the corrections to the report writer?

## P50

> It waits for line 8 of `/home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/bug-hunt-fixes/invocation/backlog/ST-0296.md`, as shown above.

## P51

> 1. **Commit check without freshness (part 3):** a story can commit for days on a stale base and only learns about conflicts at the merge. Should `refresh-story` also run when the trial merge is clean but the target is more than N commits ahead?

## P52

> `story-gates` and `story-done-gate` now appear only in the decision records and review tables that document their removal.

## P53

> A severity decides what the run does next

## P54

> **Next step:** `draft-proposal` continues with the grilling. It tests the written draft and settles the five assumptions with you. After that come the lector passes, the primer and the readiness gate, and then `status: open` for the review. Should I start the grilling?

## P55

> # The AI answers questions. Code sets the severity.

## P56

> It found no unclear sentences.

## P57

> The reconciliation agent reads the code as built and finds where the documents drifted.

## P58

> **Where the truth lives.** Agent Factory keeps the specification and the DSL as core truth, with derived views, and reconciles the code against them. BMAD treats the code as truth and keeps documents small.

## P59

> The GitHub ticket adapter of `project-agent-flows.md` runs on the platform machine. That machine has no clone of the project, so it has no `origin`.

## P60

> Meanwhile I prepare the proposal for the final merge.

## P61

> Which way does the GitHub adapter run `next-id`?

## P62

> I recommend option A. A run then has exactly two ends, finished or dropped, and in both cases nothing of the run remains except unmerged branches that the human deletes. Option B leaves stray worktrees behind, which is how this repository came to hold thirteen of them. A story returned to the backlog can start again in a later run from a fresh branch.
