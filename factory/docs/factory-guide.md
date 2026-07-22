# Factory Guide

What's inside `factory/`, and how its pieces fit together. If you are brand new, start with the [beginner's introduction](../../docs/beginner-intro.md); if you just want to get running, go to [factory/README.md](../README.md) instead. This page is background — read it once you're set up.

## Agents

An agent is one job — "write requirements," "review the architecture," "implement one story." Each agent is a single markdown file in `factory/agents/`, read by your AI CLI at the start of a session.

Most phases have two agents: an **author** and a **reviewer**. The author produces an artifact (a spec, an architecture doc, code). The reviewer checks it in a separate session, without seeing the author's reasoning — only the artifact itself. This catches mistakes a self-review would miss, the same way a second pair of eyes catches things you can't see in your own pull request.

The full list, grouped by phase, is in [`factory/INDEX.yaml`](../INDEX.yaml). Each entry includes a `tokens` field (tiktoken cl100k_base token count of the agent's prompt text) and a `total_tokens` field (body + referenced skills + referenced rulebooks) for context window budget planning.

### Running an agent in a separate session

The author/reviewer split depends on each agent running in its own session, so the reviewer sees only the artifact, never the author's reasoning. How that separate session is created depends on the CLI:

- **Claude Code and GitHub Copilot CLI** spawn subagents natively: the parent session dispatches an agent and reads back its result.
- **Pi** has no native subagent. `init-factory` installs a project-local extension, `.pi/extensions/run-agent.ts`, that registers a `run_agent` tool. Calling it spawns a genuinely separate `pi` subprocess with the chosen agent's markdown as its system prompt and returns the child's result. Under Pi, run a factory agent by calling `run_agent` — not by reading the agent file and acting it out in the current session, which would leak the author's reasoning into the review.

`run_agent` resolves the child's model from `config/model.conf` — the `pi.<tier>` row for the agent's declared tier — unless an explicit model id is passed, and it bounds nested spawns with a recursion-depth cap. The git-safety guardrail extension loads in the child too, so a spawned agent stays governed by the same guardrail as its parent. See [ADR-0004](../../docs/adr/0004-pi-subagent-invocation-via-subprocess-spawn.md) and [UC-10](../../docs/spec/use_cases/UC-10-invoke-a-factory-agent-under-pi.md).

For parallel work, a second Pi extension, `.pi/extensions/dispatch-wave.ts`, registers a `dispatch_wave` tool — the port of `implementation-agent`, which under Claude Code relies on the native Agent tool's `isolation: "worktree"` and simultaneous subagent spawns. Given one caller-planned, file-disjoint wave, `dispatch_wave` cuts a feature branch in its own git worktree per item, spawns each agent there in parallel, and — unless told not to — runs `premerge-check` before merging each finished branch into the target. It does not plan the wave: output-file overlap and dependency ordering stay with the calling agent, exactly as `implementation-agent` documents. `premerge-check` runs against the wave's frozen base, so a sibling merge advancing the target never falsely flags a later branch as stale.

## Runtime usage capture

Agent Factory records runtime token usage for Claude Code, GitHub Copilot CLI,
Codex, and Pi. Every capture site calls the same
`factory/scripts/usage-capture` pipeline: a CLI-specific transcript normalizer,
the fixed `tiktoken cl100k_base` comparison tokenizer, and an append-only JSONL
logging adapter. One record is appended to
`.agent-factory/usage/<session_id>.jsonl`; the exact text that was tokenized is
copied beneath `.agent-factory/usage/transcripts/` and linked through
`transcript_ref`. The existing `/.agent-factory/` ignore rule covers the whole
runtime area.

`normalized_input`, `normalized_output`, and their derived total are always
present. Provider `reported_*` fields and `usage_granularity` are nullable when
the transcript contains no provider breakdown. Capture is best-effort: direct
invocation reports errors on stderr and returns success, while native lifecycle
adapters may suppress those errors too. Capture failure never changes session
completion or a tool result. `remove-factory` removes Factory-owned hook assets
and exact merged entries while preserving project-owned configuration.

| CLI                | Human/root trigger                 | Child trigger                                      | Accounting rule                                                                                                                                            |
| ------------------ | ---------------------------------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Claude Code        | `Stop` in `.claude/settings.json`  | `SubagentStop`                                     | The latest cumulative root excludes child internals and usage. Add each distinct child record once.                                                        |
| GitHub Copilot CLI | `agentStop` under `.github/hooks/` | `subagentStop` for supported custom agents         | Select the latest cumulative root snapshot. It is inclusive; child records are attribution only. The built-in `general-purpose` agent emits no child hook. |
| Codex              | `Stop` in `.codex/hooks.json`      | `SubagentStop`                                     | The latest cumulative root snapshot is inclusive; child records are attribution only.                                                                      |
| Pi                 | `session_shutdown` extension       | Inline at each `run_agent` / `dispatch_wave` child | The root excludes separate subprocess spend. Add every distinct descendant record once.                                                                    |

Codex project command hooks remain inactive until their current definitions are
trusted. After `init-factory`, open Codex's `/hooks` UI and approve the installed
project hooks. `init-factory` reports this activation step on fresh installs and
re-runs. Wiring the files does not activate them: Codex skips a new or changed
hook definition until it is reviewed and trusted again.

Pi human sessions capture once at graceful `session_shutdown`. Inline child
capture disables the child's shutdown extension, preventing duplicate records.
`run_agent` and `dispatch_wave` attach nesting depth and the active parent
session id. The shared resolver prefers Pi's active session file, then the
explicit child-session environment, then a process-stable fallback. Pi totals
add the human/root record and every distinct descendant exactly once because a
separate Pi subprocess's model calls are not included in its parent's provider
or normalized totals. Boundary task/result text can occur in both records
because both model invocations consumed it.

Claude `Stop` records are cumulative snapshots of the main transcript. For
session totals, select the latest root record and add each distinct
`SubagentStop` record once. Claude's `SubagentStop.transcript_path` points to
the main transcript; Agent Factory instead captures the required
`agent_transcript_path`, which contains the child's internal messages and
per-message provider usage. Boundary task and result text can occur in both
records because it entered both model contexts; that is real normalized usage,
not aggregation duplication.

The architecture rationale is recorded in
[ADR-0007](../../docs/adr/0007-normalize-runtime-usage-through-cli-adapters.md).

## Skills

A skill is a how-to — a reusable procedure an agent (or you, directly) invokes to do one well-defined thing: run a structured interview, write an ADR, run a security review. Each skill is a folder in `factory/skills/` holding a `SKILL.md`. Agents call skills; skills don't call agents.

The full list is also in [`factory/INDEX.yaml`](../INDEX.yaml), with token counts per skill.

## Playbooks

A playbook is a step-by-step recipe in `factory/playbooks/` for a specific situation — which agents to run, in what order, with what to check in between. Pick the one that matches what you're doing; don't run the full phase chain when a smaller playbook fits.

### Beginner playbooks

Start with these. Small blast radius, few steps, nothing to set up first:

| Playbook                                                          | For                                                                                                                                                                   |
| ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`poc-spike.md`](../playbooks/poc-spike.md)                       | "Does this basic idea even work?" No spec, no architecture, no checks — one file, thrown away by default. The fastest way to see an agent and your CLI work together. |
| [`bug-fix.md`](../playbooks/bug-fix.md)                           | Fixing one reported defect. Four steps: file the bug, fix it with tests, QA validates, mark resolved.                                                                 |
| [`documentation-update.md`](../playbooks/documentation-update.md) | Syncing docs with code after they've drifted. Two steps: reconcile, validate.                                                                                         |

