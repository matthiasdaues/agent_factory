# A6-SR-11 — MemGPT (Packer et al., 2023)

```json
{
  "source_identity": "Packer et al., 'MemGPT: Towards LLMs as Operating Systems', arXiv:2310.08560, https://arxiv.org/abs/2310.08560",
  "author_or_issuing_body": "Charles Packer, Sarah Wooders, Kevin Lin, Vivian Fang, Shishir G. Patil, Ion Stoica, Joseph E. Gonzalez",
  "publisher": "arXiv",
  "publication_date": "2023-10-12T00:00:00Z",
  "relevant_event_date": "2023-10-12",
  "source_family": "Primary. Original paper. Lineage: academic preprint (UC Berkeley); v2 dated 2024-02-12. Authors later founded a vendor; not independent of that vendor's later claims.",
  "precise_evidence_location": "Abstract.",
  "method": "Describes virtual context management that moves data between memory tiers.",
  "limitations": "Shows the stated problem (limited context windows) and a tiered memory design. The memory is not a graph. Does not show evaluation results; I read the abstract only.",
  "provenance": "Read on 2026-11-17 through the WebFetch tool, which returns a model-made extract of the page, not the page itself. Re-verify by opening the URL."
}
```

## Evidence

Quotes come from that extract and are limited to short passages.

- Abstract: LLMs "are constrained by limited context windows."
- Abstract: the authors propose "virtual context management, a technique drawing inspiration from hierarchical memory systems."
- Abstract (paraphrase): the system moves data between memory tiers and uses interrupts to manage control flow.
