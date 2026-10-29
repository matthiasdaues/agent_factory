# Lector Cut Plan: Data-Model DSL Technical PoC

This plan covers `poc/data_model_from_dsl/proposal-data-model-dsl-technical-poc.md` in its working-tree state of 2026-10-29. Line numbers refer to that state. The plan leaves out the `## Primer` placeholder and the rows of the Appendix tables, as the caller asked. Nothing in the proposal is edited until the stakeholder approves items. Approve or reject each numbered item on its own.

After approval, the lector applies the approved items and runs a sentence pass over the changed sections.

## 1. Order

**1.1 Motivation: lead with the model, then the survey, then the drift.** The paragraph at line 47 starts "Since the survey", but the survey is introduced only at line 51. The two-part question at line 49 comes before the survey finding that sets up its first part. New paragraph order: line 45 (the model today), line 51 (the survey), line 47 (the code drift), line 49 (the two-part question). No heading changes.

**1.2 Design: reorder the subsections so each one uses only terms already met.** Today, "Hard requirements and scoring" (line 76) uses `dbml2sql` before the candidates are named (line 128). "Model and code" (line 72) cites Definition-of-Done items 8 and 6 before the Definition of Done appears (line 133). New order under `## Design`:

1. `### The target database` (unchanged)
2. `### Model and code` (loses its scoring sentences, see 1.3)
3. `### The acid slice`
4. `### One story per candidate`
5. `### Hard requirements` (renamed from "Hard requirements and scoring", see 1.3)
6. `### Per-story Definition of Done`
7. `### Scoring` (new, see 1.3)

**1.3 Gather the scoring rules under one new heading, `### Scoring`.** The rules for the Pugh Matrix are spread over six places: line 72 (item 8 weighs high, item 6 low), line 74 (a generated pair scores as one option), line 85 (wrapper as maintenance cost, heavy penalty without a wrapper), line 141 (PNG does not count), line 180 (the stakeholder confirms the weights), and line 189 (the completion check). The new section holds the first five as one short list, each with its DEC reference. Line 189 stays in Completion Criteria as the check. The source sections keep their non-scoring facts:

- "Model and code" keeps "So the comparison is required, and generation is a convenience" as the reason, and drops the weighting sentence and the pair-scoring sentence.
- "Hard requirements" keeps the repair rule up to "the requirement counts as met", and drops the scoring consequences.
- Definition-of-Done item 5 keeps "PNG is optional, because no consumer reads a rendered PNG diagram (DEC-06)".

**1.4 Acid slice: put the map before the list.** The entity table (lines 91–101) describes each entity by its constructs before the twelve constructs are listed (lines 103–116). Move the construct list above the table. The section opens with one sentence that defines the term "acid slice", which today has no definition and opens with a fragment (line 89): "The acid slice is the fixed input to every candidate story: nine entities from today's `entity-model.md` that together carry the twelve constructs below (DEC-03)." This sentence replaces both sentences of line 89.

**1.5 Terms used before their introduction.** "Pugh Matrix" appears at line 41 but is linked only at line 154. Move the link to the first use in the Summary. "Gigacron" is never introduced; see item 6.2.

## 2. Duplicates

**2.1 Summary retells the Motivation.** Line 41, sentences 2 and 3 ("The survey answered … nobody installed or ran them.") repeat line 51. Home: Motivation, line 51. Cut them from the Summary. Also drop "The bake-off", which is a second name for the PoC; the playbook link moves into the next sentence. Proposed Summary, four sentences: "This proof-of-concept settles by observation which text-based data-modeling language can hold the Gigacron entity model as a checked source of truth. Under the `technical-poc.md` playbook, it ports one fixed slice of today's entity model to four candidates, runs each one, and compares each with Gigacron's SQLAlchemy mappings. The first release ends with four comparison notes and a `Pugh Matrix`. It does not adopt a language (DEC-01)."

**2.2 Guiding Rule repeats a Core Principle.** Line 195 says what line 56 ("Observation outranks documentation") already says. Home: the principle at line 56, because the reader meets it first. Cut the `## Guiding Rule` section (lines 193–195). The template marks it optional. If the stakeholder prefers to keep the Guiding Rule, cut the first sentence of the principle instead.

**2.3 The survey-citation rule appears twice.** Line 56, second sentence ("Where the survey recorded a documented claim, the note says whether observation confirmed it or contradicted it") repeats line 174. Home: Design Details, line 174, which also says how to cite (by source-record filename). Cut the sentence at line 56.

**2.4 The poc-only boundary appears four times.** Line 156 (Scope), line 168 sentence 2 (Design Details), line 191 (Completion Criteria), and the deferral at line 162. Home for the location rule: line 168 sentence 1, which also says the material stays marked as spike code. Home for the check: line 191. Cut the Scope bullet at line 156 and the sentence "This proposal promotes nothing into the specification or the factory scripts" at line 168.

