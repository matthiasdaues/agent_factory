# Feature Request — Pi Invocation Layer

**Status:** Input to the `feature-addition` playbook (Phase 1, Requirements)
**Scope:** Contained to the `factory/` subproject — a new CLI-dispatch surface,
not an overarching repository change. It extends the existing
[Factory Flow Control spec](../../../docs/spec/prd.md) (domain: `factory/` — the
state-machine harness, dispatch mechanism, and generated catalog); it does not
touch the `orchestrator/` subproject.
**Scope size:** Large — new runtime component, a new model-callable tool, a
model-configuration schema change, and at least one architecture decision.
**Branch:** `bug/pi-init-factory`

This brief seeds the `feature-addition` playbook. It states the problem, the
platform facts already researched (so downstream phases need not re-derive
them), a proposed solution as a starting point, and the questions requirements
and architecture must resolve. The proposed design is a recommendation, not a
settled contract.

## 1. Problem

Agent Factory supports three CLIs: Claude Code, GitHub Copilot CLI, and Pi. The
Pi scaffold already committed on this branch (`init-factory` writes `.pi/`,
symlinks the factory content, installs the guardrail extension, wires
orientation through the root `AGENTS.md`) makes Pi able to *find* the factory's
content. It does not make Pi able to *run* all of it.

The gap is uneven across the three kinds of content:

- **Skills** run natively. Pi has a first-class skills concept and
  auto-discovers `.pi/skills/<name>/SKILL.md` once project trust is granted,
  invoking them automatically or by `/skill:name`. The existing symlink is
  sufficient; the factory's `SKILL.md` frontmatter (`name`, `description`) is
  already Pi-compatible. No further work is required for skills beyond
  end-to-end validation.

- **Playbooks, `INDEX.yaml`, orientation** are read by the model because
  `AGENTS.md` instructs it to. This works today.

- **Agents do not run as designed.** Pi has no subagent concept. `.pi/agents/`
  is inert: Pi never discovers or spawns an agent from it. The `AGENTS.md` line
  that points the model at `.pi/agents/<name>.md` yields only in-context
  role-play — the model reads the file and acts it out in the *current*
  session. That destroys the two properties the factory's multi-agent design
  depends on:

  1. **Author/reviewer independence.** A reviewer agent must not see the
     author's reasoning; the value of the second pair of eyes is that it works
     from the artifact alone. One shared context cannot provide this.
  2. **Parallel dispatch.** The `implementation-agent` dispatcher fans work out
     to parallel `developer-agent` subagents, each isolated in its own git
     worktree. Pi offers no native mechanism for this.

The feature is the missing **invocation layer for agents under Pi**: the
mechanism that lets the model run a factory agent in a genuinely separate Pi
session, and — for the dispatcher — run several in parallel across worktrees.

## 2. Platform facts (Pi)

Primary source: the `earendil-works/pi` repository, package
`@earendil-works/pi-coding-agent`, docs under `packages/coding-agent/docs/`.
Pi version validated locally: **0.80.8**.

### What Pi has

- **Context files.** Pi auto-loads `AGENTS.md` (or `CLAUDE.md`) at global,
  parent-directory, and project-root scope, most-specific last
  (`docs/usage.md`). Disable with `--no-context-files` / `-nc`.
- **Skills.** First-class, following the Agent Skills standard. Discovered at
  `~/.pi/agent/skills/`, `.pi/skills/` (trust-gated), package `skills/` dirs,
  settings paths, and `--skill <path>`. Invoked automatically, by
  `/skill:name`, or by `--skill` (`docs/skills.md`).
- **Prompt templates.** File-based saved prompts at `.pi/prompts/<name>.md`
  (trust-gated), invoked as `/name [args]` with positional substitution
  (`docs/prompt-templates.md`).
