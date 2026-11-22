# scope: global
Feature: CRAP Gate Setup

  The CRAP gate checks the functions that a story changes. CRAP stands for
  Change Risk Anti-Patterns. The score of one function is
  complexity² × (1 − coverage/100)³ + complexity, so it grows with the
  cyclomatic complexity and falls as tests cover more of the function. A
  changed function fails when its score is above the threshold.

  The project measures, and the Factory judges. A measure is one entry
  under gates.crap-score.measures in docs/testing.yaml. It names a files
  pattern, optional exclude patterns, a measuring command, and an optional
  ready command. The measuring command is a project-owned script that
  writes the complexity and the coverage of each function as rows of JSON.
  The ready command answers one question: can the measuring command run
  now? The script crap-score runs the commands, computes the scores, and
  judges the changed functions. It holds no language-specific code.

  The skill setup-crap-score sets the gate up once per project. The
  test-strategy agent runs it, and the User decides every value. The
  script gate-setup-proof plants an untested function and a tested one
  and checks that the gate catches the first and passes the second.

  The exceptions register docs/findings/exceptions.md holds the functions
  that a person accepts above the threshold. Only a person writes it.

  A gate cannot measure when crap-score exits 2. Then nobody has judged
  the code, so no developer agent can fix it. The story stops as blocked
  with the reason "gate cannot measure: crap-score", and dispatch
  resume-gates sends it back to the gate-check step with its code
  unchanged.

  This feature changes Rules of run-lifecycle.feature. The comment
  "changes run-lifecycle" names each Scenario there that changes, and
  docs/spec/work/crap-gate-setup-gaps.md lists them all.

  The examples use the feature branch feature/login, the story ST-0350,
  a threshold of 8, and the measures backend and python. The measure
  backend tests against a Compose stack and has the ready command
  scripts/crap-ready-backend.

  Proposal trace: docs/proposals/crap-gate-setup.md

  Rule: User sets up the CRAP gate through the test-strategy agent and decides every value
    # actor: User
    # @packages/factory/agents/test-strategy-agent.md
    # @packages/factory/skills/crap-score/SKILL.md

    Scenario: The User enables the gate after the proof passes
      Given docs/testing.yaml has no entry gates.crap-score
      When the test-strategy agent runs setup-crap-score
      And the User confirms the tools, the exclusions, the threshold, and the time limit
      And gate-setup-proof passes with the final threshold
      And the User confirms the start of the gate
      Then docs/testing.yaml has the entry gates.crap-score with enabled true
      And the entry holds threshold, timeout_minutes, measured_minutes, and one measure per part of the code

    Scenario: The agent reads the languages and the suites from docs/testing.yaml
      Given docs/testing.yaml lists the suites python and typescript
      When the test-strategy agent runs step 1 of setup-crap-score
      Then the agent proposes one measure for Python and one for TypeScript

    Scenario: The agent tries a candidate tool on a real file before it proposes the tool
      Given the candidate table names radon first for Python
      When the test-strategy agent runs step 2 of setup-crap-score
      Then the agent runs radon on one Python file of the project before it proposes radon

    Scenario: A language outside the candidate table gets tools the agent looked up and tried
      Given the project has Go code and the candidate table has no row for Go
      When the test-strategy agent runs step 2 of setup-crap-score
      Then the agent looks up complexity and coverage tools for Go
      And the agent tries each proposed tool on a real Go file of the project

    Scenario: The agent proposes each exclusion with a reason
      Given the coverage of packages/server/backend/src/db/alembic/versions/ depends on the state of a local database
      When the test-strategy agent runs step 3 of setup-crap-score
      Then the agent proposes the exclude pattern "**/db/alembic/versions/**"
      And the proposal names the database state as the reason

    Scenario: The agent writes docs/testing.yaml only after the User confirms
      When the test-strategy agent runs step 4 of setup-crap-score
      Then the agent shows the change to docs/testing.yaml with the proposed threshold and time limit
      And the agent writes docs/testing.yaml only after the User confirms the change
      And the agent writes the entry gates.crap-score with enabled false
      # DEC-18

    Scenario: The agent measures the whole project and reports the failures and the run time
      Given the proof of step 5 passed
      When the test-strategy agent runs step 6 of setup-crap-score
      Then the agent runs crap-score --all on the whole project
      And the agent reports the number of functions that would fail and the run time
      And the User confirms the final threshold and sets timeout_minutes from that run time

    Scenario: Step 6 keeps the measured run time next to the time limit
      Given crap-score --all took 7 minutes in step 6
      And the User sets timeout_minutes to 10
      When the test-strategy agent writes the results of step 6
      Then the entry gates.crap-score in docs/testing.yaml has measured_minutes 7 and timeout_minutes 10
      # DEC-19

    Scenario: A threshold changed in step 6 runs the proof again before the gate is enabled
      Given the proof of step 5 passed with the threshold 8
      And the User changes the threshold to 10 in step 6
      When the test-strategy agent runs step 7 of setup-crap-score
      Then the agent writes the threshold 10 into docs/testing.yaml
      And the agent runs gate-setup-proof again, which reads the threshold 10
      And the gate gets enabled true only after that proof passes and the User confirms
      # DEC-08

    Scenario: A failed proof leaves the gate disabled
      Given gate-setup-proof fails in step 5
      When the test-strategy agent shows the output of the proof
      Then the entry gates.crap-score in docs/testing.yaml keeps enabled false

    Scenario: The setup writes no exception and no commit hook
      When the test-strategy agent completes setup-crap-score
      Then docs/findings/exceptions.md is unchanged
      And .pre-commit-config.yaml has no hook that runs crap-score
      # DEC-05

    Scenario: The setup commits once, after the User confirms the start of the gate
      Given the test-strategy agent has written docs/testing.yaml and scripts/crap-measure-python in steps 4 to 7
      When the User confirms the start of the gate in step 7
      Then the agent commits docs/testing.yaml, the measuring commands, and the ready commands in one commit
      And no earlier step of setup-crap-score makes a commit
      # DEC-32

  Rule: Test-strategy agent checks with gate-setup-proof that the measuring command reports true coverage
    # actor: Test-strategy agent

    Scenario: The proof passes for a measuring command that measures the code of its folder
      Given docs/testing.yaml has the entry gates.crap-score with enabled false and the threshold 8
      And the measure python matches packages/factory/scripts/*
      And setup-crap-score has written .current-work/gate-setup-proof/plant/python/base/packages/factory/scripts/proof-plant with the functions proof_untested and proof_tested, both of complexity 3
      And .current-work/gate-setup-proof/plant/python/base/packages/factory/tests/test_proof_plant.py covers proof_tested fully
      And .current-work/gate-setup-proof/plant/python/gap/packages/factory/tests/test_proof_gap.py holds a failing test
      When the test-strategy agent runs gate-setup-proof --measure python --plant .current-work/gate-setup-proof/plant/python/
      Then the first commit of the proof worktree holds the files of base/ at packages/factory/scripts/proof-plant and packages/factory/tests/test_proof_plant.py
      And the check "Repeatable" passes
      And the check "Catches CRAP" passes, because proof_untested scores 12 and fails
      And the check "Sees the folder" passes, because proof_tested shows 100 % coverage and passes
      And the check "Reports a gap" passes, because the second commit adds the failing test of gap/ and crap-score exits 2
      And gate-setup-proof exits 0
      # DEC-30

    Scenario: The proof copies each subfolder of the plant folder onto the root of its worktree
      Given .current-work/gate-setup-proof/plant/python/base/ holds packages/factory/scripts/proof-plant and packages/factory/tests/test_proof_plant.py
      And .current-work/gate-setup-proof/plant/python/gap/ holds packages/factory/tests/test_proof_gap.py
      When the test-strategy agent runs gate-setup-proof --measure python --plant .current-work/gate-setup-proof/plant/python/
      Then the first commit of the proof worktree adds packages/factory/scripts/proof-plant and packages/factory/tests/test_proof_plant.py
      And the second commit adds packages/factory/tests/test_proof_gap.py
      # DEC-28, DEC-30

    Scenario: The first commit of the proof holds the setup files of the working tree
      Given step 4 has written the entry gates.crap-score with enabled false and the threshold 8 into docs/testing.yaml and has not committed it
      And the measure python names the command scripts/crap-measure-python, which is not committed either
      When the test-strategy agent runs gate-setup-proof --measure python --plant .current-work/gate-setup-proof/plant/python/
      Then the first commit of the proof worktree holds docs/testing.yaml and scripts/crap-measure-python as they are in the working tree
      And the first commit also holds the files of base/
      And crap-score in the proof worktree reads the threshold 8
      # DEC-32

    Scenario: The first commit of the proof lists only the chosen measure
      Given the entry gates.crap-score in docs/testing.yaml lists the measures backend and python
      When the test-strategy agent runs gate-setup-proof --measure python --plant .current-work/gate-setup-proof/plant/python/
      Then the docs/testing.yaml of the first proof commit keeps threshold and timeout_minutes of the entry
      And its gates.crap-score lists only the measure python
      And the proof starts neither scripts/crap-ready-backend nor the measuring command of backend
      # DEC-52

    Scenario: The proof after a changed threshold reads the threshold of the working tree
      Given the User changed the threshold to 10 in step 6 and nothing is committed
      When the test-strategy agent runs gate-setup-proof again in step 7
      Then crap-score in the proof worktree reads the threshold 10
      # DEC-32

    Scenario: The proof reads the threshold from docs/testing.yaml
      Given the entry gates.crap-score in docs/testing.yaml has enabled false and the threshold 8
      When the test-strategy agent runs gate-setup-proof --measure python --plant .current-work/gate-setup-proof/plant/python/
      Then gate-setup-proof judges the planted functions against the threshold 8
      And the call of gate-setup-proof names no threshold
      # DEC-18

    Scenario Outline: The proof fails for a measuring command that hides a fault
      Given the measuring command of the measure python <fault>
      When the test-strategy agent runs gate-setup-proof --measure python --plant .current-work/gate-setup-proof/plant/python/
      Then the check "<check>" fails
      And gate-setup-proof exits 1

      Examples:
        | fault                                                                                                  | check           |
        | gives different rows on two runs of one commit                                                         | Repeatable      |
        | reports 100 % coverage for every function                                                              | Catches CRAP    |
        | finds the planted functions in the proof worktree but takes coverage from a test run in another folder | Sees the folder |
        | exits 0 after a failed test run and reports 0 % coverage                                               | Reports a gap   |

    Scenario Outline: A wrong call of the proof exits 2
      When the test-strategy agent runs gate-setup-proof <call>
      Then gate-setup-proof exits 2
      And the message names <cause>
      And gate-setup-proof runs no check

      Examples:
        | call                                                              | cause                                     |
        | --measure python                                                  | the missing --plant                       |
        | --plant .current-work/gate-setup-proof/plant/python/              | the missing --measure                     |
        | --measure go --plant .current-work/gate-setup-proof/plant/python/ | go, which docs/testing.yaml does not list |
      # DEC-18

    Scenario Outline: Wrong planted code stops the proof with exit 2
      Given the threshold is 8
      And <defect>
      When the test-strategy agent runs gate-setup-proof --measure python --plant .current-work/gate-setup-proof/plant/python/
      Then gate-setup-proof exits 2
      And the message names <cause>
      And gate-setup-proof runs no check

      Examples:
        | defect                                                                          | cause                                                                                               |
        | base/ holds proof-plant at its top level, not at packages/factory/scripts/      | the files pattern packages/factory/scripts/*, which no planted file matches                         |
        | the plant folder has no subfolder gap/                                          | the missing subfolder gap/                                                                          |
        | the plant folder has no subfolder base/                                         | the missing subfolder base/                                                                         |
        | the rows of the measuring command hold no function proof_tested                 | the missing function proof_tested                                                                   |
        | the rows give proof_untested the complexity 9                                   | proof_untested and its complexity 9, which is above the threshold 8                                 |
        | the rows give proof_untested the complexity 3 and proof_tested the complexity 4 | the two complexities 3 and 4, which differ                                                          |
        | the rows give proof_untested and proof_tested the complexity 2                  | the complexity 2, the score 6 at 0 % coverage, and the threshold 8, which the score does not exceed |
      # DEC-28, DEC-30, DEC-31, DEC-60

    Scenario: The proof runs exactly four checks
      When the test-strategy agent runs gate-setup-proof
      Then gate-setup-proof runs the checks "Repeatable", "Catches CRAP", "Sees the folder", and "Reports a gap"
      And gate-setup-proof runs no other check

    Scenario: The proof starts the measuring command without changed code on the current branch
      Given the current branch has no change against its base
      When the test-strategy agent runs gate-setup-proof
      Then the measuring command starts in each of the three gate runs: the two runs of "Repeatable" and the run of "Reports a gap"
      And "Catches CRAP" and "Sees the folder" judge the report of the first run of "Repeatable"
      And each planted function lies in a file that matches the files pattern of the measure
      # @packages/factory/scripts/gate-setup-proof::run_checks

    Scenario: The planted functions are decided by coverage alone
      Given the threshold is 8
      When setup-crap-score writes the planted functions
      Then proof_untested and proof_tested have the same complexity, at or below 8
      And proof_untested scores above 8 at 0 % coverage
      # DEC-31

    Scenario: The proof checks the planted complexity before it judges the checks
      Given the rows give proof_untested and proof_tested the complexity 3
      When gate-setup-proof reads the rows of the first commit
      Then gate-setup-proof checks both complexities against the threshold and against each other
      And only then it judges the check "Catches CRAP"
      # DEC-31

    Scenario: The proof leaves the project's branches unchanged
      Given the tip of dev is commit A and the tip of feature/login is commit B
      When the test-strategy agent runs gate-setup-proof
      Then all four checks run in a temporary worktree of gate-setup-proof
      And the tip of dev is still commit A and the tip of feature/login is still commit B
      And no branch of the project holds a planted function or a planted test

    Scenario: A proof stopped by a signal stops its command first
      Given gate-setup-proof runs the measuring command of python
      When the run receives SIGTERM
      Then gate-setup-proof stops the measuring command of python
      And gate-setup-proof exits 143
      # DEC-56

    Scenario: The proof makes its worktree at a fixed path
      When the test-strategy agent runs gate-setup-proof --measure python --plant .current-work/gate-setup-proof/plant/python/
      Then the temporary worktree of the proof lies at .current-work/gate-setup-proof/worktree
      And no plant folder under .current-work/gate-setup-proof/plant/ can take that path
      # DEC-46, DEC-64

    Scenario: A second proof at the same time is refused
      Given a run of gate-setup-proof holds the lock on the proof worktree
      When the test-strategy agent starts gate-setup-proof --measure python --plant .current-work/gate-setup-proof/plant/python/
      Then the second run exits 2
      And the message names the lock on the proof worktree
      And the first run goes on unchanged
      # DEC-57

    Scenario: The proof switches no git hook off
      Given the project has a reference-transaction hook that refuses every ref update
      When the test-strategy agent runs gate-setup-proof --measure python --plant .current-work/gate-setup-proof/plant/python/
      Then gate-setup-proof exits 2
      And the message names the reference-transaction hook
      # DEC-57

    Scenario: The proof removes a worktree left by a crashed run before it starts
      Given an earlier run of gate-setup-proof crashed and left its worktree at .current-work/gate-setup-proof/worktree
      When the test-strategy agent runs gate-setup-proof --measure python --plant .current-work/gate-setup-proof/plant/python/
      Then gate-setup-proof removes the left worktree before it makes a new one
      And the four checks run in the new worktree
      # DEC-46

  Rule: User measures each part of the code with a measuring command the project owns
    # actor: User

    Scenario: The measuring command writes its rows to the path in GATE_OUTPUT
      Given the measure python has the command scripts/crap-measure-python
      When crap-score runs the measure python
      Then scripts/crap-measure-python writes one JSON array to the path in GATE_OUTPUT
      And each row has the fields file, function, start_line, end_line, complexity, and coverage_pct
      And file is a path relative to the repository root

    Scenario: The measuring command reports the qualified name of a method
      Given packages/server/backend/src/orders/parser.py holds the class Parser with the method parse
      When crap-score runs the measure backend
      Then the row of that method has the function Parser.parse
      # DEC-12

    Scenario: A script without a file ending is measured like any other file
      Given the measure python matches packages/factory/scripts/*
      When crap-score runs the measure python
      Then the rows hold the functions of packages/factory/scripts/finding-lint

    Scenario Outline: A measuring command reports a case it cannot measure with a non-zero exit
      Given <case>
      When crap-score runs the measure backend
      Then scripts/crap-measure-backend exits non-zero
      And its message names <cause>
      And no row reports a function as 0 % covered because of that case

      Examples:
        | case                                                              | cause                         |
        | the test database is at a revision that the code does not know    | the revision of the database  |
        | coverage cannot reach packages/server/backend/src/plugins/load.py | the file that coverage misses |

    Scenario: A measuring command reports a file it cannot parse as a row with parse_error
      Given story/ST-0350 leaves packages/factory/scripts/finding-lint with a syntax error
      When crap-score runs the measure python
      Then scripts/crap-measure-python reports a row for packages/factory/scripts/finding-lint with the field parse_error
      # DEC-34

    Scenario: A measuring command that tests against a service measures the code of its own folder
      Given the measure backend tests against a Compose stack
      When crap-score runs the measure backend in the temporary worktree of premerge-check
      Then the Compose stack serves the code of that temporary worktree

    Scenario: The Python measuring command starts from the Factory template
      When setup-crap-score writes the measuring command for Python
      Then the command holds the radon and coverage.py code of the template
      And the header of the command names the duty to exit non-zero for a case it cannot measure

    Scenario: The project's commands refer to nothing under .agent-factory/
      When setup-crap-score completes
      Then no measuring command, ready command, or tool configuration that it wrote names a path under .agent-factory/

    Scenario: A person runs a measuring command without the Factory
      Given GATE_OUTPUT names the file /tmp/rows.json
      When the User runs scripts/crap-measure-python in the root of the repository
      Then /tmp/rows.json holds the rows of the measure python

    Scenario: crap-score holds no language-specific code
      When the Factory maintainer reads packages/factory/scripts/crap-score
      Then it has no language-specific import and no file pattern of a language
      # @packages/factory/scripts/crap-score::iter_python_files
      # @packages/factory/scripts/crap-score::load_coverage

  Rule: Implementation agent gets one verdict for the functions a story changed
    # actor: Implementation agent
    # @packages/factory/scripts/crap-score::main
    # @packages/factory/scripts/crap-score::crap_formula

    Scenario: A changed function above the threshold fails the gate and is named
      Given story/ST-0350 changes one line inside the function tree_severity of packages/factory/scripts/finding-lint
      And tree_severity has complexity 9 and 100 % coverage
      When crap-score runs with --base feature/login
      Then crap-score exits 1
      And the output names packages/factory/scripts/finding-lint, tree_severity, and the score 9.00

    Scenario: A function above the threshold that the story does not change passes
      Given tree_severity scores 9
      And story/ST-0350 changes no line inside tree_severity
      When crap-score runs with --base feature/login
      Then tree_severity does not fail the gate

    Scenario: A function in which lines were only deleted counts as changed
      Given tree_severity scores 9 after the change
      And story/ST-0350 deletes two lines inside tree_severity and adds no line
      When crap-score runs with --base feature/login
      Then tree_severity fails the gate
      # DEC-15

    Scenario: A deletion between two functions counts for both neighbours
      Given story/ST-0350 deletes the last two lines of tree_severity in packages/factory/scripts/finding-lint
      And in the new file the deletion lies between the end_line of tree_severity and the start_line of bug_bar_level
      When crap-score runs with --base feature/login
      Then crap-score judges tree_severity and bug_bar_level as changed functions
      # DEC-37

    Scenario Outline: A deletion outside every function counts for the last function or for none
      Given tree_severity is the first function and main is the last function of packages/factory/scripts/finding-lint
      And story/ST-0350 deletes two lines <place>
      When crap-score runs with --base feature/login
      Then crap-score judges <judged> as changed

      Examples:
        | place                                  | judged      |
        | below main, at the end of the file     | main        |
        | above tree_severity, among the imports | no function |
      # DEC-51

    Scenario Outline: The gate compares the threshold with the score rounded to two decimals
      Given the threshold is 8
      And story/ST-0350 changes tree_severity, which then scores <score>
      When crap-score runs with --base feature/login
      Then tree_severity gets pass_fail <result>

      Examples:
        | score | result |
        | 8.004 | pass   |
        | 8.006 | fail   |
      # DEC-14

    Scenario: A function changed only by an earlier story on the feature branch does not fail
      Given ST-0349 merged a change inside tree_severity into feature/login
      And story/ST-0350 starts from feature/login and changes no line inside tree_severity
      When crap-score runs with --base feature/login
      Then tree_severity does not fail the gate

    Scenario: A change that the feature branch gets after the story branched does not count
      Given story/ST-0350 starts from feature/login and changes no line inside tree_severity
      And ST-0351 then merges a change inside tree_severity into feature/login
      When crap-score runs on story/ST-0350 with --base feature/login
      Then crap-score takes the changed lines from the diff between the merge base of feature/login and HEAD
      And tree_severity does not fail the gate
      # DEC-29

    Scenario: crap-score --all judges every measured function
      Given tree_severity scores 9 and no commit of story/ST-0350 changes it
      When crap-score runs with --all
      Then tree_severity fails the gate

    Scenario Outline: --base takes any git revision
      Given story/ST-0350 changes one line inside tree_severity, which scores 9
      When crap-score runs with --base <revision>
      Then tree_severity fails the gate

      Examples:
        | revision                                          |
        | feature/login                                     |
        | the commit at the tip of feature/login, by its ID |
      # DEC-42

    Scenario: A call without --base or --all cannot measure
      When crap-score runs with --story-id ST-0350 and neither --base nor --all
      Then crap-score exits 2
      And the message names the missing --base or --all

    Scenario: A call with both --base and --all cannot measure
      When crap-score runs with --base feature/login and --all
      Then crap-score exits 2
      And the message names --base and --all
      # DEC-16

    Scenario: One commit and one state of the exceptions register get the same verdict
      Given the head of story/ST-0350 and the exceptions register on dev do not change
      When crap-score runs twice with --base feature/login
      Then both runs give the same exit code and the same rows

    Scenario: A file that matches an exclude pattern never fails the gate
      Given the measure backend has the exclude pattern "**/db/alembic/versions/**"
      And story/ST-0350 changes a function of packages/server/backend/src/db/alembic/versions/0042_orders.py that scores 20
      When crap-score runs with --base feature/login
      Then that function does not fail the gate

    Scenario Outline: crap-score applies files and exclude to the rows a measuring command reports
      Given the measure backend has the files pattern "packages/server/backend/**" and the exclude pattern "**/db/alembic/versions/**"
      And the measuring command of backend reports a row for <file>
      When crap-score runs with --all
      Then crap-score judges no row of <file>

      Examples:
        | file                                                           |
        | packages/server/backend/src/db/alembic/versions/0042_orders.py |
        | packages/server/frontend/src/main.ts                           |
      # DEC-10

    Scenario Outline: files and exclude use one glob dialect
      Given the measure has the pattern "<pattern>"
      When crap-score checks the path <path> against the pattern
      Then the pattern <result> the path

      Examples:
        | pattern                    | path                                                           | result         |
        | packages/factory/scripts/* | packages/factory/scripts/finding-lint                          | matches        |
        | packages/factory/scripts/* | packages/factory/scripts/lib/report.py                         | does not match |
        | **/db/alembic/versions/**  | packages/server/backend/src/db/alembic/versions/0042_orders.py | matches        |
      # DEC-35

    Scenario: A file the measuring command cannot parse fails the gate
      Given the measuring command of python reports a row for packages/factory/scripts/finding-lint with the field parse_error
      When crap-score runs with --base feature/login
      Then crap-score exits 1
      And the output names packages/factory/scripts/finding-lint and the parse error
      # DEC-34

    Scenario: Two measures that report the same function cannot measure
      Given the measure backend has the files pattern "packages/server/backend/**"
      And the measure python has the files pattern "packages/**/*.py"
      And both measures report the function create_app of packages/server/backend/src/app.py
      When crap-score runs with --all
      Then crap-score exits 2
      And the message names create_app, the measure backend, and the measure python
      # DEC-11, DEC-29

    Scenario: A row that the files pattern drops counts in no duplicate check
      Given the measure backend has the files pattern "packages/server/backend/**"
      And the measure python has the files pattern "packages/factory/scripts/*"
      And both measures report the function create_app of packages/server/backend/src/app.py
      When crap-score runs with --all
      Then crap-score judges create_app once, by the row of the measure backend
      And crap-score does not exit 2 for create_app
      # DEC-29

    Scenario: A file that holds the same qualified name twice cannot measure
      Given the measuring command of backend reports two rows for Parser.parse in packages/server/backend/src/orders/parser.py
      When crap-score runs with --all
      Then crap-score exits 2
      And the message names packages/server/backend/src/orders/parser.py and Parser.parse
      # DEC-12

    Scenario: The measures run one after another in list order
      Given gates.crap-score.measures lists backend and then python
      When crap-score runs
      Then crap-score runs scripts/crap-ready-backend, then the measuring command of backend, then the measuring command of python

    Scenario Outline: An enabled gate without a required value cannot measure
      Given docs/testing.yaml has the entry gates.crap-score with enabled true and no <key>
      When crap-score runs with --base feature/login
      Then crap-score exits 2
      And the message names <key>

      Examples:
        | key             |
        | threshold       |
        | timeout_minutes |
        | measures        |

    Scenario Outline: A measure without a required field cannot measure
      Given the measure backend in docs/testing.yaml has no <field>
      When crap-score runs with --base feature/login
      Then crap-score exits 2
      And the message names the field <field>

      Examples:
        | field   |
        | name    |
        | files   |
        | command |
      # DEC-29

    Scenario Outline: A measure name that is no safe file name or a wrong ready value cannot measure
      Given the measure backend in docs/testing.yaml has <value>
      When crap-score runs with --base feature/login
      Then crap-score exits 2
      And the message names <named>

      Examples:
        | value                 | named                 |
        | the name "../backend" | the name "../backend" |
        | the name "back end/x" | the name "back end/x" |
        | an empty ready value  | the ready value       |
        | a ready value of 5    | the ready value       |
      # DEC-59

    Scenario: An empty measures list cannot measure
      Given docs/testing.yaml has the entry gates.crap-score with enabled true and an empty list measures
      When crap-score runs with --base feature/login
      Then crap-score exits 2
      And the message names the empty list measures
      # BR-128 in docs/spec/validation-rules.md

    Scenario: Two measures with one name cannot measure
      Given gates.crap-score.measures lists two measures with the name python
      When crap-score runs with --base feature/login
      Then crap-score exits 2
      And the message names python and both measures
      # BR-128 in docs/spec/validation-rules.md

    Scenario: A disabled gate that a story names runs in full
      Given docs/testing.yaml has the entry gates.crap-score with enabled false and no timeout_minutes
      And backlog/ST-0350.md has quality-gates [crap-score]
      When the implementation agent runs the gate-check step of ST-0350
      Then crap-score runs as for an enabled gate
      And crap-score exits 2
      And the message names timeout_minutes
      # BR-066 in docs/spec/validation-rules.md

    Scenario: A disabled gate that a story names runs its ready commands
      Given docs/testing.yaml has the entry gates.crap-score with enabled false
      And the measure backend has the ready command scripts/crap-ready-backend
      And backlog/ST-0350.md has quality-gates [crap-score]
      When the implementation agent runs the gate-check step of ST-0350
      Then crap-score runs scripts/crap-ready-backend before the measuring command of backend
      # BR-066 in docs/spec/validation-rules.md, DEC-39

    Scenario: Two runs of a measure with ready commands do not overlap
      Given the measure backend has the ready command scripts/crap-ready-backend
      And the gate-check step of ST-0350 runs crap-score in the worktree of ST-0350
      When the gate-check step of ST-0351 starts crap-score in the worktree of ST-0351 while the first run measures backend
      Then the second run waits for the lock of the measure backend under the git common directory
      And the second run starts scripts/crap-ready-backend only after the first run has finished the measuring command of backend
      # DEC-43

    Scenario: A run whose time limit runs out while it waits for the lock cannot measure
      Given gates.crap-score.timeout_minutes is 10
      And another run holds the lock of the measure backend for more than 10 minutes
      When crap-score runs with --base feature/login
      Then crap-score exits 2
      And the message names the measure backend and the lock it waited for
      # DEC-43

    Scenario: A killed run leaves no lock that makes the next run wait
      Given a run of crap-score held the lock crap-score/backend.lock under the git common directory
      And that run was killed while it measured backend
      And the file crap-score/backend.lock still exists
      When crap-score runs the measure backend
      Then crap-score takes the lock without waiting
      # DEC-47

    Scenario: A measure without ready commands takes no lock
      Given the measure python has no ready command
      And another run of crap-score measures python in the worktree of ST-0351
      When crap-score runs the measure python in the worktree of ST-0350
      Then crap-score starts the measuring command of python without waiting
      # DEC-43

    Scenario Outline: A run stopped by a signal stops its command first and gives no verdict
      Given crap-score runs the measuring command of backend in the gate-check step of ST-0350
      When the run receives <signal>
      Then crap-score stops the measuring command of backend
      And crap-score exits <code>
      And the implementation agent runs crap-score again and records no attempt for ST-0350

      Examples:
        | signal  | code |
        | SIGTERM | 143  |
        | SIGINT  | 130  |
        | SIGHUP  | 129  |
      # DEC-56

    Scenario: The time limit covers the whole gate run
      Given gates.crap-score.timeout_minutes is 10
      And the ready command and the measuring command of backend take 6 minutes together
      And the measuring command of python takes 5 minutes
      When crap-score runs
      Then crap-score stops the measuring command of python when the 10 minutes run out
      And crap-score exits 2
      And the message names the measure python and the limit of 10 minutes

    Scenario: A report in the wrong shape cannot measure
      Given the measuring command of python writes rows without the field end_line
      When crap-score runs
      Then crap-score exits 2
      And the message names the measure python and the field end_line

    Scenario: The shape check covers rows that the filter drops
      Given the measure backend has the files pattern "packages/server/backend/**"
      And the measuring command of backend writes a row for packages/server/frontend/src/main.ts without the field end_line
      When crap-score runs
      Then crap-score exits 2
      And the message names the measure backend and the field end_line
      # DEC-53

    Scenario: A row whose start_line lies above its end_line is in the wrong shape
      Given the measuring command of python writes a row for tree_severity with start_line 40 and end_line 12
      When crap-score runs
      Then crap-score exits 2
      And the message names the measure python, tree_severity, and the two lines
      # DEC-42

    Scenario: The report holds a score and a result for each row
      When crap-score runs with --base feature/login --story-id ST-0350 --report-dir .current-work/crap-score/
      Then .current-work/crap-score/ST-0350.json holds one JSON array
      And each row holds the six measurement fields, crap_score, and pass_fail
      And pass_fail is pass, fail, or accepted
      # @packages/factory/scripts/crap-score::write_report

    Scenario: A new report replaces the earlier report of the same story
      Given .current-work/crap-score/ST-0350.json holds the report of an earlier commit
      When crap-score runs with --story-id ST-0350 --report-dir .current-work/crap-score/
      Then .current-work/crap-score/ST-0350.json holds only the rows of the current run

    Scenario: A run that cannot measure writes no report
      Given .current-work/crap-score/ST-0350.json holds the report of an earlier commit
      And the Compose stack is stopped, so scripts/crap-ready-backend exits 1
      When crap-score runs with --base feature/login --story-id ST-0350 --report-dir .current-work/crap-score/
      Then crap-score exits 2
      And .current-work/crap-score/ST-0350.json still holds the report of the earlier commit
      And the message names the measure backend and scripts/crap-ready-backend
      # DEC-17

    Scenario Outline: Without --story-id the report takes its name from the environment
      Given <source>
      When crap-score runs without --story-id
      Then the report is .current-work/crap-score/<name>.json

      Examples:
        | source                                                     | name     |
        | STORY_ID is ST-0350                                        | ST-0350  |
        | STORY_ID is unset and the current branch is story/ST-0350  | ST-0350  |
        | STORY_ID is unset and the current branch is story/BUG-0090 | BUG-0090 |
        | STORY_ID is unset and git names no current branch          | adhoc    |
      # @packages/factory/scripts/crap-score::detect_story_id
      # DEC-27

    Scenario Outline: The gate-check step runs crap-score in the folder of the story
      Given <way> is active on feature/login
      When the implementation agent runs the gate-check step of ST-0350
      Then crap-score runs from the root of <folder> with --base feature/login
      And the report lies under .current-work/crap-score/ of <folder>

      Examples:
        | way                 | folder                                              |
        | an orchestrated run | the worktree of ST-0350                             |
        | a run by hand       | the primary checkout with story/ST-0350 checked out |

    Scenario: The gate-check step waits for crap-score as a background job
      When the implementation agent runs crap-score in the gate-check step
      Then the implementation agent starts crap-score as a background job
      And the implementation agent reads the verdict only from the exit code of that job

  Rule: User accepts a function above the threshold in the exceptions register
    # actor: User

    Scenario: A function accepted on dev passes and stays visible
      Given the section "## CRAP score" of docs/findings/exceptions.md on dev has a row for packages/factory/scripts/finding-lint and tree_severity with the accepted score 9
      And story/ST-0350 changes one line inside tree_severity, which still scores 9
      When crap-score runs with --base feature/login
      Then tree_severity gets pass_fail accepted
      And crap-score exits 0
      And the output names tree_severity, the score 9.00, and the reason of the row

    Scenario: A change that raises the score above the accepted score fails again
      Given dev accepts tree_severity with the accepted score 9
      And story/ST-0350 adds a branch to tree_severity, which then scores 10
      When crap-score runs with --base feature/login
      Then tree_severity fails the gate

    Scenario: An exceptions-register row names a method by its qualified name
      Given dev accepts Parser.parse of packages/server/backend/src/orders/parser.py with the accepted score 12
      And story/ST-0350 changes Parser.parse and Lexer.parse of that file, which both score 12
      When crap-score runs with --base feature/login
      Then Parser.parse gets pass_fail accepted
      And Lexer.parse fails the gate
      # DEC-12

    Scenario: A function with an exceptions-register row that scores at or below the threshold passes
      Given the threshold is 8
      And dev accepts tree_severity with the accepted score 9
      And story/ST-0350 removes a branch from tree_severity, which then has complexity 8, 100 % coverage, and the score 8
      When crap-score runs with --base feature/login
      Then tree_severity gets pass_fail pass
      And the output shows tree_severity as a plain pass row, without the reason of the exceptions-register row
      # DEC-24, DEC-26

    Scenario Outline: The gate compares the accepted score with the score rounded to two decimals
      Given dev accepts tree_severity with the accepted score 9
      And tree_severity is changed and scores <score>
      When crap-score runs with --base feature/login
      Then tree_severity gets pass_fail <result>

      Examples:
        | score | result   |
        | 9.004 | accepted |
        | 9.006 | fail     |

    Scenario Outline: The rounding rounds half up
      Given dev accepts tree_severity with the accepted score <accepted>
      And story/ST-0350 changes tree_severity, which then has complexity 8 and 87.5 % coverage and scores 8.125
      When crap-score runs with --base feature/login
      Then crap-score rounds the score to 8.13
      And tree_severity gets pass_fail <result>

      Examples:
        | accepted | result   |
        | 8.13     | accepted |
        | 8.12     | fail     |
      # DEC-36

    Scenario: A row that exists only on the story branch does not change the verdict
      Given dev has no docs/findings/exceptions.md
      And story/ST-0350 adds a row that accepts tree_severity with the accepted score 9
      When crap-score runs with --base feature/login
      Then tree_severity fails the gate

    Scenario: crap-score reads only the section for the CRAP score
      Given docs/findings/exceptions.md on dev names tree_severity only in the section "## Mutation testing"
      When crap-score runs with --base feature/login
      Then tree_severity fails the gate

    Scenario: A project without the exceptions register has no exceptions
      Given dev has no docs/findings/exceptions.md
      When crap-score runs with --base feature/login
      Then no function gets pass_fail accepted
      And crap-score does not exit 2 for the missing file

    Scenario: A repository without a branch dev has no exceptions
      Given the repository has no branch dev
      And docs/findings/exceptions.md on story/ST-0350 accepts tree_severity with the accepted score 9
      When crap-score runs with --base feature/login
      Then tree_severity fails the gate
      And the output says that crap-score read no exceptions register, because no branch dev exists
      # DEC-13, DEC-25

    Scenario Outline: crap-score reads the exceptions register only from refs/heads/dev
      Given <case>
      When crap-score runs with --base feature/login
      Then crap-score reads no exceptions register
      And the output says that crap-score read no exceptions register

      Examples:
        | case                                                                     |
        | the repository has the ref refs/remotes/origin/dev and no refs/heads/dev |
        | crap-score runs outside a git repository                                 |
      # DEC-55

    Scenario: Only the first table under the CRAP score section counts
      Given the section "## CRAP score" on dev holds two tables
      And only the second table has a row for tree_severity with the accepted score 9
      When crap-score runs with --base feature/login
      Then tree_severity fails the gate
      # DEC-55

    Scenario Outline: A broken exceptions-register row cannot measure
      Given the section "## CRAP score" on dev has a row <defect>
      When crap-score runs with --base feature/login
      Then crap-score exits 2
      And the message names that row

      Examples:
        | defect                         |
        | with an empty Reason cell      |
        | with the accepted score "nine" |
        | with the accepted score "9e0"  |
        | with the accepted score "+9"   |
      # DEC-55: the accepted score is a plain decimal

    Scenario: A table whose header does not name the five columns cannot measure
      Given the first table under "## CRAP score" on dev has the header File, Function, Score, Reason
      When crap-score runs with --base feature/login
      Then crap-score exits 2
      And the message names the header and the five columns File, Function, Accepted score, Reason, and Accepted by
      # DEC-55

    Scenario: Two exceptions-register rows for one function cannot measure
      Given the section "## CRAP score" on dev has two rows for packages/factory/scripts/finding-lint and tree_severity
      When crap-score runs with --base feature/login
      Then crap-score exits 2
      And the message names both rows
      # DEC-38

  Rule: User keeps agents from writing the exceptions register
    # actor: User
    # @packages/factory/config/hooks/guard-human-fields::check_call
    # @packages/factory/config/hooks/guard-human-fields::guarded

    Scenario Outline: guard-human-fields refuses an agent's write to the exceptions register
      When an agent <call>
      Then guard-human-fields refuses the call
      And docs/findings/exceptions.md is unchanged

      Examples:
        | call                                                                        |
        | writes docs/findings/exceptions.md with its file-writing tool               |
        | edits docs/findings/exceptions.md with its edit tool                        |
        | runs a shell command that redirects output into docs/findings/exceptions.md |

    Scenario: finding-lint passes with the exceptions register present
      Given docs/findings/exceptions.md exists with a section "## CRAP score"
      When finding-lint runs on the repository
      Then finding-lint reports no problem for docs/findings/exceptions.md
      # @packages/factory/scripts/finding-lint::is_finding_path

    Scenario: The stop notice does not report the exceptions register
      Given docs/findings/exceptions.md exists at the head of the current branch
      When dispatch prints its stop notice
      Then the stop notice does not name docs/findings/exceptions.md
      # @packages/factory/scripts/dispatch_lib.py::stop_notice

  Rule: Implementation agent stops a story without a counted attempt when the gate cannot measure
    # actor: Implementation agent
    # @packages/factory/scripts/dispatch::cmd_mark_blocked
    # changes run-lifecycle: Scenario Outline "A story stops in the state that names its cause"

    Scenario Outline: Exit 2 in the gate-check step blocks the story
      Given ST-0350 is dispatched on feature/login
      And <cause>
      When the implementation agent runs crap-score in the gate-check step of ST-0350
      Then crap-score exits 2
      And the implementation agent runs dispatch mark-blocked ST-0350 --reason "gate cannot measure: crap-score"
      And the implementation agent spawns no developer agent
      And the attempts of ST-0350 are unchanged
      And the stop names the gate crap-score and the message of crap-score, which names the cause
      # DEC-17

      Examples:
        | cause                                                                   |
        | scripts/crap-ready-backend exits 1 because the Compose stack is stopped |
        | the measuring command of backend exits 1 because a test failed          |
        | the gate run takes longer than timeout_minutes                          |
        | the measuring command of python writes rows without end_line            |
        | the entry gates.crap-score has no timeout_minutes                       |
        | a row of the exceptions register has the accepted score "nine"          |
        | the measures backend and python both report one function                |

    Scenario: The developer agent commits while the gate cannot measure
      Given the Compose stack is stopped
      When the developer agent commits on story/ST-0350
      Then the commit does not run crap-score
      And the commit lands on story/ST-0350

  Rule: Implementation agent merges a story only when crap-score measures and passes at its branch head
    # actor: Implementation agent
    # @packages/factory/scripts/premerge-check::gate_command
    # @packages/factory/scripts/premerge-check::rerun_gate
    # @packages/factory/scripts/dispatch::cmd_merge_story

    Scenario: premerge-check passes its merge target to crap-score
      Given docs/testing.yaml has the entry gates.crap-score with enabled true
      When dispatch merge-story ST-0350 runs premerge-check against feature/login
      Then premerge-check runs crap-score with --base feature/login and no list of files
      # changes run-lifecycle: Scenario Outline "premerge-check builds the call of a gate that it names"
      # @packages/factory/scripts/premerge-check::gate_command

    Scenario: A story that changes only scripts without a file ending is scored at the merge
      Given story/ST-0350 changes only packages/factory/scripts/finding-lint
      When premerge-check runs on story/ST-0350
      Then crap-score judges the changed functions of packages/factory/scripts/finding-lint
      And premerge-check prints no notice that the story changed no .py file

    Scenario: The measuring command at the merge measures the code of the story branch
      Given story/ST-0350 adds a test that covers tree_severity fully
      When premerge-check reruns crap-score on story/ST-0350
      Then the measuring command runs in .current-work/feature/login/premerge/ST-0350
      And the row of tree_severity shows 100 % coverage

    Scenario Outline: A gate that cannot measure at the merge blocks the story on both ways
      Given <way> is active on feature/login
      And ST-0350 is dispatched
      And every check of premerge-check passes on story/ST-0350 except crap-score, which exits 2
      When the implementation agent runs dispatch merge-story ST-0350
      Then premerge-check exits 3
      And the refusal of premerge-check starts with the line "GATE CANNOT MEASURE: crap-score"
      And the refusal holds the message of crap-score
      And merge-story records ST-0350 as blocked with reason "gate cannot measure: crap-score"
      And the tip of feature/login is the same commit as before the merge-story call

      Examples:
        | way                 |
        | an orchestrated run |
        | a run by hand       |
      # changes run-lifecycle: Scenario "A refused premerge-check sends a story in an orchestrated run back to the gate-check step"
      # changes run-lifecycle: Scenario "A refused premerge-check leaves the primary checkout on the story branch"

    Scenario: The refusal names the failing functions from the report after exit 1
      Given tree_severity fails crap-score at the head of story/ST-0350
      When premerge-check runs on story/ST-0350
      Then crap-score exits 1
      And the refusal of premerge-check names tree_severity from the report of crap-score
      # DEC-54

    Scenario: The exit code of crap-score alone decides at the merge
      Given crap-score exits 0 at the head of story/ST-0350
      And .current-work/crap-score/ST-0350.json holds a row with pass_fail fail from an earlier run
      When premerge-check runs on story/ST-0350
      Then premerge-check passes the gate crap-score
      # DEC-54

    Scenario: After exit 2 premerge-check reads no report
      Given crap-score exits 2 at the head of story/ST-0350
      And .current-work/crap-score/ST-0350.json holds the report of an earlier commit
      When premerge-check runs on story/ST-0350
      Then the refusal of premerge-check holds the message of crap-score and no row of that report
      # DEC-54

    Scenario: A gate that cannot measure beside another failed check keeps the story dispatched
      Given ST-0350 is dispatched
      And crap-score exits 2 on story/ST-0350
      And dependency-check fails on story/ST-0350
      When the implementation agent runs dispatch merge-story ST-0350
      Then premerge-check exits 1
      And the ledger records ST-0350 as dispatched
      # DEC-29: exit 3 only when every other check that ran passed

    Scenario: A failed ready command at the merge stops premerge-check before the test suite
      Given the measure backend has the ready command scripts/crap-ready-backend
      And the Compose stack is stopped, so scripts/crap-ready-backend exits 1
      When premerge-check runs on story/ST-0350
      Then premerge-check exits 3 before it runs the test suite
      And premerge-check runs no gate
      And the refusal names the measure backend and scripts/crap-ready-backend
      # @packages/factory/scripts/premerge-check::check_test_suite

    Scenario: The ready check of premerge-check takes no lock
      Given a run of crap-score in the worktree of ST-0351 holds the lock of the measure backend
      When premerge-check runs its ready check on story/ST-0350
      Then premerge-check runs scripts/crap-ready-backend without waiting for the lock
      # DEC-62

    Scenario: A disabled gate that a story names runs its ready commands at the merge
      Given docs/testing.yaml has the entry gates.crap-score with enabled false
      And backlog/ST-0350.md has quality-gates [crap-score]
      And the Compose stack is stopped, so scripts/crap-ready-backend exits 1
      When premerge-check runs on story/ST-0350
      Then premerge-check runs scripts/crap-ready-backend before the test suite
      And premerge-check exits 3 before it runs the test suite
      # DEC-39

    Scenario: The report of a refused merge stays in the primary checkout
      Given tree_severity fails crap-score at the head of story/ST-0350
      When premerge-check refuses story/ST-0350
      Then the report of crap-score lies at .current-work/crap-score/ST-0350.json of the primary checkout
      And the temporary worktree .current-work/feature/login/premerge/ST-0350 is gone

    Scenario: The feature merge runs no crap-score
      Given docs/testing.yaml has the entry gates.crap-score with enabled true
      When premerge-check dev feature/login runs before the feature merge
      Then premerge-check runs no semantic gate
      And premerge-check does not run crap-score
      # @packages/factory/scripts/premerge-check::is_feature_merge
      # @packages/factory/scripts/premerge-check::main

  Rule: User resumes a story blocked by a gate that cannot measure without new code
    # actor: User
    # @packages/factory/scripts/dispatch_lib.py::VALID_TRANSITIONS
    # changes run-lifecycle: Scenario "A fixed cause lets the story continue in the same run"

    Scenario: resume-gates returns the story to the gate-check step
      Given ST-0350 is blocked with reason "gate cannot measure: crap-score"
      And ST-0350 has two counted attempts
      And the User has started the Compose stack
      When the User tells the implementation agent to continue
      Then the implementation agent runs dispatch resume-gates ST-0350
      And the ledger records ST-0350 as dispatched
      And ST-0350 still has two counted attempts and the branch story/ST-0350 at the same head
      And the implementation agent spawns no developer agent
      And the next step of ST-0350 is the gate-check step

    Scenario: resume-gates returns a finding to the gate-check step
      Given the finding BUG-0090 is blocked with reason "gate cannot measure: crap-score"
      And the User has started the Compose stack
      When the implementation agent runs dispatch resume-gates BUG-0090
      Then the ledger records BUG-0090 as dispatched
      And the implementation agent spawns no developer agent
      And the next step of BUG-0090 is the gate-check step
      # DEC-22

    Scenario Outline: resume-gates refuses any other story
      Given ST-0350 is <state>
      When the implementation agent runs dispatch resume-gates ST-0350
      Then dispatch exits 1
      And the message names the state of ST-0350, and its reason when the entry has one
      And the ledger entry of ST-0350 is unchanged, its reason included
      # DEC-29

      Examples:
        | state                                         |
        | blocked with reason "merge conflict"          |
        | blocked with reason "post-merge test failure" |
        | dispatched                                    |
        | failed                                        |

    Scenario: re-dispatch stays the way back for a story whose code must change
      Given ST-0350 is blocked with reason "gate cannot measure: crap-score"
      And the User decides that the code of ST-0350 must change
      When the implementation agent runs dispatch re-dispatch ST-0350
      Then the ledger records ST-0350 as prepared
      # @packages/factory/scripts/dispatch::cmd_re_dispatch

    Scenario Outline: resume-gates refuses an entry without a story branch
      Given the ledger records ST-0350 as blocked with reason "gate cannot measure: crap-score"
      And <branch state>
      When the implementation agent runs dispatch resume-gates ST-0350
      Then dispatch exits 1
      And the message names the missing branch story/ST-0350
      And the ledger entry of ST-0350 is unchanged

      Examples:
        | branch state                                                 |
        | ST-0350 was marked blocked before dispatch cut story/ST-0350 |
        | git no longer holds the branch story/ST-0350                 |
      # DEC-63

    Scenario: A stop refuses resume-gates
      Given ST-0350 is blocked with reason "gate cannot measure: crap-score"
      And docs/findings/BUG-0096.md has severity critical and status open, and its stop is not confirmed
      When the implementation agent runs dispatch resume-gates ST-0350
      Then dispatch exits 1
      And dispatch prints the stop notice
      And the ledger entry of ST-0350 is unchanged
      # DEC-44

  Rule: User starts a run only when every ready command of an enabled gate passes
    # actor: User
    # @packages/factory/scripts/dispatch::cmd_init

    Scenario: dispatch init runs every ready command once in the primary checkout
      Given docs/testing.yaml has the entry gates.crap-score with enabled true
      And the measure backend has the ready command scripts/crap-ready-backend
      When the User starts a run with dispatch init on feature/login
      Then dispatch init runs scripts/crap-ready-backend once from the root of the primary checkout
      And dispatch init runs it before it cuts the branch feature/login and writes the ledger
      # DEC-23

    Scenario: A failed ready command stops dispatch init and leaves nothing behind
      Given the branch feature/login does not exist
      And the Compose stack is stopped, so scripts/crap-ready-backend exits 1
      When the User starts a run with dispatch init on feature/login
      Then dispatch init exits 1
      And the message names the measure backend and scripts/crap-ready-backend
      And the branch feature/login does not exist
      And .current-work/feature/login/dispatch-ledger.yaml does not exist
      And no story of the run starts
      # DEC-23

    Scenario: A ready command that runs past the time limit stops dispatch init
      Given gates.crap-score.timeout_minutes is 10
      And scripts/crap-ready-backend starts a child process and runs longer than 10 minutes
      When the User starts a run with dispatch init on feature/login
      Then dispatch init stops scripts/crap-ready-backend and its child process after 10 minutes
      And dispatch init exits 1
      And the message names the measure backend and the limit of 10 minutes
      And no branch feature/login, no worktree of feature/login, and no ledger of the run exist
      # DEC-61

    Scenario: The ready check of dispatch init takes no lock
      Given a run of crap-score holds the lock of the measure backend
      When the User starts a run with dispatch init on feature/login
      Then dispatch init runs scripts/crap-ready-backend without waiting for the lock
      # DEC-62

    Scenario: dispatch init runs no ready command of a gate that is not enabled
      Given docs/testing.yaml has the entry gates.crap-score with enabled false
      And the measure backend has the ready command scripts/crap-ready-backend
      When the User starts a run with dispatch init on feature/login
      Then dispatch init does not run scripts/crap-ready-backend

  Rule: User merges stories without a CRAP gate until a person sets it up
    # actor: User
    # @packages/factory/scripts/premerge-check::resolve_gates
    # @packages/factory/scripts/premerge-check::gate_refusal

    Scenario: A project without a gates section runs no crap-score at the merge
      Given docs/testing.yaml has no gates section
      When premerge-check runs on story/ST-0350
      Then premerge-check does not run crap-score
      And premerge-check prints one line that names crap-score with the skill setup-crap-score and mutation-testing with the skill mutation-testing
      And the merge continues with the other checks
      # @packages/factory/scripts/premerge-check::not_set_up_notice
      # @packages/factory/scripts/premerge-check::BUILT_IN_GATES

    Scenario Outline: The line names every built-in gate without an entry
      Given docs/testing.yaml has a gates section with <entries>
      When premerge-check runs on story/ST-0350
      Then premerge-check prints one line that names <named>
      # DEC-20, DEC-33

      Examples:
        | entries                                      | named                                                                       |
        | only the entry gates.license-check           | crap-score with setup-crap-score and mutation-testing with mutation-testing |
        | the entry gates.mutation-testing and no more | crap-score with setup-crap-score                                            |
        | the entry gates.crap-score and no more       | mutation-testing with mutation-testing                                      |

    Scenario: The line leaves out a built-in gate that the story names
      Given docs/testing.yaml has a gates section without the entries crap-score and mutation-testing
      And backlog/ST-0350.md has quality-gates [crap-score]
      When premerge-check runs on story/ST-0350
      Then premerge-check prints one line that names mutation-testing with mutation-testing
      And the line does not name crap-score, because the refusal of ST-0350 names it
      # DEC-50

    Scenario Outline: A story that names crap-score before the setup is refused
      Given docs/testing.yaml has no entry gates.crap-score
      And backlog/ST-0350.md has quality-gates [crap-score]
      When <step> runs for ST-0350
      Then <step> refuses ST-0350 as it refuses a gate that docs/testing.yaml cannot run
      And the refusal names crap-score and the skill setup-crap-score
      And the attempts of ST-0350 are unchanged
      # DEC-21, DEC-58
      # changes run-lifecycle: Scenario Outline "A quality-gates entry that docs/testing.yaml cannot run is refused"

      Examples:
        | step                |
        | the gate-check step |
        | premerge-check      |

    Scenario: The refusal of a gate without an entry is not a gate that cannot measure
      Given docs/testing.yaml has no entry gates.crap-score
      And backlog/ST-0350.md has quality-gates [crap-score]
      When the implementation agent runs dispatch merge-story ST-0350
      Then premerge-check exits 1
      And the ledger records ST-0350 as dispatched
      And the attempts of ST-0350 are unchanged
      # DEC-21, DEC-58

    Scenario: A project set up from the charter template has no CRAP gate
      Given docs/testing.yaml is a copy of packages/factory/rulebooks/templates/charter-testing.yaml
      When premerge-check runs on story/ST-0350
      Then premerge-check does not run crap-score
      And premerge-check prints the line that names crap-score with the skill setup-crap-score
      # DEC-41

    Scenario: The story template and the implementation agent name no default gate
      When the Factory maintainer reads packages/factory/rulebooks/templates/story.md and packages/factory/agents/implementation-agent.md
      Then neither file names a default that runs crap-score alone

  Rule: Factory maintainer reads one CRAP gate contract in every Factory document
    # actor: Factory maintainer

    Scenario: The skill crap-score describes the gate and names no tool and no threshold
      When the Factory maintainer reads packages/factory/skills/crap-score/SKILL.md
      Then the skill describes the measurement format, the formula, the exit codes, the exceptions register, and where the gate runs
      And the skill names no default threshold and no tool
      # DEC-01

    Scenario: The setup skill is in the generated index
      When index-lint --check runs
      Then index-lint exits 0
      And the generated index lists setup-crap-score

    Scenario: The test-strategy agent runs the setup and no gate on a story
      When the Factory maintainer reads packages/factory/agents/test-strategy-agent.md
      Then the agent definition calls setup-crap-score
      And it says that the agent runs gate-setup-proof and the whole-project measurement during setup
      And it says that the agent runs no gate on a story
      And its completion criteria do not say that no gate ran

    Scenario: The implementation agent runs crap-score as a background job
      When the Factory maintainer reads packages/factory/agents/implementation-agent.md
      Then it says that the gate-check step runs crap-score as a background job and waits for its exit

    Scenario: The architecture names exit code 2 of crap-score
      When the Factory maintainer reads docs/adr/0003-test-execution-via-hooks.md and docs/arc42/05_building_block_view.md
      Then ADR-0003 carries the amendment of decision 5 that names crap-score as the exception to the exit-code-only contract
      And arc42 § 5 lists exit code 2 for crap-score
      # DEC-02

    Scenario Outline: The business rules state the gate's behaviour
      When the Factory maintainer reads <rule> in docs/spec/validation-rules.md
      Then <rule> states that <content>

      Examples:
        | rule   | content                                                 |
        | BR-066 | premerge-check runs no gate by default                  |
        | BR-027 | crap-score reads the report of the measuring command    |
        | BR-092 | only the stakeholder writes docs/findings/exceptions.md |
        | BR-116 | a gate that cannot measure is a fourth cause of blocked |
        | BR-124 | merge-story turns exit 3 of premerge-check into blocked |

    Scenario: T-0402 names both proposals
      When the Factory maintainer reads T-0402 in docs/spec/work/todo.md
      Then T-0402 names docs/proposals/crap-gate-setup.md for the CRAP part
      And T-0402 names docs/proposals/mutation-gate.md for the mutation part

  Rule: Factory maintainer runs the CRAP gate on this repository for Python and TypeScript
    # actor: Factory maintainer

    Scenario: The gate is enabled with a measure for Python and one for TypeScript
      When the Factory maintainer reads docs/testing.yaml of this repository
      Then the entry gates.crap-score has enabled true
      And it has one measure for Python and one for TypeScript
      And gate-setup-proof passes for each measure

    Scenario: The TypeScript measure uses the test runner of node
      When the Factory maintainer reads the measuring command of the TypeScript measure
      Then the command runs node --test --experimental-test-coverage

    Scenario: The scripts that start with uv run show measured coverage
      Given packages/factory/scripts/dispatch starts with uv run --script
      When crap-score runs with --all in this repository
      Then every function of the 21 scripts that start with uv run shows measured coverage
      And no exclude pattern matches one of those scripts
      # DEC-04

    Scenario: The time limit covers the measured run time
      When the Factory maintainer reads the entry gates.crap-score in docs/testing.yaml of this repository
      Then the entry has measured_minutes from setup step 6
      And timeout_minutes is at least measured_minutes
      # DEC-19
