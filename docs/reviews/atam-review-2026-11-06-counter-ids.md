---
type: atam-review
title: ATAM review of the counter-ids ID allocation
date: 2026-11-06
status: defects
reviewer: architecture-review-agent
findings_filed: 4
story: counter-ids
scope: Commit 137361173920a183357e88d48e543729cd1dd021 on dev — the ID Allocation container and its views in architecture.dsl, ADR-0031, ADR-0032, and arc42 sections 5.1, 5.5, 5.11, 6.15, 7.1, 8.18, chapter 9, and QS-18 — checked against the counter-ids proposal, counter-ids.feature, BR-068 to BR-075, the next-id contract, and the Claim Lifecycle
---

# ATAM review of the counter-ids ID allocation

The leased push on one ref keeps QS-18 for every claim that `next-id` makes. The new container ID Allocation is the right home for that claim. Four Medium findings remain, and none of them reopens a decision:

- ADR-0032 says a push outside `next-id` cannot repeat a number. A hand-made claim commit can lower the counter, so it can (ATAM-0010).
- QS-18 holds only while every clone's `origin` is the same repository. The architecture does not state that, and forks silently repeat IDs (ATAM-0011).
- A claim's git calls have no time limit and no rule for credential prompts, so a claim can hang instead of naming its cause (ATAM-0012).
- Chapter 10 has no scenario for availability, security, or operability of a claim (ATAM-0013).

No finding is critical or major, so planning may start. Next, the architecture agent fixes the four findings. ATAM-0012 changes the `next-id` contract, so its fix should land before the planning agent cuts the `next-id` story.

## Reviewed architecture

- `docs/spec/architecture.dsl`: the software system Project Git Remote, the container ID Allocation with the components `next-id`, Counter Port, and Git-Ref Adapter, the seven counter-ids relationships, the views `IdAllocationComponents` and `IdClaimStaleLeaseRetry`, and the container instance in the Release 1 deployment.
- `docs/spec/dependency-rules.dsl`, which the commit leaves unchanged.
- ADR-0031 (one ref with leased pushes, Pugh matrix) and ADR-0032 (agents push the claim ref through `next-id`).
- Sections 5.1, 5.5, 5.11, 6.15, 7.1, 8.18, chapter 9, QS-18, and the 10.2 row for QS-18.
- Reference material: `docs/proposals/counter-ids.md` with its Decisions table, `docs/spec/features/counter-ids.feature`, BR-068 to BR-075 in `docs/spec/validation-rules.md`, the `next-id` contract in `docs/spec/interface-contracts.md`, the Claim Lifecycle in `docs/spec/state-machines.md`, the Counter IDs vocabulary in `docs/spec/glossary.md`, and `docs/spec/work/counter-ids-gaps.md`.

`.agent-factory/factory/scripts/arch-lint --docs-dir docs/arc42` found 0 errors, 1 warning, and 0 info, and exited 0. `.agent-factory/factory/scripts/structurizr validate` exited 0.

## Deterministic findings

| Finding                                                             | Disposition                                                                                                                                            |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `ARCH-PARSE` warning: could not extract ports from DSL or chapter 5 | Dismissed. The warning exists before this commit. The new container opens no listening port; it talks to the remote as a git client over SSH or HTTPS. |

## Prior findings

This is the first ATAM pass on counter-ids. ATAM-0001 to ATAM-0009 belong to other features and are all `resolved`.

## Rules check

No mismatch from this commit. The commit adds no rule, and section 5.11 states why: the three components ship as one script, so `dependency-check` has no module boundary to check.

The two existing rules name `factory` and `usage`, and neither matches an identifier or a name in the component view. Both rules predate counter-ids, so the brief puts them out of scope, and this review files nothing for them.

## Quality scenarios

1. **QS-18: No ID is handed out twice** (chapter 10, priority 1).

The brief names three more attributes at stake. Chapter 10 has no scenario for them (ATAM-0013), so this review evaluates them against the scenarios it derives below. The derived scenarios are the reviewer's, not the architecture's.

2. **Derived A: Availability.** Several sessions claim at the same moment, and the remote is slow or out of reach.
3. **Derived S: Security.** A principal other than `next-id` moves `refs/ids/counters`.
4. **Derived O: Operability.** A claim fails, and the person or agent must see why.

## Findings

### QS-18: No ID is handed out twice

**Architectural approach.** All sequences live in one claim commit at `refs/ids/counters` on the remote. A claim pushes a new claim commit with `--force-with-lease=refs/ids/counters:<old sha>`, and the remote accepts only one of two pushes that read the same SHA. A random token gives each claim commit its own SHA. The seed uses a create-only lease (ADR-0031, 8.18, BR-071 to BR-073).

