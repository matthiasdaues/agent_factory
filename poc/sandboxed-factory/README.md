# PoC — Sandboxed Factory (rootless container + egress control)

**Topical PoC folder.** Question: does running the whole factory in one
rootless container with the project dir mounted read-write, plus configurable
egress control, give a meaningfully stronger security boundary (host-fs escape,
undesired network) than today's host-native subprocess model?

Referenced by `poc/spikes/*` (stories) and evaluated in `notes/*`.

## Layout

```
.
├── spikes/          # technical-poc stories (baseline + candidate)
├── notes/           # comparison notes — the evidence the decision reads
├── build/           # Containerfile.worker (runtime image)
├── proxy/           # allowlist/denylist egress proxy (policy.json = the config)
├── run-worker.sh    # launcher: deny | allow posture
└── README.md
```

## Build

```bash
podman build -t poc-worker:latest -f build/Containerfile.worker build
```

## Deny posture (isolation + enforced no-egress)

```bash
podman run --rm --network none --userns=keep-id \
  -v "$PWD:/work:rw" -w /work poc-worker:latest bash -c '
  ls -d /home/*/;                        # expect only /home/worker
  ls ~/.aws ~/.ssh ~/.config 2>&1;       # expect No such file
  curl -sS -m 6 https://example.com;'    # expect fail (no network)
```

## Cross-phase persistence (two separate containers, shared volume)

```bash
podman run --rm --network none --userns=keep-id -v "$PWD:/work:rw" -w /work \
  poc-worker:latest bash -c 'echo v1 > /work/poc/artifacts/a.txt && cat /work/poc/artifacts/a.txt'
podman run --rm --network none --userns=keep-id -v "$PWD:/work:rw" -w /work \
  poc-worker:latest bash -c 'cat /work/poc/artifacts/a.txt'
```

## Factory runs inside the sandbox

```bash
podman run --rm --network none --userns=keep-id -v "$PWD:/work:rw" -w /work \
  poc-worker:latest bash -c 'python factory/scripts/phase advance --playbook greenfield-development --dry-run'
```

## Allow posture — egress proxy (sidecar, shared pod netns)

```bash
cat > /tmp/poc-policy.json <<'EOF'
{ "mode": "allowlist", "rules": ["example.com", "*.example.com"] }
EOF
podman pod create --name poc-pod --network slirp4netns
podman run -d --pod poc-pod --name poc-proxy \
  -v /tmp/poc-policy.json:/policy/policy.json:ro \
  -v "$PWD/proxy:/proxy:ro" -e EGRESS_POLICY=/policy/policy.json \
  python:3.12-slim python3 /proxy/allowlist_proxy.py
podman run --rm --pod poc-pod \
  -e http_proxy=http://127.0.0.1:8080 -e https_proxy=http://127.0.0.1:8080 \
  poc-worker:latest bash -c '
  curl -x http://127.0.0.1:8080 -o /dev/null -w "ALLOWED example.com -> %{http_code}\n" https://example.com
  curl -x http://127.0.0.1:8080 -o /dev/null -w "DENIED example.net -> %{http_code}\n" https://example.net'
podman pod rm -f poc-pod    # cleanup
```

## Honest limitation to keep in view

`--network none` is fully enforced. The allowlist proxy is enforced at its own
choke point but is **advisory** against a hostile process under rootless
slirp4netns (raw sockets are not firewalled there). True selective-egress
enforcement may need Docker-rootful firewall / nftables or a dedicated egress
gateway — this is the crux of the decision.
