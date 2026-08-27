---
schema_version: 2
title: "Agent Execution Isolation and Optional Container Distribution"
status: open
owner: agent-factory
created: 2026-08-10
updated: 2026-08-10
supersedes: superseded/containerized-agent-factory.md

impact:
  scope: cross_project
  architecture_change: true
  external_contract_change: true
  boundaries:
    - orchestrator
    - factory/scripts/init-factory
    - factory/scripts/run-playbook
    - factory/config/hooks/block-dangerous-git.sh
    - factory/scripts/commit-safe
    - factory/scripts/verify-base
    - factory/scripts/premerge-check
    - factory/docs/factory-guide.md
    - docs/arc42/architecture.dsl

governance:
  assurance: critical
  risk_domains:
    - security
    - privacy
    - data_integrity
    - compatibility
    - reliability
    - operations

estimate:
  as_of: 2026-08-10
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
---

# Proposal: Agent Execution Isolation and Optional Container Distribution

## Summary

Run Factory-enabled agents under a dedicated, unprivileged operating-system
UID. Ordinary filesystem ownership, mode bits, and POSIX ACLs grant that UID
standing access to registered project paths while denying access to unrelated
user files. Removal of `sudo`, privileged groups, credential agents, and
container-management authority prevents the agent from escaping that UID. A
private mount namespace or equivalent sandbox is the per-session enforcement
boundary: it exposes only that session's grants and enforces mount-level
read-only access.

Offer a versioned OCI image as an optional, pinned execution environment. The
container receives the same delegated paths and access modes as a host-native
session; it neither defines nor broadens filesystem authority. That profile is
designed here and deferred beyond release 1, which ships host-native execution
only.

Agent-proof Git authorization and publication are intended to become a
separate privileged capability in the orchestrator subproject. The
`orchestrator/` directory is currently in very early stages: it sequences
playbook steps and delegates decisions to project-local scripts. It is not
currently a security boundary, authorization service, credential holder, or
publication broker. Existing Git hooks and wrappers remain in force as
accident-prevention controls until an independently protected orchestrator
replacement ships in the same release.

This proposal supersedes the separate
[Factory CLI Security Hardening](superseded/factory-cli-security-hardening.md) and
[Containerized Agent Factory Distribution](superseded/containerized-agent-factory.md)
proposals. It separates three concerns that those proposals mixed together:
host filesystem isolation, reproducible execution, and Git/publication
authority.

## Motivation

The immediate problem is that an AI CLI started as the human operator inherits
that human's UID and therefore their filesystem permissions, credential
agents, privileged groups, and process authority. Repository instructions and
tool hooks cannot reliably constrain a process that already possesses those
rights.

The first goal is consequently **UID-based access and escalation control**:
run the agent as a different, unprivileged UID; grant that UID access only to
related paths; and remove every supported route by which it could become the
human user, root, or a container/runtime administrator. The delegation record
describes intended grants, but kernel-enforced discretionary access control
(DAC), POSIX ACLs, and mount permissions provide enforcement.

Containers answer a different question: how to pin and distribute the Factory
and its toolchains. Future orchestrator work answers a third: how to mediate
privileged Git integration and publication. Neither is a prerequisite for
obtaining the first security improvement.

## Alternatives Analysis

The status quo is the baseline. Scores are relative (`-1`, `0`, `+1`) and
weights reflect this proposal's critical security assurance and secondary
usability and operations goals.

| Criterion                                     | Weight | Human UID + remote protection (baseline) | Dedicated UID + ACL + namespace + cgroup | Landlock-only under human UID | Per-project VM |
| --------------------------------------------- | -----: | ---------------------------------------: | ---------------------------------------: | ----------------------------: | -------------: |
| Deny unrelated filesystem access              |      3 |                                        0 |                                       +1 |                            +1 |             +1 |
| Prevent identity or credential escalation     |      3 |                                        0 |                                       +1 |                            -1 |             +1 |
| Support unrelated multi-tree grants           |      2 |                                        0 |                                       +1 |                            +1 |              0 |
| Enforce per-path read-only access             |      3 |                                        0 |                                       +1 |                            +1 |             +1 |
| Preserve ordinary development usability       |      2 |                                        0 |                                        0 |                            +1 |             -1 |
| Operational and deployment simplicity         |      2 |                                        0 |                                       -1 |                            +1 |             -1 |
| Evidence available for release-1 backend      |      2 |                                        0 |                                        0 |                            -1 |             -1 |
| Reuse contract for a future container profile |      1 |                                        0 |                                       +1 |                             0 |             +1 |
| Clear authorization boundary                  |      2 |                                        0 |                                       +1 |                             0 |             +1 |
| **Weighted total**                            |        |                                    **0** |                                  **+12** |                        **+7** |         **+6** |

The dedicated-UID design wins because it changes operating-system identity as
well as path visibility while retaining explicit multi-tree grants. Landlock
remains defense in depth: under the human UID it does not remove inherited
credential and process authority. A VM provides a strong outer boundary but
adds lifecycle, file-sharing, and toolchain costs and does not by itself define
fine-grained related-path grants. The result is not close: changing any single
weight within the stated 1–3 range does not displace the selected option. The
null option remains the comparison baseline and retains remote protection as a
deployment prerequisite, not as local isolation.

## Goals

1. **Separate identity and prevent escalation.** An agent runs under a
   dedicated UID whose DAC permissions differ from the human operator's. It
   has no supported route to acquire the human UID, root, privileged groups,
   credential agents, or container-management authority.
2. **Protect unrelated host files.** Filesystem ownership, permissions, ACLs,
   and sandbox mounts allow the agent to access related paths while denying
   unrelated user files and credentials.
3. **Support related files wherever they live.** A delegation may contain
   several paths from different directory trees. Each grant states whether
   access is read-only or read-write; the model is not limited to one mounted
   repository or one common parent.
4. **Keep delegation policy outside agent control.** Project content,
   repository configuration, model instructions, and the agent itself cannot
   add paths, broaden access, or change the effective policy.
5. **Preserve normal development capability.** Within delegated paths, agents
   can edit files, run project tools, test, and create reviewable local
   changes. Host-native execution remains supported.
6. **Provide an optional pinned environment.** Projects may select a versioned
   container image to obtain reproducible Factory and toolchain versions
   without changing the filesystem authority model. The profile is specified
   here and deferred beyond release 1.
7. **Develop agent-proof Git authorization and publication separately.** A
   future privileged orchestrator capability will mediate protected Git
   mutations and publication. Until then, existing guardrails remain active
   and are described honestly as bypassable accident prevention.

## Non-goals

- Protecting delegated read-write files from the agent authorized to modify
  them.
- Treating containers, repository hooks, `AGENTS.md`, command-string matching,
  or Git branch names as security boundaries.
- Requiring a container for every Factory session.
- Restricting a project to one repository, one directory tree, or one
  read-write mount.
- Moving general Git authorization or publication policy into a container
  launcher.
- Preventing compromise of the trusted host kernel, sandbox implementation,
  container runtime, or future privileged orchestrator.
- Guaranteeing selective network egress in the first release.
- Making arbitrary project dependencies reproducible without a project-owned
  environment definition.
- Preventing execution of arbitrary programs within delegated paths in the
  first release. Executable allowlisting, dependency trust, interpreter
  mediation, and scoped command approval remain separate hardening work.
- Preserving project tools that require the ordinary session to create user or
  mount namespaces. Container-based test suites, `bwrap`-based tools, and
  nested AI-CLI sandboxes are unsupported in release 1 unless adapted to a
  launcher-created, capability-free sandbox profile.
- Replacing protected remote refs, independent CI, backups, or tested
  restoration. Those remain deployment prerequisites because a writable
  project can be damaged by its agent.

## Threat Model

The agent process, model output, repository contents, dependencies, generated
programs, project tool configuration, and remote content are untrusted. Assume
the agent can execute arbitrary programs with all authority granted to its
session.

The human operator, host kernel, operating-system sandbox policy, protected
delegation records, administrative provisioning path, and remote Git
protection are trusted. A future privileged orchestrator control plane and
publication credential store will join the trusted base only after their
design and implementation satisfy a separate security proposal.

The design contains damage to explicitly delegated paths and capabilities. It
does not promise that an agent cannot corrupt a writable project or disclose a
credential that a human deliberately places inside a readable delegated path.

## Responsibility Boundaries

| Concern                               | Authority                                           |
| ------------------------------------- | --------------------------------------------------- |
| Agent execution identity              | Dedicated unprivileged operating-system UID         |
| Effective file access                 | UID, DAC, POSIX ACLs, and mount permissions         |
| Visible host paths and mount access   | Host launcher and operating-system sandbox          |
| Delegation-policy storage             | Human-controlled state outside delegated paths      |
| Grant provisioning and revocation     | Privileged human-operated administration path       |
| Session lifetime and process reaping  | Launcher-owned, agent-inaccessible cgroup           |
| Factory and toolchain versions        | Host environment or optional pinned container image |
| Current local workflow gates          | Project-local Factory scripts                       |
| Current dangerous-Git prevention      | Existing hooks and wrappers; bypassable guardrails  |
| Future privileged Git and publication | Separately protected orchestrator capability        |
| Protected refs                        | Remote server enforcement                           |

## Filesystem Delegation Model

### Dedicated identity

Ordinary agents run as a dedicated `agent-factory` operating-system user. It
has no administrative, container-management, desktop-session, backup, or
human-login authority. Its private home contains only explicitly provisioned
Factory and provider state. It cannot read the human operator's home or
credential stores.

