# Research Survey Plan — Graph And Embeddings

The plan follows [research-brief.json](research-brief.json). It splits the survey by the four scope areas of the brief, so no two assignments research the same concept. All four assignments run in parallel as one wave.

## Research Questions

1. Area 1: Which architectures combine a graph with embeddings for storing, linking, and retrieving knowledge, from GraphRAG and its successors to hybrid graph and vector retrieval, and how does each keep the graph and the vectors consistent?
2. Area 1: Where does an architecture use knowledge graph embeddings of entities and relations, and where does it use text embeddings of nodes and spans, and what does each kind of embedding serve?
3. Area 2: Which stores hold a graph and vectors together, and how do they compare on data model, query languages, transaction and consistency boundary, one query that runs a traversal and a similarity search, maturity, release activity, and project health?
4. Area 3: What can embedding similarity establish for paraphrase, claim matching, text reuse, near-duplicate detection, and same-idea detection, and what does it miss, such as negation, entailment direction, and domain shift?
5. Area 3: Which check turns a similarity result into a confirmed edge, and how are vectors versioned and recomputed when the embedding model changes?
6. Area 4: How did nearest-neighbour indexes develop from locality-sensitive hashing through inverted files and product quantization to graph-based indexes such as HNSW and DiskANN, how does a vector search combine with structured predicates, and what does it cost to keep an index current under updates?
7. Across areas: Which concepts went through several documented rounds of formulation, criticism, and reformulation, and what criticism drove each change?

## Search Angles

- The original paper for each architecture, index, or embedding method, then the papers that criticized it or replaced it
- Peer-reviewed surveys as the overview of each area, such as surveys of graph retrieval-augmented generation, knowledge graph embedding, sentence embedding, and approximate nearest-neighbour search
- Benchmarks and their criticism, such as ANN-Benchmarks, BEIR, MTEB, and the semantic textual similarity tasks, used for what they measure and what their authors say they do not measure
- Project repositories, release notes, and changelogs for each candidate store, which show release activity, maintainers, and open issues
- Project documentation for stated features and query syntax only, never as evidence of performance or adoption
- Foundation and governance records, such as the Apache project reports of Apache AGE, for project health

## Source Targets

- The GraphRAG paper by Edge and others (2024), its successors such as LightRAG and HippoRAG, surveys of graph retrieval-augmented generation from 2024 onward, and the retrieval-augmented generation paper by Lewis and others (2020) as the starting point
- Knowledge graph embedding papers from TransE (2013) through TransH, TransR, DistMult, ComplEx, and RotatE, and surveys of knowledge graph embedding
- Documentation, repositories, and release notes of PostgreSQL, Apache AGE, pgvector, Neo4j, Memgraph, FalkorDB, DuckDB with its graph and vector extensions, and two or three separate vector stores, such as Qdrant, Milvus, or Weaviate
- PostgreSQL mailing list threads and commitfest entries on SQL/PGQ, for its implementation status in PostgreSQL as of November 2026
- Sentence embedding papers, such as InferSent, the Universal Sentence Encoder, Sentence-BERT, and SimCSE, and papers on their limits with negation, entailment direction, anisotropy, and domain shift
- Papers on paraphrase identification, claim matching, text reuse, and near-duplicate detection, such as MinHash by Broder and SimHash by Charikar, and on cross-encoder and natural language inference checks of similarity candidates
- Nearest-neighbour index papers: Indyk and Motwani on locality-sensitive hashing (1998), Jégou and others on product quantization (2011), the navigable small world and HNSW papers by Malkov and others, DiskANN and FreshDiskANN, and papers on filtered search such as Filtered-DiskANN and ACORN

## Assignments

