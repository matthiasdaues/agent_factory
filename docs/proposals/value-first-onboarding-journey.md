---
schema_version: 2
title: Value-First Onboarding Journey
status: open
owner: md@matthiasdaues.de
created: 2026-09-22
updated: 2026-09-23
supersedes:

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - README.md
    - init-factory
    - packages/factory/README.md
    - packages/factory/VERSION
    - packages/factory/scripts/build-release
    - packages/factory/scripts/install-agent-factory
    - packages/factory/scripts/init-factory
    - packages/factory/scripts/update-factory
    - packages/factory/scripts/remove-factory
    - packages/factory/config/AGENTS.claude.md
    - packages/factory/config/AGENTS.codex.md
    - packages/factory/config/AGENTS.copilot.md
    - packages/factory/config/AGENTS.pi.md
    - packages/factory/config/session-menu.md
    - packages/factory/agents/virgil.md
    - packages/factory/skills/newcomer-tour/SKILL.md
    - packages/factory/playbooks/poc-spike.md
    - packages/factory/docs/factory-guide.md
    - tests/factory/test_install_agent_factory.py
    - tests/factory/test_init_factory.py
    - tests/factory/test_build_release.py

governance:
  assurance: high
  risk_domains:
    - security
    - compatibility
    - reliability
    - operations

estimate:
  as_of: 2026-09-22
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Value-First Onboarding Journey

## Summary

Agent Factory will guide a newcomer from system diagnosis to one safe result
before it asks for advanced configuration. The journey will diagnose the host,
offer confirmed fixes, install the Factory, inspect the real project without
changing it, and offer an isolated first task. The first release covers the
command-line onboarding journey from a trusted distribution remote through the
first completed task.

## Motivation

The
[onboarding journey review](../reviews/ux-review-2026-09-21-onboarding-journey.md)
found that the Factory asks for commitment and Factory knowledge before it
delivers value. The public install command is not ready to copy. Installation
guidance also contradicts the Factory's safety rules. Fitting and menu choices
then delay the first useful result.

The current journey also gives inconsistent greenfield guidance. One entry
path reports readiness while model configuration can still stop a later
dispatch. A newcomer cannot predict the next action from the installation
receipt.

The Factory needs one safe path from discovery to use. The path must show what
the system can do before it asks the user to optimize models or learn internal
workflow terms.

## Core Principles

- Diagnose before changing the host or project.
- Ask for separate confirmation before each prerequisite fix.
- Verify each accepted fix before offering the next one.
- Show the exact installation effects before requesting approval.
- Use the real project for read-only insight.
- Isolate the first task from the user's working tree.
- Explain Factory concepts when the user encounters them.
- Keep cancellation available at every change boundary.

## Design

### 1. Public bootstrap

The [root README](../../README.md) will provide one inspectable command per
approved distribution remote. Each command will download the latest stable
bootstrap script. The command will save the script instead of executing
downloaded content through a shell pipe. The same section will show how to
inspect and run the saved file.

The bootstrap will require exactly one source selector:

- `--from-local <relative-path>` will install from an Agent Factory checkout.
- `--from-remote <URL>` will install from a distribution remote.

The selectors will be mutually exclusive. A local path will resolve against
the shell's current working directory. Preflight will show its absolute path
and verify that it contains an Agent Factory source tree.

With `--from-remote`, the bootstrap will accept `--version <release>`. The
option will fetch a named release for reproducible installation. Without the
option, the bootstrap will fetch the latest stable release. Using `--version`
with `--from-local` will be an error without changes.

First installation will require `--target <path>`. The canonical example will
use `--target .`, but the bootstrap will not infer the current directory when
the option is absent. Missing target input will print usage and exit without
changes.

Preflight will resolve and display the absolute target. It will classify the
target as an existing Git repository, an empty directory, or unsupported
content. It will state whether Git initialization is proposed. It will reject
the filesystem root, the user's home directory, and any target it cannot
resolve safely.

Remote bootstrap and Factory archives will come from the selected Agent
Factory distribution remote over HTTPS. The canonical command for each remote
will pass that remote through `--from-remote`. Git remote names are local
aliases and will not become persistent source identities.

The remote URL will identify an Agent Factory release base. It will expose this
host-neutral layout:

```text
<base>/latest
<base>/releases/<version>/install-agent-factory
<base>/releases/<version>/agent-factory.tar.gz
<base>/releases/<version>/SHA256SUMS
```

Private release bases will use credentials already configured for the URL. The
bootstrap will not request, store, or print credentials.

After resolving the latest stable release, the bootstrap will use an immutable
versioned URL. Each distribution remote will publish byte-identical Factory
archives with the same SHA-256 digest. The bootstrap will refuse an archive
with a missing or mismatched digest before extraction.

A deterministic release command will build the bootstrap, Factory archive,
and checksum manifest from one versioned source tree. It will normalize archive
metadata so approved distribution remotes can publish byte-identical assets.

The installation preview will show the resolved local source path or normalized
remote URL. A remote preview will also show the resolved release URL and
digest. The receipt will record the resolved source. Updates will use that
source by default.

