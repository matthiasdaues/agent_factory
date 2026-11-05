# Gaps Report: counter-ids

Generated: 2026-11-05
Source: [counter-ids.md](../../proposals/counter-ids.md)

This pass ran in full auto mode, without the stakeholder. Each point where the requirements agent would have asked the stakeholder is in [Choices made without the stakeholder](#choices-made-without-the-stakeholder), with its reason.

## Actor-Goal Matrix

The User is the person who drives the Factory by hand, as the glossary defines. A caller is the User or a CLI-Invoked Agent that runs `next-id`. A Factory producer is a file that tells its reader how to number a new indexed artifact.

| ID     | Actor                          | Goal                                               | Rule                                                                       | Status    |
| ------ | ------------------------------ | -------------------------------------------------- | -------------------------------------------------------------------------- | --------- |
| CID-01 | User                           | Seed the counter once for a project                | Rule: User seeds the counter once for a project                            | specified |
| CID-02 | User or CLI-Invoked Agent      | Claim the next ID of a prefix                      | Rule: Caller claims the next ID of a prefix                                | specified |
| CID-03 | User or CLI-Invoked Agent      | Get an ID that no parallel caller gets             | Rule: Two callers that claim at the same time get different IDs            | specified |
| CID-04 | User or CLI-Invoked Agent      | See a failed claim stop and name its reason        | Rule: Caller sees a failed claim stop and name its reason                  | specified |
| CID-05 | User, agent, or ticket adapter | Claim on a named remote without a clone            | Rule: Caller claims on a named remote without a clone                      | specified |
| CID-06 | User or CLI-Invoked Agent      | Keep the clone unchanged by a claim                | Rule: Caller's clone stays unchanged by a claim                            | specified |
| CID-07 | Factory producer               | Take each new ID from `next-id`                    | Rule: Factory producer takes each new ID from next-id                      | specified |
| CID-08 | CLI-Invoked Agent              | Commit an indexed artifact on any branch           | Rule: CLI-Invoked Agent commits an indexed artifact on any branch          | specified |
| CID-09 | CLI-Invoked Agent              | Push the claim ref through `next-id` in both modes | Rule: CLI-Invoked Agent pushes the claim ref through next-id in both modes | specified |
| CID-10 | `init-factory`                 | Tell the user how to seed the counter              | Rule: init-factory tells the user how to seed the counter                  | specified |
| CID-11 | Stakeholder                    | Check the claim protocol against GitHub            | Rule: Stakeholder checks the claim protocol against GitHub                 | specified |

The ticket adapters of [project-agent-flows.md](../../proposals/project-agent-flows.md) appear only as callers of `--remote` in CID-05, because that proposal is a draft.

## Completion Criteria Trace

Each completion criterion of the proposal traces to a Rule or to a gap below.

| Completion criterion (short form)                                                   | Rule or gap     |
| ----------------------------------------------------------------------------------- | --------------- |
| `next-id ST` prints the next story ID, and the claim commit holds it                | CID-02          |
| The race test: 20 rounds, 40 different IDs, no skipped number, every call exits `0` | CID-03          |
| Ten rejected claims in a row: exit non-zero, name `ST` and the last number          | CID-04, CID-G01 |
| `next-id XX` names `XX` and the list of prefixes                                    | CID-04          |
| A refusal other than a stale lease fails after one try with git's message           | CID-04          |
| A clone without `user.name` claims, and the claim commit names `next-id`            | CID-02          |
| A missing `refs/ids/counters` names `next-id --seed`                                | CID-04          |
| An unreachable remote is named                                                      | CID-04          |
| No `origin` and no `--remote`: exit non-zero, no ID, `origin` and `--remote` named  | CID-04          |
| `--remote` claims on that remote, also outside any clone                            | CID-05          |
| The clone holds no new ref and no new object after a claim                          | CID-06          |
| `--seed 1000` creates the ref, and the next ST is `ST-1001`                         | CID-01          |
| `--seed 1000 ADR=6` writes `ADR=0006`, and the next ADR is `ADR-0007`               | CID-01          |
| `--seed` on an existing ref exits non-zero and leaves the ref unchanged             | CID-01          |
| `--seed 10000`, `--seed abc`, `--seed 1000 XX=5` fail and create no ref             | CID-01          |
| Two parallel seeds leave exactly one seed                                           | CID-01          |
| `init-factory` prints the seed message, the remote message, and the warning         | CID-10, CID-G02 |
| Each producer file calls `next-id` and none scans for the highest number            | CID-07          |
| `rules.md` § Branching, `branching-policy.md`, `planning-agent.md` allow any branch | CID-08          |
| `rules.md` § Dispatch and § Git workflow state the claim push exception             | CID-09          |
| Manual check: the race test on GitHub hands out no number twice                     | CID-11          |
| `index-lint --check` passes                                                         | CID-G08         |

## Missing Rules

None. Every actor-goal pair has a Rule.

## Rules Without Scenarios

None. Every Rule has at least one Scenario. The feature file holds 11 Rules and 39 Scenarios, counting each Scenario Outline once.

## Ambiguous Wording

| ID      | Location                                      | Text                                                                                   | Issue                                                                                                                                                                                                                                                                                                       | Suggested fix                                                                                                                                         |
| ------- | --------------------------------------------- | -------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| CID-G01 | Proposal, Completion Criteria, ten rejections | "A test makes a local bare repository reject every update … with a `pre-receive` hook" | A `pre-receive` hook refuses with its own message, not with a stale lease. Under DEC-23, `next-id` then fails after one try, as the read-only criterion states. So the test that the criterion names cannot produce ten rejections. The behaviour itself is clear, so the Scenario states ten stale leases. | The test-strategy agent picks a setup that makes the remote report a stale lease ten times, for example a remote that moves the ref before each push. |
| CID-G03 | Proposal, `next-id --seed`, step 4            | "Print the seed lines on standard output"                                              | The proposal does not say whether the token line counts as a seed line. The Scenario says only "prints the seed lines".                                                                                                                                                                                     | State whether the output holds the token line.                                                                                                        |

## Other Gaps

| ID      | Gap                                                                                                                                                                                                                                                                                                              |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CID-G02 | The proposal gives `init-factory`'s exit code only for an unreachable `origin` (exit `0`). It names no exit code for a missing counter or a missing `origin`, and no output when the counter exists. The Scenarios state only the messages. Since the install needs no counter, exit `0` is the likely intent.   |
| CID-G04 | A claim on a prefix whose line holds 9999 has no defined result. The proposal defers numbers above 9999 and gives no error row for that case.                                                                                                                                                                    |
| CID-G05 | A claim commit whose message has no `start` line, or a line that is not a number, has no defined result. `seed` always writes a `start` line, so the case arises only when someone writes the ref by hand.                                                                                                       |
| CID-G06 | The proposal states the throwaway bare repository for `claim` only. It does not say whether `--seed` also runs in one, or whether `--seed` leaves the clone unchanged. CID-06 covers claims only.                                                                                                                |
| CID-G07 | The guardrail hook lets `git -C . push` pass, so an agent can push the claim ref without `next-id` (DEC-22). The lease still refuses every stale claim, so such a push can leave a gap but no duplicate. The hook stays unchanged, so no Rule covers it. T-0017 in `docs/spec/work/todo.md` tracks the hook gap. |
| CID-G08 | `index-lint --check` is a gate for the changed Factory files, not a behaviour of the counter. No Scenario holds it. The QA strategy runs it as a gate.                                                                                                                                                           |

## Proposal Statements Without a Scenario

These statements describe git's own behaviour or a limit, not a behaviour of `next-id`. No Scenario can check them through `next-id`:

- The claim ref lives outside `refs/heads/` and `refs/tags/`, so no branch list shows it, and a default clone does not fetch it.
- git's garbage collection removes old claim commits.
- Only a person or token with write access can change or delete the claim ref.
- Credentials come from the user's global git config, a credential helper, or an SSH key. A credential helper in the clone's own `.git/config` does not reach the claim. This is a limit, and a test cannot show it without a remote that asks for credentials.
- Without the remote, no session can create an indexed artifact (DEC-07). The unreachable-remote Scenarios of CID-04 cover the observable part.

`poc/counters/ref-claim-race.sh` shows the claim protocol on a local bare remote. It is evidence for CID-03, not the implementation, so the feature file carries no @-reference to it.

## Choices made without the stakeholder

| ID      | Choice                                                                                                                                                                | Reason                                                                                                                                                        |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CID-C01 | Step 1d wrote no area spec.                                                                                                                                           | The brief orders it. The proposal describes one script and its rule changes, and the feature file holds that depth.                                           |
| CID-C02 | The scope map was not rebuilt with `reverse-map`.                                                                                                                     | `docs/spec/scope-map.md` exists, and the requirements agent leaves an existing map as it is.                                                                  |
| CID-C03 | The new scope-map rows link the feature file in the Sources column and leave Feature Link empty.                                                                      | The existing `specified` rows, such as those of core-artifact-ownership, follow this form. The reconciliation agent fills Feature Link after implementation.  |
| CID-C04 | The ten-rejections criterion became a Scenario with ten stale leases, and its test method went to CID-G01. The pass did not stop.                                     | The behaviour is clear from DEC-15 and DEC-23. Only the test method in the criterion conflicts with DEC-23, and the test-strategy agent owns the test method. |
| CID-C05 | The `init-factory` Scenarios state no exit code for a missing counter or a missing `origin`.                                                                          | The proposal states none (CID-G02). A Scenario that states one would decide for the stakeholder.                                                              |
| CID-C06 | The actors use the glossary terms User and CLI-Invoked Agent. "Caller" in a Rule name means either one, and "Factory producer" is defined in the feature description. | The glossary defines User and CLI-Invoked Agent. A new glossary term belongs to the domain-modeling agent.                                                    |
| CID-C07 | `PROP` and `RETRO` appear in the Scenario Outline of prefixes that `next-id` refuses.                                                                                 | The proposal gives neither a sequence (DEC-09, § The counter port). The prefix check refuses every prefix outside the list.                                   |
| CID-C08 | The split-story letters got a Scenario that keeps their scan.                                                                                                         | The proposal defers the letters. The Scenario keeps `create-backlog-slice-story` from switching to `next-id` by mistake.                                      |

## Deferred Scope

The proposal defers counter adapters for other backends, the renaming of existing IDs, numbers above 9999, and letters for split stories. This specification defines no Rule for them, apart from the Scenario of CID-C08.
