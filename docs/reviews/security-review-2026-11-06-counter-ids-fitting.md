---
type: security-review
title: Security review of counter-ids-fitting
date: 2026-11-06
status: pass
reviewer: qa-agent
findings_filed: 0
branch: feature/counter-ids-fitting
branch_base: 432069116cfe2f9dc9099cad3db0d29ebbd184b6
branch_head: 4b3a875d07dcf3c655b513f01a4d9b97df6e46b8
---

# Security review of counter-ids-fitting

## Result

The review found no security finding at `major` or `minor`. No new output path shows a token, and no git call of the claim or the move can prompt or run without the time limit. The move pushes from a throwaway repository. The notes below record four observations that need no change now.

Next, the branch goes back to the Implementation Agent for FAGAN-0033 of the Fagan inspection. That finding is not a security finding.

## Scope

The review covers `git diff dev...feature/counter-ids-fitting` at `4b3a875d`: `next-id` (`--plan-seed`, the local counter, `--move-to-origin`), `check_counter` and `record_counter_seeded` in `init-factory`, `housekeeping-about`, `virgil.md` § Fitting, and `session-menu.md` § Counter check. The trust boundary is the one of counter-ids: an agent runs `next-id` through the User's shell, and the counter lives either on a remote or in the project's own `.git`. The review classifies by the bug bar of `finding-classification.md` § Class: security. It ran every reproduction in a temporary directory, with local bare repositories and made-up tokens only.

## OWASP Top 10

| Category                               | Outcome                                                                                                                                                                                                                                                                                           |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A01 Broken Access Control              | The local counter is a ref in the project's `.git`. Who can write that directory can move the counter with `git update-ref`, without any push. This is the gap that ADR-0032 and T-0017 already describe for the remote counter. Such a writer already holds the capability, so it is no finding. |
| A02 Cryptographic Failures             | No secret is stored. The marker holds the redacted URL.                                                                                                                                                                                                                                           |
| A03 Injection                          | Every git call passes its arguments as a list. `check_counter` puts `--` before the URL. The pairs of the seed command are a prefix from `PREFIXES` and an integer, so a file name on a fetched branch cannot put shell text into the command that VIRGIL runs.                                   |
| A04 Insecure Design                    | The move never puts C back (DEC-16). A hand-written marker makes claims fail and names the text after `moved=`. Nothing uses that text as a URL for git. See the note on the marker's parent.                                                                                                     |
| A05 Security Misconfiguration          | The claim and the move set `GIT_TERMINAL_PROMPT=0`, add `BatchMode=yes` to ssh, and stop every git call after 30 seconds (BR-076, CIFP-C09). The `--seed` command keeps its prompts, as BR-076 states.                                                                                            |
| A06 Vulnerable and Outdated Components | No new dependency. `next-id` uses only the standard library.                                                                                                                                                                                                                                      |
| A07 Identification and Authentication  | Credentials stay with git and its credential helper. No new mode reads or writes them.                                                                                                                                                                                                            |
| A08 Software and Data Integrity        | The marker sets with a lease on C, and the push uses the create-only lease. The tests force the race between a claim and the marker.                                                                                                                                                              |
| A09 Security Logging and Monitoring    | Not applicable to a command-line tool without a log.                                                                                                                                                                                                                                              |
| A10 Server-Side Request Forgery        | The remote comes from `--remote`, the setting, or `origin`. All three are written by the User. git's default `protocol.allow` refuses `ext::`.                                                                                                                                                    |

## Checks the brief asked for

**No token in the clear (BR-077).** Every line of `next-id` passes through `RedactingStream`, including tracebacks and argparse errors. The review traced each new output: the in-use line and the warnings of `--plan-seed`, the success, collision, refusal, and timeout messages of the move, and the `MovedCounter` message. Each shows the URL as `https://***@host/...`. `format_marker` redacts the URL before git stores it, so the `moved=<remote>` line in the project's `.git` never holds a token. A hand-written marker with a token is redacted again when `next-id` prints it. `check_counter` prints only the redacted URL. The move tests run `_assert_no_token` on every failing path.

**No prompt and no hang.** Each git call of the move goes through `_guarded` or `git(..., guarded=True)`. That covers the setting, `ls-remote --get-url`, the read of the local counter, the marker, `update-ref`, the throwaway fetch and push, the second `ls-remote`, and the collision read. `subprocess.run` kills git at the limit and does not wait for git's child processes, so a stuck ssh cannot extend the wait.

**The move pushes from a throwaway repository.** `push_to_origin` fetches the local counter into a new bare repository without a template and pushes C from there. A pre-push hook of the project does not run.

## Notes

These observations need no change now. They stay in this report only.

**The local counter runs the project's receive hooks.** A claim on the local counter pushes into the project's `.git`, and git runs the project's `pre-receive` and `reference-transaction` hooks there. The marker's `update-ref` runs `reference-transaction` too. A test with logging hooks showed both. `init-factory` and the pre-commit framework install none of these hook types, so no Factory hook runs.

**The move does not check that C is a claim commit.** A marker written by hand with any commit as its parent makes the next move push that commit and its history to `refs/ids/counters` on `origin`. A first move pushes whatever the local ref holds, too. Writing that marker needs write access to the project's `.git`, and that access can push anyway, so the bug bar gives no finding. A check that C has no parent and the empty tree would cost two git calls. This is a `hardening` suggestion.

**`--plan-seed` can reach `origin` through its local reads.** In a partial clone, `git cat-file blob` fetches each missing blob from `origin`, without `GIT_TERMINAL_PROMPT=0`, without `BatchMode`, and without the time limit. A `GIT_TRACE` run on a `--filter=blob:none` clone showed the fetch. The guarded read of the counter runs first and fails on a dead remote or missing credentials. So only a remote that stalls between the two calls can hang the plan. Partial clones are not the default.

**The setting can live in the global git config.** `next-id` reads `agent-factory.counterRemote` with `git config --get`, which includes the global file. A value there would send the claims of every project on the machine to one local counter. VIRGIL writes the setting into the repository config. BUG-0119 in the code register records what the move does in that case.
