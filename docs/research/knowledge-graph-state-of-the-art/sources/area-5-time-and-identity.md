# Area 5: Time and identity

This index covers temporal and bitemporal knowledge graphs, entity resolution, and the use and misuse of `owl:sameAs`. It reports what the recorded sources document. It does not judge whether any concept survived refutation. The records are in the folder `sources/area-5/` and carry the IDs `A5-SR-01` to `A5-SR-14`. Each record states what its source shows and what it does not show.

## State of the art, as the sources document it

- OWL defines `owl:sameAs` as a statement that two URI references refer to the same thing (A5-SR-01). OWL 2 does not assume unique names (A5-SR-02).
- Linked Data publishers used `owl:sameAs` for weaker relations as well. Two studies from 2010 describe this (A5-SR-03, A5-SR-04). In one rater experiment, about 51% of sampled links looked correct, with a wide spread (A5-SR-04).
- The later response keeps `owl:sameAs` and scores each link instead. An identity graph of over 500 million statements gets an error degree per link from its community structure (A5-SR-05).
- Temporal RDF started as a proposal to label triples with validity intervals (A5-SR-06). A 2021 survey lists six ways to attach time to an edge and names no single winner (A5-SR-09).
- SQL:2011 standardised two time periods per row. The literature calls a table with both periods bitemporal (A5-SR-08).
- A 2025 agent memory system defines two timelines on graph edges and invalidates old edges with a language model (A5-SR-10).
- Entity resolution moved from probabilistic comparison vectors to learned matchers (A5-SR-11), then to fine-tuned language models (A5-SR-12), then to prompted language models (A5-SR-13). Checking the resulting links is a separate and less studied problem (A5-SR-14).

## Hardened concepts

Four concepts in this area show several documented formulations with criticism between them. Each step below names its source. A step without a source is marked as a gap.

### 1. Identity semantics of `owl:sameAs` (4 steps)

1. **Strict identity, 2004.** `owl:sameAs` states that two URI references "actually refer to the same thing" (A5-SR-01). The 2012 edition keeps the framework and states that OWL 2 does not make the unique name assumption (A5-SR-02). Criticism that led to step 2: in 2010, Ding et al. report that links do not always follow the formal semantics. Merging two profiles of one person lets a reasoner infer facts that were never true. Properties such as a licence can spread across datasets (A5-SR-03).
2. **Use by context, 2010.** Ding et al. advise consumers to pick an interpretation per use. For some links only one URI should be chosen, and for others the descriptions should be merged (A5-SR-03). Criticism that led to step 3: this gives no way to say which relation a publisher meant. Halpin et al. argue that identity is "one point on a scale of similarity, one that is often too strong" (A5-SR-04).
3. **A scale of similarity relations, 2010.** Halpin et al. propose a Similarity Ontology with referentially opaque alternatives (A5-SR-04). Their experiment found that about 21% of the sampled links fit a coarse "similar and related" relation, and about 27% could not be judged from the RDF alone. Criticism that led to step 4: the authors themselves conclude that the ontology "explores too large of a design space to be reliably deployed". They suggest one simple similarity property instead (A5-SR-04).
4. **Keep the property, score the links, 2018 to 2020.** Raad et al. keep `owl:sameAs`. They compute an error degree per link from community structure, and they publish subgraphs cut at chosen error degrees (A5-SR-05). The record shows that about 5% of the statements score above 0.8. It does not show a labelled precision figure.

Gaps for this concept: I did not find evidence that the simple similarity property of Halpin et al. was adopted. I did not read the 2007 posts by Vatant and Passant, which Ding et al. cite. I did not read the sameAs.cc paper of 2018, and I did not read the 2018 error-degree paper. Their content reaches this index only through A5-SR-05.

### 2. Temporal labeling of RDF (3 steps)

1. **Label triples with validity intervals, 2005.** Gutierrez, Hurtado, and Vaisman prefer labeling to versioning. Labeling keeps the distributed nature of RDF and handles valid time. Versioning handles only transaction time (A5-SR-06). Criticism that led to step 2: the next paper states that time had so far entered the Semantic Web only as a datatype property, and it works within existing RDF syntax. It names no fault of step 1 (A5-SR-07).
2. **Named graphs and standard SPARQL, 2009.** Tappolet and Bernstein express temporal RDF with named graphs, so that any temporal query runs in standard SPARQL. They add a shorthand, T-SPARQL (A5-SR-07). Only the abstract was reachable. Criticism that led to step 3: the 2021 survey reports no verdict against it. It lists named graphs, property graph attributes, RDF-star, reification, n-ary relations, and singleton properties side by side (A5-SR-09).
3. **Several representations in parallel, 2021.** Hogan et al. describe the options and call named graphs the most flexible, because one graph name carries the context of many edges (A5-SR-09).

