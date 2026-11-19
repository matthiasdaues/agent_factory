# A1-SR-04: Guo et al., LightRAG: Simple and Fast Retrieval-Augmented Generation

```json
{
  "source_identity": "Zirui Guo, Lianghao Xia, Yanhua Yu, Tu Ao, Chao Huang, 'LightRAG: Simple and Fast Retrieval-Augmented Generation', arXiv:2410.05779v3; https://arxiv.org/abs/2410.05779",
  "author_or_issuing_body": "Guo, Xia, Yu, Ao, Huang (Beijing University of Posts and Telecommunications; University of Hong Kong)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2024-10-08T00:00:00Z",
  "relevant_event_date": "2024-10-08",
  "source_family": "Primary. Successor design to GraphRAG (A1-SR-02), which it criticises on cost of retrieval and of incremental update.",
  "precise_evidence_location": "Abstract; Section 3.1 Graph-based Text Indexing (LLM profiling, deduplication, fast adaptation to incremental knowledge base); Section 3.2 Dual-level Retrieval Paradigm; Section 4 cost analysis, incremental text update paragraph",
  "method": "Design description and experiments. An LLM extracts entities and relations from chunks, writes a key-value profile for each, merges duplicates, and stores keys in a vector database. Queries extract keywords, match them to entities and relations by vector similarity, and add one-hop neighbours. New documents are indexed the same way and merged by set union.",
  "limitations": "Date is arXiv v1; the text read is v3 of 28 April 2025. Authors evaluate their own design. The GraphRAG update cost is an estimate from token counts, not a measured run. The update procedure covers additions only. Shows: the embedded units are short keys for entities and relations, the query path is vector match followed by graph expansion, and the additive update path. Does not show: deletion, change of an existing document, or how stale profiles are found.",
  "provenance": "PDF downloaded with curl from arXiv on 2026-11-18 and extracted with pdftotext; quotes copied from the extracted text, with line breaks and hyphenation joined. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "Additionally, the integration of graph structures with vector representations facilitates efficient retrieval of related entities and their relationships, significantly improving response times while maintaining contextual relevance."
- Section 3.1, LLM profiling: "Each index key is a word or short phrase that enables efficient retrieval, while the corresponding value is a text paragraph summarizing relevant snippets from external data to aid in text generation. Entities use their names as the sole index key, whereas relations may have multiple index keys derived from LLM enhancements that include global themes from connected entities."
- Section 3.2, step (ii): "The algorithm uses an efficient vector database to match local query keywords with candidate entities and global query keywords with relations linked to global keys."
- Section 3.2, step (iii), paraphrase: the algorithm then adds the one-hop neighbouring nodes of the retrieved nodes and edges.
- Section 3.1, incremental: "For a new document D′ , the incremental update algorithm processes it using the same graph-based indexing steps φ as before" and the result is merged "by taking the union of the node sets" and edge sets. Note: the two quoted fragments come from one passage; the formula symbols were dropped in extraction.
- Section 4, incremental text update: "When a new dataset of the same size as the legal dataset is introduced, GraphRAG must dismantle its existing community structure to incorporate new entities and relationships, followed by complete regeneration."
- Not shown: a search of the full text for the word stems delet and remov finds no deletion procedure.
