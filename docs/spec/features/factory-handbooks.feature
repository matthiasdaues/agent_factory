# scope: global
Feature: Factory Handbooks

  The factory has two handbooks. The user handbook lives in
  packages/factory/docs/handbook/ and installs with the factory into
  .agent-factory/factory/docs/handbook/. Its reader runs the factory in a
  project. The contributor handbook lives in docs/handbook/ and stays in
  this repository. Its reader is a contributor: a person who changes the
  factory itself.

  A handbook is a folder of Markdown pages. Each chapter is one folder.
  A page starts with frontmatter. The fields title, type, and status are
  required. type is one of tutorial, concept, how-to, reference, and
  learn. status is implemented or stub (DEC-05). description is optional
  and holds one sentence. order is an optional integer with the default
  100. Zero and negative integers are valid. A stub is a page for behaviour that does not exist yet. It carries
  status stub, one sentence of scope, and links to its sources.

  Every folder has an index.md, the chapter page. A chapter folder holds
  pages and no folder. index.md is a page, so
  the same frontmatter rules apply to it. The script handbook-index
  writes the folder's page list into index.md, between the markers
  <!-- handbook-index:start --> and <!-- handbook-index:end --> (DEC-06).
  Each index.md holds each marker exactly once, the start marker before
  the end marker.
  The script handbook-lint checks both handbooks. It runs
  handbook-index --check and does not check links, because link-check
  owns links.

  The migration deletes three files: packages/factory/docs/factory-guide.md,
  docs/arc42/concepts.md, and docs/arc42/beginner-intro.md (DEC-07,
  DEC-10, DEC-13). The migration map docs/spec/work/factory-handbooks-migration-map.md
  assigns each section of the three files to the handbook page that now
  holds it. A live document is every
  tracked Markdown file outside poc/ and outside the record folders. The
  record folders are backlog/, docs/handoffs/, docs/findings/,
  docs/reviews/, docs/transcripts/, docs/research/, docs/spec/work/,
  docs/proposals/implemented/, docs/proposals/superseded/, and ~archive/.

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
  the trace of the Scenario it checks.

  The conversation that session menu H starts belongs to
  newcomer-onboarding.feature, Rule "Newcomer walks through a guided tour
  before choosing a workflow". This feature checks that every entry point
  names the handbook pages.

  Proposal trace: docs/proposals/factory-handbooks.md

  Rule: Contributor sees the page list of a folder written by handbook-index
    # actor: Contributor
    # trace: FH-01

    Scenario: handbook-index writes the page list between the markers
      # trace: FH-01-01
      Given cli-integrations/index.md holds the marker pair and no list
      When the contributor runs handbook-index
      Then the text between the markers of cli-integrations/index.md lists every page of the chapter that is not a stub
      And handbook-index exits 0

    Scenario: The page list groups pages by type in the order of the type table
      # trace: FH-01-02
      Given cli-integrations/ holds implemented pages of the types how-to and concept
      When the contributor runs handbook-index
      Then the page list of cli-integrations/index.md has the group heading "Concepts" followed by the group heading "How-to guides"
      And "How the CLIs differ" is listed under "Concepts"
      And "Remove a CLI integration" and "Add a CLI integration" are listed under "How-to guides"

    Scenario Outline: Each type has a fixed group heading
      # trace: FH-01-11
      Given getting-started/ holds an implemented page of the type <type>
      When the contributor runs handbook-index
      Then the page list of getting-started/index.md has the group heading "<heading>"

      Examples:
        | type      | heading       |
        | tutorial  | Tutorials     |
        | concept   | Concepts      |
        | how-to    | How-to guides |
        | reference | Reference     |
        | learn     | Learning      |

    Scenario: The groups follow the order tutorial, concept, how-to, reference, learn
      # trace: FH-01-12
      Given getting-started/ holds one implemented page of each of the five types
      When the contributor runs handbook-index
      Then the group headings of getting-started/index.md appear in the order "Tutorials", "Concepts", "How-to guides", "Reference", "Learning"

    Scenario: A type with no listed page has no group heading
      # trace: FH-01-13
      Given the only reference page of cli-integrations/ is a stub
      When the contributor runs handbook-index
      Then the page list of cli-integrations/index.md has no group heading "Reference"

    Scenario: Pages in a group sort by order and then by title
      # trace: FH-01-03
      Given "Remove a CLI integration" has order 20 and "Add a CLI integration" has no order
      When the contributor runs handbook-index
      Then the how-to group lists "Remove a CLI integration" before "Add a CLI integration"

    Scenario: Pages with the same order sort by title
      # trace: FH-01-04
      Given two how-to pages "Update a CLI integration" and "Add a CLI integration" both have no order
      When the contributor runs handbook-index
      Then the how-to group lists "Add a CLI integration" before "Update a CLI integration"

    Scenario: Each entry links to the page with its title and shows its description
      # trace: FH-01-05
      When the contributor runs handbook-index
      Then the entry of remove-an-integration.md is a link with the text "Remove a CLI integration" to remove-an-integration.md
      And the description "Remove the files of one CLI from a project." follows the link
      And the entry of add-an-integration.md holds the link and no description

    Scenario: A stub stays out of the page list
      # trace: FH-01-06
      Given opencode-desktop.md has status stub
      When the contributor runs handbook-index
      Then the page list of cli-integrations/index.md does not name "OpenCode Desktop"

    Scenario: A filled stub joins the page list
      # trace: FH-01-07
      Given the contributor fills opencode-desktop.md and sets its status to implemented
      When the contributor runs handbook-index
      Then the how-to group of cli-integrations/index.md lists "OpenCode Desktop"

    Scenario: An index.md never appears in its own page list
      # trace: FH-01-08
      When the contributor runs handbook-index
      Then the page list of cli-integrations/index.md has no entry for index.md

    Scenario: handbook-index leaves the text outside the markers unchanged
      # trace: FH-01-09
      Given cli-integrations/index.md holds an introduction above the start marker and a note below the end marker
      When the contributor runs handbook-index
      Then the introduction and the note are unchanged byte for byte

    Scenario Outline: An index.md with a broken marker pair stops handbook-index
      # trace: FH-01-10
      Given cli-integrations/index.md <defect>
      When the contributor runs handbook-index
      Then handbook-index exits non-zero
      And it reports the path of cli-integrations/index.md
      And it changes no marker in cli-integrations/index.md

      Examples:
        | defect                                       |
        | holds no start marker                        |
        | holds no end marker                          |
        | holds the start marker twice                 |
        | holds the end marker twice                   |
        | holds the end marker before the start marker |

    Scenario: A page that breaks the page format stops handbook-index
      # trace: FH-01-14
      Given add-an-integration.md has no type field
      And cli-differences.md has status set to planned
      When the contributor runs handbook-index
      Then handbook-index exits non-zero
      And it writes no file
      And it reports the path of add-an-integration.md and the field type
      And it reports the path of cli-differences.md and the field status

    Scenario: Pages with the same order and title sort by the path of their file
      # trace: FH-01-15
      Given add-an-integration.md and add-cli.md in cli-integrations/ are implemented how-to pages with the title "Add a CLI integration" and no order
      When the contributor runs handbook-index
      Then the how-to group of cli-integrations/index.md lists add-an-integration.md before add-cli.md

  Rule: Contributor sees every chapter in the top-level index of a handbook
    # actor: Contributor
    # trace: FH-02

    Scenario: The top-level index lists the chapters by their order field
      # trace: FH-02-01
      Given the index.md of getting-started/ has order 10 and the index.md of cli-integrations/ has order 80
      When the contributor runs handbook-index
      Then the page list of the handbook's top-level index.md lists getting-started/ before cli-integrations/
      And each entry links to the index.md of its chapter with the chapter's title

    Scenario: Chapters with the same order sort by title
      # trace: FH-02-04
      Given the index.md of research/ has the title "Research" and the index.md of usage-capture/ has the title "Usage capture"
      And neither index.md has an order field
      When the contributor runs handbook-index
      Then the top-level index.md lists research/ before usage-capture/

    Scenario: A chapter of stubs stays in the top-level index
      # trace: FH-02-02
      Given every page of docs/handbook/release/ except its index.md is a stub
      When the contributor runs handbook-index
      Then the top-level index.md of the contributor handbook lists the chapter release/

    Scenario: A new chapter appears without a change to the script
      # trace: FH-02-03
      Given the contributor creates the folder troubleshooting/ with an index.md that holds the marker pair
      When the contributor runs handbook-index
      Then the top-level index.md lists the chapter troubleshooting/

    Scenario: Chapters with the same order and title sort by the path of their folder
      # trace: FH-02-05
      Given the index.md of research/ and the index.md of usage-capture/ both have the title "Research" and no order
      When the contributor runs handbook-index
      Then the top-level index.md lists research/ before usage-capture/

  Rule: Contributor learns from handbook-index --check that a page list is out of date
    # actor: Contributor
    # trace: FH-03

    Scenario: Current page lists pass the check
      # trace: FH-03-01
      Given handbook-index has written every page list of both handbooks
      When the contributor runs handbook-index --check
      Then handbook-index exits 0
      And it changes no file

    Scenario: A page added after the last run fails the check
      # trace: FH-03-02
      Given the contributor adds the implemented page cli-differences.md and does not run handbook-index
      When the contributor runs handbook-index --check
      Then handbook-index exits non-zero
      And it reports the path of cli-integrations/index.md
      And it changes no file

    Scenario Outline: An index.md with a broken marker pair fails the check
      # trace: FH-03-03
      Given cli-integrations/index.md <defect>
      When the contributor runs handbook-index --check
      Then handbook-index exits non-zero
      And it reports the path of cli-integrations/index.md

      Examples:
        | defect                                       |
        | holds no start marker                        |
        | holds no end marker                          |
        | holds the start marker twice                 |
        | holds the end marker twice                   |
        | holds the end marker before the start marker |

    Scenario: A page that breaks the page format stops the check
      # trace: FH-03-04
      Given add-an-integration.md has no type field
      When the contributor runs handbook-index --check
      Then handbook-index exits non-zero
      And it writes no file
      And it reports the path of add-an-integration.md and the field type

  Rule: Contributor learns from handbook-lint which page breaks the page format
    # actor: Contributor
    # trace: FH-04

    Scenario: Both handbooks in the page format pass
      # trace: FH-04-01
      Given every page of both handbooks has a valid title, type, and status
      And every folder with pages has an index.md with current page lists
      When the contributor runs handbook-lint
      Then handbook-lint exits 0

    Scenario Outline: A page without a required field fails
      # trace: FH-04-02
      Given remove-an-integration.md has no <field> field
      When the contributor runs handbook-lint
      Then handbook-lint exits non-zero
      And it reports the path of remove-an-integration.md and the field <field>

      Examples:
        | field  |
        | title  |
        | type   |
        | status |

    Scenario Outline: A field value outside the page format fails
      # trace: FH-04-03
      Given remove-an-integration.md has <field> set to <value>
      When the contributor runs handbook-lint
      Then handbook-lint exits non-zero
      And it reports the path of remove-an-integration.md and the field <field>

      Examples:
        | field  | value     |
        | title  | 42        |
        | title  | ""        |
        | title  | null      |
        | type   | guide     |
        | status | planned   |
        | status | specified |
        | order  | first     |
        | order  | 2.5       |

    Scenario: A folder with pages but no index.md fails
      # trace: FH-04-04
      Given the folder docs/handbook/testing/ holds the page layers.md and no index.md
      When the contributor runs handbook-lint
      Then handbook-lint exits non-zero
      And it reports the folder docs/handbook/testing/

    Scenario Outline: An index.md with a broken marker pair fails
      # trace: FH-04-05
      Given cli-integrations/index.md <defect>
      When the contributor runs handbook-lint
      Then handbook-lint exits non-zero
      And it reports the path of cli-integrations/index.md

      Examples:
        | defect                                       |
        | holds no start marker                        |
        | holds no end marker                          |
        | holds the start marker twice                 |
        | holds the end marker twice                   |
        | holds the end marker before the start marker |

    Scenario Outline: Two implemented pages with one title in one chapter fail
      # trace: FH-04-06
      Given add-an-integration.md in cli-integrations/ has the title "<first title>" and status implemented
      And add-cli.md in cli-integrations/ has the title "<second title>" and status implemented
      When the contributor runs handbook-lint
      Then handbook-lint exits non-zero
      And it reports both paths and the title "<second title>"

      Examples:
        | first title           | second title          |
        | Add a CLI integration | Add a CLI integration |
        | Add a CLI integration | add a CLI Integration |

    Scenario: A stub may share a title with an implemented page
      # trace: FH-04-07
      Given add-cli.md in cli-integrations/ has the title "Add a CLI integration" and status stub
      And add-an-integration.md has the same title and status implemented
      When the contributor runs handbook-lint
      Then handbook-lint reports no duplicate title

    Scenario: Pages in two chapters may share a title
      # trace: FH-04-08
      Given packages/factory/docs/handbook/cli-integrations/ and docs/handbook/cli-integrations/ each hold an implemented page with the title "Add a CLI integration"
      When the contributor runs handbook-lint
      Then handbook-lint reports no duplicate title

    Scenario: An out-of-date page list fails
      # trace: FH-04-09
      Given the page list of cli-integrations/index.md differs from what handbook-index would write
      When the contributor runs handbook-lint
      Then handbook-lint exits non-zero
      And it reports the path of cli-integrations/index.md

    Scenario: One run reports the failures of both handbooks
      # trace: FH-04-10
      Given a page of the user handbook has no type
      And a page of the contributor handbook has no status
      When the contributor runs handbook-lint
      Then handbook-lint exits non-zero
      And it reports both pages

    Scenario: handbook-lint does not check links
      # trace: FH-04-11
      Given cli-differences.md links to a page that does not exist
      And the handbook is otherwise in the page format
      When the contributor runs handbook-lint
      Then handbook-lint exits 0

    Scenario: handbook-lint does not check rule words
      # trace: FH-04-12
      Given cli-differences.md holds the sentence "You must restart the CLI after the update."
      And the handbook is otherwise in the page format
      When the contributor runs handbook-lint
      Then handbook-lint exits 0
      # DEC-12

    Scenario: A folder inside a chapter folder fails
      # trace: FH-04-13
      Given the chapter cli-integrations/ holds the folder cli-integrations/opencode/
      When the contributor runs handbook-lint
      Then handbook-lint exits non-zero
      And it reports the path of cli-integrations/opencode/

    Scenario Outline: Any integer is a valid order
      # trace: FH-04-14
      Given remove-an-integration.md has order set to <value>
      And the handbook is otherwise in the page format
      When the contributor runs handbook-lint
      Then handbook-lint exits 0

      Examples:
        | value |
        | 0     |
        | -5    |
        | 20    |

    Scenario: handbook-lint reports page-format failures and goes on with its other checks
      # trace: FH-04-15
      Given add-an-integration.md in the user handbook has no type field
      And a page of the contributor handbook has status set to planned
      And the folder docs/handbook/testing/ holds the page layers.md and no index.md
      When the contributor runs handbook-lint
      Then handbook-lint exits non-zero
      And it reports the path of add-an-integration.md and the field type
      And it reports the path of the contributor page and the field status
      And it reports the folder docs/handbook/testing/

    Scenario: handbook-lint reports a stale page list next to a page with bad metadata
      # trace: FH-04-16
      Given add-an-integration.md in the user handbook has no type field
      And the page list of docs/handbook/contributing/index.md is out of date
      When the contributor runs handbook-lint
      Then handbook-lint exits non-zero
      And it reports the path of add-an-integration.md and the field type
      And it reports the path of docs/handbook/contributing/index.md as out of date

  Rule: Contributor cannot commit a handbook page that breaks the page format
    # actor: Contributor
    # trace: FH-05
    # @.pre-commit-config.yaml
    # @packages/factory/scripts/init-factory::handle_precommit

    Scenario: A commit with a page that lacks type fails
      # trace: FH-05-01
      Given the contributor stages a new page docs/handbook/testing/layers.md without a type field
      When the contributor commits
      Then the pre-commit hook handbook-lint fails
      And the commit is not created

    Scenario: A commit with a valid page and a current page list passes the handbook checks
      # trace: FH-05-02
      Given the contributor stages a new implemented page with title, type, and status
      And the contributor stages the index.md that handbook-index wrote for it
      When the contributor commits
      Then the pre-commit hook handbook-lint passes

    Scenario: handbook-lint runs on a commit that changes no handbook file
      # trace: FH-05-03
      Given the contributor stages only packages/factory/scripts/link-check
      When the contributor commits
      Then the pre-commit hook handbook-lint runs

    Scenario: A commit that only deletes a page is checked
      # trace: FH-05-05
      Given the contributor deletes remove-an-integration.md and stages only the deletion
      When the contributor commits
      Then the pre-commit hook handbook-lint fails, because the page list of cli-integrations/index.md is out of date
      And the commit is not created

    Scenario: init-factory installs no handbook hook into a user project
      # trace: FH-05-04
      When init-factory installs the factory into a user project
      Then the pre-commit configuration of the user project names neither handbook-lint nor handbook-index

  Rule: Contributor repeats a binding rule only in a rule summary that links to its home
    # actor: Contributor
    # trace: FH-06

    Scenario: Every rule summary links to the rule's home
      # trace: FH-06-01
      Given a page of either handbook holds a callout line that starts with "> Rule summary:"
      Then the next line of the callout starts with "> Source:"
      And the Source line links to packages/factory/rulebooks/rules.md or to a file under packages/factory/rulebooks/
      # DEC-02

  Rule: User reads the installed user handbook after init-factory or update-factory
    # actor: User
    # trace: FH-07
    # @packages/factory/scripts/update-factory::_run_init
    # @packages/factory/scripts/init-factory::main

    Scenario: The installed handbook lists every user handbook chapter
      # trace: FH-07-01
      Given a project has a factory installation from before this release
      When the user runs update-factory
      Then .agent-factory/factory/docs/handbook/index.md exists
      And its page list names each of the twelve chapters of the user handbook

    Scenario: The installed handbook matches the source handbook file for file
      # trace: FH-07-02
      When the user runs update-factory
      Then the set of relative paths under .agent-factory/factory/docs/handbook/ equals the set under packages/factory/docs/handbook/
      And every installed file has the same bytes as its source file

    Scenario: The update removes a handbook page that the source no longer holds
      # trace: FH-07-05
      Given the project holds .agent-factory/factory/docs/handbook/cli-integrations/old-page.md from the earlier installation
      And packages/factory/docs/handbook/cli-integrations/ holds no old-page.md
      When the user runs update-factory
      Then .agent-factory/factory/docs/handbook/cli-integrations/old-page.md does not exist

    Scenario: A fresh installation holds the user handbook and no contributor handbook
      # trace: FH-07-06
      Given a project has no factory installation
      When the user runs init-factory
      Then the set of relative paths under .agent-factory/factory/docs/handbook/ equals the set under packages/factory/docs/handbook/
      And no file of the contributor handbook docs/handbook/ is copied into the project
      # DEC-04

    Scenario: The update removes the installed guide
      # trace: FH-07-03
      Given the project holds .agent-factory/factory/docs/factory-guide.md from the earlier installation
      When the user runs update-factory
      Then .agent-factory/factory/docs/factory-guide.md does not exist

    Scenario: The changelog names the new path of the guide's content
      # trace: FH-07-04
      Then the CHANGELOG.md entry of the release names the move of factory-guide.md
      And it names the path .agent-factory/factory/docs/handbook/
      # DEC-07

  Rule: User finds the content of the factory guide on user handbook pages
    # actor: User
    # trace: FH-08

    Scenario: The user handbook has its twelve chapters
      # trace: FH-08-01
      Then packages/factory/docs/handbook/ holds an index.md and the chapter folders getting-started/, concepts/, playbooks/, agent-context/, quality-and-review/, branches-and-dispatch/, research/, cli-integrations/, installation-and-updates/, usage-capture/, reference/, and troubleshooting/
      And each chapter folder holds an index.md

    Scenario: Every section of the guide has a user handbook page
      # trace: FH-08-02
      Given the migration map docs/spec/work/factory-handbooks-migration-map.md
      Then every section heading of factory-guide.md at commit 4ebf5101f70c1540a0d53dcfb3d00cfa977d361a has a row in the map
      And each row names a user handbook page that exists

    Scenario: The Getting Started section becomes the getting-started tutorial
      # trace: FH-08-03
      Then packages/factory/docs/handbook/getting-started/ holds a page with type tutorial and status implemented
      And docs/spec/work/factory-handbooks-migration-map.md assigns the guide's section "Getting Started" to that page

    Scenario: The guide no longer exists in the source
      # trace: FH-08-04
      Then packages/factory/docs/factory-guide.md does not exist
      And rg factory-guide packages/ tests/ README.md docs/spec/features/ --glob '!CHANGELOG.md' --glob '!docs/spec/features/factory-handbooks.feature' finds no match
      # The handbook specification names its migration inputs by design, so the search leaves it out.

  Rule: User and contributor find the content of concepts.md and beginner-intro.md in the handbooks
    # actor: User, Contributor
    # trace: FH-09
    # @docs/README.md

    Scenario: The phase chain and the key ideas move to a concept page of the user handbook
      # trace: FH-09-01
      Then packages/factory/docs/handbook/concepts/ holds a page with type concept that holds the sections "The phase chain" and "Key ideas"
      # DEC-09

    Scenario: The directory tree moves to a reference page of the contributor handbook
      # trace: FH-09-02
      Then docs/handbook/architecture/ holds a page with type reference and status implemented that holds the project directory tree
      And the tree names packages/factory/ as the source of the factory
      # DEC-09

    Scenario: docs/README.md links to the two new pages
      # trace: FH-09-03
      Then docs/README.md links to the concept page of FH-09-01 and to the reference page of FH-09-02

    Scenario: The three replaced files are deleted, not archived
      # trace: FH-09-04
      Then docs/arc42/concepts.md and docs/arc42/beginner-intro.md do not exist
      And ~archive/ holds no copy of factory-guide.md, concepts.md, or beginner-intro.md
      # DEC-10, DEC-13

  Rule: User and contributor follow every old link to the new home of its information
    # actor: User, Contributor
    # trace: FH-10
    # @packages/factory/scripts/_link_rewrite.py::rewrite_links
    # @packages/factory/scripts/link-check::main

    Scenario: A link with an anchor points to the page that holds its section
      # trace: FH-10-01
      Given README.md links to packages/factory/docs/factory-guide.md#runtime-usage-capture
      And the migration map assigns the section "Runtime usage capture" to a page in packages/factory/docs/handbook/usage-capture/
      When the migration rewrites the links
      Then the link in README.md points to that page

    Scenario: The rewritten link keeps its anchor when the new page has the heading
      # trace: FH-10-02
      Given the page that holds "Runtime usage capture" has the heading "Runtime usage capture"
      When the migration rewrites the links
      Then the link in README.md ends with #runtime-usage-capture

    Scenario: The rewritten link drops its anchor when the new page lacks the heading
      # trace: FH-10-03
      Given the page that holds "Runtime usage capture" has no heading "Runtime usage capture"
      When the migration rewrites the links
      Then the link in README.md points to the page without an anchor

    Scenario Outline: A link without an anchor points to the page that holds the file's opening
      # trace: FH-10-04
      Given a document links to <old file> without an anchor
      When the migration rewrites the links
      Then the link points to <new page>

      Examples:
        | old file                               | new page                                                  |
        | packages/factory/docs/factory-guide.md | the top-level index.md of the user handbook               |
        | docs/arc42/concepts.md                 | the concept page of FH-09-01                              |
        | docs/arc42/beginner-intro.md           | the tutorial page of the user handbook's getting-started/ |

    Scenario: A link to the installed guide points to the installed handbook
      # trace: FH-10-05
      Given docs/adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md links to ../../.agent-factory/factory/docs/factory-guide.md
      When the migration rewrites the links
      Then the link points to ../../.agent-factory/factory/docs/handbook/index.md

    Scenario: A record changes only in its link targets
      # trace: FH-10-06
      Given docs/findings/BUG-0042.md links to one of the three deleted files
      When the migration rewrites the links
      Then the diff of docs/findings/BUG-0042.md changes only link destinations
      # DEC-14

    Scenario: No tracked Markdown file links to a deleted file
      # trace: FH-10-07
      When the migration is complete
      Then no tracked Markdown file outside .agent-factory/ holds a link to factory-guide.md, docs/arc42/concepts.md, or docs/arc42/beginner-intro.md
      And link-check reports no problem for any rewritten link, in live documents and in records

    Scenario: link-check passes over every live document
      # trace: FH-10-08
      When the contributor runs link-check over every live document
      Then link-check exits 0

  Rule: Contributor runs the test suite against the handbook pages
    # actor: Contributor
    # trace: FH-11
    # @tests/factory/test_brownfield_order.py::test_factory_guide_names_scope_map_before_dsl
    # @tests/factory/test_hook_missing_factory.py::test_guide_documents_the_key
    # @tests/factory/test_core_layout_references.py::test_spec_writer_file_names_no_old_path

    Scenario: The tests read handbook pages instead of the guide
      # trace: FH-11-01
      Then no file under tests/ names factory-guide.md
      And test_core_layout_references.py keeps its scan of every spec-writer file, with the handbook path in place of docs/factory-guide.md
      And test_brownfield_order.py and test_hook_missing_factory.py keep their content assertions and read the user handbook page that now holds the checked text

    Scenario: The full test suite passes after the move
      # trace: FH-11-02
      When the contributor runs the full test suite
      Then every test passes

  Rule: User reaches the user handbook from every factory entry point
    # actor: User
    # trace: FH-12
    # @packages/factory/config/session-menu.md
    # @packages/factory/skills/newcomer-tour/SKILL.md
    # @packages/factory/skills/guided-tour/SKILL.md
    # @packages/factory/skills/explain-concept/SKILL.md
    # @packages/factory/agents/virgil.md
    # @packages/factory/INDEX.yaml
    # @packages/factory/README.md

    Scenario: Session menu H sends a new user to the getting-started tutorial
      # trace: FH-12-01
      Then the H section of session-menu.md routes a new user to the newcomer-tour skill with the user handbook's getting-started/ tutorial

    Scenario: newcomer-tour reads the getting-started tutorial
      # trace: FH-12-02
      Then the procedure of newcomer-tour reads the tutorial page of .agent-factory/factory/docs/handbook/getting-started/

    Scenario: guided-tour describes option H with the getting-started tutorial
      # trace: FH-12-03
      Then the description of option H in guided-tour names the user handbook's getting-started/ tutorial

    Scenario: explain-concept looks up user handbook pages
      # trace: FH-12-04
      Then the sources of explain-concept name .agent-factory/factory/docs/handbook/ in place of the guide

    Scenario: VIRGIL reads the user handbook
      # trace: FH-12-05
      Then virgil.md names .agent-factory/factory/docs/handbook/ in place of the guide
      And the inputs of VIRGIL in INDEX.yaml name .agent-factory/factory/docs/handbook/index.md

    Scenario: The package README keeps the commands and links to the handbook
      # trace: FH-12-06
      Then packages/factory/README.md holds the install, update, and removal commands
      And it links to the user handbook for every other topic

    Scenario: No entry point names a deleted file
      # trace: FH-12-07
      Then session-menu.md, newcomer-tour, guided-tour, explain-concept, virgil.md, INDEX.yaml, and packages/factory/README.md name neither factory-guide.md nor beginner-intro.md

  Rule: Contributor reaches the contributor handbook from the root README and the agent context
    # actor: Contributor
    # trace: FH-13
    # @README.md
    # @docs/agent-context.md

    Scenario: The root README sends a contributor to the getting-started tutorial
      # trace: FH-13-01
      Then the section "Contributing" of README.md links to the tutorial page of docs/handbook/getting-started/

    Scenario Outline: The agent context routes a contributor concern to a contributor handbook page
      # trace: FH-13-02
      Then docs/agent-context.md routes the concern "<concern>" to a page under docs/handbook/

      Examples:
        | concern                |
        | write a skill or agent |
        | add a gate             |
        | release                |

  Rule: Contributor finds the first contributor chapters written and the others started as stubs
    # actor: Contributor
    # trace: FH-14

    Scenario: The contributor handbook has its nine chapters
      # trace: FH-14-01
      Then docs/handbook/ holds an index.md and the chapter folders getting-started/, architecture/, agents-and-skills/, gates-and-hooks/, cli-integrations/, testing/, workflow/, release/, and contributing/
      And each chapter folder holds an index.md

    Scenario: The getting-started tutorial runs from git clone to a passing test run
      # trace: FH-14-02
      Given a person follows the tutorial page of docs/handbook/getting-started/ from its first step
      When the person runs each command of the tutorial in order
      Then the person starts with git clone and ends with a passing test run
      And every script and path that the tutorial names exists in the repository
      # DEC-08

    Scenario: The contributing chapter describes the page format, the stub rule, and both scripts
      # trace: FH-14-03
      Then docs/handbook/contributing/ holds implemented pages that describe the page format, the stub rule, handbook-index, and handbook-lint
      # DEC-08

    Scenario: Every other contributor chapter holds at least one stub that names its sources
      # trace: FH-14-04
      Then each of architecture/, agents-and-skills/, gates-and-hooks/, cli-integrations/, testing/, workflow/, and release/ holds at least one page with status stub
      And each stub holds one sentence of scope and at least one link to a source

    Scenario: The directory-tree reference page of architecture/ is written in full
      # trace: FH-14-05
      Then the reference page of FH-09-02 has status implemented
      And architecture/ still holds at least one stub, as FH-14-04 requires
