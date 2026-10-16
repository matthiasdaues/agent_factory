# Handoff: brownfield onboarding run, closed 2026-10-16

The run is done. All five stories, ST-0313 to ST-0317, merged into `dev` as
`55ece0a7`; the full suite passed there. BUG-0093 to BUG-0096 are resolved
with their fix commits and known gaps. BUG-0092 stays open for the
brief-storage run. The plan is
[brownfield-onboarding-run-2026-10-16.md](../reviews/brownfield-onboarding-run-2026-10-16.md).

## Iterations

- ST-0313: two iterations. The first left the architecture agent's archive
  step, which would archive the new scope map.
- ST-0314: three iterations, the tier's limit. The Stage 1 exit check first
  never failed, then passed a draft map when `spec-lint` crashed.
- ST-0315: two iterations. Overlapping workflow branches, and no stop on a
  draft map.
- ST-0316 and ST-0317: one iteration each.

## Exceptions granted in this run

- ST-0313's scope was widened by `rulebooks/rules.md` and
  `tests/factory/test_index_lint.py` for its second iteration (`1a71db31`).
- ST-0317's scope was widened by 21 diagram SVGs that the `arch-lint` hook
  re-rendered for a timestamp alone (`1e5bd2a1`). The orchestrator
  committed ST-0317 itself, on the stakeholder's word.
- The stakeholder ran `update-factory`, because the installed `arch-lint`
  lacked a flag the hook passes.

## What is left in place

- `.current-work/feature/brownfield-onboarding/` keeps the ledger, the
  briefs, the analysis report and the review probes. It is ignored by git.
- The integration worktree and the story worktrees are still there; remove
  them with their branches once `dev` is pushed.

## Evidence for the gate proposal (bug-hunt handoff item 23b)

- A hook that runs the installed copy blocked a correct commit because the
  copy was older than the source.
- The `arch-lint` hook re-renders every SVG for a timestamp and stages it.
- `merge-story` scales the file limit by the number of `touches` entries,
  so a folder entry lowers the limit for many files.
- A developer ran `verify-base` in the invocation worktree again and left a
  marker there that would let an unchecked commit through.
- `update-factory`'s last question did not show behind the `!` prefix.
- The handoff contract named bare `uv run pytest` (BUG-0109).
- `update-factory` never refreshes a project's hook block (BUG-0110), and
  hooks pass silently when the factory folder is missing (BUG-0111). In
  another project every gate passed unchecked for this reason.

## Next work

1. Brief-storage run: the brief rule (bug-hunt handoff item 18), BUG-0092,
   BUG-0102 and BUG-0103.
2. Gate proposal with `draft-proposal` (bug-hunt handoff item 23b and the
   evidence above).
3. Findings filed after this run: BUG-0098 to BUG-0109.
