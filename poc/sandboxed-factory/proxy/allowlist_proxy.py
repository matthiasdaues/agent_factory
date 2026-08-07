"""Allowlist/denylist forward proxy (PoC).

The single choke point for container egress. Policy is a plain JSON file:
"easy configuration of whitelist or blacklist egress control". Apps inside
the worker point http_proxy/https_proxy here; the proxy admits or refuses each
outbound target before a single byte is sent upstream.

Supports HTTP forward requests (absolute-form) and HTTPS via CONNECT, which is
what AI CLIs and package managers use.
"""

import json
import os
import socket
import sys
import threading
from urllib.parse import urlparse

POLICY_FILE = os.environ.get("EGRESS_POLICY", "/policy/policy.json")
LISTEN = os.environ.get("EGRESS_PROXY_LISTEN", "0.0.0.0:8080")


def load_policy():
    with open(POLICY_FILE) as fh:
        return json.load(fh)


def allowed(host: str) -> tuple[bool, str]:
    p = load_policy()
    rules = p.get("rules", [])
    matched = False
    for r in rules:
        if host == r:
            matched = True
            break
        if r.startswith("*.") and host.endswith(r[1:]):
            matched = True
            break
    if p.get("mode") == "allowlist":
        return matched, "mode=allowlist"
    return (not matched), "mode=denylist"


def _conn_error(client, msg: bytes):
    try:
        client.sendall(
            b"HTTP/1.1 403 Forbidden\r\nContent-Type: text/plain\r\n\r\n" + msg
        )
    except OSError:
        pass


def pump(src, dst):
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            dst.sendall(data)
    except OSError:
        pass
    finally:
        for s in (src, dst):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                s.close()
            except OSError:
                pass


def _target_of(method, target):
    """Return (host, port) for a request line, or None."""
    if method == "CONNECT":
        host, _, port = target.partition(":")
        return host, int(port or 443)
    parsed = urlparse(target)
    if not parsed.hostname:
        return None
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    return parsed.hostname, int(port)


def handle(client):
    try:
        client.settimeout(20)
        head = client.recv(65536).decode("utf-8", errors="ignore")
        if not head:
            return
        lines = head.split("\r\n")
        parts = lines[0].split() if lines else []
        if len(parts) < 2:
            return
        method, target = parts[0], parts[1]
        hp = _target_of(method, target)
        if hp is None:
            _conn_error(client, b"bad target\n")
            return
        host, port = hp
        ok, why = allowed(host)
        if not ok:
            _conn_error(client, f"EGRESS-POLICY-DENIED {host} ({why})\n".encode())
            return
        upstream = socket.create_connection((host, port), timeout=20)
        if method == "CONNECT":
            client.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")
            t = threading.Thread(target=pump, args=(client, upstream))
            t.start()
            pump(upstream, client)
            t.join(timeout=1)
        else:
            # forward absolute-form HTTP request as-is
            upstream.sendall(head.encode("utf-8", errors="ignore"))
            t = threading.Thread(target=pump, args=(client, upstream))
            t.start()
            pump(upstream, client)
            t.join(timeout=1)
    except Exception as exc:  # noqa: BLE001 - PoC
        try:
            client.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n" + str(exc).encode())
        except OSError:
            pass
    finally:
        try:
            client.close()
        except OSError:
            pass


def main():
    host, _, port = LISTEN.partition(":")
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, int(port)))
    srv.listen(128)
    print(f"egress proxy on {LISTEN} policy={POLICY_FILE}", flush=True)
    while True:
        conn, _ = srv.accept()
        threading.Thread(target=handle, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    sys.exit(main())