**Sensitivity points.**

- The token. Without it, two claims that write the same message produce the same SHA, and git accepts a push that leaves a ref where it is (DEC-13).
- The stale-lease test. Only `stale info` and `cannot lock ref … is at <sha> but expected <sha>` lead to a retry. The second message comes from the remote's git, which may use another language. Then a stale lease fails at once. That costs availability, not uniqueness.
- The read after each stale lease. The adapter fetches again before it raises the line, so the retry sees the other caller's number. Section 6.15 and the dynamic view show this.
- The meaning of `origin`. Uniqueness holds only while every clone reaches the same remote (ATAM-0011).
- The content of a push outside `next-id`. The lease checks the old SHA, not the new numbers (ATAM-0010).

**Tradeoff points.** One ref for all prefixes keeps the ref list at one entry. In exchange, claims of different prefixes collide and retry (DEC-14, DEC-15). The throwaway repository keeps the clone clean and parallel claims apart. In exchange, it cannot read the clone's `.git/config` credentials (DEC-19, DEC-23).

**Risks.** ATAM-0010 (Medium) and ATAM-0011 (Medium).

**Non-risks.**

- Two claims through `next-id` on one remote, for one prefix or two, never return the same number. The race evidence of DEC-14 covers a local bare remote and two GitHub repositories.
- A claim that the remote accepts, followed by a crash before `next-id` prints, leaves a gap and no duplicate. Gaps are allowed.
- Two seeds at once leave exactly one claim commit, because the seed lease is create-only.
- The Pugh matrix arithmetic in ADR-0031 checks out: −6, +1, +2, +1 against the baseline 0.

### Derived A: Availability

**Architectural approach.** Every claim needs the remote, and there is no local fallback (DEC-07, DEC-20). A stale lease retries after a random wait of 0.1 to 1 second, at most ten times in a row (DEC-15).

**Sensitivity points.** The retry budget and the wait window, compared with the time one fetch and push takes on a hosted remote. The number of claims that run at once: the implementation agent sets no upper limit on parallel developer agents.

**Tradeoff points.** Availability against uniqueness. The design gives up offline work so that no number repeats. That is a settled decision, not a risk.

**Risks.** No response measure exists for more than two parallel claims (ATAM-0013, Medium). A slow or silent remote has no time limit (ATAM-0012, Medium).

**Non-risks.** A session without the remote fails with a named reason and no ID. That matches DEC-07 and DEC-20.

### Derived S: Security

**Architectural approach.** Only a principal with write access to the repository can change or delete the ref. Agents push the ref only through `next-id`, as the one exception to the human's ownership of pushes. The guardrail hook stays unchanged (ADR-0032, DEC-16, DEC-22).

**Sensitivity points.** The hook matches the text `git push`, so `git -C . push` passes it. Branch protection on a hosted remote does not cover `refs/ids/`.

**Tradeoff points.** An unchanged hook against enforcement of the `next-id` path. The stakeholder chose the unchanged hook, and T-0017 tracks the gap.

**Risks.** ATAM-0010 (Medium): the text calls the bypass harmless, but a hand-made claim commit can lower the counter.

**Non-risks.** A claim push changes no branch and carries no code. A deleted ref stops every claim with a message that names `next-id --seed`; it does not hand out numbers. The person who seeds again must pick a number above every ID in use, including IDs on unpushed branches. The proposal accepts that in its Design Details.

### Derived O: Operability

**Architectural approach.** `next-id` prints nothing on standard output when it fails. It exits non-zero and names one cause from the error table. It runs git with `LC_ALL=C` (8.18, BR-072, the `next-id` contract).

**Sensitivity points.** Every cause in the error table assumes that git returns. Credential prompts and a silent network make git wait instead.

**Tradeoff points.** None beyond the language trade in QS-18.

**Risks.** ATAM-0012 (Medium).

**Non-risks.** A refusal other than a stale lease fails after one push and keeps git's message (DEC-23). The fixed committer identity lets a clone without `user.name` claim.

### The container choice and YAGNI

The new container ID Allocation is the right call. Its job does not fit any existing container:

- **Validator** checks the repository and refuses bad changes. It never writes outside the clone.
- **Dispatcher** starts sessions and keeps the wave ledger.
- **Distribution** installs and updates the Factory. Its `init-factory` only asks whether the counter exists.

ID Allocation is the only part of the Factory that writes to the project's remote. It is also the only part whose result depends on the network, and it carries its own state machine. A reader who looks for the one place where an agent may push finds it as one box in the container view, and that is what ADR-0032 needs. Putting `next-id` in Dispatcher, which already holds the non-dispatch tool `index-lint`, would hide that boundary.

