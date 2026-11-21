# Handoff: CRAP gate setup, from acceptance to planning

## Where the work stands

The proposal `docs/proposals/crap-gate-setup.md` is `accepted` on `dev` at
commit `61426f3a6c464879ee7e7c789019fd2b0701aa19`. The next step is specification, then architecture, then planning, as
`feature-addition.md` routes it: `external_contract_change: true` needs the
requirements, domain-modeling and test-strategy agents and a spec review, and
`architecture_change: true` needs the architecture agent and an ATAM review
before the planning agent cuts stories on `dev`. Implementation runs later on
`feature/crap-gate-setup`, with story worktrees off that branch.

The proposal is the source of truth. Read it in full; this handoff repeats
none of its design.

## How it got there

Three commits on `dev` carry the history:

- `35cf451f84bcad5bebcc0c3a5ca6c549564dd202` records review pass 1 and
  DEC-01 to DEC-04.
- `eaa4d284d5916fd6ebe590b1ca41f4d687c04255` revises the proposal after passes
  1 and 2.
- `61426f3a6c464879ee7e7c789019fd2b0701aa19` adds the fixes of pass 3, a new
  Primer, the lector's two passes, DEC-08, and the acceptance.

The Appendix of the proposal holds every decision (DEC-01 to DEC-08) and every
review row (PROP-01 to PROP-28) with its resolution.

## Points a planner must not miss

- **Run-lifecycle is built.** Its stories are `done` and merged
  (`4a9e2faf`). The proposal changes the built `premerge-check` in five places
  and adds `dispatch resume-gates`. No story rebuilds what run-lifecycle
  delivered.
- **PROP-25 to PROP-28 are `fixed`, not `resolved`.** The stakeholder accepted
  without a fourth review pass. Their fixes are in the text; no reviewer has
  checked them.
- **Architecture change.** `architecture_change: true`. ADR-0003 decision 5
  gets an amendment, and arc42 § 5 and § 8 change (DEC-02). Feature-addition
  routing therefore goes through the architecture agent before or alongside
  planning.
- **The existing `crap-score` skill** is rewritten, not ignored (DEC-01).
- **No commit hook** for the gate (DEC-05).

## Review artifacts outside git

The review reports and briefs live under `.current-work/dev/`, which git does
not track:

- `.current-work/dev/scratch/proposal-review-agent/crap-gate-setup-pass-1.md`,
  `-pass-2.md`, `-pass-3.md`
- `.current-work/dev/scratch/lector-agent/crap-gate-setup-cut-plan.md`
- `.current-work/dev/scratch/write-primer/crap-gate-setup-primer.md`
- `.current-work/dev/briefs/` for the briefs of each spawn

## Working tree, not mine

These changes in the primary checkout belong to the stakeholder or another
session. Do not stage, revert, or delete them:

- `docs/spec/work/todo.md` (modified)
- `docs/proposals/agent-cli-devcontainer.md`,
  `docs/proposals/saas-browser-switchboard.md`,
  `docs/research/miro-browser-access/` (untracked)

## Other open items from the session

- Four small `af-preserve` fixture folders remain under `/tmp`, left by
  worktrees with old code. The stakeholder has not answered whether to delete
  them.
- Offered and not started: enable the gates in `docs/testing.yaml` for
  core-artifact-ownership; test the finding-classification rules R3 and R4 on
  another project; the FAGAN-0003 gap; T-0012 on transcript retention; the
  unstable layout of the FindingClassification diagram.

## Working rules of this stakeholder

- Commit only when asked. Run `git diff --cached --stat` before each commit,
  because the hooks stage files.
- Lone git commands, never compound ones.
- Format with `pre-commit run mdformat --files <file>`, never
  `.venv/bin/mdformat`.
- Edit `packages/factory/`, never `.agent-factory/factory/`.
- Present review findings before writing or fixing them.
- Full 40-character SHAs in machine-read places.

## Suggested skills

- `create-backlog`, through the planning agent, to cut the stories from the
  proposal; it runs `create-backlog-epics` and `testability-probe` on the way.
- `maintain-architecture` and `write-adr`, through the architecture agent, for
  the ADR-0003 amendment and the arc42 updates.
- `run-step`, to let the Factory pick the next agent from the state on disk.
- `explain-concept`, when a Factory term in the proposal needs a definition.
