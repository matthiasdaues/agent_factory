# A1-SR-08: Peng et al., Graph Retrieval-Augmented Generation: A Survey

```json
{
  "source_identity": "Boci Peng, Yun Zhu, Yongchao Liu, Xiaohe Bo, Haizhou Shi, Chuntao Hong, Yan Zhang, Siliang Tang, 'Graph Retrieval-Augmented Generation: A Survey', arXiv:2408.08921v2; https://arxiv.org/abs/2408.08921",
  "author_or_issuing_body": "Peng, Zhu, Liu, Bo, Shi, Hong, Zhang, Tang (Peking University, Zhejiang University, Ant Group, Renmin University of China, Rutgers University)",
  "publisher": "arXiv (Cornell University); formatted for an ACM journal with placeholder volume and DOI",
  "publication_date": "2024-08-15T00:00:00Z",
  "relevant_event_date": "2024-08-15",
  "source_family": "Secondary. Survey of graph-based RAG methods. Summarises GraphRAG (A1-SR-02), HybridRAG (A1-SR-07), and knowledge-graph question answering systems; independent of the primary design papers.",
  "precise_evidence_location": "Abstract; Section 5.2 Indexing (text, vector, hybrid indexing); Section 6.1.4 Discussion of retrievers; Section 6.4.2 Knowledge Enhancement (reranking); Section 10.1 Dynamic and Adaptive Graphs",
  "method": "Literature survey. Defines a three-stage workflow and sorts methods by indexing, retrieval, and generation technique.",
  "limitations": "Date is arXiv v1; the text read is v2 of 10 September 2024. The ACM reference shows placeholder volume and DOI, so peer-review status was not confirmed. Written before LightRAG (A1-SR-04) and the 2025 criticism (A1-SR-09, A1-SR-10). Shows: the taxonomy of graph, text, vector, and hybrid indexing, and that the survey names dynamic update as an open direction. Does not show: an assessment of any method's update behaviour.",
  "provenance": "PDF downloaded with curl from arXiv on 2026-11-18 and extracted with pdftotext; quotes copied from the extracted text, with line breaks and hyphenation joined. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "We formalize the GraphRAG workflow, encompassing Graph-Based Indexing, Graph-Guided Retrieval, and Graph-Enhanced Generation."
- Section 5.2.3: "G-Retriever [55] employs language models to encode textual information associated with each node and edge within the graph, while GRAG [58] uses language models to convert 𝑘-hop ego networks into graph embeddings, thereby better preserving structural information."
- Section 5.2.4: "Each of the above three indexing methods offers distinct advantages: graph indexing facilitates easy access to structural information, text indexing simplifies retrieval of textual content, and vector indexing enables quick and efficient searches."
- Section 5.2.4: "For instance, HybridRAG [144] retrieves both vector and graph data simultaneously to enhance the content retrieved."
- Section 6.4.2: "KagNet [97] decomposes the retrieved paths into triplets and reranks the paths based on the confidence score measured by the knowledge graph embedding (KGE) techniques." Note: this is the one place in the survey where a knowledge graph embedding serves retrieval directly, as a reranking score.
- Section 10.1: "Most GraphRAG methods [32, 41, 85, 86, 111, 188] are built upon static databases; however, as time progresses, new entities and relationships inevitably emerge [20, 44, 181]."
- Section 10.1: "Developing efficient methods for dynamic updates and real-time integration of new data will significantly enhance the effectiveness and relevance of GraphRAG systems."
