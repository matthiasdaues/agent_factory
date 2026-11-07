---
type: atam-review
title: ATAM review of the finding-classification architecture
date: 2026-11-07
status: defects
reviewer: architecture-review-agent
findings_filed: 3
story: finding-classification
scope: Commit 439d86fbc2cedd03cb027a1dc9487e9905407f6f on dev — ADR-0034 to ADR-0036, the Finding Classification elements and views in architecture.dsl, and arc42 sections 5.1, 5.9, 5.12, 6.17 to 6.21, the chapter 7 paragraph, 8.19, the chapter 9 rows, and QS-24 to QS-27 — checked against the finding-classification proposal (DEC-01 to DEC-63), its feature file, BR-079 to BR-095, BR-109, BR-110, the finding-classification contracts, and the Finding Lifecycle
---

# ATAM review of the finding-classification architecture

The register file per finding keeps QS-26 without a merge driver. The stop check reads the working tree and `HEAD`, so an uncommitted change cannot end a stop. Two risks block planning:

- The guard handles a patch call only in Codex. Copilot CLI and Pi also guard `apply_patch` without that rule, and the OpenCode row names no tools (ATAM-0018, `major`).
- A committed lowering ends a stop in every project whose pre-commit hook does not run `finding-lint`. The architecture does not say how the hook reaches a project (ATAM-0019, `major`).

One `minor` risk went to `docs/findings/register/architecture.jsonl` (ATAM-0020). The notes below are four sensitivity points, three non-risks, four tradeoff points, and five notes on the documents. Next, the architecture agent fixes ATAM-0018 and ATAM-0019, and the stakeholder confirms the consent class of `finding-lint` that ATAM-0019 asks for.

Every finding uses the architecture class of the accepted proposal `docs/proposals/finding-classification.md`, as the brief requires. Priority 1 in section 10.2 gives importance `high`, and priority 2 gives `medium`.

## Reviewed architecture

- `docs/spec/architecture.dsl`: the containers Finding Registers, Finding Schemas, and Factory Settings; the components `finding-lint`, `guard-human-fields`, the five guard entries, `premerge-check`, Main Checkout Locator, Stop Check, and Migration Agent; the relationships tagged `Finding Classification`, two of them also `Cross-feature`; the view `FindingClassification`; and the dynamic views `CriticalStop`, `GuardRefusesHumanField`, `GuardFailsClosed`, `FindingLintCommit`, and `FindingMigration`.
- `docs/spec/dependency-rules.dsl`, which the commit leaves unchanged.
- ADR-0034, ADR-0035, and ADR-0036.
- Sections 5.1, 5.9, 5.12, 6.17 to 6.21, the paragraph in 7.1, 8.19, the chapter 9 rows, QS-24 to QS-27, and their rows in 10.2.
- Reference material: the proposal with DEC-01 to DEC-63, `docs/spec/features/finding-classification.feature`, BR-079 to BR-095, BR-109, and BR-110 in `docs/spec/validation-rules.md`, the Finding Classification Contracts in `docs/spec/interface-contracts.md`, the Finding Lifecycle in `docs/spec/state-machines.md`, and `docs/spec/work/finding-classification-gaps.md`.
- Code read to check claims of the architecture: `packages/factory/scripts/premerge-check`, `packages/factory/config/hooks/block-dangerous-git.sh`, `packages/factory/config/extensions/dispatch-wave.ts`, `packages/factory/config/pre-commit-config.yaml`, `packages/factory/config/hook-metadata.yaml`, `packages/factory/scripts/hook-subset`, and the guard wiring in `packages/factory/scripts/init-factory`.

`.agent-factory/factory/scripts/arch-lint --docs-dir docs/arc42` found 0 errors, 1 warning, and 0 info, and exited 0. `.agent-factory/factory/scripts/structurizr validate` exited 0.

## Deterministic findings

| Finding                                                             | Disposition                                                                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `ARCH-PARSE` warning: could not extract ports from DSL or chapter 5 | Dismissed. The warning exists before this commit. No Finding Classification element opens a port or listens on one. |

