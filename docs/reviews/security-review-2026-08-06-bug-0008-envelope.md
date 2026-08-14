---
title: Security Review — BUG-0008 envelope recovery + branch diff
review: security-review
branch: bug/run-agent-envelope-recovery
tip: 477518d3fecae58b3249393c52abf0397318df74
merge-base: 04256d941ecba2245e01db4d2a3c42d1812cbee9
date: 2026-08-06
reviewer: qa-agent
---

# Security Review — BUG-0008 envelope recovery + branch diff

## Scope

Realistic attack vectors only, across the diff `04256d9…HEAD`. Attack surface:
the `run_agent` child-result envelope parser and git disclosure
(`factory/config/extensions/run-agent.ts`), `dispatch-wave.ts`, `trigger`,
`init-factory` (pre-push hook install + project identity), `update-factory`,
`handoff-lint`, and `orchestrator/src/agent_factory_orchestrator/cli.py`.

## OWASP Top 10 — categories considered

- **A01 Broken Access Control.** `run_agent` spawns `pi -a` (project trust per
  spawn) — intended (BR-031); the child is bound by the git-safety guardrail
  (BR-033). No new access control is introduced. N/A.
- **A03 Injection.** Every changed production script invokes subprocesses with
  list argv — no `shell=True`, no `os.system`, no `eval`, no `yaml.load` (grep
  across all changed `.py/.ts/.mjs` confirmed; the only `shell=True` is in a
  *test*, `test_init_factory_codex.py:185`, over the repo-constant
  `CODEX_GUARDRAIL_HOOK_COMMAND`). `run-agent.ts` git calls use list argv with a
  `--` option separator before the child-supplied path (`git ls-files --error-unmatch -- -- <path>`). **Path traversal in
  `validateChildResultArtifacts` is robust**: it rejects absolute paths,
  backslashes, `../` prefixes, `.` , and any path where
  `posix.normalize(path) !== path`, then requires the file to exist, be a
  regular file, and be `git ls-files --error-unmatch`-tracked. No injection.
- **A04 Insecure Design.** The BUG-0008 disclosure is additive transport
  metadata on error results; it does not relax the four-field envelope (BR-040)
  or expose child reasoning. Disclosed `freshChildCommits` are short oneline
  git log lines (≤10), attacker-controlled only by a child that can already
  commit to the repo. No new trust boundary.
- **A05 Security Misconfiguration.** ST-0073 pre-push `entry: factory/scripts/run-tests --full` with `pass_filenames: false` and `language: system` — fixed string, no filename interpolation, no shell metachar surface. `init-factory` installs both hook types with an explicit, asserted argv.
- **A06 Vulnerable Components.** ADR-0004 pins Pi 0.80.8; the local env has
  0.84.0. This is an environment/CI pinning concern, not a branch defect.
- **A07 Auth Failures.** N/A — no auth in scope.
- **A08 Data Integrity Failures.** `gitLocalHead`/`childCommitsSince` use a
  12-char short SHA captured before dispatch; `git log <short>..HEAD` resolves
  unambiguously. Best-effort only; failures yield `null`, never a hard error.
- **A09 Logging Failures.** `run_agent` retains only bounded stderr tail
  (16 KiB) and parser state; the complete raw stream goes to a protected
  capture file with `0o600`. No secrets logged.
- **A10 SSRF.** N/A.

## Findings

None at Medium or above. Two informational Lows noted (not filed):

- **[Low] Pathological child output can make the balanced-brace scan O(n²).**
  `extractEnvelopeObject`'s fallback scan is O(n²) worst case (a nested loop
  over every `{`). The whole-message and fenced candidates are tried first, so
  the scan runs only when those fail; the JSONL line cap (`MAX_JSONL_LINE_BYTES`
  = 4 MiB) bounds input. A child emitting a large non-JSON dump with many braces
  could cause a multi-second parse. The child is a factory agent (semi-trusted,
  guardrail-bound), not an external attacker. Mitigation: cap the scan input or
  short-circuit when a four-field record is found.
- **[Low, pre-existing] Model-controlled git ref args in `dispatch-wave.ts`.**
  `item.branch` / `base` / `scope` (model-provided tool params) reach
  `git merge --no-ff <branch>` and `premerge-check --scope <s>` as list argv —
  no shell — but a branch name beginning with `-` could be misread as a git
  option. This predates BUG-0008 and is not changed by this branch. Consider
  `--` separation or ref-shape validation.

## Verification Evidence

- `grep -nE "shell=True|os.system|eval\(|__import__|yaml.load\(|subprocess.call\(|Popen\("` across all changed scripts: only test-side hits; no production `shell=True`.
- `run-agent.ts` path validation reviewed line-by-line (`validateChildResultArtifacts`); probe confirms rejected paths surface as errors.
- `trigger` uses a hardcoded tool allowlist (never `--dangerously-skip-permissions`/`--allow-all-tools`) and `check=False` to propagate return codes — security-positive.