**2.5 Completion criteria that restate Definition-of-Done items.** Line 185 already requires every note to answer all nine items. Line 187 restates item 4, and line 188 restates item 8. Home: the Definition of Done. Cut lines 187 and 188. Keep line 186, because "never from documentation" adds a condition the items do not state.

**2.6 The baseline's slice.** Line 131, sentence 2 ("The baseline runs on the same slice as the challengers") repeats the principle at line 55. Merge it with the reason: "Otherwise …" becomes "Running the baseline on the same slice turns 'better than what we have' into a finding, not an assertion."

**2.7 Open Questions carries a rule.** Line 180, sentence 2, states the weight confirmation, which is not an open question. Its home is the new Scoring section (item 1.3) and Completion Criteria line 189. The section keeps only "None."

## 3. Record

**3.1 No decision stamps.** The target-state text holds no dates, "Decision:" stamps, or "who decided" remarks. The file already uses the new layout, so no review sections need converting. No Open Questions item is already decided.

**3.2 DEC-01 is never cited.** A reader may ask why the PoC adopts nothing. The Summary sentence "It does not adopt a language" gets "(DEC-01)", as shown in item 2.1.

## 4. Blocks to cut or shrink

| Block                                          | Lines           | Words saved |
| ---------------------------------------------- | --------------- | ----------- |
| Summary survey sentences (2.1)                 | 41              | about 30    |
| Guiding Rule section (2.2)                     | 193–195         | about 25    |
| Principle survey sentence (2.3)                | 56              | about 18    |
| Scope bullet and Design Details sentence (2.4) | 156, 168        | about 18    |
| Completion criteria 187 and 188 (2.5)          | 187–188         | about 35    |
| Open Questions sentence 2 (2.7)                | 180             | about 14    |
| Scoring sentences, net after the merge (1.3)   | 72, 74, 85, 141 | about 15    |

No section is cut as a whole except the Guiding Rule. Each remaining section serves a reader who plans or runs a candidate story.

## 5. Inbound links

`grep -rn "proposal-data-model-dsl-technical-poc" .` finds no file that links to this proposal, so no anchor has an inbound link. The proposal links to no internal anchor. Items 1.2, 1.3, and 2.2 rename, add, and remove headings and break no link. If item 1.3 cites the Definition of Done by link, the target is `#per-story-definition-of-done`, which survives the reorder.

## 6. Content fixes

**6.1 Broken table row for `OUTBOX` (line 100).** The cell reads "the zero-or-one side of \`ATTEMPT" and stops. The pipes of the Mermaid notation `ATTEMPT ||--o| OUTBOX` most likely split the cell. Source: Gigacron's `entity-model.md`, line 401, `ATTEMPT ||--o| OUTBOX : dispatches_with`. Proposed cell: "nullable composite foreign key to `ATTEMPT`; the zero-or-one side of the relationship from `ATTEMPT`".

**6.2 "Gigacron" is never introduced.** The Primer may cover it later, but the Summary should stand for a planner. Source: Gigacron's `README.md`, "a professional enterprise scheduler". Proposed: "the entity model of Gigacron, the enterprise job scheduler" at the first use in the Summary.

**6.3 `NAME_CLAIM` is unexplained (line 47).** Source: Gigacron's `entity-model.md`, line 1184: a claim of one Task or Folder on its name inside one containing Folder. Proposed: "because a separate `NAME_CLAIM` table keeps each name unique inside its containing Folder."

**6.4 Wrapper deferral against DEC-07 (line 163).** "The stories use throwaway container commands only" conflicts with the wrapper a story builds under DEC-07. Proposed: "The stories build only throwaway commands and wrappers (DEC-07)." The stakeholder confirms that this is the intended meaning.

## 7. Estimate

The target-state text from Summary to Guiding Rule holds about 2,050 words today. After items 1–6 it holds about 1,900 words. The record holds about 360 words and does not change.

## Left for the stakeholder

- **Possible contradiction, line 59 against line 85.** The principle calls a candidate that misses its Definition of Done "ruled out". DEC-07 keeps a candidate that fails a hard requirement in the matrix with a penalty. The plan does not resolve which wording holds.
- **Unclear, line 172.** "No agent builds the candidates. The builds are done directly" does not say who builds them. The sentence pass leaves it unchanged.
- **Frontmatter, lines 14–17.** The `boundaries` paths name Gigacron files. In this repository, `docs/spec/supplementary_specs/entity-model.md` resolves to the factory's own entity model, and `packages/server/…/task_registry/models.py` does not exist. `domain_registry/models.py` is missing from the list. The lector does not edit frontmatter.