This UID boundary is the first and load-bearing control. The account has no
`sudo` rule, Factory-accessible setuid helper, login session, access to the
human's SSH or desktop agents, or membership in `docker`, `podman`, `libvirt`,
backup, journal, or other privilege-bearing groups. The launcher sanitizes the
environment and closes inherited file descriptors before changing identity.
Tests prove that the session cannot signal or inspect human-user processes and
cannot reach a container-runtime socket.

The agent home is not an unbounded policy surface. Launcher-owned CLI
configuration, hooks, MCP definitions, and permission rules are immutable to
the agent. A separate writable state directory contains only caches, logs, and
provider state classified as non-authoritative. The launcher reconstructs or
validates authoritative configuration on every session; editing writable state
cannot change later grants or trusted hooks.

Every release-1 session runs in a launcher-owned cgroup created before any
agent-controlled code starts. The agent UID has no write access to the cgroup
hierarchy and cannot migrate itself or descendants out of that cgroup. The
launcher treats complete cgroup reaping as a prerequisite for namespace
teardown, revocation, and a successful session-end audit record.

The dedicated account has a `nologin` shell, no password, SSH keys, user cron
or `at` jobs, per-user systemd manager, or D-Bus activation path. No service
starts programs as that UID except the protected launcher. Provisioning and
revocation probes use a root-owned helper that enters the target cgroup and
sandbox, drops to the agent UID only for the access check, reports the result
through a launcher-owned descriptor, and exits; it cannot accept an arbitrary
command or create a persistent execution path.

The identity boundary and sandbox apply equally to host-native and
containerized execution. A container must run from the dedicated identity and
must not receive the human user's broader authority merely to preserve file
ownership.

### Delegation policy

A session is launched from a host-controlled policy such as:

```yaml
project: /work/acme/application
paths:
  - path: /work/acme/application
    access: read-write
  - path: /work/shared/schemas
    access: read-only
  - path: /data/test-fixtures
    access: read-only
```

The policy is an allowlist. No shared parent is implied: granting
`/work/acme/application` and `/data/test-fixtures` does not grant `/work`,
`/work/acme`, or `/data`.

The policy file is not itself enforcement. It is input to a privileged,
human-operated provisioning step and the trusted launcher. Release 1 enforces
a grant as follows:

1. Project and related files remain owned by the human or project owner, not
   by `agent-factory`.
2. For each `read-only` grant, provisioning gives the agent UID only the
   traversal and read ACL entries required for that tree. Because the agent
   does not own those objects, it cannot use `chmod` or `chown` to grant itself
   write access.
3. For each `read-write` grant, provisioning installs access ACLs for existing
   objects and default ACLs on directories so new content remains editable by
   both the human and agent UID. The session uses a documented umask. Tests
   prove that each user can edit files created by the other without
   administrative repair.
4. Parent directories receive traversal-only ACLs where needed. They do not
   receive list or read access merely because a descendant is delegated.
5. A root-owned launcher constructs a private mount namespace before changing
   to the agent UID. It exposes each canonical grant separately, makes
   read-only bind mounts recursively read-only, and locks mount attributes
   against remount by namespaces available to the session. The namespace hides
   unrelated host trees that DAC would otherwise expose, including
   world-readable files outside the minimum runtime filesystem.
6. The launcher then drops supplementary groups and every capability, changes
   to the agent UID, enables `no-new-privileges`, and applies a syscall policy
   that denies creation or entry of user and mount namespaces. No subordinate
   UID or GID ranges are assigned to `agent-factory`. Only after verifying this
   final state does it start agent-controlled code. The session cannot invoke
   the privileged provisioning step.

DAC and ACLs are persistent project-registration state bound to the dedicated
UID. The private mount namespace enforces which subset of that standing
authority a particular session can exercise and strengthens read-only
semantics. Both layers must agree. The agent UID has no login or unsandboxed
execution path. A session fails closed if the effective UID, ACL probe,
namespace restrictions, or mount probe differs from policy.

ACL grants have an explicit administrative lifecycle. Provisioning records
each installed access/default ACL and traversal entry in owner-controlled
state. A privileged revocation first prevents new launches, terminates and
reaps every launcher cgroup whose policy references the grant, dismantles its
namespaces, removes only the recorded ACL entries, and verifies denial under
the agent UID. Failure at any step leaves the grant marked `revoking`, blocks
new sessions, and requires operator repair; it never reports successful
revocation. Concurrent sessions with different policies remain confined to
their own namespaces. Persistent project registration avoids racing ACL
removal between concurrent sessions; revocation applies to all sessions that
reference the revoked grant.

The launcher writes an owner-only invocation record outside every delegated
path. It records the effective UID, canonical paths and stable identities,
access modes, execution profile, image digest where applicable, network and
credential posture, command, start/end time, and exit status. The agent cannot
mount or write this location. Failure to create or finalize the record fails
the launch closed; the record is evidence against the agent, not against the
trusted human owner who controls its storage.

Before launch, the trusted launcher:

1. reads policy only from owner-controlled state outside delegated paths;
2. resolves every path without executing project-provided code;
3. rejects missing paths, ambiguous paths, disallowed broad roots, and unsafe
   policy or path ownership;
4. records stable path identity sufficient to detect replacement between
   validation and sandbox entry;
5. rejects grants whose canonical paths overlap with contradictory access
   modes;
6. verifies that DAC and ACL entries grant no more than the declared access
   and that cross-user editing works for read-write paths;
7. constructs a private mount namespace from the validated grants;
8. verifies the effective access mode under the final agent UID before
   starting agent-controlled code; and
9. fails closed rather than widening a grant or falling back to the human
   identity.

Symlinks inside a delegated tree do not confer access to an undelegated target.
Pre-existing hardlinks are inode aliases and therefore make their target part
of the grant. Provisioning inspects entries whose link count exceeds one and
accounts for their other same-filesystem links within configured, owner-chosen
scan roots. An unaccounted link fails closed. `git clone --local`, shared
content-addressed package stores, `cp -l` fixtures, and similar layouts are
therefore expected to fail unless the human records an explicit acceptance of
the inode identities and all affected paths in protected policy. Each scan has
an owner-configured entry and elapsed-time budget; exhausting either refuses
provisioning rather than silently accepting the topology. Nested mounts are
hidden or rejected unless explicitly granted. All nonessential inherited
descriptors are closed before the sandbox transition. Scan roots, budgets, and
accepted inode identities live with the protected delegation policy outside
every delegated path. The launcher checks recorded filesystem generations and
stable identities at every launch; a changed identity or link count triggers a
complete bounded rescan, and budget exhaustion or an unaccounted link refuses
launch. These properties are tested for each supported backend rather than
inferred from lexical path checks.

Default ACLs do not guarantee that every project tool preserves effective ACL
masks. After checkout, formatting, archive extraction, dependency installation,
or another ordinary workflow step, the launcher re-runs the bidirectional ACL
probe before a subsequent session. A failed probe refuses launch. If a tool
strips an ACL during a session,
the affected operation may make the tree temporarily unusable to one identity;
the session must not broaden permissions itself. The operator runs the
privileged reconciliation command, which restores only ACL entries recorded by
provisioning and re-runs both UID probes before work resumes.

### Access modes

- `read-only` permits traversal and reads but denies content creation,
  mutation, and deletion through both DAC/ACL and a read-only mount. Metadata
  operations are denied where the selected kernel and backend provide an
  enforceable control; each backend contract names residual metadata
  operations instead of making a portable blanket claim.
- `read-write` permits normal project mutation within the grant.
- No implicit access is inherited from the human user's groups, environment,
  credential agents, or desktop session.

Resource and network policy are separate dimensions. The launcher may add
CPU, memory, process, and network constraints, but filesystem delegation does
not depend on selective-egress enforcement.

## Execution Profiles

### Host-native profile

The launcher enters the configured operating-system sandbox as the dedicated
identity and exposes the delegated paths with their declared modes. Approved
host toolchains may be used. This is the baseline profile and must support
ordinary development without requiring container-specific repository layouts.

The release-1 Linux reference is a root-constructed private mount namespace
with separate bind mounts for each grant, layered on the dedicated UID and
provisioned ACLs. Namespace construction and mount locking precede the UID
transition; the final session has no capabilities, subordinate-ID mapping, or
permission to create or enter user or mount namespaces.
Landlock, AppArmor, SELinux, or systemd sandboxing may add defense in depth but
does not replace the UID/DAC contract. Each supported backend records kernel
version and relevant ABI and proves multi-tree grants, mount-level read-only
enforcement, symlink and nested-mount handling, inherited-descriptor closure,
and absence of the human home and credentials.

### Containerized profile (deferred)

The optional containerized profile publishes Agent Factory and supported
toolchains as versioned, digest-addressable OCI images. Its purpose is pinned,
portable execution—not a different authorization model.

This profile is deferred beyond release 1. A rootless runtime executing as
`agent-factory` requires subordinate UID and GID ranges for that account, which
the release-1 identity model refuses in enforcement step 6. Release 1 therefore
ships one identity model rather than two. The profile may ship once one of the
following is evidenced: a runtime that needs no subordinate ranges, a
root-constructed capability-free container session that reuses the host-native
ordering, or an accepted and recorded residual risk. Its user namespace and
mounts must in every case be constructed and locked before agent-controlled
code runs, under the same ordering the host-native reference uses.

When it ships, the trusted launcher derives bind mounts from the already
validated delegation policy:

- every delegated path is mounted separately with its declared access mode;
- no common parent, host home, credential directory, or container-runtime
  socket is mounted implicitly;
- image selection and runtime configuration come from host-controlled state;
- the image cannot request additional host paths or change a read-only grant;
- the runtime is rootless, capabilities are dropped, and
  `no-new-privileges` is enabled;
- effective ownership and read/write behavior are tested before agent work;
  and
- unsupported runtime or ownership behavior fails closed.

The container may provide Factory commands, AI CLIs, Git, language runtimes,
linters, and formatters. Projects may extend or replace the toolchain through
an explicit, reviewed environment definition. Container use must not forbid
host-native execution, external related-file grants, or ordinary project
topologies merely because an initial image does not support them.

The [sandboxed Factory PoC](../../poc/sandboxed-factory/README.md) supplies
evidence only that rootless Podman can hide the host home and enforce a
no-network posture while preserving writes under its tested `keep-id` model.
It does not prove the dedicated-UID ownership contract in this proposal; that
contract requires the separate DAC/ACL interoperability tests above.

## Git and Publication Transition

### Current state

The `orchestrator/` subproject is in very early stages. Today it turns the
playbook crank: it selects the next step and calls project-local scripts. Its
in-project `factory/scripts/run-playbook` shim can select a package source from
the environment. Neither component is suitable for privileged execution, and
this proposal does not claim otherwise.

Current `block-dangerous-git.sh`, `commit-safe`, `verify-base`, and
`premerge-check` behavior remains shipped. These controls reduce accidents but
are bypassable by an agent with write access to the repository and `.git`.
Calling them non-security-boundaries does not remove, weaken, or replace them.

### Intended future boundary

A separate orchestrator security proposal will define agent-proof Git
authorization and publication. Its privileged path must execute outside every
delegated path, under an identity distinct from `agent-factory`, from an
immutable digest-pinned artifact. It must ignore project launchers and refuse
`AF_ORCHESTRATOR_SOURCE` or equivalent environment overrides. Gate
implementations, authorization records, publication credentials, and audit
records used by that path must be outside every agent-writable grant.

An ordinary agent session:

- may inspect and modify delegated repositories according to filesystem
  grants;
- may create local working-tree and index changes where granted;
- has no publication credential;
- cannot grant itself approval for a protected Git mutation;
- cannot change orchestrator policy or privileged audit records; and
- cannot convert a repository-local marker or hook result into authority.

A future privileged orchestrator capability:

- evaluates authorization against the current full 40-character Git object
  identities and other operation inputs;
- runs privileged integration or publication under a separate capability;
- constrains remotes, refspecs, protected destinations, force updates, and
  deletions;
- keeps credentials and authoritative records outside agent-readable and
  agent-writable paths;
- revalidates state at the point of use and rejects stale approvals; and
- records decisions in an audit sink the ordinary agent cannot modify.

For that future proposal, privileged Git operations mean publication to any
remote; creation, update, force-update, or deletion of protected local or
remote refs; changing configured remotes; and merging or rebasing into a
protected integration branch such as `dev` or `main`. Ordinary commits,
temporary branches, index changes, and merges among unprotected per-story
branches remain available inside a read-write grant. Protected refs are
declared per project; branch names alone never establish trust.

Repository hooks and Factory gates may report evidence to the orchestrator,
but only the orchestrator decides whether that evidence authorizes a privileged
operation. Detailed protocols, state machines, storage, and credential
handling belong to an orchestrator proposal and are not duplicated here.

No-regression transition rule: a release may demote or remove an existing Git
control only if the same release ships and tests its replacement. Until that
point, completion criteria and acceptance cases concerning agent-proof Git or
publication are requirements of the future orchestrator proposal, not claims
about the current `orchestrator/` implementation.

## Network and Credentials

The ordinary session receives only provider credentials explicitly required
to operate its AI CLI. Project, cloud, SSH, publication, password-store, and
desktop credentials are absent unless a human creates a separate, narrowly
scoped grant.

The first release supports two honest network postures:

- `standard`: network access available to the session; no selective-egress
  security claim;
- `deny`: network access blocked by the selected sandbox backend.

| Activity                        | Default posture                  | Reason                                      |
| ------------------------------- | -------------------------------- | ------------------------------------------- |
| Interactive AI CLI session      | `standard`                       | Must reach its configured model provider    |
| Offline Factory gate or hook    | `deny`                           | Requires no provider or dependency access   |
| Explicit dependency acquisition | `standard`                       | Separate, visible network-bearing operation |
| Future privileged publication   | Defined by orchestrator proposal | Not implemented by the current orchestrator |

Release 1 confines filesystem **access**, not disclosure. Any content readable
by an interactive agent can be transmitted through its model-provider channel.
A read-only grant prevents mutation; it does not make the granted content
confidential from the agent or its configured provider.

An allowlist proxy without a non-bypassable network boundary is an ergonomic
control, not a security boundary. Enforced selective egress requires separate
evidence and acceptance.

## Scope

### First release

- Dedicated unprivileged execution identity.
- Human-controlled, per-project delegation records outside delegated paths.
- Multiple canonical path grants across unrelated directory trees.
- Per-path read-only and read-write access modes.
- POSIX ACL provisioning, including default ACLs that make human-created and
  agent-created files mutually editable within read-write grants.
- At least one supported host-native operating-system sandbox backend.
- Default-deny visibility through the private mount namespace, layered on UID
  and ACL authority, plus symlink-escape tests.
- Explicit `standard` and `deny` network postures where the backend supports
  them.
- A common launcher contract from which host-native sandboxes and later
  container mounts are derived.
- A launcher-owned cgroup for every session, inaccessible to the agent UID,
  from which the session and all descendants cannot migrate.
- Preservation of existing Git guardrails with an explicit no-regression
  transition contract for later orchestrator-owned capabilities.
- An owner-only launcher audit record outside delegated paths for every
  invocation, recording effective UID, canonical grants, access modes, profile,
  image digest where applicable, network posture, command, and exit status.
- Diagnostics that report the selected identity, profile, grants, image
  digest where applicable, and effective network posture.

### Deferred

- The containerized profile and its versioned OCI image, until a runtime is
  evidenced that satisfies the release-1 identity model — in particular its
  refusal of subordinate UID and GID ranges for `agent-factory`.
- Additional operating-system sandbox and container-runtime backends until
  independently tested.
- macOS and Windows enforcement where their filesystem and container semantics
  differ.
- Shared-group-only models without POSIX ACLs and subordinate-UID recovery
  until proven safe.
- Enforced selective egress.
- Arbitrary project-environment reproducibility without an explicit project
  definition.
- The orchestrator's detailed Git authorization, publication, credential, and
  audit protocol, which requires its own proposal and acceptance proof.

## Security Claims

For a tested backend, the release may claim:

> Agent Factory runs ordinary agent processes under a dedicated unprivileged
> UID, removes supported escalation paths, and confines filesystem access to an
> explicit, human-controlled set of canonical paths and access modes through
> DAC, POSIX ACLs, and sandbox mounts. The agent cannot broaden that set or
> obtain the human operator's protected unrelated files and credentials
> through the supported launcher. This is an access-control claim, not a
> confidentiality claim for readable grants: interactive sessions may disclose
> readable content, including the provider credential deliberately provisioned
> to the agent identity, through their unrestricted model-provider connection.

When the deferred containerized profile ships, it may additionally claim:

> The selected digest identifies the Factory and bundled tool environment, and
> container mounts are derived from—not authoritative over—the same validated
> filesystem delegation policy.

Claims must name the tested operating system, sandbox or runtime backend,
version range, mount/grant set, identity model, and network posture. They
exclude kernel, runtime, sandbox, launcher, and orchestrator compromise.

## Acceptance Proof

| Case                                          | Required result                                                       |
| --------------------------------------------- | --------------------------------------------------------------------- |
| Undelegated human-home file                   | Read, write, metadata, and discovery attempts fail                    |
| Undelegated unrelated repository              | Agent cannot traverse or access it                                    |
| Read-write primary project                    | Normal edit, rename, delete, test, and local Git workflows succeed    |
| Read-only related directory in another tree   | Reads succeed; every mutation class fails                             |
| Read-write related directory in another tree  | Intended writes succeed without granting its parent                   |
| Two grants with no common delegated parent    | Both work; siblings and parents remain inaccessible                   |
| Symlink from a grant to an undelegated target | Target remains inaccessible                                           |
| Replaced path after validation                | Launch is refused or replacement remains inaccessible                 |
| Agent edits project-local policy              | Effective grants do not change                                        |
| Broad root or human-home grant                | Refused unconditionally in release 1                                  |
| Host-native profile                           | Uses the dedicated identity and passes all filesystem cases           |
| Container-runtime socket                      | Absent from the ordinary session                                      |
| `deny` network posture                        | Local-host and internet egress fail                                   |
| `standard` network posture                    | Report states that selective egress is not enforced                   |
| Human edits agent-created file                | Succeeds without administrative ownership repair                      |
| Agent edits human-created file in RW grant    | Succeeds without administrative ownership repair                      |
| Agent edits human-created file in RO grant    | Fails                                                                 |
| Ordinary toolchain strips a recorded ACL      | Next launch detects the failed bidirectional probe and refuses        |
| Privileged ACL reconciliation                 | Restores only recorded entries and both UID probes then pass          |
| Agent edits writable CLI state                | Next launch's grants and trusted hooks are unchanged                  |
| Cross-boundary hardlink                       | Re-scanned at launch; rejected unless explicitly accepted             |
| Local clone or shared package-store hardlinks | Expected refusal unless protected policy accepts all affected paths   |
| Undeclared nested mount                       | Hidden or launch refused                                              |
| Inherited host descriptor                     | Closed before agent-controlled execution                              |
| Concurrent session with a different policy    | Cannot reach the other session's grants                               |
| Process attempts to survive session end       | Reaped before namespace teardown; revoked grant then becomes denied   |
| Agent attempts to leave its session cgroup    | Migration and cgroup-hierarchy writes fail                            |
| Direct execution as the agent UID             | No shell, SSH, scheduler, user-service, or D-Bus path starts code     |
| Privileged access-verification probe          | Runs only the fixed probe in its sandbox and leaves no process        |
| Agent remounts a read-only grant read-write   | Remount fails and grant remains read-only                             |
| Agent creates a nested user namespace         | Creation denied; no undelegated access or subordinate-ID `chown`      |
| Agent edits in-project delegation decoy       | Host-controlled effective grants do not change                        |
| Agent edits `run-playbook` or sets source env | Future privileged path is unchanged; current path claims no authority |
| Agent edits a gate or fabricates approval     | Future privileged operation is not authorized                         |
| Agent attempts publication                    | Ordinary session has no publication credential                        |
| Launcher audit record                         | Created outside grants and not writable by the agent                  |

