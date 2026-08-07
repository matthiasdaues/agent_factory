#!/usr/bin/env bash
# PoC launcher — run the whole factory in a rootless container with the
# project dir (cwd) mounted read-write, and selectable egress posture.
#
# Usage:
#   ./run-worker.sh deny    # --network none → no egress at all (enforced)
#   ./run-worker.sh allow   # slirp network + allowlist proxy on host:8080
set -euo pipefail

IMAGE=poc-worker:latest
PODMAN="${PODMAN:-podman}"
POSTURE="${1:-deny}"
CWD_PROJECT="$(pwd)"
PROJECT_NAME="$(basename "$CWD_PROJECT")"
CONTAINER="poc-$PROJECT_NAME-$POSTURE"

# Build the worker image if missing.
if ! "$PODMAN" image exists "$IMAGE" 2>/dev/null; then
  echo ">> building $IMAGE"
  "$PODMAN" build -t "$IMAGE" -f "$(dirname "$0")/build/Containerfile.worker" "$(dirname "$0")/build"
fi

# Remove any prior container with this name (PoC scratch, safe to delete).
"$PODMAN" rm -f "$CONTAINER" >/dev/null 2>&1 || true

NET_ARGS=()
if [ "$POSTURE" = "allow" ]; then
  # slirp4netns network; all app egress is pointed at the host allowlist proxy.
  # NOTE (honest limitation): rootless slirp4netns does NOT firewall raw
  # sockets, so a hostile in-container process could bypass the proxy. A truly
  # enforced egress needs Docker-rootful firewall or a dedicated egress gateway.
  NET_ARGS+=(--network slirp4netns)
  NET_ARGS+=(-e http_proxy=http://10.0.2.2:8080 -e https_proxy=http://10.0.2.2:8080)
else
  # deny: fully enforced — no network interface at all inside the container.
  NET_ARGS+=(--network none)
fi

echo ">> launching rootless container '$CONTAINER' ($POSTURE posture)"
echo "   cwd (project) mounted read-write at /work"

"$PODMAN" run --rm -it --name "$CONTAINER" \
  --userns=keep-id \
  -v "$CWD_PROJECT:/work:rw" \
  -w /work \
  "${NET_ARGS[@]}" \
  "$IMAGE"