### Full-chain playbooks

Once you're comfortable, these drive some or all of the five-phase chain (requirements → architecture → planning → implementation → quality — see [docs/concepts.md § The phase chain](../../docs/concepts.md#the-phase-chain)):

| Playbook                                                              | For                                                                                                                                                              |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`greenfield-development.md`](../playbooks/greenfield-development.md) | A brand-new project, start to finish.                                                                                                                            |
| [`brownfield-onboarding.md`](../playbooks/brownfield-onboarding.md)   | Bringing Agent Factory into an existing codebase that has no spec or architecture docs yet.                                                                      |
| [`feature-addition.md`](../playbooks/feature-addition.md)             | Adding a feature to a project Agent Factory already manages. Skips straight to planning for small features; runs the full chain for large ones.                  |
| [`refactoring.md`](../playbooks/refactoring.md)                       | Restructuring code without changing behaviour, with a measured baseline and a safety net.                                                                        |
| [`technical-poc.md`](../playbooks/technical-poc.md)                   | A real technical risk question, usually comparing 2+ candidate approaches, feeding an actual decision. Heavier than `poc-spike.md`, lighter than the full chain. |
| [`architecture-review.md`](../playbooks/architecture-review.md)       | Reviewing existing architecture documentation against quality attributes.                                                                                        |

