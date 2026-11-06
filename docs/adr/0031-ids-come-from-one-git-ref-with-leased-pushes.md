---
id: 0031
status: accepted
evaluation: pugh-matrix
---

# IDs come from one git ref on the project's remote with leased pushes

## Context

A session takes the number of a new story, finding, todo entry, or ADR by
looking for the highest number in the files it can see. Two sessions on
different branches see the same highest number, so both create `ST-0346`. The
rule "Indexed Artifacts On Dev" in `branching-policy.md` works around this:
every indexed artifact must be committed to `dev`. The manual-mode story flow
cannot follow that rule, because a code review files its findings on the story
branch.

So the number must come from one place that every clone reaches, and that
place must refuse a second claim of the same number. The accepted proposal
[counter-ids.md](../proposals/counter-ids.md) weighed four sources against the
scan:

- **The counter service countapi.** Anyone who knows a key can set a counter
  back, so a number can come out twice (DEC-01, DEC-12).
- **One ref per ID**, `refs/ids/<PREFIX>/<NNNN>`, created with a create-only
  push. Every ID adds a ref to `git ls-remote` and `git log --all` (DEC-12,
  DEC-14).
- **One ref, `refs/ids/counters`, claimed from a throwaway bare repository.**
  Each call of `next-id` works in a new temporary directory and deletes it at
  exit (DEC-14, DEC-19).
- **One ref, claimed from a shared cache repository.** Parallel claims on one
  machine would share the fetched ref of the cache (DEC-19).

The criteria come from
[chapter 10](../arc42/10_quality_requirements.md). Weight 3 marks a quality of
priority 1, weight 2 a quality of priority 2, and weight 1 a quality that no
scenario names. The scale runs from −1 to +1 against the scan as baseline.

## Decision

Every ID number comes from one git ref, `refs/ids/counters`, on the project's
remote. The ref points at a claim commit: a commit with no parent on the empty
tree. Its message holds the seed value `start`, one line per prefix with the
highest number claimed so far, and a random token. The token gives every claim
commit its own SHA.

`next-id <PREFIX>` claims a number in a throwaway bare repository. It fetches
the ref, raises the line of the prefix, and pushes a new claim commit with
`--force-with-lease=refs/ids/counters:<old sha>`. When another caller claimed
first, for any prefix, the lease is stale, and the remote refuses the push.
`next-id` then waits a random 0.1 to 1 second and starts again, at most ten
times in a row. Any other refusal fails at once with git's message (DEC-15,
DEC-23). `next-id --seed` creates the ref once with a create-only lease, so a
seed never changes a counter in use (DEC-17).

`next-id` reaches the counter through a port with the operations `claim` and
`seed`. The git-ref adapter is the only adapter, and `next-id` uses it without
a choice or a config file (DEC-11, DEC-18).

The stakeholder has not confirmed this matrix. The brief for the architecture
step ran in full auto mode, so the scores are the architecture agent's
reading of the proposal's Decisions table.

| Criterion                                                      | Weight | Scan of the highest number (baseline) | countapi service | One ref per ID | One ref, throwaway repository | One ref, shared cache repository |
| -------------------------------------------------------------- | ------ | ------------------------------------- | ---------------- | -------------- | ----------------------------- | -------------------------------- |
| Unique IDs across branches and clones (QS-18)                  | 3      | 0                                     | 0                | +1             | +1                            | +1                               |
| Tests run on a local bare repository (QS-3)                    | 3      | 0                                     | −1               | 0              | 0                             | 0                                |
| Only repository writers change the counter (Safety)            | 2      | 0                                     | −1               | 0              | 0                             | 0                                |
| No new service, config, or state to keep (Simplicity)          | 2      | 0                                     | −1               | −1             | −1                            | −1                               |
| Producers depend on a port, not a backend (Clean Architecture) | 2      | 0                                     | +1               | +1             | +1                            | +1                               |
| Parallel claims on one machine share no state                  | 1      | 0                                     | 0                | 0              | 0                             | −1                               |
| The remote's ref list stays at one entry                       | 1      | 0                                     | 0                | −1             | 0                             | 0                                |
| Works without the network                                      | 1      | 0                                     | −1               | −1             | −1                            | −1                               |
| **Weighted total**                                             |        | **0**                                 | **−6**           | **+1**         | **+2**                        | **+1**                           |

Three results are close. One ref per ID and the shared cache repository each
lose to the chosen option on one criterion of weight 1: the ref list and the
shared state. The scan trails the chosen option by two
points only, because it is simple and works offline. But the scan fails the
case that started the change, two branches with the same highest number. So
the unique-ID criterion decides, whatever weight the other criteria get.

## Consequences

- An indexed artifact may be created and committed on any branch. The rule
  "Indexed Artifacts On Dev" goes away.
- Every producer of an indexed artifact needs the remote. Without it, no
  session can create a story, finding, todo entry, or ADR (DEC-07, DEC-20).
- Claims of different prefixes collide on the one ref and retry. The proposal's
  race script needed one or two tries per claim on a local bare remote and on
  two GitHub repositories (DEC-14).
- The clone gains no ref and no object. Credentials must come from the user's
  global git config, a credential helper, or an SSH key, because the throwaway
  repository does not read the clone's `.git/config` (DEC-23).
- QS-18 holds only while every clone that creates indexed artifacts has the
  one shared project repository as `origin`, because the producer steps call
  `next-id` without `--remote`. A fork or a mirror as `origin` holds its own
  counter. A person who seeds a fork starts a second sequence, and IDs repeat
  across forks without any step failing. Support for fork workflows would need
  a new decision in the proposal.
- QS-19 to QS-21 in
  [chapter 10](../arc42/10_quality_requirements.md#qs-19-parallel-claims-succeed-within-the-retry-budget)
  set the availability, operability, and security measures of a claim.
- A writer who deletes `refs/ids/counters` stops every claim until a person
  seeds again with a number above the highest ID. Nothing in the Factory
  deletes the ref.
- A remote that refuses custom refs needs a second adapter. The port keeps
  that change inside the ID Allocation container.
- [8.18](../arc42/08_crosscutting_concepts.md#818-id-allocation) describes the
  concept, and [6.15](../arc42/06_runtime_view.md#615-id-claim-with-a-stale-lease)
  shows a claim with a retry.
