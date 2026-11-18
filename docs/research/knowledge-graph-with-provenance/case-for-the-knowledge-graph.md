# The Case For A Knowledge Graph With Provenance

This document joins three settled inputs: the stakeholder's [design position](design-position.md), the [first survey](../knowledge-graph-state-of-the-art/survey-report.md) on graph models, and the [second survey](../knowledge-across-sources/survey-report.md) on knowledge across sources. It adds no research. Both surveys number their records the same way, so [A1-SR-18](../knowledge-graph-state-of-the-art/sources/area-1/A1-SR-18-gpml-gql-pgq.md) and [A1-SR-18](../knowledge-across-sources/sources/area-1/A1-SR-18-w3c-web-annotation-data-model-2017.md) are two different records. Every record identifier below is therefore a link to its file.

## 1. The decision in brief

People keep knowledge in news, email, chat, and conversation transcripts. Across those sources, a claim loses its origin, and an idea loses its link to the decisions that rest on it.

The proposed system is a knowledge graph with provenance in three layers. The provenance layer keeps each source and the exact spans quoted from it. The knowledge layer keeps problems, conjectures, criticisms, and tests. The decision layer keeps each human decision as a node in the same store, linked to the conjectures it rests on. A refutation in the knowledge layer reopens the decisions that rest on the refuted conjecture.

The Agent Factory is the first tenant and the method that builds the system. Its own sessions and decisions are the first source family and the pilot.

The stakeholder decides four questions, set out in section 7:

1. Whether the store follows the Resource Description Framework (RDF) or a property graph.
2. Whether one store serves one person or one team.
3. Which candidate design claim gets falsification research first.
4. Which identifier (ID) prefix the records use.

Section 8 describes the pilot that follows.

## 2. The problem

Knowledge spread across documents, messages, and sessions loses its sources and its links. The factory shows this on its own material, as the first round's [internal inventory](sources/internal-inventory.md) found. Only 19 of 83 proposals have a Decisions table, and each table numbers its own rows, so `DEC-01` exists 19 times. The "Raised by" cell holds free text such as "draft conversation", never a link. The twenty decisions on the run lifecycle sit in an untracked handoff, while the proposal says "Open Questions: None". All sources hold about 636,000 words, so no session can read them all.

Other sources lose links in the same way. Mail software often wrote the reply header as free text ([A3-SR-06](../knowledge-across-sources/sources/area-3/A3-SR-06-jwz-message-threading-1997-2002.md)). A Slack export does not separate thread replies from channel messages ([A3-SR-13](../knowledge-across-sources/sources/area-3/A3-SR-13-slack-help-data-exports.md)). In one study, up to 75% of Dutch online news articles came from the news agency, much of it verbatim ([A4-SR-04](../knowledge-across-sources/sources/area-4/A4-SR-04-boumans-agency-copy-2018.md)). Without provenance, fifty copies of one report look like fifty sources that agree.

