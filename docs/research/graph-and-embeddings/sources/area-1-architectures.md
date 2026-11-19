# Area 1: Architectures That Combine Graphs and Embeddings

This index covers the 15 source records in [area-1/](area-1/). It reports what the sources document. It does not rank the designs and does not judge any claim.

## State of the Art

Retrieval-augmented generation (RAG) joins a language model to a dense vector index of text chunks (A1-SR-01). The original design updates its knowledge by replacing the whole index (A1-SR-01). Later papers call this design "vector RAG" (A1-SR-02).

Graph-based RAG adds a graph that an LLM extracts from the same text. The designs differ in what they embed:

| Design       | Record   | Graph built from                                       | What is embedded                     | How graph and vector results meet                                                       |
| ------------ | -------- | ------------------------------------------------------ | ------------------------------------ | --------------------------------------------------------------------------------------- |
| GraphRAG     | A1-SR-02 | LLM-extracted entities, relations, claims              | Nothing on the global query path     | Community summaries, map-reduce; no vector step                                         |
| HippoRAG     | A1-SR-05 | Open information extraction triples                    | Noun-phrase nodes                    | Embeddings add synonymy edges and pick seed nodes; Personalized PageRank ranks passages |
| LightRAG     | A1-SR-04 | LLM-extracted entities and relations                   | Short keys of entities and relations | Vector match on keys, then one-hop graph expansion                                      |
| LazyGraphRAG | A1-SR-03 | Noun-phrase co-occurrence                              | Text chunks                          | Chunk similarity ranks communities of the concept graph                                 |
| HippoRAG 2   | A1-SR-06 | Open information extraction triples plus passage nodes | Phrases, triples, passages           | Embedding scores seed the PageRank walk                                                 |
| HybridRAG    | A1-SR-07 | Knowledge graph from the documents                     | Text chunks in a separate store      | The two retrieved contexts are concatenated                                             |

Every graph-based design read here embeds text: chunks, passages, phrases, or keys (A1-SR-03 to A1-SR-07). None of them embeds graph structure with a knowledge graph embedding. The survey A1-SR-08 lists designs that encode nodes, edges, or ego networks with language models, and one design that reranks paths with a knowledge graph embedding score.

Knowledge graph embeddings such as TransE and RotatE learn vectors from triples alone (A1-SR-11, A1-SR-13). They serve link prediction, not retrieval of text. Text-based completion encodes entity and relation descriptions instead (A1-SR-14). Joining structure and text in one space is a named challenge (A1-SR-15).

Evaluations from 2025 report that graph-based RAG often falls behind vector RAG on factual questions (A1-SR-06, A1-SR-09, A1-SR-10). A1-SR-06 comes from the HippoRAG authors; A1-SR-09 and A1-SR-10 are benchmark studies by other groups. The benchmarks report higher construction cost, latency, storage, and prompt tokens (A1-SR-09, A1-SR-10). One study reports that extracted graphs miss about a third of answer entities on two datasets (A1-SR-09).

On consistency, the record is thin. GraphRAG describes no update procedure (A1-SR-02). LightRAG adds new documents by set union and describes no deletion (A1-SR-04). The survey A1-SR-08 names dynamic update as an open direction. No source read here describes how a changed or deleted document propagates to both the graph and the vectors.

## Hardened Concept 1: Graph-Based Retrieval-Augmented Generation

1. **Vector RAG over text chunks, 2020-05.** A dense index of 100-word chunks feeds a generator (A1-SR-01). Criticism that led on: the design "fails on global questions directed at an entire text corpus" (A1-SR-02). A second criticism states that "each new passage is encoded in isolation" (A1-SR-05).
2. **GraphRAG community summaries, 2024-04.** An LLM builds an entity graph, Leiden groups it, and summaries of each community answer global questions (A1-SR-02). Criticism that led on: indexing cost and a full rebuild of communities on new data (A1-SR-04); no sense of which communities matter for local queries (A1-SR-03); evaluation by an LLM judge without references, which shows position bias (A1-SR-09).
3. **HippoRAG, 2024-05.** Personalized PageRank over an open knowledge graph, with embedding-based synonymy edges and seed nodes (A1-SR-05). Criticism that led on: ignoring context causes about 48% of errors in its own analysis (A1-SR-05). Its performance drops most on discourse understanding (A1-SR-06).
4. **LightRAG, 2024-10.** Entity and relation keys in a vector database, one-hop graph expansion, and additive updates (A1-SR-04). Criticism that led on: structure-augmented designs fall below embedding-only RAG on factual tasks (A1-SR-06). Gap: the one source found that criticises its missing deletion path was unreachable (see Gaps).
5. **LazyGraphRAG, 2024-11.** The GraphRAG authors drop up-front summarisation and use chunk embeddings to rank communities at query time (A1-SR-03). Gap: no independent criticism was found.
6. **HippoRAG 2, 2025-02.** Passage nodes join the graph, and embedding similarity seeds the PageRank walk (A1-SR-06). Criticism that led on: graph pipelines, HippoRAG 2 among them, add prompt tokens over vanilla RAG (A1-SR-10).
7. **Systematic evaluation, 2025-02 to 2025-06.** One benchmark finds that vector and graph retrieval are complementary, with no consistent winner (A1-SR-09). A second reports that graph-based RAG often underperforms vanilla RAG (A1-SR-10). Gap: no source criticising these benchmarks was found.

