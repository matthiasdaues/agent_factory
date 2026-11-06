---
id: 0033
status: accepted
evaluation: none
---

# The project's own repository holds the counter until `origin` exists

## Context

Take a new project on one laptop, with two worktrees and no `origin`. The
fitting reaches the step that seeds the ID counter, and the planning agent
then runs `next-id ST` for the first story. Under
[ADR-0031](0031-ids-come-from-one-git-ref-with-leased-pushes.md), the counter
`refs/ids/counters` lives on the project's remote. Without a remote, the seed
has nowhere to go, and every claim fails. So the project cannot create a
story, a finding, a todo entry, or an ADR until someone adds `origin`.

The accepted proposal
[counter-ids-fitting.md](../proposals/counter-ids-fitting.md) settles where
the counter lives without `origin`: in the project's own repository, not in a
separate or a named repository (DEC-05). Every worktree of a repository shares
its `.git`, and a local clone has the project's path as its `origin`. So one
ref in the project's `.git` reaches every session on the machine. A
reasonable reader could expect `next-id` to fall back to the local repository
whenever `origin` is missing. The proposal rejects that, because a clone that
lost its `origin` by mistake would then start a second counter without any
step failing (DEC-08).

## Decision

Without `origin`, the counter is `refs/ids/counters` in the `.git` of the
project's main repository: the local counter. The git setting
`agent-factory.counterRemote` holds the absolute path of that repository, the
parent of the directory that `git rev-parse --git-common-dir` prints. The
fitting step sets it when the project has no `origin`. The setting lives in
the shared `.git/config`, so every worktree sees it.

`next-id` resolves its remote in this order: `--remote`, then
`agent-factory.counterRemote`, then `origin` (BR-096). A claim on the local
counter is the same leased push as a claim on `origin`, through the same
git-ref adapter. A clone without `origin` and without the setting still fails
and names `origin` and `--remote`.

Once `origin` exists, VIRGIL offers the move at the session start and runs
`next-id --move-to-origin` after the User confirms (DEC-09). The move is a
mode of `next-id`, because an agent may push the claim ref only through
`next-id` ([ADR-0032](0032-agents-push-the-claim-ref-through-next-id.md)). It
runs in this order (BR-102):

1. It reads the claim commit `C` of the local counter.
2. It replaces the local ref with a marker commit, `moved=<remote>`, under a
   lease on `C`. The marker has `C` as its only parent, so `C` stays
   reachable from the local ref (DEC-14). A stale lease starts the move again
   at step 1.
3. It pushes `C` to `origin` with the create-only lease
   `--force-with-lease=refs/ids/counters:`. The push runs from a throwaway
   bare repository, so no hook of the project runs.
4. When the push succeeds, it removes `agent-factory.counterRemote`. When the
   push fails, the marker and the setting stay, and `next-id` names the
   cause. It never puts `C` back: from step 2 on, the Local Counter hands out
   no number, so it cannot repeat a number of a counter that someone seeded
   on `origin` meanwhile (DEC-16).

The marker goes in before the push. So a claim during the move either lands
before the marker and travels to `origin` with `C`, or it reads the marker and
fails (BR-103). A claim or a `--plan-seed` that reads the marker names the
remote that now holds the counter and never advises a seed (BR-097).

A second run of `next-id --move-to-origin` finishes a move that stopped after
step 2 (DEC-14). It finds the marker, takes `C` from the marker's parent, and
goes on at step 3. When `origin` already holds `C`, the earlier push went
through, so the move keeps the marker and removes the setting. When `origin` holds a claim commit other than `C`, the move cannot
tell whether that counter grew from `C`, because a claim commit has no parent.
So it treats the case as a collision: it names both counters and changes
nothing. The Local Counter keeps the marker and the setting stays, so no
claim lands on `C` again. That is the same outcome as a counter that someone
else seeded. A failed push ends the same way as a cut-off move, so a second run resumes
after both. So an interrupted move needs no new seed, and no claimed number
goes out twice.

This decision replaces one rule of ADR-0031: "without the remote, no session
can create an indexed artifact" (counter-ids DEC-20). Every other part of
ADR-0031 stands.

## Consequences

- A project without `origin` creates indexed artifacts from its first fitting
  on, and every worktree and local clone claims from the one local counter.
- The main repository gains the ref `refs/ids/counters` and the setting
  `agent-factory.counterRemote`. A claim still adds no ref and no object to
  the clone it runs in.
- A clone that lost its `origin` by mistake fails as before, because it holds
  no setting.
- When `origin` already holds a counter, the create-only lease refuses the
  push. The Local Counter keeps the marker, the setting stays, and every claim
  fails until a human resolves the collision. `next-id` names both counters,
  and VIRGIL reports
  the collision, so a counter that someone else seeded never goes unnoticed
  (DEC-05). How a human resolves the collision is open (gap CIF-G03).
- After the move, a local clone whose `origin` is the project's path reads the
  marker and fails with the name of the new remote. The human then points the
  clone's `origin` at that remote.
- A move that stops between the marker and the push leaves the marker, no
  counter on `origin`, and the setting. Every claim then fails and names
  `origin`, until VIRGIL offers the move again at the next session start and
  the second run finishes it. VIRGIL offers it, because the setting is still
  set and `origin` exists.
- The marker keeps `C` alive in the main repository, so `git gc` never prunes
  the last claim commit of the Local Counter. A claim reads only the message
  of the marker, so the parent changes no claim.
- [8.18](../arc42/08_crosscutting_concepts.md#818-id-allocation) describes the
  concept, [6.16](../arc42/06_runtime_view.md#616-move-of-a-local-counter-to-origin)
  shows the move, and QS-22 and QS-23 in
  [chapter 10](../arc42/10_quality_requirements.md#qs-22-a-move-hands-out-no-id-twice)
  set its measures.
