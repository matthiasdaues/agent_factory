---
schema_version: 2
title: "Containerized Agent Factory Distribution"
status: open
owner: agent-factory
created: 2026-08-07
updated: 2026-08-07
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
shell. The first release supports rootless Docker Engine on native Linux and
rootless Podman; it does not claim that their user-namespace mappings are
equivalent or that arbitrary project hooks are reproducible without a prepared
project toolchain image.

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

The image filesystem is read-only at runtime. `/tmp` and `/run` are ephemeral
`tmpfs` mounts. The approved project is mounted at `/workspace`; project-owned
runtime state and reusable caches live under the already ignored
`/workspace/.agent-factory/` namespace.

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

Trusted installation metadata lives outside the project, keyed by a stable
project identifier and canonical path, for example:

```text
$XDG_CONFIG_HOME/agent-factory/installations/<project-id>.json
```

It records the approved image digest, runtime kind, canonical project path,
and network policy. A project-local manifest may report the same values for
diagnosis, but it cannot select an image to execute. Changing the trusted
digest requires an explicit human launcher command.

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

### Project permissions

`doctor` tests effective operations rather than only inspecting mode bits:

- create, atomically rename, and remove a regular file under
  `.agent-factory/`;
- create a directory and Git lock file;
- set and execute a file's executable bit;
- write every approved in-project worktree;
- run `git status` without a global `safe.directory=*` exception; and
- confirm that a newly created file has the expected host ownership.

Image-owned and generated scripts are packaged or created with their intended
modes. Unexpected mode drift fails validation. The runtime never repairs a
project through recursive ownership or permission changes and never uses
world-writable mode as a fallback.

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
environment, dependency state, and network policy. This is the deterministic
path.

Plain host `git commit` and `git push` are supported through a compatibility
bridge. A host-side dispatcher locates the Git common directory and worktree,
loads trusted installation metadata, verifies that the approved image already
exists locally, and invokes the fixed internal hook command without a TTY. It
forwards hook arguments, standard input, output, signals, and exit status. A
hook never pulls an image or enables network access.

An image-owned runtime marker plus a bounded hook-depth value prevents
recursive dispatch. An environment variable alone is not accepted as proof
that the command runs in the approved image.

### Git-hook integration

Initialization detects `core.hooksPath`, existing hook files, pre-commit,
Husky, and recognized hook managers before changing hook configuration. It
selects exactly one recorded strategy:

1. **Factory-owned:** install thin dispatchers where no hook owner exists.
2. **Pre-commit adapter:** add prefixed local Factory gate entries to the
   existing `.pre-commit-config.yaml` through the established merge contract.
3. **Recognized manager adapter:** add or document that manager's supported
   invocation of `agent-factory hook <stage>`.
4. **Manual:** stop before mutation and provide exact wiring instructions when
   safe composition cannot be proven.

The Factory never splices arbitrary shell hook bodies. `doctor` verifies that
the recorded strategy remains active. Git's explicit `--no-verify` bypass
still exists, but bypassing a local hook does not bypass a phase gate.

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

The preparation manifest binds the derived image digest to hashes of every
dependency input, including applicable lockfiles and
`.pre-commit-config.yaml`. Before an offline gate runs, it recomputes those
hashes. A changed or missing input fails with an instruction to run
`agent-factory prepare`; the gate never silently enables networking or trusts
a mutable cache as proof of reproducibility.

### Home, caches, credentials, and network

Runtime home and caches live under ignored project state:

```text
/workspace/.agent-factory/home
/workspace/.agent-factory/cache
```

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

The launcher and internal entrypoint fail before project mutation when:

- the runtime is not a supported, verified rootless profile;
- the UID-mapping probe does not preserve host ownership;
- the approved image digest is absent locally during a hook;
- the project is read-only, `noexec`, group-only writable, or has unsupported
  Git topology;
