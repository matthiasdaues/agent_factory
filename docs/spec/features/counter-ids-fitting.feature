# scope: global
Feature: Counter IDs fitting

  Every ID claim needs the counter refs/ids/counters, which counter-ids
  defines. Until a seed creates it, every ID claim fails. So the fitting
  gets a step that seeds the counter. VIRGIL, the session agent, leads the
  step. It runs next-id --plan-seed, shows the seed command that the mode
  prints, and runs it after the User confirms.

  The command holds one pair per ID prefix with the highest number in use,
  so every sequence continues without a jump. The mode reads file names,
  the id fields of the register lines, and the todo headings. It never reads
  body text, because body text holds examples such as ST-9999.

  A project without origin keeps the counter in its own .git, which all its
  worktrees share. The git setting agent-factory.counterRemote holds the
  path of the project's main repository, so next-id finds that local
  counter. next-id resolves its remote in this order: --remote, then
  agent-factory.counterRemote, then origin. Once origin exists,
  next-id --move-to-origin moves the counter there.

  Every ID producer names the literal ID prefix of the artifact it creates,
  so no agent picks a prefix from a list. The convention id-prefixes.md
  holds one table of all twelve ID prefixes.

  In the scenarios, a local bare repository stands in for origin.

  Proposal trace: docs/proposals/counter-ids-fitting.md

  Rule: User confirms the seed of the counter in a fitting step
    # actor: User
    # @packages/factory/agents/virgil.md

    Scenario: The seed step follows the hooks step and sets the sixth fitting key
      Given packages/factory/agents/virgil.md § Fitting
      When the User reads the list of fitting steps
      Then step 4 "Seed the ID counter" comes directly after step 3 "Decide on hooks"
      And step 4 sets fitting.counter_seeded in .agent-factory/config/project-context.json

    Scenario: VIRGIL shows the seed command and runs it after the User confirms
      Given origin exists and holds no refs/ids/counters
      And the project holds backlog/ST-0375.md and docs/adr/0032-agents-push-the-claim-ref-through-next-id.md
      When VIRGIL runs next-id --plan-seed in the seed step
      Then VIRGIL shows the command next-id --seed 0 with the pairs ADR=32 and ST=375
      And VIRGIL says that the command creates refs/ids/counters on origin once and that every later ID continues from it
      When the User confirms the command
      Then VIRGIL runs the command
      And origin holds refs/ids/counters
      And fitting.counter_seeded is true

    Scenario: The User declines the seed command
      Given origin exists and holds no refs/ids/counters
      When VIRGIL shows the seed command and the User declines it
      Then VIRGIL runs no seed and names the reason
      And fitting.counter_seeded stays false
      And the next session start lists the seed step as open

    Scenario: An unreachable origin stops the seed step
      Given origin points at a URL that does not answer
      When VIRGIL runs the seed step
      Then VIRGIL runs no seed and names the unreachable remote as the reason
      And fitting.counter_seeded stays false

    Scenario: A counter in use completes the seed step without a seed
      Given origin holds refs/ids/counters
      When VIRGIL runs the seed step
      Then VIRGIL reports that the counter is in use
      And VIRGIL runs no seed
      And fitting.counter_seeded is true

  Rule: VIRGIL points next-id at the project's own repository when origin is missing
    # actor: VIRGIL
    # @packages/factory/agents/virgil.md

    Scenario: VIRGIL sets agent-factory.counterRemote to the main repository before it plans the seed
      Given the project at /work/demo has no origin
      And /work/demo-feature is a second worktree of /work/demo
      When VIRGIL runs the seed step in /work/demo-feature
      Then VIRGIL sets agent-factory.counterRemote to /work/demo before it runs next-id --plan-seed
      And /work/demo is the parent of the directory that git rev-parse --git-common-dir prints

    Scenario: The seed lands in the project's own .git, and a second worktree claims from it
      Given the project at /work/demo has no origin
      And /work/demo-feature is a second worktree of /work/demo
      When the User confirms the seed command in the seed step
      Then /work/demo/.git holds refs/ids/counters
      And fitting.counter_seeded is true
      And next-id ST in /work/demo-feature prints the next ST ID

  Rule: User walks the seed step in a greenfield project
    # actor: User
    # @packages/factory/agents/virgil.md

    Scenario: A greenfield project walks the model matrix step and the seed step
      Given fitting.status is greenfield
      When the User walks the fitting
      Then VIRGIL runs step 0 "Configure the model matrix" and the seed step

    Scenario: A greenfield project seeds with zero, and the first story is ST-0001
      Given fitting.status is greenfield
      And the project holds no indexed artifact
      When VIRGIL runs next-id --plan-seed in the seed step
      Then next-id prints the command next-id --seed 0
      When the User confirms the command
      Then the next ID claim with next-id ST prints ST-0001

  Rule: User sees the fitting finished only when all six fitting keys are true
    # actor: User
    # @packages/factory/scripts/init-factory::_fitting_status

    Scenario: Five true keys leave the fitting unfinished
      Given fitting.model_matrix_configured, fitting.fingerprint_confirmed, fitting.agent_context_populated, fitting.test_regime_detected, and fitting.hooks_decided are true
      And fitting.counter_seeded is false
      When init-factory derives fitting.status
      Then fitting.status is fitting

    Scenario: Six true keys finish the fitting
      Given all six fitting keys are true, fitting.counter_seeded among them
      When init-factory derives fitting.status
      Then fitting.status is fitted

    Scenario Outline: Each orientation file lists six fitting keys
      Given the orientation file <file>
      When the User reads its table of fitting keys
      Then the table holds six keys, and the sixth is counter_seeded
      And the file counts the fitting steps as six

      Examples:
        | file                                      |
        | packages/factory/config/AGENTS.claude.md  |
        | packages/factory/config/AGENTS.codex.md   |
        | packages/factory/config/AGENTS.copilot.md |
        | packages/factory/config/AGENTS.pi.md      |

  Rule: next-id --plan-seed prints one seed command from the highest number of each ID prefix
    # actor: next-id --plan-seed
    # @packages/factory/scripts/next-id::PREFIXES

    Scenario: The highest numbers on all branches make the pairs of the command
      Given origin holds no refs/ids/counters
      And the branch dev holds backlog/ST-0375.md and docs/adr/ up to 0032-agents-push-the-claim-ref-through-next-id.md
      And the branch feature/fitting holds backlog/ST-0380.md
      When the User runs next-id --plan-seed
      Then next-id prints next-id --seed 0 with the pairs ADR=32 and ST=380
      And next-id exits 0
      And the clone and origin hold the same refs as before

    Scenario: Remote-tracking branches count like local branches
      Given origin holds no refs/ids/counters
      And the local branch dev holds backlog/ST-0375.md
      And the remote-tracking branch origin/feature/fitting holds backlog/ST-0380.md
      When the User runs next-id --plan-seed
      Then the command holds the pair ST=380

    Scenario: Body text never counts as an ID in use
      Given origin holds no refs/ids/counters
      And backlog/ST-0214.md quotes ST-9999 as an example in its body text
      And backlog/ST-0375.md is the highest story file
      When the User runs next-id --plan-seed
      Then the command holds the pair ST=375

    Scenario: A gap in a sequence does not lower the pair
      Given origin holds no refs/ids/counters
      And docs/findings/ holds BUG-0003.md and BUG-0012.md and no other BUG file
      When the User runs next-id --plan-seed
      Then the command holds the pair BUG=12

    Scenario: An ID in a register line counts like an ID in a file name
      Given origin holds no refs/ids/counters
      And docs/findings/ holds FAGAN-0004.md
      And a line of docs/findings/register/code.jsonl holds the id FAGAN-0007
      When the User runs next-id --plan-seed
      Then the command holds the pair FAGAN=7

    Scenario: A todo heading counts as an ID in use
      Given origin holds no refs/ids/counters
      And docs/spec/work/todo.md holds the headings ## T-0016 and ## T-0017
      When the User runs next-id --plan-seed
      Then the command holds the pair T=17

    Scenario: An ID prefix without an ID in use gets no pair
      Given origin holds no refs/ids/counters
      And the project holds backlog/ST-0375.md and no other indexed artifact
      When the User runs next-id --plan-seed
      Then next-id prints next-id --seed 0 ST=375
      And the next ID claim with next-id BUG after that seed prints BUG-0001

    Scenario: A project without indexed artifacts gets a seed of zero
      Given origin holds no refs/ids/counters
      And the project holds no indexed artifact
      When the User runs next-id --plan-seed
      Then next-id prints next-id --seed 0

  Rule: next-id --plan-seed counts an old file name by its number and warns about it
    # actor: next-id --plan-seed

    Scenario: A titled name and a split story count, and a name without a number does not
      Given origin holds no refs/ids/counters
      And the clone holds docs/findings/ATAM-0014-some-title.md, backlog/ST-0380A.md, and docs/findings/BUG-HUNT.md
      And the clone holds no other indexed artifact
      When the User runs next-id --plan-seed
      Then the command holds the pairs ATAM=14 and ST=380 and no BUG pair
      And next-id prints a warning that names docs/findings/ATAM-0014-some-title.md
      And next-id prints no warning about backlog/ST-0380A.md or docs/findings/BUG-HUNT.md
      And next-id exits 0

    Scenario: A name with three digits counts by its number and gets a warning
      Given origin holds no refs/ids/counters
      And docs/findings/ holds SPEC-011-title.md and no other SPEC file
      When the User runs next-id --plan-seed
      Then the command holds the pair SPEC=11
      And next-id prints a warning that names docs/findings/SPEC-011-title.md

  Rule: next-id --plan-seed checks the remote before it plans a seed
    # actor: next-id --plan-seed

    Scenario: A counter in use ends the mode without a command
      Given origin holds refs/ids/counters
      When the User runs next-id --plan-seed
      Then next-id prints that the counter is in use on the remote
      And next-id prints no seed command
      And next-id exits 0

    Scenario: A clone without origin and without the setting fails like an ID claim
      Given a clone without the remote origin and without the git setting agent-factory.counterRemote
      When the User runs next-id --plan-seed without --remote
      Then next-id exits non-zero and prints no seed command
      And the message names origin and --remote

    Scenario: An unreachable remote fails like an ID claim
      Given origin points at a URL that does not answer
      When the User runs next-id --plan-seed
      Then next-id exits non-zero and prints no seed command
      And the message names the remote and git's error message
      And the remote shows without its user info

    Scenario: A moved counter names its new remote and advises no seed
      Given the local clone /work/demo-clone has the project path /work/demo as its origin
      And /work/demo/.git holds the marker commit moved=https://***@host/demo.git at refs/ids/counters
      When the User runs next-id --plan-seed in /work/demo-clone
      Then next-id exits non-zero
      And the message names https://***@host/demo.git as the remote that holds the counter
      And the message does not mention --seed

  Rule: ID Producer claims an ID from the local counter in a project without origin
    # actor: ID Producer
    # @packages/factory/scripts/next-id::resolve_remote

    Scenario: The setting points the ID claim at the local counter
      Given the project at /work/demo has no origin
      And agent-factory.counterRemote holds /work/demo
      And /work/demo/.git holds refs/ids/counters with the line ST=0012
      When an ID producer runs next-id ST
      Then next-id prints ST-0013
      And the claim commit in /work/demo/.git holds the line ST=0013

    Scenario: The setting comes before origin, and --remote comes before the setting
      Given agent-factory.counterRemote holds /work/demo, whose counter holds the line ST=0012
      And origin holds a counter with the line ST=0040
      And /tmp/remote.git holds a counter with the line ST=0070
      When an ID producer runs next-id ST
      Then next-id prints ST-0013
      When an ID producer runs next-id ST --remote /tmp/remote.git
      Then next-id prints ST-0071
      And the counter on origin still holds the line ST=0040

    Scenario: A clone without origin and without the setting fails as before
      Given a clone without the remote origin and without the git setting agent-factory.counterRemote
      When an ID producer runs next-id ST without --remote
      Then next-id exits non-zero and prints no ID
      And the message names origin and --remote

    Scenario: A moved counter fails the ID claim and names its new remote
      Given the local clone /work/demo-clone has the project path /work/demo as its origin
      And /work/demo/.git holds the marker commit moved=https://***@host/demo.git at refs/ids/counters
      When an ID producer runs next-id ST in /work/demo-clone
      Then next-id exits non-zero and prints no ID
      And the message names https://***@host/demo.git as the remote that holds the counter
      And the message does not mention --seed

  Rule: VIRGIL offers to move a local counter to origin at the session start
    # actor: VIRGIL

    Scenario: VIRGIL offers the move when the setting and origin both exist
      Given agent-factory.counterRemote is set
      And origin exists
      When a session starts
      Then VIRGIL offers to move the counter to origin
      When the User confirms the move
      Then VIRGIL runs next-id --move-to-origin

    Scenario: VIRGIL offers no move without origin
      Given agent-factory.counterRemote is set
      And the project has no origin
      When a session starts
      Then VIRGIL offers no move

    Scenario: VIRGIL reports a collision with a counter on origin
      Given agent-factory.counterRemote is set
      And origin holds refs/ids/counters
      When VIRGIL runs next-id --move-to-origin after the User confirms the move
      Then VIRGIL reports that two counters exist and names both

    Scenario: The guardrail hook lets the move pass
      Given the guardrail hook block-dangerous-git.sh
      When a CLI-Invoked Agent's shell command is next-id --move-to-origin
      Then the hook exits 0
      # @packages/factory/config/hooks/block-dangerous-git.sh

  Rule: next-id --move-to-origin moves the local counter to an origin without a counter
    # actor: next-id --move-to-origin

    Scenario: The move copies the claim commit to origin and leaves a marker behind
      Given agent-factory.counterRemote holds /work/demo
      And /work/demo/.git holds refs/ids/counters at the claim commit C with the line ST=0012
      And origin at https://user:token@host/demo.git holds no refs/ids/counters
      When the User runs next-id --move-to-origin
      Then origin holds refs/ids/counters at the claim commit C
      And /work/demo/.git holds a marker commit at refs/ids/counters whose message is the one line moved=https://***@host/demo.git
      And the git setting agent-factory.counterRemote no longer exists
      And the next ID claim with next-id ST prints ST-0013 from origin

  Rule: next-id --move-to-origin leaves both counters as they are when origin holds one or the push fails
    # actor: next-id --move-to-origin

    Scenario: A counter on origin refuses the move
      Given /work/demo/.git holds refs/ids/counters at the claim commit C
      And origin holds refs/ids/counters at another claim commit D
      When the User runs next-id --move-to-origin
      Then the message names both counters
      And /work/demo/.git holds refs/ids/counters at C
      And origin holds refs/ids/counters at D
      And agent-factory.counterRemote holds /work/demo

    Scenario: A failed push puts the claim commit back on the local counter
      Given /work/demo/.git holds refs/ids/counters at the claim commit C
      And origin holds no refs/ids/counters
      And the remote refuses every update of refs/ids/counters with a pre-receive hook that prints read-only
      When the User runs next-id --move-to-origin
      Then /work/demo/.git holds refs/ids/counters at C
      And agent-factory.counterRemote holds /work/demo
      And the message holds git's message with read-only

  Rule: next-id --move-to-origin hands out no number twice while ID claims run during the move
    # actor: next-id --move-to-origin

    Scenario: An ID claim between the read and the marker makes the move start again
      Given /work/demo/.git holds refs/ids/counters at the claim commit C with the line ST=0012
      And next-id --move-to-origin has read C
      When an ID claim in a worktree raises the local counter to ST=0013 before the marker is set
      Then the lease on C refuses the marker
      And next-id --move-to-origin reads the local counter again
      And origin receives the claim commit with the line ST=0013

    Scenario: An ID claim after the marker fails and claims nothing
      Given next-id --move-to-origin has set the marker on /work/demo/.git
      When an ID claim in a worktree reads the local counter
      Then the ID claim exits non-zero and prints no ID
      And the message names the remote that holds the counter

  Rule: init-factory derives counter_seeded from the remote that next-id uses
    # actor: init-factory
    # @packages/factory/scripts/init-factory::_derive_fitting_keys

    Scenario Outline: The key follows the counter on the resolved remote
      Given <setting>
      And <origin>
      When the User runs init-factory
      Then fitting.counter_seeded is <value>

      Examples:
        | setting                                                               | origin                                       | value |
        | agent-factory.counterRemote is not set                                | origin holds refs/ids/counters               | true  |
        | agent-factory.counterRemote is not set                                | origin holds no refs/ids/counters            | false |
        | agent-factory.counterRemote is not set                                | the project has no origin                    | false |
        | agent-factory.counterRemote names a repository that holds the counter | origin exists and holds no refs/ids/counters | true  |
        | agent-factory.counterRemote names a repository without the counter    | the project has no origin                    | false |

    Scenario: init-factory checks the counter with git ls-remote and changes no ref
      Given origin holds refs/ids/counters
      When the User runs init-factory
      Then init-factory reads refs/ids/counters with git ls-remote
      And origin holds the same refs as before

    Scenario: An unreachable remote leaves the key as it is
      Given fitting.counter_seeded is true
      And origin points at a URL that does not answer
      When the User runs init-factory
      Then fitting.counter_seeded is still true

    Scenario: A greenfield project follows the same rule
      Given fitting.status is greenfield
      And agent-factory.counterRemote names a repository that holds the counter
      When the User runs init-factory
      Then fitting.counter_seeded is true

  Rule: ID Producer names the literal ID prefix at each step that creates an indexed artifact
    # actor: ID Producer

    Scenario Outline: Each ID producer names next-id with its own ID prefix
      Given the ID producer <file>
      When the User reads its step that creates <artifact>
      Then the step names next-id <prefix>
      And no line of the file holds next-id <TAG>

      Examples:
        | file                                                    | artifact                   | prefix |
        | packages/factory/skills/create-backlog/SKILL.md         | a story                    | ST     |
        | packages/factory/skills/create-backlog-stories/SKILL.md | a story                    | ST     |
        | packages/factory/skills/retrospective/SKILL.md          | a todo entry               | T      |
        | packages/factory/skills/retrospective/SKILL.md          | a backlog story            | ST     |
        | packages/factory/skills/write-adr/SKILL.md              | an ADR                     | ADR    |
        | packages/factory/rulebooks/conventions/todo-format.md   | a todo entry               | T      |
        | packages/factory/playbooks/bug-fix.md                   | a bug finding              | BUG    |
        | packages/factory/skills/inspect-spec/SKILL.md           | a specification finding    | SPEC   |
        | packages/factory/agents/spec-review-agent.md            | a specification finding    | SPEC   |
        | packages/factory/skills/atam-review/SKILL.md            | an architecture risk       | ATAM   |
        | packages/factory/agents/architecture-review-agent.md    | an architecture risk       | ATAM   |
        | packages/factory/skills/maintain-architecture/SKILL.md  | an architecture finding    | ARCH   |
        | packages/factory/agents/code-review-agent.md            | a code review finding      | IMPL   |
        | packages/factory/skills/fagan-review/SKILL.md           | a Fagan finding            | FAGAN  |
        | packages/factory/skills/security-review/SKILL.md        | a security finding         | SEC    |
        | packages/factory/skills/mutation-testing/SKILL.md       | a mutation testing finding | QA     |
        | packages/factory/skills/bug-hunt/SKILL.md               | a bug finding              | BUG    |
        | packages/factory/agents/qa-agent.md                     | a bug finding              | BUG    |
        | packages/factory/skills/reconcile-spec/SKILL.md         | a drift finding            | RECON  |
        | packages/factory/skills/reconcile-spec/SKILL.md         | a code defect              | BUG    |
        | packages/factory/agents/reconciliation-agent.md         | a drift finding            | RECON  |
        | packages/factory/agents/reconciliation-agent.md         | a code defect              | BUG    |

    Scenario: A file that creates two kinds of artifact names one ID prefix at each step
      Given packages/factory/skills/reconcile-spec/SKILL.md
      When the User reads its step that files a drift finding and its step that files a code defect
      Then the first step names next-id RECON
      And the second step names next-id BUG

  Rule: ID Producer that adds a todo entry names next-id T
    # actor: ID Producer

    Scenario: A step that adds a todo entry names next-id T and points to todo-format.md
      Given a review skill that records an open question as an entry in docs/spec/work/todo.md
      When the User reads that step
      Then the step names next-id T
      And the step points to todo-format.md for the form of the entry

    Scenario: A file that only links to todo.md is no ID producer
      Given packages/factory/skills/write-prd/SKILL.md links to entries of docs/spec/work/todo.md
      And the file does not point to todo-format.md
      When the text test for ID producers runs
      Then the text test does not require next-id T in the file

  Rule: User finds every ID prefix in one table in id-prefixes.md
    # actor: User

    Scenario: id-prefixes.md lists the twelve ID prefixes of next-id
      Given packages/factory/rulebooks/conventions/id-prefixes.md
      When the User reads its table
      Then the table holds one row for each of ST, BUG, SPEC, FAGAN, SEC, RECON, ATAM, IMPL, T, ADR, ARCH, and QA
      And each row names the kind of artifact and the ID producer files of that ID prefix

    Scenario Outline: The rulebooks point to id-prefixes.md
      Given the file <file>
      When the User reads its rule on ID prefixes
      Then the rule points to id-prefixes.md

      Examples:
        | file                                                       |
        | packages/factory/rulebooks/rules.md                        |
        | packages/factory/rulebooks/conventions/branching-policy.md |
        | packages/factory/rulebooks/conventions/finding-format.md   |

    Scenario: finding-format.md keeps the review of each tag, with a row for RECON
      Given packages/factory/rulebooks/conventions/finding-format.md
      When the User reads its table of finding tags
      Then each row names the tag and the review that files it
      And the table holds a row for RECON with the reconciliation agent

  Rule: User sees the text test fail when an ID producer or the prefix table drifts from next-id
    # actor: User

    Scenario: The text test fails when an ID producer drops its ID prefix
      Given packages/factory/skills/fagan-review/SKILL.md without next-id FAGAN
      When the User runs the text test for ID producers
      Then the text test fails and names the file and FAGAN

    Scenario: The text test fails when a todo writer does not name next-id T
      Given a skill that points to todo-format.md at a step that adds a todo entry
      And the skill does not name next-id T
      When the User runs the text test for ID producers
      Then the text test fails and names the skill

    Scenario: The text test fails when id-prefixes.md differs from the list in next-id
      Given id-prefixes.md holds a row for a thirteenth ID prefix PROP
      And the list of ID prefixes in next-id does not hold PROP
      When the User runs the text test for ID producers
      Then the text test fails and names PROP
