# Survey Validation, Pass 3: Knowledge Graph State Of The Art

## Verdict

**Fail.** All five mechanical checks pass. The semantic review finds that the report still claims things its records do not show, in the concept histories and in the prose of section 3. Two findings are partly supported, 17 are supported, and none is unsupported. Of the 11 pass-2 corrections, 10 are fixed or settled by the script. The `owl:sameAs` correction (pass-2 number 2) is fixed in form but introduces a new unsupported sentence. Correct the seven items under "Required corrections" and run Step 5 again.

Validator: research orchestrator, in a role separate from the survey's researchers and report writer. The validator wrote, reviewed, and voted on no artifact of this survey. The validator ran the full inspection fresh, as `review-loop-discipline.md` requires, then checked each pass-2 correction.

## Mechanical results

| No. | Check                                                             | Result                                                                                                    |
| --- | ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| 1   | `source-record-check sources`                                     | Exit 0. 101 records checked, 0 failures, 6 area index files skipped.                                      |
| 2   | `concept-history-check` on the survey folder                      | Exit 0. 12 histories pass.                                                                                |
| 3   | `schema-validate` on the json block against the report schema     | Exit 0.                                                                                                   |
| 4   | Section 3 tables against `concept-history-check --table`          | Equal. Both tables appear line for line and without a gap.                                                |
| 5   | Every record ID in the report resolves to a file under `sources/` | Pass. All 89 distinct IDs in the report resolve, and all 83 distinct IDs in `source_record_refs` resolve. |

No script exited 2. The playbook and the brief agree on what must pass.

## History results

The script settles quotes, dates, counts, entry rule, and rank. The review below judges only what a script cannot. "Fails" means the entry does not show what it claims. "Partly" means the entry holds but needs a correction.

| Concept                  | Entry                           | Verdict | Reason                                                                                                                                                                                                                                             |
| ------------------------ | ------------------------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Nanopublications         | Steps 1 to 4, criticisms 1 to 3 | Pass    | Each quote shows its formulation. The A3-SR-08 criticism faults the web's lack of an immutability mechanism, and the paper presents it as the reason for trusty URIs.                                                                              |
| Nanopublications         | Step 5                          | Partly  | The quote shows only that trusty URIs are recommended. The three-graph structure is in A3-SR-10 but not in the quote.                                                                                                                              |
| Shape languages          | All entries                     | Pass    | The 2013 criticism is general and the report says so. Step 5 is a new version with new features.                                                                                                                                                   |
| AIF                      | All entries                     | Pass    | Both criticisms come from later papers, and both `drove_next: false` values match the dates.                                                                                                                                                       |
| `owl:sameAs`             | Step 2 formulation quote        | Fails   | The quote "Section 5: the Similarity Ontology that systematises them" is the researcher's gloss in A5-SR-04's record. It does not show a scale of identity and similarity relations. Use the abstract's "one point on a scale of similarity".      |
| `owl:sameAs`             | Steps 1, 3, 4                   | Pass    | The step 1 criticism is presented as the reason for the Similarity Ontology.                                                                                                                                                                       |
| Recursive shapes         | Step 5                          | Partly  | SHACL 2017 records a decision not to define recursion. It is the gap the next steps answer, not a formulation. Keep it, and label it as a gap step.                                                                                                |
| Recursive shapes         | Other entries                   | Pass    | The step 6 criticism of the stable model is presented in A4-SR-13 as the reason for the well-founded semantics.                                                                                                                                    |
| Constraint semantics     | Step 2 criticism quote          | Partly  | "Why we are not completely satisfied with existing solution" names a section heading in A4-SR-03. It states no fault. A4-SR-04 holds the counterexamples (Examples 4 and 5).                                                                       |
| Constraint semantics     | Other entries                   | Pass    | The step 1 criticism of OWL as a checking language is in A4-SR-02.                                                                                                                                                                                 |
| Property graph languages | Step 3 criticism                | Fails   | A1-SR-19 says schema support is limited "in the first version of the GQL Standard". That faults GQL, not GPML. Step 3 is GPML.                                                                                                                     |
| Property graph languages | Steps 4 and 6                   | Partly  | The quotes show that SQL/PGQ and GQL were published. Step 3 already names GPML as their shared core, so the quotes do not show a new formulation.                                                                                                  |
| Property graph languages | Steps 1, 2, 5                   | Pass    | The step 2 criticism "did not succeed on its own in establishing a standard" leads into GQL in A1-SR-18.                                                                                                                                           |
| Entity resolution        | Step 2 criticism                | Fails   | The quote "a sharp contrast to other EM systems" carries no content. In A5-SR-12 it concerns schema handling, and the paper's footnote says DeepMatcher can drop the same-schema requirement. The paper's reason for step 3 is pre-trained models. |
| Entity resolution        | Step 3 criticism                | Pass    | A5-SR-13 presents the robustness limit as the reason to try generative models.                                                                                                                                                                     |
| Entity resolution        | Step 4 quote                    | Partly  | The quote shows that prompts need tuning. It does not show zero-shot, in-context, and fine-tuned settings.                                                                                                                                         |
| OPM to PROV              | Step 1 `drove_next: true`       | Fails   | A3-SR-02 does not present its criticism as leading to PROV, and A3-SR-03 does not mention OPM. Section 3.9 itself says no record states that PROV replaced OPM.                                                                                    |
| OWL language design      | All entries                     | Pass    | "Conservative" is presented in A1-SR-11 as the reason for the extension. The step 2 and step 3 quotes are the record's own wording of the source.                                                                                                  |
| RDF-star                 | Step 2 criticism                | Partly  | The quote is the record's summary of the "seminal example" passage. "It" refers to that example, not to quoted triples as a whole.                                                                                                                 |
| RDF-star                 | Other entries                   | Pass    | The report states that the criticism behind the transparent design is not recorded.                                                                                                                                                                |
| Graph-based retrieval    | Step 1 quote and its criticism  | Partly  | Both quotes come from lines the record marks as a paraphrase or an extract. Replace them with source words, or mark them as paraphrase in the history.                                                                                             |
| Graph-based retrieval    | Steps 2 to 4                    | Pass    | The report names the vendor criticism as the only one.                                                                                                                                                                                             |

