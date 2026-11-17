Adversarial review of /home/matthiasdaues/Documents/datenschoenheit/agent_factory/docs/proposals/run-lifecycle.md at commit bb71767817d75a4f8ad1fed7b8a3eabc3d3621a5. This is HEAD, and it is also the last commit that touched the proposal. I edited and wrote no files. The handoff skill asks for a file in the OS temp directory, but your constraint forbids writing files, so I skipped it. Result: 7 major, 9 minor, 3 note. Every major is a defect or risk, so the proposal is not ready for `accepted`.

## The eight checks

1. Completion criteria testable: **fail.** Findings 2, 6 and 7.
2. Scope boundary sharp: **fail.** Finding 5.
3. Design decomposable: **fail.** Findings 1, 3, 4 and 14.
4. Impact classification consistent: **pass.** `cross_component`, `architecture_change: true` and `external_contract_change: true` match the new commands and the new ledger.
5. Boundary references exist: **pass.** All 30 paths resolve at HEAD. Finding 16 lists boundaries that are missing.
6. Open questions genuine: **fail.** "None" hides open decisions. Findings 1 to 7 are those decisions, and FC-QG24 (the OpenCode plugin format is unchecked) is still open.
7. Motivation justifies timing: **pass.** I checked the numbers: 6 ledgers, 13 worktrees besides the primary checkout, and 36,109 files under `.current-work/`. No code ever sets `closed`.
8. Estimate plausible: **pass.** `unknown` is honest. Finding 18 adds a note.

## Findings

**1. major. The git guardrail and Guidance by hand.**

- **Defect:** The by-hand set refuses only four `dispatch` command texts. Every other route to the same step stays open to the agent.
  - The Always set allows `git merge <branch>` once a `premerge-check-ok` marker exists. The implementation agent runs `premerge-check` to show its output, and `premerge-check` writes that marker on a pass (`write_marker`, premerge-check:87).
  - The proposal moves three rules from every session into the orchestrated set: no branch creation without a worktree, worktrees only under `.current-work/`, and `verify-base-ok` for commits in a linked worktree. Today `block-dangerous-git.sh` applies all three always. A by-hand agent may then run `git checkout -b story/ST-0350` itself.
  - The ST-0214 check, which requires a ledger before a commit on a story branch, appears in no set.
  - The guardrail sees only shell commands. An agent can change `mode: by-hand` to `orchestrated` in the ledger with the Edit tool, and no guard covers the ledger.
  - The guard matches command text. `python3 .agent-factory/factory/scripts/dispatch merge-story` or `bash -c` may not match, which is the DEC-42 blind spot of guard-human-fields.
  - In an orchestrated run, the table names the human for `return-story` and for the merge into `dev`, but nothing refuses the agent either step.
- **Failure case:** In a by-hand run, the agent runs `dispatch merge-story ST-0350 --dry-run`. The check passes, and the agent then runs `git merge story/ST-0350`. The guardrail allows the merge. The sentence "the ledger shows that a person took each decision" is then false.
- **Severity:** major, because a planner who builds the table as written builds a gate that does not hold (`fails_purpose`).

**2. major. The git guardrail, and the five-tool completion criterion.**

- **Defect:** "The git guardrail" is not one implementation today.
  - pi runs its own TypeScript copy, `config/extensions/block-dangerous-git.ts`, and that copy already differs from the shell script. It reads only `docs/charter/testing.yaml`, while the shell script reads `docs/testing.yaml` first. It has no ST-0214 ledger check.
  - The OpenCode plugin `config/plugins/agent-factory.ts` holds only guard-human-fields. Its hook name `execute.before` and its call format were never run against a real OpenCode session; its own header cites FC-QG24. `init-factory` wires OpenCode only when the user names it (`DEFAULT_CLIS` leaves it out).
  - The proposal does not say where the mode-aware logic lives: in one script that every tool calls, as guard-human-fields does, or ported to each tool.
- **Failure case:** A story adds the by-hand set to `block-dangerous-git.sh`. Claude Code, Codex and Copilot refuse `dispatch merge-story`. pi allows it, because its TypeScript list was not changed. The OpenCode test passes against a mock, but the plugin never fires in OpenCode.
- **Note:** I did not run any of the five tools live. The Codex and Copilot hook wiring exists in `init-factory` and `hooks/block-dangerous-git.json`.
- **Severity:** major, because a planner must ask where the logic lives and how OpenCode is checked (`fails_purpose`).

**3. major. Two ways to drive it, Fix rounds and stops, Close, and The ledger.**

