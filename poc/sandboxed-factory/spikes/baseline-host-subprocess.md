# PoC Story — Candidate 1: Baseline (host-native subprocess)

Plain-markdown spike story per `technical-poc` Step 1. Not tracked backlog work.

## Goal

Characterize the current orchestrator boundary mechanically, so we have a
**control** to measure the containerized candidate against. It must show that
today's host-native `subprocess.run(phase/trigger)` model gives the agent
process reach over host secrets and arbitrary network.

## Why this is a candidate

The whole premise of the PoC is that the current model is "not very secure or
sandboxed." There is no point claiming it is unless we can demonstrate the gap
as a mechanical checklist. This story does not build anything — it instruments
the existing flow to record the baseline.

## What to build

Nothing new. Run the orchestrator the way it runs today (host process) and,
from that process, enumerate:

- read access to `/etc/shadow`, `~/.aws`, `~/.ssh`, `~/.config`, and any other
  host secret paths;
- outbound egress to the public internet (e.g. `curl https://example.com`) and
  to a local listener.

## Definition of done

Mechanical checklist, all confirmed by running (not assumed):

- [ ] Host secret paths are **readable** from the agent process.
- [ ] Arbitrary outbound egress **succeeds** from the agent process.
- [ ] One-line summary of effort/risk this baseline commits to.

Record these as `poc/notes/baseline-<date>.md` (the comparison note this story
consumes).

## Comparison note

Close this story by writing the note above. Step 4 reads every note side by
side.
