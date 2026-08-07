# PoC Story — Candidate 2: Whole-factory rootless container, cwd mounted, egress-controlled

Plain-markdown spike story per `technical-poc` Step 1. Not tracked backlog work.

## Goal

Prove that running the **entire factory** inside a single **rootless**
container — project directory (cwd) bind-mounted as a read-write volume, a
rootless runtime user, attached shell — delivers a meaningfully stronger
boundary against (a) host-filesystem/credential escape and (b) undesired
network egress, while the orchestrator flow still works against the mounted
cwd. Second-class goal folded in from the stakeholder: **whitelist/blacklist
egress must be easy to configure** (a config file, not a hand-tuned firewall).

## Why this is a candidate

Containerization buys a hard host boundary that today's host-native subprocess
model lacks. Rootless removes the "root-in-container = root-on-host" escalation
path (user-namespace mapping to an unprivileged host uid). The simplification
over per-phase containers: ONE sandbox around the whole factory instead of
orchestrating per-phase isolation. Restricting the container's network and
routing all egress through a small allowlist/denylist proxy delivers the
"easy configuration" criterion declaratively.

## What to build

- A rootless container runtime (podman 3.4.4 is rootless-by-default and
  already installed; Docker-rootless is the equivalent alternative).
- A base image with the factory's runtimes (python + node) so the
  orchestrator/scripts can run inside.
- The project dir bind-mounted read-write into the container (this is cwd).
- Rootless runtime user; no host home directories mounted.
- Network restricted; the container's ONLY egress path is an allowlist/denylist
  proxy configured by a plain text config file.
- Inside the container, a minimal orchestrator run proving phase dispatch,
  artifact persistence across phases on the mounted cwd, and gate resolution.
  (Real AI-CLI auth is out of scope for the boundary proof — a stand-in "agent"
  that writes an artifact is enough; the boundary does not depend on it.)

## Definition of done

Mechanical checklist, each run and confirmed (commented-out "should" is not
done):

- **(a) host isolation**
  - [ ] From inside the container: `/etc/shadow`, `~/.aws`, `~/.ssh`,
    `~/.config` are unreadable (no-such-file / permission-denied).
  - [ ] A secret file planted on the host at a known path is **not visible**
    inside the container.
  - [ ] The mounted cwd (project) IS read-write and usable from inside.
- **(b) egress control**
  - [ ] With default allow-entire-egress *disabled*, an exfil attempt: `curl`
    to a local host listener AND `curl https://example.com` → **blocked**.
  - [ ] With a whitelist entry added, the allowlisted endpoint **is** reachable.
  - [ ] Policy change is a one-file config edit (whitelist OR blacklist mode).
- **integration**
  - [ ] A phase "agent" runs inside the container and writes the worktree.
  - [ ] A later phase reads that artifact from the shared mounted cwd.
  - [ ] Gate / human-gate / final-state resolution behaves as it does today.

Record evidence as `poc/notes/containerized-<date>.md` (the comparison note).

## Comparison note

Close this story by writing the note above with the (a)/(b)/integration
checklists' actual results, plus effort and friction observed (rootless setup,
UID mapping of the bind mount, network/proxy wiring). Step 4 reads it.
