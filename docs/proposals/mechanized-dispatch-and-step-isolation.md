---
schema_version: 2
title: Mechanized Dispatch and Step Isolation
status: accepted
owner: md@matthiasdaues.de
created: 2026-08-21
updated: 2026-08-26
supersedes:
  - docs/proposals/mechanize-dispatch-orchestration.md
  - docs/proposals/artifact-pipeline-discipline.md
  - docs/proposals/cost-aware-agent-delegation.md

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - factory/scripts/dispatch
    - factory/scripts/step-guard
    - factory/agents/implementation-agent.md
    - factory/agents/developer-agent.md
    - factory/agents/planning-agent.md
    - factory/rulebooks/rules.md
    - factory/rulebooks/conventions/dispatch-contract.md
    - factory/rulebooks/conventions/branching-policy.md
    - factory/rulebooks/templates/story.md
    - factory/scripts/backlog-lint
    - factory/scripts/premerge-check
    - factory/scripts/verify-base
    - factory/scripts/init-factory
    - factory/skills/create-backlog/SKILL.md
    - factory/docs/factory-guide.md
    - config/project.json
    - config/model.conf
    - .claude/settings.json
    - .codex/hooks.json
    - .github/hooks/
    - .pi/extensions/
    - .gitignore

governance:
  assurance: high
  risk_domains:
    - compatibility
    - reliability
    - operations

estimate:
  as_of: 2026-08-21
  basis: judgment
  confidence: low
  human_review_hours:
    min: 6.0
    max: 14.0
  normalized_tokens:
    min: 40000
    max: 80000
  estimated_consumption:
    min: 600000
    max: 1600000
    overhead_multiplier: 20
    playbook: feature-addition
---

# Feature Request: Mechanized Dispatch and Step Isolation

## Summary

Move deterministic orchestration work — git state management, file-access
enforcement, tier selection, prompt composition, and failure handling — into
scripts and hooks. The LLM sequences script calls; the scripts own state
transitions and validate each step. Three implementation phases build on each
other: (1) a dispatch script that owns the full story lifecycle,
(2) per-step file-access guards enforced by hooks, and (3) a tier-aware
delegation procedure with evidence-gated escalation.

## Motivation

The 2026-08-17 bausteinsicht feature-addition and the 2026-08-18 charter
dispatch exposed a shared failure pattern: the Factory assigns deterministic
orchestration work to a probabilistic executor and catches mistakes too late.

**Context blowup.** Phase 1 consumed 1.08M tokens against a 40–80k estimate.
Serial grilling, review-fix-review loops, and stale agents all grew context
monotonically because nothing mechanically caps what a step agent may read.

**Branch contamination.** ST-0078's worktree accumulated commits from three
other stories. `premerge-check` caught it at merge time — after the full
subagent budget was spent — because `verify-base` was an instruction the agent
ignored.

**Silent rework.** The dispatcher sent a two-line prompt, the subagent lacked
context, the run failed, and a human retried with a stronger model instead of
a better handoff. No recorded failure class, no escalation predicate, no
evidence trail.

The Factory's foundational principle already separates these concerns: "agents
create artifacts; mechanically triggered gates run scripts that validate."
The dispatch and step-execution workflows have not applied this principle to
themselves.

## Core Principles

- Agents create artifacts; scripts own state. The LLM never runs branch,
  worktree, merge, or ledger commands directly during a dispatch.
- Gates run before work, not after. Verify-base, context guards, and tier
  checks all fire before a subagent is spawned.
- File-access enforcement is layered: deterministic for `Read`/`Edit`/`Write`
  tool calls, best-effort for `Bash`, hard-capped by input-size guard at spawn.
  The bound targets project artifacts, not Factory machinery.
- Missing context is a handoff defect, not a capability defect. Five of
  seven failure classes (context_missing, contract_violation, environment,
  spend_death, seam_defect) are handoff or environment defects and never
  raise the model tier. Only `acceptance_unmet` and
  `contradictory_evidence` may escalate — they are proxies for a possible
  capability gap, not proof of one. The escalation is a bounded bet:
  one tier, once, with evidence.
- One manifest per working directory, one agent per manifest, one escalation
  per story, one escalation per wave.

## Working Directory: `.current_work/`

All ephemeral dispatch state lives under `.current_work/`, gitignored in its
entirety. This directory is runtime state — never committed, never shared
across clones.

