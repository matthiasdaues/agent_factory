---
schema_version: 2
title: OpenCode CLI Integration
status: open
owner: Agent Factory maintainers
created: 2026-09-20
updated: 2026-09-21
supersedes:

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - packages/factory/scripts/init-factory
    - packages/factory/config/AGENTS.md
    - packages/factory/config/AGENTS.opencode.md
    - packages/factory/config/plugins/agent-factory.ts
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
servers, and child sessions. A later check against the current
[OpenCode V2 plugin API](https://opencode.ai/v2/docs/build/plugins/) and
[permission model](https://opencode.ai/v2/docs/permissions) found additional
safety controls. OpenCode V2 plugins can intercept tools, evaluate permissions,
control sessions, and manage Git worktrees.

The original survey's blocker conclusion therefore does not apply to OpenCode
V2. The Factory needs a dedicated plugin that maps those controls to existing
Factory invariants.

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

None. The proposal defers no decision needed to plan the first release.

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
