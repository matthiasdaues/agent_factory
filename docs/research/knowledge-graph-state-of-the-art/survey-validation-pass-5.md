# Survey Validation, Pass 5: Knowledge Graph State Of The Art

## Verdict

**Fail.** All five mechanical checks pass, and all 7 pass-4 corrections are fixed. The fresh semantic review finds one blocking defect. Section 6 and the `evidence_gaps` list say that no record states why SHACL left recursion undefined. Record A4-SR-16 quotes the reason, and its limitations say so. No earlier fix created this defect. The sentence has stood since pass 1, and all earlier passes missed it. All 19 findings are supported. Every history entry passes or passes in part, and none needs a correction. Correct the one item under "Required corrections" and run Step 5 again.

Validator: research orchestrator, in a role separate from the survey's researchers and report writer. The validator wrote, reviewed, and voted on no artifact of this survey. The validator ran the full inspection fresh, as `review-loop-discipline.md` requires, then checked each pass-4 correction.

## Mechanical results

| No. | Check                                                             | Result                                                                                                                                        |
| --- | ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `source-record-check sources`                                     | Exit 0. 101 records checked, 0 failures, 6 area index files skipped.                                                                          |
| 2   | `concept-history-check` on the survey folder                      | Exit 0. 12 histories pass.                                                                                                                    |
| 3   | `schema-validate` on the json block against the report schema     | Exit 0. A control run on `{"findings":[]}` exits 1 with 4 violations, so the check is live.                                                   |
| 4   | Section 3 tables against `concept-history-check --table`          | Equal. `diff` of the script output against report lines 70 to 88 prints nothing, blank lines excluded.                                        |
| 5   | Every record ID in the report resolves to a file under `sources/` | Pass. All 89 distinct IDs in the report resolve.                                                                                              |
| -   | Extra check: report quotes against the records                    | Pass. Every double-quoted phrase in sections 1 to 6 lies inside a double-quoted passage of the Evidence section of a record the report cites. |

No script exited 2. The playbook and the brief agree on what must pass.

## History results

The script settles quotes, dates, counts, entry rule, and rank. This review judges three things a script cannot: whether a quote shows what is new in its step, whether a step is a new formulation, and whether a `drove_next: true` criticism is one the source presents as leading to the next formulation. "Partly" means the entry holds in part and needs no correction. Entries not listed pass.

| Concept              | Entry                   | Verdict | Reason                                                                                                                                                                                                                                                                                           |
| -------------------- | ----------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Nanopublications     | Step 5 quote (A3-SR-10) | Partly  | "MUST contain a link to the assertion graph identifier" shows a provenance graph apart from an assertion graph. That is new against the 2010 statement and annotation model. The publication info graph is in a separate quoted passage of A3-SR-10, not in the quote. The rank does not change. |
| Constraint semantics | Step 1 quote (A1-SR-10) | Partly  | The quote shows the OWL DL guarantees, not the open-world reading the later steps react to. The step's formulation and section 3.3 both state this bound, and section 3.3 points to A4-SR-01 for the open-world assumption.                                                                      |
| Entity resolution    | Step 4 quote (A5-SR-13) | Partly  | Unchanged since pass 4. The quote shows that prompts need tuning per model and dataset, not generative models directly.                                                                                                                                                                          |
| All other entries    | All                     | Pass    | Each quote shows what is new in its step, and each step is a new formulation. Each `drove_next: true` is presented by its source as the reason for the next step: A3-SR-07, A3-SR-08, A4-SR-02, A4-SR-06, A4-SR-13, A5-SR-04, A5-SR-13, and A1-SR-18.                                            |

The three pass-4 history defects are gone. Constraint semantics steps 3 and 4 are one step. The RDF-star history drops A2-SR-14 as a step. The recursive shapes step 5 criticism has `drove_next: false`.

## Findings

Findings 8 to 19 are the twelve concepts in the order of the json block.

