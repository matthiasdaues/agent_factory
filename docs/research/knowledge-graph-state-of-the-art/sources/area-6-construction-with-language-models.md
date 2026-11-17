# Area 6: Construction And Use With Language Models

This index reports what 17 recorded sources document. It makes no claim that any concept survived refutation. Records sit in the folder `area-6/` and are cited as `A6-SR-NN`. Section 2 lists the records by concept. Primary and secondary marks, and what each record does not show, are in the records.

## 1. State of the art as the sources document it

- A language model can extract graph facts from text, but early tests found it a weak few-shot extractor whose output needed manual checks (A6-SR-01).
- Ontology-conformance and hallucination metrics for extraction exist as a benchmark. Its baselines are two small 2023 models (A6-SR-02).
- GraphRAG builds an LLM-extracted entity graph and community summaries to answer questions about a whole corpus (A6-SR-03). Variants add graph-based retrieval (A6-SR-04), incremental updates (A6-SR-05), and deferred LLM use (A6-SR-06).
- Independent evaluations report that GraphRAG helps on some tasks and not on others. They also report that earlier gains were overstated (A6-SR-07, A6-SR-08, A6-SR-09).
- Agent memory moved from a plain-text record (A6-SR-10) to tiered memory (A6-SR-11) to graph-based memory (A6-SR-13, A6-SR-14). The graph results in these records are vendor self-reports.
- The benchmarks for agent memory are themselves criticized (A6-SR-15).
- An embedded graph database with Cypher, full-text search, and vector search is documented. Its repository was archived in October 2025 (A6-SR-16, A6-SR-17).

## 2. Hardened concepts

A concept is listed here when the records show at least three formulations with a criticism between them. The criticism column states what the cited source says. A step without a source is marked as a gap.

### 2.1 LLM-based knowledge graph extraction (4 steps)

1. **Few-shot extraction with a general model.** May 2023 (A6-SR-01). Criticism: GPT-4 is judged better as an inference assistant than as an extractor. The output needs manual validation. Hallucination is flagged (A6-SR-01).
2. **Ontology-driven extraction with conformance and hallucination metrics.** August 2023 (A6-SR-02). Criticism: baseline results "show that there is room for improvement" (A6-SR-02).
3. **LLM extraction as the indexing step of GraphRAG.** April 2024 (A6-SR-03). Criticism: LLM extraction and summarization make indexing expensive (A6-SR-06, vendor authors).
4. **Extraction by noun-phrase NLP, with LLM use deferred to query time.** November 2024 (A6-SR-06). Criticism: the sources do not evaluate the quality of LLM-extracted graphs directly. Graphs from different implementations vary much in structure (A6-SR-09).

Gap: no recorded source shows measured extraction accuracy on current models.

### 2.2 Graph-based retrieval-augmented generation (5 steps)

1. **Plain RAG.** Gap: the original RAG paper predates 2023 and is not recorded. Edge et al. state its failure: it "fails on global questions" (A6-SR-03).
2. **Entity graph with community summaries.** April 2024 (A6-SR-03). Criticism: cost of indexing (A6-SR-06). Flat data representations in other RAG systems (A6-SR-05).
3. **Graph plus Personalized PageRank (May 2024, A6-SR-04) and dual-level retrieval with incremental updates (October 2024, A6-SR-05).** Criticism: the sources record no direct criticism of these two papers. Gap.
4. **Deferred LLM use.** November 2024 (A6-SR-06). Criticism: later evaluations question the reported gains (A6-SR-07, A6-SR-08).
5. **Conditional use.** February to June 2025 (A6-SR-07, A6-SR-08, A6-SR-09). The sources state that GraphRAG shows "distinct strengths" (A6-SR-07), that gains are "much more moderate than reported previously" (A6-SR-08), and that basic RAG matches or beats GraphRAG on simple fact retrieval (A6-SR-09).

Step 3 is two parallel formulations. The records do not show that LightRAG answered Edge et al. (A6-SR-05).

### 2.3 Agent memory (6 steps)

1. **Natural-language memory stream with reflection.** April 2023 (A6-SR-10). Criticism: gap. The abstract names none.
2. **Tiered memory for limited context windows.** October 2023 (A6-SR-11). Criticism: gap for this step. The benchmark in step 3 reports that models lag humans.
3. **Benchmark for long conversational memory.** February 2024 (A6-SR-12). It reports that long-context models and RAG "still substantially lag behind human performance." Criticism of the benchmark itself: gap. Third-party gold-answer errors surfaced only in search summaries.
4. **Temporal knowledge graph memory.** January 2025 (A6-SR-13, vendor). Its stated problem is static retrieval that loses historical relationships. Criticism: the Mem0 authors' competing claims are in vendor blog posts, not recorded.
5. **Graph variant of extracted memories.** April 2025 (A6-SR-14, vendor). It reports about 2% higher score than its own base configuration.
6. **Benchmarks of explicit facts are too narrow.** February 2026 (A6-SR-15). Existing benchmarks "primarily focus on surface-level factual recall."

## 3. Embedded and file-based stores

The records give one store, Kuzu: documented features (A6-SR-16) and an archived repository with a user reaction (A6-SR-17). Two formulations of one product are not a hardened concept, so no sequence is listed. The Apple acquisition reports are not recorded.

## 4. Gaps

- The original RAG paper (2020) is outside the 2023 start and not recorded.
- Most records are abstract pages read through a page-extract tool. Evaluation tables are unread except parts of A6-SR-09.
- No independent source evaluates agent memory graphs. Zep and Mem0 results are vendor self-reports.
- The dispute between those two vendors is in vendor blog posts, which this survey excludes as evidence.
- Third-party claims of gold-answer errors in LoCoMo are unconfirmed. The Mnemosyne page did not state them.
- No source on embedded stores other than Kuzu was recorded.
- Surveys of LLM-based construction (for example arXiv:2510.20345) and GraphRAG (arXiv:2408.08921) were found and not recorded.
