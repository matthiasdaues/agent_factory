---
schema_version: 2
title: OpenCode CLI Integration
status: accepted
owner: Agent Factory maintainers
created: 2026-09-20
updated: 2026-09-22
supersedes:

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - packages/factory/scripts/init-factory
    - packages/factory/config/AGENTS.md
    - packages/factory/config/model.conf
    - packages/factory/rulebooks/rules.md
    - packages/factory/docs/factory-guide.md
    - packages/factory/README.md

governance:
  assurance: high
  risk_domains:
    - compatibility
    - reliability
    - operations

estimate:
  as_of: 2026-09-21
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: OpenCode CLI Integration

## Summary

Add OpenCode V2 as an Agent Factory command-line interface (CLI) target. An
OpenCode user can install the Factory, enter through an OpenCode-specific
orientation, discover the local catalog, and run Factory workflows with
plugin-enforced permissions, step boundaries, usage capture, and isolated
worktrees.

## Motivation

The Factory supports Claude Code, GitHub Copilot CLI, Pi, and OpenAI Codex.
OpenCode users cannot install a dedicated integration or apply the Factory's
safety controls today.

The completed [OpenCode research survey](../research/opencode-cli-integration/survey-report.md) found
native support for Markdown agents, skills, Model Context Protocol (MCP)
servers, and child sessions. A follow-up study of the
[OpenCode V2 plugin API](https://opencode.ai/v2/docs/build/plugins/) and
[permission model](https://opencode.ai/v2/docs/permissions) confirmed that V2
plugins can intercept tools (`execute.before`/`execute.after` hooks), evaluate
permissions (`permission.hook("evaluate")`), observe sessions
(`session.hook("context"/"prompt")`), manage Git worktrees
(`worktree.transform()` + CRUD), and restrict tools per agent
(`tool.transform()` with `editor.remove()`). These findings are documented in
[SR-0013](../research/opencode-cli-integration/sources/SR-0013.md) through
[SR-0017](../research/opencode-cli-integration/sources/SR-0017.md). The
community [cc-safety-net plugin](../research/opencode-cli-integration/sources/SR-0016.md)
independently confirms that tool denial and shell blocking work in V2 plugins.

The original survey's blocker conclusion therefore does not apply to OpenCode
V2. The Factory needs a dedicated plugin that maps those controls to existing
Factory invariants.

One known limitation remains: OpenCode's model inheritance bug persists in V2
(issue #49765, open as of 2026-09-18). Subagents fall back to the global model
instead of inheriting the parent's model. The `event.model` field in the plugin
context hook is typed `readonly`, so a plugin-based override is not currently
possible. See [Model mapping](#model-mapping) for the mitigation.

## Core Principles

- Factory safety rules must be enforced by OpenCode controls, not prompt text.
- Existing CLI integrations must keep their files and behavior.
- The OpenCode integration must not replace the root `AGENTS.md` used by Pi and
  Codex.
- A missing or unhealthy Factory plugin must fail closed.
- Generated files must remain removable by
  [`remove-factory`](../../packages/factory/scripts/remove-factory).

## Design

### Installation and discovery

[`init-factory`](../../packages/factory/scripts/init-factory) recognizes
OpenCode and creates `.opencode/`. It links the Factory catalog into
`.opencode/INDEX.yaml` and exposes the canonical agents, playbooks, rulebooks,
and scripts through that directory. It keeps skills under `.agents/skills/`,
which OpenCode discovers natively.

The installer links the Factory OpenCode plugin into `.opencode/plugins/`.
OpenCode discovers that directory without a project configuration entry. The
installer records every created OpenCode path so
[`remove-factory`](../../packages/factory/scripts/remove-factory) can undo only
Factory-owned changes.

Automatic detection selects OpenCode when `.opencode/`, `opencode.json`, or
`opencode.jsonc` exists. Explicit `--cli opencode` selection remains available.
Before writing any OpenCode path, the installer requires OpenCode CLI `1.18.31`
or a later compatible release. An unsupported version stops installation with
an upgrade instruction.

### Orientation and catalog routing

`packages/factory/config/AGENTS.opencode.md` describes OpenCode's tool names,
child-session behavior, skill discovery, and session-start procedure. The
plugin injects this orientation into the assembled system context. It does not
depend on the legacy `instructions` configuration field or replace the root
`AGENTS.md`.

The shared CLI table in
[AGENTS.md](../../packages/factory/config/AGENTS.md) includes OpenCode and
`.opencode/INDEX.yaml`. OpenCode agents live under `.opencode/agents/`. Skills
remain under `.agents/skills/`. The installer generates agent definitions with
OpenCode modes, model tiers, and permissions from the canonical catalog.

### Safety plugin

`packages/factory/config/plugins/agent-factory.ts` provides the OpenCode
adapter. It applies ordered `allow`, `ask`, and `deny` rules to shell commands,
file access, skills, MCP tools, and child agents. Explicit denials protect
dangerous Git commands and paths outside the assigned workspace.

A pre-tool hook reads the active step manifest and rejects reads, writes, and
shell operations outside its declared boundary. Permission hooks may narrow an
OpenCode decision but must never broaden a configured denial.

The plugin removes tools that the active agent must not use. Review agents
receive read-only permissions unless their procedure declares a write output.
Child sessions inherit session-scoped restrictions and apply their own
generated agent permissions.

### Usage capture

The plugin observes completed root and child sessions and sends their usage to
the existing Factory usage pipeline. OpenCode records follow the existing usage
contract and avoid counting child usage twice. Session completion does not
reactivate the agent or introduce an OpenCode-specific completion gate.

### Isolated dispatch

The plugin registers a Factory worktree strategy through OpenCode's worktree
API. The strategy delegates branch and worktree creation to Factory scripts so
existing naming, base, path, and verification rules remain authoritative.
OpenCode tracks the resulting location and starts each child session there.
The original checkout receives a session-scoped write denial while isolated
work is active.

The dispatcher keeps the Factory's existing branch, verification, ledger, and
merge rules. OpenCode supplies session and worktree lifecycle primitives.

### Model mapping

[model.conf](../../packages/factory/config/model.conf) gains OpenCode entries
for economy, standard, and strong tiers. The fitting flow presents OpenCode
model identifiers in `provider/model` form. Missing mappings follow the
existing halt policy.

Because of the model inheritance bug (issue #49765), the plugin must set the
model for each child session explicitly through agent catalog entries rather
than relying on runtime inheritance. Each generated OpenCode agent definition
carries a `model` field derived from its tier mapping in `model.conf`. This
workaround becomes removable when OpenCode fixes the inheritance bug.

### Verification

Installer tests cover fresh installation, update, removal, coexistence with Pi
and Codex, and repeated installation. Catalog tests check every generated
OpenCode link. Plugin tests exercise permission denial, step boundaries,
usage capture, session permissions, and worktree lifecycle.

An integration check starts OpenCode in a fixture project when the executable
is available. The check confirms orientation injection, catalog discovery,
agent and skill discovery, denial of a representative unsafe command,
rejection of an out-of-bound write, usage capture, and worktree-isolated child
execution. Deterministic tests remain the required owner when OpenCode is not
installed in continuous integration.

## Scope

**In the first release:**

- Detect OpenCode and create its project-local integration files.
- Add an OpenCode orientation and local catalog mapping.
- Expose compatible agents and existing skills through native discovery paths.
- Install a Factory plugin that enforces permissions and step boundaries.
- Capture root and child session usage through the existing usage pipeline.
- Dispatch child sessions into Factory-managed Git worktrees.
- Add OpenCode model-tier configuration to fitting.
- Preserve user-owned OpenCode files during install, update, and removal.
- Reject unsupported OpenCode versions before changing OpenCode-owned files.
- Document plugin trust, host-authority limits, and recovery behavior.
- Test installation, coexistence, idempotency, removal, and discovery.

**Explicitly deferred (do NOT plan stories for these):**

- Operating-system sandboxing is deferred because OpenCode shell commands use
  the host user's authority. The Factory plugin restricts tool use but does not
  claim to contain a hostile process.
- Remote workspace provisioning is deferred because the OpenCode worktree API
  manages local directories.
- OpenCode Desktop support is deferred. The first release targets the CLI and
  its tested plugin lifecycle.
- An MCP-based adapter is deferred because the native plugin API exposes the
  required permission, session, tool, and worktree controls.
- Built-in task tracking (TaskCreate/TaskUpdate equivalent) is deferred because
  OpenCode has no native task tool. The plugin can register a custom tool via
  `ctx.tool.transform()` in a later release if needed. Task tracking is a
  convenience, not a safety invariant.
- Built-in workflow orchestration (Workflow tool equivalent) is deferred because
  no direct substitute exists in the V2 plugin API. External orchestrators or a
  custom plugin tool can be added later.
- Built-in persistent cross-session memory is deferred because the Factory's
  file-based memory convention works without CLI-native support. The plugin's
  `ctx.storage` provides plugin-scoped persistence for plugin state only.

## Design Details

The first release supports OpenCode CLI `1.18.31` and later compatible
releases. Installation checks `opencode --version`. An older version receives
an upgrade instruction before the installer changes OpenCode paths.

The integration must not rely on OpenCode's Claude Code compatibility mode or
legacy V1 plugin hooks. Dedicated Factory files and the V2 plugin API define
the supported contract.

The plugin must fail closed when initialization, manifest loading, permission
evaluation, or worktree creation fails. Its error must name the failed control
and the recovery action. Usage capture remains best-effort and reports failures
without blocking the session.

The plugin must never treat prompt instructions, agent visibility, or an
OpenCode snapshot as an enforcement boundary. Permissions, hooks, Factory gate
scripts, and Git worktrees own enforcement.

## Open Questions

1. **`execute.before` denial contract** — The `execute.before` hook's return
   type is `void | Promise<void>` in the official docs, but the cc-safety-net
   plugin demonstrates denial by returning `Tool.Error`. Is this a stable API
   contract or an undocumented side effect? The plugin's enforcement model
   depends on this mechanism. [SR-0016]

2. **Permission hooks in child sessions** — Whether `permission.hook("evaluate")`
   fires for child sessions (not just the root session) is undocumented. If it
   does not, child sessions may bypass plugin-enforced permission narrowing.
   [SR-0013]

3. **Tool removal persistence** — Whether tool removal via `context` hook
   (`delete event.tools.X`) persists across turns or is re-evaluated per turn
   is undocumented. If per-turn, the plugin must re-apply restrictions on every
   context assembly. [SR-0013]

4. **Claude Code compatibility and skill discovery** — When
   `OPENCODE_DISABLE_CLAUDE_CODE=1` disables compatibility mode, does it also
   suppress `.claude/skills/` discovery? If so, the installer must copy or link
   skills into `.agents/skills/` or `.opencode/skills/` rather than relying on
   the Claude Code discovery path. [SR-0014]

These questions can be resolved during implementation by testing against the
target OpenCode version. None blocks the planning phase.

## Completion Criteria

- A fixture with OpenCode selected receives `.opencode/INDEX.yaml`, an
  OpenCode orientation plugin, discoverable agents, and discoverable skills.
- A project that uses Pi, Codex, and OpenCode keeps one valid root `AGENTS.md`;
  OpenCode receives its dedicated orientation through the Factory plugin.
- Installation, update, and removal preserve user-owned files under
  `.opencode/`.
- Detection selects OpenCode for `.opencode/`, `opencode.json`, and
  `opencode.jsonc`; explicit CLI selection produces the same installation.
- An unsupported OpenCode version stops installation before any OpenCode path
  changes and reports the required upgrade.
- Repeated installation produces no additional changes.
- A configured dangerous Git command is denied before shell execution.
- A read or write outside an active step manifest is denied before tool
  execution.
- A review agent cannot edit a path that its declared outputs do not allow.
- Completed root and child sessions produce contract-valid usage records
  without counting child usage twice.
- Each dispatched implementation child runs in its own Factory branch and Git
  worktree under `.current-work/<feature-branch>/`.
- Each dispatched child verifies its declared base before reading or changing
  story files.
- The primary checkout rejects writes while isolated child work is active.
- A missing or unhealthy Factory plugin stops the Factory entry flow and names
  the recovery action.
- Fitting accepts OpenCode `provider/model` identifiers for all three model
  tiers and halts when a required tier has no mapping.
- The Factory guide and package README list the supported OpenCode version,
  plugin trust model, and host-authority limitation.
- `remove-factory` removes Factory-owned OpenCode entries and files without
  removing user-owned OpenCode configuration.
- The full automated test suite passes with OpenCode absent from the test host.
- The optional integration check passes when a supported OpenCode executable is
  available.

## Guiding Rule

Map every Factory safety invariant to an enforceable OpenCode control.

## Review — 2026-09-21

Reviewer: proposal-review-agent
Reviewed commit: 9e302527cffb4df610e34485acd334fbeb2a2619
Disposition: findings

### Findings

| ID      | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                                                                           |
| ------- | -------- | ----- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | major    | 05    | resolved | Two boundary paths removed from `impact.boundaries`. New-file paths are described as deliverables in the Design section.                                                                                                                                                                                          |
| PROP-02 | major    | 06    | resolved | V2 plugin API documented in SR-0013 through SR-0017. Open Questions section now lists four genuine unresolved questions with source references. Motivation section updated with specific V2 API capabilities and evidence citations. Model inheritance bug acknowledged with mitigation in Model mapping section. |
| PROP-03 | minor    | 02    | resolved | TaskCreate/TaskUpdate, Workflow tool, and persistent memory added to the Deferred list with rationale.                                                                                                                                                                                                            |
| PROP-04 | minor    | 03    | resolved | Five source records (SR-0013 through SR-0017) added to `docs/research/opencode-cli-integration/sources/`, covering V2 plugin API surface, Claude Code compatibility, subagent depth, enforcement in practice, and survey gap coverage.                                                                            |

### Summary

All four findings addressed on 2026-09-21. Boundary paths corrected (PROP-01).
V2 plugin API evidence added as SR-0013 through SR-0017, Open Questions
populated, model inheritance bug acknowledged with mitigation (PROP-02). Survey
gaps added to Deferred with rationale (PROP-03). Evidence trail now covers the
design's V2 assumptions (PROP-04). Ready for re-review.

## Review — 2026-09-21 (repeat pass)

Reviewer: proposal-review-agent
Reviewed commit: 9e302527cffb4df610e34485acd334fbeb2a2619
Disposition: clean

Note: reviewed the working-tree copy. The fixes to PROP-01 through PROP-04 and
the five new source records (SR-0013 through SR-0017) are not yet committed.

### Prior Findings

All four findings from the first review verified individually:

- **PROP-01** (boundary references): the two non-existent paths were removed.
  All six remaining paths in `impact.boundaries` resolve. Set to resolved.
- **PROP-02** (open questions and evidence): five source records added with full
  provenance, evidence, contrary-evidence searches, and limitations. Open
  Questions lists four genuine API-behavior questions with source citations.
  Model inheritance bug acknowledged with a concrete workaround in the Model
  mapping section. Set to resolved.
- **PROP-03** (scope gaps): TaskCreate/TaskUpdate, Workflow tool, and persistent
  cross-session memory added to the Deferred list, each with a rationale tied to
  OpenCode's current capabilities. Set to resolved.
- **PROP-04** (design evidence): SR-0013 through SR-0017 cover the V2 plugin API
  surface, Claude Code compatibility mode, subagent depth and model inheritance,
  enforcement in practice (cc-safety-net), and survey gap coverage. The design
  section's assumptions now trace to documented evidence. Set to resolved.

### Eight-Check Results

| Check | Name                             | Result | Notes                                                                                                                         |
| ----- | -------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------- |
| 01    | Completion criteria testable     | pass   | All 19 criteria specify concrete observable outcomes verifiable without author consultation.                                  |
| 02    | Scope boundary sharp             | pass   | 11 in-scope items and 7 deferred items partition the space. Each deferred item carries a rationale.                           |
| 03    | Design decomposable              | pass   | Seven design subsections map to concrete stories. No "use a suitable approach" language.                                      |
| 04    | Impact classification consistent | pass   | cross_component, architecture_change: true, external_contract_change: true match the plugin, orientation, and contract scope. |
| 05    | Boundary references exist        | pass   | All six paths in impact.boundaries resolve in the working tree.                                                               |
| 06    | Open questions genuine           | pass   | Four questions target undocumented API behavior with cited sources. None is padding.                                          |
| 07    | Motivation justifies timing      | pass   | V2 plugin API removes the V1 blocker identified in the original survey. The enabler arrived.                                  |
| 08    | Estimate plausible               | pass   | All numeric fields are unknown with confidence: low. Honest given four open questions and an unfamiliar plugin API.           |

### Summary

All eight checks pass. All four prior findings resolved. No new findings. The
proposal is ready to plan from. Next step per feature-addition routing:
architecture_change is true, so hand off to the Requirements Agent or
Architecture Agent.
