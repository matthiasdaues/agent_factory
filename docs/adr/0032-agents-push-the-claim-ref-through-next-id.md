---
id: 0032
status: accepted
evaluation: none
---

# Agents push the claim ref through `next-id`

## Context

Take a code review in manual mode. The review files the finding `FAGAN-1004`
on the story branch. Its number comes from `next-id FAGAN`, and `next-id`
pushes a new claim commit to `refs/ids/counters` on the remote
([ADR-0031](0031-ids-come-from-one-git-ref-with-leased-pushes.md)).

`rules.md` § Dispatch gives the human every push in manual mode. If that rule
held for the claim, the review would stop at every finding and wait for the
human to push. A reader of `rules.md` would expect the rule to hold here too.

The accepted proposal [counter-ids.md](../proposals/counter-ids.md) settles the
question in DEC-16 and DEC-22. No open alternative is left to weigh, so
`evaluation: none`.

## Decision

An agent may push the claim ref through `next-id`, in manual and in automated
mode. `rules.md` § Dispatch and § Git workflow state this as the one exception
to the human's ownership of pushes.

The guardrail hook `block-dangerous-git.sh` stays unchanged. It matches the
text `git push` in a shell command, so the command `next-id ST` passes it.

## Consequences

- An agent creates an indexed artifact without waiting for the human.
- A claim push changes no branch and carries no code. The lease refuses every
  stale update, so a push cannot hand out a number twice.
- The hook does not force a claim through `next-id`. A push written as
  `git -C . push` passes the hook too. Such a push can leave a gap in a
  sequence, but no duplicate. T-0017 in `docs/spec/work/todo.md` tracks the
  hook gap.
