# EPICs — Test-Design Layer Redistribution

Proposal trace: [test-design-layer-redistribution.md](../docs/proposals/test-design-layer-redistribution.md)

## EPIC A: Testability Probe and Planning Integration

### Why this EPIC exists

Without a lightweight testability check at planning time, untestable epic scoping passes silently into story slicing — surfacing only when a developer tries and fails to write a meaningful test. The current test-design skill catches this, but at the cost of authoring detailed failure scenarios against code that does not exist yet. This EPIC extracts the planning-level signal (testability assessment and contract ownership resolution) into a dedicated probe and wires it into the create-backlog sequence, so that planning retains its gate while shedding the speculative test authoring.

### Actor Goals

- Planning agent assesses whether each epic's actor goals can be expressed as observable, assertable outcomes, and flags scoping defects when they cannot
- Planning agent resolves contract ownership (one owner per contract, backlog-wide) at epic level, recording ownership assignments in `backlog/epics.md` without writing failure scenarios or test paths
- The `create-backlog` sequence references `testability-probe` at phase 2.5 instead of `test-design`, and the `create-backlog-write-epics` skill surfaces the probe as the pre-story-slicing option
- The `create-backlog-stories` skill carries ownership assignments — not failure scenarios — from `epics.md` into individual story files

### Demo

1. The user runs `create-backlog-write-epics` and produces a confirmed `backlog/epics.md` with three EPICs.
2. The planning agent invokes `testability-probe` against the confirmed epics.
3. For each EPIC, the probe writes a testability paragraph assessing whether the actor goals produce observable, assertable outcomes. One EPIC has an acceptance criterion that resists concrete testing — the probe flags it as a testability red flag.
4. The probe identifies instrumentation boundaries (system seams tests would instrument) per EPIC, naming the seams without writing test cases.
5. The probe resolves contract ownership across the full backlog: for each traced contract, it records "contract X owned by ST-NNNN" in `epics.md`, using topological ordering from EPIC dependencies and building-block inventory row order.
6. The user reviews the testability assessment and ownership table, confirms or adjusts, and proceeds to story slicing.
7. When `create-backlog-stories` runs, each story file receives ownership assignments from `epics.md` — no `#### Failure scenarios` or `#### Prior Tests` sections appear in new stories.

### Scope

**In:**

- `testability-probe` skill at `factory/skills/testability-probe/SKILL.md` — new skill with four concerns: testability assessment (observable outcomes), instrumentation boundary identification (naming seams), testability red-flag detection (scoping defects), and backlog-wide contract ownership resolution (topological sort, one owner per contract)
- Testability-probe output format — a short section per EPIC in `backlog/epics.md` containing a testability paragraph plus an ownership table, not a scenario catalog
- `create-backlog` parent skill sequence table — phase 2.5 row changes from `test-design` to `testability-probe`
- `create-backlog-write-epics` skill — the "Optional: Invoke test-design" section becomes "Invoke testability-probe" (mandatory, per resolved open question)
- `create-backlog-stories` skill — carry ownership assignments from `epics.md` into story files; stop carrying `#### Failure scenarios` and `#### Prior Tests` sections for new stories

**Out:**

- Refactoring the `test-design` skill itself (EPIC B)
- Developer agent changes (EPIC B)
- QA, reconciliation, and gate changes (EPIC C)
- Changes to `backlog-lint` validation rules (explicitly deferred per proposal)

### Dependencies

None. This is the foundational EPIC.

### Boundaries

- Skill: `factory/skills/testability-probe/SKILL.md` (new)
- Skill: `factory/skills/create-backlog/SKILL.md` (sequence table edit)
- Skill: `factory/skills/create-backlog-write-epics/SKILL.md` (probe invocation section)
- Skill: `factory/skills/create-backlog-stories/SKILL.md` (ownership propagation)
- Planning agent: `factory/agents/planning-agent.md` (skill list update)

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                                                                      | Tier     | Size | Basis                                                                                               |
| ------- | --------------------------------------------------------------------------------------------------------------- | -------- | ---- | --------------------------------------------------------------------------------------------------- |
| ST-0226 | Create the `testability-probe` skill with testability assessment and backlog-wide contract ownership resolution | standard | L    | New skill procedure (4 concerns, prerequisite guard, output format), substantial authoring effort   |
| ST-0227 | Wire `testability-probe` into the create-backlog sequence and update planning-integration skills                | economy  | M    | Three existing skills edited (sequence table, invocation section, story propagation), low ambiguity |

## EPIC B: Implementation-Time Test Design

### Why this EPIC exists

With testability assessment moved to the probe (EPIC A), the `test-design` skill's detailed machinery — failure scenarios, risk classification, edge-case identification — no longer runs at planning time against imagined code. This EPIC refactors it as an implementation skill that the developer agent invokes post-GREEN with actual code in hand. The developer gets a two-pass TDD model (pass 1: acceptance-criteria TDD, pass 2: test-design for integration gaps) and records test traceability in the story file at commit time, giving downstream agents (QA, reconciliation) a mechanical signal to audit.