- **Extensions.** TypeScript modules auto-discovered at `.pi/extensions/*.ts`
  (trust-gated) and `~/.pi/agent/extensions/` (loaded before trust). An
  extension may `registerTool` (a schema'd, model-callable tool),
  `registerCommand` (a user-typed slash command), hook a wide event set
  (`tool_call`, `before_agent_start`, `context`, and more), and inject
  instructions or messages (`docs/extensions.md`).
- **Headless invocation.** `-p` / `--print` runs one prompt and prints the
  final text; `--mode json` streams session events as JSON lines (final text in
  `message_end`) (`docs/usage.md`, `docs/json.md`).
- **System-prompt injection.** `--system-prompt <text>` replaces the default
  (context files and skills still append); `--append-system-prompt <text>`
  appends. Both take **text, not a path** (`docs/usage.md`).
- **Trust for headless children.** Non-interactive modes never show a trust
  prompt, but with the default `defaultProjectTrust: 'ask'` an unattended run
  *skips* project-local resources. `-a` / `--approve` trusts project-local
  files for that run; `defaultProjectTrust: 'always'` auto-grants. Decisions
  persist by canonical directory in `~/.pi/agent/trust.json` (`docs/security.md`).
- **Model / tier selection.** `--model <provider/id:thinking>` and
  `--thinking <level>` (`docs/usage.md`).
- **Session isolation.** `--no-session` runs ephemeral (nothing saved); `cwd`
  sets the project dir (`docs/usage.md`).

### What Pi lacks

- **No subagents or agent hierarchy.** Pi's docs state it "intentionally does
  not include ... sub-agents" (`docs/usage.md`), and extensions "cannot define
  sub-agents or agent hierarchies" (`docs/extensions.md`). The sanctioned path
  is to spawn `pi` as a subprocess or build the orchestration yourself.
- **No `--system-prompt` file flag, no `--yolo`/`--trust` flag.** Read the
  persona file yourself; grant trust with `-a` or settings.

**Consequence for design.** The only faithful way to give a factory agent a
separate Pi session is to spawn a fresh `pi` subprocess with the agent's
markdown as its system prompt. An extension `registerTool` is the surface that
makes that spawn *model-callable by name*.

## 3. Goal

Let a person working conversationally in Pi invoke any factory agent and have it
run with the same separate-session semantics Claude Code provides natively — and
let the `implementation-agent` dispatch parallel, worktree-isolated
`developer-agent` runs — without weakening the existing non-interference,
traceless-removal, or git-safety guarantees.

## 4. Proposed solution (recommendation)

### Phase 1 — single-agent primitive

A new extension, `factory/config/extensions/run-agent.ts`, symlinked to
`.pi/extensions/run-agent.ts` by `init-factory` (the same pattern the guardrail
extension already uses). It registers one model-callable tool:

```
run_agent(agent: string, task: string, model?: string)
```

Execution: resolve `factory/agents/<agent>.md`; resolve the model (the `model`
argument, else `model.conf` `pi.<tier>`, else a default); spawn

```
pi --no-session -a --model <m> --append-system-prompt <agent.md> -p <task>
```

in the project directory; return the subagent's final text as the tool result.
`-a` makes the child a full factory citizen (its own skills, guardrail, and
`AGENTS.md` load); `--no-session` keeps it throwaway; `--append-system-prompt`
layers the agent persona over Pi's defaults. The spawn is a genuinely separate
session, so author/reviewer independence holds.

This phase covers every author/reviewer pair — requirements and spec-review,
architecture and its review, reconciliation, and QA.

### Phase 2 — dispatcher

A second tool layered on the Phase 1 primitive, e.g. `dispatch_wave`, that
spawns several agents in parallel, each in its own git worktree, with a
per-story `--model` tier, and integrates the existing `premerge-check`. This is
the port of `implementation-agent`, whose current prose depends on Claude
Code's Agent tool (`isolation: "worktree"`, simultaneous subagent spawns).

### Supporting changes

- **`factory/config/AGENTS.md`** — correct the orientation. Under Pi, agents are
  not auto-discovered from `.pi/agents/`; to run one in a separate session the
  model calls `run_agent`, rather than reading the file and role-playing it in
  context.
- **`factory/config/model.conf`** — add `pi.economy`, `pi.standard`, and
  `pi.strong` tier rows (only `copilot.*` tiers exist today).
- **`factory/scripts/init-factory`** — extend the Pi step to symlink
  `run-agent.ts` alongside the guardrail extension, with a wiring test mirroring
  the guardrail test in `orchestrator/tests/test_init_factory_guardrail.py`.

## 5. Scope

**In scope**

- The `run_agent` primitive and its supporting `AGENTS.md`, `model.conf`, and
  `init-factory` changes.
- The dispatcher tool (`dispatch_wave` or equivalent) and worktree isolation.
- End-to-end validation against Pi 0.80.8, including the author/reviewer
  independence property and one parallel dispatch.

**Out of scope**

- The headless orchestrator path (`orchestrator/run_playbook.py` →
  `factory/scripts/trigger --cli ...`). Adding `--cli pi` there is a separate,
  automation-oriented feature; this brief is the *conversational* invocation
  layer.
- Any change to how Claude Code or Copilot CLI invoke agents.

## 6. Constraints and interactions

- **Non-interference and traceless removal.** `run-agent.ts` lives in
  `factory/config/extensions/`, is symlinked into the git-ignored `.pi/`, and
  must be reversed by `remove-factory` the same way the guardrail is. It adds no
  tracked project state.
- **Guardrail interplay.** A spawned child loads `.pi/extensions/` under `-a`,
  so the git-safety guardrail applies to subagents too. Confirm the child can
  still run the one sanctioned test path, `factory/scripts/run-tests --staged`.
- **Trust.** The parent is already trusted; the child in the same directory
  inherits the decision from `~/.pi/agent/trust.json`. Decide whether to rely on
  that or pass `-a` explicitly per spawn (recommended, for determinism).
- **Recursion.** The child also loads `run-agent.ts` and could in principle
  spawn its own subagents. Decide whether to bound this (e.g. a depth guard via
  an environment variable the parent sets).

## 7. Open questions for Requirements and Architecture

1. Should `run_agent` return plain final text (`-p`) or structured JSON
   (`--mode json`, parsing `message_end`)? Plain is simpler; JSON exposes
   tool-call detail and token usage.
2. `--append-system-prompt` (layer over Pi's defaults) versus `--system-prompt`
   (replace). Recommendation: append, to keep Pi's own tool guidance.
3. Should the child load the project `AGENTS.md` (local-first orientation, at
   the cost of a spurious greeting), or run with `-nc` for a clean slate?
4. How should `dispatch_wave` express and enforce output-file overlap and
   dependency ordering — inside the tool, or left to the calling agent's plan?
5. Depth/recursion bound for nested `run_agent` calls.
6. Model-tier mapping: what Pi model patterns should `pi.economy/standard/strong`
   resolve to, and how does `on_missing = halt` apply when a tier is unset?

## 8. Acceptance criteria (seeds)

- A conversational Pi session can invoke a factory agent by name and receive its
  result from a separate `pi` session that never saw the caller's context.
- A spec authored by one agent is reviewed by `spec-review-agent` in a session
  that provably lacks the author's reasoning.
- `implementation-agent` dispatches at least two `developer-agent` runs in
  parallel worktrees, each on its own branch, merged through `premerge-check`.
- `init-factory` installs `run-agent.ts` idempotently and `remove-factory`
  reverses it to a clean `git status`.
- The git-safety guardrail still blocks its full pattern set inside spawned
  subagents, and still permits `factory/scripts/run-tests --staged`.
- No new tracked state enters the target project.

## 9. References

- Pi scaffold commit: `e18fa48` on `bug/pi-init-factory`.
- Factory spec this feature extends: [`docs/spec/prd.md`](../../../docs/spec/prd.md)
  (Factory Flow Control).
- Guardrail port precedent: [`factory/config/extensions/block-dangerous-git.ts`](../../config/extensions/block-dangerous-git.ts)
  and its shell twin `factory/config/hooks/block-dangerous-git.sh`.
- Install/remove precedent: `factory/scripts/init-factory`,
  `factory/scripts/remove-factory`.
- CLI-safety and Pi caveat prose: [`factory/docs/factory-guide.md`](../factory-guide.md)
  (§ CLI safety guardrails).
- Pi docs (primary source): `earendil-works/pi`,
  `packages/coding-agent/docs/{usage,skills,prompt-templates,extensions,security,json}.md`.
