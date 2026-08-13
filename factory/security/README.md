# Agent Execution Sandbox

`af-sandbox` runs an AI coding CLI under a dedicated, unprivileged operating-system
identity that can reach an explicit set of directory trees and nothing else. It is
the working implementation of release 1 of
[Agent Execution Isolation and Optional Container Distribution](../../docs/proposals/agent-execution-isolation-and-distribution.md).

The agent works normally inside its grants: it edits files, runs tests, uses Git,
and installs project dependencies. Outside them it has no read access, no write
access, and no route to acquire any.

## Requirements

Linux with systemd 239 or later, cgroup v2, and a filesystem mounted with POSIX
ACL support. `ext4`, `xfs`, and `btrfs` enable ACLs by default. Run
`factory/security/af-sandbox doctor` to check a host before provisioning it.

## Setup

Create and verify the dedicated identity once per host:

```
sudo factory/security/af-sandbox install
```

This creates the `agent-factory` system account and refuses to continue unless the
account has a `nologin` shell, a locked password, no supplementary groups, and no
subordinate UID or GID ranges. Those four properties are load-bearing, so the tool
asserts them rather than assuming them.

Describe a project in a root-owned policy file at
`/etc/agent-factory/projects/<name>.yaml`:

```yaml
paths:
  - path: /home/you/work/acme-application
    access: read-write
  - path: /home/you/reference/schemas
    access: read-only
network: standard
command: ["claude"]
credentials:
  anthropic: /etc/agent-factory/credentials/anthropic
```

The policy lives outside every delegated path, so the agent can neither read nor
modify the document that constrains it. Granting two paths grants nothing else:
their common parent stays invisible.

Provision and launch:

```
sudo factory/security/af-sandbox grant acme
sudo factory/security/af-sandbox run acme
```

## How the confinement works

Five layers apply in order, and a session starts only if all five agree.

**Delegation policy.** Root-owned YAML outside every grant. `af-sandbox` refuses a
policy file that is group-writable, world-writable, or not owned by root.

**Ownership and ACLs.** Project files stay owned by the human. The agent UID
receives one explicit ACL entry per grant — `rwX` for read-write, `rX` for
read-only — plus a matching default ACL so that files either identity creates stay
editable by the other. Because the agent owns nothing, it cannot use `chmod` or
`chown` to widen its own access.

**The systemd sandbox.** `ProtectSystem=strict` and `ProtectHome=yes` make the
whole filesystem read-only and hide every user home. `BindPaths` and
`BindReadOnlyPaths` then re-expose exactly the granted trees. systemd builds this
namespace as PID 1, before dropping to the agent UID, so the ordering that makes
read-only mounts unforgeable is guaranteed by the implementation rather than by
this tool.

A useful consequence: the agent never needs traversal permission on your real home
directory. Inside the namespace, `/home` is an empty tmpfs and the only path that
exists beneath it is the mount point of the grant itself.

**seccomp and capabilities.** `RestrictNamespaces=yes` denies `unshare`, `clone`
with namespace flags, and `setns`, so the session cannot build a nested sandbox and
cannot remount a read-only grant. All capabilities and supplementary groups are
dropped, and `NoNewPrivileges=yes` blocks setuid escalation.

**cgroup.** Each session runs in a systemd-owned unit cgroup without `Delegate=`,
and `ProtectControlGroups=yes` makes the hierarchy read-only to the session, so no
process can migrate out. `--wait --collect` reaps every descendant at exit.

## Credentials

Provider credentials reach the agent through systemd's credential mechanism.
Root reads the file at unit start and exposes it on a private tmpfs readable only
by that unit, at `$CREDENTIALS_DIRECTORY/<name>`. The credential never lives in
agent-writable state and disappears when the session ends. `af-sandbox` refuses a
credential source that is not root-owned and mode 0600.

## Day-to-day operation

| Command               | Effect                                                                      |
| --------------------- | --------------------------------------------------------------------------- |
| `doctor`              | Report host capability and identity state. Needs no privilege.              |
| `install`             | Create the dedicated identity and assert its escalation surface is closed.  |
| `grant <project>`     | Scan for hardlinks, install ACLs, probe both identities, record the result. |
| `run <project>`       | Revalidate everything, write an audit record, launch the session.           |
| `verify <project>`    | Re-run the bidirectional probe against the current state.                   |
| `reconcile <project>` | Restore ACL entries a tool stripped. Restores only what was recorded.       |
| `revoke <project>`    | Block launches, stop sessions, remove recorded ACLs, verify denial.         |

`run --dry-run` prints the exact `systemd-run` invocation, which is the fastest way
to see what a session will actually receive.

Ordinary tools rewrite ACLs. `git checkout` with a mode change, `rsync`, `tar`,
`unzip`, and `install -m` can all clear the ACL mask and lock one identity out of a
tree. `run` re-runs the bidirectional probe before every launch and refuses to
start when it fails; `reconcile` repairs it.

Hardlinks are inode aliases, so a pre-existing link from inside a grant to a file
outside it makes that file part of the grant. `grant` refuses when it finds one it
cannot account for. This is expected to reject `git clone --local`, `git worktree`
layouts sharing an object store, shared content-addressed package caches, and
`cp -l` fixtures. Widen `hardlink_scan_roots` so the other links are accounted for,
or list the inode keys under `accepted_hardlinks`.

## Verifying the host

```
sudo factory/security/af-acceptance
```

This builds a throwaway fixture, provisions it, and runs each acceptance case
inside a real session — attempting to read an undelegated file, follow a symlink
out of a grant, write a read-only tree, remount it, create a nested user namespace,
leave the cgroup, reach a container socket, and read the audit log. Run it after
any kernel or systemd upgrade.

## What this does not do

**It does not protect a read-write grant from the agent authorised to write it.**
An agent that can edit a repository can damage it, `.git` included. Protected
remote refs, independent CI, and tested backups remain deployment prerequisites.

**It confines access, not disclosure.** Anything the agent can read, it can send to
its model provider. A read-only grant protects the host from mutation; it does not
make the content confidential. This includes the provider credential deliberately
provisioned to the agent identity.

**Egress is not selectively filtered.** `network: standard` means ordinary network
access. `network: deny` means none, enforced by a private network namespace. There
is no supported middle setting, because an allowlist proxy the session can bypass
would be an ergonomic control described as a security one.

**Revocation removes what it installed.** If a tree is world-readable, the agent
UID keeps DAC read access through the `other` mode bits after its ACL entry is
gone. `revoke` reports this explicitly instead of claiming a denial it did not
produce. Confinement then rests on the namespace no longer exposing the path.

**Programs inside a grant run freely.** Executable allowlisting, dependency trust,
and interpreter mediation are separate hardening work, not part of this release.

**Tools that need their own sandbox will not work.** `RestrictNamespaces=yes`
denies namespace creation, so container-based test suites, `bwrap`-based tooling,
and AI CLIs that sandbox their own tool execution cannot run inside a session.

## Relationship to the Git guardrails

`block-dangerous-git.sh`, `commit-safe`, `verify-base`, and `premerge-check` keep
their current behaviour. They prevent accidents; they are not boundaries, because
an agent with write access to a repository can bypass them. This sandbox does not
demote or replace them. Agent-proof Git authorisation remains future work under a
separate proposal, and no control here may be removed until that replacement ships
and is tested in the same release.
