# Fagan Review Report — 2026-07-22

## Scope

- Branch: `qa/token-usage-capture`, complete feature range
  `af81d0a0cf724570ae20e8af190f820c8c35b390..8bfaf279e74c6fb7d8c9df9d3e0d95ad7cbdc3ca`.
- All 47 changed files were inspected: usage records and persistence, all four
  CLI normalizers and lifecycle adapters, installer/remover behavior, Pi
  invocation extensions, seven changed test modules, architecture/ADR/proposal,
  reconciliation evidence, guide, and backlog stories.
- Compliance references: ST-0042 through ST-0044, ADR-0007, the token-usage
  proposal, UC-08, UC-10, and repository conventions.

## Finding table

| Finding                                                                                                                                                                      | Artifact                                                                          | Category   | Severity |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ---------- | -------- |
| Pi capture registration is not atomic with the removal fence; use one shared filesystem exclusion protocol and cover the late-registration interleaving.                     | `factory/config/extensions/pi-usage.ts:122`; `factory/scripts/remove-factory:356` | Defect     | Major    |
| Concurrent captures for one session can allocate the same record ID and overwrite transcript evidence; make allocation inter-process safe and transcript creation exclusive. | `factory/scripts/usage-capture:965`                                               | Defect     | Major    |
| Copilot child attribution does not carry parent correlation where the native payload permits it; map a native parent identifier or document the unavailable relationship.    | `factory/config/hooks/capture-copilot-usage.sh:5`                                 | Suggestion | Minor    |
| Persisted normalized text uses a `.jsonl` suffix despite no longer being an event stream; use an accurate suffix or explicitly document the representation.                  | `factory/scripts/usage-capture:281`                                               | Suggestion | Minor    |

Defects are filed as `FAGAN-0002` and `FAGAN-0003`.

## Five focus areas

**Correctness.** The four normalizers implement the documented conservation
rules and the installed-path tests cover ordinary root/child behavior, native
events, trust activation, repeated Copilot snapshots, and Pi teardown. The two
Major defects above remain at concurrency seams: removal registration and
same-session ID allocation.

**Clean Architecture.** CLI event shapes remain behind per-CLI adapters. The
fixed tokenizer, canonical record, and logging adapter remain shared, and
native hooks remain the sole capture owners. No dependency-direction violation
was found.

**SOLID.** The normalizer and logging protocols preserve open extension seams
without speculative implementations. No consequential SOLID violation was
found.

**Maintainability.** Tests are broad and use installed consumer-project seams,
but the concurrency suites omit the two exact interleavings in the filed
findings. Comments claiming collision-free parallel operation overstate the
guarantee because append atomicity does not make ID allocation atomic.

**Consistency.** Installation and removal generally follow manifest ownership,
merge-safe hook configuration, idempotency, and best-effort capture conventions.
The two Minor suggestions record attribution and representation inconsistencies
that do not independently block this review.

## YAGNI check

The normalizer registry, logging protocol, and Pi lifecycle fence all serve
current supported paths. No unused abstraction or speculative implementation
was found. The persistence race demonstrates that the lifecycle protocol needs
one stronger atomic boundary, not another layer of generality.

## Done-check

- [x] Every changed file inspected against all five focus areas
- [x] Findings categorized and actionable
- [x] Specification and acceptance criteria explicitly checked
- [x] YAGNI checked
- [ ] Review passes: two Major defects remain open
