# Todo

## T-0001 — openwebui.ts: API key typed as slash-command argument

- status: resolved
- source: fagan-review (docs/reviews/fagan-review-2026-08-19-openwebui.md), answered 2026-08-19 (repeat pass)

`/register <name> <baseUrl> [apiKey]` takes the key as a typed command argument (openwebui.ts:347–367, external target). Author-absent question: confirm the typed command line containing the key is excluded from pi's session transcripts and command history. If it is persisted anywhere, key entry should move to a prompt-based flow. Resolve by checking pi's session persistence or asking the author.

**Resolution:** answered by the author on the 2026-08-19 repeat pass. The positional `apiKey` is now optional; omitting it prompts via `ctx.ui.input()` (verified to exist, `dist/core/extensions/types.d.ts:74`), with a headless guard (`!ctx.hasUI` → usage error). The header recommends the prompt path. The positional form remains available as an accepted risk; its transcript exposure inside pi was not independently confirmed.

## T-0002 — openwebui.ts: re-register drops the selected model

- status: resolved
- source: fagan-review (docs/reviews/fagan-review-2026-08-19-openwebui.md), answered 2026-08-19 (repeat pass)

`/register` unregisters the provider, re-discovers, and re-registers (openwebui.ts:281–283, external target). Author-absent question: what is the intended behavior when the session's currently selected model disappears from the new model list? Resolve by confirming pi's behavior on provider model-list shrink (graceful fallback vs. stuck selection) and documenting it in the extension header.

**Resolution:** answered by the author on the 2026-08-19 repeat pass. `/register` now checks `ctx.model` after re-registration and warns when the currently selected model is no longer offered: "pick a new one with /model". The behavior is documented in the extension header.

## T-0003 — Mechanized dispatch: cancellation semantics during a running step

- status: resolved
- source: root-cause cross-reference (RC-1 from [root-cause-2026-08-21-implementation-baseline-failures.md](../../reviews/root-cause-2026-08-21-implementation-baseline-failures.md))

The step manifest and guard design in [mechanized-dispatch.md](../areas/mechanized-dispatch.md) assumes a clean agent lifecycle (manifest written, agent runs, manifest removed). Agent death without cleanup is covered (`dispatch clear-manifest --force`), but signal and cancellation semantics during a running step — what happens if the parent dispatcher is killed, the user sends SIGINT, or the subagent times out mid-write — are not specified. The QA strategy has no cancellation test for dispatch subcommands.

**Action:** specify cancellation semantics in the dispatch spec and add at least one cancellation scenario to the QA strategy's integration layer.

**Resolution:** addressed by adding the Interruption Safety cross-cutting invariant to the spec. Every dispatch subcommand must either complete atomically or leave the ledger in a state that Subcommand Idempotency can resume from. Abort signals are explicitly optional — callers may omit them, callees must not assume they exist. Six scenarios cover pre-write interruption, partial-write resumption, merge-story interruption, omitted signal, active signal, and pre-aborted signal. The QA strategy adds six integration tests in `tests/test_dispatch_interruption_integration.py`.

## T-0004 — Mechanized dispatch: "validators must not mutate" not stated as invariant

- status: resolved
- source: root-cause cross-reference (RC-4 from [root-cause-2026-08-21-implementation-baseline-failures.md](../../reviews/root-cause-2026-08-21-implementation-baseline-failures.md))

The spec's `dispatch verify-story` uses `git cat-file -e` and `git branch --contains` (both non-mutating), and `dispatch merge-story` runs `premerge-check` (also non-mutating). The principle "validators must not mutate working-tree or index state" is implicit but not stated as a cross-cutting invariant. An implementer could reasonably add a checkout or reset inside a verification command.

**Action:** state the invariant explicitly in the spec's cross-cutting concerns or guard specification.

**Resolution:** addressed by adding the Verification Immutability cross-cutting invariant to the spec. Dispatch subcommands that verify state must not modify the working tree, index, or HEAD. Four scenarios cover verify-story index immutability, verify-story working-tree immutability, premerge-check staging prohibition, and escalation-check state immutability. The QA strategy adds four integration tests in `tests/test_dispatch_immutability_integration.py`.

