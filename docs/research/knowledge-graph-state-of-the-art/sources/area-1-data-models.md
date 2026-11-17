# Area 1: Data Models, Source Index

This index covers RDF and OWL, labeled property graphs, and hybrids. It reports what the recorded sources document. Records sit in `area-1/` and carry the IDs `A1-SR-01` to `A1-SR-20`. Each record is primary unless this index calls it secondary. Only A1-SR-20 is secondary.

## 1. State of the art as of 2026-11-17

- **RDF 1.2 is not yet a W3C Recommendation.** RDF 1.2 Concepts and RDF 1.2 Semantics are Candidate Recommendation Drafts, with Candidate Recommendation snapshots dated 7 April 2026 (A1-SR-01, A1-SR-02). The RDF 1.2 syntax documents (Turtle, TriG, N-Triples, N-Quads, XML) are Working Drafts (A1-SR-02).
- **SPARQL 1.2 is at Working Draft.** SPARQL 1.2 Query, Update, Protocol, Federated Query, and Entailment Regimes are all Working Drafts (A1-SR-02, A1-SR-03). No SPARQL 1.2 document is a Candidate Recommendation on the page read.
- **RDF-star and triple terms.** The RDF 1.2 Concepts draft defines "a triple term" as "an RDF triple used as an RDF term within another triple". The text read does not use the name RDF-star (A1-SR-01). The concept history belongs to area 2.
- **ISO GQL is published and has a second edition in draft.** ISO/IEC 39075:2024 was published on 2024-04-12 and is at stage 90.92, "to be revised". Corrigendum Cor 1:2026 is listed as published. ISO/IEC CD 39075 (edition 2) closed its comment period on 2026-01-30 (A1-SR-04, A1-SR-05).
- **SQL/PGQ is published and also under revision.** ISO/IEC 9075-16:2023 was published on 2023-06-01 and is at stage 90.92. Cor 1:2026 is listed as published, and ISO/IEC CD 9075-16 is in development (A1-SR-06).
- **GQL and SQL/PGQ share one pattern-matching core.** Their designers state that the core is the same sublanguage, called GPML (A1-SR-18).
- **RDF and property graphs differ in how they attach data to an edge.** A survey says an RDF graph needs an extra node or a named graph to annotate an edge. A property graph carries property-value pairs on the edge. The survey says the two convert without loss of information (A1-SR-20, secondary).
- **Property graph schemas are thin in the first GQL edition.** The PG-Schema authors say schema support is limited in systems and in the first GQL version (A1-SR-19).

The ISO records come from ISO's `committee.iso.org` host, because `www.iso.org` returned HTTP 403 (A1-SR-04, A1-SR-05, A1-SR-06).

## 2. Hardened concepts

### 2.1 The RDF data model: three steps

1. **RDF 1.0 (2004).** Gap. No RDF 1.0 document was fetched. Later records refer to it (A1-SR-07, A1-SR-08).
2. **RDF 1.1 (2014-02-25).** Identifiers become IRIs. Simple literals become a synonym for `xsd:string`. Datasets with named graphs are introduced. Serializations other than RDF/XML are added (A1-SR-07, A1-SR-08). The note states a reason for only some changes: blank node identifiers are not portable, `rdf:HTML` follows DOM4, and RDF is the data model, not a syntax (A1-SR-08). Criticism that led to 1.2: not stated in the records that were read.
3. **RDF 1.2 (Candidate Recommendation Draft, 2026-11-16).** Adds triple terms (A1-SR-01). The "What's New in RDF 1.2" draft does not yet document the changes or reasons (A1-SR-09). Criticism that drove step 3: gap.

### 2.2 OWL: three steps

1. **OWL 1 (Recommendation, 2004-02-10).** Three sublanguages. OWL DL keeps decidability. OWL Full gives up guarantees for RDF's syntactic freedom. Transitive properties need a side condition, or OWL Lite and OWL DL become undecidable (A1-SR-10). Criticism that led to step 2: the OWL 1.1 authors call the first design "conservative" and say practical use of OWL DL showed useful missing constructs (A1-SR-11).
2. **OWL 1.1 (Member Submission, 2006-12-19).** Moves from SHOIN to SROIQ. Adds qualified cardinality, local reflexivity, property characteristics, disjoint properties, property chains, user-defined datatypes, and punning. W3C did not endorse the submission (A1-SR-11). Criticism that led to step 3: the OWL 2 working group lists the same kinds of limits, and adds that DL, Full, and Lite were "not sufficient" for later deployments (A1-SR-12).
3. **OWL 2 (second edition Recommendation, 2012-12-11).** Adds the features of step 2, keys, annotated axioms, declarations, and the EL, QL, and RL profiles. OWL Lite is not re-specified (A1-SR-12). The sources do not link each OWL 2 feature to a named critic. Whether OWL 1.1 was the direct input to OWL 2 is not shown by A1-SR-12.

