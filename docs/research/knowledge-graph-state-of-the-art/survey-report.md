# Survey Report: Knowledge Graph State Of The Art

This report answers the two questions of [research-brief.json](research-brief.json) from the source records under [sources/](sources/) only. It reports what the records document: a concept was formulated, criticized, and reformulated a number of times. Whether any concept holds up is for the later falsification study.

A record ID such as `A4-SR-08` names the file `sources/area-4/A4-SR-08-*.md`. Each step in section 3 carries a mark when its source is weak:

- **(gap)**: no record covers the step.
- **(secondary)**: the step rests on a source that reports another source.
- **(abstract only)**: only the abstract or a one-page summary was read.
- **(extract)**: the page was read through a fetch tool that returns a model-written extract, so quotes may be paraphrases.

## 1. Answer

**State of the art in 2026.** Two data models dominate. RDF has W3C standards, and RDF 1.2 adds triple terms for statements about statements, but it is still a Candidate Recommendation Draft. SPARQL 1.2 is a Working Draft. Property graphs have two published ISO standards, SQL/PGQ (2023) and GQL (2024), and both are under revision. Provenance has W3C PROV (2013) and the nanopublication pattern. Validation has SHACL and ShEx, but the meaning of recursive shapes is still undefined in SHACL. LLM-built graphs and GraphRAG help on some tasks and not on others, and agent memory graphs rest mainly on vendor reports.

**Concepts with several documented rounds.** Twelve concepts have a checked history file, and six meet the entry rule of `concept-history-check`. The script ranks them in this order: nanopublication structure and identity, the Argument Interchange Format, constraint semantics for OWL axioms, the identity meaning of `owl:sameAs`, shape languages for RDF validation, and the semantics of recursive shapes. Section 3 shows the full table.

## 2. State of the art by area

### 2.1 Data models

Knowledge graphs use two main models. A survey says an RDF graph needs an extra node or a named graph to annotate an edge, while a property graph carries key-value pairs on the edge. It says the two convert without loss (A1-SR-20, secondary).

RDF 1.1 (2014) made identifiers IRIs and added datasets with named graphs (A1-SR-07, A1-SR-08). The RDF 1.2 draft adds the triple term, "an RDF triple used as an RDF term within another triple" (A1-SR-01).

GQL and SQL/PGQ share one pattern-matching core, called GPML, according to a 2021 paper that predates both published standards (A1-SR-18). Section 4 gives the status of each standard.

### 2.2 Statements about statements

RDF has a reification vocabulary in the 2004 Recommendation; its first introduction is not recorded. Both the 2004 and the 2014 texts state that a reification neither entails nor is entailed by the triple it describes (A2-SR-01, A2-SR-02). A named graph in RDF 1.1 is only a syntactic pair of a name and a graph, and RDF sets no restriction on what the name denotes (A2-SR-05). The Wikidata team wrote in 2014 that no standard gives semantics to graph names (A2-SR-08).

A 2015 study on Wikidata data found "no clear winner between standard reification, n-ary predicates and named graphs." Singleton properties broke indexing in two of five engines (A2-SR-11).

The RDF 1.2 draft attaches data to a statement through a reifier. The reifier is linked by `rdf:reifies` to a triple term, the triple term may stay unasserted, and its terms are transparent (A2-SR-17). Wikidata models a claim as a main value with qualifiers, references, and a rank, and its RDF export gives each statement its own node (A2-SR-07, A2-SR-08, A2-SR-12, A2-SR-13). For edge properties in property graphs, only one abstract was read (A2-SR-10, abstract only).

### 2.3 Provenance and claims

W3C published PROV on 30 April 2013 as twelve documents. Four are Recommendations: PROV-O, PROV-DM, PROV-N, and PROV-CONSTRAINTS (A3-SR-03, extract). PROV-DM names relations such as `wasGeneratedBy`, `used`, and `wasDerivedFrom` (A3-SR-04, extract).

A nanopublication has three named graphs in the current guidelines: an assertion, the provenance of the assertion, and publication information. Trusty URIs, which put a hash of the content into the identifier, are the recommended integrity key (A3-SR-10, extract). A micropublication ranges from "any statement with an attribution" to a knowledge base with support and challenge links and evidence graphs (A3-SR-13, extract).

The Argument Interchange Format (AIF) models arguments with information nodes for claims and scheme nodes for inference, preference, and conflict (A3-SR-14). It has had an RDF Schema form, a dialogue extension, and an OWL form (A3-SR-15, A3-SR-16, A3-SR-17). No dated source in this area is from after 2021.

### 2.4 Validation and world assumptions

OWL treats a missing fact as unknown, and it does not assume that different names mean different things (A4-SR-01). Authors argued from 2007 on that this stops OWL axioms from acting as data checks (A4-SR-02, A4-SR-03).

SHACL became a W3C Recommendation in 2017 (A4-SR-11). ShEx was proposed in 2014 with a formal semantics by inference rules (A4-SR-08). A 2015 paper restricts negation in recursive ShEx schemas "to guarantee well-defined semantics" (A4-SR-10). SHACL leaves the meaning of recursive shapes to implementations, and the SHACL 1.2 Core draft of 16 November 2026 keeps that position (A4-SR-11, A4-SR-16). A 2026 test found that "current tools implicitly commit to different semantics" (A4-SR-15). How to validate SHACL together with an OWL ontology is still a research problem in 2026 (A4-SR-14).

### 2.5 Time and identity

