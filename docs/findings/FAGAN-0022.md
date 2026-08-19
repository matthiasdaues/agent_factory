---
id: FAGAN-0022
source: fagan-review
severity: major
category: defect
artifact: /home/matthiasdaues/.pi/agent/extensions/openwebui.ts:303
status: resolved
---

# /unregister on env-sourced instances unregisters anyway, then misleads

**What is wrong:** The handler calls `pi.unregisterProvider(providerIdFor(name))` unconditionally (line 310) before checking `removeInstance`'s result, and only then — when the name was not in the config file — warns "No instance named X … If it came from environment variables, unset them instead." That message implies nothing happened. In fact the provider is gone for the current session while its env configuration is still intact, and it silently re-registers on the next `/reload`. The header claim "removes an instance from the config file and unregisters its provider" is false for this path.

**Fix:** Choose one semantic and make the message truthful. Either (a) detect env-sourced names (`envPrefixFor(name)` + `process.env`) and refuse with "unset the environment variables instead", leaving the provider registered; or (b) keep the unregister but warn "unregistered for this session; it will return on /reload unless you unset OPENWEBUI\_<NAME>\_BASE_URL." Option (a) is less surprising.

**Resolution (repeat pass 2026-08-19):** Fixed as claimed, adopting option (a). The handler calls `pi.unregisterProvider` only when `removeInstance` returned true; the not-in-file branch warns "No instance named X in CONFIG_PATH; nothing removed. If it came from environment variables, unset them and /reload." and leaves the provider untouched. The header now documents exactly this semantic ("env-sourced instances cannot be removed by command"). One residual edge (file+env dual-sourced name) is recorded as suggestion S11 in the repeat report.
