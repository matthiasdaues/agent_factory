# scope: global
Feature: Finding classification

  A reviewer agent records each problem it finds as a finding: a short record
  that names the artifact, what is wrong, and the fix. The orchestrator is the
  agent that starts each step of a playbook run. It sends a blocking finding
  back to its owner and waits for the fix. So the severity of a finding
  decides how long the review loop runs.

  The reviewer agent does not pick the severity. It records the basis: a set of
  yes/no answers and choices from fixed lists. A fixed rule computes the
  severity from the basis, and the script finding-lint computes it again.
  Every finding uses one scale: critical, major, minor, or note.

  The review class names the rule. It follows the reviewed material, not the
  review that found the problem: document, code, security, architecture, or
  runtime. Text that agents execute is code: playbooks, skills, agent
  definitions, rulebooks, and hook configuration.

  An artifact is in use when something outside the current playbook run
  depends on it: the artifact is on dev or main, at a release tag, or in the
  installed copy, or an artifact that the run did not produce reads it. The
  feature branch of the run does not count. A document is in use only when stories or
  code outside the run encode its statement.

  A finding is blocking when its category is defect or risk and its severity
  is critical or major. A critical finding stops the run until the
  stakeholder confirms the damage checks. A major finding loops back to its owner. A
  minor finding becomes one line in the register of its class and never
  blocks. A note stays in the review report.

  Each project names the git tags that count as releases. The key
  release_tag_patterns in the tracked file docs/factory-settings.yaml holds a
  list of glob patterns, such as ["v[0-9]*"]. The Factory sets no default,
  and init-factory does not write the file.

  The rules live in
  packages/factory/rulebooks/conventions/finding-classification.md. The
  stakeholder is the person who owns the project, as the glossary defines.
  Only the stakeholder confirms a stop, waives a finding, or lowers a filed
  finding. The user runs validate and commits.

  Contracts. The feature changes four outside contracts. Each one has a Rule
  below that states it.
  - The finding file: the frontmatter fields and the body lines of
    docs/findings/<ID>.md (Rule: Reviewer agent files a blocking finding as a
    finding file).
  - The register line: one JSON object per line in
    docs/findings/register/<class>.jsonl, with one JSON Schema per class in
    packages/factory/rulebooks/schemas/ (Rule: Reviewer agent records a minor
    finding as one register line).
  - The child-result envelope: finding_counts with the four keys critical,
    major, minor, and note (Rule: Reviewer agent reports its counts on the
    shared scale).
  - The stop notice that dispatch and premerge-check print (Rule:
    Orchestrator stops the run on a critical finding that the stakeholder has
    not confirmed).

  Proposal trace: docs/proposals/finding-classification.md

  Rule: Reviewer agent finds the classification rules in one rulebook
    # actor: Reviewer agent
    # @packages/factory/rulebooks/conventions/report-format.md
    # @packages/factory/rulebooks/conventions/finding-format.md
    # @packages/factory/rulebooks/principles/owasp-top-10.md

    Scenario: A review skill names its review class and links its class section
      Given finding-classification.md holds a section for each of the five review classes
      When the reviewer agent reads packages/factory/skills/fagan-review/SKILL.md
      Then the skill names the review class code
      And the skill links the section "Class: code" of finding-classification.md

    Scenario Outline: Each review skill and agent in the boundaries names its class
      Given the file <file> reviews material of the class <class>
      When the reviewer agent reads <file>
      Then <file> links the class section for <class> in finding-classification.md
      And <file> defines no severity level of its own

      Examples:
        | file                                                 | class                       |
        | packages/factory/skills/inspect-spec/SKILL.md        | document                    |
        | packages/factory/skills/reconcile-spec/SKILL.md      | document                    |
        | packages/factory/agents/proposal-review-agent.md     | document                    |
        | packages/factory/agents/spec-review-agent.md         | document                    |
        | packages/factory/agents/reconciliation-agent.md      | document                    |
        | packages/factory/skills/fagan-review/SKILL.md        | code                        |
        | packages/factory/agents/code-review-agent.md         | code                        |
        | packages/factory/skills/security-review/SKILL.md     | security                    |
        | packages/factory/skills/atam-review/SKILL.md         | architecture                |
        | packages/factory/agents/architecture-review-agent.md | architecture                |
        | packages/factory/skills/bug-hunt/SKILL.md            | runtime                     |
        | packages/factory/agents/qa-agent.md                  | code, security, and runtime |

    Scenario: The older rulebooks link the new rulebook instead of defining severity
      Given report-format.md has the sections "Category rules" and "Severity"
      And finding-format.md has the section "When to file"
      When the reviewer agent reads these sections and owasp-top-10.md
      Then each of them links finding-classification.md
      And none of them defines a severity level

    Scenario: Each class section gives calibration examples per level
      Given the code class has a real major finding in docs/findings/ and no real critical finding
      When the reviewer agent reads the section "Class: code" before its first classification of the session
      Then the section lists two or three real major findings with their basis
      And it lists one invented critical example that names real project files

  Rule: Reviewer agent classifies a finding by the class of its material
    # actor: Reviewer agent

    Scenario: A document defect that ATAM review finds belongs to the document class
      Given ATAM review finds that ADR-0026 does not define what happens to an untracked file in the path table
      When the reviewer agent classifies the finding
      Then the finding carries source atam-review and review_class document
      And its type is incomplete

    Scenario: A finding in a playbook belongs to the code class
      Given a diagnosis finds that playbooks/feature-addition.md:37 tells the orchestrator to merge before the premerge check
      When the reviewer agent classifies the finding
      Then the finding carries review_class code

    Scenario Outline: The type comes from the vocabulary of the class
      Given a finding of the review class <class>
      When the reviewer agent picks its type
      Then the type is one of <types>

      Examples:
        | class        | types                                                                                                                                                         |
        | document     | incorrect, ambiguous, incomplete, inconsistent, unverifiable, infeasible, untraced, unnecessary, compound, code-defect, spec-stale, undocumented, speculative |
        | code         | function, interface, checking, assignment, timing, algorithm, build, documentation, structure, test                                                           |
        | security     | an OWASP Top 10 category such as A06                                                                                                                          |
        | architecture | risk, non-risk, sensitivity-point, tradeoff-point                                                                                                             |
        | runtime      | crash, hang, wrong-result, data-loss, security, performance, usability, cosmetic                                                                              |

    Scenario: The type of a document or code finding follows the demanded fix
      Given a code finding whose Fix line demands a missing bounds check
      When the reviewer agent picks the type
      Then the type is checking
      And the reviewer agent does not guess where the defect came from

    Scenario: A question becomes a todo entry and no finding
      Given the reviewer agent needs the author's intent before it can classify a problem
      When the reviewer agent records the problem
      Then the problem becomes an entry in docs/spec/work/todo.md
      And no finding file and no register line carries the category question

    Scenario: An observation that names no artifact is not a finding
      Given a retrospective observation such as RETRO-0002 names no artifact
      When the reviewer agent records it
      Then it becomes an action item of its retrospective or an entry in docs/spec/work/todo.md
      And no finding file is written for it

    Scenario: A suggestion of the consequence tree classes describes material that works
      Given a code finding of category suggestion whose basis answers yes to fails_purpose
      When finding-lint runs
      Then it exits 1 and names the file and the rule
      And a suggestion of the document, code, or runtime class answers false to harms_downstream and fails_purpose

    Scenario: A suggestion of another class is at most minor
      Given an architecture finding of category suggestion with importance high and exposure fails
      When the rule computes the severity
      Then the severity is minor

    Scenario: A nitpick label gives a note
      Given a review comment carries the Conventional Comments label nitpick
      When the reviewer agent classifies the comment
      Then the severity is note

  Rule: Reviewer agent gets a document, code, or runtime severity from the consequence tree
    # actor: Reviewer agent

    Scenario Outline: The first yes answer sets the severity
      Given a finding of the class <class> with in_use <in_use>
      And the answers harms_downstream <harms>, fails_purpose <fails>, and raises_cost <cost>
      When the rule computes the severity
      Then the severity is <severity>

      Examples:
        | class    | in_use | harms | fails | cost  | severity |
        | code     | true   | true  | true  | true  | critical |
        | code     | false  | false | true  | true  | major    |
        | document | false  | false | false | true  | minor    |
        | runtime  | false  | false | false | false | note     |

    Scenario: A defect on the feature branch only is major
      Given BUG-0037: an empty story passes verify-story, and a red suite then resets earlier merges
      And the defective lines exist only on feature/core-artifact-ownership
      When the reviewer agent classifies the finding
      Then the basis records in_use false, harms_downstream false, and fails_purpose true
      And the severity is major

    Scenario: The same defect in the installed copy is critical
      Given the defective lines of BUG-0037 also exist in .agent-factory/factory/scripts/
      When the reviewer agent classifies the finding
      Then the basis records in_use true and harms_downstream true
      And the severity is critical

    Scenario: The reviewer agent records all three answers after the first yes
      Given the reviewer agent answers yes to harms_downstream
      When it records the basis
      Then the basis also holds the answers to fails_purpose and raises_cost

    Scenario: A document is in use only through what is built from it
      Given ADR-0026 is accepted and merged on dev
      And no story or code outside the run encodes its statement on the untracked file
      When the reviewer agent classifies the gap that ATAM-0004 names
      Then the basis records in_use false
      And the severity is major

    Scenario: The QA triage table states the consequence and the tree sets the severity
      Given the triage table of a QA strategy lists data loss under the consequence "harm if in use"
      And a bug hunt finds a new migration step that deletes the story files of a test project on the feature branch only
      When the reviewer agent classifies the finding
      Then the severity is major
      And the same defect on dev is critical

  Rule: Reviewer agent gets the severity of a security finding from the bug bar
    # actor: Reviewer agent

    Scenario: SEC-0003 lands at major
      Given every installed lifecycle hook runs usage-capture, which declares tiktoken with no version pin
      And the effect class is execution, which starts at Critical
      And second_breach is yes and the other three preconditions are no
      And the path from the declaration to the execution is traced, so the confidence is proven
      When the rule computes the severity
      Then the level is High
      And the severity is major
      And the rating field holds High

    Scenario Outline: Each yes to a precondition lowers the level one step
      Given the effect class <effect> with the starting level <start>
      And <yes_count> preconditions are answered yes
      When the rule computes the level
      Then the level is <level>

      Examples:
        | effect      | start    | yes_count | level    |
        | secrets     | Critical | 0         | Critical |
        | gate-bypass | High     | 1         | Medium   |
        | limited     | Medium   | 1         | Low      |
        | leak        | Low      | 2         | Low      |

    Scenario Outline: The level maps onto the shared scale
      Given a security finding with the level <level>, in_use <in_use>, and confidence <confidence>
      When the rule maps the level
      Then the severity is <severity>

      Examples:
        | level    | in_use | confidence | severity |
        | Critical | true   | proven     | critical |
        | Critical | true   | plausible  | major    |
        | Critical | false  | proven     | major    |
        | High     | true   | proven     | major    |
        | Medium   | false  | plausible  | major    |
        | Low      | true   | proven     | minor    |

    Scenario: A hardening finding is a suggestion of severity note
      Given the reviewer agent names a missing defense in depth that gives an attacker nothing today
      When the reviewer agent classifies it
      Then the effect class is hardening
      And the finding is a suggestion of severity note

    Scenario: An attack that needs the capability it gains is not a finding
      Given an attack needs write access to the repository
      And it gains only write access to the repository
      When the reviewer agent judges the attack
      Then the reviewer agent records no finding

  Rule: Reviewer agent gets the severity of an architecture risk from the matrix
    # actor: Reviewer agent

    Scenario Outline: Importance and exposure set the severity
      Given a risk against a quality scenario of priority <priority> in arc42 section 10.2
      And the exposure is <exposure>
      And nothing built from the decision is in use
      When the rule computes the severity
      Then the severity is <severity>

      Examples:
        | priority | exposure  | severity |
        | 1        | fails     | major    |
        | 1        | uncertain | major    |
        | 2        | fails     | major    |
        | 2        | uncertain | minor    |

    Scenario: A risk against a released design is critical
      Given a risk against QS-9 "Read-only preflight before installation" that the matrix rates major
      And an installer built from that design is released
      When the rule computes the severity
      Then in_use raises the severity to critical

    Scenario: Non-risks, sensitivity points, and tradeoff points are notes
      Given ATAM review records a non-risk
      When the reviewer agent classifies it
      Then the severity is note
      And the non-risk names the assumptions it rests on

  Rule: Reviewer agent files a blocking finding as a finding file
    # actor: Reviewer agent
    # @packages/factory/rulebooks/templates/finding.md
    # @packages/factory/scripts/next-id

    Scenario: A major code finding carries the new fields
      Given the reviewer agent files a major code finding on packages/factory/scripts/premerge-check:120
      When it writes the finding file from the template
      Then the frontmatter holds id, source, review_class, category, type, severity, basis, rating, override_by, override_reason, stop_confirmed_by, stop_confirmed_reason, artifact, owner, status, and traces
      And override_by, override_reason, stop_confirmed_by, and stop_confirmed_reason are null
      And the body holds the lines "What is wrong:", "Why this severity:", and "Fix:"

    Scenario Outline: The basis has the shape of the class
      Given the reviewer agent files a finding of the class <class>
      When it writes the basis
      Then the basis holds the fields <fields>

      Examples:
        | class        | fields                                                                              |
        | document     | in_use, harms_downstream, fails_purpose, raises_cost                                |
        | code         | in_use, harms_downstream, fails_purpose, raises_cost                                |
        | runtime      | in_use, harms_downstream, fails_purpose, raises_cost                                |
        | security     | effect, second_breach, trusted_access, non_default, user_action, confidence, in_use |
        | architecture | importance, exposure, in_use                                                        |

    Scenario: A critical finding lists its possible damage
      Given the reviewer agent files BUG-0037 as critical
      When it writes the finding file
      Then the body holds the section "## Possible damage"
      And one item reads "merges on dev from dispatch runs since the installed copy was last updated" with a check that compares git log --merges dev with the merges the dispatch log records

    Scenario: The artifact names a line range or a heading
      Given the reviewer agent files a finding
      When it writes the artifact field
      Then the artifact has the form path:line, path:start-end, or path#anchor

    Scenario: The finding takes its ID from next-id
      Given the reviewer agent files a SEC finding
      When it needs an ID
      Then it runs next-id SEC and uses the printed ID

    Scenario: The status values of a finding file
      Given a finding file that carries review_class
      When an agent sets its status
      Then the status is open or resolved
      And only the stakeholder sets the status waived
      And no agent sets the status deferred, because only the migration sets it, on a file without review_class

    Scenario: The stakeholder sets a blocking finding aside with waived, not deferred
      Given FAGAN-0042 is open with severity major and review_class code
      When the stakeholder decides not to fix it now
      Then the stakeholder sets status waived with override_by and override_reason
      And finding-lint rejects status deferred on that file

  Rule: Reviewer agent records a minor finding as one register line
    # actor: Reviewer agent

    Scenario: A minor security finding adds one line to the security register
      Given a security review produces a finding of level Low
      When the reviewer agent records it
      Then docs/findings/register/security.jsonl gains one line at its end
      And no finding file is written for it

    Scenario: A register line holds the fields of a finding
      Given the reviewer agent writes a register line
      When finding-lint checks the line against the register schema of its class, such as finding-register-code.schema.json
      Then the line holds the ID, source, review_class, category, type, severity, artifact, story, finding, basis, the Why this severity sentence, and the reviewed commit
      And the basis has the shape of its class
      And a line that replaces a filed finding also holds override_by and override_reason

    Scenario: Two parallel reviews add lines without touching each other's lines
      Given two reviews on two branches each add one line to docs/findings/register/code.jsonl
      When both branches merge into dev
      Then the register holds both lines
      And no earlier line of the register changed

    Scenario: Two register lines from two branches merge without a conflict
      Given .gitattributes marks docs/findings/register/*.jsonl with merge=union
      And branch A and branch B each append one line to the end of docs/findings/register/code.jsonl
      When branch A merges into dev and then branch B merges into dev
      Then git reports no merge conflict
      And docs/findings/register/code.jsonl holds both new lines

    Scenario: The review loop skips the register
      Given docs/findings/register/code.jsonl holds a line with severity minor
      When the orchestrator greps docs/findings/*.md for status: open
      Then the register line is not in the result

    Scenario: The fix of a minor finding deletes its register line
      Given docs/findings/register/document.jsonl holds the line of RECON-0027
      When the commit that fixes RECON-0027 lands
      Then that commit deletes the line of RECON-0027 from the register
      And git log keeps the deleted line

  Rule: Proposal-review agent rates each Appendix row with two questions
    # actor: Proposal-review agent
    # @packages/factory/agents/proposal-review-agent.md
    # @packages/factory/rulebooks/templates/proposal.md

    Scenario Outline: The first yes answer sets the row severity
      Given a review row of an open proposal
      And the answers fails_purpose <fails> and raises_cost <cost>
      When the proposal-review agent rates the row
      Then the row severity is <severity>

      Examples:
        | fails | cost  | severity |
        | true  | true  | major    |
        | false | true  | minor    |
        | false | false | note     |

    Scenario: A proposal row is never critical
      Given a proposal under review has no stories built from it
      When the proposal-review agent rates a row
      Then the row severity is major, minor, or note

    Scenario: The Finding cell ends with the severity sentence
      Given the proposal-review agent writes a row in adversarial mode
      When it fills the Finding cell
      Then the cell ends with a sentence that starts with "Severity:" and names the deciding answer

    Scenario: A major row blocks acceptance and minor rows stay in the table
      Given a proposal has one open major row and two minor rows
      When the stakeholder asks to set the proposal to accepted
      Then the major row blocks the transition
      And the minor rows stay in the Appendix table and enter no register

    Scenario: The consultative pass writes only notes
      Given a draft proposal
      When the proposal-review agent runs its consultative pass
      Then every row it writes has severity note

  Rule: Reviewer agent reports its counts on the shared scale
    # actor: Reviewer agent
    # @packages/factory/rulebooks/conventions/report-format.md

    Scenario: The envelope carries all four keys
      Given a review files one major finding and records no other finding
      When the reviewer agent returns its child-result envelope
      Then finding_counts is {"critical": 0, "major": 1, "minor": 0, "note": 0}

    Scenario: Claim review counts a BLOCKER under major
      Given adversarial-review records one BLOCKER and one NOTE on a research claim
      When it returns its child-result envelope
      Then finding_counts is {"critical": 0, "major": 1, "minor": 0, "note": 1}
      And adversarial-review keeps its own scale in its records

  Rule: finding-lint rejects a finding whose recorded values break the classification rules
    # actor: finding-lint

    Scenario: A severity that does not match the basis fails
      Given a code finding with severity minor and a basis that answers yes to fails_purpose
      When finding-lint runs
      Then it exits 1
      And it names the file and the rule

    Scenario Outline: A severity mismatch fails in every review class
      Given a finding of the class <class> whose recorded severity differs from the severity of its basis
      When finding-lint runs
      Then it exits 1

      Examples:
        | class        |
        | document     |
        | code         |
        | security     |
        | architecture |
        | runtime      |

    Scenario Outline: A structural rule is broken
      Given a finding file that <violation>
      When finding-lint runs
      Then it exits 1 and names the file and the rule

      Examples:
        | violation                                                                        |
        | holds a type outside the vocabulary of its class                                 |
        | has the category risk in the code class                                          |
        | holds a basis without the field fails_purpose in the code class                  |
        | is a suggestion of severity major                                                |
        | has the category question                                                        |
        | lacks the line "Why this severity:"                                              |
        | has status waived and an empty override_reason                                   |
        | has status waived and severity minor                                             |
        | has status waived, severity critical, and no stop_confirmed_by                   |
        | has status resolved, severity critical, and no stop_confirmed_by                 |
        | has status resolved, severity critical, and an empty stop_confirmed_reason       |
        | has the status fixed, which is not open, resolved, deferred, or waived           |
        | carries review_class and has status deferred                                     |
        | is a code suggestion whose basis answers yes to fails_purpose                    |
        | has status open and severity minor                                               |
        | has status open and severity note                                                |
        | has the ID BUG-0067, which is also the ID of a register line                     |
        | has severity critical and no section "## Possible damage"                        |
        | has severity major and a section "## Possible damage"                            |
        | sets stop_confirmed_by and leaves stop_confirmed_reason empty                    |
        | sets stop_confirmed_by on a major finding                                        |
        | names the artifact packages/factory/scripts/dispatch without a line or a heading |
        | answers harms_downstream true and in_use false in the code class                 |

    Scenario Outline: A minor line of the consequence tree classes needs its fails_purpose sentence
      Given a line in docs/findings/register/<class>.jsonl with severity minor
      And its Why this severity sentence does not contain the marker "no to fails_purpose"
      When finding-lint runs
      Then it exits 1 and names the register file, the ID, and the rule

      Examples:
        | class    |
        | document |
        | code     |
        | runtime  |

    Scenario Outline: A minor security or architecture line needs no fails_purpose sentence
      Given a line in docs/findings/register/<class>.jsonl with severity minor and a basis that matches it
      And its Why this severity sentence gives <reason> and does not contain the marker "no to fails_purpose"
      When finding-lint runs
      Then it does not reject the line for a missing fails_purpose sentence

      Examples:
        | class        | reason                          |
        | security     | one sentence per precondition   |
        | architecture | the importance and the exposure |

    Scenario: A register line whose severity does not match its basis fails
      Given a line in docs/findings/register/document.jsonl with severity minor and a basis that answers yes to fails_purpose
      When finding-lint runs
      Then it exits 1

    Scenario: An agent cannot move a filed finding into the register
      Given HEAD holds docs/findings/FAGAN-0042.md with severity major and review_class code
      And an agent changes its answer to fails_purpose to false
      And the agent removes the file and adds a line of FAGAN-0042 to docs/findings/register/code.jsonl without override_by and override_reason
      When finding-lint runs
      Then it exits 1 and names FAGAN-0042 and the rule

    Scenario: An agent cannot lower the severity of a finding file
      Given HEAD holds docs/findings/BUG-0037.md with severity critical, review_class code, and no stop_confirmed_by
      And an agent changes its answer to harms_downstream to false, so the file has severity major
      And override_by and override_reason are null
      When finding-lint runs
      Then it exits 1 and names BUG-0037 and the rule

    Scenario: The stakeholder lowers a filed finding with the override fields
      Given HEAD holds docs/findings/FAGAN-0042.md with severity major and review_class code
      And the stakeholder changes its answer to fails_purpose to false
      And the stakeholder removes the file and adds a line of FAGAN-0042 to docs/findings/register/code.jsonl with override_by and override_reason that hold text
      When finding-lint runs
      Then it exits 0

    Scenario: An agent may raise a filed finding
      Given HEAD holds docs/findings/FAGAN-0042.md with severity major and review_class code
      And an agent changes its answer to harms_downstream to true, sets severity critical, and adds "## Possible damage"
      And override_by and override_reason are null
      When finding-lint runs
      Then it does not ask for override_by or override_reason
      And it exits 0

    Scenario: The stakeholder lowers a critical finding only after its stop is confirmed at HEAD
      Given HEAD holds docs/findings/BUG-0037.md with severity critical, review_class code, and no stop_confirmed_by
      And the stakeholder changes its answer to harms_downstream to false and writes override_by and override_reason
      When finding-lint runs
      Then it exits 1 and names BUG-0037 and the rule
      And the same lowering passes once HEAD holds both confirmation fields of BUG-0037

    Scenario: A finding lowered from critical to major drops its confirmation fields
      Given HEAD holds docs/findings/BUG-0037.md with severity critical, review_class code, and text in stop_confirmed_by and stop_confirmed_reason
      And the stakeholder changes its answer to harms_downstream to false, so the file has severity major
      And the stakeholder writes override_by and override_reason and sets stop_confirmed_by and stop_confirmed_reason to null
      When finding-lint runs
      Then it exits 0
      And the same lowering fails when the file keeps text in stop_confirmed_by

    Scenario: A finding file with review_class is never removed without a replacing register line
      Given HEAD holds docs/findings/FAGAN-0042.md with severity major, status resolved, and review_class code
      And an agent removes the file
      And no register line of FAGAN-0042 with override_by and override_reason replaces it
      When finding-lint runs
      Then it exits 1 and names FAGAN-0042 and the rule
      And a finding that the stakeholder does not want fixed is set aside with waived, never lowered to a note

    Scenario: The migration moves a finding into the register without the override fields
      Given HEAD holds docs/findings/BUG-0067.md without review_class
      And the migration commit removes the file and adds a line of BUG-0067 to its register without override_by and override_reason
      When finding-lint runs on the staged migration commit
      Then it does not ask for override_by or override_reason, because the HEAD version carries no review_class

    Scenario: A file without review_class is skipped
      Given a resolved finding file from before the migration carries no review_class
      When finding-lint runs
      Then it does not check that file

    Scenario: A clean set of findings passes
      Given every finding file with review_class and every register line follows the rules
      When finding-lint runs
      Then it exits 0

  Rule: finding-lint checks in_use against git for code, runtime, and security findings
    # actor: finding-lint

    Scenario: Lines that exist unchanged on dev make in_use true
      Given a Fagan review on feature/core-artifact-ownership files BUG-0037 with in_use false
      And the story did not touch the defective lines, so dev carries them unchanged
      When finding-lint runs
      Then it exits 1 with the message "artifact lines exist unchanged on dev"

    Scenario: A security finding gets the same check
      Given a security finding with in_use false whose artifact lines exist unchanged on dev
      When finding-lint runs
      Then it exits 1

    Scenario: A runtime finding gets the same check
      Given a bug hunt files a runtime finding with in_use false on packages/factory/scripts/dispatch:1588
      And those lines exist unchanged on dev
      When finding-lint runs
      Then it exits 1 with the message "artifact lines exist unchanged on dev"

    Scenario: A heading artifact is checked as the section under the heading
      Given a code finding with in_use false names packages/factory/playbooks/feature-addition.md#step-11--update-specification
      And the section under that heading exists unchanged on dev
      When finding-lint runs
      Then it compares the lines of that section, up to the next heading of the same or a higher level
      And it exits 1

    Scenario: Lines on origin/dev count when the local dev lags behind
      Given the local dev lags behind origin/dev
      And the artifact lines of a code finding with in_use false exist unchanged on origin/dev only
      When finding-lint runs
      Then it exits 1 with a message that names origin/dev

    Scenario: A branch that the clone lacks is skipped and named
      Given the clone has neither main nor origin/main
      And the artifact lines of a code finding with in_use false exist on no other place that counts
      When finding-lint runs
      Then it skips main and origin/main
      And its output names main and origin/main as skipped
      And it accepts in_use false

    Scenario: Lines in the installed copy make in_use true
      Given a code finding with in_use false whose artifact lines exist unchanged in .agent-factory/factory/
      When finding-lint runs
      Then it exits 1

    Scenario: Shifted lines are still the same lines
      Given a story inserted 20 lines above the defect
      And the defective lines sit at 120-134 on the feature branch and at 100-114 on dev
      When finding-lint compares their line identities from git blame -M -C --porcelain
      Then the identities match
      And the lint rejects in_use false

    Scenario: Lines that moved to another file are found in their old file
      Given the artifact range moved from packages/factory/scripts/dispatch to packages/factory/scripts/dispatch_lib.py on the feature branch
      When finding-lint blames, on dev, the artifact path and every rename or copy source that git diff -M -C between dev and the feature branch names
      Then it finds the lines in packages/factory/scripts/dispatch on dev
      And the lint rejects in_use false

    Scenario: Lines introduced under a path that was later renamed are still found
      Given the defective lines were introduced while the script lived at factory/scripts/dispatch
      And on dev and on the feature branch the script lives at packages/factory/scripts/dispatch
      When finding-lint blames packages/factory/scripts/dispatch on dev
      Then the porcelain output names factory/scripts/dispatch, a path that no longer exists, as part of each line identity
      And the lint finds the identities on dev and rejects in_use false

    Scenario: A lint run in a linked worktree finds the installed copy in the main checkout
      Given finding-lint runs in a linked story worktree that holds no .agent-factory/
      And the main checkout holds .agent-factory/factory/ with the artifact lines of a code finding unchanged
      And the finding records in_use false
      When finding-lint looks for the installed copy
      Then it finds .agent-factory/factory/ in the main checkout
      And it exits 1

    Scenario: Lines in the installed copy that git has no record of do not count as unchanged
      Given a range in the installed copy whose lines no commit introduced
      When finding-lint blames the installed copy with --contents
      Then the lines do not count as unchanged
      And in_use false passes

    Scenario: A single brace has its own identity
      Given an artifact range that holds a single closing brace
      When finding-lint compares line identities
      Then the range matches only the same line and not every other brace in the file

    Scenario: The git check sets a lower bound only
      Given a code finding with in_use true whose lines exist on no branch, tag, or installed copy
      And its Why this severity line names the other project that reads the artifact
      When finding-lint runs
      Then it accepts in_use true

    Scenario: A consumer project skips the installed copy step
      Given a consumer project has no packages/factory/
      When finding-lint runs the git check
      Then it checks dev, main, origin/dev, origin/main, and the tags that release_tag_patterns names
      And it does not check an installed copy

    Scenario Outline: Only the tags that release_tag_patterns names count as releases
      Given docs/factory-settings.yaml sets release_tag_patterns to ["v[0-9]*"]
      And the artifact lines of a code finding with in_use false exist unchanged only at the tag <tag>
      When finding-lint runs the git check
      Then it <outcome>

      Examples:
        | tag                 | outcome                               |
        | v1.0.0              | exits 1, because the lines are in use |
        | v1.1.0-rc           | exits 1, because the lines are in use |
        | 1.1.0               | accepts in_use false                  |
        | orchestrator-v0.1.0 | accepts in_use false                  |

    Scenario Outline: A missing release setting fails closed
      Given <state>
      And a new code finding needs the git check
      When finding-lint runs
      Then it exits 1
      And it names the file docs/factory-settings.yaml and the key release_tag_patterns
      And it does not guess which tags are releases

      Examples:
        | state                                                      |
        | docs/factory-settings.yaml does not exist                  |
        | docs/factory-settings.yaml has no key release_tag_patterns |

    Scenario: init-factory leaves the release setting to the project
      Given a project without docs/factory-settings.yaml
      When the user runs init-factory
      Then docs/factory-settings.yaml still does not exist

    Scenario: An empty release setting counts no tag
      Given docs/factory-settings.yaml sets release_tag_patterns to []
      When finding-lint runs the git check
      Then it checks dev, main, origin/dev, origin/main, and the installed copy
      And it checks no tag

    Scenario: A missing release setting does not matter when no git check is due
      Given docs/factory-settings.yaml does not exist
      And the only changed finding is a document finding
      When finding-lint runs
      Then it does not report the missing setting

    Scenario: A waived finding whose branch merged into dev still passes
      Given a major code finding was filed with in_use false on its feature branch
      And the branch merged into dev
      When the stakeholder sets status waived with override_by and override_reason
      And finding-lint runs
      Then it does not run the git check, because basis and artifact equal their HEAD version
      And it exits 0

    Scenario: validate runs the check on a new, uncommitted finding
      Given a new finding file that does not exist at HEAD
      When the user runs validate
      Then finding-lint runs the git check on the working tree version

    Scenario: The pre-commit hook compares the staged file
      Given a staged finding file whose basis differs from its HEAD version
      When the pre-commit hook runs finding-lint
      Then finding-lint runs the git check on the staged version

    Scenario: A new register line gets the git check
      Given a new line in docs/findings/register/code.jsonl that HEAD does not hold
      And the line records in_use false
      And its artifact lines exist unchanged on dev
      When finding-lint runs
      Then it exits 1 with the message "artifact lines exist unchanged on dev"

    Scenario: A register line that HEAD holds is not checked again
      Given HEAD holds the line of FAGAN-0032 in docs/findings/register/code.jsonl with in_use false
      And its artifact lines exist unchanged on dev
      When finding-lint runs
      Then it does not run the git check on that line

    Scenario: Document and architecture findings skip the git check
      Given a document finding with in_use false whose artifact lines exist on dev
      When finding-lint runs
      Then it does not reject in_use false

  Rule: User runs finding-lint through validate and the pre-commit hook
    # actor: User
    # @packages/factory/scripts/validate
    # @packages/factory/skills/validate/SKILL.md
    # @packages/factory/config/pre-commit-config.yaml

    Scenario: validate runs finding-lint
      Given docs/findings/ holds a finding with a severity mismatch
      When the user runs the validate skill
      Then the report lists the finding-lint violation

    Scenario: A commit with a broken finding fails
      Given a staged finding file with a severity mismatch
      When the user commits
      Then the pre-commit hook runs finding-lint and the commit fails

  Rule: Orchestrator loops a major finding back to its owner until no blocking finding is open
    # actor: Orchestrator
    # @packages/factory/playbooks/feature-addition.md

    Scenario: An open major finding loops back
      Given docs/findings/FAGAN-0042.md has severity major and status open
      When the orchestrator greps docs/findings/*.md for status: open
      Then it sends FAGAN-0042 to its owner
      And the loop repeats until no file has status open

    Scenario: A waived finding drops out of the loop
      Given docs/findings/FAGAN-0042.md has status waived
      When the orchestrator runs the loop grep of a playbook
      Then the grep does not list FAGAN-0042

    Scenario: A confirmed critical finding loops like a major one
      Given a critical finding has stop_confirmed_by and stop_confirmed_reason set
      When the orchestrator runs the loop
      Then it sends the finding to its owner
      And the finding keeps severity critical

  Rule: Orchestrator stops the run on a critical finding that the stakeholder has not confirmed
    # actor: Orchestrator
    # @packages/factory/scripts/dispatch::main
    # @packages/factory/scripts/premerge-check::main
    # @packages/factory/config/hooks/block-dangerous-git.sh
    # @packages/factory/skills/explain-review-finding/SKILL.md

    Scenario Outline: dispatch refuses every subcommand that starts or merges work
      Given docs/findings/BUG-0037.md has severity critical, status open, and no stop_confirmed_by
      When the orchestrator runs dispatch <subcommand>
      Then dispatch exits 1
      And it prints the stop notice

      Examples:
        | subcommand       |
        | init             |
        | prepare-wave     |
        | prepare-story    |
        | mark-dispatching |
        | mark-dispatched  |
        | re-dispatch      |
        | escalate         |
        | refresh-story    |
        | merge-story      |
        | close-wave       |

    Scenario Outline: dispatch still answers reads and status queries during a stop
      Given docs/findings/BUG-0037.md has severity critical, status open, and no stop_confirmed_by
      When the orchestrator runs dispatch <subcommand>
      Then dispatch runs the subcommand as it does without a stop

      Examples:
        | subcommand         |
        | status             |
        | plan               |
        | suggest-merge-args |
        | verify-story       |
        | mark-done          |
        | mark-blocked       |
        | mark-failed        |
        | clear-manifest     |

    Scenario: The scripts read the findings of the working tree they run in
      Given the feature worktree of feature/core-artifact-ownership holds an uncommitted BUG-0037 with severity critical and status open
      And the main checkout on dev does not hold BUG-0037
      When the orchestrator runs premerge-check in the feature worktree
      Then premerge-check stops on BUG-0037
      And premerge-check run in the main checkout does not stop on BUG-0037

    Scenario: premerge-check refuses to run
      Given docs/findings/BUG-0037.md has severity critical, status open, and no stop_confirmed_by
      When the orchestrator runs premerge-check dev feature/core-artifact-ownership
      Then premerge-check exits 1
      And it prints the stop notice
      And it writes no premerge-check-ok marker

    Scenario: No merge passes the stop
      Given premerge-check refused to run because of BUG-0037
      When an agent runs git merge feature/core-artifact-ownership
      Then block-dangerous-git denies the merge, because no marker exists for that branch head

    Scenario: The stop notice names what the stakeholder must check
      Given BUG-0037 stops the run
      When dispatch or premerge-check prints the stop notice
      Then the notice names the finding ID BUG-0037 and its title
      And it names the artifact and the evidence for in_use
      And it lists each item of "## Possible damage" with its check
      And it names the confirmation step with stop_confirmed_by and stop_confirmed_reason
      And dispatch and premerge-check print the same notice

    Scenario: An interactive session explains the stopping finding
      Given BUG-0037 stops the run in an interactive session
      When the orchestrator receives the stop notice
      Then it explains BUG-0037 with explain-review-finding, starting with cause and effect

    Scenario: A headless run ends with the notice
      Given BUG-0037 stops a headless run
      When the orchestrator receives the stop notice
      Then the run ends without waiting
      And its final summary carries the stop notice

    Scenario: A confirmed stop lets the scripts run again
      Given the stakeholder set stop_confirmed_by and stop_confirmed_reason in the working-tree version of BUG-0037
      And the stakeholder has not committed the change
      When the orchestrator runs dispatch and premerge-check again
      Then neither script stops on BUG-0037

    Scenario: The stop holds while stop_confirmed_reason is empty
      Given BUG-0037 has severity critical, status open, stop_confirmed_by human, and an empty stop_confirmed_reason
      When the orchestrator runs dispatch prepare-wave 3 or premerge-check
      Then the script exits 1
      And it prints the stop notice

    Scenario: A fixed critical finding becomes resolved only after its stop is confirmed
      Given the defect of BUG-0037 is fixed and its stop is not confirmed
      When the reviewer agent of the repeat pass sets status resolved on BUG-0037
      Then finding-lint exits 1
      And the stop holds until stop_confirmed_by and stop_confirmed_reason both hold text

    Scenario Outline: Only the confirmation lifts the stop
      Given HEAD holds docs/findings/BUG-0037.md with severity critical, review_class code, status open, and no stop_confirmed_by
      And an agent <change> in the working tree and commits nothing
      When the orchestrator runs dispatch prepare-wave 3 or premerge-check
      Then the script exits 1
      And it prints the stop notice for BUG-0037

      Examples:
        | change                                       |
        | sets status deferred on BUG-0037             |
        | sets status resolved on BUG-0037             |
        | lowers BUG-0037 to severity major            |
        | removes docs/findings/BUG-0037.md            |

    Scenario: A committed status other than open still stops on a file with review_class
      Given HEAD holds docs/findings/BUG-0037.md with severity critical, review_class code, status deferred, and no stop_confirmed_by
      When the orchestrator runs dispatch prepare-wave 3 or premerge-check
      Then the script exits 1
      And it prints the stop notice for BUG-0037

    Scenario: A resolved critical finding from before the migration stops no run
      Given a finding file with severity critical, status resolved, and no review_class, at HEAD and in the working tree
      When the orchestrator runs dispatch prepare-wave 3 or premerge-check
      Then the script does not stop on that file

  Rule: Orchestrator shows each new minor finding with its fails_purpose sentence
    # actor: Orchestrator
    # @packages/factory/rulebooks/conventions/finding-format.md

    Scenario: The pause point shows each new minor finding before any file is written
      Given an ATAM review produces a minor finding on the gap in ADR-0026
      And its sentence for the no to fails_purpose reads "an implementer can pick the obvious behavior"
      When the orchestrator reaches the pause point
      Then the stakeholder sees the finding with that sentence before any file is written

    Scenario: The stakeholder raises a wrong downgrade by changing the answer
      Given the stakeholder disagrees with the no to fails_purpose at the pause point
      When the stakeholder changes the answer to yes
      Then the rule computes major
      And the finding becomes a finding file and not a register line

    Scenario: A headless run lists the new register lines in its final summary
      Given a headless run added two register lines
      When the run ends
      Then its final summary lists both lines as text with their fails_purpose sentences

    Scenario: A minor security finding shows its Why this severity line
      Given a security review produces a finding of level Low
      When the orchestrator reaches the pause point
      Then the stakeholder sees the finding with its sentence for each precondition
      And the stakeholder sees no fails_purpose sentence for it

    Scenario: The stakeholder raises a registered minor finding to blocking
      Given docs/findings/register/code.jsonl holds the line of FAGAN-0032 with severity minor
      When the stakeholder changes its answer to fails_purpose to yes
      Then docs/findings/FAGAN-0032.md exists with severity major and status open
      And the register no longer holds the line of FAGAN-0032
      And finding-lint exits 0

  Rule: Stakeholder confirms the stop of a critical finding after the damage checks
    # actor: Stakeholder

    Scenario: The stakeholder confirms the stop
      Given BUG-0037 stops the run
      When the stakeholder runs each check under "## Possible damage"
      And writes stop_confirmed_by and stop_confirmed_reason into the finding file
      Then stop_confirmed_reason says what the stakeholder checked and found
      And the scripts run again and the finding loops back to its owner

  Rule: Stakeholder waives a blocking finding with a reason
    # actor: Stakeholder

    Scenario: The stakeholder waives a major finding
      Given a major finding on wave-0 handling that the stakeholder decides not to fix
      When the stakeholder sets status waived with override_by and override_reason
      Then the finding keeps its computed severity
      And the review loop no longer lists it

    Scenario: A critical finding can be waived only after its stop is confirmed
      Given a critical finding with no stop_confirmed_by
      When the stakeholder sets status waived with override_by and override_reason
      Then finding-lint exits 1 until stop_confirmed_by and stop_confirmed_reason are set

    Scenario: No override raises a minor finding
      Given a minor finding at the pause point or in a register
      When the stakeholder wants it to block
      Then no override field makes it blocking
      And the stakeholder raises it only by changing an answer of its basis

    Scenario: The stakeholder waives a major proposal row
      Given an open major row in the Appendix of a proposal
      When the stakeholder sets its Status cell to waived with the reason in its Resolution cell
      Then the row no longer blocks the transition to accepted

  Rule: Agent is refused when it sets a field that only the stakeholder writes
    # actor: Agent, as the guard hook guard-human-fields answers it

    Scenario: An Edit that sets stop_confirmed_by is refused
      Given docs/findings/BUG-0037.md has stop_confirmed_by: null
      When an agent calls Edit with new_string stop_confirmed_by: human
      Then guard-human-fields refuses the call

    Scenario: A Bash call that sets status waived is refused
      Given docs/findings/FAGAN-0042.md has status open
      When an agent runs sed -i 's/status: open/status: waived/' docs/findings/FAGAN-0042.md
      Then guard-human-fields refuses the call

    Scenario: An Edit that sets override_by in a register line is refused
      Given docs/findings/register/code.jsonl holds a line of FAGAN-0042 without override_by
      When an agent calls Edit with a new_string that adds "override_by": "human" to that line
      Then guard-human-fields refuses the call

    Scenario: A headless run cannot confirm its own stop
      Given a critical finding stops a headless run
      When the orchestrator tries to write stop_confirmed_by: human into the finding file
      Then guard-human-fields refuses the edit
      And the run ends with the stop notice

    Scenario: A Bash call that sets waived in the Status cell of a proposal row is refused
      Given a proposal Appendix row with the Status cell open
      When an agent runs a sed -i command on the proposal that writes waived into that Status cell
      Then guard-human-fields refuses the call

    Scenario Outline: Legitimate calls pass
      Given <situation>
      When an agent makes the call
      Then guard-human-fields lets the call through

      Examples:
        | situation                                                                                   |
        | a Write of a new finding from the template, where every human field is null                 |
        | an Edit that fixes a typo in the title of a waived finding and leaves its status line as is |
        | an Edit of packages/factory/rulebooks/templates/finding.md                                  |
        | a read-only grep "status: waived" docs/findings/                                            |
        | a heredoc that writes a test fixture with override_by: human outside docs/findings/         |

    Scenario Outline: The installer registers the guard in every supported CLI
      Given a project that uses <cli>
      When the user runs init-factory or update-factory
      Then <cli> runs guard-human-fields before each edit, write, and shell call of an agent

      Examples:
        | cli         |
        | Claude Code |
        | Codex       |
        | Copilot CLI |
        | Pi          |
        | OpenCode    |

    Scenario: The stakeholder writes the fields outside the tool hooks
      Given the stakeholder runs a ! command in the session that writes stop_confirmed_by
      When the command runs
      Then the hook does not see it, and the field is set

  Rule: Test-strategy agent states the consequence in the QA triage table
    # actor: Test-strategy agent
    # @packages/factory/rulebooks/templates/qa-strategy.md

    Scenario: The triage table has a Consequence column
      Given the test-strategy agent writes a QA strategy from the template
      When it fills the triage table
      Then the table has a Consequence column with the values "harm if in use", "fails purpose", and "raises cost"
      And the table has no severity column

    Scenario: The action follows the computed severity
      Given a triage row with the consequence "harm if in use"
      When a finding of that row is classified
      Then a critical finding stops the run, a major finding loops back to its author, and a minor finding goes to the register

  Rule: Stakeholder gets the open findings migrated under the new rules
    # actor: Stakeholder

    Scenario: The migration covers every open finding without review_class
      Given on 2026-11-06 47 findings are open without review_class, among them SPEC-0055 and ATAM-0010
      When the migration agent collects the findings to migrate
      Then it counts the open findings without review_class again at the time it runs
      And it collects every one of them
      And it skips an open finding that already carries review_class

    Scenario: The release setting exists before the migration commit
      Given the migration commit adds review_class and basis to code findings, so finding-lint runs the git check
      When the migration agent prepares the migration commit
      Then docs/factory-settings.yaml with the key release_tag_patterns is already committed
      And finding-lint does not fail on a missing release setting

    Scenario: The stakeholder reviews every result before any file changes
      Given the migration agent has classified every open finding without review_class with the new rulebook
      When it reaches the migration pause point
      Then the stakeholder sees review_class, basis, severity, and the Why this severity line of each finding
      And no finding file has changed yet

    Scenario: The migration rewrites the artifact to the range of the fix
      Given BUG-0016 names docs/ and BUG-0086 names packages/factory/scripts/dispatch
      When the migration agent migrates them
      Then each artifact names the line range or heading where its fix goes

    Scenario: A migrated minor finding becomes a register line under its old ID
      Given BUG-0067 comes out minor
      When the migration agent changes the files
      Then the register of its class holds a line with the ID BUG-0067
      And the file docs/findings/BUG-0067.md is removed, and git history keeps its text

    Scenario: A migrated major finding stays a file
      Given BUG-0105 comes out major
      When the migration agent changes the files
      Then docs/findings/BUG-0105.md stays and carries review_class, basis, and the Why this severity line

    Scenario: A migrated critical finding is confirmed at the pause point
      Given a migrated finding comes out critical
      When the migration agent fills its "## Possible damage"
      And the stakeholder runs the checks and sets stop_confirmed_by and stop_confirmed_reason
      Then the migration commit holds no unconfirmed critical finding
      And the migration review report states how many migrated findings are critical

    Scenario: A finding without an artifact moves into the todo list
      Given RETRO-0002 names no artifact
      When the migration agent migrates it
      Then docs/spec/work/todo.md gains an entry for it
      And the file gets status deferred with the todo ID in its body
      And the file carries no review_class

    Scenario: After the migration the lint passes and no open finding is minor
      Given the migration commit is in place
      When finding-lint runs on docs/findings/
      Then it exits 0
      And every open finding carries review_class
      And no open finding file has severity minor

    Scenario: Findings that are not open stay as they are
      Given a resolved finding without review_class
      When the migration runs
      Then the file stays unchanged

  Rule: Stakeholder measures how often two runs agree on the severity
    # actor: Stakeholder

    Scenario: The agreement check passes
      Given a fixed set of 20 closed findings, picked as 6 document, 5 code, 4 runtime, 2 architecture, and 3 security
      And the security picks are FAGAN-0021, SEC-0005, and SEC-0006
      And each run is a fresh subagent on the review agents' model with only the rules under test and the 20 texts
      When two runs classify the set with the new rulebook and two runs with the rules of report-format.md before this change
      Then the two new runs agree on the severity of at least 16 of the 20 findings
      And they agree on more findings than the two old runs do
      And a review report in docs/reviews/ records the quotas, the picks, the model, and both counts

    Scenario: A question counts as disagreement
      Given one run answers a finding of the set with the category question
      When the agreement is counted
      Then that finding counts as a disagreement

    Scenario: The set holds no migrated finding and no calibration example
      Given the rulebook names its calibration examples and the proposal its worked examples
      When the stakeholder picks the set
      Then no finding in the set is migrated, a calibration example, or a worked example