If corrections 2 and 3 below remove the property graph and entity resolution criticisms, each concept has one recorded criticism and falls below the entry rule. The script then ranks six concepts, not eight. The report copies the new table and its counts.

## Findings

Findings 8 to 19 are the twelve concepts in the order of the json block.

| No. | Finding                             | Verdict          | Reason                                                                                                                                                                                     |
| --- | ----------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Two main data models                | Supported        | A1-SR-20, A1-SR-07, A1-SR-08, A1-SR-01, A1-SR-18, and A1-SR-19 match, including the bounds on dates. A1-SR-09 is gone.                                                                     |
| 2   | Statements about statements         | Supported        | A2-SR-11 reports problems in two of five engines. A2-SR-05, A2-SR-08, and A2-SR-17 match the named graph and triple term statements.                                                       |
| 3   | Provenance and claims               | Supported        | A3-SR-03, A3-SR-04, A3-SR-10, A3-SR-13, and A3-SR-14 match. A3-SR-10 has no publication date, so "no dated source after 2021" holds.                                                       |
| 4   | Validation and world assumptions    | Supported        | A4-SR-01, A4-SR-02, A4-SR-08, A4-SR-11, A4-SR-14, A4-SR-15, and A4-SR-16 match.                                                                                                            |
| 5   | Time and identity                   | Supported        | The 51% figure, the survey wording, the SQL:2011 periods, and the four timestamps match their records. The count "six" is gone.                                                            |
| 6   | Language models                     | Supported        | A6-SR-01, A6-SR-07 to A6-SR-09, and A6-SR-13 to A6-SR-17 match. The vendor results are marked.                                                                                             |
| 7   | Standards status                    | Supported        | Every status, stage, and date matches A1-SR-01 to A1-SR-06.                                                                                                                                |
| 8   | Nanopublications                    | Supported        | A3-SR-05 to A3-SR-08, A3-SR-10, and A3-SR-13 match. The distribution step is excluded, as A3-SR-09 shows.                                                                                  |
| 9   | Shape languages                     | Supported        | A4-SR-05 to A4-SR-09, A4-SR-11, A4-SR-13, and A4-SR-16 match.                                                                                                                              |
| 10  | Argument Interchange Format         | Supported        | A3-SR-14 to A3-SR-17 match, and the 2007 disjointness limit is not counted as a criticism.                                                                                                 |
| 11  | `owl:sameAs`                        | Partly supported | "A 2020 paper does not cite Halpin's self-criticism" is not in A5-SR-05. The record says the paper cites Halpin et al. as reference [3] and does not show what it cites. See correction 1. |
| 12  | Recursive shapes                    | Supported        | A4-SR-07 to A4-SR-13, A4-SR-15, and A4-SR-16 match, and the gap on Corman et al. is stated.                                                                                                |
| 13  | Constraint semantics for OWL axioms | Supported        | A1-SR-10, A4-SR-01 to A4-SR-04, and A4-SR-14 match. Section 3.6 holds one unsupported detail. See correction 5.                                                                            |
| 14  | Property graph query languages      | Partly supported | "All sources are by participants" fails for A1-SR-04 and A1-SR-06, which are ISO catalogue records. The A1-SR-19 criticism is misplaced. See correction 2.                                 |
| 15  | Entity resolution                   | Supported        | A5-SR-11 to A5-SR-13 match the text of the finding. The history defect is in correction 3.                                                                                                 |
| 16  | OPM to PROV                         | Supported        | A3-SR-01 to A3-SR-04 match, and the finding says no record states that PROV replaced OPM.                                                                                                  |
| 17  | OWL language design                 | Supported        | A1-SR-10 to A1-SR-12 match, including "conservative".                                                                                                                                      |
| 18  | RDF-star to triple terms            | Supported        | A2-SR-09, A2-SR-14 to A2-SR-17 match, and the missing driver is a stated gap.                                                                                                              |
| 19  | Graph-based retrieval               | Supported        | A6-SR-03 to A6-SR-06, A6-SR-08, and A6-SR-09 match, and A6-SR-08 is scoped to three methods.                                                                                               |