- **Defect:** The proposal does not map its lifecycle onto the existing ledger state machine or the existing subcommands.
  - `merge-story` requires `status: dispatched`. By hand, nobody runs `mark-dispatching` or `mark-dispatched`.
  - The proposal places none of these existing subcommands: `verify-story`, `mark-failed`, `mark-blocked`, `re-dispatch`, `escalate`, `mark-done` and `refresh-story`. `re-dispatch` already "returns story to prepared", and the proposal adds `return-story` beside it without saying how the two relate.
  - `VALID_TRANSITIONS` has no "returned" state. Both `premerge-check dev` and `dispatch close` must tell "returned" apart from "pending, never started".
  - `init` requires `--stories` and creates the feature branch in a worktree at `.current-work/<fb>/invocation`. The proposal does not say whether a by-hand run declares its stories at init, or whether it skips that worktree.
  - Today `init` refuses while any non-terminal ledger exists, which contradicts "several runs may be active at once". The proposal lists neither change.
- **Failure case:** By hand, `init` creates the invocation worktree. Later, `merge-story` tries to check out the feature branch in the primary checkout, and git refuses with "already checked out at .current-work/feature/login/invocation".
- **Severity:** major (`fails_purpose`).

**4. major. Checks at the merge (the feature merge), and The run, step 5.**

- **Defect:** `premerge-check dev` must find "blocking findings filed by those reports". No field links a finding file to its report. `source` names the skill, and a feature-level finding has an empty `story`.
- **Defect:** Feature findings are "fixed as stories of a new wave in the same run". The proposal names no author for those story files, and the ledger's story list is fixed at `init --stories`.
- **Failure case:** An open FAGAN finding from an unrelated review on `dev` blocks the feature merge, or a feature-level finding is missed. The planner cannot tell which result the design wants.
- **Severity:** major (`fails_purpose`).

**5. major. The gates, Fast gates as pre-commit hooks, and Scope.**

- **Defect:** Scope includes the security hook and the scanner gate at the merge. Both depend on "a scanner that `docs/testing.yaml` enables". The proposal defers the setup skill and defines no key, no command field and no default. `testing.yaml` has no scanner entry today.
- **Failure case:** A planner cuts the hook story and must invent `gates.security.*`. The deferred proposal may later define a different shape.
- **Severity:** major, because the In and Deferred lists do not partition this space (`fails_purpose`).

**6. major. Close (old runs), Design Details "The leftovers", and Completion Criteria.**

- **Defect:** Three of the six ledgers have no branch left: `brownfield-onboarding`, `core-artifact-layout` and `bug-hunt-fixes`. So `dispatch close` cannot check its precondition that the human merged the feature branch into `dev`.
  - All six ledgers carry `mode: automated` and `closed: false`, and the proposal defines no reading of those old values.
  - The nested ledger at `.current-work/feature/counter-ids-fitting/.current-work/feature/counter-ids-fitting/dispatch-ledger.yaml` is not where a lookup by branch finds it.
  - No completion criterion covers an old run.
- **Failure case:** Someone runs `dispatch close` for `feature/bug-hunt-fixes` and it refuses, because no branch exists to test for "merged". `--drop` does not fit either, since its 14 stories are `done`.
- **Severity:** major (`fails_purpose`).

**7. major. Terms, and the vocabulary completion criterion.**

- **Defect:** The criterion "No Factory document uses the terms…" has no boundary. 46 files under `packages/factory`, `docs/spec` and `docs/arc42` use the old terms. The proposal does not say whether these count:
  - accepted ADRs and superseded proposals;
  - file names, such as `docs/spec/areas/mechanized-dispatch.md`;
  - code identifiers, such as `invocation_branch`, `_main_checkout.py`, the mode value `"automated"` and the `"invocation branch"` error messages.
- **Failure case:** A planner cuts a story that rewrites accepted ADRs, or one that leaves `invocation_branch` in the ledger. Both readings meet the criterion as written.
- **Severity:** major (`fails_purpose`).

**8. minor. Motivation (fix rounds), and Fix rounds and stops.**

- **Defect:** The claim "ADR-0012 allows three, the implementation agent six" does not hold. ADR-0012 line 106 also allows six spawns with escalation. The real mismatches are elsewhere:
  - ADR-0012 marks such a story `blocked`, and the agent marks it `failed`.
  - The agent counts iteration 1, the original implementation, as one of the 3.
- **Defect:** `gates.fix_rounds: 3` leaves open whether the 3 counts the original implementation. It also leaves open whether escalation still needs the six evidence conditions of `dispatch escalate`.
- **Failure case:** The new code allows 3 fix attempts, where today the agent allows 2 per tier. The planner cannot tell whether that change is intended.
- **Severity:** minor (`raises_cost`: a source that does not hold).

**9. minor. Wave close (QA findings).**

- **Defect:** The proposal says that close-wave "sends each open QA finding to the test-strategy agent". Today the routing goes by owner (implementation-agent.md:137-141): a finding with `owner: planning-agent` waits for a story.
- **Defect:** The proposal also says a gate files a QA finding. In the code, the implementation agent files it.
- **Failure case:** The test-strategy agent receives a finding for a missing test that belongs to the planning agent.
- **Severity:** minor. "Documents that change" does not list this change, so a planner can keep the documented routing (`raises_cost`).

**10. minor. The gates.**