Tests must exercise non-default host UIDs, filenames containing spaces and
special characters, nested repositories, path replacement races, and every
supported backend. Each result records kernel version, sandbox backend, and
relevant ABI. Full 40-character Git SHAs are required in machine-consumed
authorization and audit records.

The following cases belong to the deferred containerized profile and are
prerequisites of its own release, not of release 1.

| Case                                       | Required result                                                                             |
| ------------------------------------------ | ------------------------------------------------------------------------------------------- |
| Containerized profile                      | Derives separate mounts and modes from the same grants                                      |
| Container requests an extra mount          | Request has no effect and launch fails closed where applicable                              |
| Pinned image missing under offline posture | Fails without pulling or enabling network                                                   |
| Container session identity                 | No subordinate UID or GID range is required or mapped, or the accepted residual is recorded |
| Container mount and namespace ordering     | Constructed and locked before agent-controlled code runs                                    |

## Operational Sequence

```text
human selects project and related paths
  -> trusted launcher loads host-controlled delegation policy
  -> privileged provisioning verifies UID-owned DAC and ACL grants
  -> launcher canonicalizes and validates every path and access mode
  -> launcher revalidates hardlinks and refuses stale or over-budget topology
  -> launcher selects host-native or pinned-container execution profile
  -> launcher creates an agent-inaccessible per-session cgroup
  -> launcher constructs and verifies the private mount namespace
  -> ordinary agent works only within delegated capabilities
  -> launcher reaps the cgroup and tears down the namespace
  -> current Factory hooks and wrappers reduce accidental Git damage
  -> future protected orchestrator independently authorizes integration
  -> future separate capability performs and audits publication

human revokes a grant
  -> privileged administration blocks launches referencing the grant
  -> launcher reaps every affected cgroup and dismantles its namespaces
  -> administration removes only recorded ACL entries
  -> fixed sandboxed probe verifies denial under the agent UID
  -> grant becomes revoked, or remains revoking on any failure
```

## Completion Criteria

- The filesystem delegation format and launcher contract are documented and
  versioned.
- A supported host-native backend passes the full multi-tree acceptance proof.
- The agent runs under a dedicated identity and cannot access the human home,
  unrelated credentials, or container-runtime authority.
- UID transition, environment sanitization, inherited-descriptor closure,
  privileged-group absence, and `no-new-privileges` are mechanically tested.
- Every session is confined to a launcher-owned cgroup that the agent cannot
  modify or leave, and session completion reaps all descendants.
- The dedicated UID has no login, SSH, scheduler, user-service, D-Bus, sudo,
  setuid, or other unsandboxed execution path; the fixed privileged access
  probe cannot execute arbitrary commands or persist.
- Read-only and read-write grants work across unrelated directory trees without
  implicitly exposing their parents.
- Human and agent UIDs can edit each other's files in read-write grants without
  administrative ownership repair.
- ACL provisioning has a recorded lifecycle; revocation blocks new launches,
  reaps affected sessions, removes recorded entries, and verifies denial.
- Read-only mounts remain locked against session-created namespaces; nested
  user/mount namespaces and subordinate UID/GID mappings are unavailable.
- The ordinary checkout, formatter, dependency-install, and archive workflows
  include a negative test that strips a recorded ACL, proves the next launch
  fails closed, and proves privileged reconciliation restores both UID probes.
- Hardlink identity and link counts are revalidated at every launch; changed
  topology is fully rescanned within protected budgets or launch is refused.
- Delegation records and effective policy cannot be modified by the agent.
- Authoritative agent configuration is immutable; writable home state cannot
  change later grants, hooks, or launcher policy.
- Host-native development remains usable for ordinary project workflows.
- Release 1 ships one identity model. When the deferred containerized profile
  ships, its pinned image consumes the common delegation model, passes the same
  filesystem proof for its supported runtime, and satisfies the identity model
  without subordinate UID or GID ranges unless a residual risk is recorded and
  accepted.
- Container-specific limitations are documented as profile limitations, not
  restrictions on the general authorization model.
- Existing Git guardrails remain active until the same release ships and tests
  their protected replacements.
- Ordinary sessions contain no Git publication credential.
- The current orchestrator is explicitly non-authoritative and early-stage;
  its future security boundary requires a separate accepted proposal and
  immutable execution path outside delegated storage.
- The launcher writes an owner-only per-invocation audit record outside every
  delegated path, and failure to write that record fails the launch closed.
- Documentation distinguishes filesystem isolation, execution
  reproducibility, and Git/publication authorization as independent concerns.

## Open Questions

1. How are provider credentials provisioned to the dedicated identity without
   exposing unrelated credential stores?
2. Which OCI runtime is the first supported container profile after testing
   the dedicated-user ownership model, and can it satisfy the identity model
   without subordinate UID and GID ranges for `agent-factory`?
3. Which orchestrator proposal defines the authorization protocol and its
   integration contract with Factory gates?

## Review (2026-08-10, adversarial)

Adversarial review of this proposal in the spirit of the `adversarial-review`
skill: the ten checks applied to a design seed rather than to a falsifiable
research claim. The review reads this proposal against the two documents it
supersedes and the twenty-one findings adjudicated in their appended reviews,
against the controls this repository ships today
(`factory/config/hooks/block-dangerous-git.sh`, `factory/scripts/commit-safe`,
`factory/scripts/verify-base`, `factory/scripts/premerge-check`), against the
orchestrator as it actually exists (`orchestrator/README.md`,
`factory/scripts/run-playbook`), and against the
[sandboxed Factory PoC](../../poc/sandboxed-factory/README.md) that supplies
its only execution evidence.

One BLOCKER and seven MAJOR defects were found. The separation of concerns is
the right one, and the multi-tree delegation model is a genuine improvement
over both predecessors. The defects are almost all consequences of the
supersession itself: the new document narrows its subject correctly but drops
controls, evidence qualifications, and adjudicated findings that its
predecessors carried.

### Verdict by check

| #   | Check                      | Verdict                                                                                               |
| --- | -------------------------- | ----------------------------------------------------------------------------------------------------- |
| 01  | Testable                   | WEAK — the matrix is concrete, but five rows test a component this proposal defers                    |
| 02  | Alternatives considered    | FAIL — third consecutive review; no comparison of backends, profiles, or the null option              |
| 03  | Tests severe               | WEAK — severe on filesystem confinement; silent on ownership, hardlinks, and the agent home           |
| 04  | Survives unchanged         | N/A (design seed, not a claim)                                                                        |
| 05  | Sources / exact wording    | WEAK — the PoC is cited for a property produced by the UID model this proposal forbids                |
| 06  | Independence               | WEAK — one PoC, one runtime, and the host-native backend is still unnamed                             |
| 07  | Assumptions explicit       | FAIL — orchestrator trust, gate location, ownership interoperability, and the agent home are unstated |
| 08  | Scope creep                | WEAK — scope discipline improved, but release 1 claims a separation whose mechanism is deferred       |
| 09  | Contrary evidence          | WEAK — the egress limit is carried honestly; the retired controls and the PoC UID mismatch are not    |
| 10  | Surviving refutation paths | PASS — five open questions and an honest deferral list                                                |

### Coverage of the inherited security objective

The superseded hardening proposal states six outcomes that compromise inside a
Factory CLI must not produce. Measured against them, this proposal improves
two, defers one to a document that does not exist, and drops one without
naming it.

| Inherited objective                            | Status here                                                                                |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------ |
| 1. Become the operator or gain admin privilege | IMPROVED — the dedicated identity now binds both profiles                                  |
| 2. Change the policy that constrains it        | PARTIAL — delegation policy is protected; gates, launcher, and agent home are not          |
| 3. Read unrelated user data or credentials     | MET, subject to backend proof                                                              |
| 4. Execute arbitrary programs                  | DROPPED — command mediation and executable trust appear in no section, including Non-goals |
| 5. Mutate protected refs or hide damage        | DEFERRED — and the shipped denials are demoted in the meantime (B1)                        |
| 6. Publish or contact services unapproved      | PARTIAL — no publication credential; egress unrestricted in every usable posture           |

### Defect register + amendments

