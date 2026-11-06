---
id: FAGAN-0033
source: fagan-review
review_class: code
category: defect
type: checking
severity: major
basis:
  in_use: false
  harms_downstream: false
  fails_purpose: true
  raises_cost: false
rating:
override_by:
override_reason:
stop_confirmed_by:
stop_confirmed_reason:
artifact: packages/factory/agents/virgil.md:302-308
owner: developer-agent
status: open
traces: [ST-0379, ST-0382, BR-096, BR-104, CIFP-C04, counter-ids-fitting.feature/Rule-CIF-01]
---

# Step 4 seeds a second counter when a leftover setting meets an origin that holds the counter

**What is wrong:** A project can end up with two counters that hand out the same numbers. The User who receives this is a newcomer who declined the seed while the project had no `origin`, and who later added an `origin` that a teammate has already seeded.

The first layer that loses the information is fitting step 4 in `virgil.md:302-308`. Step 4 covers only the project without `origin`. It says nothing about a project that has `origin` now but still holds the setting `agent-factory.counterRemote` from the declined seed. CIFP-C04 keeps that setting, on the premise that "a second walk of the step sets the same value". That premise holds only while `origin` is still missing. `next-id` resolves the setting before `origin` (BR-096). So `--plan-seed` reads the local repository, finds no counter there, and never asks `origin`. The session-start check leads to the same place: the move fails and names fitting step 4 (CIFP-C16). The behavior looks unintended. Each piece follows its own decision, but no text covers the path where they meet.

```text
1. The newcomer declines the seed. The setting points at the project's own repository, which holds no counter (CIFP-C04).
2. The project gains an origin. A teammate has already seeded that origin.
3. At the session start, the move fails: "the local counter ... holds no refs/ids/counters; set up the local counter in fitting step 4".
4. In step 4, --plan-seed resolves the setting, finds no counter there, and prints "next-id --seed 0 ST=12".
5. The newcomer confirms. A second counter starts in the project's .git, and this clone claims from it while the teammates claim from origin.
```

Reproduction in a temporary directory, with local repositories only: seed a bare `origin.git` with `next-id --seed 0 ST=40`, and claim `ST-0041` there. In `demo`, commit `backlog/ST-0012.md`. Set `agent-factory.counterRemote` to `demo` and add `origin.git` as `origin`. `next-id --move-to-origin` then exits 1 and names fitting step 4. `next-id --plan-seed` prints `next-id --seed 0 ST=12` and exits 0, although `origin` holds a counter. After that seed, `next-id ST` in `demo` prints `ST-0013`, and `next-id ST --remote origin.git` prints `ST-0042`. Once the newcomer has fetched the teammates' branches, the plan starts from their highest committed number. Then the local counter hands out numbers that `origin` has already handed out but no branch holds yet.

**Why this severity:** Step 4 exists to start the one counter of a project, and on this path it starts a second one, so two clones can claim the same ID (`fails_purpose`). The QA strategy triages "two claims hand out one number twice" as blocking. The text exists only on `feature/counter-ids-fitting`, so it is not in use.

**Fix:** In `virgil.md` § 4, add one rule before `--plan-seed`. When `git remote` lists `origin` and the setting is set, check the setting's repository with `git ls-remote <path> refs/ids/counters`. When that check prints nothing, remove the setting with `git config --unset agent-factory.counterRemote` and say why. `--plan-seed` then reads `origin` and reports the counter in use. CIFP-C04 still holds: a declined seed keeps the setting while the project has no `origin`. Add a text test beside `test_fitting_text.py` for the new rule. The domain-modeling agent records the path in BR-104 and in the Rule of CIF-01.
