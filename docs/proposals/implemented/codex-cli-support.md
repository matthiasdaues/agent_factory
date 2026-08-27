---
schema_version: 2
title: "Codex CLI Support"
status: implemented
owner: agent-factory
created: 2026-07-24
updated: 2026-07-29
supersedes:

impact:
  scope: cross_project
  architecture_change: true
  external_contract_change: true
  boundaries:
    - factory/scripts/init-factory
    - factory/config/hooks/capture-codex-usage.sh

governance:
  assurance: high
  risk_domains:
    - compatibility
    - reliability
    - security

estimate:
  as_of: 2026-07-29
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
---

# Feature Request — Codex CLI Support

**Status:** Implemented
**Scope:** Contained to the `factory/` subproject. It adds Codex as a fourth
supported conversational coding CLI alongside Claude Code, GitHub Copilot CLI,
and Pi. It does not add a new headless orchestrator backend.
**Scope size:** Large — Codex uses different discovery formats for skills and
custom agents, requires merge-safe project hook configuration, and needs
end-to-end validation of the factory's author/reviewer and dispatcher semantics.

This brief seeds the `feature-addition` playbook. It captures the platform facts
known at proposal time, recommends an integration shape, and identifies the
questions that Requirements and Architecture must settle. The proposed design
is a starting point, not an adopted contract.

## 1. Problem

Agent Factory currently installs project-local resources for Claude Code,
GitHub Copilot CLI, and Pi. `factory/scripts/init-factory` creates and wires
their discovery locations, installs CLI-specific git guardrails and usage
capture where available, and records every owned path for exact reversal by
`factory/scripts/remove-factory`.

Codex can already read the repository's root `AGENTS.md` when one exists, but
Agent Factory does not install a Codex-native resource layout. Consequently:

- factory skills are not installed in Codex's repository skill discovery path;
- factory agent Markdown files are not valid Codex custom-agent definitions;
- the shared dangerous-git guardrail is not wired into Codex lifecycle hooks;
- usage capture does not receive Codex `Stop` and `SubagentStop` events;
- `INDEX.yaml`, playbooks, rulebooks, and scripts have no Codex-local aliases
  matching the orientation convention used for the other CLIs;
- removal has no manifest-tested Codex footprint to reverse.

The feature is complete Codex support with the same promises as every existing
CLI: local discoverability, faithful separate subagent execution,
non-interference with project-owned configuration, idempotent installation,
and traceless removal.

## 2. Platform facts (Codex)

These facts were checked against the official Codex documentation on
2026-07-21. Exact formats should be revalidated during implementation because
Codex custom-agent authoring is documented as still evolving.

### Orientation

- Codex reads `AGENTS.md` before work begins.
- At project scope it walks from the repository root to the current working
  directory, taking at most one guidance file per directory. In each directory
  it checks `AGENTS.override.md`, then `AGENTS.md`, then configured fallback
  names.
- A root `AGENTS.md` is therefore the native orientation surface. There is no
  need for a `.codex/CLAUDE.md` equivalent.

### Skills

- Repository skills use the open Agent Skills format: one directory per skill,
  with a required `SKILL.md` containing `name` and `description`.
- Codex scans `.agents/skills` from the current directory up to the repository
  root, and supports symlinked skill directories.
- `.codex/skills` is not the documented repository discovery path. The current
  generic `DOT_DIRS` loop therefore cannot be extended with `.codex` for skills.

### Agents and subagents

- Codex has native parallel subagents and supports project-scoped custom agents
  under `.codex/agents/*.toml`.
- Each custom-agent TOML file requires `name`, `description`, and
  `developer_instructions`. Optional settings include model, reasoning effort,
  sandbox mode, MCP servers, and skill configuration.
- Factory agents are Markdown persona files with YAML frontmatter. They cannot
  merely be symlinked into `.codex/agents`; installation needs a deterministic
  adapter or generated Codex agent catalog.