**BLOCKER B1 — the supersession retires shipped controls and defers their
replacement to a proposal that does not exist.** Today
`factory/config/hooks/block-dangerous-git.sh` denies `git push`,
`push --force`, `reset --hard`, `clean -fd`, `branch -D`, and `--no-verify`
outright, and gates commits and merges on `.agent-factory/verify-base-ok` and
`.agent-factory/premerge-check-ok`. This proposal declares hooks non-boundaries
and repository-local markers incapable of conferring authority, drops both
`block-dangerous-git.sh` and `commit-safe` from `impact.boundaries` — the
superseded hardening proposal listed both — and assigns the replacement to an
orchestrator proposal that Open Question 5 admits is not yet identified. A
release could satisfy every Completion Criterion in this document while the
only mechanical Git enforcement the project owns has been documented into
irrelevance and nothing has replaced it. This is the same defect the first
review of the containerization proposal raised as its BLOCKER, reintroduced by
a different route.

*Amendment.* State the fate of every control named in the `boundaries` of both
superseded proposals. Add a Completion Criterion: no release may demote a
control unless the same release ships its replacement, and until the
orchestrator exists, the current hook keeps its behavior with its scope
relabelled as accident prevention rather than authority. Restore
`factory/config/hooks/block-dangerous-git.sh` and `factory/scripts/commit-safe`
to `impact.boundaries`.

**MAJOR A1 — the orchestrator is trusted by declaration, while its documented
purpose, location, and distribution all contradict that trust.**
`orchestrator/README.md` states that the orchestrator "replaces you pressing
'enter' between agent sessions. Nothing more," and that it "holds no opinions."
`factory/scripts/run-playbook` — copied into every initialized project, and
therefore inside the read-write grant — is a thirty-line shim that runs
`uvx --from` a *mutable* Git tag (`orchestrator-v0.1.0`), with the source
overridable through the `AF_ORCHESTRATOR_SOURCE` environment variable. This
proposal makes that component the authorization service, the publication
service, the credential holder, and the audit sink, without stating where it
executes relative to the sandbox, how it is acquired, or why an agent that can
rewrite the shim and set its environment cannot influence it.

*Amendment.* State that privileged orchestrator execution occurs outside every
delegated path, under an identity distinct from `agent-factory`, from an
immutable, digest-pinned artifact, with environment-sourced source overrides
refused on the privileged path. Add `factory/scripts/run-playbook` and the
orchestrator package to `impact.boundaries`, and add a matrix case: *agent
edits the in-project launcher or sets `AF_ORCHESTRATOR_SOURCE`* must not change
what the privileged path executes.

**MAJOR A2 — gate implementations live inside the read-write grant, and the
mechanism that protected them has been dropped.** The responsibility table
assigns local workflow legality to "Factory orchestrator and gate
implementations," but `init-factory` copies `factory/scripts/*` into the
project, which the delegation model then grants read-write. The superseded
containerization proposal solved this twice over — image-owned gates under
`/opt/agent-factory/factory`, and host-owned gate authorizations binding full
SHAs and consumed atomically with the operation they authorize, both recorded
as ACCEPTED remediations. Neither survives here, and the host-native profile is
the baseline, so the problem is now unmitigated in the default configuration.

*Amendment.* Require that gate implementations and gate-authorization records
reside outside every read-write grant in both profiles, and carry forward the
SHA-bound, atomically consumed authorization record. Add matrix cases: *agent
edits `factory/scripts/premerge-check`* and *agent fabricates an authorization
record* must not produce an accepted gate result.

**MAJOR A3 — Goal 4 contradicts the identity model, and the deferral list
removes the mechanism that would reconcile them.** A dedicated `agent-factory`
user writing into a human-owned project produces files the human does not own.
The mechanisms that make this workable — "shared-group write models and
subordinate-UID recovery" — are explicitly Deferred. The single piece of
evidence cited for preserved writes is the PoC, which achieved that property
with `--userns=keep-id`, that is, by running as the invoking human's UID: the
exact arrangement this proposal forbids in the paragraph above the citation.
Release 1 therefore has no evidence for its writable-project case under the
identity it mandates, and Goal 4 rests on a deferred mechanism.

*Amendment.* Define the ownership contract for release 1 explicitly — umask
plus a shared group, POSIX ACLs, or an idmapped mount — and prove it: *human
edits a file the agent wrote, and the agent edits a file the human wrote,
without administrative action*. Alternatively, gate the dedicated identity
behind the same spike requirement this proposal applies to unproven container
runtimes. Restate the PoC citation as evidence for host-home concealment and
no-network enforcement only.

**MAJOR A4 — the two network postures do not describe the posture every real
session uses.** An agent session must reach its model provider, so `standard`
is the only posture an interactive session can run; `deny` applies to gates and
hooks. The superseded proposal's per-command posture table, recorded as the
ACCEPTED remediation of finding A6, is gone. As written, a reader can believe
`deny` is an available operating mode for agent work, and the Security Claims
never state that everything readable inside a grant can leave through the
provider channel.

*Amendment.* Restore a table assigning a posture to every command or phase.
State in both the Motivation and the Security Claims that release 1 confines
*access*, not *disclosure*, and that read-only grants protect the host from
mutation, not their contents from exfiltration.

**MAJOR A5 — the access-mode definition exceeds what the candidate backends can
enforce, and the backend is still an open question.** `read-only` is defined to
deny "creation, mutation, deletion, metadata changes, and executable state
changes." Landlock, the first backend named, has no access right covering
`chmod`, `chown`, or `utimes`; truncation is only restrictable from ABI 3
(Linux 6.2); and its network scoping covers TCP connect and bind only, so the
`deny` posture requires a network namespace regardless. Read-only bind mounts
in a mount namespace do satisfy the stated semantics — which quietly answers
Open Question 1 in favor of a mechanism the document never names.

*Amendment.* Define each access mode per backend, with the minimum kernel and
ABI version, or weaken the general definition to what every supported backend
enforces and state metadata separately. Require the acceptance matrix to record
kernel version, backend, and ABI alongside each result.

**MAJOR A6 — the launcher audit record has been lost.** The superseded design
required one record per invocation — resolved image digest, canonical project
path with device and inode, profile, posture, credential grants, command, exit
status — written to owner-only storage outside the project, with privileged
operations failing closed when the record cannot be written. That was finding
A4, ACCEPTED. Here the only audit belongs to the orchestrator, which is
deferred, and the launcher receives "Diagnostics that report the selected
identity, profile, grants…" — a display feature, not a record. Release 1 as
scoped produces no audit trail at all.

*Amendment.* Restore the per-invocation launcher record and its storage
location, add a Completion Criterion, and add a matrix case proving the record
is not writable from inside the session.

**MAJOR A7 — controls dropped by silence.** Command mediation, executable and
dependency trust, the interpreter problem, scoped and expiring approval, and
the recovery prerequisites (protected remote refs, backups, tested restoration)
were all substantive sections of the superseded hardening proposal, and two of
them were adjudicated findings. None appears here — not in Scope, not in
Deferred, not in Non-goals. The first review of the containerization proposal
named exactly this failure mode: a reader of this document alone concludes the
security work is finished.

*Amendment.* Add the dropped controls to Deferred by name, or to Non-goals with
a reason. Restore protected remote refs, independent CI, backups, and tested
restoration as documented deployment prerequisites, since this proposal again
grants the agent read-write access to `.git` and again defers protecting a
project from its own agent.

**MINOR A8 — the agent's own home is an unbounded writable surface and a policy
vector.** The dedicated identity's home "contains only explicitly provisioned
Factory and provider state," is writable by the agent, is not a delegated path,
and has no declared access mode. AI CLI configuration lives there — settings,
hooks, permission rules, MCP server definitions — and that configuration
executes commands. Goal 3 says the agent cannot change its effective policy;
this path lets it change what its own harness runs at the next launch.
*Amendment:* declare which parts of the agent home are launcher-managed and
read-only, and add a matrix case: *agent edits its CLI configuration* leaves
grants and hook set unchanged at the next launch.

**MINOR A9 — symlinks are addressed; hardlinks, nested mounts, and inherited
descriptors are not.** A hardlink inside a grant to a file outside it is
indistinguishable from an ordinary entry to both Landlock and a bind mount,
because both are path-based and the link is a path in the tree. Nested mount
points inside a grant and descriptors inherited across the sandbox transition
raise the same question. *Amendment:* extend the validation step and the matrix
to hardlinks and nested mounts, or state plainly that delegation is granted at
inode level and that a grant's pre-existing links are part of the grant.

**MINOR A10 — the acceptance matrix answers an open question.** The row "Broad
root or human-home grant — refused unless an explicit administrative policy
permits it" decides that broad grants are permissible under policy, while Open
Question 2 asks whether release 1 should reject them unconditionally. Related:
"Agent edits project-local policy — effective grants do not change" is not
executable until a project-local policy path exists to plant. *Amendment:*
resolve the question in one place, and name the decoy path the test writes.

**MINOR A11 — `supersedes` carries a list, and the predecessors were retired
before their replacement was accepted.** `factory/rulebooks/templates/proposal.md`
line 20 defines `supersedes` as "proposal path, or null," and the second review
of the containerization proposal already flagged list usage as a template
violation. Both predecessors now read `status: superseded` while this document
reads `status: open`, so the project's documented controls point at a design
that has not been accepted. *Amendment:* either extend the template to permit a
list and lint it, or keep one edge and express the rest in prose; hold the
predecessors at `open` until this proposal is `accepted`.

