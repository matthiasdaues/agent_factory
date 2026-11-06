---
type: fagan-review
title: Fagan inspection and bug hunt of counter-ids-fitting
date: 2026-11-06
status: defects
reviewer: qa-agent
findings_filed: 1
branch: feature/counter-ids-fitting
branch_base: 432069116cfe2f9dc9099cad3db0d29ebbd184b6
branch_head: 4b3a875d07dcf3c655b513f01a4d9b97df6e46b8
---

# Fagan inspection and bug hunt of counter-ids-fitting

## Result

The inspection found one major defect. It is not in use, so it is not critical. FAGAN-0033: fitting step 4 starts a second counter when a setting left over from a declined seed meets an `origin` that already holds the counter. Two clones can then claim the same ID.

The fix belongs in `virgil.md`, which lies outside the QA agent's fix ownership. So the bug hunt made no fix commit. The hunt filed one `minor` finding as a register line, BUG-0119, and found no other bug.

Next, the Implementation Agent fixes FAGAN-0033 and submits the branch for QA again. The branch is not ready to merge into `dev` until then.

## Scope

The review covers `git diff dev...feature/counter-ids-fitting` at `4b3a875d`. The review read this code and the text that agents execute:

- `packages/factory/scripts/next-id`: `--plan-seed`, the local counter, and `--move-to-origin`
- `check_counter`, `record_counter_seeded`, and `_fitting_status` in `packages/factory/scripts/init-factory`
- `packages/factory/scripts/housekeeping-about`
- `virgil.md` § Fitting, `session-menu.md` § Counter check, and the four `AGENTS.*.md` files
- the new and changed tests in `tests/factory/`

The review checked them against `counter-ids-fitting.feature`, the QA strategy `counter-ids-fitting-qa-strategy.md`, BR-096 to BR-108, the stories ST-0376 to ST-0385, and the planning choices CIFP-C01 to C18. The Decisions DEC-01 to DEC-16 and ADR-0031 to ADR-0033 count as settled. The review did not file again what the code review (IMPL-0008 to IMPL-0013), the reconciliation (RECON-0030 to RECON-0033), and the todo entries T-0017, T-0019, T-0403, and T-0404 already hold.

The classification follows `finding-classification.md`, code class.

## Acceptance test

The QA strategy sets the acceptance layer to `out`. The project declares no Gherkin runner, and every Scenario traces to a pytest test through the `spec` marker. The review found a marked test for every contract row, apart from the rows that RECON-0032 already names. The QA agent did not run the suite, because no test changed. Every commit on the branch passed the `run-tests` hook.

## Findings

| Finding                                                                                                                                                                                                                                                    | Artifact                                    | Category | Type     | Severity |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- | -------- | -------- | -------- |
| [FAGAN-0033](../findings/FAGAN-0033.md): step 4 handles only a project without `origin`. When the declined seed left the setting in place and `origin` already holds a counter, `--plan-seed` reads the local repository and prints a seed command for it. | `packages/factory/agents/virgil.md:302-308` | defect   | checking | major    |
| BUG-0119 (register `docs/findings/register/code.jsonl`): when the setting lives in the global git config, the move pushes C and then fails on `git config --unset` with a traceback. A resumed move fails the same way.                                    | `packages/factory/scripts/next-id:883`      | defect   | checking | minor    |

## Inspection by focus area

**Correctness.** `--plan-seed` reads the counter before it counts, and stops on a claim commit or a marker (BR-097, BR-098). It counts file names, register `id` fields, and todo headings on every branch and in the working tree, never body text (BR-099, BR-100). The pairs follow `PREFIXES` (CIFP-C06). `resolve_remote` takes `--remote`, then the setting, then `origin` (BR-096). The move sets the marker with a lease on C, pushes from a throwaway repository, never puts C back, and resumes from the marker's parent (BR-102, BR-103, DEC-16). `check_counter` returns `True`, `False`, or `None`, and `record_counter_seeded` leaves the key alone on `None` (BR-105). The one gap is the path of FAGAN-0033, where three settled pieces meet and no text covers the result.

**Clean Architecture.** `next-id` still uses only the standard library. The move reaches git through `LocalCounter` and module functions. BUG-0117 already covers the gap between the counter port and the architecture.

**SOLID.** No new violation with a concrete cost.

**Maintainability.** The new functions are short and their names say what they do. `_after_refusal` and the resume branch of `move_to_origin` each hold one unset of the setting and one collision check. IMPL-0012 already covers the untested branch.

**Consistency.** The new modes use the existing `git()` wrapper, `throwaway`, `_push`, and the redacted output streams, as the claim does.

**YAGNI.** No unused abstraction. `Refusal` bundles the five values that `_after_refusal` needs, and nothing else uses it.

## Bug hunt

The hunt ran `next-id` and `init-factory` from the branch head in temporary directories. It used local bare repositories and made-up values only. One cycle ran, and a second cycle over the same paths found nothing new.

| Path tried                                                                                                  | Outcome                                                                                                           |
| ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| A declined seed leaves the setting, and `origin` arrives with a counter                                     | FAGAN-0033. The move names step 4, and `--plan-seed` prints `next-id --seed 0 ST=12` beside `ST=0041` on `origin` |
| The setting in the global git config, then a move                                                           | BUG-0119. C lands on `origin`, then a traceback and exit 1                                                        |
| `--plan-seed` in a partial clone (`--filter=blob:none`)                                                     | Works. The local reads fetch missing blobs from `origin` (see the security review)                                |
| A file name `backlog/ST-9999.md`                                                                            | `--plan-seed` prints `ST=9999`, which `--seed` refuses (see Notes)                                                |
| Old file names, register lines, todo headings, an empty repository, a subdirectory as the working directory | As the Rules of CIF-05 and CIF-06 state                                                                           |

## Notes

These observations need no change now. They stay in this report only.

**A resumed move does not compare the marker with the current `origin`.** Take a first move to `origin` A that is cut off after the push. The User then points `origin` at B, and B holds no counter. The resume pushes C to B, while A still hands out numbers from C. A host change without the counter has the same effect without any move, so the move adds no new risk.

**A seed command at the top of the range fails.** A claim can reach `ST-9999`, because `MAX_SEED` is 9998 and a claim raises it by one. `--plan-seed` then prints `ST=9999`, and `--seed` refuses it. A project that has used all four digits cannot claim any further ID either.

**The printed command names a bare `next-id`.** Step 4 tells VIRGIL to run the command as printed, and the installed script is `.agent-factory/factory/scripts/next-id`. The feature file fixes the printed form, and an agent sees the error at once.

**A lock on the local counter ends the move without a retry.** When a claim's push holds `refs/ids/counters.lock`, `update-ref` reports "File exists", not a stale lease. The move then fails with "the move changed nothing", and the local counter stays at C. A test with a hand-made lock file showed this. The outcome is safe, and the User runs the move again.
