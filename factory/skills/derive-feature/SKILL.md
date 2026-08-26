---
name: derive-feature
description: Derive a Gherkin .feature file from a proposal using Cockburn reasoning as internal process. Outputs a Rule-per-actor-goal .feature file with @-references to existing code and a gaps report.
category: requirements
disable-model-invocation: false
---

# Derive Feature

Derive a consolidated Gherkin `.feature` file from a proposal using the
Cockburn reasoning sequence as an **internal working discipline** — not
document production. Outputs a single-file specification that coders and QA
agents can read in one pass.

Supersedes `derive-spec` as the primary specification step for features.
The Cockburn chain (actors, goals, scenarios) remains the reasoning engine;
the intermediate documents (actor-goal list, UC-XX files) are not produced.

## Inputs

- **Invocation argument:** path to the proposal file (e.g.,
  `docs/proposals/agentic-quality-gates.md`)
- **From proposal frontmatter:** `impact.boundaries` — list of files and
  modules the feature touches
- **From `impact.boundaries`:** scanned modules in `src/` (or equivalent)

## Outputs

| File                               | Contents                                                                    |
| ---------------------------------- | --------------------------------------------------------------------------- |
| `docs/spec/<feature-name>.feature` | Gherkin feature with Rule-per-actor-goal structure and @-references         |
| `docs/spec/<feature-name>-gaps.md` | Completeness report: actor-goal matrix, missing coverage, ambiguous wording |

## Step 1 — Validate Input

The skill receives the proposal file path as its invocation argument.

1. Verify the proposal file exists and is readable. Fail with diagnostic
   if missing or unreadable.
2. Parse the YAML frontmatter. Fail with diagnostic if `impact.boundaries`
   is absent.

```
FAIL: proposal not found at docs/proposals/my-feature.md
FAIL: proposal lacks required field: impact.boundaries in frontmatter
```

## Step 2 — Scan Existing Code

Read `impact.boundaries` from the proposal frontmatter. For each boundary
path:

1. Resolve it against the project root.
2. Scan `src/` (or equivalent source directory) for modules, classes, and
   functions matching those boundaries.
3. Build a symbol index: `{ path → [class_or_function_names] }`.

This step is read-only. It discovers what already exists so @-references
can point at it. Scenarios without an @-reference are new behavior.

If `src/` does not exist, scan the project root for source files by
extension (`.py`, `.ts`, `.js`, `.go`, `.java`, etc.).

## Step 3 — Derive Actor-Goal Pairs (Internal)

Use the Cockburn reasoning sequence as a working discipline held in context:

1. **Identify actors** — enumerate who interacts with the feature (users,
   systems, external services). Apply the goal-level test: does the actor
   go home happy if this goal is achieved? If yes, it's a **User Goal**.
   If not, it's a **Subfunction** — include only when reused across
   multiple use cases.
2. **Identify goals per actor** — what does each actor want to accomplish?
3. **Build the actor-goal matrix** — one row per actor-goal pair.

Hold the matrix in working context. Do not commit it as a separate
artifact — it appears in the gaps report as completeness evidence.

## Step 4 — Derive Rules from Actor-Goal Pairs

For each actor-goal pair in the matrix:

1. **Create one Rule** in the `.feature` file.
2. **Rule name** states the goal: `Rule: <actor wants X>`.
3. **Actor comment** identifies who: `# actor: <who>`.
4. **@-reference** if the Rule extends existing code: add a `@`-reference
   to the implementing module or class from the symbol index.

```
Rule: User authenticates via SSO
  # actor: End user
  # @src/auth/sso.py::SSOHandler
```

## Step 5 — Enumerate Scenarios Under Each Rule

For each Rule, decompose the goal into Given/When/Then scenarios:

1. **Cockburn workflow-to-edge-case progression:**
   - Main success path first (happy day)
   - Extensions and variations
   - Failure modes and error handling
2. **@-reference each Scenario** that exercises existing functions:
   append `# @<path>::<Symbol>` as a Gherkin comment.
3. **Scenarios for new behavior** carry **no @-reference** — absence
   means "to be implemented."

```
Scenario: Valid SSO token presented
  # @src/auth/sso.py::SSOHandler.authenticate
  Given the user holds a valid SSO token
  When the user authenticates
  Then the session is established

Scenario: Expired SSO token presented
  # @src/auth/sso.py::SSOHandler.authenticate
  When the user authenticates with an expired token
  Then authentication is rejected
```

## Step 6 — Cross-Check Completeness

Verify completeness against the actor-goal matrix:

| Check                                       | Failure → Gaps Report Entry  |
| ------------------------------------------- | ---------------------------- |
| Every actor-goal pair has at least one Rule | Actor-goal pair without Rule |
| Every Rule has at least one Scenario        | Rule without Scenario        |

Record failures in the gaps report (Step 8).