- Subagents run as separate agent threads, satisfying the factory's
  author/reviewer independence requirement. Codex supports concurrency limits
  through `agents.max_threads`; nesting defaults to direct children only.
- Subagents inherit the parent sandbox and approval policy unless a custom
  agent narrows its sandbox. The factory must not assume a child can request
  new approval in a non-interactive run.

### Hooks

- Project hooks may be declared in `.codex/hooks.json` or inline in
  `.codex/config.toml`. If both forms exist in one layer Codex merges them and
  warns, so Agent Factory should choose one representation.
- Codex supports `PreToolUse`, `Stop`, and `SubagentStop`, matching the existing
  guardrail and usage-capture needs.
- For shell execution, `PreToolUse` uses the `Bash` matcher. It can deny a call
  with the Codex hook result schema or by exiting with status 2 and writing the
  reason to stderr.
- Project-local command hooks require explicit trust and are skipped until the
  user approves their current definition. Installation must report this
  activation step; silently installed but untrusted hooks are not operational.

## 3. Goal

After `init-factory`, a trusted Codex session in the target project can discover
and invoke every factory skill, spawn every factory agent as a native custom
subagent, follow the factory orientation and local-first rule, and receive the
same dangerous-git and usage-capture coverage intended for the other supported
CLIs. `remove-factory` must restore the target to its exact pre-install state.

## 4. Proposed solution (recommendation)

### 4.1 Treat Codex as an adapter, not another `DOT_DIRS` entry

Keep the shared canonical content under `factory/`, but add a dedicated
`install_codex(...)` path in `init-factory`. The Codex layout crosses two root
directories and mixes links with generated files:

```text
AGENTS.md                         -> factory/config/AGENTS.md, if root file absent
.agents/skills/<name>            -> factory/skills/<name>
.codex/agents/<name>.toml        generated adapter for factory/agents/<name>.md
.codex/playbooks                 -> factory/playbooks
.codex/rulebooks                 -> factory/rulebooks
.codex/scripts                   -> factory/scripts
.codex/INDEX.yaml                -> factory/INDEX.yaml
.codex/hooks/block-dangerous-git.sh -> shared or Codex-adapted hook script
.codex/hooks/capture-usage.sh    -> shared or Codex-adapted capture script
.codex/hooks.json                merge-safe Codex hook declarations
```

Whether aliases for playbooks, rulebooks, scripts, and `INDEX.yaml` belong
under `.codex/` or should be referenced directly as `factory/...` is a
Requirements decision. The orientation must name the final paths accurately.

### 4.2 Install skills at `.agents/skills`

Create `.agents/skills` if needed and symlink each individual factory skill
directory into it. Do not symlink the whole `.agents` directory: a target may
already own unrelated repo skills. For every destination:

- an absent path is linked and recorded in `remove_paths`;
- an identical Agent Factory link is an idempotent no-op and remains recorded;
- a real file, directory, or foreign symlink is a collision and stops before
  later steps mutate the target;
- remover pruning deletes `.agents/skills` and `.agents` only when empty.

This per-skill strategy preserves project-owned Codex skills and makes
traceless removal possible.

### 4.3 Generate Codex custom-agent TOML

Add a deterministic adapter script, for example
`factory/scripts/generate-codex-agents`, that reads each canonical
`factory/agents/*.md` file and emits `.codex/agents/<name>.toml`.

Initial mapping:

- frontmatter `name` or filename -> `name`;
- frontmatter `description` -> `description`;
- the full agent Markdown instructions -> `developer_instructions`;
- factory tier -> model and reasoning settings resolved from project
  `config/model.conf`, if Requirements chooses install-time pinning;
- review-only agents -> `sandbox_mode = "read-only"` where their actual duties
  require no artifact writes.

