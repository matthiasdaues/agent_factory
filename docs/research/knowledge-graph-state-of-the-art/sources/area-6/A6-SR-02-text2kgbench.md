# A6-SR-02 — Text2KGBench: ontology-driven KG generation from text (2023)

```json
{
  "source_identity": "Mihindukulasooriya et al., 'Text2KGBench: A Benchmark for Ontology-Driven Knowledge Graph Generation from Text', arXiv:2308.02357, https://arxiv.org/abs/2308.02357",
  "author_or_issuing_body": "Nandana Mihindukulasooriya, Sanju Tiwari, Carlos F. Enguix, Kusum Lata",
  "publisher": "arXiv",
  "publication_date": "2023-08-04T00:00:00Z",
  "relevant_event_date": "2023-08-04",
  "source_family": "Primary. Original benchmark paper. Lineage: academic preprint (IBM Research and collaborators).",
  "precise_evidence_location": "Abstract.",
  "method": "Benchmark construction from Wikidata-TekGen (10 ontologies, 13,474 sentences) and DBpedia-WebNLG (19 ontologies, 4,860 sentences), with seven metrics, and two baseline models.",
  "limitations": "Shows that the task is framed as extraction that complies with a given ontology, with metrics for ontology conformance and hallucination. Does not show current model performance: the baselines are Vicuna-13B and Alpaca-LoRA-13B only. I did not read the result tables. The author list and affiliations were not verified against the PDF.",
  "provenance": "Read on 2026-11-17 through the WebFetch tool, which returns a model-made extract of the page, not the page itself. Re-verify by opening the URL."
}
```

## Evidence

Quotes come from that extract and are limited to short passages.

- Abstract: the task requires "extract facts from the text while complying with the given ontology."
- Abstract: the benchmark defines "seven evaluation metrics to measure fact extraction performance, ontology conformance, and hallucinations by LLMs."
- Abstract: "The baseline results show that there is room for improvement."
- Abstract: two datasets, Wikidata-TekGen (10 ontologies, 13,474 sentences) and DBpedia-WebNLG (19 ontologies, 4,860 sentences).
