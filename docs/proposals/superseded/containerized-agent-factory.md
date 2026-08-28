---
schema_version: 2
title: "Containerized Agent Factory Distribution"
status: superseded
owner: agent-factory
created: 2026-08-07
updated: 2026-08-10
supersedes: factory-cli-security-hardening.md

impact:
  scope: cross_project
  architecture_change: true
  external_contract_change: true
  boundaries:
    - factory/scripts/init-factory
    - factory/scripts/run-playbook
    - factory/scripts/run-tests
    - factory/config/pre-commit-config.yaml
    - factory/config/hooks/block-dangerous-git.sh
    - factory/scripts/commit-safe
    - factory/docs/factory-guide.md
    - docs/arc42/architecture.dsl

governance:
  assurance: critical
  risk_domains:
    - security
    - data_integrity
    - compatibility
    - reliability
    - operations

estimate:
  as_of: 2026-08-07
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
---

# Feature Request: Containerized Agent Factory Distribution

> **Superseded on 2026-08-10.** This proposal is retained as design history.
> Its scope is replaced by
> [Agent Execution Isolation and Optional Container Distribution](../agent-execution-isolation-and-distribution.md),
> which makes multi-path host filesystem delegation the primary security goal,
> treats containers as an optional pinned environment, and leaves privileged
> Git authorization and publication to a future, separately accepted
> orchestrator security proposal. Existing guardrails remain in force meanwhile.

## Summary

Publish Agent Factory as a versioned OCI image and run it against a new or
existing project mounted read-write at `/workspace`. A trusted host launcher
and policy broker select a pinned image, prove the rootless runtime's UID
mapping before mounting the project read-write, mediate Git authority, and
expose no other host-writable path.

The image becomes the canonical environment for Factory initialization,
playbook execution, Git operations, deterministic gates, and an attached
shell. Host Git and host project tooling are excluded once a project is
delegated because repository-controlled hooks and configuration are untrusted.
The first release supports rootless Podman on native Linux. Rootless Docker
and reproducible execution of foreign project hooks require later, independent
evidence.

## Motivation

The current host-native subprocess model gives an agent the invoking user's
filesystem and network authority. The
[sandboxed Factory PoC](../../../poc/sandboxed-factory/README.md) demonstrates
that a rootless container with only the project mounted meaningfully improves
host-filesystem isolation, preserves project writes and cross-phase state, and
can enforce a no-network posture. It also establishes that an in-container
allowlist proxy is not an enforced selective-egress boundary under rootless
slirp networking.

The PoC used Podman's `--userns=keep-id`. That result must not be generalized
to rootless Docker: under rootless Docker, container UID `0` normally maps to
the unprivileged host user that owns the daemon, while a numerically identical
nonzero container UID normally maps into a subordinate UID range. Blindly
running `--user "$(id -u):$(id -g)"` can therefore make a host-owned bind mount
unwritable or create subordinate-owned files.

The current installation also assumes host Python, `uv`, pre-commit, language
toolchains, and an AI coding CLI. Providing the Factory as an image should
remove those host dependencies without weakening the principle that agents
create artifacts and mechanically triggered gates validate them. Git hooks,
pre-commit integration, pre-push checks, and phase gates therefore need one
image-owned gate implementation, not parallel host and container
implementations.

The practical first-release gain is deliberately narrower than general
sandboxing: it confines host-filesystem access while an interactive agent may
still receive a full shell, provider credentials, and unrestricted rootless
networking under an explicit human grant. Structured command allowlisting and
selective egress remain separate hardening layers governed by
[Factory CLI Security Hardening](factory-cli-security-hardening.md).

## Core Principles

- The rootless runtime is the host boundary; repository-local instructions and
  hooks are not security boundaries.
- Mount only the approved project read-write; never mount the host home,
  container-runtime socket, or an arbitrary parent directory.
- Prove effective write ownership before granting a real project mount; do not
  infer it from matching UID numbers.
- Never recursively `chown` or broadly `chmod` a mounted project.
- Keep image selection and runtime policy in host-controlled state, outside the
  agent-writable project.
- Run Git operations and deterministic gates in one pinned execution
  environment.
- Make the Factory gate runner authoritative; Git hook frameworks are adapters.
- Separate dependency acquisition from offline validation.
- Fail closed on unsupported hooks, repository topology, permissions, or stale
  dependency preparation.
- Scope every security claim to the tested runtime, mount set, and network
  posture.

### Threat model and trust boundary

The delegated agent and every file below the approved project path are
untrusted. This includes `.git/config`, hook programs, hook-manager
configuration, tool configuration, generated files, and persistent Factory
state. A repository-controlled program must never be executed directly by a
host Git process or the host launcher.

The trusted computing base is limited to:

- the human-operated launcher binary and its installation directory;
- an owner-only host installation record;
- the selected rootless container runtime and host kernel;
- the approved image identified by digest; and
- explicit credential and network grants for one invocation.

This proposal defines the **containerized profile** of
[Factory CLI Security Hardening](factory-cli-security-hardening.md). Within
this profile, verified user-namespace isolation plus a single approved bind
mount replaces the hardening proposal's dedicated host account. Files retain
the invoking user's ownership, but the agent process has no host-user process
authority outside the namespace. This substitution is valid only within the
stated runtime-compromise exclusion; baseline and hardened-workstation
profiles still require the dedicated `agent-factory` account.

The launcher protects the host outside approved mounts. It does not protect
the delegated project from its agent, defend against a compromised host
kernel or container runtime, or make network-visible credentials safe from a
process deliberately granted both those credentials and network access.

Plain host commands executed inside an agent-writable repository are outside
the boundary: host Git may execute repository-selected hooks, and project
build tools may execute repository code. The supported workflow therefore
does not use host Git or host project tooling after delegation.

## Design

### Distribution

Publish a multi-architecture image by immutable digest and human-readable
version tags:

```text
ghcr.io/datenschoenheit/agent-factory:0.2.0
ghcr.io/datenschoenheit/agent-factory:0
ghcr.io/datenschoenheit/agent-factory@sha256:<digest>
```

The image contains:

- immutable Factory content under `/opt/agent-factory/factory`;
- the orchestrator and its pinned Python dependencies;
- Git, Python, `uv`, Node.js, and the supported AI coding CLIs;
- pinned Factory-owned linters and formatters;
- a runtime probe and permission-aware entrypoint;
- the internal `init`, `update`, `run`, `shell`, `git`, `gate`, `prepare`, and
  `doctor` commands.

Release 1 contains `prepare` only as an unavailable reserved command that
reports its release-2 status. It does not build project toolchain images.

The image filesystem is read-only at runtime. `/tmp`, `/run`, and the default
runtime home and caches are ephemeral `tmpfs` mounts. The approved project is
mounted at `/workspace`. Durable Factory artifacts live below the already
ignored `/workspace/.current-work/state/` namespace, but deterministic gates
do not consume executable code, configuration, plugins, or tool caches from
that agent-writable location.

### Trusted host launcher

A small host launcher named `agent-factory` is the supported entry point. Its
only host prerequisites are the launcher, Git for project discovery, and one
supported rootless container runtime.

```bash
agent-factory init ./new-project
agent-factory init ./existing-project
agent-factory run --playbook brownfield-development
agent-factory git commit -m "feat: example"
agent-factory shell
agent-factory doctor
agent-factory publish --remote origin --refspec refs/heads/task:refs/heads/task
```

The launcher:

1. Resolves the canonical project path without evaluating project-provided
   shell text.
2. Rejects `/`, the host home, unresolved paths, and mounts broader than the
   approved project.
