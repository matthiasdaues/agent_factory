# Comparison note — Candidate 2: Whole-factory rootless container

Date: 2026-08-07
Runtime: Ubuntu 22.04, kernel 6.8, podman 3.4.4 (rootless), image python:3.12-slim.

## Definition-of-done results

### (a) host isolation

- [x] Host secret paths unreadable from inside the container.
  - `~/.aws`, `~/.ssh`, `~/.config` → **absent** (host home not mounted;
    only the container's own `/home/worker` exists).
  - `/etc/shadow` and `/root` are the **container's own** (from the base
    image), not the host's.
- [x] Host secret file planted at `~/poc-host-secret.*` → **not visible**
  inside (`/home/matthiasdaues/` does not exist in the container).
- [x] Mounted cwd (project) is read-write and usable (`WROTE to /work/.poc-write-test OK`; gate script runs from `/work`).

### (b) egress control

- [x] **Deny posture** (`--network none`): egress **blocked and enforced** —
  only `lo` interface, `curl https://example.com` fails with
  "Could not resolve host", HTTP 000.
- [x] **Allowlist proxy (sidecar, shared pod netns)**: worker reaches the
  proxy at `127.0.0.1:8080`; `curl -x` → ALLOWED `example.com` **HTTP 200**,
  DENIED `example.net` → **403 from proxy**.
- [x] Policy change is a one-file JSON edit (`mode: allowlist|denylist` +
  `rules: [..]`); bare-domain + `*.subdomain` wildcard matching.

### integration

- [x] A phase agent runs inside the container and writes the worktree.
- [x] A **separate** container (phase B) reads an artifact written by phase A
  via the shared bind-mounted cwd — cross-run persistence works.
- [x] Factory machinery runs inside the sandbox against the mounted project:
  `python factory/scripts/phase advance --playbook greenfield-development --dry-run` → `would advance INIT -> PHASE_1_REQUIREMENTS`, exit 0.

## Effort / friction observed

- Rootless works out of the box on this host (rootlesskit, slirp4netns,
  newuidmap, subuid `100000:65536` all present).
- `--userns=keep-id` cleanly preserves host ownership of the mounted project —
  files written in the container are owned by host uid 1000, no UID-shifting
  manual work.
- **Known, honest limitation (documented, not hidden):** rootless
  slirp4netns does **not** firewall raw sockets. A hostile in-container
  process could bypass an in-pod proxy and reach the internet directly via
  slirp. The `--network none` deny posture is fully enforced; the *proxy
  allowlist* is enforced at the proxy choke point but is **advisory** against
  a hostile process under slirp4netns. True enforcement of selective egress in
  this nested-dev shape needs Docker-rootful firewall / nftables or a
  dedicated egress gateway.
- `--userns` and `--pod` cannot be combined; the pod-based proxy test runs
  without `keep-id` (fine — it does not need the bind mount).

## Verdict (for Step 4)

- **(a) Host-fs/credential isolation: SOLID WIN.** The rootless container is a
  real, enforced boundary; the project's own secret surface (`.aws`, `.ssh`,
  `.config`) is simply not present. Strictly stronger than the baseline.
- **(b) Egress: PARTIAL.** `--network none` gives strong enforced
  isolation; the easy-config allowlist/denylist proxy is demonstrated and
  ergonomically attractive, but under rootless slirp it is advisory, not
  enforced, against a hostile process.
- **Integration: SOLID.** Orchestration and cross-phase artifact flow run
  unmodified against the mounted cwd.
- **Operational cost: MODERATE.** Rootless podman is near-zero friction here;
  helper/sidecar topology adds a little but stays simple.

**Bottom line:** the whole-factory-rootless-container model is a genuine,
meaningful hardening over the status quo (a) and integration, and a good
ergonomic base for (b) — but the egress story must be scoped honestly: strong
(`--network none`) or ergonomic-but-advisory (allowlist proxy) under rootless.
