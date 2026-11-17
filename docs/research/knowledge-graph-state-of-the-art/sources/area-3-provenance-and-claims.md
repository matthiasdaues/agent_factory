# Area 3: Provenance and Claims

This index covers how PROV, nanopublications, micropublications and the Argument Interchange Format (AIF) record provenance and claims. Records sit in `sources/area-3/` and carry the IDs `A3-SR-01` to `A3-SR-17`. The survey reports what the sources document. It makes no statement that a concept survived refutation.

## State of the art

- W3C published PROV in 2013 as a family of twelve documents. Four are Recommendations: PROV-O, PROV-DM, PROV-N and PROV-CONSTRAINTS (A3-SR-03).
- The Working Group states that PROV's design stems from the recommendations of the Provenance Incubator Group (A3-SR-03, A3-SR-02).
- PROV-DM names core relations such as `wasGeneratedBy`, `used` and `wasDerivedFrom` (A3-SR-04).
- A nanopublication has three parts in the current guidelines: an assertion, the provenance of the assertion, and publication information. Trusty URIs are the recommended integrity key (A3-SR-10).
- A 2021 paper still defines nanopublications by these three elements (A3-SR-11).
- A micropublication is minimally a statement with an attribution. At the maximum it is a knowledge base with evidence graphs (A3-SR-13).
- AIF has an abstract model of information nodes and scheme nodes (A3-SR-14). It has had an RDFS form (A3-SR-15), a dialogue extension (A3-SR-16) and an OWL form (A3-SR-17).

Two cautions apply to every concept below.

- Most criticism in the nanopublication and AIF sequences comes from the authors of the next formulation. Authors of an extension have a reason to describe the gap their work fills. No record here holds a critic outside the research groups involved.
- No record is dated after 2021. Sources from 2022 to 2026 on these concepts were not researched.

## Concept 1: Provenance interchange model (OPM to PROV)

1. **Open Provenance Model (OPM), version 1.00 to 1.1, 2007 to 2010 (A3-SR-01).** A data model crafted at an August 2007 workshop after the second Provenance Challenge. Version 1.01 followed a June 2008 workshop. Version 1.1 followed a public vote. Criticism recorded in the same source: "further guidance is needed" for agents, and "no guidance is provided by OPM" for collections (A3-SR-01).
2. **Provenance Incubator Group report, 8 December 2010 (A3-SR-02).** The group chose OPM as the reference model for mapping other vocabularies. It recorded that OPM "cannot be used to represent" provenance of changing Web resources and that no standard exists for versioning provenance. It issued eight recommendations (A3-SR-02).
3. **PROV Recommendations, 30 April 2013 (A3-SR-03, A3-SR-04).** The Working Group says PROV's design stems from the Incubator recommendations (A3-SR-03). It changed PROV-DM after Last Call comments, for example ISSUE-525 (Membership, Alternate and Specialization are not Influence) and the move of "Mention" to a separate note (A3-SR-04).
4. **Criticism after 2013.** Gap. No source on it was found.

The sources do not say that PROV replaced OPM, and they give no term-by-term comparison. The two steps are linked only by the Incubator report, which chose OPM as its reference (A3-SR-02).

## Concept 2: Nanopublication structure and identity

1. **Richly annotated statements, October 2009 (A3-SR-05).** A statement carries context and provenance and is the unit of publication. The authors give one reason for the design: one triple per connection would make the store "explode". They criticize no earlier formulation (A3-SR-05).
2. **Statements, annotations and S-Evidence on Named Graphs, draft of February 2010 (A3-SR-06).** A nanopublication is a set of annotations on one uniquely identified statement. Each statement is a separate Named Graph. The draft states that SWAN's provenance ontology offers no way to claim a nanopublication, and it proposes the Semantic Web Publishing ontology for that (A3-SR-06).
3. **Informal assertions with AIDA sentences, March 2013 (A3-SR-07).** The authors call the requirement of a formal RDF assertion "problematic" and "unrealistic in many cases". They propose English sentences in the AIDA scheme (A3-SR-07).
4. **Trusty URIs, May 2014 (A3-SR-08).** Criticism: "Published nanopublications are supposed to be immutable, but the current web has no mechanism to enforce this". The fix is a cryptographic hash inside the URI (A3-SR-08).
5. **Decentralized server network, preprint of 2014 and 2015 (A3-SR-09).** Criticism: repositories such as Figshare and Dryad have "centralized architectures" and give "no possibility to check whether the data have been [...] modified". The fix is a network of servers that store nanopublications and rely on trusty URIs (A3-SR-09).
6. **Three-graph guidelines, undated, not older than 2014 (A3-SR-10).** Assertion, provenance and publication info, with trusty URIs as the integrity key. The page names no criticism and gives no version history (A3-SR-10).
7. **Claim semantics beyond RDF and OWL, 2021 (A3-SR-11).** The authors find that claims in articles are "more complex than what a straight-forward application of formalisms like RDF or OWL account for". They derive a five-slot "super-pattern" that maps to higher-order logic. This criticism targets plain RDF and OWL, not the nanopublication specification (A3-SR-11).

