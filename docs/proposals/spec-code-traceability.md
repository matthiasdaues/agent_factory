# Proto-Proposal: Spec-Code Traceability

Status: **collecting ideas**

## Problem

After implementation, specification documents (.feature files, scope-map) carry
no machine-verifiable link to the code that implements them. References rot
silently — renamed functions, moved files, deleted modules — and nobody notices
until a reconciliation run.

## Ideas

### Annotation format

- Current format: `# impl: path/to/file.py:Class.method` as Gherkin comments
  under each Rule's `# scope:` line
- Tag prefixes: `impl:`, `route:`, `test:`, `model:` — one per traceability
  concern
- Compound rules get suffixed tags: `impl-create:`, `impl-activate:`
- No line numbers — they deprecate with every edit or formatting run
- File path + function/class name is the right granularity: coarse enough to
  survive refactoring, fine enough to be useful

### Mechanical verification (spec-link-checker)

- Split annotation on `:` → file path + dotted symbol
- Check file exists relative to source root
- `ast.parse` the file, walk AST for class/function definition
- Broken ref → finding with location in the .feature file
- Catches renames, deletions, moves — the exact rot line numbers had, at a
  checkable grain

### Where the checker runs

- **Reconciliation skill step** — runs at review time, produces findings in the
  reconciliation report
- **Pre-commit hook** — runs on every commit touching annotated files (.feature,
  scope-map.md), blocks commit on broken refs
- **Both** — hook for fast feedback, reconciliation for completeness

### Coverage estimation from annotations

- **Spec-rule coverage ratio**: count Rules with `# test:` vs. total Rules →
  percentage of spec rules with at least one verified test
- **Scenario-level gap detection**: a Rule may have a `# test:` but not cover
  all its Scenarios — visible gap
- **Layer coverage matrix**: presence of `impl`, `route`, `test` per rule shows
  which layers are covered; missing columns after status flips to `implemented`
  is a red flag
- Orthogonal to `pytest --cov` — this is spec-to-test traceability, not line
  coverage

### Making references navigable

- **Markdown files** (scope-map, reconciliation reports): real relative links to
  source files, clickable on GitHub and in IDEs
- **Gherkin files**: plain text only (comments aren't rendered as links) — the
  linter provides the navigation instead
- Link verbosity in table cells is a trade-off — short display text with a link
  target may be acceptable

### Autonomous unit test generation by dev agent

- Cluster-A failure scenarios are senior-written and mandatory — the dev agent
  implements exactly those tests
- Below that: the dev agent autonomously identifies unit tests that bolster the
  bottom of the testing trophy / pyramid
- These are low-level, fast, deterministic tests covering pure logic, edge
  cases, and internal invariants that the failure scenarios don't reach
- The agent decides scope by inspecting the code it just wrote — no human
  enumeration needed for this layer
- Budget constraint still applies: distinct failure modes, not coverage count
- Traceability tie-in: autonomously generated tests get `# test:` annotations
  back into the .feature or scope-map just like prescribed ones
- Clear separation: prescribed tests (from failure scenarios) vs. autonomous
  tests (agent-chosen) — both traceable, different authority

### Where the rules live

- Annotation format and "no line numbers" rule must live in a factory skill or
  agent definition, not just Claude Code memory
- All CLIs (Claude Code, GitHub Copilot CLI, Pi, Codex) need access
- `reconcile-spec` skill is the natural home — it already owns the
  reconciliation procedure
- The annotation step becomes part of the reconciliation output contract

## Open questions

- Should the checker be a standalone script, a pytest plugin, or inline in the
  reconciliation skill?
- Should broken-ref findings block a PR, or just warn?
- What source root convention for resolving paths? (currently relative to
  `packages/server/backend/src/gigacron_server/`)
- Should the scope-map use Markdown links or stay plain text for consistency
  with .feature?
