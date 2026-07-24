# Final Security Review Report — 2026-07-22

## Scope and trust boundaries

- Branch: `qa/token-usage-final`, complete feature range
  `af81d0a0cf724570ae20e8af190f820c8c35b390..328e46d9b43b0896f78719bd2a12d8b5bf3f0456`.
- All changed files were reevaluated against OWASP A01 through A10.
- Focused tests covered hostile identifiers, traversal, symlink and hard-link
  attacks, exact local permissions, transcript omission, poisoned tooling,
  offline provisioning failure, dependency hashes, and runtime network
  isolation. The targeted security set passed 45 tests.

## Finding table

| Finding                                                    | Artifact | Category | Severity |
| ---------------------------------------------------------- | -------- | -------- | -------- |
| None — no new realistic Medium-or-higher security finding. | —        | —        | —        |

No new `SEC-*` finding was filed.

## Prior finding verification

- **SEC-0001 — resolved:** opaque identifiers are mapped to bounded filesystem
  keys; storage paths enforce containment and reject symlinked or hard-linked
  targets; transcript creation is exclusive and no-follow.
- **SEC-0002 — resolved:** directories and files use exact `0700`/`0600` modes
  independent of umask. Safe repair avoids links. `omit` retains normalized and
  reported totals without transcript content and invalid/unsupported settings
  fail closed.
- **SEC-0003 — resolved:** all four hook paths invoke a package-manager-free
  runtime. Initialization provisions exact hash-verified requirements with
  builds and Python downloads disabled; lifecycle hooks remain inactive when
  provisioning cannot complete.

## OWASP coverage

- **A01:** identifier mapping, canonical containment, link rejection, and
  exclusive creation reverified.
- **A02:** owner-only permissions and explicit full/omit retention reverified.
- **A03:** subprocess calls use argument arrays; shell hook values remain quoted.
- **A04:** storage and runtime provisioning fail closed without affecting runs.
- **A05:** unsafe storage/config/runtime paths are rejected.
- **A06:** the runtime dependency set is exact and hash verified.
- **A07:** no authentication surface is introduced by local usage capture.
- **A08:** requirements and artifacts are integrity constrained at provisioning.
- **A09:** capture errors do not log transcript contents; the cleanup diagnostic
  gap is tracked as correctness finding `FAGAN-0004`.
- **A10:** installed lifecycle runtime performs no package resolution or
  attacker-selected network request.

## Conclusion

Security review passes. The remaining detached-worker cleanup defect is a
correctness and test-determinism blocker, not a new Medium-or-higher security
finding.
