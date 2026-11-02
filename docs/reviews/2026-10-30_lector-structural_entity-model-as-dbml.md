# Lector structural pass: entity-model-as-dbml.md

- Document: [docs/proposals/entity-model-as-dbml.md](../proposals/entity-model-as-dbml.md)
- Commit read: `2e817167` on `dev`
- Protected: the frontmatter, the Primer placeholder, and the Appendix tables
  (Decisions, Review findings, Review passes).
- Status: plan only. The proposal is unchanged. Approve or reject each item by
  its number.

Line numbers refer to the proposal at the commit above.

## 1. Order

**S-01. Lint rules use two terms before their sections introduce them.** The
lint table (lines 193–201) names `enum-matches-state`, whose "linked" enum is
defined in "State-machine link" (line 228). It names `prose-in-notes`, whose
reason is given in "Explanations in the model" (line 216). Proposal: keep the
section order and add a link in each of the two table cells, to
`#state-machine-link` and `#explanations-in-the-model`. Moving both sections
in front of the table would put the rules after their details, so the table
would no longer be the map.

**S-02. "Drift check" interrupts the `validate` thread.** The script table
(line 141) says `validate` "runs the lint rules below", but the drift check
(`compare`, the last slice) stands between the table and the lint rules.
Proposed order of the `## Design` subsections:

01. The core artifact set
02. Moving installed projects
03. The `entity-model` script
04. Lint rules
05. Explanations in the model
06. State-machine link
07. Pre-commit hook
08. Drift check
09. Factory wiring
10. Gigacron pilot

No heading changes, so no anchor breaks.

**S-03. The drift-check probe is described only in Scope.** Lines 284–287
define what the probe runs and what a failed probe does. That is design, and
the heading "Drift check" predicts it. Proposal: move the three sentences from
"The probe runs…" to "…(DEC-10)" to the end of "Drift check". Scope keeps the
slice order (lines 281–284) and ends with "The drift check opens with a probe;
see `[Drift check](#drift-check)`."

**S-04. Paragraph order inside "Drift check".** The output format (line 185)
comes after the `detect-test-regime` note. Proposed order: steps 1–4, the
output line format, `schema.comments`, the `schema.dump` fallback,
`detect-test-regime`, then the probe from S-03. The reader then learns what
`compare` prints right after how it works.

**S-05. "Design Details" holds facts that belong to the script.** All three
bullets (lines 313–318) describe the `entity-model` script: the pinned image,
the `validate` output format, and the `render` output path. The template marks
"Design Details" as optional. Proposal: move the bullets to the end of "The
`entity-model` script" and remove the `## Design Details` heading. No file
links to its anchor. Reject this item to keep the template heading.

## 2. Duplicates

**S-06. E10 is deferred twice.** Lines 203–204 and the deferred list (lines
291–292) both say E10 needs an SQL expression parser. Home: the deferred list.
Replace lines 203–204 with "E10 is deferred; see `[Scope](#scope)`." Saves about
12 words.