The split into `next-id`, Counter Port, and Git-Ref Adapter adds no artificial complexity. The port is settled by DEC-11, and the three components ship as one script, so the split costs no deployment or rule. The port is a seam by convention only, because `dependency-check` cannot check inside one script. The section says so in 5.11.

## Minor findings

These stay in the report and are not filed.

| Finding                                                                                                                                                                                                                                                                                          | Artifact                                                        | Category   | Severity |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------- | ---------- | -------- |
| Section 7.1 says the project's git remote is "the one remote that Release 1 needs". The Distribution Remote serves `install-agent-factory --from-remote` and `update-factory`. Name the project's git remote as the one remote that a working session needs.                                     | `docs/arc42/07_deployment_view.md` § 7.1                        | Defect     | Minor    |
| The glossary lists bare "Claim" and "Producer" under Avoid. Sections 5.11, 6.15, 8.18, ADR-0031, ADR-0032, and the DSL relationship from `cliAgent` use them, for example "Producer steps" and "A claim pushes". Write "ID claim" and "ID producer", or define the short form once.              | `docs/arc42/05_building_block_view.md` § 5.11, 8.18, ADRs, DSL  | Suggestion | Minor    |
| The Pugh matrix in ADR-0031 ties two criteria to QS-3 (Testability, priority 1) but weighs them 3 and 2. The rule above the matrix gives weight 3 to every priority-1 quality. The ranking does not change, because every ref option scores the same on both. Make both weights follow the rule. | `docs/adr/0031-ids-come-from-one-git-ref-with-leased-pushes.md` | Defect     | Minor    |
| The `initFactory` component description does not mention the counter check, though a new relationship goes from `initFactory` to Project Git Remote. Add the check to the description.                                                                                                           | `docs/spec/architecture.dsl`, component `initFactory`           | Defect     | Minor    |
| The technology of ID Allocation is "Script, git CLI" and names no language. `crap-score` and `dependency-check` work per language, so the planner must ask. Name the language of `next-id`.                                                                                                      | `docs/spec/architecture.dsl`, container `idAllocation`          | Question   | Minor    |
| Section 8.18 says "Every session works online for this reason". The cause runs the other way: because a claim needs the remote, every session must work online (DEC-07). Rewrite the sentence that way.                                                                                          | `docs/arc42/08_crosscutting_concepts.md` § 8.18                 | Suggestion | Minor    |

## Risk summary

| ID        | Risk                                                                                             | Severity | Mitigation                                                                                                     |
| --------- | ------------------------------------------------------------------------------------------------ | -------- | -------------------------------------------------------------------------------------------------------------- |
| ATAM-0010 | A hand-made push of the counter lowers a line, and the next claim repeats a number               | Medium   | Correct ADR-0032 and 8.18: name the duplicate path and what guards against it                                  |
| ATAM-0011 | Clones whose `origin` is a fork or a mirror claim on separate counters and repeat IDs silently   | Medium   | State the shared-`origin` assumption in ADR-0031 and 8.18, and limit the seed message to the shared repository |
| ATAM-0012 | A credential prompt or a silent remote makes a claim hang without a named reason                 | Medium   | Run git without prompts in a claim, bound each git call in time, and add a timeout event to the contract       |
| ATAM-0013 | No response measure for availability, security, or operability; QS-18 covers two parallel claims | Medium   | Add three scenarios to chapter 10, including the largest number of parallel claims                             |

## Tradeoff summary

| Tradeoff                                                         | Gains                                                        | Costs                                                                    | Settled by     |
| ---------------------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------ | -------------- |
| One ref for all prefixes instead of one ref per ID               | One entry in the ref list; no growth in `git log --all`      | Claims of different prefixes collide and retry                           | DEC-14, DEC-15 |
| Throwaway bare repository instead of the clone or a shared cache | No ref or object in the clone; parallel claims share nothing | No access to credentials in the clone's `.git/config`                    | DEC-19, DEC-23 |
| Remote as the only source instead of a local fallback            | No number repeats across clones                              | No indexed artifact without the remote                                   | DEC-07, DEC-20 |
| Unchanged guardrail hook instead of a hook that forces `next-id` | No hook change; `next-id` passes the hook as it is           | An agent can push the counter by hand (ATAM-0010)                        | DEC-16, DEC-22 |
| Retry only on the two English stale-lease messages               | Every other refusal fails at once with its real cause        | A remote that writes another language turns a stale lease into a failure | DEC-23         |