### 2.3 SPARQL: four steps

1. **SPARQL 1.0 (Recommendation, 2008-01-15).** Matches with simple entailment only. Postpones 12 issues, "including aggregate functions, and an update language" (A1-SR-13). Criticism that led to step 2: the 2009 rationale says features came from "real applications and user and tool-developer experience". It names no individual complaint (A1-SR-14).
2. **SPARQL 1.1 plan (Working Draft, 2009-07-02).** Required features: aggregates, subqueries, negation, project expressions, update, service description. Each has a stated motivation. Update is needed "to avoid using third-party APIs" (A1-SR-14).
3. **SPARQL 1.1 Query (Recommendation, 2013-03-21).** The record shows date and status only. A list of changes from 1.0 was not found (A1-SR-15).
4. **SPARQL 1.2 (Working Draft, 2026-11-16).** Status is shown (A1-SR-02, A1-SR-03). Criticism that drove it: gap. The "What's New in SPARQL 1.2" note was not read.

### 2.4 Property graph query languages: six steps

1. **Cypher and openCypher (openCypher announced late 2015).** Many systems offer disparate languages. The standardization goal and the lack of a standard are stated by the Cypher authors (A1-SR-16). A later paper says openCypher "did not succeed on its own in establishing a standard" (A1-SR-18). Criticism that led to step 2: the G-CORE task force says the lack of a common language "kept coming up" in benchmark discussions and asks for composability and paths as first-class values (A1-SR-17).
2. **G-CORE (2017-12-05).** A closed language on property graphs, with paths as first-class citizens (A1-SR-17). The G-CORE record names no specific flaw in Cypher or SPARQL. Criticism that led to step 3: Cypher authors answer with a different design, closure under table-graphs (A1-SR-16).
3. **Cypher 9 and the Cypher 10 proposal (SIGMOD 2018).** Cypher 9 is the first version under the openCypher Implementers Group. Cypher 10 plans graph projections and multiple named graphs (A1-SR-16). The paper says both proposals were in the same spirit but differ on output (A1-SR-16).
4. **GPML as the shared core of GQL and SQL/PGQ (paper, 2021-12-12).** JTC 1 approved GQL in 2019. SQL/PGQ has been in development since 2017 (A1-SR-18).
5. **Published standards.** SQL/PGQ on 2023-06-01 and GQL on 2024-04-12 (A1-SR-06, A1-SR-04). Criticism that led to step 6: schema support is limited in the first GQL version (A1-SR-19).
6. **PG-Schema proposal and GQL edition 2.** The PG-Schema authors anticipate a richer data definition language in edition 2 (A1-SR-19). An edition 2 committee draft exists (A1-SR-05). No source read shows that edition 2 contains PG-Schema.

### 2.5 Not a sequence

The RDF versus property graph choice appears in one secondary source only (A1-SR-20). The records do not show a series of formulations with criticism, so this index does not list it as a hardened concept. Area 2 covers the statement-level hybrids.

## 3. Gaps

- RDF 1.0 (2004) was not fetched. The RDF 1.1 criticism is stated only in part.
- The first OWL 2 Recommendation of 2009 was not fetched. A1-SR-12 is the second edition of 2012.
- "What's New in SPARQL 1.2" and the SPARQL 1.1 change list were not read. The motivation for SPARQL 1.2 is not recorded.
- The ISO pages at `www.iso.org` returned HTTP 403. The records rely on `committee.iso.org`. The technical text of GQL and SQL/PGQ is paywalled and was not read.
- Fetched W3C and ISO pages came through a tool that returns a model-written extract. The W3C status paragraphs are paraphrased, and long pages were read only in part (see `limitations` in each record).
- Criticism of RDF 1.2 triple terms and of the RDF-star lineage belongs to area 2.
- No independent critique of GQL, SQL/PGQ, or Cypher was found. Sources on their history are written by participants.
