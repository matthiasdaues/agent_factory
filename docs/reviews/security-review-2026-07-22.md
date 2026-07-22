# Security Review Report — 2026-07-22

## Scope and trust boundaries

- Branch: `qa/token-usage-capture`, complete feature range
  `af81d0a0cf724570ae20e8af190f820c8c35b390..8bfaf279e74c6fb7d8c9df9d3e0d95ad7cbdc3ca`.
- All 47 changed files were evaluated against OWASP A01 through A10.
- Trust boundaries include CLI lifecycle JSON entering shell hooks, transcript
  paths and identifiers entering local persistence, Pi subprocess/environment
  propagation, project-root discovery, installed hook trust, package resolution,
  and removal of Factory-owned paths.
- This is local developer tooling, but lifecycle payloads and transcript content
  are not safe filesystem identifiers and transcripts can contain secrets.

## Finding table

| Finding                                                                                                                                                        | Artifact                            | OWASP category                                         | Severity |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------ | -------- |
| Hook-supplied session IDs can traverse outside the usage root; encode IDs and enforce canonical containment with symlink rejection.                            | `factory/scripts/usage-capture:274` | A01 — Broken Access Control                            | High     |
| Full prompts, reasoning, and tool results are stored with group/world-readable file modes; restrict directories/files and define retention/redaction controls. | `factory/scripts/usage-capture:274` | A02 — Cryptographic Failures / Sensitive Data Exposure | Medium   |
| Automatic hooks execute a floating `tiktoken` dependency; pin and integrity-protect the reviewed artifact at a trusted installation boundary.                  | `factory/scripts/usage-capture:4`   | A06 — Vulnerable and Outdated Components               | Medium   |

Filed as `SEC-0001`, `SEC-0002`, and `SEC-0003`.

## OWASP analysis

- **A01:** High finding. Unsanitized identifiers directly select write paths.
- **A02:** Medium finding. Sensitive transcript text lacks restrictive local
  permissions and a retention/redaction contract.
- **A03 — Injection:** no credible command-injection path was found. Shell
  scripts quote values and TypeScript subprocesses use argument arrays.
- **A04 — Insecure Design:** concurrency defects are recorded by the Fagan
  review; no separate security design finding beyond A01/A02 was identified.
- **A05 — Security Misconfiguration:** Codex trust activation is explicitly
  reported and tested; Pi root validation rejects untrusted redirection.
- **A06:** Medium finding. The runtime tokenizer dependency floats.
- **A07 — Identification and Authentication Failures:** no authentication or
  identity-management surface exists in this local capture feature.
- **A08 — Software and Data Integrity Failures:** the package-integrity aspect
  is captured under A06. Hook configuration is Factory-owned or merge-exact.
- **A09 — Security Logging and Monitoring Failures:** best-effort capture
  intentionally avoids affecting runs. No security-event monitoring claim is
  made; plaintext confidentiality is covered by SEC-0002.
- **A10 — Server-Side Request Forgery:** the runtime path makes no outbound
  request except dependency resolution; no attacker-selected URL sink exists.

## Conclusion

Security review does not pass. One High and two Medium findings require
implementation-agent fixes and re-submission before exploratory bug hunting and
final QA.