Counts: 17 supported, 2 partly supported, 0 unsupported.

## Section 3 prose

The prose states no count, rank, or order that the histories do not hold. The statement "Both recorded criticisms are dated after the step that follows the criticized one" holds for AIF (2008 after 2007, 2011 after 2008). Four sentences state a fact that no record shows.

- Section 3.4 and finding 11: "A5-SR-05 does not cite Halpin's self-criticism". See correction 1.
- Section 3.4: "Halpin et al. do not criticize Ding et al." A5-SR-04's record shows no mention of Ding et al. It does not show that the paper omits one.
- Section 3.6: "without naming Tao et al." The record gives the cited works only as [6,14]. See correction 5.
- Section 3.7 and finding 14: "Participants wrote every source." See correction 2.

## Pass-2 corrections

| No. | Pass-2 correction                                    | Result                | Note                                                                                                                                                                                   |
| --- | ---------------------------------------------------- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | OPM to PROV fails the entry rule                     | Settled by the script | The concept sits below the entry rule with 2 rounds and 1 criticism.                                                                                                                   |
| 2   | Property graph step 1: "kept coming up"              | Fixed                 | Section 3.7 states it as the 2014 reason for the task force. The 2021 quote is the criticism. The step 3 criticism is a new defect.                                                    |
| 3   | Shape languages step 4: verbatim quote               | Settled by the script | The history quotes A4-SR-13 verbatim.                                                                                                                                                  |
| 4   | Section 2.4: "formal semantics in 2015"              | Fixed                 | Section 2.4 now gives the 2014 inference-rule semantics and the 2015 negation restriction.                                                                                             |
| 5   | Rounds: definition applied to shape languages and ER | Fixed                 | Entity resolution step 2 is now deep learning, and learned matchers are excluded. Shape languages count SHACL 1.2 as a new version and recursion does not. Distribution is not a step. |
| 6   | Rank order does not follow the rule                  | Settled by the script | The script computes the rank. A disagreement with the rule is a note for the stakeholder.                                                                                              |
| 7   | Section 5 point 4: step 4 keeps `owl:sameAs`         | Fixed                 | Point 4 states it and states that adoption of the similarity property is not recorded.                                                                                                 |
| 8   | AIF: not every transition has a criticism            | Fixed                 | Section 3.3 names the two criticisms and the two transitions that have none.                                                                                                           |
| 9   | Graph retrieval: "three representative methods"      | Fixed                 | Sections 2.6 and 3.12 and findings 6 and 19 use the scoped wording.                                                                                                                    |
| 10  | Section 2.5: remove "six"                            | Fixed                 | The sentence says "several ways".                                                                                                                                                      |
| 11  | Finding 1: drop A1-SR-09, date A1-SR-19              | Fixed                 | Finding 1 and section 3.7 state that the July 2023 paper predates the April 2024 GQL.                                                                                                  |

