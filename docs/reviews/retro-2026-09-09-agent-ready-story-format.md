# Session Retrospective — 2026-09-09

**Session scope**: Agent-Ready Story Format campaign — proposal draft through implementation and reconciliation on `feature/agent-ready-story-format`
**Duration**: two sessions (context compaction boundary between planning and implementation)
**Mode**: mixed (interactive proposal/review, autonomous implementation dispatch)

## Went well

- **Proposal pipeline worked end to end** — draft → open → adversarial review → finding resolution → re-review (clean) → accept → plan → commit to dev → dispatch → reconcile, all within the factory's own playbook. Evidence: 6 stories planned, dispatched, implemented, reconciled without a single blocked story.
- **User caught stale knowledge before it shipped** — I added Failure Scenarios (10a) and Prior Tests (10b) sections to the new template based on obsolete test-design behavior. The user challenged this with "The test-layer-redistribution has changed a lot about the test assignation." Reading the implemented redistribution proposal revealed both sections were removed from planning-time output. Cost of catching it early: one proposal revision. Cost if it had shipped: a template that contradicts the redistribution design.
- **Post-implementation verification against git diff** — after the implementation agent reported "all done," diffing `dev..feature/agent-ready-story-format` revealed three real issues: out-of-scope dispatch script modifications, stray markdown fences in story.md, and removed user-prompt questions. None were in the agent's report. Evidence: fixup commit `b66f0cc`.
- **Economy tier handled prose-only stories well** — all 6 stories were `tier: economy` (Haiku). Despite being prose edits requiring precise transcription from a large proposal document, Haiku completed all stories with only minor issues (stray fences, one count error). Token cost: 73K subagent tokens for the full dispatch.
- **Reconciliation found real gaps** — RECON-0002 ("Three" should be "Two" quality gates) and RECON-0003 (missing `risk_level` test) were genuine issues that slipped past implementation and post-implementation review. Evidence: fixup commit `9ded815`.
- **The `touches` hygiene rule emerged from a concrete example** — the user pasted a real wildly-redundant `touches` list, which produced a clear, practical guideline: most specific directories, no parent+child, no speculative paths, derive from Affected Paths.

## Caused friction

| Friction                                                              | Root cause                                                                                                                                  | Cost                                                                                                        |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Added obsolete Failure Scenarios and Prior Tests sections to template | Stale mental model — did not read the implemented test-design-layer-redistribution proposal before designing sections that interact with it | One proposal revision cycle, user had to flag the error                                                     |
| Edit tool failed when updating developer-agent cue table              | `mdformat` reformatted table column widths between reads, so the `old_string` no longer matched on-disk text                                | Re-read at correct offset, ~2 minutes rework                                                                |
| Implementation agent modified dispatch script (out of scope)          | The dispatch script's worktree creation failed in the agent's environment; the agent patched it instead of stopping                         | Extra fixup commit, verification time                                                                       |
| Implementation agent silently removed user-prompt questions           | ST-0238 replaced the quality gate section but did not preserve the "Present the complete backlog" prompt that followed it                   | Extra fixup commit, could have broken interactive planning if unnoticed                                     |
| `factory/` symlink missing from worktrees                             | `init-factory` creates `factory/` as a local convenience path; `dispatch init` does not replicate it into story or feature worktrees        | Pre-commit hooks and tests fail in worktrees; manual `ln -s packages/factory factory` required per worktree |
| Reconciliation agent false positive on RECON-0001                     | Agent compared intermediate commit history instead of diffing HEAD against merge-base                                                       | Verification time to confirm dispatch had zero diff against dev                                             |
| Context compaction between planning and implementation                | Large proposal document + 6 story files exceeded context window                                                                             | Session restart required; summary carried forward but exact proposal text had to be re-read                 |

## Stop doing

- **Designing sections that interact with recently-changed subsystems without reading the current implementation first**. The Failure Scenarios / Prior Tests mistake happened because I relied on pre-redistribution knowledge. Evidence: user had to ask "Why do we need Failure Scenarios again?" and then direct me to check the redistribution proposal.

## Continue doing

- **Verifying subagent reports against observable git/fs state** — the implementation agent's summary said "218 insertions, 63 deletions" but the actual diff showed 2031/109 (inflated by the dispatch copy file). Three real issues were found only by reading the diff. Evidence: fixup commit `b66f0cc` caught issues the agent did not report.
- **Two-pass commit pattern after hooks modify files** — the pre-commit hooks (mdformat, index-lint) rewrite files deterministically. Stage with `git add -u` and recommit. Evidence: used successfully three times this session.
- **Running backlog-lint on existing stories during template changes** — the 230-story backlog is the backward-compatibility proof. Evidence: `0 error(s), 11 warning(s)` (all pre-existing) confirmed no regression.
- **The full proposal pipeline (draft → review → resolve → accept → plan → implement → reconcile)** — even for factory-internal changes, the structured pipeline caught issues at each stage that would have compounded later.

## Start doing

- **Dispatch script should create the `factory/` symlink in every worktree it provisions** — add `ln -s packages/factory factory` to `dispatch init`, `dispatch prepare-wave`, and `dispatch prepare-story`. Without it, pre-commit hooks and tests fail in worktrees. Evidence: all 6 story worktrees and the feature worktree lacked the symlink; manual creation was needed.
- **Implementation agent scope check: diff committed files against story `touches` before reporting done** — if the agent commits changes to files outside `touches`, flag them as out-of-scope rather than silently including them. Evidence: dispatch script modifications were not in any story's `touches`.
- **Reconciliation agent should diff HEAD against merge-base, not inspect intermediate commit messages** — comparing against merge-base avoids false positives from reverts that appear as "introductions" in the commit log. Evidence: RECON-0001 false positive.
- **Test coverage for every lint validation path added** — ST-0234 added `risk_level` enum validation to backlog-lint but no test. The reconciliation agent caught it (RECON-0003), but it should have been part of the story's definition of done. Evidence: 3 tests added post-hoc in fixup commit `9ded815`.

## Action items

| #   | Action                                                                                         | Category                   | Tracked in           |
| --- | ---------------------------------------------------------------------------------------------- | -------------------------- | -------------------- |
| 1   | Add `factory/` symlink creation to dispatch script worktree setup                              | Start                      | pending confirmation |
| 2   | Add scope-check to implementation agent: diff committed files against `touches` post-commit    | Start                      | pending confirmation |
| 3   | Reconciliation agent: diff against merge-base not commit history                               | Start                      | pending confirmation |
| 4   | Stories that add lint validation paths must include test cases in acceptance criteria          | Start                      | pending confirmation |
| 5   | Read the current state of any recently-changed subsystem before designing interactions with it | Stop (reframe as practice) | pending confirmation |
