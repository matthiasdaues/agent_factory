# A1-SR-05: Gutiérrez et al., HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models

```json
{
  "source_identity": "Bernal Jiménez Gutiérrez, Yiheng Shu, Yu Gu, Michihiro Yasunaga, Yu Su, 'HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models', NeurIPS 2024; arXiv:2405.14831v3; https://arxiv.org/abs/2405.14831",
  "author_or_issuing_body": "Gutiérrez, Shu, Gu, Yasunaga, Su (The Ohio State University; Stanford University)",
  "publisher": "arXiv (Cornell University); conference version in NeurIPS 2024",
  "publication_date": "2024-05-23T00:00:00Z",
  "relevant_event_date": "2024-05-23",
  "source_family": "Primary. Independent line of graph-based RAG built on Personalized PageRank over an open knowledge graph. Successor in A1-SR-06 by the same group.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Detailed Methodology section (Offline Indexing, Online Retrieval); Conclusions & Limitations section; Appendix F error analysis",
  "method": "Design description and experiments. An LLM extracts triples by open information extraction; a retrieval encoder adds synonymy edges between noun phrases whose embeddings exceed a cosine threshold; a query's named entities are matched to nodes by embedding; Personalized PageRank spreads from those nodes and passage scores follow from a node-passage count matrix.",
  "limitations": "Date is arXiv v1; the text read is v3 of 14 January 2025. Authors evaluate their own design on multi-hop question answering. Shows: embeddings of noun-phrase nodes serve two jobs, synonymy edges and query-node lookup; the graph search is PageRank, not vector search. Does not show: a procedure for removing or changing a passage; the term continuously updating is claimed in the conclusion without a described update algorithm in the sections read.",
  "provenance": "PDF downloaded with curl from arXiv on 2026-11-18 and extracted with pdftotext; quotes copied from the extracted text, with line breaks and hyphenation joined. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "HippoRAG synergistically orchestrates LLMs, knowledge graphs, and the Personalized PageRank algorithm to mimic the different roles of neocortex and hippocampus in human memory."
- Section 1: "However, current RAG methods are still unable to help LLMs perform tasks that require integrating new knowledge across passage boundaries since each new passage is encoded in isolation."
- Detailed Methodology, Offline Indexing: "Finally, we use M to add the extra set of synonymy relations E ′ discussed above when the cosine similarity between two entity representations in N is above a threshold τ ."
- Detailed Methodology, Online Retrieval: "These named entities Cq from the query are then encoded by the same retrieval encoder M . Then, the previously defined query nodes are chosen as the set of nodes in N with the highest cosine similarity to the query named entities Cq ."
- Conclusions & Limitations: "Given that the rest of the errors are graph search errors, also in Appendix F, we note that several avenues for improvements over simple PPR exist, such as allowing relations to guide graph traversal directly."
- Conclusions & Limitations: "Finally, and perhaps most importantly, HippoRAG’s scalability still calls for further validation."
- Appendix F: "Unfortunately, this design is also one of our method’s greatest limitations since ignoring contextual cues accounts for around 48% of errors in our small-scale error analysis."