3. Reads the approved image digest and runtime policy from host-controlled
   configuration, not from the project.
4. Detects Podman and verifies its supported rootless mode.
5. Runs the runtime-specific UID-mapping probe.
6. Mounts the project read-write only after the probe succeeds.
7. Drops capabilities, enables `no-new-privileges`, and omits the runtime
   socket and host home.
8. Uses no network for hooks and gates; commands that require network use a
   separate explicit posture.

The launcher starts from a sanitized environment. It ignores project-local
runtime selection and caller-controlled Podman connection, configuration, and
plugin variables. It invokes an
installation-pinned runtime executable and an owner-controlled rootless Unix
socket. It verifies the socket and trusted configuration are regular or
expected socket types, owned by the invoking user, not group/world writable,
and reached without a symlink through an untrusted directory.

Trusted installation metadata lives outside the project, keyed by a stable
project identifier and canonical path, for example:

```text
$XDG_CONFIG_HOME/agent-factory/installations/<project-id>.json
```

It records the approved image digest, runtime kind and endpoint, canonical
project path, project directory device/inode identity, and network policy. The
record and every parent below the user's configuration directory must be owned
by the invoking user and not group/world writable. Records are created and
replaced atomically without following symlinks. Immediately before the mount,
the launcher reopens the project path, rejects symlink traversal, and verifies
that its device/inode identity still matches the approved record. A
project-local manifest may report the same values for diagnosis, but it cannot
select an image, runtime, endpoint, mount, credential, or network posture.
Changing trusted values requires an explicit human launcher command.

### Runtime-specific identity

The launcher supports one secure profile in release 1:

| Runtime               | Container identity                                           | Host result                                    |
| --------------------- | ------------------------------------------------------------ | ---------------------------------------------- |
| Rootless Podman/Linux | `--userns=keep-id`, caller UID/GID inside the user namespace | Preserves the invoking user's numeric identity |

The container runs with all capabilities dropped, `no-new-privileges`, a
read-only root filesystem, and the restricted mount set.

Before mounting a real project read-write, the launcher creates a host-owned
temporary probe directory, mounts it into the candidate image, and asks the
container to create and mode-change a probe file. The launcher verifies that:

- the resulting file is owned by the invoking host UID;
- the file is writable and removable by that user;
- its executable bit can be set and it can execute when the host mount permits
  execution; and
- no subordinate-UID ownership leaks onto the host.

The launcher removes the probe and stops before mounting the project if any
assertion fails. Rootless Docker, Docker Desktop, rootful runtimes, group-only
writable projects, and other user-namespace modes are not inferred from this
profile and are deferred until independently tested. A rootless Docker spike
must specifically test `CAP_CHOWN` removal, subordinate-UID ownership attacks,
setuid creation, and ordinary-user recovery before Docker can enter scope.

### Project preflight and permissions

Preflight has three explicit stages:

1. The runtime identity probe uses only a launcher-created temporary directory;
   failure prevents any project mount.
2. The project is mounted read-only. `doctor` validates canonical identity,
   repository topology, symlinks, hook ownership, mount flags, and trusted
   installation metadata without running project code.
3. The project is remounted in a fresh container read-write. A bounded
   capability probe operates only in a launcher-created
   `.current-work/probe/<nonce>/` directory, records its intended changes,
   removes them, and verifies that cleanup completed before workflow execution.

The read-write capability probe tests effective operations rather than only
inspecting mode bits:

- create, atomically rename, and remove a regular file under
  `.current-work/`;
- create a directory and a representative lock file;
- set and execute a file's executable bit;
- write every approved in-project worktree;
- run image-owned `git status` with an invocation-local, exact
  `safe.directory=/workspace` value; and
- confirm that a newly created file has the expected host ownership.

Image-owned and generated scripts are packaged or created with their intended
modes. Unexpected mode drift fails validation. The runtime never repairs a
project through recursive ownership or permission changes and never uses
world-writable mode as a fallback.

Failure at stage 1 prevents a project mount. Failure at stage 2 prevents a
read-write mount. Failure at stage 3 may have created only the declared probe
directory; an incomplete cleanup is reported as a bounded mutation requiring
manual inspection. The proposal does not describe stage-3 failures as
occurring before all project mutation.

The default umask is `0022`. Shared-group operation and `0002` are deferred
until supplementary-group behavior is proven for each runtime. A project that
is writable only through group membership receives an actionable failure in
release 1.

### New and existing projects

For a new project, the launcher creates the requested directory as the host
user before mounting it. For a new or existing project, the image invokes the
existing initializer with immutable image content as its source:

```bash
/opt/agent-factory/factory/scripts/init-factory \
  --source /opt/agent-factory \
  --target /workspace
```

Initialization retains the current non-interference, collision, idempotency,
and reversible-removal contracts of
[`init-factory`](../../../factory/scripts/init-factory). It does not overwrite
project-owned configuration or change unrelated modes. Preflight resolves all
destinations before mutation; a collision stops at the existing documented
boundary.

`update` stages a new Factory copy under `.current-work/`, validates generated
CLI adapters and gates, and replaces only Factory-owned content. It records the
installed version and image digest for diagnosis, while the host-controlled
installation record remains the execution trust root.

### Repository topology

Release 1 supports one Git repository wholly contained beneath `/workspace`.
Factory-created worktrees live beneath:

```text
/workspace/.current-work/worktrees/
```

`doctor` rejects external worktrees, external Git object alternates, submodule
worktrees outside `/workspace`, and required symlink targets outside the
mount. Later support may add individually resolved and approved mounts; it must
not mount an arbitrary parent directory for convenience.

### Authoritative deterministic gate runner

The image owns one gate interface:

```text
af-internal gate staged
af-internal gate full
af-internal gate phase <state>
```

The modes share implementations and differ only in declared scope:

| Invocation           | Scope                                                        |
| -------------------- | ------------------------------------------------------------ |
| `gate staged`        | Structural checks, format/lint checks, and staged-file tests |
| `gate full`          | All applicable checks and the complete project test suite    |
| `gate phase <state>` | State-machine conditions plus the required staged/full gates |

The gate runner, not `.pre-commit-config.yaml`, owns ordering, applicability,
exit semantics, and reporting. It invokes the current Factory scripts such as
[`run-tests`](../../../factory/scripts/run-tests) and the applicable deterministic
linters. Git hooks, pre-commit, pre-push, and phase transitions are thin
adapters to this interface.

Formatting and checking are distinct operations:

```bash
agent-factory format       # may modify project files
agent-factory gate staged  # check-only
agent-factory gate full    # check-only
```

Hooks and phase gates never stage changes. A project may explicitly retain
format-on-commit compatibility behavior, but a formatter change makes the hook
fail so the human or agent can review and stage it.

### Canonical Git execution

The reference workflow runs Git inside the pinned image:

```bash
agent-factory git commit ...
agent-factory git status
```

Agent-created commits, attached-shell commits, hooks, phase gates, and
playbook-driven Git operations therefore share the same image, mounts,
environment, dependency state, and network policy. This is the only supported
Git path after a project is delegated to an agent.

Plain host `git commit`, `git push`, and other host commands that may execute
repository-controlled programs are deliberately not bridged. Git selects and
starts a hook before any proposed hook dispatcher could establish the
container boundary; an agent-writable hook or local Git configuration could
therefore execute with the invoking host user's authority. No repository hook
can safely repair that ordering.

