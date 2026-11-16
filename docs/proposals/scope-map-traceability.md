---
scope: global
schema_version: 2
title: Scope Map Traceability
status: draft
owner: agent-factory
created: 2026-11-09
updated: 2026-11-09
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - docs/spec/scope-map.md
    - packages/factory/config/pre-commit-config.yaml
    - packages/factory/skills/derive-feature/SKILL.md
    - packages/factory/skills/reverse-map/SKILL.md
    - packages/factory/skills/testability-probe/SKILL.md
    - packages/factory/agents/requirements-agent.md

governance:
  assurance: elevated
  risk_domains:
    - data_integrity
    - compatibility

estimate:
  as_of: 2026-11-09
  basis: judgment
  confidence: low
  human_review_hours:
    min: 0.5
    max: 1.5
  normalized_tokens:
    min: 5000
    max: 12000
  estimated_consumption:
    min: 75000
    max: 180000
    overhead_multiplier: 15
    playbook: feature-addition
---

# Feature Request: Scope Map Traceability

## Primer

Agent Factory is a set of AI agents and scripts that a software project installs to plan, build, and review work. The project writes down what its product must do as Rules. One Rule says: "Remove-factory leaves project test infrastructure intact." An engineer who changes this Rule needs to find the code behind it. An AI agent that works out how to test a Rule needs the same code.

Today that link lives in two places, and they disagree. One place is a feature file, which describes behaviour Rule by Rule. A comment below each Rule, called an "@ reference", names the code. The other place is the scope map, one table with a row for each Rule. Its Sources column says where the Rule comes from, usually a feature file. Its Feature Link column holds the link to the code, written by hand.

Take the Rule above. Its scope map row names the correct path of the script that removes the factory from a project. Its feature file names a path that does not exist. Over half of the scope map's links point into the installed copy of the factory. Git ignores that copy, so a clean checkout does not have it. No check catches this, so the cost falls on whoever follows a wrong link.

The idea is that each link between a Rule and its code has one home, and every commit checks it. When a row's Sources column links to a feature file, the row's Feature Link cell stays empty. A reader follows Sources and reads the comments under the Rule. For our Rule, the feature file gets the correct path and the scope map cell becomes empty. The 17 rows without a feature file keep their hand-written links, and the check covers them too.

A new script does the check, and a pre-commit hook runs it. The script fails a commit in three cases. A linked path is not tracked by git. A link points into the installed copy. A row with a feature file has a filled cell. A script could generate the column from the feature files. The proposal leaves the cell empty, so nobody has to maintain a generator.

The hook runs on every commit, because a commit that deletes a source file can break a link. The hook blocks commits from its first release, also in other projects that install the factory. After the update, a project with a broken link or filled cell fails its next commit. Someone then repairs it or sets the skip option in the changelog.

A one-time repair comes first. The requirements agent, which writes the scope map, reviews the links that only the scope map holds. It places each correct link under its Rule. The repair then empties the cells and, as its last step, enables the hook. A finished feature file moves to an archive folder, so its links stay reachable through Sources. The proposal has no open questions.

## Summary