Generated files must carry a clear ownership marker and stable formatting.
`init-factory` must never overwrite a project-owned TOML agent with the same
name. Re-running against an Agent Factory-owned generated file may refresh it
only if update semantics are explicitly included; otherwise it should retain
the existing rule that refreshing copied factory content belongs to a future
update command.

### 4.4 Wire hooks through `.codex/hooks.json`

Prefer `.codex/hooks.json` over modifying `.codex/config.toml`. JSON matches the
existing Claude merge machinery, avoids editing arbitrary TOML, and is a
documented Codex project hook source.

Install:

- a `PreToolUse`/`Bash` entry for dangerous-git blocking;
- `Stop` and `SubagentStop` entries for usage capture.

The existing shell scripts cannot be assumed wire-compatible. Add Codex payload
fixtures and prove that each script correctly reads Codex fields and emits the
Codex denial/output schema. If compatibility would complicate the shared
scripts, add thin Codex adapters that delegate to shared policy logic.

When `.codex/hooks.json` already exists, merge only Agent Factory-owned entries,
without reformatting or deleting project hooks. The manifest must record
whether the file pre-existed. Removal either deletes a Factory-created file or
strips only exact Factory hook entries from a project-owned file.

At the end of installation, print a clear instruction to open `/hooks` and
trust the newly installed project hooks. This human trust decision is not
something `init-factory` should bypass.

### 4.5 Preserve orientation non-interference

Continue using the root `AGENTS.md` as Codex's orientation file. If a real root
`AGENTS.md` already exists, leave it byte-for-byte unchanged and record
`skipped-existing`, as Pi support does today. The feature must decide how a
project with its own `AGENTS.md` learns the local-first Factory rule; silently
shadowing or appending to that file violates non-interference.

Update `factory/config/AGENTS.md` so its CLI table includes Codex paths and
states that Codex agents are native generated TOML definitions, not Markdown
files to role-play in the parent session.

### 4.6 Extend manifest, ignore, and removal behavior

`init-factory` should add only paths it owns to the marker-delimited ignore
block. Expected additions include `/.codex/`; `/.agents/` must not be ignored
wholesale because the project may own checked-in skills. Instead ignore each
Factory-created `.agents/skills/<name>` entry, analogous to the current
per-entry `.github` treatment.

The removal manifest must retain enough information to:

- remove generated Codex agents and created symlinks;
- strip Factory hook entries from a pre-existing `.codex/hooks.json`;
- preserve project-owned `.agents`, `.codex`, agents, skills, hooks, and config;
- prune only empty directories;
- restore the original `.gitignore` bytes and final-newline state.

## 5. Scope

**In scope**

- Codex-native discovery of all factory skills.
- Generated Codex custom agents for all canonical factory agents.
- Native Codex subagent invocation, including author/reviewer separation.
- Dangerous-git `PreToolUse` coverage.
- Usage capture for root and subagent turns.
- Codex orientation and access to the catalog, playbooks, and rulebooks.
- Idempotent install, collision handling, manifest recording, and traceless
  removal.
- Automated tests plus one manual end-to-end run in the current Codex CLI.

**Out of scope**

- A `--cli codex` backend for `orchestrator/run_playbook.py` or
  `factory/scripts/trigger`.
- Codex cloud task orchestration.
- Packaging Agent Factory as a distributable Codex plugin or marketplace item.
- Changing canonical factory agent Markdown into Codex TOML for all CLIs.
- Refresh/update semantics for an already copied `factory/` payload, unless the
  feature-addition process explicitly expands scope.

## 6. Constraints and interactions

- **Canonical-source rule.** Factory agent Markdown and skill directories remain
  canonical. Codex artifacts are adapters and must be reproducible.
- **Non-interference.** Existing `AGENTS.md`, `.agents`, `.codex`, hooks, skills,
  agents, and config remain untouched unless an exact merge contract is defined.
- **Traceless removal.** Every created path or merged entry is represented in
  `.agent-factory/factory-install.json`.
