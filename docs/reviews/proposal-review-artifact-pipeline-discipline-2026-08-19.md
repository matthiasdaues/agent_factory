# Proposal Review — Artifact Pipeline Discipline

- **Date:** 2026-08-19
- **Reviewer role:** spec-review-agent (adapted — target is a proposal, not a
  Phase-1 spec; `spec-lint` does not apply, so the deterministic pass used the
  gates that do)
- **Reviewed artifact:** [artifact-pipeline-discipline.md](../proposals/superseded/artifact-pipeline-discipline.md)
  (status: `draft`)
- **Disposition (pass 1):** **fail** — 2 Critical, 3 Major, 5 Minor
- **Disposition (pass 2, 2026-08-19):** **pass** — all Critical and Major
  findings resolved; 2 new Minor findings, 2 Suggestions
- **Note:** findings are recorded inline below as one list, per reviewer's
  instruction, not as individual `docs/findings/SPEC-*.md` files. The author
  addresses this document directly.

## Pass 1 — Deterministic checks

| Check                   | Result                                                      |
| ----------------------- | ----------------------------------------------------------- |
| `link-check`            | Pass — all local links resolve                              |
| `mdformat --check`      | Fail — file not formatted (list renumbering: 2./3./4. → 1.) |
| Repo-claim verification | Mostly confirmed                                            |

Verified claims:

- `factory/config/hooks/block-dangerous-git.sh` exists and performs exactly the
  claimed jq normalization across Claude Code, Copilot CLI, and Codex.
- Pi extension block mechanism is real (`{block: true, reason}` in
  `.pi/extensions/block-dangerous-git.ts`).
- `SubagentStop` hooks are configured in `.claude/settings.json` and
  `.codex/hooks.json`.
- `.current-work/` is git-ignored, consistent with the manifest location.
- `factory/scripts/step-guard` and `factory/scripts/write-step-manifest` are
  correctly absent (new deliverables).

## Pass 2 — Findings

### 1. Critical — Bash bypass defeats the read and write guards

**What is wrong.** The guards hook only `Read`/`Edit`/`Write` tool calls. Any
step agent can read undeclared files via `bash cat`, `rg`, or `grep`, and
write outside its declared outputs via shell redirect. The project's own
precedent (`block-dangerous-git.sh`) guards the `Bash` matcher precisely
because that is the dangerous surface, and [AGENTS.md](../../AGENTS.md)
mandates `rg`/`bash` for hidden files. The Core Principle "an agent that tries
to read outside its declared inputs is blocked before the read executes" is
unachievable as designed.

**What to do.** Either extend `step-guard` to Bash calls (deny path references
outside declared inputs, or allowlist commands — acknowledging shell parsing
limits), or downgrade the claim: the read guard is best-effort and the real
bound is the context guard at spawn. Restate the Core Principle accordingly.

### 2. Critical — A single global manifest cannot represent concurrent step agents

**What is wrong.** `.current-work/current-step.yml` is one file, git-ignored,
in the main checkout. Phase 4 dispatches parallel waves via `dispatch_wave`,
each in its own git worktree — where a git-ignored manifest does not exist.
Two concurrent step agents in one checkout would overwrite each other's
manifest. Yet the Completion Criteria demand a `steps:` block "covering all
phases."

**What to do.** Use per-instance manifests
(e.g. `.current-work/steps/<instance-id>.yml`); the hook resolves its own
session's manifest; the orchestrator writes the manifest into each worktree at
spawn.

### 3. Major — The `role` exemption is self-contradictory across sessions

**What is wrong.** One shared manifest file is read by hooks in both the
orchestrating session and the step-agent session. While `role: step-agent`,
the orchestrator's own broad reads (it must "read broadly to assemble inputs
and validate outputs") are denied by its own hook process; while
`role: orchestrator`, the step agent is exempt too. Hooks cannot distinguish
sessions from a shared file.

**What to do.** Specify session-scoped activation: an environment variable, a
per-session marker, or a manifest path passed to the spawned agent. Describe
the exact write → spawn → switch sequence.

### 4. Major — `running_agents` bookkeeping is impossible as described

**What is wrong.** "The orchestrator appends the agent's instance ID to
`running_agents` on successful spawn" — but the spawn guard is a `PreToolUse`
hook that fires *before* the spawn; it cannot know the outcome. That requires
`PostToolUse`, which is absent from the current `.claude/settings.json` and
`.codex/hooks.json` and unmentioned in the proposal. Removal via
`SubagentStop` exists for Claude Code and Codex but is unverified for Copilot
CLI and Pi `run_agent`.

