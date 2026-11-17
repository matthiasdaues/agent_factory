# Area 4: Validation and World Assumptions

This index covers OWL open-world reasoning, SHACL, and ShEx. It reports what 16 recorded sources document. It does not rate any concept. A record ID such as A4-SR-04 names the file `sources/area-4/A4-SR-04-*.md`. A source is primary unless the text marks it secondary.

## State of the art in this area

- OWL 2 reads missing data as unknown and does not treat different names as different things (A4-SR-01). Two authors' groups argued from 2007 on that this behavior prevents OWL axioms from acting as data checks (A4-SR-02, A4-SR-03).
- Proposals to give OWL axioms a closed-world reading exist as research and as a Pellet prototype (A4-SR-03, A4-SR-04). The sources read do not show any of them in a W3C Recommendation.
- W3C participants asked for a shape language in 2013, because SPARQL alone was not a complete solution (A4-SR-06). Resource Shape 2.0, ShEx, and SHACL followed (A4-SR-07, A4-SR-08, A4-SR-11).
- The SHACL Recommendation of 2017 leaves the meaning of recursive shapes undefined (A4-SR-11). The SHACL 1.2 Core draft of 16 November 2026 repeats this (A4-SR-16).
- Three semantics for recursive SHACL are published: supported models, stable models, and well-founded (A4-SR-12, A4-SR-13). A 2026 comparison finds that ShEx validators seem to implement greatest fixpoints and that SHACL validators differ (A4-SR-15).
- Validating SHACL together with an OWL ontology is still a research problem in 2026 (A4-SR-14).

## Concept 1: Constraint semantics for OWL axioms

This concept asks how an OWL axiom can act as a check on data. Five steps are recorded.

1. **OWL standard semantics, as restated in 2012** (A4-SR-01). The OWL 2 Primer says a missing fact "may simply be missing (but possibly true)" and that OWL "does not make the assumption that different names are names for different individuals." Criticism that followed: Motik, Horrocks, and Sattler wrote in 2007 that "in OWL it is not possible to formalize integrity constraints that behave as checks" (A4-SR-02). That criticism targets OWL before the 2012 Primer. The primer itself shows the semantics unchanged. The 2004 OWL text was not read.
2. **Integrity constraints as a second TBox under minimal models, 2007** (A4-SR-02). Axioms in the constraint TBox "are interpreted as checks." Criticism that followed: Tao et al. show two cases where this reading gives the wrong result. A constraint that every product has a known producer is satisfied when the producer is one of two unknown candidates. A constraint on one category is violated when the item may belong to another category (A4-SR-04, Examples 4 and 5).
3. **Closed-world constraint semantics with a weak unique name assumption, Pellet prototype, 2009** (A4-SR-03). The authors say they are "not completely satisfied with existing solution" and cite Motik et al. Their prototype reduces validation to SPARQL queries. The detailed criticism is in the next step's source.
4. **Per-axiom constraint semantics, AAAI 2010** (A4-SR-04). Modelers choose which axioms get the constraint reading, so "open world reasoning" and "closed world constraint validation" combine. Criticism that followed: the shape-language papers say OWL-based approaches stay limited by "Open World and Non-Unique Name Assumption" (A4-SR-08, Section 7). The 2026 paper (next step) criticizes minimal-model constructions directly.
5. **Core universal models for SHACL under an ontology, 2026** (A4-SR-14). The authors state that minimal Skolem models "give very weak semantics in formalisms with negation such as SHACL," and show a graph that satisfies all ontology axioms but fails validation. They propose "core universal models" and a rewriting to standard validation. The paper treats one Horn fragment of OWL only. No later criticism was found.

## Concept 2: Shape languages for RDF validation

This concept asks how a graph can be checked against a declared structure. Six steps are recorded.

1. **Constraints as SPARQL queries attached to classes, SPIN, 22 February 2011** (A4-SR-05). SPIN links "class definitions with SPARQL queries to capture constraints and rules." Criticism that followed: workshop participants agreed in 2013 that "SPARQL does not constitute a complete solution," because its queries "cannot easily be inspected and understood" (A4-SR-06).
2. **Workshop consensus on a shape description, 10 to 11 September 2013** (A4-SR-06). Participants asked for "a declarative way of describing simple integrity constraints" with an extension mechanism, and found "no standard addressing these needs." Criticism that followed: the report names two candidates, Shape Expressions and OSLC Resource Shape, and records that "some in the audience pushed back on the need for RDF validation at all."
3. **Resource Shape 2.0, 11 February 2014** (A4-SR-07). Shapes are an RDF vocabulary checked with SPARQL. The submission calls the use of RDFS or OWL for constraints "a misapplication of those technologies." Criticism that followed: a 2015 paper by the same author says "Neither of the member submissions included a precise definition of recursion" (A4-SR-09).
4. **Shape Expressions, 4 September 2014** (A4-SR-08). A grammar for RDF shapes in the style of regular expressions, with a formal semantics by inference rules. It rejects OWL and RDFS for validation because of the open-world and non-unique-name assumptions. Criticism that followed: the semantics for recursion needed more analysis, see concept 3.
5. **SHACL Recommendation, 20 July 2017** (A4-SR-11). It defines shapes graphs for validating RDF graphs. Criticism that followed: later authors note that it "defines semantics only for non-recursive SHACL constraints" (A4-SR-13, A4-SR-12).
6. **SHACL 1.2 Core Working Draft, 16 November 2026** (A4-SR-16). It keeps recursion undefined and says "future work, for example in W3C Community Groups, will lead to the definition of specific dialects." The draft is not a Recommendation. No later source exists.