For human ergonomics, the launcher accepts Git-compatible arguments and
forwards terminal input, standard input, output, signals, and exit status to
Git inside the approved image. Shell completion and an optional, separately
installed `af-git` launcher symlink may abbreviate `agent-factory git`; a Git
alias is not used because repository-local configuration can override it.
Documentation warns humans not to use plain host Git in a delegated repository.
Factory phase gates remain authoritative even if a human ignores that warning
and creates a host-side commit with hooks disabled.

### Git policy, gate authorization, and publication

The launcher exposes structured Git operations, not an unrestricted argument
pass-through. Its image-owned policy replaces the security-relevant behavior
of `factory/config/hooks/block-dangerous-git.sh` and uses
`factory/scripts/commit-safe` as the implementation behind the structured
`git commit` operation. Repository-local CLI hooks retain only
defense-in-depth feedback.

Normal agent sessions may inspect Git state, create objects and task-branch
commits, and run declared gates. They receive no publication credential. The
policy denies push, forced reference movement, reference deletion, destructive
reset and clean operations, protected-ref mutation, remote changes, hook-path
changes, and gate bypasses. Because an interactive shell can bypass a local
wrapper and damage `.git`, local repository state remains recoverable scratch;
remote branch protection and backups are deployment prerequisites.

Gate authorization lives in owner-only host state beside the trusted
installation record, never below `/workspace`. The launcher writes a record
only after an image-owned gate succeeds. Each record binds:

- the project identifier and canonical device/inode;
- gate kind and policy version;
- the full 40-character commit SHA and, where applicable, target ref and SHA;
- approved image and toolchain digests;
- a nonce, creation and expiry times, and one-time-use status.

An operation that requires a gate and the protected mutation it authorizes run
as one broker transaction. The broker re-resolves every bound SHA immediately
before mutation, consumes the authorization atomically, and refuses stale,
missing, replayed, project-local, or mismatched records. Existing
`.current-work/verify-base-ok` and `.current-work/premerge-check-ok` files
may remain as diagnostic compatibility artifacts during migration, but they
grant no authority.

Publication is a separate human operation:

```bash
agent-factory publish \
  --remote origin \
  --refspec refs/heads/task:refs/heads/task
```

The launcher displays the resolved remote URL, source SHA, destination ref,
and expected movement and requires a fresh confirmation on the host launcher's
controlling terminal. Confirmation input is never accepted from the container,
project files, redirected standard input, or an agent-generated environment
value. It then starts one container under the `factory-publisher` capability
with a short-lived credential restricted to the named remote and allowed ref
class.
The credential is absent from ordinary `run`, `shell`, `git`, hook, and gate
containers. Force updates, deletions, and protected destinations are denied in
release 1 rather than approvable. The remote must independently enforce branch
protection and required CI.

### External audit

The launcher appends one redacted record per invocation to owner-only,
append-only host storage outside the workspace. The record contains timestamp,
session and approval identifiers, canonical project path and device/inode,
runtime profile, image and toolchain digests, network posture, credential and
Git capabilities, structured command, full relevant commit SHAs, policy
decision, exit status, duration, and resource usage. Publication additionally
records the resolved remote and ref movement.

The container cannot mount or write the audit sink. Failed and denied
operations are recorded too. If the configured sink cannot accept an event,
commands requiring credentials, network, protected Git mutation, or a consumed
gate authorization fail closed; offline read-only diagnosis may continue with
an explicit degraded-audit warning.

### Git-hook integration

Initialization detects configured hook paths, existing hook files, pre-commit,
Husky, and recognized hook managers before changing hook configuration. It
selects exactly one recorded strategy:

1. **Factory-owned:** install thin in-container adapters where no hook owner
   exists.
2. **Pre-commit adapter:** in release 1, use this only when every configured
   entry is Factory-owned; otherwise select manual. Add prefixed local Factory
   gate entries through the established merge contract.
3. **Recognized manager adapter:** in release 1, use this only when the manager
   can invoke the Factory gate without also running foreign hooks; otherwise
   select manual.
4. **Manual:** stop before mutation and provide exact wiring instructions when
   safe composition cannot be proven.

The Factory never splices arbitrary shell hook bodies. All executed hooks run
inside a container, never directly on the host. Release-1 Factory-owned hooks
run in the base image; release-2 foreign hooks may run only in an admitted
project toolchain image.
`doctor` verifies the recorded strategy before each Git mutation rather than
assuming an earlier result is still current. A session may reuse a host-owned
validation record for up to 30 seconds when it binds the project device/inode,
image digest, Git configuration hash, hook-path and hook-manager inventory
hash, and current full SHA. Any mismatch or protected operation forces a fresh
check. The warm-path budget is 500 ms at the 95th percentile on the supported
test host. Git's explicit `--no-verify` bypass still exists, but bypassing a
local hook does not bypass a phase gate.

The adapters map as follows:

```text
pre-commit → gate staged
pre-push   → gate full
phase      → gate phase <state>
```

### Project hook and dependency preparation

The universal Factory image guarantees only Factory-owned gates. In release 1,
`doctor` classifies existing project hooks without executing them. Factory-owned
hooks run offline; every foreign project hook, including one that appears
image-compatible, receives the `manual` outcome. It is not part of the
deterministic gate or first-release completion claim.

Release 2 may introduce `prepare` and classify foreign hooks as follows:

| Class | Meaning                                        | Potential release 2 behavior                             |
| ----- | ---------------------------------------------- | -------------------------------------------------------- |
| A     | Image-compatible and offline                   | Run inside the project toolchain image                   |
| B     | Requires dependency or hook-environment setup  | Require `agent-factory prepare`                          |
| C     | Host-bound, service-bound, or nested-container | Exclude from the deterministic claim; require a decision |
| D     | Unsafe or unclassifiable                       | Fail closed                                              |

In release 2, `agent-factory prepare` is the only normal
dependency-acquisition step. With
an explicit network posture, it builds a project toolchain image `FROM` the
approved Factory digest. That image contains the environments implied by
project lockfiles and supported local hook declarations.

Preparation is adapter-driven and fail-closed. Each supported ecosystem
adapter declares a closed input set: manifests, lockfiles, tool-version and
package-manager configuration, patches, local path dependencies, submodule
identities, referenced hook files, and the subset of environment values that
can affect resolution or installation. Inputs outside the adapter's declared
model, lifecycle scripts requiring undeclared services, and dependencies that
escape `/workspace` are unsupported rather than silently omitted.

The build uses a generated context containing only the declared dependency
inputs. It pins the base by digest, records the builder and target-platform
identity, and grants build secrets only to steps that declare them. The
preparation manifest binds the derived image digest to the ordered input
inventory, each content hash, adapter version, Factory digest, platform, and
resolution parameters. Registry publication and signing remain deferred, but
local consumption verifies the resulting image's digest and manifest labels
before execution.

Before an offline gate runs, it recomputes the complete adapter inventory and
hashes. An added, changed, missing, or newly unsupported input fails with an
instruction to run `agent-factory prepare`; the gate never silently enables
networking or trusts mutable cache contents as proof of reproducibility.

Derived images are content-addressed and reference-counted by trusted
installation records. `agent-factory prepare prune` defaults to a dry run,
retains every referenced digest plus the two most recent unreferenced digests
per project for 30 days, and requires explicit human confirmation before
deletion. A configurable owner-controlled disk quota stops preparation before
the limit is exceeded and reports reclaimable digests. These lifecycle
requirements are release-2 completion criteria, not release-1 work.

### Home, caches, credentials, and network

Interactive agent sessions may opt into durable, ignored project state:

```text
/workspace/.current-work/state/agent-home
/workspace/.current-work/state/agent-cache
```