- **Defect:** The proposal says the story's `quality-gates` field "can add a gate". In `premerge-check`, `_picked_guardrails` lets the field replace the `testing.yaml` pick, and it accepts only `crap-score` and `mutation-testing`.
- **Failure case:** A story lists `quality-gates: [crap-score]` while `testing.yaml` enables mutation testing. Today mutation testing then does not run. The proposal reads as if it would.
- **Severity:** minor (`raises_cost`).

**11. minor. Documents that change (the copy into the installed folder).**

- **Defect:** `merge-story` copies `packages/factory` into `.agent-factory/factory` (dispatch:1954-1962). With several runs active, the guardrail and scripts of every session, including sessions on `dev`, become the code of the run that merged last.
- **Failure case:** Run A merges a story that breaks `block-dangerous-git.sh`, and run B's agents lose the guardrail.
- **Severity:** minor (`raises_cost`). This happens only in the factory repository itself.

**12. minor. Checks at the merge (the stash in the primary checkout).**

- **Defect:** By hand, `git stash push --include-untracked` sweeps the human's unrelated untracked files into the stash on every story merge. In this repository those are 15 paths, among them `poc/findings-board/` and three draft proposals. If `pop` fails, those files stay in the stash.
- **Severity:** minor (`raises_cost`).

**13. minor. Wave close.**

- **Defect:** "close-wave … has the implementation agent spawn the owner" gives a script an agent's action. The proposal does not say how many times the agent runs `close-wave`, or what the first run prints. By hand, it does not say who runs `close-wave` after each story.
- **Severity:** minor, because the existing ADR-0029 flow gives a workable reading (`raises_cost`).

**14. minor. Terms.**

- **Defect:** The glossary already uses "playbook run", in the In Use entry at `docs/spec/glossary.md:148`. The proposal's "run" is narrower, and `docs/spec/glossary.md` is not a boundary.
- **Severity:** minor (`raises_cost`: two terms for one concept).

**15. minor. Fast gates as pre-commit hooks.**

- **Defect:** `dependency-check` starts with `#!/usr/bin/env -S uv run --script`, so a consumer project without `uv` fails the hook.
- **Defect:** "When a commit stages a source file" is not defined, and the hook checks Python only.
- **Defect:** Today a missing DSL file exits non-zero. The proposal's skip is a change of behavior, and the proposal does not name it as one.
- **Severity:** minor (`raises_cost`).

**16. minor. impact.boundaries.**

- **Defect:** These boundaries are missing: `config/hooks/guard-human-fields`, `config/hooks/block-dangerous-git.json`, `docs/spec/glossary.md`, `docs/spec/state-machines.md`, `scripts/verify-base`, and the gate scripts that `premerge-check` will now run (`crap-score`, `mutation-testing`, `test-design-verify`).
- **Severity:** minor (`raises_cost`).

**17. note. Motivation.**

- The invented example, CRAP score 42 against a threshold of 30, disagrees with this project's threshold of 8 (disabled) in `docs/testing.yaml`.
- **Severity:** note.

**18. note. The estimate.**

- Every value is `unknown` on an `elevated` proposal that has 30 boundaries and touches five tools. One rough figure, or a split, would help: the guardrail per tool and the cleanup of old runs could each be a separate release.
- **Severity:** note.

**19. note. Core Principles ("Every piece of state has a reader").**

- After the change, the result files in `.current-work/<gate>/<story>.json` keep a reader only for `mutation-testing`. The gate scripts still write the others on every commit.
- **Severity:** note.

## Claims I checked and found true

- `merge-story` already sets `status: done` in the merge commit.
- `merge-story` already moves the branch back after a red test suite, with `reset --hard`.
- No code ever sets `closed`.
- OpenCode has no git guardrail today.
- Register files require `story`.
- report-format.md defines `story` and `branch_head`.
- `dependency-check` reads Python imports only.
- `!` commands in Claude Code run outside the tool hooks, as the guard-human-fields header states.

## Decisions for the author

These are my recommendations for the five largest questions.

1. **Where does the guardrail logic for each mode live?** Recommendation: one script that all five tools call, as guard-human-fields does. pi's TypeScript copy then becomes a thin wrapper. This settles finding 2.
2. **How does the agent fail to complete a person decision?** Recommendation: refuse by hand `git merge`, all branch creation, and edits to `.current-work/**/dispatch-ledger.yaml`. Also stop `premerge-check` from writing its marker unless `dispatch merge-story` called it. This settles finding 1.
3. **How is "returned" recorded?** Recommendation: add a ledger state `returned`, reachable from `failed` and `blocked`, and fold `re-dispatch` into `return-story`. This settles finding 3.
4. **Is the security scanner in or out of the first release?** Recommendation: defer the scanner hook and the scanner gate together with the setup proposal. This settles finding 5.
5. **What does the vocabulary criterion cover?** Recommendation: only the living documents under `packages/factory/` and `docs/spec/`. Leave ADRs, superseded proposals and code identifiers out. This settles finding 7.

Handoff: there are 7 open major findings. The author fixes each one, then re-opens the proposal for a second pass.