Each assignment declares agent, tier, independent session, a unique output, and a bounded task. The output is a record folder, an ID prefix, and one area index beside the folder, as [source-research](../../../packages/factory/skills/source-research/SKILL.md#record-file) defines. Every task carries the same four requirements:

- For each hardened concept in the area, record the sequence of formulations and the criticism that drove each change, with a source for each step.
- Put the source's own words in straight double quotes in the Evidence section, because `concept-history-check` anchors only on quoted words. When the quoted words hold quotation marks of their own, quote the whole passage from its opening mark to its closing mark.
- Mark each source primary or secondary, and state what it shows and what it does not show.
- Do not install, run, or benchmark any tool or store, and do not use vendor marketing as evidence of capability, performance, or adoption.

Five boundaries keep the areas apart:

- Area 2 owns every fact about a specific product, including its index implementation and its features for keeping vectors in sync. Area 1 and area 4 cite designs and algorithms, not products.
- Area 1 owns how a retrieval pipeline combines graph results and vector results. Area 4 owns how one query combines a vector search with structured predicates inside an index or a query executor.
- Area 3 owns MinHash and SimHash as methods for near-duplicate detection. Area 4 owns locality-sensitive hashing as a family of nearest-neighbour indexes.
- Area 3 owns embedding model versioning and the recomputation of vectors. Area 4 owns the cost of rebuilding or updating an index.
- Graph data models and the standards status of ISO GQL and SQL/PGQ belong to the earlier [knowledge-graph-state-of-the-art](../knowledge-graph-state-of-the-art/survey-report.md) survey. Area 2 records only whether and how a product implements them.

| ID  | Agent      | Tier     | Area                                             | Output                                                                                  | Independent Session |
| --- | ---------- | -------- | ------------------------------------------------ | --------------------------------------------------------------------------------------- | ------------------- |
| A1  | researcher | standard | architectures that combine graphs and embeddings | `sources/area-1/`, prefix `A1-SR-`, index `sources/area-1-architectures.md`             | false               |
| A2  | researcher | standard | stores that hold both                            | `sources/area-2/`, prefix `A2-SR-`, index `sources/area-2-stores.md`                    | false               |
| A3  | researcher | standard | embedding similarity for the system's tasks      | `sources/area-3/`, prefix `A3-SR-`, index `sources/area-3-embedding-similarity.md`      | false               |
| A4  | researcher | standard | nearest-neighbour indexes and hybrid queries     | `sources/area-4/`, prefix `A4-SR-`, index `sources/area-4-nearest-neighbour-indexes.md` | false               |

## Stop Conditions

- Each of the four assignments has recorded sources for the main concepts of its area, and `source-record-check` exits 0 on its folder.
- Area 2 has, for every candidate store, a record-backed value or a recorded gap for each simplicity fact: components, query languages, consistency boundaries, what must be kept in sync, release activity, and project health.
- Area 3 has, for each of its five tasks, at least one record of what similarity finds and one of what it misses, or a recorded gap.
- At least five concepts across the survey have a recorded sequence of formulations, with the criticism and a source for each step. Each area index names its hardened concepts or states that it found none.
- A secondary source is marked as secondary and used only where no primary source is reachable.
- An assignment stops searching when further sources are unlikely to change its findings, and records its failed searches as gaps in its area index.

## Structured Block

The block below is the plan in the shape of `research-survey-plan.schema.json`. The tasks in `assignments` are the full text each researcher receives.

```json
{
  "research_questions": [
    "Area 1: Which architectures combine a graph with embeddings for storing, linking, and retrieving knowledge, from GraphRAG and its successors to hybrid graph and vector retrieval, and how does each keep the graph and the vectors consistent?",
    "Area 1: Where does an architecture use knowledge graph embeddings of entities and relations, and where does it use text embeddings of nodes and spans, and what does each kind of embedding serve?",
    "Area 2: Which stores hold a graph and vectors together, and how do they compare on data model, query languages, transaction and consistency boundary, one query that runs a traversal and a similarity search, maturity, release activity, and project health?",
    "Area 3: What can embedding similarity establish for paraphrase, claim matching, text reuse, near-duplicate detection, and same-idea detection, and what does it miss, such as negation, entailment direction, and domain shift?",
    "Area 3: Which check turns a similarity result into a confirmed edge, and how are vectors versioned and recomputed when the embedding model changes?",
    "Area 4: How did nearest-neighbour indexes develop from locality-sensitive hashing through inverted files and product quantization to graph-based indexes such as HNSW and DiskANN, how does a vector search combine with structured predicates, and what does it cost to keep an index current under updates?",
    "Across areas: Which concepts went through several documented rounds of formulation, criticism, and reformulation, and what criticism drove each change?"
  ],
  "search_angles": [
    "The original paper for each architecture, index, or embedding method, then the papers that criticized it or replaced it",
    "Peer-reviewed surveys as the overview of each area, such as surveys of graph retrieval-augmented generation, knowledge graph embedding, sentence embedding, and approximate nearest-neighbour search",
    "Benchmarks and their criticism, such as ANN-Benchmarks, BEIR, MTEB, and the semantic textual similarity tasks, used for what they measure and what their authors say they do not measure",
    "Project repositories, release notes, and changelogs for each candidate store, which show release activity, maintainers, and open issues",
    "Project documentation for stated features and query syntax only, never as evidence of performance or adoption",
    "Foundation and governance records, such as the Apache project reports of Apache AGE, for project health"
  ],
  "source_targets": [
    "The GraphRAG paper by Edge and others (2024), its successors such as LightRAG and HippoRAG, surveys of graph retrieval-augmented generation from 2024 onward, and the retrieval-augmented generation paper by Lewis and others (2020) as the starting point",
    "Knowledge graph embedding papers from TransE (2013) through TransH, TransR, DistMult, ComplEx, and RotatE, and surveys of knowledge graph embedding",
    "Documentation, repositories, and release notes of PostgreSQL, Apache AGE, pgvector, Neo4j, Memgraph, FalkorDB, DuckDB with its graph and vector extensions, and two or three separate vector stores, such as Qdrant, Milvus, or Weaviate",
    "PostgreSQL mailing list threads and commitfest entries on SQL/PGQ, for its implementation status in PostgreSQL as of November 2026",
    "Sentence embedding papers, such as InferSent, the Universal Sentence Encoder, Sentence-BERT, and SimCSE, and papers on their limits with negation, entailment direction, anisotropy, and domain shift",
    "Papers on paraphrase identification, claim matching, text reuse, and near-duplicate detection, such as MinHash by Broder and SimHash by Charikar, and on cross-encoder and natural language inference checks of similarity candidates",
    "Nearest-neighbour index papers: Indyk and Motwani on locality-sensitive hashing (1998), Jégou and others on product quantization (2011), the navigable small world and HNSW papers by Malkov and others, DiskANN and FreshDiskANN, and papers on filtered search such as Filtered-DiskANN and ACORN"
  ],
  "assignments": [
    "A1 | agent: researcher | tier: standard | independent_session: false | area: architectures that combine graphs and embeddings | output: folder sources/area-1/, ID prefix A1-SR-, index sources/area-1-architectures.md | task: Architectures that combine graphs and embeddings. Start from retrieval-augmented generation (Lewis and others, 2020) and cover retrieval over knowledge graphs from GraphRAG (Edge and others, 2024) to its successors, such as LightRAG and HippoRAG, and hybrid retrieval that combines graph traversal results with vector search results. Cover knowledge graph embeddings of entities and relations, from TransE through TransH, TransR, DistMult, ComplEx, and RotatE, and contrast them with text embeddings of nodes and text spans: what each kind serves in retrieval and linking. For each architecture, record the design facts a simplicity comparison needs: the components the design requires, the query paths, what must be kept in sync between the graph and the vectors, and how the design rebuilds derived data. Cite papers and design descriptions, not products; every fact about a specific store belongs to area 2. Do not research how an index combines a vector search with structured predicates; area 4 owns it. Do not research what similarity establishes for text tasks; area 3 owns it. Use retrieval research from 2020 onward, and older sources only for the history of a concept. For each hardened concept in the area, such as graph retrieval-augmented generation or the translational embedding model, record the sequence of formulations and the criticism that drove each change, with a source for each step. Put the source's own words in straight double quotes in the Evidence section; when the quoted words hold quotation marks of their own, quote the whole passage from its opening mark to its closing mark. Mark each source primary or secondary. State for each source what it shows and what it does not show. Do not install, run, or benchmark any tool. Record failed searches and gaps in the area index.",
    "A2 | agent: researcher | tier: standard | independent_session: false | area: stores that hold both | output: folder sources/area-2/, ID prefix A2-SR-, index sources/area-2-stores.md | task: Stores that hold a graph and vectors together. The candidate stores are PostgreSQL with Apache AGE and pgvector, PostgreSQL with SQL/PGQ where an implementation exists as of November 2026, Neo4j, Memgraph, and FalkorDB with their native vector indexes, DuckDB with its graph and vector extensions, and a graph store beside a separate vector store, such as Qdrant, Milvus, or Weaviate. Add at most two further stores, and only when a primary source shows that they hold both; record the reason in the area index. For each candidate store, record its data model, its query languages, its transaction and consistency boundary, whether and how one query runs a graph traversal and a similarity search together, its vector index implementation and the cost of keeping it current, any feature that keeps vectors in sync with their source text, maturity, release activity, and project health. Record the simplicity facts for each store: number of components, number of query languages, consistency boundaries, and what must be kept in sync. Take release activity and project health from repositories, release notes, changelogs, and foundation reports, such as commit and release dates, active maintainers, open issues, and governance status; never take them from vendor claims. Use vendor documentation only for stated features and syntax. Record only whether a component is open source; do not assess pricing or licences. Do not research the standards status of ISO GQL or SQL/PGQ; the knowledge-graph-state-of-the-art survey covers it. Use the documentation and release state as of November 2026. For each hardened concept in the area, record the sequence of formulations and the criticism that drove each change, with a source for each step. Put the source's own words in straight double quotes in the Evidence section; when the quoted words hold quotation marks of their own, quote the whole passage from its opening mark to its closing mark. Mark each source primary or secondary. State for each source what it shows and what it does not show. Do not install, run, or benchmark any store. Record for every store and every simplicity fact either a record or a gap in the area index. Record failed searches and gaps in the area index.",
    "A3 | agent: researcher | tier: standard | independent_session: false | area: embedding similarity for the system's tasks | output: folder sources/area-3/, ID prefix A3-SR-, index sources/area-3-embedding-similarity.md | task: Embedding similarity for five tasks: paraphrase, claim matching, text reuse, near-duplicate detection, and same-idea detection. Cover sentence embeddings from averaged word vectors through InferSent, the Universal Sentence Encoder, Sentence-BERT, and contrastive methods such as SimCSE, and the benchmarks that measure them, such as the semantic textual similarity tasks, BEIR, and MTEB, with their criticism. For each task, record what similarity finds and what it misses, such as negation, entailment direction, anisotropy, and domain shift. Record the checks that confirm or reject a similarity candidate before it becomes a graph edge, such as cross-encoders and natural language inference models. Cover MinHash and SimHash as methods for near-duplicate detection; locality-sensitive hashing as a nearest-neighbour index belongs to area 4. Record how vectors are versioned and recomputed when the embedding model changes, from papers and model documentation; product features for vector sync belong to area 2, and the cost of rebuilding an index belongs to area 4. Use embedding research from 2020 onward, and older sources only for the history of a concept. For each hardened concept in the area, such as the sentence embedding or the semantic textual similarity benchmark, record the sequence of formulations and the criticism that drove each change, with a source for each step. Put the source's own words in straight double quotes in the Evidence section; when the quoted words hold quotation marks of their own, quote the whole passage from its opening mark to its closing mark. Mark each source primary or secondary. State for each source what it shows and what it does not show. Do not install, run, or benchmark any model. Record for each of the five tasks at least one finding and one limit, or a gap. Record failed searches and gaps in the area index.",
    "A4 | agent: researcher | tier: standard | independent_session: false | area: nearest-neighbour indexes and hybrid queries | output: folder sources/area-4/, ID prefix A4-SR-, index sources/area-4-nearest-neighbour-indexes.md | task: Approximate nearest-neighbour indexes and hybrid queries. Trace the index lineage from tree-based indexes and locality-sensitive hashing (Indyk and Motwani, 1998) through inverted files and product quantization (Jégou and others, 2011) to graph-based indexes: navigable small world, HNSW, DiskANN, and FreshDiskANN. Cover filtered vector search that combines a similarity search with structured predicates, such as pre-filtering, post-filtering, Filtered-DiskANN, and ACORN, and the cost of keeping an index current under inserts, updates, and deletes. Cover ANN-Benchmarks and its criticism for what the benchmark measures. Cite algorithms and papers, not products; every fact about a specific store's index belongs to area 2. MinHash and SimHash as near-duplicate methods belong to area 3. How a retrieval pipeline combines graph and vector results belongs to area 1. Older sources from the 1990s onward are expected for the history of the index lineage. For each hardened concept in the area, such as the graph-based index or filtered search, record the sequence of formulations and the criticism that drove each change, with a source for each step. Put the source's own words in straight double quotes in the Evidence section; when the quoted words hold quotation marks of their own, quote the whole passage from its opening mark to its closing mark. Mark each source primary or secondary. State for each source what it shows and what it does not show. Do not install, run, or benchmark any index. Record failed searches and gaps in the area index."
  ],
  "stop_conditions": [
    "Each of the four assignments has recorded sources for the main concepts of its area, and source-record-check exits 0 on its folder.",
    "Area 2 has, for every candidate store, a record-backed value or a recorded gap for each simplicity fact: components, query languages, consistency boundaries, what must be kept in sync, release activity, and project health.",
    "Area 3 has, for each of its five tasks, at least one record of what similarity finds and one of what it misses, or a recorded gap.",
    "At least five concepts across the survey have a recorded sequence of formulations, with the criticism and a source for each step. Each area index names its hardened concepts or states that it found none.",
    "A secondary source is marked as secondary and used only where no primary source is reachable.",
    "An assignment stops searching when further sources are unlikely to change its findings, and records its failed searches as gaps in its area index."
  ]
}
```
