---
scope: global
schema_version: 2
status: draft
owner: md@matthiasdaues.de
created: 2026-10-08
updated: 2026-10-08
supersedes:

impact:
  scope: cross_project
  architecture_change: false
  external_contract_change: true
  boundaries:
    - init-factory
    - packages/factory/config/
    - docs/proposals/agent-execution-isolation-and-distribution.md

governance:
  assurance: elevated
  risk_domains:
    - security
    - operations

estimate:
  as_of: 2026-10-08
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Proposal: Dev Container for AI CLI Sessions

## Summary

`init-factory` can generate a dev container for a project. An AI CLI then runs
inside the container and sees only the project and the extra folders the
project lists, each read-only or read-write. A firewall in the container
allows outbound traffic only to the hosts the chosen CLI needs, plus the
project's own Docker Compose network.

The container works for every CLI the Factory supports: Claude Code, GitHub
Copilot CLI, Codex, and Pi. One image holds all four. A variable at start
selects the CLI, and with it the firewall's host list.

This is a practical step for today. It stops an agent from reading or writing
outside its project by accident. It is not the security boundary that
[Agent Execution Isolation](agent-execution-isolation-and-distribution.md)
designs, and it does not replace it.

## Motivation

### What happened

On 2026-10-08, a Claude Code session in a Factory project ran in auto mode.
While looking up a term, it searched the folders next to the project, found a
customer's scheduler export there, and parsed it. It printed counts and five
real job names. The names went to the model provider as part of the tool
output. The user had not asked for any of this. Nothing in the setup stopped
it.

### Why the CLI settings did not stop it

The Claude Code documentation shows the limits:

- Deny rules always win over allow rules. So "deny everything except the
  project and two folders" cannot be written as rules.
- Path rules cover the CLI's file tools and a few shell commands such as
  `cat`. They miss a Python script that opens files itself, and `grep -r` on
  a directory.
- The OS sandbox for shell commands closes that gap, but only when it is
  configured with care. And only the machine-wide managed settings file is
  out of the agent's reach.
- Broad allow rules in the user's own settings, such as `Write` without a path
  or `Bash(docker *)`, undo every path limit. In the incident, both were set.
- In that project, `.claude/` was ignored by Git. Project settings therefore
  existed only on one machine.

The other CLIs have their own permission models, each with its own gaps. A
Factory user should not have to master four permission systems to keep an
agent inside its project.

### Why a container

A path that is not mounted does not exist for any program in the container.
No rule can be bypassed: not by a script, not by `grep -r`, not by a file tool
that runs outside a shell sandbox. The limit is the same for every CLI.

Anthropic publishes a reference dev container for Claude Code with exactly
this design: bind mounts plus an `iptables` allowlist. A first version for one
project exists: `.devcontainer/` on the `dev` branch of the gigacron project,
not yet tested. This proposal turns it into a Factory feature for all CLIs.

### Why not wait for Agent Execution Isolation

That proposal designs the real boundary: a dedicated user ID, ACLs, a
root-owned launcher, and a private mount namespace. It has been open since
2026-08-10 and needs root provisioning on every machine. The container needs
only Docker, which Factory projects mostly use already. It closes the
accidental-access gap now, at a cost a single developer can carry.

## Alternatives Considered

### Microsoft eXecution Container (MXC)

