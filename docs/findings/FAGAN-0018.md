---
id: FAGAN-0018
source: fagan-review
severity: major
category: defect
artifact: /home/matthiasdaues/.pi/agent/extensions/openwebui.ts:120
status: resolved
---

# Env-only instances beyond "default" are never loaded

**What is wrong:** `loadInstances` iterates `["default", ...Object.keys(fileInstances)]` (line 122), so the environment is only ever consulted for the literal name `default` plus names already present in the config file. An instance defined purely by environment variables — e.g. `OPENWEBUI_WORK_BASE_URL` / `OPENWEBUI_WORK_API_KEY` with no `work` entry in the file — is silently never registered, and no warning is emitted. This contradicts both the header comment ("OPENWEBUI\_<NAME>_BASE_URL / OPENWEBUI_<NAME>\_API_KEY otherwise", lines 17–21) and the function's own doc comment ("env can supply any instance by name convention", line 119).

**Fix:** Either scan `process.env` for `OPENWEBUI_<NAME>_BASE_URL` pairs (regex `^OPENWEBUI_(.+)_BASE_URL$`, mapping `_` back to `-` per `envPrefixFor`) and merge them under the file's precedence, or correct the two documentation claims to state "environment supplies `default` and file-known names only." The first option matches the documented contract; the second narrows it.

**Resolution (repeat pass 2026-08-19):** Fixed as claimed. `envConfiguredNames()` scans `process.env` with `ENV_BASE_URL_PATTERN = /^OPENWEBUI(?:_([A-Z0-9_]+))?_BASE_URL$/` and merges scanned names with file-known names in `loadInstances` (empty group maps to `default`, uppercase group lowercased with underscores mapped back to dashes — the exact inverse of `envPrefixFor`). The header comment now also documents that the environment is scanned for any name.