## Hardened Concept 2: Combining Graph Results and Vector Results

1. **Concatenation of two independent contexts, 2024-08.** HybridRAG appends vector context, then graph context (A1-SR-07). Criticism that led on: context precision drops to 0.79 against 0.96 for graph retrieval alone (A1-SR-07, self-reported).
2. **Hybrid indexing as a category, 2024-08.** The survey sorts indexing into graph, text, vector, and hybrid (A1-SR-08). It names no criticism of the hybrid category. Gap: no source criticises the taxonomy.
3. **Score ensemble, then fusion inside the graph walk, 2024-05 to 2025-02.** HippoRAG adds graph and embedding scores (A1-SR-05). HippoRAG 2 criticises that it "simply aggregates scores" and moves passage similarity into the PageRank seeds (A1-SR-06).
4. **Selection or integration per query, 2025-02.** One method routes each query to vector or graph retrieval; the other runs both and concatenates (A1-SR-09). Criticism recorded by the same source: integration scores higher but runs both pipelines for every query (A1-SR-09). Gap: no later reformulation was found.

## Hardened Concept 3: Knowledge Graph Embedding, Structure or Text

1. **TransE, 2013.** A relation is a translation between entity vectors, learned from triples alone (A1-SR-11). Criticism that led on: TransE handles reflexive, one-to-many, many-to-one, and many-to-many relations poorly (A1-SR-12).
2. **TransH, 2014.** A relation is a translation on a relation-specific hyperplane (A1-SR-12). Criticism that led on: each earlier model, the TransE family and DistMult and ComplEx, captures only some relation patterns (A1-SR-13). Gap: TransR, DistMult, and ComplEx were not read in full text; A1-SR-13 summarises them as a secondary source.
3. **RotatE, 2019-02.** A relation is a rotation in complex space and covers symmetry, inversion, and composition (A1-SR-13). Criticism that led on: structure-only embeddings "suffer from the sparseness of knowledge graphs" (A1-SR-14).
4. **Text-based completion, 2019-09.** KG-BERT scores a triple from the text of its entity and relation descriptions (A1-SR-14). Criticism recorded by the same source: the model is expensive at link prediction time (A1-SR-14). The survey A1-SR-15 names joint embedding of structure and text as a challenge.
5. **Use in graph-based RAG, 2024 onward.** The RAG designs read here embed text, not structure (A1-SR-02 to A1-SR-07). The survey cites one design that reranks with a knowledge graph embedding score (A1-SR-08). Gap: no source explains why graph-based RAG designs dropped structure embeddings.

## Hardened Concept 4: Keeping the Graph and the Vectors Consistent

1. **Whole-index replacement, 2020-05.** RAG swaps a 2016 index for a 2018 index (A1-SR-01). Criticism that led on: gap; no source criticises the swap directly.
2. **No update procedure, 2024-04.** GraphRAG describes none (A1-SR-02). Criticism that led on: new data forces a regeneration of all community summaries (A1-SR-04).
3. **Additive union, 2024-10.** LightRAG indexes a new document and unions its nodes and edges into the graph (A1-SR-04). Criticism that led on: gap; the preprint that addresses deletion was unreachable.
4. **Open direction, 2024-08.** The survey states that most methods rest on static databases (A1-SR-08). Gap: no source read describes deletion or change of a source document across both graph and vectors.

## Gaps

- **Jigsaw-LightRAG preprint (Preprints.org 202511.1058).** A web search named it as an extension of LightRAG with local updates and deletions. The landing page and the PDF returned "Access Denied". It is not recorded, and step 4.3 has no criticism source.
- **Ruffinelli et al., "You CAN Teach an Old Dog New Tricks!", ICLR 2020.** OpenReview returned an HTML page instead of the PDF. This criticism of knowledge graph embedding training is not recorded.
- **Sun et al., "A Re-evaluation of Knowledge Graph Completion Methods", ACL 2020 (arXiv:1911.03903).** The PDF was read but not recorded. It criticises the evaluation protocol of neural completion models, which lies outside this area's question of structure or text.
- **TransR, DistMult, ComplEx.** Not read in full text. A1-SR-13 covers them as a secondary source.
- **Zhou et al. (2025).** Cited by A1-SR-10 for latency figures. Not read.
- **Independent criticism of LazyGraphRAG.** None found. Its only source is the authors' blog (A1-SR-03).
- **Peer review of A1-SR-08 and A1-SR-14.** The venue was not confirmed.
- **Product update features.** The documentation and release notes of GraphRAG and LightRAG software were not read. Facts about products belong to area 2.
- **Vector recomputation after an embedding model change.** Area 3 owns this question. No area 1 source addresses it.