That state is untrusted and is never mounted as the home, configuration,
plugin, executable, or dependency cache for `doctor`, `git`, hooks, or gates.
Those commands receive a fresh tmpfs home and cache, a fixed image-owned
`PATH`, a sanitized environment, and no user/site plugin discovery. In release
2, prepared dependencies come only from the verified project toolchain image.
Commands that intentionally consume durable agent state are outside the
deterministic gate claim and report that fact.

The host home, `.ssh`, cloud configuration, password stores, browser profiles,
and container-runtime socket are not mounted. Credentials enter only through
an explicit allowlist of environment variables, runtime secrets, narrowly
mounted read-only files, or an opt-in SSH-agent socket. Credential mounts are
never writable.

Every command has one declared network posture:

| Command                                   | Posture                 | Credential scope                                    |
| ----------------------------------------- | ----------------------- | --------------------------------------------------- |
| `init`, `update`, `doctor`                | `deny`                  | none                                                |
| `git`, hooks, `format`, `gate`            | `deny`                  | none                                                |
| `run`, `shell`                            | explicit `standard`     | invocation allowlist; no Git publication credential |
| `publish`                                 | restricted publication  | short-lived named-remote/ref credential             |
| `image fetch <digest>`                    | host runtime networking | registry read only; explicit human operation        |
| `prepare` and `prepare prune` (release 2) | `standard` / `deny`     | declared build secrets / none                       |

`deny` means runtime `--network none`. `standard` means unrestricted rootless
runtime networking and is never inferred: a human must grant it for the
invocation. `publish` permits only the resolved Git remote through an external
control or a credential whose server-side policy makes other destinations and
refs unusable; it is not the interactive `standard` posture.

The image contains the pinned pre-commit executable and every Factory-owned
hook environment needed by initialization. `init` invokes that packaged
executable directly rather than `uvx`, and `update` does not acquire
dependencies. Foreign project hook environments remain manual in release 1,
so `init`, `update`, and `doctor` complete under `deny` on a cold host.

Selective egress enforcement is deferred. An HTTP proxy may improve
observability and configuration, but the Factory must not call it a security
boundary under rootless slirp networking.

### Failure behavior

The launcher and internal entrypoint fail before workflow mutation when:

- the runtime is not a supported, verified rootless profile;
- the UID-mapping probe does not preserve host ownership;
- the approved image digest is absent locally during Git, a hook, or a gate;
- the project is read-only, `noexec`, group-only writable, or has unsupported
  Git topology;
- existing hooks cannot be composed safely;
- a foreign project hook is requested in release 1;
- in release 2, dependency inputs differ from the preparation manifest;
- a hook is host-bound or unclassifiable; or
- the requested operation needs a host mount or network capability outside its
  declared posture.

The bounded read-write capability probe is the sole exception: it may create
only its nonce-scoped probe directory and must remove it before continuing.

Errors name the failed assertion, affected path or runtime, and one supported
remediation. The implementation does not fall back to rootful execution,
broader mounts, `chmod 777`, recursive `chown`, Docker-socket exposure, or
implicit networking.

## Scope

**In the first release:**

- A versioned, digest-addressable Agent Factory OCI image for Linux AMD64 and
  ARM64.
- A trusted host launcher and Git policy broker for native Linux rootless
  Podman.
- Runtime detection and a destructive-target-safe UID/write/execute probe
  before the project is mounted read-write.
- `init`, `update`, `doctor`, `shell`, `run`, structured `git`, `publish`,
  `format`, and `gate` commands.
- New and existing project initialization using the current non-interference
  and removal contracts.
- One `/workspace` host-writable mount, in-project Factory worktrees, and
  project-local ignored runtime state.
- An image-owned staged/full/phase gate runner used by Git, pre-commit,
  pre-push, and playbook phase transitions.
- Container-only Git execution with Git-compatible launcher argument and
  terminal forwarding.
- Image-owned dangerous-Git denial, `commit-safe` integration, host-owned
  SHA-bound gate authorizations, and separately credentialed publication.
- Hook ownership detection with Factory-owned or manual outcomes; no foreign
  project hook execution.
- An external append-only audit record for every invocation and policy
  decision.
- `deny` and `standard` network postures with no selective-egress security
  claim.
- Automated proof across non-1000 UIDs, existing repositories, worktrees,
  hooks, formatting, linting, tests, Git authority, audit, and network failure
  modes.

**In release 2, under separate acceptance:**

- `prepare`, versioned ecosystem adapters, and derived project toolchain
  images.
- Foreign hook classes A and B when their complete dependency-input model is
  supported.
- Content-addressed image retention, quota enforcement, and confirmed pruning.

**Explicitly deferred (do NOT plan stories for these):**

- Rootful Docker as a supported secure profile.
- Rootless Docker until its identity and recovery spike passes.
- Docker Desktop, Windows bind mounts, and macOS bind mounts.
- Group-only writable and shared-group repositories.
- External worktrees, external Git object stores, and project mounts broader
  than one repository.
- Enforced selective egress; a dedicated external gateway or host firewall is
  required for that guarantee.
- Nested Docker-based project hooks or exposure of Docker/Podman sockets.
- Automatic support for unrecognized hook managers and arbitrary remote
  pre-commit environments.
- Structured command allowlisting and enforced selective provider egress from
  the broader security-hardening proposal.
- Plain host Git or host project tooling as part of the secured workflow.
- Managed registry publication, image signing infrastructure, SBOM policy, and
  vulnerability-remediation service levels beyond emitting build artifacts
  needed for later adoption.
- Protection of files inside the delegated project from an agent authorized to
  write that project.

## Design Details

### Security claim

The release may claim:

> On verified supported rootless Podman, Agent Factory confines host
> filesystem mutation by agent-executed processes to the approved project bind
> mount, executes Factory-owned gates in a pinned image with fresh runtime
> state, keeps gate and publication authority outside the agent-writable
> project, and preserves host ownership through a mechanically tested Podman
> identity mapping. This claim excludes runtime or kernel compromise, foreign
> project hooks, unrestricted-command prevention, selective egress, and any
> host command a human runs directly in the agent-writable repository.

It must not claim that arbitrary project hooks are deterministic, mutable
caches are reproducible, Git hooks are unbypassable, an in-container proxy
enforces selective egress, the containerized profile implements executable
allowlisting, or rootless Docker is supported.

### Acceptance proof matrix

The owning automated test layer must cover each distinct contract without
duplicating deterministic linter rules:

| Case                                             | Required result                                             |
| ------------------------------------------------ | ----------------------------------------------------------- |
| Rootless Podman with `keep-id`                   | Writes retain invoking host ownership                       |
| Rootless Docker                                  | Refused as a deferred, unproved runtime                     |
| Host UID other than `1000`                       | Probe, initialization, gates, and Git succeed               |
| Rootful or unrecognized runtime                  | Refused before the project is mounted read-write            |
| Group-only writable repository                   | Refused with an explicit deferred-capability message        |
| New project                                      | Directory and Git repository initialize as the host user    |
| Existing project                                 | Existing files, history, hooks, and configuration survive   |
| Read-only or `noexec` project                    | Refused before workflow execution; probe effects bounded    |
| Existing `core.hooksPath`                        | Preserved through a supported adapter or stopped safely     |
| Existing pre-commit or recognized hook manager   | Factory-owned hooks run; foreign hooks resolve to manual    |
| Unrecognized hook manager                        | No mutation; exact manual wiring guidance                   |
| In-project Factory worktree                      | Git operations and gates succeed                            |
| External worktree or object alternate            | Rejected without mounting a broader parent                  |
| Formatter detects changes                        | Check fails without staging files                           |
| Agent attempts push without publication grant    | Denied; no publication credential is present                |
| Agent attempts force update or ref deletion      | Denied, including during an approved publication            |
| Publisher targets protected ref                  | Denied locally and by remote policy                         |
| Containerized commit                             | Arguments, standard input, signals, output, and status pass |
| Approved image absent during Git command         | Command fails without pulling or enabling network           |
| Modified project-local image manifest            | Trusted host-selected digest remains unchanged              |
| Replaced project hook or local Git configuration | Executes only inside the approved image                     |
| Tampered host installation record or symlink     | Refused before the project is mounted                       |
| Caller-supplied runtime endpoint or config       | Ignored; only the trusted endpoint is contacted             |
| Poisoned durable agent home or cache             | Deterministic Git and gates remain unaffected               |
| Agent fabricates an in-project gate marker       | No operation is authorized                                  |
| Host gate record names abbreviated or stale SHA  | Refused; full current SHA required                          |
| Agent attempts to write the audit sink           | Path is absent and write fails                              |
| Privileged audit write fails                     | Operation fails closed                                      |
| `init`, `update`, or `doctor` on a cold host     | Completes under `deny` without dependency acquisition       |
| Warm repeated Git validation                     | Meets the declared p95 latency budget                       |
| Host home and container-runtime socket           | Not visible inside the container                            |
| `deny` network posture                           | Local-host and internet egress fail                         |

Release 2 owns separate cases for preparation-input closure, stale derived
images, foreign hooks, quota enforcement, and pruning. They are not release-1
exit criteria.

### Operational sequence

```text
human chooses project and approved image digest
  → launcher verifies trusted installation record
  → launcher verifies rootless runtime
  → temporary UID/write/execute probe succeeds
  → project is mounted read-only at /workspace
  → doctor validates repository topology and hook ownership without project code
  → fresh container mounts project read-write and runs bounded capability probe
  → init or update wires Factory-owned resources
  → Factory-owned Git hooks and phase transitions call the offline gate runner
  → launcher records SHA-bound gate authorization and audit event outside project
  → optional human publication uses a separate credential and protected remote
```

## Open Questions

The first-release decisions raised by the adversarial review are resolved:
Podman is the only runtime; the containerized profile specializes the broader
identity model; gate authorization and audit live in host-controlled state;
ordinary agents cannot publish; and foreign hooks are manual.

Release 2 remains open until its own proposal selects the initial ecosystem
adapters and proves their input-closure and image-lifecycle contracts. Docker,
additional repository topologies, structured executable allowlisting, and
selective-egress enforcement likewise require separate proposals or a material
revision that returns this proposal to `open`.

## Completion Criteria

- The Factory image is reproducibly built for Linux AMD64 and ARM64 and reports
  its version and immutable content identity.
- The host launcher selects images exclusively from explicit human input or
  host-controlled trusted installation metadata.
- Rootless Podman `keep-id` passes the pre-mount ownership probe; Docker and
  every unrecognized runtime are refused.
- A failed identity probe prevents any project mount; a failed read-only
  preflight prevents a read-write mount; a failed read-write capability probe
  leaves no change outside its declared nonce-scoped probe directory.
- New and existing projects initialize idempotently without recursive ownership
  or broad mode changes.
- The only ordinary host-writable mount is the approved project, and tests
  prove the host home and runtime socket are absent.
- Factory-created worktrees remain under `.current-work/worktrees`; unsupported
  external Git topology is rejected.
- Staged, full, and phase validation use one image-owned gate implementation.
- Pre-commit, pre-push, and phase adapters preserve their declared scope and
  exact exit behavior.
- All supported Git and hook execution occurs inside the approved image and
  uses the same internal gate command; repository-controlled hooks are never
  executed directly by a host process.
- Existing hook ownership is detected before mutation, and no arbitrary hook
  body is automatically rewritten.
- Foreign project hooks resolve to manual and no release-1 gate depends on a
  prepared project toolchain image.
- The image-owned Git policy preserves dangerous-operation denial and
  `commit-safe` behavior; ordinary sessions cannot push or receive publication
  credentials.
- Gate authorizations live outside `/workspace`, bind full current SHAs and
  image identity, and are atomically consumed with the authorized operation.
- Publication requires fresh human confirmation, a named remote and refspec,
  a short-lived publisher credential, and independent remote branch
  protection; force updates, deletion, and protected destinations are denied.
- Every invocation produces an external append-only audit event; failure to
  record a privileged operation fails that operation closed.
- Deterministic Git, hook, and gate commands use fresh home and cache mounts,
  fixed tool discovery, and no executable or configuration state from the
  agent-writable project state directory.
- Formatting gates do not stage changes, and check-only modes do not modify
  files.
- Hooks and deterministic gates run with networking disabled and never pull a
  missing image implicitly.
- `init`, `update`, and `doctor` work offline on a cold host using the packaged
  pre-commit executable and Factory-owned hook environments.
- Operator documentation makes protected remote refs, required independent CI,
  repository backups, and tested restoration prerequisites for recoverability.
- The full acceptance proof matrix passes on every supported runtime.
- Specifications and arc42 architecture document the new launcher, image,
  runtime identity, trust, gate, hook, dependency, and failure contracts.
- Factory operator documentation includes installation, initialization,
  updating, credential provisioning, troubleshooting, removal, and the exact
  limits of the security claim.
- Independent architecture and security reviews have no open blocking or major
  findings.

## Guiding Rule

Prove the runtime boundary first, then run every Factory operation and gate
inside the one pinned environment that boundary admits.

## Review (2026-08-09, adversarial)

Adversarial review of this proposal in the spirit of the `adversarial-review`
skill: the ten checks applied to a design seed rather than to a falsifiable
research claim. The review reads this proposal against the security objective
and acceptance criteria of
[Factory CLI Security Hardening](factory-cli-security-hardening.md), against
the [sandboxed Factory PoC](../../../poc/sandboxed-factory/README.md) that
supplies its only evidence, and against the controls this repository already
ships.

One BLOCKER and six MAJOR defects were found. The BLOCKER must be resolved
before this proposal moves from `open` to `accepted`. A1 through A3 must be
resolved before any story is planned; A4 through A6 must be resolved before the
first release is declared complete. Each finding is distilled as an amendment.

### Verdict by check

| #   | Check                      | Verdict                                                                               |
| --- | -------------------------- | ------------------------------------------------------------------------------------- |
| 01  | Testable                   | PASS — the acceptance matrix states results that could genuinely fail                 |
| 02  | Alternatives considered    | FAIL — the hardening proposal's three deployment profiles are never compared          |
| 03  | Tests severe               | WEAK — severe where present; no case exercises authority held inside the container    |
| 04  | Survives unchanged         | N/A (design seed, not a claim)                                                        |
| 05  | Sources / exact wording    | WEAK — the cited initializer requires network access the proposal never grants it     |
| 06  | Independence               | FAIL — one evidence family (Podman); the Docker profile ships on no evidence          |
| 07  | Assumptions explicit       | FAIL — identity model, push authority, audit, marker trust, and cost are all unstated |
| 08  | Scope creep                | FAIL — the first release bundles work that the security claim does not require        |
| 09  | Contrary evidence          | WEAK — the PoC limitation is carried honestly; the hardening exclusions are not cited |
| 10  | Surviving refutation paths | FAIL — "Open Questions: None for the first release" is not sustainable                |

### Coverage of the hardening security objective

