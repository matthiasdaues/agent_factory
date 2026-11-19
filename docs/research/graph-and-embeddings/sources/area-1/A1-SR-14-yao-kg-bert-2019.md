# A1-SR-14: Yao, Mao, Luo, KG-BERT: BERT for Knowledge Graph Completion

```json
{
  "source_identity": "Liang Yao, Chengsheng Mao, Yuan Luo, 'KG-BERT: BERT for Knowledge Graph Completion', arXiv:1909.03193v2; https://arxiv.org/abs/1909.03193",
  "author_or_issuing_body": "Yao, Mao, Luo (Northwestern University)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2019-09-07T00:00:00Z",
  "relevant_event_date": "2019-09-07",
  "source_family": "Primary. Text-based knowledge graph completion. Criticises structure-only embeddings such as TransE (A1-SR-11).",
  "precise_evidence_location": "Abstract; Introduction; Discussions paragraph before the Conclusion",
  "method": "Model design and experiments. Entity and relation descriptions of a triple are fed as a text sequence to a fine-tuned BERT model that scores the triple.",
  "limitations": "Date is arXiv v1; the text read is v2 of 11 September 2019. Peer-review venue not confirmed. Shows: the turn from structure embeddings to text encoders for scoring triples, and its cost. Does not show: use in retrieval for generation.",
  "provenance": "PDF downloaded with curl from arXiv on 2026-11-18 and extracted with pdftotext; quotes copied from the extracted text, with line breaks and hyphenation joined. Re-verify at the URL above."
}
```

## Evidence

- Introduction: "However, most knowledge graph embedding models only use structure information in observed triple facts, which suffer from the sparseness of knowledge graphs."
- Abstract: "We treat triples in knowledge graphs as textual sequences and propose a novel framework named Knowledge Graph Bidirectional Encoder Representations from Transformer (KG-BERT) to model these triples."
- Abstract: "Our method takes entity and relation descriptions of a triple as input and computes scoring function of the triple with the KG-BERT language model."
- Discussions: "However, a major limitation is that BERT model is expensive, which makes the link prediction evaluation very time consuming, link prediction evaluation needs to replace head or tail entity with almost all entities, and all corrupted triple sequences are fed into the 12 layer Transformer model."
