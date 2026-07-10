# Fagan Review Report — 2026-07-10

## Scope

- Branch: `feature/integrate-orchestrator`, full range `e8a8565..0e8fda7`.
- Code-changes-only, per this pass's mandate (documentation-only commits are out of
  scope for the five standard focus areas, but see the YAGNI section below, which the
  user explicitly extended to cover process-doc and scaffolding additions).
- Files inspected:
  - `orchestrator/src/orchestrator/cli.py` — `_tooling_root()`, `_resolve_agents_dir()`,
    `_run_menu_mode()`'s inline fallback, `_handle_init()`'s `_COPY_DIRS` resolution,
    the two leftover "Agent HQ" string replacements (`ST-0065` commit `ce71932`,
    `RECON-0004` commit `cf9fd70`).
  - `factory/scripts/merge-precommit-config` — `extract_marker_id()`,
    `MARKER_HOOK_ID` removal, `HOOK_ID_LINE` regex (`RECON-0001` commit `6378652`).
  - `orchestrator/tests/test_merge_precommit_config.py` (new, same commit).
  - `.pre-commit-config.yaml` (root, de-symlinked and merged, `ST-0067`),
    `orchestrator/pre-commit-config.yaml` (`ST-0066`), `orchestrator/.pre-commit-config.yaml`
    (`RECON-0003` sync) — reviewed as executable configuration, not prose.
  - Excluded: the bulk `orchestrator/src/*` reinstatement (commit `6badd42`) — pre-existing
    code from `agent_hq`, not newly authored logic in this range, already subject to its
    own historical Fagan passes (`orchestrator/docs/findings/FAGAN-0001..0057`). Re-auditing
    ~7,800 lines of already-reviewed, unmodified-by-this-range source is out of scope for
    this pass and would duplicate that prior work.
- Known, already-accepted, out-of-scope items (not re-flagged): the 19 pre-existing
  `arch-lint` ADR-frontmatter errors, `ST-0059`/`ST-0061` backlog-lint warnings, root
  `docs/findings/RECON-0004.md` (deliberately left open), and `docs/adr/0010`'s
  outdated distribution model (tracked via `orchestrator/docs/spec/todos.md` T-41).

## Finding table

| Finding                                                                                                                                                                                                                                                                                                            | Artifact                                                   | Category | Severity |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------- | -------- | -------- |
| `extract_marker_id()` can silently pick up a hook id from a later, non-`repo: local` block if the local block itself has no `- id:` line before the next top-level `repo:` entry — a real latent bug in newly-introduced code, uncovered by the new test suite (which only exercises the single-block happy path). | `factory/scripts/merge-precommit-config#extract_marker_id` | Defect   | Minor    |

Filed as `docs/findings/FAGAN-0001.md`.

## Five focus areas

**1. Correctness.** The `cli.py` path fixes (`factory/agents`, `factory/skills`,
`factory/scripts`) are simple, mechanical, and verified by `orchestrator/tests/test_init.py`
(asserts `(root / "factory" / "agents").is_dir()` etc.) and the commit's own claimed
`33 failed → 0 failed` full-suite result. The `merge-precommit-config` fix correctly
solves the regression it targets (both directions are now covered by
`test_merge_precommit_config.py`), but introduces the boundary-condition bug above
(`FAGAN-0001`).

**2. Clean Architecture.** No layer-boundary changes in this range — the `cli.py` edits
are all within existing path-resolution helper functions, at the same architectural
level as before (CLI-adapter-layer path lookups, not touching `ports.py`/`entities.py`).
No new dependency-direction violations introduced.

**3. SOLID.** No new class hierarchies or abstractions introduced in this range's actual
code delta. `extract_marker_id()` is a small, single-purpose function extraction from
inline logic in `merge()` — a legitimate SRP improvement over the prior hardcoded
constant, not an over-abstraction.