- existing hooks cannot be composed safely;
- dependency inputs differ from the preparation manifest;
- a hook is host-bound or unclassifiable; or
- the requested operation needs a host mount or network capability outside its
  declared posture.

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
- Canonical containerized Git execution plus a fail-closed host-hook bridge.
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
- Managed registry publication, image signing infrastructure, SBOM policy, and
  vulnerability-remediation service levels beyond emitting build artifacts
  needed for later adoption.
- Protection of files inside the delegated project from an agent authorized to
  write that project.

## Design Details

### Security claim

The release may claim:

> On a verified supported rootless runtime, Agent Factory confines host
> filesystem mutation to explicitly approved bind mounts, executes Factory
> gates in a pinned image, and preserves host ownership through a
> runtime-specific, mechanically tested identity mapping.

It must not claim that arbitrary project hooks are deterministic, mutable
caches are reproducible, Git hooks are unbypassable, an in-container proxy
enforces selective egress, or Docker and Podman share one UID strategy.

### Acceptance proof matrix

The owning automated test layer must cover each distinct contract without
duplicating deterministic linter rules:

| Case                                            | Required result                                             |
| ----------------------------------------------- | ----------------------------------------------------------- |
| Rootless Docker, ordinary user-owned repository | Writes retain invoking host ownership                       |
| Rootless Podman with `keep-id`                  | Writes retain invoking host ownership                       |
| Host UID other than `1000`                      | Probe, initialization, gates, and Git succeed               |
| Rootful or unrecognized runtime                 | Refused before the project is mounted read-write            |
| Group-only writable repository                  | Refused with an explicit deferred-capability message        |
| New project                                     | Directory and Git repository initialize as the host user    |
| Existing project                                | Existing files, history, hooks, and configuration survive   |
| Read-only or `noexec` project                   | Refused before workflow execution                           |
| Existing `core.hooksPath`                       | Preserved through a supported adapter or stopped safely     |
| Existing pre-commit or recognized hook manager  | One recorded integration strategy remains active            |
| Unrecognized hook manager                       | No mutation; exact manual wiring guidance                   |
| In-project Factory worktree                     | Git operations and gates succeed                            |
| External worktree or object alternate           | Rejected without mounting a broader parent                  |
| Missing prepared dependency offline             | Gate fails and requests `prepare`                           |
| Changed lockfile after preparation              | Gate fails before tests execute                             |
| Formatter detects changes                       | Check fails without staging files                           |
| Pre-push bridge                                 | Arguments, standard input, signals, output, and status pass |
| Approved image absent during host hook          | Hook fails without pulling or enabling network              |
| Modified project-local image manifest           | Trusted host-selected digest remains unchanged              |
| Host home and container-runtime socket          | Not visible inside the container                            |
| `deny` network posture                          | Local-host and internet egress fail                         |

### Operational sequence

```text
human chooses project and approved image digest
  → launcher verifies trusted installation record
  → launcher verifies rootless runtime
  → temporary UID/write/execute probe succeeds
  → project is mounted at /workspace
  → doctor validates repository topology and hook ownership
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
- A failed identity or permission probe prevents the real project from being
  mounted read-write.
- New and existing projects initialize idempotently without recursive ownership
  or broad mode changes.
- The only ordinary host-writable mount is the approved project, and tests
  prove the host home and runtime socket are absent.
- Factory-created worktrees remain under `.agent-factory/worktrees`; unsupported
  external Git topology is rejected.
- Staged, full, and phase validation use one image-owned gate implementation.
- Pre-commit, pre-push, and phase adapters preserve their declared scope and
  exact exit behavior.
- Canonical containerized Git and the host-hook bridge run the same approved
  image and internal gate command.
- Existing hook ownership is detected before mutation, and no arbitrary hook
  body is automatically rewritten.
- `prepare` produces a project toolchain image and manifest bound to all
  supported dependency inputs; offline gates reject stale preparation.
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
