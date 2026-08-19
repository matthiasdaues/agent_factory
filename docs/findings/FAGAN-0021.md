---
id: FAGAN-0021
source: fagan-review
severity: major
category: defect
artifact: /home/matthiasdaues/.pi/agent/extensions/openwebui.ts:85
status: open
---

# escapeConfigValue escapes only the leading character; interior $VAR still interpolates

**What is wrong:** `escapeConfigValue` prefixes `$` only when the key starts with `$` or `!`. But pi's resolver (`dist/core/resolve-config-value.js`) parses the value as a template: every unescaped `$NAME` or `${NAME}` anywhere in the string interpolates from the environment, and only `$$` / `$!` are literal escapes. A literal key such as `ab$HOME` or `x$1$y` passes through unchanged (it does not start with `$`/`!`) and is then silently corrupted at resolve time — a wrong bearer token is sent, or resolution returns `undefined` and auth fails. Where interpolation succeeds, environment values leak into the `Authorization` header.

**Fix:** Escape every `$`, then neutralize a leading `!`. Beware JavaScript's replacement-string syntax: `value.replace(/\$/g, "$$")` is a **no-op** (each `$$` in a replacement string yields one literal `$`). Use `value.replace(/\$/g, "$$$$")` (or `value.split("$").join("$$")`), then `$`-prefix when the result starts with `!`. Verify against pi's resolver with keys containing `$x`, `${x}`, `$!`, and leading `!`.

**Repeat-pass verification (2026-08-19):** Still open. The rework adopted exactly the no-op form (`value.replace(/\$/g, "$$")`), so interior `$VAR` and `${VAR}` still interpolate. Empirical round-trip against the installed resolver (`@earendil-works/pi-coding-agent@0.84.0`, `dist/core/resolve-config-value.js`): 13 probe keys — `ab$HOME` resolves to `ab/home/matthiasdaues`, `x$1$y` resolves to `undefined`, `$HOME`, `${HOME}`, `!$HOME`, `$$double`, `a${HOME}b` all mangled; `$!` handling works only when no `$` is present. The corrected form with `"$$$$"` passes all 13 cases (PASS `ab$HOME` → `ab$$HOME` → literal) — the fix is one character pair away.
