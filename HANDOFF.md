# HANDOFF — Agent Factory, 2026-07-22

Terse by design (caveman). Exact names/paths/SHAs kept. Git-ignored (local handoff, not versioned).

## ⬆ UPDATE 2026-07-22 — retro improvements MERGED to dev (supersedes stale sections below)

- **All retro action items implemented and MERGED to `dev`** (merge commit `f8ca1ab`): ST-0045 `commit-safe`, ST-0046 guardrail parser, ST-0047 verify-base marker enforcement, the `git-workflow` convention, and the official proposal format. `chore/retro-improvements` was squashed → rebased → merged clean. **448 tests pass**, index-lint/backlog-lint clean.
- **RESOLVED since the sections below were written:** the "rebase chore onto dev" step and ST-0047 are DONE; the remove-factory gap was already fixed on dev (FAGAN-0005).
- **Still open (operator):** push `dev` (~85 ahead of origin, unpushed); branch cleanup — `chore/retro-improvements` is now merged/deletable plus the 5 leftovers; `config/model.conf` skew (uncommitted drift, yours); `docs/proposals/implemented/codex-cli-support.md` (untracked, yours). See the (mostly still-accurate) "Environment gotchas" + "Open issues #3–6" below; ignore issues #1–2 (done).

______________________________________________________________________

## Local-first reminder

Read `.claude/INDEX.yaml` (or `.github/`/`.pi/` per your CLI). Prefer this repo's local skills/agents over any global copy. This repo IS the factory source — `factory/` is tracked source, NOT vendored. `config/model.conf` shows modified in the tree = the operator's intentional drift; do not revert it.

## Repo state

- **`dev` is the source of truth and has advanced far** — tip `8e418d6`, ~83 commits past `af81d0a`. Shipped: research playbook, token-usage-tracking (extended to Copilot/Codex/Pi capture, ST-0035..0044), plus a run of FAGAN QA fixes (Pi capture supervisor, native-capture fencing). `dev` == `main` were in sync earlier; re-check before pushing.
- **`chore/retro-improvements`** @ `d6c9499` (current checkout) — the retrospective process improvements. **Branched off the OLD `dev` (`af81d0a`); it is ~83 commits behind current `dev` and MUST be rebased before it can merge.**

## Retrospective — DONE this session

Report: `docs/reviews/retro-2026-07-21.md` (committed on `chore/retro-improvements`).

**Self-improvement (Claude Code memory, persists):** 5 feedback memories — git-command hygiene, verify-before-declaring, don't-revert-user-drift, deterministic-commit-after-hooks, large-dispatch spend discipline.

**Factory improvements (committed on `chore/retro-improvements`):**