| No. | Finding                             | Verdict   | Reason                                                                                                                                                                     |
| --- | ----------------------------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Two main data models                | Supported | A1-SR-20, A1-SR-07, A1-SR-08, A1-SR-01, A1-SR-18, and A1-SR-19 match, with the date bounds of A1-SR-18 and A1-SR-19.                                                       |
| 2   | Statements about statements         | Supported | A2-SR-11 reports loading problems in 4store and GraphDB out of five engines, caused by their indexing schemes. A2-SR-05, A2-SR-08, A2-SR-12, A2-SR-13, and A2-SR-17 match. |
| 3   | Provenance and claims               | Supported | A3-SR-03, A3-SR-04, A3-SR-10, A3-SR-13, and A3-SR-14 match. The only dated area 3 record from 2021 is A3-SR-11, so "no dated source after 2021" holds.                     |
| 4   | Validation and world assumptions    | Supported | A4-SR-01, A4-SR-02, A4-SR-08, A4-SR-11, A4-SR-14, A4-SR-15, and A4-SR-16 match. The defect on the recursion reason is in section 6, see correction 1.                      |
| 5   | Time and identity                   | Supported | The 51% figure, the survey wording, the SQL:2011 periods, the four timestamps, and the entity resolution sequence match A5-SR-01 to A5-SR-13.                              |
| 6   | Language models                     | Supported | A6-SR-01, A6-SR-07 to A6-SR-09, and A6-SR-13 to A6-SR-17 match. Vendor results are marked.                                                                                 |
| 7   | Standards status                    | Supported | Every status, stage, and date matches A1-SR-01 to A1-SR-06.                                                                                                                |
| 8   | Nanopublications                    | Supported | A3-SR-05 to A3-SR-08, A3-SR-10, and A3-SR-13 match. The micropublication authors share no author with the nanopublication papers.                                          |
| 9   | Argument Interchange Format         | Supported | A3-SR-14 to A3-SR-17 match. Both critics, Reed et al. 2008 and Rahwan et al. 2011, share Reed or Rahwan with the 2007 paper.                                               |
| 10  | `owl:sameAs`                        | Supported | A5-SR-03 cites Halpin et al. as reference [4], and A5-SR-05 cites them as reference [3], as the finding says.                                                              |
| 11  | Shape languages                     | Supported | A4-SR-05 to A4-SR-09, A4-SR-11, A4-SR-13, and A4-SR-16 match. A4-SR-06 records IBM's plan to submit Resource Shape, which supports the step 1 driver.                      |
| 12  | Recursive shapes                    | Supported | A4-SR-07 to A4-SR-13, A4-SR-15, and A4-SR-16 match. The finding gives no driver for the stable model step, in line with the history.                                       |
| 13  | Constraint semantics for OWL axioms | Supported | A4-SR-03 and A4-SR-04 share authors, and no quoted passage of A4-SR-04 shows what it adds, so the merged step holds. Example 4 matches A4-SR-04.                           |
| 14  | OPM to PROV                         | Supported | A3-SR-01 to A3-SR-04 match. The OPM editors Gil, Groth, Miles, and Moreau also edited the Incubator report.                                                                |
| 15  | Property graph query languages      | Supported | A1-SR-16 to A1-SR-19, A1-SR-04, and A1-SR-06 match. Section 3.8 now bounds GPML by the 2021 paper.                                                                         |
| 16  | Graph-based retrieval               | Supported | A6-SR-03 to A6-SR-06, A6-SR-08, and A6-SR-09 match, and the cost statement is excluded as a paraphrase.                                                                    |
| 17  | RDF-star to triple terms            | Supported | A2-SR-09 and A2-SR-14 to A2-SR-17 match. In A2-SR-14, opacity and non-assertion appear only outside quotes, as the finding says.                                           |
| 18  | OWL language design                 | Supported | A1-SR-10 to A1-SR-12 match. A1-SR-11 and A1-SR-12 quote limits of OWL 1, not the new constructs.                                                                           |
| 19  | Entity resolution                   | Supported | A5-SR-11 to A5-SR-13 match, and the Ditto contrast is not counted.                                                                                                         |

Counts: 19 supported, 0 partly supported, 0 unsupported.

## Section 3 prose

Every count, rank, step order, and stated cause in sections 3.1 to 3.12 matches the histories and the script table. Section 1 lists the six concepts in the script's order. One sentence outside section 3 states a gap that a record fills:

- Section 6, "Evidence gaps": "No record states why SHACL left recursion undefined in 2017". The json `evidence_gaps` list repeats it. A4-SR-16 quotes the SHACL 1.2 Core draft: "By leaving recursion undefined, implementations may choose to not support recursion so that they can issue a static set of SPARQL queries (against SPARQL end points) without having to support cycles." The record's limitations say: "The reasons for the 2017 choice are given only in the non-normative paragraph quoted below." A4-SR-13 also quotes that recursion "was intentionally left unspecified". See correction 1.

One wording in section 3 is imprecise but not wrong. "Criticism coverage" is defined as "the share of formulations followed by a recorded criticism". The script divides by the formulations other than the last. So OPM to PROV shows 2 rounds, 1 criticism, and 100%. The report copies the script header's wording. A reader who checks the OPM row by the stated definition expects 50%. See suggestion 2.

## Pass-4 corrections

