---
title: Session Log Addendum
status: proposal
---

# Session Log Addendum

**Status: proposal, not yet adopted.** This memo proposes a mechanism. Nothing here is built or decided; it is written to be argued with.

## Problem

An AI CLI session runs several `factory/scripts/*` gates over a phase, and narrates the work in prose ("I created `docs/spec/prd.md`, wrote the traceability graph, and ran `spec-lint` clean"). Nothing checks that narration against reality. The gates print to the transcript and exit; no run leaves a durable, parseable trace. So we cannot tell whether a file the agent claims to have written actually changed, whether a gate it claims to have run clean actually exited 0, or whether something it never mentioned changed anyway.

The fix is a **session log**: every gate run appends one structured record to a logfile, and a reconciliation step at phase end compares that machine-captured record against the agent's stated claims.

## 1. Log entry schema

One record per run, as a single [JSON Lines](https://jsonlines.org/) object. The fields:

| Field           | Source                        | Why it is needed                                                           |
| --------------- | ----------------------------- | -------------------------------------------------------------------------- |
| `seq`           | count of prior lines          | Total order of runs within the session; survives equal timestamps.         |
| `ts`            | script process clock (UTC)    | When the run ended. See the timestamp note below.                          |
| `script`        | script basename               | Which gate ran.                                                            |
| `argv`          | the invocation arguments      | What it ran against (`docs/spec`, `--graph`, ...).                         |
| `exit_code`     | the process exit status       | Clean or not — for `spec-lint`, the error count (see the script's header). |
| `files_changed` | `git status --porcelain` diff | What actually moved on disk around the run — the ground truth (see §3).    |
| `summary`       | the script's own JSON output  | Structured detail the record can carry cheaply, when the gate emits it.    |

**Format.** JSON Lines, not YAML or a JSON array. Appending a run is one `open(..., "a")` write of one line — no whole-file reparse, no rewriting a closing bracket. Each line parses independently, so an interrupted run leaves every earlier line valid. Consuming it is `json.loads` per line, stdlib only.

**The timestamp note.** An agent cannot read a wall clock; it sees only the date injected into its context, so any time an agent writes down is untrustworthy. The record's `ts` therefore comes from the gate's own process clock (`datetime.now(timezone.utc)`) at the moment the run ends — a fact the agent cannot forge. That is the whole point of the log: it records what the machine observed, not what the agent said.

A real record, grounded in [`spec-lint`](../../scripts/spec-lint) run with `--graph` (which writes `traceability.json` and exits on the error count):

```json
{"seq":4,"ts":"2026-07-11T14:32:07Z","script":"spec-lint","argv":["docs/spec","--graph"],"exit_code":0,"files_changed":[{"path":"docs/spec/traceability.json","status":"M"}],"summary":{"error":0,"warning":2,"info":1}}
```

The `summary` here is `spec-lint --format json`'s own `summary` block, captured as-is. Gates with no JSON mode omit the field.

## 2. Where the log lives, and how scripts write to it

**One unified logfile per session**, not one per script with an index. Reconciliation reads it in a single pass; a per-script scheme would buy nothing and cost an index to keep in sync.

**Path: `.agent-factory/session-log.jsonl`, git-ignored.** The raw log is ephemeral machine telemetry, not a reviewed deliverable — the same class as the git-ignored `session-scratchpad.md`, so it belongs in a hidden namespace, not in `docs/`. The reconciliation *report* (§4) is human-facing and can land in `docs/reviews/` alongside the retrospective, but the log itself does not.

**Mechanism: one shared helper, `factory/scripts/_session_log.py`**, stdlib only (`json`, `os`, `subprocess`, `datetime`). The leading underscore marks it an importable helper, not a callable gate. It exposes a context manager the Python gates wrap their `main()` in:

```python
with session_log.record(
    "spec-lint", argv
):  # snapshots git before/after, times, appends
    return real_main(argv)
```

`record` reads the log path from an env var (`AF_SESSION_LOG`); when it is unset the manager is a no-op. So logging is transparent — the agent still calls `spec-lint docs/spec/` unchanged and cannot forget to log it — yet pre-commit and CI stay silent unless the session opts in by exporting the path once at session start. The two bash scripts (`mdformat`, `scratchpad`) and `structurizr` reach the same helper through a thin CLI mode on `_session_log.py`, added only when their turn comes (§5).

## 3. The "actually happened" inventory

The exit code and args say what ran; they do not say what changed on disk. Two ways to capture that:

- **Self-reporting** — each script reports the paths it touched. Precise, but it must be added to every script, and most gates touch nothing: `spec-lint`, `arch-lint`, and the rest are read-only linters. Self-reported paths would be empty for almost every run, and would still miss the files the *agent* wrote by hand between runs — which is exactly what reconciliation exists to catch.
- **External git diff** — the helper snapshots `git status --porcelain` before and after the run and records the delta. No per-script change beyond the wrap. It catches every filesystem effect git tracks, including the agent's own edits that happen to fall in the run's window, not only the gate's writes.

**Recommendation: the git-diff snapshot, in the shared helper.** It is the only option that catches the agent's hand-edits, and it costs no per-script logic. Where a gate already emits structured output — `spec-lint --format json` — the helper folds that into `summary` for free, so we get the precision of self-reporting for the gates that offer it, without asking the read-only ones to invent it.

## 4. The reconciliation step

A new deterministic script, `factory/scripts/session-reconcile`, callable exactly the way [`spec-lint`](../factory-guide.md#linting-and-gating) is. It reads two machine facts and compares them:

1. the session log — every run, its exit code, and the tree delta around it;
2. the phase's real git state — `git diff --name-only` across the phase's commits, plus the current working tree.

It flags, with no LLM and no prose-parsing:

- working-tree or committed changes that **no logged run and no commit accounts for** — an unexplained change;
- a **required phase-boundary gate that never ran**, or last ran before the final edit to what it checks — a stale clean;
- files a run's `files_changed` shows touched that are **neither staged nor committed** — silent drift.

Its output is a discrepancy report (text, plus `--format json`); blocking discrepancies can be filed as findings per [finding-format.md](../../rulebooks/conventions/finding-format.md#frontmatter-schema).

The agent's *prose* claims — from the phase review report and the commit messages — are the harder half. A deterministic script cannot judge whether "I updated the traceability graph" is true prose. So reconciliation splits: `session-reconcile` establishes the machine facts and their internal contradictions; the **phase reviewer agent** then reads that report as evidence and judges the narration against it. This plugs in where the gates already do — the reviewer runs `session-reconcile` as a step at the phase boundary, the same way it runs `spec-lint` first.

## 5. Migration path

Instrument one gate end to end before touching the rest: **`spec-lint` first.** It already emits structured JSON (a rich `summary` for free), it writes a file under `--graph` (so it exercises the git-diff path, unlike the pure read-only gates), and it guards a real phase boundary. The smallest viable slice is:

1. add `_session_log.py` with the `record` context manager and the `AF_SESSION_LOG` env gate;
2. wrap `spec-lint`'s `main()` in it — two lines;
3. prove it: run `spec-lint --graph` in a session, confirm one correct JSONL line lands; then run `session-reconcile` against a deliberately false claim and confirm it flags.

Only then roll the same two-line wrap out to the other Python gates (`arch-lint`, `backlog-lint`, `matrix-lint`, `statemachine-lint`, `index-lint`), then the bash scripts via the CLI shim. `init-factory` is one-shot setup, outside any phase loop — instrument it last, or not at all.

## Referenced from

- Nothing yet — this is a proposal.
