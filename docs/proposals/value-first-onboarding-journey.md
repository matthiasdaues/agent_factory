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
    - .pre-commit-config.yaml
    - packages/factory/README.md
    - packages/factory/VERSION
    - packages/factory/config/pre-commit-config.yaml
    - packages/factory/scripts/init-factory
    - packages/factory/scripts/update-factory
    - packages/factory/scripts/remove-factory
    - packages/factory/config/AGENTS.claude.md
    - packages/factory/config/AGENTS.codex.md
    - packages/factory/config/AGENTS.copilot.md
    - packages/factory/config/AGENTS.pi.md
    - packages/factory/config/session-menu.md
    - packages/factory/agents/virgil.md
    - packages/factory/skills/capture-context/SKILL.md
    - packages/factory/skills/newcomer-tour/SKILL.md
    - packages/factory/playbooks/poc-spike.md
    - packages/factory/docs/factory-guide.md
    - tests/factory/test_init_factory.py
    - tests/factory/test_capture_context_update.py

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

A paired installation with a new user on 2026-09-23 exposed a second gap. The
fitting presented a hook inventory before it demonstrated why the hooks matter.
It also presented two hooks that cannot run because their matching files are
gitignored. The defect is recorded in
[`BUG-0029`](../findings/BUG-0029.md).

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
digest. The receipt will record the resolved source.

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

Before installation approval, the bootstrap will recursively discover every
existing regular file named `AGENTS.md` or `copilot-instructions.md` beneath
the target. Discovery will use a fixed documented exclusion list for Factory
runtime directories, Git metadata, dependency directories, caches, and
generated build output. At minimum, it will exclude `.git/`,
`.agent-factory/`, `.current-work/`, `node_modules/`, virtual environments,
`vendor/`, `dist/`, `build/`, and language build caches.

The installation preview will list every discovered instruction file. The
installer will prepend one idempotent, marker-delimited Factory header to each
file. Repository links in the header will be relative to that file's location.
The install manifest will record each injection and its original newline state
so update and uninstall can refresh or remove only the Factory block.

Discovery will not follow external symlinks. The preview will report a
matching symlink as unchanged. The recursive pass will not create missing
nested instruction files. Existing root-orientation creation for selected
command-line interfaces remains separate.

#### Update flow

`update-factory` will read the installed source selector and resolved source
from the installation manifest. A local installation will resolve its recorded
local source again. A remote installation will query that recorded release
base for the latest stable version unless the user requests `--version`.

Update preflight will report the installed and candidate versions, source,
digest, locally modified Factory files, and instruction headers that would be
added, refreshed, or removed. `--check` will stop after this report. A normal
update will require confirmation before downloading or changing files.

The update will download and verify remote assets before changing the
installation. It will stage the replacement Factory tree, derived CLI files,
hook configuration, and instruction-header edits before applying them. A
failure will restore the previous Factory tree and headers. User-modified
Factory files will continue to stop the update unless the user explicitly
chooses the existing preservation flow.

Changing between `--from-local` and `--from-remote`, or changing the recorded
remote URL, will require an explicit source selector. The preview will call
out the trust-boundary change and require separate confirmation. A successful
update will record the selected source, immutable resolved version or local
revision, archive digest when remote, and changed paths in the manifest and
receipt.

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

When the journey reaches context capture, it will not announce only "Now
populate agent context." It will explain the activity before invoking the
[`capture-context` skill](../../packages/factory/skills/capture-context/SKILL.md).
The explanation will state that the skill will:

- scan the repository for the stack, test setup, documentation, and scope;
- identify the project-wide, technical, and domain topics that agents may need;
- show the evidence and ask the user to confirm or adjust each topic;
- create one shared routing file at `docs/agent-context.md`;
- create no legacy agent-context YAML files or `docs/agent-context/` directory;
- validate the confirmed file with `concern-lint`.

The explanation will state who uses the result. Agents read the routing map to
find the project knowledge required for a task. Humans read and edit the same
Markdown file to control those routes. The file points to project knowledge;
it does not replace or duplicate that knowledge.

Onboarding will then introduce the formal term with this explanation:
"Agent context groups project knowledge by topic—for example testing, the
frontend, or payments. The Factory calls each topic a concern. Here, concern
does not mean a problem or warning."

The user may continue, defer context capture, or cancel before the repository
scan begins.

### 6. Early gate demonstration and hook introduction

Before fitting asks the user to configure hooks, the Factory will offer a
one-minute demonstration of one deterministic check. The demonstration will
run a real Factory gate against a Factory-owned disposable fixture. It will
show the failing input, the gate's specific failure, the corrected input, and
the passing result. It will then remove the fixture and verify that the target
project did not change.

The demonstration will explain the connection to daily work: the same kind of
check can run automatically before a commit, so a specific error is corrected
before review. The user may skip the demonstration without changing hook
defaults.

