---
id: FAGAN-0021
source: fagan-review
severity: major
category: defect
artifact: ~/.pi/agent/extensions/openwebui.ts:103
status: resolved
---

# escapeConfigValue escapes only the leading character; interior $VAR still interpolates

**What is wrong:** `escapeConfigValue` prefixes `$` only when the key starts with `$` or `!`. But pi's resolver (`dist/core/resolve-config-value.js`) parses the value as a template: every unescaped `$NAME` or `${NAME}` anywhere in the string interpolates from the environment, and only `$$` / `$!` are literal escapes. A literal key such as `ab$HOME` or `x$1$y` passes through unchanged (it does not start with `$`/`!`) and is then silently corrupted at resolve time — a wrong bearer token is sent, or resolution returns `undefined` and auth fails. Where interpolation succeeds, environment values leak into the `Authorization` header.

**Fix:** Escape every `$`, then neutralize a leading `!`. Beware JavaScript's replacement-string syntax: `value.replace(/\$/g, "$$")` is a **no-op** (each `$$` in a replacement string yields one literal `$`). Use `value.replace(/\$/g, "$$$$")` (or `value.split("$").join("$$")`), then `$`-prefix when the result starts with `!`. Verify against pi's resolver with keys containing `$x`, `${x}`, `$!`, and leading `!`.

**Repeat-pass verification (2026-08-19):** Still open. The rework adopted exactly the no-op form (`value.replace(/\$/g, "$$")`), so interior `$VAR` and `${VAR}` still interpolate. Empirical round-trip against the installed resolver (`@earendil-works/pi-coding-agent@0.84.0`, `dist/core/resolve-config-value.js`): 13 probe keys — `ab$HOME` resolves to `ab~`, `x$1$y` resolves to `undefined`, `$HOME`, `${HOME}`, `!$HOME`, `$$double`, `a${HOME}b` all mangled; `$!` handling works only when no `$` is present. The corrected form with `"$$$$"` passes all 13 cases (PASS `ab$HOME` → `ab$$HOME` → literal) — the fix is one character pair away.

**Verification pass 2 (2026-08-19):** Resolved. The function now reads `value.replace(/\$/g, "$$$$")` (each `$` doubled) plus `$`-prefixing when the escaped result starts with `!`. Re-verified independently, not from the author's claim: the function was extracted verbatim from the current file and round-tripped through the installed resolver (`@earendil-works/pi-coding-agent@0.84.0`, `dist/core/resolve-config-value.js`). **17/17 probes pass** — the author's 10 (`ab$HOME`, `x$1$y`, `$HOME`, `${HOME}`, `!$HOME`, `$$double`, `a${HOME}b`, `!cmd`, `plain-key`, `sk-abc123`) plus 7 extras (`$!`, `!`, `a$b$c`, `sp ace`, `a!b$HOME`, `${HOME` unclosed, `!!`) — every probe resolves to its raw input. The escaped output can never begin with `!`, so the resolver's shell-command path is unreachable, and the doc comment above the function now accurately describes the implementation.
