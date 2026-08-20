---
title: Fagan Inspection — Pi extension openwebui.ts
date: 2026-08-19
reviewer: qa-agent
target: ~/.pi/agent/extensions/openwebui.ts (327 lines, external to this repo)
scope: Fagan Inspection only — no OWASP pass, no bug-hunt/fix loop, no code changes
---

# Fagan Inspection — openwebui.ts

## Roles

- **Moderator/Reader/Tester:** qa-agent (this session).
- **Author:** absent. Author-clarification items are recorded as Questions (Q1–Q2) and filed in [docs/spec/todo.md](../spec/todo.md).

The target is a Pi extension that registers named OpenWebUI instances as pi providers with dynamic model discovery from `/api/models`. Framework claims were verified against the installed pi package (`@earendil-works/pi-coding-agent`, `dist/core/resolve-config-value.js`, `dist/core/model-runtime.js`, README/docs env-var table) rather than assumed.

## Header-comment claims vs. actual behavior

| #   | Claim (lines 6–36)                                              | Verdict                                                                                                                                   |
| --- | --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Model list fetched from OpenAI-compatible `/api/models`         | Holds                                                                                                                                     |
| 2   | `/register` adds/updates, persists, re-registers immediately    | Holds                                                                                                                                     |
| 3   | `/unregister` removes from config file and unregisters provider | **False for env-sourced instances:** provider is unregistered even when nothing was in the file — [FAGAN-0022](../findings/FAGAN-0022.md) |
| 4   | Env config by name convention (`OPENWEBUI_<NAME>_…`)            | **False beyond `default` + file-known names** — [FAGAN-0018](../findings/FAGAN-0018.md)                                                   |
| 5   | Provider registered even when discovery/auth fails              | Holds (catch → warning → registers with empty model list)                                                                                 |
| 6   | Auth heals via `/login <provider-id>`                           | Holds for the `$ENV`-reference case (pi resolves a single-env-var apiKey); literal-key case plausible via pi auth storage                 |
| 7   | Persists to `~/.pi/agent/openwebui.json`                        | **False when `PI_CODING_AGENT_DIR` is set** — [FAGAN-0019](../findings/FAGAN-0019.md)                                                     |
| 8   | `MODEL_OVERRIDES` keyed by `<instance>/<model id>`              | Incomplete — undocumented bare-model-id fallback (line 196); see S4                                                                       |

## Inspection walkthrough by logical unit

### Module docstring (lines 1–36)

Clear and mostly accurate; claims 3, 4, 7, 8 deviate as tabled above. The "first source wins" precedence is implemented correctly for names that are checked at all.

### Config load/persist (lines 91–149)

- `readFileInstances` swallows all errors (missing/malformed file → `{}`), including the legacy-shape migration. Acceptable, but note S6 (no URL validation on file-sourced values).
- `persistInstance` / `removeInstance` are read-modify-write with no serialization — [FAGAN-0023](../findings/FAGAN-0023.md).
- `writeInstances` sets `0o600` — good key hygiene on the persisted file.

### Env resolution (lines 75–88, 118–128)

- `envPrefixFor` is correct and collision-free (NAME_PATTERN excludes underscores).
- The name iteration misses env-only instances — [FAGAN-0018](../findings/FAGAN-0018.md).
- `escapeConfigValue` is under-powered against pi's actual template parser — [FAGAN-0021](../findings/FAGAN-0021.md).

### Discovery + provider registration (lines 151–203)

- Timeout via `AbortSignal.timeout`, typed filter on payload, warnings instead of throws — sound.
- Verified against pi: `unregisterProvider` on an unknown id is a safe no-op (`Map.delete` + recompose), and a single `$ENV` apiKey supports `/login` healing.
- S4: override lookup falls back to a bare model id, undocumented.

### `/register` command (lines 239–298)

- Name validated against `NAME_PATTERN`; usage error on missing args — good.
- URL validation is too weak — [FAGAN-0020](../findings/FAGAN-0020.md). Local-host check edge cases and userinfo acceptance: S1. Silent dropping of extra args: S2.
- Persist-then-discover ordering matches the documented heal-later design.

### `/unregister` command (lines 300–325)

- Env-sourced-instance semantics are broken — [FAGAN-0022](../findings/FAGAN-0022.md).

