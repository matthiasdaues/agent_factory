# Finding Classification: Implementation Notebook

This notebook records each step that the orchestrator takes for the
finding-classification feature, from planning to the merge-ready feature
branch. The stakeholder merges the feature branch into `dev`.

The proposal is `docs/proposals/finding-classification.md`. The playbook is
`packages/factory/playbooks/feature-addition.md`.

## Standing instructions

- The stakeholder asked on 2026-11-07 to continue the playbook all the way
  and to be called when the feature branch is ready to merge into `dev`.
- Every reviewer applies the finding-classification rating rules already.
  Only a `defect` or `risk` at `critical` or `major` blocks.
- Every ST, SPEC, ATAM, ADR, IMPL, FAGAN, SEC, BUG, RECON, and T number comes
  from `next-id`.
- An agent's "decision for you" is checked against the spec first. Only what
  the model leaves open goes to the stakeholder.

## Steps before this notebook

| Step              | Result                                                                                            | Commits                |
| ----------------- | ------------------------------------------------------------------------------------------------- | ---------------------- |
| 0.2 Accept        | Proposal accepted                                                                                 | `74e036f1`             |
| 1.1 Specification | Feature file, gaps report, domain model, QA strategy                                              | `db3bd3aa`…`5d597aeb`  |
| 1.2 Spec review   | Three passes. SPEC-0071 to SPEC-0084 fixed. DEC-55 to DEC-59 decided by the stakeholder           | `2b1a540f`…`749a9278`  |
| 1.3 and 1.4       | Clean. `module-graph-check` reports `architecture_change=true`                                    | none                   |
| Spec alignment    | One register file per minor finding, guard in every CLI, `node:test` suite (DEC-60 to DEC-63)     | `54c325d3`, `4f626ca6` |
| 2.1 Architecture  | ADR-0034 to ADR-0036, DSL, arc42                                                                  | `439d86fb`             |
| 2.2 ATAM review   | Three passes. ATAM-0018 and ATAM-0019 fixed. ATAM-0020 stays a minor register entry. DEC-64 added | `710961cb`…`c15c918d`  |
| QA strategy       | 111 contract-owner rows. `docs/testing.yaml` declares the `typescript` suite                      | `a6635e62`, `d79d0be6` |

## Log

### 2026-11-07, Step 3.1: planning started

The planning agent runs the `create-backlog` sequence for finding-classification
on `dev`. Its brief asks for actor-outcome stories, one owner per QA row, and
stories for the cross-feature items: the `--plan-seed` change, the guard-only
OpenCode plugin, and `docs/factory-settings.yaml`.

### 2026-11-07, Step 3.1 to Step 3.3: backlog planned

The planning agent wrote 5 EPICs and 21 stories, ST-0386 to ST-0406, in
`backlog/epics-finding-classification.md`. Every one of the 111 QA rows has one
owning story, and every Completion Criterion is covered. `backlog-lint` reports
0 errors and 12 warnings, all in older stories. The reforecast estimate is 1.8M
to 3.1M tokens with `confidence: medium`.

Waves: W1 ST-0386, ST-0397, ST-0400, ST-0404. W2 ST-0387, ST-0389, ST-0390,
ST-0401, ST-0402. W3 ST-0388, ST-0391, ST-0398, ST-0403. W4 ST-0392, ST-0393,
ST-0399. W5 ST-0394, then ST-0395, then ST-0396. W6 ST-0405. W7 ST-0406.

### 2026-11-07, Step 3.4: backlog approved under the standing instruction

The open questions of the stories were settled by the model and the planning
agent's recommendations. Each answer is in the story's section "Decisions of
2026-11-07".

- ST-0405: release candidates count as releases.
- ST-0406: a migrated finding that comes out `note` keeps its file with
  `status: resolved`.
- ST-0394: the settings parser accepts the flow and the block list form.
- ST-0403: `init-factory --cli opencode` writes only the plugin link.
- ST-0396: the guardrail may extend its bypass rule to `git commit -n`, because
  QA row FC-12-IT-03 requires the denial.
- Lint failures on old findings before ST-0406 are reported, not fixed.

### 2026-11-07, Step 4.1: mode

No project file sets the implementation mode. The stakeholder asked to drive
the feature to a merge-ready branch without them, so the mode is automated:
`dispatch` owns the feature branch `feature/finding-classification`, the story
worktrees under `.current-work/`, and the ledger. The orchestrator session acts
as the dispatcher and starts one developer agent per story.