After the demonstration, fitting will introduce hooks by the outcomes they
protect:

- readable and connected documentation;
- consistent specifications and architecture;
- valid Factory configuration;
- project tests and repository-specific checks.

Fitting will show only hooks that can run in the installed project. A hook that
has no matching artifacts yet will be described as available when those
artifacts exist, not as an error or a decision. Source-maintenance hooks will
appear only in the Agent Factory source repository.

Fitting will recommend a default hook set. It will ask the user only about
material trade-offs, such as automatic file changes or a slow test command. It
will not ask whether to retain a hook that cannot receive matching files.

The consumer hook set will omit `index-lint`. Model configuration will run
`matrix-lint` after an edit and before dispatch instead of relying on a
pre-commit file trigger. The Agent Factory source repository will retain
`index-lint` on tracked source inputs and run `matrix-lint` against the tracked
`packages/factory/config/model.conf` file.

### 7. Isolated first task

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

### 8. Handoff to real work

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
- Recursive Factory-header injection into every existing regular `AGENTS.md`
  and `copilot-instructions.md` outside excluded trees.
- A read-only first-session scan summary and contextual recommendation.
- Deferred advanced configuration until the selected action needs it.
- A plain-language preview before context capture that explains the work,
  output, validation, and human and agent use.
- A plain-language introduction to `concern` as a routing topic, not a problem.
- A disposable failure-to-pass gate demonstration before hook configuration.
- A hook introduction organized by protected outcomes and material trade-offs.
- Removal of consumer hooks that can match only gitignored runtime paths.
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

### Planned artifacts

The following files do not exist yet and are planned outputs rather than
inspectable current boundaries:

- `packages/factory/scripts/build-release`
- `packages/factory/scripts/install-agent-factory`
- `packages/factory/scripts/hook-demo`
- `tests/factory/test_build_release.py`
- `tests/factory/test_install_agent_factory.py`
- `tests/factory/test_hook_demo.py`

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

None.

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
- `update-factory --check` reports the installed and candidate versions,
  source, digest, local modifications, and planned header changes without
  changing files.
- A normal update verifies all remote assets before changing files. A failed
  application restores the previous Factory tree and instruction headers.
- An update stops on modified Factory-owned files unless the user explicitly
  chooses the preservation flow. Its receipt records the resolved version or
  local revision, source, remote digest when applicable, and changed paths.
- Changing the source selector or remote URL requires an explicit option and
  separate confirmation before the update proceeds.
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
- The preview lists every existing regular `AGENTS.md` and
  `copilot-instructions.md` outside the fixed exclusion set.
- Installation injects one Factory-owned header into every listed file.
  Reinstallation is idempotent, nested links resolve from their file location,
  and uninstall restores the original content and newline state.
- Matching external symlinks and instruction files inside excluded trees remain
  unchanged and are reported accurately.
- The first session reports the detected stack and test entry point, or states
  that either was not detected; it identifies at least one observed safety
  signal or its absence and recommends one next action without changing
  project files.
- On the defined ready-host path, the first project insight appears within two
  minutes and no more than three user decisions after installation approval.
- Advanced configuration appears only when the selected next action requires
  it.
- Before context capture, the user sees what will be scanned, what decisions
  they will make, that `docs/agent-context.md` is the only agent-context file
  created, how `concern-lint` validates it, and how humans and agents use it.
- Before using `concern` without a paraphrase, onboarding states that agent
  context groups knowledge by topic, calls each topic a concern, and does not
  use the word to mean a problem or warning.
- The user can defer or cancel context capture before scanning starts.
- Before hook configuration, the user can run or skip a one-minute
  demonstration that exercises a real Factory gate from failure to success.
- The gate demonstration removes its fixture and leaves the target project
  unchanged.
- Fitting explains hook value by protected outcome, recommends defaults, and
  asks only about material behavior or cost trade-offs.
- No consumer pre-commit hook uses a file filter that can match only ignored
  Factory runtime paths.
- `matrix-lint` runs after model configuration and before dispatch. Consumer
  projects do not receive an `index-lint` pre-commit hook.
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

## Review — 2026-09-23

Reviewer: proposal-review-agent
Reviewed commit: 628f665b530a08819741722b1a0279ff640ad2bf
Disposition: findings

### Findings

| ID      | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                                                                                                                                                                       |
| ------- | -------- | ----- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | major    | 05    | resolved | Four boundary paths do not resolve at the reviewed commit: `packages/factory/scripts/build-release`, `packages/factory/scripts/install-agent-factory`, `tests/factory/test_install_agent_factory.py`, and `tests/factory/test_build_release.py`. The boundary list must reference files a reviewer can inspect. List planned files separately or remove them from `impact.boundaries` until they are tracked. |
| PROP-02 | major    | 03    | resolved | The scope includes "Explicit local or remote source selection for installation and updates." The Design section covers the update flow in two sentences. A planning agent cannot write update stories from "Updates will use that source by default." Add an update-flow design subsection or move updates to the deferred list with a stated reason.                                                         |
| PROP-03 | minor    | 01    | resolved | Completion criterion "The first session produces a useful project-specific summary" contains the subjective term "useful." The Design section already defines observable content: detected stack, test entry point, missing safety signal. State those observables in the criterion so a tester can verify it without subjective judgment.                                                                    |

