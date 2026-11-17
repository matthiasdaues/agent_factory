# A6-SR-03 — From Local to Global: A Graph RAG Approach (Edge et al., 2024)

```json
{
  "source_identity": "Edge et al., 'From Local to Global: A Graph RAG Approach to Query-Focused Summarization', arXiv:2404.16130, https://arxiv.org/abs/2404.16130",
  "author_or_issuing_body": "Darren Edge, Ha Trinh, Newman Cheng, Joshua Bradley, Alex Chao, Apurva Mody, Steven Truitt, Dasha Metropolitansky, Robert Osazuwa Ness, Jonathan Larson (Microsoft)",
  "publisher": "arXiv",
  "publication_date": "2024-04-24T00:00:00Z",
  "relevant_event_date": "2024-04-24",
  "source_family": "Primary. Original GraphRAG paper. Lineage: Microsoft Research preprint; v2 dated 2025-02-19. Authors are the system's vendor, so capability claims are self-reported.",
  "precise_evidence_location": "Abstract and introduction.",
  "method": "Proposes an LLM-built entity graph, community detection, pregenerated community summaries, and combined partial answers. Evaluated on datasets in the one-million-token range.",
  "limitations": "Shows the problem statement and the method. The authors report better comprehensiveness and diversity on global questions. Does not show cost, and later work questions the evaluation (see A6-SR-07, A6-SR-08, A6-SR-09). I read the abstract page only, not the evaluation section.",
  "provenance": "Read on 2026-11-17 through the WebFetch tool, which returns a model-made extract of the page, not the page itself. Re-verify by opening the URL."
}
```

## Evidence

Quotes come from that extract and are limited to short passages.

- Introduction: "RAG fails on global questions directed at an entire text corpus."
- Introduction: such questions are "inherently a query-focused summarization (QFS) task, rather than an explicit retrieval task."
- Introduction: "Prior QFS methods, meanwhile, do not scale to the quantities of text indexed by typical RAG systems."
- Abstract (paraphrase): an LLM builds an entity knowledge graph, pregenerates community summaries, and combines partial responses into a final answer.
