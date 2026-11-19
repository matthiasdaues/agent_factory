# A1-SR-07: Sarmah et al., HybridRAG: Integrating Knowledge Graphs and Vector Retrieval Augmented Generation for Efficient Information Extraction

```json
{
  "source_identity": "Bhaskarjit Sarmah, Benika Hall, Rohan Rao, Sunil Patel, Stefano Pasquali, Dhagash Mehta, 'HybridRAG: Integrating Knowledge Graphs and Vector Retrieval Augmented Generation for Efficient Information Extraction', arXiv:2408.04948v1; https://arxiv.org/abs/2408.04948",
  "author_or_issuing_body": "Sarmah, Pasquali, Mehta (BlackRock, Inc.); Hall, Rao, Patel (NVIDIA)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2024-08-09T00:00:00Z",
  "relevant_event_date": "2024-08-09",
  "source_family": "Primary. Hybrid of a knowledge-graph RAG and a vector RAG on financial transcripts. Cited by the survey A1-SR-08 as its example of hybrid indexing.",
  "precise_evidence_location": "Abstract; Section 4.4 HybridRAG; Section 5 Results (Table 5 discussion)",
  "method": "Experiment on earnings-call transcripts. Runs a vector RAG and a knowledge-graph RAG separately, concatenates both retrieved contexts, and scores answers with RAGAS-style metrics.",
  "limitations": "Industry authors; one domain and one dataset. The term GraphRAG in this paper means knowledge-graph RAG in general, not the A1-SR-02 design. Shows: the simplest fusion, which is concatenation of two independent retrieval results, and its cost in context precision. Does not show: any shared index, any embedding of graph elements, or any consistency rule between the two stores.",
  "provenance": "PDF downloaded with curl from arXiv on 2026-11-18 and extracted with pdftotext; quotes copied from the extracted text, with line breaks and hyphenation joined. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "we show that HybridRAG which retrieves context from both vector database and KG outperforms both traditional VectorRAG and GraphRAG individually when evaluated at both the retrieval and generation stages in terms of retrieval accuracy and answer generation."
- Section 4.4: "For the proposed HybridRAG technique, upon obtaining all the contextual information from VectorRAG and GraphRAG, we concatenate these contexts to form a unified context utilizing both techniques."
- Section 4.4: "The context from VectorRAG is appended first, followed by the context from GraphRAG."
- Section 5: "Context precision was highest for GraphRAG at 0.96, significantly surpassing VectorRAG (0.84) and HybridRAG (0.79)."
- Section 5: "While this integration allows for more comprehensive information retrieval, it also introduces additional content that may not align precisely with the ground truth, thus affecting the context precision metric."
- Not shown: how the vector database and the knowledge graph are built from the same documents or kept in step.