- `fc8e896` — CLI-universal rules (read by every CLI via INDEX): new `factory/rulebooks/conventions/git-workflow.md` (lone git commands, premerge-check marker, blocked-ops safe forms, deterministic two-pass commit); `rules.md` Git-workflow + Proposals + verify-reports rules; `dispatch-contract.md`. Plus the **official proposal format**: `factory/rulebooks/templates/proposal.md`, wired into `feature-addition.md` + a factory-guide Proposals section. (No ADR — `write-adr`'s own gate says a process convention isn't ADR-worthy.)
- `f8a4202` — **ST-0046** guardrail parser hardening (`block-dangerous-git.sh`): isolate the merge segment (multi-line `cd`/`git merge` no longer parses `cd` as the branch); git-scope the `--no-verify` block (a `grep --no-verify` isn't blocked). Real blocking intact. Tests: `test_guardrail_parser.py`.
- `8b76ca4` — **ST-0045** `factory/scripts/commit-safe` two-pass commit helper (+ `test_commit_safe.py`), now dogfooded for every commit.
- `98d855f` — renumbered my stories from ST-0042/0044 (which collided with dev's token-tracking IDs) to **ST-0045/0046**.
- `d6c9499` — filed **ST-0047** (see below).

**Already handled elsewhere:** the remove-factory Stop/SubagentStop gap was fixed on `dev` by `f823f07 (FAGAN-0005)`.

## OPEN ISSUES — prepared for implementation

1. **ST-0047 — close the verify-base enforcement gap** (story on `chore/retro-improvements`, `backlog/ST-0047.md`, tier strong). The guardrail's worktree-commit check only tests marker *presence*, not that verify-base passed for the worktree's actual branch/base — a stale-base worktree can commit (retro: base `da899a9`). Reproduce-first; bind the marker to worktree identity; require the marker's base to be an *ancestor* of HEAD (not an exact head match, so TDD commits still pass). Coordinate with `factory/scripts/verify-base` (already writes `target=`/`expect_base=`/`head=`). **Held deliberately** — needs the careful pass, not a rushed guardrail change.

2. **Rebase `chore/retro-improvements` onto current `dev` (`8e418d6`), then merge.** Before merge: renumber-safe already done (ST-0045/0046/0047 are free of dev's ST-0042/0043/0044). Expect small conflicts in `rules.md`, `factory-guide.md`, `INDEX.yaml`, and possibly `block-dangerous-git.sh` (dev's QA may have touched the guardrail — diff before resolving). Regenerate `INDEX.yaml` after. Then `premerge-check dev chore/retro-improvements` + lone `git merge`.

3. **Pi `dispatch_wave` bugs** (from the live 2-agent test; memory `project_pi-invocation-layer.md`) — worktree factory-tracking gap + no per-child timeout. **Verify against current `dev` first** — the FAGAN/Pi-supervisor work may already cover them; file as BUG stories only if still open.

4. **`config/model.conf` skew** — `copilot.strong` vs `pi.strong`, no `claude.*` rows. Operator was reviewing; currently shows as uncommitted drift. Decide + commit or drop.

5. **Branch cleanup** — needs `git branch -D` (guardrail-blocked for the assistant; operator runs): `bug/pi-init-factory-prerebase-backup`, `feat/guardrail-in-init-factory`, `premerge-check-test-branch`, `worktree-agent-ad608c16459984868`, `doc/rewrite-documentation-ahistoric`. Plus `chore/retro-improvements` after it merges.

6. **Upstream report** — the Claude Code `isolation:"worktree"` provisioner cuts from a stale fixed base (seen `849481f`, `da899a9`); recurred across dispatches. Operator to report upstream.

## Environment gotchas

- Git as **lone commands** — no `cd …; git …` compound (guardrail mis-parses), and keep guardrail-trigger strings (`--no-verify`, `push --force`, `git merge <branch>`) OUT of shell commands incl. commit messages (they match inside the message). Use `factory/scripts/commit-safe -m "…" <paths>` for commits (handles the hook two-pass).
- `git merge <branch>` needs a `.agent-factory/premerge-check-ok` marker → run `premerge-check <target> <branch>` first, then merge lone.
- Guardrail blocks `git branch -D`, `git checkout .`, `--no-verify`, `core.hooksPath`, `git reset --hard`/`clean`/`push --force`; `rm -rf` via classifier. Use `git checkout HEAD -- <path>`.
- Tests: `uvx pytest orchestrator/tests/…` only.
- Org monthly **spend limit** killed dispatches repeatedly — salvage-and-resume (see memory `feedback-large-dispatch-spend-discipline`).
- Claude Code **worktree stale-base bug** — mandate `git rebase <invocation-branch>` as the developer's first command; `premerge-check` is the backstop.
- Story IDs are per-branch — an unmerged branch and `dev` can allocate the same ST number (this bit ST-0042/0044). Renumber to the next free after `dev`'s highest before merging.

## Memory

`~/.claude/projects/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/memory/` — `MEMORY.md` (index), `project_research-playbook-feature.md`, `project_token-usage-tracking-interview.md`, `project_pi-invocation-layer.md`, `project_retro-process-improvements.md`, and the 5 `feedback-*` memories.

## Immediate resume options

1. Implement **ST-0047** (verify-base gap) — the prepared, held story.
2. Rebase `chore/retro-improvements` onto `dev` and merge.
3. Verify + (if open) file the Pi `dispatch_wave` bugs; resolve `model.conf` skew.