`owl:sameAs` states that two URI references refer to the same thing (A5-SR-01, extract). Linked Data publishers also used it for weaker relations. In one rater study, about 51% (plus or minus 21%) of sampled links looked correct (A5-SR-04). A later approach keeps the property and gives each link an error degree from the structure of its identity cluster (A5-SR-05).

Temporal RDF started in 2005 as triples labelled with validity intervals (A5-SR-06). A 2021 survey lists several ways to attach time to an edge and calls named graphs "the most flexible" (A5-SR-09, secondary). SQL:2011 has a system-time period and an application-time period per row, and the literature calls a table with both bitemporal (A5-SR-08, secondary). A 2025 agent memory system stores four timestamps per graph edge and lets an LLM end an edge's validity when a new edge contradicts it (A5-SR-10). The vendor paper reports no check of how often the invalidation is right.

Entity resolution moved from probabilistic comparison vectors to learned matchers, then to fine-tuned language models, then to prompted language models (A5-SR-11, secondary; A5-SR-12; A5-SR-13). Checking links after they are made is less studied (A5-SR-14).

### 2.6 Construction and use with language models

An early test judged GPT-4 better "as inference assistants rather than few-shot information extractors", and its graphs still needed manual checks (A6-SR-01, extract). A benchmark measures ontology conformance and hallucination (A6-SR-02, abstract only).

GraphRAG builds an LLM-extracted entity graph with community summaries to answer questions about a whole corpus (A6-SR-03, abstract only). Variants add Personalized PageRank (A6-SR-04), incremental updates (A6-SR-05), and deferred LLM use (A6-SR-06). Independent evaluations found that the two approaches have "distinct strengths" (A6-SR-07), that gains on three representative methods are "much more moderate than reported previously" (A6-SR-08), and that basic RAG matches or beats GraphRAG on simple fact retrieval (A6-SR-09).

Agent memory moved from a natural-language record (A6-SR-10) to tiered memory (A6-SR-11) to graph memory, with vendor-reported results (A6-SR-13, A6-SR-14). A 2026 benchmark says memory benchmarks "primarily focus on surface-level factual recall" (A6-SR-15). The one embedded store recorded, Kuzu, offers Cypher and vector search, and its repository was archived on 10 October 2025 (A6-SR-16, A6-SR-17).

## 3. Hardened concepts

Each concept has a history file under [histories/](histories/). A history step is one new formulation with a quote from its record, and each step carries the criticism recorded against it or none. Every quote lies inside a passage the record quotes from its source. The script `concept-history-check` checks every quote against its record file, checks the dates, and applies the entry rule and the rank defined in its header. The tables below are its `--table` output. "Criticism coverage" is the share of formulations, excluding the latest one, that are followed by a recorded criticism.

| Rank | Concept                                | Area | Rounds | Criticisms | Primary anchors | Criticism coverage | Records                                                              |
| ---- | -------------------------------------- | ---- | ------ | ---------- | --------------- | ------------------ | -------------------------------------------------------------------- |
| 1    | Nanopublication structure and identity | 3    | 5      | 3          | 100%            | 75%                | A3-SR-05, A3-SR-06, A3-SR-07, A3-SR-08, A3-SR-13, A3-SR-10           |
| 2    | Argument Interchange Format            | 3    | 4      | 2          | 100%            | 67%                | A3-SR-14, A3-SR-16, A3-SR-15, A3-SR-17                               |
| 3    | Constraint semantics for OWL axioms    | 4    | 4      | 2          | 100%            | 67%                | A1-SR-10, A4-SR-02, A4-SR-04, A4-SR-03, A4-SR-14                     |
| 4    | Identity meaning of owl:sameAs         | 5    | 4      | 2          | 100%            | 67%                | A5-SR-01, A5-SR-04, A5-SR-03, A5-SR-05                               |
| 5    | Shape languages for RDF validation     | 4    | 4      | 3          | 100%            | 67%                | A4-SR-05, A4-SR-06, A4-SR-07, A4-SR-09, A4-SR-08, A4-SR-11, A4-SR-13 |
| 6    | Semantics of recursive shapes          | 4    | 7      | 3          | 100%            | 50%                | A4-SR-07, A4-SR-09, A4-SR-08, A4-SR-10, A4-SR-11, A4-SR-12, A4-SR-13 |

Below the entry rule (at least 3 formulations and 2 recorded criticisms):

| Rank | Concept                                   | Area | Rounds | Criticisms | Primary anchors | Criticism coverage | Records                                |
| ---- | ----------------------------------------- | ---- | ------ | ---------- | --------------- | ------------------ | -------------------------------------- |
| -    | Provenance interchange model, OPM to PROV | 3    | 2      | 1          | 100%            | 100%               | A3-SR-01, A3-SR-02, A3-SR-03           |
| -    | Property graph query languages            | 1    | 4      | 1          | 100%            | 33%                | A1-SR-17, A1-SR-16, A1-SR-18, A1-SR-19 |
| -    | Graph-based retrieval (GraphRAG)          | 6    | 4      | 0          | 100%            | 0%                 | A6-SR-03, A6-SR-04, A6-SR-05, A6-SR-06 |
| -    | RDF-star to RDF 1.2 triple terms          | 2    | 2      | 0          | 100%            | 0%                 | A2-SR-09, A2-SR-17                     |
| -    | OWL language design                       | 1    | 1      | 1          | 100%            | 0%                 | A1-SR-10, A1-SR-11                     |
| -    | Entity resolution methods                 | 5    | 4      | 1          | 60%             | 33%                | A5-SR-11, A5-SR-12, A5-SR-13           |

The area indexes name further concepts, such as standard reification, named graphs, singleton properties, n-ary relations, the Wikidata statement model, temporal RDF, and agent memory. They have no history file, so the script does not rate them. Section 2 reports what their records show.

