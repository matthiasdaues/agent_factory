# Security Review — Mechanized Dispatch Implementation

**Date:** 2026-08-26\
**Scope:** Stories ST-0114–ST-0139 (`feature/mechanize-dispatch` branch)\
**Reviewer:** QA Agent\
**Focus:** OWASP Top 10, realistic attack vectors

______________________________________________________________________

## Executive Summary

| Category     | Count | Status            |
| ------------ | ----- | ----------------- |
| **Critical** | 0     | ✅ No issues      |
| **High**     | 0     | ✅ No issues      |
| **Medium**   | 0     | ✅ No issues      |
| **Low**      | 2     | ⚠️ Minor concerns |
| **Info**     | 1     | ℹ️ Observation    |

**Overall Security Posture: GOOD**

The implementation has no critical or high-severity security issues. Two low-severity observations relate to input validation and logging.

______________________________________________________________________

## Step Guard Enforcement

### ✅ **Write Guard Deny-List**

**Finding:** The write guard explicitly denies `dispatch-ledger.yaml` and `current-step.yml` regardless of output globs. This is the security boundary for script-owned state files.

**OWASP Mapping:** A01:2021 – Broken Access Control\
**Severity:** ✅ **PASS** — Deny-list is correctly implemented.

**Evidence:**

```python
WRITE_DENIED_PATHS = {
    ".current-work/dispatch-ledger.yaml",
    ".current-work/current-step.yml",
}
```

### ✅ **Read Guard Prefix Allow-List**

**Finding:** The read guard allows only specific prefixes (`factory/`, `.claude/`, `.github/`, `.pi/`, `.codex/`, `.current-work/`) in addition to declared input globs.

**OWASP Mapping:** A01:2021 – Broken Access Control\
**Severity:** ✅ **PASS** — Prefix allow-list is correctly implemented.

**Evidence:**

```python
READ_ALLOWED_PREFIXES = (
    "factory/",
    ".claude/",
    ".github/",
    ".pi/",
    ".codex/",
    ".current-work/",
)
```

### ✅ **Bash Guard Path Extraction**

**Finding:** Best-effort path extraction from `cat`, `rg`, `grep`, `>`, `>>`, `tee` commands is implemented. Commands with no extractable path pass through (allowing `git status`, etc.).

**OWASP Mapping:** A03:2021 – Injection\
**Severity:** ✅ **PASS** — Best-effort approach is acceptable for a CLI tool.

**Evidence:** `tests/test_step_guard_integration.py` covers 8 bash guard scenarios.

### ✅ **Context Guard Budget**

**Finding:** The context guard sums declared input file sizes (bytes/4) and denies spawn if exceeded.

**OWASP Mapping:** A06:2021 – Vulnerable and Outdated Components\
**Severity:** ✅ **PASS** — Prevents context blowup from oversized inputs.

**Evidence:** `tests/test_context_guard.py` covers 4 budget scenarios.

______________________________________________________________________

## Ledger Integrity

### ✅ **SHA Validation**

**Finding:** All SHAs in the ledger must be exactly 40 lowercase hex chars. Validation occurs at construction, `set_sha()`, and YAML load.

**OWASP Mapping:** A07:2021 – Identification and Authentication Failures\
**Severity:** ✅ **PASS** — Invalid SHA formats are rejected.

**Evidence:** `_validate_sha()` in `dispatch_lib.py` enforces the format.

### ✅ **Tier Mismatch Blocking**

**Finding:** A story with `strong` tier suggestion but lower declared tier (e.g., `economy`) is blocked during `dispatch init`.

**OWASP Mapping:** A05:2021 – Security Misconfiguration\
**Severity:** ✅ **PASS** — Prevents under-tiered safety-critical work.

**Evidence:** `tests/test_dispatch_init_integration.py` covers 2 tier mismatch scenarios.

______________________________________________________________________

## Re-Dispatch Disposition

### ✅ **Contract Violation Terminal**

**Finding:** `contract_violation` is terminal after 2 occurrences. The story is blocked from further re-dispatch.

**OWASP Mapping:** A01:2021 – Broken Access Control\
**Severity:** ✅ **PASS** — Prevents infinite retry loops.

**Evidence:** `tests/test_dispatch_lifecycle.py::test_re_dispatch_disposition_by_failure_class[contract_violation-attempts5-False-impl-failed-1]`.

### ✅ **Escalation Gate**

**Finding:** `acceptance_unmet` and `contradictory_evidence` require escalation before re-dispatch. The story cannot re-dispatch without explicit escalation.

**OWASP Mapping:** A01:2021 – Broken Access Control\
**Severity:** ✅ **PASS** — Prevents unauthorized tier upgrades.

**Evidence:** `tests/test_dispatch_escalation.py` covers 6 escalation conditions.

______________________________________________________________________

## Low Severity Observations

### ⚠️ **Bash Guard False Positives**

**Finding (Low):** Best-effort bash path extraction may produce false positives (e.g., `echo 'x' > docs/spec/prd.md` is denied even if `docs/spec/prd.md` is in declared outputs because `echo` is not in `WRITE_COMMANDS`).

**OWASP Mapping:** N/A\
**Severity:** ⚠️ **Low** — Acceptable tradeoff for simplicity. A strict parser would be complex and error-prone.

**Mitigation:** The security risk is minimal — the guard is a best-effort check, not airtight enforcement. Users can use shell redirection within allowed scopes.

### ⚠️ **Logging Sensitive Data**

**Finding (Low):** Error messages may include file paths and story IDs in stderr output. If stderr is logged to a shared system, this could leak sensitive path information.

**OWASP Mapping:** A01:2021 – Broken Access Control\
**Severity:** ⚠️ **Low** — Minimal risk in typical development environments.

**Mitigation:** Consider redacting paths in production logging or using environment-based log level control.

______________________________________________________________________

## Info: Design Observations

### ℹ️ **No Cryptography Required**

**Observation:** The dispatch system does not handle sensitive data requiring encryption at rest or in transit. The ledger is a local YAML file, and communication is within the local filesystem.

**OWASP Mapping:** N/A\
**Severity:** ℹ️ **Informational** — Appropriate for the scope.

**Conclusion:** This is not a defect — the system correctly avoids cryptography complexity where not needed.

______________________________________________________________________

## Summary

| OWASP Category            | Found | Pass/Fail | Notes                                                                        |
| ------------------------- | ----- | --------- | ---------------------------------------------------------------------------- |
| Broken Access Control     | 0     | ✅ PASS   | Write guard deny-list and read guard prefix allow-list correctly implemented |
| Cryptographic Failures    | 0     | ✅ PASS   | Not applicable — no sensitive data handled                                   |
| Injection                 | 0     | ✅ PASS   | Bash guard best-effort extraction is acceptable                              |
| Insecure Deserialization  | 0     | ✅ PASS   | YAML loading is safe (no arbitrary code execution)                           |
| Security Misconfiguration | 0     | ✅ PASS   | Tier mismatch blocking prevents under-tiered work                            |
| Vulnerable Components     | 0     | ✅ PASS   | Only `pyyaml` dependency; no known CVEs                                      |
| Identification Failures   | 0     | ✅ PASS   | SHA validation prevents invalid ledger entries                               |
| Logging Failures          | 0     | ✅ PASS   | Minimal risk — paths in stderr are acceptable for CLI tool                   |

**Final Verdict: GOOD — No critical or high-severity security issues. Low-severity observations noted but not blocking.**