**NOTE A12 — the adjudication trail is severed.** Two adversarial reviews
produced twenty-one findings with recorded dispositions, and ten of them
(A11–A20 of the second review) were never resolved — the proposal carrying them
was superseded instead. Which dispositions survive into this design is recorded
nowhere. *Amendment:* add a carry-forward table mapping each prior finding to
carried, dropped, or obsolete, with a reason. Several findings in this review
are prior findings that reappeared because no such table existed.

**NOTE A13 — the alternatives gap is now three reviews old.** With
`architecture_change: true` and `assurance: critical`, and with Open Questions 1
and 4 both being selections among genuine alternatives, a Pugh matrix over the
candidate host-native backends — and over the null option of the existing
host-native model plus remote branch protection — is this project's own
documented expectation. This is a judgment call for the owner: produce the
matrix, or record that the comparison was made and its outcome accepted without
one.

**NOTE A14 — "privileged Git mutation" is never enumerated, and the Factory
workflow depends on the answer.** Factory agents today create branches, run
`premerge-check`, and merge locally; the implementation dispatcher merges its
subagents' branches. If local merges into `dev` are privileged, the entire
dispatch workflow becomes orchestrator-mediated, which is a large unstated cost.
If they are not, the claim that privileged Git authorization resides in the
orchestrator is much narrower than it reads. *Amendment:* enumerate the
privileged operations, local ones included.

**NOTE A15 — the estimate did not move while the scope grew.** This document
spans host sandboxing, container distribution, and an orchestrator boundary —
more surface than either predecessor — with `basis: judgment`,
`confidence: low`, and both effort fields `unknown`. At minimum, size release 1
once Open Question 1 is answered, since the backend choice drives most of the
work.

### Recommendation

Status remains `open`. B1 must be resolved before any story is planned: as
scoped, release 1 is a net reduction in mechanical enforcement, because it
demotes working controls and defers their replacement to an unwritten proposal.
A1 through A3 must be resolved before `accepted` — each one places a trusted
component inside agent-writable space or rests a goal on a deferred mechanism.
A4 through A7 are restorations of remediations the predecessors already earned
and should be cheap to carry forward. A12 is the process fix that prevents the
next supersession from losing them again.

The strongest section is the delegation policy and its eight-step validation.
Multi-tree grants with per-path access modes, no implied common parent,
validation without executing project code, stable path identity across the
validation-to-entry gap, and refusal to widen or fall back are a better model
than either predecessor offered, and the separation of filesystem isolation
from execution reproducibility from Git authority is the correct decomposition.
The gap is that only the first of those three concerns is actually specified
here; the second rests on one runtime's evidence, and the third is a promise
addressed to a document that does not exist.

## Review Response (2026-08-10)

The proposal remains `open`. The design body above incorporates the following
remediations; the original review remains unchanged as an audit trail.

| Finding | Disposition                                                                                                                                                                                    |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| B1      | Addressed: existing Git hooks and wrappers remain active until protected replacements ship in the same release.                                                                                |
| A1      | Addressed: `orchestrator/` is explicitly very early-stage and non-authoritative; the future privileged path requires a separate proposal, identity, location, and immutable artifact.          |
| A2      | Addressed at boundary level: future authoritative gates and records must live outside writable grants; current project-local gates make no security claim.                                     |
| A3      | Addressed: release 1 uses human ownership plus access/default POSIX ACLs and requires bidirectional editing tests. The PoC evidence is narrowed.                                               |
| A4      | Addressed: activity-specific network postures and the access-versus-disclosure limitation are explicit.                                                                                        |
| A5      | Addressed: release-1 reference is a private mount namespace layered on UID/DAC/ACL enforcement; backend claims record kernel and ABI limitations.                                              |
| A6      | Addressed: owner-only per-invocation launcher records are restored and fail closed.                                                                                                            |
| A7      | Addressed: executable/dependency trust and command mediation are explicitly outside release 1; remote protection and recovery remain prerequisites.                                            |
| A8      | Addressed: authoritative agent-home configuration is immutable and writable state is non-authoritative.                                                                                        |
| A9      | Addressed: hardlinks, nested mounts, and inherited descriptors have rules and acceptance cases.                                                                                                |
| A10     | Addressed: `/` and the human home are refused unconditionally in release 1; the project-local policy test uses a decoy.                                                                        |
| A11     | Addressed structurally: the single-value `supersedes` chain is new proposal → container proposal → hardening proposal. Source proposals remain superseded as explicitly directed by the owner. |
| A12     | Partially addressed by this response table. A full twenty-one-finding carry-forward remains required before acceptance.                                                                        |
| A13     | Open: alternatives analysis is still required before acceptance.                                                                                                                               |
| A14     | Open: the future orchestrator proposal must enumerate privileged Git operations. No current orchestrator authority is claimed.                                                                 |
| A15     | Open: estimate remains unknown until the reference implementation is decomposed.                                                                                                               |

## Review 2 (2026-08-10, adversarial — remediation)

Adversarial re-review of the remediation recorded in the Review Response above.
The review verifies each claimed disposition against the amended text and
against the artifacts the proposal cites, then looks for defects the
remediation itself introduced. The verdict table in the first review is
superseded by the table here; its defect register is retained as an audit
record and must not be edited.

The BLOCKER is cleared, and no BLOCKER is raised in this pass. The remediation
is substantive: it replaces a declared authority with an enforced one, and the
enforcement model it now names — a dedicated UID with POSIX ACLs beneath a
private mount namespace — is a stronger and more honest design than the
delegation-record abstraction it replaces. Two MAJOR defects are new, both
introduced by that shift, and both concern the boundary between what the ACLs
grant and what the namespace scopes.

### Verification of claimed dispositions

| Finding | Verified disposition                                                                                                                            |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| B1      | ACCEPTED — four control paths restored to `boundaries`, a no-regression transition rule, and a matching Completion Criterion                    |
| A1      | ACCEPTED — the current orchestrator is named non-authoritative; the future path requires separate identity, location, and pinned artifact       |
| A2      | ACCEPTED at boundary level — project-local gates now make no security claim, which is consistent with the B1 rule                               |
| A3      | ACCEPTED — human ownership, access and default ACLs, documented umask, bidirectional edit cases; the PoC citation is correctly narrowed         |
| A4      | ACCEPTED — activity posture table, and the access-versus-disclosure limit reaches the Security Claims, not only the prose                       |
| A5      | ACCEPTED — mount namespace named as the release-1 reference, Landlock demoted to defense in depth, kernel and ABI recorded per result           |
| A6      | ACCEPTED — owner-only per-invocation record, fail-closed, matrix case, and the earlier "against the agent, not the owner" qualification         |
| A7      | ACCEPTED — the dropped controls appear in Non-goals by name, and recovery prerequisites are restored                                            |
| A8      | ACCEPTED — authoritative agent configuration is immutable, writable state is non-authoritative, with a matrix case                              |
| A9      | ACCEPTED — hardlinks, nested mounts, and inherited descriptors each have a rule and a case; residue in A18                                      |
| A10     | ACCEPTED — broad roots refused unconditionally, the stale open question removed, and the decoy named                                            |
| A11     | ACCEPTED — the chain on disk is this proposal, then `superseded/containerized-agent-factory.md`, then the hardening proposal, all single-valued |
| A12     | PARTIAL, as claimed — the response table is not the twenty-one-finding carry-forward                                                            |
| A13–A15 | OPEN, as claimed                                                                                                                                |

### Verdict by check (re-run)

| #   | Check                      | Verdict                                                                                                  |
| --- | -------------------------- | -------------------------------------------------------------------------------------------------------- |
| 01  | Testable                   | PASS — the matrix now tests the mechanism this release ships, not a deferred component                   |
| 02  | Alternatives considered    | FAIL — unchanged; acknowledged as open in the response                                                   |
| 03  | Tests severe               | PASS — ownership interoperability, hardlinks, nested mounts, descriptors, and decoys refute              |
| 04  | Survives unchanged         | N/A (design seed, not a claim)                                                                           |
| 05  | Sources / exact wording    | PASS — the PoC now supports only what it demonstrated                                                    |
| 06  | Independence               | WEAK — one PoC and one runtime remain, but release 1 no longer rests on them                             |
| 07  | Assumptions explicit       | WEAK — the privilege that builds the namespace and the lifetime of ACL grants are implicit               |
| 08  | Scope creep                | PASS — release 1 now claims only what its own mechanisms enforce                                         |
| 09  | Contrary evidence          | PASS — bypassable guardrails, disclosure through the provider channel, and backend limits are all stated |
| 10  | Surviving refutation paths | PASS — three open questions, each genuinely undecided                                                    |

### New defect register + amendments

**MAJOR A16 — ACL grants are persistent host state, while the document
describes them as session grants.** The Summary says the policy grants "each
agent session" access, and Goal 4 speaks of policy the agent cannot broaden.
Enforcement steps 1 through 4, however, install access and default ACLs on
disk. Those entries outlive the session, and they accumulate: after three
projects have been delegated, the `agent-factory` UID holds standing read-write
authority over all three, reachable by absolute path from any process running
under that UID, including a stale background process from an earlier session.
Only the mount namespace scopes a session to its own grants. This inverts the
document's own summary of the layering — "DAC and ACLs bind authority to the
dedicated UID; the mount namespace limits visibility" — because visibility is
what confines one session's authority to one delegation. No de-provisioning,
expiry, or revocation step is defined anywhere.

