---
schema_version: 2
title: "Factory CLI Security Hardening"
status: superseded
owner: agent-factory
created: 2026-07-28
updated: 2026-08-10
supersedes:

impact:
  scope: cross_project
  architecture_change: true
  external_contract_change: true
  boundaries:
    - factory/config/hooks/block-dangerous-git.sh
    - factory/scripts/commit-safe

governance:
  assurance: critical
  risk_domains:
    - security
    - privacy
    - data_integrity
    - operations

estimate:
  as_of: 2026-07-29
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
---

# Proposal: Factory CLI Security Hardening

> **Superseded on 2026-08-10.** This proposal is retained as design history.
> Its scope is replaced by
> [Agent Execution Isolation and Optional Container Distribution](../agent-execution-isolation-and-distribution.md),
> which makes multi-path host filesystem delegation the primary security goal,
> treats containers as an optional pinned environment, and leaves privileged
> Git authorization and publication to a future, separately accepted
> orchestrator security proposal. Existing guardrails remain in force meanwhile.

## Summary

Run Factory-enabled AI coding CLIs under a dedicated, unprivileged operating
system identity and enforce least privilege outside the repository. Layer
filesystem controls, command mediation, executable allowlisting, credential
separation, and remote Git protection so repository-local hooks prevent
accidents without being mistaken for a security boundary.

The design must permit normal development—reading the project, editing the
working tree, running approved tools, testing, and creating reviewable
commits—while preventing the CLI from weakening its own controls or performing
unapproved destructive and external actions.

## Security Objective

Compromise, prompt injection, or faulty reasoning inside a Factory CLI must not
allow that process to:

1. Become the human operator or obtain administrative privileges.
2. Change the policy that constrains it.
3. Read unrelated user data or credentials.
4. Execute arbitrary downloaded or workspace-provided programs.
5. Mutate protected Git references or conceal destructive repository changes.
6. Publish code, delete remote data, or contact unrelated services without a
   separately authorized capability.

The objective is containment and recoverability, not perfect prevention of
damage inside files explicitly delegated to the CLI.

## Threat Model

The CLI, model output, repository contents, dependencies, generated scripts,
tool output, and remote content are untrusted. The human workstation, host
kernel, policy broker, protected credential store, audit sink, and remote Git
server are trusted.

The following are not security boundaries:

- `AGENTS.md` and model instructions.
- `PreToolUse`, pre-commit, or other repository-local hooks.
- command-string pattern matching.
- Git branch naming conventions.
- a container whose control socket or privileged host mounts are exposed.
- `noexec` mounts alone; an allowed interpreter can still read and execute a
  script from such a mount.

Any process with arbitrary execution and write access to `.git` can bypass
local Git policy. Strong enforcement must therefore be owned outside the
repository and outside the CLI's writable identity.

## Proposed Control Model

### 1. User Management and Execution Identity

Create a dedicated operating-system account, `agent-factory`, for Factory
CLIs. It must not share the human operator's identity.

The account has:

- no `sudo`, administrative, container-management, or login-manager rights;
- no membership in `docker`, `podman`, `libvirt`, system journal, backup, or
  other privilege-bearing groups;
- a private home containing only CLI state explicitly provisioned for Factory;
- a restricted supplementary group for the delegated project workspaces;
- resource limits for processes, memory, file descriptors, disk, and runtime;
- no access to the human home, SSH directory, password stores, browser
  profiles, cloud configuration, or desktop session secrets.

For interactive use, the human invokes a trusted launcher that changes to this
identity and enters the sandbox. Direct execution of the AI CLI under the
human account is unsupported because it defeats identity separation.

The [Containerized Agent Factory Distribution](containerized-agent-factory.md)
defines one explicit specialization of this rule. Its verified rootless Podman
profile may preserve the invoking user's file ownership only because the agent
process remains inside a user namespace with one approved bind mount, no host
home or runtime socket, dropped capabilities, and a mechanically proved
identity mapping. That profile supersedes this subsection only within its
stated exclusion of kernel or runtime compromise. Baseline and hardened
workstation deployments still require the dedicated `agent-factory` account.

Use separate identities where capabilities differ materially:

| Identity             | Purpose                           | Important capabilities                                |
| -------------------- | --------------------------------- | ----------------------------------------------------- |
| `agent-factory`      | Normal CLI and subagent execution | Delegated workspace writes and approved tools         |
| `factory-integrator` | Human-approved integration        | Update selected local refs; no remote administration  |
| `factory-publisher`  | Human-approved publication        | Push only allowed refs to allowed remotes             |
| Human administrator  | Policy and host maintenance       | Change sandbox, identities, and protected credentials |

The CLI must never receive credentials for the latter identities. Elevation is
an external workflow decision, not a command the model can perform itself.