### Actor Goals

- The developer agent invokes the narrowed `test-design` skill after GREEN on non-`.feature`-governed stories to identify and author integration and edge-case tests from implemented code
- The developer agent skips the post-TDD `test-design` invocation for `.feature`-governed stories, where the `.feature` file is the test design
- The developer agent writes the `tests:` field (test modules the story owns) and the `test-design-pass` field (`done` or `skipped-feature-governed`) in the story file at commit time
- The story template documents the `tests:` and `test-design-pass` fields so future backlog authors and developers know their purpose

### Demo

1. The developer agent picks up a non-`.feature`-governed story and implements it through the standard RED-GREEN-REFACTOR cycle (pass 1: tests derived from acceptance criteria).
2. After GREEN, the developer agent invokes `test-design` against the implemented code.
3. The `test-design` skill reads the code, classifies owned contracts by risk class, and identifies two integration paths the TDD cycle did not cover.
4. The skill authors two additional test files in the test suite covering those paths.
5. The developer agent writes `tests: [tests/unit/test_foo.py, tests/integration/test_foo_seam.py]` and `test-design-pass: done` into the story file's frontmatter at commit time.
6. A second developer agent picks up a `.feature`-governed story and completes RED-GREEN-REFACTOR.
7. The developer agent skips the `test-design` invocation and writes `test-design-pass: skipped-feature-governed` into the story file.
8. The story template at `factory/rulebooks/templates/story.md` shows `tests:` and `test-design-pass` field documentation alongside existing frontmatter fields.

### Scope

**In:**

- `test-design` skill refactoring — the procedure at `factory/skills/test-design/SKILL.md` rewrites to the story-level procedure described in the proposal's Change 2: reads implemented code, reads ownership assignments from `epics.md`, classifies contracts by risk class, identifies untested integration paths, and authors test files in the project's test suite
- `test-design` skill boundaries — does not resolve ownership (the probe did that), does not write into `epics.md`, does not run for `.feature`-governed stories
- Developer agent workflow update at `factory/agents/developer-agent.md` — adds `test-design` to skill list, two-pass TDD model (pass 1: acceptance criteria, pass 2: test-design post-GREEN), conditional skip for `.feature`-governed stories
- Developer agent commit-time fields — writes `tests:` and `test-design-pass` into story frontmatter
- Story template update at `factory/rulebooks/templates/story.md` — documents the two new fields

**Out:**

- QA agent review criteria (EPIC C)
- Reconciliation agent traceability audit (EPIC C)
- `test-design-verify` gate adaptation (EPIC C)
- `testing-strategy.md` convention update (EPIC C)
- Backward compatibility for old `#### Failure scenarios` — already handled by the developer agent's existing conditional path; this EPIC stops generating new ones but does not remove old ones

### Dependencies

