# A6-SR-13 — Zep: A Temporal Knowledge Graph Architecture for Agent Memory (Rasmussen et al., 2025)

```json
{
  "source_identity": "Rasmussen et al., 'Zep: A Temporal Knowledge Graph Architecture for Agent Memory', arXiv:2501.13956, https://arxiv.org/abs/2501.13956",
  "author_or_issuing_body": "Preston Rasmussen, Pavlo Paliychuk, Travis Beauvais, Jack Ryan, Daniel Chalef",
  "publisher": "arXiv",
  "publication_date": "2025-01-20T00:00:00Z",
  "relevant_event_date": "2025-01-20",
  "source_family": "Primary for the design; vendor paper. Lineage: preprint describing the commercial Zep service and its Graphiti engine.",
  "precise_evidence_location": "Abstract.",
  "method": "Describes a memory service built on Graphiti, a temporally aware knowledge graph engine, and evaluates on DMR and LongMemEval.",
  "limitations": "Shows the design claim: a temporal graph that keeps historical relationships. Does not show capability independently: the results are self-reported by the vendor and the page lists no affiliations. I did not check the numbers. Vendor results are not used as evidence of capability here.",
  "provenance": "Read on 2026-11-17 through the WebFetch tool, which returns a model-made extract of the page, not the page itself. Re-verify by opening the URL."
}
```

## Evidence

Quotes come from that extract and are limited to short passages.

- Abstract: "Zep addresses this fundamental limitation through its core component Graphiti -- a temporally-aware knowledge graph engine."
- Abstract: "Zep demonstrates superior performance (94.8% vs 93.4%)" against MemGPT on the DMR benchmark (self-reported).
- Abstract: "accuracy improvements of up to 18.5% while simultaneously reducing response latency by 90%" on LongMemEval (self-reported).
