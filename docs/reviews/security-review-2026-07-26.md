# Security Review Report — Research Survey — 2026-07-26

## Scope and trust boundaries

- Branch: `dev`.
- Implementation range:
  `3cd1f35e3cb884f7a99fabba06a9659f14652333..ade350086158f6422626f2d11bcd4c4c9a59fbc8`.
- QA remediation commits:
  `58ac1a7a45fe2f32509036cf91cb1995de8645f0` and
  `35cd0e71449898683d5e7b91d8fed3f45765c87c`.
- All 28 changed files were evaluated against OWASP A01 through A10.
- Relevant boundaries are local JSON artifact validation, agent consumption of
  recorded source material, CLI-specific dispatch adapters, and installation
  of canonical Markdown contracts into a consumer project.

The change adds schemas, Markdown contracts, generated discovery metadata, and
tests. It adds no network client, credential store, authentication endpoint,
deployment surface, or production file resolver.

## Finding table

| Finding                                                | Artifact | Category | Severity |
| ------------------------------------------------------ | -------- | -------- | -------- |
| None — no realistic Medium-or-higher security finding. | —        | —        | —        |

No `SEC-*` finding was filed.

## OWASP coverage

- **A01 — Broken Access Control:** no authorization surface is added. The
  test-only survey resolver originally accepted paths outside its fixture run;
  this undermined acceptance evidence but exposed no production privilege
  boundary. It is resolved as correctness finding `BUG-0001`, including
  traversal, absolute-path, and symlink containment.
- **A02 — Cryptographic Failures:** the change stores no secrets and introduces
  no cryptographic operation or sensitive-data transport.
- **A03 — Injection:** schema-validation subprocesses use argument arrays, not
  shell interpolation. Research strings remain data for agentic review; no new
  command, query, or template execution sink was introduced.
- **A04 — Insecure Design:** survey and falsification use separate artifact and
  role contracts. Falsification independence remains fail-closed; survey source
  access remains a preflight requirement.
- **A05 — Security Misconfiguration:** mode defaults and CLI mappings are
  explicit. Installed-surface tests cover Claude Code, Copilot, Codex, and Pi.
  No new security-sensitive runtime configuration is introduced.
- **A06 — Vulnerable and Outdated Components:** no runtime dependency was added.
  Pytest and Ruff were QA tooling only.
- **A07 — Identification and Authentication Failures:** no identity or
  authentication implementation is changed. Independent agent identity remains
  a falsification workflow precondition, not an authentication mechanism.
- **A08 — Software and Data Integrity Failures:** source records retain
  provenance, source family, precise evidence location, method, and limitations.
  Reports require source-record references and semantic support checks. The
  installer discovery surface is validated from canonical Factory artifacts.
- **A09 — Security Logging and Monitoring Failures:** the feature adds no
  operational logging path and does not place source contents or credentials in
  diagnostics.
- **A10 — Server-Side Request Forgery:** source access is a declared capability,
  but this change implements no URL fetcher or server-side network request. No
  attacker-controlled request target exists in the reviewed code.

## Verification

- Source-reference containment regression: 3 passed after a 3-case red
  reproduction.
- Complete research regression: 170 passed.
- Full orchestrator regression: 467 passed with warnings as errors.
- Final changed-surface hunt cycle: 48 passed; zero new bugs.
- Ruff, schema-facing acceptance tests, installed-surface checks, and catalog
  validation passed.

## Conclusion

Security review passes. No realistic OWASP Medium-or-higher defect remains.