*Amendment.* State that ACL grants are persistent host state with a lifecycle,
and define the revocation step and who performs it. Reclassify the mount
namespace as enforcement for session scoping rather than visibility, or install
and remove ACLs per session and state what happens when teardown fails or two
sessions run concurrently. Add matrix cases: *a second concurrent session with
a different policy* cannot reach the first session's grants, and *a process
surviving session end* has no path into a revoked grant.

**MAJOR A17 — the privilege that constructs the mount namespace, and the
agent's own namespace authority, are unstated.** A read-only bind mount
prevents writes only while the agent cannot remount it read-write. That holds
when the namespace is created at higher privilege and the mounts propagate
locked to any namespace the agent can create; it does not hold if the agent
shares the user namespace that owns the mounts. The proposal never says who
creates the namespace, at what privilege, whether unprivileged user namespaces
are available to the session, or whether subordinate UID ranges are mapped.
`no-new-privileges` does not prevent user-namespace creation, and a nested user
namespace grants `CAP_SYS_ADMIN` and `CAP_CHOWN` within itself — the same
capability that produced the unrecoverable-ownership finding against the Docker
profile in the superseded proposal.

*Amendment.* State the launcher's privilege and the ordering of namespace
construction against the UID transition. Require that read-only mounts are
locked against the session's namespaces. Decide explicitly whether the session
may create nested user namespaces and whether subordinate UID ranges are mapped
for it. Add matrix cases: *agent attempts to remount a read-only grant
read-write*, and *agent creates a nested user namespace and attempts to reach an
undelegated path or to chown grant content into subordinate UID space*.

**MINOR A18 — the hardlink rule refuses ordinary Git and package layouts, and
its cost is unbounded.** `git clone --local` hardlinks object files into the
source repository's store, `git worktree` setups and content-addressed package
stores do the same, and `cp -l` is common in fixtures. Under "provisioning
detects and rejects cross-boundary hardlinks where it cannot prove that this is
intended," those ordinary topologies fail provisioning, and the detection scan
is a full walk of every grant with no stated bound. *Amendment:* define
detection as entries with a link count above one whose other links resolve
outside the grant, state the expected failure for `--local` clones and shared
package stores, give an explicit human accept mechanism, and bound or budget
the scan for large trees.

**MINOR A19 — the ACL interoperability tests prove the initial state, not the
steady state.** Default ACLs are inherited on creation, but ordinary tools
overwrite them: `rsync`, `tar`, `unzip`, `install -m`, and a `git checkout`
that carries a mode change can clear the group mask and drop the effective
access of one UID or the other in the middle of a session. The two matrix rows
run immediately after provisioning. *Amendment:* add a case that runs the
project's ordinary toolchain — checkout, formatter, dependency install — and
then re-verifies that both UIDs can still edit, and document the repair path
when a tool strips an ACL.

**MINOR A20 — the supersede banners on both predecessors are stale by one
revision.** Each says the replacement "assigns privileged Git authorization and
publication to the orchestrator subproject," which is the claim this revision
deliberately walks back. A reader arriving through either predecessor is told
the opposite of what this document now says. *Amendment:* update both banners
to state that privileged Git authorization is future work requiring a separate
proposal, and that existing guardrails remain in force meanwhile.

**NOTE A21 — "default-deny filesystem enforcement" no longer describes the
model.** DAC is default-allow for world-readable content; default-deny is a
property of the mount namespace, as the delegation section correctly explains.
The Scope bullet still carries the older phrase, which points an implementer at
the wrong property to test. *Amendment:* restate it as default-deny visibility
through the private mount namespace, layered on UID and ACL authority.

**NOTE A22 — provider-credential provisioning is now load-bearing and remains
open.** Open Question 1 asks how provider credentials reach the dedicated
identity. Under this design that credential must live in agent-readable state
in a home whose authoritative parts are immutable, while the interactive
session runs the `standard` posture with unrestricted egress. Until the
question is answered, the credential is the one secret deliberately placed
inside the agent's reach. *Amendment:* name it in the Security Claims
exclusions, so the claim is not read as covering the credential the design
hands over.

### Recommendation

Status remains `open`, and the path to `accepted` is short. A16 and A17 are the
two places where the remediation's stronger mechanism outran its description:
both are specification work on the layering the design already chose, and
neither implies a different design. A18 and A19 are matrix and provisioning
detail. A20 and A21 are wording. A12 through A15 remain the owner's, and A13 —
the alternatives comparison — is now the only finding that has survived three
consecutive reviews.

The strongest change in this revision is the replacement of a policy record
with kernel-enforced mechanisms. The first version described grants that a
launcher would honor; this one describes ownership, ACLs, mounts, capability
drops, and probes that fail closed, and it says plainly which layer enforces
what. The same honesty appears in the Git section, where the current
orchestrator is described as early-stage and non-authoritative rather than
promoted to a trusted base by assertion. That correction — refusing to claim a
boundary the code does not have, while keeping the imperfect controls that
exist — is the right instinct, and it is what makes the remaining findings
small.

## Review 2 Response (2026-08-10)

The proposal remains `open`. The design body above incorporates the Review 2
remediations; the review itself remains unchanged as an audit trail.

| Finding | Disposition                                                                                                                                                                                                                                                                       |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A16     | Addressed: ACLs are persistent project-registration state; namespaces scope sessions; privileged revocation blocks launches, reaps affected cgroups, removes recorded ACLs, verifies denial, and fails closed in `revoking`. Concurrent sessions have an explicit isolation case. |
| A17     | Addressed: a root-owned launcher constructs and locks mounts before the UID transition; the final session has no capabilities, subordinate-ID mappings, or ability to create or enter user/mount namespaces. Remount and nested-user-namespace cases were added.                  |
| A18     | Addressed: scanning targets multiply linked entries, accounts for other links within protected scan roots, has entry/time budgets, fails closed, documents expected failures, and requires explicit inode/path acceptance in protected policy.                                    |
| A19     | Addressed: ordinary checkout, formatting, archive, and dependency workflows re-test bidirectional editing; a privileged reconciliation command restores only recorded ACLs and verifies both UIDs.                                                                                |
| A20     | Addressed: both predecessor banners now describe Git authorization as future work under a separate proposal and retain existing guardrails meanwhile.                                                                                                                             |
| A21     | Addressed: release-1 scope now claims default-deny namespace visibility layered on UID and ACL authority.                                                                                                                                                                         |
| A22     | Addressed: the Security Claims explicitly exclude confidentiality of the deliberately provisioned provider credential under unrestricted provider connectivity.                                                                                                                   |

Earlier findings A12 through A15 retain their recorded partial/open
dispositions. In particular, the carry-forward register, alternatives analysis,
future privileged-Git enumeration, and release estimate remain prerequisites
to acceptance rather than being silently closed by this remediation.

## Review 3 (2026-08-10, adversarial — remediation)

Adversarial re-review of the remediation recorded in the Review 2 Response
above. The review verifies each claimed disposition against the amended text
and against the artifacts the proposal cites, then looks for defects the
remediation itself introduced. The defect registers and verdict tables of the
two earlier reviews are retained as audit records and must not be edited.

No BLOCKER is raised. Every disposition claimed in the Review 2 Response is
truthful: each one is supported by text that exists, and no claim overstates
what the body contains. One MAJOR defect was found in the claimed scope of the
A17 disposition, and it has been resolved by deferral during this review. Three
further MAJOR defects and three lesser ones remain, and they share a single
cause: each Review 2 fix was written into the section that raised it and not
carried to the sections that depend on it.

### Verification of claimed dispositions

| Finding | Verified disposition                                                                                                                                                                                                                                                                                                                                                                                                              |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A16     | ACCEPTED — DAC and ACLs reclassified as persistent project-registration state, the namespace as session enforcement, with a revocation lifecycle that blocks launches, reaps cgroups, removes only recorded entries, verifies denial, and fails closed in `revoking`. The Summary was corrected to "standing access," which the response table did not claim. Two matrix cases and a completion criterion. Residue in A24 and A25 |
| A17     | ACCEPTED for the host-native profile — namespace construction and mount locking precede the UID transition, capabilities and supplementary groups are dropped, a syscall policy denies namespace creation and entry, and no subordinate ID ranges are assigned. Two matrix cases and a completion criterion. The disposition was claimed unconditionally; see A23                                                                 |
| A18     | ACCEPTED — detection targets entries with a link count above one, accounts for other same-filesystem links within owner-chosen scan roots, fails closed on an unaccounted link, names the expected failures, budgets the scan, and requires explicit inode and path acceptance in protected policy. Residue in A26                                                                                                                |
| A19     | ACCEPTED — the post-workflow bidirectional probe, the prohibition on self-widening, and a privileged reconciliation restoring only recorded entries. Residue in A27                                                                                                                                                                                                                                                               |
| A20     | ACCEPTED — verified in both predecessor files, not merely asserted. Each banner now reads that privileged Git authorization is left to a future, separately accepted orchestrator proposal, with existing guardrails in force meanwhile                                                                                                                                                                                           |
| A21     | ACCEPTED — the Scope bullet states default-deny visibility through the private mount namespace, layered on UID and ACL authority. No stale phrasing survives outside the frozen review text                                                                                                                                                                                                                                       |
| A22     | ACCEPTED — the exclusion names the provisioned provider credential inside the Security Claims themselves, not only in the surrounding prose                                                                                                                                                                                                                                                                                       |
| A12–A15 | PARTIAL and OPEN as claimed. A13 is now four reviews old                                                                                                                                                                                                                                                                                                                                                                          |

