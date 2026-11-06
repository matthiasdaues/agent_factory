---
type: security-review
title: Security review of the counter-ids implementation
date: 2026-11-06
status: defects
reviewer: qa-agent
findings_filed: 1
story: counter-ids
branch: feature/counter-ids
branch_base: 5e2c9b52c9353aa45a07230826fe6a60bbfaae8e
branch_head: d0a78a5c40327c1f7e4c9a204ab5e766a7e0c44b
---

# Security review of the counter-ids implementation

## Result

The review found one blocking finding. `next-id` and `init-factory` print a
password or token that sits in the remote URL (SEC-0007, Medium, `major`). The
lease, the throwaway repository, and the parser of the claim commit hold. Next,
the Implementation Agent removes the credential from every message that names
the remote, and the QA agent checks the fix.

## Scope

The review covers `git diff dev...feature/counter-ids` at `d0a78a5c`:
`packages/factory/scripts/next-id`, `check_counter` in
`packages/factory/scripts/init-factory`, and the tests that run them. It reads
the trust boundaries from QS-21 in `docs/arc42/10_quality_requirements.md` and
from ADR-0032. Three inputs cross a boundary:

- the commit message that the remote returns for `refs/ids/counters`
- the remote URL from `--remote` or from `git remote get-url origin`
- the user's git setup: credentials, ssh command, and global config

The classification follows the bug bar of `finding-classification.md` §
Class: security, as the brief requires. Nothing on `dev` runs `next-id` yet, so
no finding is `critical`. Each attack path below was reproduced with
`next-id` from the branch head, a temporary `HOME`, and local bare
repositories or a local HTTP server.

## Findings

| ID                                  | OWASP | Rating | Severity | Title                                                                    |
| ----------------------------------- | ----- | ------ | -------- | ------------------------------------------------------------------------ |
| [SEC-0007](../findings/SEC-0007.md) | A09   | Medium | major    | `next-id` and `init-factory` print the password or token of a remote URL |

## Question for the author

**A claim can open an askpass dialog.** BR-076 says that a claim runs every git
call without a prompt. `next-id` sets `GIT_TERMINAL_PROMPT=0`, but git still
calls the program in `GIT_ASKPASS` or `core.askPass`. A run against an HTTP
server that answers `401` called a test askpass script twice, once for the user
name and once for the password. VS Code sets `GIT_ASKPASS` in its terminal, so
there a claim can open a credential dialog and wait up to 30 seconds. Clearing
`GIT_ASKPASS` would stop the dialog, but it would also break a CI job that
hands its token to git through an askpass script. The author decides which
case wins. The question needs an entry in `docs/spec/work/todo.md`, which this
run does not own.

## Notes

These observations need no change. They stay in this report only.

- **A03, option injection through `--remote`.** `next-id` passes the URL to
  `git fetch` and `git push` as an argument without `--` in front. So
  `next-id ST "--remote=--upload-pack=<command>"` runs `<command>`. The run
  confirmed this. The attacker must make the user or an agent run that command
  line, and that person could run `<command>` directly. The permission system
  sees the same command text either way, and no allowlist names `next-id`. So
  the attacker gains nothing. A `--` before the URL would close the path as a
  hardening step.
- **A03, terminal control characters from the remote.** A claim commit with a
  line that is not a number ends the claim. The message quotes that line raw,
  including escape sequences. Only a user with write access to the remote can
  write the claim commit, so the attacker already holds more than the escape
  sequence gives.
- **A08, the claim commit from the remote.** `parse_message` accepts only ASCII
  digits as values and writes every other key back unchanged. The new message
  goes to `git commit-tree` on standard input, never into a command line. A
  writer of the ref can set any number, as ADR-0032 records, and that writer
  already has push access.
- **A01, who moves the ref.** The code pushes only `refs/ids/counters`, always
  with a lease. A seed uses the create-only lease. This matches ADR-0032 and
  QS-21. The hook gap of T-0017 is known.
- **A05, the user's global git config.** The throwaway repository reads the
  global config, as DEC-23 intends. A global `commit.gpgSign=true` does not
  reach `git commit-tree`. The run checked this with a signing program that
  logs its calls, and nothing called it.
- **A07, credentials at rest.** `next-id` stores no credential. The throwaway
  directory comes from `tempfile.TemporaryDirectory`, which creates it with
  mode `0700`, and is deleted at exit.
- **Other categories.** A02: the token comes from `secrets.token_hex` and only
  makes each claim commit unique, so it needs no secrecy. A06: `next-id` uses
  the standard library only. A10: `next-id` contacts no host except the remote
  that the user names, through git's own transport. A04 is covered by the
  lease and the throwaway repository above.