- **Local-first behavior.** Orientation must require checking the installed
  project catalog before global Codex skills or agents of the same name.
- **Reviewer independence.** Review agents must be spawned as separate native
  subagent threads, never simulated by reading their Markdown into the author
  thread.
- **Concurrency and file overlap.** Native parallelism does not itself provide
  branch/worktree isolation. The implementation dispatcher still needs the
  factory's dependency and overlap-aware scheduling rules.
- **Hook trust.** An installed but untrusted hook is inactive; acceptance must
  distinguish successful wiring from user activation.
- **Version drift.** Codex custom-agent and hook schemas must be isolated behind
  tests and adapters so future CLI changes do not alter canonical content.

## 7. Open questions for Requirements and Architecture

1. Should Codex agent TOML be generated during repository development and
   copied by `init-factory`, or generated inside each target at install time?
2. Should model tiers be resolved into each TOML at install time, or should
   agents inherit the parent model and use only reasoning/sandbox overrides?
3. Which factory agents are genuinely read-only? Several reviewers currently
   file findings, so `sandbox_mode = "read-only"` may conflict with their
   required outputs.
4. Should `.codex/hooks.json` merging preserve exact bytes, preserve semantic
   JSON only, or reject pre-existing files and require manual integration?
5. Can `capture-usage.sh` consume Codex transcript and token fields without a
   CLI-specific adapter? Codex documents transcript format as unstable.
6. When root `AGENTS.md` is project-owned, should installation merely report
   the skipped Factory orientation, generate a copy-paste include block, or use
   a configured fallback filename? Any choice must preserve non-interference.

## 8. Resolution — 2026-07-24

The implementation uses the following decisions. They supersede the open
questions above.

1. Generate `.codex/agents/*.toml` inside the target during `init-factory`.
   Canonical Factory agent Markdown remains the source. A generated file carries
   a stable ownership marker; a re-run may refresh only files with that marker.
   A foreign path is a collision.
2. Do not pin `model`, `model_reasoning_effort`, or `sandbox_mode`. Codex custom
   agents inherit the parent defaults. Several Factory reviewers write findings,
   so classifying them as read-only from their names would be incorrect.
3. Install each Factory skill as an individual symlink under
   `.agents/skills/<name>`. Preserve all project-owned `.agents` content and
   ignore only Factory-owned entries.
4. Install generated agents plus `.codex/INDEX.yaml`, `playbooks`, `rulebooks`,
   and `scripts`. These aliases support the local-first orientation; Codex-native
   discovery itself applies only to skills and custom agents.
5. Use `.codex/hooks.json` exclusively. Merge a `PreToolUse`/`^Bash$` guardrail
   with the existing `Stop` and `SubagentStop` capture hooks. Commands resolve
   their scripts from `git rev-parse --show-toplevel`, because Codex may start in
   a nested directory.
6. Keep an existing root `AGENTS.md` byte-identical. Report that Factory
   orientation was skipped and must be incorporated manually. Creating an
   override would shadow the project's own instructions and violate
   non-interference.
7. Use `agents.max_concurrent_threads_per_session` in documentation; the older
   `agents.max_threads` name is only a legacy alias.
8. Hook installation and hook activation are separate acceptance states.
   `init-factory` always reports the `/hooks` review-and-trust action after it
   changes or reaffirms Factory hook definitions.

These decisions were checked against the current official Codex manual on
2026-07-24. Custom-agent authoring remains an evolving surface, so TOML
generation and hook payload handling stay behind focused adapter tests.
7\. Do playbooks, rulebooks, scripts, and `INDEX.yaml` need `.codex` aliases, or
should Codex orientation reference `factory/...` directly?
8\. How should the implementation dispatcher obtain worktree isolation under
Codex native subagents? Shared-workspace parallelism alone is insufficient
for file-overlapping stories.
9\. What minimum Codex CLI version is supported, and how does `init-factory`
detect an older version lacking custom agents or lifecycle hooks?
10\. Should hook trust remain a documented manual post-install step, or should
the installer offer a separate explicit opt-in automation path?

