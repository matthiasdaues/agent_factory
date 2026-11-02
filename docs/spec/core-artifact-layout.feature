# scope: global
Feature: Core artifact layout

  Every file of a project's specification core lives in docs/spec/, and no
  other file sits at the top of that folder. Feature files live in
  docs/spec/features/, payload schemas in docs/spec/schemas/, area specs in
  docs/spec/areas/, and the working output of agents in docs/spec/work/.
  The script migrate-spec-layout moves an installed project into this layout
  during the factory update. The terms of the domain vocabulary live in
  docs/spec/glossary.md, and docs/agent-context.md is the one routing file.

  Proposal trace: docs/proposals/core-artifact-layout.md

  Rule: Newcomer finds the whole specification core at one root
    # actor: Newcomer

    Scenario: The top of the specification folder holds only core files
      Given the factory's own repository after its migration
      When the newcomer lists the top of docs/spec/
      Then every file there is one of the single-file core artifacts of the proposal's core table
      And the only folders there are features/, schemas/, areas/, and work/

    Scenario: The payload schema folder exists only with payload schemas
      Given a migrated project without payload schemas
      When the newcomer lists the top of docs/spec/
      Then no folder named schemas/ exists

    Scenario: Working output and todo lists live in the work folder
      Given a migrated project that had gaps reports, QA strategies, prd.md, SPEC-UPDATE-SUMMARY.md, todo.md, and todos.md
      When the newcomer opens docs/spec/work/
      Then each of these files is there under its old file name

    Scenario: Files that do not specify the system stay outside the specification folder
      Given a migrated project
      When the newcomer looks for testing.yaml, agent-context.md, the ADRs, and the arc42 chapters
      Then docs/testing.yaml and docs/agent-context.md are in docs/
      And the ADRs are in docs/adr/
      And the arc42 chapters are in docs/arc42/

  Rule: Project maintainer previews the layout migration without changes
    # actor: Project maintainer

    Scenario: Dry run prints the plan and changes no file
      Given a copy of an installed project in the old layout
      When the project maintainer runs migrate-spec-layout --dry-run
      Then the script prints every planned move and every planned link rewrite
      And git status shows no change in the project

  Rule: Project maintainer moves the project into the new layout with its history kept
    # actor: Project maintainer

    Scenario Outline: A file of the path table moves with git
      Given a project in the old layout with the file <old path>
      When the project maintainer runs migrate-spec-layout
      Then the file is at <new path>
      And git records the change as a rename

      Examples:
        | old path                                             | new path                               |
        | docs/spec/payments.feature                           | docs/spec/features/payments.feature    |
        | docs/spec/supplementary_specs/entity-model.md        | docs/spec/entity-model.md              |
        | docs/spec/supplementary_specs/state-machines.md      | docs/spec/state-machines.md            |
        | docs/spec/supplementary_specs/validation-rules.md    | docs/spec/validation-rules.md          |
        | docs/spec/supplementary_specs/interface-contracts.md | docs/spec/interface-contracts.md       |
        | docs/arc42/architecture.dsl                          | docs/spec/architecture.dsl             |
        | docs/arc42/dependency-rules.dsl                      | docs/spec/dependency-rules.dsl         |
        | docs/spec/prd.md                                     | docs/spec/work/prd.md                  |
        | docs/spec/payments-gaps.md                           | docs/spec/work/payments-gaps.md        |
        | docs/spec/payments-qa-strategy.md                    | docs/spec/work/payments-qa-strategy.md |
        | docs/spec/SPEC-UPDATE-SUMMARY.md                     | docs/spec/work/SPEC-UPDATE-SUMMARY.md  |
        | docs/spec/todo.md                                    | docs/spec/work/todo.md                 |
        | docs/spec/todos.md                                   | docs/spec/work/todos.md                |
        | docs/spec/supplementary_specs/billing.md             | docs/spec/areas/billing.md             |
        | docs/spec/supplementary_specs/billing-qa-strategy.md | docs/spec/work/billing-qa-strategy.md  |

    Scenario: The Structurizr theme moves next to the rendered images
      Given a project with docs/arc42/themes/default/theme.json and a DSL that loads it
      When the project maintainer runs migrate-spec-layout
      Then the theme is in docs/assets/themes/default/
      And the theme line of docs/spec/architecture.dsl reads theme ../assets/themes/default/theme.json
      And structurizr validate accepts docs/spec/architecture.dsl

    Scenario: The actor-goal list and the use-case files are removed, also from the archive
      Given a project with docs/~archive/spec/actor-goal-list.md, docs/~archive/spec/use_cases/, and other archived files
      When the project maintainer runs migrate-spec-layout
      Then git records actor-goal-list.md and every file in use_cases/ as removed
      And every other file in docs/~archive/ is unchanged

    Scenario: A project already in the new layout gives the script no work
      Given a project in the new layout
      And chapter 12 holds its link to docs/spec/glossary.md and a list of references
      And docs/arc42/CONTEXT-MAP.md waits for the fold of routing
      When the project maintainer runs migrate-spec-layout
      Then the script moves no file, prints nothing, and exits 0

    Scenario: A failure partway undoes every change of the script
      Given a project in the old layout whose git status shows no change
      And one planned move fails after earlier moves, one link rewrite, and the rewrite of the factory hook block succeeded
      When migrate-spec-layout handles the failure
      Then git status shows no change against the state before the run
      And the script exits non-zero

  Rule: Project maintainer keeps every Markdown link working after the move
    # actor: Project maintainer
    # @packages/factory/scripts/link-check::check

    Scenario: A link that points at an old path points at the new path
      Given docs/arc42/09_architecture_decisions.md links to ../spec/supplementary_specs/entity-model.md
      When the project maintainer runs migrate-spec-layout
      Then the link points at ../spec/entity-model.md

    Scenario: Relative links inside a moved file are rebased
      Given docs/spec/todo.md links to ../reviews/retro.md
      When the project maintainer runs migrate-spec-layout
      Then docs/spec/work/todo.md links to ../../reviews/retro.md
      And link-check passes on docs/spec/work/todo.md

    Scenario: A link to a removed file becomes its link text in a code span
      Given docs/spec/scope-map.md links to ../~archive/spec/use_cases/UC-04-dispatch-an-agent-via-trigger.md with the text UC-04
      When the project maintainer runs migrate-spec-layout
      Then the scope map shows `UC-04` in a code span instead of the link
      And link-check passes on docs/spec/scope-map.md

    Scenario: Link check passes on the migrated project
      Given a copy of an installed project in the old layout
      When the project maintainer runs migrate-spec-layout
      Then link-check passes on every Markdown file under docs/

  Rule: Project maintainer learns every old path that the script does not rewrite
    # actor: Project maintainer

    Scenario: An old path outside Markdown is listed and left unchanged
      Given .github/workflows/docs.yml names docs/arc42/architecture.dsl
      When the project maintainer runs migrate-spec-layout
      Then the script prints the file, the line, and the old path
      And .github/workflows/docs.yml is unchanged

    Scenario: The project's own hooks keep their old paths and are listed
      Given the project's .pre-commit-config.yaml has its own hook whose files pattern names docs/spec/supplementary_specs/
      When the project maintainer runs migrate-spec-layout
      Then that hook is unchanged
      And the script prints its old path like any other occurrence

  Rule: Project maintainer gets one glossary from chapter 12 and from every vocabulary file
    # actor: Project maintainer

    Scenario: Chapter 12 tables move into the glossary under their headings
      Given docs/arc42/12_glossary.md holds the section "Usage Analysis Vocabulary" with a two-column table
      When the project maintainer runs migrate-spec-layout
      Then docs/spec/glossary.md has the section "Usage Analysis Vocabulary" with that table's terms
      And docs/arc42/12_glossary.md starts with one line that links to docs/spec/glossary.md

    Scenario: Git shows the glossary as a new file and keeps the history of chapter 12
      Given docs/arc42/12_glossary.md holds a two-column table and has earlier commits
      When the project maintainer runs migrate-spec-layout
      Then git shows docs/spec/glossary.md as added
      And git shows docs/arc42/12_glossary.md as modified
      And git log docs/arc42/12_glossary.md lists the commits from before the migration

    Scenario: A table directly under the chapter title becomes the section Terms
      Given docs/arc42/12_glossary.md holds a two-column table directly under its title
      When the project maintainer runs migrate-spec-layout
      Then docs/spec/glossary.md has the section "Terms" with that table's terms

    Scenario: A two-column table gets the columns Term, Definition, and Avoid
      Given a chapter 12 table with the columns "Begriff" and "Bedeutung"
      When the project maintainer runs migrate-spec-layout
      Then the glossary table has the columns Term, Definition, and Avoid
      And every Avoid cell is empty

    Scenario: A section without a table stays in chapter 12
      Given docs/arc42/12_glossary.md holds the section "Referenced from" with a list of links
      When the project maintainer runs migrate-spec-layout
      Then that section stays in docs/arc42/12_glossary.md below the link line

    Scenario: The terms of a CONTEXT.md become a section of their own
      Given docs/CONTEXT.md has the title "Billing" and a "## Language" section in the template's list form
      When the project maintainer runs migrate-spec-layout
      Then docs/spec/glossary.md has the section "Billing" as a table with the columns Term, Definition, and Avoid
      And each "_Avoid_:" entry of the list form is in the Avoid cell of its term
      And docs/CONTEXT.md has no "## Language" section

    Scenario: Two vocabularies never stop the script
      Given docs/CONTEXT.md defines the term "Invoice" under "## Language"
      And docs/arc42/12_glossary.md also defines the term "Invoice"
      When the project maintainer runs migrate-spec-layout
      Then docs/spec/glossary.md holds both sets of terms in separate sections
      And the script lists "Invoice" as a term that appears in more than one section
      And the script exits 0

    Scenario: A per-context CONTEXT.md becomes that context's section
      Given docs/arc42/CONTEXT-MAP.md lists the context "Ledger" with packages/ledger/CONTEXT.md
      And packages/ledger/CONTEXT.md has a "## Language" section
      When the project maintainer runs migrate-spec-layout
      Then docs/spec/glossary.md has a section for "Ledger" with its terms
      And packages/ledger/CONTEXT.md has no "## Language" section

    Scenario: A CONTEXT.md without terms holds routing only and stays in place
      Given docs/CONTEXT.md has no "## Language" section
      When the project maintainer runs migrate-spec-layout
      Then docs/CONTEXT.md is unchanged

    Scenario: No CONTEXT.md keeps a Language section after the migration
      Given a project with several CONTEXT.md files that have a "## Language" section
      When the project maintainer runs migrate-spec-layout
      Then no CONTEXT.md in the project has a "## Language" section

    Scenario: The script names the two follow-up steps
      Given a migrated project with docs/arc42/CONTEXT-MAP.md and a listed duplicate term
      When migrate-spec-layout finishes
      Then the script names capture-context --fold-context-map as the step that folds the routing
      And the script names the cleanup of duplicate glossary terms, for example with domain-modeling

  Rule: Project maintainer receives the new layout with the factory update
    # actor: Project maintainer
    # @packages/factory/scripts/update-factory::_run_init
    # @packages/factory/scripts/init-factory::load_prior_manifest

    Scenario: An update from a version before the layout moves the files
      Given a project whose .agent-factory/install.json records a factory version older than the layout release
      When the project maintainer approves the factory update
      Then init-factory runs migrate-spec-layout as its last step
      And the project is in the new layout
      And the project maintainer was not asked about the move

    Scenario Outline: An install record without a usable version counts as older
      Given a project in the old layout whose .agent-factory/install.json has <factory_version entry>
      When the project maintainer approves the factory update
      Then the project is in the new layout

      Examples:
        | factory_version entry          |
        | no factory_version key         |
        | factory_version set to unknown |

    Scenario: A first install moves no file and lists the old paths
      Given a project in the old layout without .agent-factory/install.json
      When the project maintainer installs the factory
      Then init-factory moves no file
      And init-factory lists each old path it finds
      And init-factory names migrate-spec-layout as a command the project maintainer can run

    Scenario: A later run of init-factory at the same version moves nothing
      Given a project whose .agent-factory/install.json records the layout release or a later one
      When the project maintainer runs init-factory again
      Then init-factory does not run migrate-spec-layout
      And no project file moves

    Scenario: A failed migration rolls the update back
      Given a project in the old layout and an approved factory update
      And migrate-spec-layout fails partway
      And migrate-spec-layout had rewritten one Markdown link and the factory hook block before it failed
      When update-factory handles the failure of init-factory
      Then every project file has its old path and its old content
      And .pre-commit-config.yaml has its old content
      And .agent-factory/install.json records the old factory version
      And the factory tree is the old one
      And update-factory reports the failure
      # @packages/factory/scripts/update-factory::_rollback_update

    Scenario: The factory hook block follows the template without a question
      Given a project in the old layout whose agent_factory_hook-* block has the old files pattern for arch-lint
      When the project maintainer approves the factory update
      Then each factory hook in the block has the files value of the new hook template
      And a change to docs/spec/architecture.dsl triggers arch-lint
      And a change to docs/arc42/05_building_block_view.md triggers arch-lint
      And the project maintainer was not asked about the hooks

  Rule: Project maintainer folds context routing into the agent context file
    # actor: Project maintainer
    # @packages/factory/skills/capture-context/SKILL.md

    Scenario: The fold writes one domain concern per listed context
      Given docs/arc42/CONTEXT-MAP.md lists three contexts
      When the project maintainer runs capture-context --fold-context-map
      Then docs/agent-context.md has one domain concern per listed context
      And each of these concerns is marked as folded
      And each of these concerns has a Read path that concern-lint accepts
      And the skill shows the result to the project maintainer
      And concern-lint passes

    Scenario: The fold reads a CONTEXT.md that holds routing only
      Given docs/CONTEXT.md has no "## Language" section and names a context
      When the project maintainer runs capture-context --fold-context-map
      Then docs/agent-context.md has a domain concern for that context

    Scenario: The fold points every link at the agent context file
      Given docs/arc42/concepts.md links to CONTEXT-MAP.md
      And a review report under docs/reviews/ links to docs/CONTEXT.md
      When the project maintainer runs capture-context --fold-context-map
      Then both links point at docs/agent-context.md

    Scenario: The old routing files are gone after the project maintainer deletes them
      Given the fold has finished
      When the project maintainer deletes docs/CONTEXT.md and docs/arc42/CONTEXT-MAP.md
      Then neither file exists
      And link-check passes on every Markdown file under docs/

    Scenario: A later rescan keeps every folded concern
      Given docs/agent-context.md holds concerns marked as folded that are not scope-map areas
      When the project maintainer runs capture-context --update --scan
      Then the rescan offers no removal of a folded concern
      And every folded concern stays in docs/agent-context.md

  Rule: Project maintainer's gates check the core at its new paths
    # actor: Project maintainer

    Scenario Outline: Each gate fails on a deliberate error at the new path
      Given a copy of the factory's repository after its migration
      And <file> holds a deliberate error that <gate> reports
      When the project maintainer runs <gate>
      Then <gate> exits non-zero

      Examples:
        | gate                 | file                                            |
        | link-check           | docs/spec/work/todo.md                          |
        | arch-lint            | docs/spec/architecture.dsl                      |
        | structurizr validate | docs/spec/architecture.dsl                      |
        | dependency-check     | docs/spec/dependency-rules.dsl                  |
        | spec-lint            | docs/spec/validation-rules.md                   |
        | scope-lint           | docs/spec/features/core-artifact-layout.feature |
        | statemachine-lint    | docs/spec/state-machines.md                     |

    Scenario: The architecture tools read the DSL from the specification folder
      Given a migrated project
      When the project maintainer runs arch-lint and structurizr
      Then both read architecture.dsl from docs/spec/
      And arch-lint reads chapter 5 from docs/arc42/
      # @packages/factory/scripts/arch-lint::main

    Scenario Outline: A change to the DSL runs the architecture lint as a hook
      Given <project>
      When the project maintainer runs pre-commit run --files docs/spec/architecture.dsl
      Then pre-commit runs arch-lint

      Examples:
        | project                                          |
        | the factory's own repository after its migration |
        | a project installed from the new hook template   |

  Rule: Project maintainer checks glossary terms and business rules without use-case files
    # actor: Project maintainer
    # @packages/factory/scripts/spec-lint::check_glossary
    # @packages/factory/scripts/spec-lint::check_traceability

    Scenario: GLOSS001 reports a term that only the glossary and working output use
      Given docs/spec/glossary.md defines the term "Settlement" in its table
      And only docs/spec/glossary.md and docs/spec/work/payments-gaps.md use "Settlement"
      When the project maintainer runs spec-lint
      Then spec-lint reports GLOSS001 as info for "Settlement"

    Scenario: GLOSS001 stays silent for a term that another core file uses
      Given docs/spec/glossary.md defines the term "Settlement" in its table
      And docs/spec/entity-model.md uses "Settlement"
      When the project maintainer runs spec-lint
      Then spec-lint reports no GLOSS001 finding for "Settlement"

    Scenario: GLOSS001 stays silent for a term that only a feature file uses besides the glossary
      Given docs/spec/glossary.md defines the term "Settlement" in its table
      And docs/spec/features/payments.feature uses "Settlement"
      And no other core file uses "Settlement"
      When the project maintainer runs spec-lint
      Then spec-lint reports no GLOSS001 finding for "Settlement"

    Scenario: A business rule that is referenced but never defined blocks the commit
      Given a project without use_cases/
      And docs/spec/features/payments.feature references BR-099
      And no core file defines BR-099
      When the project maintainer runs spec-lint
      Then spec-lint reports TRACE002 as an error
      And spec-lint exits 1

    Scenario: spec-lint reads no use-case file
      Given a project with docs/spec/ in the new layout
      When the project maintainer runs spec-lint
      Then spec-lint runs no check that reads use-case files
      And spec-lint runs TRACE002, TRACE003, and TRACE004

  Rule: Project maintainer publishes the architecture PDF with the glossary as chapter 12
    # actor: Project maintainer
    # @packages/factory/scripts/_docs_assemble.py::assemble

    Scenario: The PDF renders the glossary in place of the chapter 12 link
      Given the publish-docs test fixture has docs/arc42/12_glossary.md with the term "Ledger Entry"
      And its manifest selects arc42/12_glossary.md
      When migrate-spec-layout runs on the fixture
      And the project maintainer runs publish-docs
      Then publish-docs builds the PDF
      And chapter 12 of the PDF contains "Ledger Entry"

    Scenario: A manifest glob that includes chapter 12 renders the glossary
      Given a migrated project whose manifest selects arc42/*.md
      When the project maintainer runs publish-docs
      Then chapter 12 of the PDF shows the content of docs/spec/glossary.md
      And the manifest is unchanged

  Rule: Project maintainer starts feature work once the anchor files exist
    # actor: Project maintainer
    # @packages/factory/playbooks/feature-addition.md
    # @packages/factory/playbooks/brownfield-onboarding.md

    Scenario: A migrated project with the four anchor files passes the check
      Given a migrated project with docs/spec/architecture.dsl, docs/spec/scope-map.md, docs/spec/glossary.md, and docs/agent-context.md
      And the project has no docs/CONTEXT.md
      When the project maintainer starts feature-addition
      Then the anchor-file check passes
      And feature-addition proceeds

    Scenario Outline: A missing anchor file stops feature-addition
      Given a migrated project with every anchor file except <missing file>
      When the project maintainer starts feature-addition
      Then feature-addition reports <missing file> as missing
      And feature-addition suggests running brownfield-onboarding

      Examples:
        | missing file               |
        | docs/spec/architecture.dsl |
        | docs/spec/scope-map.md     |
        | docs/spec/glossary.md      |
        | docs/agent-context.md      |

    Scenario: The brownfield Stage 1 exit checks the same four anchor files
      Given a project in brownfield onboarding with docs/spec/architecture.dsl, docs/spec/scope-map.md, and docs/spec/glossary.md
      And the project has no docs/agent-context.md
      When the Stage 1 exit check of brownfield-onboarding runs
      Then the check reports docs/agent-context.md as missing

  Rule: CLI-invoked agent reads and writes the core at its new paths
    # actor: CLI-Invoked Agent

    Scenario: domain-modeling writes a new term as a glossary table row
      Given a migrated project with docs/spec/glossary.md
      When domain-modeling settles the term "Payout" for the context "Billing"
      Then the "Billing" section of docs/spec/glossary.md has a row for "Payout" with Term, Definition, and Avoid
      # @packages/factory/skills/domain-modeling/SKILL.md

    Scenario: reverse-map seeds the domain vocabulary into the glossary
      Given a project in the new layout in brownfield onboarding
      When reverse-map extracts the domain vocabulary from the code
      Then docs/spec/glossary.md holds the extracted terms in tables with the columns Term, Definition, and Avoid
      And reverse-map writes no docs/CONTEXT.md
      # @packages/factory/skills/reverse-map/SKILL.md

    Scenario: The developer agent and the reconciliation agent have no use-case fallback
      Given a migrated project without use_cases/
      When developer-agent or reconciliation-agent looks for the behaviour of a story
      Then it reads the scope map and the feature files
      And it never looks for a use-case file
      # @packages/factory/agents/developer-agent.md
      # @packages/factory/agents/reconciliation-agent.md

    Scenario: The requirements agent writes features and working output to their folders
      Given a migrated project and an accepted proposal named payments
      When requirements-agent derives the specification
      Then the feature file is docs/spec/features/payments.feature
      And the gaps report and the QA strategy are in docs/spec/work/
      # @packages/factory/skills/derive-feature/SKILL.md

  Rule: Factory maintainer keeps the factory free of old paths
    # actor: Factory maintainer

    Scenario Outline: No factory file names an old path
      Given the factory's repository after the layout change
      When the factory maintainer runs grep -rE '<pattern>' on packages/factory/, tests/factory/, and .pre-commit-config.yaml
      Then grep finds nothing outside CHANGELOG.md, reports/, scripts/migrate-spec-layout, and that script's tests

      Examples:
        | pattern                                 |
        | supplementary_specs                     |
        | docs/arc42/[a-z-]+\.dsl                 |
        | docs/spec/[^/]+\.feature                |
        | docs/spec/prd\.md                       |
        | docs/spec/[^/]+-(gaps\|qa-strategy)\.md |
        | docs/spec/todos?\.md                    |
        | docs/arc42/themes                       |
        | arc42/\(architecture                    |
        | UC-XX                                   |
        | use_cases                               |
        | actor-goal-list                         |

    Scenario: No factory file names the old routing files
      Given the factory's repository after the layout change
      When the factory maintainer runs grep -rE 'CONTEXT(-MAP)?\.md' packages/factory/
      Then grep finds nothing outside CHANGELOG.md, scripts/migrate-spec-layout and its tests, and the --fold-context-map section of capture-context

  Rule: Factory maintainer migrates the factory's own repository first
    # actor: Factory maintainer

    Scenario: The factory's own migration runs without stopping
      Given the factory's repository in the old layout
      And docs/CONTEXT.md has no "## Language" section
      When the factory maintainer runs migrate-spec-layout
      Then the script exits 0
      And docs/spec/glossary.md holds the terms of the old docs/arc42/12_glossary.md

    Scenario: Every gate passes on the migrated factory repository
      Given the factory's own repository after its migration
      When the factory maintainer runs link-check, arch-lint, structurizr validate, dependency-check, spec-lint, scope-lint, and statemachine-lint
      Then every gate exits 0

    Scenario: The factory's routing folds into the agent context file
      Given the factory's repository after migrate-spec-layout
      When the factory maintainer runs capture-context --fold-context-map
      And the factory maintainer deletes docs/CONTEXT.md and docs/arc42/CONTEXT-MAP.md
      Then docs/agent-context.md has one domain concern per context of the old CONTEXT-MAP.md
      And concern-lint passes

    Scenario: Every section of the factory's glossary is a Term table
      Given the factory's repository after its migration
      When the factory maintainer reads docs/spec/glossary.md
      Then every section is a table with the columns Term, Definition, and Avoid
      And the section "Acronyms and Abbreviations" is among them
      And GLOSS001 reads the terms of every section

    Scenario: No actor-goal list and no use-case folder remain
      Given the factory's repository after its migration
      When the factory maintainer runs find docs -name actor-goal-list.md -o -name use_cases
      Then find prints nothing
