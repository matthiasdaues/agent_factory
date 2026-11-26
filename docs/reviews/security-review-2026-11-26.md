---
type: security-review
title: Security review of feature/handbooks
date: 2026-11-26
status: pass
reviewer: qa-agent
findings_filed: 0
story:
run: feature/handbooks
branch: feature/handbooks
branch_base: 43964dac1d1cb6bd933c1f459ead2b39b949c33c
branch_head: f1c6a265def3184eb7c938631af3783b6a85f14d
---

# Security review of feature/handbooks

## Verdict

The feature has no finding with a plausible attack path. Three notes stay in this report. The scripts run no subprocess, parse YAML with `safe_load`, and write only the page lists of the two fixed handbook roots.

## Scope

The review covers `git diff 43964dac..f1c6a265` for `handbook-index`, `handbook-lint`, `_link_rewrite.py`, the hook of `.pre-commit-config.yaml`, and the install path of the handbook into `.agent-factory/factory/docs/handbook/`. The trust boundary is the working tree of a contributor: a pull request can add or change any page, and the hook then reads it. The review ran the scripts against scratch handbooks under /tmp.

## Questions of the caller

**Can a page make a script read or write outside the two roots?** No. The roots are constants. `_linked_part` refuses a symlink in any part of a root path, and the readers refuse a symlink entry before they read. `run` writes only the `index.md` paths that the walk produced, and skips a symlink. A swap between the check and the write needs a second process with write access to the tree, which already controls the repository.

**Can page metadata forge a marker or inject Markdown into a list?** A title is escaped for the backslash, `[`, and `]`, and `<!--` is encoded, so a title cannot end or restart the generated region. A description is raw Markdown by design. An author of a page can already write any Markdown in the page, so a description gains nothing.

**Does an installed project run the new code automatically?** No. `init-factory` writes no handbook hook (BR-148, FH-CT-58). The scripts ship but run only when a person calls them.

## OWASP categories

| Category                                       | Result                                                                                                                                                         |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A01 Broken Access Control                      | Reads and writes stay inside two fixed roots, with symlinks refused. No finding.                                                                               |
| A02 Cryptographic Failures                     | No secret or cryptography. No finding.                                                                                                                         |
| A03 Injection                                  | No shell, no subprocess, no `eval`. File names reach output through `quote`. A page title cannot form a marker. A description is trusted Markdown. No finding. |
| A04 Insecure Design                            | A refusal writes nothing, and a page list with a broken input is skipped. No finding.                                                                          |
| A05 Security Misconfiguration                  | The hook runs the script with `always_run` and no file list. No finding.                                                                                       |
| A06 Vulnerable and Outdated Components         | N-1 below. No finding, because the exposure existed before the feature.                                                                                        |
| A07 Identification and Authentication Failures | No authentication code. No finding.                                                                                                                            |
| A08 Software and Data Integrity Failures       | Same as A06. The generated text is checked by `--check` against a fresh computation. No finding.                                                               |
| A09 Security Logging and Monitoring Failures   | Failure lines name the path and the field. A path with control characters prints raw (N-3). No finding.                                                        |
| A10 Server-Side Request Forgery                | No network code. No finding.                                                                                                                                   |

## Findings

None.

## Notes

- N-1: `handbook-index` and `handbook-lint` declare `pyyaml`, `mdformat`, and `mdformat-gfm` without a version. A compromised release would run with the contributor's privileges on every commit (OWASP A06, CWE-1104). The same packages already run unpinned in the `mdformat` hook of the same file and in three other scripts, so the feature adds no new exposure. The attack also needs a second breach, an upstream release, and the hook exists only in the source repository. A pin with a lock for all hook scripts would be a separate change.
- N-2: A page with 200,000 nested brackets in its frontmatter makes `yaml.safe_load` raise `RecursionError`, which `parse_page` does not catch. The script prints a traceback and exits 1. The attacker needs a pull request, and the commit is refused, so the gain is nothing (effect `hardening`). Catching `RecursionError` beside `yaml.YAMLError` would name the page.
- N-3: A page file name with a terminal escape sequence prints raw in a failure line. Only a contributor can create the file, so the gain is nothing.

## Next step

No change is needed for this review. The Implementation Agent continues with the bug-hunt report.
