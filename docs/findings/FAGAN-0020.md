---
id: FAGAN-0020
source: fagan-review
severity: major
category: defect
artifact: /home/matthiasdaues/.pi/agent/extensions/openwebui.ts:255
status: resolved
---

# URL validation accepts non-http(s) schemes and bare host:port forms

**What is wrong:** `/register` validates with `new URL(baseUrlArg)` and then only warns when the protocol is not `https:` and the hostname is not `localhost`/`127.0.0.1`. `new URL` accepts far more: `file:///etc/…`, `ftp://host`, and scheme-like `host:port` inputs such as `localhost:8080` (parsed as protocol `localhost:`, empty hostname). All of these pass with at most a misleading "plain HTTP to a remote host" warning, are persisted to the config file, and only fail later at discovery with a confusing fetch error — the handler's own success notification then claims the config was saved.

**Fix:** After parsing, hard-reject unless the protocol is `http:` or `https:` and the hostname is non-empty. Emit the plain-HTTP warning only for an actual `http:` non-local URL. Apply the same guard in `normalizeConfig` so hand-edited or legacy config files are validated on load.

**Resolution (repeat pass 2026-08-19):** Fixed and verified empirically. `normalizeBaseUrl()` hard-rejects non-http(s) schemes, empty hosts, userinfo, query, and fragment, and is reused by `normalizeConfig` for file-sourced values and by `loadInstances` for env-sourced values; invalid file entries are dropped into an `invalid` list surfaced as startup warnings. A 15-case probe (`file:`, `ftp:`, `localhost:8080`, userinfo, `[::1]`, trailing-dot `localhost.`, `0.0.0.0`, `127.*`) rejects all malformed inputs and accepts all valid ones. Also closes S1 (userinfo now rejected; `[::1]`, `0.0.0.0`, trailing-dot handled) and S6 (file values validated).