**S-07. The JSON Schema limit is stated twice.** Lines 208–209 ("This release
checks JSON Schema files only; another format gets a rule when a project needs
one") repeat the deferred item on line 305. Home: the deferred list. Keep "This
release checks JSON Schema files only (DEC-13)." and cut the rest. Saves about
10 words.

**S-08. "The parser drops comments" appears twice.** The `prose-in-notes` cell
(line 201) and "Explanations in the model" (line 216) both give the reason.
Home: "Explanations in the model". The cell becomes "The file has no `//` or
`/* */` comment. Every explanation is a note." plus the link from S-01. Saves
about 6 words.

**S-09. "Behaviour belongs in…" closes a paragraph that already said it.**
Line 224 repeats line 221 and the core principle "Structure only" (lines
83–85). Home: the core principle. Cut the last sentence of line 223–224.
Saves 12 words.

**S-10. Non-PostgreSQL dumps.** The deferred item (lines 302–304) repeats
lines 177–179 in its second sentence. Home: "Drift check". The deferred item
becomes "**Built-in dump steps for databases other than PostgreSQL.** A
built-in step follows when a project needs one." Saves about 6 words.

Checked and kept: the Scope list restates the Design sections, as the
template asks. The Summary orients and does not retell the Primer.

## 3. Record

**S-11. No decision stamps, dates, or "who decided" remarks** appear in the
target-state text. Open Questions holds nothing already decided. The file
uses the current Appendix layout. No item.

**S-12. History words for the sentence pass.** Line 250 "`entity-model.md` is
no longer written" and line 117 "Working output … moves to `docs/spec/work/`"
describe a change, not the target state. Proposed: "The factory writes no
`entity-model.md`." and "Working output … lives in `docs/spec/work/`." The
migration itself stays in "Moving installed projects".

## 4. Blocks to cut or shrink

No block is cut whole. Every section serves a planner. The savings come from
S-06 to S-10.

## 5. Inbound links

`grep -rn "entity-model-as-dbml.md#" docs` finds no anchor link. Two links
point at the file itself, from `docs/spec/work/todo.md` lines 84 and 89. No item
renames a heading except S-05, which removes `#design-details`; nothing links
to it. New internal links from S-01, S-03, and S-06 point at existing
headings.

## 6. Content fixes

The caller handed over no content points. These come from reading the text
against its sources.

**S-13. "PoC DEC-08" collides with this proposal's DEC-08.** Line 89 cites the
PoC's decision, but the reader finds a different DEC-08 in this file's
Appendix. Proposed: "(DEC-08 of the
[PoC proposal](../../poc/data_model_from_dsl/proposal-data-model-dsl-technical-poc.md#decisions))".
Source: the PoC proposal, line 246.

**S-14. "PoC", "acid slice", and case IDs such as E04 arrive undefined.** The
lint table (line 195) and Scope (line 281) use them; the reader has not met
them. Proposed sentence for Motivation, after "ADR-0024 chose DBML after a
technical PoC.": "The PoC ported the acid slice, nine entities of Gigacron's
model, and tested each tool on twelve broken variants of it, E01 to E12." Link
"PoC" to the PoC proposal and "acid slice" to
`poc/data_model_from_dsl/acid-slice.md`. Source: PoC proposal lines 95–97 and
`poc/data_model_from_dsl/validation/cases.tsv`. The stakeholder should check
the phrase "twelve broken variants" against `cases.tsv` before approval.

**S-15. "DiagramView" is used without a word on what it is** (lines 142, 329).
Proposed addition after the script table: "A `DiagramView` is a DBML block
that names a subset of tables for one diagram." Source:
`poc/data_model_from_dsl/views/dbml-views.sh`, line 4. The lector has not
checked the DBML documentation; mark the sentence for review.

## 7. Estimate

| Part                             | Now   | After  |
| -------------------------------- | ----- | ------ |
| Target-state text (lines 50–371) | 2,547 | ~2,560 |
| Record (Appendix, lines 372–407) | 894   | 894    |

The cuts save about 46 words. S-03, S-14, and S-15 add about 60. The
structural pass fixes order and single homes, not length.

## Possible contradictions (not resolved by this plan)

- **T-0006 status.** Line 73–74 says T-0006 "is still open", and the
  Completion Criteria (line 350) expect it to be resolved. `docs/spec/work/todo.md`
  line 56 already marks it `resolved`, with a 2026-10-30 revision to DBML.
- **Definition of the core.** Line 97–99 says every core file is one "that a
  gate checks". The table row for `CONTEXT.md` (line 115) names gate "none
  yet".
- **Containers only.** The core principle on lines 90–91 says every tool runs
  through `docker run --rm`. Step 2 of the drift check (lines 163–164) runs the
  project's `apply` command "in the project's own toolchain". The principle
  probably means factory tools only; the text does not say so.
- **Count of core artifacts.** DEC-08 says "nine core artifacts"; the table
  lists ten rows and the Completion Criteria count eight single files plus two
  folders. DEC-13 added `schemas/`, so the record may be correct; the lector
  leaves the record alone.
- **Summary scope.** The Summary (lines 56–58) lists tooling, agents and
  playbooks, and the pilot. It omits the core layout and the migration script,
  which Scope puts in the first release.
