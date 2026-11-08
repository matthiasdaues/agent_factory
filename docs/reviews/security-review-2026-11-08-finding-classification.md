---
type: security-review
title: Security review of finding-classification
date: 2026-11-08
status: pass
reviewer: qa-agent
findings_filed: 0
branch: feature/finding-classification
branch_base: 2e4cd6fb975db9b1bffbfab56696284ebbe66c68
branch_head: 107bd1dee469710ef3eac740bdfbfd56d55e2520
---

# Security review of finding-classification

## Result

The review filed no `SEC` finding. The guard is a check against an agent's ordinary next step, not a boundary against a determined attacker, as DEC-42 states. So an agent that hides a field name is the accepted blind spot and not a finding.

The one gate bypass that an ordinary call reaches is the Pi `edit` tool. It is filed once, as [BUG-0123](../findings/BUG-0123.md), and not again here.

## Scope

The review covered the attack surface that the QA brief names: `finding-lint`, `guard-human-fields`, the Pi, Codex, Copilot, and OpenCode registrations, the stop in `dispatch` and `premerge-check`, and `init-factory` as it installs the hook.

| OWASP category                        | Result for this diff                                                                                                                                                                                                                                  |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A01 Broken Access Control             | The human fields are the access rule of this feature. The only reachable gap is BUG-0123. The `artifact` path cannot read outside the repository: the values `../../../../../../etc/passwd:1` and `/etc/passwd:1` ended in the "cannot be read" case. |
| A02 Cryptographic Failures            | The diff holds no cryptography and no secret.                                                                                                                                                                                                         |
| A03 Injection                         | Every git call passes a list of arguments, without a shell. The artifact path stands after `--` or inside `<rev>:<path>`. The value `--output=/tmp/x:1` wrote no file. The Pi and OpenCode entries start the guard without a shell.                   |
| A04 Insecure Design                   | The in-use check sets a lower bound by design, and BR-088 records that an unreadable range passes.                                                                                                                                                    |
| A05 Security Misconfiguration         | The installer links the guard with its executable mode. Pi and OpenCode block a call when the script is missing.                                                                                                                                      |
| A06 Vulnerable Components             | `finding-lint` and the guard use the Python standard library only. The diff adds no dependency.                                                                                                                                                       |
| A07 Identification and Authentication | The diff holds no authentication.                                                                                                                                                                                                                     |
| A08 Software and Data Integrity       | `finding-lint` loads `schema-validate` from its own folder. Changing that folder needs the write access that the attack would gain.                                                                                                                   |
| A09 Logging and Monitoring            | The refusal messages name the file and the field. The stop notice goes to standard output, as the contract says.                                                                                                                                      |
| A10 Server-Side Request Forgery       | The diff makes no network request.                                                                                                                                                                                                                    |

## Not checked

The review did not read `docs/arc42/` for the trust boundaries, because ADR-0035 and BR-092 define the boundary of the guard. No real session of Codex, Copilot CLI, or OpenCode ran (FC-QG23, FC-QG24).

## Findings

No finding of this review reaches the bug bar.
