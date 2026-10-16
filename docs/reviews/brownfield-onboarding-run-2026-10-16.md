---
status: draft
---

# Brownfield onboarding run, 2026-10-16

An onboarding run of the factory on a real brownfield project filed five
findings, BUG-0092 to BUG-0096. They show that the brownfield playbook cannot
run as written. An analysis on `dev` at `4c001778` confirmed all five. This
run fixes four of them. BUG-0092 moves to the following run, which changes
where briefs live, because both changes touch the dispatch contract.

## Decisions

The stakeholder decided on 2026-10-16:

1. **Order.** The brownfield playbook builds the scope map before the
   architecture DSL. `reverse-map` reads nothing the DSL step writes, so the
   order can change. The archive step stays first.
2. **Required inputs.** Agent definitions get an `any_of` form for required
   inputs. `architecture-agent` then needs a `.feature` file or the scope
   map, and `requirements-agent` an accepted proposal or the scope map.
   Greenfield keeps its order.
3. **Draft marker.** An unattended `reverse-map` writes the scope map with a
   frontmatter field that marks it as a draft. The Stage 1 exit refuses a
   draft scope map.
4. **Worktrees.** Linking the factory into new worktrees and resolving the
   main checkout at use. This is story S6 of the analysis and moves to the
   brief-storage run.

## Stories

| Story   | Outcome                                                                                        | Findings | Runs after |
| ------- | ---------------------------------------------------------------------------------------------- | -------- | ---------- |
| ST-0313 | Brownfield Stage 1 builds the scope map first, and `run-step` can reach the architecture agent | BUG-0093 |            |
| ST-0314 | `reverse-map` runs without a stakeholder and marks its scope map as a draft                    | BUG-0096 | ST-0313    |
| ST-0315 | `derive-feature` writes the brownfield feature file from the scope map                         | BUG-0094 | ST-0313    |
| ST-0316 | `scope-lint` finds the workstream IDs in a linked worktree                                     | BUG-0095 |            |
| ST-0317 | `.feature` and `.dsl` files declare their scope with one comment form                          | BUG-0095 | ST-0316    |

ST-0313, ST-0314 and ST-0315 all change `brownfield-onboarding.md`, so they
run one after another. ST-0316 and ST-0317 run beside them.

## Not in this run

- BUG-0092 (worktrees lack the factory): the brief-storage run.
- Side findings of the analysis: `scope-lint` runs from no hook; no template
  tells an author to write a scope declaration; `architecture-agent` demands
  Component views in the first pass, which the playbook defers; the playbook
  names two `CONTEXT.md` locations; `dispatch-wave.ts` puts worktrees under
  `.current-work/worktrees/`. They are filed as findings after the run.

The analysis report lies in
`.current-work/feature/brownfield-onboarding/analysis-report.md`, outside git.
