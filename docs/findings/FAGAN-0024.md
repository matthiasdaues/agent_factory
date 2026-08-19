---
id: FAGAN-0024
source: fagan-review
severity: minor
category: defect
artifact: /home/matthiasdaues/.pi/agent/extensions/openwebui.ts:364
status: resolved
traces: [Q1]
---

# Q1 rework introduced a strict-mode type error on the apiKey assignment

**What is wrong:** `let apiKey = apiKeyArg;` infers type `string` from the positional argument, then the prompt fallback assigns `(await ctx.ui.input(...))?.trim()`, whose type is `string | undefined` — `tsc --strict` rejects with `TS2322: Type 'string | undefined' is not assignable to type 'string'` (line 368 of the external target). Runtime behavior is unaffected (pi transpiles extensions without typechecking, and the following `if (!apiKey) return` guards `undefined`), but the file no longer passes a strict typecheck, so the rework shipped unverified against the one cheap deterministic gate available for a TypeScript artifact.

**Fix:** Annotate the declaration: `let apiKey: string | undefined = apiKeyArg;`. Verified: the file then passes `tsc --noEmit --strict --skipLibCheck --module esnext --moduleResolution bundler --target es2022` clean against `@earendil-works/pi-coding-agent@0.84.0`.

**Verification pass 2 (2026-08-19):** Resolved. The declaration now carries exactly that annotation (line 364). Re-run independently, not from the author's claim: the file was copied byte-identically (sha256 match) into a probe workspace with `@types/node` and the installed package's types, and `tsc --noEmit --strict --skipLibCheck --module esnext --moduleResolution bundler --target es2022` (typescript 5.9.3) exits 0 with no diagnostics. Mutation control: removing the annotation reproduces the original TS2322 at line 370 — the gate genuinely exercises this defect class, so the green run is not trivial. The edit is annotation-only; runtime behavior and the `if (!apiKey)` guards are unchanged, and no new diagnostics appeared anywhere in the file.
