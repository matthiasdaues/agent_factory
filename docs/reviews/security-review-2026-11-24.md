---
type: security-review
title: Security review of feature/crap-gate-self-host
date: 2026-11-24
status: defects
reviewer: qa-agent
findings_filed: 1
story:
run: feature/crap-gate-self-host
branch: feature/crap-gate-self-host
branch_base: 634135fefd07cbbadd33acdfbc4e17de1e771706
branch_head: 94079fc1766d28a7bd11f3507a63771df71a880e
---

# Security review of feature/crap-gate-self-host

## Verdict

The feature has one blocking finding, SEC-0013. Every run of the CRAP gate on this repository installs ESLint's dependencies from npm without a lock and runs their code. The finding is `major` and goes back to the Implementation Agent. No other OWASP category yields a finding with a plausible attack path.

## Scope

The review covers `git diff dev...feature/crap-gate-self-host` from `634135fe` to `94079fc1`, without the 1.14 usage work from `dev`. It read DEC-75 and DEC-84 to DEC-87, BR-128 to BR-131, and the trust boundaries of the gate in the header of `crap-score`. The trusted gate source takes the threshold, the `files` patterns and the `exclude` lists from `refs/heads/dev`. `command` and `ready` come from the story head (DEC-75).

## Questions of the caller

**Can a story make the gate judge it by its own values through `GATE_CHANGED_FILES`?** No. `crap-score` builds the list from its own diff of the merge base of `--base` and `HEAD`, with the same `parse_diff` that selects the judged rows. It then filters the rows by the trusted patterns and judges the changed functions itself (BR-131). A measure that leaves out a changed file only drops rows, as any measure could before this feature. A path with a line break exits 2.

**Can it do so through `SELECT_COMMAND`?** Only by changing the measuring code at the story head. `SELECT_COMMAND` is a constant of `scripts/crap-measure-python`, and the gate runs `scripts/crap-measure-python` and `tests/select_tests.py` from the story head. DEC-75 accepts that and leaves the guard to the code review and the scope check. A story that needs that change already controls `command`, so the attack gains nothing beyond DEC-75, and the bug bar records no finding. The Fagan report keeps this as note N-4. Without such a change, `select_tests.py` can only run fewer tests than `TEST_COMMAND`, and fewer tests only lower the coverage (DEC-84). The bug hunt checked each path where the selector runs no test: the measure exits 1, so the gate fails closed.

**Is `npx --yes eslint@<pinned>` a supply-chain or offline risk?** It is both. The supply-chain risk is SEC-0013. The offline cost is a runtime matter and is filed by the bug hunt as BUG-0148.

**Can the update path lose usage data or switch capture off?** No path found. `update-factory` copies only `runtime/` aside, and never moves the usage records. The copy keeps the mode `0700` of the runtime. `_restore_runtime` checks the copy before it moves anything and never follows a symlink. `init-factory` keeps the marker until a new runtime is complete.

## OWASP categories

| Category                                       | Result                                                                                                                                                                                                                                                     |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A01 Broken Access Control                      | The trusted gate source is unchanged. `GATE_CHANGED_FILES` gives a story no new control over threshold or patterns. No finding.                                                                                                                            |
| A02 Cryptographic Failures                     | The feature handles no secret. `init-factory` keeps `--require-hashes` for the usage runtime. No finding.                                                                                                                                                  |
| A03 Injection                                  | `GATE_SCOPE` and `GATE_CHANGED_FILES` are environment values, never parsed by a shell. The changed paths reach `select_tests.py` as an argument list. An option-shaped file name changes only the selection and fails closed (Fagan note N-1). No finding. |
| A04 Insecure Design                            | The narrow scope keeps the rule that the gate may fail wrongly but never pass wrongly. No finding.                                                                                                                                                         |
| A05 Security Misconfiguration                  | The runtime copy lies in `.agent-factory/`, which the Factory's `.gitignore` block ignores, and keeps the mode of the runtime. No finding.                                                                                                                 |
| A06 Vulnerable and Outdated Components         | `eslint@10.14.0` is pinned, but its dependency tree is not. Filed under A08 as SEC-0013, because the gap is the missing integrity check.                                                                                                                   |
| A07 Identification and Authentication Failures | No authentication code in the diff. No finding.                                                                                                                                                                                                            |
| A08 Software and Data Integrity Failures       | SEC-0013: `npx --yes` installs and runs the newest matching releases of ESLint's 30 dependency ranges, with install scripts on, and no lock.                                                                                                               |
| A09 Security Logging and Monitoring Failures   | A failed runtime build now names its cause in the init report (IMPL-0114). No finding.                                                                                                                                                                     |
| A10 Server-Side Request Forgery                | No server code. No finding.                                                                                                                                                                                                                                |

## Findings

| Finding                                                                                                                                                                                                                                                                                                                                                           | Artifact                                  | Category | Severity | Filed as                                         |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- | -------- | -------- | ------------------------------------------------ |
| Every gate run starts `npx --yes eslint@10.14.0`, which installs the newest releases that match ESLint's dependency ranges, runs their install scripts, and runs their code with the developer's privileges. Install ESLint from a committed `package-lock.json` with `npm ci --ignore-scripts` at a setup step, and run the local binary without network access. | `scripts/crap-measure-typescript:285-291` | Defect   | major    | [SEC-0013](../findings/SEC-0013.md), rating High |

## Next step

The Implementation Agent fixes SEC-0013 on the feature branch and resubmits the feature for QA.