EPIC A (the developer agent's `test-design` invocation reads ownership assignments written by the testability probe; the probe must exist and be wired into the sequence before the implementation-time skill can reference its output).

### Boundaries

- Skill: `factory/skills/test-design/SKILL.md` (rewrite)
- Agent: `factory/agents/developer-agent.md` (skill list, workflow, commit-time fields)
- Template: `factory/rulebooks/templates/story.md` (field documentation)

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                                                           | Tier     | Size | Basis                                                                                                     |
| ------- | ---------------------------------------------------------------------------------------------------- | -------- | ---- | --------------------------------------------------------------------------------------------------------- |
| ST-0228 | Refactor `test-design` skill as implementation-time procedure that reads code and authors test files | standard | L    | Substantial rewrite of skill procedure (8-step implementation procedure, new inputs/outputs), high effort |
| ST-0229 | Integrate two-pass TDD into developer agent and record test traceability in story files and template | standard | M    | Developer agent workflow change (skill list, conditional invocation, commit-time fields) + template edit  |

## EPIC C: Review, Enforcement, and Convention

### Why this EPIC exists

The probe (EPIC A) and the narrowed test-design skill (EPIC B) create test artifacts — ownership tables, test files, traceability fields — but no one checks whether those artifacts are correct, complete, or consistent. Without downstream enforcement, a developer who skips the test-design pass or omits the `tests:` field creates an invisible gap. This EPIC closes the loop: QA cross-references tests against contracts, the reconciliation agent audits traceability, the `test-design-verify` gate enforces the new fields mechanically, and the `testing-strategy.md` convention documents the two-pass model so the rationale survives beyond this feature's implementation.

### Actor Goals

- The QA agent's Fagan inspection (a structured code review technique that examines artifacts against defined criteria) cross-references the test suite against traced contracts and checks the `test-design-pass` field, flagging non-`.feature` stories where the field is absent or where gaps remain despite a `done` status
- The reconciliation agent (the post-QA agent that brings documentation back in line with code-as-built) verifies that every story's `tests:` field matches its actual test files, backfills missing entries, and files `RECON` findings for contracts with ownership but no test coverage
- The `test-design-verify` gate (a deterministic script that runs before story completion) validates `tests:` and `test-design-pass` for new-model stories, and continues to validate `#### Failure scenarios` / `#### Prior Tests` for old-model stories, distinguishing the two by the presence of the `test-design-pass` field
- The `testing-strategy.md` convention documents the two-pass test authoring model — TDD contract tests first, design-driven integration tests second — so that the rationale is available to agents and humans independently of the proposal

### Demo

1. A developer agent completes a non-`.feature` story with `test-design-pass: done` and `tests: [tests/test_widget.py]`.
2. The QA agent runs Fagan inspection and cross-references `tests/test_widget.py` against the story's traced contracts — all contracts have corresponding tests. No finding.
3. A second story ships with `test-design-pass` absent (the developer skipped the step). The QA agent flags this as a finding: "non-feature-governed story missing test-design-pass field."
4. The reconciliation agent runs post-QA. It reads each story's `tests:` field and confirms that the listed test files exist on disk. One story lists `tests/test_stale.py`, which was renamed — the agent backfills the correct path and files a `RECON` finding noting the correction.
5. The reconciliation agent finds a contract with an ownership assignment in `epics.md` but no corresponding test coverage in the owning story — it files a `RECON` finding.
6. The `test-design-verify` gate runs against a new-model story. It checks that `tests:` is present and lists at least one module per owned contract, and that `test-design-pass` is `done` or `skipped-feature-governed`. Both pass — gate green.
7. The gate runs against an old-model story with `#### Failure scenarios`. It uses its existing validation logic — no regression.
8. A developer reads `testing-strategy.md` and finds the new "Two-pass test authoring" section explaining the model, when each pass runs, and why.

### Scope

**In:**

- QA agent Fagan criteria at `factory/agents/qa-agent.md` — add review criteria for `test-design-pass` field validation, contract-to-test cross-referencing, and testability-flag follow-up
- Reconciliation agent test traceability audit at `factory/agents/reconciliation-agent.md` — new audit step verifying `tests:` fields against actual test files, backfilling missing entries, and filing `RECON` findings for unresolved ownership-without-coverage gaps
- `test-design-verify` gate adaptation at `factory/scripts/test-design-verify` — dual-model validation: new-model stories (identified by `test-design-pass` presence) checked for `tests:` and `test-design-pass`; old-model stories checked for `#### Failure scenarios` / `#### Prior Tests` per existing logic; backward compatibility for pre-existing old-model stories (completion criterion 12)
- `testing-strategy.md` convention at `factory/rulebooks/conventions/testing-strategy.md` — new section documenting the two-pass test authoring model (pass 1: TDD from acceptance criteria, pass 2: test-design for integration gaps), when each runs, and why

**Out:**

- Changes to `backlog-lint` validation rules (explicitly deferred per proposal)
- Retroactive testability probes for backlogs planned before this change
- Migration of existing `#### Failure scenarios` sections (backward-compatible as-is)

### Dependencies

EPIC B (QA and reconciliation audit the `tests:` and `test-design-pass` fields the developer agent writes; the gate validates those same fields; the convention documents the model those fields encode).

### Boundaries

- Agent: `factory/agents/qa-agent.md` (Fagan criteria expansion)
- Agent: `factory/agents/reconciliation-agent.md` (new audit step)
- Script: `factory/scripts/test-design-verify` (dual-model validation)
- Convention: `factory/rulebooks/conventions/testing-strategy.md` (two-pass model section)

### Size

4 stories.

### Building-Block Inventory

| Story   | Capability                                                                                                 | Tier     | Size | Basis                                                                                                        |
| ------- | ---------------------------------------------------------------------------------------------------------- | -------- | ---- | ------------------------------------------------------------------------------------------------------------ |
| ST-0230 | Expand QA agent Fagan inspection with `test-design-pass` validation and contract-to-test cross-referencing | economy  | S    | Adding review criteria bullet points to an existing agent definition, low complexity                         |
| ST-0231 | Extend reconciliation agent with test traceability audit step — verify, backfill, and file RECON findings  | economy  | M    | New audit step in existing agent, moderately complex (file existence checks, ownership resolution, findings) |
| ST-0232 | Adapt `test-design-verify` gate for dual-model validation — new-model fields and old-model backward compat | standard | M    | Python script modification (two validation paths, field detection heuristic), medium complexity              |
| ST-0233 | Document the two-pass test authoring model in `testing-strategy.md` convention                             | economy  | S    | Convention document section addition, low complexity, but must be precise for agent consumption              |