Sections 3.1 to 3.6 follow the first table. Sections 3.7 to 3.12 cover the concepts below the entry rule, in the order of the second table.

### 3.1 Nanopublication structure and identity

The history runs from richly annotated statements (A3-SR-05, 2009) to a named-graph model (A3-SR-06, 2010), informal AIDA assertions (A3-SR-07, 2013), trusty URIs (A3-SR-08, 2014), and the three-graph guidelines (A3-SR-10, extract). Kuhn et al. call a required formal assertion "unrealistic in many cases", and the trusty URI paper says the web "has no mechanism to enforce" immutability. Both papers present that criticism as the reason for their own step. The micropublication authors, outside this research circle, say nanopublications "model only the indicated statement" (A3-SR-13, extract). The guidelines page is undated, so its history date is the retrieval date. The server network of 2014 to 2015 (A3-SR-09) changes distribution, not structure, and is not a step.

### 3.2 Argument Interchange Format

The abstract model of 2006 (A3-SR-14) was written in RDF Schema with argumentation schemes in 2007 (A3-SR-15), extended to dialogue in 2008 (A3-SR-16), and recast in OWL in 2011 (A3-SR-17). Both recorded criticisms are dated after the step that follows the criticized one. The 2008 paper says the 2006 form "had not integrated modelling of dialogue". The 2011 paper says the 2007 form "causes some redundancy at the instance level". The 2007 sentence that "disjointedness cannot be expressed in RDFS" is a limit of that paper's own choice, not a criticism of the 2006 model. All critics belong to one circle around Rahwan and Reed.

### 3.3 Constraint semantics for OWL axioms

The history starts at OWL 1 (A1-SR-10, extract). That record does not show the open-world assumption. The OWL 2 Primer of 2012, a non-normative tutorial, states it (A4-SR-01). Motik et al. wrote in 2007 that OWL cannot express "integrity constraints that behave as checks" and proposed a constraint TBox under minimal models (A4-SR-02). In 2009 Sirin and Tao placed their work "in line with recent research by Motik et al." and reduced checks to SPARQL (A4-SR-03). In 2010 Tao et al. present "an alternative IC semantics for OWL that allows applications to work with the CWA and the weak UNA" (A4-SR-04). No quoted passage shows what the 2010 paper adds to the 2009 one, so the history merges the two into one step. The 2010 Example 4 shows that a constraint requiring a known producer "is still satisfied by the semantics of (Motik, Horrocks, and Sattler 2007)" although no producer is known. The history records this as the criticism of the 2007 step. It is dated after the 2009 step, so the history does not count it as the driver of that step. In 2026 Oudshoorn et al. proposed core universal models and said minimal models "give very weak semantics" with negation (A4-SR-14). No criticism of the merged 2009 to 2010 step or of the 2026 step is recorded.

### 3.4 Identity meaning of `owl:sameAs`

OWL defines `owl:sameAs` as strict identity (A5-SR-01, extract). Halpin et al. say it encodes "only one point on a scale of similarity" and is "often too strong" for many current uses (A5-SR-04). They propose a Similarity Ontology and then judge it "too large of a design space to be reliably deployed". Ding et al. advise choosing an interpretation per use (A5-SR-03). Raad et al. keep the property and score each link by an error degree (A5-SR-05). A5-SR-04 has a year-only date. A5-SR-03 cites Halpin et al. as reference [4], which supports the order in the history. A5-SR-05 cites Halpin et al. as reference [3]. Its record does not show whether the paper addresses Halpin's self-criticism. No record shows adoption of the simple similarity property that Halpin et al. suggest.

### 3.5 Shape languages for RDF validation

SPIN attaches SPARQL queries to classes (A4-SR-05, 2011). The 2013 workshop agreed that "SPARQL does not constitute a complete solution" (A4-SR-06). That report criticizes SPARQL-based validation in general and names no tool. Resource Shape 2.0 (A4-SR-07) and ShEx (A4-SR-08) followed in 2014, and SHACL in 2017 (A4-SR-11). Ryman's 2015 remark that neither member submission defined recursion precisely (A4-SR-09) is a later assessment, not a driver. A 2024 paper notes that SHACL defines "the semantics of non-recursive constraints only" (A4-SR-13). The SHACL 1.2 Core draft of 2026 lists new features such as node expressions (A4-SR-16). Its record quotes none of these features, so the history does not count the draft as a step. No record states that SHACL descends from SPIN or ShEx.

### 3.6 Semantics of recursive shapes

Resource Shape 2.0 lets shapes refer to shapes (A4-SR-07). That the text gives no rule for cycles is the researcher's reading. ShEx adds the current type to the typing context (A4-SR-08). In 2015 Ryman defines recursion for Resource Shape (A4-SR-09), and the ShEx authors forbid negation through cycles (A4-SR-10). Ryman's remark that it is "not clear" whether ShEx usage fits his framework concerns his framework, not a flaw in ShEx. SHACL 2017 leaves recursion undefined (A4-SR-11). The history labels this step as a gap step: it records a decision not to define recursion, and the next steps answer that gap. The stable model paper records that gap, but it presents its criticism of earlier semantics proposals as the reason for stable models (A4-SR-12, abstract only). So the history does not count the gap as the driver. The well-founded paper says stable models still have "the intractability (specifically, NP-hardness) of validation" (A4-SR-13). The supported model semantics of Corman et al. (2018) has no record, so it is not a step. A 2026 comparison finds that validators "implicitly commit to different semantics" (A4-SR-15). That comparison and the SHACL 1.2 draft (A4-SR-16) add no formulation.

