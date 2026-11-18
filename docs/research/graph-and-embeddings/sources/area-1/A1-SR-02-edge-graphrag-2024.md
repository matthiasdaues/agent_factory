# A1-SR-02: Edge et al., From Local to Global: A GraphRAG Approach to Query-Focused Summarization

```json
{
  "source_identity": "Darren Edge et al., 'From Local to Global: A GraphRAG Approach to Query-Focused Summarization', arXiv:2404.16130v2; https://arxiv.org/abs/2404.16130",
  "author_or_issuing_body": "Edge, Trinh, Cheng, Bradley, Chao, Mody, Truitt, Metropolitansky, Ness, Larson (Microsoft Research, Microsoft Strategic Missions and Technologies, Microsoft Office of the CTO)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2024-04-24T00:00:00Z",
  "relevant_event_date": "2024-04-24",
  "source_family": "Primary. Origin of the community-summary design of graph-based RAG, called GraphRAG. Cites Lewis et al. (A1-SR-01) as the RAG origin. Criticised by A1-SR-04, A1-SR-09, and A1-SR-10; revised by its own authors in A1-SR-03.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Figure 1 caption; Section 6.2 Future work",
  "method": "Design description and evaluation. An LLM extracts an entity graph from text chunks, Leiden community detection groups the graph, an LLM writes community summaries, and a map-reduce over the summaries answers global questions. Answers are compared head-to-head by an LLM judge on comprehensiveness, diversity, and empowerment.",
  "limitations": "Date is arXiv v1; the text read is v2 of 19 February 2025. Paper by the design's authors. The evaluation uses an LLM judge without ground-truth references; A1-SR-09 reports position bias in this kind of judgement. The paper does not describe how the index changes when a source document changes. Shows: the pipeline stages and what is summarised. Does not show: an embedding of graph structure, a combined graph and vector query, or any incremental update.",
  "provenance": "PDF downloaded with curl from arXiv on 2026-11-18 and extracted with pdftotext; quotes copied from the extracted text, with line breaks and hyphenation joined. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "However, RAG fails on global questions directed at an entire text corpus, such as" a question about the main themes of the dataset. Note: the quote stops before an inner quotation.
- Abstract: "Our approach uses an LLM to build a graph index in two stages: first, to derive an entity knowledge graph from the source documents, then to pregenerate community summaries for all groups of closely related entities."
- Abstract: "Given a question, each community summary is used to generate a partial response, before all partial responses are again summarized in a final response to the user."
- Section 1: "A common approach to conventional RAG is to use text embeddings, retrieving records closest to the query in vector space where closeness corresponds to semantic similarity (Gao et al., 2023)."
- Section 1: "While some RAG approaches may use alternative retrieval mechanisms, we collectively refer to the family of conventional approaches as vector RAG."
- Figure 1 caption: "This graph index spans nodes (e.g., entities), edges (e.g., relationships), and covariates (e.g., claims) that have been detected, extracted, and summarized by LLM prompts tailored to the domain of the dataset."
- Section 6.2: "This includes RAG approaches that operate in a more local manner, via embedding-based matching of user queries and graph annotations. In particular, we see potential in hybrid RAG schemes that combine embeddingbased matching with just-in-time community report generation before employing our map-reduce summarization mechanisms."
- Note: the global query path described here uses community summaries, not vector search. The paper names embedding-based matching only as future work.
- Not shown: any procedure for adding, changing, or deleting a source document after indexing.