The hardening proposal states six outcomes that compromise inside a Factory CLI
must not produce. Measured against them, this proposal is a strong control for
three and silent on three.

| Hardening objective                            | Status here                                                          |
| ---------------------------------------------- | -------------------------------------------------------------------- |
| 1. Become the operator or gain admin privilege | PARTIAL — host root is denied, but the agent acts as the human's UID |
| 2. Change the policy that constrains it        | MET — trusted installation record, host-controlled digest            |
| 3. Read unrelated user data or credentials     | MET — the host home, `.ssh`, and cloud configuration are unmounted   |
| 4. Execute arbitrary programs                  | NOT ADDRESSED — no command broker, no executable allowlist           |
| 5. Mutate protected Git refs or hide damage    | REGRESSED — see BLOCKER B1                                           |
| 6. Publish or contact services unapproved      | NOT ADDRESSED — `standard` posture is unrestricted egress            |

Objectives 4 and 6 are legitimately a different layer of defense, and the
proposal is honest about the egress limit inside its threat model. The defect
is that the Scope section never defers the hardening controls by name, so a
reader of this proposal alone would reasonably conclude the security work is
finished.

### Defect register + amendments

**BLOCKER B1 — the first release promotes `git push` to a supported command
and retires an active control without replacing it.** The shipped guardrail
`factory/config/hooks/block-dangerous-git.sh` (lines 68-76) currently denies
agent-issued `git push`, `push --force`, `reset --hard`, `clean -fd`, and
`branch -D` outright. This proposal lists `agent-factory git push` in the
launcher synopsis as ordinary usage and declares container Git "the only
supported Git path after a project is delegated," without stating what becomes
of that guardrail. Hardening §6 and §7 require publication under a separate
`factory-publisher` identity, remote branch protection, and explicit human
approval for reference deletion and forced movement. As written, the first
release could satisfy every Completion Criterion in this document while an
agent gained an unmediated, credentialed push it does not have today. A
security proposal must not regress a security control by omission.

*Amendment.* State the fate of every control listed in the hardening
proposal's `boundaries` — `block-dangerous-git.sh` and `commit-safe` — under
the containerized model. Reimplement dangerous-operation denial image-side,
where it is outside agent-writable content, rather than relying on a
repository-local CLI hook the new threat model declares untrusted. Split push
authority from ordinary Git: `agent-factory git push` requires an explicit
per-invocation human grant naming the remote and refspec, and push credentials
are never present in an ordinary agent session. Add matrix cases for *agent
attempts push without a grant* and *agent attempts forced update of a
protected ref*.

**MAJOR A1 — the identity model contradicts the hardening proposal, and
neither document defers to the other.** Hardening §1 requires a dedicated
`agent-factory` operating-system account that "must not share the human
operator's identity," and states that direct execution under the human account
is unsupported because it defeats identity separation. This proposal's central
probe asserts the opposite invariant: writes must "retain invoking host
ownership," Podman uses `keep-id`, and Docker maps container UID 0 to the
daemon-owning user — who is the human. Both documents are `status: open`, both
declare `assurance: critical`, both claim boundaries over agent execution, and
`supersedes:` is empty in each. A reader cannot determine which identity model
governs.

*Amendment.* Resolve the contradiction in writing. Either this proposal
supersedes hardening §1 for the containerized profile, and says why bounding
the mount is an adequate substitute for identity separation; or the mount
identity becomes a dedicated non-human host account and the ownership
invariant is restated in those terms. Record the choice in both documents and
populate `supersedes:`.

**MAJOR A2 — gate authority still rests on agent-writable marker files.** The
Distribution section states that deterministic gates "do not consume
executable code, configuration, plugins, or tool caches" from the
agent-writable state directory, and the threat model declares "persistent
Factory state" untrusted. Both statements are refuted by the current design:
`block-dangerous-git.sh` gates commits on `.current-work/verify-base-ok` and
merges on `.current-work/premerge-check-ok` (lines 33, 41, and 61-63). Those
markers are ordinary files inside the agent-writable mount, consumed as
authorization. Under this proposal's own threat model an agent forges them by
writing a file. The proposal does not notice that its trust boundary
invalidates an existing mechanism.

*Amendment.* Move gate-authorization state out of `/workspace` into
host-controlled state keyed by the project identifier, written only by the
launcher after an image-owned gate run and read only by the launcher — the
same trust root as the installation record. Marker content must bind the full
40-character SHA the gate actually validated. Add a matrix case: *agent
fabricates a gate marker* must not authorize the gated operation.

**MAJOR A3 — the Docker profile ships in the first release on no evidence, and
its privilege model is untested.** The Motivation section correctly says the
Podman `keep-id` result "must not be generalized to rootless Docker." The
Scope section then supports both runtimes in release 1. The PoC tested Podman
only. Worse, the Docker profile runs the agent as namespace UID 0, which
carries `CAP_CHOWN` inside the namespace: the agent can chown files under
`/workspace` into subordinate UID space that the invoking user cannot restore
without `newuidmap` or `podman unshare`. The probe verifies ownership of
*newly created* files and says nothing about ownership the agent changes
later. The deferral list excuses damage the agent does to files inside the
project, but this produces host-side state the owner cannot repair with
ordinary tools.

*Amendment.* Narrow release 1 to rootless Podman, and gate the Docker profile
behind a spike that reproduces the PoC's evidence for Docker. If Docker
remains in release 1, drop `CAP_CHOWN` in that profile, and add two matrix
cases: *agent chowns inside `/workspace`* must leave a documented host
recovery path, and *agent sets a setuid or subordinate-owned file* must be
refused or recoverable.

**MAJOR A4 — no audit record exists, and the launcher is the obvious place for
one.** Hardening §8 requires recorded execution identity, capability grants,
full commit SHAs, and policy decisions sent to append-only storage outside the
workspace, and its acceptance criteria require every privileged operation to
be attributable to an external record. This proposal records nothing. The
launcher already resolves the image digest, project identity, network posture,
and credential grants for every invocation; it is the natural choke point and
the record would cost little.

*Amendment.* The launcher appends one record per invocation to owner-only
host storage outside the project: timestamp, resolved image digest, canonical
project path with device and inode, runtime profile, network posture,
credential grants, command, and exit status. Add a Completion Criterion and a
matrix case proving the record is not writable from inside the container.

**MAJOR A5 — the first release exceeds the scope its security claim
requires.** Release 1 bundles the image, the launcher, two runtime profiles, a
gate-runner rewrite, hook-manager adapters, and a versioned ecosystem-adapter
framework for `prepare` with a closed input model covering manifests,
lockfiles, tool-version configuration, patches, local path dependencies,
submodule identities, and resolution-affecting environment values. The
preparation framework is a product in its own right and is not load-bearing
for the security claim: confinement of host filesystem mutation holds whether
or not foreign project hooks can be gated offline.

*Amendment.* Split the release. R1 delivers the image, launcher, identity
probe, staged preflight, and `init`, `update`, `doctor`, `shell`, `run`,
`git`, `format`, and `gate` over Factory-owned gates only, with hook classes B,
C, and D all resolving to the `manual` outcome. R2 delivers `prepare`, the
ecosystem adapters, and classes A and B. The security claim is unchanged by
the split; only offline gating of foreign project hooks is deferred.

**MAJOR A6 — `init` has no declared network posture, and the initializer this
proposal cites needs one.** The proposal declares `deny` for hooks and
prepared deterministic gates and `standard` for provider access and `prepare`.
It assigns no posture to `init`, `update`, or `doctor`. The cited
[`init-factory`](../../../factory/scripts/init-factory) runs
`uvx pre-commit install` (line 1472), which requires network access on a cold
cache. Under `deny`, initialization of a fresh project fails; under
`standard`, the first command run against an untrusted project has network
access. The `--source` and `--target` contract the proposal cites is otherwise
accurate (lines 1477-1499 and 1501).

