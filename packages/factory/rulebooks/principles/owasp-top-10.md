---
title: OWASP Top 10
version: 1.0.0
---

# OWASP Top 10

The Open Web Application Security Project (OWASP) Top 10 is the standard
awareness document for web application security risks.

## Categories (2021 edition)

| ID  | Category                                   |
| --- | ------------------------------------------ |
| A01 | Broken Access Control                      |
| A02 | Cryptographic Failures                     |
| A03 | Injection                                  |
| A04 | Insecure Design                            |
| A05 | Security Misconfiguration                  |
| A06 | Vulnerable and Outdated Components         |
| A07 | Identification and Authentication Failures |
| A08 | Software and Data Integrity Failures       |
| A09 | Security Logging and Monitoring Failures   |
| A10 | Server-Side Request Forgery (SSRF)         |

## Application in security review

For each finding, identify the OWASP category, describe the attack
vector, and provide a concrete remediation. The OWASP category is the type
of the finding. Rate the finding with the bug bar in
[finding-classification.md § Class: security](../conventions/finding-classification.md#class-security).
Report only findings with a plausible attack vector in the specific
codebase under review.

## Referenced from

- [finding-classification.md § Class: security](../conventions/finding-classification.md#class-security)
