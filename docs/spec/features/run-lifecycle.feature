# scope: global
Feature: Run Lifecycle

  A run is everything the Factory does for one feature branch, from
  dispatch init to dispatch close. The glossary calls it a Dispatch Run.
  The feature branch is the branch of the run, cut from dev. Each story
  of the run gets a story branch story/<story-id>, cut from the feature
  branch. The ledger .current-work/<feature-branch>/dispatch-ledger.yaml
  tracks the state of each story while the run is active.

  A run is driven in one of two ways. In an orchestrated run, the
  implementation agent starts stories in waves, sets of stories that start
  together, and each story runs in its own worktree under .current-work/.
  In a run by hand, the implementation agent starts each story after the
  User's go, one story at a time, in the primary checkout. The primary
  checkout is the repository's main folder. Both ways share the same
  branches, ledger states, story workflow, checks, and end.

  A unit of work is a story or a blocking finding that runs through the
  story workflow on a branch story/<id>. The gate-check step runs the gates
  on a story branch and fixes what they report. A drift session is the
  spawn of an owner, or of that owner's reviewer, to settle one row of a
  spec-feedback report.

  A unit of work has stopped when it waits for the User. A blocked unit
  of work has stopped. A failed unit of work has stopped in two cases
  only: its counted attempts on its tier are used up and it cannot
  escalate any more, or two of its attempts have the failure class
  contract_violation. A unit of work cannot escalate any more when
  dispatch escalate refuses it for any reason of BR-115: it runs on the
  tier strong, it has already escalated, gates.attempts_escalated is 0,
  verify-base fails, or its diff leaves its scope. Every other failed unit
  of work still has a retry, so the implementation agent runs it again
  without the User.

  The User is the person who drives the Factory, as the glossary defines.
  The examples use the feature branch feature/login, the stories ST-0350,
  ST-0351 and ST-0352, the finding BUG-0090, and the finding QA-0012.

  Proposal trace: docs/proposals/run-lifecycle.md

  Rule: User starts a run on a feature branch in either way of driving it
    # actor: User
    # @packages/factory/scripts/dispatch::cmd_init
    # The User asks the implementation agent for the run. The implementation
    # agent runs dispatch init on both ways, so the User runs only the three
    # commands of the Rule on a run driven by hand.

    Scenario: A run by hand starts without a worktree for the feature branch
      Given no ledger exists for feature/login
      And the primary checkout has dev checked out
      When the implementation agent runs dispatch init --mode by-hand --base dev --feature-branch feature/login --stories ST-0350,ST-0351
      Then the branch feature/login exists and points at the tip of dev
      And no worktree holds feature/login
      And the primary checkout still has dev checked out
      And .current-work/feature/login/dispatch-ledger.yaml has mode by-hand
      And the ledger records ST-0350 and ST-0351 as pending

    Scenario: An orchestrated run starts with a worktree for the feature branch
      Given no ledger exists for feature/login
      When the implementation agent runs dispatch init --mode orchestrated --base dev --feature-branch feature/login --stories ST-0350,ST-0351
      Then a worktree under .current-work/ holds feature/login
      And the ledger of feature/login has mode orchestrated

    Scenario: dispatch init without --mode starts an orchestrated run
      Given no ledger exists for feature/login
      When the implementation agent runs dispatch init --base dev --feature-branch feature/login --stories ST-0350
      Then the ledger of feature/login has mode orchestrated
      And a worktree under .current-work/ holds feature/login

    Scenario: The branch root is the tip of the feature branch at init
      Given no ledger exists for feature/login
      When the implementation agent runs dispatch init --mode orchestrated --base dev --feature-branch feature/login --stories ST-0350
      Then the ledger's branch_root is the 40-character SHA of the tip of feature/login
      # @packages/factory/scripts/dispatch::cmd_init

    Scenario: The test command comes from docs/testing.yaml
      Given docs/testing.yaml names no test command
      When the implementation agent runs dispatch init --mode orchestrated --base dev --feature-branch feature/login --stories ST-0350
      Then dispatch exits non-zero
      And the message names docs/testing.yaml
      # @packages/factory/scripts/dispatch::_read_test_command

    Scenario: A second orchestrated run starts while another run is active
      Given an orchestrated run is active on feature/login
      When the implementation agent runs dispatch init --mode orchestrated --base dev --feature-branch feature/search --stories ST-0352
      Then dispatch exits 0
      And .current-work/feature/search/dispatch-ledger.yaml exists

    Scenario: A second run by hand is refused while a run by hand is active
      Given a run by hand is active on feature/login
      When the implementation agent runs dispatch init --mode by-hand --base dev --feature-branch feature/search --stories ST-0352
      Then dispatch exits non-zero
      And the message names the active run on feature/login
      And no ledger exists for feature/search

    Scenario: A feature branch whose ledger lists other stories is refused
      Given .current-work/feature/login/dispatch-ledger.yaml lists ST-0350
      When the implementation agent runs dispatch init --mode orchestrated --base dev --feature-branch feature/login --stories ST-0351
      Then dispatch exits non-zero
      And the message names the ledger of feature/login
      And the ledger of feature/login still lists only ST-0350

    Scenario: dispatch init on a ledger with the same stories resumes an interrupted start
      Given .current-work/feature/login/dispatch-ledger.yaml lists ST-0350 and ST-0351
      When the implementation agent runs dispatch init --mode orchestrated --base dev --feature-branch feature/login --stories ST-0350,ST-0351
      Then dispatch exits 0
      And the ledger of feature/login is unchanged
      # @packages/factory/scripts/dispatch::cmd_init

    Scenario: A story whose dependency outside the run is not done is refused
      Given ST-0351 depends on ST-0349
      And backlog/ST-0349.md has status pending
      And ST-0349 is not named in --stories
      When the implementation agent runs dispatch init --mode orchestrated --base dev --feature-branch feature/login --stories ST-0351
      Then dispatch exits non-zero
      And the message names ST-0349
      And no ledger exists for feature/login

  Rule: Implementation agent runs every story through the same story workflow on both ways
    # actor: Implementation agent
    # @packages/factory/scripts/dispatch::cmd_mark_dispatching
    # @packages/factory/scripts/dispatch::cmd_mark_dispatched

    Scenario: A story reaches dispatched in a run by hand
      Given a run by hand is active on feature/login
      And ST-0350 is prepared
      When the implementation agent runs dispatch mark-dispatching ST-0350
      And the implementation agent spawns a developer agent for ST-0350
      And the developer agent commits on story/ST-0350
      And the implementation agent runs dispatch mark-dispatched ST-0350
      Then the ledger records ST-0350 as dispatched

    Scenario: The story workflow runs its steps in order on the story branch
      Given ST-0350 is dispatched in a run on feature/login
      When the story workflow of ST-0350 completes
      Then story/ST-0350 holds the developer agent's implementation commit
      And story/ST-0350 holds a code-review report whose story is ST-0350
      And no blocking finding with story ST-0350 is open at the head of story/ST-0350
      And the gate-check step has run every gate of the story on story/ST-0350
      And ST-0350 has merged into feature/login through dispatch merge-story

    Scenario: A repeat review follows each fix of a blocking finding
      Given the code review of ST-0350 filed a major defect finding with story ST-0350
      When a fresh developer agent fixes the finding and commits
      Then the code-review agent reviews story/ST-0350 again
      And the loop ends only when no blocking finding with story ST-0350 is open

    Scenario: Only dispatch merge-story sets a story to done
      Given ST-0350 is dispatched in a run on feature/login
      When dispatch merge-story ST-0350 merges story/ST-0350 into feature/login
      Then backlog/ST-0350.md has status done in the merge commit
      And no commit of the developer agent on story/ST-0350 sets status done
      # @packages/factory/scripts/dispatch::cmd_merge_story

    Scenario: dispatch has no mark-done subcommand
      When the User runs dispatch mark-done ST-0350
      Then dispatch exits non-zero
      And the usage text lists no mark-done subcommand
      # @packages/factory/scripts/dispatch::cmd_mark_done

    Scenario: The developer agent runs no gate script
      Given the developer agent implements ST-0350
      When the developer agent finishes its commits
      Then the developer agent has run no gate script
      And the implementation agent runs the gate-check step on story/ST-0350

  Rule: User approves each step that needs a person in a run driven by hand
    # actor: User

    Scenario Outline: The implementation agent stops and waits before a decision point
      Given a run by hand is active on feature/login
      When the run reaches <point>
      Then the implementation agent shows the story, its branch head, the findings with their status, and the output of premerge-check where it applies
      And the implementation agent names the command it will run
      And the implementation agent runs no command until the User's go

      Examples:
        | point                                                                         |
        | the start of ST-0350                                                          |
        | dispatch add of QA-0012                                                       |
        | the merge of ST-0350                                                          |
        | a stop of ST-0350 as blocked                                                  |
        | a stop of ST-0350 as failed after its last counted attempt on the tier strong |
        | a stop of ST-0350 as failed after its second contract_violation attempt       |
        | the merge of feature/login into dev                                           |

    Scenario: A failed attempt with a retry left is no decision point
      Given a run by hand is active on feature/login
      And docs/testing.yaml sets gates.attempts to 3
      And ST-0350 runs on the tier standard
      When the first attempt of ST-0350 fails crap-score
      Then the ledger records ST-0350 as failed
      And ST-0350 has not stopped
      And the implementation agent runs dispatch re-dispatch ST-0350 without a stop for the User

    Scenario: prepare-story checks out the story branch in the primary checkout
      Given a run by hand is active on feature/login
      And ST-0350 is pending and has no dependency inside the run
      When the User gives the go and the implementation agent runs dispatch prepare-story ST-0350
      Then the primary checkout has story/ST-0350 checked out
      And story/ST-0350 starts at the tip of feature/login
      # @packages/factory/scripts/dispatch::cmd_prepare_story

    Scenario: merge-story runs premerge-check before it checks out the feature branch
      Given a run by hand is active on feature/login
      And the primary checkout has story/ST-0350 checked out
      And ST-0350 is dispatched
      And every check of premerge-check passes at the head of story/ST-0350
      When the User gives the go and the implementation agent runs dispatch merge-story ST-0350
      Then merge-story runs premerge-check on story/ST-0350 while the primary checkout still has story/ST-0350 checked out
      And merge-story checks out feature/login only after premerge-check exits 0
      And the primary checkout has feature/login checked out
      And feature/login holds the merge commit of story/ST-0350

    Scenario: A refused premerge-check leaves the primary checkout on the story branch
      Given a run by hand is active on feature/login
      And the primary checkout has story/ST-0350 checked out
      And ST-0350 is dispatched
      And the head of story/ST-0350 fails dependency-check
      When the User gives the go and the implementation agent runs dispatch merge-story ST-0350
      Then premerge-check exits non-zero
      And the message names dependency-check
      And the primary checkout still has story/ST-0350 checked out
      And the files in the primary checkout are unchanged
      And the tip of feature/login is the same commit as before the merge-story call

    Scenario: A changed tracked file in the primary checkout does not hide a failing gate
      Given a run by hand is active on feature/login
      And the primary checkout has story/ST-0350 checked out
      And ST-0350 is dispatched
      And story/ST-0350 changed src/login.py
      And the primary checkout holds an uncommitted change to src/login.py
      And the head of story/ST-0350 fails dependency-check
      When the User gives the go and the implementation agent runs dispatch merge-story ST-0350
      Then premerge-check exits non-zero
      And the message names dependency-check and no git checkout error
      And the primary checkout still has story/ST-0350 checked out
      And the uncommitted change to src/login.py is unchanged
      And the tip of feature/login is the same commit as before the merge-story call

    Scenario: The User runs only three commands in a run by hand
      Given a run by hand is active on feature/login
      When the run goes from dispatch init to dispatch close
      Then the User runs at most dispatch return-story, dispatch close --drop, and dispatch close
      And the User merges feature/login into dev
      And the implementation agent runs dispatch init and every other dispatch command of the run

    Scenario: A run by hand needs no refresh of the story branch
      Given a run by hand is active on feature/login
      When ST-0350 runs from prepare-story to merge-story
      Then the implementation agent does not run dispatch refresh-story ST-0350

  Rule: Reviewer agent files reviews and findings that name their story or run
    # actor: Reviewer agent

    Scenario: The review report carries the story ID in its name
      Given ST-0350 is dispatched on story/ST-0350
      When the code-review agent reviews story/ST-0350 on 2026-11-24
      Then the report is docs/reviews/code-review-ST-0350-2026-11-24.md
      And the report's story field is ST-0350
      And the report's branch_head is the head of story/ST-0350 that it reviewed

    Scenario: A second review on the same day adds a number to the name
      Given docs/reviews/code-review-ST-0350-2026-11-24.md exists on story/ST-0350
      When the code-review agent reviews story/ST-0350 again on 2026-11-24
      Then the new report is docs/reviews/code-review-ST-0350-2026-11-24-2.md
      And a third review that day writes docs/reviews/code-review-ST-0350-2026-11-24-3.md

    Scenario: Two stories reviewed on the same day merge without a conflict on their reports
      Given ST-0350 and ST-0351 run in one wave of feature/login
      And both are reviewed on 2026-11-24
      When dispatch merge-story merges ST-0350 and then ST-0351
      Then both merges succeed without a conflict on a review report

    Scenario: A story finding names its story
      When the code-review agent files a finding about story/ST-0350
      Then the finding file has story ST-0350 and an empty run
      And the developer agent commits the finding on story/ST-0350

    Scenario: A review without findings still commits its report
      Given the code review of ST-0350 files no finding
      When the developer agent commits after the review
      Then story/ST-0350 holds docs/reviews/code-review-ST-0350-2026-11-24.md

    Scenario: A feature-level finding names its run
      When the QA agent files a finding about feature/login
      Then the finding file has an empty story and run feature/login

    Scenario Outline: A feature-level report names its run
      When the <agent> writes its <report> in the feature checks of feature/login
      Then the report's run field is feature/login
      And the report's branch_head is the head of feature/login that it reviewed

      Examples:
        | agent             | report                             |
        | code-review agent | code-review report                 |
        | QA agent          | Fagan report                       |
        | QA agent          | security report                    |
        | QA agent          | bug-hunt report                    |

    Scenario: A finding from a review outside any run names neither
      When a reviewer agent files a finding outside any run
      Then the finding file has an empty story and an empty run

    Scenario: finding-lint refuses a finding that names both a story and a run
      Given docs/findings/BUG-0095.md has story ST-0350 and run feature/login
      When finding-lint checks docs/findings/BUG-0095.md
      Then finding-lint exits non-zero
      And the message names BUG-0095 and the fields story and run

  Rule: Implementation agent retries a failing gate within the configured attempts
    # actor: Implementation agent
    # @packages/factory/scripts/dispatch::cmd_escalate

    Scenario: With the defaults, a failing story gets three attempts on each tier and is then failed
      Given docs/testing.yaml sets neither gates.attempts nor gates.attempts_escalated
      And ST-0350 runs on the tier standard
      And crap-score fails on every attempt of ST-0350
      When the gate-check step of ST-0350 runs to its end
      Then three attempts ran on the tier standard, the first attempt included
      And three attempts ran on the tier strong
      And the ledger records ST-0350 as failed

    Scenario: A failing gate records the failure class acceptance_unmet
      Given crap-score fails on the first attempt of ST-0350
      When the implementation agent records the attempt
      Then the attempt in the ledger has the failure class acceptance_unmet

    Scenario: dispatch escalate refuses before the attempts on the tier are used
      Given docs/testing.yaml sets gates.attempts to 3
      And ST-0350 runs on the tier standard
      And two attempts of ST-0350 failed with the failure class acceptance_unmet
      When the implementation agent runs dispatch escalate ST-0350
      Then dispatch exits non-zero
      And the ledger records ST-0350 on the tier standard
      # @packages/factory/scripts/dispatch::cmd_escalate

    Scenario: dispatch escalate grants after the attempts on the tier are used
      Given docs/testing.yaml sets gates.attempts to 3
      And ST-0350 runs on the tier standard
      And three attempts of ST-0350 failed with the failure class acceptance_unmet
      When the implementation agent runs dispatch escalate ST-0350
      Then the ledger records ST-0350 on the tier strong
      # @packages/factory/scripts/dispatch::cmd_escalate

    Scenario: An attempt of another failure class does not count toward gates.attempts
      Given docs/testing.yaml sets gates.attempts to 3
      And ST-0350 runs on the tier standard
      And the first attempt of ST-0350 failed with the failure class acceptance_unmet
      And the second attempt died on the spend limit with the failure class spend_death
      And the third attempt failed with the failure class acceptance_unmet
      When the implementation agent runs dispatch escalate ST-0350
      Then dispatch exits non-zero
      And the ledger records ST-0350 on the tier standard
      And the next attempt of ST-0350 runs on the tier standard as the third counted attempt
      # @packages/factory/scripts/dispatch::cmd_escalate

    Scenario: A story on the tier strong does not escalate and fails after its attempts
      Given docs/testing.yaml sets neither gates.attempts nor gates.attempts_escalated
      And ST-0350 runs on the tier strong
      And crap-score fails on every attempt of ST-0350
      When the gate-check step of ST-0350 runs to its end
      Then three attempts ran on the tier strong, the first attempt included
      And the implementation agent did not run dispatch escalate ST-0350
      And the ledger records ST-0350 as failed

    Scenario: Each retry gets a fresh developer agent with the gate output
      Given crap-score fails on the first attempt of ST-0350
      When the implementation agent starts the second attempt
      Then it spawns a fresh developer agent
      And the brief of that developer agent holds the output of crap-score

    Scenario: A value of 0 turns escalation off
      Given docs/testing.yaml sets gates.attempts_escalated to 0
      And crap-score fails on every attempt of ST-0350
      When the gate-check step of ST-0350 runs to its end
      Then no attempt of ST-0350 ran with a stronger model
      And the ledger records ST-0350 as failed

    Scenario: dispatch escalate refuses when gates.attempts_escalated is 0
      Given docs/testing.yaml sets gates.attempts to 3 and gates.attempts_escalated to 0
      And ST-0350 runs on the tier standard
      And three attempts of ST-0350 failed with the failure class acceptance_unmet
      When the implementation agent runs dispatch escalate ST-0350
      Then dispatch exits non-zero
      And the ledger records ST-0350 on the tier standard
      # @packages/factory/scripts/dispatch::cmd_escalate

    Scenario: dispatch re-dispatch refuses when the attempts on the tier are used up
      Given docs/testing.yaml sets gates.attempts to 3
      And ST-0350 runs on the tier standard and has not escalated
      And three attempts of ST-0350 failed with the failure class acceptance_unmet
      When the implementation agent runs dispatch re-dispatch ST-0350
      Then dispatch exits non-zero
      And the message says that ST-0350 requires escalation before re-dispatch
      And the message names dispatch escalate
      And the ledger records ST-0350 as failed on the tier standard
      # @packages/factory/scripts/dispatch::cmd_re_dispatch

    Scenario: dispatch re-dispatch keeps the tier while attempts on it remain
      Given docs/testing.yaml sets gates.attempts to 3
      And ST-0350 runs on the tier standard
      And two attempts of ST-0350 failed with the failure class acceptance_unmet
      When the implementation agent runs dispatch re-dispatch ST-0350
      Then the ledger records ST-0350 as prepared on the tier standard
      # @packages/factory/scripts/dispatch::cmd_re_dispatch

    Scenario: Two stories of one wave both escalate
      Given ST-0350 and ST-0351 run in wave 1 of feature/login
      And both use up their attempts on their own tier
      When the implementation agent runs dispatch escalate for ST-0350 and for ST-0351
      Then both escalations are granted

    Scenario: The same counts apply in a run by hand
      Given a run by hand is active on feature/login
      And docs/testing.yaml sets gates.attempts to 2
      And crap-score fails on every attempt of ST-0350
      When the gate-check step of ST-0350 runs
      Then two attempts ran on the tier of ST-0350 before escalation

  Rule: User decides how a stopped story continues
    # actor: User
    # @packages/factory/scripts/dispatch_lib.py::VALID_TRANSITIONS
    # dispatch re-dispatch grants new attempts to a failed story only when the
    # story can no longer escalate. dispatch cannot see whether the User fixed
    # the cause, so on the last tier an agent can start a retry that the User
    # did not ask for. The User watches the run, and the guardrail blocks only
    # the commands that destroy work (RL-G22).

    Scenario Outline: A story stops in the state that names its cause
      Given ST-0350 is dispatched in a run on feature/login
      When <cause>
      Then the ledger records ST-0350 as <state>
      And ST-0350 has stopped
      And the run waits for the User

      Examples:
        | cause                                                                        | state   |
        | a gate still fails on the last counted attempt of ST-0350 on the tier strong | failed  |
        | a second attempt of ST-0350 fails with the failure class contract_violation  | failed  |
        | dispatch merge-story meets a merge conflict                                  | blocked |
        | dispatch merge-story meets a conflict in the refresh                         | blocked |
        | the test suite fails after the merge of story/ST-0350                        | blocked |

    Scenario: A story whose diff leaves its scope stops when dispatch escalate refuses it
      Given docs/testing.yaml sets gates.attempts to 3 and gates.attempts_escalated to 3
      And ST-0350 runs on the tier standard and has not escalated
      And three attempts of ST-0350 failed with the failure class acceptance_unmet
      And the diff of story/ST-0350 changes a file outside the declared outputs of ST-0350
      When the implementation agent runs dispatch escalate ST-0350
      Then dispatch exits non-zero
      And the ledger records ST-0350 as failed on the tier standard
      And the entry of ST-0350 has reason "escalate refused: scope"
      And ST-0350 has stopped
      And the run waits for the User
      # @packages/factory/scripts/dispatch::cmd_escalate

    Scenario: A red test suite after a merge moves the feature branch back
      Given feature/login is at commit A
      And story/ST-0350 merges into feature/login cleanly
      When the test suite fails on the merge commit
      Then feature/login is back at commit A
      And feature/login holds no revert commit
      And the ledger records ST-0350 as blocked with reason "post-merge test failure"
      # @packages/factory/scripts/dispatch::cmd_merge_story

    Scenario: A fixed cause lets the story continue in the same run
      Given ST-0350 is blocked with reason "merge conflict"
      And the User has fixed the cause
      When the User tells the implementation agent to continue
      Then the implementation agent runs dispatch re-dispatch ST-0350
      And ST-0350 continues in the run on feature/login
      # @packages/factory/scripts/dispatch::cmd_re_dispatch

    Scenario: After the User's fix, re-dispatch grants new attempts to a failed story whose attempts are used up
      Given docs/testing.yaml sets neither gates.attempts nor gates.attempts_escalated
      And ST-0350 failed three counted attempts on the tier standard and three on the tier strong
      And the ledger records ST-0350 as failed on the tier strong
      And the User has fixed the shared test fixture that made every attempt fail
      When the User tells the implementation agent to continue
      Then the implementation agent runs dispatch re-dispatch ST-0350
      And the ledger records ST-0350 as prepared on the tier strong
      And ST-0350 has three new counted attempts on the tier strong
      And ST-0350 continues in the run on feature/login
      # @packages/factory/scripts/dispatch::cmd_re_dispatch

    Scenario: After the User's fix, re-dispatch grants new attempts when escalation is off
      Given docs/testing.yaml sets gates.attempts to 3 and gates.attempts_escalated to 0
      And ST-0350 failed three counted attempts on the tier standard
      And the ledger records ST-0350 as failed on the tier standard
      And the User has fixed the shared test fixture that made every attempt fail
      When the User tells the implementation agent to continue
      Then the implementation agent runs dispatch re-dispatch ST-0350
      And the ledger records ST-0350 as prepared on the tier standard
      And ST-0350 has three new counted attempts on the tier standard
      # @packages/factory/scripts/dispatch::cmd_re_dispatch

    Scenario: After the User's fix, re-dispatch refuses a failed story that can still escalate
      Given docs/testing.yaml sets gates.attempts to 3 and gates.attempts_escalated to 3
      And ST-0350 failed three counted attempts on the tier standard and has not escalated
      And the ledger records ST-0350 as failed on the tier standard
      And the User has fixed the shared test fixture that made every attempt fail
      When the implementation agent runs dispatch re-dispatch ST-0350
      Then dispatch exits non-zero
      And the message names dispatch escalate
      And the ledger records ST-0350 as failed on the tier standard
      # @packages/factory/scripts/dispatch::cmd_re_dispatch

    Scenario Outline: return-story sets a stopped story back to pending
      Given ST-0350 is <state> in the run on feature/login
      When the User runs dispatch return-story ST-0350
      Then the ledger records ST-0350 as pending
      And the entry of ST-0350 has returned true
      And backlog/ST-0350.md has status pending

      Examples:
        | state   |
        | failed  |
        | blocked |

  Rule: Implementation agent starts a story only when its dependencies inside the run are done
    # actor: Implementation agent
    # @packages/factory/scripts/dispatch::cmd_prepare_wave
    # @packages/factory/scripts/dispatch::cmd_prepare_story

    Scenario: A returned story holds back the chain behind it
      Given ST-0351 depends on ST-0350 and ST-0352 depends on ST-0351
      And ST-0353 depends on none of them
      And the User has returned ST-0350
      When the implementation agent runs dispatch prepare-wave and dispatch prepare-story for the next stories
      Then dispatch refuses to start ST-0351
      And dispatch refuses to start ST-0352
      And ST-0353 starts

    Scenario: prepare-story refuses a returned story and names the return
      Given wave 1 of feature/login has a wave record
      And the User returned ST-0351 in wave 1, so the entry of ST-0351 has returned true
      When the implementation agent runs dispatch prepare-story ST-0351
      Then dispatch exits non-zero
      And the message names the return of ST-0351
      And the ledger records ST-0351 as pending
      # @packages/factory/scripts/dispatch::cmd_prepare_story

    Scenario: Every dependency inside the run is checked
      Given ST-0352 depends on ST-0350 and on ST-0351
      And ST-0350 is done and ST-0351 is dispatched
      When the implementation agent runs dispatch prepare-story ST-0352
      Then dispatch exits non-zero
      And the message names ST-0351

    Scenario: Returned stories stay in the backlog at the end of the run
      Given the User has returned ST-0350
      And ST-0351 waits on ST-0350
      When the run on feature/login ends
      Then ST-0350 and ST-0351 are pending in the ledger and in the backlog

  Rule: Implementation agent merges a unit of work only when premerge-check passes at its branch head
    # actor: Implementation agent
    # @packages/factory/scripts/premerge-check::main

    Scenario: A story branch without a matching review report is refused
      Given story/ST-0350 holds no code-review report whose story is ST-0350 and whose branch_head is an ancestor of its head
      When dispatch merge-story ST-0350 runs premerge-check
      Then premerge-check exits non-zero
      And story/ST-0350 is not merged

    Scenario: An open blocking finding at the branch head is refused and named
      Given the head of story/ST-0350 holds docs/findings/BUG-0091.md with story ST-0350, a blocking severity, and status open
      And the folder where premerge-check runs holds no open finding
      When premerge-check runs on story/ST-0350
      Then premerge-check exits non-zero
      And the message names BUG-0091

    Scenario: A finding that does not block leaves the merge open
      Given the head of story/ST-0350 holds an open minor finding of ST-0350 in docs/findings/register/
      And it holds an open finding file with story ST-0350 that the blocking rule does not count
      And every other check passes
      When premerge-check runs on story/ST-0350
      Then premerge-check exits 0

    Scenario: The gates rerun on the branch head and ignore a stored result
      Given the head of story/ST-0350 fails dependency-check
      And .current-work/dependency-check/ST-0350.json holds a passing result
      When premerge-check runs on story/ST-0350
      Then premerge-check exits non-zero
      And the message names dependency-check
      # @packages/factory/scripts/premerge-check::check_semantic_gates

    Scenario: Without dependency rules, premerge-check skips dependency-check and names the skip
      Given docs/spec/dependency-rules.dsl does not exist
      And every other check of story/ST-0350 passes
      When premerge-check runs on story/ST-0350
      Then premerge-check does not run dependency-check
      And premerge-check prints that it skipped dependency-check because docs/spec/dependency-rules.dsl does not exist
      And premerge-check exits 0

    Scenario: The rerun leaves the primary checkout as it was
      Given the primary checkout holds a changed tracked file and an untracked file
      And the gates pass at the head of story/ST-0350
      When premerge-check runs on story/ST-0350
      Then premerge-check exits 0
      And both files in the primary checkout are unchanged
      And git stash list shows no new stash
      And the temporary worktree under .current-work/feature/login/premerge/ is gone

    Scenario: A worktree left by a crashed premerge-check does not block the next check
      Given a crashed premerge-check left a worktree at .current-work/feature/login/premerge/ST-0350
      And the gates pass at the head of story/ST-0350
      When premerge-check runs on story/ST-0350
      Then premerge-check removes the leftover worktree before it adds its own temporary worktree at that path
      And premerge-check exits 0
      And no worktree is left at .current-work/feature/login/premerge/ST-0350

    Scenario: An untracked test file in the story's checkout takes no part in the rerun
      Given the story's checkout holds an untracked test file
      When premerge-check reruns the gates of ST-0350
      Then the gates run without that test file
      And the untracked test file is back in the story's checkout afterwards

    Scenario: The rerun takes the gate scripts from the installed copy of the calling checkout
      Given the primary checkout holds the installed copy .agent-factory/factory
      And the temporary worktree at the head of story/ST-0350 holds no .agent-factory/
      When premerge-check, called from the primary checkout, reruns the gates of ST-0350
      Then each gate script runs from .agent-factory/factory of the primary checkout
      And each gate script reads the temporary worktree as its source root
      And the temporary worktree builds its own uv environment

    Scenario: The story's review reports and findings do not count toward the file limit
      Given story/ST-0350 holds its code-review report, two finding files with story ST-0350, and one register file with story ST-0350
      When dispatch merge-story ST-0350 runs premerge-check
      Then those files are in the declared scope
      And premerge-check does not count them toward the file limit

    Scenario: A finding of another story outside the scope blocks the merge
      Given story/ST-0350 holds docs/findings/BUG-0092.md with story ST-0351
      When dispatch merge-story ST-0350 runs premerge-check
      Then premerge-check exits non-zero
      And the message names docs/findings/BUG-0092.md

    Scenario: merge-story declares no file scope for a finding
      Given docs/findings/BUG-0090.md has artifact packages/factory/scripts/dispatch:1383
      And story/BUG-0090 changes packages/factory/scripts/dispatch and adds tests/factory/test_dispatch_close.py
      And every other check passes
      When dispatch merge-story BUG-0090 runs premerge-check
      Then premerge-check receives neither --scope nor --scope-glob
      And premerge-check exits 0

    Scenario: The file limit still applies to a finding
      Given story/BUG-0090 changes 21 files outside docs/reviews/ and docs/findings/
      When dispatch merge-story BUG-0090 runs premerge-check with --max-files 20
      Then premerge-check exits non-zero
      And the message names the file limit

    Scenario Outline: The semantic gates run on every story branch name
      Given a branch <branch> whose gates fail
      When premerge-check runs on <branch>
      Then premerge-check exits non-zero
      And the message names the failing gate
      # @packages/factory/scripts/premerge-check::extract_story_id

      Examples:
        | branch          |
        | story/ST-0350   |
        | story/BUG-0090  |

  Rule: Test-strategy agent sets the gates of every story in docs/testing.yaml
    # actor: Test-strategy agent
    # @packages/factory/scripts/premerge-check::resolve_gates

    Scenario: premerge-check runs a gate that the script does not name
      Given docs/testing.yaml has the entry gates.license-check with enabled true and a command
      When premerge-check runs on story/ST-0350
      Then premerge-check runs the command of license-check on the head of story/ST-0350

    Scenario Outline: premerge-check builds the call of a gate that it names
      Given docs/testing.yaml has the entry gates.<gate> with enabled true and no command
      When premerge-check runs on story/ST-0350
      Then premerge-check runs its built-in call of <gate> on the head of story/ST-0350

      Examples:
        | gate             |
        | crap-score       |
        | mutation-testing |

    Scenario: premerge-check reads the old key crap_score
      Given docs/testing.yaml has the entry gates.crap_score with enabled true and threshold 8
      When premerge-check runs on story/ST-0350
      Then premerge-check runs crap-score with the threshold 8 on the head of story/ST-0350
      And docs/testing.yaml still has the entry gates.crap_score

    Scenario: crap-score reads the old key crap_score
      Given docs/testing.yaml has the entry gates.crap_score with threshold 8
      And docs/testing.yaml has no entry gates.crap-score
      When crap-score runs on ST-0350
      Then crap-score checks every function of ST-0350 against the threshold 8
      # @packages/factory/scripts/crap-score::read_threshold_from_testing_yaml

    Scenario: mutation-testing reads the old key mutation_testing
      Given docs/testing.yaml has the entry gates.mutation_testing with a command and timeout_minutes 45
      And docs/testing.yaml has no entry gates.mutation-testing
      When mutation-testing runs on ST-0350
      Then mutation-testing runs that command with a time limit of 45 minutes
      # @packages/factory/scripts/mutation-testing::read_section

    Scenario: The test-strategy agent writes gate keys with hyphens
      Given docs/testing.yaml has no gates section
      When the test-strategy agent records the gate crap-score in docs/testing.yaml
      Then docs/testing.yaml has the entry gates.crap-score
      And docs/testing.yaml has no entry gates.crap_score

    Scenario: A story's quality-gates field adds a gate and keeps the project's gates
      Given docs/testing.yaml has the entry gates.crap-score with enabled true
      And docs/testing.yaml has the entry gates.mutation-testing with enabled false
      And backlog/ST-0350.md has quality-gates [mutation-testing]
      When premerge-check runs on story/ST-0350
      Then premerge-check runs crap-score and mutation-testing

    Scenario Outline: A quality-gates entry that docs/testing.yaml cannot run is refused
      Given backlog/ST-0350.md has quality-gates [license-check]
      And <state>
      When premerge-check runs on story/ST-0350
      Then premerge-check exits non-zero
      And the message names license-check

      Examples:
        | state                                                                 |
        | docs/testing.yaml has no entry gates.license-check                    |
        | docs/testing.yaml has the entry gates.license-check without a command |

    Scenario: The gate list of a story
      Given docs/spec/dependency-rules.dsl exists
      And docs/testing.yaml has the entry gates.crap-score with enabled true
      And backlog/ST-0350.md has a Test Design section
      When premerge-check resolves the gates of ST-0350
      Then the gates are dependency-check, test-design-verify, and crap-score

  Rule: Developer agent learns at commit time that its imports break a dependency rule
    # actor: Developer agent
    # @packages/factory/scripts/dependency-check
    # @packages/factory/config/pre-commit-config.yaml
    # @packages/factory/config/hook-metadata.yaml

    Scenario: A commit that breaks a dependency rule fails in the hook
      Given docs/spec/dependency-rules.dsl forbids an import from module a into module b
      And a staged .py file under the source root of module a imports module b
      When the developer agent commits
      Then the dependency-check hook fails
      And the commit is not created

    Scenario: The hook runs only for a staged Python file under the source root
      Given the commit stages only Markdown files
      When the developer agent commits
      Then the dependency-check hook does not run

    Scenario: A project without dependency rules skips the hook with a notice
      Given docs/spec/dependency-rules.dsl does not exist
      And uv is not installed
      And the dependency-check hook is installed
      When the developer agent commits a staged .py file under the source root
      Then the hook prints "dependency-check: no docs/spec/dependency-rules.dsl, skipped"
      And the hook passes

    Scenario: The script called directly still exits 2 without a rules file
      Given docs/spec/dependency-rules.dsl does not exist
      When the User runs dependency-check directly
      Then dependency-check exits 2

    Scenario: Fitting leaves the hook out of a project without a rules file
      Given docs/spec/dependency-rules.dsl does not exist
      When fitting generates the pre-commit configuration
      Then the configuration holds no agent_factory_hook-dependency-check

    Scenario: The hook has its metadata entry
      When the test test_every_hook_has_metadata runs
      Then hook-metadata.yaml has an entry agent_factory_hook-dependency-check with availability requires-path:docs/spec/dependency-rules.dsl
      And the test passes

  Rule: Implementation agent starts the next wave only after the wave close
    # actor: Implementation agent
    # @packages/factory/scripts/dispatch::cmd_close_wave
    # A wave can close when each of its units of work is done, blocked,
    # failed and stopped, pending after a return, or pending and held back
    # by a returned dependency, directly or through another story.

    Scenario: close-wave refuses while a drift row is not handled
      Given every story of wave 1 is done or has stopped
      And docs/spec/work/spec-feedback-ST-0350.md has a row with status open
      And docs/spec/work/spec-feedback-ST-0351.md has a fixed row about docs/spec/glossary.md, an artifact on the core list
      When the implementation agent runs dispatch close-wave 1
      Then dispatch exits non-zero
      And the message lists both rows with their owners
      And the ledger holds no wave record for wave 1

    Scenario: The implementation agent runs the drift sessions and closes the wave
      Given dispatch close-wave 1 listed a row whose owner is the domain-modeling agent
      When the implementation agent spawns the domain-modeling agent and then its reviewer
      And both commit on feature/login
      And the implementation agent runs dispatch close-wave 1 again
      Then dispatch exits 0
      And the ledger holds a wave record for wave 1

    Scenario: The wave close does not wait for the User's go
      Given a run by hand is active on feature/login
      When the last story of a wave merges or stops
      Then the implementation agent runs dispatch close-wave without a stop for the User

    Scenario: A wave that holds a returned story closes, and the next independent story starts
      Given an orchestrated run is active on feature/login
      And wave 1 holds ST-0350 and ST-0351, and wave 2 holds ST-0352
      And ST-0352 depends on neither ST-0350 nor ST-0351
      And ST-0350 is done
      And the User has returned ST-0351, so the ledger records ST-0351 as pending
      And the entry of ST-0351 has returned true
      And no spec-feedback report of wave 1 has an open row or a fixed row about an artifact on the core list
      When the implementation agent runs dispatch close-wave 1
      Then dispatch exits 0
      And the ledger holds a wave record for wave 1
      And the ledger still records ST-0351 as pending in wave 1
      And dispatch prepare-wave 2 prepares ST-0352

    Scenario: A wave closes while its stories wait on a returned dependency
      Given an orchestrated run is active on feature/login
      And wave 1 holds the serial chain ST-0350, ST-0351, ST-0352
      And ST-0351 depends on ST-0350, and ST-0352 depends on ST-0351
      And the User has returned ST-0350
      And the entry of ST-0350 has returned true
      And ST-0351 and ST-0352 are pending and have never been prepared
      And the entries of ST-0351 and ST-0352 have returned false
      And no spec-feedback report of wave 1 has an open row or a fixed row about an artifact on the core list
      When the implementation agent runs dispatch close-wave 1
      Then dispatch exits 0
      And the ledger holds a wave record for wave 1
      And the ledger still records ST-0350, ST-0351 and ST-0352 as pending in wave 1

    Scenario: A wave closes when dispatch escalate refused a failed story for its scope
      Given wave 1 holds ST-0350 and ST-0351, and ST-0351 is done
      And docs/testing.yaml sets gates.attempts to 3 and gates.attempts_escalated to 3
      And ST-0350 failed three counted attempts on the tier standard and has not escalated
      And dispatch escalate refused ST-0350, because the diff of story/ST-0350 changes a file outside the declared outputs of ST-0350
      And the entry of ST-0350 has reason "escalate refused: scope"
      And no spec-feedback report of wave 1 has an open row or a fixed row about an artifact on the core list
      When the implementation agent runs dispatch close-wave 1
      Then dispatch exits 0
      And the ledger holds a wave record for wave 1
      And the ledger still records ST-0350 as failed on the tier standard
      # @packages/factory/scripts/dispatch::cmd_close_wave

    Scenario Outline: close-wave refuses while a unit of work of the wave can still go on
      Given wave 1 holds ST-0350 and ST-0351
      And ST-0350 is done
      And ST-0351 <state>
      When the implementation agent runs dispatch close-wave 1
      Then dispatch exits non-zero
      And the message names ST-0351
      And the ledger holds no wave record for wave 1

      Examples:
        | state                                                                                 |
        | is dispatched                                                                         |
        | is failed after its first counted attempt on the tier standard, with gates.attempts 3 |
        | is pending with returned false and has no returned dependency                         |

    Scenario: The next wave waits for the wave record
      Given the ledger holds no wave record for wave 1
      When the implementation agent runs dispatch prepare-wave 2
      Then dispatch exits non-zero
      And no story of wave 2 is prepared

    Scenario: In a run by hand, each story is a wave of its own
      Given a run by hand is active on feature/login
      And ST-0350 has merged and its spec-feedback report has an open row
      When the implementation agent runs dispatch prepare-story ST-0351
      Then dispatch exits non-zero
      And ST-0351 is not prepared

  Rule: Implementation agent runs a blocking finding from the feature checks as a unit of work
    # actor: Implementation agent

    Scenario: dispatch add puts an open finding into a new wave
      Given the QA agent filed docs/findings/BUG-0090.md with run feature/login and status open
      When the implementation agent runs dispatch add BUG-0090
      Then the ledger holds BUG-0090 in a new wave of the run on feature/login
      And BUG-0090 runs on the branch story/BUG-0090 on the default tier

    Scenario: The merge of a finding sets it resolved
      Given BUG-0090 is dispatched on story/BUG-0090 with a regression test for the fix
      When dispatch merge-story BUG-0090 merges it into feature/login
      Then docs/findings/BUG-0090.md has status resolved in the merge commit

    Scenario: Returning a finding changes only its ledger entry
      Given BUG-0090 is failed in the run on feature/login
      When the User runs dispatch return-story BUG-0090
      Then the ledger records BUG-0090 as pending
      And the entry of BUG-0090 has returned true
      And docs/findings/BUG-0090.md keeps status open and run feature/login
      And dispatch reads no backlog/BUG-0090.md
      And premerge-check dev feature/login still exits non-zero

    Scenario: Adding a returned finding again reuses its entry
      Given the ledger holds BUG-0090 as pending after a return
      And the entry of BUG-0090 has returned true
      When the implementation agent runs dispatch add BUG-0090
      Then the same ledger entry is in a new wave
      And the entry of BUG-0090 has returned false
      And its attempts restart at the first attempt on the default tier
      And the next attempt runs on the existing branch story/BUG-0090

    Scenario: dispatch add refuses an ID in any state but pending
      Given the ledger holds BUG-0090 as dispatched
      When the implementation agent runs dispatch add BUG-0090
      Then dispatch exits non-zero
      And the message names the state dispatched

    Scenario Outline: dispatch add accepts only an open blocking finding
      Given <case>
      When the implementation agent runs dispatch add <id>
      Then dispatch exits non-zero
      And the message names <reason>
      And the ledger holds no entry for <id>

      Examples:
        | case                                                              | id       | reason                            |
        | backlog/ST-0351.md is a story of the backlog                      | ST-0351  | that add takes only a finding     |
        | docs/findings/BUG-0093.md has status resolved                     | BUG-0093 | the status resolved               |
        | docs/findings/BUG-0094.md has status open and the severity minor  | BUG-0094 | that BUG-0094 does not block      |

    Scenario: A stop refuses dispatch add
      Given docs/findings/BUG-0096.md has severity critical and status open, and its stop is not confirmed
      And docs/findings/BUG-0090.md has run feature/login, a blocking severity, and status open
      When the implementation agent runs dispatch add BUG-0090
      Then dispatch exits 1
      And dispatch prints the stop notice
      And the ledger holds no entry for BUG-0090

    Scenario Outline: The gate-check step files a blocking QA finding for a mutant it cannot resolve
      Given an orchestrated run is active on feature/login
      And mutation-testing leaves a surviving mutant in plan_moves on story/ST-0350
      And the gate-check step can neither kill the mutant nor remove it as dead code, because <cause>
      When the implementation agent files the mutant
      Then docs/findings/QA-0012.md has severity major, status open, owner <owner>, and run feature/login
      # The wave close routes the finding by its owner: Scenario "The wave
      # close routes the open QA findings by owner". A filed mutant counts
      # as resolved for the story merge and blocks the feature merge (RL-G25).

      Examples:
        | cause                                                                                      | owner               |
        | the mutant needs a test that the step could not write within its attempts                  | planning-agent      |
        | the mutant does not change behaviour or a gate setting is wrong, so no test should kill it | test-strategy-agent |

    Scenario: A story merges with its mutant filed, and the QA finding runs in the next wave on the story's code
      Given an orchestrated run is active on feature/login
      And the gate-check step resolved each surviving mutant on story/ST-0350 by one of the three actions of the mutation-testing skill
      And it filed the surviving mutant in plan_moves as docs/findings/QA-0012.md with owner planning-agent and run feature/login
      And the gate-check step committed docs/findings/QA-0012.md on story/ST-0350
      And the entry of that mutant in the list mutants of the mutation-testing result of ST-0350 names QA-0012 in its field finding
      And every other check of story/ST-0350 passes
      When the implementation agent runs dispatch merge-story ST-0350, dispatch close-wave 1, and dispatch add QA-0012
      Then the scope check of premerge-check admits docs/findings/QA-0012.md on story/ST-0350, because the entry in mutants names it
      And the ledger records ST-0350 as done in wave 1
      And docs/findings/QA-0012.md keeps status open and run feature/login
      And QA-0012 is a unit of work of wave 2
      And story/QA-0012 is cut from feature/login after the merge of ST-0350
      And plan_moves on story/QA-0012 holds the code that ST-0350 merged
      And premerge-check dev feature/login exits non-zero and names QA-0012

    Scenario: An unresolved surviving mutant blocks the merge of its story
      Given mutation-testing leaves a surviving mutant in plan_moves on story/ST-0350
      And the gate-check step gave the mutant none of the three actions of the mutation-testing skill, so the mutant is unresolved
      And every other check of story/ST-0350 passes
      When dispatch merge-story ST-0350 runs premerge-check
      Then premerge-check exits non-zero
      And the message names mutation-testing
      And story/ST-0350 is not merged

    Scenario: A non-zero mutation run with an empty mutants list blocks the merge of its story
      Given the mutation command exits non-zero on story/ST-0350 within its time limit
      And the mutation-testing result of ST-0350 holds an empty list mutants
      And every other check of story/ST-0350 passes
      When dispatch merge-story ST-0350 runs premerge-check
      Then premerge-check exits non-zero
      And the message names mutation-testing
      And story/ST-0350 is not merged

    Scenario: The wave close routes the open QA findings by owner
      Given an orchestrated run is active on feature/login
      And wave 1 filed QA-0012 and QA-0013 as open blocking findings with run feature/login
      And QA-0012 has owner planning-agent and QA-0013 has owner test-strategy-agent
      When dispatch close-wave 1 passes
      Then the implementation agent runs dispatch add QA-0012
      And QA-0012 is a unit of work of wave 2
      And the implementation agent spawns the test-strategy agent for QA-0013
      # @packages/factory/agents/implementation-agent.md

    Scenario: The next wave waits until every spawn of the test-strategy agent returns
      Given wave 1 filed QA-0013 and QA-0014 with owner test-strategy-agent
      And dispatch close-wave 1 passed
      And the test-strategy agent for QA-0013 has returned and the one for QA-0014 has not
      When the implementation agent decides the next step
      Then the implementation agent does not run dispatch prepare-wave 2
      And it runs dispatch prepare-wave 2 after the test-strategy agent for QA-0014 returns

    Scenario: A QA finding that the test-strategy agent hands to the planning agent runs in the next wave
      Given wave 1 filed QA-0013 with owner test-strategy-agent and run feature/login
      And dispatch close-wave 1 passed
      And the test-strategy agent for QA-0013 returned with QA-0013 open and owner planning-agent, because a test is missing
      When the implementation agent decides the next step
      Then the implementation agent runs dispatch add QA-0013 before dispatch prepare-wave 2
      And QA-0013 is a unit of work of wave 2

  Rule: User merges the feature branch into dev only after the feature merge check passes
    # actor: User

    Scenario: The feature checks run after the last wave closes
      Given every wave of feature/login has a wave record
      When the feature checks run
      Then the code-review agent writes docs/reviews/code-review-feature-login-2026-11-24.md
      And the QA agent then explores feature/login

    Scenario Outline: premerge-check dev refuses a run that is not ready
      Given the run on feature/login has <condition>
      When the implementation agent runs premerge-check dev feature/login
      Then premerge-check exits non-zero
      And the message names <named>

      Examples:
        | condition                                                      | named                       |
        | ST-0350 as failed                                              | ST-0350                     |
        | ST-0351 as blocked                                             | ST-0351                     |
        | wave 2 without a wave record                                   | wave 2                      |
        | no code-review report of the whole feature with run feature/login | the end-of-feature review |
        | no Fagan report with run feature/login                         | the Fagan report            |
        | no security report with run feature/login                      | the security report         |
        | no bug-hunt report with run feature/login                      | the bug-hunt report         |
        | an open blocking finding with run feature/login                | that finding                |
        | an open blocking finding with story ST-0350                    | that finding                |
        | a failing test suite at the head of feature/login              | the test suite              |

    Scenario: A QA report of another run does not count for the feature merge
      Given docs/reviews/ holds a Fagan report with run feature/search
      And it holds no Fagan report with run feature/login
      When the implementation agent runs premerge-check dev feature/login
      Then premerge-check exits non-zero
      And the message names the Fagan report

    Scenario: The feature merge check runs the test suite in a temporary worktree
      Given the primary checkout holds a changed tracked file and an untracked file
      And every other check of feature/login passes
      When the implementation agent runs premerge-check dev feature/login
      Then the full test suite runs in a temporary worktree at the head of feature/login
      And premerge-check exits 0
      And both files in the primary checkout are unchanged
      And git stash list shows no new stash
      And no temporary worktree of premerge-check is left under .current-work/feature/login/premerge/

    Scenario: A finding of another run does not block the feature merge
      Given an open blocking finding has run feature/search
      And every other check of feature/login passes
      When the implementation agent runs premerge-check dev feature/login
      Then premerge-check exits 0

    Scenario: The User merges after the implementation agent shows the result
      Given premerge-check dev feature/login passed
      When the implementation agent shows the result
      Then the User merges feature/login into dev
      And the implementation agent does not merge into dev

  Rule: User ends a run and leaves no run state behind
    # actor: User

    Scenario: dispatch close removes the state of a finished run
      Given the User has merged feature/login into dev
      And every story of the run is done or pending
      When the User runs dispatch close
      Then .current-work/feature/login/dispatch-ledger.yaml is gone
      And the story worktrees and the worktree of feature/login are gone
      And the gate results of the run's stories under .current-work/ are gone
      And the premerge-check-ok and verify-base-ok markers of the run are gone
      And the briefs and scratch files under .current-work/feature/login/ are gone
      And every merged branch of the run is deleted with git branch -d

    Scenario: dispatch close lists what it cannot delete
      Given story/ST-0351 is not merged
      When the User runs dispatch close
      Then dispatch lists story/ST-0351 as unmerged
      And story/ST-0351 still exists

    Scenario: dispatch close stashes uncommitted files under a name
      Given the worktree of ST-0350 holds an untracked file notes.txt
      And it holds a change to the tracked file src/login.py that is not committed
      When the User runs dispatch close on 2026-11-24
      Then one stash named "run feature/login ST-0350 2026-11-24" holds notes.txt and the change to src/login.py
      And dispatch close lists that stash
      And neither file is put back

    Scenario: dispatch close refuses a run with a stopped story
      Given ST-0350 is failed in the run on feature/login
      When the User runs dispatch close
      Then dispatch exits non-zero
      And the message names ST-0350
      And the ledger of feature/login still exists

    Scenario: dispatch close refuses a feature branch that is not merged into dev
      Given every story of the run on feature/login is done or pending
      And feature/login is not merged into dev
      When the User runs dispatch close
      Then dispatch exits non-zero
      And the message names dispatch close --drop
      And the ledger of feature/login still exists

    Scenario: The User drops a run
      Given the User has returned every unfinished story of the run to the backlog
      When the User runs dispatch close --drop
      Then the run's ledger, worktrees, gate results, markers, and briefs are gone
      And dispatch lists each unmerged branch of the run

    Scenario: The record of a closed run lives in git and the backlog
      Given the User has closed the run on feature/login
      Then the merge commits in dev and the status done in each story file are the record of the run

    Scenario: A temporary premerge worktree left by a crash is removed
      Given .current-work/feature/login/premerge/ST-0350 is left behind after a crash
      When the User runs dispatch close
      Then that worktree is gone

    Scenario Outline: A stop allows the commands that start and merge nothing
      Given docs/findings/BUG-0096.md has severity critical and status open, and its stop is not confirmed
      And <precondition>
      When the User runs <command>
      Then dispatch prints no stop notice
      And <command> does what it does without a stop

      Examples:
        | command                       | precondition                                                       |
        | dispatch return-story ST-0350 | ST-0350 is failed in the run on feature/login                      |
        | dispatch close                | feature/login is merged into dev and every story is done or pending |
        | dispatch close --drop         | every unfinished story of feature/login is returned                |
        | dispatch close --orphans      | a worktree under .current-work/ belongs to no ledger               |

  Rule: User cleans up the runs that no active run owns
    # actor: User

    Scenario: --orphans removes a worktree whose branch is merged into dev
      Given a worktree under .current-work/ belongs to no ledger
      And its branch is merged into dev
      When the User runs dispatch close --orphans
      Then that worktree is gone

    Scenario Outline: --orphans lists a worktree whose branch is not merged into dev
      Given a worktree under .current-work/ belongs to no ledger
      And its branch <merge state>
      When the User runs dispatch close --orphans
      Then that worktree still exists
      And dispatch lists it

      Examples:
        | merge state                                          |
        | is merged into no branch                             |
        | is merged into feature/login and not into dev        |

    Scenario: --orphans removes a ledger without a branch whose stories are all done
      Given a ledger nested inside a worktree names a feature branch that is gone
      And every story in it is done
      When the User runs dispatch close --orphans
      Then that ledger is gone

    Scenario: --orphans lists a ledger without a branch that holds an unfinished story
      Given a ledger names a feature branch that is gone
      And it marks ST-0344 as blocked
      When the User runs dispatch close --orphans
      Then that ledger still exists
      And dispatch lists it

    Scenario: --orphans handles an old ledger with mode automated
      Given a ledger has mode automated and names a feature branch that is gone
      And every story in it is done
      When the User runs dispatch close --orphans
      Then that ledger is gone

    Scenario: --orphans in this repository leaves one ledger without a branch
      Given this repository holds the ledgers of brownfield-onboarding, bug-hunt-fixes, and core-artifact-layout without a branch
      When the User runs dispatch close --orphans
      Then the only ledger without a branch left is the one of core-artifact-layout
      And dispatch lists that ledger

  Rule: User keeps agents from destroying work in every agent tool
    # actor: User
    # @packages/factory/config/hooks/block-dangerous-git.sh
    # Limit: the guardrail reads the command text. A command built from
    # variables, such as D=dispatch followed by "$D close --drop", passes it.

    Scenario Outline: The guardrail refuses agents the two commands that destroy work
      Given an agent session in <tool>
      When the agent issues <command>
      Then the guardrail refuses the command

      Examples:
        | tool        | command                        |
        | Claude Code | dispatch return-story ST-0350  |
        | Claude Code | dispatch close --drop          |
        | Codex       | dispatch return-story ST-0350  |
        | Codex       | dispatch close --drop          |
        | Copilot     | dispatch return-story ST-0350  |
        | Copilot     | dispatch close --drop          |
        | pi          | dispatch return-story ST-0350  |
        | pi          | dispatch close --drop          |
        | OpenCode    | dispatch return-story ST-0350  |
        | OpenCode    | dispatch close --drop          |

    Scenario Outline: The guardrail refuses every form of the two commands
      Given an agent session in Claude Code
      When the agent issues <form>
      Then the guardrail refuses the command

      Examples:
        | form                                                            |
        | .agent-factory/factory/scripts/dispatch return-story ST-0350    |
        | ./.agent-factory/factory/scripts/dispatch close --drop          |
        | packages/factory/scripts/dispatch close --drop                  |
        | git status && dispatch close --drop                             |
        | git status; dispatch return-story ST-0350                       |
        | bash -c "dispatch close --drop"                                 |
        | bash -c "git status && dispatch return-story ST-0350"           |

    Scenario: The guardrail refuses no other dispatch command
      Given a run by hand is active on feature/login
      When an agent issues dispatch merge-story ST-0350
      Then the guardrail allows the command

    Scenario: In an orchestrated run, the implementation agent merges a story without a refusal
      Given an orchestrated run is active on feature/login
      And premerge-check passed for story/ST-0350
      When the implementation agent runs dispatch merge-story ST-0350
      Then the guardrail does not refuse the command

    Scenario: A merge needs a marker for the current head of the branch
      Given .current-work/premerge-check-ok names story/ST-0350 at an older head
      When an agent issues git merge story/ST-0350
      Then the guardrail refuses the command

    Scenario: The guardrail finds the run from the folder's branch
      Given .current-work/feature/search/dispatch-ledger.yaml exists and does not list story/ST-0350
      And no ledger lists story/ST-0350
      When an agent issues git commit on story/ST-0350
      Then the guardrail refuses the command
      And the message names the missing ledger of story/ST-0350

    Scenario: A ledger of another branch does not count on dev
      Given the primary checkout has dev checked out
      And .current-work/feature/login/dispatch-ledger.yaml exists
      When an agent issues git commit in the primary checkout
      Then the guardrail does not apply the ledger check of a commit on a story branch
      And the guardrail allows the commit
      # @packages/factory/config/hooks/block-dangerous-git.sh

    Scenario: pi's guardrail holds no rule of its own
      When pi's extension config/extensions/block-dangerous-git.ts receives a shell command
      Then it passes the command to config/hooks/block-dangerous-git.sh
      And it returns the script's answer
      And it holds no refusal rule of its own
      # @packages/factory/config/extensions/block-dangerous-git.ts

    Scenario: OpenCode has a git guardrail that calls the same script
      Given a real OpenCode session, not a mock
      When the agent issues dispatch close --drop
      Then the plugin config/plugins/agent-factory.ts passes the command to config/hooks/block-dangerous-git.sh
      And the command is refused
      # @packages/factory/config/plugins/agent-factory.ts

    Scenario Outline: OpenCode's git guardrail also checks the execute tool
      Given an agent session in OpenCode
      When the agent calls the execute tool with the JavaScript <code>
      Then the plugin config/plugins/agent-factory.ts passes that JavaScript to config/hooks/block-dangerous-git.sh as the command text
      And the guardrail refuses the call
      # @packages/factory/config/plugins/agent-factory.ts
      # The human-fields guard of the same plugin already treats execute as a shell channel.

      Examples:
        | code                                    |
        | execSync("git push origin dev")         |
        | execSync("dispatch close --drop")       |

  Rule: Factory maintainer finds in the dispatch contract exactly the fields the ledger holds
    # actor: Factory maintainer
    # @packages/factory/scripts/dispatch_lib.py::Ledger
    # @packages/factory/scripts/dispatch_lib.py::StoryEntry

    Scenario: The ledger uses the run's names
      When dispatch init writes a ledger
      Then the ledger has feature_branch and no invocation_branch
      And its mode is orchestrated or by-hand

    Scenario: The ledger holds no field that no command reads
      When dispatch writes a ledger
      Then the ledger has no closed field
      And no story entry has a gate_results field

    Scenario: dispatch reads the old names of a ledger and writes only the new ones
      Given the ledger of feature/login has invocation_branch feature/login and mode automated
      When the implementation agent runs dispatch mark-blocked ST-0350 --reason "design question"
      Then the ledger of feature/login has feature_branch feature/login and no invocation_branch
      And its mode is orchestrated

    Scenario: dispatch close closes a run whose ledger has the old names
      Given the ledger of feature/login has invocation_branch feature/login and mode automated
      And feature/login is merged into dev
      And every story of the run is done
      When the User runs dispatch close
      Then dispatch exits 0
      And .current-work/feature/login/dispatch-ledger.yaml is gone

    Scenario: The dispatch contract lists exactly the fields the code writes
      When the Factory maintainer compares dispatch-contract.md with the fields that Ledger and StoryEntry write
      Then each written field is listed, under the name the code uses
      And no listed field is missing from the code

    Scenario: After a merge, commit_sha holds the merge commit
      Given ST-0350 merged into feature/login
      Then the ledger's commit_sha of ST-0350 is the merge commit
      And dispatch prepare-story of the next story in a serial chain starts from that commit

    Scenario: A new session continues an interrupted run
      Given a session stopped after dispatch mark-dispatched ST-0350
      When a new session runs the next dispatch command
      Then dispatch reads the ledger and the branch state before it acts
      And the run continues from where it stopped

  Rule: Factory maintainer runs the tests against the source, not the installed copy
    # actor: Factory maintainer
    # @packages/factory/scripts/dispatch::cmd_merge_story

    Scenario: merge-story copies nothing into the installed copy
      Given this repository holds packages/factory and .agent-factory/factory
      When dispatch merge-story ST-0350 merges and runs the test suite
      Then .agent-factory/factory is unchanged

    Scenario: The test suite of this repository reads no installed copy of its own
      When the test suite of this repository runs
      Then it runs the code under packages/factory
      And it reads nothing from this repository's .agent-factory/factory
      And a test that installs the Factory into a temporary project still reads that project's .agent-factory

    Scenario: A link to this repository's .agent-factory for scope-lint is no read of the installed copy
      Given tests/factory/test_core_layout_gates.py links this repository's .agent-factory into a baseline copy
      And scope-lint reads .agent-factory/workstreams through that link
      When the Factory maintainer checks the test suite for reads of the installed copy
      Then the check does not count that link as a read of .agent-factory/factory

  Rule: Factory maintainer reads one vocabulary in every Factory document
    # actor: Factory maintainer

    Scenario: No living Factory document uses a replaced term
      When the Factory maintainer searches every Markdown file under packages/factory/ and under docs/spec/ outside docs/spec/work/, and every .feature file under docs/spec/features/
      Then no file uses the terms automated mode, manual mode, mechanized dispatch, invocation branch, gate-check loop, drift report, or main checkout
      And accepted ADRs, superseded proposals, and file names keep their terms
      And a sentence that names a replaced term only to forbid it keeps the term, as this Scenario does
      And the files under docs/spec/work/ keep their terms, because they record earlier passes

    Scenario: No error message uses a replaced term
      When dispatch or premerge-check prints an error message
      Then the message does not say "invocation branch" or "main checkout"

    Scenario: The index of the Factory stays consistent
      When the Factory maintainer runs index-lint --check
      Then index-lint exits 0