[MXC](https://github.com/microsoft/mxc) is a software development kit (SDK)
for running untrusted code in a sandbox. A launcher program embeds the SDK
and passes a JSON policy with read-only, read-write, and denied paths and an
outbound network policy. On Linux, MXC uses Bubblewrap. On macOS, it uses
Seatbelt. It gives the same path allowlist as bind mounts, without Docker, on
more platforms.

This proposal does not use MXC. The README, read on 2026-10-08, leaves four
gaps:

1. It names no ready launcher for Linux, only `wxc-exec.exe` for Windows. The
   Factory would have to build and maintain its own launcher.
2. It calls host filtering "backend-dependent" and does not say whether
   Bubblewrap supports it. The firewall claim depends on host filtering.
3. It documents streamed standard input and output, but not an interactive
   terminal session. An AI CLI needs a full terminal.
4. It has no published release, and several backends are experimental.

**Revisit when** a Linux experiment passes three checks: Claude Code runs
interactively through MXC, `example.com` is unreachable, and
`api.anthropic.com` is reachable. MXC is then a candidate for a macOS and
Windows profile and for the deferred container profile of
[Agent Execution Isolation](agent-execution-isolation-and-distribution.md#containerized-profile-deferred).

## Core Principles

- The container limits what an agent can see by accident. It does not claim to
  stop an agent that tries to break out.
- Mounts and hosts are listed explicitly. Nothing is mounted or allowed because
  it is next to the project.
- One image and one firewall script serve every supported CLI. Only the host
  list and the config volume differ.
- No credential enters the container unless the user puts it there on
  purpose: no SSH key, no Docker socket, no host home directory.
- The proposal states what it protects against and what it does not, in the
  same terms as
  [Agent Execution Isolation](agent-execution-isolation-and-distribution.md#security-claims).

## Design

### What `init-factory` generates

The container is an `init-factory` component named `container`, like the
existing `usage` component. Decided 2026-10-08.

- `init-factory --add container` writes `.devcontainer/` and a starter
  `.agent-factory/config/container.yaml` with an empty `mounts:` list.
- `init-factory --update container` regenerates `.devcontainer/` after
  `container.yaml` changes.
- `init-factory --remove container` deletes `.devcontainer/` and keeps
  `container.yaml`.

`.devcontainer/` is fully generated. `--update container` overwrites hand
edits there. Project-specific settings go only into `container.yaml`, and the
generated `README.md` says so.

`init-factory --add container` writes these files:

| File                       | Content                                                                                           |
| -------------------------- | ------------------------------------------------------------------------------------------------- |
| `Dockerfile`               | Base image, the project's language runtimes, the four CLIs, the firewall tools, and `pre-commit`. |
| `devcontainer.json`        | Mounts, volumes, environment, and the firewall start command.                                     |
| `init-firewall.sh`         | Default-deny firewall. Loads the host list of the selected CLI and the attached Docker networks.  |
| `allowed-hosts/<cli>.txt`  | One file per CLI with the hosts it needs.                                                         |
| `allowed-hosts/common.txt` | Hosts every session needs: GitHub, and the package registries the project uses.                   |
| `README.md`                | How to start a session, check the boundary, and move a CLI's memory into the container.           |

The runtimes come from the project fingerprint that `init-factory` already
records, for example `.python-version` and `.nvmrc`.

### Where the mounts come from

The project declares extra folders in `.agent-factory/config/container.yaml`:

```yaml
mounts:
  - path: ../concept-repo
    mode: read-only
  - path: ../shared-fixtures
    mode: read-write
compose_network: myproject_default   # optional
```

`init-factory` turns each entry into a bind mount. It keeps each folder's
position relative to the project, so relative links between repositories
still resolve. The project itself is always mounted read-write. Nothing else
from the host is mounted.

### Selecting the CLI

`devcontainer.json` passes `FACTORY_AGENT_CLI` from the host into the
container. The firewall script loads `common.txt` plus the file for that CLI.
A Codex session then cannot reach the Anthropic API, and a Claude Code session
cannot reach the OpenAI API.

Each CLI keeps its login and history in a Docker volume of its own, mounted at
its config folder, for example `~/.claude` or `~/.codex`.

### Per-CLI details

| CLI                | Needs                                                                                                                                                 |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Claude Code        | The Anthropic API and login hosts.                                                                                                                    |
| GitHub Copilot CLI | GitHub and the Copilot API hosts. Its GitHub token needs the Copilot permission, so keep it apart from a push token.                                  |
| Codex              | The OpenAI API and login hosts. Codex has its own sandbox, which may clash with the container. Find out whether it must run with its own sandbox off. |
| Pi                 | The hosts of the model provider Pi is set to use. Its list is project-specific.                                                                       |

The host names, package names, and config folders for Copilot, Codex, and Pi
are not yet confirmed. They are listed under [Open Questions](#open-questions).

### Firewall

The firewall follows Anthropic's reference script, with three changes:

- **No outbound SSH.** The reference allows port 22 to every host. That is an
  open channel. Git uses HTTPS with a token instead.
- **The Compose network by interface, not by guess.** The script allows the
  networks the container is attached to. The reference allows a /24 around
  the gateway, which can miss services or include unrelated hosts.
- **Host lists per CLI**, as above.

The firewall cannot be reloaded at run time. The agent has write access to
the project, so no firewall input may come from the project mount:

1. The `Dockerfile` copies `init-firewall.sh` and the host lists into the
   image under `/etc/factory-firewall/`. Root owns these files, and they are
   read-only.
2. The script reads only from `/etc/factory-firewall/`. It never reads from
   the project mount.
3. On its first run, the script writes the selected CLI to a root-owned lock
   file under `/run`. A second run exits non-zero and changes no rule.
4. The `sudoers` entry allows only this script, with no arguments. It does not
   pass `FACTORY_AGENT_CLI` through.

An edit to the host lists in `.devcontainer/` therefore takes effect only
after a human rebuilds the container. Decided 2026-10-08.

### Toolchain inside the container

- The container keeps its own language environments in volumes, for example
  a Python virtual environment. The host's environments belong to the host's
  interpreters and break inside the container.
- `pre-commit` is installed in the image. Git hooks generated on the host name
  the host's Python path. The hook falls back to `pre-commit` on the `PATH`
  when that path is missing.
- Runtimes are installed at build time. The firewall blocks their download
  servers at run time.

## Security Claims

For a session in the generated container, the Factory may claim:

- A host path that is not listed is not visible.
- A path listed as read-only cannot be written.
- No SSH key, Docker socket, or host home directory is present unless the
  user adds it.
- Outbound connections go only to the hosts resolved at start for the
  selected CLI, to GitHub, and to the attached Docker networks.
- The agent cannot reload or change the firewall rules while the container
  runs.

The Factory may not claim, and the README must say so:

- **Not a boundary against a determined agent.** A kernel or Docker bug can
  break the container. The agent runs as the same user ID as the human on the
  bind mounts.
- **Not enforced selective egress.** Hosts are resolved once, at start.
  Addresses behind a CDN are shared with other sites. This is the
  "ergonomic control" that
  [Agent Execution Isolation](agent-execution-isolation-and-distribution.md#network-and-credentials)
  describes.
- **Not confidentiality.** Anything the agent can read can reach the model
  provider. A read-only mount stops changes, not disclosure.
- **Not tamper-proof.** The agent can edit `.devcontainer/` and
  `container.yaml` in the project. The change takes effect only when a human
  rebuilds the container, and it shows up in the diff.

## Scope

**In this proposal:**

- The `container` component of `init-factory`, with `--add`, `--update`, and
  `--remove`, and the generated files above.
- `container.yaml` with read-only and read-write mounts and an optional
  Compose network.
- One image with the four supported CLIs, and per-CLI host lists.
- Per-CLI config volumes.
- A boundary check script that runs the checks from the README and exits
  non-zero on failure.
- Docker on Linux.

**Not in this proposal (do NOT plan stories for these):**

- A dedicated user ID, ACLs, or a root-owned launcher. That is
  [Agent Execution Isolation](agent-execution-isolation-and-distribution.md).
- Enforced selective egress, for example through a proxy outside the
  container. It needs its own evidence.
- Podman, macOS, and Windows. They differ in mount ownership and networking
  and need their own tests.
- Moving CLI memory automatically. The README describes the one-time copy.
- Starting or stopping the project's Compose stack from inside the container.
  That would need the Docker socket, which breaks the boundary.

## Design Details

- **Relationship to Agent Execution Isolation.** This proposal does not
  supersede it. When that proposal's container profile ships, its launcher
  derives mounts from the protected delegation record instead of
  `container.yaml`. The host lists and the per-CLI images from this proposal
  can carry over.
- **Docker Compose.** The container joins the project's Compose network, so
  services resolve by name. The developer starts the stack on the host first.
- **Git.** The container commits with an identity passed from the host.
  Pushing needs a fine-grained token limited to the repository. Without one,
  the developer pushes from the host.
- **CLI memory.** Some CLIs key their memory by project path. Inside the
  container the path differs, so the memory starts empty. The README shows the
  copy for each CLI that has this behavior.

## Open Questions

- **Which hosts, package names, and config folders do Copilot CLI, Codex, and
  Pi need?** Check each against its current documentation before the host
  lists are written.
- **Does Codex need its own sandbox switched off inside the container?**
  Check the Codex documentation and test both settings.
- **Which login hosts does Claude Code need besides `api.anthropic.com`?** The
  gigacron draft adds `claude.ai` and `console.anthropic.com`, unconfirmed.
- **Is `--container` part of `init-factory`, or a separate skill?** Decided
  2026-10-08: it is the `init-factory` component `container`. See
  [What `init-factory` generates](#what-init-factory-generates).

## Completion Criteria

- `init-factory --add container` on a fresh project produces a `.devcontainer/`
  that builds and starts with Docker on Linux.
- In the container, the boundary check passes: the host home is absent,
  `example.com` is unreachable, a read-only mount refuses a write, and GitHub
  is reachable.
- A second `sudo init-firewall.sh` exits non-zero, and `example.com` stays
  unreachable afterwards.
- With `FACTORY_AGENT_CLI` set to each of the four CLIs, the CLI starts, logs
  in, and answers a prompt. The API host of a different CLI is unreachable.
- A folder listed in `container.yaml` appears at its relative position with
  its declared mode. A folder next to the project that is not listed is
  absent.
- With `compose_network` set, a Compose service resolves by name from the
  container.
- `pre-commit` hooks run inside the container without the host's Python.
- After a change to `container.yaml`, `init-factory --update container`
  regenerates `.devcontainer/`, and the change appears in the generated files.
- `init-factory --remove container` deletes `.devcontainer/` and keeps
  `container.yaml`.
- The README states the five claims and the four non-claims from
  [Security Claims](#security-claims).

## Guiding Rule

An agent sees what the project lists, and nothing next to it.