*Amendment.* Publish a table assigning an explicit network posture to every
launcher command. Pin pre-commit and its hook environments into the image so
that `init` and `update` complete under `deny`. Where a command cannot run
offline, say so and state why the exposure is acceptable.

**MINOR A7 — derived toolchain images have no lifecycle.** Every lockfile
change invalidates the preparation manifest and produces a new image, per
project and per branch, indefinitely. There is no pruning command, no disk
bound, and no Completion Criterion. *Amendment:* add a retention and pruning
contract, or accept it as resolved by the A5 split and defer it to R2 with the
rest of `prepare`.

**MINOR A8 — `doctor` before every Git mutation is an unpriced cost.** The
Git-hook integration section requires `doctor` to verify the recorded strategy
"before each Git mutation," which implies a container start and topology
validation on every commit. The entire security model depends on humans not
reaching for host Git; if a commit takes several seconds, they will, and the
proposal itself concedes that a human-created host commit cannot be prevented.
*Amendment:* state a latency budget, or define a session-scoped validation
cache with an explicit invalidation rule, and add it to the matrix.

**NOTE A9 — the residual risk belongs in the Motivation, not only in the
threat model.** Normal interactive operation is the `standard` posture: a full
shell, provider credentials, and unrestricted egress with no enforced
selective egress. The practical gain over the host-native model is
host-filesystem confinement. The Security-claim section says this correctly;
the Motivation still reads as general isolation. One sentence up front
prevents the reader forming the wrong expectation.

**NOTE A10 — recoverability is a stated precondition, not an assumption.**
Hardening requires that deletion or corruption of local workspace state be
recoverable from authoritative remote refs and backups. This proposal grants
the agent read-write access to the whole mount, `.git` included, and defers
protecting the project from its agent. That deferral is only tolerable when
the remote is protected. *Amendment:* name remote branch protection and
backup as documented deployment prerequisites in the operator documentation
Completion Criterion.

### Recommendation

Status remains `open`. Resolve B1 and A1 through A3 before `accepted`; resolve
A4 through A6 before stories are planned. Adopt the A5 split so that the first
release delivers the boundary this proposal proves and nothing else.

Replace "Open Questions: None for the first release" with the questions this
review surfaces: which identity model governs (A1), where gate-authorization
state lives (A2), whether Docker is in release 1 at all (A3), and which
ecosystems receive `prepare` adapters in R2 (A5). The last of these moves the
estimate by a large factor and is the reason `human_review_hours` is still
`unknown`.

The proposal's strongest section is the trusted installation record — device
and inode re-verification immediately before mount, atomic symlink-free
replacement, and the refusal to accept project-local values for image,
runtime, endpoint, mount, credential, or network selection. That reasoning is
the standard the rest of the document should meet: it is also the correct
place to anchor the fixes for B1, A2, and A4, all three of which are failures
to keep authority out of agent-writable space.

### Review resolution (2026-08-09)

The proposal remains `open` pending implementation evidence and independent
re-review, but every design defect above now has an explicit disposition:

| Finding | Disposition in this revision                                                                                                                                                                 |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| B1      | **Resolved in design:** ordinary sessions cannot push; image-owned Git policy preserves the existing denials; publication is a separately confirmed, narrowly credentialed broker operation. |
| A1      | **Resolved in design:** this proposal defines a named containerized specialization of hardening §1, and the hardening proposal links back to that specialization.                            |
| A2      | **Resolved in design:** gate authorization is owner-only host state bound to full SHAs and atomically consumed; project markers are non-authoritative.                                       |
| A3      | **Resolved in scope:** release 1 supports Podman only; Docker requires a separate ownership and recovery spike.                                                                              |
| A4      | **Resolved in design:** every invocation and policy decision produces an external append-only audit event; privileged operations fail closed if it cannot be recorded.                       |
| A5      | **Resolved in scope:** release 1 contains only Factory-owned gates; `prepare`, ecosystem adapters, and foreign-hook execution move to release 2.                                             |
| A6      | **Resolved in design:** every command has a network posture; packaged pre-commit assets let `init`, `update`, and `doctor` run offline.                                                      |
| A7      | **Resolved for R1 / specified for R2:** derived images are absent from R1; R2 has retention, quota, and confirmed-pruning requirements.                                                      |
| A8      | **Resolved in design:** host-owned session validation may be reused for 30 seconds under complete invalidation keys and a 500 ms warm-path p95 budget.                                       |
| A9      | **Resolved editorially:** Motivation now states that R1 gains host-filesystem confinement, not general command or network confinement.                                                       |
| A10     | **Resolved operationally:** protected remote refs, independent CI, backups, and tested restoration are release prerequisites.                                                                |

“Resolved in design” does not mean proven. The acceptance matrix must exercise
the amended contracts, after which an independent architecture and security
review decides whether the proposal may move to `accepted`.

## Review 2 (2026-08-09, adversarial — remediation `6d2cc1d`)

Adversarial re-review of the remediation recorded in commit
`6d2cc1d0c3492d6dad9e8c40542577e6922dd949`, which amends this proposal and
[Factory CLI Security Hardening](factory-cli-security-hardening.md). The
review verifies each claimed disposition against the amended text and the
artifacts both documents cite, and then looks for defects the remediation
itself introduced.

The BLOCKER is cleared. No BLOCKER is raised in this pass. Three MAJOR defects
are new or unaddressed, all of them consistency failures rather than design
failures: the remediation added a strong Git policy without retiring the
sentences the old design left behind. The verdict table in the review above is
superseded by the table here; the defect register above is retained as an
audit record and must not be edited.

### Disposition of prior findings

| Finding  | Verified disposition                                                                                                                        |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| B1       | ACCEPTED — structured operations, `publish` broker, credential absence, four new matrix cases, two new criteria; residue in A13             |
| A1       | ACCEPTED — both documents now state the specialization and its limits; residue in A16                                                       |
| A2       | ACCEPTED — host-owned, SHA-bound, one-time, atomically consumed authorizations; markers demoted; residue in A19                             |
| A3       | ACCEPTED — release 1 is Podman only, and the Docker spike must test `CAP_CHOWN`, subordinate-UID attack, setuid, and ordinary-user recovery |
| A4       | ACCEPTED — external append-only sink, denied operations recorded, fail-closed on sink failure; residue in A18                               |
| A5       | ACCEPTED — release split; `prepare` is a reserved unavailable command in release 1; residue in A15                                          |
| A6       | ACCEPTED — posture table, packaged pre-commit replacing `uvx`, cold-host criterion and matrix case; residue in A14                          |
| A7       | ACCEPTED — reference counting, dry-run default, retention window, quota; correctly deferred with `prepare`                                  |
| A8       | ACCEPTED — 500 ms p95 budget and a bounded validation cache; residue in A17                                                                 |
| A9       | ACCEPTED — the narrower gain is stated in the Motivation                                                                                    |
| A10      | ACCEPTED — prerequisites stated in the design and in the operator-documentation criterion                                                   |
| Check 02 | NOT ADDRESSED — see A20                                                                                                                     |

The remediation resolution table above covers the eleven lettered findings but
omits check 02, which was recorded as a check-level failure rather than a
lettered defect. It remains the only substantive process gap.

### Verdict by check (re-run)