## Step 7 — Detect Ambiguous Wording

While deriving Rules and Scenarios, flag any Given/When/Then step that
uses ambiguous language:

- Vague quantifiers without bounds ("some", "several", "many")
- Conditional without explicit condition ("if valid", but valid what?)
- Subject missing or unclear ("then it works", but what is "it"?)

Flag in the gaps report. Do not silently fix — the author decides.

## Step 8 — Write Outputs

### Output 1: Feature File

Write `docs/spec/<feature-name>.feature`:

```gherkin
Feature: <feature-name>

  Rule: <actor-goal statement>
    # actor: <who>
    # @<existing-module-path>::<ClassOrFunction>

    Scenario: <main success path>
      Given <precondition>
      When <action>
      Then <observable outcome>
      # @<existing-implementation>::<method>

    Scenario: <extension or variant>
      Given <variant precondition>
      When <action>
      Then <variant outcome>

    Scenario: <failure mode>
      Given <precondition that leads to failure>
      When <action>
      Then <error or rejection>
```

**Format rules:**

- Rule names are sentence-case, statement form ("User authenticates via SSO")
- Scenario names are sentence-case, description form ("Valid SSO token presented")
- Each Given/When/Then step is a single declarative sentence
- @-references appear as Gherkin comments (`#`) directly below the construct they annotate
- Blank line between Rules
- No Gherkin tags (`@`) unless required by the test framework

### Output 2: Gaps Report

Write `docs/spec/<feature-name>-gaps.md`:

```markdown
# Gaps Report: <feature-name>

Generated: YYYY-MM-DD
Source: <proposal file path>

## Actor-Goal Matrix

| Actor | Goal | Rule | Status |
| ----- | ---- | ---- | ------ |
| End user | Authenticate via SSO | Rule: User authenticates via SSO | specified |
| Admin | Configure SSO provider | — | missing |

## Missing Rules

(List actor-goal pairs without a corresponding Rule)

## Rules Without Scenarios

(List Rules that have no Scenario)

## Ambiguous Wording

| Location | Step Text | Issue | Suggested Fix |
| -------- | --------- | ----- | ------------- |
| Scenario: X | "Given some valid tokens" | "some" is vague | "Given the user holds 3 valid tokens" |
```

## Input Contract Summary

| Field               | Required | Source               |
| ------------------- | -------- | -------------------- |
| `impact.boundaries` | Yes      | Proposal frontmatter |

## Failure Diagnostics

| Diagnostic            | Meaning                                     |
| --------------------- | ------------------------------------------- |
| `PROPOSAL_NOT_FOUND`  | Path does not exist                         |
| `PROPOSAL_UNREADABLE` | Path exists but cannot be read              |
| `NO_BOUNDARIES`       | `impact.boundaries` absent from frontmatter |

## References

- [cross-reference-format.md](../../rulebooks/conventions/cross-reference-format.md) — @-reference notation
- [testing-strategy.md](../../rulebooks/conventions/testing-strategy.md) — acceptance test layer

## Scope Map Integration

After the `.feature` file is written, update `docs/spec/scope-map.md` if it
exists. For each Rule in the new feature:

1. If the Rule is not in the scope map, add it with status `specified`
   and a link to the new `.feature` file.
2. If the Rule is already in the scope map with status `deferred`, update
   it to `specified` and link to the new `.feature` file.
3. Leave `implemented` entries untouched.

If `docs/spec/scope-map.md` does not exist, create it from scratch with
Rules derived from this feature as initial `specified` entries.

## Slice Lifecycle

Each invocation of this skill produces a per-slice `.feature` file containing
only the Rules being implemented in that slice. The `.feature` file is live
during the slice lifecycle (Phases 1–5) and is read by the developer-agent,
qa-agent, and reconciliation-agent.

**Status transitions in the scope map:**

| Transition                  | When                                   |
| --------------------------- | -------------------------------------- |
| `deferred` → `specified`    | This skill writes the `.feature` file  |
| `specified` → `implemented` | Feature branch merges to dev (Phase 5) |

After merge, the `.feature` file may be deleted or moved to `docs/~archive/`
at human discretion. The scope map is the persistent record that survives
across slices.

**@-reference lifecycle across phases:**

| Phase                | Who writes @-refs      | What is annotated                                |
| -------------------- | ---------------------- | ------------------------------------------------ |
| Phase 1 (this skill) | `derive-feature`       | Scenarios that touch existing code               |
| Phase 4              | `developer-agent`      | Step definitions reference @-annotated code      |
| Phase 5              | `reconciliation-agent` | Fills missing @-refs for newly implemented Rules |

After reconciliation, every Rule in the current slice's `.feature` file must
have at least one @-reference. A Rule without one is a finding. Rules in the
scope map that remain `deferred` (their slice has not been worked on yet)
carry no @-reference and no `.feature` file — that is expected, not a gap.