## 8. Acceptance criteria (seeds)

- `init-factory` installs all factory skills into Codex's documented repository
  discovery path without hiding or modifying project-owned skills.
- Every canonical factory agent has a valid project-scoped Codex TOML adapter
  with equivalent name, description, and behavioral instructions.
- A Codex session can spawn a factory author agent and a separate reviewer agent;
  the reviewer thread does not contain the author's private reasoning.
- The implementation dispatcher can run at least two file-disjoint developer
  tasks concurrently without cross-writing, and overlap constraints prevent an
  unsafe wave.
- The dangerous-git hook blocks the full shared policy set for root and
  subagent shell calls, while permitting the sanctioned test command.
- `Stop` and `SubagentStop` capture distinguish the root session from subagents
  and write valid usage records without relying on an undocumented transcript
  schema.
- Installation reports that project hooks require `/hooks` review and trust.
- Re-running installation creates no duplicate links, agents, hook entries,
  ignore lines, or manifest paths.
- Collisions stop with the exact conflicting path and do not overwrite the
  target's content.
- Removal after installation restores a clean `git status` and preserves all
  pre-existing `AGENTS.md`, `.agents`, `.codex`, hook, config, skill, and agent
  content byte-for-byte where promised.
- Existing Claude Code, Copilot CLI, and Pi installation/removal tests continue
  to pass unchanged in behavior.

## 9. Verification strategy

Add focused tests alongside the existing init/remove coverage:

- `test_init_factory_codex_skills.py`: discovery layout, individual symlinks,
  collisions, idempotency, and mixed project-owned skills;
- `test_generate_codex_agents.py`: frontmatter mapping, TOML escaping, stable
  output, required fields, model policy, and malformed source failures;
- `test_init_factory_codex_hooks.py`: create/merge/idempotency/collision cases
  and Codex payload/output fixtures;
- `test_init_factory_codex_orientation.py`: absent and project-owned root
  `AGENTS.md` behavior;
- extend `test_remove_factory.py`: mixed pre-existing `.agents` and `.codex`
  trees, exact hook stripping, directory pruning, and clean-status proof;
- end-to-end smoke test in a temporary git repository with the minimum supported
  Codex CLI, followed by `remove-factory` and byte-level comparison of the
  pre-install tree.

## 10. Implementation status — 2026-07-24

First-class Codex support is implemented. `init-factory` installs repository
skills, generated native agents, local aliases, and root-resolved guardrail and
usage hooks without replacing project-owned content. Re-runs refresh only
manifest-owned generated agents. `remove-factory` removes only manifest-owned
paths and appended hook handlers, then prunes shared directories only when
empty.

The automated consumer smoke validates every generated TOML with `tomllib`,
skill and alias discovery layout, hook shape, idempotent installation, and
byte-identical removal. Lower-level adapter suites retain collision, ownership,
payload, and accounting coverage.

One bounded manual limitation remains: Codex project trust and `/hooks`
approval are user-owned security decisions and cannot be activated by the
installer or automated test. The smoke proves the installed on-disk contract;
an operator must still review and trust current hook definitions in Codex.

## 11. References

- Install/remove precedent: [`factory/scripts/init-factory`](../../../factory/scripts/init-factory)
  and [`factory/scripts/remove-factory`](../../../factory/scripts/remove-factory).
- Factory orientation: [`factory/config/AGENTS.md`](../../../factory/config/AGENTS.md).
- Pi adapter precedent: [`pi-invocation-layer.md`](pi-invocation-layer.md).
- Official Codex documentation:
  [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
  [skills](https://learn.chatgpt.com/docs/build-skills),
  [subagents and custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
  and [hooks](https://learn.chatgpt.com/docs/hooks).
