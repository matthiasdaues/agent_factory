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

### 2026-11-07, Wave 1: dispatch

`dispatch init --base dev --feature-branch feature/finding-classification`
recorded 21 stories. `dispatch plan` set the seven waves of the backlog.
`model.conf` has no Claude Code rows, so the tiers map onto the Agent tool's
aliases: economy to haiku, standard to sonnet, strong to opus. Wave 1 started
ST-0386, ST-0397, ST-0400 (opus) and ST-0404 (sonnet) from base `2e4cd6fb`.

The pre-commit `run-tests` hook failed on every story branch, because
`tests/factory/test_structure_gates.py` pinned arc42 chapter 5 at 57
components, and the architecture commit `439d86fb` raised it to 68 on purpose.
`dev` was red there since `439d86fb`; the docs commits never ran the suite.
Every wave-1 story makes the identical two-line edit to 68, so the merges stay
clean. No hook was skipped.

`premerge-check` blocked the first merge of ST-0404, because the test file
lies outside the story's `touches`. The fix moved to the invocation branch as
`7cfda707`, and `refresh-story` brings it into each story branch, so it drops
out of the story diffs.

- ST-0404 merged (`a68a6dbc`, merge `f569be63`). Post-merge suite: 3207 passed.
  Spec feedback: three open rows for the domain-modeling agent (BR-099, the
  `--plan-seed` contract, `ID_IN_USE`).
- ST-0397 merged (`95abbea9`). Post-merge suite: 3257 passed. The stop lives
  in the source copy; the installed `dispatch` that runs this wave is
  unchanged until `update-factory`. Spec feedback: two rows for the
  domain-modeling agent.
- ST-0386 merged (`82f2b0b0`). Post-merge suite: 3275 passed. Spec feedback:
  one row for the test-strategy agent (FC-QG22). Follow-ups for later
  stories: BUG-0116 contradicts BR-081 and goes through the migration
  (ST-0406); the minor examples link the old `.jsonl` registers, which
  ST-0406 must re-point; ST-0390 leaves the six runtime examples BUG-0035,
  BUG-0054, BUG-0058, BUG-0063, BUG-0073, and BUG-0081 out of its agreement
  set.
- ST-0400 merged (`dcd8da53`). Post-merge suite: 3305 passed. Spec feedback:
  two rows for the domain-modeling agent. The manual check in a real Claude
  Code session (FC-QG23) is still to do.

Drift rows: the domain-modeling agent fixes the seven spec rows, and the spec
review agent reviews them. The test-strategy agent fixes the one QA row,
which closes at `fixed`.

Drift results. The domain-modeling agent fixed six of the seven spec rows.
The seventh, the ST-0400 Blind spot row, showed a code defect: the guard does
not follow `cd`, so `cd docs && sed -i …waived… findings/X.md` passes. That
became BUG-0120 (`code`, `major`), owned by the developer agent, and ST-0401
fixes it, because it touches the guard and its tests. The new first-sentence
rule for the Why line of a critical finding needs the three critical
calibration examples of the rulebook reordered; ST-0387 does it and gains the
rulebook in its `touches`. The test-strategy agent closed the ST-0386 row and
FC-QG22. The spec review agent reviews the six fixed spec rows.
The spec review agent confirmed all six fixed spec rows and filed no BUG.

### 2026-11-07, Wave 1: closed

All four stories merged. The `cd` row of ST-0400 stays `open` until ST-0401
fixes BUG-0120.

`close-wave 1` refused while the `cd` row of ST-0400 was `open`. The contract
names `rejected` for a row whose code breaks an accepted requirement, with a
`BUG` that carries the fix, so the row became `rejected` with a reference to
BUG-0120 (`bcd19208`). Then `close-wave 1` recorded the wave. No QA finding
was open.

### 2026-11-07, Wave 2: dispatch

`prepare-wave 2` prepared all five stories in parallel, but two pairs touch
the same files: ST-0401 and ST-0402 (`init-factory`, `remove-factory`, the
installer tests), and ST-0387 and ST-0389 (`INDEX.yaml`,
`test_finding_classification_text.py`). The orchestrator runs them as serial
chains: ST-0387 (sonnet), ST-0390 (sonnet), and ST-0401 (opus) first, then
ST-0389 after ST-0387 and ST-0402 after ST-0401, each refreshed before it
starts. ST-0401 gained `docs/findings/BUG-0120.md` in its `touches`
(`62c41dfe`).

- ST-0390 merged (`b8498217`) with its report "passed: no". The new rulebook
  agreed on 18 of 20 findings and reached the target of 16, but the old rules
  agreed on 20 of 20 by rating nearly everything blocking, so the condition
  of DEC-23 failed. The runs split on SPEC-0012 and BUG-0006. On 2026-11-08
  the stakeholder chose to sharpen the rulebook and re-measure on a fresh set.
  The planning agent writes that story; it runs as a short second dispatch
  after the 21 planned stories, because `dispatch plan` adds no story to a
  running ledger.
- ST-0401 merged (`2e5278fc`): Codex, Copilot CLI, the patch parser, and the
  BUG-0120 fix (`cd` is followed). Suite: 3327 passed. One drift row for the
  domain-modeling agent (payload keys per CLI). Manual check in real Codex
  and Copilot CLI sessions still open (FC-QG23); Copilot CLI may need a JSON
  deny decision instead of exit 2.
- ST-0387 merged (`2926a1af`): 26 files, inside its scaled limit of 42. It
  also rewrote three old filing rules and their assertions in
  `test_core_artifact_ownership_text.py`, which encoded the rules this
  feature replaces; the file joined its `touches` (`87219aae`). Suite: 3387
  passed. Two drift rows for the domain-modeling agent.
- Chain followers started: ST-0389 (haiku) after ST-0387, ST-0402 (sonnet)
  after ST-0401.
- ST-0407 planned (`d59905b2`): sharpen the `major`/`minor` line of the
  document and runtime classes, then re-measure on 20 fresh findings. No
  fresh security finding is eligible, so on 2026-11-08 the stakeholder chose
  to keep 20 findings and give the three security slots to document and
  runtime (8, 5, 5, 2, 0). It runs as wave 8.
- ST-0402 merged (`44fd3005`): the Pi extension, fail closed. TypeScript
  suite 37 of 37. Suite: 3390 passed. No drift.
- ST-0389 merged (`1f9e70ba`): the `Consequence` column in the triage table.
  Suite: 3391 passed. One drift row for the requirements agent (scope map);
  its reviewer is the stakeholder, so it waits at `fixed` for the merge
  report.

Wave-2 drift: the domain-modeling agent fixes three rows (ST-0387, ST-0401),
the requirements agent one row (ST-0389).
The spec review agent confirmed the three domain rows and filed no BUG.

### 2026-11-08, Wave 2: closed

All five stories merged. The scope-map row of ST-0389 waits at `fixed` for
the stakeholder.

The stakeholder confirmed the scope-map row of ST-0389 on 2026-11-08.
