---
type: security-review
title: Security review of the BUG-0115 fix
date: 2026-11-06
status: pass
reviewer: qa-agent
findings_filed: 0
story: BUG-0115
branch: feature/bug-0115-dispatch-ledger
branch_base: 279f01a8fc60d7daff9a092a688f2cda6db6a439
branch_head: 80bdb99a1f2edac6ea829393cd619797d772d211
---

# Security review of the BUG-0115 fix

`dispatch` is a local CLI run by the operator. The trust boundary is the
operator's own checkout. The review finds nothing at Medium or higher.

## Notes

- A03 Injection: the SHA passes a `[0-9a-f]{4,40}` full match before it reaches
  `git rev-parse`. It cannot start with `-`, so it cannot act as an option. The
  script calls git with an argument list, not a shell.
- A01 Broken Access Control: the branch name builds a path under
  `.current-work/`. Git refuses `..` components in a branch name, and the result
  must equal a ledger the glob found, so no path escapes.
- A09 Logging: the new error prints ledger paths on stderr. This matches the
  accepted risk in SEC-0006.
- A04 Insecure Design: an abbreviated SHA can resolve to a hex-named ref. This
  records the wrong commit but gives an attacker nothing. FAGAN-0032 covers it
  as a correctness issue.