| #   | Check                      | Verdict                                                                              |
| --- | -------------------------- | ------------------------------------------------------------------------------------ |
| 01  | Testable                   | PASS — the matrix now exercises authority, audit, offline, and latency contracts     |
| 02  | Alternatives considered    | FAIL — unchanged; see A20                                                            |
| 03  | Tests severe               | PASS — fabricated marker, stale SHA, audit-write, and denied-push cases would refute |
| 04  | Survives unchanged         | N/A (design seed, not a claim)                                                       |
| 05  | Sources / exact wording    | PASS — the `uvx` defect is fixed at its source and both controls are now boundaries  |
| 06  | Independence               | PASS — release 1 now rests only on the runtime the PoC actually tested               |
| 07  | Assumptions explicit       | WEAK — enforcement mechanism per denial is still implicit; see A13 and A18           |
| 08  | Scope creep                | WEAK — the split is clean, but stale scope text and one undeclared command remain    |
| 09  | Contrary evidence          | WEAK — the proxy limit is restated, then contradicted for `publish`; see A12         |
| 10  | Surviving refutation paths | PASS — Open Questions now names what release 2 must settle                           |

### New defect register + amendments

**MAJOR A11 — the Scope section still promises the pass-through the new policy
forbids.** The Git policy section opens with "The launcher exposes structured
Git operations, not an unrestricted argument pass-through." The Scope section
still lists "Container-only Git execution with Git-compatible launcher argument
and terminal forwarding," and the Canonical Git execution section still states
that the launcher "accepts Git-compatible arguments." Argument compatibility
and structured operations are opposite contracts. A story planned from the
Scope section would build the interface the policy section rejects.

*Amendment.* Enumerate the structured operations release 1 exposes and state
which arguments each accepts. Replace the Scope bullet and the Canonical Git
paragraph with that enumeration, keeping terminal, signal, and exit-status
forwarding, which is compatible with either interface.

**MAJOR A12 — the `publish` posture offers a proxy as an alternative to
server-side credential scoping.** The posture table's explanatory paragraph
says `publish` "permits only the resolved Git remote through an external
control or a credential whose server-side policy makes other destinations and
refs unusable." Two paragraphs later the same section repeats that a proxy is
not a security boundary under rootless slirp networking, and the Security-claim
section forbids claiming otherwise. The disjunction makes an unenforced control
interchangeable with an enforced one, and it does so for the single command
that holds a live credential.

*Amendment.* Make server-side credential scoping mandatory: the publisher
credential must be unusable for any other remote, ref class, or operation
regardless of what the container attempts. State plainly that the publication
container has unrestricted rootless networking, that the credential is the only
enforced restriction, and that an external egress control is optional
observability. Add a matrix case: *publisher credential used against a
different remote or ref* must fail at the server.

**MAJOR A13 — the policy's denials are stated without naming what enforces
them.** "The policy denies push, forced reference movement, reference deletion,
destructive reset and clean operations, protected-ref mutation, remote changes,
hook-path changes, and gate bypasses" reads as command mediation. The Scope
section explicitly defers "structured command allowlisting," `shell` and `run`
grant an interactive session inside an image that contains Git, and the same
paragraph concedes that "an interactive shell can bypass a local wrapper and
damage `.git`." Only two of the listed denials are actually enforced against an
in-container shell: push and remote publication, because no credential is
present. The rest are enforced only on the launcher path.

*Amendment.* Split the list in two. State which denials hold against any
process inside the container and why — credential absence for publication,
host-owned state for gate authorization, mount scope for everything outside
`/workspace` — and which hold only for launcher-mediated invocations and are
therefore accident prevention. This distinction is the difference between a
boundary and a wrapper, and this proposal has been careful about it everywhere
else.

**MINOR A14 — which copy of `commit-safe` runs is ambiguous.** The policy
section names `factory/scripts/commit-safe` as the implementation behind the
structured commit operation. Initialization copies Factory content into the
project, so a writable `/workspace/factory/scripts/commit-safe` also exists and
the threat model declares it untrusted. *Amendment:* cite the image-owned path
under `/opt/agent-factory/factory` explicitly, and add the project copy to the
list of paths gates never execute.

**MINOR A15 — `image fetch <digest>` is introduced only in the posture
table.** It appears nowhere in the image's internal command list, the launcher
synopsis, the Scope section, or the Completion Criteria, yet it is the one
release-1 command that contacts a registry. *Amendment:* declare it with the
other commands, or fold registry acquisition into an explicit `update` step.

**MINOR A16 — `supersedes` is used for a relationship it does not express.**
`factory/rulebooks/templates/proposal.md` defines `supersedes` as a single
proposal path, and states that the superseded proposal takes status
`superseded`. Here it holds a list whose entry carries a section anchor, and
the hardening proposal remains `open` and amended rather than replaced. The
anchor style belongs to `boundaries`, which the template documents as "tracked
path with optional Markdown anchor." *Amendment:* return `supersedes` to
`null`. The prose cross-reference both documents now carry already expresses
the specialization correctly, and it is the stronger record.

**MINOR A17 — the 30-second validation cache is a time window unless its
inputs are re-read.** The record binds the Git configuration hash and hook
inventory hash, but a cache is only sound if those hashes are recomputed at
each use; otherwise an agent that edits `.git/config` inside the window meets a
stale verdict. The bound "current full SHA" also does not cover the index,
which is what a staged gate validates. *Amendment:* state that the launcher
re-reads and rehashes the bound inputs on every use, that reading never
executes project content, and that the cache covers topology and hook strategy
only, never gate results.

**NOTE A18 — "append-only" is a property against the container, not the
operator.** The invoking user owns the sink and can rewrite it; true
append-only storage needs privilege this design does not claim. The trust model
makes this acceptable, since the human is trusted, but the word should be
qualified so that a later reader does not treat the sink as evidence against
the operator.

**NOTE A19 — the marker migration has no ordering rule.** The proposal states
that `.current-work/verify-base-ok` and `.current-work/premerge-check-ok`
"grant no authority," but `factory/config/hooks/block-dangerous-git.sh` still
reads them as authorization today. Until the broker ships, both mechanisms
exist and the weaker one decides. *Amendment:* require that the same release
which introduces host-owned authorizations removes the marker-reading logic
from the shipped hook, and add it to the Completion Criteria.

**NOTE A20 — the alternatives gap is unchanged.** The hardening proposal
describes three deployment profiles, and its Baseline profile — a dedicated
`agent-factory` account with an operating-system sandbox — reaches hardening
objectives 1 and 3 without an image, a launcher, a policy broker, or a gate
runner rewrite. This proposal now positions itself as a specialization of that
document but still never compares itself to its sibling profiles. With
`architecture_change: true` and `assurance: critical`, a Pugh matrix over
Baseline, Hardened Workstation, and the containerized profile is the
project's own documented expectation.

### Recommendation

The remediation is substantive and the design is close. A11 through A13 are
wording and enumeration work on text the remediation left behind; they are
cheap and they matter, because each one currently promises a stronger or
different contract than the design delivers. Resolve them, then A14 through
A17, before this proposal moves to `accepted`.

A20 is the remaining judgment call and it belongs to the human owner, not to a
reviewer: whether to justify the containerized profile against the cheaper
sibling profile in the hardening proposal, or to record that the comparison was
made and the outcome accepted without a formal matrix.

The strongest addition in this revision is the gate-authorization transaction —
host-owned records binding full SHAs and image identity, atomically consumed
with the operation they authorize, with in-project markers demoted to
diagnostics. It removes the last place where agent-writable content decided
whether a gate had passed.