Gap between steps 2 and 6: the 2010 draft uses statement, annotation and S-Evidence, while the guidelines use three graphs. No source states why the terms changed. A separate criticism of nanopublications, by the micropublication authors, sits under Concept 3 (A3-SR-13).

## Concept 3: Scientific claim and evidence model (SWAN to micropublications)

1. **SWAN ontology, 2008 journal paper and 2009 W3C Note (A3-SR-12).** A discourse ontology for neuromedicine with a provenance module. The Note holds no criticism of itself. The 2008 journal paper is unread, so step 1 rests on the later Note.
2. **Micropublications, submitted May 2013, published July 2014 (A3-SR-13).** The authors criticize SWAN: it models a principal statement with supporting statements from the same publication only, and it supports neither claim networks nor direct empirical evidence. They criticize nanopublications: they "model only the indicated statement" and give no way "to build claim networks of arbitrary depth" (A3-SR-13). The new model adds claims, support and challenge links and evidence graphs. It moved from the Annotation Ontology to Open Annotation for attaching these to documents (A3-SR-13).
3. **Criticism after 2014.** Gap. No source was found.

This sequence is thin: two steps, one of which carries the criticism, written by authors who also wrote SWAN. It documents a change of design, not several rounds of review.

## Concept 4: Argument Interchange Format (AIF)

1. **Argument mark-up languages before 2006.** Gap as a step. The only source is the criticism in A3-SR-14: each language serves one tool, and none has a semantic model for software agents. The languages' own documents were not read.
2. **Abstract AIF model, 2006 (A3-SR-14).** Information nodes (claims) and scheme nodes (inference, preference, conflict). The authors call the draft "a starting point for further discussion", not a definitive model (A3-SR-14).
3. **AIF-RDF and ArgDF, 2007 (A3-SR-15).** AIF extended with Walton argumentation schemes and form nodes, written in RDF Schema. Criticism of earlier argument tools: they support few participants and fix one argumentation theory. Criticism of the RDFS choice: "disjointedness cannot be expressed in RDFS" (A3-SR-15).
4. **AIF+ for dialogue, 2008 (A3-SR-16).** Criticism of the 2006 form: it "had not integrated modelling of dialogue". The extension maps locutions to information nodes and steps between locutions to scheme nodes. The source gives no RDF or OWL form of AIF+ (A3-SR-16).
5. **Description Logic ontology in OWL, 2011 (A3-SR-17).** Criticism of the 2007 RDFS form: it "causes some redundancy at the instance level" and does not capture that a scheme node instantiates a generic scheme. Schemes become classes and scheme nodes become their instances, which allows OWL reasoning (A3-SR-17).

Step 4 extends the 2006 model, not the 2007 or 2011 ontologies. The sources do not state that the dialogue extension and the OWL ontology were ever combined.

## Gaps

- **Toulmin and IBIS.** The brief names argumentation models. Toulmin's model appears only in A3-SR-13, which says it avoids Toulmin's separate warrant and backing classes. IBIS appears only as a proposed mapping in A3-SR-12. Their original texts (Toulmin 1958, Kunz and Rittel 1970) were not researched.
- **PROV-O.** A fetch of PROV-O showed its Recommendation date (30 April 2013) and earlier drafts (24 July 2012, 11 December 2012, 12 March 2013), but no record was made. Its change logs were not read. The qualified-influence pattern in PROV-O belongs to the statements-about-statements question in area 2 and was not examined here.
- **OPM to PROV.** No W3C or OPM-authored text states what PROV changed from OPM or why. A secondary search result (a Portuguese-language comparison paper) maps OPM terms to PROV terms but was not read, and it is not recorded.
- **Unreachable or unread texts.** The published IOS Press version of Groth et al. 2010 and the PeerJ 2016 paper on decentralized nanopublications (HTTP 403). The COMMA 2010 AIF+ paper (HTTP 503). The 2008 SWAN journal paper (cookie wall). Kuhn et al. 2018 on the nanopublication network and the 2015 TKDE extension of trusty URIs were found but not read. Earlier versions of the nanopublication guidelines were not located.
- **Unread parts.** The last 18,118 characters of A3-SR-02 and the Discussion section of A3-SR-13.
- **Dates.** Several records use month-only or year-only dates, A3-SR-06 takes its date from a URL, and A3-SR-10 uses the retrieval date. Each record says which.
- **Independence.** All nanopublication records after 2009 come from one research circle around Kuhn, Dumontier and Groth, and the AIF records share Rahwan and Reed. No outside critic was found.
- **Record count.** The set has 17 records, above the aim of 8 to 15. Each step in the sequences above needs one source, so none was dropped.
