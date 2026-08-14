---
id: FAGAN-0017
source: fagan-review
severity: minor
category: defect
artifact: factory/config/extensions/run-agent.ts:336
status: resolved
traces: [BUG-0008, UC-10, BR-040]
---

# extractEnvelopeObject keeps the rightmost record, not the largest; a valid leading envelope can be discarded

**What is wrong:** `extractEnvelopeObject`'s last-resort balanced-brace scan
keeps the record whose closing brace has the largest index
(`if (i > recoveredEnd) { … recovered = value; recoveredEnd = i; }`) — i.e. the
rightmost balanced object — though the doc comment says it keeps "the LARGEST
decoded object." For a single envelope with nested JSON the outer object is
both rightmost-closing and largest, so the intended case works. But for a
message that is neither a single JSON record nor a fenced block, where a valid
envelope is followed by a *larger sibling* JSON object (e.g. an example), the
scan selects the later sibling; `parseChildResultEnvelope` then rejects it for
not having the four canonical fields, and a valid envelope is reported as a
parse error. The whole-message and fenced-code-block candidates handle the
common cases, so the window is narrow, and the BUG-0008 commit-disclosure
fallback still surfaces completed work, so no work is lost — but the envelope
itself is discarded and the result degrades to a disclosed error.

**Fix:** Prefer an envelope-shaped record over a merely-rightmost one. Among
recovered records, return the first that `JSON.parse`es to an object with
exactly the four canonical fields; or keep the largest by
`JSON.stringify(...).length` rather than by closing-brace index; or, at
minimum, correct the doc comment to state "rightmost balanced object" and add a
regression test for the envelope-then-larger-sibling case.

## Verification Evidence

- Probe `factory/config/extensions/__tests__/__qa_probe.mjs` (run via the
  envelope-loader stub) case 3:
  `goodText + " example: " + JSON.stringify({a:{b:1,c:2,d:3,e:4,f:5}})`
  → `extractEnvelopeObject` returns `{"a":{"b":1,…}}` (the later sibling),
  and `parseChildResultEnvelope` returns
  `"expected exactly four canonical fields"` — the valid envelope is lost.
- The reverse order (smaller sibling then envelope, case 3b) correctly returns
  the envelope (it is the rightmost record).

## Re-validation Evidence (2026-08-06)

**Verdict: PASS — status confirmed `resolved`.** Fix commit `14a6d19` rewrites
the balanced-brace scan to collect all records, then return the first with
exactly the four canonical fields (`ENVELOPE_FIELDS` is pre-sorted, so
`Object.keys(value).sort().join("|")` compares correctly), else fall back to the
largest by raw-slice length. The doc comment matches the behaviour. The
envelope-then-larger-sibling case now returns the envelope; the throwaway probe
`__qa_probe.mjs` is removed and the case is folded into `envelope.test.ts`.

- Envelope suite: **19 pass, 0 fail**, incl.
  `extractEnvelopeObject prefers envelope over larger sibling (FAGAN-0017)`,
  `…finds envelope when it is the rightmost`, and
  `…falls back to largest when no envelope-shaped`.
- Full report: `docs/reviews/qa-revalidation-2026-08-06-bug-run-agent-envelope.md`.