### 3.7 Provenance interchange model, OPM to PROV

OPM (A3-SR-01) and PROV (A3-SR-03, extract) are the two formulations. The Incubator report says OPM "cannot be used to represent" provenance of changing Web resources, and PROV's design "stems from" its recommendations (A3-SR-02, A3-SR-03, both extract). No record presents the Incubator criticism as the reason for PROV, and no record states that PROV replaced OPM. The OPM authors also edited the Incubator report.

### 3.8 Property graph query languages

G-CORE proposes "a closed query language on Property Graphs" with "paths as first-class citizens" (A1-SR-17, 2017). Its task force formed in 2014 because the lack of a common language "kept coming up" in benchmark discussions. That is the reason for G-CORE, not a criticism of a formulation. Cypher 9 and the Cypher 10 proposal followed in 2018 (A1-SR-16). openCypher was announced in late 2015, but the history dates the Cypher step by that paper. A 2021 paper says openCypher "did not succeed on its own in establishing a standard" and describes GPML (A1-SR-18). The PG-Schema paper of July 2023 proposes a schema language "aiming to inspire the development of GQL" (A1-SR-19). It says schema support is limited "in the first version of the GQL Standard". That faults the GQL draft, not GPML, so the history attaches it to no step. The 2021 paper names GPML as the shared core before either standard was published (A1-SR-18). The catalogue records of SQL/PGQ (2023) and GQL (2024) show their publication, not their content, so they are not steps (A1-SR-06, A1-SR-04). Section 4 gives their status. With one recorded criticism, the concept falls below the entry rule. The four papers come from one community (A1-SR-19). The ISO records are catalogue entries.

### 3.9 Graph-based retrieval (GraphRAG)

The formulations are GraphRAG (A6-SR-03, 2024), HippoRAG (A6-SR-04), LightRAG (A6-SR-05), and LazyGraphRAG (A6-SR-06), all abstracts or vendor material. The GraphRAG paper treats global questions as "inherently a query-focused summarization (QFS) task" (A6-SR-03). No criticism of a step is recorded in source words. The vendor's statement that full GraphRAG is expensive to index is a paraphrase in its record (A6-SR-06, extract), so the history drops it. Later evaluations add no formulation and attach to no single step. One reports that on three representative methods the gains are "much more moderate than reported previously" (A6-SR-08, abstract only). Another finds that basic RAG matches or beats GraphRAG on simple fact retrieval (A6-SR-09).

### 3.10 RDF-star to RDF 1.2 triple terms

The formulations are embedded triples (A2-SR-09, 2014) and transparent triple terms under `rdf:reifies` (A2-SR-17). The community group report (A2-SR-14) defines quoted triples, but its record quotes no words that show their opacity or that they need not be asserted. So the history does not count the report as a step. A 2024 argument for full opacity (A2-SR-15, extract) and the June 2024 minutes (A2-SR-16, extract) show the debate before the 2026 draft. The criticism that settled the transparent design is not recorded.

### 3.11 OWL language design

The history has one step, OWL 1 (A1-SR-10, extract). The OWL 1.1 authors say the original design "was conservative in several ways" (A1-SR-11, extract). The history records that as the criticism of OWL 1. The records of OWL 1.1 (A1-SR-11) and OWL 2 (A1-SR-12) quote no words that show their new formulation, so the history drops both steps. The OWL 2 rationale quotes limits of OWL 1, such as "impossible to state that properties are disjoint." No record shows that OWL 1.1 was the direct input to OWL 2.

### 3.12 Entity resolution methods

The history runs from the probabilistic model of Fellegi and Sunter (1969) and deep learning matchers, both known through one survey (A5-SR-11, secondary), to fine-tuned pre-trained models (A5-SR-12, 2020) and prompted generative models (A5-SR-13). The deep learning step carries the survey's 2020 date. Ditto's authors call their schema handling "a sharp contrast" to DeepMatcher, and their own footnote says DeepMatcher can drop the shared-schema requirement. That passage names no fault, and Ditto gives pre-trained language models as its reason, so the history records no criticism of the deep learning step. Peeters et al. say fine-tuned models "are not robust concerning out-of-distribution entities" and that the prompt "needs to be tuned for each model/dataset combination" (A5-SR-13). With one recorded criticism, the concept falls below the entry rule. The learned matchers between 1969 and deep learning follow "the same conceptual model" as Fellegi and Sunter and are not a step.

## 4. Standards status

The dates come from W3C and ISO pages fetched on 17 November 2026 as extracts. ISO's `www.iso.org` returned HTTP 403, so the ISO entries come from ISO's `committee.iso.org` host.

| Standard   | Status on 17 November 2026                                                                                                                                        | Key dates                                                                                              | Records                      |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ---------------------------- |
| RDF 1.2    | Concepts and Semantics are Candidate Recommendation Drafts. Turtle, TriG, N-Triples, N-Quads, and XML syntax are Working Drafts. No document is a Recommendation. | Concepts draft 16 Nov 2026; Semantics draft 24 Sep 2026; Candidate Recommendation snapshots 7 Apr 2026 | A1-SR-01, A1-SR-02, A2-SR-17 |
| SPARQL 1.2 | Query, Update, Protocol, Federated Query, and Entailment Regimes are Working Drafts.                                                                              | Query 16 Nov 2026; Update 15 Nov 2026; Federated Query 23 Apr 2026; Entailment Regimes 9 Apr 2026      | A1-SR-02, A1-SR-03           |
| ISO GQL    | ISO/IEC 39075:2024 is published, at stage 90.92 "to be revised". Corrigendum Cor 1:2026 is listed as published. Edition 2 is a committee draft at stage 30.60.    | Published 12 Apr 2024; edition 2 draft registered 5 Nov 2025; comment period closed 30 Jan 2026        | A1-SR-04, A1-SR-05           |
| SQL/PGQ    | ISO/IEC 9075-16:2023 is published, at stage 90.92 "to be revised". Cor 1:2026 is published. A committee draft is in development.                                  | Published 1 Jun 2023; stage 90.92 dated 22 Jun 2025                                                    | A1-SR-06                     |