Gaps: I did not find a paper that criticises the labelled-triple syntax directly. The journal version of Temporal RDF is unread. The change to RDF 1.2 triple terms belongs to area 2.

### 3. Valid time and transaction time (4 steps)

1. **Two time dimensions in RDF, 2005.** Gutierrez et al. separate valid time from transaction time and say that versioning records only the second (A5-SR-06). Criticism that led to step 2: none is recorded for this step. The origin of the two terms in the temporal database literature is a gap.
2. **A standard proposal, 1995 to 2001.** The ISO SQL committee started a temporal part based on TSQL2 in 1995. The proposals "generated considerable controversy", and the work was cancelled in 2001 (A5-SR-08). The text of TSQL2 itself is a gap. Criticism that led to step 3: according to the committee members who wrote the account, the hidden period column "is incompatible with SQL's notion of tables" (A5-SR-08).
3. **System time and application time, 2011.** SQL:2011 adds a system-time period for transaction time and an application-time period for valid time as named columns. A table with both is called bitemporal in the literature (A5-SR-08). The record is secondary because the standard text was not read.
4. **Bitemporal edges with model-based invalidation, 2025.** Zep defines a timeline of events and a timeline of ingestion. It stores four timestamps per fact and sets the end of validity of an edge when a new edge contradicts it (A5-SR-10). The paper names no criticism of step 3 and does not cite it in the text read. Its authors sell the system, and the paper reports no check of how often the invalidation is correct.

### 4. Entity resolution methods (5 steps)

1. **Probabilistic comparison vectors, 1969.** Fellegi and Sunter proposed a probabilistic model that uses attribute similarities as comparison vectors (A5-SR-11, secondary). I could not read the 1969 paper, so this step rests on a survey. Newcombe's earlier procedure is a gap.
2. **Learned matching functions.** A large number of works learn the match probabilities from training data (A5-SR-11, section 5.3). Criticism that led to step 3: the survey names no single criticism. The records do not show why the field moved to neural models, and that reason is a gap.
3. **Deep learning matchers.** DeepER and DeepMatcher use word embeddings and recurrent networks (A5-SR-11, section 9.1). Criticism that led to step 4: the authors of Ditto say their approach does not need entries with the same schema, "a sharp contrast" to DeepMatcher. Their own footnote says DeepMatcher can drop that requirement (A5-SR-12).
4. **Fine-tuned pre-trained language models, 2020.** Ditto reports up to 29% higher F1 than the previous best and needs at most half the labelled data on some benchmarks (A5-SR-12). The authors measured this and I did not repeat it. Criticism that led to step 5: Peeters et al. state that such models need much task-specific training data and are not robust on unseen entities (A5-SR-13).
5. **Prompted generative language models, 2023 to 2024.** Peeters et al. test zero-shot and in-context prompting and fine-tuned large models. They find that no single prompt is best, because each model and dataset needs its own (A5-SR-13). Criticism for a later step: none recorded.

A related line concerns checking links after they are made. Idrissou et al. note that only ground truth, manual work, and crowd sourcing exist for this, and propose network metrics over links between several datasets (A5-SR-14). Raad et al. apply the same family of ideas to `owl:sameAs` (A5-SR-05).

## Gaps

- **Fellegi and Sunter 1969.** Two copies were reachable. Both returned unreadable data. The step is secondary (A5-SR-11).
- **Beek et al., sameAs.cc, ESWC 2018.** Only a search summary was reachable. It is not recorded.
- **Raad et al., ISWC 2018.** The publisher page needs access I did not have. Content reaches the index through A5-SR-05 only.
- **Halpin and Hayes, OWLED 2010, and Vatant 2007.** Not found. Ding et al. mention them (A5-SR-03).
- **Valid time and transaction time before 2005.** I found no source for Snodgrass and Ahn or for the TSQL2 text.
- **ISO/IEC 9075:2011 itself.** Paywalled. The account of it is secondary (A5-SR-08).
- **OWL 2 individual equality.** Section 9.6.1 of the 2012 text was not read (A5-SR-02).
- **Time Ontology (OWL-Time).** A survey mentions it (A5-SR-09). I did not read the Recommendation.
- **Criticism of Temporal RDF.** I found no direct critique. The change from step 1 to step 2 is documented only as a design choice.
- **Overlaps.** Reification, named graphs, and RDF-star belong to area 2. The Zep paper also belongs to area 6, which owns its capability claims. Area 5 uses it only for its time model.
