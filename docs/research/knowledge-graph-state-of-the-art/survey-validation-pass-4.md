# Survey Validation, Pass 4: Knowledge Graph State Of The Art

## Verdict

**Fail.** All five mechanical checks pass, and all 7 pass-3 corrections are fixed. The fresh semantic review finds seven new defects. Three history steps carry a quote that shows nothing the step before does not already show. One `drove_next: true` overstates what its source says. Three sentences in section 3 state a fact that the cited records do not show, or deny one that a record shows. One of these defects changes a rank. Of the 19 findings, 17 are supported, 2 are partly supported, and none is unsupported. Correct the items under "Required corrections" and run Step 5 again.

Validator: research orchestrator, in a role separate from the survey's researchers and report writer. The validator wrote, reviewed, and voted on no artifact of this survey. The validator ran the full inspection fresh, as `review-loop-discipline.md` requires, then checked each pass-3 correction.

## Mechanical results

| No. | Check                                                             | Result                                                                                                       |
| --- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| 1   | `source-record-check sources`                                     | Exit 0. 101 records checked, 0 failures, 6 area index files skipped.                                         |
| 2   | `concept-history-check` on the survey folder                      | Exit 0. 12 histories pass.                                                                                   |
| 3   | `schema-validate` on the json block against the report schema     | Exit 0. A control run on an empty object exits 1 with 5 violations, so the check is live.                    |
| 4   | Section 3 tables against `concept-history-check --table`          | Equal. `diff` of the script output against report lines 70 to 88 prints nothing.                             |
| 5   | Every record ID in the report resolves to a file under `sources/` | Pass. All 89 distinct IDs in the report resolve. The 83 distinct IDs in `source_record_refs` are among them. |

No script exited 2. The playbook and the brief agree on what must pass.

## History results

The script settles quotes, dates, counts, entry rule, and rank. This review judges three things a script cannot: whether a quote shows what is new in its step, whether a step is a new formulation, and whether a `drove_next: true` criticism is one the source presents as leading to the next formulation. "Fails" means the entry does not show what it claims. "Partly" means the entry holds in part. Entries not listed pass.

| Concept                  | Entry                      | Verdict | Reason                                                                                                                                                                                                                                                                                                                      |
| ------------------------ | -------------------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Constraint semantics     | Step 4 (A4-SR-04, 2010)    | Fails   | The step is not shown to be a new formulation. Its quote, "an alternative IC semantics for OWL that allows applications to work with the CWA and the weak UNA", says what step 3 already says. "Chosen per axiom" is the researcher's word outside any quote. A4-SR-04's `source_family` says the paper "extends record 3". |
| Nanopublications         | Step 5 (A3-SR-10)          | Fails   | The quote shows only that trusty URIs are recommended, which is step 4. The new part, the three graphs, is not in the quote. A3-SR-10 quotes it elsewhere, for example "MUST contain a link to the assertion graph identifier".                                                                                             |
| RDF-star                 | Step 2 (A2-SR-14)          | Fails   | The quote "A quoted triple is a triple used as the subject or object of another triple" says what step 1 already says. Opacity and non-assertion, the new parts, appear in A2-SR-14 only in the researcher's words.                                                                                                         |
| Recursive shapes         | Step 5 criticism, A4-SR-12 | Partly  | A4-SR-12 says the open recursion semantics led to "proposals", meaning the supported model semantics. Its stated reason for the stable model is the criticism of those proposals: "This semantics is not constructive". The gap is the context, not the driver of step 6. Set `drove_next` to false.                        |
| Entity resolution        | Step 4 quote               | Partly  | The quote shows that prompts need tuning per model and dataset. That is new, but it does not show generative models directly. No correction is required.                                                                                                                                                                    |
| Nanopublications         | Step 3 criticism, A3-SR-08 | Pass    | The immutability criticism targets nanopublications in general, not AIDA in particular. The paper presents it as the reason for trusty URIs, so `drove_next: true` holds.                                                                                                                                                   |
| Property graph languages | Step 2 criticism, A1-SR-18 | Pass    | "did not succeed on its own in establishing a standard" leads in A1-SR-18 to the 2019 GQL project and the shared core GPML.                                                                                                                                                                                                 |
| `owl:sameAs`             | Step 2 quote               | Pass    | The quote is the pass-3 replacement. It is the same passage as the step 1 criticism, and it shows the scale of similarity that step 2 claims.                                                                                                                                                                               |
| All other entries        | All                        | Pass    | Each quote shows what is new in its step. Each other `drove_next: true` is presented by its source as the reason for the next step: A3-SR-07, A4-SR-02, A4-SR-06, A4-SR-13, A5-SR-04, and A5-SR-13.                                                                                                                         |

