---
schema_version: 2
title: "Containerized Agent Factory Distribution"
status: open
owner: agent-factory
created: 2026-08-07
updated: 2026-08-09
supersedes:

impact:
  scope: cross_project
  architecture_change: true
  external_contract_change: true
  boundaries:
    - factory/scripts/init-factory
    - factory/scripts/run-playbook
    - factory/scripts/run-tests
    - factory/config/pre-commit-config.yaml
    - factory/docs/factory-guide.md
    - docs/architecture.dsl

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

## Summary

Publish Agent Factory as a versioned OCI image and run it against a new or
existing project mounted read-write at `/workspace`. A trusted host launcher
selects a pinned image, proves the rootless runtime's UID mapping before it
mounts the project read-write, and exposes no other host-writable path.

The image becomes the canonical environment for Factory initialization,
playbook execution, Git operations, deterministic gates, and an attached
shell. Host Git and host project tooling are excluded once a project is
delegated because repository-controlled hooks and configuration are untrusted.
The first release supports rootless Docker Engine on native Linux and rootless
Podman; it does not claim that their user-namespace mappings are equivalent or
that arbitrary project hooks are reproducible without a prepared project
toolchain image.

## Motivation

The current host-native subprocess model gives an agent the invoking user's
filesystem and network authority. The
[sandboxed Factory PoC](../../poc/sandboxed-factory/README.md) demonstrates
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

The image filesystem is read-only at runtime. `/tmp`, `/run`, and the default
runtime home and caches are ephemeral `tmpfs` mounts. The approved project is
mounted at `/workspace`. Durable Factory artifacts live below the already
ignored `/workspace/.agent-factory/state/` namespace, but deterministic gates
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
agent-factory git push
agent-factory shell
agent-factory doctor
```

The launcher:

1. Resolves the canonical project path without evaluating project-provided
   shell text.
2. Rejects `/`, the host home, unresolved paths, and mounts broader than the
   approved project.
3. Reads the approved image digest and runtime policy from host-controlled
   configuration, not from the project.
4. Detects Docker or Podman and verifies its supported rootless mode.
5. Runs the runtime-specific UID-mapping probe.
6. Mounts the project read-write only after the probe succeeds.
7. Drops capabilities, enables `no-new-privileges`, and omits the runtime
   socket and host home.
8. Uses no network for hooks and gates; commands that require network use a
   separate explicit posture.

The launcher starts from a sanitized environment. It ignores project-local
runtime selection and caller-controlled Docker or Podman context, host,
connection, configuration, and plugin variables. It invokes an
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

The launcher supports two secure profiles in release 1:

| Runtime                      | Container identity                                           | Host result                                    |
| ---------------------------- | ------------------------------------------------------------ | ---------------------------------------------- |
| Rootless Docker Engine/Linux | UID/GID `0` inside the already rootless user namespace       | Maps to the unprivileged daemon-owning user    |
| Rootless Podman/Linux        | `--userns=keep-id`, caller UID/GID inside the user namespace | Preserves the invoking user's numeric identity |

Container UID `0` in the Docker profile is acceptable only because the
launcher first verifies that the daemon is rootless and proves the mapping. It
does not grant host root. The container still runs with all capabilities
dropped, `no-new-privileges`, a read-only root filesystem, and the restricted
mount set.

Before mounting a real project read-write, the launcher creates a host-owned
temporary probe directory, mounts it into the candidate image, and asks the
container to create and mode-change a probe file. The launcher verifies that:

- the resulting file is owned by the invoking host UID;
- the file is writable and removable by that user;
- its executable bit can be set and it can execute when the host mount permits
  execution; and
- no subordinate-UID ownership leaks onto the host.

The launcher removes the probe and stops before mounting the project if any
assertion fails. Docker Desktop, rootful Docker, group-only writable projects,
and other user-namespace modes are not inferred from these profiles and are
deferred until independently tested.

### Project preflight and permissions

Preflight has three explicit stages:

1. The runtime identity probe uses only a launcher-created temporary directory;
   failure prevents any project mount.
2. The project is mounted read-only. `doctor` validates canonical identity,
   repository topology, symlinks, hook ownership, mount flags, and trusted
   installation metadata without running project code.
3. The project is remounted in a fresh container read-write. A bounded
   capability probe operates only in a launcher-created
   `.agent-factory/probe/<nonce>/` directory, records its intended changes,
   removes them, and verifies that cleanup completed before workflow execution.

The read-write capability probe tests effective operations rather than only
inspecting mode bits:

- create, atomically rename, and remove a regular file under
  `.agent-factory/`;
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
[`init-factory`](../../factory/scripts/init-factory). It does not overwrite
project-owned configuration or change unrelated modes. Preflight resolves all
destinations before mutation; a collision stops at the existing documented
boundary.

`update` stages a new Factory copy under `.agent-factory/`, validates generated
CLI adapters and gates, and replaces only Factory-owned content. It records the
installed version and image digest for diagnosis, while the host-controlled
installation record remains the execution trust root.

### Repository topology

Release 1 supports one Git repository wholly contained beneath `/workspace`.
Factory-created worktrees live beneath:

```text
/workspace/.agent-factory/worktrees/
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
[`run-tests`](../../factory/scripts/run-tests) and the applicable deterministic
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
agent-factory git push ...
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

