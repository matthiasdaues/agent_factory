# EPICs -- Test Design Skill

Proposal trace: [test-design-skill.md](../docs/proposals/test-design-skill.md)
Feature trace: [test-design.feature](../docs/spec/test-design.feature)

## EPIC 1: Establish risk-class conventions and gate configuration

### Actor Goals

- Human Operator configures risk classes per project in testing.yaml
- Human Operator configures gate thresholds centrally in testing.yaml
- Dispatcher resolves CRAP threshold from testing.yaml gates section

### Demo

A human operator opens `factory/rulebooks/conventions/testing-strategy.md` and sees three risk classes (critical, standard, structural) with their failure-scenario formats and budget rules. They open `docs/charter/testing.yaml`, add a `gates:` section with `crap_score.threshold: 8`, and the `crap-score` script uses that threshold instead of its hardcoded default of 30.

### Scope

Extend the testing strategy with risk-class definitions. Add `gates` and `risk_classes` sections to `testing.yaml` and the charter template. Migrate the CRAP threshold from the dead-code `read_threshold_from_house_rules()` path to `testing.yaml`.

### Dependencies

None. This is the foundational EPIC.

### Boundaries

- Rulebook: `factory/rulebooks/conventions/testing-strategy.md`
- Charter: `docs/charter/testing.yaml`
- Template: `factory/rulebooks/templates/charter-testing.yaml`
- Script (Validator): `factory/scripts/crap-score`
- Skill: `factory/skills/crap-score/SKILL.md`

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                               | Tier    | Estimate |
| ------- | -------------------------------------------------------- | ------- | -------- |
| ST-0182 | Extend testing strategy with risk-class definitions      | economy | 0.5 day  |
| ST-0183 | Add gates and risk_classes configuration to testing.yaml | economy | 0.5 day  |
| ST-0184 | Migrate CRAP threshold to testing.yaml gates section     | economy | 0.5 day  |

## EPIC 2: Build the test-design skill and integrate into backlog sequence

### Actor Goals

- Planning Agent designs test scenarios from feature contracts before stories are cut
- Planning Agent guards on detect-test-regime prerequisite
- Planning Agent assigns one test owner per contract across the backlog
- Planning Agent classifies contracts by risk class to determine test treatment
- Planning Agent propagates prior tests to non-owning stories
- Planning Agent integrates test-design as optional step in create-backlog sequence
- Planning Agent carries test-design sections from epics.md into story files

### Demo

A planning agent invokes `test-design` after epic slicing. The skill reads `.feature` contracts and the scope map, assigns one test owner per contract across the backlog, classifies each contract by risk class (critical, standard, structural), and writes Given/When/Then/Forbidden failure scenarios for critical contracts into `epics.md`. When the planning agent then runs `create-backlog-stories`, each story file carries its Test Design and Prior Tests sections verbatim from `epics.md`. The create-backlog-write-epics skill prompts the user about the test-design option before proceeding to step 3.

### Scope

Create the new `test-design` skill with prerequisite guard, ownership resolution, risk-class classification, failure-scenario generation, and Prior Tests propagation. Wire the skill into the `create-backlog` sequence as optional step 2.5. Update `create-backlog-stories` to carry test-design sections into story files.

### Dependencies

EPIC 1 (risk-class definitions must exist in the testing strategy before the test-design skill can reference them).

### Boundaries

- Skill (new): `factory/skills/test-design/SKILL.md`
- Skill: `factory/skills/create-backlog/SKILL.md`
- Skill: `factory/skills/create-backlog-write-epics/SKILL.md`
- Skill: `factory/skills/create-backlog-stories/SKILL.md`

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                             | Tier     | Estimate |
| ------- | ------------------------------------------------------ | -------- | -------- |
| ST-0185 | Create the test-design skill                           | standard | 1 day    |
| ST-0186 | Integrate test-design into the create-backlog sequence | economy  | 0.5 day  |

## EPIC 3: Prescribe the developer RED phase and verify test-design completeness

### Actor Goals

- Developer-Agent consumes prescribed RED phase from test-design output
- Developer-Agent falls back to existing behavior without test-design
- Dispatcher validates test-design completeness via gate script
- Dispatcher reads gate configuration from testing.yaml

### Demo

A developer-agent opens a story that contains a Test Design section and writes exactly the prescribed failure scenarios as failing tests -- no invented tests, no substitutions. A separate story without test-design output still works with the existing Red-Green-Refactor cycle. The `test-design-verify` gate script validates that every `.feature` scenario reachable through the story's traces has a corresponding test assertion or valid waiver, exiting 0 on pass and 1 on failure. The dispatcher reads per-gate enabled/threshold configuration from `testing.yaml` instead of hardcoding, and ADR-0012 documents `test_design_verify` as a conditional gate.

### Scope

Update the developer-agent to consume test-design output as its RED phase with backward-compatible fallback. Create the `test-design-verify` gate script with trace-to-scenario resolution chain and waiver validation. Update the implementation-agent to read gate config from `testing.yaml` and amend ADR-0012.

### Dependencies

EPIC 2 (test-design skill must exist before consumption and verification can be built).
EPIC 1 (gates section must exist in testing.yaml for dispatcher integration).

### Boundaries

- Agent: `factory/agents/developer-agent.md`
- Script (Validator, new): `factory/scripts/test-design-verify`
- Agent: `factory/agents/implementation-agent.md`
- ADR: `docs/adr/0012-dispatcher-owned-semantic-gate-loop.md`

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                                     | Tier     | Estimate |
| ------- | -------------------------------------------------------------- | -------- | -------- |
| ST-0187 | Update developer-agent to consume prescribed RED phase         | economy  | 0.5 day  |
| ST-0188 | Create the test-design-verify gate script                      | standard | 1 day    |
| ST-0189 | Update dispatcher to read gate configuration from testing.yaml | standard | 0.5 day  |
