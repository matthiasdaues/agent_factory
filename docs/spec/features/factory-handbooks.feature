# scope: global
Feature: Factory Handbooks

  The factory has two handbooks. The user handbook lives in
  packages/factory/docs/handbook/ and installs into
  .agent-factory/factory/docs/handbook/. Its reader runs the factory in a
  project. The contributor handbook lives in docs/handbook/ and stays in
  this repository. Its reader is a contributor: a person who changes the
  factory itself.

  A handbook is a folder of Markdown pages, one folder per chapter. The
  page rules BR-140 to BR-143 in docs/spec/validation-rules.md set the
  frontmatter of a page, the folders, the titles, and the markers
  <!-- handbook-index:start --> and <!-- handbook-index:end --> in each
  index.md. The script handbook-index writes the page list of each
  index.md between the markers, as BR-144 and BR-145 set. The script
  handbook-lint checks both handbooks against the page rules and runs
  handbook-index --check.

  The migration deletes packages/factory/docs/factory-guide.md,
  docs/arc42/concepts.md, and docs/arc42/beginner-intro.md (DEC-07,
  DEC-10, DEC-13). The migration map
  docs/spec/work/factory-handbooks-migration-map.md assigns each section
  of the three files to the handbook page that now holds it.

  The examples use the user handbook chapter cli-integrations/. Its
  index.md has the title "CLI integrations" and order 80. The chapter
  holds four more pages. remove-an-integration.md is the implemented
  how-to "Remove a CLI integration" with order 20 and the description
  "Remove the files of one CLI from a project." add-an-integration.md is
  the implemented how-to "Add a CLI integration" without order.
  cli-differences.md is the implemented concept "How the CLIs differ".
  opencode-desktop.md is the how-to "OpenCode Desktop" with status stub.

  Each Rule carries a trace comment FH-NN, and each Scenario carries a
  trace comment FH-NN-NN. FH stands for Factory Handbooks. A test names
  the trace of the Scenario it checks. The gaps report
  docs/spec/work/factory-handbooks-gaps.md lists the acceptance criteria
  of the one-time migration that no Scenario states.

  Proposal trace: docs/proposals/factory-handbooks.md

  Rule: Contributor sees the page lists of a handbook written by handbook-index
    # actor: Contributor
    # trace: FH-01

    Scenario: handbook-index writes the grouped and sorted page list between the markers
      # trace: FH-01-01
      Given cli-integrations/index.md holds the marker pair and no list
      When the contributor runs handbook-index
      Then the page list of cli-integrations/index.md has the group heading "Concepts" followed by the group heading "How-to guides"
      And "How the CLIs differ" is listed under "Concepts"
      And the how-to group lists "Remove a CLI integration" before "Add a CLI integration"
      And the entry "Remove a CLI integration" links to remove-an-integration.md and shows the description "Remove the files of one CLI from a project."
      And handbook-index exits 0

    Scenario: A stub stays out of the page list and the text outside the markers stays unchanged
      # trace: FH-01-02
      Given opencode-desktop.md has status stub
      And cli-integrations/index.md holds an introduction above the start marker and a note below the end marker
      When the contributor runs handbook-index
      Then the page list of cli-integrations/index.md names neither "OpenCode Desktop" nor index.md
      And the introduction and the note are unchanged byte for byte

    Scenario: A page that breaks the page rules stops handbook-index
      # trace: FH-01-03
      Given add-an-integration.md has no type field
      When the contributor runs handbook-index
      Then handbook-index exits non-zero
      And it writes no file
      And it reports the path of add-an-integration.md and the field type

    Scenario: The top-level index.md lists every chapter of its handbook
      # trace: FH-01-04
      Given the index.md of getting-started/ has order 10 and the index.md of cli-integrations/ has order 80
      And every page of docs/handbook/release/ except its index.md is a stub
      When the contributor runs handbook-index
      Then the top-level index.md of the user handbook lists getting-started/ before cli-integrations/
      And each entry links to the index.md of its chapter with the chapter's title
      And the top-level index.md of the contributor handbook lists the chapter release/

  Rule: Contributor learns which page or page list breaks the handbook rules
    # actor: Contributor
    # trace: FH-02

    Scenario: handbook-index --check reports an out-of-date page list and changes nothing
      # trace: FH-02-01
      Given the contributor adds the implemented page cli-differences.md and does not run handbook-index
      When the contributor runs handbook-index --check
      Then handbook-index exits non-zero
      And it reports the path of cli-integrations/index.md
      And it changes no file

    Scenario Outline: handbook-lint reports each kind of page rule failure
      # trace: FH-02-02
      Given both handbooks pass handbook-lint
      And then <defect>
      When the contributor runs handbook-lint
      Then handbook-lint exits non-zero
      And it reports <report>
      And it reports no other failure

      Examples:
        | defect                                                                                                                 | report                                                    |
        | remove-an-integration.md has no type field                                                                             | the path of remove-an-integration.md and the field type   |
        | remove-an-integration.md has status set to planned                                                                     | the path of remove-an-integration.md and the field status |
        | the folder docs/handbook/testing/ holds the page layers.md and no index.md                                             | the folder docs/handbook/testing/                         |
        | the chapter cli-integrations/ holds the folder cli-integrations/opencode/                                              | the folder cli-integrations/opencode/                     |
        | docs/handbook/ holds chapter folders and no index.md                                                                   | the folder docs/handbook/                                 |
        | add-an-integration.md and add-cli.md in cli-integrations/ are implemented pages with the title "Add a CLI integration", and the page list of cli-integrations/index.md is current | both paths and the title "Add a CLI integration"          |
        | cli-integrations/index.md holds the end marker before the start marker                                                 | the path of cli-integrations/index.md                     |

    Scenario: One run of handbook-lint reports every failure of both handbooks
      # trace: FH-02-03
      Given add-an-integration.md in the user handbook has no type field
      And the folder docs/handbook/testing/ holds the page layers.md and no index.md
      And the page list of docs/handbook/contributing/index.md is out of date
      When the contributor runs handbook-lint
      Then handbook-lint exits non-zero
      And it reports the path of add-an-integration.md and the field type
      And it reports the folder docs/handbook/testing/
      And it reports the path of docs/handbook/contributing/index.md as out of date

  Rule: Contributor cannot commit a handbook page that breaks the page rules
    # actor: Contributor
    # trace: FH-03
    # @.pre-commit-config.yaml

    Scenario: A commit with a page that lacks type fails
      # trace: FH-03-01
      Given the contributor stages a new page docs/handbook/testing/layers.md without a type field
      When the contributor commits
      Then the pre-commit hook handbook-lint fails
      And the commit is not created

  Rule: User reads the installed user handbook after init-factory or update-factory
    # actor: User
    # trace: FH-04
    # @packages/factory/scripts/init-factory::main
    # @packages/factory/scripts/update-factory::_run_init

    Scenario Outline: The installed handbook equals the user handbook of the source
      # trace: FH-04-01
      Given <project>
      When the user runs <command>
      Then the set of relative paths under .agent-factory/factory/docs/handbook/ equals the set under packages/factory/docs/handbook/
      And every installed file has the same bytes as its source file
      And .agent-factory/factory/docs/factory-guide.md does not exist
      And no file of the contributor handbook docs/handbook/ is copied into the project

      Examples:
        | project                                                        | command        |
        | a project has no factory installation                          | init-factory   |
        | a project has a factory installation from the previous release | update-factory |

  Rule: User and contributor find the content of the three deleted files at its new home
    # actor: User, Contributor
    # trace: FH-05
    # @packages/factory/scripts/_link_rewrite.py::rewrite_links
    # @packages/factory/scripts/link-check::main

    Scenario: Every section of the three deleted files has a home in the migration map
      # trace: FH-05-01
      Given the migration map docs/spec/work/factory-handbooks-migration-map.md
      Then every section heading of factory-guide.md, concepts.md, and beginner-intro.md at commit 4ebf5101f70c1540a0d53dcfb3d00cfa977d361a has a row in the map
      And each row names a handbook page that exists
      And each row of factory-guide.md, of beginner-intro.md, and of the concepts.md sections "The phase chain" and "Key ideas" names a page of the user handbook
      And the row of the concepts.md section "Project directory tree" names the reference page in the contributor handbook's architecture/ chapter

    Scenario: Every link to the three deleted files points to the new home of its information
      # trace: FH-05-02
      When the migration is complete
      Then no tracked Markdown file outside .agent-factory/ links to factory-guide.md, docs/arc42/concepts.md, or docs/arc42/beginner-intro.md
      And each rewritten link points to the page that BR-151 gives it
      And each file in a record folder changes only in its link destinations
      And link-check reports no problem for any rewritten link
      And link-check over every live document exits 0

    Scenario: No factory file, test, or feature file names the guide
      # trace: FH-05-03
      When the migration is complete
      Then packages/factory/docs/factory-guide.md, docs/arc42/concepts.md, and docs/arc42/beginner-intro.md do not exist
      And ~archive/ holds no copy of the three files
      And rg factory-guide packages/ tests/ README.md docs/spec/features/ --glob '!CHANGELOG.md' --glob '!docs/spec/features/factory-handbooks.feature' finds no match
      # The handbook specification names its migration inputs, so the search leaves it out (L-30).

  Rule: User reaches the user handbook from every factory entry point
    # actor: User
    # trace: FH-06
    # @packages/factory/config/session-menu.md
    # @packages/factory/skills/newcomer-tour/SKILL.md
    # @packages/factory/skills/guided-tour/SKILL.md
    # @packages/factory/skills/explain-concept/SKILL.md
    # @packages/factory/agents/virgil.md
    # @packages/factory/INDEX.yaml
    # @packages/factory/README.md

    Scenario: Every factory entry point leads to the user handbook
      # trace: FH-06-01
      Then the H section of session-menu.md routes a new user to the newcomer-tour skill with the user handbook's getting-started/ tutorial
      And the procedure of newcomer-tour reads the tutorial page of .agent-factory/factory/docs/handbook/getting-started/
      And the description of option H in guided-tour names the user handbook's getting-started/ tutorial
      And explain-concept, virgil.md, and the inputs of VIRGIL in INDEX.yaml name .agent-factory/factory/docs/handbook/
      And packages/factory/README.md holds the install, update, and removal commands and links to the user handbook for every other topic

  Rule: Contributor reaches the contributor handbook from the root README and the agent context
    # actor: Contributor
    # trace: FH-07
    # @README.md
    # @docs/agent-context.md

    Scenario: The root README and the agent context lead to contributor handbook pages
      # trace: FH-07-01
      Then the section "Contributing" of README.md links to the tutorial page of docs/handbook/getting-started/
      And docs/agent-context.md routes the concerns "write a skill or agent", "add a gate", and "release" to pages under docs/handbook/
