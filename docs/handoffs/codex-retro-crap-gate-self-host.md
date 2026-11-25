# Brief: independent retrospective of the run `feature/crap-gate-self-host`

Run a retrospective of the implementation run `feature/crap-gate-self-host`.
A Claude Code session runs its own retrospective of the same run. The User
compares both, so work from the sources alone and do not read the other
report.

## What the run did

The run enabled the CRAP gate on this repository. It ran from 2026-11-23,
about 17:00 UTC, to the merge into `dev` on 2026-11-24. Release 1.15.0, the
update, the SEC-0010 waiver and the exceptions register followed on
2026-11-24 and 2026-11-25.

| Unit     | Content                                                                   |
| -------- | ------------------------------------------------------------------------- |
| ST-0451  | `crap-score` hands the changed paths to each measuring command (DEC-84)   |
| BUG-0141 | The Python template piled up `--basetemp` in `PYTEST_ADDOPTS`             |
| ST-0449  | The gate on this repository: Python and TypeScript measures, threshold 30 |
| BUG-0147 | A failed runtime build or update switched usage capture off               |
| SEC-0013 | ESLint comes from a committed lock, not from `npx --yes`                  |

## Sources

Read them in this order:

1. **The git history.** The feature range is `a8f61d28^1..a8f61d28^2`, with 51
   commits. The merge is `a8f61d28`. The commits after it on `dev`, up to
   `21af8714`, are the release and the follow-ups.
2. **The decisions.** `docs/proposals/crap-gate-setup.md`, DEC-84 to DEC-87.
3. **The stories and findings.** `backlog/ST-0449.md` and `backlog/ST-0451.md`.
   The findings BUG-0141, BUG-0145 to BUG-0149, SEC-0010, SEC-0013, and
   IMPL-0101 to IMPL-0117 sit under `docs/findings/` and
   `docs/findings/register/`.
4. **The reviews.** The files `docs/reviews/*-2026-11-23.md` and
   `docs/reviews/*-2026-11-24.md`, and `docs/spec/work/spec-feedback-*.md` of
   the five units.
5. **The session transcript.** It is
   `~/.claude/projects/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04.jsonl`.
   It is a JSON line per event, and the session began on 2026-11-19, so read
   only the events with a `timestamp` from `2026-11-23T17:00` on. The User's
   messages have `"type": "user"`. Read the file with a script; it is large.

## How to run it

Follow `.claude/skills/retrospective/SKILL.md`, steps 1 and 2, with the
format of `.claude/skills/retrospective/RETRO-FORMAT.md`. Write in the voice
of `packages/factory/rulebooks/conventions/factory-voice.md`.

- Every item cites a concrete event: a commit, a finding, a file, or a
  transcript timestamp.
- A friction row names its root cause and its cost.
- Judge the agents and the User's process alike. Where the Claude session
  erred, name the error and its cause plainly.
- Where the sources do not show a cause, say so. Do not guess.

## Boundaries

- Write one file: `docs/reviews/retro-2026-11-25-codex.md`. Change no other
  file.
- Do not read `docs/reviews/retro-2026-11-25.md`, the Claude session's report.
- Commit nothing, run no `next-id`, and file no todo or story. Step 3 of the
  skill happens with the User later. End the report with the action items you
  propose, in the table of the format, with `proposed` in the column
  `Tracked in`.
- Do not touch `.agent-factory/`, the usage records, or the git refs.