### Summary

Six of eight checks pass. Two major findings prevent planning readiness. Four boundary paths reference files that do not exist at the reviewed commit (PROP-01). The update flow is in scope but the Design section does not support story decomposition for it (PROP-02). One minor finding asks a subjective completion criterion to name the observable content the Design already specifies (PROP-03). Address the two major findings and re-open for a repeat pass.

### Author response — 2026-09-23

- **PROP-01 addressed:** `impact.boundaries` now contains only existing paths.
  The six new files appear under **Planned artifacts**.
- **PROP-02 addressed:** **Update flow** now defines source resolution,
  preview, verification, rollback, local-change handling, source changes, and
  receipt data. Matching completion criteria cover each behavior.
- **PROP-03 addressed:** the first-session criterion now names the stack, test
  entry point, safety signal, recommendation, and no-change requirement.

The proposal is open for an independent repeat review.

## Review — 2026-09-23 (repeat)

Reviewer: proposal-review-agent
Reviewed commit: 9818c1615ba01857559aafdee7807c5077f2ad6d
Disposition: findings

### Prior findings

| ID      | Prior status | New status | Verification                                                                                                                                                                                                                                       |
| ------- | ------------ | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | open         | resolved   | The four non-existent paths are removed from `impact.boundaries` and listed under **Planned artifacts**. All 34 boundary paths resolve at the reviewed commit.                                                                                     |
| PROP-02 | open         | resolved   | The **Update flow** subsection now covers source resolution, version queries, `--check` preview, confirmation, staged replacement, rollback, local-change handling, source selector changes, and receipt data. Matching completion criteria added. |
| PROP-03 | open         | resolved   | The first-session criterion now states detected stack, test entry point, safety signal or its absence, one recommended next action, and no file changes.                                                                                           |

### Fresh inspection

| #   | Check                            | Result | Detail                                                                                                                                                                                      |
| --- | -------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01  | Completion criteria testable     | pass   | Each criterion names an observable outcome or measurement. Usability criteria define protocol-recorded evidence.                                                                            |
| 02  | Scope boundary sharp             | pass   | The In and Deferred lists partition the space. Confirmed fixes versus automatic installation is clean. No item reads as either.                                                             |
| 03  | Design decomposable              | pass   | All nine design subsections support INVEST story decomposition, including the expanded update flow. One gap in Planned artifacts inventory (see PROP-04).                                   |
| 04  | Impact classification consistent | pass   | Cross-component scope, architecture change, and external contract change match the design: new distribution system, area vocabulary rename, hook reconfiguration, public install contract.  |
| 05  | Boundary references exist        | pass   | All 34 paths in `impact.boundaries` resolve at the reviewed commit. Planned artifacts correctly list six files that do not yet exist.                                                       |
| 06  | Open questions genuine           | pass   | "None" is defensible after grilling and the first review pass. No unresolved questions hide in the design.                                                                                  |
| 07  | Motivation justifies timing      | pass   | A traceable UX review, a broken install command, a safety-rule contradiction, and a paired-installation finding ([BUG-0029](../findings/BUG-0029.md)) distinguish this from a backlog item. |
| 08  | Estimate plausible               | pass   | `unknown` at low confidence with judgment basis is honest for a cross-component proposal with 34 boundary files. The template endorses `unknown` over fabricated precision.                 |

### New findings

| ID      | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                                                                               |
| ------- | -------- | ----- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-04 | minor    | 03    | resolved | Design section 6 introduces `area-lint` as a new validator and describes `concern-lint` as its deprecated wrapper. Neither `packages/factory/scripts/area-lint` nor `tests/factory/test_area_lint.py` appears in the Planned artifacts list. Add both so the inventory of new files is complete for a planning agent. |

### Summary

All three prior findings are resolved. The author removed non-existent paths from boundaries, expanded the update-flow design to support story decomposition, and replaced the subjective first-session criterion with observable outcomes. All eight checks pass. One new minor finding asks the Planned artifacts section to list `area-lint` and its test, which the Design section unambiguously introduces but the inventory omits. The proposal is ready to plan from once that inventory is complete.

### Author response — 2026-09-23

**PROP-04 resolved by design correction:** `concern` remains the canonical
Factory term. Onboarding now paraphrases it as a routing topic and explicitly
states that it does not mean a problem or warning. The proposed `area-lint`,
`areas:` field, compatibility parser, and migration artifacts have been removed.
