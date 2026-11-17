# A6-SR-06 — LazyGraphRAG blog post (Edge, Trinh, Larson, 2024)

```json
{
  "source_identity": "Edge, Trinh, Larson, 'LazyGraphRAG: Setting a new standard for quality and cost', Microsoft Research blog, https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/",
  "author_or_issuing_body": "Darren Edge, Ha Trinh, Jonathan Larson (Microsoft)",
  "publisher": "Microsoft Research blog",
  "publication_date": "2024-11-25T00:00:00Z",
  "relevant_event_date": "2024-11-25",
  "source_family": "Primary for the design rationale; vendor communication, same authors as A6-SR-03. Not independent of A6-SR-03.",
  "precise_evidence_location": "Body text on indexing cost and on the LazyGraphRAG method.",
  "method": "Vendor blog post describing a change to the GraphRAG indexing design.",
  "limitations": "Shows what the GraphRAG authors state as the indexing cost problem and their changed design. This is vendor material: it is not used as evidence of capability or adoption. The cost ratio is a vendor claim and I did not check it. No peer review.",
  "provenance": "Read on 2026-11-17 through the WebFetch tool, which returns a model-made extract of the page, not the page itself. Re-verify by opening the URL."
}
```

## Evidence

Quotes come from that extract and are limited to short passages.

- Text (extract): full GraphRAG is expensive to index because an LLM extracts and describes entities and relationships, summarizes them, and builds community structure.
- Text (extract): LazyGraphRAG replaces LLM extraction with NLP noun-phrase extraction for concepts and co-occurrences and skips LLM summarization at index time.
- Text (extract): it "defers all LLM use until query time."
- Text (extract): the vendor states cost of "0.1% of the costs of full GraphRAG" and indexing cost "identical to vector RAG."