PROV-O has been a W3C Recommendation since 30 April 2013 (A3-SR-03, extract). SHACL 2017 is a Recommendation, and SHACL 1.2 Core is a Working Draft of 16 November 2026 (A4-SR-11, A4-SR-16).

## 5. What this means for the Agent Factory graph

**This section is interpretation.** It applies the findings to the graph described in [the provenance synthesis](../knowledge-graph-with-provenance/synthesis.md): one record per idea, a provenance anchor to an unchanging source, and a decision history. Each point names the findings it rests on. Section 7 turns each point into a testable claim.

1. **Statement-level provenance has a long record in one pattern.** Nanopublications separate the assertion from its provenance and from publication information, and they fix integrity with a hash in the identifier (sections 2.3 and 3.1). The factory's anchor to a full commit SHA plays the same role as a trusty URI. RDF 1.2 triple terms are the W3C route, but they are still a draft, and the reason for their final semantics is not recorded (sections 3.10 and 4).
2. **Criticism links have documented models.** AIF splits claims from the scheme nodes that support, prefer, or attack them, and micropublications add support and challenge links with evidence (sections 2.3 and 3.2). A conjecture and a criticism map onto these node types. AIF's own history shows that the schema language must express disjoint node types (section 3.2).
3. **Record checks need a closed-world reading.** Under OWL's open world, a decision without a source produces no error (sections 2.4 and 3.3). Shape languages check what is present. Recursive shapes have no agreed meaning and validators disagree, so the factory's checks gain from staying non-recursive (sections 3.5 and 3.6).
4. **Merging ideas as identical is the documented failure.** Merging two profiles of one person through strict identity lets a reasoner infer a job the person never held (A5-SR-03). The `owl:sameAs` history ends with an approach that keeps the property and scores each link, and no record shows adoption of the weaker similarity property that Halpin et al. suggest (section 3.4). A `same-as` link between idea records would carry the same risk.
5. **Superseding a decision is a time question.** Valid time and recorded time are separate in SQL:2011 and in the Zep model, and Zep ends an edge instead of deleting it (section 2.5). The evidence for the LLM-driven invalidation step is a vendor report.
6. **LLM extraction needs a human check.** Extracted graphs needed manual checks, extraction quality on current models is not measured, and GraphRAG gains depend on the task (sections 2.6 and 3.9). The one recorded embedded store was archived (section 2.6), which weighs against tying the graph to one store.

## 6. Uncertainties, evidence gaps, and limitations

**Uncertainties.** Most W3C, ISO, and area 6 pages were read as fetch-tool extracts, so their quotes may be paraphrases. Many criticisms come from the authors of the next formulation, who have a reason to stress the gap they fill. This holds for nanopublications, AIF, the property graph languages, and the SHACL semantics. Several dates are year-only, month-only, or the retrieval date, and each record says which. The date of OPM version 1.00 differs between the paper and the project page (A3-SR-01).

**Evidence gaps.** The decisive criticism behind RDF 1.2's transparent triple terms is not recorded. The only recorded reason why SHACL leaves recursion undefined comes from a non-normative paragraph of the 2026 Working Draft: implementations may then "issue a static set of SPARQL queries" without supporting cycles (A4-SR-16). The 2017 Working Group minutes were not read. No record states why PROV changed from OPM or why the nanopublication terms changed. The primary texts of RDF 1.0, the first OWL 2 edition, Corman et al. 2018, Fellegi and Sunter 1969, TSQL2, and SQL:2011 were not read. No dated source after 2021 covers provenance and argumentation. No independent evaluation of agent memory graphs and no measurement of current LLM extraction accuracy were found. Toulmin and IBIS appear only as mentions. The records of OWL 1.1, OWL 2, the published SQL/PGQ and GQL, and the SHACL 1.2 Core features quote no source words that show a new formulation, so the histories do not count them as steps.

**Limitations.** Records marked abstract only cannot show methods or numbers. Vendor papers (A5-SR-10, A6-SR-03, A6-SR-06, A6-SR-13, A6-SR-14) count for their design, not for capability. The GQL and SQL/PGQ texts are paywalled, so only their catalogue status is recorded. Each area index lists sources it found and did not record.

## 7. Structured block