All dispatch state is namespaced by feature branch, with per-story
subdirectories:

```
.current_work/
  <feature-branch>/
    dispatch-ledger.yaml
    <story-branch>/
      current-step.yml
```

Each `dispatch init` creates a namespace keyed by the feature branch name. Two
concurrent feature-addition runs on different feature branches write to
separate subdirectories — no locking, no collision, no merge conflict on the
ledger.

`dispatch status` without arguments detects the current feature branch and
reads the matching ledger. With `--all`, it lists every active dispatch.

The durable record is git itself: branches, merges, story-file status fields,
and commit messages. The ledger is a convenient index that `dispatch` maintains
for its own bookkeeping. If lost (crashed session, deleted `.current_work/`),
the script can reconstruct terminal states from the branch and merge history;
non-terminal states require re-preparation.

`dispatch close-wave` and the final merge clean up the namespace directory.
`.current_work/` is added to `.gitignore` by `init-factory`.

## Design

### Phase 1 — Dispatch script

A single `factory/scripts/dispatch` script (Python, stdlib only) with
subcommands covering the full story lifecycle. Each subcommand is atomic and
idempotent: it does its work, updates the ledger, and writes any durable
state changes to git.

#### Subcommands

**`dispatch plan --backlog-dir backlog [--stories ST-0074,...]`**
Read stories, build the dependency graph, compute file-overlap sets, output a
wave plan as YAML. Includes wave assignments, parallel-safe sets, serial
chains, model tier per story, and a suggested tier from the rubric (Phase 3).
No state changes.

**`dispatch init --base <branch> --stories ST-0074,... [--feature-branch <name>]`**
Create the feature branch from `--base` and initialize the dispatch ledger at
`.current_work/<feature-branch>/dispatch-ledger.yaml`. Preflight
`test_command` in `config/project.json`. Exit non-zero on untracked target
directories unless `--baseline-commit` is given (creates an explicit baseline
commit on the base branch before the feature branch is cut; because this
mutates a potentially shared branch, the script prints the base branch name
and requires `--yes` or interactive confirmation before committing).
With `--feature-branch`: skip branch creation and initialize the ledger on
the named existing branch. The branch must exist and its tip must be
reachable from `--base`. If a dispatch ledger already exists for this
branch under `.current_work/`, initialization is rejected — the operator
must close or remove the existing dispatch first. `--baseline-commit` is
incompatible with `--feature-branch`.

**`dispatch prepare-wave <N>`**
Verify all stories in waves < N are terminal (mechanical wave gate). For each
story being prepared: create story branch and worktree off the feature branch,
verify the mapping with `git worktree list --porcelain`, run
`factory/scripts/verify-base <feature-branch> --expect-base <sha>`, write
the step manifest (Phase 2), and record `prepared` in the ledger. Parallel-safe
stories and serial-chain heads are prepared from the feature branch tip;
chain links stay `pending`.

**`dispatch prepare-story <story-id>`**
Lazily prepare one serial-chain link after its predecessor merges. Same
sequence as `prepare-wave` but cut from the predecessor's merge commit.

**`dispatch mark-dispatched <story-id>`**
Update ledger from `prepared` to `dispatched` after the LLM spawns the
subagent.

**`dispatch verify-story <story-id> --sha <sha>`**
SHA verification: `git cat-file -e`, `git branch --contains`. Update ledger.
`premerge-check` is deliberately not here — it runs inside `merge-story`,
paired with its own merge.

**`dispatch merge-story <story-id> [--dry-run]`**
In the feature-branch worktree: run
`premerge-check --scope-glob <output-glob>` (scopes derived from the story's
`outputs`), immediately merge, update story status to `done` in the merge
commit, run the test suite (`test_command` from `config/project.json`), clean
up worktree and branch. On merge conflict: `git merge --abort`, mark blocked.
On red suite: revert the merge commit, restore the feature branch to its
pre-merge state, mark `blocked` with `post-merge test failure`, exit non-zero.
With `--dry-run`: run `premerge-check` and report its result without merging,
modifying the ledger, or cleaning up. Exit zero if the merge would proceed,
non-zero if `premerge-check` fails.

**`dispatch mark-blocked <story-id> --reason <text>`**
Record a blocking condition (human decision, free text).

