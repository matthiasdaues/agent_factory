# scope: global

Feature: Counter IDs

Every new story, finding, todo entry, and ADR takes its number from one
counter on the project's remote. The script next-id claims the number and
prints the ID, such as ST-1001. The remote accepts only one claim per
number, so two branches in two sessions never create the same ID.

The counter is the ref refs/ids/counters on the remote origin. It points at
a claim commit: a commit with no parent on the empty tree. The message of
the claim commit holds a line start=<number>, one line per prefix with the
highest number claimed so far, such as ST=1012, and a random token. A
prefix without a line has claimed nothing yet, and its first claim returns
start plus one.

The prefix list lives in next-id: ST, BUG, SPEC, FAGAN, SEC, RECON, ATAM,
IMPL, T, and ADR. A Factory producer is a skill, agent, convention, or
playbook that tells its reader how to number a new indexed artifact, such
as create-backlog-stories or write-adr.

In the scenarios, a local bare repository stands in for the remote, unless
a scenario names GitHub.

Proposal trace: docs/proposals/counter-ids.md

Rule: User seeds the counter once for a project
\# actor: User

```
Scenario: A seed creates the counter, and every prefix continues above the seed number
  Given the backlog holds ST-0348 and the findings hold BUG-0012
  And refs/ids/counters does not exist on origin
  When the user runs next-id --seed 1000
  Then origin holds refs/ids/counters with the line start=1000
  And next-id prints the seed lines and exits 0
  And the next call of next-id ST prints ST-1001
  And the next call of next-id BUG prints BUG-1001

Scenario: A seed gives the ADR sequence its own start
  Given docs/adr/ holds ADRs up to 0006-short-title.md
  And refs/ids/counters does not exist on origin
  When the user runs next-id --seed 1000 ADR=6
  Then the claim commit holds the lines start=1000 and ADR=0006
  And the next call of next-id ADR prints ADR-0007

Scenario: A seed keeps the names of the existing IDs
  Given the backlog holds backlog/ST-0327.md
  And refs/ids/counters does not exist on origin
  When the user runs next-id --seed 1000
  Then backlog/ST-0327.md keeps its name and its content

Scenario: A seed on a counter in use fails and leaves the counter as it is
  Given refs/ids/counters exists on origin with the line ST=1012
  When the user runs next-id --seed 1000
  Then next-id exits non-zero
  And the message names the remote and refs/ids/counters
  And refs/ids/counters on origin points at the same claim commit as before

Scenario Outline: A seed with a wrong argument fails before it reaches the remote
  Given refs/ids/counters does not exist on origin
  When the user runs next-id --seed <arguments>
  Then next-id exits non-zero
  And the message names <named>
  And origin holds no refs/ids/counters

  Examples:
    | arguments | named                         |
    | 10000     | the argument 10000            |
    | abc       | the argument abc              |
    | 1000 XX=5 | XX and the list of prefixes   |
    | 1000 ST=x | the argument ST=x             |

Scenario: Two seeds at the same time leave exactly one seed
  Given refs/ids/counters does not exist on origin
  When two clones run next-id --seed 1000 at the same time
  Then origin holds exactly one claim commit at refs/ids/counters
  And one call exits 0 and the other call exits non-zero

Scenario: A seed without a remote fails
  Given a clone without the remote origin
  When the user runs next-id --seed 1000 without --remote
  Then next-id exits non-zero
  And the message names origin and --remote

Scenario: A seed on an unreachable remote fails
  Given origin points at a URL that does not answer
  When the user runs next-id --seed 1000
  Then next-id exits non-zero
  And the message names the remote and git's error message

Scenario: A seed on a named remote creates the counter there
  Given a local bare repository at /tmp/remote.git without refs/ids/counters
  When the user runs next-id --seed 1000 --remote /tmp/remote.git
  Then /tmp/remote.git holds refs/ids/counters with the line start=1000
```

Rule: Caller claims the next ID of a prefix
\# actor: User or CLI-Invoked Agent

