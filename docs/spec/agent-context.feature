# scope: global
Feature: Concern-oriented agent context
Factory agents route project knowledge through one CLI-agnostic concern
registry while machine-consumed test configuration remains separate.

Proposal trace: docs/proposals/factory-concern-oriented-agent-context.md

Rule: Factory agent reads project knowledge by concern
\# actor: Factory Agent

```
Scenario: Cross-cutting concerns are always active
  Given "docs/agent-context.md" contains the required concern categories
  When a factory agent starts work
  Then it reads every concern under "Always (cross-cutting)"

Scenario: Story concerns focus implementation context
  Given a story declares controlled domain and technical concern names
  When an implementation agent reads the story
  Then it follows the matching sections in "docs/agent-context.md"
  And the declared concerns focus relevance rather than restrict file access

Scenario: Pre-backlog agents survey the registry by judgment
  Given requirements, architecture, or quality work has no story frontmatter
  When its agent needs project-native knowledge
  Then it reads the full concern registry and selects relevant sections by judgment
```

Rule: User initializes a concern registry from project evidence
\# actor: User
\# @.agent-factory/factory/skills/capture-context/SKILL.md

```
Scenario: Greenfield fitting creates the concern registry
  Given "docs/agent-context.md" does not exist
  When the user runs "capture-context --init"
  Then generic cross-cutting concerns are seeded
  And detected technologies are proposed as technical concerns
  And scope-map areas are proposed as domain concerns when a scope map exists
  And the confirmed registry is written to "docs/agent-context.md"

Scenario: Brownfield fitting enriches concern paths
  Given a project contains existing documentation and implementation signals
  When the user runs "capture-context --init --scan"
  Then the scan proposes concern names and existing "Read:" and "Boundary:" paths
  And the user confirms the proposed concern batches before they are written

Scenario: Registry sections have one stable shape
  Given the confirmed concern vocabulary
  When "docs/agent-context.md" is written
  Then it contains "Always (cross-cutting)", "Technical concerns", and "Domain concerns"
  And each concern has a description and at least one "Read:" path
```

Rule: User migrates legacy context into the concern registry
\# actor: User
\# @.agent-factory/factory/skills/capture-context/SKILL.md

```
Scenario: Bare capture-context offers legacy YAML migration
  Given any legacy YAML agent-context file exists
  When the user invokes "capture-context" without flags
  Then it proposes concern sections derived from the legacy values and paths
  And it waits for user confirmation before changing files

Scenario: Confirmed migration leaves one routing format
  Given the user confirms the proposed concern registry
  When migration completes
  Then "docs/agent-context.md" contains the confirmed concerns
  And test configuration is at "docs/testing.yaml"
  And the legacy YAML agent-context files and "docs/charter/" are absent

Scenario: Declined migration preserves the existing project
  Given migration has presented a proposed concern registry
  When the user declines
  Then the legacy files remain unchanged
  And "docs/agent-context.md" is not created by that invocation
```

Rule: Planning maintainer assigns controlled concerns to stories
\# actor: Planning maintainer

```
Scenario: Story concerns use the confirmed vocabulary
  Given the concern registry contains technical and domain concern headings
  When the planning maintainer writes a story
  Then its "concerns" mapping names only matching technical and domain headings
  And cross-cutting concerns are omitted because they are always active

Scenario: A missing concern requires confirmation
  Given a story needs knowledge not represented by a registered concern
  When the planning maintainer prepares the story
  Then it proposes a concern name, description, and initial file list
  And it adds the concern only after user confirmation
```

Rule: Project team maintains concern routes directly
\# actor: Project team

```
Scenario: Maintainer updates a moved knowledge path
  Given a registered "Read:" or "Boundary:" path has moved
  When the maintainer edits its concern section in "docs/agent-context.md"
  Then the registry contains the current project-local path

Scenario: update-context reports its retirement
  Given the concern-oriented model is active
  When a user invokes the "update-context" skill
  Then the skill reports that direct "docs/agent-context.md" editing replaces it
  And it performs no write
```

Rule: concern-lint validates concern structure and references
\# actor: concern-lint
\# @.agent-factory/factory/scripts/concern-lint

```
Scenario: CTX-SECTIONS validates the registry shape
  Given "docs/agent-context.md" is present
  When "concern-lint" runs
  Then "CTX-SECTIONS" requires all three category headings
  And each concern has a description and at least one "Read:" path

Scenario: CTX-PATHS validates routed paths
  Given a concern contains "Read:" and "Boundary:" paths
  When "concern-lint" runs
  Then "CTX-PATHS" reports every path or glob with no repository match

Scenario: CTX-REFS validates story concern names
  Given the registry and backlog stories exist
  When "concern-lint" runs
  Then "CTX-REFS" reports every story concern without a matching technical or domain heading

Scenario: CTX-LEGACY rejects competing context formats
  Given "docs/agent-context.md" exists beside legacy YAML context or "docs/charter/"
  When "concern-lint" runs
  Then "CTX-LEGACY" reports the legacy residue
```

Rule: Test configuration remains separate from context routing
\# actor: Test regime detector
\# @.agent-factory/factory/skills/detect-test-regime/SKILL.md

```
Scenario: detect-test-regime writes the canonical configuration path
  Given the project test suites have been scanned
  When "detect-test-regime" records the test regime
  Then it writes machine-consumed configuration to "docs/testing.yaml"
  And it does not place test configuration in the concern registry

Scenario: Factory consumers use only the canonical test path
  Given a factory gate needs test configuration
  When it resolves the configuration
  Then it reads "docs/testing.yaml"
  And it does not fall back to a legacy charter or agent-context directory
```

Rule: Factory governance codifies concern-oriented composition
\# actor: Factory governance

```
Scenario: Composition rules distinguish routing from configuration
  Given the concern-oriented feature is implemented
  When a developer reads the agent-context composition convention
  Then it defines concern categories, controlled vocabulary, and direct maintenance
  And it identifies "docs/testing.yaml" as machine configuration rather than routing

Scenario: Factory consumers use the concern registry
  Given a factory agent, skill, playbook, script, or hook needs project-native knowledge
  When its active definition is inspected
  Then it routes that knowledge through "docs/agent-context.md"
  And no active consumer requires the retired YAML routing model
```