The feature answers one question that the project cannot answer reliably today: which code implements this Rule? Each link between a Rule and its code gets one home, the feature file, and the new script `reference-check` fails a commit when a link does not resolve. The first release repairs the existing links once. It leaves out generated columns, symbol checks, and graph tooling, as [Scope](#scope) lists.

## Motivation

An engineer who changes a Rule needs to find its code. An agent that runs the `testability-probe` skill needs the same link. Today the link lives in two places, and they disagree.

An `@` reference is a comment such as `# @packages/factory/scripts/next-id::plan_seed` below a Rule or Scenario in a feature file. It names the code that implements that behaviour. The Feature Link column of the [scope map](../spec/scope-map.md) holds the same kind of link, written by hand. The two copies have drifted:

- Counted as whole files, 63 appear in both places, 30 only in feature files, and 16 only in the scope map.
- Seven of the 217 `@` references in the feature files do not resolve to a tracked path.
- Two scope-map rows with status `implemented` point at the `mutation-analysis` skill, which does not exist.
- 76 of 138 scope-map references use `.agent-factory/factory/`. That path is a gitignored copy, so a clean checkout does not have it.

No check catches any of this. No script reads Feature Link, so nothing breaks today. The cost falls on the person or agent who follows a wrong link.

## Core Principles

- The scope map stays organized per Rule. It is not an inventory of every file (DEC-01).
- A link between a Rule and its code has one home. For a Rule in a feature file, that home is the feature file (DEC-13).
- A check that runs on every commit is worth more than a second copy that someone has to keep current.

## Design

### One home for each link

A scope-map row whose Sources column links to a feature file under `docs/spec/features/` leaves Feature Link empty. To find the code, a reader follows Sources to the feature file and reads the `@` references under the Rule. Today 187 of the 204 rows link to such a file.

The other 17 rows have no feature file, so they keep their hand-written links, and the check covers those links too.

A finished feature file moves to `docs/~archive/` and is not deleted, so its references stay reachable through the Sources link.

### The check

`packages/factory/scripts/reference-check` is a read-only script of about 30 lines. It exits 1 on any error and otherwise 0. Errors use the form that `spec-lint` prints: `ERROR: <path> — <detail>`. The script exits 0 in a project that has neither a scope map nor feature files.

| Check                  | Fails when                                                                                         |
| ---------------------- | -------------------------------------------------------------------------------------------------- |
| Path exists            | A referenced path is not tracked by git, or is a directory without tracked files.                  |
| Not the installed copy | A reference starts with `.agent-factory/`.                                                         |
| One home               | A row whose Sources links to a feature file under `docs/spec/features/` has a filled Feature Link. |

A reference in a feature file is a comment line that starts with `# @` or `\# @`. Three feature files use the second form today. A reference in the scope map is a code span in Feature Link that contains a `/`. The script ignores a `::Symbol` suffix and any text after the path.

The script resolves paths with `git ls-files`, so it gives the same answer in a linked worktree and in the primary checkout. It reads the git index, so a commit that deletes a referenced file fails in that commit.

### The hook

The hook `agent_factory_hook-reference-check` goes into [pre-commit-config.yaml](../../packages/factory/config/pre-commit-config.yaml) with `always_run: true`. A filter on `docs/spec/` would miss a commit that deletes or renames a referenced source file (DEC-05).

The hook is enforcing from its first release, in this repository and in consumer projects (DEC-11). After `update-factory`, a consumer project with a stale reference or a filled cell fails its next commit until someone repairs it or sets `SKIP=agent_factory_hook-reference-check`. The entry in [CHANGELOG.md](../../packages/factory/CHANGELOG.md) names that setting.

### Changes to existing artifacts

| Artifact                                                                                     | Change                                                                                                                                             |
| -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| [requirements-agent.md](../../packages/factory/agents/requirements-agent.md)                 | In brownfield, links each matched row to its feature file through Sources.                                                                         |
| [derive-feature/SKILL.md](../../packages/factory/skills/derive-feature/SKILL.md)             | In brownfield, writes the feature file link into Sources and leaves Feature Link empty (DEC-06). A finished feature file is archived, not deleted. |
| [reverse-map/SKILL.md](../../packages/factory/skills/reverse-map/SKILL.md)                   | States that Feature Link stays empty on a row that links to a feature file.                                                                        |
| [testability-probe/SKILL.md](../../packages/factory/skills/testability-probe/SKILL.md)       | Reads the `@` references under the Rule instead of Feature Link.                                                                                   |
| Scope map header                                                                             | States that Feature Link stays empty on a row that links to a feature file, and where the code links live.                                         |
| `tests/factory/test_derive_feature_brownfield.py`, `tests/factory/test_reverse_map_draft.py` | Follow the new wording of the two skills.                                                                                                          |

### Repair order

The repair runs on one feature branch, and the last step enables the hook.

1. Add to the feature files the references that only the scope map holds. Emptying the cells would otherwise lose 48 of them, across 40 distinct targets. The 48 are counted per row, so another Rule may still reference the same file. The requirements agent keeps each one that is correct and places it under its Rule.
2. Change every `.agent-factory/factory/` reference to `packages/factory/`.
3. Fix the stale references. `factory/scripts/init-factory` and `factory/scripts/remove-factory` become `packages/factory/scripts/init-factory` and `packages/factory/scripts/remove-factory`. The `mutation-analysis` skill becomes `mutation-testing`.
4. Delete the references to the removed scripts `run-tests` and `mutation-analysis`. The Rule that records their removal needs no link to a file that does not exist.
5. Retire the Rule "Orchestrator package is dormant", because `packages/orchestrator/` holds no tracked file and the Rule is false on a clean checkout (DEC-09). Remove the Rule and its one Scenario from `activity-graph-orchestration.feature`, and remove its scope-map row.
6. Empty Feature Link on every row that links to a feature file under `docs/spec/features/`.
7. Enable the hook.

## Scope

**In the first release:**

- The script `reference-check` and its hook.
- The one-time repair of the references in the scope map and the feature files.
- The changes in [Changes to existing artifacts](#changes-to-existing-artifacts).

**Explicitly deferred (do NOT plan stories for these):**

- Generating Feature Link from the feature files. Emptying the cell removes the second copy with no generator to maintain (DEC-13).
- Symbol checks. 41 of the 217 references carry a symbol, and a stale function name is cheap to notice (DEC-14).
- A check that every `implemented` Rule has a reference. The reconciliation agent already reports a Rule without one.
- A check that demands a reference for every new file. Nothing has broken for lack of one, and many files implement no Rule of their own.
- The review of the 25 test files that no story or feature file names. It does not touch the scope map, so it gets its own entry in `docs/spec/work/todo.md` (DEC-15).
- Links from individual test functions to Scenarios. Story-level links answer the question that engineers ask today (DEC-03).
- The four `@` references to tests in `core-artifact-ownership.feature`. They resolve, so they are no broken link, and they do not block this work.
- The `specified` row "LinkML entity model serves as canonical domain source", which names a feature file that lacks its Rule. Its Feature Link is empty, so the check does not depend on it.
- Stable Rule IDs. Nothing in this design matches on Rule text.
- A graph database, GraphRAG, or a third-party traceability tool. The script reads plain text, and git still shows every change for review (DEC-08).
- Renaming the Feature Link column. The name misleads, because the column holds code. A rename touches every consumer's table header and changes no behaviour.

## Open Questions

None.

## Completion Criteria

- `reference-check` exits 0 on the head of the feature branch.
- In a test repository, the script exits 1 for each of the three checks and names the offending row or reference.
- The script checks a reference written as `\# @`.
- The script exits 0 in a project that has neither a scope map nor feature files.
- The hook refuses a commit that deletes a file referenced by a feature file.
- No `@` reference and no Feature Link cell starts with `.agent-factory/`.
- Every row that links to a feature file under `docs/spec/features/` has an empty Feature Link.
- Each of the 48 references that only the scope map held sits under its Rule, or the repair commit message names it as wrong.
- The changes in [Changes to existing artifacts](#changes-to-existing-artifacts) are present.

## Guiding Rule

A link between a Rule and its code has one home, and every commit checks that it resolves.

# Appendix

## Decisions

| ID     | Date       | Kind     | Decided by  | Decision                                                                                                                                                                                                                       | Raised by                         |
| ------ | ---------- | -------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------- |
| DEC-01 | 2026-11-09 | decision | stakeholder | The scope map stays per Rule and does not list every file.                                                                                                                                                                     | traceability audit                |
| DEC-02 | 2026-11-09 | decision | stakeholder | Generate the code column from `@` references, instead of repairing the 30 missing files by hand. Withdrawn by DEC-13.                                                                                                          | traceability audit                |
| DEC-03 | 2026-11-09 | decision | stakeholder | Test links stay in story files, and no test function must trace to a Scenario.                                                                                                                                                 | reconciliation-agent rule         |
| DEC-04 | 2026-11-09 | decision | stakeholder | A row whose feature file is archived keeps its last value and becomes hand-written. Withdrawn by DEC-13.                                                                                                                       | derive-feature lifecycle          |
| DEC-05 | 2026-11-09 | decision | stakeholder | The hook runs on every commit, because deleting source code must trigger it.                                                                                                                                                   | drafting                          |
| DEC-06 | 2026-11-09 | decision | stakeholder | On a row that links to a feature file, Feature Link stays empty, and the feature file link always lives in Sources.                                                                                                            | derive-feature conflict           |
| DEC-07 | 2026-11-09 | decision | stakeholder | Keep Rule text as the key between a row and its feature file, and fail the check when an `implemented` or `specified` row loses its Rule. Withdrawn by DEC-13.                                                                 | research SRC-01 to SRC-05         |
| DEC-08 | 2026-11-09 | decision | stakeholder | Keep the source in text and derive the graph with a script. Adopt no graph database, GraphRAG, or third-party traceability tool.                                                                                               | research SRC-01 to SRC-14         |
| DEC-09 | 2026-11-09 | decision | stakeholder | Retire the Rule "Orchestrator package is dormant", because `packages/orchestrator/` holds no tracked file.                                                                                                                     | open question: orchestrator Rule  |
| DEC-10 | 2026-11-09 | decision | stakeholder | A Rule with no implementing code references the artifact that carries its result. No second marker exists. A Rule with neither is retired. Withdrawn by DEC-13.                                                                | open question: Rules without code |
| DEC-11 | 2026-11-09 | decision | stakeholder | The hook is enforcing from its first release. The stakeholder knows every user of the few installed projects.                                                                                                                  | open question: consumer rollout   |
| DEC-12 | 2026-11-09 | decision | stakeholder | The `(deleted)` marker exists only in feature files, so the scope map holds no dead links. Withdrawn by DEC-13.                                                                                                                | lector cut plan, item 20          |
| DEC-13 | 2026-11-09 | decision | stakeholder | Leave Feature Link empty on rows that link to a feature file, and check references with one script of about 30 lines. This removes the second copy with no generator, and replaces DEC-02, DEC-04, DEC-07, DEC-10, and DEC-12. | independent skeptical review      |
| DEC-14 | 2026-11-09 | decision | stakeholder | The check verifies paths only. A renamed function does not fail a commit.                                                                                                                                                      | independent skeptical review      |
| DEC-15 | 2026-11-09 | decision | stakeholder | The review of the 25 unnamed test files leaves this proposal and gets its own todo entry.                                                                                                                                      | independent skeptical review      |

## External sources

| ID     | Retrieved  | Evidence                  | Source                                                                                                                                              | Used for                                                                                   |
| ------ | ---------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| SRC-01 | 2026-11-09 | search summary            | [StrictDoc FAQ](https://strictdoc.readthedocs.io/en/latest/strictdoc_02_faq.html)                                                                   | How StrictDoc compares with Doorstop and Sphinx-Needs.                                     |
| SRC-02 | 2026-11-09 | search summary            | [StrictDoc user guide](https://strictdoc.readthedocs.io/en/latest/strictdoc_01_user_guide.html)                                                     | Two-way links to source files. Source parsing is experimental, for Python and C.           |
| SRC-03 | 2026-11-09 | search summary            | [OpenFastTrace user guide](https://github.com/itsallcode/openfasttrace/blob/main/doc/user_guide.md)                                                 | Coverage tags placed in code comments.                                                     |
| SRC-04 | 2026-11-09 | search summary            | [Eclipse Ankaios requirement tracing](https://eclipse-ankaios.github.io/ankaios/0.7/development/requirement-tracing)                                | A project that uses OpenFastTrace tags in practice.                                        |
| SRC-05 | 2026-11-09 | search summary            | [Sphinx-Needs schema validation](https://sphinx-needs.readthedocs.io/en/8.5.0/schema/index.html)                                                    | Typed requirement items validated against declared schemas.                                |
| SRC-06 | 2026-11-09 | search summary, vendor    | [SCIP announcement](https://sourcegraph.com/blog/announcing-scip)                                                                                   | SCIP as an index format for definitions and references.                                    |
| SRC-07 | 2026-11-09 | search summary            | [SCIP repository](https://github.com/scip-code/scip)                                                                                                | The indexers per programming language.                                                     |
| SRC-08 | 2026-11-09 | search summary, vendor    | [Sourcegraph context comparison](https://sourcegraph.com/resources/context-compare)                                                                 | The claim that SCIP returns every reference, not ranked matches.                           |
| SRC-09 | 2026-11-09 | search summary, preprint  | [AST-derived and LLM-extracted graphs, arXiv 2601.08773](https://arxiv.org/html/2601.08773)                                                         | Deterministic graphs compared with LLM-extracted graphs on Java repositories.              |
| SRC-10 | 2026-11-09 | search summary, secondary | [Summary of arXiv 2601.08773](https://www.emergentmind.com/papers/2601.08773)                                                                       | The LLM-built graph skipped or missed 377 files on Shopizer.                               |
| SRC-11 | 2026-11-09 | search summary            | [pytest-cov contexts](https://pytest-cov.readthedocs.io/en/latest/contexts.html)                                                                    | Per-test coverage as a measured link from a test to code. Not adopted in this release.     |
| SRC-12 | 2026-11-09 | search summary            | [coverage.py contexts](https://coverage.readthedocs.io/en/6.5.0/contexts.html)                                                                      | The SQLite data file and the "what test ran this line" query. Not adopted in this release. |
| SRC-13 | 2026-11-09 | search summary, secondary | [Microsoft GraphRAG overview](https://www.mintlify.com/microsoft/graphrag/concepts/overview)                                                        | GraphRAG builds its graph by LLM extraction.                                               |
| SRC-14 | 2026-11-09 | search summary, secondary | [GraphRAG implementation guide](https://blog.premai.io/graphrag-implementation-guide-entity-extraction-query-routing-when-it-beats-vector-rag-2026) | Indexing cost per chunk, and quality bounded by extraction.                                |

## Review findings

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