```
Scenario: A claim prints the next ID and records it on the remote
  Given the claim commit on origin holds the lines start=1000 and ST=1012
  When the caller runs next-id ST
  Then next-id prints ST-1013 on standard output and exits 0
  And the claim commit on origin holds the line ST=1013

Scenario: The first claim of a prefix returns the seed number plus one
  Given the claim commit on origin holds the lines start=1000 and ST=1012
  And the claim commit holds no BUG line
  When the caller runs next-id BUG
  Then next-id prints BUG-1001
  And the claim commit on origin holds the lines BUG=1001 and ST=1012

Scenario: A claim keeps the lines of the other prefixes
  Given the claim commit on origin holds the lines start=1000, ST=1012, and FAGAN=1003
  When the caller runs next-id FAGAN
  Then the claim commit on origin holds the lines start=1000, ST=1012, and FAGAN=1004
  And the token line of the new claim commit differs from the token line of the old one

Scenario Outline: Every prefix of the list can be claimed
  Given the claim commit on origin holds the line start=1000 and no <prefix> line
  When the caller runs next-id <prefix>
  Then next-id prints <prefix>-1001 and exits 0

  Examples:
    | prefix |
    | ST     |
    | BUG    |
    | SPEC   |
    | FAGAN  |
    | SEC    |
    | RECON  |
    | ATAM   |
    | IMPL   |
    | T      |
    | ADR    |

Scenario: A claim works in a clone without a git user name
  Given a clone whose git config holds no user.name and no user.email
  When the caller runs next-id ST
  Then next-id exits 0
  And the claim commit names next-id <next-id@agent-factory.invalid> as author and committer

Scenario: A claim uses the URL of origin after the clone's URL rewrites
  Given the clone's git config rewrites the origin URL with url.<base>.insteadOf
  When the caller runs next-id ST
  Then next-id claims on the rewritten URL that git remote get-url origin prints
```

Rule: Two callers that claim at the same time get different IDs
\# actor: User or CLI-Invoked Agent

```
Scenario: The race test hands out no ID twice and skips no number
  Given two clones of one local bare repository whose counter is seeded
  When the race test runs 20 rounds of two parallel next-id calls
  And in 10 rounds both calls claim ST
  And in the other 10 rounds one call claims ST and the other claims FAGAN
  Then all 40 printed IDs differ
  And no number of ST or FAGAN is skipped
  And every call exits 0

Scenario: A claim that loses the race to another claim tries again
  Given another caller pushes a new claim commit after this claim reads the counter
  When the remote rejects this claim because the lease is stale
  Then next-id waits a random time between 0.1 and 1 second
  And next-id reads the counter again and claims the next free number
```

Rule: Caller sees a failed claim stop and name its reason
\# actor: User or CLI-Invoked Agent

```
Scenario: Ten stale claims in a row end the claim
  Given the remote reports a stale lease on ten claims of ST in a row
  When the caller runs next-id ST
  Then next-id exits non-zero and prints no ID
  And the message names ST and the last number it tried

Scenario: A refusal for another reason ends the claim after one try
  Given the remote refuses every update of refs/ids/counters with a pre-receive hook that prints read-only
  When the caller runs next-id ST
  Then next-id pushes once, exits non-zero, and prints no ID
  And the message holds git's message with read-only

Scenario: A missing counter ends the claim
  Given refs/ids/counters does not exist on origin
  When the caller runs next-id ST
  Then next-id exits non-zero and prints no ID
  And the message names the remote and next-id --seed

Scenario: An unreachable remote ends the claim
  Given origin points at a URL that does not answer
  When the caller runs next-id ST
  Then next-id exits non-zero and prints no ID
  And the message names the remote and git's error message

Scenario: A clone without origin and without --remote cannot claim
  Given a clone without the remote origin
  When the caller runs next-id ST without --remote
  Then next-id exits non-zero and prints no ID
  And the message names origin, --remote, and next-id --seed

Scenario Outline: A prefix outside the list is refused
  When the caller runs next-id <prefix>
  Then next-id exits non-zero and prints no ID
  And the message names <prefix> and the list of prefixes

  Examples:
    | prefix |
    | XX     |
    | PROP   |
    | RETRO  |
```

Rule: Caller claims on a named remote without a clone
\# actor: User or CLI-Invoked Agent, such as a ticket adapter on a machine without a clone

```
Scenario: A claim with --remote uses that remote and not origin
  Given a clone whose origin holds a seeded counter with the line ST=1012
  And a second seeded remote at /tmp/remote.git with the line ST=1040
  When the caller runs next-id ST --remote /tmp/remote.git in the clone
  Then next-id prints ST-1041
  And the claim commit on origin still holds the line ST=1012

Scenario: A claim with --remote works outside any clone
  Given the current directory is not inside a git repository
  And /tmp/remote.git holds a seeded counter
  When the caller runs next-id ST --remote /tmp/remote.git
  Then next-id prints an ST ID and exits 0
```

Rule: Caller's clone stays unchanged by a claim
\# actor: User or CLI-Invoked Agent