| No. | Pass-4 correction                                                 | Result | Note                                                                                                                                            |
| --- | ----------------------------------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Constraint semantics: merge steps 3 and 4                         | Fixed  | The history has 4 steps. The script ranks the concept third, and section 1, section 3.3, and finding 13 follow that rank and explain the merge. |
| 2   | Nanopublications, step 5: replace the quote                       | Fixed  | The quote is the one pass 4 proposed. It shows the assertion and provenance graphs, see the history results.                                    |
| 3   | RDF-star, step 2: anchor opacity or drop the step                 | Fixed  | The step is dropped. The script settles the new count of 2 rounds, and section 3.10 says why A2-SR-14 is not a step.                            |
| 4   | Recursive shapes, step 5 criticism: `drove_next` false            | Fixed  | Step 5 has `drove_next: false`. Section 3.6 and finding 12 say that A4-SR-12 gives its criticism of the earlier proposals as its reason.        |
| 5   | Section 3.8: bound GPML by A1-SR-18                               | Fixed  | Section 3.8 says the 2021 paper names GPML as the shared core before either standard was published.                                             |
| 6   | `owl:sameAs`: state reference [4]                                 | Fixed  | Section 3.4 and finding 10 say that A5-SR-03 cites Halpin et al. as reference [4], which supports the order in the history.                     |
| 7   | Section 3.9: no quotation marks on "three representative methods" | Fixed  | Section 3.9 quotes only "much more moderate than reported previously".                                                                          |

## Brief completion criteria

| No. | Criterion                                                              | Result | Note                                                                                                                                                                                                                               |
| --- | ---------------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Each of six areas has findings backed by recorded sources              | Met    | Findings 1 to 6 cover areas 1 to 6.                                                                                                                                                                                                |
| 2   | At least five concepts with sequence and the criticism that drove each | Met    | Five concepts above the entry rule have at least one `drove_next: true` criticism: nanopublications, constraint semantics, `owl:sameAs`, shape languages, and recursive shapes. AIF has none. Section 3 names each missing driver. |
| 3   | Standards status of RDF 1.2, SPARQL 1.2, GQL, SQL/PGQ                  | Met    | Finding 7 and section 4 match the standards bodies' records.                                                                                                                                                                       |
| 4   | Candidates phrased as testable design claims                           | Met    | Nine claims each carry a refutation condition.                                                                                                                                                                                     |
| 5   | No claim that a concept survived refutation                            | Met    | A scan found no "survived", "admitted", or "validated claim". "Refuted if" appears only in the nine conditions of section 7.                                                                                                       |

## Required corrections

Each correction carries its class under `finding-classification.md`. The report is a document of the document class. It is not in use, because no story or code encodes it.

1. **Section 6 and `evidence_gaps`: the reason SHACL left recursion undefined.** Replace "No record states why SHACL left recursion undefined in 2017" and the matching `evidence_gaps` entry with what the records hold. The 2017 text read gives no reason (A4-SR-11). The SHACL 1.2 Core draft gives one in a non-normative paragraph: implementations can then issue a static set of SPARQL queries without supporting cycles (A4-SR-16). Category `defect`, type `incorrect`. `harms_downstream`: no, the report is not in use. `fails_purpose`: yes, because the report tells the falsification study that a reason is missing while a record holds it. Severity `major`, blocking. No earlier fix created it. The sentence predates pass 1, and A4-SR-16 was recorded before pass 1.
2. **Section 3: the definition of "Criticism coverage".** Optionally define it as the share of formulations, except the last, that carry a recorded criticism. Category `suggestion`. `harms_downstream`: no. `fails_purpose`: no, because the table is the script output and the ranks hold. `raises_cost`: no measurable cost. Severity `note`, not blocking. No earlier fix created it. The same wording is in the script header, so the stakeholder may prefer to fix it there.

## Notes for the stakeholder

These notes need no correction.

- The finding titles "Hardened concept 1" to "Hardened concept 6" and the heading of section 3 use the brief's word. "Hardened" can read as a verdict that a concept survived criticism. Passes 3 and 4 raised the same point.
- Completion criterion 2 asks for "the criticism that drove each change". No concept has a recorded driver for every change. The report states each missing driver, so this review reads the criterion as met. If the stakeholder reads it strictly, no concept meets it.
- Section 5, point 2, says that AIF's history shows a need for disjoint node types. A3-SR-15 supports it: "the core AIF requires that all classes of edges and nodes are disjoint". Section 3.2 calls the same sentence a limit of the 2007 paper's own choice. Both statements hold, but a citation of A3-SR-15 in point 2 would let a reader check it directly.

## Stakeholder Decision, 2026-11-17

The stakeholder accepted the survey without a pass 6. Both required corrections were made in `survey-report.md`, and the parent session checked them against the records:

1. Line 170 and the `evidence_gaps` entry now give the reason from A4-SR-16. The quoted words "issue a static set of SPARQL queries" stand inside the record's quoted passage. Both places say the 2017 minutes were not read.
2. Line 68 now defines "Criticism coverage" as the share of formulations, excluding the latest one, that are followed by a recorded criticism.

After the fix, `source-record-check` and `concept-history-check` exit 0, the report's json block passes `schema-validate`, and the section 3 tables equal the `--table` output. The three notes above stay open for the stakeholder.
