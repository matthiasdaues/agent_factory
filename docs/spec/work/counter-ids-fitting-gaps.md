# Gaps Report: counter-ids-fitting

Generated: 2026-11-06
Source: [counter-ids-fitting.md](../../proposals/counter-ids-fitting.md)

This pass ran in full auto mode, without the stakeholder. Each point where the requirements agent would have asked the stakeholder is in [Choices made without the stakeholder](#choices-made-without-the-stakeholder), with its reason.

## Actor-Goal Matrix

The User is the person who walks the fitting and runs the scripts. VIRGIL is the session agent that leads the fitting. An ID producer is a file that tells its reader how to number a new indexed artifact; the proposal calls it a requestor. `next-id --plan-seed`, `next-id --move-to-origin`, and `init-factory` act as system actors. The terms counter, claim commit, ID claim, ID prefix, indexed artifact, seed, and ID producer are defined in the [glossary](../glossary.md).

| ID     | Actor                      | Goal                                                             | Rule                                                                                                          | Status    |
| ------ | -------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | --------- |
| CIF-01 | User                       | Confirm the seed of the counter in a fitting step                | Rule: User confirms the seed of the counter in a fitting step                                                 | specified |
| CIF-02 | VIRGIL                     | Point `next-id` at the project's own repository without `origin` | Rule: VIRGIL points next-id at the project's own repository when origin is missing                            | specified |
| CIF-03 | User                       | Walk the seed step in a greenfield project                       | Rule: User walks the seed step in a greenfield project                                                        | specified |
| CIF-04 | User                       | See the fitting finished only with six true keys                 | Rule: User sees the fitting finished only when all six fitting keys are true                                  | specified |
| CIF-05 | `next-id --plan-seed`      | Print one seed command from the highest number of each ID prefix | Rule: next-id --plan-seed prints one seed command from the highest number of each ID prefix                   | specified |
| CIF-06 | `next-id --plan-seed`      | Count an old file name by its number and warn about it           | Rule: next-id --plan-seed counts an old file name by its number and warns about it                            | specified |
| CIF-07 | `next-id --plan-seed`      | Check the remote before planning a seed                          | Rule: next-id --plan-seed checks the remote before it plans a seed                                            | specified |
| CIF-08 | ID Producer                | Claim an ID from the local counter without `origin`              | Rule: ID Producer claims an ID from the local counter in a project without origin                             | specified |
| CIF-09 | VIRGIL                     | Offer to move a local counter to `origin` at the session start   | Rule: VIRGIL offers to move a local counter to origin at the session start                                    | specified |
| CIF-10 | `next-id --move-to-origin` | Move the local counter to an `origin` without a counter          | Rule: next-id --move-to-origin moves the local counter to an origin without a counter                         | specified |
| CIF-11 | `next-id --move-to-origin` | Keep the marker and the setting on a collision or a failed push  | Rule: next-id --move-to-origin keeps the marker and the setting when origin holds a counter or the push fails | specified |
| CIF-12 | `next-id --move-to-origin` | Hand out no number twice while ID claims run during the move     | Rule: next-id --move-to-origin hands out no number twice while ID claims run during the move                  | specified |
| CIF-13 | `init-factory`             | Derive `counter_seeded` from the remote that `next-id` uses      | Rule: init-factory derives counter_seeded from the remote that next-id uses                                   | specified |
| CIF-14 | ID Producer                | Name the literal ID prefix at each step that creates an artifact | Rule: ID Producer names the literal ID prefix at each step that creates an indexed artifact                   | specified |
| CIF-15 | ID Producer                | Name `next-id T` at a step that adds a todo entry                | Rule: ID Producer that adds a todo entry names next-id T                                                      | specified |
| CIF-16 | User                       | Find every ID prefix in one table                                | Rule: User finds every ID prefix in one table in id-prefixes.md                                               | specified |
| CIF-17 | User                       | See the text test fail when an ID producer or the table drifts   | Rule: User sees the text test fail when an ID producer or the prefix table drifts from next-id                | specified |

## Completion Criteria Trace

Each completion criterion of the proposal traces to a Rule or to a gap below.

| Completion criterion (short form)                                                                      | Rule or gap     |
| ------------------------------------------------------------------------------------------------------ | --------------- |
| `virgil.md` § Fitting has the seed step and `counter_seeded`; `"fitted"` needs six true keys           | CIF-01, CIF-04  |
| The four orientation files list six keys, the sixth `counter_seeded`                                   | CIF-04          |
| `ST-0375.md` and `ADR` up to `0032` on one branch, `ST-0380.md` on another: `ST=380`, `ADR=32`, no ref | CIF-05          |
| A remote that holds the counter: "in use", exit `0`                                                    | CIF-07          |
| A repository without indexed artifacts: `next-id --seed 0`                                             | CIF-03, CIF-05  |
| Without `origin`: the seed lands in the own `.git`, the setting is set, a second worktree claims       | CIF-02          |
| No `origin` and no setting: `next-id ST` fails and names `origin` and `--remote`                       | CIF-08          |
| The move copies to an empty `origin` and removes the setting; a counter on `origin` refuses it         | CIF-10, CIF-11  |
| `init-factory` derives the key: setting before `origin`, unchanged when unreachable                    | CIF-13, CIF-G07 |
| `ST-0214.md` quotes `ST-9999`, `ST-0375.md` is highest: `ST=375`                                       | CIF-05          |
| `ATAM-0014-some-title.md`, `ST-0380A.md`, `BUG-HUNT.md`: `ATAM=14`, `ST=380`, one warning, exit `0`    | CIF-06          |
| After the move: the marker; a claim and `--plan-seed` in a local clone fail without `--seed`           | CIF-07, CIF-08  |
| `create-backlog-stories` names `next-id ST`, `retrospective` names `next-id T`; the todo test          | CIF-14, CIF-17  |
| Each ID producer of the table names `next-id <PREFIX>`, none `next-id <TAG>`                           | CIF-14          |
| `id-prefixes.md` lists twelve prefixes; `rules.md`, `branching-policy.md`, `finding-format.md` point   | CIF-16          |
| The text test fails on a dropped prefix or a table that differs from `next-id`                         | CIF-17, CIF-G12 |

## Missing Rules

None. Every actor-goal pair has a Rule.

## Rules Without Scenarios

None. Every Rule has at least one Scenario. The feature file holds 17 Rules and 53 Scenarios, counting each Scenario Outline once. The parser `gherkin-official` reads the file without an error and counts the same numbers.

## Ambiguous Wording

| ID      | Location                                       | Text                                                       | Issue                                                                                                                                                                                                             | Suggested fix                                                                                  |
| ------- | ---------------------------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| CIF-G09 | § `next-id --plan-seed`, item 3                | "`next-id --seed <start> <PREFIX>=<highest> …`"            | The order of the pairs is not stated. The Scenarios say "with the pairs" and name no order.                                                                                                                       | State an order, for example the order of the prefix list in `next-id`.                         |
| CIF-G10 | § `next-id --plan-seed`, item 2                | "on every local branch and every remote-tracking branch"   | The text does not say whether a file in the working tree that no commit holds yet counts. A story written but not committed would then not raise the seed.                                                        | State whether the mode reads the working tree, the index, or commits only.                     |
| CIF-G12 | § Each requestor names its prefix, second para | "A requestor missing from the table below fails the test." | The table lists only some `T` producers, but every review that adds a todo entry is a `T` producer. Read literally, every such review fails the test unless it joins the table, and the table does not name them. | State whether the test checks against this table, against `id-prefixes.md`, or by the pointer. |

## Other Gaps

| ID      | Gap                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CIF-G01 | PROP-06, open. `init-factory` still prints "add the remote `origin`, then run `next-id --seed <number>`" and "with a number above your highest ID". Both hints contradict the local counter and the seed per prefix. `config/session-menu.md` shows the fitting as "X/5" and reruns "all five fitting steps". The two `init-factory` Scenarios of CID-10 in `counter-ids.feature` keep the old hints, because the brief allowed only the remote Scenarios to change. `impact.boundaries` also leaves out the requestor files.               |
| CIF-G02 | PROP-07, open. BR-074 states "There is no local fallback (DEC-20)", and `docs/spec/architecture.dsl` places the counter only on the remote. DEC-05 and DEC-08 replace that rule. BR-075 says the clone gains no ref, but an ID claim on the local counter writes `refs/ids/counters` into the project's own `.git` by design. The Scenarios of CID-06 name a counter on `origin`, so they still hold. counter-ids DEC-17 ("the script does no scan") is replaced by `--plan-seed` but not recorded as replaced.                             |
| CIF-G03 | PROP-08, open. After a collision, the setting stays, and VIRGIL offers the same move at every session start. The project claims from its local counter while colleagues claim from `origin`. No Rule says how a human resolves the collision. CIF-11 states only the refusal.                                                                                                                                                                                                                                                               |
| CIF-G04 | PROP-09, open. The proposal does not name the file that holds the session-start check for the move. The session start lives in `AGENTS.*.md` § Session start and `config/session-menu.md`. The Scenarios of CIF-09 say "a session starts" and name no file.                                                                                                                                                                                                                                                                                 |
| CIF-G05 | PROP-13, open. A move that stops after the marker and before the push leaves the marker on the local counter, no counter on `origin`, and the setting in place. Every ID claim then fails and names a remote without a counter. No Rule covers recovery, so no Scenario does. Closed by DEC-14 of `docs/proposals/counter-ids-fitting.md`: the marker commit has the claim commit C as its parent, and a second `next-id --move-to-origin` finishes an interrupted move from it. A counter on `origin` that is not C counts as a collision. |
| CIF-G06 | § The fitting step, items 1 and 5. VIRGIL sets `agent-factory.counterRemote` before `--plan-seed`. When the User then declines the seed, the proposal does not say whether the setting stays. PROP-01 asked this, and its resolution does not answer it. The CIF-01 decline Scenario leaves the setting out.                                                                                                                                                                                                                                |
| CIF-G07 | § Fitting keys. The proposal says a greenfield project follows the same rule for `counter_seeded`. `init-factory` leaves a greenfield cache untouched (`_reconcile_project_context`, the `"greenfield"` check before `_derive_fitting_keys`), so the key is never derived there today. A greenfield session start also lists no open step, which the CIF-01 decline Scenario expects. The CIF-13 greenfield Scenario states the proposal's rule. The implementation must change the reconcile path.                                         |
| CIF-G08 | § Moving a local counter to `origin`. The proposal gives no exit code for a refused move or a failed push. The CIF-11 Scenarios state only the message and the refs.                                                                                                                                                                                                                                                                                                                                                                        |
| CIF-G11 | `counter-ids.feature`, Rule CID-07, Scenario Outline row `finding-format.md` with nine ID prefixes. This proposal moves each prefix into its own ID producer and leaves `finding-format.md` only the review that files each tag. The row may then fail. The brief allowed no change to it, so the domain-modeling agent or the spec review decides. Closed: the stakeholder approved deleting the `finding-format.md` row from CID-07. CIF-14 and CIF-16 cover the per-file claims.                                                         |

## Proposal Statements Without a Scenario

- "A new file carries the prefix and the number only, never a title (DEC-12)." No tool in the proposal checks a new file name, so no Scenario can observe the rule. CIF-06 covers the read side.
- "A plain `git push` by an agent stays blocked." This is the existing guardrail behaviour of counter-ids, and this proposal does not change it. CIF-09 checks only that `next-id --move-to-origin` passes the hook.
- The recovery of an interrupted move (PROP-13, CIF-G05).
- The deferred scope: re-seeding a counter that exists, and IDs on branches that are neither local nor fetched.

## Choices made without the stakeholder

| ID      | Choice                                                                                                                       | Reason                                                                                                                                                 |
| ------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| CIF-C01 | Step 1d wrote no area spec.                                                                                                  | The brief orders it. The feature file holds the depth of one fitting step and two script modes.                                                        |
| CIF-C02 | The scope map was not rebuilt with `reverse-map`.                                                                            | `docs/spec/scope-map.md` exists, and the requirements agent leaves an existing map as it is.                                                           |
| CIF-C03 | The new scope-map rows link the feature file in the Sources column and leave Feature Link empty.                             | The existing `specified` rows of counter-ids follow this form (CID-C03). The reconciliation agent fills Feature Link after implementation.             |
| CIF-C04 | The feature file says "ID producer" where the proposal says "requestor".                                                     | The glossary defines ID Producer for the same thing. "Requestor" has no glossary entry, and the domain-modeling agent decides whether it gets one.     |
| CIF-C05 | `next-id --plan-seed`, `next-id --move-to-origin`, and `init-factory` are the actors of their Rules.                         | The brief names them as actors. Each Rule states what the script does on its own, without a person in the loop.                                        |
| CIF-C06 | In `counter-ids.feature`, only the two Scenarios on a missing remote changed: the seed in CID-01 and the ID claim in CID-04. | The brief allows only those changes. Both now say that next-id fails only without `origin` and without `agent-factory.counterRemote` (DEC-05, DEC-08). |
| CIF-C07 | The Scenarios state no exit code for a refused or failed move, and no order of the seed pairs.                               | The proposal states neither (CIF-G08, CIF-G09). A Scenario that states one would decide for the stakeholder.                                           |
| CIF-C08 | The CIF-13 greenfield Scenario states the proposal's rule, although the code skips greenfield today. The pass did not stop.  | The proposal is consistent with itself on this point. The conflict is with the code, and the implementation resolves it (CIF-G07).                     |
| CIF-C09 | The examples use `/work/demo`, `/work/demo-feature`, `/work/demo-clone`, and `https://***@host/demo.git`.                    | Invented paths keep the Scenarios free of a real remote. The redacted URL follows BR-077.                                                              |
| CIF-C10 | The open review rows PROP-06 to PROP-09 and PROP-13 became gaps CIF-G01 to CIF-G05, and no Scenario decides them.            | The brief orders it, and DEC-13 leaves them open for planning.                                                                                         |

## Deferred Scope

The proposal defers the re-seed of a counter that exists and IDs on branches that are neither local nor fetched. This specification defines no Rule for them.