### The research workflow

Separate from the idea → production chain, [`research-topic.md`](../playbooks/research-topic.md) runs a **falsification-driven research** effort — from an approved research brief to a validated final report. It is driven by the phase-6 **Research** agents (`research-orchestrator`, `researcher`, `claim-reviewer`, `research-report-writer`) and their `research-*` skills. A claim reaches the report only after surviving a serious attempt at refutation within its stated scope; a surviving claim is never presented as proved, only as having withstood the defined tests. Every artifact passes the three-stage validation gate (schema → policy → semantic; see [§ Linting and gating](#linting-and-gating)) before the next step begins.

## Playbook phase gates

Playbooks above are prose: nothing stops staging an architecture file before the spec gate clears except the human remembering the playbook's own instructions. An optional structured harness, layered on top, catches phase-boundary mistakes mechanically instead.

A playbook can ship a `.fsm.yml` alongside its `.md` in `factory/playbooks/` — a state machine describing each phase's `outputs:` file globs and the `entry_conditions` required to advance into it. Only [`greenfield-development.fsm.yml`](../playbooks/greenfield-development.fsm.yml) exists today. This is opt-in, not a default every playbook must adopt.

| Component                           | What it does                                                                                                         |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `.agent-factory/playbook-state.yml` | Local, git-ignored marker recording which state the project is currently in.                                         |
| `factory/scripts/transition-lint`   | Pre-commit gate. Blocks staging a file whose `outputs:` glob belongs to a state other than the marker's current one. |
| `factory/scripts/phase advance`     | Subcommand that checks the next state's `entry_conditions` and, if satisfied, advances the marker.                   |

`transition-lint` deliberately does not evaluate `entry_conditions` — by its own docstring, it "governs ordering *between* phases," not within one, and "does not evaluate a state's `entry_conditions`" because "that is `phase advance`'s job." It only checks whether a staged file belongs to the current state, naming the offending path and pointing at `phase advance` when a file belongs to a later one. This is a deliberate design choice, not a gap: condition-checking lives in one place only.

`phase advance` reads the next state's `entry_conditions`, evaluates each against a small `gate_conditions` library, and refuses — non-zero exit, marker unchanged — if any is unmet. Implemented condition types: `file_exists`, `files_exist`, `no_open_findings`, and `script_exit_zero` (stubbed to always pass in this proof of concept). On success it writes the marker with `recorded_at` taken from `phase advance`'s own process clock, never agent-supplied.

If the marker file is absent, both tools are no-ops — a project not using the harness sees no behavior change.

See [Structured Playbooks as a Deterministic Harness](proposals/playbook-structured-harness-strategy.md) for the full design rationale and the proof of concept's scope. The harness now has its own full specification — actors, use cases, entity model, and business rules — at [docs/spec/prd.md](../../docs/spec/prd.md).

## Rulebooks

A rulebook is a cross-cutting convention that applies across agents and skills — commit message format, how to cross-reference other documents, ADR style, branch scoping. [`factory/rulebooks/rules.md`](../rulebooks/rules.md) states each rule in one line; the matching file in `factory/rulebooks/conventions/` carries the reasoning, examples, and edge cases. Agents and skills cite these rules rather than restating them.

Rulebooks are grouped by kind, one directory per kind. `index-lint` derives each rulebook's `category` from its parent directory:

| Directory                                   | Holds                                                                                       | In `INDEX.yaml`? |
| ------------------------------------------- | ------------------------------------------------------------------------------------------- | ---------------- |
| [`conventions/`](../rulebooks/conventions/) | The prose conventions above, plus the four research **policies** (`research-*.md`)          | Yes              |
| [`templates/`](../rulebooks/templates/)     | Fill-in skeletons for artifacts — ADRs, and the ten `research-*.md` artifact templates      | Yes              |
| [`schemas/`](../rulebooks/schemas/)         | JSON-Schema data contracts (`research-*.schema.json`) the research validators check against | No — see below   |

The research feature adds files across all three, marked by a `research-` filename prefix rather than a per-feature subtree (see [ADR-0006](../../docs/adr/0006-research-flat-storage-and-validation-pipeline.md)). Two points are deliberate, not drift:

- The four **research policies** live under `conventions/`, so `index-lint` catalogs them with `category: conventions` even though their own frontmatter reads `category: policies` — a label describing their nature. There is no `policies/` directory.
- `schemas/` is a genuinely new category of rulebook: machine-readable data, not prose. Its `.schema.json` files are intentionally **absent** from `INDEX.yaml`, because `index-lint` scans Markdown frontmatter only. The validators resolve them by path, never by catalog name.

## Linting and gating

A gate is a deterministic script — no LLM judgement involved — that catches a provable defect before a reviewer agent spends time on it: a broken cross-reference, a missing required section, an inconsistent ID. Cheap, reproducible, no false positives.

| Gate                           | Fires at                 | What it checks                                                                                                                      |
| ------------------------------ | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| `factory/scripts/spec-lint`    | Phase 1 → 2 boundary     | Use-case coverage, traceability links between PRD → actor-goals → use cases → supplementary specs, ID uniqueness, required sections |
| `factory/scripts/arch-lint`    | Phase 2 → 3 boundary     | arc42 chapters exist and cross-reference the Structurizr DSL, ADR index consistency, diagram file references                        |
| `factory/scripts/backlog-lint` | Phase 3 → 4 boundary     | YAML frontmatter schema, dependency graph acyclicity, priority and status values                                                    |
| `factory/scripts/matrix-lint`  | `config/model.conf` edit | Syntax, required fields, valid tier/model mappings                                                                                  |

In manual mode (driving each agent by hand, one session at a time), the reviewer agent for that phase runs its gate as its first step. Run any gate yourself the same way:

```bash
factory/scripts/spec-lint docs/spec/
factory/scripts/arch-lint --docs-dir docs/
factory/scripts/backlog-lint backlog/
factory/scripts/matrix-lint config/model.conf
```

These scripts are stdlib-only Python — no install needed to run them.

### Research artifact validation

The research workflow adds two more deterministic validators, stdlib-only in the same spirit but invoked on demand by the research skills and agents (and by you), not wired to a phase boundary. They implement the first two stages of a fixed three-stage validation order — **schema → policy → semantic** — that splits validation by whether a machine can decide it:

| Stage        | Tool                                | Checks                                                                                                              |
| ------------ | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| 1 — schema   | `factory/scripts/schema-validate`   | One JSON artifact against one JSON Schema: required fields, types, enums, identifier patterns, timestamps           |
| 2 — policy   | `factory/scripts/policy-validate`   | The enforceable half of the research policies across artifacts: role separation, references, quorum, claim versions |
| 3 — semantic | a qualified human or agent reviewer | Evidence support, source independence, test severity, claim atomicity — the judgment no script makes                |

```bash
factory/scripts/schema-validate <artifact-file> <schema-file>
factory/scripts/policy-validate --pipeline <artifact-or-dir>...   # runs stage 1, then stage 2, stopping at the first failure
```

An artifact must pass stage 1, then stage 2, then stage 3 before the next playbook step begins. The schemas live in [`factory/rulebooks/schemas/`](../rulebooks/schemas/). See [ADR-0006](../../docs/adr/0006-research-flat-storage-and-validation-pipeline.md) and [`research-topic.md` § The Validation Gate](../playbooks/research-topic.md).

Separately, `pre-commit` runs `mdformat` and `ruff` on every commit, formatting markdown and Python automatically. Both run through `uvx`, so nothing needs installing locally beyond `uv` itself — the same zero-local-install pattern `factory/scripts/structurizr` uses for its Docker dependency.

## CLI safety guardrails

`init-factory` also installs a git-safety guardrail that blocks a fixed list of dangerous git invocations before they run. For Claude Code and Copilot CLI this is a native `PreToolUse` hook; for Pi it is a project-local extension under `.pi/extensions/` that blocks the same dangerous `bash` commands when loaded. Two groups:

- **Commands that discard or overwrite work or history**: `git push`, `git reset --hard`, `git clean -f`/`-fd`, `git branch -D`, `git checkout .`, `git restore .`, and bare `push --force` / `reset --hard` fragments anywhere in a longer command line.
- **Commands that bypass this repo's own commit gates**: `--no-verify`, `git commit -n`, reassigning `core.hooksPath`, `pre-commit uninstall`, and `SKIP=...` environment overrides on `git commit` or `pre-commit`.

One script serves the hook-based CLIs: it reads the shell command from either CLI's `PreToolUse` JSON shape, and both CLIs treat the hook's exit code 2 as "deny."

The guardrail is installed automatically for every project — not opt-in, not a skill you invoke by hand. `init-factory` symlinks the script into both `.claude/hooks/` and `.github/hooks/`, and wires each CLI's own hook-config shape to it: `.claude/settings.json` as a `PreToolUse`/`Bash` hook for Claude Code, `.github/hooks/block-dangerous-git.json` (`matcher: "bash"`) for Copilot CLI. For Pi, `init-factory` symlinks `.pi/extensions/block-dangerous-git.ts` to `factory/config/extensions/block-dangerous-git.ts`; Pi auto-discovers project-local extensions from `.pi/extensions/` once the project is trusted. `.claude/` and `.pi/` are gitignored wholesale; under `.github/`, only the entries Agent Factory adds — including `.github/hooks/` — are gitignored, never your Actions workflows. This is pure local machine state, re-created fresh by `init-factory` in every clone.

**Pi caveat:** this is not as strong as the native Claude/Copilot hook path. Pi loads project-local extensions only after project trust resolves, and non-interactive runs may ignore them unless trust is already saved or the run is explicitly approved. For stronger Pi enforcement, install the same extension globally under `~/.pi/agent/extensions/`, pass it via `pi -e`, or run Pi in a sandbox/container. See Pi's own [Extensions](https://github.com/earendil-works/pi-mono/blob/main/packages/coding-agent/docs/extensions.md), [Security](https://github.com/earendil-works/pi-mono/blob/main/packages/coding-agent/docs/security.md), and [Containerization](https://github.com/earendil-works/pi-mono/blob/main/packages/coding-agent/docs/containerization.md) docs for the underlying model.

Treat it as a backstop, not a security boundary. It catches an accidental or under-pressure bypass — a background agent routing around a failing gate, for instance — not a determined one. A user with shell access outside the CLI, or anyone who edits the CLI's own configuration, can always route around it.

## Session logging

Session logging is an opt-in, append-only audit trail of gate-script runs. It exists to reconcile what an agent claims it did in a session against what actually happened on disk — not to replace or gate anything by default.

**Enable it.** Set the `AF_SESSION_LOG` environment variable to a log-file path before running gates. `factory/scripts/_session_log.py` reads it fresh on each run: unset, logging is a no-op and nothing is written; set, it appends one line per wrapped run to that path, creating the parent directory if needed.

**What gets recorded.** Each JSON Lines entry has: `ts` (UTC timestamp from the script's own process clock, not agent-supplied), `script` (the gate's name), `argv` (its invocation arguments), `exit_code`, and `files_changed` (a `git status --porcelain` diff taken before and after the run — the ground truth for what moved on disk). A `summary` field is added when the wrapped gate supplies one (`spec-lint` folds in its `--format json` error/warning/info counts).

**Current scope.** Only `spec-lint` is instrumented today. No other gate writes to the log yet.

**Reconcile.** `factory/scripts/session-reconcile` compares the log against real git state: `--log` points at the log file (default `.agent-factory/session-log.jsonl`), `--base`/`--head` bound the commit range to diff (omit `--base` to check the working tree alone). It reports three finding codes: `RECON-UNEXPLAINED` (error) — a working-tree change no logged run or commit accounts for; `RECON-DRIFT` (warning) — a run logged a change that is now neither committed nor present in the working tree; `RECON-STALE` (warning) — `docs/spec/` changed but `spec-lint` never ran this session. Exit code is the error-finding count, unless `--report-only`.

The log file lives under `.agent-factory/`, which is gitignored — local machine state, not portable, not meant to be reviewed.

See [factory/docs/proposals/session-log-addendum.md](proposals/session-log-addendum.md) for the full design rationale.

## Using this in an existing repo

`init-factory` works the same way against a repo that already has its own history, `.gitignore`, and `.pre-commit-config.yaml`. Run it from inside that repo:

```bash
cd /path/to/existing-project
/path/to/agent_factory/factory/scripts/init-factory
```

Two promises govern the whole install: it never disturbs what the project already owns, and everything it adds can be removed without a trace. Concretely, against an existing repo:

- **`.gitignore`** — adds a single marker-delimited block headed `agent_factory related`, listing exactly the footprint it introduces. It never rewrites or duplicates what's already there, and it preserves your file's exact bytes (down to a missing final newline). Under `.github/` it ignores the specific entries it adds, one by one — never the whole directory, so your `.github/workflows/` stay tracked.
- **`.pre-commit-config.yaml`** — the one tracked change. If the file doesn't exist, it's created carrying just Agent Factory's block. If it exists, `init-factory` hands off to `factory/scripts/merge-precommit-config`, which splices the `- repo: local` block — every hook id prefixed `agent_factory_hook-` — in at the top of your `repos:` list, leaving your own hooks untouched. An inert `.pre-commit-config.yml` is never touched; pre-commit only auto-reads `.yaml`.
- **Orientation files** — if you already have a `.github/copilot-instructions.md` (or `.claude/CLAUDE.md`), it is left exactly as it is. Agent Factory's orientation is not forced on top of yours.
- **Everything else** — your `docs/`, your scripts, your configuration — is left alone. `init-factory` never touches a file or directory it didn't create.

The script is idempotent: run it again any time, and anything already correctly in place is skipped. It records what it did in `.agent-factory/factory-install.json`, and a re-run reads that manifest so it never loses track of what it owns. If it finds something it can't safely work around, it stops immediately and names the exact path — it never partially applies a run.

**Removing it again.** `factory/scripts/remove-factory` reverses the whole install from the manifest — deleting the git-ignored footprint, stripping the `agent_factory related` `.gitignore` block, and removing the `agent_factory_hook-` pre-commit block while leaving your own hooks in place — back to a clean `git status`. A repo that had its own `.gitignore`, pre-commit config, orientation file, or workflows gets them all back byte-for-byte.

To trigger the install conversationally instead of from a shell, use the `init-factory` skill (`factory/skills/init-factory/SKILL.md`): it confirms the target with you, runs the script, and relays its output.

## Troubleshooting

**`init-factory: STOPPED — <path> already exists and is not a symlink to <dest>`**
Something real is already at that path. Move, rename, or remove it, then re-run `init-factory`.

**`merge-precommit-config` reports it cannot merge your `.pre-commit-config.yaml`**
This happens when the file has no top-level `repos:` list in block style, or its existing hooks aren't indented at 2 spaces. Merge Agent Factory's hooks in by hand: copy the `- repo: local` block from `factory/config/pre-commit-config.yaml` into your file's `repos:` list.

**`uvx: command not found`**
Install `uv` — see [factory/README.md § Prerequisites](../README.md#prerequisites). Every gate, and `pre-commit` itself, runs through `uvx`.

**`docker info` fails, or diagram export fails**
Start Docker Desktop (macOS) or the Docker daemon (Linux). This only blocks `factory/scripts/structurizr` — nothing else needs Docker.

**Your first commit fails, or modifies files you didn't touch**
Expected — the `mdformat` and `ruff` hooks auto-fix formatting on commit. Re-stage and commit again:

```bash
git add -u
git commit -m "<same message>"
```

**`factory/` looks out of date after you update your `agent_factory` checkout**
`init-factory` only copies `factory/` in once. There's no update script yet — delete your project's `factory/` directory and re-run `init-factory` to refresh it.

**Symlinks don't work on Windows**
Agent Factory targets macOS and Linux only. Both rely on native, git-tracked symlinks, which Windows doesn't support the same way.

## Referenced from

- [factory/README.md](../README.md)
- [docs/spec/prd.md § Problem Statement](../../docs/spec/prd.md#1-problem-statement)