**`dispatch mark-failed <story-id> --class <class> --evidence <path>`**
Record a classified failure. `--class` accepts only the seven-value vocabulary
(see [Phase 3](#phase-3--tier-aware-delegation)). `--evidence` requires a
tracked artifact path.

**`dispatch re-dispatch <story-id>`**
Return a `failed` or `blocked` story to `prepared` state for a new attempt.
Creates a new attempt entry, re-prepares the branch and worktree from the
current feature-branch tip, and runs verify-base. Phase 1 behavior: any
`failed` or `blocked` story may be re-dispatched. Phase 3 adds class-aware
constraints: `acceptance_unmet` and `contradictory_evidence` require prior
escalation via `dispatch escalate`; `contract_violation` is terminal after
two occurrences.

**`dispatch close-wave <N>`**
Verify all stories in wave N are terminal. Append closeout record. Commit.

**`dispatch status`**
Print the current ledger as a human-readable table.

**`dispatch clear-manifest --force --worktree <path>`**
Remove a stale step manifest left by a crashed agent. Logs a warning and
records the recovery in the ledger. Requires `--force` to prevent accidental
removal of an active manifest.

#### Ledger status lifecycle

`pending → prepared → dispatched → done | blocked | failed`

Additional transitions:

- `prepared → failed` (spawn failure)
- `prepared → blocked` (operator blocks before dispatch)
- `failed → prepared` (re-dispatch)
- `blocked → prepared` (re-dispatch after resolution)

`prepared` means branch and worktree exist, verify-base passed, but no
subagent has been spawned yet.

#### Implementation-agent changes

The [implementation-agent](../../factory/agents/implementation-agent.md)
workflow is rewritten to call dispatch subcommands instead of performing git
operations directly. The agent's remaining job is: review the plan, spawn
subagents, and call script subcommands in sequence.

### Phase 2 — Step isolation

Each playbook step runs as a cold-start agent that reads only declared inputs
and writes only declared outputs. A step manifest and hooks enforce the
boundary.

#### Step manifest

`prepare-wave` and `prepare-story` write a YAML manifest at
`.current_work/<feature-branch>/<story-branch>/current-step.yml`.
The manifest is local runtime state inside the gitignored `.current_work/`
tree, never committed.

```yaml
schema_version: 1
step: derive-use-cases
playbook: feature-addition
phase: 1

inputs:
  - docs/spec/prd-architecture-modeling.md
  - docs/spec/actor-goal-list.md

outputs:
  - docs/spec/use_cases/UC-*.md

max_input_tokens: 40000
```

The manifest's existence is the activation signal: when it exists, guards
apply; when it does not (between steps), tool calls are unrestricted.
`prepare-wave` writes it; after the agent completes the orchestrator removes
it. A manifest already present blocks the next write (no-supersede).

#### Enforcement hooks

A single shared script `factory/scripts/step-guard` accepts the tool event as
JSON and a guard type (`read`, `write`, `bash`, `context`). CLI-specific
adapters normalize tool input before calling it, following the pattern of
[`block-dangerous-git.sh`](../../factory/config/hooks/block-dangerous-git.sh).

**Read guard** (`PreToolUse` on `Read`): file path must match a declared
`inputs` glob or an always-allowed prefix. Always-allowed: `factory/`,
`.claude/`, `.github/`, `.pi/`, `.codex/`, `.current_work/`.

**Write guard** (`PreToolUse` on `Edit`, `Write`): file path must match a
declared `outputs` glob. Always-allowed writes: `.current_work/`,
`docs/findings/*`.

**Bash guard** (`PreToolUse` on `Bash`): best-effort path extraction from
common read/write commands (`cat`, `rg`, `grep`, `>`, `>>`, `tee`). Shell
syntax is Turing-complete; this catches common patterns, not all patterns.

**Context guard** (pre-spawn): sum input file sizes (bytes ÷ 4), compare
against `max_input_tokens`. Deny spawn if exceeded.

Glob semantics: gitignore-style (`**` = recursive). One shared matching
implementation in `step-guard` used by both the guard and the resolver.

#### CLI wiring

| CLI         | Hook config             | Adapter      |
| ----------- | ----------------------- | ------------ |
| Claude Code | `.claude/settings.json` | Shell (jq)   |
| Codex       | `.codex/hooks.json`     | Shell (jq)   |
| Copilot CLI | `.github/hooks/`        | JSON + shell |
| Pi          | `.pi/extensions/`       | TypeScript   |

#### Playbook step declarations

Playbooks gain an optional `steps:` block declaring each step's inputs,
outputs, and context cap. The `dispatch` script reads these when writing the
manifest for non-dispatch steps. For dispatch steps, the story's `outputs`
and `tests` fields serve the same purpose.

### Phase 3 — Tier-aware delegation

Three mechanisms that extend `dispatch` with tier selection, prompt
composition, and failure handling. The mechanisms are tier-aware with
retrospective measurement — they select and enforce model tiers, they do
not set or enforce per-story token budgets or cost caps. Cost reduction
is an expected outcome of correct tier assignment, not a direct input to
routing decisions.

#### Tier rubric

`dispatch plan` computes a suggested tier per story from frontmatter fields.
Stories gain one optional field:

```yaml
risk_domains: [security]   # optional; closed enum, validated by backlog-lint
```

| Condition (first match wins)                                                                                            | Suggested tier |
| ----------------------------------------------------------------------------------------------------------------------- | -------------- |
| `risk_domains` includes `security`, `privacy`, or `data_integrity`; or `outputs` matches a `safety_critical_paths` glob | `strong`       |
| `outputs` spans 2+ top-level directories, or `deps` has 3+ entries                                                      | `standard`     |
| `tests` non-empty and `outputs` within one top-level directory                                                          | `economy`      |
| otherwise                                                                                                               | `standard`     |

`safety_critical_paths` is a list of gitignore-style globs in
`config/project.json` (e.g., `["factory/scripts/*", "factory/config/hooks/*"]`). An empty or absent list means the path-match
rule never fires.

Mismatch disposition: a `strong` suggestion against a lower declared tier
blocks `dispatch init`. Every other mismatch warns. Both are resolved with
the user and recorded in the ledger.

#### Subagent handoff contract

`prepare-wave` and `prepare-story` generate the full subagent prompt — seven
parts:

1. **Outcome** — story ID, title, path to acceptance criteria (referenced, not
   inlined)
2. **Workspace** — worktree path, story branch
3. **Allowed writes** — story `outputs` globs, verbatim
4. **Forbidden actions** — merge, push, branch creation, ledger writes, hook
   bypass
5. **Required checks** — `test_command` from `config/project.json`
6. **Stop conditions** — ambiguous criterion, missing input, needed write
   outside `outputs`, suspect test
7. **Return envelope** — `status`, `commit_sha`, `files_changed`, `checks`,
   `blockers`, `failure_class`

Three existing prompt clauses are removed (substitutive, not additive):
`verify-base` preamble (now pre-spawn), sub-agent addressing clause
(inapplicable to developer-agents), and the workflow restatement (duplicates
the agent definition). Budget: 800 normalized tokens, enforced by the script.

#### Evidence-gated escalation

`dispatch mark-failed` accepts a closed failure-class vocabulary:

| Class                    | Disposition                                        |
| ------------------------ | -------------------------------------------------- |
| `context_missing`        | Re-dispatch, same tier, handoff amended            |
| `contract_violation`     | Re-dispatch, same tier; second occurrence terminal |
| `environment`            | Fix environment, re-dispatch, same tier            |
| `spend_death`            | Re-dispatch, same tier                             |
| `seam_defect`            | Re-dispatch seam session, same tier                |
| `acceptance_unmet`       | Escalate one tier                                  |
| `contradictory_evidence` | Escalate one tier                                  |

`dispatch escalate <story-id>` succeeds only when: exactly one prior `impl`
attempt failed, the class is `acceptance_unmet` or `contradictory_evidence`,
verify-base passed, no scope violation, not already `strong`, and no other
story in the same wave has already escalated in this dispatch. One escalation
per story, ever. The wave escalation slot resets at wave boundaries — a
story marked `blocked` with `wave_escalation_exhausted` in wave N may
escalate in wave N+1 if the slot is free and the story's own one-escalation
limit has not been consumed.

The ledger gains an `attempts` list per story: `session` (`seam`|`impl`),
`tier`, `failure_class`, `evidence`, `commit_sha`, `normalized_total`.

#### Seams-then-implement split

Stories gain one optional field:

```yaml
strategy: direct | seams-first   # default: direct
```

`seams-first` runs two sessions: a seam session (declared tier) writes only
test files, then an implementation session (one tier lower, floored at
`economy`) makes them pass. Escalation counts `impl` attempts only — the
seam session has no independent escalation budget. A `seam_defect` failure
returns to the seam session at the same tier without consuming the story's
one escalation slot. If the seam session fails repeatedly with
`seam_defect`, the story is blocked for human decision, not escalated.

## Scope

**In the first release:**

Phase 1:

- `.current_work/` directory layout, added to `.gitignore` by `init-factory`
- `factory/scripts/dispatch` with subcommands: `plan`, `init`, `prepare-wave`,
  `prepare-story`, `mark-dispatched`, `verify-story`, `merge-story`,
  `mark-blocked`, `mark-failed`, `re-dispatch` (basic: any `failed` or
  `blocked` story, no class-aware constraints), `close-wave`, `status`
- `config/project.json`: `test_command` key
- [implementation-agent.md](../../factory/agents/implementation-agent.md)
  rewritten to call dispatch subcommands
- [dispatch-contract.md](../../factory/rulebooks/conventions/dispatch-contract.md)
  updated: `prepared` status, script-owned ledger under `.current_work/`,
  pre-spawn verify-base, `premerge-check --scope`
- [branching-policy.md](../../factory/rulebooks/conventions/branching-policy.md)
  updated: verify-base preamble notes script-owned path

Phase 2:

- `factory/scripts/step-guard` — shared enforcement for read, write, Bash,
  and context guards
- `dispatch clear-manifest --force --worktree <path>` for stale manifest
  recovery
- Step manifest schema and lifecycle integrated into `dispatch prepare-wave`
  and `dispatch prepare-story`
- CLI-specific hook wiring for all four CLIs
- [init-factory](../../factory/scripts/init-factory) installs step-guard
  wiring alongside existing hooks
- Step declarations for
  [feature-addition.md](../../factory/playbooks/feature-addition.md)
- [rules.md](../../factory/rulebooks/rules.md) updated with step-boundary rules
- Epic-0 spike verifying the Copilot CLI `pre_tool_use` event surface for
  `Read`/`Edit`/`Write` matchers

Phase 3:

- **Backlog migration:** existing stories without `risk_domains` or
  `strategy` fields must be annotated before `backlog-lint` validation is
  enabled. This is a rollout prerequisite — Phase 3 stories should include
  a migration task that adds defaults to existing backlogs.
- Tier rubric in `dispatch plan` and `dispatch init` (same code path),
  recorded in
  [dispatch-contract.md](../../factory/rulebooks/conventions/dispatch-contract.md),
  cited from [planning-agent.md](../../factory/agents/planning-agent.md)
- `config/project.json`: `safety_critical_paths` key (list of
  gitignore-style globs for the strong-tier path-match rule)
- `risk_domains` field on
  [story.md](../../factory/rulebooks/templates/story.md),
  validated by `backlog-lint`
- `strategy` field on
  [story.md](../../factory/rulebooks/templates/story.md),
  validated by `backlog-lint`; selection guidance: use `seams-first` when
  the story's acceptance criteria are expressible as test assertions and
  the implementation path is not obvious from the tests alone; use
  `direct` otherwise
- Class-aware constraints on `dispatch re-dispatch`: `acceptance_unmet` and
  `contradictory_evidence` require prior escalation;
  `contract_violation` terminal after two occurrences
- Seven-part handoff contract from `prepare-wave`/`prepare-story`, with
  800-token budget gate
- Failure-class vocabulary on `dispatch mark-failed`
- `dispatch escalate` with six-condition predicate
- Ledger `attempts` list
- A/B measurement on the first wave after landing

**Explicitly deferred (do NOT plan stories for these):**

- Step declarations for playbooks other than feature-addition
- Automated orchestrator that drives the playbook without human intervention
- Output format validation (schema-checking step output content)
- Token counting via the fixed tokenizer (context guard uses bytes ÷ 4;
  this underestimates tokens on non-ASCII text, so the guard is permissive
  — it may allow inputs that exceed the budget, never block inputs that
  fit; acceptable for ASCII-dominant codebases)
- Step-level cost reporting or dashboards
- Retry/resume logic within the dispatch script (automatic re-run of a
  failed subcommand from its interrupted point within the same attempt;
  distinct from `re-dispatch`, which starts a new attempt)
- CI/CD integration
- Parallelism within the dispatch script itself
- Migration of the research-orchestrator to use the dispatch script
- Automatic selection of `strategy` by the planner
- Tier rubric that reads story prose
- Inheriting `risk_domains` from proposals
- Escalation beyond one tier or second escalation per story
- Per-wave escalation budget in tokens
- Tier-aware behavior for dispatchers other than the implementation agent

## Design Details

**Idempotency.** Every dispatch subcommand is idempotent: re-running after
success is a no-op; re-running after failure resumes from recorded state.

**Script-generated commits.** Follow
[commit-conventions.md](../../factory/rulebooks/conventions/commit-conventions.md):
merge commits, status-correction commits, and baseline commits each have a
defined format. The ledger itself is not committed — it is ephemeral state
under `.current_work/`.

**Crash recovery.** A stale step manifest under `.current_work/` (agent died
without cleanup) blocks subsequent writes. `--clear --force` removes it with
a warning. A missing or corrupt ledger can be partially reconstructed from
git branch and merge history for terminal states (done, merged branches).
Non-terminal story states require re-preparation via `dispatch prepare-wave`
or `dispatch prepare-story`. If both the ledger and the feature branch are
lost (e.g., `.current_work/` deleted and branch reset), recovery is manual:
the operator must inspect `git reflog`, identify surviving story branches,
and re-initialize the dispatch.

**Wave escalation tracking.** The "no other story in this wave has already
escalated" predicate is evaluated by scanning all story entries in the wave
for `escalation_granted: true`. No separate wave-level counter — the
per-story flag is authoritative.

**Tier arithmetic.** `economy < standard < strong`. Escalation adds one;
seams-first implementation subtracts one, floored at `economy`. Saturation at
`strong` blocks further escalation.

**Evidence paths.** `--evidence` requires a tracked artifact path — a finding
file, committed test output, or story file section. Free text is not evidence.

**Prompt budget.** The 800-token figure covers the generated seven-part
contract only, not the agent definition or skills. The A/B result revises it.

**Risk vocabulary.** Story `risk_domains` reuses the six values from
[proposal.md](../../factory/rulebooks/templates/proposal.md) governance.
The terms match; the values are authored per story and never inherited from a
proposal.

**Ledger compatibility.** The `attempts` list is additive. A ledger from
before Phase 3 has no `attempts` key; `dispatch escalate` treats absence as
zero attempts and refuses to escalate.

**Abort signal.** Every dispatch subcommand accepts an optional abort signal
parameter. When the signal fires, the subcommand stops at the next safe
point (after a ledger write commits or before the next begins) and leaves
the ledger reflecting only completed work. When the signal is absent or not
provided, the subcommand runs to completion normally — callees never assume
the signal exists.

**Plan/init tier evaluation.** `dispatch plan` and `dispatch init` evaluate
the tier rubric through the same code path. `plan` is informational — it
shows the suggestion so the operator can review before committing.
`init` is authoritative — it gates on mismatches. If stories change between
`plan` and `init`, the `init` evaluation governs.

**Re-dispatch vs. retry.** Re-dispatch (`dispatch re-dispatch`) returns a
story to `prepared` and runs the full lifecycle again from branch
re-preparation. It is in scope. Retry/resume logic — automatically
re-running a failed subcommand from its interrupted point within the same
attempt — is deferred.

**Scripts validate, LLM sequences.** The dispatch script owns state
transitions and validates preconditions. The LLM (implementation-agent)
sequences the script calls: prepare, mark-dispatched, verify, merge. This
division is intentional for Phase 1 — a fully automated orchestrator that
drives the playbook without human intervention is explicitly deferred. The
current design reduces the LLM's role to sequencing validated steps rather
than performing both orchestration and validation.

## Open Questions

None remaining.

## Completion Criteria

### Phase 1

- `dispatch plan` produces a correct wave plan from stories with dependencies
  and file overlaps.
- `dispatch init` creates feature branch, worktree, and ledger atomically;
  exits non-zero on untracked target directories unless `--baseline-commit`.
- `dispatch init --feature-branch` initializes the ledger on an existing
  branch without creating a new one; exits non-zero if the branch does not
  exist or is unreachable from `--base`.
- `dispatch init` and `dispatch merge-story` exit non-zero when
  `config/project.json` lacks a usable `test_command`.
- `dispatch prepare-wave` exits non-zero when prior wave has non-terminal
  stories.
- `dispatch prepare-wave` runs `verify-base --expect-base` before spawning
  and exits non-zero on failure.
- `dispatch prepare-wave` verifies each branch-to-worktree mapping with
  `git worktree list --porcelain`.
- `dispatch prepare-wave` prepares only stories whose declared base exists;
  chain links stay `pending`.
- `dispatch prepare-story` exits non-zero unless the chain predecessor is
  `done`; cuts from the predecessor's merge commit with verify-base.
- `dispatch verify-story` catches missing SHA and wrong-branch failures.
- `dispatch merge-story` runs `premerge-check --scope` immediately before its
  own merge, in the feature-branch worktree.
- `dispatch merge-story` updates story status in the merge commit and runs the
  full test suite after.
- `dispatch merge-story` marks `blocked` and exits non-zero on red suite.
- `dispatch merge-story --dry-run` runs `premerge-check` and reports pass/fail
  without merging or modifying the ledger.
- `dispatch mark-blocked`/`mark-failed` close the lifecycle for non-done
  stories.
- `dispatch close-wave` exits non-zero when any story is non-terminal.
- The ledger is never written by the LLM directly.
- Every subcommand is idempotent.
- The implementation-agent workflow uses script subcommands, not raw git.
- A dispatch of 3+ stories across 2+ waves completes with clean ledger and no
  contamination.

### Phase 2

- Step manifest is written by `prepare-wave`/`prepare-story` and removed after
  agent completion.
- A step agent is blocked from reading project files outside declared inputs
  via `Read` (Factory machinery always allowed).
- A step agent is blocked (or warned) from writing outside declared outputs via
  `Edit`/`Write`.
- `Bash` tool calls are checked best-effort for path references outside
  declared scope.
- Spawn is denied when declared inputs exceed `max_input_tokens`.
- A manifest already present blocks the next write (no-supersede).
- Between steps (no manifest), tool calls are unrestricted.
- In linked worktrees, each resolves its own manifest independently (verified
  with two concurrent worktrees).
- Hidden-directory inputs matched identically by guard and resolver.
- All four CLIs wire the step guard into their `PreToolUse` surfaces.
- `init-factory` installs step-guard wiring alongside existing hooks.
- `feature-addition` has a complete `steps:` block.

### Phase 3

- `dispatch plan` reports a suggested tier and flags mismatches.
- `dispatch init` blocks on `strong` suggestion vs. lower declared tier; warns
  on every other mismatch.
- `backlog-lint` validates `risk_domains` and `strategy` against their enums.
- `risk_domains: [security]` draws `strong` regardless of `outputs`.
- The rubric is recorded in `dispatch-contract.md` and cited from
  `planning-agent.md` — one table, no copy.
- `prepare-wave`/`prepare-story` emit the seven-part contract; `verify-base`
  preamble, sub-agent addressing, and workflow restatement are removed.
- Generated prompt measures at most 800 normalized tokens.
- `mark-failed` rejects classes outside the vocabulary and invocations without
  `--evidence`.
- `dispatch escalate` exits non-zero when any of its six conditions fails
  (tested individually).
- No story reaches a second escalation; no wave reaches a second escalation.
- A `seam_defect` attempt does not consume the story's escalation.
- Ledger records `attempts` entries with `session`, `tier`, `failure_class`,
  `evidence`, `commit_sha`, `normalized_total`.
- `backlog-lint` rejects `seams-first` when test paths fall outside `outputs`.
- A `seams-first` story runs two sessions; the implementation session runs one
  tier below.
- First wave after landing records an A/B comparison:
  - **Hypothesis:** rubric-assigned tiers produce lower `normalized_total`
    per merged story and equal or fewer rework attempts than the pre-rubric
    baseline.
  - **Control:** the last three dispatches before Phase 3 landing, using
    human-assigned tiers.
  - **Minimum sample:** at least 8 merged stories under rubric-assigned
    tiers before drawing a conclusion.
  - **Decision trigger:** if rubric-assigned tiers show higher
    `normalized_total` or more rework than the control, revise the rubric
    rules before the next dispatch; if equal or better, the rubric stands.

## Guiding Rule

Agents create; scripts orchestrate. Spend reasoning where the decision is
genuinely hard, and spend nothing anywhere else.