```json
{
  "findings": [
    {
      "title": "Two main data models, convertible without loss according to one survey",
      "summary": "RDF annotates an edge through an extra node or a named graph, while property graphs carry key-value pairs on edges. A peer-reviewed survey says the two convert without loss and that practical factors often decide. RDF 1.1 added datasets with named graphs; the RDF 1.2 draft adds triple terms. GQL and SQL/PGQ share the GPML pattern-matching core, according to a 2021 paper that predates both published standards, and a July 2023 paper, written before GQL was published in April 2024, says schema support is limited in the first GQL version.",
      "source_record_refs": [
        "A1-SR-20",
        "A1-SR-07",
        "A1-SR-08",
        "A1-SR-01",
        "A1-SR-18",
        "A1-SR-19"
      ]
    },
    {
      "title": "Statements about statements: no clear winner among the older encodings, RDF 1.2 adds reifiers on triple terms",
      "summary": "A 2015 comparison on Wikidata found no clear winner between standard reification, n-ary relations, and named graphs; singleton properties broke indexing in two of five engines, and property paths worked only for n-ary and named graphs. RDF 1.1 named graphs carry no formal semantics for the graph name. The RDF 1.2 draft links a reifier to an optionally unasserted, transparent triple term through rdf:reifies. Wikidata models claims with qualifiers, references, and ranks, and gives each statement its own node in RDF.",
      "source_record_refs": [
        "A2-SR-01",
        "A2-SR-02",
        "A2-SR-05",
        "A2-SR-08",
        "A2-SR-11",
        "A2-SR-17",
        "A2-SR-07",
        "A2-SR-12",
        "A2-SR-13"
      ]
    },
    {
      "title": "Provenance and claims: PROV, nanopublications, micropublications, and AIF",
      "summary": "W3C PROV has four Recommendations from 30 April 2013, including PROV-O and PROV-DM. Current nanopublications have an assertion, a provenance graph, and a publication info graph, with trusty URIs as integrity keys. Micropublications add support and challenge links and evidence graphs. AIF models claims as information nodes and inference, preference, and conflict as scheme nodes. No dated source in this area is from after 2021.",
      "source_record_refs": [
        "A3-SR-03",
        "A3-SR-04",
        "A3-SR-10",
        "A3-SR-13",
        "A3-SR-14"
      ]
    },
    {
      "title": "Validation: OWL is open-world, SHACL and ShEx check data, recursion in SHACL is undefined",
      "summary": "OWL treats missing facts as unknown and makes no unique name assumption, which authors argued stops OWL axioms from acting as checks. SHACL (2017) and ShEx validate graphs against shapes. SHACL leaves recursive shapes to implementations in 2017 and in the 1.2 Core draft of 16 November 2026. A 2026 test found that validators commit to different recursion semantics. Validation under an OWL ontology is still a research problem.",
      "source_record_refs": [
        "A4-SR-01",
        "A4-SR-02",
        "A4-SR-08",
        "A4-SR-11",
        "A4-SR-14",
        "A4-SR-15",
        "A4-SR-16"
      ]
    },
    {
      "title": "Time and identity: sameAs misuse, bitemporal periods, and a move to language-model matching",
      "summary": "owl:sameAs states strict identity, but in one rater study about 51% (plus or minus 21%) of sampled links looked correct; a later approach scores each link by an error degree. Temporal RDF labels triples with intervals, and a 2021 survey lists several representations of temporal context. SQL:2011 has system-time and application-time periods (secondary). A vendor agent memory system stores four timestamps per edge. Entity resolution moved from probabilistic models to prompted language models.",
      "source_record_refs": [
        "A5-SR-01",
        "A5-SR-04",
        "A5-SR-05",
        "A5-SR-06",
        "A5-SR-09",
        "A5-SR-08",
        "A5-SR-10",
        "A5-SR-11",
        "A5-SR-13"
      ]
    },
    {
      "title": "Language models: extraction needs checks, GraphRAG gains depend on the task, memory graph evidence is vendor-reported",
      "summary": "An early test judged GPT-4 better as an inference assistant than as a few-shot extractor, with manual checks still needed. Independent evaluations found that GraphRAG has distinct strengths per task, smaller gains than first reported for three representative methods, and no advantage on simple fact retrieval. Agent memory graph results come from vendors. Kuzu, the one embedded store recorded, was archived on 10 October 2025.",
      "source_record_refs": [
        "A6-SR-01",
        "A6-SR-07",
        "A6-SR-08",
        "A6-SR-09",
        "A6-SR-13",
        "A6-SR-14",
        "A6-SR-15",
        "A6-SR-16",
        "A6-SR-17"
      ]
    },
    {
      "title": "Standards status on 17 November 2026",
      "summary": "RDF 1.2 Concepts and Semantics are Candidate Recommendation Drafts and the syntaxes are Working Drafts. SPARQL 1.2 documents are Working Drafts. ISO/IEC 39075:2024 (GQL) was published on 12 April 2024 and has an edition 2 committee draft whose comment period closed on 30 January 2026. ISO/IEC 9075-16:2023 (SQL/PGQ) was published on 1 June 2023 and is under revision. Both ISO standards list a published Cor 1:2026.",
      "source_record_refs": [
        "A1-SR-01",
        "A1-SR-02",
        "A1-SR-03",
        "A1-SR-04",
        "A1-SR-05",
        "A1-SR-06"
      ]
    },
    {
      "title": "Hardened concept 1: nanopublication structure and identity",
      "summary": "Richly annotated statements (2009), a named-graph model (2010), informal AIDA assertions (2013), trusty URIs (2014), and the three-graph guidelines. The 2013 and 2014 papers present their criticism as the reason for their own step; the micropublication authors add an outside criticism. The server network of 2014 to 2015 changes distribution and is not a step.",
      "source_record_refs": [
        "A3-SR-05",
        "A3-SR-06",
        "A3-SR-07",
        "A3-SR-08",
        "A3-SR-10",
        "A3-SR-13"
      ]
    },
    {
      "title": "Hardened concept 2: Argument Interchange Format",
      "summary": "Abstract model (2006), RDF Schema form with schemes (2007), dialogue extension (2008), and OWL ontology (2011). Both recorded criticisms are dated after the step that follows the criticized one, and all critics belong to one research circle. The 2007 disjointness limit is a limit of that paper's own choice.",
      "source_record_refs": [
        "A3-SR-14",
        "A3-SR-15",
        "A3-SR-16",
        "A3-SR-17"
      ]
    },
    {
      "title": "Hardened concept 3: constraint semantics for OWL axioms",
      "summary": "OWL 1 (2004), a minimal-model constraint TBox (2007), a closed-world constraint semantics with checks reduced to SPARQL (2009 to 2010, one merged step because no quoted passage shows what the 2010 paper adds), and core universal models for SHACL under an ontology (2026). The 2010 paper's Example 4 is the recorded criticism of the 2007 step; it is dated after the 2009 step and is not counted as its driver. The OWL 1 record does not show the open-world assumption; the non-normative OWL 2 Primer states it. No criticism of the merged step or of the 2026 step is recorded.",
      "source_record_refs": [
        "A1-SR-10",
        "A4-SR-01",
        "A4-SR-02",
        "A4-SR-03",
        "A4-SR-04",
        "A4-SR-14"
      ]
    },
    {
      "title": "Hardened concept 4: identity meaning of owl:sameAs",
      "summary": "Strict identity (2004), a Similarity Ontology that treats identity as one point on a scale of similarity (2010), interpretation per use (2010), and per-link error degrees (2020). Halpin et al. has a year-only date, and Ding et al. cite Halpin et al. as reference [4], which supports the order in the history. The 2020 paper cites Halpin et al. as reference [3], and its record does not show whether it addresses Halpin's self-criticism.",
      "source_record_refs": [
        "A5-SR-01",
        "A5-SR-04",
        "A5-SR-03",
        "A5-SR-05"
      ]
    },
    {
      "title": "Hardened concept 5: shape languages for RDF validation",
      "summary": "SPIN (2011), Resource Shape 2.0 and ShEx (2014), and SHACL (2017). The 2013 workshop criticizes SPARQL-based validation in general and names no tool. Ryman's 2015 criticism is a later assessment. The SHACL 1.2 Core draft (2026) is not a step, because its record quotes none of its new features. No record states the lineage from SPIN to SHACL.",
      "source_record_refs": [
        "A4-SR-05",
        "A4-SR-06",
        "A4-SR-07",
        "A4-SR-08",
        "A4-SR-09",
        "A4-SR-11",
        "A4-SR-13",
        "A4-SR-16"
      ]
    },
    {
      "title": "Hardened concept 6: semantics of recursive shapes",
      "summary": "Resource Shape references and a ShEx typing context (2014), a labelling procedure and well-defined ShEx schemas (2015), SHACL leaving recursion open as a gap step (2017), which the stable model paper records but does not give as its reason, stable model semantics (2020), and well-founded semantics (2024). The supported model semantics of 2018 has no record and is not a step. A 2026 comparison and the SHACL 1.2 draft add no formulation.",
      "source_record_refs": [
        "A4-SR-07",
        "A4-SR-08",
        "A4-SR-09",
        "A4-SR-10",
        "A4-SR-11",
        "A4-SR-12",
        "A4-SR-13",
        "A4-SR-15",
        "A4-SR-16"
      ]
    },
    {
      "title": "Below the entry rule: OPM to PROV",
      "summary": "OPM (2007 to 2010) and PROV (2013), with the 2010 Incubator report naming what OPM cannot represent. No record presents that criticism as the reason for PROV, and no record states that PROV replaced OPM.",
      "source_record_refs": [
        "A3-SR-01",
        "A3-SR-02",
        "A3-SR-03",
        "A3-SR-04"
      ]
    },
    {
      "title": "Below the entry rule: property graph query languages",
      "summary": "G-CORE (2017), Cypher 9 and the Cypher 10 proposal (2018), GPML (2021), and PG-Schema (July 2023). The one recorded criticism is the 2021 statement that openCypher did not establish a standard on its own. The PG-Schema remark on limited schema support faults the GQL draft, not GPML, and attaches to no step. The 2021 paper names GPML as the shared core before either standard was published. The catalogue records of SQL/PGQ (2023) and GQL (2024) show their publication, not their content, and are not steps. The four papers come from one community; the ISO records are catalogue entries.",
      "source_record_refs": [
        "A1-SR-17",
        "A1-SR-16",
        "A1-SR-18",
        "A1-SR-19",
        "A1-SR-06",
        "A1-SR-04"
      ]
    },
    {
      "title": "Below the entry rule: graph-based retrieval",
      "summary": "GraphRAG, HippoRAG, LightRAG, and LazyGraphRAG (2024), all abstracts or vendor material. No criticism of a step is recorded in source words; the vendor's cost statement is a paraphrase in its record and is not counted. Later evaluations, one on three representative methods, add no formulation.",
      "source_record_refs": [
        "A6-SR-03",
        "A6-SR-04",
        "A6-SR-05",
        "A6-SR-06",
        "A6-SR-08",
        "A6-SR-09"
      ]
    },
    {
      "title": "Below the entry rule: RDF-star to RDF 1.2 triple terms",
      "summary": "Embedded triples (2014) and transparent triple terms under rdf:reifies in the 2026 draft. The community group report's record quotes no words that show opaque or unasserted quoted triples, so it is not a step. No criticism of a step is recorded in source words. The 2024 debate is recorded, but the criticism that settled the transparent design is not.",
      "source_record_refs": [
        "A2-SR-09",
        "A2-SR-14",
        "A2-SR-15",
        "A2-SR-16",
        "A2-SR-17"
      ]
    },
    {
      "title": "Below the entry rule: OWL language design",
      "summary": "One step, OWL 1 (2004), with the OWL 1.1 authors' remark that the design was conservative as its criticism. The OWL 1.1 (2006) and OWL 2 (2012) records quote no words that show their new formulation, so they are not steps. No record shows that OWL 1.1 was the direct input to OWL 2.",
      "source_record_refs": [
        "A1-SR-10",
        "A1-SR-11",
        "A1-SR-12"
      ]
    },
    {
      "title": "Below the entry rule: entity resolution methods",
      "summary": "Probabilistic comparison vectors (1969) and deep learning matchers, both through one survey, then fine-tuned pre-trained language models (2020) and prompted generative models whose prompt must be tuned per model and dataset (2023 to 2024). The one recorded criticism is that fine-tuned models are not robust to out-of-distribution entities. Ditto's contrast with DeepMatcher names no fault and is not counted. Learned matchers that follow the same conceptual model as 1969 are not a step.",
      "source_record_refs": [
        "A5-SR-11",
        "A5-SR-12",
        "A5-SR-13"
      ]
    }
  ],
  "uncertainties": [
    "Most W3C, ISO, and area 6 records were read through a fetch tool that returns a model-written extract, so their quotes may be paraphrases.",
    "Many criticisms come from the authors of the next formulation: nanopublications, AIF, property graph query languages, and SHACL recursion semantics.",
    "Agent memory graph results (Zep, Mem0) and GraphRAG cost figures are vendor self-reports.",
    "Several record dates are year-only, month-only, or the retrieval date of a living page, including the RDF-star community group report and the nanopublication guidelines.",
    "The date of OPM version 1.00 differs between the 2010 paper and the project page.",
    "The ISO status rests on the committee.iso.org host because www.iso.org returned HTTP 403."
  ],
  "evidence_gaps": [
    "The criticism that moved RDF-star from opaque quoted triples to transparent RDF 1.2 triple terms is not recorded; the working group issue tracker and decision log were not reached.",
    "The only recorded reason why SHACL leaves recursion undefined comes from a non-normative paragraph of the 2026 SHACL 1.2 Core Working Draft: implementations may then issue a static set of SPARQL queries without supporting cycles. The 2017 Working Group minutes were not read.",
    "No record states what PROV changed from OPM or why, and no criticism of PROV after 2013 was recorded.",
    "No record states why nanopublication terms changed from statement, annotation, and S-Evidence to assertion, provenance, and publication info.",
    "The criticism that drove RDF 1.2 and SPARQL 1.2 is not recorded.",
    "Primary texts not read: RDF 1.0, the first OWL 2 edition of 2009, Corman et al. 2018, Fellegi and Sunter 1969, TSQL2, and ISO/IEC 9075:2011.",
    "No dated source after 2021 covers provenance, nanopublications, micropublications, or argumentation.",
    "No independent evaluation of agent memory graphs and no measurement of current LLM extraction accuracy were recorded.",
    "Toulmin and IBIS appear only as mentions in other records.",
    "No record shows adoption of the simple similarity property that Halpin et al. suggested, or whether GQL edition 2 contains PG-Schema.",
    "The records of OWL 1.1, OWL 2, the published SQL/PGQ and GQL, and the SHACL 1.2 Core features quote no source words that show a new formulation."
  ],
  "limitations": [
    "Steps marked secondary rest on surveys or on accounts by participants, not on the original text.",
    "Records read as abstracts only cannot show methods, numbers, or limitations stated in the body.",
    "Vendor papers count for their design, not for capability or adoption.",
    "The technical texts of GQL and SQL/PGQ are paywalled; only their catalogue status is recorded.",
    "Several long pages were read only in their first 100,000 characters.",
    "The survey ran one research wave over six areas, and each area index lists sources it found but did not record."
  ],
  "candidates_for_deeper_falsification_study": [
    "Claim: one record per idea, split into an assertion, its provenance, and publication information, can hold every provenance fact the Agent Factory needs. Refuted if, in a sample of 50 ideas extracted from transcripts and handoffs, one idea needs provenance attached to a part of its assertion rather than to the whole assertion.",
    "Claim: RDF 1.2 triple terms with rdf:reifies can carry two criticisms of the same statement from two different sources and keep them apart in a query. Refuted if a current RDF 1.2 implementation cannot answer which source raised which criticism for such a statement.",
    "Claim: a non-recursive closed-world shape check catches every Agent Factory record that lacks a source anchor, a link reason, or decision evidence. Refuted if any record in a seeded set of defective records passes the check.",
    "Claim: the Agent Factory record rules can be written without recursive shapes, and two SHACL validators give the same result on them. Refuted if a required rule, such as every replaced decision existing, needs a recursive shape, or if two validators disagree on any test record.",
    "Claim: treating a same-as link between idea records as strict identity carries a wrong decision outcome or source to at least one record. Refuted if merging every confirmed same-as pair in a sample of 30 candidate pairs changes no record's outcome or source.",
    "Claim: storing a valid time and a recorded time on each decision, and ending a decision instead of deleting it, answers 'what was decided as of date D' correctly. Refuted if a query over the decision history returns a decision recorded after D.",
    "Claim: the AIF node types (claim, inference, conflict, preference) cover every link type the Agent Factory graph needs. Refuted if one link type found in transcripts, such as refines or depends-on, cannot be mapped to an AIF node type without loss.",
    "Claim: LLM extraction of ideas from transcripts yields quotes that occur verbatim in the source. Refuted if more than 2 of 100 sampled extracted quotes do not occur in the source at the stated commit.",
    "Claim: for Agent Factory lookup questions, which are mostly simple fact retrieval, plain text retrieval answers as many questions correctly as graph-based retrieval. Refuted if graph-based retrieval answers clearly more of a fixed question set correctly."
  ]
}
```