**What to do.** Add `PostToolUse` wiring per CLI, or move bookkeeping into
`write-step-manifest` / the orchestrator helper script, and verify the
completion-event surface on all four CLIs.

### 5. Major — Completion criterion contradicts Open Question 2

**What is wrong.** The criterion "blocked from reading files outside its
declared inputs (verified by test)" conflicts with runtime reality: skill
files (`factory/skills/*/SKILL.md`, `.pi/skills/*`) are read by every
skill-invoking agent (e.g. spec-review-agent reads `inspect-spec`), and are
neither always-allowed nor in the declared inputs of the example steps. The
first release either fails its own test or allows all of `factory/`, which the
proposal itself says "weakens the context bound."

**What to do.** Resolve before acceptance: always-allow `factory/skills/`,
`factory/agents/`, and invoked playbooks (harness-fetched prompt machinery),
and restate the context bound as covering *project* documentation, not factory
machinery.

### 6. Minor — mdformat gate fails

**What is wrong.** `factory/scripts/mdformat --check` rejects the proposal
(list numbering 2./3./4. is renumbered to 1.).

**What to do.** Run `factory/scripts/mdformat --number` on the file per
[rules.md § Markdown formatting](../../factory/rulebooks/rules.md).

### 7. Minor — Cross-reference rule violations

**What is wrong.** Prose cites `rules.md`, `dispatch-contract.md`,
`feature-addition.md`, `block-dangerous-git.sh`, and `factory-guide.md` as
code spans; [rules.md § Cross-references](../../factory/rulebooks/rules.md)
requires full markdown links anchored to a section.

**What to do.** Convert artifact references in prose to anchored markdown
links.

### 8. Minor — `impact.boundaries` incomplete

**What is wrong.** Scope names "Updated factory-guide.md" and "Updated
init-factory" but neither appears in `impact.boundaries`; the guide's real
path is `factory/docs/factory-guide.md`.

**What to do.** Add both tracked paths to `impact.boundaries`.

### 9. Minor — Glob semantics unspecified

**What is wrong.** The schema mixes `docs/spec/**/*.md` (recursive?) with
`UC-*.md` (single-level), and matching of not-yet-existing output files is
undefined.

**What to do.** Pin the glob flavor in the manifest schema (e.g.
gitignore-style or picomatch semantics) and state how new output paths match.

### 10. Minor — Copilot CLI hook surface unverified

**What is wrong.** The claims "custom-agent `pre_tool_use`" and
`.toolArgs.file_path` for Read/Edit on GitHub Copilot CLI are asserted but
unverified; the existing `.github/hooks/` wiring only shows a `bash` matcher.

**What to do.** Add an Epic-0 spike story verifying the Copilot CLI event
surface, or record it as an explicit assumption.

## What holds up

- The mechanization rationale is sound: the no-supersede guard turns an
  existing MUST NOT ([rules.md § Dispatch](../../factory/rulebooks/rules.md))
  into a deterministic gate — exactly the "agents create, gates validate"
  principle.
- Deferred scope is YAGNI-clean; the token-budget model is internally
  consistent; the self-estimate (15× overhead multiplier) applies the lesson
  the proposal teaches.
- Motivation figures are unverifiable but plausible and clearly framed as the
  triggering incident.

## Summary

The two Critical findings — the Bash bypass and the single-manifest conflict
with parallel waves — undermine the proposal's central claim of *mechanical*
context bounding, and both change the manifest schema and hook architecture.
Address them, plus the three Major findings, before the proposal moves from
`draft` to `open`.

______________________________________________________________________

# Pass 2 — Repeat review (2026-08-19)

Per
[review-loop-discipline.md](../../factory/rulebooks/conventions/review-loop-discipline.md):
deterministic gates re-run, each prior finding verified individually, and the
full proposal re-inspected fresh against the revised text.

## Deterministic gates (re-run)

| Check              | Result                                                                                                                              |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| `mdformat --check` | Pass                                                                                                                                |
| `link-check`       | **Fail** — 2 broken links: `../../factory/scripts/step-guard`, `../../factory/scripts/write-step-manifest` (files do not exist yet) |

## Verification of prior findings

