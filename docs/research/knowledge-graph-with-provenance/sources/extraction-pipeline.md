# Splitting Sources Into Linked Ideas

Scope: how a pipeline splits transcripts, emails, and chat messages into single ideas, anchors each idea to its source, links ideas, and records decisions. Question context: `docs/research/knowledge-graph-with-provenance/research-question.md`.

## Summary

- Use two kinds of record. A source span is verbatim and immutable. An idea is a short, derived statement that always points to one or more spans.
- Anchor with several redundant selectors (quote with context, offsets, hash, source ID). One selector alone breaks.
- Check the pipeline with deterministic rules first: the quote must exist in the source, the speaker must match, the link types must be legal. An agent's opinion comes last.
- The factory already uses this pattern for findings: the reviewer records facts and a script computes the result (`packages/factory/rulebooks/conventions/finding-classification.md`, lines 8-15). Ideas can use the same pattern.

Evidence labels: "checked" means I fetched the page in this task. "Unchecked" means I only saw it in a search snippet.

## 1. The unit of an idea

**The point.** Practitioners and papers do not agree on one unit. Pick the unit by the question the graph must answer. For a process that tracks "what was discussed and what was decided", use a small typed set: claim, question, and decision, each atomic.

| Unit                           | Where it is used                                                                                                                                                        | Strength                                       | Weakness                                                                   |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- | -------------------------------------------------------------------------- |
| Atomic claim or fact           | FActScore splits generated text into atomic facts and scores the share a source supports (https://arxiv.org/abs/2305.14251, checked)                                    | Each unit can be checked on its own            | Strips hedges and speaker stance                                           |
| Atomic note (concept)          | Zettelkasten: "one knowledge building block per note", each with a unique ID, with links that carry a stated reason (https://zettelkasten.de/introduction/, checked)    | Fits the practitioner in the research question | Judgement call; size varies by use                                         |
| Question / position / argument | IBIS: issues are questions, positions answer them, arguments support or object (https://en.wikipedia.org/wiki/Issue-based_information_system, checked)                  | Matches how a proposal discussion runs         | Three types only; no "decision" node                                       |
| Decision dialogue acts         | AMI meeting work labels utterances as issue, resolution proposed, resolution restated, agreement (https://aclanthology.org/W08-0125.pdf, via search snippet, unchecked) | Directly about decisions                       | Sparse: about 1-2% of utterances per label (unchecked)                     |
| Proposition (logic form)       | Used in knowledge-graph literature as triples                                                                                                                           | Machine-friendly                               | Not checked in this task; I found no practitioner source for meeting notes |

**Recommendation.** Three node types:

1. `claim`: one assertion, stated so it can stand alone.
2. `question`: an open issue (IBIS issue).
3. `decision`: a disposition on another idea. Values from the research question: do, won't do, defer, accept.

Rule for atomicity: one idea holds one assertion, and a reader needs no other idea to understand it. The Meeting Decision Tracker demo rewrites utterances so they stand alone (https://aclweb.org/anthology/2022.aacl-demo.10.pdf, via search snippet, unchecked). That rewrite is where nuance gets lost (see section 5).

A `concept` (a named term) is a separate case. The factory already keeps settled terms in `docs/spec/glossary.md` (named in `packages/factory/skills/process-transcript/SKILL.md`, Step 3). Do not create a second term store. Link ideas to glossary terms.

## 2. Anchoring an idea to its source

**The point.** Store the source object once, store spans against it, and store several selectors per span.

### What an anchor holds

| Field                               | Purpose                                             | Failure it survives           |
| ----------------------------------- | --------------------------------------------------- | ----------------------------- |
| Source ID                           | Names the file, thread, or message                  | Rename if the ID is stable    |
| Message or turn ID                  | Platform ID for email and chat                      | Edits to text                 |
| Timestamp and speaker               | The two fields the factory protocol already carries | Reflow of text                |
| Exact quote, plus prefix and suffix | Finds the span by text                              | Offset shifts (see below)     |
| Start and end offsets               | Fast lookup                                         | Nothing if the source changes |
| Hash of the source version          | Says which version the offsets apply to             | Detects any edit              |

The W3C Web Annotation Model defines these selectors. `TextQuoteSelector` copies the selected text as `exact`, with optional `prefix` and `suffix`. `TextPositionSelector` records character offsets and the spec warns that "any edits ... may change the selection". It advises pairing it with a state that names the version (https://www.w3.org/TR/annotation-model/, checked). Several selectors may describe one span so that at least one still works (same source).

Hypothes.is uses this scheme with fuzzy matching: it searches near the stored position for the prefix and suffix, then falls back to the quote alone (https://web.hypothes.is/blog/fuzzy-anchoring/, via search snippet, unchecked; I did not verify the present client).

### Provenance links

PROV-O gives the vocabulary. `wasQuotedFrom` is a form of `wasDerivedFrom` for repeating part of a source. `wasRevisionOf` marks a new edition. `wasInvalidatedBy` links an entity to the activity that ended its usability (https://www.w3.org/TR/prov-o/, checked, first 100,000 characters only). An idea is derived from a span by an activity (the extraction run, with model and prompt version) and an agent.

### What survives an edit or deletion

- **Edit.** Keep the old source version as an immutable copy, keyed by hash. The span stays valid against that copy. Add a new source version and re-anchor by quote; mark failures as `unanchored`. Do not overwrite.
- **Deletion at the source.** Two cases. If deletion is a privacy or legal request, delete the copy and mark dependent ideas `source-removed`. The idea may then stay only if it is itself safe to keep. If deletion is routine churn, keep the copy.
- **Rule.** An idea with no resolvable anchor is not deleted. It is flagged. A deterministic check lists such ideas on every run.

Repository note: the factory protocol file is already immutable evidence ("preserves everything and interprets nothing", `packages/factory/skills/process-transcript/SKILL.md`, Step 2). That is the right source object. Git history supplies version identity.

## 3. Duplicates and near-duplicates

**The point.** Merge in layers, cheap and exact first, and record every merge as a reversible link, not a deletion.

Layers seen in tools (all from search results, unchecked, mostly tool documentation and blogs):

1. Exact and normalized text match.
2. Embedding similarity. Published defaults cluster around cosine 0.85 to 0.92. One guide calls 0.85 too aggressive and prefers 0.88 to 0.92 (https://theneuralbase.com/graphrag/learn/intermediate/entity-resolution-for-new-content/, unchecked).
3. An LLM judge for the ambiguous band only (https://pypi.org/project/nodecanon/, unchecked).
4. Human review (https://www.mintlify.com/juanceresa/sift-kg/concepts/entity-resolution, unchecked).

Cognee deletes the merged nodes and warns that the step is destructive (https://docs.cognee.ai/guides/memify-entity-deduplication.md, unchecked). Do not copy that.

**How to record a merge.**

- Keep both ideas. Add a typed link `same-as` (exact or near) from the later idea to a canonical one. This matches PROV `alternateOf` in spirit (checked, PROV-O page above).
- Record who proposed it (rule or model), the score, and the threshold.
- Claims that look alike but differ in scope, date, or speaker stay separate, linked with `refines`. Two people saying one thing is evidence of agreement, so keep both anchors on the canonical idea.
- A merge is a proposal until a rule or the stakeholder confirms it. Near-duplicates in the ambiguous band go to the stakeholder.

Threshold values need calibration on factory data. I found no published value for meeting claims.

## 4. Typed links between ideas

**The point.** Use a small closed set of link types, each with a legal source type and target type, and require a stated reason.

IBIS gives the restricted grammar: issues connect to any node, positions only to issues, arguments only to positions (checked, Wikipedia page above). Zettelkasten adds that a link creates knowledge only when the reason is stated (checked, zettelkasten.de page above).

Proposed set:

| Link           | From              | To                | Meaning                  |
| -------------- | ----------------- | ----------------- | ------------------------ |
| `supports`     | claim             | claim or decision | Evidence or reason for   |
| `contradicts`  | claim             | claim             | Cannot both hold         |
| `refines`      | claim             | claim             | Narrower or more exact   |
| `depends-on`   | claim or decision | claim or decision | Needs the target to hold |
| `answers`      | claim             | question          | IBIS position            |
| `decided-by`   | claim or question | decision          | Disposition applied      |
| `same-as`      | any               | same type         | Merge record (section 3) |
| `derived-from` | idea              | source span       | Provenance (section 2)   |

Rules:

- A link carries a one-sentence reason, a creator (rule, model, or person), and the anchors that justify it.
- `contradicts` and `decided-by` are never created by a model alone. A model proposes, a person confirms. A wrongly stated contradiction poisons later decisions.
- A decision carries its own fields: value (accept, do, defer, won't do), who decided, the span of the decision, and a review date for `defer`.
- A later decision on the same idea supersedes the earlier one. Keep both and link them. Never overwrite.

The AMI decision scheme warns that a detector can latch onto topic words instead of decision language (via search snippet, unchecked, https://preview.aclanthology.org/fix_video/2021.sigdial-1.56.pdf). So a `decision` needs an anchor that shows the commitment, for example an agreement turn, and a person's confirmation.

## 5. What goes wrong and how to check it

**The point.** Each failure has a deterministic first check. Agents review only what rules cannot decide.

| Failure                                         | Deterministic check                                                                                                                             | Agent check, if any                                           |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Hallucinated idea: no support in the source     | The anchored quote must occur verbatim in the stored source at the stated place. Fail if not found.                                             | Entailment check that the quote supports the idea (see below) |
| Idea says more than the quote                   | None fully deterministic                                                                                                                        | Entailment model or judge, then a sample read by a person     |
| Lost nuance: hedge, condition, or scope dropped | Flag ideas whose quote contains hedge or condition words absent from the idea text (word list, per language)                                    | Sample review                                                 |
| Wrong speaker                                   | Speaker on the idea must equal the speaker label of the turn containing the quote. Fail on mismatch.                                            | None                                                          |
| Wrong or missing speaker in the source          | Source has no labels, so no identity is claimed (see section 6)                                                                                 | None                                                          |
| Merged unlike ideas                             | Merge needs same type, same scope fields, and a score within the stated band                                                                    | Stakeholder confirms ambiguous band                           |
| Illegal link                                    | Link type, endpoint types, reason, and creator must pass the grammar in section 4                                                               | None                                                          |
| Orphan or unanchored idea                       | Query for ideas with no resolvable anchor                                                                                                       | None                                                          |
| Privacy leak from email and chat                | Scan for patterns (addresses, phone numbers, tokens) and a per-source sensitivity flag; block ideas that quote flagged spans into shared output | Person decides edge cases                                     |
| Source edited after extraction                  | Stored hash differs from the source hash                                                                                                        | Re-anchor run                                                 |

External evidence on the unsupported-idea rate:

- FActScore: ChatGPT scored 58% factual precision on biographies, so about 40% of atomic facts lacked support (https://arxiv.org/abs/2305.14251, checked). That is generated text against a knowledge base, not extraction from a given transcript. Expect a lower rate when the model must quote, but I found no measured figure.
- ALCE: even the best models "lack complete citation support 50% of the time" on ELI5 (https://arxiv.org/abs/2305.14627, checked). Citations from a model are not proof. Verify them.
- SelfCheckGPT detects hallucination by sampling several answers and testing consistency, with no external source (https://arxiv.org/abs/2303.08896, checked). It is a statistical signal. Use it as a triage filter, never as the gate. A quote check is stronger because the source is available.

I could not check a source for the claim that email and chat need extra care. Treat the privacy row as design judgement, not as evidence from the survey.

Cost note: the quote check, speaker check, grammar check, and orphan check are pure string and graph rules. They run in a lint script, as `finding-lint` does for findings (`packages/factory/scripts/finding-lint`; the convention says it "recomputes the severity from the basis", `finding-classification.md`, front matter).

## 6. How `process-transcript` would change

**Today.** The skill produces two files and no ideas (`packages/factory/skills/process-transcript/SKILL.md`):

- Step 2 writes a verbatim protocol with timestamps and speaker labels, in time order.
- Step 4 writes a comparison against repo state, in prose sections §1 to §8. Each item cites a transcript timestamp and a document section.
- The skill runs only in the orchestrating session, and the user confirms before commit.

**Gaps found.**

1. The citation is a timestamp. It is not a span. Two turns can share a timestamp, and no quote or hash exists.
2. Rule 3 of Step 2 demands speaker labels. The sample `docs/transcripts/2026-08-20_pocock_martin_agentic_coding.txt` has timestamps and text only, no speaker labels (searched for "Speaker" and "Lautsprecher", no hits). So the "wrong speaker" check cannot run on that kind of source until a diarization step or a manual label exists.
3. The comparison is prose. No machine can tell what the claims are, which ones are decisions, or how they link.
4. Step 3 reads `docs/open-decisions.md`, but that file is absent in this checkout. I did not verify where the skill's decisions now live. Investigator A covers this.
5. The existing sample comparison (`docs/transcripts/martin-factory-comparison.md`) shows the prose form. Nothing in it is a queryable record.

**Proposed change (description only; do not edit the skill).**

- Keep Step 1 and Step 2. The protocol stays the immutable source object. Add a source manifest line: source ID, content hash, import date.
- Add a new step between 2 and 4, "Extract ideas". It writes one record per idea: ID (from `next-id`), type (claim, question, decision), standalone text, speaker, anchor (quote, prefix, suffix, offsets, source hash), and extraction run (model, prompt version).
- Add a new step "Link and merge". It proposes typed links and merge candidates against the existing graph, using the layers in section 3.
- Add a deterministic lint step before the human review, `idea-lint`, built like `finding-lint`: quote exists, speaker matches, link grammar, no orphans, hash current.
- Change Step 4. The comparison is generated from idea records instead of free prose. Each §-section becomes a query: §1 agreed (idea `supports` a spec claim), §3 contradictions (`contradicts`), §4 unrecorded (idea with no link to any document), §7 decisions (`decision` records). Keep the opening thesis as prose. The existing rule "every claim cites both sources" turns into "every row has a span anchor and a document anchor", which the lint can check.
- Keep Step 6. The user confirms. Add that the user confirms every `decision` and every `contradicts` link, as in section 4.
- Add a privacy gate for email and chat sources: sensitivity flag at import, and a block on quoting flagged spans into committed files.
- Add source adapters. Today the skill extracts text from DOCX, PDF, text, and HTML (Step 1). Email and chat need message-level units with platform IDs. Plain text with timestamps remains the fallback with weaker anchors.

**Relation to scratchpad.** `packages/factory/skills/scratchpad/SKILL.md` appends a verbatim note to `session-scratchpad.md` with no ID, anchor, or type. It is the raw material end of the same flow. A scratch note could enter the pipeline as a source with the date section as its anchor. I did not look at how many such notes exist.

**Relation to finding classification.** The reviewer-records-facts, rule-computes-result design applies directly. For an idea, the extractor records facts (does the quote support the idea, does the quote contain a hedge, is a speaker named). A rule computes a status such as `verified`, `needs-review`, or `rejected`. Two runs on the same facts give the same status.

## Open questions

1. Unit size. I found no measured agreement between annotators on what one meeting idea is. The factory needs a calibration set from its own transcripts.
2. Merge thresholds. All numbers I found come from tool blogs and docs (unchecked). None targets meeting claims.
3. Measured hallucination rate for quote-anchored extraction from a given transcript. FActScore and ALCE measure other tasks.
4. How email and chat sources arrive (export format, message IDs, thread structure). I did not check Slack or Teams export formats.
5. Speaker identity when a source has no labels. Needs a diarization or manual step. Not researched.
6. Privacy rules: retention, consent, and what may enter a git repository. This needs a stakeholder decision and possibly legal input.
7. Where decisions live today, and whether `docs/open-decisions.md` still exists. Left to investigator A.
8. Whether the verified-claim machinery in the research playbooks (`claim-formulation`, `adversarial-review`) should apply to ideas. I did not read those skills.
9. I did not read the end of the PROV-O and Web Annotation pages (characters past 100,000). Both pages were long.
