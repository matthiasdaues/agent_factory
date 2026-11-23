# Synthesis: Knowledge Graph With Provenance

This synthesis answers the question in
[research-question.md](research-question.md#question). It draws on four
investigator reports:

- [internal-inventory.md](sources/internal-inventory.md): where the
  repository records ideas and decisions today.
- [external-survey.md](sources/external-survey.md): outside methods,
  standards, and tools.
- [extraction-pipeline.md](sources/extraction-pipeline.md): how a pipeline
  splits sources into linked ideas.
- [codex-process-design.md](sources/codex-process-design.md): an
  independent design by Codex on `gpt-6-astra`, written without the other
  three reports.

## The answer

The proposal process can grow into an idea process. It needs three
additions and no database.

1. **One markdown record per idea, with an ID that holds across documents.**
   An idea record exists before any proposal and outlives a rejected one.
2. **A provenance anchor on every idea.** The anchor points to the exact
   passage in a source that never changes: a transcript protocol, a message
   export, or a committed file at a full commit SHA.
3. **A decision history on every idea.** The history has a fixed set of
   outcomes. A later decision is added and names the one it replaces, and
   nothing is overwritten.

A deterministic script checks the records and builds a throwaway index.
Before a proposal session suggests anything, it queries that index for
earlier ideas, including the rejected and deferred ones.

All four reports reach this shape on their own. Codex reached it without
reading the other three.

## Why the factory needs it

The factory records a decision well once a proposal holds it. Before and
around proposals, ideas are lost.

- Only 19 of 83 proposals have a Decisions table. Its DEC IDs are numbered
  per file, so `DEC-01` exists 19 times. Its "Raised by" cell is free text
  such as "draft conversation", not a link to a source
  ([internal-inventory.md § 3](sources/internal-inventory.md#3-how-artifacts-link-to-each-other-and-to-their-source)).
- No status exists for "won't do". "Defer" appears as prose lists in 59
  proposals, with no ID, owner, or date to revisit
  ([internal-inventory.md § 2](sources/internal-inventory.md#2-decision-outcomes-and-where-each-is-recorded)).
- Decisions sit in places a later session does not read. The twenty
  decisions of `docs/proposals/run-lifecycle.md` are in an untracked handoff,
  and the proposal says "Open Questions: None". Ten of the 50 handoffs are
  untracked, and the scratchpad is ignored by git
  ([internal-inventory.md § 4](sources/internal-inventory.md#4-where-an-idea-gets-lost-today)).
- Reading every source on a topic costs about 636,000 words. Reading a
  targeted slice still costs about 54,000 words, and that slice misses most
  decisions
  ([internal-inventory.md § 5](sources/internal-inventory.md#5-what-an-idea-generation-session-would-need-to-read-and-how-long-that-is)).

## What the outside world offers

No single method covers the whole need. Each part comes from a different
source, and every part works in markdown files in git
([external-survey.md § 6](sources/external-survey.md#6-fit-judgment)).

| Need                  | Borrowed from                    | What the factory takes                                                  |
| --------------------- | -------------------------------- | ----------------------------------------------------------------------- |
| Idea types            | IBIS (issue, position, argument) | A small set of types: claim, question, decision                         |
| Decision outcomes     | Python PEP statuses              | The only checked model with accept, reject, defer, and superseded       |
| Link to the source    | W3C PROV-O                       | Three field names: derived from, attributed to, revision of             |
| Exact place in source | W3C Web Annotation selectors     | Quote with text before and after, offsets, and a hash of the source     |
| Changed facts         | Graphiti                         | Sources never change; an outdated idea is marked invalid, never deleted |
| One idea per note     | Zettelkasten, evergreen notes    | The writing rule: one idea, standalone, stable ID                       |

The graph tools of the LLM era fit worst: GraphRAG, LightRAG, Graphiti,
Cognee, and Mem0. They need a running store, they differ per CLI, and none
of them records a decision
([external-survey.md § 5](sources/external-survey.md#5-llm-era-systems)).

## Design options

Codex described three options
([codex-process-design.md](sources/codex-process-design.md#option-a-annotate-source-documents)).

| Option                      | What is stored                                                     | Cost                                                             |
| --------------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------- |
| A. Annotate documents       | Idea tables inside proposals and transcript comparisons            | Fewest new habits; an idea's identity stays tied to one document |
| B. Independent idea records | One file per idea, with sources, typed links, and decision history | Curation: merging duplicates, splitting broad ideas              |
| C. Append-only ledgers      | Per-session event logs; idea pages are generated from them         | Most machinery: replay rules, event versions, edit protection    |

I recommend option B. Option A cannot follow an idea across proposals, and
that is the main gap. Option C solves history by replay, but the decision
history inside an option B record gives the same answer with less
machinery. Investigators B and C point to option B as well: their
best-fit approaches all assume one record per idea.

## How a record would look

This sketch combines the four reports. It is a proposal draft, not a
settled format.

<!-- yaml-excerpt -->

```yaml
id: <prefix>-0042
type: claim            # claim | question | decision
text: One idea, readable without any other record.
sources:
  - derived_from: docs/transcripts/2026-11-20_counter-session.md
    commit: <full 40-character SHA>
    quote: "the counter stays local until origin exists"
    prefix: "we agreed that "
    suffix: ", and then"
    speaker: stakeholder
links:
  - type: refines      # supports | contradicts | refines | depends-on | answers | same-as
    target: <prefix>-0017
    reason: Narrows the counter rule to projects without origin.
    confirmed_by: stakeholder
decisions:
  - outcome: accepted
    by: stakeholder
    evidence: docs/proposals/implemented/counter-ids.md#decisions (DEC-14)
    replaces: null
```

A deterministic `idea-lint` script, built like `finding-lint`, checks the
record. The quote must occur in the source at that commit, and the speaker
must match the turn. Every link must have a legal type, legal endpoints, and
a reason. Every replaced decision must exist, and no idea may lack a
source. The
`contradicts` link and every decision need a person's confirmation
([extraction-pipeline.md § 5](sources/extraction-pipeline.md#5-what-goes-wrong-and-how-to-check-it)).

`process-transcript` becomes the first producer. It keeps its verbatim
protocol as the source and gains three steps: extract ideas, propose links
and merges, and run `idea-lint` before the human review
([extraction-pipeline.md § 6](sources/extraction-pipeline.md#6-how-process-transcript-would-change)).

## Decisions for the stakeholder

The reports disagree on four points. Each one needs a decision before a
proposal can be decision-complete.

1. **Decision outcomes.** The question names do, won't do, defer, and accept.
   Investigator B proposes the PEP set: proposed, accepted, rejected,
   deferred, withdrawn, superseded. Codex splits the decision in two. A
   disposition answers whether to build the idea: undecided, do, won't do,
   or defer. A separate acceptance answers which proposal revision the
   stakeholder approved. Case: the stakeholder accepts the run-lifecycle
   proposal text, but one idea in it is marked "later". With one status
   field, that idea reads as accepted. With two fields, it reads as deferred
   inside an accepted proposal. I recommend the two fields, because the
   case occurs in proposals today.
2. **Name of the ID prefix.** `IDEA` collides with the IDEA delivery cycle in
   [ADR-0017](../../adr/0017-cycle-based-orchestration-supersedes-linear-playbook-fsm.md).
   "Concept" collides with the CONCEPT cycle in
   [ADR-0018](../../adr/0018-concept-internal-sequence-is-agent-owned.md).
   A different word, such as `NOTION` or `KI` (knowledge item), avoids both.
3. **Which sources may enter.** Today's transcripts and committed documents
   are safe. Email, Slack, and Teams messages carry personal data. Copying
   quotes from them into git needs a rule on consent, retention, and
   deletion. No report settles this; it is a stakeholder and possibly a
   legal question
   ([extraction-pipeline.md § Open questions](sources/extraction-pipeline.md#open-questions)).
4. **Relation to the Concept stage draft.**
   [concept-stage-knowledge-inventory.md](../../proposals/concept-stage-knowledge-inventory.md)
   tracks knowledge obligations: what the project must know and does not yet
   know. An idea record tracks what someone proposed and what was decided.
   Codex keeps the two apart: "availability target unknown" differs from
   "do not implement redundancy". I recommend one proposal that references
   the draft, not a merge of the two.

## Smallest first step

Codex proposes a pilot on one closed set of material: the counter-ID
proposal, ADR-0031, and ADR-0033
([codex-process-design.md § Recommendation and smallest proof](sources/codex-process-design.md#recommendation-and-smallest-proof)).
The steps are:

1. Write a handful of idea records by hand in one pilot folder, without
   production IDs.
2. Add one unaccepted idea from the Concept stage draft.
3. Ask a fresh session: "Can a new project without `origin` allocate IDs?"
   The session must return the local-counter decision, its condition, and
   the rule it replaced.
4. Plant a broken source anchor and two conflicting decisions. The check
   must report both.

The pilot passes when both historical answers are correct, the unaccepted
idea is not shown as policy, and neither planted defect goes unreported. The
pilot needs no extraction pipeline and no new ID prefix.

## Defects found on the way

The investigators found five defects outside the research question. Each
needs its own fix:

- `packages/factory/skills/process-transcript/SKILL.md` line 92 reads
  `docs/open-decisions.md`, and that file does not exist.
- ADR-0017 names `packages/factory/engine/models/delivery.yaml` as the
  delivery model. That file does not exist; `engine/models/` holds only
  `__init__.py`.
- The run-lifecycle decisions and review exist only in an untracked handoff.
  The proposal shows no open question.
- Eighteen `implemented` and four `superseded` proposals sit in the root of
  `docs/proposals/`, not in their subfolders.
- The status `cancelled` is defined in the proposal template and used by no
  proposal.

## Limits of this research

- The approach was improvised and skipped the claim review of the
  `research-survey` playbook. No second agent tried to refute a finding.
- Several web claims come from search snippets and are marked unchecked in
  the reports. The QOC and DRL descriptions come from secondary sources.
- No tool that extracts ideas from chat with source links was found. The
  investigators did not search for one specifically.
- No report measured how often quote-anchored extraction produces an idea
  that its source does not support. The figures from FActScore and ALCE
  measure other tasks.