| #   | Severity | Status                       | Evidence                                                                                                                                                                                                                                |
| --- | -------- | ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Critical | **Resolved**                 | New § "Bash guard (best-effort)" with honest limitation statement; Core Principles restated as layered enforcement (deterministic for tool calls, best-effort for shell, hard cap at spawn); completion criterion added for Bash checks |
| 2   | Critical | **Resolved**                 | Manifest resolved via `git rev-parse --show-toplevel`; "Worktree isolation" section; `--worktree <path>` flag; completion criterion "two concurrent worktrees"                                                                          |
| 3   | Major    | **Resolved**                 | `role` field removed; "Lifecycle-based scoping" — manifest existence is the activation signal; orchestrator operates between steps; completion criterion "no manifest → unrestricted"                                                   |
| 4   | Major    | **Resolved**                 | `running_agents` removed; no-supersede enforced by `write-step-manifest` refusing to overwrite; no `PostToolUse` needed                                                                                                                 |
| 5   | Major    | **Resolved**                 | Open Question 2 struck through and resolved: `factory/`, CLI directories, `.current-work/` always allowed; new Core Principle scopes the bound to project artifacts; completion criterion restated to "project files"                   |
| 6   | Minor    | **Resolved**                 | `mdformat --check` passes                                                                                                                                                                                                               |
| 7   | Minor    | **Resolved with regression** | Prose references converted to links — but two links point to not-yet-existing files and break `link-check` (see finding 11)                                                                                                             |
| 8   | Minor    | **Partially resolved**       | `factory/docs/factory-guide.md` and `factory/scripts/init-factory` added; `factory/scripts/write-step-manifest` still missing (see finding 12)                                                                                          |
| 9   | Minor    | **Resolved**                 | Glob-flavor question recorded in Open Questions with explicit requirement to pin one flavor and define `**` semantics                                                                                                                   |
| 10  | Minor    | **Resolved**                 | Epic-0 spike story for the Copilot CLI event surface added to Scope, recorded as an assumption until confirmed                                                                                                                          |

## New findings (fresh inspection)

### 11. Minor — Broken links to not-yet-existing scripts

**What is wrong.** The finding-7 fix converted the code-span references to
`factory/scripts/step-guard` and `factory/scripts/write-step-manifest` into
markdown links. Both files are future deliverables; `link-check` fails.

**What to do.** Revert these two references to code spans — the cross-reference
rule governs references to artifacts *in this repo*, and these do not exist
yet (the `impact.boundaries` frontmatter already lists them as tracked paths).
Alternatively ship stub scripts; code spans are simpler.

### 12. Minor — `write-step-manifest` missing from `impact.boundaries`

**What is wrong.** Scope and Design name `factory/scripts/write-step-manifest`
as a first-release deliverable, but `impact.boundaries` lists only
`factory/scripts/step-guard`.

**What to do.** Add `factory/scripts/write-step-manifest` to
`impact.boundaries`.

## Suggestions (non-blocking)

- **Crash recovery.** If a step agent dies without completing, the stale
  manifest blocks every subsequent `write-step-manifest` call in that working
  directory until a human runs `--clear`. One sentence of failure behavior
  (the template's optional "Design Details" section exists for exactly this)
  would save the first operator confusion.
- **No-supersede scope note.** The write-refusal guard blocks *any* second
  concurrent step in the same working directory, not just a same-role
  supersede — broader than the [rules.md § Dispatch](../../factory/rulebooks/rules.md#dispatch)
  MUST NOT it mechanizes. Simpler and safe; worth one sentence acknowledging
  the broader semantics.

## Observations

- Finding 9's glob-flavor question and the two remaining original Open
  Questions (`read_guard: warn`, `max_input_tokens` default) stay open. That
  is acceptable for `draft`, but per
  [rules.md § Proposals](../../factory/rulebooks/rules.md#proposals) the
  interview moving the proposal to `open` should be decision-complete — these
  three need answers before or during that interview.
- The layered-enforcement restatement (Core Principles) is the right call: it
  trades an unachievable absolute claim for an honest, verifiable one, and the
  context guard at spawn remains a true hard cap.

## Pass-2 disposition

**Pass.** No Critical or Major findings remain. Findings 11–12 are Minor and
can be fixed in minutes; the Suggestions are optional. The proposal is ready
for the decision-complete interview toward `open` once the two Minor findings
are addressed and the three Open Questions are answered.
