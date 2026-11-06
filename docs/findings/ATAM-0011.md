---
id: ATAM-0011
source: atam-review
severity: medium
category: defect
artifact: docs/adr/0031-ids-come-from-one-git-ref-with-leased-pushes.md#consequences
status: open
owner: architecture-agent
traces: [ADR-0031, QS-18, DEC-18, BR-074]
---

# The architecture assumes that every clone's `origin` is the same repository

**What is wrong:** ADR-0031 needs "one place that every clone reaches", and QS-18 sets the environment "Both clones push to the same remote". `next-id` finds that place as the URL of `origin` (BR-074), and the producer steps call `next-id <PREFIX>` without `--remote`. Neither ADR-0031 nor section 8.18 states the assumption that every clone's `origin` is one shared repository.

Take a project where two contributors work from their own forks. Each clone's `origin` is the contributor's fork. `init-factory` reports a missing counter in each fork, so each contributor seeds the fork with `next-id --seed 1000`. Both then claim `ST-1001`, and the two pull requests collide on the shared repository. No step fails, so nobody sees the duplicate until the merge. The same happens when one clone's `origin` points at a mirror.

This is a consequence of DEC-18, which keeps the counter on `origin`. The finding does not ask to change DEC-18. It asks to name the condition under which QS-18 holds.

**Fix:** Add the assumption to the consequences of ADR-0031 and to section 8.18: every clone that creates indexed artifacts must have the shared repository as `origin`. State what a fork workflow loses: each fork holds its own counter, and IDs repeat across forks. State that seeding a fork breaks QS-18, so the seed message of `init-factory` should say to seed only the shared repository. If the stakeholder wants fork workflows supported, that is a new decision for the proposal, not an architecture change.
