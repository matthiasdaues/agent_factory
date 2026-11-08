---
title: Finding Filing
category: review
enforcement: orchestrator findings-ingest loop (reads docs/findings/*.md with status open)
version: 1.0.0
---

# Finding Filing

Shared rules for filing review findings as local files. Findings are project artifacts, not entries in an external tracker. A blocking finding is one markdown file with strict frontmatter under `docs/findings/`. A `minor` finding is one JSON register file under `docs/findings/register/<class>/`.

## When to file

Canonical statement: [rules.md § Findings](../rules.md#findings).

[finding-classification.md § Shared severity scale and blocking rule](finding-classification.md#shared-severity-scale-and-blocking-rule) says which finding becomes a finding file, which becomes a register file, and which stays in the review report.

## File location and name

- Directory of a finding file: `docs/findings/`
- Filename of a finding file: `<TAG>-<NNNN>.md`, zero-padded, sequential per tag (e.g. `SPEC-0001.md`).
- Path of a register file: `docs/findings/register/<class>/<TAG>-<NNNN>.json`, where `<class>` is the review class of the finding (e.g. `docs/findings/register/security/SEC-0012.json`).
- Allocate `NNNN` with `next-id`. The prefix of each tag and the files that claim it are in [id-prefixes.md](id-prefixes.md). Read the ID from the standard output of `next-id`, because a shell variable does not survive from one agent command to the next. When `next-id` fails, stop and report its message; never pick a number by hand.

| Review                          | TAG     |
| ------------------------------- | ------- |
| Spec review                     | `SPEC`  |
| ATAM architecture review        | `ATAM`  |
| Architecture agent's read check | `ARCH`  |
| Implementation code review      | `IMPL`  |
| Fagan code inspection           | `FAGAN` |
| Security review                 | `SEC`   |
| Unresolved mutant               | `QA`    |
| Bug hunt / exploratory testing  | `BUG`   |
| Reconciliation agent            | `RECON` |

## Format

Frontmatter and body skeleton: [finding.md template](../templates/finding.md). The frontmatter holds sixteen fields: `id`, `source`, `review_class`, `category`, `type`, `severity`, `basis`, `rating`, `override_by`, `override_reason`, `stop_confirmed_by`, `stop_confirmed_reason`, `artifact`, `status`, `owner`, and `traces`. The contract of each field is in [interface-contracts.md § finding file](../../../../docs/spec/interface-contracts.md#docsfindingsidmd--finding-file).

The reviewer writes the four human fields `override_by`, `override_reason`, `stop_confirmed_by`, and `stop_confirmed_reason` as `null`. Only the stakeholder fills them.

Canonical statement: [rules.md § Findings](../rules.md#findings) — no "this looks off" without a fix direction.

## Register files

A `minor` finding gets no finding file. The reviewer writes one JSON object to `docs/findings/register/<class>/<ID>.json` with `status: open`. The keys are the contract of [interface-contracts.md § register file](../../../../docs/spec/interface-contracts.md#docsfindingsregisterclassidjson--register-file), and the schema `rulebooks/schemas/finding-register-<class>.schema.json` describes them. A register file has no `owner:` key, so the review report names the agent that acts on the finding.

The commit that fixes a `minor` finding sets `status` of its register file to `resolved`. The register file stays.

A `note` stays a row of the review report, and a `question` becomes an entry of `docs/spec/work/todo.md`. Neither gets a file in `docs/findings/`.

## Removal of a finding file

A finding file whose `HEAD` version carries `review_class` is never removed, with two exceptions. Each one leaves a register file under the same ID.

- The migration moves a `minor` finding to the register of its class.
- The stakeholder lowers a blocking finding to `minor`, and the register file with both override keys replaces the finding file.

## Owner

`owner:` in the frontmatter names the agent that acts on the finding next. The filer is not the owner. By default the owner is the producer of the artifact the finding is about. A `BUG` finding names the developer agent. A `QA` finding for a missing test names the planning agent.

A finding about a proposal under `docs/proposals/` names `virgil`, who revises the proposal with `draft-proposal`. A finding without an artifact, such as a `RETRO` finding, names `virgil`. So does a finding whose artifact spans several producers, such as `RECON-cycle-retirement`. Virgil shapes or splits such a finding into work with the stakeholder.

## Status lifecycle

- `open` — the finding stands; the owner must address it.
- `resolved` — on a repeat pass, the reviewer verified the owner's fix and set the status. Keep the file as the durable record; do not delete it.
- `waived` — the stakeholder decided not to fix the finding. Only the stakeholder sets it, with `override_by` and `override_reason`.
- `deferred` — only the migration sets it, on a file without `review_class`. No agent sets it.

## How the orchestrator reads findings

The finding files are the contract. When run under the orchestrator, the review loop reads every `docs/findings/*.md` whose frontmatter line is `status: open`. Those are the findings the phase must still address. The loop greps are anchored, `grep -l "^status: open"`, so a waived finding whose body quotes "status: open" is not listed. The orchestrator sends each open finding to the agent in `owner:`, not to the author of the reviewed phase. It sends an open finding without `owner:` to the producer of the artifact it names, read from the output declarations (`outputs:` in the agent definitions). The loop repeats until no open finding remains. The loop skips register files, because they are JSON files outside `docs/findings/*.md`. You do not emit any machine-readable block; filing the files, and setting `status: resolved` on a repeat pass once a fix is verified, is all the loop needs. This works the same whether the review ran headless or in an interactive session.

## Confirming a stop

A `critical` finding stops the run until the stakeholder confirms the stop. `dispatch` and `premerge-check` print the stop notice. The stakeholder confirms in these steps:

1. Run each check under `## Possible damage` in the finding.
2. Write `stop_confirmed_by` and `stop_confirmed_reason`. The reason says what was checked and found.

The stakeholder writes the human fields in an editor or with a `!` command, which runs outside the tool hooks. An agent that writes one is refused by `guard-human-fields`.

A confirmed `critical` finding loops back to its owner like a `major` one, and it keeps severity `critical`. The confirmation lifts the stop. It does not close the finding.

## Waiving a finding

The stakeholder waives a blocking finding in an editor or with a `!` command. The waiver sets `status: waived` with `override_by` and `override_reason`. A waived finding drops out of the loop.

## Orchestrator and the stop notice

When a script prints the stop notice, the orchestrator explains each stopping finding with `explain-review-finding` in an interactive session and waits. A headless run does not wait. It ends with the notice in its final summary, because it cannot confirm its own stop.

## Pause point

Present the findings to the user before writing any files. The user decides which findings warrant a filed finding. Then write the files and save the review report.

## Referenced from

- [finding-classification.md § Shared severity scale and blocking rule](finding-classification.md#shared-severity-scale-and-blocking-rule)
- [rules.md § Findings](../rules.md#findings)
- [report-format.md § Findings drive the loop](report-format.md#findings-drive-the-loop)
- [reconciliation-agent.md § Workflow](../../agents/reconciliation-agent.md#workflow)
- [spec-review-agent.md § Workflow](../../agents/spec-review-agent.md#workflow)
- [architecture-review-agent.md § Workflow](../../agents/architecture-review-agent.md#workflow)
- [code-review-agent.md § Workflow](../../agents/code-review-agent.md#workflow)
- [qa-agent.md § Workflow](../../agents/qa-agent.md#workflow)
- [security-review § Report](../../skills/security-review/SKILL.md#report)
- [reconcile-spec § Step 2 — Write the rows](../../skills/reconcile-spec/SKILL.md#step-2--write-the-rows)
- [bug-hunt § Phase: Hunt](../../skills/bug-hunt/SKILL.md#phase-hunt)
- [inspect-spec § Step 3 — Write the review report](../../skills/inspect-spec/SKILL.md#step-3--write-the-review-report)
- [atam-review § Step 4 — Write the review report](../../skills/atam-review/SKILL.md#step-4--write-the-review-report)
- [fagan-review § Step 3 — Write the review report](../../skills/fagan-review/SKILL.md#step-3--write-the-review-report)
- [finding.md template](../templates/finding.md)