Changing the distribution remote will require an explicit option and
confirmation. Automatic fallback will not cross an internal or external trust
boundary. This verification checks integrity while retaining the selected
remote as a trusted party. Independent cryptographic signatures are deferred
until the project maintains a signing and key-rotation process.

### 2. Read-only preflight

The bootstrap will start with a read-only preflight. The preflight will check
the supported operating system, shell, required commands, Git state, network
access, and supported coding command-line interfaces. The preflight will not
install software or edit files.

The preflight will return one of three results:

- **Ready:** installation can proceed.
- **Ready with limitations:** installation can proceed, but named capabilities
  will remain unavailable.
- **Blocked:** installation cannot proceed until named requirements are met.

Each missing prerequisite will include its purpose, proposed fix, change
scope, reversal instructions, and verification command.

The first-release bootstrap will support native macOS and Linux on `x86_64`
and `arm64`. Windows users may run the Linux path through Windows Subsystem for
Linux when preflight passes. Other systems will receive an unsupported result
without changes.

### 3. Confirmed prerequisite fixes

After diagnosis, the user may cancel or address missing prerequisites. The
bootstrap will offer one fix at a time. It will show the exact command before
requesting confirmation.

An accepted fix will run by itself. The bootstrap will then repeat the related
check. A failed verification will stop the fix sequence and show recovery
guidance. Cancellation will report completed fixes and their reversal steps.

The first release may install uv in the user account. It may then use uv to
install a managed Python version that satisfies the Factory requirement. Each
fix will show its install location and removal command before confirmation.

Missing Git, shell support, network access, or a supported coding
command-line interface will receive diagnosis and remediation guidance only.
The bootstrap will not run `sudo`, invoke a system package manager, install a
global package, or install a coding command-line interface.

The bootstrap will not interpret blank input as consent. Non-interactive use
will not install prerequisites unless the caller supplies explicit flags for
the named fixes.

### 4. Installation preview and execution

When preflight passes, the bootstrap will show the target project, Factory
version, selected command-line interfaces, files to create, files to edit, and
the uninstall command. The user may approve or cancel installation.

Blank command-line interface selection will choose one detected active
interface only when that choice is unambiguous. Otherwise, the bootstrap will
ask again or stop. Selecting all interfaces will require an explicit choice.

The installer will verify its result. Its receipt will name every changed
path, the selected interfaces, the installed version, the uninstall command,
and one exact next command.

### 5. Read-only first project interaction

The first Factory session will summarize the project scan before it asks for
configuration. The summary will state what the Factory found, what remains
unknown, and one recommended next action. This step will not edit project
files.

The session will offer the user a relevant observation from the real project.
Examples include the detected stack, test entry point, or a missing safety
signal. The session will distinguish observed facts from recommendations.

Model-tier selection, hook decisions, and extended context capture will wait
until the chosen action requires them. A required decision will appear before
the dependent action, not during general orientation.

### 6. Isolated first task

The recommended first task will be small, reversible, and time-bounded. It
will run outside the user's active working tree. Before starting, the Factory
will show the task goal, expected duration, expected artifacts, required
decisions, and cleanup method.

For a repository with a commit, the Factory will create a detached Git
worktree from current `HEAD` under
`.current-work/onboarding-spike/<session-id>/`. It will not create a branch or
commit. Uncommitted changes from the active working tree will not enter the
sandbox.

For a repository without a commit, the Factory will create a plain sandbox at
the same path. The task will run only inside the sandbox in both cases.

The first task will use the
[`poc-spike` workflow](../../packages/factory/playbooks/poc-spike.md). The
result will be runnable or otherwise directly inspectable. The user will see
what the Factory created, which checks ran, and how to remove the result.

The Factory will explain agents, playbooks, gates, and workstreams only when
the first task uses those concepts.

At completion, the user may delete the sandbox or retain selected artifacts as
reference material. Deletion will use Git worktree removal when applicable and
will verify that the sandbox no longer exists. Retention will copy selected
artifacts into a named `docs/spikes/` path through a separate confirmation. It
will not preserve the sandbox as production work.

### 7. Handoff to real work

After the isolated task, the Factory will summarize the result and ask whether
to discard it, retain it as reference material, or begin a real workstream.
Beginning real work will use the normal playbook and approval rules. The first
task will not silently become production work.

## Scope

**In the first release:**

- An inspectable bootstrap command for each approved distribution remote.
- Deterministic release assets for the host-neutral release-base layout.
- Version-pinned bootstrap downloads through `--version`.
- Explicit local or remote source selection for installation and updates.
- Read-only prerequisite and compatibility diagnosis.
- Individual confirmation, execution, and verification for supported fixes.
- An installation preview with explicit target, changes, and reversal steps.
- Safe command-line interface selection without an implicit "all" default.
- An installation receipt with one exact next action.
- A read-only first-session scan summary and contextual recommendation.
- Deferred advanced configuration until the selected action needs it.
- An isolated, reversible first task with visible outputs and cleanup.
- A post-task choice to discard, retain, or continue into real work.
- An automated journey test covering the non-interactive safe path.
- A moderated usability protocol for newcomers who did not build the Factory.