## Prior findings

This is the first ATAM pass on finding-classification, so no prior finding of this feature exists. Open `ATAM` findings of other features belong to their own repeat passes.

## Rules check

No mismatch. The commit adds no rule. The two existing rules name `factory` and `usage`, and no Finding Classification relationship crosses from Factory Flow Control to Usage Analysis or back.

## Quality scenarios

1. **QS-24: A critical finding stops every dispatch and merge** (priority 1).
2. **QS-25: No agent writes a human field** (priority 1).
3. **QS-26: Parallel reviews merge their registers without loss** (priority 1).
4. **QS-27: A wrong in_use answer fails the commit** (priority 2).

The two cross-feature dependencies and the one-time migration have no scenario of their own. This review checks them under [Cross-feature dependencies and the migration](#cross-feature-dependencies-and-the-migration).

## Findings

### QS-24: the stop

- **Approach.** The Stop Check in `dispatch` reads each finding file in the working tree and at `HEAD` (DEC-57). `dispatch` calls it before ten subcommands, and `premerge-check` calls it before any other check. During a stop, `premerge-check` writes no marker, so `block-dangerous-git.sh` denies `git merge`.
- **Risk (ATAM-0019, `major`).** Section 8.19 names three mechanisms that keep a block in the stakeholder's hands. Only `finding-lint` at the pre-commit hook covers a committed change. The guard refuses only human fields, and severity, basis, and a removal are none. A consumer project runs only the Factory hooks its user approved in fitting step 3. The architecture names no `hook-metadata.yaml` entry, consent class, or update path for `finding-lint`. In a project without the hook, an agent lowers `critical` to `major`, commits, and both versions read `major`, so the stop ends without the damage checks.
- **Sensitivity point.** The stop check must list the finding files of `HEAD` as well as those of the working tree. Otherwise a file removed in the working tree is never read, and the stop ends. BR-091 and the key points of 6.17 require this. The component text in 5.12 and the DSL, "reads each `docs/findings/*.md` in the working tree and its `HEAD` version", reads like a list of the working tree only. Stating the union of both lists in the component text would remove the doubt.
- **Sensitivity point.** The stop holds dispatch only inside `dispatch`. The Pi tools `dispatch-wave` and `run-agent` and the component `trigger` start sessions during a stop. Merges still fail, because `dispatch-wave` gates each merge with `premerge-check`, and `dispatch merge-story` calls the stop check. This follows DEC-28, which puts the stop into two scripts, so it is a note.
- **Sensitivity point.** During a stop, `premerge-check` writes no marker, but it does not remove an existing one. The marker holds a branch and its head SHA. A marker left from an earlier pass therefore matches only a branch that `dispatch merge-story` passed just before. An agent could still run `git merge` on that branch after a red post-merge suite reset the merge. Removing the marker during a stop would close this case at the cost of one line.
- **Non-risk.** No open finding in `docs/findings/` has `severity: critical` today, so the stop does not fire on old findings when it ships. Assumption: nobody files an old-format `critical` finding before the migration commit. A consumer project that holds an open old-format `critical` finding stops after `update-factory`, and its stop notice has no damage items. That outcome matches the old meaning of "Critical", which already blocked the phase.

### QS-25: the guard

- **Approach.** One script, `guard-human-fields`, holds the rule. Each of the five CLIs calls it from its own hook for edit, write, and shell calls (ADR-0035). Pi and OpenCode block the call when the script is missing.
- **Risk (ATAM-0018, `major`).** The rule for a patch that the guard cannot parse holds only in Codex. Copilot CLI and Pi guard `apply_patch` too, with no such rule. The OpenCode row says "the plugin's edit, write, and shell tools" and names none of them, so the QS-25 measure "every guarded call type of every CLI" has no test cases for OpenCode. As this reviewer knows the OpenCode source, it also has a patch tool and a multi-edit tool. This review did not check the current release.
- **Tradeoff point.** The guard checks the text of each call. That keeps it to one script behind five thin entries and needs no process outside the CLI. The cost is the blind spot that DEC-42 defers to gate-evidence.
- **Tradeoff point.** Pi and OpenCode fail closed. A broken install cannot let a human field through. In exchange, every guarded edit fails until the guard script is back, also the edits that set no human field.

### QS-26: the registers

- **Approach.** Each `minor` finding is one register file with a status (ADR-0034). A fix sets `resolved` and keeps the file.
- **Non-risk.** Two reviews add two paths, and two fixes change two files, so git merges them without a conflict and without `.gitattributes`. A fix on one branch and a raise of the same finding on another branch give a modify/delete conflict, which git reports and does not resolve silently. Assumptions: `next-id` hands out every ID once, and no step writes a register file under an ID that a finding file already holds. `finding-lint` checks the second assumption (DEC-53).
- **Tradeoff point.** One file per finding removes the lost-fix fault of the deleted line. A reader no longer sees the register of a class as one file. ADR-0034 records that trade at +2 against 0.

### QS-27: the git check of in_use

- **Approach.** `finding-lint` compares the line identities from `git blame -M -C --porcelain` with `dev`, `main`, their remote branches, each release tag, and the installed copy. The check runs only for a code, runtime, or security finding that `HEAD` does not hold, or whose basis or artifact changed (DEC-43, DEC-46).
- **Risk (ATAM-0020, `minor`, register).** At a merge commit, `HEAD` is the first parent. So a register file or a finding file that the other branch brings in counts as new. Feature A records a `minor` code finding with `in_use: false` and merges into `dev`. When feature B merges `dev`, the lines of that finding exist unchanged on `dev`, and the lint rejects an answer that was correct. This happens at the `pre-merge-commit` stage or at a merge that ends with `git commit` after a conflict. The fix: a file counts as new only when no parent holds it.
- **Sensitivity point.** Each due check runs `git blame` on up to five branches, each release tag, and the installed copy, plus a `git diff -M -C` per place. This repository has ten git tags today. The cost grows with the tags that `release_tag_patterns` matches, and it falls at every commit that adds a code finding.
- **Tradeoff point.** The Factory sets no release-tag default (DEC-48). So no project gets a guessed setting. In exchange, the first commit of a code, runtime, or security finding fails in every project until someone writes `docs/factory-settings.yaml`. An agent that writes `release_tag_patterns: []` only to pass the lint turns off the release-tag part of the check, and no rule refuses that.

### Cross-feature dependencies and the migration

- **Note.** 5.12 and ADR-0034 hand the new count of `next-id --plan-seed` to the counter-ids-fitting stories. Those stories are done: ST-0376 has `status: done` and counts the `id` fields of `.jsonl` lines. The gaps file `finding-classification-gaps.md` gives the change to the planner and orders it before the migration commit. 6.20 names only `docs/factory-settings.yaml` as a precondition of the migration. The exposure is low, because an unseeded project gets no ID from `next-id`, so it has no register files to miss. The architecture agent can name the planner as owner and add the order to 6.20.
- **Non-risk.** The guard-only OpenCode plugin builds on ADR-0019 through `execute.before` and keeps fail-closed behavior, as QS-7 asks. Assumption: the OpenCode CLI feature extends `agent-factory.ts` and keeps the guard, as the gaps file states.

### Notes on the documents

These items demand no change to the design. Each one leaves a reader with a wrong or incomplete picture, so the architecture agent may correct the text.

- **The blind spot of the guard is wider than QS-25 says.** The QS-25 measure calls a field name built from pieces in a script "the one known pass". The same text check also passes a `cp` of a prepared file into a guarded path, a script written outside the guarded paths and then run, and `git checkout <ref> -- <file>`. DEC-42 defers the whole class, "an agent that hides the field name". So the measure should name the class, not one example.
- **The installer change for four CLIs is not in the model.** The DSL shows `init-factory` only for the OpenCode link. The feature scenario "The installer registers the guard in every supported CLI" also needs `init-factory` and `update-factory` to write the entries for Claude Code, Codex, Copilot CLI, and Pi. Today `init-factory` writes `step-guard` entries for `Read`, `Edit`, `Write`, and `Bash` only, so `MultiEdit` and `NotebookEdit` are new. A relationship from `init-factory` to the four guard entries would show this.
- **The schema path differs between chapters.** The 5.1 table and the DSL container Finding Schemas name `packages/factory/rulebooks/schemas/`. Chapter 7 names `.agent-factory/factory/rulebooks/schemas/`, and BR-090 writes the `packages/` path into the `schema-validate` command. A consumer project has no `packages/factory/`. The Core List row already says "under the Factory root", and the schema rows can use the same words.
- **The Migration Agent is a component without a definition.** It runs once and is the role of a session, not an agent definition. It could appear only as a participant of `FindingMigration`, so the Factory Agents container lists only definitions that exist.
- **The YAGNI pass found no other excess.** The Main Checkout Locator and `schema-validate` exist already. The five guard entries are five real hook configurations, and each needs its own test.

## Risk summary

| ID        | Risk                                                                                                       | Scenario | Severity | Mitigation                                                                                                                                                           |
| --------- | ---------------------------------------------------------------------------------------------------------- | -------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ATAM-0018 | The patch rule holds only in Codex, and the OpenCode tools are not named.                                  | QS-25    | major    | Make the patch rule part of the shared guard rule; name the OpenCode tools and check them against the targeted release.                                              |
| ATAM-0019 | A committed lowering ends a stop where the pre-commit hook lacks `finding-lint`.                           | QS-24    | major    | Define the hook entry with `trade_off: none` and `availability: always` and the update path, or record the gap in 8.19 and QS-24; add a committed lowering to QS-24. |
| ATAM-0020 | At a merge commit, the git check treats files from the other parent as new and rejects a correct `in_use`. | QS-27    | minor    | Count a file as new only when no parent of the commit holds it.                                                                                                      |

Risk theme: enforcement outside the reviewed path. All three risks concern a path that the main flow does not take: a patch call in a CLI other than Codex, a commit without the hook, and a merge commit.

## Tradeoff summary

| Tradeoff                                 | Gains                                                       | Costs                                                                                        |
| ---------------------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Text check of each call (DEC-42)         | One script behind five entries; no process outside the CLI. | An agent that hides the field name gets past the guard.                                      |
| Fail closed in Pi and OpenCode (DEC-61)  | A broken install lets no human field through.               | Every guarded edit fails until the guard script is back.                                     |
| One register file per finding (ADR-0034) | No lost fix after a merge; no merge driver.                 | A reader no longer sees a register as one file.                                              |
| No release-tag default (DEC-48)          | No project runs the check with a guessed setting.           | The first code finding commit fails until the project writes the file; `[]` passes silently. |
| Stop in two scripts (DEC-28)             | The stop needs no change to the Pi tools or to `trigger`.   | Sessions still start during a stop; only merges are refused.                                 |

## Pass 2

Pass 2 checked only the fix commit `809df5ac` against ATAM-0018, ATAM-0019, and the notes of pass 1. The fix of ATAM-0018 holds. The fix of ATAM-0019 leaves the hook out of every new project, so ATAM-0019 is open again and blocks planning. Next, the architecture agent sets `availability: always` for `agent_factory_hook-finding-lint` in the places that name the entry: 5.12, chapter 7, 8.19, QS-24, the `finding-lint` contract, and the DSL.

### Checks run

`.agent-factory/factory/scripts/arch-lint --docs-dir docs/arc42` found 0 errors, 1 warning, and 0 info, and exited 0. The warning is the `ARCH-PARSE` warning of pass 1, dismissed for the same reason. `.agent-factory/factory/scripts/structurizr validate` exited 0. The commit adds no dependency rule, so the rules check has no mismatch.

### Verdict per pass-1 finding

| ID        | Verdict  | Reason                                                                                                                                                                                                                                                                      |
| --------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ATAM-0018 | resolved | The patch rule is part of the shared guard rule in every place. The OpenCode tools `edit`, `write`, `patch`, `shell`, and `execute` match `opencode.ai/docs/tools`, read on 2026-11-07.                                                                                     |
| ATAM-0019 | open     | The entry has `availability: requires-path:docs/findings`. `hook-subset generate` leaves an unavailable hook out, and a new project has no `docs/findings/` at fitting time. So a new project runs without `finding-lint` until an `update-factory` that its user confirms. |
| ATAM-0020 | open     | Out of scope for this pass, as the brief states. It stays in `docs/findings/register/architecture.jsonl`.                                                                                                                                                                   |

### ATAM-0019: the hook does not reach a new project

The architecture now names the hook id, the metadata entry, and the update path, as the finding asked. One value differs from the finding: the entry has `availability: requires-path:docs/findings`, not `availability: always`. The code of `hook-subset` decides availability by the path at fitting time and leaves an unavailable hook out of the generated config. During fitting step 3, a new project has no `docs/findings/`, because no review has run yet.

So in a new project, the first `critical` finding arrives without the hook. An agent can lower it with a matching basis and commit, and the stop ends. QS-24 lists two accepted residual cases: a user who bypasses the hook, and a user who answers no to the update. This third case is not among them, and the stakeholder has not accepted it. The text "fitting includes it without asking" in 5.12, chapter 7, 8.19, QS-24, and the `finding-lint` contract is wrong for such a project.

The fix is one value. With `availability: always`, the `files: ^docs/findings/` filter of the hook keeps the lint idle until the folder exists. The rating stays `major`. QS-24 has priority 1, so importance is `high`, and no code is built yet, so `in_use` is false.

This review did not settle one point in the fitting text. `init-factory` writes the full factory block into a project without a `.pre-commit-config.yaml`. Step 3 of the Virgil fitting then builds the filtered set, but it does not say clearly that the filtered set replaces that block. In both readings, the architecture claims an inclusion that `hook-subset` does not make.

### Contradictions with the rest of the architecture

The fix agrees with ADR-0034 to ADR-0036, 6.17 to 6.21, chapter 7, 8.19, QS-24 to QS-27, the DSL, BR-092, and the guard and `finding-lint` contracts, apart from the availability value above. This review checked these claims of the fix against the code:

- `update-factory` re-splices the full `agent_factory_hook-*` block with `merge-precommit-config --update`. It asks first, and it writes without asking after the layout migration (`refresh_precommit_hooks` in `packages/factory/scripts/update-factory`).
- `update-factory` runs the `init-factory` of the new release, so the guard entries reach an earlier install.
- `block-dangerous-git.sh` denies every git call that carries the flag that skips hooks.
- `hook-metadata.yaml` knows the values `trade_off: none` and `availability: requires-path:<path>`. Fitting includes a `none` hook without asking when the hook is available.

The fix also handles three notes of pass 1. The blind spot now names the class of hidden field names. The DSL has the relationships from `init-factory` to the four guard entries. 6.20 orders the cross-feature `next-id --plan-seed` story before the migration commit. The schema path in chapter 7 belongs to the BR-090 work of the requirements agent, so this pass does not file it.

### Notes

- **The OpenCode tool `subagent` starts a session with its own tool calls.** This review assumes that each such call fires `execute.before` in the same plugin, so the guard sees it. The OpenCode CLI feature can check that assumption with test FC-18-LN-03.

### Counts

| Severity | Count | Items                            |
| -------- | ----- | -------------------------------- |
| critical | 0     |                                  |
| major    | 1     | ATAM-0019, reopened              |
| minor    | 0 new | ATAM-0020 stays open from pass 1 |
| note     | 1     | The `subagent` assumption        |

This pass claimed no new ATAM number, because the open risk is ATAM-0019 itself.