```
Scenario: A claim adds no ref and no object to the clone
  Given a clone with a seeded counter on origin
  When the caller runs next-id ST
  Then the clone holds the same refs as before
  And the clone holds the same objects as before

Scenario: A claim deletes its throwaway repository
  Given a clone with a seeded counter on origin
  When the caller runs next-id ST
  Then the temporary directory that next-id created no longer exists after next-id exits
```

Rule: Factory producer takes each new ID from next-id
\# actor: Factory producer

```
Scenario Outline: A producer file tells its reader to call next-id
  Given the producer file <file>
  When the factory maintainer reads its rule for a new <ids> ID
  Then the rule tells the reader to call next-id with the prefix
  And no rule in the file tells the reader to scan for the highest number

  Examples:
    | file                                                     | ids                                    |
    | packages/factory/skills/create-backlog/SKILL.md          | ST                                     |
    | packages/factory/rulebooks/conventions/finding-format.md | SPEC, FAGAN, SEC, BUG, RECON, ATAM, IMPL |
    | packages/factory/playbooks/bug-fix.md                    | BUG                                    |
    | packages/factory/rulebooks/conventions/todo-format.md    | T                                      |
    | packages/factory/skills/write-adr/SKILL.md               | ADR                                    |

Scenario: An ADR keeps its file name form
  Given next-id ADR prints ADR-0007
  When the write-adr skill saves the ADR "Counter ref on the remote"
  Then the file is docs/adr/0007-counter-ref-on-the-remote.md

Scenario: A split story keeps its letter from a scan
  Given the backlog holds backlog/ST-0327.md
  When create-backlog-slice-story splits ST-0327
  Then the new stories are ST-0327A and ST-0327B
  And create-backlog-slice-story calls no next-id

Scenario: A new ID keeps the form of the existing IDs
  When the caller runs next-id ST
  Then the printed ID has the form ST-NNNN with four digits
  And backlog-lint accepts a story file with that ID
```

Rule: CLI-Invoked Agent commits an indexed artifact on any branch
\# actor: CLI-Invoked Agent

```
Scenario Outline: The branching rules allow indexed artifacts on any branch
  Given the file <file>
  When the factory maintainer reads its rule for indexed artifacts
  Then the rule allows an indexed artifact on any branch
  And no rule in the file requires indexed artifacts on dev

  Examples:
    | file                                                       |
    | packages/factory/rulebooks/rules.md § Branching            |
    | packages/factory/rulebooks/conventions/branching-policy.md |
    | packages/factory/agents/planning-agent.md                  |

Scenario: A code review in manual mode files a finding on the story branch
  Given the human names the story branch of ST-1001 in manual mode
  When the code-review agent runs next-id IMPL and gets IMPL-1004
  Then the agent commits docs/findings/IMPL-1004.md on the story branch
```

Rule: CLI-Invoked Agent pushes the claim ref through next-id in both modes
\# actor: CLI-Invoked Agent
\# @packages/factory/config/hooks/block-dangerous-git.sh

```
Scenario Outline: rules.md states the claim push by next-id as an exception
  Given packages/factory/rulebooks/rules.md
  When the factory maintainer reads § <section>
  Then the section states the claim push by next-id as an exception to its push rule
  And the exception holds for <modes>

  Examples:
    | section      | modes                      |
    | Dispatch     | manual mode                |
    | Git workflow | manual and automated mode  |

Scenario: The guardrail hook lets next-id pass
  Given the guardrail hook block-dangerous-git.sh
  When an agent's shell command is next-id ST
  Then the hook exits 0
```

Rule: init-factory tells the user how to seed the counter
\# actor: init-factory
\# @packages/factory/scripts/init-factory::main

```
Scenario: init-factory names the seed command when the counter is missing
  Given origin exists and holds no refs/ids/counters
  When the user runs init-factory
  Then init-factory prints "run `next-id --seed <number>` with a number above your highest ID"
  And origin still holds no refs/ids/counters

Scenario: init-factory names the remote when origin is missing
  Given a project without the remote origin
  When the user runs init-factory
  Then init-factory prints "add the remote `origin`, then run `next-id --seed <number>`"

Scenario: init-factory finishes the install when origin is unreachable
  Given origin points at a URL that does not answer
  When the user runs init-factory
  Then init-factory prints a warning that names the remote
  And init-factory finishes the install and exits 0
```

Rule: Stakeholder checks the claim protocol against GitHub
\# actor: Stakeholder
\# manual check: an agent cannot run it, because it pushes to GitHub

```
Scenario: The race test on a GitHub repository hands out no number twice
  Given the stakeholder has write access to a GitHub repository
  When the stakeholder runs the race test with --remote and the repository's URL
  Then no number is handed out twice
```