**Explicitly deferred (do NOT plan stories for these):**

- A graphical installer. The first release must establish the command-line
  contract before adding another interface.
- Native Windows installation. The next platform slice will add a real-file
  materialization strategy for environments where links are unavailable. It
  will record copied-file digests, update copies atomically, protect modified
  copies, and remove only verified Factory-owned files. Each supported
  command-line interface must pass install, first-session, hook, update, and
  uninstall acceptance journeys before native Windows support is declared.
- Automatic installation of every missing prerequisite. The first release
  supports only reviewed fixes with clear verification and reversal.
- Personalized onboarding based on a persistent user profile. The first
  release uses current host and project evidence only.
- Automatic production changes after the first task. The user must enter a
  normal workstream and approve its workflow.
- A hosted demonstration environment. The local path must work before a
  hosted alternative adds operational scope.

## Design Details

### Consent and cancellation

Every mutating step will use an affirmative response or an explicit command
flag. Blank input means no consent. Cancellation will leave the project in a
valid state and print any completed changes.

### Output contract

Preflight and installation output will use the same terms for readiness,
limitations, blocked requirements, changes, and recovery. Errors will state
what failed, whether any change completed, and the next safe command.

### Existing onboarding work

The
[implemented newcomer onboarding proposal](newcomer-onboarding-and-incremental-brownfield.md)
remains historical context. This proposal changes the sequence around its
tour and first-spike behavior.

The implemented
[progressive fitting proposal](progressive-fitting-and-session-continuity.md)
remains the historical baseline. This proposal replaces only its session-start
fitting sequence. Its other delivered behavior remains in force unless a scope
item in this proposal changes it explicitly.

### Measurement

The journey test will record decisions before the first inspectable result.
The usability protocol will record elapsed time, unclear terms, abandonment
points, recovery attempts, and whether the user can name the next action.

On a ready host with an existing repository and one detected command-line
interface, the read-only project insight will appear within two minutes of
opening the first Factory session. The journey will require no more than three
user decisions between installation approval and that insight.

An inspectable isolated task result will appear within ten minutes of opening
the session. The journey will require no more than five user decisions before
that result. Prerequisite download time and external authentication delays will
be measured separately.

## Open Questions

None. The grilling pass resolved the first-release contract.

## Completion Criteria

- The [root README](../../README.md) contains an inspectable bootstrap command
  for each approved distribution remote.
- One release build produces the bootstrap, Factory archive, and checksum
  manifest required by the release-base layout. Repeated builds from the same
  source and version produce the same archive digest.
- A user can request a named release with `--version` and the installer reports
  the selected version before changing the system or project.
- Installation requires exactly one of `--from-local <relative-path>` and
  `--from-remote <URL>`. Invalid or conflicting source input exits without
  changes.
- A local source resolves from the invocation directory. The preview shows its
  absolute path, and the receipt records it for updates.
- First installation exits without changes when `--target` is missing,
  unresolved, or resolves to the filesystem root or user home directory.
- The bootstrap refuses release content when its SHA-256 digest is missing or
  does not match the published digest.
- The installation receipt records the normalized Agent Factory distribution
  remote, and updates use it unless the user confirms a source change.
- The installer never falls back across internal and external distribution
  remotes without explicit confirmation.
- Preflight reports **Ready**, **Ready with limitations**, or **Blocked**
  without changing the host or project.
- Preflight supports native macOS and Linux on `x86_64` and `arm64`, and the
  same Linux path under Windows Subsystem for Linux. Other systems stop before
  changes.
- Each supported prerequisite fix requires separate confirmation, shows its
  scope and reversal, and passes a related verification before the next fix.
- Cancellation reports all completed changes and leaves the target project in
  a valid state.
- Blank input never selects all command-line interfaces and never authorizes a
  prerequisite fix.
- The installation preview lists the target, version, selected interfaces,
  affected paths, and uninstall command before approval.
- The installation receipt lists changed paths and gives one command that
  opens the first Factory session.
- The first session produces a useful project-specific summary without
  changing project files.
- On the defined ready-host path, the first project insight appears within two
  minutes and no more than three user decisions after installation approval.
- Advanced configuration appears only when the selected next action requires
  it.
- The first task runs outside the active working tree and provides a cleanup
  action.
- The first task ends with inspectable output, check results, and a choice to
  discard, retain, or begin real work.
- On the defined ready-host path, the first task result appears within ten
  minutes and no more than five user decisions after installation approval.
- A participant can identify the next action without consulting separate
  documentation.
- Cancelling before installation leaves the target project unchanged. Deleting
  the first-task sandbox restores the repository to its pre-task state.
- An automated acceptance journey checks diagnosis, cancellation, explicit
  consent, installation, receipt, and first-session routing.
- A newcomer usability session records time, decisions, unclear terms,
  recovery, and understanding of the next action.

## Guiding Rule

Show one safe result before asking the user to configure the Factory.