**4. Maintainability.** The new `test_merge_precommit_config.py` suite (5 tests, both
splice directions) is clear and well-named, but has a coverage gap on
`extract_marker_id()`'s own boundary condition — see `FAGAN-0001`'s fix recommendation
for the missing test case. `_resolve_agents_dir()`'s docstring ("package-relative first,
then symlink in cwd") is stale against the now-real (non-symlinked) `factory/agents`
directory this fix resolves to — but this drift is part of the already-tracked
`ADR-0010`/`T-41` distribution-model cleanup, not newly introduced by this range's
edit (the docstring itself wasn't touched), so it is not re-flagged as a new finding.

**5. Consistency.** The `cli.py` fixes follow the existing codebase's established
pattern of degrade-not-crash path resolution (`try`/`except RuntimeError` around
`_tooling_root()`, `ValueError` on total failure) — consistent with the rest of the
file. `_resolve_agents_dir()`'s cwd-fallback branch now resolving `factory/agents`
even though `ADR-0010` describes that branch as a downstream project's own bare
`agents/` dir is a deliberate, already-documented judgment call (recorded in
`ST-0065`'s own Analysis section, with the regression-risk assessment "no existing
test exercises that branch directly") — checked and confirmed consistent with that
record, not re-flagged.

## YAGNI check

The user asked this pass to scrutinize four specific areas for speculative
generality or process theater, rather than treating YAGNI as an afterthought.
Findings below are stated plainly where the answer is "no violation" — no
speculative finding was manufactured to fill out the section.

**1. Root `docs/`/`backlog/` multi-context scaffolding — `docs/CONTEXT-MAP.md`'s
`factory_api/` stub.** Checked for any actual structure built ahead of need: a
repo-wide search found `factory_api/` referenced only in prose (`docs/CONTEXT-MAP.md`,
`README.md`'s directory-tree comment, `docs/adr/0001`, two backlog stories) — **no
directory, no code, no config entry exists for it anywhere**. `CONTEXT-MAP.md`'s own
wording ("a vision-stub only... No docs or code yet. Not scheduled for implementation")
is exactly the honest-placeholder framing YAGNI asks for, not scaffolding. **No
violation.**

**2. `orchestrator/.pre-commit-config.yaml` vs the template `orchestrator/pre-commit-config.yaml`
— is maintaining both still justified?** This exact question was already raised and
resolved earlier in this same range: `orchestrator/docs/findings/RECON-0003.md`
explicitly asked "decide and record whether this dev-only config should keep existing
at all... if it stays, its header comment should say what it is for that the root file
doesn't already cover" — and its fix commit (`12da219`) added precisely that
justification to the file's header: it lets a contributor run
`pre-commit run -c orchestrator/.pre-commit-config.yaml --all-files` to exercise
orchestrator-only gates in isolation, without the rest of the monorepo's hooks running
or needing their tools installed — a real, concrete, currently-usable capability the
merged root file cannot provide (the root file always runs every hook matching its
`files:` scope for whatever's staged, not an isolated orchestrator-only subset on
demand). Re-verified the justification holds and is not re-flagged as a duplicate.
**No violation — already resolved via `RECON-0003`.**

**3. The four process-improvement doc edits (`ST-0005`/`0006`/`0007`/`0008`) — process
theater or real?** All four trace to a concrete incident or immediate dogfooding within
this same range, not hypothetical future benefit:

- `ST-0005` (worktree isolation): motivated by `retro-2026-07-10.md`'s documented
  incident ("a subagent's first git command ran against the shared main checkout...
  chain-renaming the main branch through four story names") and echoes a *recurring*
  historical pattern already logged in `orchestrator/docs/reviews/retro-2026-07-08.md`
  (worktree base-ref issues recurring across `ST-0038`, `ST-0039`, `ST-0042`, `ST-0046`,
  `ST-0049`, `ST-0059`) — a real, repeat-offending failure mode, not speculative.
- `ST-0006` (backlog-story destination for retro action items): immediately dogfooded
  in this exact range — `ST-0005`..`ST-0008` themselves exist as backlog stories
  precisely because this option was added to the retro's tracking menu.
- `ST-0007` (multi-context checklist): derived directly from this range's own friction
  (the root `docs/`/`backlog/` split happened in separate follow-up rounds, per
  `retro-2026-07-10.md`); backports the lesson for next time, standard retro→skill
  feedback loop, not built ahead of any observed need.
- `ST-0008` (directory-tracking pre-flight): motivated by the same `retro-2026-07-10.md`
  incident as `ST-0005` — the dispatcher had to discover `orchestrator/` and root
  `backlog/` were untracked mid-dispatch and improvise a baseline commit; this codifies
  checking that up front.
  All four are small, targeted edits (a sentence or a short new subsection each), not new
  mechanisms, frameworks, or configurability. **No violation.**

**4. `merge-precommit-config`'s `RECON-0001` fix — proportionate, or speculative
generality beyond the one bug?** The fix (`extract_marker_id()`) replaces a hardcoded
`MARKER_HOOK_ID` constant with a same-shaped, single small function — no new CLI flags,
no configurability, no plugin mechanism. Verified the script has a real, current
consumer beyond hypothetical future subprojects: `factory/scripts/init-factory` invokes
`merge-precommit-config` today for the original factory-into-project direction. The bug
this fix addresses is real and already-manifesting risk, not purely `factory_api`-shaped
speculation: root `.pre-commit-config.yaml` already contains `id: index-lint` (from the
existing factory-into-project splice) *and* now also the orchestrator hooks (added by
hand in `ST-0067`, per that story's own Analysis section, precisely because the
unfixed script would have silently no-op'd); the next time anyone runs this script in
the subproject-into-root direction against this same file, the old hardcoded check would
have wrongly reported "already merged." **No violation** — the generality added is
exactly what the discovered bug required, no more.

## Done-check

- [x] Review covers all changed files in scope (code-changes-only, per this pass's
  mandate; bulk pre-existing reinstatement explicitly and reasonably excluded)
- [x] Findings are categorised (Defect / Suggestion / Question) — one Defect (Minor)
- [x] The Defect is actionable — states what's wrong and what to do
- [x] Spec compliance explicitly checked (Correctness section, against `ST-0065`'s
  and `RECON-0001`'s own acceptance criteria and test coverage)
- [x] YAGNI given equal weight to the five standard areas, per explicit user
  instruction — four specific areas investigated, one real gap already resolved
  by a prior pass in this same range, three confirmed load-bearing/honest, zero
  speculative findings manufactured