### 2. Workspace and Filesystem Access

Give `agent-factory` read access only to:

- the delegated repository;
- approved toolchains and immutable Factory assets;
- the minimum system libraries and device files required to run;
- an isolated package cache populated through a controlled dependency step.

Give it write access only to:

- the delegated working tree;
- task-specific temporary directories;
- isolated build, test, and package caches;
- Factory runtime state and usage spools;
- explicitly authorized Git areas.

Deny access to:

- the human home and credentials;
- other repositories and workspaces;
- system configuration, service sockets, and host logs;
- Docker or Podman sockets;
- arbitrary removable media and network-mounted shares;
- policy files, launcher configuration, and the audit log.

Use owner/group permissions as a baseline and an operating-system sandbox such
as Landlock, AppArmor, SELinux, or a systemd service sandbox for enforcement.
Container isolation may supplement this, but the container must be rootless,
drop all capabilities, use a read-only base filesystem, and expose neither the
host root nor a container-management socket.

#### Git metadata

Git metadata requires special treatment because normal commits write objects
and references, while unrestricted `.git` writes defeat branch protection.

The preferred model is:

1. The CLI writes the working tree and a task-specific Git object/worktree
   area.
2. A policy broker owns protected reference mutation.
3. The broker exposes narrow operations such as creating a task branch,
   recording a commit, and requesting integration.
4. The broker rejects mutation of `main`, `dev`, safety refs, hooks, Git
   configuration, remotes, and worktree metadata unless the operation has the
   required external approval.
5. Integration occurs under `factory-integrator`, after validation.

If direct local Git writes remain necessary during transition, treat the local
repository as recoverable scratch state. The authoritative protection must
remain on the remote, and snapshots must make local destruction recoverable.

### 3. Command and Capability Mediation

Replace unrestricted shell authority with a broker that evaluates structured
operations. Policy decisions must use the resolved executable, arguments,
working directory, environment, requested filesystem effects, and caller
identity—not substring matching against a shell command.

The default policy is deny. Initial allowed capabilities should include:

- read-only repository inspection;
- edits inside the delegated working tree;
- repository-provided deterministic lint and test gates;
- approved compilers, formatters, and test runners with bounded arguments;
- non-destructive Git inspection;
- task-branch commits through the Git broker;
- explicitly scoped temporary-file creation.

Every capability declares:

- permitted executable digest or trusted package identity;
- allowed arguments and subcommands;
- permitted working-directory roots;
- environment variables that may pass through;
- filesystem and network effects;
- timeout and resource limits;
- whether human approval is required;
- audit fields and redaction rules.

Shell composition, redirection, command substitution, dynamic loaders, arbitrary
interpreters, and generic script runners require separate scrutiny because they
can collapse a narrow allowlist into arbitrary execution.

### 4. Executable and Dependency Trust

Only execute binaries and scripts from immutable, administrator-owned
toolchains or from reviewed, content-addressed Factory distributions.

Controls:

1. Resolve executables to canonical paths before policy evaluation.
2. Pin tool versions and verify hashes or signatures.
3. Keep trusted launchers and policy helpers outside CLI-writable paths.
4. Prevent `PATH`, aliases, shell functions, environment variables, or local
   files from replacing trusted executables.
5. Clear unsafe loader variables and use a minimal environment.
6. Separate dependency acquisition from dependency execution.
7. Download through an approved proxy or lockfile-verifying builder, then
   expose an immutable cache to the CLI.
8. Treat repository scripts as untrusted until explicitly admitted by policy.
9. Revalidate executable content whenever a permitted file changes.

An executable allowlist must account for interpreters. Allowing unrestricted
`bash`, Python, Node, `env`, or a compiler is effectively allowing arbitrary
program execution. Prefer narrow, administrator-owned launchers that expose
one validated operation.

### 5. Network and Credential Restrictions

Normal CLI execution receives no ambient SSH agent, cloud credentials,
password-store access, browser session, Git credential helper, or unrestricted
network access.

Network policy should default to deny and selectively permit:

- the configured model provider through an egress proxy;
- approved source and package services during designated operations;
- the local Usage Accounting endpoint, if enabled;
- no inbound listeners unless explicitly required.

The proxy records destination, identity, time, and byte counts and blocks IP
literals, redirects to unapproved domains, and DNS rebinding.

Use short-lived, task-scoped credentials issued after approval. Separate
read-only source access from publication credentials. Secrets are injected
into the specific child operation, never written into the workspace, inherited
by unrelated subprocesses, or exposed to model context.

### 6. Git and Supply-Chain Protection

The remote Git server is the authoritative repository boundary.

Require:

- branch protection for `main` and `dev`;
- prohibition of force pushes and branch deletion for CLI credentials;
- reviewed pull or merge requests;
- required CI gates independent of the agent workspace;
- signed commits or attestations where provenance matters;
- restricted creation or modification of workflows and release configuration;
- immutable audit events for pushes, merges, permission changes, and deletions;
- dependency and artifact provenance checks in trusted CI.

Local hooks remain useful for fast feedback and accident prevention, but remote
policy must independently reject prohibited outcomes.

### 7. Approval and Destructive Operations

Human approval must be required for:

- deletion or forced movement of Git references;
- changes to hooks, policy, sandbox configuration, remotes, or credentials;
- writes outside delegated roots;
- installation or execution of new tools;
- network access outside the base allowlist;
- publication, deployment, release, or external messaging;
- destructive database, infrastructure, or filesystem actions.

Approval must name the resolved operation, exact targets, expected effects, and
expiry. It must not authorize a generic shell, interpreter, or broad command
prefix. The approval record is written to an audit system the CLI cannot
modify.

### 8. Auditing, Detection, and Recovery

Record:

- execution identity, session, task, model, and parent session;
- policy decision and approval reference;
- canonical executable identity and arguments with secret redaction;
- working directory, repository, branch, and full commit SHA;
- filesystem, network, credential, and Git capabilities granted;
- exit status, duration, and resource consumption;
- protected-reference and policy changes.

Send audit events to append-only storage outside the workspace. Alert on denied
policy changes, attempts to access credentials, executable substitution,
unexpected network destinations, destructive Git operations, and repeated
approval probing.

Recovery requires:

- authoritative protected refs on the remote;
- regular repository and usage-data backups;
- bounded local retention and disk quotas;
- reproducible workspaces and toolchains;
- documented credential revocation and incident isolation;
- tested restoration of deleted local branches and corrupted worktrees.

## Deployment Profiles

### Baseline

- Dedicated `agent-factory` user.
- Human data and credentials inaccessible.
- Project-scoped writable workspace.
- No `sudo` or container socket.
- Remote branch protection.
- Explicit approval for destructive commands and publication.

This materially reduces accidental damage but still treats local `.git` and
allowed interpreters as weak points.

### Hardened Workstation

- Baseline controls.
- Operating-system sandbox with default-deny filesystem and network policy.
- Immutable trusted toolchain.
- Structured command broker.
- Short-lived brokered credentials.
- External audit sink.
- Task-specific worktrees and resource limits.

### High-Assurance Runner

- Ephemeral, rootless execution environment per task.
- No direct write access to authoritative Git refs.
- Content-addressed source input and artifacts.
- All commits, integration, publication, and secrets mediated externally.
- Independent trusted CI validation.
- Environment destroyed after exporting approved artifacts and audit evidence.

## Rollout

1. Inventory current CLI identities, groups, credentials, sockets, filesystem
   access, executable paths, network destinations, and Git operations.
2. Create the `agent-factory` identity and trusted launcher; move CLI-specific
   configuration into its isolated home.
3. Restrict workspace and cache permissions and remove access to human data,
   administrative groups, credential agents, and container sockets.
4. Enforce remote Git branch protection and introduce separate integration and
   publication credentials.
5. Add default-deny filesystem and network sandboxing in observe-only mode,
   then enforce after resolving legitimate denials.
6. Replace broad shell permissions with structured command capabilities,
   starting with destructive Git, package installation, network access, and
   publication.
7. Pin and attest executable toolchains and separate dependency acquisition
   from agent execution.
8. Export immutable audit events and test alerts, revocation, and recovery.
9. Move sensitive or unattended workloads to ephemeral high-assurance runners.

Each stage must preserve a documented break-glass path owned by a human
administrator. The CLI identity must not possess that path.

## Acceptance Criteria

- Factory CLIs cannot read the human user's private files or ambient
  credentials.
- Factory CLIs cannot obtain administrative or container-host privileges.
- Policy, trusted launchers, and audit records are not writable by the CLI
  identity.
- An allowed command cannot be replaced through `PATH`, workspace files, or
  environment manipulation.
- Unapproved executables and network destinations are denied.
- Destructive Git plumbing and direct protected-ref writes are denied as well
  as equivalent porcelain commands.
- CLI credentials cannot push to, force-update, or delete protected remote
  branches.
- Approval is scoped to exact operations and expires.
- Every privileged operation is attributable to an external approval record.
- Deletion or corruption of local workspace state can be recovered from
  authoritative remote refs and backups.
- A test suite demonstrates that representative bypass attempts fail at the
  operating-system or broker boundary, not merely at a repository hook.

## Guiding Rule

The agent may modify delegated work; it may not modify the authority that
defines what work is delegated.