## T-0005 — Mechanized dispatch: spawn-success verification before mark-dispatched

- status: resolved
- source: root-cause cross-reference (RC-6 from [root-cause-2026-08-21-implementation-baseline-failures.md](../../reviews/root-cause-2026-08-21-implementation-baseline-failures.md))

`dispatch mark-dispatched` assumes the subagent has been spawned when called, but the spec does not specify how the dispatcher confirms that spawning succeeded. If the subagent process fails to start (resource exhaustion, bad config, model unavailable), the story enters DISPATCHED with no running agent.

**Action:** specify a spawn-verification precondition for `mark-dispatched` — at minimum, confirm the subagent process ID or tool-call acknowledgment exists before marking.

**Resolution:** addressed by adding the DISPATCHING intermediate state to the story lifecycle. `mark-dispatching` records intent to spawn (PREPARED → DISPATCHING). `mark-dispatched` requires the story to be in DISPATCHING state and the subagent spawn to have returned an acknowledgment (DISPATCHING → DISPATCHED). Spawn failure from DISPATCHING transitions to FAILED via `mark-failed --class environment`.

## T-0006 — Harmonize the canonical ERD location across scenarios

- status: resolved
- source: discussion of [PROP-09](../../proposals/cycle-based-orchestration.md#review--2026-09-14) (proposal superseded)

Multiple scenarios reference `docs/spec/entity-model.md` as a canonical
artifact, while the [brownfield onboarding procedure](../../../.agent-factory/factory/playbooks/brownfield-onboarding.md#step-33--extract-entity-model)
produces `docs/spec/entity-model.md` only during its optional
second stage. All scenarios must use the same canonical ERD location.

**Action:** choose one project-wide ERD path, update every scenario, template,
gate, and cross-reference to use it, and define how existing ERDs at legacy paths
are discovered or migrated.

**Resolution:** the stakeholder selected LinkML on 2026-09-14. The canonical
source is `docs/spec/entity-model.yaml`. `docs/spec/entity-model.md` and
`docs/assets/images/entity-model.svg` are derived projections. Migration of
live scenarios, templates, and legacy paths is pending. Structured
JSON payloads are LinkML value-object classes validated by generated Pydantic
models and persisted in JSON or JSONB columns.

**Note (2026-10-29):** the LinkML choice is an assumption until the
[data-model DSL PoC](../../../poc/data_model_from_dsl/proposal-data-model-dsl-technical-poc.md)
ends with a Pugh Matrix and an ADR confirms it (DEC-01 there). No migration
work starts before then.

**Revision (2026-10-30):** [ADR-0024](../../adr/0024-dbml-as-entity-model-language.md)
replaces LinkML with DBML. The canonical source is `docs/spec/entity-model.dbml`;
`entity-model.md` is retired: its prose moves into DBML notes, its diagrams
into rendered SVGs. Payload schemas live in `docs/spec/schemas/`. Details are
in the proposal [entity-model-as-dbml.md](../../proposals/entity-model-as-dbml.md).

## T-0007 — Choose a validatable state-machine language

- status: open
- source: grilling of [entity-model-as-dbml.md](../../proposals/entity-model-as-dbml.md) (DEC-04 there)

`state-machines.md` holds a home-grown pseudocode. `statemachine-lint` checks
only that the derived Mermaid diagram matches it. Nothing checks whether a
machine is sound: unreachable states, dead ends, or transitions to undeclared
states. The entity model had the same gap before ADR-0024.

**Action:** run a survey of state-machine languages under the licence rule
(MIT, Apache-2.0, or similar; no paywalled features), then a technical PoC on
Gigacron's state machines, scored with the criteria of the `architecture.dsl`
pattern. Known candidates, unverified: SCXML, XState, Umple, P, TLA+/PlusCal.
A soundness check for the current pseudocode waits for this result.

## T-0008 — Merge `todo.md` and `todos.md`

- status: open
- source: [core-artifact-layout.md](../../proposals/core-artifact-layout.md) (DEC-09 there)

The factory keeps two todo lists with two ID schemes: `todo.md` (`T-0001`…)
and `todos.md` (`T-01`…). Agents and skills refer to both names.

**Action:** merge them into one list with one ID scheme, and update every
reference to a renumbered entry.

## T-0009 — Dispatch briefs must not use `git stash`

- status: open
- source: implementation of `core-artifact-layout`, wave 1 (2026-11-02)

All linked worktrees share one stash list. A developer brief told agents to
set work aside with `git stash`, and the entries of ST-0325 and ST-0335
collided. The merged result still passed, but only by luck.

**Action:** remove `git stash` from the developer brief template and the
dispatch contract, prescribe a temporary WIP commit instead, and add a
`step-guard` or guardrail check that blocks bare `git stash` inside a story
worktree.

## T-0010 — scope-lint reports 77 findings on this repository

- status: open
- source: implementation of `core-artifact-layout`, ST-0343 (2026-11-02)

After the migration, `scope-lint` reports 77 errors on the tracked files of
this repository. 66 backlog stories and 8 proposals have no `scope` field in
their frontmatter. Three files declare a scope that names no workstream under
`.agent-factory/workstreams/`: `usage-data-recovery` once and
`value-first-onboarding-journey` twice, in its proposal and its feature file.
CAL-14-IT-01 therefore only checks that no new finding appears.

**Action:** add a scope to every story and proposal, register or correct the
unknown scope values, and then bring scope-lint to zero findings and restore
the plain exit-0 check in CAL-14-IT-01.

## T-0011 — The usage backup of `init-factory` copies instead of moving

- status: open
- source: ST-0343, the factory's own update (2026-11-02)

Before a reinstall, `init-factory` copies `.agent-factory/usage/` and
`.agent-factory/user-changes/` with `shutil.copytree` into a temporary folder
under `/tmp` (`PRESERVE_DIRS`, `packages/factory/scripts/init-factory` around
line 529). In this repository, `usage/` holds 22 GB. The copy filled the disk
(`Errno 28`), and the update rolled back. The backup folders are also never
removed: 125 `af-preserve-usage-*` folders had piled up in `/tmp`.

**Action:** move the preserved folders with a rename when the backup folder is
on the same file system, and copy only across file systems; remove the backup
after a successful update and after a rollback; add a test for each case.

## T-0012 — Usage transcripts grow without a limit

- status: open
- source: ST-0343, the factory's own update (2026-11-02)

`.agent-factory/usage/transcripts/` holds 21 GB in this repository. Nothing
rotates, compresses, or prunes the transcripts, so every update and backup
carries them along.

**Action:** define a retention rule for transcripts (for example, by age or by
total size), decide which derived records must survive a prune, and implement
the rule with a test.

## T-0013 — `duplicate_terms` misses duplicates between sections with the same heading

- status: open
- source: [IMPL-0003](../../findings/IMPL-0003.md), code re-review of `core-artifact-layout` (2026-11-03)

`migrate-spec-layout` counts glossary sections by their heading text. When two
`CONTEXT.md` files share a `###` subheading, the glossary gets two sections
with the same heading, and a term in both gets no `duplicate term:` line. No
data is lost, and the run exits 0.

**Action:** count sections by position in `duplicate_terms`, or name
subheading sections after their context (for example `Billing: Orders`), and
add a test.

## T-0014 — `dispatch` has no command that closes a dispatch

- status: open
- source: closing the `core-artifact-layout` dispatch (2026-11-03)

The Close section of `dispatch-contract.md` and the implementation-agent
definition give the dispatch script the cleanup duty: check that every story
is terminal, run `git worktree prune`, remove the worktrees and delete the
branches of merged stories, keep blocked ones, and save the ledger. The script
has no command for it; `close-wave` only records the wave. After the
`core-artifact-layout` dispatch, five worktrees and seven merged branches were
left and had to be removed by hand.

**Action:** add `dispatch close [--abandon --reason <text>]`. A completed
close refuses while a story is not terminal, removes merged worktrees with
`git worktree remove` and their branches with `git branch -d`, keeps blocked
ones, prunes, and records the close in the ledger. An abandoned close records
the reason and force-removes the dispatch's worktrees and branches. Add a test
per case, and point the Close section and the implementation-agent at the
command.

## T-0015 — arc42 has no chapters 01 to 04 and 11

- status: open
- source: architecture pass of `core-artifact-ownership` (2026-11-03)

`docs/arc42/` holds chapters 05 to 10 and 12. Introduction and goals,
constraints, context and scope, solution strategy, and risks and technical
debt are missing. So a reader of the architecture finds no stated goals and
no overview before the building blocks.

**Action:** create chapters 01 to 04 and 11 in a separate architecture pass,
derived from `architecture.dsl` and the accepted proposals.

## T-0016 — No rule decides which review findings must be fixed

- status: open
- source: [review-scrapbook.md](../../../poc/workflow/review-scrapbook.md) BAD-04, and [manual-mode-gates.md](../../proposals/manual-mode-gates.md) DEC-06 (2026-11-03)

Every review loop files each finding and loops back until none is open. No
loop has a threshold below which a finding is recorded and left unfixed. So
late passes spend tokens on edge cases that an earlier fix created, and
`story-gates` in manual mode blocks on every open finding.

**Action:** two proposals answer this item.
[finding-classification.md](../../proposals/finding-classification.md) defines
which finding blocks: a computed severity, a register for `minor` findings, and
a human override. [review-loop-cap.md](../../proposals/review-loop-cap.md)
applies that rule to every review loop and stops each loop after three passes.
Set this item to `resolved` when both proposals are `accepted`.

## T-0017 — The guardrail hook misses a push with git options before the subcommand

- status: open
- source: [counter-ids.md](../../proposals/counter-ids.md) PROP-09 and DEC-22 (2026-11-05)
- traces: `packages/factory/config/hooks/block-dangerous-git.sh`

`block-dangerous-git.sh` matches the literal text `git push`. A command with a
git option between `git` and the subcommand passes it: fed
`git -C . push origin abc123:refs/ids/counters`, the hook exits `0`, and fed
the same command without `-C .`, it exits `2`. `git --work-tree=. push` passes
too. The other blocked commands are caught with options in front: the hook
exits `2` for `reset --hard` after `-c x=y` and for `clean -fd` after
`--git-dir=.git`. So an agent can push although the hook is meant to stop it.

**Action:** let the hook skip git's global options before it checks for
`push`, and add a test per option.

## T-0018 — Three feature files do not parse as Gherkin

- status: open
- source: [spec-review-2026-11-05-counter-ids.md](../../reviews/spec-review-2026-11-05-counter-ids.md) and SPEC-0039 (2026-11-05)

`mdformat` treats a `.feature` file as Markdown. It wraps Rules in code
fences and escapes each `#` as `\#`, and then a Gherkin parser no longer sees
the Rules. These files have code fences today:

- `docs/spec/features/agent-context.feature`
- `docs/spec/features/opencode-cli-integration.feature`
- `docs/spec/features/local-usage-processing-and-analysis.feature`

**Action:** restore valid Gherkin in the three files. Make `derive-feature`
and every skill that formats its outputs name only `.md` files for `mdformat`.

## T-0019 — The test suite renders the diagrams into the repository

- status: open
- source: the counter-ids implementation run, ST-0369, ST-0375, and BUG-0115 (2026-11-06)

`test_CAL_14_gate_passes_on_the_factory_repository[arch-lint]` in
`tests/factory/test_core_layout_gates.py` runs `arch-lint` on the real
repository without `--no-validate`. `arch-lint` then starts the Structurizr
container and runs `export-all`, which rewrites about 30 SVG files in
`docs/assets/images/`. The test carries no `container` marker, so it runs in
every commit's `run-tests` hook. Three agents that committed at once ran up to
six containers beside six suites with `-n auto`, and the machine nearly
stalled. Each agent then had to restore the SVG files by hand.

**Action:** run `arch-lint` with `--no-validate` in the default suite. The
container test `test_CAL_14_structurizr_validate_passes_on_the_factory_repository`
already covers `structurizr validate`. Cap the agents' test runs, so that
parallel story agents do not each run the suite twice per commit.

Done: `15ca486a` and `00e05229` give `arch-lint` `--no-validate` in the CAL-14
test and in the characterization check. A full run in a story worktree, also
with `GIT_INDEX_FILE` set, now leaves the SVG files unchanged. Still open: during
the first commit attempts of ST-0370 and ST-0374, a hook run rewrote the SVG
files again, and the cause is not found. The `arch-lint` hook stages every
SVG file with `git add docs/assets/images/*.svg`, and an agent's `git add -A`
then carried 29 of them into the ST-0374 commit. `premerge-check` blocked that
merge. Story briefs now forbid `git add -A`.

Cause found on 2026-11-06: `arch-lint` exports every diagram when
`architecture.dsl` is newer than the newest SVG, and `--no-validate` does not
stop that. A merge or checkout that touches the DSL gives it a fresh mtime, so
every later run of the two default-suite callers and of the commit hook
rendered all diagrams in a container. `62beeb74` adds `--no-export`, used by
both test callers; the post-merge suite of ST-0376 then left every SVG
unchanged and took 80 s. Open: only the cap on parallel test runs.

## T-0020 — A claim can still open a credential dialog through `GIT_ASKPASS`

- status: open
- source: [security-review-2026-11-06-counter-ids.md](../../reviews/security-review-2026-11-06-counter-ids.md) (2026-11-06)

BR-076 says a claim runs git without a prompt. `next-id` sets
`GIT_TERMINAL_PROMPT=0` and ssh's `BatchMode`, but git still calls the program
in `GIT_ASKPASS` or `core.askPass`. In a VS Code terminal, that program opens a
credential dialog. Turning askpass off would also break CI jobs that pass their
token through an askpass script.

**Action:** decide whether a claim unsets `GIT_ASKPASS` and `core.askPass`, and
how a CI job then passes its token. Record the answer in BR-076.

## T-0021 — An agent can read a token in a remote URL with ordinary commands

- status: open
- source: SEC-0007 and the stakeholder's rule of 2026-11-06: an agent must never see a token in the clear

`next-id` and `init-factory` redact the user info of every URL they print
(SEC-0007). A token stored in `.git/config` stays readable for an agent all the
same: `git remote -v`, `git remote get-url`, `git config --list`, or
`cat .git/config` print it. `init-factory` warns about such a URL, but nothing
stops an agent from reading it.

**Action:** decide how the guardrail hook blocks the common commands that
print remote URLs, and say in `rules.md` that credentials belong in a
credential helper, never in a remote URL. A hook cannot catch every way to
read a file, so the rule carries the main weight.

## T-0402 — The CRAP and mutation gates are installed but cannot run

- status: open
- source: stakeholder question after the counter-ids `update-factory` run (2026-11-06)

`crap-score` and `mutation-testing` are installed and current, but both are
`enabled: false` in `docs/testing.yaml`, and new stories carry
`quality-gates: []`. Neither gate could run usefully today:

- `crap-score` needs `coverage.json`. `coverage` is not installed and no test
  run writes the file, so every function counts as 0 % covered.
- `mutation-testing` runs `gates.mutation_testing.command`, which does not
  exist, and the project has no mutation tool.

**Action:** the `test-strategy-agent` and the stakeholder decide the test
regime. Add `pytest-cov` and a step that writes `coverage.json`, then enable
`crap_score`. Pick a mutation tool, such as `mutmut` or `cosmic-ray`, write its
command and time limit into `docs/testing.yaml`, and pick the gate per story
through `quality-gates` for stories with risky logic.

## T-0403 — `test_st_0365_slow_command_is_stopped_with_its_child_and_blocks_the_merge` fails at random

- status: open
- source: the first commit attempt of ST-0376 (2026-11-06)

The test raised `FileNotFoundError` on `/proc/<pid>/stat`: the child process it
watches had already exited when it read the file. A second run passed. A
flaky test aborts an agent's commit and costs one full suite run each time.

**Action:** make the test tolerate a process that exits between the lookup
and the read, for example by treating a missing `/proc/<pid>/stat` as "gone".