### Load-time sequence + `session_start` replay (lines 205–236)

- No stdout/stderr writes at load (TUI-safe) — correct and documented.
- Warnings replayed per instance on `session_start`; dropped silently when headless (S7).
- No race between load-time discovery and command handlers: commands register only after discovery completes. The cost is sequential blocking (S5).

## Finding table

| Finding                                                                                                                                              | Artifact                | Category                            | Severity  |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- | ----------------------------------- | --------- |
| [FAGAN-0018](../findings/FAGAN-0018.md) — env-only instances beyond `default` never load; contradicts header + doc comment                           | openwebui.ts:120–131    | Defect (logic / interface-contract) | Major     |
| [FAGAN-0019](../findings/FAGAN-0019.md) — `CONFIG_PATH` ignores `PI_CODING_AGENT_DIR`                                                                | openwebui.ts:40         | Defect (interface/contract, data)   | Major     |
| [FAGAN-0020](../findings/FAGAN-0020.md) — URL validation accepts non-http(s) schemes and `host:port` forms; persists unusable config                 | openwebui.ts:255–268    | Defect (logic, error handling)      | Major     |
| [FAGAN-0021](../findings/FAGAN-0021.md) — `escapeConfigValue` escapes only the leading character; interior `$VAR` still interpolates at resolve time | openwebui.ts:85–87, 193 | Defect (security, data)             | Major     |
| [FAGAN-0022](../findings/FAGAN-0022.md) — `/unregister` unregisters env-sourced providers anyway, then misleads; silent resurrection on `/reload`    | openwebui.ts:303–318    | Defect (logic / interface-contract) | Major     |
| [FAGAN-0023](../findings/FAGAN-0023.md) — read-modify-write race on config file between async command handlers                                       | openwebui.ts:131–149    | Defect (concurrency)                | Minor     |
| S1 — `isLocal` misses `[::1]`, `0.0.0.0`, trailing-dot `localhost.`; userinfo `https://user:pass@host` accepted and persisted into `baseUrl`         | openwebui.ts:262–263    | Suggestion                          | Minor     |
| S2 — extra args silently dropped; whitespace inside `apiKey` truncated                                                                               | openwebui.ts:242        | Suggestion                          | Minor     |
| S3 — generic command names `register`/`unregister` risk collision with other extensions; namespace them                                              | openwebui.ts:239, 300   | Suggestion                          | Minor     |
| S4 — `MODEL_OVERRIDES` bare-id fallback undocumented (comment line 53 vs lookup line 196)                                                            | openwebui.ts:53, 196    | Suggestion                          | Minor     |
| S5 — load-time discovery is sequential; N dead instances × 10 s timeout delays extension load and command registration. Use `Promise.all`            | openwebui.ts:233–236    | Suggestion                          | Minor     |
| S6 — `normalizeConfig` applies no URL validation to file-sourced values                                                                              | openwebui.ts:91–100     | Suggestion                          | Minor     |
| S7 — warnings silently dropped when `!ctx.hasUI`; consider a headless fallback                                                                       | openwebui.ts:209–217    | Suggestion                          | Editorial |
| Q1 — is the typed `/register … <apiKey>` command line excluded from session transcripts/history? If not, key entry should use a prompt               | openwebui.ts:239–248    | Question                            | —         |
| Q2 — intended behavior when `/register` re-registers with a model list that drops the session's currently selected model?                            | openwebui.ts:281–283    | Question                            | —         |

## Fagan summary

- **Critical:** 0 — **Major:** 5 — **Minor:** 1 (defects); plus 7 minor/editorial suggestions and 2 author questions held in this report.
- Error-handling paths: discovery failures degrade gracefully by design; the gaps are validation (FAGAN-0020), unregister semantics (FAGAN-0022), and escaping (FAGAN-0021).
- No load-time/command-handler race exists (commands register after discovery); the real concurrency defect is config-file write interleaving (FAGAN-0023).
- API-key hygiene is otherwise good: `0o600` on the config file, no key in notifications, `$ENV` reference when no key is held.

**Verdict: rework.** Five major defects must be fixed; a re-inspection pass should verify the fixes (per review-loop discipline) before the extension is considered accepted.