Files in git cannot hold this material ([design position](design-position.md#why-files-in-git-do-not-hold-the-knowledge)). One meeting yields too many ideas for review in a pull request, and graph and similarity queries need a database. A quote marked by quotation marks in prose also breaks when the source has quotation marks of its own; the factory's own quote check failed this way during the second survey.

## 3. The proposed system

### 3.1 Three layers

| Layer      | Holds                                                                | Who writes it                  | Where it lives                                              |
| ---------- | -------------------------------------------------------------------- | ------------------------------ | ----------------------------------------------------------- |
| Provenance | Sources and the exact spans quoted from them                         | Import scripts, never edited   | A store outside git, where a record can be deleted for good |
| Knowledge  | Problems, conjectures, criticisms, tests, and their outcomes         | Agents propose, reviewers test | The same store, rebuildable from the sources                |
| Decisions  | Do, won't do, defer, accept, each naming the conjectures it rests on | A person, always               | The same store, as nodes linked to their conjectures        |

The ideas carry the volume, and the decisions carry the authority. That authority comes from the person who records a decision and from its history, not from git. The store never overwrites a decision; a new one replaces an old one and names it. A markdown view can serve review, but it is never the record ([design position](design-position.md#three-layers)). Copyright and data protection are out of scope for now and for both surveys, so every source counts as storable.

### 3.2 Claims, ideas, and decisions

The system keeps three units as distinct records:

- A claim is a statement that a source makes about the world. Fact-checking research matches and verifies claims as units of their own ([A2-SR-10](../knowledge-across-sources/sources/area-2/A2-SR-10-kazemi-claim-matching-beyond-english-2021.md), [A2-SR-12](../knowledge-across-sources/sources/area-2/A2-SR-12-schlichtkrull-averitec-2023.md)).
- An idea is a conjecture that a person or an agent proposes against a problem. The second survey found no record that treats an idea as a unit of its own ([§ 5](../knowledge-across-sources/survey-report.md#5-what-this-means-for-the-wider-knowledge-system)).
- A decision is a choice that a person makes. Meeting research labels a decision as roles of several utterances: an issue, a proposed resolution, and an agreement ([A3-SR-21](../knowledge-across-sources/sources/area-3/A3-SR-21-fernandez-decisions-multiparty-dialogue-2008.md)). Flat labels on single utterances reached F-scores of about 0.3 and 0.35 ([A3-SR-20](../knowledge-across-sources/sources/area-3/A3-SR-20-purver-action-items-2007.md), [A3-SR-21](../knowledge-across-sources/sources/area-3/A3-SR-21-fernandez-decisions-multiparty-dialogue-2008.md)). So the system anchors each role to its own utterance.

Claims and ideas are conjectures in the knowledge layer. Every record points to at least one span, which names the source item, the exact quote, the speaker or author, and the time.

### 3.3 The Popperian model

The model uses Popper's terms: a problem, competing conjectures against it, criticism, and error elimination. The design position sets six rules ([design position](design-position.md#the-popperian-model)):

1. The problem is a node type of its own. The Issue-Based Information System (IBIS) has the same shape: issue, position, argument.
2. Every conjecture states what would refute it. A conjecture without a refutation condition is marked "not testable yet", not discarded.
3. A status describes the history of tests, not truth: conjecture, corroborated, refuted, unresolved, superseded, or withdrawn.
4. Repetition is not support. A claim that fifty outlets repeat gains fifty mentions and passes no test. Merging duplicates raises a mention count, never the corroboration.
5. A refutation is fallible too. It points to the spans it rests on, so anyone can challenge it.
6. A refutation reopens the decisions that rest on the refuted conjecture. This is the error elimination.

### 3.4 How a decision reopens

A decision in this repository reads: "Won't do: one Git ref per ID, because leased pushes on many refs are too slow." When a test refutes the conjecture about speed, the graph flags the decision for review. Today nothing does that. A person then writes a new decision that names the old one as replaced. The flag is one query inside the store, from the refuted conjecture to every decision that names it.

## 4. Sources and their anchors

An anchor is the link from a record to the span it came from. Each source family offers an identifier, and each identifier has its own scope. The table covers email, Slack, the chat protocol Matrix, the Extensible Messaging and Presence Protocol (XMPP), and the factory's own sessions.

| Source family    | Identifier                                 | Unique within               | Thread structure                                           | Records                                                                                                                                                                                                          |
| ---------------- | ------------------------------------------ | --------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Email            | `Message-ID`, new for each message version | The world, by rule          | `In-Reply-To` names the parent, `References` the ancestors | [A3-SR-04](../knowledge-across-sources/sources/area-3/A3-SR-04-rfc2822-internet-message-format-2001.md), [A3-SR-05](../knowledge-across-sources/sources/area-3/A3-SR-05-rfc5322-internet-message-format-2008.md) |
| Slack            | `ts`, which looks like a time but is an ID | One channel                 | One level, keyed by `thread_ts`                            | [A3-SR-14](../knowledge-across-sources/sources/area-3/A3-SR-14-slack-dev-retrieving-messages.md)                                                                                                                 |
| Matrix           | Event ID, a hash of the event              | Not stated; no domain part  | Flat threads that point to their root                      | [A3-SR-11](../knowledge-across-sources/sources/area-3/A3-SR-11-matrix-room-versions-event-ids.md), [A3-SR-12](../knowledge-across-sources/sources/area-3/A3-SR-12-matrix-client-server-threading.md)             |
| XMPP             | Stanza ID, an Experimental extension       | The entity that assigned it | An opaque thread value per conversation                    | [A3-SR-08](../knowledge-across-sources/sources/area-3/A3-SR-08-rfc6121-xmpp-im-thread-2011.md), [A3-SR-10](../knowledge-across-sources/sources/area-3/A3-SR-10-xep0359-stable-stanza-ids-2015-2023.md)           |
| Factory sessions | `uuid` per message, with `sessionId`       | Not stated                  | `parentUuid` names the parent message                      | [design position](design-position.md#the-store-already-half-exists)                                                                                                                                              |

### 4.1 Email

The email rules are explicit, and practice breaks them. A Request for Comments (RFC) is an internet standard text. RFC 2822 builds `References` from the parent's `References` plus the parent's `Message-ID` ([A3-SR-04](../knowledge-across-sources/sources/area-3/A3-SR-04-rfc2822-internet-message-format-2001.md)). One developer's survey of 22,950 messages found free text in `In-Reply-To` and contradictory `References` ([A3-SR-06](../knowledge-across-sources/sources/area-3/A3-SR-06-jwz-message-threading-1997-2002.md)). The threading standard of the Internet Message Access Protocol (IMAP) falls back on the first valid `Message-ID` in `In-Reply-To` ([A3-SR-07](../knowledge-across-sources/sources/area-3/A3-SR-07-rfc5256-imap-sort-thread-2008.md)). So an import must tolerate missing and contradictory parents.

### 4.2 Chat

A chat anchor stores the identifier together with its scope, because a Slack `ts` is unique only within one channel ([A3-SR-14](../knowledge-across-sources/sources/area-3/A3-SR-14-slack-dev-retrieving-messages.md)). The official Slack export puts thread replies in the flow of the channel ([A3-SR-13](../knowledge-across-sources/sources/area-3/A3-SR-13-slack-help-data-exports.md)). Matrix moved to a hash of the event as its ID, because servers met duplicate IDs ([A3-SR-11](../knowledge-across-sources/sources/area-3/A3-SR-11-matrix-room-versions-event-ids.md)). The second survey reads this, untested, as a hint that a hash of each imported item could serve as an ID without scope.

### 4.3 Transcripts

Factory sessions carry a message ID and a parent ID, so every record can point to its exact message. The pipeline stores a session once per recording, so an import first removes repeated copies ([design position](design-position.md#the-store-already-half-exists)). Meeting recordings are weaker anchors. Speaker diarization answers "who spoke when" but does not name the speakers ([A3-SR-22](../knowledge-across-sources/sources/area-3/A3-SR-22-ryant-dihard-ii-2019.md)). One meeting corpus attributes speech by recording one close-talking channel per speaker ([A3-SR-17](../knowledge-across-sources/sources/area-3/A3-SR-17-ami-meeting-corpus-documentation.md)).

### 4.4 News

The second survey recorded no message identity for news, only an anchor in the text. The World Wide Web Consortium (W3C) sets web standards. Its Web Annotation Data Model points into a document with a Text Quote Selector, which quotes the passage and the words around it ([A1-SR-18](../knowledge-across-sources/sources/area-1/A1-SR-18-w3c-web-annotation-data-model-2017.md)). A State names the version read. The factory's quoted anchors have the same shape. A news anchor also needs the source's own time, because one fact-checking benchmark allows only evidence published before the claim ([A2-SR-12](../knowledge-across-sources/sources/area-2/A2-SR-12-schlichtkrull-averitec-2023.md)).

### 4.5 How settled these anchors are

The second survey ranks concepts by how often each was formulated, criticized, and reformulated. A rank does not say whether a concept holds. These rows are copied from its [table](../knowledge-across-sources/survey-report.md#3-hardened-concepts):

| Rank | Concept                    | Rounds | Criticisms |
| ---- | -------------------------- | ------ | ---------- |
| 1    | In-Reply-To and References | 3      | 3          |
| 2    | The Matrix event ID        | 3      | 2          |
| 3    | The stance-detection task  | 3      | 2          |
| 4    | The Message-ID rule        | 5      | 2          |
| 6    | Measuring a frame in text  | 3      | 2          |
| 7    | Text reuse class           | 3      | 2          |
| 10   | Frame                      | 4      | 3          |

All three Matrix steps come from one record with an unconfirmed date ([A3-SR-11](../knowledge-across-sources/sources/area-3/A3-SR-11-matrix-room-versions-event-ids.md)). Frame ranks last, because most of its anchors are secondary sources.

## 5. Propagation

### 5.1 The 51-source model

A wire report and fifty outlets that repeat it are 51 sources ([design position](design-position.md#the-propagation-model)). The wire report is the primary source of the factual claim, and repetition adds no support to it. Each outlet is a source of what it did with the report, in one of four reuse classes. It copies the wording (verbatim), changes the wording or the claim's strength (altered), adds its own claims, sentiment, or spin (reframed), or reports on its own and becomes a new primary source (independent). Spread and reach are knowledge in their own right.

No recorded source has one scheme with all four classes. The closest match is a claim provenance graph with edges labelled identical, paraphrased, entailed, or contradicted. Its authors state that they have not solved the problem ([A4-SR-15](../knowledge-across-sources/sources/area-4/A4-SR-15-zhang-claim-provenance-2020.md)).

### 5.2 What each class can show

| Class       | A recorded method shows                     | The second survey found no method that shows       | Who sets the edge                     |
| ----------- | ------------------------------------------- | -------------------------------------------------- | ------------------------------------- |
| Verbatim    | Shared wording and its share                | Who copied from whom, or a shared upstream source  | A script checks the overlap           |
| Altered     | Changed meaning, scored without a direction | An automatic score with the direction of change    | A script scores it, without direction |
| Reframed    | A frame or stance label for one text        | A frame change between a source and another outlet | A person, as an attributed judgement  |
| Independent | That no reuse was found                     | Independence from an undisclosed shared source     | A person or a disclosed source        |

Verbatim reuse is found by text reuse detection, which measures shared wording. The METER corpus detects agency copy by string overlap ([A4-SR-01](../knowledge-across-sources/sources/area-4/A4-SR-01-clough-meter-2002.md)). Memetracker groups variants of quoted phrases but does not identify the outlet that copied ([A4-SR-03](../knowledge-across-sources/sources/area-4/A4-SR-03-leskovec-memetracker-2009.md)). A shared press release produces the same overlap as direct copying ([A4-SR-04](../knowledge-across-sources/sources/area-4/A4-SR-04-boumans-agency-copy-2018.md)).

Altered reuse has a manual method with a direction and automatic methods without one. Sumner et al. code causal claim strength by hand on a seven-point scale ([A4-SR-14](../knowledge-across-sources/sources/area-4/A4-SR-14-sumner-exaggeration-press-releases-2014.md)). The Scientific Paraphrase and Information Change Dataset (SPICED) scores change between science findings automatically ([A4-SR-13](../knowledge-across-sources/sources/area-4/A4-SR-13-wright-spiced-2022.md)). Outside science, the second survey records two automatic methods at the level of meaning. Textual entailment labels the provenance graph's edges ([A4-SR-15](../knowledge-across-sources/sources/area-4/A4-SR-15-zhang-claim-provenance-2020.md)). Claim matching pairs messages that one fact-check can serve ([A2-SR-10](../knowledge-across-sources/sources/area-2/A2-SR-10-kazemi-claim-matching-beyond-english-2021.md)), and repeats of a claim are more often paraphrases than copies ([A4-SR-16](../knowledge-across-sources/sources/area-4/A4-SR-16-nakov-assisting-fact-checkers-2021.md)). Neither method gives a direction.

Reframing is measured one text at a time. The Media Frames Corpus labels the frame of an article ([A4-SR-09](../knowledge-across-sources/sources/area-4/A4-SR-09-card-media-frames-corpus-2015.md)). Stance detection labels a text against a target, and stance differs from sentiment ([A4-SR-11](../knowledge-across-sources/sources/area-4/A4-SR-11-mohammad-semeval-2016-task6.md)). People agree poorly on these labels: alpha 0.342 for frames before consolidation ([A4-SR-10](../knowledge-across-sources/sources/area-4/A4-SR-10-piskorski-semeval-2023-task3.md)), and kappa .218 on three related stance classes ([A4-SR-12](../knowledge-across-sources/sources/area-4/A4-SR-12-hanselowski-fnc1-retrospective-2018.md)). The nearest pairwise method, MediaSpin, labels bias that a headline edit adds or removes within one outlet. Its most common error is the direction ([A4-SR-17](../knowledge-across-sources/sources/area-4/A4-SR-17-verma-mediaspin-2026.md)).

Independent reporting cannot be told apart from undisclosed reuse of a shared source. Three records name this limit ([A4-SR-04](../knowledge-across-sources/sources/area-4/A4-SR-04-boumans-agency-copy-2018.md), [A4-SR-14](../knowledge-across-sources/sources/area-4/A4-SR-14-sumner-exaggeration-press-releases-2014.md), [A4-SR-15](../knowledge-across-sources/sources/area-4/A4-SR-15-zhang-claim-provenance-2020.md)). So the system records "no reuse found", and only a person or a disclosed source turns it into "independent".

Memetracker alone tracks spread, with a typical lag of 2.5 hours between news and blog peaks ([A4-SR-03](../knowledge-across-sources/sources/area-4/A4-SR-03-leskovec-memetracker-2009.md)). No record measures reach per outlet, and the search plan did not cover reach.

Every edge beyond a script's overlap check or score is a judgement, stored with its author, label scheme, and spans. So it is a statement about a statement, like a refutation.

## 6. What the field has settled for the graph

The first survey ranks graph concepts by the same rule. Section 6.4 explains the Open Provenance Model (OPM) and PROV. These rows are copied from its [table](../knowledge-graph-state-of-the-art/survey-report.md#3-hardened-concepts). A dash marks a concept below the entry rule of 3 rounds and 2 recorded criticisms.

| Rank | Concept                                   | Rounds | Criticisms |
| ---- | ----------------------------------------- | ------ | ---------- |
| 1    | Nanopublication structure and identity    | 5      | 3          |
| 2    | Argument Interchange Format               | 4      | 2          |
| 4    | Identity meaning of owl:sameAs            | 4      | 2          |
| 5    | Shape languages for RDF validation        | 4      | 3          |
| 6    | Semantics of recursive shapes             | 7      | 3          |
| -    | Provenance interchange model, OPM to PROV | 2      | 1          |
| -    | Entity resolution methods                 | 4      | 1          |

### 6.1 Nanopublications and the Argument Interchange Format

A nanopublication splits one claim into three named graphs: the assertion, its provenance, and information about the publication ([A3-SR-10](../knowledge-graph-state-of-the-art/sources/area-3/A3-SR-10-nanopublication-guidelines.md)). A named graph is a set of RDF statements with its own name. Trusty Uniform Resource Identifiers (URIs) put a hash of the content into the identifier, because the web "has no mechanism to enforce" immutability ([A3-SR-08](../knowledge-graph-state-of-the-art/sources/area-3/A3-SR-08-kuhn-dumontier-trusty-uris.md)). Critics add that nanopublications "model only the indicated statement" ([A3-SR-13](../knowledge-graph-state-of-the-art/sources/area-3/A3-SR-13-clark-micropublications.md)), so they carry no links between claims.

The Argument Interchange Format (AIF) supplies those links. Information nodes hold claims, and scheme nodes hold the inference, preference, or conflict between them ([A3-SR-14](../knowledge-graph-state-of-the-art/sources/area-3/A3-SR-14-chesnevar-towards-an-argument-interchange-format.md)). A criticism maps onto a conflict node. The core AIF requires disjoint node classes ([A3-SR-15](../knowledge-graph-state-of-the-art/sources/area-3/A3-SR-15-rahwan-world-wide-argument-web.md)), so the store keeps node types apart.

### 6.2 Why `owl:sameAs` is the wrong tool for "same claim"

The Web Ontology Language (OWL) defines `owl:sameAs` as strict identity ([A5-SR-01](../knowledge-graph-state-of-the-art/sources/area-5/A5-SR-01-owl-reference-2004.md)). In one rater study, about 51% (plus or minus 21%) of sampled links looked correct ([A5-SR-04](../knowledge-graph-state-of-the-art/sources/area-5/A5-SR-04-halpin-sameas-isnt-same-2010.md)). Merging two profiles of one person let a reasoner infer a job the person never held ([A5-SR-03](../knowledge-graph-state-of-the-art/sources/area-5/A5-SR-03-ding-sameas-empirical-2010.md)). So a merge of two claims must not pass a status or a decision from one to the other, as rule 4 of section 3.3 says. Finding duplicates is entity resolution, and its latest prompted models need a prompt per model and dataset ([A5-SR-13](../knowledge-graph-state-of-the-art/sources/area-5/A5-SR-13-peeters-llm-entity-matching-2023.md)).

### 6.3 Shape validation

OWL treats a missing fact as unknown, which is the open-world assumption ([A4-SR-01](../knowledge-graph-state-of-the-art/sources/area-4/A4-SR-01-owl2-primer-open-world.md)). So a person without a social security number raises no error ([A4-SR-02](../knowledge-graph-state-of-the-art/sources/area-4/A4-SR-02-motik-integrity-constraints-owl.md)). A record check needs the closed-world assumption, so that a conjecture without a span fails. The Shapes Constraint Language (SHACL) treats the data as complete ([A4-SR-14](../knowledge-graph-state-of-the-art/sources/area-4/A4-SR-14-oudshoorn-shacl-ontologies-2026.md)) and became a W3C Recommendation in 2017 ([A4-SR-11](../knowledge-graph-state-of-the-art/sources/area-4/A4-SR-11-shacl-recommendation-2017.md)).

SHACL leaves the meaning of recursive shapes to each implementation, and the SHACL 1.2 draft keeps that position ([A4-SR-16](../knowledge-graph-state-of-the-art/sources/area-4/A4-SR-16-shacl12-core-working-draft-2026.md)). The SPARQL Protocol and RDF Query Language (SPARQL) queries RDF, and the draft's reason is that implementations can then "issue a static set of SPARQL queries" without supporting cycles. A 2026 test found that "current tools implicitly commit to different semantics" ([A4-SR-15](../knowledge-graph-state-of-the-art/sources/area-4/A4-SR-15-common-foundations-recursive-shape-languages-2026.md)). So the record rules stay non-recursive.

### 6.4 Provenance from OPM to PROV

OPM dates from a 2007 workshop ([A3-SR-01](../knowledge-graph-state-of-the-art/sources/area-3/A3-SR-01-opm-core-specification.md)). A W3C Incubator report of 2010 says OPM "cannot be used to represent" provenance of changing Web resources ([A3-SR-02](../knowledge-graph-state-of-the-art/sources/area-3/A3-SR-02-prov-incubator-final-report.md)). W3C published the PROV family in 2013, with the PROV Ontology (PROV-O) among its Recommendations ([A3-SR-03](../knowledge-graph-state-of-the-art/sources/area-3/A3-SR-03-prov-overview.md)). The PROV data model names relations such as `wasDerivedFrom` and `wasAttributedTo` ([A3-SR-04](../knowledge-graph-state-of-the-art/sources/area-3/A3-SR-04-prov-dm-recommendation.md)). No record states that PROV replaced OPM.

### 6.5 Data models and the standards status

RDF needs an extra node or a named graph to annotate an edge, and a property graph carries key-value pairs on it. A secondary survey says the two convert without loss and that practical factors often decide between them ([A1-SR-20](../knowledge-graph-state-of-the-art/sources/area-1/A1-SR-20-hogan-kg-survey.md)). A 2015 study found "no clear winner between standard reification, n-ary predicates and named graphs" ([A2-SR-11](../knowledge-graph-state-of-the-art/sources/area-2/A2-SR-11-reifying-rdf-wikidata-2015.md)). RDF 1.2 adds the triple term, a triple used inside another triple ([A2-SR-17](../knowledge-graph-state-of-the-art/sources/area-2/A2-SR-17-rdf12-concepts-cr-2026.md)).

The International Organization for Standardization (ISO) publishes the Graph Query Language (GQL) and the property graph part of the Structured Query Language (SQL), called SQL Property Graph Queries (SQL/PGQ). The survey records only their catalogue status, because their texts are not free.

| Standard   | Status on 17 November 2026                                                                  | Records                                                                                                                                                                                   |
| ---------- | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RDF 1.2    | Concepts and Semantics are Candidate Recommendation Drafts; the syntaxes are Working Drafts | [A1-SR-01](../knowledge-graph-state-of-the-art/sources/area-1/A1-SR-01-rdf12-concepts.md), [A1-SR-02](../knowledge-graph-state-of-the-art/sources/area-1/A1-SR-02-w3c-wg-publications.md) |
| SPARQL 1.2 | All documents are Working Drafts                                                            | [A1-SR-02](../knowledge-graph-state-of-the-art/sources/area-1/A1-SR-02-w3c-wg-publications.md), [A1-SR-03](../knowledge-graph-state-of-the-art/sources/area-1/A1-SR-03-sparql12-query.md) |
| GQL        | Published 12 April 2024, "to be revised"; edition 2 is a committee draft                    | [A1-SR-04](../knowledge-graph-state-of-the-art/sources/area-1/A1-SR-04-iso-39075-2024.md), [A1-SR-05](../knowledge-graph-state-of-the-art/sources/area-1/A1-SR-05-iso-39075-cd-ed2.md)    |
| SQL/PGQ    | Published 1 June 2023, "to be revised"                                                      | [A1-SR-06](../knowledge-graph-state-of-the-art/sources/area-1/A1-SR-06-iso-9075-16-2023.md)                                                                                               |

The one embedded graph store the survey records, Kuzu, has an archived repository ([A6-SR-16](../knowledge-graph-state-of-the-art/sources/area-6/A6-SR-16-kuzu-readme.md), [A6-SR-17](../knowledge-graph-state-of-the-art/sources/area-6/A6-SR-17-register-kuzu-archived.md)).

## 7. Open decisions

### 7.1 RDF or a property graph

- Case: An outlet repeats a wire report and adds its own spin. A reviewer labels the edge from the article to the report "reframed" and quotes a span from each text.
- Outcome with a property graph: The edge `reframes` carries the reviewer, the label scheme, and both spans as properties.
- Outcome with RDF: The edge needs provenance of its own, so it is a statement about a statement. RDF writes it as a named graph, a reification, or an RDF 1.2 triple term, which is still a draft.
- Recommendation: Build a property graph in tables of DuckDB, an embedded analytical database, with provenance columns named after PROV relations and the three nanopublication parts kept apart. A property graph holds a statement about a statement today, while RDF's route is a draft. DuckDB already runs in the factory, and the one recorded embedded graph store is archived (section 6.5).
- What would change it: RDF wins if the graph must exchange records with outside parties, because PROV-O and SHACL are RDF Recommendations, or once RDF 1.2 becomes one. A query the tables cannot answer reopens the engine choice.
- What the answer settles: The store schema and the import format of the pilot.

### 7.2 One store per person or per team

The wider scope rules out a store per repository, because a chat thread is not about one repository.

- Case: A Slack thread in the team channel discusses the counter rule of this repository. One team member's mailbox holds a newsletter on graph databases.
- Outcome with a store per person: Each member who imports the thread holds a copy, so joining copies of one idea needs entity resolution across stores. The newsletter raises no access question.
- Outcome with a store per team: The thread and its ideas exist once. Each record needs an owner and a read rule, because the newsletter came from one person's mailbox.
- Recommendation: Start with one store per person, and let each project write back only the decisions that concern it. DuckDB runs inside one program, so one person's store needs no server and no access rules. The factory's transcripts already sit in each person's checkout.
- What would change it: If the pilot shows that most ideas come from team channels and team meetings, a team store avoids the copies. It then needs a server or a sync method, and access rules.
- What the answer settles: Where the store lives, and whether the proposal includes access rules.

### 7.3 Which candidate claim gets falsification research first

The first survey states nine candidate claims ([§ 7](../knowledge-graph-state-of-the-art/survey-report.md#7-structured-block)), and so does the second ([§ 6](../knowledge-across-sources/survey-report.md#6-structured-block)). These four bear most on the pilot:

| Survey | No. | Claim in short                                                                                                  |
| ------ | --- | --------------------------------------------------------------------------------------------------------------- |
| Second | 6   | Transcript decisions can be extracted as issue, proposal, and agreement, each anchored to an existing utterance |
| First  | 8   | Extraction by a large language model (LLM) yields quotes that occur verbatim in the source                      |
| Second | 4   | Email threads can be rebuilt from `Message-ID`, `In-Reply-To`, and `References` alone                           |
| Second | 1   | A script can record a verbatim reuse edge by text overlap alone, without human review                           |

- Case: The pilot imports the session behind the run-lifecycle handoff, whose twenty decisions are already listed.
- Outcomes: Second-survey claim 6 tests extraction against that known list and checks every anchor. First-survey claim 8 checks only the quotes. Claims 4 and 1 need email or news, which stage 1 does not import.
- Recommendation: Test second-survey claim 6 first, then first-survey claim 8. The handoff gives the test a known answer, and every later refutation rests on anchored spans.
- What would change it: If news becomes the second source family, second-survey claim 1 moves to second place.
- What the answer settles: The brief of the first falsification study.

### 7.4 The ID prefix for records

- Case: A record named `IDEA-0042` appears next to the architecture decision record (ADR) [ADR-0017](../../adr/0017-cycle-based-orchestration-supersedes-linear-playbook-fsm.md), which defines an IDEA delivery cycle.
- Outcomes: With `IDEA`, the reader cannot tell record from cycle. `CONCEPT` collides with the CONCEPT cycle of [ADR-0018](../../adr/0018-concept-internal-sequence-is-agent-owned.md). `NOTION` and `KI` (knowledge item) collide with neither ([synthesis](synthesis.md#decisions-for-the-stakeholder)).
- Recommendation: Decide after stage 1, which needs no production IDs. Then choose `NOTION`, because a reader understands it without looking it up. The proposal must also settle whether store IDs use the factory counter, which today assigns IDs to files in git.
- What would change it: If claims and ideas get separate prefixes, a narrower name for each fits better.
- What the answer settles: The ID prefix registry entry, which changes together with the ID allocator ([process design](sources/codex-process-design.md#fit-with-factory-constraints)).

## 8. Next step: the pilot

The stakeholder has not yet approved the pilot ([design position](design-position.md#the-spike)). It runs in two stages.

### 8.1 Stage 1: factory sessions

- What it builds: An import of a few sessions from `usage/transcripts/`, starting with the session behind the run-lifecycle handoff of 2026-11-16. It removes repeated copies, extracts ideas and decisions with message anchors, and loads them into a DuckDB file outside git.
- What it shows: A session asks "What was decided about the run lifecycle?" The answer finds the twenty decisions of the handoff, each with a message that exists.
- What counts as failure: A decision is missing, or an anchor points to no message.

### 8.2 Stage 2: one email mailbox

Email is the recommended second family. Its anchors hold two of the top four ranks in section 4.5, and its import rules are written down. Slack exports lose thread structure ([A3-SR-13](../knowledge-across-sources/sources/area-3/A3-SR-13-slack-help-data-exports.md)), and news needs a person for most propagation edges.

- What it builds: An import of one mailbox that stores each message with its `Message-ID`, rebuilds threads from `In-Reply-To` and `References`, and anchors claims and decisions to quoted spans.
- What it shows: Whether second-survey claim 4 holds for the system's own mail.
- What counts as failure: More replies than a share set before the test lack a resolvable parent or carry contradictory `References`.

## 9. Limitations

- The factory's deterministic gates read files in git, so checks on the store must be written as queries ([design position](design-position.md#costs)).
- Every command-line interface (CLI) the factory runs in needs the same query command.
- The provenance and knowledge layers can be rebuilt from the sources. Decisions cannot, so the store needs a backup and an export of its decision history that nothing can rewrite. The store needs its own approved proposal before a shipped agent may reference it.
- No record covers DuckDB as a graph store, and no record measures how accurately a current LLM extracts ideas.
- The first survey was accepted without a sixth validation pass, and three notes stay open ([pass 5](../knowledge-graph-state-of-the-art/survey-validation-pass-5.md#notes-for-the-stakeholder)). Its word "hardened" can read as a verdict, and no concept has a recorded driver for every change. Many W3C and ISO quotes may be paraphrases, and critics are often the next authors.
- The second survey passed its gate on [pass 3](../knowledge-across-sources/survey-validation-pass-3.md), which judged only changed sentences, by the stakeholder's order. Its correction P3-01 is not yet applied: the report names entailment as the sole automatic method at the level of meaning outside science. Section 5.2 names both methods.
- Several second-survey steps rest on secondary or abstract-only records, and MediaSpin was read from a preprint ([A4-SR-17](../knowledge-across-sources/sources/area-4/A4-SR-17-verma-mediaspin-2026.md)).
- The second survey did not search chat exports other than Slack, or reach per outlet. Its fact-checking material from 2022 onwards is thin.

## 10. Glossary

- ADR (architecture decision record). A factory file that records one settled architecture choice. ADR-0017 and ADR-0018 matter for the ID prefix.
- AIF (Argument Interchange Format). A model of arguments with claim nodes and nodes for inference, preference, and conflict. It is the documented model for linking a criticism to a conjecture.
- Anchor. The link from a record to the span it came from. Each anchor stores the source's identifier together with its scope.
- Claim. A statement that a source makes about the world, such as a figure in a wire report. The system stores it as a conjecture in the knowledge layer.
- Claim matching. The task of finding messages that one fact-check can serve. It groups mentions of one claim, which raises a mention count, not support.
- CLI (command-line interface). One of the agent tools the factory runs in, such as Claude Code or Codex. Each CLI writes its own transcript format.
- Closed-world assumption. The reading that treats the data as complete, so a missing fact counts as false. A record check needs it, because a missing span must fail.
- Conjecture. A proposed answer to a problem, kept open to refutation. Every claim and idea in the graph stays one.
- Corroborated. The status of a conjecture that passed stated tests, recorded with their severity. It never means true.
- Diarization. The task of finding "who spoke when" in a recording. It labels speakers without naming them.
- DuckDB. An embedded analytical database that runs inside a program, without a server. The factory's usage analysis already uses it.
- Entailment. A relation in which one statement supports another. A textual entailment model labels such relations between sentences automatically.
- Entity resolution. Deciding which records describe the same thing. Merging duplicate claims or ideas is a case of it.
- Error elimination. The step that removes a refuted conjecture from use. Here it marks the conjecture refuted and flags every decision that rests on it.
- F-score. A measure that combines how many found items are right and how many right items are found. A value of 1 is perfect.
- Falsification research. Research that tries to refute a claim with tests defined in advance. The surveys' candidate claims are its input.
- Frame. The aspects of a topic that a text selects and makes salient. Framing research labels the frame of one text at a time.
- GQL (Graph Query Language). The ISO standard query language for property graphs, published in 2024. It is under revision.
- IBIS (Issue-Based Information System). A method that records issues, positions, and arguments. It has the same shape as problem, conjecture, and criticism.
- ID (identifier). A key that names one record.
- IMAP (Internet Message Access Protocol). The protocol mail clients use to read mail on a server. Its threading standard rebuilds email threads from headers.
- `In-Reply-To`. The email header that names the parent of a reply by its `Message-ID`. Mail software often filled it with free text.
- ISO (International Organization for Standardization). The body that publishes GQL and SQL/PGQ.
- Kappa and alpha. Measures of how well people agree when they label the same items. A value of 1 is full agreement, and the recommended alpha threshold is 0.667.
- LLM (large language model). A model that generates text, as the factory's agents do. No record measures how accurately one extracts ideas.
- Matrix. An open chat protocol. Its event ID is a hash of the event.
- MediaSpin. A dataset of headline edits within one outlet, labelled for bias that each edit adds or removes. Its labels come from one LLM.
- Memetracker. A method that tracks quoted phrases and their variants across news and blogs.
- `Message-ID`. The email header that names one version of one message. It must be globally unique.
- METER. A corpus of British news stories labelled as wholly, partially, or not derived from agency copy.
- Named graph. A set of RDF statements with its own name. A nanopublication uses three of them.
- Nanopublication. A small published claim split into assertion, provenance, and publication information. It is the documented pattern for one claim per record.
- Open-world assumption. The reading that treats a missing fact as unknown, not false. OWL uses it, so OWL raises no error for a missing source.
- OPM (Open Provenance Model). A provenance model from 2007, before PROV.
- OWL (Web Ontology Language). A W3C language for describing concepts and inferring facts. Its axioms do not act as record checks.
- `owl:sameAs`. The OWL property that states two names mean the same thing. Its misuse shows why "same claim" must not mean strict identity.
- Property graph. A graph model whose nodes and edges carry key-value pairs. It is the recommended shape of the store.
- PROV. The W3C family of provenance standards from 2013. The store borrows its relation names.
- PROV-O (PROV Ontology). The PROV standard that maps PROV to RDF. It has been a Recommendation since 2013.
- Provenance. The link from a piece of information back to its source and how it came to be.
- RDF (Resource Description Framework). The W3C data model that describes data as triples. RDF 1.2 is still a draft.
- Recursive shape. A shape that refers to itself through other shapes. SHACL leaves its meaning open, so record rules avoid it.
- `References`. The email header that lists the ancestors of a reply, oldest first. A reply builds it from its parent's `References` and `Message-ID`.
- Refutation condition. The observation that would show a conjecture wrong. A conjecture without one is "not testable yet".
- Reification. An RDF encoding that turns a statement into a node, so other statements can describe it.
- RFC (Request for Comments). The series of internet standard texts. The email rules are in RFC 2822 and RFC 5322.
- SHACL (Shapes Constraint Language). The W3C standard shape language from 2017. It is the documented way to check RDF data.
- Shape. A rule set that data must meet, such as "every conjecture has a span".
- Span. An exact passage of a source, with its item, speaker or author, and time. Every record points to at least one.
- SPARQL (SPARQL Protocol and RDF Query Language). The query language for RDF. Version 1.2 is a Working Draft.
- SPICED (Scientific Paraphrase and Information Change Dataset). A dataset of science findings and their retellings, scored for how much the information changed.
- SQL (Structured Query Language). The standard language for relational databases.
- SQL/PGQ (SQL Property Graph Queries). The part of the SQL standard that queries property graphs, published in 2023.
- Stance detection. The task of labelling whether a text is for, against, or neutral towards a target. Stance differs from sentiment.
- State. A part of a W3C annotation that names the version of the document the annotation meant.
- Text Quote Selector. A W3C annotation part that points into a document by quoting the passage and the words around it.
- Text reuse. The use of one text's wording in another. Its detection measures shared wording and cannot tell who copied from whom.
- Triple. One RDF statement of subject, predicate, and object.
- Triple term. An RDF 1.2 triple used inside another triple. It lets RDF make statements about statements.
- Trusty URI. A URI that contains a hash of its content, so any change to the content no longer matches the URI.
- `ts`. The Slack message ID. It looks like a time but is unique only within one channel.
- URI (Uniform Resource Identifier). A string that names a resource on the web.
- Validation pass. One run of a survey's review gate by a reviewer who wrote none of the survey. A pass lists corrections, each with a severity.
- W3C (World Wide Web Consortium). The body that sets web standards. Its stages run from Working Draft to Candidate Recommendation Draft to Recommendation, the final standard.
- XMPP (Extensible Messaging and Presence Protocol). An open chat protocol. Its stable message ID is unique only within the entity that assigned it.