## Concept 3: Semantics of recursive shapes

This concept asks what it means when a shape refers to itself directly or through other shapes. Ten steps are recorded.

01. **Reference by oslc:valueShape without a stated rule for cycles, 2014** (A4-SR-07). The submission lets "one resource shape refer to another." It states no rule for cycles. That is the researcher's reading of the text. Criticism that followed: A4-SR-09, as in concept 2, step 3.
02. **ShEx recursion by a typing context, 2014** (A4-SR-08). "To avoid infinite loops, we add the current type to the context." Criticism that followed: Ryman writes that it is "not clear" whether ShEx recursion fits his definition and that "more analysis is required" (A4-SR-09, Sections 7.2 and 8).
03. **Labelling procedure for Resource Shape 2.0, v2 dated 1 November 2015** (A4-SR-09). A procedure over a finite graph that always terminates. The paper says Resource Shape recursion "causes no difficulties." The paper gives no result for SHACL, which was then in draft. Criticism that followed: none in the sources read. The next step comes from the ShEx authors.
04. **Well-defined ShEx schemas, v2 dated 16 November 2015** (A4-SR-10). Recursion is allowed. A shape that appears negated may not lead to cyclic dependencies. The paper does not give a semantics for recursion through negation.
05. **SHACL 2017: recursion left to implementations** (A4-SR-11). "The validation with recursive shapes is not defined in SHACL." Criticism that followed: Okulmus and Simkus (2024) say the choice leaves validator developers "to come up with ad-hoc solutions" (A4-SR-13). This is a later reading of the Recommendation.
06. **Supported model semantics, ISWC 2018 (Corman, Reutter, Savkovic).** The primary paper was not reached, see Gaps. Secondary sources state its content (A4-SR-13, A4-SR-15, both secondary for this step). It treats a graph as valid if some assignment of shapes to nodes satisfies all constraints. Criticism that followed: the semantics "allows multiple conforming shape assignments" (A4-SR-15, Section 2.3). It also "allows for unfounded (self-supported) justifications" and its validity problem is intractable (A4-SR-13, Section 1).
07. **Stable model semantics, WWW 2020** (A4-SR-12). The proposal is "stricter, more constructive." It requires each shape assignment to be "properly justified by the input constraints." Criticism that followed: it "solves (b) but still has the problem (a)," where (a) is NP-hardness when recursion and negation meet (A4-SR-13). This is a competing author's view. A4-SR-12 holds the abstract only.
08. **Well-founded semantics, KR 2024** (A4-SR-13). It "is not only intuitive, but it is also computationally tractable." Criticism that followed: none found. A 2026 paper by overlapping authors names this semantics without comment (A4-SR-15).
09. **Comparison of least fixpoint, greatest fixpoint, and supported model semantics, v2 dated 13 May 2026** (A4-SR-15). Least and greatest fixpoint "allow polynomial-time data complexity for all languages, whereas SMS immediately leads to intractability." Validators "implicitly commit to different semantics." Criticism that followed: none found.
10. **SHACL 1.2 Core draft, 16 November 2026** (A4-SR-16). Recursion stays undefined. The draft says leaving it open lets implementations issue "a static set of SPARQL queries."

## Differences in what each language assumes

- OWL assumes the data is incomplete (A4-SR-01, A4-SR-14).
- SHACL treats the data graph as complete and validates it under a closed-world view (A4-SR-14, author's description). The Recommendation text read does not state this as a principle (A4-SR-11).
- ShEx validates a node against shape definitions and, in the 2014 paper, motivates itself by the difficulty of OWL for validation (A4-SR-08).
- Which semantics SHACL should adopt for recursion is not settled in the sources (A4-SR-15, A4-SR-16).

## Gaps

1. **Corman, Reutter, and Savkovic, ISWC 2018.** The Springer page redirected to a login, the KRDB technical report URL returned a web page instead of a PDF, and ResearchGate returned HTTP 403. Step 6 of concept 3 rests on secondary sources.
2. **Andresel et al., WWW 2020.** The ACM page returned HTTP 403. A4-SR-12 holds the abstract from the Semantic Scholar record only.
3. **Reasons for SHACL's design.** No source read states why the Data Shapes Working Group left recursion undefined in 2017. The non-normative paragraph of the 2026 draft states a rationale (A4-SR-16). The Working Group's issue tracker and minutes were not read.
4. **ShEx 2.0 and 2.1.** The ShEx 2.1 Community Group Report of 8 October 2019 was fetched. It describes stratified negation and a unique typing. It has no record here, because the sources already filled the concept 3 steps. The ShEx 2.0 release date was not found.
5. **OWL 2004 text.** The criticism of 2007 targets the first OWL Recommendation, which was not read. A4-SR-01 shows the 2012 restatement only.
6. **SPIN to SHACL lineage.** The SHACL text read does not mention SPIN or ShEx. The link between SPIN and SHACL comes from the shared editor and from workshop and paper statements, not from a source that states the lineage.
7. **Reasoner and adoption evidence.** No source read shows how widely Pellet ICV, Stardog constraints, or any recursive SHACL semantics are deployed.
8. **Wikidata and survey coverage.** The survey by Hogan et al. (ACM Computing Surveys 2021) and Wikidata's use of ShEx were not read for this area.
9. **Dates.** A4-SR-04 and A4-SR-13 use the first day of the conference month, as the limitations fields say. A4-SR-12 uses the date the Semantic Scholar record gives, and a Wikidata record gives 4 May 2020.
