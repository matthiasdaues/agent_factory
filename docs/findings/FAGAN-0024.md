---
id: FAGAN-0024
source: fagan-review
severity: minor
category: defect
artifact: /home/matthiasdaues/.pi/agent/extensions/openwebui.ts:362
status: open
traces: [Q1]
---

# Q1 rework introduced a strict-mode type error on the apiKey assignment

**What is wrong:** `let apiKey = apiKeyArg;` infers type `string` from the positional argument, then the prompt fallback assigns `(await ctx.ui.input(...))?.trim()`, whose type is `string | undefined` — `tsc --strict` rejects with `TS2322: Type 'string | undefined' is not assignable to type 'string'` (line 368 of the external target). Runtime behavior is unaffected (pi transpiles extensions without typechecking, and the following `if (!apiKey) return` guards `undefined`), but the file no longer passes a strict typecheck, so the rework shipped unverified against the one cheap deterministic gate available for a TypeScript artifact.

**Fix:** Annotate the declaration: `let apiKey: string | undefined = apiKeyArg;`. Verified: the file then passes `tsc --noEmit --strict --skipLibCheck --module esnext --moduleResolution bundler --target es2022` clean against `@earendil-works/pi-coding-agent@0.84.0`.
