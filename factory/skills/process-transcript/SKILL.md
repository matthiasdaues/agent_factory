---
name: process-transcript
description: >-
  Process a meeting transcript into two markdown artifacts — a verbatim
  protocol and a comparison against the current repository state. Use when
  the user provides a transcript, mentions "process transcript", or wants
  to compare a discussion against the spec.
category: utility
version: 1.0.0
disable-model-invocation: false
---

# Process Transcript

Turn a meeting transcript into two markdown files: one preserving the
discussion as citable evidence, the other measuring it against the
project's documented state.

The key words "MUST", "MUST NOT", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "MAY", and "OPTIONAL" in this document are to be interpreted
as described in RFC 2119.

This skill MUST run in the orchestrating session, never as a spawned
subagent. The user MUST confirm the output path and review the comparison
before commit.

## Inputs

| Input       | Required | Default             | Description                                        |
| ----------- | -------- | ------------------- | -------------------------------------------------- |
| Source file | MUST     | —                   | Path to the transcript source file                 |
| Output path | MUST     | `docs/transcripts/` | Directory for the two artifacts                    |
| Date        | MUST     | from filename/today | ISO date prefix (`YYYY-MM-DD`)                     |
| Slug        | MUST     | derived from title  | Kebab-case filename stem (e.g. `transport-review`) |

## Outputs

Two files in the output directory:

1. **`YYYY-MM-DD_<slug>.md`** — verbatim protocol (evidence)
2. **`YYYY-MM-DD_<slug>-vs-state.md`** — comparison against repo state (verdict)

## Step 1 — Extract text

Extract plain text from the source file by format:

| Format              | Method                                                                  |
| ------------------- | ----------------------------------------------------------------------- |
| DOCX                | Python 3 `zipfile` + `xml.etree.ElementTree` — extract `w:t` nodes      |
| PDF                 | `pdftotext` or Python 3 `PyPDF2` / `pdfplumber`                         |
| Plain text/Markdown | Use as-is                                                               |
| HTML                | Python 3 `html.parser` or `BeautifulSoup` — strip tags, keep paragraphs |
| Other               | MUST ask the user                                                       |

SHOULD prefer stdlib or pre-installed tools over pip packages.

MUST preserve every paragraph, including empty ones. MUST NOT reorder,
summarise, or filter.

## Step 2 — Write the verbatim protocol

Write `YYYY-MM-DD_<slug>.md`. This file is **evidence** — it preserves
everything and interprets nothing.

### Rules

1. **Verbatim.** Every speaker turn MUST appear exactly as transcribed.
   Keep filler ("Mhm", "Yeah"), false starts, and incomplete thoughts.
   MUST NOT paraphrase or omit.

2. **Chronological.** Order by time code only. MUST NOT reorganise by
   topic.

3. **Attributed.** Every turn carries a timestamp and speaker label:
   `N Minuten M Sekunden - Speaker: Name`. Where the source gives only
   "Lautsprecher N", preserve that label. MUST NOT guess identities.

4. **No commentary.** MUST NOT add summaries, groupings, analysis, or
   section heads. Structure comes from the transcript alone.

5. **Degraded passages stay.** Keep garbled or mixed-language artifacts
   verbatim. MAY insert one HTML comment above the region:
   `<!-- transcript quality degrades here -->`.

## Step 3 — Read the repository state

Before writing the comparison, MUST read the project's documented state.
At minimum check:

- Specification (`docs/spec/`)
- ADRs (`docs/adr/`)
- Open decisions (`docs/open-decisions.md`)
- Agent context (`docs/agent-context/`, falls back to `docs/charter/` for legacy projects)
- Domain model (`docs/CONTEXT.md`)
- PRD (`docs/prd/`)

Note which documents exist and what they say. Every claim in the
comparison MUST cite both a transcript timestamp and a document section.

## Step 4 — Write the comparison

Write `YYYY-MM-DD_<slug>-vs-state.md`. This file is the **verdict** — it
classifies every substantive discussion point against the documented state
and produces actionable work items.

### Section order

Follow this order. Omit sections with no findings — MUST NOT write empty
sections.

#### Opening thesis — "The N that matter"

Numbered list of the most consequential findings. Each item: one sentence,
one tension or resolution. Not a topic label.

#### §1 — Agreed, no action

Alignment between discussion and documents. Each item MUST cite timestamp
and matching section.

#### §2 — Documentation has moved past the discussion

Stale transcript points. MUST name the transcript as the stale source so
readers do not follow outdated agreements.

#### §3 — Contradictions needing a decision

Each item MUST name the spec section and the timestamp, state the clash in
one sentence, and list the options.

#### §4 — Unrecorded points

Agreements that lack a home in any document. MUST state what was agreed,
cite the timestamp, and name the target artifact.

#### §5 — Features discussed, not committed

Ideas surfaced but not in scope. Record without endorsing.

#### §6 — Scope, schedule, and risk

Deadlines, external commitments, blockers.

#### §7 — Decisions and next steps

What was decided; what was deferred.

#### §8 — Recommended actions

Numbered table with columns:

| #   | Action | Target artifact | Status |
| --- | ------ | --------------- | ------ |

Status values: `open`, `done`, `filed as OD-NNN`, `filed as ADR-NNNN`.

After the table, MUST add a reconciliation note (counts of open, done,
filed).

### Quality rules

- Every claim MUST cite both sources — timestamp and document section.
- Every item MUST carry a disposition (decide, record, remove, raise,
  confirm) — not just "this was discussed."
- MUST call out staleness explicitly: name the stale source and why.
- Tone MUST be forensic. No hedging. Contradictions are contradictions;
  gaps are gaps.

## Step 5 — Format

MUST run `factory/scripts/mdformat --number` on both files per
[markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).

## Step 6 — Present for review

Show the user:

1. Filename and line count of the protocol.
2. Opening thesis of the comparison.
3. Recommended actions table.

MUST wait for user confirmation before committing.