## Brief completion criteria

| No. | Criterion                                                              | Result | Note                                                                                                                                                                                                          |
| --- | ---------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Each of six areas has findings backed by recorded sources              | Met    | Findings 1 to 6 cover areas 1 to 6.                                                                                                                                                                           |
| 2   | At least five concepts with sequence and the criticism that drove each | Met    | Six or more concepts keep a `drove_next: true` criticism after corrections 2 to 4. They are nanopublications, shape languages, `owl:sameAs`, recursive shapes, constraint semantics, and OWL language design. |
| 3   | Standards status of RDF 1.2, SPARQL 1.2, GQL, SQL/PGQ                  | Met    | Finding 7 and section 4 match the standards bodies' records.                                                                                                                                                  |
| 4   | Candidates phrased as testable design claims                           | Met    | Nine claims each carry a refutation condition.                                                                                                                                                                |
| 5   | No claim that a concept survived refutation                            | Met    | A scan found no "survived", "admitted", or "validated claim". "Refuted if" appears only in the nine conditions of section 7.                                                                                  |

## Required corrections

1. `owl:sameAs`, section 3.4 and finding 11: drop "A5-SR-05 does not cite Halpin's self-criticism" and "Halpin et al. do not criticize Ding et al." State that A5-SR-05 cites Halpin et al. as reference [3] and that the record does not show whether it addresses the self-criticism. In the history, replace the step 2 quote with "can be viewed as encoding only one point on a scale of similarity" from A5-SR-04.
2. Property graph languages, section 3.7 and finding 14: remove the A1-SR-19 criticism from step 3, because it faults the first GQL version and not GPML. Change "Participants wrote every source" to say that the ISO records are catalogue entries. Rerun the script and copy the new table.
3. Entity resolution, history step 2: remove the Ditto "sharp contrast" criticism or set `drove_next` to false with a quote that shows the schema point. The record shows that Ditto's reason for step 3 is pre-trained models. Rerun the script and copy the new table and the counts in section 1.
4. OPM to PROV, history step 1: set `drove_next` to false, because no record presents the criticism as leading to PROV and section 3.9 says so.
5. Section 3.6: drop "without naming Tao et al." The record does not show who the cited works [6,14] are.
6. Graph-based retrieval, step 1: replace the quote and the criticism quote with source words, such as "RAG fails on global questions directed at an entire text corpus" (A6-SR-03). The cost criticism in A6-SR-06 is a paraphrase in its record, so mark it as one or drop it.
7. Constraint semantics, step 2 criticism: replace the A4-SR-03 section-heading quote with the A4-SR-04 text of Example 4, "is still satisfied by the semantics of (Motik, Horrocks, and Sattler 2007)".

## Notes for the stakeholder

These notes need no correction. The first two are for the stakeholder's decision.

- The finding titles "Hardened concept 1" to "Hardened concept 8" use the brief's word, but "hardened" can read as a verdict that the concept survived criticism. A title such as "Concept with several rounds" avoids the reading.
- The rank rule counts a recorded criticism whether or not its source presents it as leading to the next step. Nanopublications rank first with one such criticism (A3-SR-13) that drove no step.
- Recursive shapes step 5 and property graph steps 4 and 6 are counted as rounds although they record a gap and two publications. The rule counts them, and the script settles the count.
