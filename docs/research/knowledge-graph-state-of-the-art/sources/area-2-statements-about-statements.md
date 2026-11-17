# Area 2: statements about statements

This index covers how RDF and related models attach information to a statement, such as its source, time, or confidence. Records live in `area-2/`. Each record ID below is `A2-SR-NN`, written `NN` in short. Standards status belongs to area 1 and is not assessed here. The text reports what the sources document.

## State of the art, as the sources document it

- RDF has carried a reification vocabulary since the 2004 standard. The 2004 and 2014 specifications both state that a reification neither entails nor is entailed by the triple it describes (01, 02).
- Four older ways to attach metadata are compared on Wikidata data in one 2015 study: standard reification, n-ary relations, singleton properties, and named graphs (11). That study found no clear winner among three of them on query time. Singleton properties caused indexing problems in two of five engines (11).
- RDF 1.1 defines a named graph as a graph paired with a name and sets no formal restriction on what the name denotes (05).
- RDF-star started as a 2014 proposal to use a triple as the subject or object of another triple (09). The community group report calls such a triple a quoted triple and treats it as referentially opaque (14). The RDF 1.2 Candidate Recommendation Draft of November 2026 uses triple terms, an `rdf:reifies` predicate, and a transparent reading (17).
- Wikidata describes a claim as a main value plus qualifiers, references, and a rank (07, 12). Its RDF export gives each statement its own node (08, 13).
- Property graphs carry edge properties natively. One 2014 paper claims a formal bridge to RDF\* (10).

## Hardened concepts

Six concepts show at least two documented formulations. Each step names the formulation, its date, the criticism that led on, and the records for both. A step with no source is a gap.

### 1. RDF standard reification

1. **RDF 1.0 reification vocabulary, 2004.** A reified triple describes a triple token. It is not quotation, and it does not entail the triple (01). Criticism that led on: none in this record.
2. **RDF 1.1, 2014.** The informative appendix repeats the 2004 meaning (02). Criticism that led on: none in this record.
3. **Criticisms from successors, 2014.** Four extra triples per statement and queries that need extra patterns (09). No formal semantics tying the statement to its description, and about fourfold data growth (06). The Wikidata team also calls it inefficient and without formal semantics (08).

Gap: the origin of the vocabulary (the 1999 RDF Model and Syntax) and any criticism before 2014 are not recorded. The 2004 specification and the 2006 note (03) sit in the middle of that period without stated criticism of reification beyond the note's section 4.

### 2. N-ary relations

1. **Best-practice patterns, 2006.** Add a new class and n new properties to describe a relation instance, or use an ordered list. The note separates this from reification because reification describes a triple's source while an n-ary relation adds arguments (03). Criticism that led on: none in this record.
2. **Wikidata qualifiers, 2014.** The Wikidata paper says qualifiers can encode a ternary relation but warns against reading them as a workaround for higher arity, because statements have no fixed arity (07). The RDF export paper adds that "the boundary between context annotation and n-ary relation is fuzzy" (08).
3. **Measured as an RDF encoding, 2015.** The n-ary model was the only one of the four with built-in property path support. Loading and query results were mixed (11).

Gap: no source records criticism of the 2006 patterns from their users. The 2006 note gives no reasons for its choice beyond section 4.

### 3. Named graphs

1. **Named Graphs, 2005.** A named graph attaches a name to an RDF graph. The paper says reification has well-known problems and describes a single-triple graph as a migration path from reification, with different semantics (04).
2. **RDF 1.1 datasets, 2014.** The standard keeps the graph name as a syntactic pairing and sets no restriction on what it denotes (05).
3. **Criticism, 2014 and 2015.** The Wikidata export paper says no current standard gives semantics to graph names. It states that proposed semantics "did not find their ways into standards" (08). In the 2015 test, 4store slowed to 24 triples per second on the full named graph data (11).

Gap: the 2005 paper's formal semantics sections were not read. The reasons the working group gave for "minimal semantics" in 2014 are not recorded.