The audit trail is intact. Both earlier reviews are unedited, including
passages the body has since overtaken — Review 2's A18 still quotes wording
that no longer exists, which is correct behavior for a frozen record.

### Verdict by check (re-run)

| #   | Check                      | Verdict                                                                                                                                                                   |
| --- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01  | Testable                   | PASS — improved; the container cases have left the release-1 matrix for the deferred profile's own table                                                                  |
| 02  | Alternatives considered    | FAIL — unchanged through four reviews; acknowledged as open                                                                                                               |
| 03  | Tests severe               | WEAK — a downgrade; the assertions carrying A16 and A19 have no cases of their own (A25, A27)                                                                             |
| 04  | Survives unchanged         | N/A (design seed, not a claim)                                                                                                                                            |
| 05  | Sources / exact wording    | PASS — the PoC still supports only what it demonstrated                                                                                                                   |
| 06  | Independence               | WEAK — improved; deferring the container profile removes the one place where release 1 rested on a single runtime's evidence, but one reference implementation remains    |
| 07  | Assumptions explicit       | WEAK — the load-bearing assumptions moved rather than disappearing: cgroup confinement, the absence of an unsandboxed execution path, and scan freshness are now implicit |
| 08  | Scope creep                | PASS — release 1 ships one identity model and claims only what its own mechanisms enforce                                                                                 |
| 09  | Contrary evidence          | PASS — bypassable guardrails, disclosure through the provider channel, and backend limits remain stated                                                                   |
| 10  | Surviving refutation paths | PASS — three open questions, each genuinely undecided                                                                                                                     |

### New defect register + amendments

**MAJOR A23 — the A17 disposition was claimed for a profile the remediation did
not amend. Resolved during this review.** The disposition stated
unconditionally that the final session has no subordinate-ID mappings and
cannot create or enter namespaces. Those rules sit in the profile-general
enforcement enumeration, and the identity section binds them to both profiles.
The containerized profile, then in release-1 scope, still specified a rootless
runtime; a rootless runtime executing as `agent-factory` requires subordinate
UID and GID ranges for that account, which enforcement step 6 refuses outright.
Release 1 would have shipped two identity models while claiming one. The
namespace-creation denial was a weaker objection, since the runtime creates its
namespace before agent-controlled code runs, and that is an ordering
requirement rather than a contradiction.

*Disposition.* The owner deferred the containerized profile beyond release 1.
The profile section records the conflict and the three conditions under which
it may ship, its cases moved to a separate deferred acceptance table, the
Security Claim and completion criterion are now conditional on its own release,
and Open Question 2 asks whether a candidate runtime can satisfy the identity
model without subordinate ranges. Release 1 now ships one identity model.

**MAJOR A24 — revocation depends on cgroup confinement the design leaves
optional.** The revocation step terminates and reaps "every launcher cgroup
whose policy references the grant," and the matrix tests a process surviving
session end. Nothing requires a session to run in a launcher-owned cgroup it
cannot leave. The only other mention is permissive: the launcher "may add CPU,
memory, process, and network constraints." A16 was accepted on the strength of
a revocation that reliably reaps, and that reaping has no required mechanism in
Scope or the Completion Criteria.

*Amendment.* Make a per-session cgroup a required release-1 mechanism, state
that the session can neither write the cgroup hierarchy nor migrate out of it,
and add it to Scope beside the existing revocation criterion.

**MAJOR A25 — persistent grants make the absence of an unsandboxed execution
path load-bearing, and nothing tests it.** A16 was answered by keeping ACLs
persistent and confining sessions with namespaces. That answer holds only while
no code can run as `agent-factory` outside the launcher, because standing
authority is reachable by absolute path from any process under that UID. The
proposal asserts this in one clause — "The agent UID has no login or
unsandboxed execution path" — and never returns to it. There is no case and no
criterion for a `nologin` shell, absent SSH `authorized_keys`, absent user cron
or `at` jobs, no per-user systemd manager or D-Bus activation, and no setuid or
sudo entry point. That sentence now carries as much weight as the namespace
does. Relatedly, revocation "verifies denial under the agent UID," which
requires privileged tooling to execute as that UID; the design should say how
that probe runs without being the execution path it forbids.

*Amendment.* Promote the assertion to a specified property with its own
acceptance cases and completion criterion, and state how the privileged
verification probe executes as the agent UID.

**MINOR A26 — the hardlink scan runs at provisioning while grants persist
across sessions.** The A18 fix is provisioning-time. The A16 fix makes grants
standing state that outlives any session. The launcher's pre-launch validation
records stable path identity but does not re-scan link counts. Between
provisioning and a later session, a `git worktree`, a local clone, or a
restored backup can introduce a link from grant content to an undelegated file,
and the launch will proceed. The two fixes were written against each other's
assumptions.

*Amendment.* State when the scan re-runs — every launch, on a recorded
provisioning generation, or never — and if never, record the residual risk
explicitly rather than leaving it implied by the provisioning-time framing.

**MINOR A27 — the post-toolchain ACL probe has no stated failure behavior, and
its case can pass on the happy path.** Elsewhere the document is precise about
failing closed. The A19 paragraph says only that the launcher re-runs the
bidirectional probe "before a subsequent session" and that the operator runs
reconciliation "before work resumes"; it never says a failed probe refuses the
launch. The matrix row reads "Both UIDs still edit, or reconciliation restores
recorded ACLs," a disjunction satisfied by a run in which no tool stripped
anything, so the repair path can ship untested.

*Amendment.* State that a failed pre-launch ACL probe refuses the launch, and
split the row into two cases: the probe detects a stripped ACL, and
reconciliation restores it and passes both UID probes.

**NOTE A28 — denying user namespaces to the session has an unacknowledged cost
against Goal 5.** The syscall policy forbids the session from creating any
nested sandbox. That rules out container-based test suites, tooling built on
`bwrap`, and the sandboxing features some AI CLIs use for their own tool
execution. This may be the right trade, but Goal 5 promises that agents can run
project tools and test, and neither Non-goals nor Deferred records the loss.

*Amendment.* Name it in Non-goals or Deferred, so an implementer meets it in
the design rather than in a failing test suite.

**NOTE A29 — supporting sections did not follow the remediation.** The grant
lifecycle is new authority with a new actor, and it appears in neither the
Responsibility Boundaries table nor the Operational Sequence, which still runs
from provisioning to publication with no de-provisioning step. Separately, scan
roots and budgets are "configured, owner-chosen" without a statement that they
live in the same protected storage as the delegation policy, which is what
keeps them beyond the agent's reach.

*Amendment.* Add a revocation row and a de-provisioning step, and state where
scan roots and budgets are stored.

### Recommendation

Status remains `open`. The Review 2 Response is an honest record, and the
remediation behind it is mechanism rather than relabeling: the revocation
lifecycle, the privilege ordering, and the link-count accounting are all things
an implementer can build and a test can refute. A16 and A17 are closed for the
profile release 1 ships.

The pattern worth naming is the one that produced this register. Each fix
landed in the section that raised it and stopped there. The namespace rules did
not reach the container profile, which is A23 and is now resolved by deferral.
The revocation step assumed a cgroup that Scope leaves optional, which is A24.
The decision to make grants persistent did not reach the hardlink scan or the
execution-path assertion, which are A26 and A25. A carry-forward register — the
A12 amendment, still outstanding — would catch this class before the next
review does, because it forces each disposition to name the sections it touches.

A24 and A25 should be resolved before `accepted`: each leaves a mechanism that
the accepted findings depend on either optional or untested. A26 through A29
are specification work on decisions already made. A13 remains the finding that
has survived four consecutive reviews, and it remains the owner's call.

## Review 3 Response (2026-08-10)

The proposal remains `open`. The normative body above incorporates the Review
3 remediations; the review remains unchanged as an audit trail.

| Finding | Disposition                                                                                                                                                                                                                                                                  |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A24     | Addressed: every session now requires a launcher-owned, agent-inaccessible cgroup; migration, hierarchy writes, descendant reaping, scope, sequence, tests, and completion criteria are explicit.                                                                            |
| A25     | Addressed: direct execution paths are enumerated and denied; a fixed-command, sandboxed privileged probe performs UID verification without creating a general execution path; both properties have acceptance cases and completion criteria.                                 |
| A26     | Addressed: protected policy owns scan roots and budgets; every launch checks identities and link counts, triggers a bounded full rescan on change, and refuses stale, unaccounted, or over-budget topology.                                                                  |
| A27     | Addressed: a failed pre-launch ACL probe refuses launch; detection and privileged reconciliation are separate negative acceptance cases and completion criteria.                                                                                                             |
| A28     | Addressed: release-1 incompatibility with tools that create user or mount namespaces is explicit in Non-goals.                                                                                                                                                               |
| A29     | Addressed: responsibility boundaries name provisioning, revocation, and cgroup ownership; the operational sequence includes de-provisioning; protected policy owns hardlink scan configuration.                                                                              |
| A13     | Proposed resolution: the Alternatives Analysis supplies a weighted Pugh matrix including the null option, Landlock-only, and a VM. Owner confirmation of its criteria and scores remains required.                                                                           |
| A14     | Addressed for this proposal's boundary: protected local/remote ref mutations, remote changes, publication, and integration into protected branches are enumerated; unprotected story-branch work remains ordinary. The future orchestrator proposal still owns the protocol. |

A12's complete predecessor-finding carry-forward register, A15's release
estimate, provider-credential provisioning, the deferred container runtime,
and the future orchestrator protocol remain prerequisites to acceptance.