### Git-hook integration

Initialization detects configured hook paths, existing hook files, pre-commit,
Husky, and recognized hook managers before changing hook configuration. It
selects exactly one recorded strategy:

1. **Factory-owned:** install thin in-container adapters where no hook owner
   exists.
2. **Pre-commit adapter:** add prefixed local Factory gate entries to the
   existing `.pre-commit-config.yaml` through the established merge contract.
3. **Recognized manager adapter:** add or document that manager's supported
   invocation of `af-internal gate <scope>` inside the container.
4. **Manual:** stop before mutation and provide exact wiring instructions when
   safe composition cannot be proven.

The Factory never splices arbitrary shell hook bodies. All retained project
hooks execute inside the project toolchain image, never directly on the host.
`doctor` verifies the recorded strategy before each Git mutation rather than
assuming an earlier result is still current. Git's explicit `--no-verify`
bypass still exists, but bypassing a local hook does not bypass a phase gate.

The adapters map as follows:

```text
pre-commit → gate staged
pre-push   → gate full
phase      → gate phase <state>
```

### Project hook and dependency preparation

The universal Factory image guarantees only Factory-owned gates. Existing
project hooks are classified during `doctor` and `prepare`:

| Class | Meaning                                        | Release 1 behavior                                       |
| ----- | ---------------------------------------------- | -------------------------------------------------------- |
| A     | Image-compatible and offline                   | Run inside the project toolchain image                   |
| B     | Requires dependency or hook-environment setup  | Require `agent-factory prepare`                          |
| C     | Host-bound, service-bound, or nested-container | Exclude from the deterministic claim; require a decision |
| D     | Unsafe or unclassifiable                       | Fail closed                                              |

`agent-factory prepare` is the only normal dependency-acquisition step. With
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

### Home, caches, credentials, and network

Interactive agent sessions may opt into durable, ignored project state:

```text
/workspace/.agent-factory/state/agent-home
/workspace/.agent-factory/state/agent-cache
```

That state is untrusted and is never mounted as the home, configuration,
plugin, executable, or dependency cache for `doctor`, `git`, hooks, or gates.
Those commands receive a fresh tmpfs home and cache, a fixed image-owned
`PATH`, a sanitized environment, and no user/site plugin discovery. Prepared
dependencies come only from the verified project toolchain image. Commands
that intentionally consume durable agent state are outside the deterministic
gate claim and report that fact.

The host home, `.ssh`, cloud configuration, password stores, browser profiles,
and container-runtime socket are not mounted. Credentials enter only through
an explicit allowlist of environment variables, runtime secrets, narrowly
mounted read-only files, or an opt-in SSH-agent socket. Credential mounts are
never writable.

The supported network postures are:

- `deny`: runtime `--network none`, used by hooks and prepared deterministic
  gates;
- `standard`: rootless runtime networking, explicitly selected for AI provider
  access and `prepare`.

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
- dependency inputs differ from the preparation manifest;
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
- A trusted host launcher for native Linux rootless Docker Engine and rootless
  Podman.
- Runtime detection and a destructive-target-safe UID/write/execute probe
  before the project is mounted read-write.
- `init`, `update`, `doctor`, `shell`, `run`, `git`, `format`, `gate`, and
  `prepare` commands.
- New and existing project initialization using the current non-interference
  and removal contracts.
- One `/workspace` host-writable mount, in-project Factory worktrees, and
  project-local ignored runtime state.
- An image-owned staged/full/phase gate runner used by Git, pre-commit,
  pre-push, and playbook phase transitions.
- Container-only Git execution with Git-compatible launcher argument and
  terminal forwarding.
- Hook ownership detection with Factory, pre-commit, recognized-manager, and
  manual integration outcomes.
- Project toolchain image preparation bound to dependency-input hashes.
- `deny` and `standard` network postures with no selective-egress security
  claim.
- Automated proof across non-1000 UIDs, existing repositories, worktrees,
  hooks, formatting, linting, tests, and offline dependency failure modes.

**Explicitly deferred (do NOT plan stories for these):**

- Rootful Docker as a supported secure profile.
- Docker Desktop, Windows bind mounts, and macOS bind mounts.
- Group-only writable and shared-group repositories.
- External worktrees, external Git object stores, and project mounts broader
  than one repository.
- Enforced selective egress; a dedicated external gateway or host firewall is
  required for that guarantee.
- Nested Docker-based project hooks or exposure of Docker/Podman sockets.
- Automatic support for unrecognized hook managers and arbitrary remote
  pre-commit environments.
- Plain host Git or host project tooling as part of the secured workflow.
- Managed registry publication, image signing infrastructure, SBOM policy, and
  vulnerability-remediation service levels beyond emitting build artifacts
  needed for later adoption.
- Protection of files inside the delegated project from an agent authorized to
  write that project.

## Design Details

### Security claim

The release may claim:

> On a verified supported rootless runtime, Agent Factory confines host
> filesystem mutation by agent-executed processes to the approved project bind
> mount, executes Factory gates in a pinned Factory-and-toolchain image pair
> with fresh runtime state, and preserves host ownership through a
> runtime-specific, mechanically tested identity mapping. This claim excludes
> runtime or kernel compromise and any host command a human runs directly in
> the agent-writable repository.

It must not claim that arbitrary project hooks are deterministic, mutable
caches are reproducible, Git hooks are unbypassable, an in-container proxy
enforces selective egress, or Docker and Podman share one UID strategy.

### Acceptance proof matrix

The owning automated test layer must cover each distinct contract without
duplicating deterministic linter rules:

| Case                                             | Required result                                             |
| ------------------------------------------------ | ----------------------------------------------------------- |
| Rootless Docker, ordinary user-owned repository  | Writes retain invoking host ownership                       |
| Rootless Podman with `keep-id`                   | Writes retain invoking host ownership                       |
| Host UID other than `1000`                       | Probe, initialization, gates, and Git succeed               |
| Rootful or unrecognized runtime                  | Refused before the project is mounted read-write            |
| Group-only writable repository                   | Refused with an explicit deferred-capability message        |
| New project                                      | Directory and Git repository initialize as the host user    |
| Existing project                                 | Existing files, history, hooks, and configuration survive   |
| Read-only or `noexec` project                    | Refused before workflow execution; probe effects bounded    |
| Existing `core.hooksPath`                        | Preserved through a supported adapter or stopped safely     |
| Existing pre-commit or recognized hook manager   | One recorded integration strategy remains active            |
| Unrecognized hook manager                        | No mutation; exact manual wiring guidance                   |
| In-project Factory worktree                      | Git operations and gates succeed                            |
| External worktree or object alternate            | Rejected without mounting a broader parent                  |
| Missing prepared dependency offline              | Gate fails and requests `prepare`                           |
| Changed lockfile after preparation               | Gate fails before tests execute                             |
| Formatter detects changes                        | Check fails without staging files                           |
| Containerized pre-push                           | Arguments, standard input, signals, output, and status pass |
| Approved image absent during Git command         | Command fails without pulling or enabling network           |
| Modified project-local image manifest            | Trusted host-selected digest remains unchanged              |
| Replaced project hook or local Git configuration | Executes only inside the approved image                     |
| Tampered host installation record or symlink     | Refused before the project is mounted                       |
| Caller-supplied runtime endpoint or config       | Ignored; only the trusted endpoint is contacted             |
| Changed or newly added dependency input          | Offline gate refuses the prepared image                     |
| Poisoned durable agent home or cache             | Deterministic Git and gates remain unaffected               |
| Host home and container-runtime socket           | Not visible inside the container                            |
| `deny` network posture                           | Local-host and internet egress fail                         |

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
  → prepare builds a dependency-input-bound project image
  → Git hooks and phase transitions call the same offline gate runner
```

## Open Questions

None for the first release. Deferred runtime platforms, repository topologies,
hook classes, and selective-egress enforcement require separate proposals or a
material revision that returns this proposal to `open`.

## Completion Criteria

- The Factory image is reproducibly built for Linux AMD64 and ARM64 and reports
  its version and immutable content identity.
- The host launcher selects images exclusively from explicit human input or
  host-controlled trusted installation metadata.
- Rootless Docker and Podman use separate identity strategies, and both pass
  the pre-mount ownership probe for supported cases.
- A failed identity probe prevents any project mount; a failed read-only
  preflight prevents a read-write mount; a failed read-write capability probe
  leaves no change outside its declared nonce-scoped probe directory.
- New and existing projects initialize idempotently without recursive ownership
  or broad mode changes.
- The only ordinary host-writable mount is the approved project, and tests
  prove the host home and runtime socket are absent.
- Factory-created worktrees remain under `.agent-factory/worktrees`; unsupported
  external Git topology is rejected.
- Staged, full, and phase validation use one image-owned gate implementation.
- Pre-commit, pre-push, and phase adapters preserve their declared scope and
  exact exit behavior.
- All supported Git and hook execution occurs inside the approved image and
  uses the same internal gate command; repository-controlled hooks are never
  executed directly by a host process.
- Existing hook ownership is detected before mutation, and no arbitrary hook
  body is automatically rewritten.
- `prepare` produces a project toolchain image and manifest bound to the closed
  input inventory declared by a versioned ecosystem adapter; offline gates
  reject changed, added, missing, or unsupported inputs.
- Deterministic Git, hook, and gate commands use fresh home and cache mounts,
  fixed tool discovery, and no executable or configuration state from the
  agent-writable project state directory.
- Formatting gates do not stage changes, and check-only modes do not modify
  files.
- Hooks and deterministic gates run with networking disabled and never pull a
  missing image implicitly.
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
the [sandboxed Factory PoC](../../poc/sandboxed-factory/README.md) that
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
`block-dangerous-git.sh` gates commits on `.agent-factory/verify-base-ok` and
merges on `.agent-factory/premerge-check-ok` (lines 33, 41, and 61-63). Those
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
[`init-factory`](../../factory/scripts/init-factory) runs
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