### 4. Singleton properties

1. **Singleton property, 2014.** One unique property per statement in a context, linked to its generic property by `singletonPropertyOf` (06). Proposed as a reaction to reification's lack of semantics and its size (06).
2. **Criticism, 2014.** The Wikidata team says the relation between such triples and their annotations is not captured by standard semantics (08).
3. **Test, 2015.** Singleton properties gave the most concise triple representation. Two engines struggled with the number of unique predicates. Property paths cannot be written in this model (11).

Gap: no later source on the concept was found, so its status after 2015 is not documented here.

### 5. RDF-star to RDF 1.2 triple terms

1. **RDF\* embedded triples, 2014.** A triple may stand in subject or object position, and the formalization stays backward compatible with standard reification (09). It addresses the two reification shortcomings named in 09. The v3 note says embedded triples were defined through standard reification and treated as implicitly asserted when nested (09).
2. **Community group report, quoted triples.** A quoted triple is not asserted unless it is in the graph, and is referentially opaque. The report separates two older modes: one in which every quoted triple was also asserted (PG-mode) and one that required a separate assertion (SA-mode). Annotation syntax replaced the two modes (14). The report says its seminal provenance example gave wrong expectations and breaks with several creators and sources (14).
3. **RDF 1.2 triple terms, 2024 to 2026.** A triple term sits in the object position of a reifying triple with `rdf:reifies`. It may be unasserted. Its terms are transparent (17). The Working Group debated opacity in 2024. One member argued for full opacity and warned that transparency makes simple entailment more complex (15). The minutes show the group weighed a weaker opacity and a single `rdf:reifies` property (16).

Gap: the criticism that moved the design from quoted triples to triple terms and from opaque to transparent is not documented by any record here. Records 15 and 16 show the debate, not its outcome. The group's issue tracker and decision log were not reached. Records for the 2021 report and the 2025 working drafts as dated versions are also missing.

### 6. Wikidata statement model

1. **Property-value pairs, 2014.** The first model is a property with a value. The paper calls this too simple and adds qualifiers (07).
2. **Qualifiers, references, ranks, 2014.** A statement may have qualifiers, a list of references, and a rank of preferred or deprecated (07). Ranks have three values including normal (08, 12). Wikidata does not record provenance automatically but provides structure for references (07).
3. **RDF export with statement nodes, 2014.** Statements, complex values and references become resources, and the authors state that Wikidata objects, not RDF triples, are reified (08).
4. **Current documented model.** Statement nodes, `pq:` qualifiers, `prov:wasDerivedFrom` references, and `wikibase:rank`. Truthy `wdt:` triples keep only best non-deprecated statements and ignore qualifiers (13). The data model page says it is not a formal semantics (12).

Gap: the dates and the criticism that led to ranks, and to each change of the export after 2014, are not recorded. The records show the model at two points, not the steps between.

## Edge properties and property graphs

One source (10) is thin: only an abstract was read. It shows a 2014 claim of a formal link between property graphs and RDF\*. No source on the origin of edge properties in property graph systems was gathered.

## Gaps

- The RDF-star Working Group issue tracker, decision log, and wiki baseline pages were not reached. The decisive record for step 5.3 is missing.
- Dated versions of the community group report and of the 2025 RDF 1.2 working drafts were not read.
- Property graph primary sources (Cypher, Gremlin, ISO GQL) are not recorded. Area 1 may hold them.
- Pre-2004 history (RDF Model and Syntax 1999, quads proposals in 2001) appears only as statements in 08. No primary record was gathered.
- Hogan et al., "Knowledge Graphs" (ACM Computing Surveys 2021), was not recorded as a secondary overview.
- Several dates are year-only or the retrieval date (records 04, 08, 11, 12, 13, 14). The limitations field of each says which.
- All quotes passed through a summarizing fetch tool, except records read from downloaded PDFs and HTML (04, 06 to 09, 11, 14, 17). Re-check quotes of 01, 02, 03, 05, 12, 13, 15, 16 against the pages.