If correction 1 merges constraint semantics steps 3 and 4, the concept keeps 2 criticisms and enters with 4 rounds. Its criticism coverage then rises, so its rank changes. The script decides the new rank, and the report copies the new table and the order in section 1.

## Findings

Findings 8 to 19 are the twelve concepts in the order of the json block.

| No. | Finding                             | Verdict          | Reason                                                                                                                                                                                                       |
| --- | ----------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Two main data models                | Supported        | A1-SR-20, A1-SR-07, A1-SR-08, A1-SR-01, A1-SR-18, and A1-SR-19 match, with the date bounds. "Key-value pairs on edges" is the property graph definition and is not quoted in A1-SR-20.                       |
| 2   | Statements about statements         | Supported        | A2-SR-11 reports loading problems in two of five engines and the property path results. A2-SR-05, A2-SR-08, and A2-SR-17 match.                                                                              |
| 3   | Provenance and claims               | Supported        | A3-SR-03, A3-SR-04, A3-SR-10, A3-SR-13, and A3-SR-14 match.                                                                                                                                                  |
| 4   | Validation and world assumptions    | Supported        | A4-SR-01, A4-SR-02, A4-SR-08, A4-SR-11, A4-SR-14, A4-SR-15, and A4-SR-16 match.                                                                                                                              |
| 5   | Time and identity                   | Supported        | The 51% figure, the survey wording, the SQL:2011 periods, the four timestamps, and the entity resolution sequence match their records.                                                                       |
| 6   | Language models                     | Supported        | A6-SR-01, A6-SR-07 to A6-SR-09, and A6-SR-13 to A6-SR-17 match. Vendor results are marked.                                                                                                                   |
| 7   | Standards status                    | Supported        | Every status, stage, and date matches A1-SR-01 to A1-SR-06.                                                                                                                                                  |
| 8   | Nanopublications                    | Supported        | A3-SR-05 to A3-SR-08, A3-SR-10, and A3-SR-13 match. The step 5 quote defect is in the history, see correction 2.                                                                                             |
| 9   | Argument Interchange Format         | Supported        | A3-SR-14 to A3-SR-17 match. The dates and the one circle around Rahwan and Reed match the author lists.                                                                                                      |
| 10  | `owl:sameAs`                        | Partly supported | "The records do not show whether Ding et al. or Halpin et al. came first" is contradicted by A5-SR-03. Its `source_family` says the paper cites Halpin et al. (A5-SR-04) as reference [4]. See correction 6. |
| 11  | Shape languages                     | Supported        | A4-SR-05 to A4-SR-09, A4-SR-11, A4-SR-13, and A4-SR-16 match. The SHACL 1.2 features in A4-SR-16 are outside quotes, as the finding says.                                                                    |
| 12  | Recursive shapes                    | Supported        | A4-SR-07 to A4-SR-13, A4-SR-15, and A4-SR-16 match. The finding states no driver. The `drove_next` defect is in the history, see correction 4.                                                               |
| 13  | Constraint semantics for OWL axioms | Partly supported | "a per-axiom constraint reading (2010)" is presented as a step after the 2009 prototype. A4-SR-04 quotes nothing that the 2009 paper lacks, and the record says it extends A4-SR-03. See correction 1.       |
| 14  | OPM to PROV                         | Supported        | A3-SR-01 to A3-SR-04 match. The finding says no record states that PROV replaced OPM.                                                                                                                        |
| 15  | Property graph query languages      | Supported        | A1-SR-16 to A1-SR-19, A1-SR-04, and A1-SR-06 match the finding's text. The defect in section 3.8 is not in the finding, see correction 5.                                                                    |
| 16  | Graph-based retrieval               | Supported        | A6-SR-03 to A6-SR-06, A6-SR-08, and A6-SR-09 match, and the cost statement is excluded as a paraphrase.                                                                                                      |
| 17  | RDF-star to triple terms            | Supported        | A2-SR-09 and A2-SR-14 to A2-SR-17 match. Opacity is in the record's own summary of A2-SR-14, so the finding holds. The anchor defect is in the history, see correction 3.                                    |
| 18  | OWL language design                 | Supported        | A1-SR-10 to A1-SR-12 match.                                                                                                                                                                                  |
| 19  | Entity resolution                   | Supported        | A5-SR-11 to A5-SR-13 match, and the Ditto contrast is not counted.                                                                                                                                           |

Counts: 17 supported, 2 partly supported, 0 unsupported.

## Section 3 prose

Every count, rank, and step order in section 3 matches the histories and the script table. Three sentences state a fact that the records do not hold:

- Section 3.8: "SQL/PGQ (2023) and GQL (2024) publish the GPML core (A1-SR-06, A1-SR-04)." A1-SR-04 and A1-SR-06 are catalogue records, and their limitations say the technical content is paywalled. Only A1-SR-18, written before publication, names GPML as the shared core. Section 2.1 states that bound correctly. See correction 5.
- Section 3.3: "The records do not show which came first." A5-SR-03 cites Halpin et al. as reference [4]. See correction 6.
- Section 3.9: the report quotes "three representative methods" as source words. In A6-SR-08 the phrase stands outside the quoted passage. Section 2.6 gets it right. See correction 7.

Section 3.6 says "In 2010 Tao et al. chose the constraint reading per axiom". That sentence rests on the record's own words, not on a quote, and correction 1 covers it.

## Pass-3 corrections

| No. | Pass-3 correction                                          | Result | Note                                                                                                                                                                      |
| --- | ---------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `owl:sameAs`: drop two sentences, state [3], replace quote | Fixed  | Section 3.3 and finding 10 state reference [3] and what the record does not show. The step 2 quote is the abstract's wording. Correction 6 is a separate, older sentence. |
| 2   | Property graph: remove A1-SR-19 criticism, ISO wording     | Fixed  | Step 3 has no criticism. Section 3.8 says the ISO records are catalogue entries. SQL/PGQ and GQL are no longer steps. Correction 5 concerns a new sentence.               |
| 3   | Entity resolution: Ditto criticism                         | Fixed  | Step 2 has no criticism. The table and section 1 show six concepts above the entry rule.                                                                                  |
| 4   | OPM to PROV: `drove_next` false                            | Fixed  | Step 1 has `drove_next: false`.                                                                                                                                           |
| 5   | Section 3.6: drop "without naming Tao et al."              | Fixed  | The phrase is gone.                                                                                                                                                       |
| 6   | Graph retrieval: source words, drop paraphrase             | Fixed  | Step 1 quotes A6-SR-03's source words. The cost criticism is dropped, and section 3.9 says why.                                                                           |
| 7   | Constraint semantics: Example 4 as step 2 criticism        | Fixed  | Step 2 quotes Example 4 with `drove_next: false`, and section 3.6 explains the date.                                                                                      |

## Brief completion criteria

| No. | Criterion                                                              | Result | Note                                                                                                                                                                                    |
| --- | ---------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Each of six areas has findings backed by recorded sources              | Met    | Findings 1 to 6 cover areas 1 to 6.                                                                                                                                                     |
| 2   | At least five concepts with sequence and the criticism that drove each | Met    | Five concepts above the entry rule keep a `drove_next: true` criticism after correction 4: nanopublications, `owl:sameAs`, shape languages, recursive shapes, and constraint semantics. |
| 3   | Standards status of RDF 1.2, SPARQL 1.2, GQL, SQL/PGQ                  | Met    | Finding 7 and section 4 match the standards bodies' records.                                                                                                                            |
| 4   | Candidates phrased as testable design claims                           | Met    | Nine claims each carry a refutation condition.                                                                                                                                          |
| 5   | No claim that a concept survived refutation                            | Met    | A scan found no "survived", "admitted", or "validated claim". "Refuted if" appears only in the nine conditions of section 7.                                                            |

## Required corrections

1. Constraint semantics, steps 3 and 4: merge them into one formulation, or have a researcher add a quoted passage to A4-SR-04 that shows what the 2010 paper adds to the 2009 one. Then rerun the script, copy the new table, and update the order in section 1, section 3.6, and finding 13.
2. Nanopublications, step 5: replace the quote with a passage from A3-SR-10 that shows the three graphs, such as "MUST contain a link to the assertion graph identifier".
3. RDF-star, step 2: anchor opacity or non-assertion with source words from A2-SR-14, or drop the step and rerun the script. The concept stays below the entry rule either way.
4. Recursive shapes, step 5 criticism: set `drove_next` to false, because A4-SR-12 presents its criticism of the supported model proposals, not the open semantics, as the reason for stable models.
5. Section 3.8: replace "SQL/PGQ (2023) and GQL (2024) publish the GPML core (A1-SR-06, A1-SR-04)" with the A1-SR-18 bound: the 2021 paper names GPML as the shared core before either standard was published.
6. Section 3.3 and finding 10: replace "The records do not show which came first" with the fact that A5-SR-03 cites Halpin et al. as reference [4], which supports the order in the history.
7. Section 3.9: take the quotation marks off "three representative methods", as section 2.6 does.

## Notes for the stakeholder

These notes need no correction.

- The finding titles "Hardened concept 1" to "Hardened concept 6" use the brief's word. "Hardened" can read as a verdict that a concept survived criticism. Pass 3 raised the same point.
- The checker tests that each quote occurs in a quoted passage of its record. It cannot test whether a quote shows what is new in its step. Corrections 1 to 3 fall into that gap, so the semantic review stays the only check for them.
